"""FastAPI backend wrapping existing RSA digital-signature demo functions."""

from __future__ import annotations

import base64
import hashlib
import io
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pyhanko import stamp
from pyhanko.keys import load_cert_from_pemder
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import fields, signers
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext

app = FastAPI(title="RSA Digital Signature Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
CERT_DIR = OUTPUT_DIR / "certs"
PDF_DIR = OUTPUT_DIR / "pdf"
UPLOAD_DIR = OUTPUT_DIR / "uploads"
SIGNED_DIR = OUTPUT_DIR / "signed"

for d in (CERT_DIR, PDF_DIR, UPLOAD_DIR, SIGNED_DIR):
    d.mkdir(parents=True, exist_ok=True)

DEFAULT_PASSPHRASE = "123456"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/generate-keys")
async def generate_keys():
    """Generate an RSA-2048 key pair and self-signed certificate."""
    session_id = uuid.uuid4().hex[:12]
    key_path = CERT_DIR / f"{session_id}_private_key.pem"
    cert_path = CERT_DIR / f"{session_id}_certificate.pem"

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "RSA Demo"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Demo Signer"),
    ])

    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )

    # PEM bytes
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            DEFAULT_PASSPHRASE.encode()
        ),
    )
    cert_pem = certificate.public_bytes(serialization.Encoding.PEM)

    # Public key PEM (for display)
    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    key_path.write_bytes(key_pem)
    cert_path.write_bytes(cert_pem)

    return {
        "sessionId": session_id,
        "publicKey": pub_pem.decode(),
        "privateKey": key_pem.decode(),
        "certificate": cert_pem.decode(),
    }


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF and return its SHA-256 hash."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10 MB limit.")

    file_id = uuid.uuid4().hex[:12]
    save_path = UPLOAD_DIR / f"{file_id}.pdf"
    save_path.write_bytes(contents)

    file_hash = _sha256_hex(contents)

    return {
        "fileId": file_id,
        "fileName": file.filename,
        "fileSize": len(contents),
        "hash": file_hash,
    }


@app.post("/api/sign")
async def sign_pdf(fileId: str = Form(...), sessionId: str = Form(...)):
    """Sign an uploaded PDF using the generated key pair."""
    pdf_path = UPLOAD_DIR / f"{fileId}.pdf"
    key_path = CERT_DIR / f"{sessionId}_private_key.pem"
    cert_path = CERT_DIR / f"{sessionId}_certificate.pem"

    for p, label in [(pdf_path, "PDF"), (key_path, "Private key"), (cert_path, "Certificate")]:
        if not p.exists():
            raise HTTPException(status_code=404, detail=f"{label} not found. ID may have expired.")

    signed_path = SIGNED_DIR / f"{fileId}_signed.pdf"

    signer_obj = signers.SimpleSigner.load(
        str(key_path),
        str(cert_path),
        key_passphrase=DEFAULT_PASSPHRASE.encode(),
    )

    with pdf_path.open("rb") as infile, signed_path.open("wb") as outfile:
        writer = IncrementalPdfFileWriter(infile)
        fields.append_signature_field(
            writer,
            sig_field_spec=fields.SigFieldSpec(
                "Signature1", on_page=0, box=(72, 80, 322, 150)
            ),
        )
        meta = signers.PdfSignatureMetadata(
            field_name="Signature1",
            reason="RSA Digital Signature Demo",
            location="Web Application",
            name="Demo Signer",
        )
        pdf_signer = signers.PdfSigner(
            meta,
            signer=signer_obj,
            stamp_style=stamp.TextStampStyle(
                stamp_text="Digitally signed by: %(signer)s\nTime: %(ts)s"
            ),
        )
        pdf_signer.sign_pdf(writer, output=outfile)

    # Compute hash + raw signature bytes for visualization
    signed_bytes = signed_path.read_bytes()
    signed_hash = _sha256_hex(signed_bytes)

    # Read the actual signature value from the signed PDF for display
    with signed_path.open("rb") as f:
        reader = PdfFileReader(f)
        sigs = list(reader.embedded_signatures)
        sig_hex = ""
        if sigs:
            sig_obj = sigs[0]
            raw = sig_obj.pkcs7_content
            sig_hex = raw[:64].hex() + "..."

    original_hash = _sha256_hex(pdf_path.read_bytes())

    return {
        "fileId": fileId,
        "signedFileId": f"{fileId}_signed",
        "originalHash": original_hash,
        "signedHash": signed_hash,
        "signaturePreview": sig_hex,
        "fileName": f"{fileId}_signed.pdf",
        "fileSize": len(signed_bytes),
    }


@app.get("/api/download/{file_id}")
async def download_signed(file_id: str):
    """Download a signed PDF."""
    signed_path = SIGNED_DIR / f"{file_id}.pdf"
    if not signed_path.exists():
        raise HTTPException(status_code=404, detail="Signed file not found.")
    return FileResponse(
        signed_path,
        media_type="application/pdf",
        filename=f"{file_id}.pdf",
    )


@app.post("/api/verify")
async def verify_signature(
    file: UploadFile = File(...),
    sessionId: str = Form(...),
):
    """Verify the signature of an uploaded signed PDF."""
    cert_path = CERT_DIR / f"{sessionId}_certificate.pem"
    if not cert_path.exists():
        raise HTTPException(status_code=404, detail="Certificate not found.")

    contents = await file.read()
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    trusted_cert = load_cert_from_pemder(str(cert_path))
    validation_context = ValidationContext(
        trust_roots=[trusted_cert],
        allow_fetching=False,
    )

    try:
        reader = PdfFileReader(io.BytesIO(contents))
        signatures = list(reader.embedded_signatures)

        if not signatures:
            return {
                "valid": False,
                "message": "No signatures found in the PDF.",
                "details": [],
            }

        results = []
        all_valid = True
        for idx, sig in enumerate(signatures, start=1):
            status = validate_pdf_signature(
                sig, signer_validation_context=validation_context
            )
            is_valid = bool(status.bottom_line)
            if not is_valid:
                all_valid = False
            signer_cert = status.signing_cert
            subject = signer_cert.subject.human_friendly if signer_cert else "Unknown"
            results.append({
                "index": idx,
                "fieldName": sig.field_name,
                "valid": is_valid,
                "intact": bool(status.intact),
                "cryptoValid": bool(status.valid),
                "coverage": status.coverage.name,
                "modificationLevel": status.modification_level.name,
                "hashAlgorithm": status.md_algorithm,
                "signatureMechanism": str(status.pkcs7_signature_mechanism),
                "signer": subject,
                "signedAt": (
                    status.signer_reported_dt.isoformat()
                    if status.signer_reported_dt
                    else None
                ),
            })

        return {
            "valid": all_valid,
            "message": "VALID SIGNATURE" if all_valid else "INVALID SIGNATURE",
            "hash": _sha256_hex(contents),
            "details": results,
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Verification failed: {str(e)}",
            "details": [],
        }


@app.post("/api/tamper")
async def tamper_pdf(fileId: str = Form(...)):
    """Create a tampered copy of a signed PDF for demo purposes."""
    signed_path = SIGNED_DIR / f"{fileId}.pdf"
    if not signed_path.exists():
        raise HTTPException(status_code=404, detail="Signed file not found.")

    data = bytearray(signed_path.read_bytes())
    if len(data) < 400:
        raise HTTPException(status_code=400, detail="PDF too small to tamper.")

    data[350] ^= 0x01
    tampered_id = f"{fileId}_tampered"
    tampered_path = SIGNED_DIR / f"{tampered_id}.pdf"
    tampered_path.write_bytes(data)

    return {
        "tamperedFileId": tampered_id,
        "fileName": f"{tampered_id}.pdf",
        "fileSize": len(data),
    }

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
def health():
    return {"status": "ok"}


@app.post("/api/generate-keys")
def generate_keys():
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
def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF and return its SHA-256 hash."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = file.file.read()
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
def sign_pdf(fileId: str = Form(...), sessionId: str = Form(...)):
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

    sig_field_name = f"Signature_{uuid.uuid4().hex[:8]}"

    with pdf_path.open("rb") as infile, signed_path.open("wb") as outfile:
        writer = IncrementalPdfFileWriter(infile)
        fields.append_signature_field(
            writer,
            sig_field_spec=fields.SigFieldSpec(
                sig_field_name, on_page=0, box=(72, 80, 322, 150)
            ),
        )
        meta = signers.PdfSignatureMetadata(
            field_name=sig_field_name,
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
def download_signed(file_id: str):
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
def verify_signature(
    file: UploadFile = File(...),
    sessionId: str = Form(...),
):
    """Verify the signature of an uploaded signed PDF."""
    cert_path = CERT_DIR / f"{sessionId}_certificate.pem"
    if not cert_path.exists():
        raise HTTPException(status_code=404, detail="Certificate not found.")

    contents = file.file.read()
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


@app.post("/api/verify-external")
def verify_external(
    file: UploadFile = File(...),
    publicKey: str = Form(...),
):
    """
    Verify a signed PDF using an external public key.
    This allows verifying signatures from outside the current session
    without requiring local session state.
    """
    contents = file.file.read()
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Convert public key string to bytes, trim whitespace
    pub_str = publicKey.strip() if isinstance(publicKey, str) else publicKey.decode().strip()
    pub_pem_bytes = pub_str.encode()

    try:

        if not (pub_pem_bytes.startswith(b'-----BEGIN') and b'-----END' in pub_pem_bytes):
            raise HTTPException(
                status_code=400,
                detail="Public key must be PEM format (starting with '-----BEGIN PUBLIC KEY-----' and ending with '-----END PUBLIC KEY-----')."
            )

        # Reject common wrong formats explicitly for better UX.
        if b'-----BEGIN CERTIFICATE-----' in pub_pem_bytes:
            raise HTTPException(
                status_code=400,
                detail="This endpoint verifies with PUBLIC KEY. Please paste '-----BEGIN PUBLIC KEY----- ... -----END PUBLIC KEY-----', not a certificate."
            )

        if b'-----BEGIN PRIVATE KEY-----' in pub_pem_bytes or b'-----BEGIN RSA PRIVATE KEY-----' in pub_pem_bytes:
            raise HTTPException(
                status_code=400,
                detail="Private key is not allowed for verification. Please paste a PUBLIC KEY PEM."
            )

        # Load and validate provided PUBLIC KEY
        try:
            provided_pub_key = serialization.load_pem_public_key(pub_pem_bytes)
            provided_pub_spki_der = provided_pub_key.public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid public key format: {str(e)[:150]}"
            )

        reader = PdfFileReader(io.BytesIO(contents))
        signatures = list(reader.embedded_signatures)

        if not signatures:
            return {
                "valid": False,
                "message": "No signatures found in the PDF.",
                "usedPublicKey": pub_str[:100] + "..." if len(pub_str) > 100 else pub_str,
                "details": [],
            }

        results = []
        all_valid = True
        for idx, sig in enumerate(signatures, start=1):
            try:
                # Verify signature cryptographic integrity first.
                status = validate_pdf_signature(sig)

                signer_cert = status.signing_cert
                subject = signer_cert.subject.human_friendly if signer_cert else "Unknown"

                # Compare signer's embedded public key with the provided external key.
                key_match = False
                if signer_cert is not None:
                    signer_cert_der = signer_cert.dump()
                    signer_x509 = x509.load_der_x509_certificate(signer_cert_der)
                    signer_pub_key = signer_x509.public_key()
                    signer_pub_spki_der = signer_pub_key.public_bytes(
                        serialization.Encoding.DER,
                        serialization.PublicFormat.SubjectPublicKeyInfo,
                    )
                    key_match = signer_pub_spki_der == provided_pub_spki_der

                is_valid = bool(status.intact) and bool(status.valid) and key_match
                if not is_valid:
                    all_valid = False

                results.append({
                    "index": idx,
                    "fieldName": sig.field_name,
                    "valid": is_valid,
                    "keyMatch": key_match,
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
            except Exception as sig_error:
                results.append({
                    "index": idx,
                    "fieldName": sig.field_name,
                    "valid": False,
                    "error": str(sig_error),
                })
                all_valid = False

        return {
            "valid": all_valid,
            "message": "VALID SIGNATURE" if all_valid else "INVALID SIGNATURE",
            "hash": _sha256_hex(contents),
            "usedPublicKey": pub_str[:100] + "..." if len(pub_str) > 100 else pub_str,
            "details": results,
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "valid": False,
            "message": f"Verification failed: {str(e)}",
            "usedPublicKey": pub_str[:100] + "..." if len(pub_str) > 100 else pub_str,
            "details": [],
        }


@app.post("/api/export-public-key")
def export_public_key(sessionId: str = Form(...)):
    """
    Export the public key from session certificate for external verification.
    """
    cert_path = CERT_DIR / f"{sessionId}_certificate.pem"

    if not cert_path.exists():
        raise HTTPException(status_code=404, detail="Certificate not found for this session.")

    cert_pem = cert_path.read_bytes()
    cert_obj = x509.load_pem_x509_certificate(cert_pem)
    pub_pem = cert_obj.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    return {
        "publicKey": pub_pem,
        "sessionId": sessionId,
    }


@app.post("/api/tamper")
def tamper_pdf(fileId: str = Form(...)):
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

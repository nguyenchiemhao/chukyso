from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from pyhanko import stamp
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
CERT_DIR = OUTPUT_DIR / "certs"
PDF_DIR = OUTPUT_DIR / "pdf"

DEFAULT_KEY_PATH = CERT_DIR / "demo_private_key.pem"
DEFAULT_CERT_PATH = CERT_DIR / "demo_certificate.pem"
DEFAULT_UNSIGNED_PDF = PDF_DIR / "unsigned_demo.pdf"
DEFAULT_SIGNED_PDF = PDF_DIR / "signed_demo.pdf"
DEFAULT_PASSPHRASE = "123456"


def ensure_directories() -> None:
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)


def generate_self_signed_certificate(
    cert_path: Path, key_path: Path, passphrase: str
) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Chu ky so demo"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Demo Signer"),
        ]
    )

    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
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

    key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode()),
    )
    cert_bytes = certificate.public_bytes(serialization.Encoding.PEM)

    key_path.write_bytes(key_bytes)
    cert_path.write_bytes(cert_bytes)


def create_demo_pdf(pdf_path: Path) -> None:
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4

    c.setTitle("Digital signature demo")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, "PDF Digital Signature Demo")

    c.setFont("Helvetica", 12)
    lines = [
        "This PDF is created by Python.",
        "The visible signature area is placed at the bottom of page 1.",
        "After signing, changing the file content will invalidate the signature.",
    ]

    y = height - 110
    for line in lines:
        c.drawString(72, y, line)
        y -= 22

    c.setLineWidth(1)
    c.rect(72, 80, 250, 70)
    c.drawString(82, 130, "Visible signature placeholder")

    c.save()


def sign_pdf(
    input_pdf: Path, output_pdf: Path, cert_path: Path, key_path: Path, passphrase: str
) -> None:
    signer = signers.SimpleSigner.load(
        str(key_path),
        str(cert_path),
        key_passphrase=passphrase.encode(),
    )

    with input_pdf.open("rb") as infile, output_pdf.open("wb") as outfile:
        writer = IncrementalPdfFileWriter(infile)
        fields.append_signature_field(
            writer,
            sig_field_spec=fields.SigFieldSpec(
                "Signature1",
                on_page=0,
                box=(72, 80, 322, 150),
            ),
        )

        meta = signers.PdfSignatureMetadata(
            field_name="Signature1",
            reason="Demo PDF signing with Python",
            location="Local machine",
            name="Demo Signer",
        )

        pdf_signer = signers.PdfSigner(
            meta,
            signer=signer,
            stamp_style=stamp.TextStampStyle(
                stamp_text="Digitally signed by: %(signer)s\nTime: %(ts)s"
            ),
        )
        pdf_signer.sign_pdf(writer, output=outfile)


def run_demo(passphrase: str) -> None:
    ensure_directories()
    generate_self_signed_certificate(
        cert_path=DEFAULT_CERT_PATH,
        key_path=DEFAULT_KEY_PATH,
        passphrase=passphrase,
    )
    create_demo_pdf(DEFAULT_UNSIGNED_PDF)
    sign_pdf(
        input_pdf=DEFAULT_UNSIGNED_PDF,
        output_pdf=DEFAULT_SIGNED_PDF,
        cert_path=DEFAULT_CERT_PATH,
        key_path=DEFAULT_KEY_PATH,
        passphrase=passphrase,
    )

    print("Demo completed successfully.")
    print(f"Certificate: {DEFAULT_CERT_PATH}")
    print(f"Private key: {DEFAULT_KEY_PATH}")
    print(f"Unsigned PDF: {DEFAULT_UNSIGNED_PDF}")
    print(f"Signed PDF: {DEFAULT_SIGNED_PDF}")
    print(
        "Note: this uses a self-signed certificate, so PDF viewers may warn that "
        "the signer is not trusted."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Basic PDF signing demo with Python and pyHanko."
    )
    parser.add_argument(
        "--passphrase",
        default=DEFAULT_PASSPHRASE,
        help="Passphrase used to encrypt the private key.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_demo(passphrase=args.passphrase)


if __name__ == "__main__":
    main()

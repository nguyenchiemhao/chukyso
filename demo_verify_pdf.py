from __future__ import annotations

import argparse
from pathlib import Path

from pyhanko.keys import load_cert_from_pemder
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CERT_PATH = BASE_DIR / "output" / "certs" / "demo_certificate.pem"
DEFAULT_PDF_PATH = BASE_DIR / "output" / "pdf" / "signed_demo.pdf"


def verify_pdf(pdf_path: Path, cert_path: Path, show_details: bool) -> int:
    trusted_cert = load_cert_from_pemder(str(cert_path))
    validation_context = ValidationContext(
        trust_roots=[trusted_cert],
        allow_fetching=False,
    )

    with pdf_path.open("rb") as infile:
        reader = PdfFileReader(infile)
        signatures = reader.embedded_signatures

        if not signatures:
            print("Khong tim thay chu ky nao trong file PDF.")
            return 1

        print(f"Da tim thay {len(signatures)} chu ky trong PDF.")

        exit_code = 0
        for index, embedded_signature in enumerate(signatures, start=1):
            status = validate_pdf_signature(
                embedded_signature,
                signer_validation_context=validation_context,
            )

            print(f"\n=== Chu ky #{index}: {embedded_signature.field_name} ===")
            print(f"Trang thai tong quat: {'VALID' if status.bottom_line else 'INVALID'}")
            print(f"Toan ven noi dung: {'OK' if status.intact else 'FAILED'}")
            print(f"Chu ky ma hoc: {'OK' if status.valid else 'FAILED'}")
            print(f"Pham vi bao ve: {status.coverage.name}")
            print(f"Muc do sua doi: {status.modification_level.name}")
            print(f"Thuat toan bam: {status.md_algorithm}")
            print(f"Co che ky: {status.pkcs7_signature_mechanism}")

            signer_cert = status.signing_cert
            subject = signer_cert.subject.human_friendly if signer_cert else "Unknown"
            print(f"Nguoi ky: {subject}")

            if status.signer_reported_dt is not None:
                print(f"Thoi gian ky: {status.signer_reported_dt.isoformat()}")

            if show_details:
                print("\nChi tiet xac minh:")
                print(status.pretty_print_details())

            if not status.bottom_line:
                exit_code = 1

        return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recipient-side demo: verify whether a signed PDF is valid."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=DEFAULT_PDF_PATH,
        help="Path to the signed PDF file.",
    )
    parser.add_argument(
        "--cert",
        type=Path,
        default=DEFAULT_CERT_PATH,
        help="Path to the sender certificate (contains the public key).",
    )
    parser.add_argument(
        "--show-details",
        action="store_true",
        help="Print full validation details from pyHanko.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    exit_code = verify_pdf(
        pdf_path=args.pdf,
        cert_path=args.cert,
        show_details=args.show_details,
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()

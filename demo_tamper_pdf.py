from __future__ import annotations

import argparse
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_PDF = BASE_DIR / "output" / "pdf" / "signed_demo.pdf"
DEFAULT_OUTPUT_PDF = BASE_DIR / "output" / "pdf" / "tampered_demo.pdf"


def tamper_pdf(input_pdf: Path, output_pdf: Path) -> None:
    data = bytearray(input_pdf.read_bytes())

    if len(data) < 400:
        raise ValueError("PDF qua nho de tao demo sua doi.")

    # Flip one byte in the signed content range so signature validation fails.
    data[350] ^= 0x01
    output_pdf.write_bytes(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a tampered copy of a signed PDF for verification testing."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PDF,
        help="Path to the original signed PDF.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PDF,
        help="Path to write the tampered PDF copy.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    tamper_pdf(args.input, args.output)
    print(f"Tampered PDF created at: {args.output}")


if __name__ == "__main__":
    main()

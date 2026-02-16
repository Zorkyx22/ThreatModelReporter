"""CLI entry point for STERIS."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from steris import __version__
from steris.csv_reader import CSVValidationError, read_threats
from steris.generator import RenderError, TypstNotFoundError, generate_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="steris",
        description="Generate a PDF threat modeling report from a CSV file.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        metavar="CSV",
        type=Path,
        help="Path to the threat modeling CSV file.",
    )
    parser.add_argument(
        "-o", "--output",
        default=Path("output/report.pdf"),
        metavar="PDF",
        type=Path,
        help="Destination path for the generated PDF (default: output/report.pdf).",
    )
    parser.add_argument(
        "--template",
        metavar="TYP",
        type=Path,
        default=None,
        help="Path to a custom Typst template file.",
    )
    parser.add_argument(
        "--typst-bin",
        metavar="PATH",
        default=None,
        help="Explicit path to the Typst binary (default: 'typst' on PATH).",
    )
    parser.add_argument(
        "--title",
        default="Threat Modeling Report",
        help="Report title (default: 'Threat Modeling Report').",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        threats = read_threats(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except CSVValidationError as e:
        print(f"CSV validation error: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        generate_report(
            threats=threats,
            output_pdf=args.output,
            template=args.template,
            typst_bin=args.typst_bin,
            title=args.title,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except TypstNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)
    except RenderError as e:
        print(f"Render error: {e}", file=sys.stderr)
        sys.exit(4)

    print(f"Report written to: {args.output}")


if __name__ == "__main__":
    main()

"""Report generation: render a Typst template and produce a PDF."""

from __future__ import annotations

import csv
import shutil
import subprocess
import tempfile
from pathlib import Path

from steris.csv_reader import Threat


DEFAULT_TEMPLATE = Path(__file__).parent.parent.parent / "templates" / "report.typ"


class TypstNotFoundError(Exception):
    pass


class RenderError(Exception):
    pass


def _find_typst(typst_bin: str | None) -> str:
    """Resolve the Typst binary path.

    Args:
        typst_bin: Explicit path provided by the user, or None to search PATH.

    Returns:
        The resolved path string.

    Raises:
        TypstNotFoundError: If the binary cannot be found.
    """
    candidate = typst_bin or "typst"
    resolved = shutil.which(candidate)
    if resolved is None:
        raise TypstNotFoundError(
            f"Typst binary not found: '{candidate}'. "
            "Install Typst from https://github.com/typst/typst/releases "
            "and ensure it is on your PATH (or pass --typst-bin)."
        )
    return resolved


def _write_data_typ(threats: list[Threat], dest: Path) -> None:
    """Write threat data as a Typst-importable CSV file."""
    if not threats:
        return

    fieldnames = list(threats[0].keys())
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(threats)


def generate_report(
    threats: list[Threat],
    output_pdf: Path,
    template: Path | None = None,
    typst_bin: str | None = None,
    title: str = "Threat Modeling Report",
) -> None:
    """Render a PDF report from threat data using Typst.

    Args:
        threats: Parsed threat list from csv_reader.read_threats().
        output_pdf: Destination path for the generated PDF.
        template: Path to a .typ template file. Defaults to templates/report.typ.
        typst_bin: Explicit path to the Typst binary.
        title: Report title injected as a Typst input variable.

    Raises:
        TypstNotFoundError: If Typst cannot be located.
        RenderError: If Typst exits with a non-zero status.
    """
    typst = _find_typst(typst_bin)
    template_path = template or DEFAULT_TEMPLATE

    if not template_path.exists():
        raise FileNotFoundError(f"Typst template not found: {template_path}")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Sort by Interaction so the template can group threats into sections
        sorted_threats = sorted(threats, key=lambda t: t.get("Interaction", "").casefold())

        # Write threat data as CSV for Typst to import
        data_csv = tmp_path / "threats.csv"
        _write_data_typ(sorted_threats, data_csv)

        # Copy template into temp dir so relative imports resolve
        tmp_template = tmp_path / "report.typ"
        tmp_template.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")

        cmd = [
            typst,
            "compile",
            str(tmp_template),
            str(output_pdf.resolve()),
            "--input", f"title={title}",
            "--input", f"data={data_csv.name}",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RenderError(
                f"Typst compilation failed:\n{result.stderr.strip()}"
            )

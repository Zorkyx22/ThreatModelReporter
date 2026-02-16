"""Tests for the report generator module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from steris.generator import (
    RenderError,
    TypstNotFoundError,
    _find_typst,
    _write_data_typ,
    generate_report,
)


# ─── _find_typst ──────────────────────────────────────────────────────────────

def test_find_typst_on_path():
    with patch("shutil.which", return_value="/usr/bin/typst"):
        assert _find_typst(None) == "/usr/bin/typst"


def test_find_typst_explicit_path():
    with patch("shutil.which", return_value="/opt/typst/typst"):
        assert _find_typst("/opt/typst/typst") == "/opt/typst/typst"


def test_find_typst_not_found_raises():
    with patch("shutil.which", return_value=None):
        with pytest.raises(TypstNotFoundError, match="Typst binary not found"):
            _find_typst(None)


# ─── _write_data_typ ──────────────────────────────────────────────────────────

def test_write_data_typ_creates_csv(tmp_path):
    threats = [
        {"ID": "T-001", "Title": "XSS", "Description": "...", "State": "Open", "Justification": "Pending"},
    ]
    dest = tmp_path / "threats.csv"
    _write_data_typ(threats, dest)
    assert dest.exists()
    content = dest.read_text()
    assert "T-001" in content
    assert "XSS" in content


def test_write_data_typ_empty_list_does_nothing(tmp_path):
    dest = tmp_path / "threats.csv"
    _write_data_typ([], dest)
    assert not dest.exists()


# ─── generate_report ──────────────────────────────────────────────────────────

SAMPLE_THREATS = [
    {
        "ID": "T-001",
        "Title": "SQL Injection",
        "Description": "Attacker injects SQL.",
        "State": "Open",
        "Justification": "No fix yet.",
    }
]


def test_generate_report_typst_not_found(tmp_path):
    with patch("shutil.which", return_value=None):
        with pytest.raises(TypstNotFoundError):
            generate_report(SAMPLE_THREATS, tmp_path / "out.pdf")


def test_generate_report_missing_template(tmp_path):
    with patch("shutil.which", return_value="/usr/bin/typst"):
        with pytest.raises(FileNotFoundError, match="template not found"):
            generate_report(
                SAMPLE_THREATS,
                tmp_path / "out.pdf",
                template=tmp_path / "nonexistent.typ",
            )


def test_generate_report_render_error(tmp_path):
    fake_template = tmp_path / "report.typ"
    fake_template.write_text("#let x = 1")

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "error: unknown variable: foo"

    with patch("shutil.which", return_value="/usr/bin/typst"):
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RenderError, match="Typst compilation failed"):
                generate_report(
                    SAMPLE_THREATS,
                    tmp_path / "out.pdf",
                    template=fake_template,
                )


def test_generate_report_success(tmp_path):
    fake_template = tmp_path / "report.typ"
    fake_template.write_text("#let x = 1")

    mock_result = MagicMock()
    mock_result.returncode = 0

    output_pdf = tmp_path / "out.pdf"

    with patch("shutil.which", return_value="/usr/bin/typst"):
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            generate_report(SAMPLE_THREATS, output_pdf, template=fake_template)

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[0] == "/usr/bin/typst"
    assert "compile" in args
    assert str(output_pdf.resolve()) in args

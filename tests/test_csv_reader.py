"""Unit tests for csv_reader module."""

from pathlib import Path

import pytest

from steris.csv_reader import (
    CSVValidationError,
    read_threats,
)

SAMPLE_CSV = Path(__file__).parent / "sample.csv"


def test_read_sample_csv_returns_threats():
    threats = read_threats(SAMPLE_CSV)
    assert len(threats) == 5


def test_required_fields_present():
    threats = read_threats(SAMPLE_CSV)
    for threat in threats:
        assert threat["ID"]
        assert threat["Title"]
        assert threat["State"]


def test_optional_fields_populated_when_present():
    threats = read_threats(SAMPLE_CSV)
    assert threats[0]["Category"] == "Injection"
    assert threats[0]["Interaction"] == "User submits login form"
    assert threats[0]["Source"] == "Browser"
    assert threats[0]["Target"] == "Database"


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        read_threats(Path("nonexistent.csv"))


def test_empty_file_raises(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    with pytest.raises(CSVValidationError, match="empty or has no header row"):
        read_threats(empty)


def test_missing_required_column_raises(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    # Missing "State" and "Justification"
    bad_csv.write_text("ID,Title,Description\n1,XSS,A cross-site scripting issue.\n")
    with pytest.raises(CSVValidationError, match="missing required column"):
        read_threats(bad_csv)


def test_no_data_rows_raises(tmp_path):
    header_only = tmp_path / "header_only.csv"
    header_only.write_text("ID,Title,Description,State,Justification,Category,Interaction,Source,Target\n")
    with pytest.raises(CSVValidationError, match="no threat rows"):
        read_threats(header_only)


def test_blank_rows_are_skipped(tmp_path):
    csv_with_blanks = tmp_path / "blanks.csv"
    csv_with_blanks.write_text(
        "ID,Title,Description,State,Justification,Category,Interaction,Source,Target\n"
        "T-001,XSS,Reflected XSS.,Open,No fix yet.,XSS,User searches,Browser,Web Server\n"
        ",,,,,,,, \n"
        "T-002,SQLI,SQL injection.,Mitigated,Parameterised queries.,Injection,User logs in,Browser,Database\n"
    )
    threats = read_threats(csv_with_blanks)
    assert len(threats) == 2


def test_bom_utf8_encoding(tmp_path):
    """Files saved by Excel often include a UTF-8 BOM."""
    bom_csv = tmp_path / "bom.csv"
    bom_csv.write_bytes(
        b"\xef\xbb\xbfID,Title,Description,State,Justification,Category,Interaction,Source,Target\r\n"
        b"T-001,Test,Desc,Open,Reason,Cat,Int,Src,Tgt\r\n"
    )
    threats = read_threats(bom_csv)
    assert threats[0]["ID"] == "T-001"

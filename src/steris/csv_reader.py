"""CSV ingestion and validation for threat modeling data."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TypedDict


REQUIRED_COLUMNS = {
    "Id",
    "Title",
    "Description",
    "State",
    "Justification",
    "Category",
    "Interaction",
    "Source",
    "Target",
}

class Threat(TypedDict, total=False):
    ID: str
    Title: str
    Description: str
    State: str
    Justification: str
    Category: str
    Interaction: str
    Source: str
    Target: str


class CSVValidationError(Exception):
    pass


def read_threats(csv_path: Path, delimiter: str) -> list[Threat]:
    """Parse a threat modeling CSV file and return a list of threat dicts.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        A list of threat dictionaries with at least the required columns populated.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        CSVValidationError: If required columns are missing or the file is empty.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        if reader.fieldnames is None:
            raise CSVValidationError("CSV file is empty or has no header row.")

        headers = set(reader.fieldnames)
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise CSVValidationError(
                f"CSV is missing required column(s): {', '.join(sorted(missing))}\n"
                f"Only the following columns were found:\n{', '.join(sorted(headers))}"
            )

        threats: list[Threat] = []
        for line_num, row in enumerate(reader, start=2):
            # Skip entirely blank rows (including whitespace-only cells)
            if not any(v.strip() for v in row.values()):
                continue

            threat: Threat = {
                col: (row.get(col) or "").strip()
                for col in REQUIRED_COLUMNS
                if col in headers
            }
            threats.append(threat)  # type: ignore[arg-type]

        if not threats:
            raise CSVValidationError("CSV contains no threat rows.")

    return threats

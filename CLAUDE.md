# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

STERIS generates PDF threat modeling reports from CSV files.

**Data flow:** CSV (threat data) → `csv_reader.py` → `generator.py` → Typst CLI subprocess → PDF

**External dependency:** [Typst CLI](https://github.com/typst/typst/releases) must be installed and on PATH.

## Commands

```bash
# Set up
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run
steris --input threats.csv --output output/report.pdf

# Test
pytest
pytest --cov=steris --cov-report=term-missing

# Run a single test
pytest tests/test_csv_reader.py::test_blank_rows_are_skipped
```

## Architecture

```
src/steris/
  csv_reader.py   — parses and validates the threat modeling CSV; raises CSVValidationError for bad input
  generator.py    — writes a temp CSV, invokes Typst CLI via subprocess, raises TypstNotFoundError / RenderError
  main.py         — argparse CLI; maps exit codes to error types (1=IO, 2=CSV, 3=Typst missing, 4=render)
templates/
  report.typ      — Typst template; receives `title` and `data` (path to threats CSV) as --input variables
tests/
  sample.csv      — realistic 5-row threat dataset used by integration tests
```

## Key Design Decisions

- **No third-party runtime dependencies** — stdlib only (`csv`, `subprocess`, `argparse`, `tempfile`). Keeps the install footprint minimal and avoids enterprise proxy/firewall issues.
- **Temp directory isolation** — the template and data CSV are copied into a `tempfile.TemporaryDirectory` before calling Typst, so relative Typst imports resolve correctly regardless of CWD.
- **UTF-8 BOM handling** — CSV is opened with `encoding="utf-8-sig"` to transparently handle files exported from Excel.
- **Exit codes** — distinct codes (1–4) let the tool be used reliably in scripts and CI pipelines.

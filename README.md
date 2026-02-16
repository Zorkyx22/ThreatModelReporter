# STERIS

Automatically generate PDF threat modeling reports from CSV files using [Typst](https://typst.app/).

## Requirements

- Python 3.10+
- [Typst CLI](https://github.com/typst/typst/releases) — install and ensure `typst` is on your PATH

## Installation

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -e ".[dev]"
```

## Usage

```bash
steris --input threats.csv --output output/report.pdf
```

| Option | Description |
|---|---|
| `-i / --input` | Path to the threat modeling CSV file (required) |
| `-o / --output` | Destination PDF path (default: `output/report.pdf`) |
| `--title` | Report title (default: `Threat Modeling Report`) |
| `--template` | Path to a custom `.typ` template file |
| `--typst-bin` | Explicit path to the Typst binary if not on PATH |

## CSV Format

The input CSV must have these columns (additional columns are passed through):

| Column | Required | Description |
|---|---|---|
| `ID` | Yes | Unique threat identifier (e.g. `T-001`) |
| `Title` | Yes | Short threat name |
| `Description` | Yes | Full threat description |
| `State` | Yes | `Open`, `Mitigated`, `Accepted`, or `Transferred` |
| `Justification` | Yes | Reasoning for the current state |
| `Category` | No | Threat category (e.g. `Injection`) |
| `Interaction` | No | The interaction that exposes the threat |
| `Source` | No | Origin of the interaction (e.g. `Browser`) |
| `Target` | No | Destination of the interaction (e.g. `Database`) |

A sample CSV is provided at `tests/sample.csv`.

## Running Tests

```bash
pytest
# With coverage:
pytest --cov=steris --cov-report=term-missing
```

## Customising the Template

The default Typst template is at `templates/report.typ`. You can edit it directly or supply your own via `--template`. It receives two Typst input variables:

- `title` — the report title string
- `data` — absolute path to the threats CSV (written to a temp directory at render time)

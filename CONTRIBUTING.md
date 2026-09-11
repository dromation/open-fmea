# Contributing to Open FMEA

Thank you for considering a contribution to Open FMEA.

Open FMEA is a local-first Django application for Failure Modes and Effects Analysis workflows. Contributions should keep the project portable, reviewable, and useful for real FMEA work.

## Ways to Contribute

- Report bugs with clear reproduction steps.
- Suggest workflow improvements for FMEA, workbook import, risk review, or cause analysis.
- Improve documentation, tests, packaging, or accessibility.
- Submit focused pull requests that solve one problem at a time.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Checks Before a Pull Request

Run these before opening a pull request:

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## Contribution Guidelines

- Keep changes scoped and easy to review.
- Do not commit local databases, generated build output, virtual environments, or uploaded files.
- Keep the framework-free domain layer independent from Django imports.
- Add or update tests when behavior changes.
- Prefer stable IDs and portable exchange data over database-specific IDs.
- Keep sample data non-sensitive and suitable for public repositories.

## Pull Request Description

Please include:

- What changed.
- Why it changed.
- How it was tested.
- Any known limitations or follow-up work.


# Open FMEA

Open FMEA is being rebuilt as a domain-first Django application for Failure Modes and Effects Analysis. The current development line keeps the legacy Tkinter prototype for reference, while new work starts from portable Python domain objects and thin Django persistence.

## Repository Layout

```text
architecture/                 Architecture reports, ADRs, and future specs
django_app/                   Django project and application packages
domain/fmea_domain/           Framework-free Open-FMEA domain model and rules
docs/exchange-format/         Open-FMEA Exchange Format documentation and schema
legacy/tkinter-prototype/     Frozen Tkinter/SQLite prototype from beta-v01
tests/                        Domain and portability tests
```

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run Checks

```powershell
python -m unittest discover -s tests
python manage.py check
```

## Run the Django PoC

```powershell
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Legacy Prototype

The previous Tkinter/PyInstaller prototype is preserved under `legacy/tkinter-prototype/`. It is a historical reference and seed-data source, not the active architecture for new feature work.

## Architecture

The starting architecture report is stored at `architecture/OpenFMEA_Architecture_and_Portability_Report.md`. The first ratified implementation decision is `architecture/adr/ADR-0000-adopt-django-poc-and-freeze-legacy.md`.

## License

This project is licensed under the GPL 3.0 License. See `LICENSE` for details.

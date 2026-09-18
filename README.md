> **Canonical HTML application:** open [`open_fmea.html`](open_fmea.html) directly in your browser. This standalone runtime requires no Python, Node, Django, server or database. Portable data is in [`open_fmea.container`](open_fmea.container). See [single HTML architecture and usage](architecture/open_fmea_runtime.md). Historical HTML versions are preserved under `history/`; the existing backend documentation below is retained for that separate codebase.

<p align="center">
  <img src="django_app/fmea_app/static/fmea_app/img/logo.png" alt="Open FMEA logo" width="96">
</p>

# Open FMEA

Open FMEA is a local-first Django application for building, reviewing, and maintaining Failure Modes and Effects Analysis records. The current app combines a portable Python domain layer with Django persistence, workbook ingestion, review queues, risk evaluation, Ishikawa cause analysis, and focused FMEA workflow screens.

## Available editions in this migration

- **Standalone HTML:** open `open_fmea.html`; portable data is in `open_fmea.container`.
- **Django application:** application packages in `django_app/` and portable rules in `domain/`.
- **SharePoint Online demo:** see [installation instructions](open_fmea_sharepoint_version/INSTALLATION.md) and the [installable package](open_fmea_sharepoint_version/sharepoint/solution/open-fmea-sharepoint.sppkg). This edition currently uses personal browser storage.
- **Architecture, tests, and history:** development documentation, test fixtures, and historical sources are included in this migration snapshot. Earlier public-release packaging notes below describe that earlier release scope.

See [GitLab migration notes](docs/GITLAB_IMPORT.md).

## Repository Layout

```text
django_app/                   Django project and application packages
domain/fmea_domain/           Framework-free Open-FMEA domain model and rules
docs/exchange-format/         Open-FMEA Exchange Format documentation and schema
samples/open_fmea/            Workbook fixtures used by ingestion tests
tests/                        Domain and portability tests
```

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the App

```powershell
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Run Checks

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## Current App Surface

- FMEA workspace dashboard
- FMEA projects and team roster
- DFMEA/PFMEA worksheet views
- Product and process characteristics
- Functions, failure modes, effects, causes, controls, and actions
- Risk matrix and risk trajectory views
- Ishikawa cause influence review
- Workbook import and row-level review

## Packaging Notes

The application is designed to run locally from the Django project today. The historical prototype and architecture working notes are intentionally not part of the public app release branch.

For a fresh local database, run `python manage.py migrate` and `python manage.py seed_demo` before starting the server.

## License

This project is licensed under the GPL 3.0 License. See `LICENSE` for details.

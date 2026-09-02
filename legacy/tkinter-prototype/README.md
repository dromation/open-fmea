# Legacy Tkinter Prototype

This directory preserves the previous Open-FMEA Tkinter/SQLite prototype from the `beta-v01` line.

It is kept for:

- historical reference;
- comparison against the new Django implementation;
- candidate seed data under `contents/`, `tables/`, and the SQLite files.

It is not the active architecture for new feature work.

## Run Legacy Prototype

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python fmea_app.py
```

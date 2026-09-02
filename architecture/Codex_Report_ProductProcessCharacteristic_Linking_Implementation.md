# Codex Report — ProductCharacteristic, ProcessCharacteristic, and Characteristics Linking

Date: 2026-09-01
Repositories:

- `D:\Dromation\org\apps\open_fmea`
- `D:\Dromation\org\apps\open_fmea_training_set`

## Verdict

Implemented, mirrored to the training set, and verified in both repository locations.

## Implemented

- Renamed `fmea_app.Characteristic` to `fmea_app.ProductCharacteristic` with a Django `RenameModel` migration.
- Added nullable, dormant `ProductCharacteristic.primary_classification_id`.
- Added `ProcessCharacteristic` as an instance-level entity tied to one `Operation`.
- Added `ProcessCharacteristic.cause_category_id` and flexible JSON `attributes`.
- Widened `CauseInfluence.source_type` with `ProcessCharacteristic`.
- Widened `CauseInfluence.target_type` with `ProductCharacteristic`.
- Updated ingestion candidate types and header mapping from `Characteristic` to `ProductCharacteristic`.
- Added a `fmea_review` data migration for old `ImportCandidateRecord.suggested_domain_type = "Characteristic"` rows and old row-group detected-field keys.
- Updated OFEF import/export for `ProductCharacteristic` and `ProcessCharacteristic`.
- Added process-characteristic GUI endpoints:
  - `/process-characteristics/`
  - `/process-characteristics/new/`
  - `/process-characteristics/<stable_id>/`
- Updated the FMEA worksheet GUI to show product characteristics.
- Updated demo seed data with one process characteristic.

## Deliberate Boundary Call

The implementation does not add `ProductCharacteristic` as a `CauseInfluence.source_type`.

The instruction's exact allowed-set only widened sources with `ProcessCharacteristic` and targets with `ProductCharacteristic`. A later sentence described a direct `ProductCharacteristic -> FailureMode` second edge, which would require another source-type widening not present in the allowed-set. To avoid silently expanding scope, this slice implements the approved allowed-set exactly:

```text
ProcessCharacteristic -> ProductCharacteristic
ProductCharacteristic -> Requirement -> FailureMode
```

That preserves the current object chain without adding an unapproved `ProductCharacteristic` source type.

## Existing Data Backfill Counts

Checked before applying the new migrations:

```text
D:\Dromation\org\apps\open_fmea\db.sqlite3
old ImportCandidateRecord rows: 0
old FmeaRowGroup detected-field keys: 0

D:\Dromation\org\apps\open_fmea_training_set\db.sqlite3
old ImportCandidateRecord rows: 0
old FmeaRowGroup detected-field keys: 0
```

The migration still exists and will backfill any older database where those rows are present.

## Main Repo Verification

Executed in `D:\Dromation\org\apps\open_fmea`:

```text
python -B -m pytest
80 passed

python manage.py check
System check identified no issues

python manage.py makemigrations --check --dry-run --no-input
No changes detected
```

Real workbook count verification:

```text
FMEA_templates.xlsx              1904 candidates, old type absent, ProductCharacteristic present
FMEA_442710252570.00.xlsx         316 candidates, old type absent, ProductCharacteristic present
PPAP_Prirobnica.XX2.xlsx          198 candidates, old type absent
```

The PPAP sample has no product-characteristic header in the currently mapped table, so no `ProductCharacteristic` candidate is expected there.

## Training Set Verification

Mirrored source from `D:\Dromation\org\apps\open_fmea` to `D:\Dromation\org\apps\open_fmea_training_set`, preserving the training-only packaging directory and existing local runtime data. The training database was migrated in place.

Executed in `D:\Dromation\org\apps\open_fmea_training_set`:

```text
python manage.py migrate --noinput
fmea_app.0003_rename_characteristic_to_productcharacteristic OK
fmea_app.0004_processcharacteristic_and_widen_causeinfluence OK
fmea_review.0003_backfill_product_characteristic_candidate_type OK

python -B -m pytest
80 passed

python manage.py check
System check identified no issues

python manage.py makemigrations --check --dry-run --no-input
No changes detected
```

Real workbook count verification:

```text
FMEA_templates.xlsx              1904 candidates, old type absent, ProductCharacteristic present
FMEA_442710252570.00.xlsx         316 candidates, old type absent, ProductCharacteristic present
PPAP_Prirobnica.XX2.xlsx          198 candidates, old type absent
```

Backfill verification after migration:

```text
old ImportCandidateRecord rows: 0
old FmeaRowGroup detected-field keys: 0
```

Source parity verification:

```text
domain/django_app/tests/docs: byte-identical for every source file present in open_fmea
architecture: byte-identical for every source file present in open_fmea
docs/exchange-format/demo.ofef.json: byte-identical, LF-only
```

The training set still contains one training-only historical architecture report not present in the main repo; it was intentionally preserved and not treated as drift.

## Training EXE Verification

Built with `D:\Dromation\org\apps\open_fmea_training_set\packaging\build_exe.ps1`.

The build script itself completed:

```text
pip install dependencies OK
python -m pytest: 80 passed
python manage.py check: no issues
python manage.py makemigrations --check --dry-run --no-input: no changes
PyInstaller build completed
```

Started:

```text
D:\Dromation\org\apps\open_fmea_training_set\dist\OpenFMEA-Training\OpenFMEA-Training.exe
PID: 5740
URL: http://127.0.0.1:8765/
```

HTTP smoke checks passed with status 200:

```text
/
/process-characteristics/
/process-characteristics/demo:process-characteristic:installation-force/
/cause-influences/new/?source_type=ProcessCharacteristic&source_id=demo%3Aprocess-characteristic%3Ainstallation-force
/fmea/demo:fmea:brake-assembly-process/
```

Content checks also passed: `Seal installation force`, `Known Product Characteristics`, `Seal seat surface condition`, `Preselected Source`, and the FMEA `Product Characteristics` column all render from the EXE.

## Still Deferred

- `ClassificationScheme` / `ClassificationTerm`
- product-characteristic classification assignment UI
- process-characteristic reusable library
- category inheritance from `ProcessCharacteristic` to `CauseInfluence`
- AI wiring for `classify_ishikawa_category`
- visual fishbone diagram
- coverage metrics
- lessons learned
- Control Plan hooks

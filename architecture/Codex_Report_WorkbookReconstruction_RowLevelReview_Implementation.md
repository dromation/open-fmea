# Codex Report: Workbook Reconstruction and Row-Level Review Implementation

Date: 2026-08-31

## Scope Implemented

Implemented the approved workbook-reconstruction slice on top of the existing OOXML `.xlsx/.xlsm` ingestion layer.

The parser still extracts source cells first. A new transient reconstruction layer groups parsed cells by workbook, sheet, and source row into logical FMEA rows. Only the review boundary is persisted:

- `fmea_ingestion.reconstruction.FmeaRowCandidate` is transient and framework-free.
- `fmea_review.FmeaRowGroup` is persistent and stores the row-group review object.
- `ImportCandidateRecord.row_group` links every candidate cell back to its reconstructed row when a row is detected.

The row grouping threshold is intentionally conservative: a row must include a mapped `FailureMode` and at least one other mapped Open-FMEA field. Rows that do not meet that threshold remain available in the cell-level candidate queue.

## GUI Boundary

The GUI now keeps both views:

- `/review/session/<stable_id>/` shows `Detected FMEA Rows` above the existing `Cell Candidates` table.
- `/review/row/<stable_id>/` shows the reconstructed row, detected fields, source cells, and row-level `Accept Row` / `Reject Row` actions.
- `/review/candidate/<stable_id>/` still supports the original cell-level accept/reject/modify/link/merge workflow.

This gives the operator a fast row-level review path while preserving detailed per-cell correction and provenance.

## Backend Boundary

`Accept Row` uses the same approved construction service path as cell-level acceptance:

`fmea_review.services.accept_row_group` -> `fmea_app.services.promote_import_candidate_to_domain_object`

The service creates a logical chain when enough context exists:

`Function` -> `Requirement` -> `FailureMode` -> `FailureEffect` / `FailureCause` -> `PreventionControl` / `DetectionControl`

Unmapped cells attached to an accepted row are not silently dropped. They are marked `needs_clarification` and remain traceable to the same row group.

## AI and Training Boundary

No AI model was trained or expanded in this slice.

Current active AI behavior remains:

- `DisabledProvider` is the default.
- `OllamaProvider.extract_structured_data` is the only real optional AI call.
- Characteristic classification, Ishikawa/5M+E classification, relationship suggestion, retrieval, and summarization remain contract-only/unavailable.

Where AI is needed later:

- header/cell classification for ambiguous workbook columns,
- Product vs Process Characteristic classification,
- 5M+E/Ishikawa cause categorization,
- candidate relationship suggestions across rows,
- similarity retrieval from prior accepted FMEA rows.

Where training/prompt corpus data now flows:

`OOXML workbook` -> `ImportCandidateRecord` -> optional `FmeaRowGroup` -> human review decision -> `export_ai_corpus`

The AI corpus export now includes `row_group_stable_id` and `source_range`, so future prompts can use row context without losing source-cell provenance.

## Explicitly Not Implemented

- no VBA/XLM macro execution,
- no persistent workbook/table/range object graph beyond `FmeaRowGroup`,
- no S/O/D rating import,
- no ProductCharacteristic/ProcessCharacteristic split,
- no AI classification activation,
- no automatic approval.

## Verification

Main repo `D:\Dromation\org\apps\open_fmea`:

- `pytest`: 38 passed
- `python manage.py check`: OK
- `python manage.py makemigrations --check --dry-run`: no changes detected

Training repo `D:\Dromation\org\apps\open_fmea_training_set`:

- `pytest`: 38 passed
- `python manage.py check`: OK
- `python manage.py makemigrations --check --dry-run`: no changes detected
- `packaging\build_exe.ps1`: EXE build succeeded
- EXE started at `http://127.0.0.1:8765/`
- Runtime smoke test uploaded `sample_fmea_minimal.xlsx`, displayed 3 row groups, accepted the first row, created `Seal leaks` as a `FailureMode`, marked 7 cells accepted and 1 cell `needs_clarification`.

Real workbook reconstruction in main repo:

- `FMEA_templates.xlsx`: 1904 candidates, 132 row groups
- `FMEA_442710252570.00.xlsx`: 316 candidates, 22 row groups
- `PPAP_Prirobnica.XX2.xlsx`: 198 candidates, 15 row groups

## Result

The approved workbook-reconstruction slice is implemented and verified. The application now has a functional row-level FMEA review path without losing the existing cell-level review safety net.

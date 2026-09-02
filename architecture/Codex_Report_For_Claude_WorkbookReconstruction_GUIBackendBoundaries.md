# Codex Report for Claude — Workbook Reconstruction, GUI and Backend Boundaries

Status: implementation handoff and architecture-review input.

Author: Codex.

Date: 2026-08-31.

Repository: `D:\Dromation\org\apps\open_fmea`

Training/sandbox copy: `D:\Dromation\org\apps\open_fmea_training_set`

## 1. Instruction Boundary

This report distinguishes prior document text from the active user request.

The earlier architecture document `OpenFMEA_SampleData_Findings_IngestionRobustness_AICorpusPlan.md` contained a local document instruction saying not to implement until reviewed. That was treated as project context, not as an overriding instruction. The active user instruction in this thread was to continue implementation in the main `open_fmea` folder, with `open_fmea_training_set` used as the test/sandbox copy.

No GitHub push was performed.

## 2. Current Working Model

The application now has three relevant layers:

1. Pure domain layer under `domain/fmea_domain`.
2. Django persistence/GUI layer under `django_app/fmea_app` and `django_app/fmea_review`.
3. Ingestion/AI boundary layer under `django_app/fmea_ingestion` and `django_app/fmea_ai`.

The key practical boundary is:

- Excel/OOXML import is not allowed to write accepted FMEA domain objects directly.
- Imported workbook content becomes review candidates first.
- Human review still gates object creation through `fmea_app.services.promote_import_candidate_to_domain_object`.
- AI can assist extraction only; it is not authoritative.

## 3. Implemented Backend Objects

Current Django/domain object surface includes:

- `FMEAProject`
- `FMEA`
- `Product`
- `Process`
- `Operation`
- `Function`
- `Requirement`
- `Characteristic`
- `FailureMode`
- `FailureEffect`
- `FailureCause`
- `FailureMechanism`
- `PreventionControl`
- `DetectionControl`
- `MeasurementMethod`
- `ResponsibleRole`
- `RecommendedAction`
- `Evidence`
- `EffectivenessVerification`
- `EvaluationDefinition`
- `RiskEvaluation`
- `FMEARevision`
- `DomainRelationship`

The existing GUI and import workflow do not yet expose all of these equally. The currently functional user-facing path is centered on FMEA, failure modes, effects, causes, prevention/detection controls, and risk evaluation.

## 4. Recent Implementation: Robust OOXML Workbook Ingestion

The parser in `django_app/fmea_ingestion/parsers/xlsx.py` was changed from a simple XLSX row scanner to an OOXML-aware workbook parser.

Implemented behavior:

- Supports `.xlsx` and `.xlsm`.
- Opens `.xlsm` as workbook structure only.
- Does not execute VBA, XLM, or macro code.
- Uses formal Excel Table metadata first when a worksheet contains table objects.
- Falls back to worksheet scanning when no formal table metadata exists.
- Scores candidate header rows by mapped Open-FMEA domain columns.
- Skips cover-sheet metadata rows such as `Item`, `PFMEA Number`, `Prepared by`.
- Scans the first 80 rows rather than stopping at the first row with two non-empty cells.
- Merges two-row AIAG-style headers, for example `Current Process` + `Controls Detection`.
- Expands merged cells from their top-left value before header detection and row extraction.
- Treats numeric and spreadsheet-error header cells as blank so helper/formula areas do not enter the review queue as fake columns.
- Isolates worksheets: one non-FMEA or picture/helper sheet no longer aborts the whole workbook.

Parser provenance version is now `ooxml-v1`.

## 5. Real Workbook Results After Fix

The parser was run against the real sample files in `samples/open_fmea`.

Before the robustness fix:

- `FMEA_templates.xlsx` -> 171 candidates, 171 unmapped, 100% unmapped.
- `FMEA_442710252570.00.xlsx` -> 84 candidates, 84 unmapped, 100% unmapped.
- `PPAP_Prirobnica.XX2.xlsx` -> failed with `AmbiguousWorkbookError`.

After the OOXML/merged-cell fix:

| Workbook | Result |
| --- | --- |
| `FMEA_templates.xlsx` | 1904 candidates |
| `FMEA_442710252570.00.xlsx` | 316 candidates |
| `PPAP_Prirobnica.XX2.xlsx` | 198 candidates from the `FMEA` sheet |

Observed mapped type counts:

`FMEA_templates.xlsx`

- `Characteristic`: 132
- `DetectionControl`: 132
- `FailureCause`: 132
- `FailureEffect`: 132
- `FailureMode`: 132
- `Function`: 132
- `PreventionControl`: 132
- `unmapped`: 980

`FMEA_442710252570.00.xlsx`

- `Characteristic`: 22
- `DetectionControl`: 22
- `FailureCause`: 22
- `FailureEffect`: 22
- `FailureMode`: 22
- `Function`: 22
- `PreventionControl`: 22
- `unmapped`: 162

`PPAP_Prirobnica.XX2.xlsx`

- `DetectionControl`: 15
- `FailureCause`: 15
- `FailureEffect`: 15
- `FailureMode`: 15
- `Function`: 15
- `unmapped`: 123

The high `unmapped` count is expected for this slice because ratings, RPN, CTQ, classification, action status, responsibility, dates, and helper/calculation columns are not yet modeled as full row-level FMEA structures during import.

## 6. Characteristic Import Change

`Characteristic` is now a valid import candidate type.

Reason: the existing domain and Django model already include `Characteristic`, and real workbook headers contain `Product Characteristics ID/Description` / `Characteristics`.

Implemented:

- Added `Characteristic` to `VALID_DOMAIN_TYPES`.
- Added it to the structured extraction schema enum.
- Added header mappings for real workbook characteristic columns.
- Added promotion through `fmea_app.services.promote_import_candidate_to_domain_object`.
- `requirement_stable_id` is optional because the current Django model allows `Characteristic.requirement = null`.
- Review candidate UI accepts optional `requirement_stable_id`.

This is not the same as the larger Product/Process Characteristic taxonomy from earlier architecture discussions. No classification schemes or special-characteristic libraries were introduced in this change.

## 7. Current GUI Boundary

The GUI should not be treated as a raw spreadsheet renderer.

Current GUI surfaces:

- Dashboard with FMEA list and quick creation forms.
- FMEA detail page with both:
  - a worksheet-style FMEA table, and
  - detailed panels/forms for failure modes, effects, causes, controls, and risk evaluations.
- Import review queue:
  - upload `.xlsx` / `.xlsm`
  - session list
  - candidate list
  - candidate detail
  - Accept
  - Modify
  - Reject
  - Link Existing
  - Merge
- Django admin for low-level inspection.

Current FMEA worksheet table boundary:

- Shows `Function`
- Shows `Requirement`
- Shows `Failure Mode`
- Shows `Effects`
- Shows `Cause`
- Shows `Prevention Controls`
- Shows `Detection Controls`
- Shows `S`
- Shows `O`
- Shows `D`
- Shows calculated risk result

Missing for a functional FMEA-grade GUI:

- Row-group reconstruction from imported workbooks.
- One review action per logical FMEA row, not one action per cell.
- Rating import for `S/O/D`, `Po/S/Pd`, `RPN`.
- Action columns: recommended action, planned action, responsible, due/follow-up date, verification/signoff.
- Classification columns: classification, CTQ, special characteristic.
- Process step/operation hierarchy reconstruction.
- Workbook preview showing which sheet/range/table was detected before candidate creation.
- Better linkage UI using selectable objects rather than manual stable-id inputs.

## 8. AI State

AI is present as a provider-neutral boundary, not as an active decision maker.

Implemented provider contract methods:

- `extract_structured_data`
- `classify_characteristic`
- `classify_ishikawa_category`
- `suggest_relationships`
- `retrieve_similar_cases`
- `summarize_evidence`

Current reality:

- `DisabledProvider` implements all methods as `unavailable`.
- `OllamaProvider` only implements `extract_structured_data`.
- All other Ollama methods return `unavailable`.
- AI is off by default.
- AI output is schema-validated.
- AI cannot bypass human review.

AI corpus export was added:

```powershell
python manage.py export_ai_corpus exports/ai-corpus.jsonl
```

Default export includes accepted and modified review candidates. It is intended for prompt context / few-shot examples, not model training. It does not yet feed back into `OllamaProvider`.

## 9. Backend Commands

Current useful management commands:

- `seed_demo`
- `export_ofef`
- `export_ai_corpus`

Current command boundary:

- `export_ofef` exports accepted domain objects.
- `export_ai_corpus` exports reviewed import decisions for future prompt context.
- There is not yet a command that reconstructs a workbook into a logical FMEA row model.

## 10. Test and Runtime Verification

Original repository verification:

- `python -B -m pytest` -> 34 passed
- `python -B manage.py check` -> OK
- `python -B manage.py makemigrations --check --dry-run --no-input` -> no changes detected

Training set verification:

- `python -B -m pytest` -> 34 passed
- `python -B manage.py check` -> OK
- `python -B manage.py makemigrations --check --dry-run --no-input` -> no changes detected
- real workbook diagnostic produced the same candidate counts as original

Training EXE:

- rebuilt successfully
- path: `D:\Dromation\org\apps\open_fmea_training_set\dist\OpenFMEA-Training\OpenFMEA-Training.exe`
- running on `http://127.0.0.1:8765/`
- `/` returned HTTP 200
- `/review/` returned HTTP 200
- upload HTML accepts `.xlsx,.xlsm`

## 11. Architectural Gap: Workbook Reconstruction Layer

The current parser still outputs cell-level candidates. That is useful for traceability but not sufficient for a good FMEA application.

Recommended next architecture slice:

Create a workbook reconstruction layer between OOXML parsing and review queue.

Suggested internal model:

- `WorkbookStructure`
- `WorksheetStructure`
- `DetectedTable`
- `HeaderBand`
- `ColumnRole`
- `RowGroup`
- `FmeaRowCandidate`
- `CellProvenance`

The purpose is to reconstruct logical FMEA rows before creating review records.

This layer should understand:

- formal Excel tables
- merged header bands
- merged body cells
- repeated values carried by merged cells
- hidden/helper/calculation areas
- sheet-level role detection
- named ranges where they identify FMEA regions
- rating columns
- action-result blocks
- classification/CTQ columns

The output should be a logical FMEA row candidate with nested fields, for example:

- function
- requirement
- characteristic
- failure_mode
- effects
- causes
- prevention_controls
- detection_controls
- severity
- occurrence
- detection
- rpn/action_priority
- recommended_actions
- responsible
- due/follow_up_date
- classification/ctq
- provenance for every source cell

## 12. Claude Review Questions

Please review and decide:

1. Should the next approved slice introduce a persistent `WorkbookImportStructure` / `FmeaRowCandidate` model, or keep reconstruction transient and only persist `ImportCandidateRecord` rows?
2. Should review move from cell-level approval to row-level approval first, while retaining cell-level provenance underneath?
3. Should rating cells become first-class import targets now, or wait until row-level reconstruction is implemented?
4. Should `Characteristic` remain a generic existing entity for now, or should Product/Process Characteristic separation be introduced before further import work?
5. Should `Classification`, `CTQ`, and special-characteristic schemes be implemented before AI characteristic classification is activated?
6. Should named ranges from legacy `.xlsm`/OOXML files be used as hard hints for table detection, or only as diagnostic metadata until we have more real files?
7. Should `export_ai_corpus` be wired into `OllamaProvider.extract_structured_data` as optional few-shot context in the next AI slice?

## 13. Recommended Next Slice

Recommendation: build workbook reconstruction before adding more AI.

Rationale:

- AI cannot reliably classify content if the app still thinks in isolated cells.
- The GUI needs logical FMEA rows to behave like a real FMEA tool.
- Rating/action/classification fields depend on row context.
- Review ergonomics improve dramatically when users approve or correct one logical FMEA row instead of many independent cells.

Minimal next slice:

1. Add transient reconstruction classes in `fmea_ingestion`.
2. Convert OOXML parser output into `FmeaRowCandidate` objects.
3. Preserve per-cell provenance.
4. Add tests using current real workbook shapes replicated as synthetic fixtures.
5. Add a review preview page that shows detected sheet/range and reconstructed rows before import-session creation.
6. Keep the existing cell-level `ImportCandidateRecord` path available for fallback.

Do not execute macros. Use OOXML structure, workbook metadata, named ranges, tables, merged cells, and explicit user review.

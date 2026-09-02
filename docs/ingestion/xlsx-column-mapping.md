# OOXML Workbook Column Mapping

Open-FMEA slice 1 imports `.xlsx` and `.xlsm` OOXML workbooks into review candidates. The upload step never writes directly to accepted FMEA objects; every parsed cell becomes an `ImportCandidateRecord` with source provenance and starts in `UNREVIEWED`.

Macro-enabled `.xlsm` files are read as workbook structure only. The parser does not execute or trust VBA/XLM macro code.

## Default Header Mapping

| Header variants | Suggested domain type |
| --- | --- |
| `Function`, `Product Function`, `Process Function`, `Item Function`, AIAG/VDA process-function variants such as `Process Function/ Requirment`, PPAP `Function / Part / Operation` | `Function` |
| `Requirement`, `Requirements`, `Specification`, `Requirement Specification` | `Requirement` |
| `Product Characteristics ID/Description`, `Characteristics` | `ProductCharacteristic` |
| `Failure Mode`, `Potential Failure Mode`, `Failure` | `FailureMode` |
| `Effect`, `Failure Effect`, `Potential Effect`, `Potential Effects`, `Potential Effect(s) of Failure`, `Effects of Failure`, PPAP undesirable-customer-effect variants | `FailureEffect` |
| `Cause`, `Failure Cause`, `Potential Cause`, `Potential Cause(s) of Failure`, `Causes of failure` | `FailureCause` |
| `Prevention Control`, `Prevention Controls`, `Current Prevention Control`, `Current Prevention Controls`, `Controls Prevention`, `Current Process Controls Prevention`, `Current Design Controls Prevention` | `PreventionControl` |
| `Detection Control`, `Detection Controls`, `Current Detection Control`, `Current Detection Controls`, `Controls Detection`, `Current Process Controls Detection`, `Current Design Controls Detection`, `Testing - Simulation` | `DetectionControl` |

Header matching is case-insensitive and normalizes whitespace, punctuation, underscores, hyphens, and slashes. Unknown headers are not dropped. Their cells are imported as `suggested_domain_type = "unmapped"` and carry a validation issue for human review.

When a worksheet contains formal Excel Table metadata, those table ranges are parsed before the loose worksheet scan. If a workbook has no formal tables, the parser scans the first 80 rows of each worksheet and chooses the strongest FMEA table header by mapped-domain score, not the first row with two non-empty cells. This lets it skip cover-sheet metadata such as `Item`, `PFMEA Number`, and `Prepared by`.

Merged cells are expanded from their top-left cell before header detection and row extraction. When an AIAG-style header uses a main header row plus a sub-header row, the parser merges them for controls, for example `Current Process` + `Controls Detection` becomes `Current Process Controls Detection`.

Non-tabular worksheets inside multi-sheet PPAP packages are skipped instead of aborting the whole workbook. Numeric or spreadsheet-error cells found in a header row are treated as blank headers so formula/helper areas do not flood the review queue.

## Provenance

Each candidate records the workbook name, SHA-256 document version, sheet name, row number, column name, extraction method, and parser version. Candidate `stable_id` values are deterministic from the document hash, sheet, row, column, and extracted value.

## Workbook Row Reconstruction

After cell extraction, the ingestion layer reconstructs lightweight logical FMEA rows from candidates that share the same workbook, sheet, and source row. Reconstruction is intentionally transient: the parser does not persist worksheet tables, merged ranges, or workbook internals as domain objects.

Only one row-level review object is persisted:

- `FmeaRowGroup` stores the import session, stable row-group ID, sheet, source row range, parser version, detected mapped fields, review status, and accepted object IDs.
- `ImportCandidateRecord.row_group` links each source cell back to its reconstructed logical row.
- Unmapped source cells remain attached to the row group and keep their original provenance.

A row is reconstructable when it contains a mapped `FailureMode` and at least one other mapped Open-FMEA field. Rows that do not meet this threshold remain available in the cell-level candidate list.

## Review Workflow

The review queue is available under `/review/`.

- `Accept` promotes one reviewed candidate into an existing `fmea_app` model through `fmea_app.services.promote_import_candidate_to_domain_object`.
- `Reject` records the rejection without creating a domain object.
- `Modify` edits the candidate value/type first, then follows the same acceptance path.
- `Link Existing` records an existing Open-FMEA object stable ID.
- `Merge` marks a candidate as a duplicate of another candidate in the same import session.
- `Accept Row` promotes one reconstructed FMEA row through the same construction service path, creating a Function/Requirement/FailureMode/Effect/Cause/Control chain where enough parent context exists.
- `Reject Row` rejects the row group and all cell candidates attached to that row group.

The GUI shows both levels: Detected FMEA Rows for row-level review and Cell Candidates as the fallback for detailed correction.

Some domain types require parent context because the existing Django model requires it:

| Suggested domain type | Required context |
| --- | --- |
| `Requirement` | `function_stable_id` |
| `ProductCharacteristic` | optional `requirement_stable_id` |
| `ProcessCharacteristic` | `operation_stable_id` |
| `FailureMode` | `fmea_stable_id` |
| `FailureEffect` | `failure_mode_stable_id` |
| `FailureCause` | `failure_mode_stable_id` |
| `PreventionControl` | `failure_cause_stable_id` |
| `DetectionControl` | `failure_cause_stable_id` |

## Local AI / Ollama

AI enrichment is off by default. Configuration is read from Django settings and environment:

```powershell
$env:OPEN_FMEA_AI_ENABLED = "1"
$env:OPEN_FMEA_OLLAMA_ENDPOINT = "http://127.0.0.1:11434"
$env:OPEN_FMEA_OLLAMA_MODEL = "your-local-model"
$env:OPEN_FMEA_OLLAMA_TIMEOUT_SECONDS = "30"
```

When AI is disabled, unavailable, or returns invalid structured output, deterministic mapping is kept and the import still proceeds. In this slice only `extract_structured_data` is wired as optional enrichment.

`classify_characteristic`, `classify_ishikawa_category`, relationship suggestions, retrieval, and RAG remain contract-only stubs returning `unavailable`. The reason is documented in `architecture/OpenFMEA_LocalAI_Ingestion_ArchitectureReview.md` and `architecture/OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md`: configurable product-characteristic classification and AI category assignment are separate implementation slices.

## AI Corpus Export

Reviewed import candidates can be exported as deterministic JSONL examples for future prompt context:

```powershell
python manage.py export_ai_corpus exports/ai-corpus.jsonl
```

The default export includes `accepted` and `modified` candidates. Add `--include-rejected`, `--include-duplicates`, or `--include-unreviewed` only when building diagnostic corpora. This export does not train a model and does not bypass human review; it serializes review decisions so future prompt construction can use real workbook phrasing and corrected domain labels.

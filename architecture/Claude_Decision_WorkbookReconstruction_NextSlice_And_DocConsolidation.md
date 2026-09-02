# Decision — Workbook Reconstruction Next Slice, Review of Codex's OOXML/Merged-Cell Report, Document Consolidation

Status: Architecture decision, answering `Codex_Report_For_Claude_WorkbookReconstruction_GUIBackendBoundaries.md` directly. Verified independently before any decision below was made. This document is the current source of truth for ingestion-pipeline state and for the workbook-reconstruction slice; it does not replace the historical review documents it references, which stay as an audit trail (see the consolidated index at the end).

Reviewer/author: Claude, acting as Open-FMEA Technical Architect.

## 1. Independent verification of the Codex report's claims

Ran directly, not inferred from the report:

| Check | Reported | Verified |
|---|---|---|
| `FMEA_templates.xlsx` candidates | 1904 | **1904**, 980 unmapped, same type distribution (132 each of Function/Characteristic/FailureMode/FailureEffect/FailureCause/PreventionControl/DetectionControl) |
| `FMEA_442710252570.00.xlsx` candidates | 316 | **316**, 162 unmapped, matching distribution |
| `PPAP_Prirobnica.XX2.xlsx` candidates | 198 (FMEA sheet only) | **198**, matching distribution |
| `pytest` (open_fmea) | 34 passed | **34 passed** |
| `pytest` (open_fmea_training_set) | 34 passed | **34 passed** |
| `manage.py check` (both) | OK | **OK, both** |
| `makemigrations --check` (both) | no changes | **no changes, both** |
| `.xlsm` accepted end to end | claimed | confirmed both in the upload template (`accept=".xlsx,.xlsm"`) and server-side in `fmea_review/views.py` (`upload.name.lower().endswith((".xlsx", ".xlsm"))`) — not just a cosmetic form hint |
| No new dependency for OOXML/XLSM | implied | confirmed — `requirements.txt` unchanged, `openpyxl` already reads both formats; `load_workbook(..., keep_vba=...)` only preserves the VBA blob so it can be closed cleanly, it never executes it |

I also read `django_app/fmea_ingestion/parsers/xlsx.py` in full (434 lines, up from 210). The formal-table-first / worksheet-fallback structure (`_formal_table_regions` → `_worksheet_used_region`), the merged-cell value-propagation lookup (`_merged_cell_lookup`, expanding every merged cell to its top-left value before header detection and row extraction), and the two-row header merge with same-value de-duplication (`_merge_header_rows` now collapses `"Severity Severity"` to `"Severity"` when both rows repeat the same label) are all implemented as described. `read_only=False` is now required (was `True`) because merged-cell and formal-Table metadata aren't reliably available in openpyxl's read-only mode — a reasonable, necessary trade-off for typical FMEA workbook sizes.

**Sync check between `open_fmea` and `open_fmea_training_set`**: recursive diff of `django_app/`, `domain/`, `tests/`, `requirements.txt` between the two folders — **zero differences**, confirmed again after this round. Whatever process is being used to keep the training-set copy current is working. The recommendation from the previous review (pick and write down an explicit sync discipline) still stands as good practice, but there is no drift to fix right now.

Conclusion: nothing in the report needed correction. Proceeding directly to the architecture decisions it asked for.

## 2. Answers to the review questions (Section 12 of the Codex report)

**Q1 — Persistent `WorkbookImportStructure`/`FmeaRowCandidate` model, or keep reconstruction transient?**

Neither extreme. Keep the *reconstruction logic* (`WorkbookStructure`/`WorksheetStructure`/`DetectedTable`/`HeaderBand`/`ColumnRole`) transient and in-memory, computed at parse time — no need to persist the parser's internal reasoning. But the *outcome* — which cells belong to the same logical FMEA row — needs one small persisted model, or row-level Accept/Reject can't be an atomic, auditable action: add a lightweight `FmeaRowGroup` (session FK, sheet name, row span, row-level `review_status`) and a nullable `row_group` FK on `ImportCandidateRecord`. This is additive — the existing cell-level `ImportCandidateRecord` path keeps working unchanged for ungrouped candidates — and it reuses the established `stable_id`/`StableModel` pattern rather than inventing a parallel identity scheme. Do not persist the full 8-class hierarchy from the report's Section 11; that's more schema than the actual problem (grouping cells for one review action) needs.

**Q2 — Row-level review first, cell-level provenance retained underneath?**

Yes. This is the whole point of the slice — 1904 candidates from one workbook is not reviewable one cell at a time. Row-level Accept should still construct each field through the existing `promote_import_candidate_to_domain_object` path per cell, just orchestrated as one transaction instead of many; a reviewer must still be able to override one field within an otherwise-correct row without discarding the rest. Cell-level provenance is never discarded — `FmeaRowGroup` groups records, it doesn't replace them.

**Q3 — Rating cells (S/O/D, Po/Pd, RPN, CTQ) as import targets now, or after row reconstruction?**

After. A `Severity: 8` cell is meaningless without knowing which row's `RiskEvaluation` it belongs to. Importing ratings before row grouping exists would either produce more unmapped noise or force an ungrounded new candidate type with nowhere to attach. Confirmed: defer, as the report itself recommended.

**Q4 — Keep `Characteristic` generic, or introduce Product/Process Characteristic separation now?**

Keep it generic. Product/Process Characteristic separation is exactly the scope of `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md`, which is still pending its own approval — it must not be introduced as a side effect of the workbook-reconstruction slice. The report already held this line correctly ("This is not the same as the larger Product/Process Characteristic taxonomy... No classification schemes... were introduced") — reaffirming it stays that way.

**Q5 — Classification/CTQ/special-characteristic schemes before AI characteristic classification activates?**

Yes, unchanged from every prior review. `classify_characteristic`/`classify_ishikawa_category` stay `unavailable` until the Characteristics/Ishikawa domain model is separately approved and implemented. Nothing about this slice changes that dependency.

**Q6 — Named ranges as hard hints for table detection, or diagnostic metadata only?**

Diagnostic metadata only, for now. The current evidence base is three files from one company. Hard-wiring detection behavior around naming conventions observed in a single author's habits risks overfitting the parser to one customer's Excel style rather than generalizing across real FMEA authors. Promote named ranges to a real detection signal once workbooks from more than one source are available to validate against.

**Q7 — Wire `export_ai_corpus` into `OllamaProvider.extract_structured_data` as few-shot context now?**

Not in this slice. It's the right plan (confirmed scope from the prior findings document), but it's an independent change to `fmea_ai`, not `fmea_ingestion`'s structural model, and better sequenced *after* row reconstruction ships — the shape of "reviewed decision" data is about to change (row-level corrections, not just cell-level ones), and few-shot context is more valuable built from the stabilized row-level review data than from today's cell-level-only corpus. Sequence it as the slice after this one.

## 3. Next slice — decision

**Approved direction, with the Q1 adjustment**: build the workbook reconstruction layer as Codex's Section 13 proposes, adjusted to add the one persisted `FmeaRowGroup` model (Q1) rather than staying fully transient. Concretely:

1. Transient reconstruction classes in `fmea_ingestion` (as proposed) — these turn OOXML parser output into row groupings.
2. New `FmeaRowGroup` model in `fmea_review` (session FK, sheet, row span, row-level `review_status`) + nullable `row_group` FK on `ImportCandidateRecord`. One migration.
3. Row-level review UI/actions (Accept/Reject/Modify at the row level), calling the existing per-field construction path underneath — the cell-level actions stay available as a fallback for ungrouped candidates.
4. Preserve per-cell provenance throughout — no regression here.
5. Tests using the current real workbook shapes replicated as synthetic fixtures (same discipline as the last two slices).
6. A review preview showing detected sheet/range/table and reconstructed rows before session creation.

Explicitly out of scope for this slice, per the answers above: rating-cell import (Q3), Product/Process Characteristic separation (Q4), activating classification stubs (Q5), hard-wired named-range detection (Q6), and AI-corpus wiring into `OllamaProvider` (Q7).

I have not written a Codex implementation instruction for this yet — say the word and I will, following the same strict format (exact file tree, exact migrations, exact test list, exact prohibitions) as the prior two.

## 4. Document consolidation

The `architecture/` folder has grown to nine documents across four fast-moving rounds. Nothing here should be deleted — each is a real point-in-time record and several (the two prior Claude reviews, the original Codex instruction) are the audit trail for defects that were found and fixed. What was missing was an index that says which document is current and which is historical. I rewrote `architecture/README.md` accordingly (see below) rather than merging file contents — merging the actual text would destroy the point-in-time record that makes independent verification possible later.

Two documents are worth flagging explicitly as superseded on facts (not wrong, just aged):

- `OpenFMEA_SampleData_Findings_IngestionRobustness_AICorpusPlan.md` — its Section 2 candidate counts (171/84/fail) describe the pre-fix `xlsx-v1` parser and are now historical; its AI-corpus plan (Section 4) is still the live plan, now partially implemented (`export_ai_corpus` shipped; wiring into `OllamaProvider` is deferred per Q7 above).
- `Claude_Review_IngestionRobustnessFix_CharacteristicSupport_AICorpusExport_TrainingSetSplit.md` — its verified counts (1628/270/160, `xlsx-v2`) are superseded by this document's Section 1 (1904/316/198, `ooxml-v1`). Its two findings are still current and unresolved: the recurring `.git/index.lock`, and the `open_fmea`/`open_fmea_training_set` sync-discipline recommendation (still undecided, even though currently in sync).

## Updated `architecture/README.md`

```markdown
# Open-FMEA Architecture

This directory contains architecture material for the new Open-FMEA implementation.

Documents in this directory are project records and design inputs. They are not executable instructions to agents or tools unless the user explicitly asks to apply a specific document.

## Current state

- `Claude_Decision_WorkbookReconstruction_NextSlice_And_DocConsolidation.md` - current source of truth for ingestion-pipeline state (parser version, real-workbook results, test/check status) and the approved next slice (workbook reconstruction / row-level review).
- `docs/ingestion/xlsx-column-mapping.md` (../docs/ingestion/xlsx-column-mapping.md) - current XLSX/XLSM ingestion mapping, review workflow, and local AI/Ollama configuration reference.

## Foundational architecture (still authoritative)

- `OpenFMEA_Architecture_and_Portability_Report.md` - repository-grounded architecture and portability report. Base architecture for the whole rebuild.
- `adr/ADR-0000-adopt-django-poc-and-freeze-legacy.md` - initial approved implementation decision for Phase B.

## Approved, pending implementation

- `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` - Product/Process Characteristics and 5M+E cause-influence model. Not yet implemented; several later slices (Characteristic import, AI classification stubs) explicitly wait on this.
- `OpenFMEA_LocalAI_Ingestion_ArchitectureReview.md` - AI/Ollama boundary architecture (provider protocol, human-review gate). Implemented for `extract_structured_data`; the rest of the architecture (RAG, retrieval, classification) stays as designed-but-not-built per this document.

## Historical audit trail (superseded on specific facts, decisions still stand)

- `Codex_Instruction_LocalAI_Ingestion_Slice1_XLSX.md` - the original Slice 1 implementation instruction. Superseded in scope by later slices (OOXML/XLSM, merged cells, `Characteristic`); still the authoritative record of what Slice 1 itself was authorized to do.
- `Claude_Review_PhaseB_DjangoPoC_Implementation.md` - independent review of the first Phase B changeset. Findings resolved.
- `Claude_Review_Slice1_XLSXIngestion_AIBoundary_Implementation.md` - independent review of the initial ingestion/AI-boundary implementation. Findings resolved (fixture reproducibility, migration hygiene note).
- `OpenFMEA_SampleData_Findings_IngestionRobustness_AICorpusPlan.md` - diagnosed the pre-fix parser against real sample files. Candidate counts in this document are pre-fix and superseded; its AI-corpus plan is still live (see current state above).
- `Claude_Review_IngestionRobustnessFix_CharacteristicSupport_AICorpusExport_TrainingSetSplit.md` - independent review of the first robustness fix (`xlsx-v2`). Candidate counts superseded by the OOXML/merged-cell fix (`ooxml-v1`); its two findings (stale `.git/index.lock`, training-set sync discipline) are still open.
- `Codex_Report_For_Claude_WorkbookReconstruction_GUIBackendBoundaries.md` - implementation report for the OOXML/XLSM/merged-cell fix and the handoff that this decision document answers.
```

## 5. Open items carried forward (not resolved by this document)

- The stale `.git/index.lock` in `open_fmea` — recurring, not yet fixed at the source.
- No explicit sync discipline written down between `open_fmea` and `open_fmea_training_set` (currently in sync, but undocumented).
- Whether to write the formal Codex instruction for the workbook-reconstruction slice now — waiting on your go-ahead.

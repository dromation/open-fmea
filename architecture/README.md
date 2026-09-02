# Open-FMEA Architecture

This directory contains architecture material for the new Open-FMEA implementation.

Documents in this directory are project records and design inputs. They are not executable instructions to agents or tools unless the user explicitly asks to apply a specific document.

## Current state

- `Claude_Review_CharacteristicsLinking_GUIShell_Verification_ProcessFlowGapFix.md` - **most recent, 2026-09-02.** Independent re-verification of the characteristics-linking and GUI-shell slices, the Process Flow panel gap found and fixed, and two operational-risk findings (`.git/index.lock`, a `db.sqlite3` disk-I/O error over the device bridge).
- `OpenFMEA_DNA_CoreReference.md` - **read this first.** The consolidated master reference: non-negotiable architectural rules, the package/boundary map, the full entity-relationship model (built + approved-pending), status vocabularies, a table of exactly what's built/approved/deferred as of its last-updated date, and the sequencing dependency graph for the current push. Everything below is cited from it, not a replacement for it.
- `Codex_Report_CauseInfluence_IshikawaBackend_Implementation.md` - implemented `CauseCategoryScheme`/`CauseCategory`/`CauseInfluence`, the status-transition rules, and the list-form Ishikawa review GUI. Independently re-verified 2026-09-01: transition rules checked line-by-line against the connection-logic spec, 69/69 tests in both `open_fmea` and `open_fmea_training_set`, zero source-tree drift, boundaries confirmed by grep, EXE rebuilt with a threaded-WSGI fix for the keep-alive hang. `classify_ishikawa_category`'s gating condition is now met (not yet authorized to wire in).
- `Claude_Decision_WorkbookReconstruction_NextSlice_And_DocConsolidation.md` - source of truth for ingestion-pipeline state as of the OOXML/merged-cell fix and the approved workbook-reconstruction slice.
- `Codex_Report_WorkbookReconstruction_RowLevelReview_Implementation.md` - implemented row-level review slice: `FmeaRowGroup`, transient reconstruction, GUI boundaries, AI/data-pipeline boundary. Independently re-verified 2026-09-01 against all three real sample workbooks and both `open_fmea`/`open_fmea_training_set` locations (39/39 tests, zero source-tree drift).
- `OpenFMEA_AIProvider_ExtractionPromptSpec.md` - current behavior specification for the active `OllamaProvider.extract_structured_data` prompt. Wired in; changes prompt content only.
- `../docs/ingestion/xlsx-column-mapping.md` - current XLSX/XLSM ingestion mapping, review workflow, and local AI/Ollama configuration reference.
- `../docs/domain/cause-influence.md` - current Ishikawa/`CauseInfluence` domain documentation (entities, status rules, GUI surface, AI boundary, Man-category boundary).

## Active implementation instructions (status as of 2026-09-02)

- `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` - **implemented, independently verified 2026-09-02.** Restyles the existing Django app to a dark-theme design system, sidebar/header shell, home dashboard with only real queried numbers. No separate Codex Report exists for this slice; verified directly against the instruction (nav scope, dashboard query spec, offline-safe assets all confirmed by grep and `test_gui_navigation_scope.py`/`test_dashboard_view.py`).
- `Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md` - **implemented, independently verified 2026-09-02.** Renamed `Characteristic` to `ProductCharacteristic`, added `ProcessCharacteristic` (instance-level), widened `CauseInfluence`'s allowed types to include both. One gap found during verification (the Section 6 Process Flow panel was specified but never built) was closed in the same session -- see `OpenFMEA_DNA_CoreReference.md` Section 11.
- `Codex_Instruction_CauseInfluence_CauseCategoryScheme_IshikawaBackend_Slice.md` / `OpenFMEA_CauseInfluence_ConnectionLogic_Spec.md` - the instruction and rule spec for the now-implemented slice above; kept as the authoritative record of what was authorized and built.
- `OpenFMEA_AIProvider_IshikawaClassificationPromptSpec.md` - `classify_ishikawa_category` prompt design, prepared in advance. **Not wired in** -- its gating condition is now met (all three slices above have shipped); wiring it in still needs its own explicit go-ahead.
- Visual Ishikawa fishbone-diagram GUI - explicitly deferred, waiting on the user to supply reference images; no instruction written yet.
- PM-FMEA / Asset / Maintenance architecture review - explicitly held off by user decision until the three slices above shipped (`OpenFMEA_DNA_CoreReference.md` Section 10, Mockup 3 decision). They now have; the review itself has not been written and is not authorized to be treated as implementation-ready without one.

## Foundational architecture (still authoritative)

- `OpenFMEA_Architecture_and_Portability_Report.md` - repository-grounded architecture and portability report. Base architecture for the whole rebuild.
- `adr/ADR-0000-adopt-django-poc-and-freeze-legacy.md` - initial approved implementation decision for Phase B.

## Approved, pending implementation

- `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` - Product/Process Characteristics and 5M+E cause-influence model. The design authority for the two active instructions above; its five Section 17 decisions are now acted on as described in `OpenFMEA_DNA_CoreReference.md` Section 0/6 and the instructions' own Section 0 scoping notes. `ClassificationScheme`/`ClassificationTerm` (product multi-classification), `LessonLearned`, coverage-metric queries, and Control Plan hooks remain not-yet-approved for implementation.
- `OpenFMEA_LocalAI_Ingestion_ArchitectureReview.md` - AI/Ollama boundary architecture (provider protocol, human-review gate). Implemented for `extract_structured_data`; `classify_ishikawa_category` is specified but not wired (see above); the rest (RAG, retrieval) stays as designed-but-not-built per this document.

## Historical audit trail (superseded on specific facts, decisions still stand)

- `Codex_Instruction_LocalAI_Ingestion_Slice1_XLSX.md` - the original Slice 1 implementation instruction. Superseded in scope by later slices (OOXML/XLSM, merged cells, `Characteristic`, row-level reconstruction); still the authoritative record of what Slice 1 itself was authorized to do.
- `Claude_Review_PhaseB_DjangoPoC_Implementation.md` - independent review of the first Phase B changeset. Findings resolved.
- `Claude_Review_Slice1_XLSXIngestion_AIBoundary_Implementation.md` - independent review of the initial ingestion/AI-boundary implementation. Findings resolved (fixture reproducibility, migration hygiene note).
- `OpenFMEA_SampleData_Findings_IngestionRobustness_AICorpusPlan.md` - diagnosed the pre-fix parser against real sample files. Candidate counts in this document are pre-fix and superseded; its AI-corpus plan is still live (see current state above).
- `Claude_Review_IngestionRobustnessFix_CharacteristicSupport_AICorpusExport_TrainingSetSplit.md` - independent review of the first robustness fix (`xlsx-v2`). Candidate counts superseded by the OOXML/merged-cell fix (`ooxml-v1`); its two findings (stale `.git/index.lock`, training-set sync discipline) are still open, restated in `OpenFMEA_DNA_CoreReference.md` Section 7.
- `Codex_Report_For_Claude_WorkbookReconstruction_GUIBackendBoundaries.md` - implementation report for the OOXML/XLSM/merged-cell fix and the handoff that `Claude_Decision_WorkbookReconstruction_NextSlice_And_DocConsolidation.md` answers.

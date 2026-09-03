# Open-FMEA Architecture

This directory contains architecture material for the new Open-FMEA implementation.

Documents in this directory are project records and design inputs. They are not executable instructions to agents or tools unless the user explicitly asks to apply a specific document.

## Current state

- `OpenFMEA_DNA_CoreReference.md` - **read this first.** The consolidated master reference: non-negotiable architectural rules, the package/boundary map, the full entity-relationship model (built + approved-pending), status vocabularies, a table of exactly what's built/approved/deferred as of its last-updated date, and the sequencing dependency graph for the current push. Everything below is cited from it, not a replacement for it.
- `Codex_Report_CauseInfluence_IshikawaBackend_Implementation.md` - implemented `CauseCategoryScheme`/`CauseCategory`/`CauseInfluence`, the status-transition rules, and the list-form Ishikawa review GUI. Independently re-verified 2026-09-01: transition rules checked line-by-line against the connection-logic spec, 69/69 tests in both `open_fmea` and `open_fmea_training_set`, zero source-tree drift, boundaries confirmed by grep, EXE rebuilt with a threaded-WSGI fix for the keep-alive hang. `classify_ishikawa_category`'s gating condition is now met (not yet authorized to wire in).
- `Claude_Decision_WorkbookReconstruction_NextSlice_And_DocConsolidation.md` - source of truth for ingestion-pipeline state as of the OOXML/merged-cell fix and the approved workbook-reconstruction slice.
- `Codex_Report_WorkbookReconstruction_RowLevelReview_Implementation.md` - implemented row-level review slice: `FmeaRowGroup`, transient reconstruction, GUI boundaries, AI/data-pipeline boundary. Independently re-verified 2026-09-01 against all three real sample workbooks and both `open_fmea`/`open_fmea_training_set` locations (39/39 tests, zero source-tree drift).
- `OpenFMEA_AIProvider_ExtractionPromptSpec.md` - current behavior specification for the active `OllamaProvider.extract_structured_data` prompt. Wired in; changes prompt content only.
- `../docs/ingestion/xlsx-column-mapping.md` - current XLSX/XLSM ingestion mapping, review workflow, and local AI/Ollama configuration reference.
- `../docs/domain/cause-influence.md` - current Ishikawa/`CauseInfluence` domain documentation (entities, status rules, GUI surface, AI boundary, Man-category boundary).

## Active implementation instructions (next slices, in sequence)

- `Codex_Instruction_LightDarkThemeToggle_Slice.md` - **built, fixed, independently verified.** Built 2026-09-03 (header/app.js/theme.css/tests, mirrored to `open_fmea_training_set`); a real WCAG AA failure (`--text-muted` too light in light mode, 2.33-2.56:1 vs. required 4.5:1, five real UI text spots) was found, fixed (`--text-muted: #5b6b82`, both light blocks of `theme.css`), and independently re-verified from the actual files in both repos (math reproduced from scratch, source parity confirmed, 112/112 tests and clean checks in both locations). See `Claude_Review_TextMutedContrastFix_ThemeToggleSlice.md`. A separate, pre-existing dark-mode contrast gap in the same token was found and correctly left untouched for a future theme-token fix.
- `Codex_Instruction_TestCoverage_ContrastChecker_CrossSliceWorkflow_Slice.md` - test-only follow-up from the toggle review: an automated WCAG contrast checker (regex-parses the real `theme.css`, computes actual contrast ratios instead of just asserting CSS blocks exist) plus one cross-slice end-to-end test chaining Functions/Failure Modes/Causes/Actions/Process Characteristics/Cause Influence/Risk Matrix/theme-toggle through real HTTP requests in a single session. Does not block the `v1.0.0` release. **Precondition:** the known dark-mode `--text-muted` contrast gap must be fixed first, otherwise this test-only slice will fail correctly.
- `Codex_Instruction_PlannedNavPlaceholders_Slice.md` - **WITHDRAWN, do not implement.** Written on a misreading of the user's request; corrected to a documentation-only GUI roadmap (see `OpenFMEA_DNA_CoreReference.md` Section 10's "GUI Roadmap Index" table). Kept only as an audit-trail record.
- `OpenFMEA_EvidenceTests_ArchitectureReview.md` - **not yet ready for a Codex instruction.** "Evidence & Tests" turned out to be a much richer Test-Plan entity than the existing `Evidence`/`EffectivenessVerification` models (own status workflow, Test Type, Method, Acceptance Criteria, file attachments, a real Owner, direct FailureMode link). Six decisions are now recorded after the Validation Trajectory amendment; Decisions 1-3 remain the hard blockers for a first Codex instruction.
- `OpenFMEA_AIProvider_IshikawaClassificationPromptSpec.md` - `classify_ishikawa_category` prompt design, prepared in advance. **Not wired in** — its gating condition is now met; wiring it in needs its own explicit go-ahead.
- Visual Ishikawa fishbone-diagram GUI - explicitly deferred, waiting on the user to supply reference images; no instruction written yet.
- FMEA-Projects-as-a-page and a User/Role/Team system - both surfaced by the 2026-09-03 nav-tree audit (see `OpenFMEA_DNA_CoreReference.md` Section 10) as ready-for-review candidates; not yet reviewed, no instruction written.
- Characteristics Flow/Diagram and System Characteristics Base - cataloged only (Mockups 8-9), each stacking new-infrastructure needs (a `System` hierarchy, a `ClassificationScheme`-like model, a graph/diagram library, an AI auto-link capability with confidence scoring) on top of each other; explicitly held for later, dependency order matters if ever picked up.

## Recently completed (built + independently verified)

- `Codex_Instruction_FunctionsActionsEvidence_GUIGap_Slice.md` - narrowed scope (Functions + Actions only, `Evidence`/`EffectivenessVerification` pulled - see `OpenFMEA_EvidenceTests_ArchitectureReview.md`). Built and committed 2026-09-03 by the implementing session (git `3c560d6`, `a25eef1` in `open_fmea`, nothing pushed). Independently re-verified from the actual files: forms/views/urls/templates/tests match the narrowed scope, zero `Evidence`/`EffectivenessVerification` GUI code found by grep, no new migration, no nav/sidebar change, `FunctionForm`'s `product`/`operation` fields confirmed pre-existing on the `Function` model. Current full suite: 112/112 passing in both `open_fmea` and `open_fmea_training_set`.
- `Codex_Instruction_RiskMatrix_Slice.md` - system-wide, method-filterable 10x10 severity x occurrence risk matrix. Built and independently verified 2026-09-01: 99/99 tests, clean checks, real nav entry.
- `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` - restyles the existing Django app to a dark-theme design system (grounded in a user-supplied reference dashboard), with a sidebar/header shell and a home dashboard showing only real, queried numbers. Explicitly does not add navigation for anything not built yet - decision confirmed with the user 2026-09-01: restyle Django templates (no SPA/API rewrite), restyle-what's-built-and-grow-incrementally (no placeholder nav). Built and independently verified.
- `Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md` - renamed `Characteristic` → `ProductCharacteristic`, added `ProcessCharacteristic` (instance-level) and the Process Flow panel, widened `CauseInfluence`'s allowed types to include both. Built and independently verified, including the Process Flow gap fix.
- `Codex_Instruction_CauseInfluence_CauseCategoryScheme_IshikawaBackend_Slice.md` / `OpenFMEA_CauseInfluence_ConnectionLogic_Spec.md` - the instruction and rule spec for the Ishikawa backend slice; kept as the authoritative record of what was authorized and built.

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

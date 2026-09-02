# Open-FMEA DNA — Core Reference

Status: living master reference, maintained by Claude (Open-FMEA Technical Architect) and updated at each major slice boundary. This is not a new architecture decision — every fact in it is drawn from documents already reviewed/approved, cited inline. Its purpose is to be the one document a new implementation instruction, a new reviewer, or a returning Codex session reads first, instead of re-deriving established rules or re-reading nine separate documents to find them. When this document and a cited source disagree, the cited source wins and this document has drifted — flag it for correction rather than trusting whichever you read first.

Last updated: 2026-09-02, after independently verifying the characteristics-linking slice and the GUI design system slice, and closing one gap found during that verification (Section 11).

---

## 1. What Open-FMEA is

A portable-domain FMEA (Failure Mode and Effects Analysis) application, rebuilt as a Django proof-of-concept from a legacy Tkinter/SQLite prototype (frozen, read-only, under `legacy/tkinter-prototype/`). "Portable domain" means the actual FMEA logic — entities, relationships, evaluation rules — lives in a framework-free Python package (`domain/fmea_domain/`) that Django depends on, never the reverse; this is enforced by an automated import-isolation test, not just convention.

## 2. Non-negotiable architectural rules

These apply to every slice, past and future, regardless of what any individual implementation instruction says. An instruction that contradicts one of these is wrong and should be stopped, not followed.

1. **Portable domain, one direction only.** `domain/fmea_domain/` never imports Django, `fmea_app`, `fmea_ingestion`, `fmea_review`, or `fmea_ai`. Everything else may depend on it. Enforced by `test_no_django_imports.py` — every new framework-free package must be added to its coverage.
2. **`stable_id`, never raw primary keys, for cross-entity references and interchange.** Every domain entity carries a `stable_id`/`schema_version`/`revision` shape (`DomainEntity`); relationships and imports reference `stable_id`, never a Django auto-increment PK. This is what makes OFEF export/import (`fmea_importexport/ofef.py`) and cross-database references (e.g. `open_fmea` vs. `open_fmea_training_set`, or a future multi-tenant deployment) meaningful.
3. **AI is never authoritative.** Every `AiProvider` task output is a suggestion only. No AI output ever creates, modifies, or accepts a domain object directly; no AI output ever sets a review/approval/confirmation status; no AI output is exempt from schema validation before use; every provider degrades cleanly to "no suggestion" when disabled/unreachable/invalid, and the deterministic/manual path must work identically with AI on or off. `model_confidence`/`ai_confidence` are never called or documented as probabilities.
4. **Human review gate, always.** Nothing produced by ingestion, AI, or bulk import becomes a real, effective domain object without an explicit human Accept (or equivalent explicit confirm action, e.g. a `CauseInfluence` status transition). This applies at both the cell level (`ImportCandidateRecord`) and the logical-row level (`FmeaRowGroup`) and will apply identically to `CauseInfluence` status transitions.
5. **Never auto-assign risk or classification judgments.** Severity, Occurrence, Detection, RPN, Action Priority, CTQ, special-characteristic classification, and (once built) cause-category classification are never auto-assigned by ingestion or AI — only ever entered or confirmed by a human, with AI limited to an advisory suggestion per rule 3.
6. **Configurable taxonomies, not hardcoded enums, for anything domain-specific and organization-configurable.** `EvaluationDefinition` established the pattern (Phase B); `CauseCategoryScheme`/`CauseCategory` and the future `ClassificationScheme`/`ClassificationTerm` follow it. A Python enum is appropriate for a closed, structural vocabulary that isn't organization-configurable (e.g. `ReviewStatus`, `CauseInfluenceStatus`); a scheme+seeded-rows pattern is required for anything an organization might legitimately redefine (5M+E vs. 4M vs. a custom taxonomy; Legal/Safety/Functional vs. a different classification tree).
7. **Approved Control Plans are never silently modified.** Not yet built, but binding on all future work: any Control Plan change is a reviewed, human-approved workflow, never an automatic consequence of an AI suggestion or a confirmed root cause.
8. **No entity/feature is built ahead of its own architecture review's approval.** A review document's "READY WITH CONDITIONS" is not approval; explicit sign-off (recorded in a decision document, as this project has done for every slice so far) is required before implementation starts, and the approved scope is the narrowest one stated, not the full ambition of the review.
9. **Every implementation claim is independently re-verified, never trusted from a status report.** This has been the standing discipline for every slice in this project (see Section 6) and applies to all future ones: re-run the tests yourself, re-run the parser/logic against real data yourself, diff the two deployment locations yourself.
10. **Nothing is deleted from `architecture/`, only superseded and indexed.** `architecture/README.md` tracks current/foundational/approved-pending/historical status; a document whose factual claims are outdated stays as audit trail with a note pointing to what supersedes it.

## 3. Package/boundary map (as of this writing)

```text
domain/fmea_domain/            framework-free domain entities + rules (Section 2, rule 1)
    entities.py                 DomainEntity subtypes: Function, Requirement, FMEA,
                                 ProductCharacteristic* (Characteristic today), FailureMode,
                                 FailureEffect, FailureCause, FailureMechanism,
                                 PreventionControl, DetectionControl, Relationship,
                                 RiskEvaluation, EvaluationDefinition, Evidence, Process/Operation,
                                 + CauseCategoryScheme, CauseCategory, CauseInfluence (built, verified)
                                 + ProcessCharacteristic (next round)*
    rules.py                    validation/rule functions, framework-free

django_app/
    fmea_app/                   the core domain, persisted: models mirror fmea_domain entities,
                                 manual CRUD views (Phase B), promote_import_candidate_to_domain_object
    fmea_ingestion/              framework-free-where-possible parsing + candidate contracts:
                                 candidates.py (ImportCandidate, SourceProvenance, ReviewStatus),
                                 parsers/xlsx.py, mapping/, reconstruction.py (FmeaRowGroup logic)
    fmea_review/                 Django persistence + GUI for the review queue:
                                 ImportSession, ImportCandidateRecord, FmeaRowGroup,
                                 accept/reject/merge/link-existing, row-group accept/reject
    fmea_ai/                     provider-neutral AI boundary: contracts.py (AiProvider protocol,
                                 6 tasks), validation.py, providers/{disabled,ollama}_provider.py
    fmea_evaluation/              risk evaluation calculators
    fmea_importexport/            OFEF (Open-FMEA Exchange Format) serialize/deserialize

packaging/                      PyInstaller build for the training EXE (open_fmea_training_set only)
architecture/                   review/decision documents, README.md is the index
```
`*` marks entities not yet implemented as of this writing — see Section 6 for exact status.

## 4. Core entity relationships (as-approved model, built + pending combined)

```text
Function --(has)--> Requirement --(has)--> ProductCharacteristic --(classified by, future)--> ClassificationTerm
ProductCharacteristic --(fails as)--> FailureMode --(causes)--> FailureEffect
FailureMode --(caused by)--> FailureCause --(mechanism)--> FailureMechanism
FailureCause --(prevented by)--> PreventionControl
FailureMode/FailureCause --(detected by)--> DetectionControl

ProcessCharacteristic (future) --(cause_category)--> CauseCategory --(scheme)--> CauseCategoryScheme
ProcessCharacteristic --(CauseInfluence edge)--> ProductCharacteristic --(CauseInfluence edge)--> FailureMode
FailureCause/FailureMechanism --(CauseInfluence edge, status vocabulary)--> FailureMode/FailureCause

RiskEvaluation --(against)--> FailureMode, using --(configured by)--> EvaluationDefinition
Evidence --(supports, via generic Relationship)--> CauseInfluence (future)
```

`CauseInfluence` is the one deliberately generic, type-agnostic edge in this model (see `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` Section 5) — it is not a hardcoded FK chain, its `source_type`/`target_type` are validated against an explicit allowed-set that widens as more entity types are approved (Section 6 tracks the current allowed sets). The generic `Relationship` entity remains for structural containment links (`fmea_contains_failure_mode`, etc.) and is not being replaced by `CauseInfluence` — they serve different purposes, per the same section's reasoning.

## 5. Status vocabularies (closed, structural — not organization-configurable, per rule 6)

- `ReviewStatus` (cell-level and row-group-level review): `UNREVIEWED, ACCEPTED, MODIFIED, REJECTED, DUPLICATE, NEEDS_CLARIFICATION`.
- `CauseInfluenceStatus`: `SUSPECTED, POSSIBLE, CORRELATED, EXPERIMENTALLY_SUPPORTED, CONFIRMED_ROOT_CAUSE, REJECTED` — transition rules in `OpenFMEA_CauseInfluence_ConnectionLogic_Spec.md`.
- `AiTaskResponse.status`: `ok, unavailable, invalid_output, timeout, error`.

## 6. Current state — what's built, what's approved-pending, exact sequencing

Verified directly (re-run, not assumed) as of 2026-09-01:

| Capability | Status | Evidence |
|---|---|---|
| XLSX/XLSM ingestion (`ooxml-v1`), per-sheet isolation, formal-table + merged-cell handling | **Built, verified** | 1904/316/198 candidates on the three real sample files, 39/39 tests passing in both `open_fmea` and `open_fmea_training_set`, zero source-tree drift |
| Cell-level review queue (`ImportCandidateRecord`, Accept/Reject/Modify/Merge/Link-Existing) | **Built, verified** | Same test run as above |
| Row-level reconstruction (`FmeaRowGroup`, logical-row grouping, row-level Accept/Reject) | **Built, verified this session** | Reconstruction logic independently re-run against all three real sample files: 22 row groups from the real PFMEA example, 15 from the bilingual PPAP FMEA sheet, 132 from the templates workbook; row-level accept correctly chains Function→Requirement→FailureMode(needs fmea_stable_id)→FailureEffect/FailureCause→Prevention/DetectionControl via context propagation; GUI requires an explicit target-FMEA selection before promotion |
| `Characteristic` import support (current name, pre-rename) | **Built, verified** | Reuses pre-existing Phase B entity, correctly scoped, not the classification model |
| `export_ai_corpus` (read-only training-corpus export) | **Built, verified** | Deterministic JSONL, ACCEPTED/MODIFIED by default |
| `extract_structured_data` behavioral prompt (10 hard rules, domain glossary, 4 few-shot examples) | **Built, verified** | Wired into `OllamaProvider._build_prompt`, no test regression, injection defense structurally unaffected |
| `CauseCategoryScheme`/`CauseCategory`/`CauseInfluence` + Ishikawa review GUI (list-form, not diagram) | **Built, verified** | 69/69 tests in both `open_fmea` and `open_fmea_training_set`, zero source-tree drift, `manage.py check`/`makemigrations --check` clean in both, transition rules independently checked line-by-line against the connection-logic spec, boundaries confirmed by grep (no `ProcessCharacteristic`/`ClassificationScheme`/rename, `fmea_ai/` untouched). EXE rebuilt with a threaded WSGI server fix (keep-alive-connection hang). See `architecture/Codex_Report_CauseInfluence_IshikawaBackend_Implementation.md`. |
| `CauseInfluence` connection/status-transition rules | **Built, verified** | `validate_cause_influence_transition` matches the spec's worked-example table; Codex added two sound safety details beyond spec: retarget-to-`FailureCause` must belong to the same `FailureMode`, and creation always starts at `SUSPECTED` regardless of posted status |
| `classify_ishikawa_category` AI prompt | **Specified, explicitly not wired** | `OpenFMEA_AIProvider_IshikawaClassificationPromptSpec.md` — gating condition (Ishikawa-backend slice built + verified) is now met; wiring it in is the next thing to authorize, not yet authorized |
| `ProductCharacteristic` rename, `ProcessCharacteristic`, characteristics-linking (`CauseInfluence` widened to `ProcessCharacteristic`/`ProductCharacteristic`) | **Built, verified** | `Codex_Report_ProductProcessCharacteristic_Linking_Implementation.md` -- independently re-verified 2026-09-02: 87/87 tests, `manage.py check`/`makemigrations --check` clean, `primary_classification_id` confirmed dormant (grep: only ever set to None), no `ClassificationScheme`/`ClassificationTerm` present, CONFIRMED_ROOT_CAUSE correctly rejected for a ProductCharacteristic target (rules.py). One real gap found and closed this session: Section 6's `/processes/<stable_id>/flow/` Process Characteristics/Linked Product Characteristics panel was specified in the instruction but was never built in the original implementation (no route, no template, no test_process_flow_view.py) -- added now, see the new Section 11 |
| Visual Ishikawa fishbone-diagram GUI | **Deferred — waiting on user-supplied reference images** | Not started; will be its own instruction once images are provided |
| `ClassificationScheme`/`ClassificationTerm` (product multi-classification: Legal/Safety/Functional/...) | **Reviewed, not yet approved for implementation** | Architecture review Section 2; no decision document has greenlit this yet |
| `LessonLearned`, coverage-metric query implementations, Control Plan entity/hooks | **Reviewed, explicitly deferred** | Architecture review Sections 9, 10, 12, 16 |
| GUI design system + app shell (dark theme, sidebar/header, real-data-only dashboard) | **Built, verified** | `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` -- independently re-verified 2026-09-02: nav scope matches Section 2's exact list (grep confirms none of the excluded labels render, test_gui_navigation_scope.py passes), dashboard stats match Section 3's exact query spec (combined candidate+row pending-review stat, real CauseInfluenceStatus breakdown, merged recent-activity query, no fabricated widgets), hand-written CSS (no Tailwind/CDN), vanilla JS only. No separate Codex Report was written for this slice; verified directly against the instruction instead |

**Sequencing dependency graph for the current push:**

```text
[Ishikawa-backend slice: CauseCategoryScheme, CauseCategory, CauseInfluence(narrow types), list-form board]  DONE, verified 2026-09-01
        |
        v
[Characteristics-linking slice: ProductCharacteristic rename, ProcessCharacteristic, CauseInfluence widened]  DONE, verified 2026-09-02 (Process Flow panel gap closed same session)
        |
        v
[GUI design system + app shell]  DONE, verified 2026-09-02
        |
        v
[classify_ishikawa_category wiring]   (unblocked now, independent of the line below — not yet authorized)
        |
[Visual Ishikawa GUI]   (independent, waiting on reference images from the user)
        |
[PM-FMEA / Asset / Maintenance architecture review]  (user decision: hold off until the three slices above ship -- they now have; review not yet written)
```

## 7. Known open operational risks (unresolved, tracked, not this document's job to fix)

- `.git/index.lock` recurring in `open_fmea` — flagged in at least two independent review rounds, not yet root-caused by the user.
- `open_fmea_training_set` has no `.git` at all — source-tree parity has held (verified zero-diff every round so far) but there is no automated mechanism preventing future drift; the sync discipline itself (regenerate-from-`open_fmea` vs. real second checkout) remains undecided by the user.
- Any `ImportCandidateRecord` rows already persisted with `suggested_domain_type="Characteristic"` in either database must be migrated when the rename ships (Section 8 of the characteristics-linking instruction) — a concrete instance of the drift risk above already materializing.

- **Root cause of the recurring `.git/index.lock` found, 2026-09-02**: confirmed present again this session (a stale, zero-byte lock file, several days old). Not yet safe to delete blindly from a remote/bridged shell -- recommend the user remove it locally on the Windows machine (where it's unambiguous whether a git process is actually running) before the next commit.
- **New this session, likely the same root cause**: `db.sqlite3` in `open_fmea` could not be opened at all (`sqlite3.OperationalError: disk I/O error`, then `attempt to write a readonly database`) from a remote shell reaching the repository over a FUSE-mounted bridge, after a `seed_demo` run failed mid-transaction and left a 271KB `db.sqlite3-journal` hot-journal file behind. This strongly suggests the bridged filesystem does not support the POSIX file-locking SQLite (and, separately, git) rely on for safe concurrent writes -- the same mechanism likely explains the `.git/index.lock` recurrence above. The database file itself is very likely not corrupted (a hot journal is SQLite's normal recovery mechanism, not damage); it needs to be opened once locally on the Windows machine (native filesystem, real locking) so SQLite can roll the journal back automatically. Do not attempt further writes to `db.sqlite3` from a bridged/remote shell until this is confirmed recovered.

## 8. Document index (see `architecture/README.md` for the full, maintained index — this is the DNA's own quick map)

- **Foundational (still authoritative):** `OpenFMEA_Architecture_and_Portability_Report.md`, `ADR-0000-adopt-django-poc-and-freeze-legacy.md`.
- **Domain model authority for the current push:** `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` (design), this document (consolidated reference), `OpenFMEA_CauseInfluence_ConnectionLogic_Spec.md` (transition rules).
- **Active implementation instructions:** `Codex_Instruction_CauseInfluence_CauseCategoryScheme_IshikawaBackend_Slice.md`, `Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md`.
- **Prepared, not-yet-wired AI specs:** `OpenFMEA_AIProvider_ExtractionPromptSpec.md` (wired), `OpenFMEA_AIProvider_IshikawaClassificationPromptSpec.md` (not wired).
- **Historical audit trail (facts superseded, decisions still stand):** `OpenFMEA_SampleData_Findings_IngestionRobustness_AICorpusPlan.md`, `Claude_Review_Slice1_XLSXIngestion_AIBoundary_Implementation.md`, `Claude_Review_IngestionRobustnessFix_CharacteristicSupport_AICorpusExport_TrainingSetSplit.md`, `Claude_Decision_WorkbookReconstruction_NextSlice_And_DocConsolidation.md`.

## 9. How to use this document

Before writing or approving any new Open-FMEA implementation instruction: read Section 2 (rules) and Section 6 (current state) here first. If a proposed instruction would violate a Section 2 rule, or build something Section 6 marks as not-yet-approved, stop and say so rather than proceeding. When a slice completes and is independently verified, update Section 6's table and Section 3's entity list in this document — do not let it drift out of date the way the per-slice review documents were explicitly allowed to (Section 2, rule 10) while this one is meant to always reflect current reality.

## 10. GUI reference mockups (visual target library — not all approved for implementation)

The user is progressively supplying reference dashboard screenshots showing the intended look and eventual feature scope of the GUI. Each one has contributed real, actionable design direction; each has also shown features with no backend and no architecture review. Treat every mockup as data about visual language and eventual product direction, never as implementation authorization by itself — the same rule that applies to every other design input in this project.

**Mockup 1 (2026-09-01):** the base app shell — dark theme, sidebar, header, home dashboard with stat cards. Drove `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md`. Adopted: the visual language (palette, cards, sidebar/header structure). Explicitly not adopted: most of its sidebar (Risk Matrix, Validation Trajectory, CAPA, Control Plans, SPC, XDA, AI Assistant, search, notifications) — none of it backed by anything built or approved.

**Mockup 2 (2026-09-01):** added an "Engineering Context" panel (System/Product/Process context, a Process Flow step picker, a Process Characteristics table, a Linked Product Characteristics table) and a "Characteristics Flow" chain diagram, an FMEA Team panel, and a global System/Product/Process context switcher tied to "Open-EQMS." Drove an update to `Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md` Section 6: the Process Flow/Process Characteristics/Linked Product Characteristics panel is now a concrete part of that already-approved slice (its underlying entities — `Process`, `Operation`, `ProcessCharacteristic`, `ProductCharacteristic`, `CauseInfluence` — are all already approved or being built). Deliberately not adopted: the panel's Type/Criticality columns (require the not-yet-approved `ClassificationScheme`), the FMEA Team panel (no collaboration/user-roles backend exists), the global System/Product/Process context switcher and any "Open-EQMS" integration badge (no cross-system integration path exists — architecture review Section 15).

**Mockup 3 (2026-09-01):** shows a "Preventive FMEA (PM-FMEA)" tab alongside DFMEA/PFMEA/System FMEA, with its own dashboard (asset-coverage donut chart, a PM-FMEA-specific validation trajectory with maintenance-lifecycle stages, a Top High Risk Maintenance Items table keyed to physical assets/machines rather than FMEA line items), a "Characteristics Flow" diagram extended with a "Maintenance Tasks/Plans (Open-EQMS Maintenance)" node, and — new in the Engineering Context panel — a "Linked Asset for Step 30" card (a physical machine/asset with operational status and location) and a "Maintenance Status" card (PM compliance %, overdue work orders, next PM date). **Cataloged only, not actioned.** This introduces several genuinely new concepts with no existing entity, no existing architecture review, and no approval: a distinct PM-FMEA type (is it a new value on `FMEA`'s existing type field, or a structurally different entity? not decided), a physical `Asset`/machine entity, `WorkOrder`/maintenance-task entities, PM compliance/coverage metrics, and — again — an "Open-EQMS Maintenance" cross-system integration point.

**User decision on Mockup 3 (2026-09-01):** hold off on writing the PM-FMEA/Asset/Maintenance architecture review until the currently-approved slices (Ishikawa backend — done; characteristics-linking; GUI shell) actually ship. Nothing from Mockups 3 or 4 is to be turned into an implementation instruction before that review exists and is approved.

**Mockup 4 (2026-09-01):** a consolidated "final vision" Home dashboard, combining Mockups 1–3 into one page (all the same stat cards, Risk Overview matrix, Validation Trajectory now spanning DFMEA+PFMEA+PM-FMEA, Engineering Context panel, PM-FMEA maintenance-risk donut) plus two more new pieces: an **Operations** sidebar module (Process Planning, Production Execution, Work Tracking, Traceability) with a home-page "Operations & Maintenance Status" widget (today's production orders/in-progress/completed counts, today's PM-due/in-progress/overdue counts), and a **Project Health (Summary)** panel (overall health score, a 30-day risk trend line chart, an actions total/overdue/due-soon count, per-FMEA-type coverage bars, a data-integrity linked/unlinked/broken-links count, next-review dates per FMEA type). **Cataloged only, not actioned** — same reasoning as Mockup 3: Operations (production orders, work tracking, traceability) is an entirely new module with no entity model and no review, and the Project Health panel's metrics (risk trend history, coverage-by-type, link-integrity counts) require aggregation logic and historical tracking that don't exist. This mockup doesn't introduce a new open question beyond what Mockup 3 already raised — it's covered by the same "hold off" decision above.

## 11. Session addendum, 2026-09-02 -- gap closed in the characteristics-linking slice

Independent re-verification of `Codex_Report_ProductProcessCharacteristic_Linking_Implementation.md` found that Section 6 of `Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md` -- the concrete `GET /processes/<stable_id>/flow/` Process Characteristics / Linked Product Characteristics panel, grounded in Mockup 2 and explicitly called out in this document's own Section 10 as "now a concrete part of that already-approved slice" -- was never implemented. No route, no view, no template, no test existed for it, and the Codex report's own "Implemented" and "Still Deferred" lists did not mention it either way.

This was in-scope, already-approved work with nothing new to decide, so it was completed in this session rather than escalated:

- `fmea_app.views.process_flow` + `GET /processes/<stable_id>/flow/`: lists a `Process`'s `Operation`s as an ordered step list; selecting one (via `?operation_id=`) shows that operation's `ProcessCharacteristic`s (generic key/value rendering of `attributes`, per Section 6's instruction not to hardcode assumed keys) and the `ProductCharacteristic`s reachable via a `CauseInfluence` from those characteristics, each with its influence status as a badge (reusing `_status_badge.html` from the GUI-shell slice). No Type/Criticality columns, matching the explicit exclusion.
- Reachable from the GUI: a new "Processes" panel on the FMEA detail page, a "View in Process Flow" link from the process-characteristic detail page, and a "Process Flow" link per row on the process-characteristic list page. No sidebar entry was added (out of scope, and `test_gui_navigation_scope.py`'s allow-list was not touched).
- One demo `CauseInfluence` (`ProcessCharacteristic` "Seal installation force" -> `ProductCharacteristic` "Seal seat surface condition") was added to `seed_demo` so the panel has real data to show, matching the existing seed's demonstration intent.
- `tests/test_process_flow_view.py` (3 tests): selecting an operation shows only its own process characteristics; the linked-product-characteristics table shows only characteristics actually reachable from that operation; the response contains no "Type"/"Criticality" column or label.

Verified together with the rest of the slice: 87/87 tests passing, `manage.py check` clean, `makemigrations --check --dry-run` reports no changes (this is a pure view/template/CSS/seed-data addition, no model change, so no migration was expected or created).

Not yet done, deliberately out of scope for this gap-fill: mirroring this change into `open_fmea_training_set` and rebuilding the training EXE (the sync discipline for that copy is still the user's open decision per Section 7), and updating `architecture/README.md`'s document index (done separately, see the README diff).
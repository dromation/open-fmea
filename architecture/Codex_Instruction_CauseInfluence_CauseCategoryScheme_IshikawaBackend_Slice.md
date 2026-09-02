# Codex Implementation Instruction — CauseCategoryScheme + CauseInfluence + Ishikawa Review Backend (Slice: Ishikawa-Backend-1)

Status: Approved for implementation, subject to the conditions in `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` and the scoping decisions stated explicitly in Section 0 below.

Authority, in order: `Open-EQMS_Architecture_Baseline_v1.0.md` and `PRS-000-master-product-vision.md` (highest); `OpenFMEA_Architecture_and_Portability_Report.md`; `ADR-0000-adopt-django-poc-and-freeze-legacy.md`; `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` (this slice's design authority — Sections 4, 5, 6, 16, 17); `Claude_Decision_WorkbookReconstruction_NextSlice_And_DocConsolidation.md` (sequencing precedent). **You do not have authority to change any decision recorded in these documents or in Section 0 below. If an instruction conflicts with one of them, or a design decision is missing, stop and report — do not decide it yourself.**

Branch: continue on the current working branch used for the `FmeaRowGroup` workbook-reconstruction work unless told otherwise before you start.

Precondition, verified before this instruction was written: `FmeaRowGroup` / row-level review (reconstruction.py, migration `0002_fmearowgroup...`, `row_group_detail.html`, `accept_row_group`/`reject_row_group`) exists, is wired end-to-end, and passes 39/39 tests in both `open_fmea` and `open_fmea_training_set` with zero source-tree drift between them. This slice builds on top of that — do not modify `reconstruction.py`, the row-group models, or the row-group accept/reject services except where Section 3 explicitly says to.

## 0. Scoping decisions made for this slice (read before starting)

The architecture review's Section 17 lists five decisions requiring approval. This instruction acts on them as follows — **do not re-derive or second-guess these; if you disagree, stop and report, do not silently reinterpret:**

1. **Decision 1 (CauseInfluence design, Section 5 of the review) — APPROVED**, with one narrowing for this slice specifically: `source_id` may only reference a `FailureCause` or `FailureMechanism` in this slice (not a `ProcessCharacteristic` — that entity does not exist yet and is out of scope here, see Section 8). `target_id` may only reference a `FailureMode` or `FailureCause`. This is the "Potential Cause" pattern from Section 5: a candidate cause targets a `FailureMode` directly with `status=suspected/possible/...`; on confirmation it is promoted to a real `FailureCause` and the edge is updated to `status=confirmed_root_cause` targeting that `FailureCause`.
2. **Decision 2 (rename `Characteristic` → `ProductCharacteristic`) — NOT part of this slice.** Explicitly deferred to the separate `Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md` instruction. Do not touch `fmea_app.Characteristic` here.
3. **Decision 3 (narrower first increment) — ADOPTED, narrowed further.** The review's own "narrower increment" still included `ProductCharacteristic` extension and `ProcessCharacteristic`. This slice narrows it once more to exactly: `CauseCategoryScheme`, `CauseCategory`, `CauseInfluence` with its status vocabulary, and a functional (non-diagram) review GUI. `ProcessCharacteristic` and anything product-classification-related is out of scope here — see Section 8.
4. **Decision 4 (Man-category boundary) — APPROVED as a permanent constraint.** Enforced in this slice as described in Section 5 below.
5. **Decision 5 (`Evidence` linkage via generic `Relationship`) — APPROVED**, but not exercised in this slice (no `Evidence`-linking UI is required here; the field/mechanism must exist and be usable, not necessarily surfaced yet).

**New scoping decision specific to this slice (not in the original review — stated here for your visibility, not yours to change):** the architecture review models `cause_category_id` as a field on the not-yet-built `ProcessCharacteristic`. Since `ProcessCharacteristic` is deferred, this slice adds `cause_category` directly as an optional field **on the `CauseInfluence` edge itself** — i.e., a specific cause→failure edge can be tagged with which 5M+E bone it belongs to, independent of its source entity type. When `ProcessCharacteristic` is built in a later slice, a `CauseInfluence` sourced from a `ProcessCharacteristic` may either inherit that characteristic's own category or keep an explicit override on the edge — that reconciliation is a future decision, not this slice's problem. Do not build any inheritance logic now; the edge-level field stands alone.

## 1. Exact Scope

Implement, in this order, as separate commits (Section 9):

1. `CauseCategoryScheme` / `CauseCategory` — a configurable classification-scheme library, following the exact same pattern as `EvaluationDefinition` (already implemented and reviewed) — not hardcoded Man/Machine/Material/Method/Measurement/Environment as Python constants, but seeded default data for that 5M+E scheme.
2. `CauseInfluence` — a new first-class domain entity (`fmea_domain/entities.py`) with the status vocabulary from Section 5 of the architecture review, the source/target type restriction from Section 0.1 above, and the edge-level `cause_category` field from Section 0's new scoping note.
3. Django persistence for both (`fmea_app` models, migrations), OFEF export wiring (Section 13 of the architecture review — add to `_ENTITY_TYPES`, same serialization pattern as every other entity).
4. A functional review GUI: create a `CauseInfluence` against an existing `FailureCause`/`FailureMode`/`FailureMechanism`, list/filter `CauseInfluence`s by `status` and `cause_category`, transition `status` (via the connection-logic rules from `OpenFMEA_CauseInfluence_ConnectionLogic_Spec.md` — implement that document's rules exactly, they are this slice's authority for transition validity), and a simple grouped-list view ("Ishikawa board, list form") that, for a given `FailureMode`, lists its linked `CauseInfluence`s grouped by `cause_category`. **This is explicitly not the visual fishbone diagram** — see Section 8.

Nothing beyond this list.

## 2. Exact Allowed / New Files

```text
domain/fmea_domain/entities.py        # add CauseCategoryScheme, CauseCategory, CauseInfluence, CauseInfluenceStatus
domain/fmea_domain/rules.py           # add CauseInfluence transition-validation functions per the connection-logic spec

django_app/fmea_app/models.py         # add CauseCategoryScheme, CauseCategory, CauseInfluence (StableModel subclasses)
django_app/fmea_app/admin.py          # register the three new models
django_app/fmea_app/migrations/000X_causecategoryscheme_causecategory_causeinfluence.py
django_app/fmea_app/management/commands/seed_cause_category_scheme.py   # seeds the default 5M+E scheme, idempotent (mirrors seed_demo's idempotency pattern)

django_app/fmea_app/views.py          # add: cause_influence list/detail/create/transition views, ishikawa_board(failure_mode_stable_id) view
django_app/fmea_app/urls.py           # add routes for the above
django_app/fmea_app/templates/fmea_app/
    cause_influence_list.html
    cause_influence_detail.html
    cause_influence_form.html
    ishikawa_board.html

django_app/fmea_importexport/ofef.py  # add the three new entity types to _ENTITY_TYPES and serialization

docs/domain/cause-influence.md        # the status vocabulary, the source/target restriction, the edge-level cause_category note from Section 0, and a worked example

tests/test_cause_influence_domain.py
tests/test_cause_influence_rules.py
tests/test_cause_influence_django.py
tests/test_ishikawa_board_view.py
tests/test_ofef_export.py             # extend, do not replace — add round-trip cases for the three new types
```

Do not touch `fmea_ingestion/`, `fmea_review/`, `fmea_ai/`, or `reconstruction.py` in this slice — this is a domain-model and review-GUI slice, not an ingestion slice. If you find a genuine need to touch one of them, stop and report why.

## 3. Allowed Dependencies

None new. Everything needed already exists in `requirements.txt`.

## 4. Prohibited Dependencies / Constructs

No `ProcessCharacteristic` entity, no `ClassificationScheme`/`ClassificationTerm` (that is `ProductCharacteristic`-side taxonomy, not this slice — do not build it "since you're in the area"). No rename of `Characteristic`. No visual/canvas/diagram rendering library (no `d3`, no `mermaid`, no drag-and-drop JS) — the Ishikawa board in this slice is a plain grouped HTML list, per Section 0's narrowing. No `LessonLearned` entity. No Control Plan entity or hook. No coverage-metric query implementations (Section 12 of the architecture review — future work). No AI wiring of any kind in this slice — `classify_ishikawa_category` stays `unavailable` on both providers; a *prepared, not-yet-wired* prompt for it exists separately in `OpenFMEA_AIProvider_IshikawaClassificationPromptSpec.md` and must not be activated here. No automatic status promotion — every `CauseInfluence` status transition in this slice is an explicit human action via the GUI, never automatic, never AI-driven.

## 5. Required Data Models

`fmea_domain/entities.py` (framework-free):

- `CauseCategoryScheme`: `DomainEntity` subtype. Fields: `name: str`, `description: str`. Mirrors `EvaluationDefinition`'s "a named, referenceable scheme" shape.
- `CauseCategory`: `DomainEntity` subtype. Fields: `scheme_id: str` (references `CauseCategoryScheme.stable_id`), `name: str`, `description: str`, `sort_order: int`. No hardcoded Man/Machine/... as an enum — these are seeded *rows*, not code constants. Seed data (via the management command, Section 2) creates one `CauseCategoryScheme` named `"Ishikawa 5M+E (default)"` and six `CauseCategory` rows: Man, Machine, Material, Method, Measurement, Environment, `sort_order` 1–6.
- `CauseInfluenceStatus` enum: `SUSPECTED, POSSIBLE, CORRELATED, EXPERIMENTALLY_SUPPORTED, CONFIRMED_ROOT_CAUSE, REJECTED` — exact vocabulary from Section 5/14 of the architecture review.
- `CauseInfluence`: `DomainEntity` subtype. Fields: `source_id: str`, `source_type: Literal["FailureCause", "FailureMechanism"]` (explicit, validated — do not infer type by probing which table has the id), `target_id: str`, `target_type: Literal["FailureMode", "FailureCause"]`, `influence_type: str` (free text, e.g. `"produces"`, `"deviation"`, `"influences"` — not a closed enum, matches Section 5's extensibility requirement), `status: CauseInfluenceStatus`, `cause_category_id: str | None` (the Section 0 edge-level scoping note — optional, references `CauseCategory.stable_id`), `confidence: float | None`, `strength: str | None`, `evidence_ids: tuple[str, ...]` (empty tuple default — populated later via the `Relationship` mechanism per Decision 5, not built out in this slice), `source_context: str` (e.g. `"FMEA"`, `"8D"`, `"CAPA"` — plain string, no new entity), `review_note: str`.
- Validate on construction: `source_type`/`target_type` must be one of the allowed literals (Section 0.1); a `CauseInfluence` targeting a `FailureMode` with `status=CONFIRMED_ROOT_CAUSE` is invalid — a confirmed root cause must target a `FailureCause` (this is the promotion rule from Section 5 of the architecture review, made a hard validation rule, not just a convention).

`fmea_app/models.py` (Django): `CauseCategoryScheme`, `CauseCategory`, `CauseInfluence` as `StableModel` subclasses mirroring the domain shapes field-for-field. `CauseInfluence.source_id`/`target_id` stay as plain `CharField` stable_id references (not Django FKs to a union of model types) — same pattern the architecture review's Section 5 recommends for a type-agnostic edge; validate `source_type`/`target_type` against the actual referenced row's existence at the service layer (Section 6), not via a DB constraint that can't express a polymorphic reference.

## 6. Required APIs

Django views under `fmea_app/`:

- `GET /cause-influences/` — list, filterable by `status` and `cause_category_id` query params.
- `GET /cause-influences/new/?target_type=...&target_id=...` — form pre-populated with the target (linked to from a `FailureMode`/`FailureCause` detail page — if those detail pages don't already exist from Phase B, add the minimal link only, do not build new CRUD for `FailureMode`/`FailureCause` themselves).
- `POST /cause-influences/create/` — validates `source_id`/`target_id` actually exist as the declared `source_type`/`target_type` before saving; rejects with a clear error otherwise.
- `GET /cause-influences/<stable_id>/` — detail, showing current status and the set of statuses it may legally transition to next (per the connection-logic spec).
- `POST /cause-influences/<stable_id>/transition/` — body includes `new_status` and, when required by the connection-logic spec (e.g. moving to `CONFIRMED_ROOT_CAUSE`), the `failure_cause_stable_id` to promote/retarget to. Calls the domain-rule validator from `fmea_domain/rules.py` before saving — an illegal transition is rejected with the specific reason, never silently coerced.
- `GET /failure-modes/<stable_id>/ishikawa-board/` — the grouped-list view: every `CauseInfluence` targeting this `FailureMode` (directly, or transitively via a `FailureCause` that itself is targeted... **no** — for this slice, direct edges only: everything with `target_id=failure_mode.stable_id` OR `target_id` in `{fc.stable_id for fc in failure_causes_of_this_mode}`. Do not implement multi-hop chain traversal in this slice, that is future work per Section 6 of the architecture review), grouped by `cause_category` (an "Uncategorized" group for edges with `cause_category_id=None`).

## 7. Required Migrations

One migration adding `CauseCategoryScheme`, `CauseCategory`, `CauseInfluence`. Do not touch any existing `fmea_app`/`fmea_review` migration.

## 8. Required Validation, Error Handling, and Explicit Exclusions

- `source_type`/`target_type` are validated against Section 0.1's allowed sets at both the domain layer (construction) and the service layer (does the referenced row actually exist and match the declared type) — a `CauseInfluence` pointing at a nonexistent or wrong-type stable_id is rejected, not silently created.
- Status transitions are validated exclusively through the rules in `OpenFMEA_CauseInfluence_ConnectionLogic_Spec.md` — implement that document precisely; if you find a gap or contradiction in it, stop and report rather than filling the gap yourself.
- Man-category boundary (Decision 4): `CauseCategory` rows have no field for subjective/health data, and neither does `CauseInfluence`. Add an explicit code comment on the `CauseCategory` model and in `docs/domain/cause-influence.md` stating this is a permanent constraint, not a first-pass omission, per the architecture review Section 4 and Decision 4.
- **Never** build `ProcessCharacteristic`, `ClassificationScheme`/`ClassificationTerm`, or rename `Characteristic` in this slice (Section 0.2/0.3).
- **Never** wire `classify_ishikawa_category` into `OllamaProvider` or call it from any view in this slice — it stays `unavailable`, exactly as Slice 1's instruction already required, unchanged by this slice.
- **Never** auto-transition a `CauseInfluence`'s status, and never auto-promote a candidate cause to `CONFIRMED_ROOT_CAUSE` — every transition in this slice is an explicit `POST` from a human action.
- **Never** build the visual fishbone/canvas GUI — `ishikawa_board.html` is a plain grouped HTML list (headings per category, an unordered list of edges under each), styled minimally, no JS diagram library. The visual version is explicitly a separate, later prompt gated on the user supplying reference images.
- Do not implement coverage-metric queries, `LessonLearned`, or any Control Plan hook.

## 9. Required Tests, in Commit Order

**Commit 1 — domain entities + rules.** `CauseCategoryScheme`/`CauseCategory`/`CauseInfluence`/`CauseInfluenceStatus` in `fmea_domain/entities.py`; `test_cause_influence_domain.py` covers construction, the `source_type`/`target_type` validation, and the "`CONFIRMED_ROOT_CAUSE` must target a `FailureCause`" rule. `fmea_domain/rules.py` transition-validation functions per the connection-logic spec; `test_cause_influence_rules.py` covers every legal and illegal transition pair from that spec, including the required-context cases (e.g. promoting to `CONFIRMED_ROOT_CAUSE` without a target `FailureCause` is rejected). Both files must pass the existing import-isolation test (`test_no_django_imports.py` — extend its list of covered modules, do not duplicate the test).

**Commit 2 — Django models, migration, admin, seed command.** `fmea_app/models.py` additions, the migration, `admin.py` registration, `seed_cause_category_scheme.py` (idempotent — running it twice does not create duplicate rows, mirror `seed_demo`'s pattern). `test_cause_influence_django.py`: seeding creates exactly one scheme and six categories in the right `sort_order`; running the seed command twice is a no-op the second time; `CauseInfluence` model-level validation matches the domain-level rule.

**Commit 3 — OFEF export.** Add the three types to `fmea_importexport/ofef.py`. Extend `test_ofef_export.py` with round-trip serialize/deserialize cases for all three, and confirm the existing `"not": {"required": ["id"]}` guardrail still applies to them.

**Commit 4 — review GUI + Ishikawa board.** Views, urls, templates from Section 6. `test_ishikawa_board_view.py`: creating a `CauseInfluence` from a `FailureCause` to a `FailureMode` with a `cause_category` makes it appear in that `FailureMode`'s board view under the right category heading; an edge with no `cause_category` appears under "Uncategorized"; an illegal transition attempt (per the connection-logic spec) returns a clear error and does not change the stored status; a legal transition to `CONFIRMED_ROOT_CAUSE` without a target `FailureCause` is rejected with a clear error naming what's missing.

Each commit must leave `python -B manage.py check`, `python -B manage.py makemigrations --check --no-input`, and the full test suite passing before moving to the next commit.

## 10. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --no-input
python -B -m pytest
```

## 11. Acceptance Criteria

1. `CauseCategoryScheme`/`CauseCategory` exist, are seeded via an idempotent management command, and are not hardcoded as Python constants anywhere reachable by application logic (the seed *data* names Man/Machine/etc., the *schema* does not).
2. `CauseInfluence` exists at both the domain and Django layers, restricted in this slice to `{FailureCause, FailureMechanism}` sources and `{FailureMode, FailureCause}` targets, with the exact six-value status vocabulary from the architecture review.
3. A `CauseInfluence` cannot reach `CONFIRMED_ROOT_CAUSE` status while targeting a `FailureMode` — only while targeting a `FailureCause` — enforced at both the domain layer and the transition endpoint.
4. Every status transition is an explicit, validated human action; none happens automatically or via AI.
5. The Ishikawa board view groups a `FailureMode`'s linked causes by `cause_category`, including an "Uncategorized" group, and contains no diagram/canvas rendering.
6. `classify_ishikawa_category` remains `unavailable` on both AI providers; nothing in this slice's diff touches `fmea_ai/`.
7. `ProcessCharacteristic`, `ClassificationScheme`/`ClassificationTerm`, and the `Characteristic`→`ProductCharacteristic` rename do not appear anywhere in this slice's diff.
8. All four commits pass `manage.py check`, `makemigrations --check`, and the full test suite independently.
9. After implementation here, mirror the change into `open_fmea_training_set` (same discipline as every prior slice) and rebuild the training EXE — report the exact candidate/test counts from a clean run in both locations, the way every prior round has, so this can be independently re-verified rather than trusted from the status report alone.

## 12. Explicit Exclusions (restated for emphasis)

`ProcessCharacteristic`, `ClassificationScheme`/`ClassificationTerm`, the `Characteristic`→`ProductCharacteristic` rename, `LessonLearned`, Control Plan entities/hooks, coverage-metric query implementations, multi-hop causal-chain traversal, any visual/canvas/diagram GUI, any AI wiring of `classify_ishikawa_category`, any automatic status transition, embeddings/RAG, Celery/Redis, Kubernetes, and anything already excluded by the Slice 1 instruction that still applies generally to this codebase.

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

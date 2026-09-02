# Codex Implementation Instruction — ProductCharacteristic Rename, ProcessCharacteristic, and Characteristic-Linking (Slice: Characteristics-Linking-1)

Status: Approved for implementation, **sequenced strictly after** `Codex_Instruction_CauseInfluence_CauseCategoryScheme_IshikawaBackend_Slice.md` is implemented and independently verified. This slice extends `CauseInfluence`'s allowed source/target types — it cannot be built first without leaving `CauseInfluence` in an inconsistent state.

Authority, in order: same chain as the Ishikawa-backend instruction; additionally subordinate to that instruction's own output, since this slice modifies fields it establishes (`CauseInfluence.source_type`/`target_type` literals).

## 1. Exact Scope

Implement, in this order, as separate commits:

1. Rename `fmea_app.Characteristic` → `fmea_app.ProductCharacteristic` (Decision 2 of `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md`), with a data migration for the existing seeded demo row(s) — no data loss, no new required fields on the renamed model in this step.
2. Add `ProcessCharacteristic` (Section 3 of the architecture review) as a new entity — instance-level, tied to one `Process`/`Operation`, not yet a reusable library item (explicit scope note already in the review — do not build library-ization here).
3. Extend `CauseInfluence.source_type` to also allow `"ProcessCharacteristic"`, and `CauseInfluence.target_type` to also allow `"ProductCharacteristic"` — this is the actual "characteristics linking" the user asked for: a `ProcessCharacteristic` can now be the source of an influence edge, and a `ProductCharacteristic` can now be its target, composing with the existing `FailureCause`/`FailureMode` types from the Ishikawa-backend slice to realize the full chain from Section 1/6 of the architecture review (`ProcessCharacteristic → ProductCharacteristic → FailureMode → FailureEffect`).
4. Update every existing reference to `Characteristic` across the codebase (ingestion mapping, review templates, admin, OFEF export) to `ProductCharacteristic` — this is a rename, not a re-implementation; behavior must not change beyond the name and the one new optional field noted in Section 5.

## 2. Exact Allowed / New Files

```text
domain/fmea_domain/entities.py         # rename Characteristic -> ProductCharacteristic; add ProcessCharacteristic
domain/fmea_domain/rules.py            # extend CauseInfluence source/target type validation (no new rule categories, just widen the allowed sets from the Ishikawa-backend slice)

django_app/fmea_app/models.py          # rename model; add ProcessCharacteristic; widen CauseInfluence type choices
django_app/fmea_app/migrations/000X_rename_characteristic_to_productcharacteristic.py   # RenameModel + data migration
django_app/fmea_app/migrations/000Y_processcharacteristic.py
django_app/fmea_app/admin.py           # update registration name; register ProcessCharacteristic
django_app/fmea_app/services.py        # rename references; add ProcessCharacteristic promotion path mirroring the existing _optional_context_model pattern

django_app/fmea_ingestion/candidates.py         # VALID_DOMAIN_TYPES: "Characteristic" -> "ProductCharacteristic" (breaking rename - see Section 8)
django_app/fmea_ingestion/mapping/column_mapping.py    # update mapped HeaderMapping domain_type strings
django_app/fmea_ingestion/mapping/domain_mapping.py    # update STRUCTURED_EXTRACTION_SCHEMA enum value
django_app/fmea_review/services.py     # update _domain_object_exists reference
django_app/fmea_review/templates/fmea_review/candidate_detail.html   # update label/field references
django_app/fmea_importexport/ofef.py   # update _ENTITY_TYPES entry name; add ProcessCharacteristic

django_app/fmea_app/views.py           # add process_characteristic list/detail/create views; process_flow(process_stable_id) panel view; extend cause_influence_form to accept ProcessCharacteristic/ProductCharacteristic as source/target options
django_app/fmea_app/urls.py
django_app/fmea_app/templates/fmea_app/
    process_characteristic_list.html
    process_characteristic_detail.html
    process_characteristic_form.html
    process_flow.html                   # the Process Characteristics panel, Section 6

docs/domain/product-process-characteristics.md   # documents the rename, ProcessCharacteristic's instance-level scope, and the widened CauseInfluence type sets

tests/test_product_characteristic_rename.py       # renamed from any existing Characteristic-specific test - confirm no behavior change beyond the name
tests/test_process_characteristic_domain.py
tests/test_cause_influence_characteristics_linking.py   # the new source/target combinations specifically
```

Grep the entire repository for `Characteristic` before starting and enumerate every hit — the list above is based on the files already known to reference it from prior review rounds, but this instruction requires you to find and update every remaining reference, not just the ones listed; report any file touched that isn't in this list and why.

## 3. Allowed Dependencies

None new.

## 4. Prohibited Dependencies / Constructs

No `ClassificationScheme`/`ClassificationTerm` (Section 2 of the architecture review — multi-classification of `ProductCharacteristic` against Legal/Safety/Functional/etc. is explicitly a separate, still-unbuilt increment; do not build it "since you're renaming the model anyway"). No library-ization of `ProcessCharacteristic` (explicit scope note in Section 3 of the review). No coverage-metric queries. No `LessonLearned`. No AI wiring changes beyond the rename propagating into existing prompt/schema strings (Section 8 below).

## 5. Required Data Models

`fmea_domain/entities.py`:

- `ProductCharacteristic` — identical shape to today's `Characteristic` (`name`, `description`, `is_special`, `requirement_id: str | None`) plus one new optional field: `primary_classification_id: str | None` (reserved for the future `ClassificationScheme` work — added now as a nullable field so the later classification increment is additive, not another migration-requiring rename; **do not populate or validate it in this slice**, it stays `None` for every object this slice creates).
- `ProcessCharacteristic` — new. Fields: `name: str`, `description: str`, `operation_id: str` (references the existing `Process`/`Operation` entity — required, per Section 3's "instance-level, tied to one Operation" scope), `cause_category_id: str | None` (references `CauseCategory` from the Ishikawa-backend slice — optional, mirrors the reasoning in that slice's Section 0 edge-level note: a `ProcessCharacteristic` may carry its own default category, which a `CauseInfluence` sourced from it may inherit or override — **do not build the inheritance/override reconciliation logic in this slice either**; this field is stored but not yet read by any `CauseInfluence` creation logic), `attributes: dict` (open, typed-but-flexible bag per Section 3's stated pattern — nominal/observed/limit/state-shaped values live here, no fixed schema).

`fmea_app/models.py`: `ProductCharacteristic` (renamed `StableModel` subclass, `primary_classification_id` added as nullable), `ProcessCharacteristic` (new `StableModel` subclass). `CauseInfluence.source_type`/`target_type` choices widen from `{"FailureCause", "FailureMechanism"}`/`{"FailureMode", "FailureCause"}` to `{"FailureCause", "FailureMechanism", "ProcessCharacteristic"}`/`{"FailureMode", "FailureCause", "ProductCharacteristic"}` — no other field changes on `CauseInfluence`.

## 6. Required APIs and GUI

- Rename propagates through every existing `Characteristic`-related view/URL/template to `ProductCharacteristic` naming (URLs may keep their existing paths if renaming them would break bookmarks/tests unnecessarily — renaming Python/template identifiers is required, renaming URL paths is optional, your call, but report which you chose).
- New: `GET /process-characteristics/`, `GET /process-characteristics/<stable_id>/`, `GET/POST /process-characteristics/new/` — same rigor as the existing `fmea_app` manual CRUD views from Phase B (mirror their pattern, do not invent a new one).
- `cause_influence_form` (from the Ishikawa-backend slice) gains `ProcessCharacteristic` and `ProductCharacteristic` as selectable source/target types respectively, alongside the existing `FailureCause`/`FailureMechanism`/`FailureMode`/`FailureCause` options.

**Process Characteristics panel — concrete GUI spec, grounded in a second reference mockup the user supplied after this instruction was first drafted.** The mockup showed a "Process Flow" step list for a `Process` (an ordered sequence of `Operation`s — both already exist in the domain model per Section 3 of the architecture review), where selecting a step shows two tables: that operation's `ProcessCharacteristic`s (name/target/spec/unit — i.e. the `attributes` bag rendered as a table), and the `ProductCharacteristic`s it's linked to via `CauseInfluence` ("Linked Product Characteristics"). Build this as a real, working page, using the design system and component patterns from `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` (cards, tables, status badges — not a new visual language):

- `GET /processes/<stable_id>/flow/` — lists the `Process`'s `Operation`s in sequence (a simple ordered list/stepper, plain HTML/CSS per the GUI-shell slice's "no new JS/diagram library" rule — not the mockup's circular-node graphic, a clean numbered list is sufficient and stays inside that slice's tooling constraints). Selecting an `Operation` (via a query param or a sub-route, your call) shows:
  - **Process Characteristics table** for that `Operation`: every `ProcessCharacteristic` where `operation_id` matches, rendered as name + whatever keys exist in its `attributes` dict (render generically — a two-column key/value table per characteristic, or promote common keys like `target`/`spec`/`unit` to real columns only if you find they're consistently present; don't hardcode assumptions about `attributes`' shape beyond what Section 5 already specifies).
  - **Linked Product Characteristics table**: every `ProductCharacteristic` reachable as the `target_id` of a `CauseInfluence` whose `source_id` is one of this operation's `ProcessCharacteristic`s, showing the `ProductCharacteristic`'s name and the `CauseInfluence`'s `status` (as a status badge, reusing the badge component from the GUI-shell slice) — **not** a Type/Criticality column. The reference mockup showed Type ("Safety"/"Optical"/"Decorative") and Criticality ("Critical"/"High") for each linked characteristic — that data comes from `ClassificationScheme`/`ClassificationTerm`, which remains **not approved for implementation** (`OpenFMEA_DNA_CoreReference.md` Section 6). Omit those two columns entirely rather than faking them or hardcoding placeholder values — an incomplete-but-honest table beats a fabricated one, consistent with every AI-boundary rule elsewhere in this project applied here to GUI data too.
- Do not build: a global "System / Product / Process" context switcher, an "Open-EQMS" integration badge or context panel, a "Characteristics Flow" chain-diagram widget, or an "FMEA Team" panel — all present in the second mockup, none backed by anything that exists or is approved (no cross-system integration path exists per the architecture review Section 15; team/collaboration has no backend at all). If you think one of these is trivial to stub, stop and report rather than adding it.

## 7. Required Migrations

Two migrations: (a) `RenameModel` for `Characteristic` → `ProductCharacteristic` plus `AddField` for `primary_classification_id` (nullable, no data migration needed since it's nullable-and-unpopulated), (b) `CreateModel` for `ProcessCharacteristic`. Do not combine them with unrelated changes.

## 8. Required Validation, Error Handling, and Explicit Exclusions

- **This is a breaking rename inside `fmea_ingestion`'s `VALID_DOMAIN_TYPES`.** Any `ImportCandidateRecord` already persisted with `suggested_domain_type="Characteristic"` (real data may already exist in `open_fmea_training_set`'s accumulating database, per the standing risk noted in `Claude_Review_IngestionRobustnessFix_CharacteristicSupport_AICorpusExport_TrainingSetSplit.md` Finding 2) must not become silently unrecognized. Add a data migration or a one-time management command that updates existing `ImportCandidateRecord.suggested_domain_type` values from `"Characteristic"` to `"ProductCharacteristic"` — check both `open_fmea` and `open_fmea_training_set` databases for any such rows before considering this step done, and report the count found and updated in each. This is exactly the kind of drift risk that review flagged; do not let this slice be the moment it actually bites.
- **Never** populate or validate `primary_classification_id` — it must remain `None`/unused output of this slice, reserved for later.
- **Never** build `ClassificationScheme`/`ClassificationTerm` or any classification-assignment UI.
- **Never** implement `ProcessCharacteristic` library reuse (a "save as reusable characteristic" action, a library browser) — instance-level only.
- **Never** implement the `cause_category_id` inheritance/override reconciliation between a `ProcessCharacteristic` and a `CauseInfluence` sourced from it — both fields exist independently and neither reads the other yet.
- The widened `CauseInfluence` source/target validation must still enforce the domain-layer rule from the Ishikawa-backend slice that `CONFIRMED_ROOT_CAUSE` requires `target_type == "FailureCause"` — a `CauseInfluence` targeting a `ProductCharacteristic` can reach at most `EXPERIMENTALLY_SUPPORTED` in this slice, since "root cause" is specifically a `FailureCause`-shaped concept per the architecture review; a request to confirm one targeting `ProductCharacteristic` is rejected with a clear reason, not silently allowed.

## 9. Required Tests, in Commit Order

**Commit 1 — rename.** `test_product_characteristic_rename.py`: every existing test that referenced `Characteristic` now passes unchanged in substance against `ProductCharacteristic`; the ingestion pipeline still produces `ProductCharacteristic`-typed candidates from the same real sample files with the same counts as the last verified run (`FMEA_templates.xlsx` 1904 candidates / `FMEA_442710252570.00.xlsx` 316 / `PPAP_Prirobnica.XX2.xlsx` 198, per the last independent verification) — re-run against the real files and confirm the counts are unchanged, since this is a pure rename and must not alter parsing behavior. Include the `ImportCandidateRecord` backfill migration/command and its own test (seed a row with the old type string, run the migration/command, assert it now reads the new one).

**Commit 2 — ProcessCharacteristic.** Domain + Django model, migration, admin, minimal CRUD views. `test_process_characteristic_domain.py`: construction, `operation_id` required, `attributes` accepts an arbitrary dict.

**Commit 3 — characteristics linking + Process Characteristics panel.** Widen `CauseInfluence` type sets; build the `process_flow` view from Section 6. `test_cause_influence_characteristics_linking.py`: a `CauseInfluence` from a `ProcessCharacteristic` to a `ProductCharacteristic` is legal and appears correctly in both entities' related-edges views; a `CauseInfluence` from a `ProcessCharacteristic` to a `ProductCharacteristic` attempting `CONFIRMED_ROOT_CAUSE` is rejected; the full chain `ProcessCharacteristic → ProductCharacteristic → FailureMode` (two edges) is constructible and each edge validates independently. `test_process_flow_view.py`: selecting an `Operation` shows exactly its own `ProcessCharacteristic`s (not another operation's); the Linked Product Characteristics table shows only `ProductCharacteristic`s actually reachable via a `CauseInfluence` from that operation's characteristics; the response contains no "Type" or "Criticality" column/label (locks in the Section 6 exclusion the same way `test_gui_navigation_scope.py` locks in the GUI-shell slice's nav scope).

Each commit passes `manage.py check`, `makemigrations --check`, and the full suite before the next.

## 10. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --no-input
python -B -m pytest
```

## 11. Acceptance Criteria

1. `Characteristic` no longer exists anywhere in the codebase except as historical text in architecture documents; `ProductCharacteristic` fully replaces it with identical behavior plus the one new dormant field.
2. Real-file ingestion counts are unchanged after the rename (re-verified against all three sample workbooks, not assumed).
3. Any pre-existing `ImportCandidateRecord` rows using the old type string are found and migrated in both `open_fmea` and `open_fmea_training_set`, with counts reported.
4. `ProcessCharacteristic` exists, instance-level only, no library mechanism.
5. `CauseInfluence` accepts `ProcessCharacteristic`→`ProductCharacteristic` edges; such edges cannot reach `CONFIRMED_ROOT_CAUSE`.
6. `primary_classification_id` exists on `ProductCharacteristic`, is nullable, and is not populated or validated anywhere in this slice's diff.
7. All three commits independently pass `manage.py check`, `makemigrations --check`, and the full test suite.
8. Mirrored into `open_fmea_training_set` and the training EXE rebuilt, with a clean-run report matching the established verification discipline.

## 12. Explicit Exclusions (restated for emphasis)

`ClassificationScheme`/`ClassificationTerm`, any classification-assignment UI, `ProcessCharacteristic` library/reuse mechanism, `cause_category_id` inheritance/override logic, any change to `CauseInfluence`'s status-transition rules beyond widening the type sets, coverage-metric queries, `LessonLearned`, Control Plan hooks, any AI-provider wiring change beyond string literals updated for the rename.

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

# Codex Implementation Instruction — Evidence & Tests / Validation Trajectory (Slice F)

Status: Approved for implementation, 2026-09-04. Builds `OpenFMEA_EvidenceTests_ArchitectureReview.md`'s six decisions, now treated as confirmed, folding in Mockup 14's lifecycle-phase and "one entity, two views" findings per that review's own amendment. Picked as part of pushing every remaining mockup toward implementation-readiness, following the same narrow-scope-per-slice pattern as every prior slice in this project.

Authority, in order: same chain as prior slices (`OpenFMEA_DNA_CoreReference.md` Sections 2/6/9, `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` for visual language and tooling constraints); additionally subordinate to `OpenFMEA_EvidenceTests_ArchitectureReview.md` (design authority for this slice — its Section 3 proposed design and Section 4/4a's six decisions).

Grounded directly in the real code before writing this: `models.py`'s `StableModel`, `ResponsibleRole`, `FailureMode`, `RecommendedAction`, `Evidence`, `EffectivenessVerification`; `forms.py`'s `RecommendedActionForm`/`ProcessCharacteristicForm` (ModelForm + queryset-narrowing pattern); `urls.py`/`views.py`'s risk-matrix and process-characteristic routes (GET-filter pattern); `_sidebar.html`'s current `.nav-group`/`.nav-group-title`/`.nav-link` markup; `tests/test_gui_navigation_scope.py`'s current allow/deny-list assertions (its `"Evidence & Tests"` entry is currently in the *unbuilt* tuple — Section 4 below requires flipping it, the same kind of intentional, called-out change Slice D made for "FMEA ANALYSIS").

## 0. Decisions for this slice

Mockup 10 ("Evidence & Tests") and Mockup 14 ("Validation Trajectory") are two views over one underlying entity, not two separate things — this project's own architecture review already reached that conclusion (Section 4a of `OpenFMEA_EvidenceTests_ArchitectureReview.md`). All six of that review's decisions are now CONFIRMED, using the review's own recommended answers:

1. **File attachments — deferred.** No file/attachment storage or upload UI in this slice. `ValidationTest` is fully useful without it; storage/packaging policy (this app ships as a PyInstaller EXE) gets its own decision later.
2. **Owner — a placeholder via the existing `ResponsibleRole` catalog.** Not a new person/user field, not a real per-person account. Same pattern `RecommendedAction.responsible_role` already uses.
3. **Relationship to `EffectivenessVerification` — leave it alone.** No migration, no deletion, no field change to `Evidence` or `EffectivenessVerification`. New records going forward use `ValidationTest` instead (for the "did this action work" case, when a test exists specifically to verify one action), but nothing existing changes and no old data is touched or migrated.
4. **Nav/page scope — the lighter first cut.** A table + create/edit form + detail page only. No stat-card dashboard, no donut charts, no Chart.js of any kind (Chart.js was decided as this project's eventual charting library in `OpenFMEA_ChartingLibrary_ArchitectureDecision.md`, but is not yet wired into anything and is not required for this slice to be useful).
5. **Lifecycle phase — one `ValidationTest` row belongs to one lifecycle phase.** Not a structure where one test can appear at multiple phases over its life. `OpenFMEA_RiskTrajectoryPropagation_ArchitectureDecision.md` was checked and does not exist as an approved document in this project as of this writing, so this instruction is self-contained: it defines the six-value `lifecycle_gate` enum directly below rather than importing it from elsewhere. If that document is later written and uses different exact values, that is a separate, later migration decision — do not block this slice on it.
6. **"Test Plan" grouping entity — not in scope.** No `TestPlan` model, no `test_plan` FK on `ValidationTest` in this slice. Leave room for one later (a nullable FK can be added without reshaping anything decided here) but do not build it now, and do not add a placeholder/stub field for it either.

### `ValidationTest` field list (firm, per the review's Section 3 proposed design)

| Field | Type | Notes |
|---|---|---|
| `failure_mode` | FK to `FailureMode`, required, `on_delete=models.CASCADE`, `related_name="validation_tests"` | Matches the mockup's "DFMEA Link: F-01/FM-01" — a test links to the FMEA line item under test directly, not only through an action. |
| `recommended_action` | FK to `RecommendedAction`, nullable, `on_delete=models.SET_NULL`, `related_name="validation_tests"` | For when a test exists specifically to verify one action's effectiveness. Optional — most tests will not set this. |
| `test_type` | `CharField` + choices | Closed enum: `Validation` / `Verification` / `Reliability` / `Acceptance`. |
| `method` | `CharField(max_length=255)`, blank allowed | Free text, e.g. "Photometric Test (Lab)". |
| `objective` | `TextField`, blank allowed | Free text. |
| `nominal_target` | `CharField(max_length=255)`, blank allowed | Free text capturing "Nominal/Target" as one field — not split into structured numeric fields in this increment. |
| `acceptance_criteria` | `TextField`, blank allowed | Free text — the pass/fail bar description. |
| `result_status` | `CharField` + choices | Closed enum: `Pass` / `Fail` / `Pending`. A simple field, not a JSON blob — this is the structured result badge from the mockup. |
| `planned_date` | `DateField`, nullable | |
| `executed_date` | `DateField`, nullable | Deliberately a second, separate field from `planned_date` (today's `EffectivenessVerification.verified_at` has only one date — this is a real, decided difference for the new entity). |
| `priority` | `CharField` + choices | Closed enum: `High` / `Medium` / `Low`. |
| `owner` | FK to `ResponsibleRole`, nullable, `on_delete=models.SET_NULL`, `related_name="validation_tests"` | Placeholder per Decision 2 — not a person/login account. |
| `lifecycle_gate` | `CharField` + choices | Closed enum, exactly six values, in this order: `Concept/Design`, `Design Verification`, `Process Validation`, `Pre-Production`, `Serial Production`, `Current`. Use short internal values (e.g. `concept_design`, `design_verification`, `process_validation`, `pre_production`, `serial_production`, `current`) with the display labels above via Django `choices` — mirrors how `FMEA.fmea_type`/`ActionStatus` already pair an internal value with a display label. |
| `status` | `CharField` + choices | Closed enum: `Planned` / `In Execution` / `Completed` / `On Hold` / `Cancelled`. This is `ValidationTest`'s OWN status workflow — deliberately distinct from `ActionStatus` (which is `open`/`in_progress`/`completed`/`verified`/`cancelled`). No enforced transitions between values, consistent with how `ActionStatus` itself has no enforced transitions anywhere in this app today (a free-choice dropdown, same as `RecommendedActionForm`'s `status` field). |

A `name` field (`CharField(max_length=255)`, required) is also needed — every other `StableModel` subtype in this codebase has one for `__str__`/table display, and none of the six decisions above says otherwise; add it without treating it as a seventh open decision.

`ValidationTest(StableModel)` — same base class, same `to_domain()`-free pattern as every other Phase-B-only model added directly in `fmea_app/models.py` without a matching `fmea_domain/entities.py` counterpart is NOT the precedent here: check `models.py` — every model in this file *does* have a `DomainX`/`to_domain()` pair. Add the matching pattern: a framework-free `ValidationTest` dataclass in `domain/fmea_domain/entities.py` (fields matching the table above, `failure_mode_id`/`recommended_action_id`/`owner_id` as `stable_id` string references, not raw FKs — same as every other domain entity) plus a `to_domain()` method on the Django model, exactly mirroring how `FailureMode`/`RecommendedAction` already do it. Add a matching `TestType`, `ValidationResultStatus`, `Priority` (if not already named something reusable — check `fmea_domain` for an existing `Priority`-shaped enum before adding a new one; if none exists, add one scoped to this entity only), `LifecycleGate`, and `ValidationTestStatus` enum to `fmea_domain`, matching the closed-vocabulary pattern `ActionStatus`/`CauseInfluenceStatus`/`ReviewStatus` already use (DNA rule 6 — a closed structural vocabulary, not organization-configurable, is a Python enum; this is not a `CauseCategoryScheme`-style organization-configurable taxonomy, so an enum is correct here, not a scheme+rows pattern).

## 1. Exact Scope

1. **New `ValidationTest` model + migration.** `fmea_app/models.py` (Django model, `StableModel` subclass, per the field table above) and the matching framework-free entity + enums in `domain/fmea_domain/entities.py`. One new migration file.
2. **A new list page** — route `/validation-tests/`, name `fmea:validation_test_list`. A table with columns: FailureMode (name, linking to `fmea:fmea_detail` via `validation_test.failure_mode.fmea.stable_id`), Test Type, Method, Result Status (as a status badge, reusing the existing `_status_badge.html` component), Planned Date, Executed Date, Priority, Owner, Status, Lifecycle Gate. Standard GET-form filters (same pattern as `risk_matrix_top.html`'s method selector and `process_characteristic_list`'s filters): `<select>` dropdowns for `test_type`, `status`, and `lifecycle_gate`, submitted via `method="get"`, each defaulting to "All" (no filter applied) when omitted or empty. No AJAX — a plain form submit, matching this app's `_body-and-request.GET` convention throughout.
3. **A create/edit form.** `ValidationTestForm` (`forms.py`, `ModelForm`) covering every field in the table above (`name`, `failure_mode`, `recommended_action`, `test_type`, `method`, `objective`, `nominal_target`, `acceptance_criteria`, `result_status`, `planned_date`, `executed_date`, `priority`, `owner`, `lifecycle_gate`, `status`). `recommended_action` and `owner` are not required (mirror `RecommendedActionForm`'s `responsible_role` — `required = False` set in `__init__`, queryset ordered by `name`). `planned_date`/`executed_date` use `forms.DateInput(attrs={"type": "date"})` widgets, matching `RecommendedActionForm.due_date`. `objective`/`acceptance_criteria` use `forms.Textarea(attrs={"rows": 2})`, matching every other `description`-shaped field in this codebase. A view (`new_validation_test` or `create_validation_test`, your call to match this file's existing naming split between `new_x`/`create_x` pairs vs. single combined views — check the existing `process_characteristic`/`cause_influence` view pairs and follow whichever pattern is already used for a similarly-shaped entity) renders and processes it; on success, redirect to the new test's detail page.
4. **A detail page** — route `/validation-tests/<str:stable_id>/`, name `fmea:validation_test_detail`. Shows every field from the table above, plus a link to the linked `FailureMode` (via `fmea:fmea_detail`) and, if `recommended_action` is set, a link to it (via `fmea:action_detail`); if not set, show a plain "Not linked to an action" (or equivalent) message — same "linked / not linked" display pattern `action_detail.html` already uses for its own `failure_cause`/`failure_mode` link.
5. **New sidebar entry.** This project's canonical sidebar structure (`OpenFMEA_DNA_CoreReference.md` Section 10) places "Evidence & Tests" under a "VALIDATION & CHANGE" group, alongside "Validation Trajectory" and "Change Impact" — neither of which has any real backend yet and neither of which is built by this slice. Per the same rule Slice D used to add "FMEA ANALYSIS" (add a nav group only once something real exists under it, per Slice A's original "no navigation for anything not built yet" rule): create the `VALIDATION & CHANGE` group now, with exactly **one** link — "Evidence & Tests" → `fmea:validation_test_list`. Do not add "Validation Trajectory" or "Change Impact" as links or disabled placeholders — neither exists.

Nothing beyond this list. No file storage, no real per-person Owner, no dashboard/stat cards, no charts, no `TestPlan` entity, no change to `Evidence`/`EffectivenessVerification`.

## 2. Exact Allowed / New Files

```text
domain/fmea_domain/entities.py                                    # add ValidationTest dataclass + TestType/ValidationResultStatus/LifecycleGate/ValidationTestStatus enums (and a Priority enum only if none reusable already exists) — additive only, no existing entity touched
django_app/fmea_app/models.py                                     # add ValidationTest(StableModel) only — Evidence/EffectivenessVerification untouched
django_app/fmea_app/migrations/000X_validationtest.py             # new
django_app/fmea_app/views.py                                      # add validation_test_list, new_validation_test (or create_validation_test), validation_test_detail only
django_app/fmea_app/urls.py                                       # add the two/three new routes
django_app/fmea_app/forms.py                                      # add ValidationTestForm only
django_app/fmea_app/templates/fmea_app/validation_test_list.html   # new
django_app/fmea_app/templates/fmea_app/validation_test_form.html   # new
django_app/fmea_app/templates/fmea_app/validation_test_detail.html # new
django_app/fmea_app/templates/fmea_app/_sidebar.html                # add new VALIDATION & CHANGE group + one link only

tests/test_validation_tests.py                                    # new
tests/test_gui_navigation_scope.py                                # one required, intentional change — see Section 4
```

Nothing else. No changes to `Evidence`, `EffectivenessVerification`, `RecommendedAction`, `ActionStatus`, `fmea_detail.html`, `action_detail.html`, or `theme.css` (reuse existing `.table-shell`/`.panel`/`.panel-heading`/status-badge classes as-is — no new CSS needed for a plain table + form + detail page).

## 3. Required Validation and Explicit Exclusions

- No file/attachment storage or upload UI anywhere on either page — no `FileField`/`ImageField` on `ValidationTest`, no upload `<input>` in either template.
- No real per-person `Owner` — `owner` is a nullable FK to the existing `ResponsibleRole` catalog only, never a new person/user field, never `django.contrib.auth`'s `User` model.
- No dashboard stat cards, no donut/line/any Chart.js charts, no `<canvas>` element anywhere on either new page.
- No `TestPlan` entity, no `test_plan` field or FK anywhere in this slice's diff.
- No change to `Evidence` or `EffectivenessVerification` models, their fields, their existing usage (`action_detail.html` if it renders them, any existing view/form referencing them), or any migration touching either table. Confirm by diff/grep: zero lines changed in either model's class body, zero new migration operation naming either table.
- No lifecycle multi-phase structure — one `ValidationTest` row belongs to exactly one `lifecycle_gate` value; no separate join table, no repeating group, no JSON list of phases.
- No enforced status-transition logic on `ValidationTest.status` — a plain, free-choice `<select>`, matching `ActionStatus`'s existing no-enforced-transitions precedent in `RecommendedActionForm`.
- No AI involvement of any kind (matches the architecture review's Section 5 "what this review does not propose").
- `_sidebar.html` diff is exactly one new `VALIDATION & CHANGE` group with exactly one link — every other existing group (`HOME`/`WORKSPACE`/`CONTEXT`/`FMEA ANALYSIS`/`FMEA ELEMENTS`/`RISK`/`Import & Review`/`Ishikawa / Cause Analysis`, whatever this codebase's sidebar currently contains) is otherwise unchanged.

## 4. Required Tests

`tests/test_validation_tests.py`:

- Render `/validation-tests/` with fixture `ValidationTest` rows and assert every listed column (FailureMode name, Test Type, Method, Result Status, Planned Date, Executed Date, Priority, Owner, Status, Lifecycle Gate) shows the correct fixture data, and that the FailureMode name links to the correct `fmea:fmea_detail` URL for its owning FMEA.
- POST to the create view with all fields populated, including a `recommended_action` selection; assert a `ValidationTest` row is created with every field set correctly, including the `recommended_action` FK.
- POST to the create view with `recommended_action` omitted; assert creation still succeeds and the field is stored as null.
- Render `/validation-tests/<stable_id>/` for a test with `recommended_action` set; assert the action's name/link (`fmea:action_detail`) appears. Render it again for a test with `recommended_action` unset; assert the "not linked" message appears instead and no action link is rendered.
- Assert the GET-form filters narrow the list correctly: seed multiple `ValidationTest` rows spanning at least two different values of `test_type`, `status`, and `lifecycle_gate`; assert `?test_type=...`, `?status=...`, and `?lifecycle_gate=...` (individually and in combination) each return only the matching rows.
- Assert neither `validation_test_list.html` nor `validation_test_detail.html` (nor the form template) contains any of: a file-input/upload UI marker (e.g. `type="file"`), `<canvas`, or the literal string `"Test Plan"`.
- Assert `Evidence` and `EffectivenessVerification` are completely untouched: no migration in this slice's diff references either model; grep/assert their existing fields and any existing view/template code path that renders them is unchanged (a simple regression check — e.g. re-run any pre-existing test covering `Evidence`/`EffectivenessVerification` display and confirm it still passes unmodified).
- Full existing suite re-run with no unrelated assertion changes.

`tests/test_gui_navigation_scope.py` — **one required, intentional change**, same shape as Slice D's flip: this file's `unbuilt_label` tuple currently includes `"Evidence & Tests"` (asserted absent). Remove it from that tuple and add a positive assertion that `"Evidence & Tests"` **is** present in the rendered sidebar, alongside a new assertion that `"VALIDATION & CHANGE"` is present. Add or confirm assertions that `"Validation Trajectory"` and `"Change Impact"` remain in the unbuilt/absent list — this slice does not build either. Every other existing assertion in this file stays exactly as-is. Call this out explicitly in your report so it reads as an intentional, expected change, not a regression.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `ValidationTest` exists as a `StableModel` subclass with exactly the fields in Section 0's table (plus `name`), backed by a matching framework-free `fmea_domain` entity and enums, and one new migration.
2. `/validation-tests/` renders a real table over real `ValidationTest` rows with all ten listed columns correct, and the FailureMode column links correctly into `fmea:fmea_detail`.
3. The create/edit form successfully creates a `ValidationTest` with every field, including a correctly-linked optional `recommended_action`.
4. `/validation-tests/<stable_id>/` renders full detail for one test, with correct linkage display in both the "action set" and "action unset" cases.
5. The three GET-form filters (`test_type`, `status`, `lifecycle_gate`) correctly narrow the list, individually and combined.
6. Neither page contains any file-upload UI, any chart/canvas markup, or any "Test Plan" content.
7. `Evidence` and `EffectivenessVerification` are provably untouched — no migration, no model, view, or template change to either.
8. `_sidebar.html` gains exactly one new `VALIDATION & CHANGE` group with exactly one link ("Evidence & Tests"); every other group is unchanged; `test_gui_navigation_scope.py`'s intentional flip is applied and called out.
9. Full test suite passes, `manage.py check` clean, exactly one new migration.
10. Mirrored into `open_fmea_training_set` per the standing discipline (byte-diffed, not just size/mtime), matching the same verification bar every prior slice was held to.

## 7. Explicit Exclusions (restated for emphasis)

No file/attachment storage or upload UI of any kind. No real per-person `Owner` — placeholder via `ResponsibleRole` only, no new person/user field, no login/permission code. No dashboard stat cards, no donut/line charts, no Chart.js usage, no `<canvas>` anywhere. No `TestPlan` grouping entity or `test_plan` FK — a nullable FK may be added later without reshaping anything decided here, but not in this slice. No change of any kind to `Evidence` or `EffectivenessVerification` — both models, their fields, and their existing display/usage are left exactly as they are, with no migration touching either. No lifecycle multi-phase structure — one `ValidationTest` row belongs to exactly one `lifecycle_gate`. No enforced status-transition rules on `ValidationTest.status`. No AI involvement of any kind. If any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

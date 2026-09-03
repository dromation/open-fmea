# Codex Implementation Instruction — Functions / Actions GUI Gap

Status: Approved for implementation, **narrowed on 2026-09-03**. Originally scoped to also cover `Evidence`/`EffectivenessVerification` — that scope is **removed and paused** (see the notice immediately below). Grounded in `OpenFMEA_ActionsEvidenceFunctions_ArchitectureReview.md`; the two of its open decisions still in scope were confirmed by the user on 2026-09-03: build both the cause-tied and no-cause "Actions" sections, and add a manual `Function` picker to `FailureModeForm`.

**Evidence/EffectivenessVerification scope pulled, 2026-09-03:** a further reference mockup ("Evidence & Tests," cataloged as Mockup 10 in `OpenFMEA_DNA_CoreReference.md` Section 10) showed that "Evidence & Tests" is really a much richer Test-Plan/Validation-Test concept than the existing `Evidence`/`EffectivenessVerification` models — its own status workflow, Test Type, Method, Objective, Acceptance Criteria, structured Pass/Fail result, Planned-vs-Executed dates, Priority, file attachments (no file-upload capability exists anywhere in this app today — confirmed: no `MEDIA_ROOT`, no `FileField`/`ImageField` anywhere in `fmea_app/models.py`), and a real `Owner`. Building the small, existing-model-only Evidence/EffectivenessVerification GUI now risked immediate rework once that richer entity is designed. The user chose to stop and redesign rather than proceed — see `OpenFMEA_EvidenceTests_ArchitectureReview.md` for the new review. **Do not implement `Evidence` or `EffectivenessVerification` GUI from this document — that scope is superseded by the new review above.** Everything below is Functions + Actions only, unaffected by this change and still approved as-is.

Authority, in order: same chain as prior slices; additionally subordinate to `OpenFMEA_ActionsEvidenceFunctions_ArchitectureReview.md` (design authority for the Functions/Actions portion of this slice) and `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` (visual language and tooling constraints).

## 0. What this slice is, precisely — read before starting

`Function` and `RecommendedAction` already exist as complete, persisted Django models with matching domain entities (`fmea_app/models.py` lines 192, 484; `fmea_domain/entities.py`). This slice adds **no new entity, no new migration, no new domain rule** — it is purely a GUI-exposure slice, the same category of work as the earlier Process Flow gap fix. Every field named below already exists in the model; do not add fields beyond what's listed. (`Evidence`/`EffectivenessVerification` are out of scope — see the notice above.)

## 1. Exact Scope

1. A `Function` create form as a new worksheet section in `fmea_detail.html`, parented to the `FMEA` (mirrors the existing `Process`/`Operation` pattern — table + compact add-form).
2. An optional `Function` `<select>` added to `FailureModeForm`, populated from the parent `FMEA`'s existing `Function`s, so a user can manually link a `FailureMode` to a `Function` at creation time.
3. An "Actions" section under each `FailureCause` row in `fmea_detail.html` (mirrors the existing Prevention/Detection Controls pattern exactly).
4. A second, smaller "Actions not tied to a specific cause" section directly under each `FailureMode` row, for `RecommendedAction` rows whose `failure_cause` is null and `failure_mode` is set.
5. A new `Action` detail page, `/actions/<stable_id>/`, showing the action's fields. **Does not** show or link `Evidence`/`EffectivenessVerification` — that's paused, see the notice above; the detail page is scoped to the `RecommendedAction`'s own fields only for now.
6. `Action` status is a plain `<select>` over all five `ActionStatus` values (`open`/`in_progress`/`completed`/`verified`/`cancelled`), fully manual.

Nothing beyond this list. No new entity, no new migration, no `ResponsibleRole` CRUD page (populate its `<select>` from existing rows only), no sidebar/nav additions, no change to `test_gui_navigation_scope.py`, no `Evidence`/`EffectivenessVerification` GUI of any kind (paused — see notice above), no auto-transition logic of any kind.

## 2. Required Logic

None beyond standard Django `ModelForm`s and queryset filtering — no new query shape, no new aggregation, no new validation function in `fmea_domain/rules.py`. Confirmed: no `validate_action_transition`-style function exists today and this slice does not add one; status changes are unconstrained aside from the existing `ActionStatus` choices.

Forms needed (in `fmea_app/forms.py`, alongside the existing `FailureModeForm`/`FailureEffectForm`/`FailureCauseForm`/`PreventionControlForm`/`DetectionControlForm` — same idiom):
- `FunctionForm` (`name`, `description`)
- `FailureModeForm` — add a `function` field (optional `ModelChoiceField`/`<select>`, queryset scoped to the parent `FMEA`'s `Function`s — pass the `FMEA` into the form or filter in the view, whichever matches how `FailureModeForm` is currently constructed)
- `RecommendedActionForm` (`name`, `description`, `responsible_role` — `<select>` from existing `ResponsibleRole` rows, `status`, `due_date`)

(`EvidenceForm`/`EffectivenessVerificationForm` are removed from this instruction — paused, see the top-of-document notice.)

## 3. Required Views/APIs

- `add_function` — `POST /fmea/<str:stable_id>/functions/add/` (parented to the `FMEA`)
- `add_action_to_cause` — `POST /cause/<str:stable_id>/actions/add/`
- `add_action_to_failure_mode` — `POST /failure-mode/<str:stable_id>/actions/add/` (creates a `RecommendedAction` with `failure_cause=None`)
- `action_detail` — `GET /actions/<str:stable_id>/`

(`add_evidence`/`add_effectiveness_verification` are removed from this instruction — paused, see the top-of-document notice.)

All `POST` views follow the existing `@require_POST` + form-validate-or-`_form_errors`-redirect-back pattern used by `add_failure_mode`/`add_failure_effect`/etc. — do not invent a new error-handling idiom.

## 4. GUI Integration

- `fmea_detail.html`: add the `Function` section (parallel structure to the existing `Process`/`Operation` display block), add the `function` field to the `FailureModeForm` render, add the cause-level and failure-mode-level Actions sections (parallel structure to the existing Causes/Prevention Controls/Detection Controls sections — same `<table>` + compact `<form>` idiom, same CSS classes).
- New `action_detail.html` template — reuse the existing card/table/status-badge components and CSS tokens from `theme.css`, no new visual pattern needed (this is a detail page in the same style as `process_characteristic_detail.html`/`cause_influence_detail.html`). Scoped to the `RecommendedAction`'s own fields only, per the notice above.
- No sidebar changes. No dashboard changes. `test_gui_navigation_scope.py` is not touched by this slice.

## 5. Exact Allowed / New Files

```text
django_app/fmea_app/forms.py                  # add FunctionForm, RecommendedActionForm; extend FailureModeForm
django_app/fmea_app/views.py                  # add_function, add_action_to_cause, add_action_to_failure_mode,
                                                # action_detail
django_app/fmea_app/urls.py
django_app/fmea_app/templates/fmea_app/
    fmea_detail.html                          # extend: Function section, Actions sections, function field on FailureModeForm
    action_detail.html                        # new

tests/test_functions_actions_gui.py
```

## 6. Required Validation and Explicit Exclusions

- `RecommendedAction` creation requires exactly one of `failure_cause`/`failure_mode` to be set by construction (the cause-level add-view sets `failure_cause`; the failure-mode-level add-view sets `failure_mode` with `failure_cause=None`) — do not expose a form field letting a user set both or neither.
- `status` accepts only the five existing `ActionStatus` values via the model's `choices` — no new status values, no transition enforcement.
- `Function` `<select>` on `FailureModeForm` is scoped to the parent `FMEA`'s own `Function`s only (no cross-FMEA linkage).
- No `ResponsibleRole` create/edit UI — `<select>` reads existing rows only; if none exist, render an empty/disabled select rather than blocking the rest of the form.
- No `Evidence`/`EffectivenessVerification` GUI of any kind — paused, see the top-of-document notice.
- No new sidebar/nav entry, no `test_gui_navigation_scope.py` change.

## 7. Required Tests

- `test_functions_actions_gui.py`:
  - `Function` can be created via the new form and appears in the `FMEA`'s Function section; a `FailureMode` can be created with an optional `function` selected from that `FMEA`'s functions and the linkage is saved and displayed.
  - An `Action` created via the cause-level form has `failure_cause` set and `failure_mode` null; an `Action` created via the failure-mode-level ("not tied to a specific cause") form has `failure_mode` set and `failure_cause` null.
  - `action_detail` renders the action's own fields correctly.
  - `test_gui_navigation_scope.py`: re-run unchanged, assert it still passes with zero modifications — this slice must not alter the nav allow-list.
- Full existing suite re-run with no unrelated assertion changes.

## 8. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --no-input
python -B -m pytest
```

## 9. Acceptance Criteria

1. `Function` and `Action` (both cause-tied and no-cause) are creatable and viewable through the GUI, using only fields that already exist on their respective models.
2. `FailureModeForm` gains exactly one new optional field (`function`); no other form gains fields beyond what Section 2 lists.
3. No new entity, migration, domain rule, sidebar entry, or `test_gui_navigation_scope.py` change appears in the diff.
4. No `Evidence` or `EffectivenessVerification` view, URL, template, or form appears in the diff — that scope is paused.
5. Full test suite passes, `manage.py check` clean, no unexpected migration.
6. Mirrored into `open_fmea_training_set` and the training EXE rebuilt, with the same clean-run verification discipline as every prior slice — including actually completing the mirror before reporting this slice done.

## 10. Explicit Exclusions (restated for emphasis)

Any new entity or migration, any `ActionStatus` transition/enforcement logic, any `ResponsibleRole` CRUD page, any `Evidence`/`EffectivenessVerification` GUI (paused — see the top-of-document notice and `OpenFMEA_EvidenceTests_ArchitectureReview.md`), any sidebar/dashboard/nav change, any of the still-deferred sections (FMEA Projects-as-a-page, User/Role/Team system, System hierarchy, System Characteristics Base/`ClassificationScheme`, Characteristics Flow/Diagram, Validation Trajectory, Change Impact, PM-FMEA/Asset/Maintenance, Operations, Project Health, XDA Investigations — still undefined).

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

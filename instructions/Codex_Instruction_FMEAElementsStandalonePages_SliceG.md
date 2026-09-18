# Codex Implementation Instruction — FMEA Elements Standalone Browse Pages (Slice G)

Status: Approved for implementation, 2026-09-04. Bundles six cross-cutting, read-only browse pages (Failure Modes, Causes, Effects, Preventive Controls, Detection Controls, Actions) — all six entities are already real and already fully editable via each FMEA's worksheet; this slice only makes them browsable across all FMEAs at once, the same gap-close pattern as Engineering Context (Products/Processes) and Slice D (DFMEA/PFMEA). Picked as part of pushing every remaining mockup toward implementation-readiness, following this project's established narrow-scope-per-slice discipline.

Grounded directly in the real code before writing this: `models.py`'s `FailureMode`, `FailureEffect`, `FailureCause`, `PreventionControl`, `DetectionControl`, `RecommendedAction` (all read in full), `views.py`'s `_build_worksheet_rows`/`_worksheet_row`/`action_detail`/`cause_influence_list`/`process_characteristic_list`, and `domain/fmea_domain/entities.py`'s `ActionStatus`.

## 0. Decisions for this slice

1. **No `FailureCause` model/migration change — single-`failure_mode`-FK relationship stays exactly as it is.** Mockup 16 shows one cause linked to multiple failure modes, but the real `FailureCause` model (`django_app/fmea_app/models.py`) has a single mandatory `failure_mode = models.ForeignKey(FailureMode, related_name="causes", on_delete=models.CASCADE)`. Redesigning that into a many-to-many would be a real, data-affecting migration and is out of proportion for a browse-page slice. The standalone Causes page shows causes exactly as the real model has them today — one cause, one failure mode, one FMEA. This is a deliberate, narrow decision, not an oversight: **a future review would be needed if a genuine many-to-many redesign is ever wanted**, and that review is explicitly not this slice.
2. **Add `on_hold` as a new, additive `ActionStatus` value.** Mockup 22 shows an "On Hold" action status that doesn't exist in the real enum (`open`/`in_progress`/`completed`/`verified`/`cancelled`, in `domain/fmea_domain/entities.py`). This is low-risk and backward-compatible: `RecommendedAction.STATUS_CHOICES` is already derived mechanically from the enum (`models.py`: `STATUS_CHOICES = [(status.value, status.name.replace("_", " ").title()) for status in ActionStatus]`), and `status` is a plain `CharField(choices=...)` — adding an enum member only adds one more valid string value and one more dropdown option; it does not alter, remove, or reinterpret `verified` or any existing row's stored value. Add `ON_HOLD = "on_hold"` to `ActionStatus`, after `VERIFIED` and before `CANCELLED` is fine (position in the enum does not affect stored values or existing choices ordering guarantees beyond re-deriving the list). **Confirm before assuming no migration is needed**: `choices` on a `CharField` is validation/display metadata, not a schema change, so Django does not generate a migration for a new choices tuple on its own — but run `manage.py makemigrations --check --dry-run` per Section 5 and report honestly if it disagrees; do not just assume.
3. **Read-only, no new CRUD — standing decision for all six pages.** Every create/edit form for `FailureMode`/`FailureEffect`/`FailureCause`/`PreventionControl`/`DetectionControl`/`RecommendedAction` already exists and stays exactly where it is: inside `fmea_detail.html` (all six), plus `RecommendedAction` also already has its own read-only detail page at `fmea:action_detail`. These six new pages are pure list/browse views, each row linking back to `fmea:fmea_detail` (or `fmea:action_detail` for the Actions list) for any editing. No form, no POST handler, no `forms.py` change of any kind on any of the six new views.
4. **Exact column lists per page** (see Section 1 for full detail) — fixed now so the implementing session isn't guessing:
   - Failure Modes: FMEA (link), Function/Requirement, Name, Description, latest risk result, Effects count, Causes count, Actions count.
   - Causes: FMEA (via `failure_mode.fmea`, link), Failure Mode (name), Name, Description, Prevention Controls count, Detection Controls count, Actions count.
   - Effects: FMEA (link), Failure Mode (name), Name, Description.
   - Preventive Controls: FMEA (link), Failure Mode, Cause (name), Name, Description.
   - Detection Controls: FMEA (link), Failure Mode, Cause (name), Name, Description.
   - Actions: FMEA (link), linked Failure Mode or Cause (whichever is set), Name, Status (now including "On Hold"), Responsible Role, Due Date — Name links to `fmea:action_detail`.
5. **This is the first real content under a new "FMEA ELEMENTS" sidebar group.** `OpenFMEA_DNA_CoreReference.md` Section 10 already names this canonical group; it does not exist in the real sidebar yet because nothing real existed under it before now (the same justification used when "FMEA ANALYSIS" was created for the DFMEA/PFMEA slice, and "VALIDATION & CHANGE" for the Evidence & Tests slice). Add it now, per Slice A's own stated rule ("no navigation for anything not built yet" — now there is something built), with exactly the six links below.
6. **Reuse `_worksheet_row`'s risk-result computation logic for the Failure Modes page's latest-risk column, but do not modify or fork `_build_worksheet_rows`/`_worksheet_row` themselves.** Those two helpers are shape-committed to `fmea_detail.html` and to the Slice D worksheet pages — touching them is out of scope here. If the existing per-failure-mode "latest risk evaluation" lookup (`failure_mode.risk_evaluations.all()` ordered so `[0]` is latest, exactly as `_build_worksheet_rows` already does it) can be reused as a small standalone read (e.g. a short local helper or inline expression in the new view, computing severity/occurrence/detection and the RPN-or-priority result the same way `_worksheet_row` does), do that. If reusing it cleanly turns out to be awkward, it is acceptable to state the column simply as "Severity/Occurrence/Detection from the latest `RiskEvaluation`, if any" and render those three raw values plus the same `result`/`result_class` dict fields `RiskEvaluation.result` already stores — do not invent new risk-scoring logic.

## 1. Exact Scope

Six new views, six new routes, six new templates, all following the identical read-only list pattern already used by `cause_influence_list`/`process_characteristic_list`.

1. **Failure Modes** — view `failure_mode_list`, route `/failure-modes/`, name `fmea:failure_mode_list`. Query `FailureMode.objects.select_related("fmea", "function", "requirement").order_by("fmea__name", "name")`. Columns: FMEA (`fmea.name`, links to `fmea:fmea_detail` with `stable_id=fmea.stable_id`), Function/Requirement (`function.name` or `requirement.name`, whichever is set, else blank), Name, Description, latest risk result (per Decision 6), Effects count (`failure_mode.effects.count()`), Causes count (`failure_mode.causes.count()`), Actions count (`failure_mode.recommended_actions.count()` — note this only counts actions attached directly to the failure mode, not actions attached to one of its causes; state this plainly in the template/column header or a short caption, e.g. "Actions (direct)", so it isn't misread as a total).
2. **Causes** — view `failure_cause_list`, route `/causes/`, name `fmea:failure_cause_list`. Query `FailureCause.objects.select_related("failure_mode", "failure_mode__fmea").order_by("failure_mode__fmea__name", "failure_mode__name", "name")`. Columns: FMEA (via `failure_mode.fmea`, link), Failure Mode (name), Name, Description, Prevention Controls count (`cause.prevention_controls.count()`), Detection Controls count (`cause.detection_controls.count()`), Actions count (`cause.recommended_actions.count()`).
3. **Effects** — view `failure_effect_list`, route `/effects/`, name `fmea:failure_effect_list`. Query `FailureEffect.objects.select_related("failure_mode", "failure_mode__fmea").order_by("failure_mode__fmea__name", "failure_mode__name", "name")`. Columns: FMEA (link), Failure Mode (name), Name, Description.
4. **Preventive Controls** — view `prevention_control_list`, route `/prevention-controls/`, name `fmea:prevention_control_list`. Query `PreventionControl.objects.select_related("failure_cause", "failure_cause__failure_mode", "failure_cause__failure_mode__fmea").order_by("failure_cause__failure_mode__fmea__name", "failure_cause__failure_mode__name", "failure_cause__name", "name")`. Columns: FMEA (link), Failure Mode, Cause (name), Name, Description.
5. **Detection Controls** — view `detection_control_list`, route `/detection-controls/`, name `fmea:detection_control_list`. Same query/relatedness shape as Preventive Controls, on `DetectionControl`. Columns: FMEA (link), Failure Mode, Cause (name), Name, Description.
6. **Actions** — view `action_list`, route `/actions/`, name `fmea:action_list`. Query `RecommendedAction.objects.select_related("failure_mode__fmea", "failure_cause__failure_mode__fmea", "responsible_role").order_by("-due_date", "name")` (or another reasonable default order — not load-bearing). Resolve "owning FMEA" as `action.failure_mode.fmea if action.failure_mode else action.failure_cause.failure_mode.fmea` (one of the two FKs is always set per the model — both nullable, but not both null in valid data; if both happen to be null for some row, render the FMEA cell blank rather than raising). Columns: FMEA (link), linked Failure Mode or Cause (whichever FK is set — show its name, and label which kind it is, e.g. "Cause: <name>" vs "Failure Mode: <name>"), Name (links to `fmea:action_detail` with `stable_id=action.stable_id`), Status (rendered from `ActionStatus`/`STATUS_CHOICES`, now including "On Hold"), Responsible Role (`responsible_role.name` or blank), Due Date.
   - Filter: a standard GET-form `<select name="status">` populated from `RecommendedAction.STATUS_CHOICES` (same idiom as `cause_influence_list`'s `status` filter), applied via `.filter(status=status_filter)` when `status_filter` is non-empty. This is the one "obvious filter dimension" called for — no other filter is required on any of the six pages, though adding an equally simple one (e.g. an FMEA filter) is acceptable if it follows the same GET-param pattern and doesn't grow into new UI.

Pagination is not required on any of the six pages unless the implementing session judges the real row counts need it — this is left as a judgment call to keep the instruction from over-specifying UI polish, not a hard requirement either way.

All six templates: reuse the existing `.table-shell` + `<table>` CSS pattern (same classes already used by `process_characteristic_list.html`/`cause_influence_list.html`/Risk Matrix) — no new CSS. No new JS, no AJAX — filters are plain GET forms that reload the page, matching every other list page in this app.

Sidebar: add a new `FMEA ELEMENTS` group to `_sidebar.html` (same `.nav-group`/`.nav-group-title`/`.nav-link` markup as every other group), placed after the `FMEA ANALYSIS` group (if present) and before `Import & Review`, with exactly six links in this order: Failure Modes, Causes, Effects, Preventive Controls, Detection Controls, Actions — each pointing at its `{% url %}` name above. (If `FMEA ANALYSIS` is not yet present in the sidebar in the checkout you're working from, place `FMEA ELEMENTS` directly after the top ungrouped block — i.e. after Risk Matrix — and before `Import & Review`; report which case applied.)

## 2. Exact Allowed / New Files

```text
domain/fmea_domain/entities.py                                       # add ON_HOLD = "on_hold" to ActionStatus only
django_app/fmea_app/models.py                                        # no edit expected — STATUS_CHOICES already derives from the enum; touch only if verification in Section 0.2 proves otherwise
django_app/fmea_app/views.py                                         # six new list views only
django_app/fmea_app/urls.py                                          # six new routes
django_app/fmea_app/templates/fmea_app/failure_mode_list.html        # new
django_app/fmea_app/templates/fmea_app/failure_cause_list.html       # new
django_app/fmea_app/templates/fmea_app/failure_effect_list.html      # new
django_app/fmea_app/templates/fmea_app/prevention_control_list.html  # new
django_app/fmea_app/templates/fmea_app/detection_control_list.html   # new
django_app/fmea_app/templates/fmea_app/action_list.html              # new
django_app/fmea_app/templates/fmea_app/_sidebar.html                 # add new FMEA ELEMENTS group + six links, nothing else changed

tests/test_fmea_elements_standalone_pages.py                          # new
tests/test_gui_navigation_scope.py                                    # required update — see Section 4
```

Nothing else. No `forms.py` change (no new forms — read-only pages). No new model, no new field beyond the `ActionStatus` enum addition. If `manage.py makemigrations --check --dry-run` (Section 5) reports a pending migration from the enum change alone, generate it and add it under `django_app/fmea_app/migrations/` — note this explicitly and honestly in your report rather than silently assuming none is needed.

## 3. Required Validation and Explicit Exclusions

- No new CRUD/forms on any of the six new pages — read-only, every row linking back to `fmea_detail.html` (or `action_detail.html` for Actions) for editing.
- No `FailureCause` model or migration change — the single mandatory `failure_mode` FK stays exactly as-is (Decision 1). Confirm with a diff that `FailureCause`'s field definition is byte-identical to its current state.
- No new fields on any of the six entities beyond the `ActionStatus` enum addition (Decision 2) — `FailureMode`, `FailureEffect`, `PreventionControl`, `DetectionControl` get zero model changes; `RecommendedAction` gets zero field changes (only its `STATUS_CHOICES`, which is derived, not hand-edited).
- No charts, no stat-card dashboards, no catalogs/libraries, no complaint-linking, no AI similarity matching, no image/photo annotation — all separately flagged in the relevant mockup specs as materially bigger, unapproved concepts; none of them belong in this slice.
- No AJAX anywhere — filters are server-side GET forms only, matching every existing list page.
- `_build_worksheet_rows`/`_worksheet_row`/`fmea_detail` remain unchanged (diff them explicitly — zero lines changed).
- `_sidebar.html` diff is exactly one new `FMEA ELEMENTS` group with six links — every other group unchanged.

## 4. Required Tests

`tests/test_fmea_elements_standalone_pages.py`:
- For each of the six new pages: render it against fixture data spanning **at least two different FMEAs**, and assert rows from both FMEAs appear on the same page (not just one), with correct field values and correct links — `fmea:fmea_detail` (with the right `stable_id`) for the first five pages, `fmea:action_detail` (with the right `stable_id`) for the Actions list.
- Assert each page's counts (Effects/Causes/Actions on Failure Modes; Prevention/Detection/Actions on Causes) match known fixture counts exactly.
- Assert the Actions list page's Status filter `<select>` now includes an "On Hold" option (`value="on_hold"`), and that creating/updating a `RecommendedAction` with `status="on_hold"` persists correctly and renders "On Hold" in the list (and filters to only that row when `?status=on_hold` is applied).
- Assert `FailureCause`'s model fields are unchanged (e.g. assert it still has exactly one `failure_mode` FK, no new fields) and that existing single-failure-mode behavior (a cause belongs to exactly one failure mode) is unaffected by this slice.
- Assert none of the six new pages' rendered HTML contains any `<form method="post"` or CRUD form markup (e.g. no `<input type="submit"` beyond a GET filter's submit button, no create/edit `<form>` posting to any of the six entities' save endpoints) — read-only pages only. GET-form filter markup (e.g. the Actions status `<select>`/submit inside a `method="get"` form) is expected and fine; assert specifically that no `method="post"` form targeting these six entities appears.
- Assert `_sidebar.html` (or the rendered page containing it) shows a new "FMEA ELEMENTS" group containing all six expected link labels and that each resolves to its corresponding named URL.

`tests/test_gui_navigation_scope.py` — required, intentional update: if this test currently asserts `"FMEA ELEMENTS"` is absent from the sidebar (per Slice A's original scope, when nothing real existed under it), flip that specific assertion to assert it is now **present**, and add assertions that all six new link labels appear. Leave every other existing assertion in that file untouched — call this out explicitly in your report as an intentional, expected change, not a regression.

Full existing suite re-run with no other unrelated assertion changes.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. All six new routes render real data, correctly spanning multiple FMEAs, with correct counts and correct links into `fmea:fmea_detail`/`fmea:action_detail`.
2. `ActionStatus` gains exactly one new member, `ON_HOLD = "on_hold"`; `RecommendedAction.STATUS_CHOICES` picks it up automatically via its existing derivation; no other enum member is altered, renamed, or removed.
3. `FailureCause` is verified byte-identical in its model definition — no migration touches it.
4. No new CRUD/forms exist on any of the six new pages — confirmed by test assertions against form markup.
5. `_sidebar.html` gains exactly one new `FMEA ELEMENTS` group with exactly six links, in the specified order; every other group unchanged.
6. `_build_worksheet_rows`/`_worksheet_row`/`fmea_detail` are unchanged (diff-confirmed).
7. Full test suite passes (including the one intentional, called-out flip in `test_gui_navigation_scope.py`), `manage.py check` clean; `makemigrations --check --dry-run` either reports clean, or a migration was honestly generated and reported for the enum-derived choices change.
8. No charts, dashboards, catalogs, complaint-linking, AI similarity matching, or image annotation anywhere in the diff.
9. Mirrored into `open_fmea_training_set` per the standing discipline (byte-diffed, not just size/mtime).

## 7. Explicit Exclusions (restated for emphasis)

No new CRUD or forms on any of the six new pages — all editing stays exactly where it already is, in `fmea_detail.html` (and `action_detail.html` for Actions); these are strictly read-only cross-cutting list views. No `FailureCause` model or migration change — the single-failure-mode relationship is a deliberate, narrow decision for this slice, not a redesign, and any future many-to-many rework needs its own separate review. No new fields on any of the six entities beyond the additive `ActionStatus.ON_HOLD` enum value. No charts, stat-card dashboards, catalogs/libraries, complaint-linking, AI similarity matching, or image/photo annotation — all were separately flagged elsewhere as materially bigger, unapproved concepts and are explicitly out of scope here. If any of this seems to need changing to deliver a working slice, stop and report — do not silently expand scope.

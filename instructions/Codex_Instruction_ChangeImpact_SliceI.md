# Codex Implementation Instruction — Change Impact (Slice I)

Status: Approved for implementation, 2026-09-04. Grounded in `OpenFMEA_ChangeImpact_ArchitectureDecision.md` (READY FOR IMPLEMENTATION) — a new `Change` entity with a many-to-many link to `FailureMode`, a Change Log list, and a create/edit/detail flow. Nothing else from Mockup 13 is in scope.

## 0. Decisions for this slice

1. **`Change` is a new `StableModel` in `fmea_app/models.py`, Django-app-layer only — not mirrored into `fmea_domain/`.** No `to_domain()`/domain-entity pairing is added for it, matching `FMEAProject`/`ProjectMembership`'s own precedent for GUI-facing fields with no current OFEF/interchange requirement. Do not add anything to `domain/fmea_domain/entities.py` for this slice.
2. **`change_type`, `impact_level`, and `status` are plain Django `choices` tuples on the model** (same pattern as `FMEAProject.PROJECT_STATUS_CHOICES`/`ProjectMembership.ROLE_CHOICES`), not a `CauseCategoryScheme`-style configurable taxonomy and not routed through a `fmea_domain` enum. `status` defaults to `"under_analysis"`. No enforced status transitions — a plain free-choice `<select>`, matching `RecommendedAction.status`'s own precedent.
3. **`owner` is a nullable FK to the existing `ResponsibleRole` model**, not a new person/user field and not a `django.contrib.auth` reference. Rendered as a plain `<select>` populated from existing `ResponsibleRole` rows — no `ResponsibleRole` CRUD is added here.
4. **`affected_failure_modes` is a plain `ManyToManyField(FailureMode, blank=True)`** — no new join model, no per-link fields. Edited via the default `ModelMultipleChoiceField` multi-select widget on the edit form — no AJAX/search-as-you-type picker, consistent with every other relationship-editing widget in this app.
5. **No new domain rule, no enforced review/approval workflow.** `Change` is created and edited the same way `ProcessCharacteristic`/`FMEAProject` are — an ordinary human-driven form, unguarded.
6. **One sidebar entry only** — "Change Impact," linking to the Change Log list — added to the existing sidebar's primary nav group (the same group already containing "FMEA Projects," "Process Characteristics," "Risk Matrix"). Do not invent a new nav group for this slice.
7. **No charts, no Impact Matrix / Affected FMEA Items / Action Plan / Change History tabs, no AI-assisted impact analysis** — see Section 3/7 below; all deferred per the architecture decision.

## 1. Exact Scope

1. **`Change` model** (`fmea_app/models.py`), extending `StableModel`:
   - `title` (`CharField(max_length=255)`)
   - `change_type` (`CharField(max_length=32, choices=CHANGE_TYPE_CHOICES)`) — values: `design`/`supplier`/`regulatory`/`process`/`material`, labels Title Case ("Design," "Supplier," "Regulatory," "Process," "Material").
   - `source` (`CharField(max_length=255, blank=True)`)
   - `reason` (`TextField(blank=True)`)
   - `description` (`TextField(blank=True)`)
   - `impact_level` (`CharField(max_length=16, choices=IMPACT_LEVEL_CHOICES)`) — values: `critical`/`high`/`medium`/`low`.
   - `status` (`CharField(max_length=32, choices=STATUS_CHOICES, default="under_analysis")`) — values: `under_analysis`/`in_progress`/`open`/`closed`, labels "Under Analysis," "In Progress," "Open," "Closed."
   - `owner` (`ForeignKey(ResponsibleRole, null=True, blank=True, on_delete=models.SET_NULL, related_name="changes")`)
   - `target_date` (`DateField(null=True, blank=True)`)
   - `affected_failure_modes` (`ManyToManyField(FailureMode, blank=True, related_name="affecting_changes")`)
   - `__str__` returns `self.title`.
2. **Change Log list** — route `/changes/` (`fmea:change_list`): a `.table-shell`/`<table>` of all `Change` rows (Title / Type / Impact Level / Status / Owner / Target Date), each title linking to its detail page. A server-side GET filter form (`<select>` for `change_type`, `<select>` for `impact_level`, `<select>` for `status`, each with an "All" empty option) submitting to the same route — no AJAX, matching the app's one filtering idiom (see `process_characteristic_list`/`cause_influence_list` for the exact pattern to follow).
3. **Create/edit form** — one `ChangeForm(forms.ModelForm)` covering every field above including `affected_failure_modes`, reused by both:
   - `/changes/new/` (`fmea:new_change`) — GET renders the empty form, POST creates and redirects to the new `Change`'s detail page.
   - `/changes/<str:stable_id>/edit/` (`fmea:edit_change`) — GET renders the form pre-filled, POST updates and redirects to the detail page.
4. **Detail page** — `/changes/<str:stable_id>/` (`fmea:change_detail`): every field from Section 1.1 rendered read-only, plus a read-only table of linked `FailureMode`s (name, parent `FMEA` name linking to `fmea:fmea_detail`, and the parent FMEA's type — "DFMEA" when `fmea_type == "design"`, "PFMEA" when `fmea_type == "process"`, the raw `get_fmea_type_display()` value otherwise), plus a count of affected failure modes. No inline add/remove control on this page — linking/unlinking `FailureMode`s happens only via the edit form's multi-select (Section 1.3). An "Edit" button links to `fmea:edit_change`.
5. **Sidebar** — add exactly one new `<a class="nav-link">` entry, "Change Impact," to `_sidebar.html`'s existing primary nav group (the same group as "FMEA Projects"/"Process Characteristics"/"Risk Matrix"), linking to `fmea:change_list`.

Nothing beyond this list.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/models.py                              # add Change model only
django_app/fmea_app/migrations/0006_change.py               # new (renumber if a later migration already exists)
django_app/fmea_app/forms.py                                # add ChangeForm only
django_app/fmea_app/views.py                                # add change_list, new_change, edit_change, change_detail only
django_app/fmea_app/urls.py                                 # add the four new routes only
django_app/fmea_app/templates/fmea_app/change_list.html     # new
django_app/fmea_app/templates/fmea_app/change_form.html     # new
django_app/fmea_app/templates/fmea_app/change_detail.html   # new
django_app/fmea_app/templates/fmea_app/_sidebar.html        # add the one nav link, nothing else

tests/test_change_impact.py                                 # new
```

Nothing else. No changes to `fmea_domain/`, `fmea_evaluation/`, `FMEARevision`, `RiskEvaluation`, or any existing template beyond the one `_sidebar.html` line.

## 3. Required Validation and Explicit Exclusions

- No `to_domain()` method and no `fmea_domain` entity/enum for `Change` — confirm by grep that `domain/fmea_domain/entities.py` is untouched.
- No new join-model for the `Change`↔`FailureMode` relationship — a plain `ManyToManyField`, Django's default implicit through-table.
- No AJAX/search-as-you-type widget for `affected_failure_modes` — the default `ModelMultipleChoiceField` multi-select rendering.
- No enforced status-transition rule anywhere (`fmea_domain/rules.py` untouched) — `status` is a free-choice dropdown.
- No `ResponsibleRole` CRUD page/form added — only a `<select>` populated from existing rows.
- No Impact Matrix, Affected FMEA Items (as a separate tab), Action Plan, or Change History tab/page/route.
- No `<canvas>`, no chart/graph library reference, no donut/line-chart markup anywhere in the new templates.
- No approval/review workflow, no new confirmation/accept step beyond the plain create/edit form.
- `_sidebar.html` diff is exactly one new `<a class="nav-link">` line — no new nav group, no other line changed.
- No AI-assisted suggestion of `affected_failure_modes` or any other field.

## 4. Required Tests

`tests/test_change_impact.py`:

- Create a `Change` via `ChangeForm`/POST to `/changes/new/` with a full set of valid fields (including selecting one or more `FailureMode`s via the M2M field); assert it redirects to the new `Change`'s detail page and the record persists with the correct `change_type`/`impact_level`/`status`/`owner`/`affected_failure_modes`.
- Render `/changes/` with two or more fixture `Change` rows across different `change_type`/`impact_level`/`status` values; assert the table shows Title/Type/Impact Level/Status/Owner/Target Date correctly for each row.
- Filter `/changes/?change_type=supplier`, `/changes/?impact_level=critical`, and `/changes/?status=closed` (each independently, and at least one combined) against fixture data spanning multiple values; assert only the matching rows appear.
- Render `/changes/<stable_id>/` for a `Change` with two or more linked `FailureMode`s spanning both a `design`-type and a `process`-type `FMEA`; assert both linked-`FailureMode` rows appear with the correct parent-FMEA link and the correct "DFMEA"/"PFMEA" label.
- Submit an edit via `/changes/<stable_id>/edit/` that removes one linked `FailureMode` and adds another; assert the detail page's linked list reflects exactly the new set afterward.
- Assert `/changes/`, the create/edit form, and the detail page contain no `<canvas` markup and no "Impact Matrix"/"Action Plan"/"Change History" text — a negative check consistent with `test_gui_navigation_scope.py`'s existing pattern.
- `_sidebar.html`: assert exactly one new "Change Impact" link is present, linking to `fmea:change_list`, and that every previously-asserted-absent label in `test_gui_navigation_scope.py` remains absent.
- Full existing suite re-run with no unrelated assertion changes.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `/changes/` renders a filterable Change Log table (Title/Type/Impact Level/Status/Owner/Target Date), filter form submitting via GET, no AJAX.
2. `/changes/new/` and `/changes/<stable_id>/edit/` share one `ChangeForm`, including a plain multi-select for `affected_failure_modes`.
3. `/changes/<stable_id>/` shows every `Change` field plus a read-only linked-`FailureMode` list with correct DFMEA/PFMEA labeling, editable only via the edit form.
4. Sidebar gains exactly one new "Change Impact" link; no other nav change.
5. No `fmea_domain/` changes, no new join model, no chart/canvas markup, no approval workflow anywhere in the diff.
6. Full test suite passes, `manage.py check` clean, exactly one new migration (`0006_change.py` or the correct next sequential number).
7. Mirrored into `open_fmea_training_set` per this project's standing discipline (byte-diffed, not just size/mtime).

## 7. Explicit Exclusions (restated for emphasis)

Impact Matrix tab, Affected FMEA Items as its own tab (the detail page's read-only list is the only surface for this data), Action Plan tab (`Change`→`RecommendedAction` linkage is a separate, undecided modeling question), Change History/audit trail, any donut/line/bar chart or `<canvas>` element, any AI-assisted impact analysis or suggestion, any approval/review workflow for `Change`, any `ResponsibleRole` CRUD, any file/attachment capability, any new join-model for the `FailureMode` link, any new `fmea_domain` entity or enum. If any of this seems to need changing to deliver a working slice, stop and report — do not silently expand scope.

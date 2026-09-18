# Codex Implementation Instruction — Process Control Characteristics (Slice H)

Status: Approved for implementation, 2026-09-04. Per `OpenFMEA_ProcessControlCharacteristics_ArchitectureDecision.md` (2026-09-05): add the Mockup-21 control fields directly to the existing `ProcessCharacteristic` model as ordinary, additive, human-editable fields. This is **not** a governed/gated entity — an earlier characterization of this mockup as "the Control Plan concept" requiring an approval-workflow state machine was incorrect and is retracted; treat this exactly like any other unbuilt-fields gap on an existing model.

## 0. Decisions for this slice

1. `control_type`, `status`, and `effectiveness` are closed Python enums (mirroring the existing `ActionStatus`/`RecommendedAction.STATUS_CHOICES` pattern), rendered as `CharField(choices=...)` — not free text, not a new configurable-scheme entity.
2. `resource_equipment` is a plain `CharField` (free text). Do **not** build a Resource/Equipment catalog model — that is a separate, bigger, not-yet-approved concept.
3. `method` and `frequency_trigger` are plain `CharField` (free text). No catalog, no structured cadence model.
4. `owner` is a nullable `ForeignKey` to the existing `ResponsibleRole` model — same placeholder pattern as `RecommendedAction.responsible_role`. It is a name/description catalog reference, not a real user account.
5. `review_due` is a nullable `DateField`. No reminder/notification logic.
6. `reaction_plan` is a plain `TextField` (free text, blank-allowed). Do **not** build a structured reaction-plan sub-model or its own workflow.
7. No new routes, no new templates. Extend the three existing process-characteristic views/templates in place.
8. No audit/history fields, no KPI tiles, no donut charts, no Process Control Flow diagram, no PFMEA-link aggregation. All explicitly excluded from this slice (Section 3/7).

## 1. Exact Scope

Add to `ProcessCharacteristic` (`django_app/fmea_app/models.py`):

```python
class ControlType(models.TextChoices):
    ADMINISTRATIVE = "administrative", "Administrative"
    MEASUREMENT = "measurement", "Measurement"
    DETECTION = "detection", "Detection"
    MONITORING = "monitoring", "Monitoring"
    POKA_YOKE = "poka_yoke", "Poka-Yoke"
    TEST = "test", "Test"


class ControlStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    REVIEW = "review", "Review"
    INACTIVE = "inactive", "Inactive"


class ControlEffectiveness(models.TextChoices):
    EFFECTIVE = "effective", "Effective"
    PARTIALLY_EFFECTIVE = "partially_effective", "Partially Effective"
    NOT_EFFECTIVE = "not_effective", "Not Effective"
    UNKNOWN = "unknown", "Unknown"


class ProcessCharacteristic(StableModel):
    # ... existing fields unchanged ...
    control_type = models.CharField(max_length=32, choices=ControlType.choices, blank=True)
    method = models.CharField(max_length=255, blank=True)
    resource_equipment = models.CharField(max_length=255, blank=True)
    frequency_trigger = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=ControlStatus.choices, default=ControlStatus.ACTIVE)
    effectiveness = models.CharField(
        max_length=32, choices=ControlEffectiveness.choices, default=ControlEffectiveness.UNKNOWN
    )
    owner = models.ForeignKey(
        ResponsibleRole, null=True, blank=True, related_name="owned_process_characteristics",
        on_delete=models.SET_NULL,
    )
    review_due = models.DateField(null=True, blank=True)
    reaction_plan = models.TextField(blank=True)
```

Place the three new `TextChoices` classes near `ProcessCharacteristic` in `models.py` (adjacent to the existing `ActionStatus`-derived `STATUS_CHOICES` pattern on `RecommendedAction`, for consistency). `control_type` is left optional/blank (no default) since it has no obviously-correct default value; `status` and `effectiveness` get sane defaults so existing seeded rows remain valid without a data migration.

Extend `ProcessCharacteristicForm` (`django_app/fmea_app/forms.py`) to include all nine new fields in `Meta.fields`, with `owner`'s queryset set to `models.ResponsibleRole.objects.order_by("name")` (mirroring `RecommendedActionForm.__init__`) and `required=False`.

Extend `process_characteristic_list` (`views.py`) to accept two new `GET` filters — `control_type` and `status` — applied via `.filter(...)` before the existing `.order_by(...)`, each rendered as a `<select>` in the list template's existing filter form (or a newly added one if none exists yet on this page — check `process_characteristic_list.html` first; if no filter form exists there today, add a minimal `<form class="panel compact" method="get">` matching the pattern used on other list pages).

Extend `process_characteristic_list.html` and `process_characteristic_detail.html` to display the nine new fields (table columns or detail rows, matching each template's existing layout conventions) and `process_characteristic_form.html` to render the corresponding form fields (reuse whatever generic field-rendering loop/pattern the form template already uses; do not hand-roll a parallel set of `<input>` tags if the template already iterates `form`).

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/models.py                                   # + ControlType/ControlStatus/ControlEffectiveness, + 9 fields on ProcessCharacteristic
django_app/fmea_app/migrations/00XX_process_characteristic_control_fields.py  # new, additive migration
django_app/fmea_app/forms.py                                     # ProcessCharacteristicForm: add 9 fields, set owner queryset
django_app/fmea_app/views.py                                      # process_characteristic_list: + control_type/status GET filters
django_app/fmea_app/templates/fmea_app/process_characteristic_list.html    # + filter form (if absent), + new columns
django_app/fmea_app/templates/fmea_app/process_characteristic_detail.html  # + new fields in detail panel
django_app/fmea_app/templates/fmea_app/process_characteristic_form.html    # only if it does not already generically render all Meta.fields
tests/test_process_characteristic_domain.py                       # + new assertions (see Section 4)
```

Do not touch any other file. Do not add a sidebar/nav entry unless one is already missing for the existing process-characteristic pages (check `_sidebar.html`/nav templates first) — if it's already reachable, leave navigation untouched.

## 3. Required Validation and Explicit Exclusions

- No new model beyond the three `TextChoices` classes and the nine new fields on `ProcessCharacteristic`. No `ReactionPlan`, no `ControlRecord`, no `Equipment`/`Resource` model.
- No approval workflow, no state-machine transitions, no "who approved this control change" logic of any kind. Plain `ModelForm` save, same as every other CRUD form in this app.
- No audit/history fields (`created_by`, `updated_by`) and no history/change-log model.
- No KPI tiles, no donut charts (Control Type Distribution / Effectiveness Overview), no Process Control Flow diagram.
- No PFMEA-link aggregation/count column.
- No AJAX; filters are a server-side `GET` form with full page reload, matching the app's one filtering pattern.
- `owner` uses `on_delete=models.SET_NULL` (not `CASCADE`) since deleting a `ResponsibleRole` should not delete the `ProcessCharacteristic` records that reference it as owner — consistent with how `RecommendedAction.responsible_role` should behave (verify its `on_delete` and match it if different).

## 4. Required Tests

In `tests/test_process_characteristic_domain.py` (or a new `tests/test_process_characteristic_control_fields.py` if that file is reserved for domain-layer-only tests — check its current scope first):

- Migration applies cleanly against existing seeded `ProcessCharacteristic` rows with no data loss (existing `operation`/`name`/`description`/`cause_category_id`/`attributes` values unchanged).
- A `ProcessCharacteristic` can be created via `ProcessCharacteristicForm` with all nine new fields populated; `full_clean()`/form validation succeeds.
- `control_type`/`status`/`effectiveness` reject a value outside their enum (`ValidationError` on `full_clean()` with an invalid choice).
- `status` defaults to `Active` and `effectiveness` defaults to `Unknown` when not explicitly set.
- `owner` accepts `None` (nullable) and accepts a valid `ResponsibleRole` FK.
- `process_characteristic_list` view: `?control_type=measurement` and `?status=active` GET params each narrow the returned queryset correctly; an unrecognized/empty filter value returns the unfiltered list.
- `process_characteristic_detail.html` and `process_characteristic_list.html` render the new field values for a `ProcessCharacteristic` instance that has them set (a rendered-output assertion, e.g. checking `reaction_plan` text and `get_control_type_display()` output appear in the response content).
- Assert the response does **not** contain `<canvas` on these pages (no chart introduced) and does not contain any approval/workflow-state UI (guards against scope creep back toward the retracted "Control Plan" framing).

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `ProcessCharacteristic` has the nine new fields, migration applied, `makemigrations --check --dry-run` clean.
2. `process_characteristic_list` and `process_characteristic_detail` display and (via the create/edit form) allow editing all nine new fields using the app's standard table/panel/form markup.
3. `process_characteristic_list` supports `?control_type=` and `?status=` GET filters, matching the app's one server-side filtering pattern.
4. All required tests pass; full suite remains green.
5. No new model, no new route, no new charting, no audit/history, no approval workflow of any kind was introduced.

## 7. Explicit Exclusions (restated for emphasis)

This slice does not build: a Resource/Equipment catalog entity, a structured Reaction Plan sub-model or workflow, any audit/history trail (Created-by, Last-Updated-by, "View Full History"), any KPI dashboard tiles or donut charts for this page, the "Process Control Flow" diagram, or any PFMEA-link aggregation/count. None of these are gated by a governance rule — they are simply out of scope for this increment and may be proposed as their own future slices. This slice also does not introduce any approval-workflow state machine, review-and-approve step, or "silent AI edit" guard of any kind for `ProcessCharacteristic` — the earlier characterization of this mockup as a specially-gated "Control Plan" concept was incorrect and does not apply.

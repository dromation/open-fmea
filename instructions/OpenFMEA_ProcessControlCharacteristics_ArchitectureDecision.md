# Open-FMEA Architecture Decision — Process Control Characteristics (Mockup 21)

Status: **Decided, 2026-09-05**, per explicit user direction. This document corrects an earlier mischaracterization of this mockup and proposes a firm, narrow default for the next implementation slice.

## 0. Correction to the record

An earlier pass (see `OpenFMEA_DNA_CoreReference.md` and `OpenFMEA_MockupSpecifications_GUIWireframeArchitecture.md`'s coverage of Mockup 21) declared this mockup to be, in substance, "the Control Plan concept," specially gated by the standing project rule that "Approved Control Plans are never silently modified — any Control Plan change is a reviewed, human-approved workflow."

That characterization is wrong and is retracted here. The standing rule targets **AI/automated silent edits** to control-related data — it exists to stop an AI agent from quietly rewriting a control record. It does not target ordinary human-driven CRUD forms, and it does not transform every control-shaped field into a governed entity requiring an approval-workflow state machine. Mockup 21 is an **ordinary new-fields gap** on an existing model (`ProcessCharacteristic`), the same category of gap as every other unbuilt mockup field in this project. No governance workflow, approval state machine, or special review gate applies here. This document and its paired instruction describe plain fields edited through the app's normal create/edit forms.

## 1. Current state

`ProcessCharacteristic` (`django_app/fmea_app/models.py`) exists today with exactly: `operation` (FK to `Operation`), `name`, `description`, `cause_category_id`, and a generic `attributes` JSONField with no structured columns. The list/detail views and templates (`process_characteristic_list.html`, `process_characteristic_detail.html`, `process_characteristic_form.html`, backed by `process_characteristic_list`/`new_process_characteristic`/`process_characteristic_detail` in `views.py`) already exist and already render/edit `operation`, `name`, `description`, `cause_category_id`, and `attributes`.

Mockup 21 shows a table of control records carrying: Control Type, Method, Resource/Equipment, Frequency/Trigger, Status, Effectiveness, Owner, Review Due, and a "Reaction Plan" (what happens if the check fails) — none of which exist as fields today.

## 2. Decision — fields to add

Add the following fields directly to `ProcessCharacteristic`, as an ordinary additive migration, plain human-editable via the existing create/edit forms:

| Field | Type | Notes |
|---|---|---|
| `control_type` | `CharField` + `choices`, closed Python enum | `Administrative`, `Measurement`, `Detection`, `Monitoring`, `Poka-Yoke`, `Test` — a closed vocabulary is appropriate here (matches the mockup's fixed dropdown), same pattern already used for `ActionStatus` on `RecommendedAction`. |
| `method` | `CharField`, free text | e.g. "Torque check," "Visual inspection." No catalog — free text is sufficient for this increment. |
| `resource_equipment` | `CharField`, free text | **Not** a new Resource/Equipment catalog entity. A structured equipment/asset catalog is a separate, larger, not-yet-approved concept that appears in other mockups (Engineering Context Summary's "Machines/Assets" tile, Operations module). Keep this a plain text field for now; promoting it to a catalog FK is a future decision, not part of this slice. |
| `frequency_trigger` | `CharField`, free text | e.g. "Every shift," "100% inline." No structured cadence model — free text. |
| `status` | `CharField` + `choices`, closed enum | `Active`, `Review`, `Inactive`. |
| `effectiveness` | `CharField` + `choices`, closed enum | `Effective`, `Partially Effective`, `Not Effective`, `Unknown`. |
| `owner` | `ForeignKey` to `ResponsibleRole` | Same placeholder pattern already used for `RecommendedAction.responsible_role` — a name/description catalog, **not** a real user account or person roster. Nullable/optional, same as `RecommendedAction.responsible_role`. |
| `review_due` | `DateField`, nullable | No reminder/notification logic — just a stored date, filterable/sortable like any other date field. |
| `reaction_plan` | `TextField`, free text | **Not** a structured sub-model with its own workflow. Just a text field describing what happens if the check fails, for this first increment. A dedicated "Reaction Plan" entity (with its own status, owner, linked corrective action, etc.) is a plausible future increment but is explicitly out of scope here. |

All nine fields are optional/blank-friendly except where a sane default exists (`status` defaulting to `Active`, `effectiveness` defaulting to `Unknown`), so the migration is purely additive and safe against the existing seeded/demo `ProcessCharacteristic` rows.

## 3. Explicitly deferred (not part of this increment)

- Any audit/history trail: Created-by, Last-Updated-by, "View Full History." No audit/change-log entity exists anywhere in this codebase for any model; this slice does not introduce one for `ProcessCharacteristic` specifically.
- KPI dashboard tiles (Total Controls, Active, Not Effective, Needs Review, No Reaction Plan, and the mockup's unlabeled 6th tile) and the "Control Type Distribution" / "Effectiveness Overview" donut charts. These are simple aggregations once the fields exist, but adding them is a separate, later slice so this one stays focused on the model/CRUD gap.
- The "Process Control Flow" diagram. Per `OpenFMEA_MockupGUICodingRequirements.md`, this is buildable later as plain HTML/CSS (a static row of boxes with arrow connectors) — no charting library or new data model needed. Not a blocker for this slice; simply not included in it.
- PFMEA-link aggregation ("Top PFMEA Links" / "PFMEA Links" count column) — a computed aggregate joining `ProcessCharacteristic` through `FailureCause`/`FailureMode`/`RiskEvaluation` that does not exist today and needs its own query design. Deferred.

## 4. Scope of the paired implementation slice

1. Model field additions listed in Section 2, plus one additive migration.
2. Extend the existing `process_characteristic_list` view/template and `process_characteristic_detail` view/template to display and edit the new fields (via the existing `ProcessCharacteristicForm`), reusing the app's existing table/panel/form conventions (`.table-shell`, `.panel`).
3. Standard GET-form filters on the list page, matching the app's one filtering pattern: filter by `control_type` and by `status` (two `<select>` dropdowns, server-side `GET`, full page reload — no AJAX).

Nothing else. No new routes, no new templates, no new sidebar entry beyond what's needed to reach the already-existing pages (the sidebar entry itself, if genuinely absent, is a one-line addition noted in the paired instruction, not a redesign).

## 5. Risks / open questions

- `control_type`/`status`/`effectiveness` as `CharField(choices=...)` mirrors the existing `ActionStatus` pattern on `RecommendedAction` (Python `Enum` feeding Django `choices`) rather than a new domain-layer entity — recommended for consistency, not re-litigated here.
- `owner` reusing `ResponsibleRole` inherits that model's known limitation (a name/description catalog, not a real per-person roster tied to login) — already flagged project-wide for other mockups (Mockup 5/22); not a new risk introduced by this slice.

## 6. Recommendation

**Recommendation: READY FOR IMPLEMENTATION** — ordinary additive fields on an existing model, no governance workflow needed.

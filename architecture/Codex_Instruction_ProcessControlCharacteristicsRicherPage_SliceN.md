# Codex Implementation Instruction — Slice N: Process Control Characteristics Richer Standalone Page

Status: **Instruction, 2026-09-06** — implements `OpenFMEA_ProcessControlCharacteristicsRicherPage_ArchitectureDecision.md` exactly as decided there. Do not add, reinterpret, or "improve" anything beyond what is written below; if something here seems to conflict with the live code, stop and report back rather than guessing.

## 0. Decisions for this slice (restated from the architecture decision doc — do not re-derive)

1. Six KPI tiles (Total, Active, Not Effective, Needs Review, No Reaction Plan, Linked) — all six are aggregate queries over existing fields. No new model fields.
2. "Linked to PFMEA" = the characteristic's `operation.process.fmea` resolves and that FMEA's `fmea_type == "process"`. This is the *only* PFMEA-link fact this slice computes. No new join table, no per-cause link.
3. Right-docked detail panel driven by `?selected=<stable_id>&tab=general|method|reaction|links|history` on the existing `process_characteristic_list` route. No new route. No AJAX, no client-side tab-swap — every tab and every row-select is a normal `<a href>` GET link causing a full page render.
4. "History" tab shows only `created_at` / `updated_at`. Nothing else. Do not add an actor or field-diff trail — none exists on this model or anywhere else in this codebase.
5. Process Control Flow diagram is static HTML/CSS boxes (Process Step → Control Characteristic → Resource/Method → Result → Reaction) restating real field values already on the selected characteristic. "Result" is static descriptive text derived from `method`/`control_type` wording — never a stored field, never implies a logged inspection outcome.
6. Two Chart.js donuts: Control Type Distribution (`group by control_type`), Effectiveness Overview (`group by effectiveness`) — same `json_script` + inline `<script>` + `new Chart()` pattern as Slice K's existing dashboard chart. Use the already-vendored `django_app/fmea_app/static/fmea_app/vendor/chartjs/chart.umd.min.js`; do not add a new vendored copy or a CDN reference.
7. "Top PFMEA Links" table: PFMEA name + count of linked `ProcessCharacteristic`s only (per Decision 2's definition). No "Top Cause/FM" column.

## 1. Exact Scope

Modify only:
- `django_app/fmea_app/views.py` — extend the existing `process_characteristic_list` view function only. Do not touch `process_characteristic_detail` or `process_characteristic_form` (or their view functions) in any way.
- `django_app/fmea_app/templates/fmea_app/process_characteristic_list.html` — extend this one template only.
- `django_app/fmea_app/static/fmea_app/css/*.css` (whichever file already holds `.stat-tile`, `.panel`, `.grid`/`.split` etc. — locate it first, do not create a new stylesheet) — add only additive classes named below.

Do not touch: `urls.py` (no new route — everything hangs off the existing list URL via GET params), `models.py` (no migration in this slice — every value used already exists on `ProcessCharacteristic`, `Operation`, `Process`, `FMEA`), `forms.py`, `process_characteristic_detail.html`, `process_characteristic_form.html`, `_sidebar.html`, `app.js`.

## 2. Exact Allowed-New Files

None. This is a pure extension of three existing files (view, template, stylesheet). If Chart.js's vendored file is not already present at the path named in Decision 6 above, stop and report — do not re-vendor it; Slice K already established it.

## 3. Required Validation and Explicit Exclusions

- The six KPI tile queries, the "Linked" definition, and the two donut groupings must all be computed from the **already-filtered queryset** backing the list (i.e., respect whatever `control_type`/`status`/new filter GET params are active) — not a separate unfiltered count, so the numbers on screen stay internally consistent with the table below them.
- `?selected=<stable_id>` must validate that the characteristic belongs to the currently-filtered/visible set or at minimum exists at all (404/graceful-empty-panel on a bad id) — do not let it silently 500.
- `?tab=` must default to `general` for any value that is missing or not one of the five named values — do not 500 on an unrecognized tab value.
- The "Result" text in the flow diagram must be generated from `method`/`control_type` wording only — grep the final diff for any new model field, migration, or hardcoded per-instance "PASS"/"FAIL"/"OK"/"NOK" literal tied to a specific characteristic instance; there must be none.
- Explicit exclusions to verify absent from the diff by name/grep before calling this done:
  - No new migration file.
  - No new join table / model for characteristic-to-cause or characteristic-to-failure-mode linking.
  - No "Top Cause/FM" column or any per-row cause/failure-mode ranking logic.
  - No actor/user field-change audit trail (only `created_at`/`updated_at` rendered).
  - No AJAX/`fetch`/`XMLHttpRequest` calls, no client-side tab framework, no modal/drawer JS — every new interaction is a server-rendered GET link.
  - No new CDN `<script src="https://...">` tag — only the already-vendored local Chart.js file.
  - No "Control Plan" / approval-workflow language anywhere in new template text or comments.
  - No Resource/Equipment catalog model — `resource_equipment` stays the existing free-text field.

## 4. Required Tests

Add to the existing `fmea_app` test module covering `process_characteristic_list` (locate it — do not create a new test file):
1. KPI row: seed a small fixed set of `ProcessCharacteristic` rows with known `status`/`effectiveness`/`reaction_plan` values and assert each of the six tile counts matches expectation exactly.
2. "Linked to PFMEA" fact: one characteristic whose `operation.process.fmea.fmea_type == "process"` and one whose FMEA is `fmea_type == "design"` (or whose chain doesn't resolve) — assert the first counts as linked and the second does not, in both the KPI tile and the "Top PFMEA Links" table.
3. Detail panel: `?selected=<valid id>` renders that characteristic's real field values in the `general`/`method`/`reaction` tabs; `?selected=<valid id>&tab=history` renders only `created_at`/`updated_at` and nothing else asserted as an audit entry; an invalid/missing `selected` value does not 500 (assert graceful response, e.g. 200 with empty panel or 404, whichever the implementation lands on — pick one and assert it consistently).
4. Existing filter GET params (`control_type`, `status`) still work unchanged and the KPI/donut numbers move together with the filtered table when a filter is applied (regression + consistency check for the point above).
5. Full existing test suite for this app still passes (regression) — run it, do not just add these five.

## 5. Commands to Run

Run inside the project's existing virtualenv/test setup (whatever `manage.py test` invocation the existing Slice D–M tests already use — do not introduce a new one):
```
python manage.py test fmea_app
```
Run in both `open_fmea` and `open_fmea_training_set` if that is this project's established practice for prior slices (confirm against how Slices D–M were verified) — report the test count delta (before/after) in the completion report, the same way prior slices did.

## 6. Acceptance Criteria

- All new tests from Section 4 pass; full existing suite still passes with no regressions; report the exact before/after test count.
- `git diff` (or equivalent) touches only the three files named in Section 1 (plus the test file housing the five new tests) — no migration, no new route, no new model.
- Every item in Section 3's exclusion list is confirmed absent by direct grep in the completion report, not just asserted from memory.
- KPI tiles, donuts, and the "Top PFMEA Links" table all move consistently with active filters (manually or via the tests in Section 4).

## 7. Explicit Exclusions (restated)

No new migration. No per-cause/per-failure-mode PFMEA link. No "Top Cause/FM" ranking. No audit/actor trail beyond `created_at`/`updated_at`. No AJAX or client-side tab/panel-swap anywhere. No new charting library or CDN reference. No Resource/Equipment catalog entity. No Control-Plan/approval-workflow language. No changes to `process_characteristic_detail`, `process_characteristic_form`, `urls.py`, `_sidebar.html`, or `app.js`.

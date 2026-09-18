# Codex Implementation Instruction — Risk Trajectory & Propagation (Slice J)

Status: Approved for implementation, 2026-09-04. Grounded in `OpenFMEA_RiskTrajectoryPropagation_ArchitectureDecision.md` (READY FOR IMPLEMENTATION for the lifecycle-gate/trajectory piece; propagation chain explicitly deferred, not part of this slice). Builds one additive field on the existing `RiskEvaluation` model plus a read-only trajectory view reachable from the already-built Risk Matrix. Nothing else from Mockup 17 is in scope.

## 0. Decisions for this slice

1. **`lifecycle_gate` is an additive `CharField` with `choices` directly on `RiskEvaluation`** — not a new model, not a new FK. Six values: `concept_design` / `design_verification` / `process_validation` / `pre_production` / `serial_production` / `current`, default `"current"`. A plain Django-choices enum, matching the exact precedent of `FMEA.LIFECYCLE_CHOICES`/`ActionStatus` — this vocabulary is closed and structural, not organization-configurable.
2. **The field is optional on the evaluation form and defaults to `"current"` when left unset.** No auto-classification logic decides the gate — a human either picks one or accepts the default, matching this project's standing "never auto-assign" principle. Existing rows are backfilled to `"current"` by the migration's field default — no separate data migration.
3. **The trajectory view is read-only** — it displays existing `RiskEvaluation` history, ordered chronologically ascending (`evaluated_at`, `id`) for readability as a story-over-time, the deliberate reverse of the model's own default `-evaluated_at` ordering (which optimizes for "latest first"). It does not let you edit or delete a past evaluation, and it does not create new ones — new evaluations continue to go through the existing `evaluate_failure` flow only.
4. **Every score/band shown is read verbatim from `RiskEvaluation.result`**, never recomputed by calling `fmea_evaluation.calculate()` again — matching the Risk Matrix instruction's own explicit exclusion, for the same reason (never silently diverge from what was actually stored/reviewed at evaluation time).
5. **No propagation chain, no chart, no PM-FMEA cross-reference** — see Section 3/7. This slice is the lifecycle-gate field and the trajectory table only.
6. **One new sidebar entry**, "Risk Trajectory & Propagation" (the exact label already fixed by the canonical nav structure in `OpenFMEA_DNA_CoreReference.md`), placed in the same nav group as the existing "Risk Matrix" entry — not a new group, not a tab folded inside the Risk Matrix page itself (it is its own page/route, only *linked from* the Risk Matrix's drill-down, per the architecture decision Section 4.4).

## 1. Exact Scope

1. **`RiskEvaluation.lifecycle_gate`** (`fmea_app/models.py`): `CharField(max_length=32, choices=LIFECYCLE_GATE_CHOICES, default="current")`, where `LIFECYCLE_GATE_CHOICES` is:
   ```python
   LIFECYCLE_GATE_CHOICES = [
       ("concept_design", "Concept/Design"),
       ("design_verification", "Design Verification"),
       ("process_validation", "Process Validation"),
       ("pre_production", "Pre-Production (PPAP)"),
       ("serial_production", "Serial Production (SOP)"),
       ("current", "Current"),
   ]
   ```
2. **`evaluate_failure_mode()`** (`fmea_app/services.py`): add an optional `lifecycle_gate: str = "current"` keyword argument, included in the `values` dict passed to `.create()`/`update_or_create()` — additive only, every existing call site keeps working unchanged if it doesn't pass the new argument.
3. **`RiskEvaluationForm`** (`fmea_app/forms.py`): add an optional `lifecycle_gate = forms.ChoiceField(choices=models.RiskEvaluation.LIFECYCLE_GATE_CHOICES, required=False)`. The `evaluate_failure` view passes `form.cleaned_data.get("lifecycle_gate") or "current"` through to `evaluate_failure_mode()`.
4. **Trajectory index** — route `/risk-trajectory/` (`fmea:risk_trajectory_index`): a plain list of every `FailureMode` that has at least one `RiskEvaluation`, each row showing the `FailureMode` name, its parent `FMEA` name (linking to `fmea:fmea_detail`), and its evaluation count, linking to that `FailureMode`'s trajectory detail page. This is the sidebar's landing target — same "simple list" idiom as `risk_matrix_top.html`.
5. **Trajectory detail** — route `/failure-mode/<str:stable_id>/risk-trajectory/` (`fmea:risk_trajectory`): a `.table-shell`/`<table>` of every `RiskEvaluation` for that `FailureMode`, ordered oldest-first, columns: Date (`evaluated_at`) / Lifecycle Gate (`get_lifecycle_gate_display`) / Method / Severity / Occurrence / Detection / Score or Band (read from `result` — `result["score"]` when present, otherwise `result` however the method actually shapes it, e.g. the `aiag-vda-ap-poc` band; read verbatim, same asymmetry note already established in `risk_matrix.py`) / Actor.
6. **Risk Matrix drill-down link** — in `risk_matrix_cell.html`, add a "View Trajectory" link on each listed `FailureMode` row, pointing to `fmea:risk_trajectory` for that `FailureMode`'s `stable_id`. No other change to `risk_matrix_cell.html`, `risk_matrix.html`, or `risk_matrix_top.html`.
7. **Sidebar** — add exactly one new `<a class="nav-link">` entry, "Risk Trajectory & Propagation," to `_sidebar.html`, in the same nav group as the existing "Risk Matrix" link, pointing to `fmea:risk_trajectory_index`.

Nothing beyond this list.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/models.py                                   # add lifecycle_gate field + LIFECYCLE_GATE_CHOICES on RiskEvaluation only
django_app/fmea_app/migrations/0006_riskevaluation_lifecycle_gate.py  # new (renumber if a later migration already exists)
django_app/fmea_app/services.py                                 # evaluate_failure_mode: add optional lifecycle_gate kwarg only
django_app/fmea_app/forms.py                                     # RiskEvaluationForm: add optional lifecycle_gate field only
django_app/fmea_app/views.py                                     # add risk_trajectory_index, risk_trajectory views; evaluate_failure: thread lifecycle_gate through
django_app/fmea_app/urls.py                                       # add the two new routes only
django_app/fmea_app/templates/fmea_app/risk_trajectory_index.html # new
django_app/fmea_app/templates/fmea_app/risk_trajectory.html       # new
django_app/fmea_app/templates/fmea_app/risk_matrix_cell.html      # add the one "View Trajectory" link per row only
django_app/fmea_app/templates/fmea_app/_sidebar.html               # add the one nav link, nothing else

tests/test_risk_trajectory.py                                     # new
```

Nothing else. No changes to `fmea_domain/`, `fmea_evaluation/calculators.py`, `FailureEffect`, `risk_matrix.py`'s query logic, or `risk_matrix.html`/`risk_matrix_top.html`.

## 3. Required Validation and Explicit Exclusions

- No new model, no new FK, no self-referential `FailureEffect` field, no chain/edge entity — `lifecycle_gate` is the only schema change, additive to `RiskEvaluation`.
- No propagation-chain content anywhere (no "Local Effect"/"Next-Level Effect"/"System Effect"/"End Effect" field, column, or panel).
- No recomputation of score/band in the trajectory view — always read `RiskEvaluation.result` verbatim, never call `fmea_evaluation.calculate()` from the display path.
- No `<canvas>`, no chart/graph library reference, anywhere in the new templates.
- No PM-FMEA cross-reference panel or link.
- The existing `evaluate_failure` flow keeps working with `lifecycle_gate` omitted from the POST — falls back to `"current"`, never a validation error.
- `_sidebar.html` diff is exactly one new `<a class="nav-link">` line; `risk_matrix_cell.html` diff is exactly the one new link per row — no other markup changed in either file.
- The trajectory detail page is read-only — no edit/delete control for any `RiskEvaluation` row.

## 4. Required Tests

`tests/test_risk_trajectory.py`:

- Migration/model: create a `RiskEvaluation` without passing `lifecycle_gate` and assert it defaults to `"current"`; create one passing an explicit gate and assert it persists and round-trips via `get_lifecycle_gate_display()`.
- Seed a `FailureMode` with three or more `RiskEvaluation`s at different `evaluated_at` timestamps and different `lifecycle_gate` values (including at least one under each of two different `method`s, mirroring the existing Risk Matrix test fixture style); render `/failure-mode/<stable_id>/risk-trajectory/` and assert all rows appear, in ascending chronological order, each showing the correct gate label, method, S/O/D, and the real stored `result` value verbatim (seed one row with a deliberately stale `result` and confirm the view shows that stale value, not a recomputed one — same proof pattern as `test_risk_matrix.py`).
- Render `/risk-trajectory/` and assert it lists that `FailureMode` (name + parent FMEA link + evaluation count) and links correctly to its trajectory detail page; assert a `FailureMode` with zero evaluations does not appear.
- Render `/risk-matrix/cell/?method=...&severity=...&occurrence=...` for a cell containing a seeded `FailureMode` and assert its row now includes a "View Trajectory" link pointing to the correct `fmea:risk_trajectory` URL.
- Submit `evaluate_failure` both with and without a `lifecycle_gate` value in the POST; assert the resulting `RiskEvaluation` has the explicit gate in the first case and `"current"` in the second.
- Assert the trajectory index and detail pages contain no `<canvas` markup and no "Local Effect"/"Next-Level Effect"/"System Effect"/"End Effect"/"PM-FMEA" text — a negative check consistent with `test_gui_navigation_scope.py`'s existing pattern.
- `_sidebar.html`: assert exactly one new "Risk Trajectory & Propagation" link is present, linking to `fmea:risk_trajectory_index`, and every previously-asserted-absent label in `test_gui_navigation_scope.py` remains absent.
- Full existing suite re-run with no unrelated assertion changes, including `test_risk_matrix.py` unchanged in its existing assertions (only the one new link is additive).

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `RiskEvaluation` gains exactly one new field, `lifecycle_gate`, defaulting to `"current"`, with no other model change.
2. The evaluation form/flow accepts an optional lifecycle gate and defaults correctly when omitted.
3. `/risk-trajectory/` and `/failure-mode/<stable_id>/risk-trajectory/` render correctly, chronologically ordered, showing real stored data only (no recomputation).
4. The Risk Matrix's cell drill-down gains exactly one new "View Trajectory" link per row; no other change to any Risk Matrix template or query logic.
5. Sidebar gains exactly one new "Risk Trajectory & Propagation" link; no other nav change.
6. No propagation-chain model, field, or content anywhere in the diff; no chart/canvas markup; no PM-FMEA content.
7. Full test suite passes, `manage.py check` clean, exactly one new migration (`0006_riskevaluation_lifecycle_gate.py` or the correct next sequential number).
8. Mirrored into `open_fmea_training_set` per this project's standing discipline (byte-diffed, not just size/mtime).

## 7. Explicit Exclusions (restated for emphasis)

The failure-propagation chain (Local Effect → Next-Level Effect → System Effect → End Effect) and any self-referential `FailureEffect`/chain/edge entity — explicitly deferred to its own future architecture review, not built here. Any chart, trend line, or `<canvas>` element. Any PM-FMEA/Asset-Maintenance cross-reference panel or link. Any % reduction, primary-cause, or "actions impacting this risk" analytics beyond the plain trajectory table. Any change to `fmea_evaluation/calculators.py`, `risk_matrix.py`'s query logic, `risk_matrix.html`, or `risk_matrix_top.html` beyond the one link added to `risk_matrix_cell.html`. Any edit/delete capability on a past `RiskEvaluation` row. If any of this seems to need changing to deliver a working slice, stop and report — do not silently expand scope.

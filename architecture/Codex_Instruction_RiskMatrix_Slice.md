# Codex Implementation Instruction — Risk Matrix (Slice: RiskMatrix-1)

Status: Approved for implementation. Grounded in `OpenFMEA_RiskMatrix_ArchitectureReview.md`; all four of its open decisions were confirmed by the user on 2026-09-01: system-wide scope (all FMEAs, no per-project grouping — none exists), the review's proposed severity×occurrence banding thresholds, a method-filterable grid (not "most recent evaluation wins" regardless of method), and a full 10×10 grid (not a collapsed band summary).

Authority, in order: same chain as prior slices; additionally subordinate to `OpenFMEA_RiskMatrix_ArchitectureReview.md` (design authority for this slice) and `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` (visual language and tooling constraints — this slice adds one new sidebar/dashboard surface to that already-built shell, it does not re-derive its own design system).

## 0. What "filterable by method" means, precisely — read before starting

The grid's cell placement is always severity × occurrence (1–10 each), regardless of method — detection is never a grid axis. A method selector (`classic-rpn` / `aiag-vda-ap-poc`, using the exact constants from `fmea_evaluation.calculators`) changes two things only: (a) **which `FailureMode`s appear on the grid** — only those with at least one `RiskEvaluation` whose `method` matches the selected value, using that `FailureMode`'s most recent evaluation *under that specific method* (not its most recent evaluation overall); (b) **what score/band shows in the drill-down** for a plotted `FailureMode` — the actual computed RPN score+band for `classic-rpn`, the actual computed AP band for `aiag-vda-ap-poc`, both read from the existing `RiskEvaluation.result` dict, never recomputed by the view. The banding that colors each grid *cell* (Section 2) is independent of method — it's always the severity×occurrence product banding from the architecture review, applied the same way regardless of which method is selected.

## 1. Exact Scope

1. A banding function for severity×occurrence, additive to `fmea_evaluation/calculators.py` — does not touch `classify_rpn`, `calculate_action_priority`, or `calculate`.
2. A risk-matrix view: a 10×10 grid, method-filterable, system-wide (every `FailureMode` across every `FMEA`), with cell counts and a drill-down per cell.
3. A "Top High Risk Items" view/widget reusing the same underlying data, sorted by computed score descending.
4. A sidebar entry and a dashboard card for the matrix, added to the already-built GUI shell — the one, deliberate, reviewed addition to `test_gui_navigation_scope.py`'s allow-list.

Nothing beyond this list. No new entity, no new migration, no change to `RiskRating`/`RiskEvaluation`/`EvaluationDefinition`, no per-project scoping mechanism, no charting/canvas library.

## 2. Required Logic

`fmea_evaluation/calculators.py` — add, do not modify existing functions:

```python
def classify_severity_occurrence(severity: int, occurrence: int) -> str:
    """Bands a (severity, occurrence) pair on the same 1-10 scale RiskRating
    already validates to. Independent of any RiskEvaluation method — this is
    a grid-coloring band, not a replacement for classify_rpn or the AP bands."""
    product = severity * occurrence
    if product <= 8:
        return "low"
    if product <= 24:
        return "medium"
    if product <= 48:
        return "high"
    return "very_high"
```

Query logic (in `fmea_app/services.py` or a new `fmea_app/risk_matrix.py` — your call, but keep it out of `views.py` so it's independently testable): for a given `method` string, for every `FailureMode`, find its most recent `RiskEvaluation` where `.method == method` (there may be none — exclude that `FailureMode` from this method's grid entirely, do not show a zero/blank placeholder for it). Group the resulting set by `(inputs.severity, inputs.occurrence)`. This is a single filtered `.order_by("-evaluated_at")` query grouped in Python (or a `Window`/`annotate` if you prefer, your call) — not new aggregation infrastructure, matches the "simple counts/filters" constraint carried over from the GUI-shell instruction.

## 3. Required APIs

- `GET /risk-matrix/?method=classic-rpn` (default when `method` is omitted or unrecognized — do not error, fall back to `classic-rpn`) — renders the 10×10 grid, each cell showing a count, colored by `classify_severity_occurrence(severity, occurrence)`, plus a plain-text count of `FailureMode`s with no evaluation under the selected method ("N failure modes have no {method} evaluation yet").
- `GET /risk-matrix/cell/?method=...&severity=N&occurrence=N` — drill-down: lists the `FailureMode`s in that cell, each showing its name, parent `FMEA`, and the actual computed score/band from its `RiskEvaluation.result` (never recomputed — read what's stored).
- `GET /risk-matrix/top/?method=classic-rpn` — "Top High Risk Items": every `FailureMode` with an evaluation under the selected method, sorted by computed score descending (read `result["score"]` for `classic-rpn`; for `aiag-vda-ap-poc` there is no numeric score in the calculator's current output — sort by band severity order `high > medium > low` for that method, and say so in a code comment since this is a real asymmetry between the two methods' output shape, not an oversight).
- Method selector: a simple `<select>`/tab pair on the matrix and top-items pages (`classic-rpn` / `aiag-vda-ap-poc`), submitting via GET query param — no JS framework needed, a plain form/links is sufficient.

## 4. GUI Integration

- Sidebar: add **Risk Matrix** to the GUI shell's nav (`_sidebar.html`) — this is the one deliberate addition to the previously-locked-down list. Update `test_gui_navigation_scope.py`'s allow-list accordingly (it should now assert Risk Matrix *is* present, alongside continuing to assert the still-excluded labels — Validation Trajectory, CAPA, Control Plans, etc. — remain absent).
- Dashboard: add one real stat card — count of `FailureMode`s in the `high`/`very_high` bands under the default method (`classic-rpn`) — computed the same way as Section 2, not a new query shape. Do not add a heatmap thumbnail to the dashboard card itself; the card is a number + link to `/risk-matrix/`, consistent with every other dashboard card's "real number, no fabricated visualization" pattern from the GUI-shell instruction.
- Reuse the existing card/table/status-badge components and CSS tokens from `theme.css` — the grid itself is the one new visual pattern (a 10×10 CSS grid with background-color per band, using the existing `--status-good/warning/critical` tokens plus one new token for a fourth "very_high" tier if needed, added to `theme.css` additively).

## 5. Exact Allowed / New Files

```text
django_app/fmea_evaluation/calculators.py     # add classify_severity_occurrence only

django_app/fmea_app/risk_matrix.py            # query logic, Section 2 (or services.py — your call)
django_app/fmea_app/views.py                  # risk_matrix, risk_matrix_cell, risk_matrix_top views
django_app/fmea_app/urls.py
django_app/fmea_app/templates/fmea_app/
    risk_matrix.html
    risk_matrix_cell.html
    risk_matrix_top.html
django_app/fmea_app/templates/fmea_app/_sidebar.html    # add the one nav entry
django_app/fmea_app/templates/fmea_app/dashboard.html    # add the one stat card
django_app/fmea_app/static/fmea_app/css/theme.css        # additive: grid + band color tokens

tests/test_risk_matrix.py
tests/test_gui_navigation_scope.py            # update: assert Risk Matrix IS present now; everything else still excluded
```

## 6. Required Validation and Explicit Exclusions

- Cell placement never uses detection — confirmed by a test (Section 7).
- A `FailureMode` never appears twice on the same method's grid.
- `method` query param values outside `{classic-rpn, aiag-vda-ap-poc}` fall back to `classic-rpn` silently (not a 500, not a validation error — this is a display filter, not a form submission with a contract to enforce strictly).
- No per-project scoping mechanism — confirmed system-wide by the user, do not build a `Project`-like grouping to partially satisfy the mockup's framing.
- No recomputation of RPN/AP scores in the view layer — always read `RiskEvaluation.result`, never call `calculate()` again from the display path (that would silently diverge from whatever was actually stored/reviewed at evaluation time).
- No chart/canvas library — plain CSS grid, matching every prior slice's tooling constraint.

## 7. Required Tests

- `test_risk_matrix.py`: seed several `FailureMode`s with `RiskEvaluation`s under both methods (including a `FailureMode` with evaluations under both methods at different `evaluated_at` times, and one with only one method); assert `/risk-matrix/?method=classic-rpn` and `?method=aiag-vda-ap-poc` each show the correct, distinct sets of `FailureMode`s; assert a `FailureMode` with no evaluation under a given method is excluded from that grid and counted in the "no evaluation yet" message; assert `classify_severity_occurrence`'s four bands match the review's thresholds exactly (8/24/48 boundaries); assert the drill-down endpoint shows the real stored `result` score/band, not a recomputed one (seed a `RiskEvaluation` with a deliberately "wrong"/stale `result` value and confirm the view displays that stale value verbatim — proves it isn't recomputing).
- `test_gui_navigation_scope.py`: updated to assert "Risk Matrix" **is** present in the rendered nav, while every other still-excluded label from the GUI-shell instruction remains absent.
- Full existing suite re-run with no unrelated assertion changes.

## 8. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --no-input
python -B -m pytest
```

## 9. Acceptance Criteria

1. `/risk-matrix/` renders a 10×10 grid, system-wide, method-filterable, correctly banded per Section 2's exact thresholds.
2. Switching method changes which `FailureMode`s appear and what score/band their drill-down shows; cell placement (severity×occurrence) and cell banding are unaffected by the method switch.
3. `/risk-matrix/top/` shows the same underlying data sorted by real, stored computed score/band.
4. The dashboard gains exactly one new real stat card; the sidebar gains exactly one new nav entry; `test_gui_navigation_scope.py` is updated to reflect precisely that one addition and nothing else.
5. No new entity, migration, per-project concept, or charting library appears in the diff.
6. Full test suite passes, `manage.py check` clean, no unexpected migration.
7. Mirrored into `open_fmea_training_set` and the training EXE rebuilt, with the same clean-run verification discipline as every prior slice — including, this time, actually completing the mirror (the characteristics-linking/GUI-shell slices' mirror was still outstanding as of the last verification; do not let this slice's mirror go the same way).

## 10. Explicit Exclusions (restated for emphasis)

`Project` entity or any per-project scoping, detection as a grid axis, recomputing RPN/AP scores in the display layer, any chart/canvas library, any change to `classify_rpn`/`calculate_action_priority`/`calculate`, any new sidebar/dashboard entry beyond the one Risk Matrix addition, any of the still-deferred sections (Validation Trajectory, CAPA, Control Plans, SPC, XDA, Operations, Project Health, PM-FMEA/Asset/Maintenance).

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

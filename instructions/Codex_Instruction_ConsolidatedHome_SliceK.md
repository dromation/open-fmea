# Codex Implementation Instruction — Consolidated Home (Slice K)

Status: Approved for implementation, 2026-09-04. Per `OpenFMEA_ConsolidatedHome_ArchitectureDecision.md` (2026-09-05): extend the existing `fmea:dashboard` view/template with the stat cards, Actions summary, and one risk-trend chart that are derivable from real, already-existing data. The Operations module and any computed "health score" are explicitly not part of this slice — see Section 7.

## 0. Decisions for this slice

1. This is purely additive to the existing `dashboard` view and `dashboard.html` template — no new route, no new template file.
2. New stat tiles: Project count, Failure-Mode count, Action count. Check `dashboard.html`/`dashboard()` first for any of these already being computed or rendered under a different label before adding a duplicate tile.
3. Actions summary is Total / Overdue / Due Soon, computed at render time from real `RecommendedAction.status`/`.due_date` — no new model, no stored/cached field.
   - Overdue = `due_date < today` AND `status not in {completed, verified, cancelled}`.
   - Due Soon = `today <= due_date <= today + 7 days` AND `status not in {completed, verified, cancelled}`.
4. Risk-trend chart: Chart.js **bar** chart (simpler than line for a daily-count series; equivalently acceptable per the architecture decision), counting `RiskEvaluation` rows per day over the trailing 30 days, grouped by `evaluated_at` date. If the demo dataset is too sparse for daily buckets to be meaningful, group by week instead — implementer's call; state which was chosen in the PR/commit description.
5. Chart.js is loaded from the already-vendored local static file per `OpenFMEA_ChartingLibrary_ArchitectureDecision.md` (`{% static %}`, never a CDN). If it has not yet been vendored into `static/fmea_app/vendor/chartjs/` by any prior slice, vendoring it is in scope for this slice (download once, commit the UMD file, do not add a build step).
6. Data is passed to the template via `{{ data|json_script:"risk-trend-data" }}` and a small inline `<script>` reads it and calls `new Chart(...)`, per the fixed pattern in the charting decision. No AJAX/fetch endpoint.
7. No Operations module, no PM-FMEA donut, no health score/gauge, no coverage bars, no data-integrity/broken-link counts. None of these are touched in any way — not stubbed, not placeholder-rendered.

## 1. Exact Scope

In `django_app/fmea_app/views.py`, extend `dashboard(request)` to add to its context:

```python
today = timezone.now().date()
non_terminal_statuses = [
    ActionStatus.OPEN.value,
    ActionStatus.IN_PROGRESS.value,
]
actions_total = models.RecommendedAction.objects.count()
actions_overdue = models.RecommendedAction.objects.filter(
    due_date__lt=today, status__in=non_terminal_statuses
).count()
actions_due_soon = models.RecommendedAction.objects.filter(
    due_date__gte=today, due_date__lte=today + timedelta(days=7), status__in=non_terminal_statuses
).count()

project_count = FMEAProject.objects.count()
failure_mode_count = models.FailureMode.objects.count()
action_count = actions_total

risk_trend_labels, risk_trend_counts = _risk_evaluation_trend(days=30)
```

Add a module-level (or view-adjacent) helper `_risk_evaluation_trend(days: int)` that:
- Computes `start = today - timedelta(days=days)`.
- Queries `RiskEvaluation.objects.filter(evaluated_at__date__gte=start).annotate(day=TruncDate("evaluated_at")).values("day").annotate(count=Count("id")).order_by("day")` (or `TruncWeek` if weekly buckets were chosen per Decision 4).
- Fills any zero-count day/week gaps so the chart has a continuous, evenly-spaced x-axis (a dict comprehension over the full date range, defaulting missing buckets to 0).
- Returns two parallel lists: labels (ISO date strings) and counts (ints).

Pass `risk_trend_labels`/`risk_trend_counts` (or a single combined dict) into the template context for `json_script`.

In `dashboard.html`:
- Add stat tiles for Project count, Failure-Mode count, Action count to the existing KPI row via the existing `_stat_tile.html` include (same pattern as the existing "FMEA Projects"/"Pending Review" tiles).
- Add an Actions summary panel/tile-group (Total/Overdue/Due Soon), using `.panel`/`.stat-tile` conventions already established on this page.
- Add a new `.panel` containing `<canvas id="risk-trend-chart">`, a `{{ risk_trend_data|json_script:"risk-trend-data" }}` block, and a small inline `<script>` (or a new `dashboard.js` file if the app's convention is to keep page-specific JS out of templates — check `app.js`/existing template `<script>` usage first and match it) that reads the JSON and initializes a Chart.js bar chart.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/views.py                                    # dashboard(): + actions summary + risk trend context, + _risk_evaluation_trend helper
django_app/fmea_app/templates/fmea_app/dashboard.html            # + 3 stat tiles, + Actions summary panel, + risk-trend chart panel/canvas
django_app/fmea_app/static/fmea_app/vendor/chartjs/chart.umd.min.js   # only if not already vendored by a prior slice
tests/test_dashboard_view.py                                     # + new assertions (see Section 4)
```

Do not touch `risk_matrix.py`, any Operations-related file (none exist — do not create one), or any PM-FMEA-related code path.

## 3. Required Validation and Explicit Exclusions

- No new model, no new migration.
- No new route — everything renders on the existing `fmea:dashboard` URL.
- No AJAX/fetch; the chart's data is server-computed and embedded via `json_script`, matching the fixed charting-decision pattern.
- No "Operations" card, section, or nav entry of any kind.
- No PM-FMEA donut or PM-FMEA-scoped query of any kind.
- No "Overall Health" score, gauge, or any composite-metric computation.
- No coverage-bar computation (DFMEA/PFMEA/PM-FMEA validation coverage).
- No "Unlinked Items"/"Broken Links"/data-integrity computation.
- The risk-trend chart counts `RiskEvaluation` rows created per day/week — it does **not** attempt to reconstruct "which risk tier was each failure mode in as of date X" (a materially harder query the mockup's original line chart implies); this simpler substitute is the deliberate, stated scope.

## 4. Required Tests

In `tests/test_dashboard_view.py`:

- `dashboard` view returns the three new stat tile values matching direct `.count()` queries against seeded test data (Project, FailureMode, RecommendedAction counts).
- Actions summary: create `RecommendedAction` fixtures with a mix of past-due/open, due-in-3-days/open, due-in-30-days/open, and past-due/completed; assert `actions_overdue`/`actions_due_soon`/`actions_total` match the expected counts (the completed-but-overdue action must **not** count as overdue).
- Risk-trend helper: create `RiskEvaluation` rows on specific known dates within and outside the 30-day window; assert the returned labels/counts include only in-window dates, correctly bucketed, with zero-filled gaps for days/weeks with no evaluations.
- Rendered response contains exactly one `<canvas id="risk-trend-chart"` and a `json_script` block whose contents parse as JSON matching the computed trend data.
- Rendered response does **not** contain any of: "Operations", a PM-FMEA-labeled donut, "Overall Health", "Coverage" (DFMEA/PFMEA/PM-FMEA bars), or "Broken Links" — guarding against scope creep into the excluded sections of the mockup.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `dashboard.html` shows Project/Failure-Mode/Action stat tiles alongside the existing tiles, all real counts.
2. An Actions summary panel shows Total/Overdue/Due Soon, all real, correctly computed.
3. A single Chart.js bar (or line) chart renders a 30-day `RiskEvaluation` count trend, vendored locally, no CDN reference anywhere in the rendered HTML.
4. No new route was added; everything lives on `fmea:dashboard`.
5. All required tests pass; full suite remains green; `makemigrations --check --dry-run` is clean (no migration expected).

## 7. Explicit Exclusions (restated for emphasis)

This slice does not build, stub, or placeholder any part of: the Operations module (Process Planning/Production Execution/Work Tracking/Traceability — no entity exists and none is created), the PM-FMEA maintenance-risk donut (stays excluded until the standing PM-FMEA hold is lifted), a computed "Overall Health" score or gauge (no formula exists or is proposed — a future decision of its own if ever pursued), per-FMEA-type coverage bars, or data-integrity/broken-link counts (both need aggregation logic this instruction does not design). These are not deferred as "next slice" work items to pick up casually — each needs its own architecture review before any code is written against it.

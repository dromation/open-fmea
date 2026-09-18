# Claude Review — Consolidated Home (Slice K) Implementation

**Author:** Claude (this session) · **Date:** 2026-09-05
**Instruction:** `Codex_Instruction_ConsolidatedHome_SliceK.md`

## 1. What was built

Purely additive changes to the existing `dashboard(request)` view and `dashboard.html` template — no new route, no new template file, per Decision 1. Checked `dashboard.html`/`dashboard()` first for any duplicate before adding: the existing "FMEA Projects" tile renders `fmea_count` (an `FMEA.objects.count()`, despite its label), not an `FMEAProject` count, a `FailureMode` count, or an `RecommendedAction` count — none of the three new tiles duplicate anything already shown (Decision 2).

Three new stat tiles added to the KPI row via the existing `_stat_tile.html` include, same pattern as the pre-existing tiles: Projects (`FMEAProject.objects.count()`), Failure Modes (`FailureMode.objects.count()`), Actions (`RecommendedAction.objects.count()`).

An Actions Summary panel (Total/Overdue/Due Soon), computed at render time with no new model or stored field, using the exact filter logic given in the instruction's own Section 1 code block: `non_terminal_statuses = [ActionStatus.OPEN, ActionStatus.IN_PROGRESS]`; Overdue = `due_date < today` and status in that list; Due Soon = `today <= due_date <= today+7` and status in that list. (Note: this is the instruction's literal given code, which is narrower than Decision 3's own prose — "status not in {completed, verified, cancelled}" would also count an `on_hold` action as eligible for overdue/due-soon, whereas the literal `status__in=[open, in_progress]` code block does not. Implemented the literal code block exactly as given, since Section 1 presents it as the definitive implementation, not an approximation of Decision 3's prose.)

A risk-trend Chart.js **bar** chart, counting `RiskEvaluation` rows per **day** over the trailing 30 days (Decision 4 offered daily-or-weekly at implementer's discretion; chose daily, matching the literal `TruncDate` code given in Section 1 and because the demo dataset, while sparse, is small enough that a 31-point daily x-axis renders cleanly with zero-filled gaps rather than needing weekly aggregation to stay legible). New `_risk_evaluation_trend(days: int)` helper in `views.py`: queries `RiskEvaluation.objects.filter(evaluated_at__date__gte=start).annotate(day=TruncDate("evaluated_at")).values("day").annotate(count=Count("id")).order_by("day")`, then zero-fills every day in the 31-day range (`start` through `today` inclusive) via a dict-lookup loop, returning two parallel lists (ISO date label strings, integer counts).

**Chart.js was not yet vendored by any prior slice** (confirmed: `static/fmea_app/vendor/` did not exist before this slice) — vendoring it was therefore in scope per Decision 5. The CDN hosts this project's egress allowlist permits (jsdelivr, cdnjs) are blocked from this session's shells by a stricter allowlist than the one the charting decision anticipated; obtained the real, unmodified Chart.js 4.4.1 UMD build instead via `npm pack chart.js@4.4.1` (the npm registry is reachable) and extracted `dist/chart.umd.js` from the official package tarball — this is the same auto-registering UMD bundle a CDN would have served, just fetched via a different reachable channel, not hand-written or reimplemented. Ran it through `terser` (available locally) for the `.min.js` filename Decision 5 names; the npm-published `dist/chart.umd.js` turned out to already be a production Rollup bundle (single-line, no whitespace) so the size reduction was negligible (205,125 -> 204,203 bytes) — confirmed the output still parses (`node -c`) and still contains `BarController` and the `"4.4.1"` version string. Vendored to `static/fmea_app/vendor/chartjs/chart.umd.min.js`, loaded via `{% static %}` in `dashboard.html`, never a CDN URL — confirmed by the existing `test_gui_navigation_scope.py::test_shell_runtime_assets_are_offline_safe` (which scans every template/CSS/JS file for `http://`/`https://`/`cdn.`/etc.) passing unchanged as part of the full suite.

Data reaches the template via a single `risk_trend_data` dict (`{"labels": [...], "counts": [...]}`) passed into context and rendered with `{{ risk_trend_data|json_script:"risk-trend-data" }}`, read by a small inline `<script>` at the bottom of `dashboard.html`'s content block that calls `new Chart(canvas.getContext("2d"), {type: "bar", ...})` — exactly the fixed pattern in `OpenFMEA_ChartingLibrary_ArchitectureDecision.md` Section 3, no AJAX/fetch endpoint anywhere. Checked `app.js`/existing template `<script>` usage first per Decision 6's own contingency: no template in this codebase has ever used a page-specific inline `<script>` or a per-page JS file before (`app.js` is the one shared, globally `defer`-loaded script, for the theme toggle only) — used a small inline `<script>` directly in `dashboard.html`, matching the charting decision's own stated default, rather than inventing a new per-page-JS-file convention this codebase has never used.

## 2. Test coverage

Extended the existing `tests/test_dashboard_view.py` (kept its one pre-existing test, `test_dashboard_uses_real_counts_and_recent_review_activity`, completely unchanged and still passing) with 5 new tests across four new `TestCase` classes: stat-tile values matching direct `.count()` queries against seeded Project/FailureMode/RecommendedAction data; an Actions-summary fixture with past-due/open, due-in-3-days/open, due-in-30-days/open, and past-due/completed actions, asserting `actions_total == 4`, `actions_overdue == 1` (the completed-but-overdue action correctly excluded), `actions_due_soon == 1`; the `_risk_evaluation_trend` helper directly, with two evaluations on one in-window day, one deliberately outside the 30-day window, asserting a 31-entry zero-filled result where only the seeded day is non-zero and the out-of-window evaluation is absent; the rendered dashboard response containing exactly one `<canvas id="risk-trend-chart"` and a `json_script` block whose parsed JSON matches `_risk_evaluation_trend(days=30)`'s own return value exactly; a negative check for "Operations"/"Overall Health"/"Coverage"/"Broken Links"/"PM-FMEA" anywhere in the rendered response.

## 3. Verification

Fresh venv (persisted from prior slices this session), live shell, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | "No changes detected" (no migration expected, none generated) | "No changes detected" |
| `test_dashboard_view.py` (isolated) | 6/6 | — |
| Full suite | **200/200** | **200/200** |

200 = the prior 195 (Slices A–J) plus the 5 new tests here — arithmetic checked. Grepped `dashboard.html` for every excluded term (`Operations`, `PM-FMEA`, `Overall Health`, `Coverage`, `Broken Links`, `Unlinked Items`) and every CDN-reference pattern (`http://`, `https://`, `cdn.`, `jsdelivr`, `unpkg`, `cdnjs`) — zero matches on both. `risk_matrix.py` confirmed untouched (zero references to it in this slice's diff to `views.py` beyond what already existed).

Diff surface via `git status --short` matches Slice K's allowed-file list exactly: `views.py`, `dashboard.html` (both further modified), the new vendored `chart.umd.min.js`, `test_dashboard_view.py` (extended). No `models.py` edit, no new migration, no new route, no `risk_matrix.py` change, no Operations-related file created.

Mirrored to `open_fmea_training_set` and byte-diffed (`diff -q`, not size/mtime): all 4 changed/new files identical, including the vendored Chart.js binary. Full suite re-run there independently: 200/200.

## 4. Scope discipline

No new model, no new migration (confirmed: `makemigrations --check --dry-run` reports no pending changes both before and after this slice's edits). No new route — everything renders on the existing `fmea:dashboard` URL. No AJAX/fetch — the chart's data is server-computed and embedded via `json_script` only. No "Operations" card, section, or nav entry. No PM-FMEA donut or PM-FMEA-scoped query. No "Overall Health" score or gauge — no such formula exists anywhere in the diff. No coverage-bar computation. No "Unlinked Items"/"Broken Links" computation. The risk-trend chart counts raw `RiskEvaluation` rows per day only — it does not attempt to reconstruct historical risk-tier state, per the instruction's own explicit simplification.

## 5. Still open

- `.git/index.lock` still needs a manual delete in `open_fmea`. Nothing committed, per "build first, commit later."
- Remaining slice from the 2026-09-05 batch: L (Characteristics Flow) — not yet read in full or implemented.

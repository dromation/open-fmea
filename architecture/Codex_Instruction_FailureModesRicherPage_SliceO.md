# Codex Implementation Instruction — Slice O: Failure Modes Richer Standalone Page

Status: **Instruction, 2026-09-06** — implements `OpenFMEA_FailureModesRicherPage_ArchitectureDecision.md` exactly as decided there. Do not add, reinterpret, or "improve" anything beyond what is written below; if something here seems to conflict with the live code, stop and report back rather than guessing.

## 0. Decisions for this slice (restated from the architecture decision doc — do not re-derive)

1. Five KPI tiles (Total, Not Evaluated, High/Critical Risk, No Cause Recorded, No Action Recorded) — all reuse existing per-row computations, especially the existing `_latest_risk_result()` helper. Do not write a second risk-classification implementation anywhere in this slice — call the existing helper (or a thin wrapper around it) everywhere a classification is needed: KPI tile, filter dropdown, donut chart.
2. Filter toolbar gets three new GET-form fields: `fmea`, `risk_level`, `has_action`. Plain server-side reload, same as every existing filter in this app.
3. Right-docked detail panel via `?selected=<stable_id>&tab=general|effects|causes|actions|risk` on the existing `failure_mode_list` route. No new route, no AJAX.
4. "Actions" tab shows `RecommendedAction` rows reachable **directly or via any linked `FailureCause`** — explicitly label this "Actions (direct + via causes)" in the template so it is never confused with the flat table's existing "Actions (direct)" column, which must remain unchanged.
5. FMEA Chain View diagram: static HTML boxes restating the real Function/Requirement → Failure Mode → Effects/Causes → Actions chain for the selected failure mode. Empty branches render an explicit "None recorded" box, never a silently-omitted arrow.
6. Relationship/Coverage Summary panel: four plain counts (zero-causes, zero-effects, zero-actions-by-Decision-3's-definition, zero-risk-evaluations) over the filtered set. No composite score, no percentage, no weighting.
7. One Chart.js donut (Risk Summary/Distribution), grouped by the same classification bucket used everywhere else in this slice. Reuse the already-vendored `django_app/fmea_app/static/fmea_app/vendor/chartjs/chart.umd.min.js`; no CDN, no second vendored copy.
8. Permanent scope boundary (do not build any of): Error/Defect Catalog, Complaint/NCR link, 8D/XDA/RCA/5-Why/Ishikawa entities/workflows, AI similarity/duplicate detection, image annotation, any Open-EQMS cross-system reference field.

## 1. Exact Scope

Modify only:
- `django_app/fmea_app/views.py` — extend the existing `failure_mode_list` view function only. Do not touch `failure_cause_list`, `failure_effect_list`, `prevention_control_list`, `detection_control_list`, or any FMEA worksheet/detail view.
- `django_app/fmea_app/templates/fmea_app/failure_mode_list.html` — extend this one template only.
- `django_app/fmea_app/static/fmea_app/css/*.css` (locate the file already holding `.stat-tile`/`.panel`/`.grid` etc. — do not create a new stylesheet) — additive classes only.

Do not touch: `urls.py` (no new route), `models.py` (no migration — every value used already exists on `FailureMode`, `FailureEffect`, `FailureCause`, `RecommendedAction`, `RiskEvaluation`), `forms.py`, any FMEA worksheet add/edit template, `_sidebar.html`, `app.js`.

## 2. Exact Allowed-New Files

None. Pure extension of the view, one template, and the existing stylesheet. If a shared helper for the risk-classification bucket used by the KPI tile/filter/donut doesn't already exist as `_latest_risk_result()` (or an obviously equivalent already-shared function), reuse that function directly rather than writing a new one — do not fork the RPN/priority logic a second time anywhere in this diff.

## 3. Required Validation and Explicit Exclusions

- KPI tiles, the donut, and the filter dropdown's risk buckets must all derive from calling the same existing classification logic once per failure mode per request (or an equivalently single-source computation) — not three independently-written bucketing implementations that could silently disagree.
- The "No Action Recorded" KPI tile and the "Actions" detail-panel tab must use the exact same "direct or via any linked cause" definition — verify they agree by construction (same query/helper), not by coincidence.
- The existing flat table's "Actions (direct)" column (`row.actions_count`, from `fm.recommended_actions.count()`) must remain byte-for-byte the same query it is today — grep the diff to confirm this specific expression is unchanged.
- `?selected=<stable_id>` on a nonexistent/foreign id must not 500 — assert a graceful response (pick 404 or an empty-panel 200 and apply it consistently).
- `?tab=` defaults to `general` for any missing/unrecognized value — must not 500.
- The FMEA Chain View diagram must render an explicit "None recorded" box for any empty branch — grep the template to confirm this string (or equivalent) exists, not just a conditionally-omitted arrow.
- Explicit exclusions to verify absent from the diff by name/grep before calling this done:
  - No new migration file.
  - No Error/Defect Catalog model, no Complaint/NCR FK or model, no 8D/XDA/RCA/5-Why/Ishikawa entity or field, no AI similarity/duplicate-detection code, no image-annotation UI.
  - No new field or model referencing Open-EQMS, no cross-system stable-id bridge.
  - No composite "coverage %"/maturity score — only the four plain counts named in Decision 6.
  - No AJAX/`fetch`/`XMLHttpRequest`, no client-side tab framework, no modal/drawer JS.
  - No new CDN `<script src="https://...">` tag.

## 4. Required Tests

Add to the existing test module covering `failure_mode_list` (locate it — do not create a new test file):
1. KPI row: seed failure modes with known combinations of zero/nonzero causes, effects, actions (direct and via-cause), and risk evaluations (including at least one high/critical classification); assert each of the five tile counts matches expectation exactly.
2. Filter toolbar: assert `fmea`, `risk_level`, and `has_action` each narrow the rendered rows correctly, and that the KPI/donut numbers move together with the table when a filter is applied (consistency, mirroring Slice N's equivalent test).
3. Detail panel: `?selected=<valid id>&tab=actions` includes a `RecommendedAction` linked only via a cause (not directly) and confirm it appears in this tab while the flat table's direct-only count for that row does not include it; `&tab=risk` renders the real evaluation history in the model's existing newest-first order; an invalid `selected` value does not 500.
4. Chain diagram: a failure mode with no recorded effects renders the "None recorded" (or equivalent) box for that branch rather than silently omitting it.
5. Full existing test suite for this app still passes (regression) — run it, do not just add these four.

## 5. Commands to Run

```
python manage.py test fmea_app
```
Run in both `open_fmea` and `open_fmea_training_set` per this project's established practice for prior slices; report the exact before/after test count in the completion report.

## 6. Acceptance Criteria

- All new tests from Section 4 pass; full existing suite still passes with no regressions; report the exact before/after test count.
- `git diff` touches only the view, the one template, the existing stylesheet, and the test file — no migration, no new route, no new model.
- Every item in Section 3's exclusion list is confirmed absent by direct grep in the completion report.
- The existing "Actions (direct)" table column's query is byte-for-byte unchanged.

## 7. Explicit Exclusions (restated)

No new migration. No Error/Defect Catalog, Complaint/NCR link, 8D/XDA/RCA/5-Why/Ishikawa entity or workflow, AI similarity/duplicate detection, or image annotation — this boundary is permanent per the architecture decision doc, not scoped only to this increment. No Open-EQMS cross-system reference. No composite coverage score. No AJAX or client-side tab/panel-swap anywhere. No new charting library or CDN reference. No changes to `failure_cause_list`, `failure_effect_list`, `prevention_control_list`, `detection_control_list`, any FMEA worksheet template, `urls.py`, `_sidebar.html`, or `app.js`.

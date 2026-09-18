# Claude Review — Slice O: Failure Modes Richer Standalone Page — Implementation

Status: **Implemented and independently verified, 2026-09-12.** Implements `Codex_Instruction_FailureModesRicherPage_SliceO.md` exactly as decided in `OpenFMEA_FailureModesRicherPage_ArchitectureDecision.md`. Mirrored byte-identically into `open_fmea_training_set`.

## 1. What was built

Extended `failure_mode_list` (view + template) only, reusing Slice N's already-added generic `.detail-panel`/`.tab-nav`/`.tab-link`/`.flow-diagram`/`.flow-step`/`.flow-arrow`/`.row-selected` CSS classes rather than duplicating them — `theme.css` was not touched at all in this slice.

1. **Five KPI tiles** — Total, Not Evaluated, High/Critical Risk, No Cause Recorded, No Action Recorded — all five computed once per failure mode per request by calling the existing `_latest_risk_result()` helper unmodified (bucketed into `risk_bucket`) and the shared `_failure_mode_actions()` coverage helper. No RPN/priority threshold logic was reimplemented anywhere.
2. **Three new filter fields** — `fmea`, `risk_level`, `has_action` — plain GET-form fields, same server-reload convention as every existing filter.
3. **Right-docked detail panel** — `?selected=<stable_id>&tab=general|effects|causes|actions|risk` on the existing route. No new route.
4. **"Actions" tab** explicitly labeled "Actions (direct + via causes)", listing `RecommendedAction` rows reachable directly (`fm.recommended_actions.all()`) or through any linked cause (`RecommendedAction.objects.filter(failure_cause__in=fm.causes.all())`) via one shared helper, `_failure_mode_actions()`, called for both the KPI tile and the tab so the two definitions agree by construction, not by coincidence.
5. **FMEA Chain View diagram** — static HTML boxes (Function/Requirement → Failure Mode → Effects → Causes → Actions), each empty branch rendering an explicit "None recorded" box.
6. **Coverage Summary panel** — four plain counts (zero-causes, zero-effects, zero-actions, zero-risk-evaluations) over the currently filtered set. No composite score, no percentage.
7. **One Chart.js donut** (Risk Summary), grouped by the same `risk_bucket` value computed once and reused for the KPI tile, the `risk_level` filter, and this chart.
8. **Risk tab** — full `RiskEvaluation` history via the model's own `Meta.ordering = ["-evaluated_at", "-id"]` (already newest-first, not re-sorted), each row formatted by a small new `_risk_result_for_evaluation()` helper that performs the exact same trivial "read the already-stored classification/priority key" step `_latest_risk_result()` performs for its one latest row — no RPN/priority threshold is computed a second time anywhere, only the already-computed stored value is read per row instead of only the newest one.

The Open-EQMS permanent scope boundary (Decision 7) was respected: no Error/Defect Catalog, Complaint/NCR link, 8D/XDA/RCA/5-Why/Ishikawa entity, AI similarity, image annotation, or cross-system reference field was added.

## 2. Required tests (Section 4) — all added to the existing test module

Added `FailureModeRicherPageTests` (11 test methods) to `tests/test_fmea_elements_standalone_pages.py` (the module already covering `failure_mode_list`, located rather than duplicated):

1. `test_kpi_tiles_match_expected_counts`, `test_coverage_summary_matches_kpi_derived_facts` — four failure modes with known combinations of zero/nonzero causes, effects, direct actions, via-cause-only actions, and risk classifications (including one "high"); all five KPI tiles and all four coverage counts asserted exactly.
2. `test_fmea_filter_narrows_rows_and_kpi_together`, `test_risk_level_filter_narrows_rows_and_kpi_together`, `test_has_action_filter_narrows_rows_and_kpi_together` — each filter narrows the table and moves the KPI numbers together (mirroring Slice N's equivalent consistency test).
3. `test_actions_direct_column_is_unchanged_while_actions_tab_includes_via_cause` — a failure mode whose only action reaches it via a cause: the flat table's "Actions (direct)" cell still reads `0`, while the Actions tab shows the via-cause action and the "Actions (direct + via causes)" label.
4. `test_risk_tab_renders_history_newest_first` — two risk evaluations at different `evaluated_at` times; asserts the newer one's RPN renders before the older one's.
5. `test_chain_diagram_renders_none_recorded_for_empty_branches` — a failure mode with nothing recorded renders at least 4 "None recorded" boxes (Function/Requirement, Effects, Causes, Actions), not a silently omitted arrow.
6. `test_unrecognized_tab_defaults_to_general_without_500`, `test_invalid_selected_id_returns_404_not_500` — the two required graceful-failure paths.
7. `test_pages_have_no_open_eqms_scope_creep` — asserts Complaint/NCR/8D/XDA/5-Why/Error Catalog/Defect Catalog/Open-EQMS text never appears (deliberately excluding "Ishikawa" from this check, since the shared sidebar already carries a legitimate, pre-existing "Ishikawa / Cause Analysis" nav group from an earlier, unrelated slice).

## 3. Test count

**216 → 227 (+11)**, run via `pytest` (this project's actual established runner, same finding as Slice N — `manage.py test fmea_app` finds 0 tests since every test lives under the top-level `tests/` directory).

```
227 passed in 12.50s
```

`python manage.py makemigrations --check --dry-run` → **"No changes detected"** — `models.py` untouched.

## 4. Exclusions grep-verified (Section 3), not asserted from memory

| Exclusion | Verified |
|---|---|
| `"actions_count": fm.recommended_actions.count()` — byte-for-byte unchanged | confirmed present verbatim at its call site |
| No new migration file | `migrations/` still ends at `0013_characteristiclink.py` |
| No Error/Defect Catalog, Complaint/NCR, 8D/XDA/RCA/5-Why/Ishikawa entity/field, AI similarity, image annotation | grep across `models.py`/`views.py`/the template — no matches |
| No Open-EQMS cross-system reference | grep — no matches |
| No composite coverage %/maturity score | manual inspection of the four Coverage Summary tiles — plain integer counts only ("Zero Causes", "Zero Effects", "Zero Actions", "Zero Risk Evaluations"), no "%", no weighting |
| No AJAX/fetch/XHR/client-side tab framework/modal/drawer JS | grep — no matches |
| No new CDN `<script src="https://...">` | grep — no matches; only the already-vendored local file is referenced |
| Exactly one canvas (the one Risk Summary donut) | `grep -c "<canvas"` → 1 |
| "None recorded" renders for empty chain branches | `grep -c` → 8 occurrences across the template's 4 branch conditionals |

## 5. Diff footprint

Three files, matching the acceptance criterion ("touches only the view, the one template, the existing stylesheet, and the test file" — the stylesheet needed no changes this slice since Slice N's classes were reused as-is):
- `django_app/fmea_app/views.py` (extended `failure_mode_list` only, plus two small new module-level helpers, `_failure_mode_actions()` and `_risk_result_for_evaluation()`; no other view function's body was touched)
- `django_app/fmea_app/templates/fmea_app/failure_mode_list.html`
- `tests/test_fmea_elements_standalone_pages.py`

`urls.py`, `models.py`, `forms.py`, `failure_cause_list`/`failure_effect_list`/`prevention_control_list`/`detection_control_list` (bodies confirmed unchanged by direct read), any FMEA worksheet template, `_sidebar.html`, and `app.js` were not touched.

## 6. Mirroring

Both repositories' three target files were confirmed at matching pre-change byte sizes before writing, then written from identical source bytes (same `SendUserFile` `file_uuid`s committed to both device paths), each write pinned with `expectedMtimeMs` read moments earlier — both commits succeeded with zero rejections.

## 7. Recommendation

Slice O is complete and ready to stand as-is. Next in the approved, not-yet-built queue: **Slice P** (Product Characteristic Register), then **Slice Q** (Characteristics Flow enrichment, which depends on P).

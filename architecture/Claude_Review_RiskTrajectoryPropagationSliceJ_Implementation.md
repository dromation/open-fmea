# Claude Review — Risk Trajectory & Propagation (Slice J) Implementation

**Author:** Claude (this session) · **Date:** 2026-09-05
**Instruction:** `Codex_Instruction_RiskTrajectoryPropagation_SliceJ.md`

## 1. What was built

One additive field, `RiskEvaluation.lifecycle_gate` (`django_app/fmea_app/models.py`), placed as a new `LIFECYCLE_GATE_CHOICES` class attribute plus the field itself, exactly per the instruction's given code block: six values (`concept_design`/`design_verification`/`process_validation`/`pre_production`/`serial_production`/`current`), default `"current"`. A plain Django-choices `CharField`, matching `FMEA.LIFECYCLE_CHOICES`/`ActionStatus`'s own precedent for a closed, structural vocabulary (Decision 1) — not a new model or FK. One additive migration. The instruction names it `0006_riskevaluation_lifecycle_gate.py`, but migration numbers through 0011 already exist (the real next-sequential number, since Slice I's `Change` model landed as `0011` earlier today) — generated the actual next migration, `0012_riskevaluation_lifecycle_gate.py`, exactly one `AddField` operation, per the instruction's own explicit renumbering allowance. `RiskEvaluation.to_domain()` was **not** touched — the instruction's allowed-file list has no `fmea_domain/` entry and `DomainRiskEvaluation` isn't asked to carry this field; confirmed by `git diff --stat domain/fmea_domain/` showing zero lines changed by this slice (the diff present there is entirely Slice F's pre-existing `ValidationTest` domain entity, untouched here).

`evaluate_failure_mode()` (`services.py`) gained one optional `lifecycle_gate: str = "current"` keyword argument, added to the `values` dict passed to `.create()`/`update_or_create()` — every existing call site (including every fixture in `test_risk_matrix.py`) keeps working unchanged since the new argument defaults. `RiskEvaluationForm` (`forms.py`, a plain `forms.Form`, not a `ModelForm`) gained one optional `lifecycle_gate = forms.ChoiceField(choices=..., required=False)`. `evaluate_failure` (`views.py`) now passes `form.cleaned_data.get("lifecycle_gate") or "current"` through — omitting the field from the POST still succeeds and defaults correctly (verified directly, not just assumed).

Two new read-only views: `risk_trajectory_index` (every `FailureMode` with at least one `RiskEvaluation`, annotated with a distinct evaluation count, `FMEA`-linked, sorted `fmea__name, name` — the same "simple list" idiom as `risk_matrix_top.html`) and `risk_trajectory` (every `RiskEvaluation` for one `FailureMode`, ordered `evaluated_at, id` ascending — the deliberate reverse of the model's own default `-evaluated_at, -id` ordering, per Decision 3). Both read `RiskEvaluation.result` verbatim via the exact same `{% if evaluation.result.score %}...{% else %}...{% endif %}` + `_status_badge.html` include pattern already used in `risk_matrix_cell.html`/`risk_matrix_top.html` — no call to `fmea_evaluation.calculate()` anywhere in either new view or template (confirmed by grep). Two new routes: `/risk-trajectory/` and `/failure-mode/<str:stable_id>/risk-trajectory/`.

`risk_matrix_cell.html` gained exactly one new column, "Trajectory," with one "View Trajectory" link per row pointing to `fmea:risk_trajectory` for that row's `FailureMode` — no other markup in that file changed (confirmed via a marker-anchored programmatic replace with a single-match assertion). `risk_matrix.html`, `risk_matrix_top.html`, and `risk_matrix.py`'s query logic (`cell_evaluations`/`top_evaluations`/`latest_evaluations_by_method`) are completely untouched, confirmed by `git status --short` showing no diff against them and by `test_risk_matrix.py`'s full 12/12 pass with zero assertion changes.

One new sidebar entry, "Risk Trajectory & Propagation" (the exact label the canonical nav structure in `OpenFMEA_DNA_CoreReference.md` already fixes), added to the existing `RISK` group directly under "Risk Matrix" — not a new group, matching Decision 6 exactly and requiring no placement judgment call (unlike Slice I's stale-group problem): the `RISK` group already exists and already contains exactly the one sibling item this instruction names.

## 2. Test coverage

New `tests/test_risk_trajectory.py`, 9 tests: `lifecycle_gate` defaults to `"current"` when omitted from `evaluate_failure_mode()` and round-trips correctly via `get_lifecycle_gate_display()` when passed explicitly; a three-evaluation fixture spanning both `classic-rpn` and `aiag-vda-ap-poc` methods and three different lifecycle gates, rendered on the detail page in verified ascending chronological order, with a deliberately stale stored `result` (`{"score": 424242, ...}`, mathematically inconsistent with its own S/O/D) shown verbatim rather than recomputed — the same proof pattern `test_risk_matrix.py` already established; the index page listing the evaluated `FailureMode` (name, parent-FMEA link, count) while correctly omitting a zero-evaluation `FailureMode`; the Risk Matrix cell drill-down showing the new "View Trajectory" link with the correct target URL; `evaluate_failure` POSTed both with an explicit `lifecycle_gate` (persists it) and without one (defaults to `"current"`) — both through the real view, not a shortcut; a negative check on both new pages for `<canvas` and every propagation-chain term (`Local Effect`/`Next-Level Effect`/`System Effect`/`End Effect`/`PM-FMEA`); the sidebar assertion (exactly one "Risk Trajectory & Propagation" occurrence, correct link target, all of `test_gui_navigation_scope.py`'s existing unbuilt-label list still absent from the dashboard).

No edit was needed to `tests/test_gui_navigation_scope.py` itself this slice — unlike prior slices' required flips, "Risk Trajectory & Propagation" was never in that file's unbuilt-label negative tuple to begin with (it names labels for *other* not-yet-built features only), so there was nothing to move; the new test file's own sidebar assertion is what the instruction's Section 4 actually asks for.

## 3. Verification

Fresh venv (persisted from prior slices this session), live shell, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | "No changes detected" (after generating `0012`) | "No changes detected" |
| `test_risk_trajectory.py` (isolated) | 9/9 | — |
| `test_risk_matrix.py` (isolated, regression) | 12/12, zero assertion changes | — |
| Full suite | **195/195** | **195/195** |

195 = the prior 186 (Slices A–I) plus the 9 new tests here — arithmetic checked. Grepped `domain/fmea_domain/` for any diff from this slice — zero (the only diff present predates this slice, from Slice F). Grepped both new templates and the one modified `risk_matrix_cell.html` for every excluded term (`Local Effect`, `Next-Level Effect`, `System Effect`, `End Effect`, `PM-FMEA`, `<canvas`, `donut`, `Chart.js`) — zero matches.

Diff surface via `git status --short` matches Slice J's allowed-file list exactly: `models.py`, `forms.py`, `services.py`, `views.py`, `urls.py`, `_sidebar.html`, `risk_matrix_cell.html` (all modified/further modified), migration `0012` (new, correctly renumbered from the instruction's stale `0006` placeholder), `risk_trajectory_index.html`/`risk_trajectory.html` (new), `test_risk_trajectory.py` (new). No `fmea_domain/`, `fmea_evaluation/calculators.py`, `FailureEffect`, `risk_matrix.py`, `risk_matrix.html`, or `risk_matrix_top.html` change anywhere in the diff.

Mirrored to `open_fmea_training_set` and byte-diffed (`diff -q`, not size/mtime): all 11 changed/new files identical. Full suite re-run there independently: 195/195.

## 4. Scope discipline

No new model, no new FK, no self-referential `FailureEffect` field, no chain/edge entity anywhere. No propagation-chain content (no "Local Effect"/"Next-Level Effect"/"System Effect"/"End Effect" field, column, or panel). No recomputation of score/band in either new view — every display reads `RiskEvaluation.result` verbatim. No `<canvas>`, no chart/graph library reference. No PM-FMEA cross-reference. No edit/delete control on any past `RiskEvaluation` row — the trajectory detail page is strictly read-only; new evaluations continue to go only through the existing `evaluate_failure` flow.

## 5. Still open

- `.git/index.lock` still needs a manual delete in `open_fmea`. Nothing committed, per "build first, commit later."
- Remaining slices from the 2026-09-05 batch: K (Consolidated Home), L (Characteristics Flow) — not yet read in full or implemented.

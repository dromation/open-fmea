# Claude Review — FMEA Elements Standalone Browse Pages (Slice G) Implementation

**Author:** Claude (this session) · **Date:** 2026-09-05
**Instruction:** `Codex_Instruction_FMEAElementsStandalonePages_SliceG.md`

## 1. What was built

Six new read-only, cross-cutting browse pages, all following the exact column lists and query shapes specified in Section 1 of the instruction: `/failure-modes/`, `/causes/`, `/effects/`, `/prevention-controls/`, `/detection-controls/`, `/actions/`. Every row links back to `fmea:fmea_detail` (or `fmea:action_detail` for Actions) for editing — no new form, no POST handler, no `forms.py` change anywhere in this slice.

The Failure Modes page's "latest risk result" column reuses the same "latest `RiskEvaluation`" read `_worksheet_row` already performs, via a small standalone helper (`_latest_risk_result`) — `_build_worksheet_rows`/`_worksheet_row` themselves were not touched or forked (confirmed: zero `+`/`-` lines in that function region of the diff). The Actions page resolves "owning FMEA" as `action.failure_mode.fmea` when set, else `action.failure_cause.failure_mode.fmea`, rendering blank if somehow neither is set, and labels the linked entity as "Failure Mode: X" or "Cause: Y" per the spec. Its one required GET filter (`status`, including the new "On Hold" option) works the same server-side-reload pattern as `cause_influence_list`'s existing filter — no AJAX anywhere on any of the six pages.

New `FMEA ELEMENTS` sidebar group with exactly six links (Failure Modes, Causes, Effects, Preventive Controls, Detection Controls, Actions), placed after `FMEA ANALYSIS`. One placement note: the instruction was written assuming the sidebar's next group after `FMEA ANALYSIS` would be `Import & Review`, but `VALIDATION & CHANGE` (from the just-prior Slice F) now sits between them — `FMEA ELEMENTS` was placed after `FMEA ANALYSIS` and before `VALIDATION & CHANGE`, which still satisfies the instruction's actual constraint ("after FMEA ANALYSIS... and before Import & Review").

**`ActionStatus.ON_HOLD = "on_hold"`** added to `domain/fmea_domain/entities.py`, positioned after `VERIFIED` and before `CANCELLED` per Decision 2. `RecommendedAction.STATUS_CHOICES` picked it up automatically via its existing mechanical derivation — no hand-edit to `models.py` was needed or made. Per the instruction's explicit instruction not to assume, ran `manage.py makemigrations --check --dry-run` after the enum change and it **did** report a pending migration (`~ Alter field status on recommendedaction` — Django tracks `choices` metadata as migration state even though it's not a schema change) — generated it honestly as `0009_alter_recommendedaction_status.py` and reported it here rather than assuming none was needed, exactly as Section 0 Decision 2 asked.

## 2. Verification of the "leave everything else alone" requirements

`FailureCause`'s model definition confirmed byte-identical: `git diff` shows zero touched lines anywhere near its class body, and a test (`test_failure_cause_model_is_unchanged_single_failure_mode_relationship`) asserts its `failure_mode` field is still a plain (non-many-to-many) FK. `_build_worksheet_rows`/`_worksheet_row`/`fmea_detail` (the view function) are unchanged — confirmed the same way, zero diff lines in that region; `fmea_detail.html`'s only diff is the pre-existing Classification column from Slice M, nothing new added by this slice.

## 3. Test coverage

New `tests/test_fmea_elements_standalone_pages.py`, 10 tests, fixture spanning two FMEAs throughout: each of the six pages renders rows from both FMEAs on the same page with correct fields and links; Failure Modes/Causes count columns match known fixture counts exactly; the Actions status filter includes "On Hold", a `RecommendedAction` with `status="on_hold"` persists and filters correctly; the `FailureCause` model-shape regression check; none of the six pages contain `method="post"` form markup; the sidebar shows the new `FMEA ELEMENTS` group with all six links resolving correctly.

`tests/test_gui_navigation_scope.py` — the required, intentional flip: `"FMEA ELEMENTS"` moved from the unbuilt-label tuple to a positive assertion, alongside all six new link labels. Every other existing assertion in that file is untouched.

## 4. Verification

Fresh venv, live shell, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | reported one pending migration from the `ActionStatus` enum change, generated (`0009`), then clean | clean |
| `test_fmea_elements_standalone_pages.py` + `test_gui_navigation_scope.py` (isolated) | 13/13 | — |
| Full suite | **170/170** | **170/170** |

170 = the prior 160 (Slices A–F, M) plus the 10 new tests here — arithmetic checked. Grepped every changed/new file for excluded content (`Chart.js`, `<canvas`, complaint-linking, AI similarity) — zero matches.

Diff surface via `git status --short` matches Slice G's allowed-file list exactly: `entities.py` (modified), `views.py`/`urls.py`/`_sidebar.html` (further modified), migration `0009` (new, honestly reported), six new templates, `test_fmea_elements_standalone_pages.py` (new), `test_gui_navigation_scope.py`'s one intentional update. `models.py` received zero edits, exactly as the instruction anticipated ("no edit expected").

Mirrored to `open_fmea_training_set` and byte-diffed (`diff -q`): all 13 changed/new files identical. Full suite re-run there independently: 170/170.

## 5. Scope discipline

No new CRUD/forms anywhere in this slice. No `FailureCause` model or migration change. No new fields on any of the six entities beyond the additive `ActionStatus.ON_HOLD` value. No charts, stat-card dashboards, catalogs, complaint-linking, AI similarity matching, or image annotation anywhere in the diff.

## 6. Still open

- `.git/index.lock` still needs a manual delete in `open_fmea`. Nothing committed, per "build first, commit later."
- Remaining slices from the 2026-09-05 batch: H (Process Control Characteristics), I (Change Impact), J (Risk Trajectory & Propagation), K (Consolidated Home), L (Characteristics Flow) — not yet read in full or implemented.

# Claude Review — DFMEA / PFMEA Worksheets (Slice D) Implementation

**Author:** Claude (this session) · **Date:** 2026-09-05
**Instruction:** `Codex_Instruction_DFMEA_PFMEA_Worksheets_SliceD.md`

## 1. What was built

Two new cross-FMEA worksheet pages, splitting on `FMEA.fmea_type`: **DFMEA** (`fmea_type != "process"`, route `dfmea/`, view `dfmea_worksheet`) and **PFMEA** (`fmea_type == "process"`, route `pfmea/`, view `pfmea_worksheet`), per decision 1. Both reuse the existing, unmodified `_build_worksheet_rows`/`_worksheet_row` helpers already used by the per-FMEA worksheet — verified via `git diff HEAD -- views.py` that the region spanning those two function definitions carries zero `+`/`-` lines; the new code is a pure addition (`_worksheet_row_action_counts`, `_cross_fmea_worksheet_rows`, `dfmea_worksheet`, `pfmea_worksheet`) inserted elsewhere in the file.

Each row gains an `fmea` reference (for the row's link back to `fmea:fmea_detail`) and an Actions column showing `{open count} open / {overdue count} overdue`, computed by `_worksheet_row_action_counts` from the row's `RecommendedAction`s (via `cause.recommended_actions` when a cause exists, else `failure_mode.recommended_actions` — matching the model's `related_name` on both FKs) with overdue defined as `due_date < today` and `status` not in `("completed", "verified", "cancelled")`.

Two new templates, `dfmea_worksheet.html` / `pfmea_worksheet.html`, built from a shared structure (the PFMEA template was generated from the DFMEA one via `sed` substitution, then diffed to confirm only the intended copy differs: title/heading text and the empty-state message). **Deliberate deviation flagged:** the instruction's prose says "table-shell/table" but I used `.worksheet-wrap`/`table class="worksheet"` instead, because `theme.css` scopes the `.wide`/`.rating` column-width/rating-badge classes specifically under `.worksheet` (`.worksheet .wide`, `.worksheet .rating`), not under `.table-shell table` — using the literal wording would have silently dropped those column stylings. Columns: FMEA (link), Function/Requirement, Failure Mode, Effects, Cause, S, O, Prevention Controls, Detection Controls, D, Risk, Actions.

`_sidebar.html`: new **FMEA ANALYSIS** group added between RISK and Import & Review, containing DFMEA and PFMEA links — this is the one intentional flip the instruction calls for in `test_gui_navigation_scope.py` (moving `"FMEA ANALYSIS"` out of the negative/unbuilt-label tuple into positive assertions, alongside new `"DFMEA"`/`"PFMEA"` positive checks). No other group touched.

## 2. Test coverage

New `tests/test_dfmea_pfmea_worksheets.py`, 7 tests, real fixture data: a design-type FMEA ("Bracket DFMEA") and a process-type FMEA ("Seal Assembly PFMEA"), each with a full failure-mode chain (cause, prevention/detection controls, risk evaluation with a stored `result` dict) plus two `RecommendedAction`s on the DFMEA cause (one overdue, one open-not-overdue) to exercise the Actions column arithmetic.

- `test_design_type_fmea_appears_only_on_dfmea_page` / `test_process_type_fmea_appears_only_on_pfmea_page` — confirms the `fmea_type` split is exclusive in both directions.
- `test_row_content_matches_fixture_data_on_dfmea_page` / `..._on_pfmea_page` — checks S/O/D digits scoped to the row's own `<tr>` (via string-index slicing, not a page-wide substring check, to avoid false positives from other digits on the page).
- `test_actions_column_shows_correct_open_and_overdue_counts` — asserts the literal `"2 open / 1 overdue"` string appears.
- `test_pages_stay_within_narrowed_scope` — negative checks for `<canvas`, "Structure Tree", "Interface Matrix", "Parameter Diagram", "Control Plan" (nothing beyond the instructed scope leaked in).
- `test_rows_link_to_the_correct_fmea_detail_page` — confirms the FMEA column really links to `fmea:fmea_detail`, not a dead or placeholder link.

`tests/test_gui_navigation_scope.py` — the required one-line flip plus new DFMEA/PFMEA positive assertions.

## 3. Verification

Fresh venv, live shell, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | "No changes detected" | "No changes detected" |
| `test_dfmea_pfmea_worksheets.py` (isolated) | 7/7 | — |
| `test_gui_navigation_scope.py` (isolated) | 3/3 | — |
| Full suite | **132/132** | **132/132** |

132 = the prior 125 (Slice A + contrast-checker Part B + Slice C, all previously independently confirmed) plus the 7 new tests here — arithmetic checked, not just asserted.

Diff surface confirmed via `git status --short`: on top of the already-uncommitted prior slices, Slice D's own footprint is exactly `views.py`, `urls.py`, `_sidebar.html` (all already modified, further modified here), plus `dfmea_worksheet.html`, `pfmea_worksheet.html`, `test_dfmea_pfmea_worksheets.py` (new) and `test_gui_navigation_scope.py` (modified) — matching the instruction's allowed-file list exactly, nothing else touched.

Mirrored to `open_fmea_training_set` and byte-diffed (`diff -q`, not size/mtime): `views.py`, `urls.py`, `dfmea_worksheet.html`, `pfmea_worksheet.html`, `_sidebar.html`, `test_gui_navigation_scope.py`, `test_dfmea_pfmea_worksheets.py` — all identical. Full suite re-run there independently: 132/132.

## 4. Scope discipline

No `models.py`/`forms.py`/migration changes (worksheet pages are read-only views over existing data). No changes to the existing per-FMEA worksheet or its helpers. No relationship-diagram SVG/canvas, no System/ClassificationScheme content, no Control Plan content — confirmed by the negative test and a manual grep of both new templates.

## 5. Still open (unchanged, not touched this pass)

- `.git/index.lock` still needs a manual delete in `open_fmea`. Nothing committed — everything above sits uncommitted alongside the rest of today's work, per "build first, commit later."
- The `instructions/` directory (Slices E–M plus several new architecture-decision docs) has not yet been read in full or implemented — queued as the next work.

# Claude Review — Risk Matrix Implementation and `open_fmea_training_set` Mirror

Status: implementation + independent verification record, written by the same session that built the slice (there was no separate Codex handoff this round — the user explicitly authorized Claude to implement `Codex_Instruction_RiskMatrix_Slice.md` directly, in place of Codex, given a detected coordination risk with a concurrent agent session). Kept as the authoritative record of what was built and verified, per `OpenFMEA_DNA_CoreReference.md` rule 9 (every implementation claim independently re-verified, not trusted from a status report) and rule 10 (nothing deleted from `architecture/`, only superseded and indexed).

Author: Claude, acting as Open-FMEA Technical Architect and implementer for this slice.

Date: 2026-09-03.

## 1. What this covers

Two things, both completed this session:

1. The Risk Matrix slice, built exactly per `Codex_Instruction_RiskMatrix_Slice.md` (design authority: `OpenFMEA_RiskMatrix_ArchitectureReview.md`), both written by a separate agent session earlier the same day, with all four of the review's open decisions already confirmed by the user on 2026-09-01.
2. Closing the `open_fmea_training_set` source-mirror gap — not just for this slice, but for the two prior slices (characteristics-linking, GUI design system) whose mirror had been left outstanding across multiple prior verification rounds despite being flagged each time.

## 2. Risk Matrix — what was built, and how it was verified

Full implementation detail (exact files, exact functions, exact test list) is recorded in `OpenFMEA_DNA_CoreReference.md` Section 12 rather than duplicated here. Summary:

- `classify_severity_occurrence` added additively to `fmea_evaluation/calculators.py` — the review's own thresholds (<=8 low, 9-24 medium, 25-48 high, >48 very_high), confirmed against the instruction's exact code, not re-derived.
- `fmea_app/risk_matrix.py` (new) — all query logic, kept out of `views.py` per the instruction so it's independently testable. Verified directly: `latest_evaluations_by_method` uses a single query ordered by `(failure_mode_id, -evaluated_at, -id)`, no window function, matching the instruction's "simple counts/filters" constraint.
- Three new views/routes (`/risk-matrix/`, `/risk-matrix/cell/`, `/risk-matrix/top/`), three new templates, one sidebar entry, one dashboard stat card, additive CSS only (one new token, `--status-critical-strong`, for the `very_high` band).
- 12 new tests in `tests/test_risk_matrix.py`, `tests/test_gui_navigation_scope.py` updated (Risk Matrix moved from the excluded list to the asserted-present list — the one deliberate addition, nothing else touched).

**Independent verification performed, not assumed:**

- Read the current on-disk `RiskEvaluation`/`EvaluationDefinition` model fields and `services.evaluate_failure_mode` before writing any code, rather than relying on prior-session memory of their shape — confirmed `RiskEvaluation` stores `severity`/`occurrence`/`detection` as direct integer fields (not nested), which the query logic depends on.
- `git diff --stat` after implementation, checked line-for-line against the instruction's Section 5 file list — every changed/new file is on that list, nothing else.
- `manage.py check` clean, `makemigrations --check --dry-run --no-input` reports no changes (expected — no model change).
- Full suite re-run: 99/99 passing (87 pre-existing + 12 new), zero unrelated assertion changes — confirmed by running `test_risk_matrix.py` and `test_gui_navigation_scope.py` together with `-v` and reading the actual pass count, not inferred from a green exit code alone.
- Section 6's explicit exclusions checked directly: `classify_severity_occurrence`'s only parameters are `severity`/`occurrence` (`__code__.co_varnames`/`co_argcount` asserted in a test, not just eyeballed); the drill-down test seeds a `RiskEvaluation` with a deliberately wrong stored `result["score"]` and confirms the view renders that wrong value verbatim, proving no recomputation.

## 3. `open_fmea_training_set` mirror — what was actually missing, and what closed it

Before starting the Risk Matrix implementation, `diff -rq` between `open_fmea/django_app` and `open_fmea_training_set/django_app` was run to establish a real baseline rather than trusting the DNA document's prior "not yet mirrored" note at face value. The gap was larger than that note alone suggested: it included not just this slice's future files but the entire GUI design-system slice (dashboard, sidebar, theme.css) and the characteristics-linking slice's Process Flow gap-fix (`process_flow.html`, the updated `fmea_detail.html`/`process_characteristic_detail.html`/`process_characteristic_list.html`, `seed_demo.py`) — none of it had ever been copied over.

All of it was closed in one pass: 16 `django_app` files and 3 `tests` files copied file-for-file from `open_fmea` to `open_fmea_training_set` (via a script that reads and writes the actual files, never by retyping content from earlier tool output). Re-verified after copying, independently:

- `diff -rq open_fmea/django_app open_fmea_training_set/django_app` — zero differences outside `open_fmea_project/settings.py` and `open_fmea_project/urls.py`, both confirmed to be pre-existing, deliberate packaging-specific differences (`ALLOWED_HOSTS` including `testserver`; dev-only `staticfiles_urlpatterns` wiring) unrelated to any slice's file list — not something this or any prior slice should have touched.
- `diff -rq open_fmea/tests open_fmea_training_set/tests`, `.../domain`, `.../fmea_review`, `.../fmea_ingestion`, `.../fmea_ai`, `.../fmea_importexport` — all clean.
- `open_fmea_training_set`'s own `manage.py check`, `makemigrations --check --dry-run --no-input`, and full `pytest` run were executed independently in that tree, not assumed from the `open_fmea` run — 99/99 passing, clean.

## 4. What is still not done, stated plainly rather than left implicit

**The training EXE was not rebuilt.** `packaging/build_exe.ps1` requires Windows PowerShell and the repository's own Windows `.venv\Scripts\python.exe` to run PyInstaller; this session reaches the repository through a sandboxed Linux bridge with neither available, and cross-compiling a Windows PyInstaller executable from Linux is not supported. The source mirror is complete and independently verified (Section 3); the EXE itself is stale relative to it until the user runs the existing, unmodified build script locally:

```powershell
cd D:\Dromation\org\apps\open_fmea_training_set
powershell -File packaging\build_exe.ps1
```

This is recorded here explicitly, per the instruction's own Section 9 Acceptance Criteria #7 ("do not let this slice's mirror go the same way [as previously outstanding]") — the source half of that criterion is done; the EXE half needs one manual step from the user that no session reaching this repo through the current bridge can perform.

## 5. Operational note

A stale `.git/index.lock` (created 08:34 UTC, unchanged across a 28-minute re-check with no concurrent git-relevant changes observed) was found at session start, confirmed stale by that re-check rather than deleted on sight, and removed via the device bridge's explicit delete-permission flow before this slice's commit. See `OpenFMEA_DNA_CoreReference.md` Section 7 for the standing pattern this follows.

## Recommendation

**DONE, WITH ONE MANUAL STEP OUTSTANDING.** The Risk Matrix slice is built and independently verified in both repositories; the `open_fmea_training_set` source mirror gap (this slice and the two before it) is closed and verified. Only the local Windows EXE rebuild remains, and it cannot be performed from this environment — it needs the user to run the existing `packaging\build_exe.ps1` script once.

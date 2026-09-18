# Claude Review — Nav Shell Restyle (Slice A) + Cross-Slice Workflow Test (Contrast-Checker Part B)

**Author:** Claude (this session) · **Date:** 2026-09-04
**Scope:** Two independent, approved slices, implemented and verified in one pass per the user's "build first, commit later" direction. Both live only as uncommitted working-tree changes in `open_fmea`, mirrored to `open_fmea_training_set` (no `.git` there, nothing to commit).

## 1. Slice A — `Codex_Instruction_GUINavShellRestyle_SliceA.md`

Rewrote `django_app/fmea_app/templates/fmea_app/_sidebar.html`'s nav content into six real links under six groups, exactly matching Section 1 of the instruction: `HOME`/`Home`, `WORKSPACE`/`FMEA Projects`, `CONTEXT`/`Process Characteristics`, `RISK`/`Risk Matrix`, plus the two pre-existing groups (`Import & Review`/`Import Sessions`, `Ishikawa / Cause Analysis`/`Cause Influences`) left unchanged. Every link uses `{% url %}` against a route already in `fmea_app/urls.py`/`fmea_review/urls.py` — confirmed by grep, zero `href="#"` or hardcoded paths. Reused the existing `.nav-group`/`.nav-group-title` classes; no new CSS.

Extended `tests/test_gui_navigation_scope.py`'s existing test method (didn't replace it) with: positive assertions for all four new group headers plus the two existing ones; a negative assertion for `"Process Control Characteristics"` (the page keeps its real "Process Characteristics" label); and four new entries in the existing `unbuilt_label` exclusion tuple (`"FMEA ANALYSIS"`, `"FMEA ELEMENTS"`, `"VALIDATION & CHANGE"`, `"FMEA Team"`).

Diff surface for this slice, confirmed via `git status --short` before and after: exactly `_sidebar.html` and `tests/test_gui_navigation_scope.py`, nothing else — matches acceptance criterion 4 precisely.

## 2. Contrast-checker Part B — `Codex_Instruction_TestCoverage_ContrastChecker_CrossSliceWorkflow_Slice.md`

Precondition re-checked first: the dark-mode `--text-muted` fix (`#8b96ab`) landed earlier today and Part A's contrast test (`test_wcag_aa_contrast_for_text_background_pairs`) was re-run — still green, all 12 pairs ≥4.5:1 in both themes.

New file `tests/test_cross_slice_workflow.py`, one `TestCase`, one test method, real `self.client` HTTP requests throughout except for the three prerequisites the instruction explicitly names as ORM-only (`EvaluationDefinition`, `Product`, `Operation` — no GUI creation path for any of them today). Chain, in order: dashboard (theme-toggle present) → project create → FMEA create → Function (via `/functions/add/`, tied to the `Product`) → Failure Mode (via `/failure-modes/add/`, tied to the `Function`) → Cause (via `/causes/add/`) → Action (via `/cause/<id>/actions/add/`, confirmed `failure_cause` set / `failure_mode` null) → Process Characteristic (via `/process-characteristics/new/`, tied to the `Operation`) → Cause Influence (via `/cause-influences/create/`, `source_type=ProcessCharacteristic` → `target_type=FailureCause`, real `cause_category_id` from a seeded `CauseCategory`) → Ishikawa board for the failure mode (asserts both the cause and the process-characteristic name from the new influence appear) → Risk Matrix (renders, no per-FMEA assertion, per the standing system-wide decision) → worksheet (function/failure-mode/cause/action names all present together, theme-toggle present).

Every URL and POST field was read directly from `urls.py`/`views.py`/`forms.py`/`models.py` before writing the test, not assumed — the exact thing the instruction warned against repeating from the earlier Functions-slice mistake. One example that mattered: `CauseInfluence.SOURCE_TYPE_CHOICES` only allows `FailureCause`/`FailureMechanism`/`ProcessCharacteristic` and `TARGET_TYPE_CHOICES` only allows `FailureMode`/`FailureCause`/`ProductCharacteristic` — confirmed `ProcessCharacteristic → FailureCause` (the instruction's own required pairing) is valid before writing the POST.

## 3. Verification

Fresh venv, live shell, real `samples/` fixtures, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | "No changes detected" | "No changes detected" |
| `test_gui_navigation_scope.py` | 3/3 | — (same file, mirrored) |
| `test_cross_slice_workflow.py` | 1/1 | — |
| `test_theme_toggle.py` (incl. contrast test) | 7/7 | — |
| Full suite | **121/121** | **121/121** |

121 = the 120 the user independently confirmed for Part A, plus the one new cross-slice test — arithmetic checked, not just asserted.

Mirrored to `open_fmea_training_set` and content-diffed (`diff -q`, not size/mtime): `_sidebar.html`, `test_gui_navigation_scope.py`, `test_cross_slice_workflow.py`, `_contrast.py`, `test_theme_toggle.py`, `theme.css` — all byte-identical post-copy.

## 4. Scope discipline

No `models.py`/`views.py`/`urls.py`/`forms.py`/migration changes for Slice A (backend untouched, as required). No production code (`django_app/`, `domain/`) changed for the contrast-checker Part B — only `tests/`. Neither slice touched the other's files. Nothing pushed; nothing committed (per "build first, commit later" — both slices sit uncommitted in `open_fmea` alongside the already-uncommitted Projects+Team slice and the two `--text-muted` fixes).

## 5. Still open (unchanged from before this pass, not touched now)

- `.git/index.lock` still needs a person to delete it by hand in `open_fmea` — same finding as before, not re-investigated this pass.
- `open_fmea_training_set`'s mirror of the *Projects+Team* slice specifically (not today's two slices) is still only size/mtime-verified, not content-diffed — out of scope for this pass, not touched.
- Committing everything currently uncommitted remains deferred by explicit direction, not an oversight.

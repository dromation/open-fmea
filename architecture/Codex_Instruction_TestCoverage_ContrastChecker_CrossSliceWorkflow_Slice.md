# Codex Implementation Instruction — Automated WCAG Contrast Checker + Cross-Slice End-to-End Workflow Test

Status: Approved for implementation with a live precondition. Requested by the user 2026-09-03, in response to a gap surfaced during independent verification of `Codex_Instruction_LightDarkThemeToggle_Slice.md`: that slice's own test suite (6/6 green) did not catch a real WCAG AA contrast failure (`--text-muted` at 2.4–2.6:1 against the required 4.5:1 in light mode) because the existing tests only assert that certain CSS blocks/strings are present, never that the actual token *values* produce a legible contrast ratio. Test-only once the theme tokens are already valid. Does not block today's `v1.0.0` release.

**Precondition added after independent verification:** the light-mode `--text-muted` bug is fixed, but the original dark-mode `--text-muted: #77849a` still fails AA against `--bg-card` (4.25:1) and `--bg-card-strong` (3.80:1). Do not start this test-only slice expecting it to pass unchanged until that dark-token fix is implemented by the theme-owning slice first; otherwise the new contrast test should fail, correctly.

Authority, in order: same chain as prior slices; additionally subordinate to `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` (owns `theme.css`) and `Codex_Instruction_LightDarkThemeToggle_Slice.md` (owns the light/dark token structure this checker reads). Does not modify either.

## 0. Decisions made for this slice, and why — read before starting

Two independent pieces of work, bundled because both are test-coverage hardening discovered from the same review pass, both are test-only, and both are low-risk/quick:

1. **Contrast checker mechanism:** a small, dependency-free, regex-based CSS custom-property parser plus the standard WCAG 2.1 relative-luminance/contrast-ratio formula — not a real CSS engine, not a browser, not a new library. This matches the project's own established testing philosophy for this area (`Codex_Instruction_LightDarkThemeToggle_Slice.md` Section 5: "a simple content/regex check is sufficient... this is a template-rendering test suite, not a browser test"). The checker reads the *actual* `theme.css` shipped via Django's staticfiles finder (`django.contrib.staticfiles.finders.find`, the same pattern already used in `tests/test_theme_toggle.py::test_theme_css_defines_dark_default_and_light_override_tokens`) — never a hardcoded copy of the values — so it keeps catching regressions as the file changes, not just today's bug.
2. **Threshold policy:** hold every checked pair to the 4.5:1 "normal text" AA floor, not the relaxed 3:1 "large text / UI component" floor. WCAG's large-text exception applies only to specific font-size/weight combinations, and getting that classification wrong is exactly the kind of subtle mistake this checker exists to prevent. If a token is genuinely large-text-only or a non-text usage (background/border/outline), the fix is to leave it out of the checked-pairs list entirely (with a one-line comment saying why), not to special-case a lower threshold in the checker itself.
3. **Cross-slice test mechanism:** one new `TestCase` that chains multiple existing slices through real `self.client` HTTP requests in a single continuous flow — the same style already used in `tests/test_app_workflow.py` and every per-slice GUI test file. No new views, no new forms. Where a step's only creation path is the ORM (no GUI view exists yet — true for `Product`, `Operation`, `ProductCharacteristic`, `EvaluationDefinition`, `CauseCategory`), create that prerequisite directly via `models.X.objects.create(...)`, exactly as `test_app_workflow.py` already does for `EvaluationDefinition`. Do not invent a view or URL that doesn't exist.

## 1. Exact Scope

### Part A — Contrast checker

1. New helper module `tests/_contrast.py` (leading underscore: a test utility, not itself a test module — pytest will not collect it) with three pure functions:
   - `relative_luminance(hex_color: str) -> float` — standard WCAG 2.1 formula (sRGB channels → linearized, weighted `0.2126*R + 0.7152*G + 0.0722*B`).
   - `contrast_ratio(fg_hex: str, bg_hex: str) -> float` — `(L_lighter + 0.05) / (L_darker + 0.05)`.
   - `extract_theme_tokens(css_text: str, block_selector: str) -> dict[str, str]` — given the raw `theme.css` text and a selector string (e.g. `":root {"` or `':root[data-theme="light"] {'`), return a `{token_name: "#hexvalue"}` dict of every `--token-name: #hexvalue;` declaration inside that one block (stop at the block's closing `}`, accounting for nested `@media` blocks appearing *before* the top-level selector's own closing brace — see Section 2 for the exact structure to parse). Skip/ignore any declaration whose value is not a bare `#rrggbb` hex literal (e.g. `rgba(...)`, `var(...)`) rather than erroring.
2. Extend `tests/test_theme_toggle.py` (do not create a second test file for this — it belongs with the toggle's own tests) with a new test, `test_wcag_aa_contrast_for_text_background_pairs`, that:
   - Reads the real `theme.css` via `find("fmea_app/css/theme.css")` (same as the existing `test_theme_css_defines_dark_default_and_light_override_tokens`).
   - Extracts the dark tokens from the top `:root {` block and the light tokens from the explicit `:root[data-theme="light"] {` block (the override block, not the `@media` block — it's the one guaranteed to contain every light-mode value).
   - For each `(foreground_token, background_token)` pair in the list below, computes `contrast_ratio` for both the dark-token values and the light-token values, and asserts each is `>= 4.5`.

## 2. Required token-pair list (both themes)

Checked pairs, derived from actual `color:`-on-background usage in `theme.css` and its templates (grep-verified during the review that surfaced this gap):

```python
CHECKED_PAIRS = [
    ("--text-primary", "--bg-app"),
    ("--text-primary", "--bg-card"),
    ("--text-secondary", "--bg-app"),
    ("--text-secondary", "--bg-card"),
    ("--text-muted", "--bg-app"),
    ("--text-muted", "--bg-card"),
    ("--status-good-text", "--bg-card"),
    ("--status-warning-text", "--bg-card"),
    ("--status-critical-text", "--bg-card"),
    ("--link-color", "--bg-card"),
    ("--code-color", "--bg-card"),
    ("--brand-mark-fg", "--brand-mark-bg"),
]
```

Do **not** include `--accent-primary`, `--accent-primary-strong`, or `--accent-secondary` — grep confirms these are only ever used as `background`, `border-color`, or `outline` in `theme.css`, never as `color` (text), so they are a 3:1 UI-component concern at most, out of scope for this normal-text checker. Do **not** include `--status-critical-strong` — it is only ever paired with the hardcoded, theme-invariant `color: #fecaca` (both already fixed values, not theme tokens — if you want a regression test for that specific pair, add `contrast_ratio("#fecaca", "#7f1d1d") >= 4.5` as its own separate, explicitly-labelled assertion, not inside the token-pair loop, since it isn't a `--token`/`--token` pair).

If `theme.css` changes in a future slice and a new `color:`-on-`background`-role token pairing is introduced, add it to `CHECKED_PAIRS` in that slice — this list is not meant to be exhaustive forever, only accurate as of what's shipped today.

### Part B — Cross-slice end-to-end workflow test

New file `tests/test_cross_slice_workflow.py`, one `TestCase` with one test method, `test_full_gui_workflow_across_slices`, that exercises — in one continuous flow, via `self.client`, asserting real DB state and real rendered content at each step, not mocks — at minimum:

1. `GET` the dashboard (`fmea:dashboard`) — assert it renders and contains the theme-toggle control (`data-theme-toggle`), tying the presentational slice into the same session.
2. Create prerequisites via ORM where no GUI view exists: an `EvaluationDefinition` (classic RPN, as in `test_app_workflow.py`), a `Product`, an `Operation`.
3. `POST /projects/create/` then `POST /fmeas/create/` — real FMEA created through the GUI (as in `test_app_workflow.py`).
4. `POST /fmea/<stable_id>/functions/add/` with a `product` or `operation` reference — exercises the Functions slice (`Codex_Instruction_FunctionsActionsEvidence_GUIGap_Slice.md`).
5. `POST /fmea/<stable_id>/failure-modes/add/`, then `POST /failure-mode/<stable_id>/causes/add/` — real failure mode and cause.
6. `POST /cause/<stable_id>/actions/add/` — exercises the Actions slice on the same `FailureCause` created in step 5.
7. `POST /process-characteristics/new/` (with the `Operation` from step 2) — exercises the Process Characteristic slice (`Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md`).
8. `POST /cause-influences/create/` linking `source_type=ProcessCharacteristic` (the one from step 7) to `target_type=FailureCause` (the one from step 5) — exercises the Ishikawa/CauseInfluence backend (`Codex_Instruction_CauseInfluence_CauseCategoryScheme_IshikawaBackend_Slice.md`) end-to-end against real GUI-created objects, not fixtures.
9. `GET /failure-modes/<stable_id>/ishikawa-board/` for the failure mode from step 5 — assert the cause created in step 5 and the influence link from step 8 both appear.
10. `GET /risk-matrix/` — assert it renders (system-wide grid, per `Codex_Instruction_RiskMatrix_Slice.md`); no assertion tying it to this specific FMEA is required (Risk Matrix is deliberately system-wide, not per-FMEA — do not add a per-project filter assertion here, that would contradict the standing "system-wide, no per-project scoping" decision).
11. `GET /fmea/<stable_id>/` (the worksheet) one final time — assert the function (step 4), failure mode (step 5), cause (step 5), and action (step 6) names are all present together on the one page, and that the theme-toggle control is present here too.

This is one long test method (a real user session strung together), not eleven small ones — that's the point: it proves the pieces work *together*, which the existing per-slice tests (each scoped to its own feature) do not.

## 3. Exact Allowed / New Files

```text
tests/_contrast.py                       # new — pure functions, no Django/domain imports
tests/test_theme_toggle.py               # extended — one new test method + CHECKED_PAIRS import, nothing else changed
tests/test_cross_slice_workflow.py       # new
```

Nothing in `django_app/`, `domain/`, or any template/CSS/JS file changes for this slice. If the dark-mode `--text-muted` fix has not already landed, stop and do that as a separate theme-token fix before implementing this test-only slice. If contrast checking or the workflow test reveals any further application bug beyond that known value, stop and report; do not silently expand this slice to fix application code.

## 4. Required Validation and Explicit Exclusions

- No production code (`django_app/`, `domain/`) changes of any kind.
- No new dependency — `tests/_contrast.py` uses only the Python standard library (`re`, `pathlib`).
- The contrast checker must read the real, shipped `theme.css` (via the staticfiles finder) — not a copy, not inline hardcoded token values — so it stays accurate as the file evolves.
- The cross-slice test must use real HTTP requests (`self.client.get`/`self.client.post`) for every step that has a real GUI view; use direct ORM creation only for the prerequisites listed in Section 1 Part B step 2 that have no GUI view today. Do not invent a URL or view that doesn't exist.
- Both new/extended test files must pass together with the full existing suite — no unrelated assertion changes, no existing test's behavior altered.

## 5. Required Tests

- `tests/test_theme_toggle.py::ThemeToggleTests::test_wcag_aa_contrast_for_text_background_pairs` — as specified in Section 1 Part A. Must pass after both known `--text-muted` fixes are present (light already fixed; dark still pending at the time this instruction was updated). If it doesn't, that's a real finding, report it, don't loosen the threshold to make it pass.
- `tests/test_cross_slice_workflow.py::CrossSliceWorkflowTests::test_full_gui_workflow_across_slices` — as specified in Section 1 Part B.
- Full existing suite re-run with no unrelated assertion changes.

## 6. Commands to Run

```powershell
python -B manage.py check
python -B -m pytest
```

## 7. Acceptance Criteria

1. `tests/_contrast.py` exists, is pure-Python (no Django/domain imports), and correctly reproduces the WCAG 2.1 relative-luminance/contrast-ratio formula (spot check: `contrast_ratio("#000000", "#ffffff")` must equal `21.0`; `contrast_ratio("#ffffff", "#ffffff")` must equal `1.0`).
2. The new contrast test reads the real `theme.css` and fails loudly (not silently skips) if either the dark or light token block is missing or a checked token is absent.
3. All twelve pairs in `CHECKED_PAIRS`, in both the dark and light token sets, measure `>= 4.5`. If any doesn't, the test fails — that is correct behavior, not a bug in this slice. As of this update, dark-mode `--text-muted` is the known precondition that must be fixed before this criterion can pass.
4. The cross-slice workflow test passes and genuinely exercises Functions, Failure Modes/Causes, Actions, Process Characteristics, Cause Influence (Ishikawa), Risk Matrix, and the theme toggle control's presence, all via real HTTP requests within one continuous session.
5. Full test suite passes, `manage.py check` clean.
6. No production file (`django_app/`, `domain/`, any `.css`/`.js`/`.html`) appears in the diff.
7. Mirrored into `open_fmea_training_set` per the standing discipline. No training-EXE rebuild is required by this change alone (test-only, no static/packaging-relevant file changed).

## 8. Explicit Exclusions (restated for emphasis)

No production/application code change of any kind. No new third-party dependency (no `wcag-contrast-ratio` package, no CSS parser library — the regex approach in Section 1 is deliberate and sufficient for this file's simple structure). No browser/Selenium/Playwright test. No change to the checked-pairs' underlying token *values* — if a pair fails, the fix belongs in whichever slice owns `theme.css` (currently the Light/Dark Theme Toggle slice's own follow-up), not in this test-only slice.

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

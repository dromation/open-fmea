# Claude Review — `--text-muted` WCAG Contrast Fix (Light/Dark Theme Toggle Slice)

**Author:** Claude (this session) · **Date:** 2026-09-03
**Scope:** One-token fix to `django_app/fmea_app/static/fmea_app/css/theme.css`, applied on top of the not-yet-committed Light/Dark Theme Toggle slice (`theme.css`, `app.js`, `_header.html`, `tests/test_theme_toggle.py`).

## 1. What was flagged

While implementing `Codex_Instruction_LightDarkThemeToggle_Slice.md`, I copied the instruction's ten prescribed light-mode token values verbatim, including `--text-muted: #94a3b8`, and only independently audited the *new* tokens I introduced myself (status-text colors, link colors, etc.) for WCAG contrast. I did not re-check the instruction's own given values.

The concurrent session's `Codex_Instruction_TestCoverage_ContrastChecker_CrossSliceWorkflow_Slice.md` (Part A: a real `tests/_contrast.py` WCAG checker reading actual `theme.css` tokens) flagged that this value fails the instruction's own stated requirement — 4.5:1 for normal text — in light mode.

## 2. Independent verification of the bug

Computed actual relative-luminance contrast ratios (WCAG 2.x formula, not eyeballed) for `--text-muted: #94a3b8` against every light-mode background it composites against in the shipped token set:

| Background token | Value | Ratio vs `#94a3b8` | Required | Result |
|---|---|---|---|---|
| `--bg-app` | `#f5f7fb` | 2.39:1 | 4.5:1 | **FAIL** |
| `--bg-surface` | `#ffffff` | 2.56:1 | 4.5:1 | **FAIL** |
| `--bg-card` | `#ffffff` | 2.56:1 | 4.5:1 | **FAIL** |
| `--bg-card-strong` | `#f1f4f9` | 2.33:1 | 4.5:1 | **FAIL** |
| `--bg-input` | `#ffffff` | 2.56:1 | 4.5:1 | **FAIL** |

Confirmed: real bug, fails badly (not a borderline rounding case) against every light-mode surface it's used on. Root cause was exactly as described in Section 1 — trusting an instruction's own given value without independently re-verifying it, the same category of lesson as the earlier Functions/Actions scope-pull.

## 3. Fix applied

Replaced `--text-muted: #94a3b8` with `--text-muted: #5b6b82` at both light-mode definition sites in `theme.css` (the `prefers-color-scheme: light` media block and the explicit `[data-theme="light"]` block — both must stay in sync per the instruction's own pattern). No other token, and no dark-mode value, was touched.

New ratios for `#5b6b82`:

| Background token | Value | Ratio vs `#5b6b82` | Required | Result |
|---|---|---|---|---|
| `--bg-app` | `#f5f7fb` | 5.06:1 | 4.5:1 | PASS |
| `--bg-surface` | `#ffffff` | 5.43:1 | 4.5:1 | PASS |
| `--bg-card` | `#ffffff` | 5.43:1 | 4.5:1 | PASS |
| `--bg-card-strong` | `#f1f4f9` | 4.92:1 | 4.5:1 | PASS |
| `--bg-input` | `#ffffff` | 5.43:1 | 4.5:1 | PASS |

All five pass with margin, so the value tolerates minor future background tweaks without going borderline again.

## 4. Verification performed

- `manage.py check` — 0 issues.
- `manage.py makemigrations --check --dry-run` — no changes detected (this is a CSS-only change; expected).
- Full `pytest` suite (real Django test execution, staged source tree, own container — `device_bash` to the user's machine remains unavailable this session, see Section 6): **112/112 passing**, no regression. `tests/test_theme_toggle.py`'s existing assertions do not pin the `--text-muted` literal value, so no test file needed updating for this fix.

## 5. Related finding — not actioned (out of scope for this fix)

While computing the light-mode ratios above, I also sanity-checked the pre-existing **dark-mode** `--text-muted: #77849a` (byte-identical since before this slice, not part of my new work) against its own backgrounds:

| Background token | Value | Ratio vs `#77849a` | Required | Result |
|---|---|---|---|---|
| `--bg-app` | `#0e121b` | 4.95:1 | 4.5:1 | PASS |
| `--bg-surface` | `#121826` | 4.69:1 | 4.5:1 | PASS |
| `--bg-card` | `#192132` | 4.25:1 | 4.5:1 | **FAIL** |
| `--bg-card-strong` | `#202a3d` | 3.80:1 | 4.5:1 | **FAIL** |

This is a real, separate contrast gap in the original shipped dark theme (predates the toggle slice). Per project discipline (no scope expansion beyond what was asked, nothing changed without an approved instruction), I have **not** touched this value. Flagging it here for the concurrent session / a future explicit instruction — it's exactly the kind of case `tests/_contrast.py` (Part A of the queued contrast-checker instruction) should also catch once built, and fixing it should go through that same instruction rather than being folded silently into this one-token fix.

## 6. Current status / what's still pending

- The fix is written to disk in both `open_fmea` and `open_fmea_training_set` (confirmed via directory listing: `theme.css`, 19,125 bytes, matching fresh mtime in both trees).
- **Not yet git-committed.** This session's `device_bash` FUSE mount to the user's machine remains down (re-confirmed just now — `~/mnt/open_fmea` still fails to mount; `/proc/mounts` shows no fuse entry for it). This is the same operational-risk category already logged in `Claude_Review_FunctionsActions_Implementation_ScopeCorrection.md` Section 7. File delivery is unaffected (uses `device_list_dir`/`device_stage_files`/`device_commit_files`, a separate channel), but `git add`/`git commit` genuinely requires a working shell on the target machine and cannot be done another way.
- **Outstanding commit, once the mount recovers:** the full Light/Dark Theme Toggle slice (`theme.css`, `app.js`, `_header.html`, `tests/test_theme_toggle.py`) *plus* this `--text-muted` fix, as one clean commit (or two, slice + fix), with the required `Co-Authored-By` / `Claude-Session` footer, in both repos.
- Per the user's own framing, `Codex_Instruction_TestCoverage_ContrastChecker_CrossSliceWorkflow_Slice.md` was queued to start only after this fix — that instruction has been read into context but not yet implemented, and implementation has not started.
- Standing instruction "ne, pozabi" (never push to GitHub unless explicitly asked again) continues to apply; nothing has been pushed.

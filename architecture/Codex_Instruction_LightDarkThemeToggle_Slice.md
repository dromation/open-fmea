# Codex Implementation Instruction — Light/Dark Theme Toggle (all GUI pages)

Status: Approved for implementation. Requested by the user 2026-09-03 ("naredi night način switch in day način switch za vse GUI-je"). Purely presentational — no backend, no new entity, no migration. Worth noting: the already-built GUI shell (`Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md`) shipped dark-only, while every reference mockup the user has sent since (18 so far, cataloged in `OpenFMEA_DNA_CoreReference.md` Section 10) has been light-themed — this slice resolves that gap by supporting both, rather than picking one.

Authority, in order: same chain as prior slices; additionally subordinate to `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` (owns `theme.css`/`base.html`, which this slice extends without breaking).

## 0. Decisions made for this slice, and why — read before starting

Three judgment calls, each low-risk and easily adjusted later (this is CSS variables plus a small script, nothing structural):

1. **Mechanism:** a `data-theme="dark"` / `data-theme="light"` attribute on `<html>`, toggled by a small script. No attribute set = honor the visitor's OS-level `prefers-color-scheme`. An explicit toggle click always wins over system preference, in both directions.
2. **Persistence:** `localStorage` only (no backend field, no user account tie-in) — this app has no real per-user login in active use today (`django.contrib.auth` is installed but not meaningfully used — confirmed in the Mockup 6/7 audit), so a server-side per-user preference would be premature. Per-browser is the honest, currently-correct scope; upgrading to a per-account setting later, if/when a real user system exists, is a small follow-up, not a rework.
3. **Default on first visit (no stored preference yet):** honor `prefers-color-scheme`; if the browser reports no preference either, fall back to **dark** — matching the currently-shipped, already-verified default, so a first-time visitor with no OS preference sees exactly what's live today. This is not "light by default despite every mockup being light" — the mockups are reference material for the light palette's *content*, not a mandate to flip today's default.

## 1. Exact Scope

1. Restructure `theme.css`'s token block so dark values (today's `:root` block, verbatim, unchanged) remain the default/fallback, and a full light-mode token set is added, switched by the mechanism in Section 0.
2. A toggle control in `_header.html` (sun/moon icon or equivalent, matching the existing icon-button style already used for the sidebar-toggle button in `base.html`) — visible on every page (it lives in the shared header, not per-page).
3. A small addition to `app.js` (already deferred-loaded from `base.html`): on load, read `localStorage`, apply `data-theme` if a preference is stored; on toggle click, flip `data-theme`, write to `localStorage`, no page reload needed (pure CSS variable swap).
4. Every existing page inherits this automatically — it lives in the shared `theme.css`/`base.html`/`_header.html`, not per-template, so "for all GUIs" falls out of the shared-shell architecture already in place rather than needing per-page changes.

Nothing beyond this list. No new backend field, no per-user account setting, no new page, no visual redesign beyond the color-token swap (spacing/radius/shadow tokens stay as-is; layout is unchanged).

## 2. Required Tokens

Keep every existing dark value in `theme.css`'s current `:root` block completely unchanged (this is the fallback/default — must not regress anything already verified). Add a light-mode set, derived to match the visual language shown across the light-themed reference mockups (off-white app background, white cards, dark slate text) while preserving the same accent/status hues so charts, badges, and status colors stay recognizable in both themes:

```css
/* Dark (existing, unchanged — stays as the :root default) */
:root {
  --bg-app: #0e121b;
  --bg-surface: #121826;
  --bg-card: #192132;
  --bg-card-strong: #202a3d;
  --bg-input: #101623;
  --border-subtle: #2a3447;
  --border-strong: #3a465b;
  --text-primary: #edf1f7;
  --text-secondary: #a5afc2;
  --text-muted: #77849a;
  /* accent/status/space/radius/shadow tokens: unchanged, verbatim */
}

/* Light — new, added under both a media query (system preference,
   only when no explicit choice is stored) and an explicit override
   (always wins once the user has toggled) */
:root:not([data-theme="dark"]) {
  @media (prefers-color-scheme: light) {
    --bg-app: #f5f7fb;
    --bg-surface: #ffffff;
    --bg-card: #ffffff;
    --bg-card-strong: #f1f4f9;
    --bg-input: #ffffff;
    --border-subtle: #e2e8f0;
    --border-strong: #cbd5e1;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
  }
}
:root[data-theme="light"] {
  --bg-app: #f5f7fb;
  --bg-surface: #ffffff;
  --bg-card: #ffffff;
  --bg-card-strong: #f1f4f9;
  --bg-input: #ffffff;
  --border-subtle: #e2e8f0;
  --border-strong: #cbd5e1;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
}
```

(The duplication between the media-query block and the explicit-override block is intentional and standard for this pattern — the media query handles "no stored preference yet," the attribute selector handles "user explicitly chose.")

Accent (`--accent-primary`, `--accent-primary-strong`, `--accent-secondary`) and status (`--status-good`, `--status-warning`, `--status-critical`, `--status-info`) tokens: audit each actual usage in `theme.css` (background vs. text vs. border role) before deciding whether it needs a light-mode variant — some (e.g. `--accent-primary` used as text/icon color) will read fine unchanged on a light background; others (e.g. `--status-critical-strong`, if used as a dark-red *background* tint) will need a lighter equivalent tint to stay legible. Verify actual WCAG AA contrast (4.5:1 body text, 3:1 large text/icons) for every text/background pairing in both themes — do not ship a pairing that fails this, in either theme.

## 3. Exact Allowed / New Files

```text
django_app/fmea_app/static/fmea_app/css/theme.css   # restructure tokens per Section 2, no other rule changes
django_app/fmea_app/static/fmea_app/js/app.js       # add theme-toggle logic (Section 1.3)
django_app/fmea_app/templates/fmea_app/_header.html # add the toggle control

tests/test_theme_toggle.py
```

## 4. Required Validation and Explicit Exclusions

- No regression to any existing dark-mode visual — the dark token block is copied verbatim, not rewritten.
- No new backend field, migration, or per-user preference storage of any kind.
- No layout/spacing/component-structure change — this is colors only.
- No new JS framework/library — vanilla JS in the existing `app.js`, matching every prior slice's tooling constraint.
- Toggle control must be reachable and functional identically on every page (it's in the shared header, not duplicated per-template) — do not add it to individual page templates.
- `localStorage` read/write must be wrapped defensively (private browsing / storage disabled shouldn't break the page — fall back to system preference silently if `localStorage` throws).

## 5. Required Tests

- `test_theme_toggle.py`: render a couple of representative pages (e.g. dashboard, a detail page) and assert the toggle control markup is present in each; assert `theme.css` contains both the dark `:root` block and the light override block (a simple content/regex check is sufficient — this is a template-rendering test suite, not a browser test, consistent with how existing GUI tests in this project work); assert no existing dark-mode-specific test (`test_gui_navigation_scope.py`, any dashboard-stat test) breaks.
- Full existing suite re-run with no unrelated assertion changes.

## 6. Commands to Run

```powershell
python -B manage.py check
python -B -m pytest
```

## 7. Acceptance Criteria

1. A toggle control, in the shared header, switches every page between light and dark instantly (no reload), and the choice persists across page navigation and browser restarts via `localStorage`.
2. A first-time visitor with no stored preference sees their OS `prefers-color-scheme` if set, otherwise dark (today's shipped default) — never light-by-default without either signal.
3. Every text/background pairing in both themes meets WCAG AA contrast.
4. No existing dark-mode visual regresses; no layout/spacing change anywhere.
5. No backend, model, or migration change appears in the diff.
6. Full test suite passes, `manage.py check` clean.
7. Mirrored into `open_fmea_training_set` and the training EXE rebuilt, per the standing discipline.

## 8. Explicit Exclusions (restated for emphasis)

Any per-user/account theme preference (server-side), any new page or nav entry, any layout/component redesign beyond color tokens, any new JS/CSS framework or library, any change to the dark theme's existing values.

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

# Codex Implementation Instruction — Shared Shell / Sidebar Nav Restyle (Slice A)

Status: Approved for implementation, 2026-09-04. This is Slice A from `Codex_Instruction_GUI_Mockup_Implementation_Preparation.md`'s own recommended order (that document remains reference material generally — see `OpenFMEA_DNA_CoreReference.md` Section 6 — but its Slice A specifically is now picked and scoped below). No backend, no models, no migrations. Purely a navigation/grouping restyle grounded directly in the current route map (`fmea_app/urls.py`, `fmea_review/urls.py`) and the canonical target sidebar structure already recorded in `OpenFMEA_DNA_CoreReference.md` Section 10.

Authority, in order: same chain as prior slices. This instruction was grounded by reading the actual current routes and `_sidebar.html` directly before writing any scope below — not derived from the mockups alone.

## 0. Decisions for this slice (read before touching anything)

The canonical nav-tree (DNA Section 10) has far more items than the app has real pages for. The standing rule — "no navigation for anything not built yet," restated after the withdrawn `Codex_Instruction_PlannedNavPlaceholders_Slice.md` — governs every decision below. None of these are open questions; they're decisions, stated so you don't have to re-derive them, but flag clearly in your report if the real routes have changed since this was written.

1. **Show a canonical group label only where it has at least one real page under it today.** Of the canonical tree's seven groups (HOME / WORKSPACE / CONTEXT / FMEA ANALYSIS / FMEA ELEMENTS / RISK / VALIDATION & CHANGE), only three have any real, routed page behind them right now: HOME (dashboard), WORKSPACE (FMEA Projects list), RISK (Risk Matrix). CONTEXT gets one real item too (see decision 3). FMEA ANALYSIS, FMEA ELEMENTS, and VALIDATION & CHANGE currently have **zero** real standalone pages — DFMEA/PFMEA/PM-FMEA dashboards don't exist, and Failure Modes/Effects/Causes/Preventive Controls/Detection Controls/Actions exist only as sections inside a specific FMEA's worksheet (`fmea_detail.html`), not as their own routes. Do not add these three group headers at all in this slice — an empty or single-fake-link group is exactly the dead-link problem the withdrawn placeholder instruction created.
2. **No standalone "FMEA Team" nav entry.** The canonical tree lists it as a WORKSPACE sibling of "FMEA Projects list," but there is no global, cross-project team route — team rosters are a tab on a specific project's detail page (`fmea:project_team`, reached via `fmea:project_detail`). A top-level "FMEA Team" link would have nowhere real to point (which project's team?). Leave it out of the sidebar; it stays reachable the way it already is, from within a project.
3. **The existing "Process Characteristics" page keeps its own name — do not relabel it "Process Control Characteristics."** The canonical tree's CONTEXT group uses the label "Process Control Characteristics," but per `OpenFMEA_DNA_CoreReference.md`'s Mockup 21 audit, that label refers to a materially richer, not-yet-approved concept (Control Type, Reaction Plan, Process Control Flow diagram — this is the Control Plan concept, explicitly gated by DNA rule 7). Today's real `ProcessCharacteristic` list page (`fmea:process_characteristic_list`) is a much simpler thing. Keep its current, accurate label ("Process Characteristics") under the CONTEXT group. Do not invent a "Process Control Characteristics" link — that would misrepresent what's actually built.
4. **"Import Sessions" and "Cause Influences" keep their own existing groups, unchanged position, restyled only for visual consistency.** Neither appears anywhere in the canonical nav-tree — a gap `OpenFMEA_DNA_CoreReference.md` Section 10 already flagged explicitly ("worth a direct check with the user whenever this area is next touched, rather than guessing either way"). Both are real, both are currently linked, and dropping either would remove working functionality with no replacement. Do not fold them into a canonical group that wasn't designed to hold them (e.g. don't move Cause Influences under a "FMEA ELEMENTS" group that doesn't exist per decision 1) — keep their current group headings (`Import & Review`, `Ishikawa / Cause Analysis`) exactly as they are today, after the canonical groups.
5. **No project/context selector in the header.** Several mockups show a global "current project" switcher. Nothing in the app today is scoped by a selected project — Risk Matrix is explicitly system-wide by prior decision (`Codex_Instruction_RiskMatrix_Slice.md`), and no other page reads a "current project" from anywhere. A selector that controls nothing real is the same dead-UI problem as a nav link with nowhere to go. Do not add one.
6. **This is a markup/grouping change, not a new visual system.** The existing `.nav-group` / `.nav-group-title` CSS classes are already used for "Import & Review" and "Ishikawa / Cause Analysis" — reuse them for the new HOME/WORKSPACE/CONTEXT/RISK headers rather than adding new CSS. If existing tokens genuinely can't express something needed (they should be sufficient), stop and report rather than freelancing new design.

## 1. Exact Scope

Rewrite `django_app/fmea_app/templates/fmea_app/_sidebar.html`'s `<nav class="sidebar-nav">` content to this exact structure (brand row and toggle button at the top stay unchanged):

```text
HOME
  Home                    -> {% url 'fmea:dashboard' %}

WORKSPACE
  FMEA Projects           -> {% url 'fmea:project_list' %}

CONTEXT
  Process Characteristics -> {% url 'fmea:process_characteristic_list' %}

RISK
  Risk Matrix             -> {% url 'fmea:risk_matrix' %}

Import & Review           (unchanged group heading and content)
  Import Sessions         -> {% url 'fmea_review:session_list' %}

Ishikawa / Cause Analysis (unchanged group heading and content)
  Cause Influences        -> {% url 'fmea:cause_influence_list' %}
```

Every link must be a real named URL (use `{% url %}`, never a hardcoded path or a `#` anchor) pointing to a route that already exists in `fmea_app/urls.py` or `fmea_review/urls.py` — all six above already do.

No other template changes. No CSS changes unless the existing `.nav-group`/`.nav-group-title` styling genuinely cannot render four new small group headers correctly (it already renders two) — if you find a real rendering problem, report it rather than expanding scope to fix it silently.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/templates/fmea_app/_sidebar.html   # nav grouping restyle only, per Section 1
tests/test_gui_navigation_scope.py                     # extend, do not replace — see Section 4
```

Nothing else. No `models.py`, `views.py`, `urls.py`, `forms.py`, or migration changes. No new templates.

## 3. Required Validation and Explicit Exclusions

- No new group header for FMEA ANALYSIS, FMEA ELEMENTS, or VALIDATION & CHANGE (Section 0.1) — confirm none of those three strings appear in the rendered sidebar.
- No "FMEA Team" top-level link (Section 0.2).
- No "Process Control Characteristics" label anywhere — the existing page keeps its "Process Characteristics" label (Section 0.3).
- "Import Sessions" and "Cause Influences" remain present, under their existing (unrenamed) group headings (Section 0.4).
- No project/context selector widget added to `_header.html` or anywhere else (Section 0.5).
- No `#` or dead-anchor `href` anywhere in `_sidebar.html` — every link resolves via `{% url %}` to a route already in `urlpatterns`.
- `manage.py check` and `manage.py makemigrations --check --dry-run` clean (should be trivially true — nothing here touches models).

## 4. Required Tests

Extend `tests/test_gui_navigation_scope.py`'s existing `GuiNavigationScopeTests` (do not delete or replace its current assertions — they're still correct and worth keeping):

- Add assertions that the response to `GET /` contains the four new group header strings: `"HOME"`, `"WORKSPACE"`, `"CONTEXT"`, `"RISK"` (exact casing as written in Section 1), alongside the existing `"Import & Review"`/`"Ishikawa / Cause Analysis"` group headings which should still be present unchanged.
- Add an assertion that `"FMEA ANALYSIS"`, `"FMEA ELEMENTS"`, `"VALIDATION & CHANGE"`, and `"FMEA Team"` do **not** appear anywhere in the sidebar response (extend the existing `unbuilt_label` loop/tuple rather than writing a separate check, if that fits the current test's shape).
- Add an assertion that `"Process Control Characteristics"` does not appear anywhere in the response, while `"Process Characteristics"` still does.
- Full existing suite re-run with no unrelated assertion changes (this slice shouldn't touch any other test's behavior — it's a template-only change to one shared partial).

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. Sidebar renders exactly the structure in Section 1 — six real links under four new canonical-named groups plus the two pre-existing groups, nothing more, nothing fewer.
2. Every sidebar link is a real, resolvable Django URL — no dead anchors, no placeholder hrefs.
3. `test_gui_navigation_scope.py`'s extended assertions pass, including the negative checks (no fake group headers, no "FMEA Team," no "Process Control Characteristics" mislabel).
4. No model, view, URL, or migration changes anywhere in the diff — `git status --short` after this slice should show only `_sidebar.html` and `tests/test_gui_navigation_scope.py`.
5. Full test suite passes, `manage.py check` clean, zero new migrations (there should be nothing to migrate).
6. Mirrored into `open_fmea_training_set` per the standing discipline.

## 7. Explicit Exclusions (restated for emphasis)

No backend changes of any kind. No new pages. No project/context selector. No relabeling "Process Characteristics" to "Process Control Characteristics." No "FMEA Team" top-level link. No FMEA ANALYSIS / FMEA ELEMENTS / VALIDATION & CHANGE group headers (they'd have nothing real underneath them yet). No dropping "Import Sessions" or "Cause Influences." No new CSS system — reuse existing `.nav-group`/`.nav-group-title` markup.

If you believe any of this needs to change to deliver a working slice — for example if a route named here has since changed — stop and report; do not silently expand or narrow scope.

# Codex Implementation Instruction — Planned/Disabled Nav Placeholders

**Status: WITHDRAWN, 2026-09-03 — do not implement.** This instruction was written on a misreading of the user's request. The user's "mark them there as selectable but disabled" meant: track the full list of planned-but-not-built GUI pages in the architecture **documentation** (a roadmap/index), not: build actual disabled widgets into the running application's sidebar. Nothing in this document should be implemented. The corrected, documentation-only version of this idea lives in `OpenFMEA_DNA_CoreReference.md` Section 10's new "GUI Roadmap Index" table. Kept here, unmodified below, only as an audit trail per the DNA's own rule 10 ("nothing deleted from `architecture/`, only superseded and indexed") — the original nav-visibility policy note in the DNA has been corrected accordingly; this file is superseded by that correction and by the roadmap table, not by a replacement instruction.

---

*(Original content below, preserved for the record — not authorized for implementation.)*

Status: ~~Approved for implementation~~ **WITHDRAWN, see notice above.** Grounded in the user's 2026-09-03 refinement of the GUI shell's nav-visibility rule, recorded in `OpenFMEA_DNA_CoreReference.md` Section 10 ("Nav-visibility policy, refined 2026-09-03"). Purely additive and presentational — no backend, no new entity, no migration.

Authority, in order: same chain as prior slices; additionally subordinate to `Codex_Instruction_GUI_DesignSystem_AppShell_Slice.md` (owns the sidebar template and visual language this slice extends) and the DNA's refined nav-visibility policy (design authority for this slice).

## 0. What changed, precisely — read before starting

The original rule, enforced by `test_gui_navigation_scope.py`, was: a nav label for a feature with no real backend must not appear in the rendered sidebar at all. **The user has refined this, not removed it.** Not-yet-built features may now appear in the sidebar as **visibly disabled placeholders** — greyed out, unmistakably non-interactive, communicating the app's eventual shape without ever implying the feature works. The underlying safety property is unchanged: nothing a user can click may silently do nothing or show fabricated data. What's new is that the label may be *visible but inert*, where before it had to be *entirely absent*.

This instruction adds **zero new views, URLs, or data**. It is markup/CSS plus one test rewrite.

## 1. Exact Scope

1. A reusable "disabled nav entry" pattern in `_sidebar.html` / `theme.css`: rendered as non-focusable, non-navigating (no `<a href>` to a real route — either a `<span>`, or an `<a>` with no `href`/`href="#"` plus `aria-disabled="true"` and `tabindex="-1"`), visibly greyed (a muted text color token, not the active/hover states used by real nav items), with a small inline label — "Planned" or "Not yet built" (exact wording your call, keep it short and honest, not "Coming soon" marketing language) — so a user hovering/reading it understands why it's inert rather than assuming it's broken.
2. Populate the sidebar with disabled placeholders for the items listed in Section 2 below, grouped under the existing real groups (`FMEA WORKSPACE`, `CONTEXT (from Open-EQMS)`, etc.) or new group headers matching the already-real groups' style — **exact grouping and exact label wording are illustrative, not final**; they come from mockups that have already shown inconsistent grouping/labels across each other (see DNA Section 10, Mockup 16's note) and are cheap to relabel later since there's no logic behind them.
3. `test_gui_navigation_scope.py`: rewritten so that, for every label in Section 2, it asserts the label **is present** in the rendered HTML **and** is non-interactive (no working `href` to any resolvable URL, or an explicit disabled/aria-disabled marker — assert whichever mechanism you implement). It must continue to assert every already-real nav item (Home, FMEA Projects, Process Characteristics, Import Sessions, Cause Influences, Risk Matrix, and anything else genuinely built) renders as a normal, working link.

Nothing beyond this list. No new view, URL, template beyond `_sidebar.html`, model, or migration. No functional change to any existing page.

## 2. Exact List of Disabled Placeholder Labels

Grouped as most recently shown, exact wording adjustable:

- **FMEA WORKSPACE:** FMEA Team
- **CONTEXT (from Open-EQMS):** System / Product / Process, System Characteristics Base, Characteristics Flow / Diagram
- **FMEA PROJECT (type-scoped pages):** DFMEA, PFMEA, System FMEA, Preventive FMEA (PM-FMEA)
- **FMEA ELEMENTS (standalone pages — distinct from the worksheet sections already built/in-flight inside `fmea_detail.html`):** Functions, Failure Modes, Effects, Causes, Prevention Controls, Detection Controls, Actions
- **VALIDATION & CHANGE:** Evidence & Tests, Validation Trajectory, Change Impact
- **ANALYSIS TOOLS:** AP / Detection, XDA Investigations, 8D Problem Solving, 5 Why Analysis, FTA (Fault Tree), RCA Analysis

**Explicitly excluded from this list — do not add a placeholder for these:**
- **"Ishikawa Diagram"** — ambiguous whether this duplicates the already-real "Cause Influences" nav item or is a separate concept; do not guess. Flagged in DNA Section 10 (Mockup 16) as needing the user's clarification first.
- **"Risk Trajectory & Propagation"** — per the user, this is a *tab inside the already-real Risk Matrix page*, not a separate nav item; nothing to add here (a disabled tab inside an existing page is a different, smaller pattern — out of scope for this instruction; raise separately if wanted).
- Anything already real and working (Home, FMEA Projects, Process Flow, Process Characteristics, Import Sessions, Cause Influences, Risk Matrix) — these stay exactly as they are, fully functional, never disabled.

## 3. Exact Allowed / New Files

```text
django_app/fmea_app/templates/fmea_app/_sidebar.html   # add disabled-entry markup, Section 2's list
django_app/fmea_app/static/fmea_app/css/theme.css      # additive: disabled-nav-entry styling only

tests/test_gui_navigation_scope.py                     # rewritten per Section 1.3
```

## 4. Required Validation and Explicit Exclusions

- A disabled placeholder must not resolve to any real URL — clicking it (or a direct GET to whatever `href` it might carry, if any) must not 200 into a real page; prefer no `href` at all over a dead link.
- No JavaScript click-handler that does anything (no fake modal, no "feature coming soon" popup) — the visual disabled state is the entire interaction; simplest is safest here, matching every prior slice's "no JS framework needed" constraint.
- No change to any already-real nav item's markup, route, or test coverage beyond what's needed to keep asserting it still works.
- No backend change of any kind.

## 5. Required Tests

- `test_gui_navigation_scope.py`, rewritten:
  - For each label in Section 2: assert present in rendered HTML; assert non-interactive (pick one concrete mechanism — e.g. absence of a resolvable `href`, or an `aria-disabled`/disabled CSS class — and assert it consistently for all of them).
  - For each already-real nav item: assert present **and** fully functional (a working link to its real URL, as today's test already does).
  - Explicitly assert "Ishikawa Diagram" and "Risk Trajectory & Propagation" are **not** added as standalone sidebar entries by this slice (guards against scope creep on the two excluded items).
- Full existing suite re-run with no unrelated assertion changes.

## 6. Commands to Run

```powershell
python -B manage.py check
python -B -m pytest
```

## 7. Acceptance Criteria

1. Every label in Section 2 appears in the sidebar, visibly disabled, in a state a user would clearly read as "not yet available" rather than "broken."
2. No already-real nav item's behavior changes.
3. "Ishikawa Diagram" and "Risk Trajectory & Propagation" do not appear as new standalone sidebar entries.
4. `test_gui_navigation_scope.py` passes with the rewritten assertions described in Section 5.
5. No backend/model/migration change appears in the diff.
6. Full test suite passes, `manage.py check` clean.
7. Mirrored into `open_fmea_training_set` and the training EXE rebuilt, per the standing discipline.

## 8. Explicit Exclusions (restated for emphasis)

Any working route, view, or data behind a disabled placeholder; any JS interaction beyond the static disabled visual state; a placeholder for "Ishikawa Diagram" or "Risk Trajectory & Propagation" (excluded, see Section 2); any change to an already-real nav item's function; any backend, model, or migration change.

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

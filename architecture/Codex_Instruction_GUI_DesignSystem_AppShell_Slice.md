# Codex Implementation Instruction — GUI Design System + App Shell (Slice: GUI-Shell-1)

Status: Approved for implementation. Direction confirmed by the user against a reference dashboard mockup (dark theme, sidebar navigation, card-based dashboard) with two explicit decisions: (1) restyle the existing Django server-rendered app — no separate SPA, no new API layer; (2) restyle only what is real today and grow the navigation incrementally — no placeholder/dead-end UI for modules that don't exist on the backend yet.

Authority, in order: same chain as prior slices; additionally subordinate to `OpenFMEA_DNA_CoreReference.md` (Section 2, rule 8 — no feature ahead of approval — applies here to navigation entries as much as to backend entities: a sidebar item for a module that doesn't exist is exactly the kind of premature surface that rule already prohibits, now made explicit for GUI work too).

## 0. What the reference mockup showed, and what this slice does and does not do with it

The user supplied a reference dashboard screenshot: dark theme, a left sidebar grouped into sections (FMEA Workspace, FMEA Data, Analysis, Integration), a header with a project switcher/search/notifications/AI-Assistant button, and a home dashboard with stat cards, a risk-matrix heatmap, a validation-trajectory stepper, a top-risk-items table, recent-projects/recent-activity/knowledge panels.

This slice adopts the **visual design system** (color palette, typography, spacing, card/table/badge patterns, sidebar+header shell structure) from that reference. It does **not** adopt its full navigation — most of that sidebar (Risk Matrix, AP/Detection, Validation Trajectory, Evidence & Tests, Change Impact, XDA Investigations, CAPA, Control Plans, SPC/ITRA-DT, Documents & Links, an AI Assistant entry point, a Knowledge & References panel with a Lessons Learned database) has no backend today and several of those (Lessons Learned, coverage/validation metrics, Control Plans) are explicitly still-deferred per the DNA reference's Section 6. Building navigation chrome for them now would be exactly the "looks finished, does nothing" outcome the user explicitly ruled out. **Do not add a sidebar entry, dashboard card, or route for anything not listed in Section 2 below**, no matter how directly it maps to something in the screenshot. If you think a section is obviously safe to add as a stub, stop and report — do not add it.

## 1. Exact Scope

1. A design-tokens stylesheet (colors, spacing, radii, shadows, typography) capturing the reference's dark visual language, vendored as a static file — no CDN, no build-time network dependency at runtime (this app ships as an offline desktop EXE; see Section 4).
2. An app shell: a new `base.html` with a collapsible left sidebar and a top header, replacing the current minimal `base.html`.
3. A home dashboard (`/`) showing only real, queried numbers — no fabricated widgets.
4. Shared template partials/components (card, stat tile, status badge, data table shell) used to restyle every existing functional page without changing its behavior.
5. Restyle, in place, every currently-working page: FMEA list/detail (existing Phase B views), the ingestion review queue (`session_list`, `session_detail`, `candidate_detail`), row-group review (`row_group_detail`), and the Ishikawa/cause-influence pages (`cause_influence_list`, `cause_influence_detail`, `cause_influence_form`, `ishikawa_board`).

Nothing beyond this list. No new backend entity, no new URL beyond what Section 3 requires for the dashboard, no JS framework beyond what Section 4 specifies.

## 2. The navigation this slice builds — exact list, nothing added

```text
Home                          -> dashboard (Section 3)
FMEA Projects                 -> existing FMEA list/detail views (Phase B)
Import & Review
    Import Sessions           -> fmea_review: session_list / session_detail / candidate_detail
    Row Groups                -> linked from session_detail, not a separate top-level page (matches today's flow)
Ishikawa / Cause Analysis
    Cause Influences           -> fmea_app: cause_influence_list / detail / new
    (Ishikawa board is reached from a FailureMode, not a standalone nav item — matches today's flow: no FailureMode-picker page exists, so do not invent one just to make this a top-level nav item)
```

No "FMEA Workspace / FMEA Data / Analysis / Integration" section grouping from the mockup — that grouping implies modules that don't exist. Use plain, flat groups matching what's actually above. No search box (non-functional), no notifications bell (nothing produces notifications), no "AI Assistant" header button (the AI boundary in this project is "advisory suggestion embedded in a specific review flow," never a general chat entry point — adding one would misrepresent that boundary to every user who opens the app), no project switcher (single-workspace app today).

## 3. Home dashboard — real data only

Query real numbers, each from a specific, cited source — do not invent a metric that would require building new aggregation logic (that's out of scope; if a stat needs a query more complex than a `count()`/`filter().count()`/simple `annotate()`, cut it from this slice and report why rather than building new aggregation logic to support it):

- **FMEA Projects** — `models.FMEA.objects.count()`.
- **Pending Review** — `ImportCandidateRecord.objects.filter(review_status="unreviewed").count()` + `FmeaRowGroup.objects.filter(review_status="unreviewed").count()`, shown as one combined stat with both numbers visible (e.g. "12 candidates, 3 rows"), not silently summed into one misleading integer.
- **Cause Influences by status** — a small breakdown (not a heatmap): count of `CauseInfluence` grouped by `status`, rendered as a compact stacked bar or a simple list of status→count pairs. Use the existing `CauseInfluenceStatus` enum values as labels.
- **Recent Activity** — the 10 most recent review actions across `ImportCandidateRecord.reviewed_at`, `FmeaRowGroup.reviewed_at`, and `CauseInfluence.reviewed_at` (a simple merged-and-sorted query, not a new activity-log table), each row showing what happened (accepted/rejected/transitioned, to what) and when.

No risk-matrix heatmap (no RPN/severity-occurrence aggregation exists to back it), no validation-trajectory stepper (no such concept is built), no "Actions Overdue"/"Reviews Due" countdown (no due-date field exists on anything reviewable), no "Knowledge & References" panel (no document-library entity exists). If, while building this, you find a stat card in the mockup maps cleanly to something that already exists in the domain model but isn't listed above, report it rather than adding it silently — the omission may be deliberate scope discipline, not an oversight.

## 4. Design tokens and static assets

Approximate palette read from the reference (treat as a starting point — exact hex values are a matter of taste, not a hard requirement; do not spend implementation time pixel-matching):

```css
--bg-app: #0f1420;          /* sidebar / outermost background */
--bg-surface: #141a26;      /* main content background */
--bg-card: #1a2030;         /* card / panel surface */
--border-subtle: #262d3d;
--text-primary: #e8eaf0;
--text-secondary: #9aa3b5;
--accent-primary: #2f6fed;  /* active nav item, primary buttons, links */
--status-good: #22c55e;
--status-warning: #f5a623;
--status-critical: #ef4444;
--status-info: #6366f1;
```

Typography: system font stack (`-apple-system, "Segoe UI", Roboto, sans-serif` — no webfont download, this must work offline). Spacing/radius: an 4/8/12/16/24px spacing scale, 8px card corner radius, subtle 1px borders rather than heavy shadows (matches the reference's flat card style).

**Tooling constraint — this ships as an offline desktop EXE (per `packaging/`), so nothing in the runtime app may require network access or Node.js at runtime:**

- If you use Tailwind CSS, generate the compiled CSS with the Tailwind **standalone CLI binary** during development and commit the resulting static file (`django_app/fmea_app/static/fmea_app/css/theme.css` or similar) — do not reference `cdn.tailwindcss.com` or any hosted stylesheet, and do not add a Node/npm build step to `packaging/build_exe.ps1` or any runtime path. If hand-written CSS achieves the same result with less new tooling, that is equally acceptable — your call, report which you chose and why.
- JavaScript: vanilla JS only for this slice (sidebar collapse/expand, active-link highlighting). Do not add htmx or Alpine.js in this slice — the mockup's interactivity (collapsible sidebar, hover states) doesn't need them, and every existing view's request/response behavior (full-page POST-redirect-GET, exactly as today) must not change, since the existing test suite asserts against exact response behavior. If you find a specific, narrow case where htmx would clearly help without touching any tested behavior, stop and report it as a follow-up rather than adding the dependency inline here.
- No charting library in this slice — nothing here needs a chart (the Cause-Influence status breakdown is a simple bar/list, buildable in plain CSS).

## 5. Exact Allowed / New Files

```text
django_app/fmea_app/static/fmea_app/css/theme.css     # design tokens + component styles
django_app/fmea_app/static/fmea_app/js/app.js          # vanilla JS: sidebar collapse, active-link state

django_app/fmea_app/templates/fmea_app/
    base.html                       # rewritten: sidebar + header shell
    _sidebar.html                   # partial, the nav list from Section 2
    _header.html                    # partial
    _components/
        _card.html
        _stat_tile.html
        _status_badge.html
    dashboard.html                  # rewritten: real stats from Section 3

django_app/fmea_app/views.py        # add: dashboard view computing Section 3's real queries
django_app/fmea_app/urls.py         # dashboard route, if not already present at "/"

# Restyled in place (template markup/classes only, no behavior change):
django_app/fmea_app/templates/fmea_app/fmea_detail.html
django_app/fmea_review/templates/fmea_review/session_list.html
django_app/fmea_review/templates/fmea_review/session_detail.html
django_app/fmea_review/templates/fmea_review/candidate_detail.html
django_app/fmea_review/templates/fmea_review/row_group_detail.html
django_app/fmea_app/templates/fmea_app/cause_influence_list.html
django_app/fmea_app/templates/fmea_app/cause_influence_detail.html
django_app/fmea_app/templates/fmea_app/cause_influence_form.html
django_app/fmea_app/templates/fmea_app/ishikawa_board.html

django_app/open_fmea_project/settings.py   # STATICFILES_DIRS/STATIC_URL only if not already correctly configured — check first, most Phase B Django setups already have this right
tests/test_dashboard_view.py
tests/test_gui_navigation_scope.py          # the "no dead-end nav" lock-in test, Section 7
```

Do not touch `fmea_ingestion/`, `fmea_ai/`, `fmea_importexport/`, or any migration — this is a presentation-layer-only slice.

## 6. Required Validation and Explicit Exclusions

- **Every existing test must keep passing with zero edits to its assertions.** Templates change markup/classes freely, but any literal text a test asserts on with `assertContains` (status messages like `"Cause influence status updated."`, `"Backward CauseInfluence transition is not allowed"`, category names, entity names like `"Seal nicked"`, etc.) must still appear verbatim in the rendered output. If restyling would naturally reword one of these strings, don't — leave the string as-is even if it reads slightly awkwardly in the new design; consistency with the test suite wins over copy polish in this slice.
- **No sidebar entry, dashboard card, or route for anything outside Section 2/3's exact lists** — this is the specific, tooling-enforced version of Section 0's instruction (Section 7's test locks this in).
- **No AI Assistant UI surface of any kind** — no chat button, no "Ask AI" affordance anywhere in the shell. This project's AI boundary is "an advisory suggestion embedded in one specific review flow," and a general assistant entry point in the header would misrepresent that to every user, regardless of whether it's wired to anything real.
- **No new domain queries beyond simple counts/filters** — Section 3's explicit constraint, restated.
- Offline-safe: no `<link>`/`<script>` tag pointing at any external host (fonts, CDNs, icon libraries) anywhere in the restyled templates.

## 7. Required Tests

- `test_dashboard_view.py`: seed a small known set of FMEAs/candidates/row-groups/cause-influences, hit `/`, assert the rendered numbers match the real counts exactly (not just "a number appears" — the actual computed value).
- `test_gui_navigation_scope.py`: render the shell (any authenticated page) and assert specific strings from the mockup's *unbuilt* sections are **absent** — e.g. `assertNotContains(response, "Risk Matrix")`, `"Validation Trajectory"`, `"CAPA"`, `"Control Plans"`, `"AI Assistant"`. This test exists specifically to catch scope creep in this slice or a future one — do not weaken or remove it later without a corresponding DNA/README update explaining why a section became real.
- Full existing suite re-run with no assertion changes, per Section 6.

## 8. Commands to Run

```powershell
python -B manage.py check
python -B manage.py collectstatic --noinput --dry-run
python -B -m pytest
```

## 9. Acceptance Criteria

1. Every page listed in Section 1.5 renders in the new visual language with unchanged behavior and unchanged test assertions.
2. The dashboard shows only the four real, correctly-computed stats from Section 3 — no fabricated widgets.
3. The sidebar contains exactly the items in Section 2 — verified by `test_gui_navigation_scope.py` asserting the absence of every unbuilt section's label.
4. No external network reference (font/CDN/icon-host) exists anywhere in the new templates or CSS.
5. No new npm/Node build step is added to `packaging/build_exe.ps1`; if Tailwind's standalone CLI was used, only its compiled output is committed, not the tool itself.
6. Full test suite passes, `manage.py check` clean, no migration created.
7. Mirrored into `open_fmea_training_set` and the training EXE rebuilt, smoke-tested, with the same clean-run report discipline as every prior slice.

## 10. Explicit Exclusions (restated for emphasis)

Risk Matrix (heatmap or otherwise), Validation Trajectory / validation coverage of any kind, AP/Detection module, Evidence & Tests module, Change Impact module, XDA Investigations, CAPA, Control Plans, SPC/ITRA-DT, Documents & Links, Lessons Learned / Knowledge & References, any AI Assistant chat surface, project switcher, functional search, notifications, htmx, Alpine.js, any charting library, any webfont or external asset host, any new domain aggregation query beyond simple counts/filters, any new backend entity or migration.

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.

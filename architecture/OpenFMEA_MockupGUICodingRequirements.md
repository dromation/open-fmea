# Open-FMEA — Per-Mockup GUI Coding Requirements (all 23 reference mockups)

Status: **Specification/documentation only, 2026-09-04. Not an implementation instruction or authorization to build anything.** Written per explicit user direction: "each mockup picture/screen: classify what features and content is there and what widgets must be done for full wireframe of each screen. for each mockup create requirements for coding based on this wireframe, to code GUI."

This is the next layer down from `OpenFMEA_MockupSpecifications_GUIWireframeArchitecture.md` (the full widget/wireframe/architecture spec for all 23 mockups). This document turns that into build-ready GUI requirements: what the screen does (features), a complete widget checklist organized by page region, and concrete coding requirements — route, template, layout using this codebase's real CSS/JS vocabulary, and per-widget data binding (real field, computed aggregate, or placeholder pending new backend work).

**A correction is baked into this document's methodology.** An earlier pass wrongly declared Mockup 21 ("Process Control Characteristics") to be "the Control Plan concept, specially gated by DNA rule 7, requiring an approval-workflow state machine" — reading a rule aimed at silent/automated modification as if it blocked ordinary human-driven CRUD forms. The user caught this. Every section below states plainly what's on screen and what it would take to build, without declaring "this IS concept X" or inventing governance requirements — where a field or entity doesn't exist yet, that's stated as a plain fact (needs a new field/entity), not as a rule invocation.

## Methodology

Built from two grounded inputs per mockup: the detailed spec document (widget inventory + wireframe description, already independently verified against the source images) and a fresh re-read of the source image itself. GUI coding requirements are grounded in this codebase's **actual** CSS classes and JS behavior (confirmed directly from `theme.css` and `app.js`, not assumed) — every widget is mapped to a real, reusable class where one fits, and every genuinely new pattern (tabs, a detail/inspector panel, any chart, a graph, a diagram, file upload) is called out explicitly rather than silently assumed to already exist.

## Real GUI component vocabulary used throughout (confirmed from source)

**CSS** (`django_app/fmea_app/static/fmea_app/css/theme.css`): layout — `.grid`, `.span-3/4/5/6/7/8/12`, `.split`, `.stack`, `.section-block`, `.section-gap`; containers — `.panel`, `.panel-heading`, `.content-shell`, `.app-shell`, `.workspace`; tables — `.table-shell` (wraps a plain `<table>`), `.cell-item`, `.cell-list`, `.cell-detail`, `.attribute-table`; KPI — `.stat-tile`, `.stat-label`, `.stat-value`, `.stat-detail`; status/badges — `.status` + a fixed set of `.status-*` modifiers; risk-specific — `.risk-band-*`, `.risk-critical/high/low/medium`, `.risk-matrix-*` (the built Risk Matrix's own heat-grid system); stepper — `.process-step`, `.process-steps`, `.process-step-index` (a real link-based step-picker — the closest thing to a tab strip, but it navigates rather than swapping panel content); forms — `.form-block`, `.field-grid`, `.button`, `.button-row`, `.compact`, `.toolbar`, `.inline-actions`, `.icon-button`; sidebar — `.sidebar`, `.sidebar-nav`, `.nav-group`, `.nav-group-title`, `.nav-link`; worksheet — `.worksheet`, `.worksheet-wrap`.

**JS** (`app.js`) — exactly three behaviors exist anywhere in this app: dark/light theme toggle, sidebar collapse toggle, active-nav-link highlighting. No AJAX/fetch, no client-side filtering, no tabs, no chart/graph init, no modal/drawer, no drag-and-drop. Chart.js was just decided as the charting library (vendored locally, no CDN) but is wired into zero pages today — it covers line/bar/donut only, not force-directed graphs, Sankey, or Gantt.

**Filtering**: every filter in this app is a server-side `GET` form + `<select>` + full page reload. No client-side/AJAX filtering exists anywhere.

**Naming convention**: routes `fmea:<snake_case>`; templates `django_app/fmea_app/templates/fmea_app/<snake_case_name>.html`.

## Quick-reference index — recurring new patterns needed across the 23 screens

| New pattern | First needed by | Also needed by |
|---|---|---|
| Right-docked detail/inspector panel (persistent, populates on row click) | #10 Evidence & Tests | #15, #16, #19, #20, #21, #22, #23 |
| Tab strip that swaps panel content in place | #8 System Characteristics Base | #10, #11, #12, #16, #21, #22, #23 |
| Chart.js line/bar/donut (first real usage anywhere in the app) | #21's donuts (or whichever page ships first) | #1, #4, #8, #11, #12, #13, #14, #17, #19, #22 |
| Force-directed relationship graph (no Chart.js coverage, needs its own library) | #9 Characteristics Flow/Diagram | — |
| Sankey flow diagram (no Chart.js coverage) | #18 Effects | — |
| Gantt-style timeline (no Chart.js coverage) | #22 Actions | — |
| File upload / attachment chips (no storage exists) | #10 Evidence & Tests | #15, #19, #20, #22 |
| Static process/flow diagram (plain HTML/CSS, no library) | #21 Process Control Flow | #17 (propagation chain), #18 (effect chain) |
| Hierarchy tree widget | #7 System/Product/Process | #8 |

---

## Mockup 01 — Base App Shell: GUI Coding Requirements

### 1. Features & Content

1. App-wide chrome: collapsible sidebar navigation, top bar with project switcher, global search box, notification bell, help, and user avatar.
2. Landing/home dashboard greeting the signed-in user with a welcome message and a row of quick-action buttons (new FMEA, open project, import, reports, templates, AI assistant).
3. At-a-glance KPI summary across 5 stat cards (project count, active analyses, high-risk item count, overdue actions, reviews due).
4. Visual risk-overview heat-map summarizing every FailureMode's Severity x Occurrence distribution across all FMEAs.
5. A lifecycle/validation-progress overview (stepper + two coverage bars) for the current project's DFMEA/PFMEA.
6. A ranked table of the top highest-RPN failure modes across all FMEAs, linking out to a full list.
7. A "recent projects" list showing the most recently touched FMEA projects with status and recency.
8. A cross-entity "recent activity" feed of recent changes across the system.
9. A "knowledge & references" list of reference documents/libraries.
10. A persistent footer status bar showing environment/user/role/workspace/system-health info.

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Logo lockup: icon mark + "Open FMEA" wordmark + "Open-EQMS Family" subtitle — repeats existing `.sidebar-brand-row` pattern (`_sidebar.html`), unchanged.
- Hamburger/menu icon toggling sidebar collapse — repeats existing `.icon-button.mobile-sidebar-toggle` (`data-sidebar-toggle`), already wired in `app.js`.
- Page title "Home" — repeats existing `.topbar-title` block (`base.html` `{% block topbar_title %}`).
- Project selector dropdown "Project: New Headlamp X1" (chevron) — **new pattern**, no dropdown/select-style widget exists in the topbar today.
- Search box "Search (Ctrl+K)" with magnifying-glass icon — **new pattern**, no search input exists anywhere in the app.
- Bell/notification icon with red badge count "8" — **new pattern**, no notification affordance exists.
- "?" help icon — **new pattern** (simple static link/icon, trivial).
- Circular user avatar "JD" — **new pattern**, no avatar/initials-badge component exists (`.icon-button` exists for icon-only buttons but not an avatar chip).
- Theme toggle button — repeats existing `.icon-button.theme-toggle` (`_header.html`), already wired.
- "Offline-ready" environment pill — repeats existing `.environment-pill` (`_header.html`), unchanged.

**Sidebar**
- Grouped nav: "FMEA WORKSPACE" (Home active, FMEA Projects, DFMEA, PFMEA, System FMEA), "FMEA DATA" (Functions, Requirements, Characteristics, Failure Modes, Causes, Controls, Actions), "ANALYSIS" (AP/Detection, Risk Matrix, Validation Trajectory, Evidence & Tests, Change Impact), "INTEGRATION" (XDA Investigations, CAPA, Control Plans, SPC/ITRA-DT, Documents & Links) — repeats the existing `.nav-group` + `.nav-group-title` + `.nav-link` + `.nav-dot` pattern already used for "Import & Review" and "Ishikawa / Cause Analysis" in the real `_sidebar.html`; most of the *links themselves* are new (today's sidebar has only Home, FMEA Projects, Process Characteristics, Risk Matrix, Import Sessions, Cause Influences — a much smaller set than this mockup depicts).
- Active item ("Home") shown as filled blue pill — repeats existing `.nav-link.is-active` styling, already driven automatically by `app.js`'s pathname-matching (`data-nav-link`).
- Divider + "Settings" + "Collapse Menu" row — Collapse repeats existing `.sidebar-toggle` behavior; "Settings" link is new (no settings page exists).
- Sidebar footer "Version 1.0.0 • Open-EQMS" — **new pattern**, `_sidebar.html` has no footer region today.

**Page header content area**
- Heading "Welcome back, Janez!" + subtext — **new pattern** (a personalized greeting; today's dashboard heading is a static "FMEA Workspace" title, not a per-user greeting).
- Button row: "+ New FMEA" (primary), "Open Project", "Import", "Reports", "Templates", "AI Assistant" — repeats the existing `.toolbar` > `.button-row` pattern (seen in `dashboard.html`, `project_list.html`, `risk_matrix.html`); most individual buttons are new destinations, "Import" already exists as a working link (`fmea_review:session_list`).

**KPI row (5 stat cards)**
- "FMEA Projects" 12 / "Active projects" / "View all projects →" — repeats existing `_components/_stat_tile.html` include pattern.
- "Active Analyses" 7 / "In progress" / "View all analyses →" — same repeat pattern.
- "High Risk Items" 23 / "5 new since last review" / "View high risks →" — repeats the existing anchor-wrapped `stat-tile` pattern already used for the High Risk Items tile in `dashboard.html` (links to `fmea:risk_matrix`).
- "Actions Overdue" 8 / "2 critical • 6 normal" / "Go to actions →" — repeats stat-tile pattern; content (dual sub-count) is new.
- "Reviews Due" 4 / "Next within 7 days" / "View reviews →" — repeats stat-tile pattern.
- Note: a true 5-across equal-width row does not divide evenly under the existing 12-column `span-3/4/5/6/7/8/12` grid system (5 x span-3 = 15/12, overflowing) — see Section 3.

**Analytics row (3 columns)**
- "Risk Overview (All Projects)" card: 5x5 Severity(1-5) x Occurrence(5-1) grid with per-cell counts and color, legend (green/yellow/red 3-tier), link "Open Risk Matrix →" — repeats the existing `.risk-matrix-grid` / `.risk-matrix-cell` / `.risk-band-*` / `.risk-matrix-axis-label` / `.risk-matrix-corner` / `.risk-matrix-legend` markup already built for `risk_matrix.html`, condensed into a card. Note: this card's legend shows only 3 tiers (Low/Medium/High) while the real `risk_matrix.html` legend uses 4 (`.status-low/medium/high/very_high`) — a presentation inconsistency to reconcile when built, not a new-widget concern.
- "Validation Trajectory Overview" card: 7-node horizontal stepper with per-node status icon (check/outline/filled, colored), two labeled progress bars (DFMEA 78% green, PFMEA 62% blue), 5-item color legend, link "Open Validation Trajectory →" — **new pattern**. The existing `.process-steps`/`.process-step` nav is a plain link-list with no per-node status icon/color, so it does not cover this; the progress-bar itself does repeat the existing `<progress class="status-progress">` pattern from `dashboard.html`'s "Cause Influences by Status" section.
- "Top High Risk Items" table, link "View all →": columns Item (code + description stacked) | Project | RPN | Risk (pill) — repeats the existing `.table-shell` > `<table>` pattern plus the existing `.cell-item`/`.cell-detail` stacked-text-in-cell pattern (seen in `project_detail.html`, `fmea_detail.html`) for the Item column, and the existing `.status.status-high`/`.status-medium` badge pattern for the Risk pill.

**Bottom row (3 columns)**
- "Recent Projects" card, link "View all →": rows with leading colored icon, project name, FMEA-type sub-label, status pill, "Updated X ago" — repeats existing `.related-list` + `.cell-item`/`.cell-detail` pattern (`project_detail.html`) plus the existing `.status.status-*` badge pattern for the status pill; the **leading colored icon per row** is a new element (no icon-badge component exists yet).
- "Recent Activity" card, link "View all →": feed rows with icon, bold description, gray sub-line, relative timestamp — repeats the same `.related-list`-style layout used for "Recent Activity" in the real `dashboard.html` (`<ol class="activity-list"><li class="activity-item">`), which already exists as a component; the leading per-row icon is new.
- "Knowledge & References" card, link "View all →": rows with icon, name, type sub-label, "Updated X ago" — same `.related-list`/`activity-item`-style repeat; content and entity are entirely new.

**Footer status bar**
- "Database: OpenEQMS_Local", "User: ... (Quality Engineer)", "Role: Project Owner", "Workspace: Global", "Notifications 8", "System Status" (green dot) — **new pattern**; `base.html` has no footer element at all today. Needs a new `<footer>` region added to the shared base template plus new CSS (proposed `.statusbar` / `.statusbar-item`).

### 3. GUI Coding Requirements

**Route + template**: This screen already exists in the codebase as the Home dashboard — route `fmea:dashboard` (`path("", views.dashboard, name="dashboard")`), template `django_app/fmea_app/templates/fmea_app/dashboard.html`. This mockup is a redesign/expansion of that existing page, not a new route. Any coding work here means extending `dashboard.html` and its `views.dashboard` context, not creating a new URL.

**Layout structure**:
- `base.html`'s `.app-shell` / `.workspace` / `.topbar` / `.content-shell` skeleton stays as-is; the header additions (project selector, search, bell, help, avatar) go into `_header.html` alongside the existing `.environment-pill` and `.theme-toggle`.
- Sidebar stays `_sidebar.html`'s `.sidebar` > `.sidebar-nav` > repeated `.nav-group` (with `.nav-group-title`) > `.nav-link` (each with `data-nav-link` for the existing active-highlight JS) structure — just with more groups/links added.
- Page-header row: `.toolbar` > `<h1>`/`<p class="muted">` + `.button-row` of `.button`/`.button.primary`.
- KPI row: `.grid.section-block` containing five `{% include "fmea_app/_components/_stat_tile.html" %}` calls (or the anchor-wrapped `stat-tile` markup where the whole card is a link, as already used for High Risk Items). Because 5 does not divide the 12-column grid evenly, either (a) wrap as two rows (3 + 2) using `span-4` tiles, or (b) add a new flex-based row variant (proposed `.stat-row` with `flex: 1 1 0` children) sized independently of the `span-N` grid system.
- Analytics row: `.grid` with three `.panel.span-4` cards, reusing `.risk-matrix-grid`/`.risk-matrix-cell`/`.risk-band-*` inside the first card exactly as `risk_matrix.html` already renders them.
- Bottom row: `.grid` with three `.panel.span-4` cards, each using `.related-list`/`.cell-item`/`.cell-detail` for its rows.
- Footer status bar: new `<footer>` block added once in `base.html` (affects every page, not just this one), styled with new proposed classes `.statusbar`/`.statusbar-item`.

**New CSS/JS needed** (no existing equivalent):
- Project-selector dropdown, search-as-you-type box, notification bell+badge, avatar badge, help popover — none exist; each needs new markup and minimal new CSS. The notification bell and project selector, if they open a panel, need a small new vanilla-JS open/close toggle in `app.js` following the same `[data-*-toggle]` + click-listener pattern already used for `data-theme-toggle`/`data-sidebar-toggle` (no framework, no AJAX).
- Validation Trajectory stepper with per-node status coloring: new component, proposed `.trajectory-stepper` / `.trajectory-node` with status modifiers (e.g. `.status-completed`, `.status-planned`, `.status-not_started`) extending the existing `.status-*` badge-coloring convention rather than inventing a separate color system.
- Leading colored icon badges on list rows (Recent Projects/Recent Activity/Knowledge & References): new small icon-badge component, proposed `.row-icon` with color modifiers.
- Reports/Templates dropdown-chevron buttons: new small popover/menu, same minimal-JS toggle pattern as above.
- Global search: this app has no search index or backend anywhere; the box itself can be built as a static input, but making it functional is out of scope for GUI structure alone.

**Per-widget data binding**:
- "FMEA Projects" stat (12): (b) computed aggregate — `FMEAProject.objects.filter(status=<active>).count()`.
- "Active Analyses" stat (7): (b) computed aggregate — `FMEA.objects.filter(lifecycle=<in_progress>).count()`.
- "High Risk Items" stat (23): (b) computed aggregate over `RiskEvaluation` (latest evaluation per `FailureMode`, filtered to high/very-high classification, counted) — the existing dashboard already computes an analogous `high_risk_failure_mode_count` for its own High Risk Items tile, so this is an extension of a real, working query, not new territory. The "5 new since last review" sub-caption has no backing history/snapshot data — (c) static placeholder until a review-baseline concept exists.
- "Actions Overdue" stat (8): (b) computed aggregate — `RecommendedAction.objects.filter(due_date__lt=today).exclude(status__in=[completed, verified, cancelled]).count()`, real `RecommendedAction.due_date`/`.status` fields. The "2 critical • 6 normal" split: (c) no priority/severity field exists on `RecommendedAction` — render as placeholder until such a field exists.
- "Reviews Due" stat (4): (c) no review-scheduling entity exists in the model at all — render as static placeholder.
- Risk Overview matrix cells: (b) computed aggregate — group latest-per-`FailureMode` `RiskEvaluation.severity`/`.occurrence` into a 5x5 count grid, same shape as the real `risk_matrix.html` view already performs.
- Validation Trajectory stepper nodes and "Not Started"/"Overdue" states: (c) no lifecycle-stage entity exists — render as static placeholder. The two coverage percentage bars: (b) approximable as a computed aggregate (e.g. % of `FailureMode`s with at least one `RiskEvaluation`), but the exact formula shown is not defined anywhere, so treat any wired number as a *new, proposed* formula, not an established one.
- Top High Risk Items table: (b) computed aggregate — latest `RiskEvaluation` per `FailureMode` joined through `FailureMode.fmea` to `FMEA.project`/`FMEA.fmea_type`, sorted descending by score.
- Recent Projects list: (b) computed aggregate — `FMEAProject`/`FMEA` rows ordered by recency, status pill from `FMEA.lifecycle`; whether a real `updated_at` timestamp field exists is unconfirmed — verify before binding "Updated X ago" to real data, otherwise (c) placeholder.
- Recent Activity feed: (c) no generic cross-entity activity log exists — render as static placeholder (the narrow exception is `RiskEvaluation.actor`/`.trigger`, which could back a risk-evaluation-only slice as (b), but the feed as shown spans several unlogged entity types).
- Knowledge & References list: (c) no document/library entity exists — render as static placeholder.
- Footer "User"/"Role": (a) real — Django `User` plus `ProjectMembership.role` as a display label. "Database"/"System Status": not domain data, environment/infrastructure labels only.

**Filtering/interaction**: No dropdown-driven filtering appears on this screen; the project selector, if wired later, would follow this app's only real filtering pattern — a server-side GET form with a `<select>` and full page reload (as in `risk_matrix.html`'s `method` selector) — not client-side JS.

**Sidebar entry**: This screen *is* the Home entry — already present as the first, ungrouped link in the sidebar (`fmea:dashboard`). No new sidebar entry needed for this page itself; the many additional sidebar links this mockup depicts belong to their own respective future pages, each slotting into the nav-group structure described above.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 02 — Engineering Context Panel: GUI Coding Requirements

### 1. Features & Content

1. Everything in the Home dashboard (mockup-01), reorganized under an additional tab strip and narrowed by a docked right-hand panel.
2. Tab-based switching between "Project Dashboard", "DFMEA", "PFMEA", "System FMEA" views for the current project.
3. A persistent, closeable right-hand drawer ("Engineering Context") that surfaces System/Product/Process data alongside the main dashboard content.
4. Within that drawer, drill-down/master-detail browsing of a process's ordered steps (Operations), with the selected step driving two dependent tables below it.
5. Viewing a selected process step's own characteristics (Process Characteristics) and the product characteristics it affects (Linked Product Characteristics).
6. A project team roster with roles, plus an "add member" action.
7. A static visual summary ("Characteristics Flow") of how Requirements → Functions → Characteristics → Failure Modes → Controls relate to each other.

### 2. Full Wireframe Widget Checklist

**Header/Chrome** — identical to mockup-01, with one substitution: a 9-dot "app launcher" grid icon replaces the "?" help icon. Both are **new patterns** (no icon-only nav-launcher exists today).

**Sidebar** — same base groups as mockup-01 plus a new "CONTEXT (from Open-EQMS)" group: a collapsible sub-group "System / Product / Process" (chevron, expanded, with sub-items System/Product/Process — Process carries a green "Enabled" pill), and separately System Characteristics, Characteristics Flow, Process Flow (external-link icon), Process Characteristics (external-link icon). The `.nav-group`/`.nav-group-title`/`.nav-link` pattern repeats from the existing sidebar; the **collapsible sub-group** (chevron expand/collapse within a nav group) is a **new pattern** — today's `.nav-group` is flat, not expandable. The green "Enabled" pill next to "Process" is a **new pattern** (small inline status badge inside a nav link — could reuse `.status.status-*` styling in miniature).

**Page header + KPI row + tab bar**
- "Welcome back, Janez!" heading, button row — same as mockup-01.
- 5 stat cards — identical set/content to mockup-01, same repeat/gap notes.
- Tab bar "Project Dashboard" (active, blue underline) / "DFMEA" / "PFMEA" / "System FMEA" — **new pattern**. The closest existing thing, `.process-steps`/`.process-step`, is a link-list of *different pages* (full reload per click), not a true tab-panel-swap that keeps one page's layout while changing an underlined "active" tab; it can be reused as the underlying navigation mechanism (each tab is a plain link/GET to a different view or query-string), but the horizontal-underline-tab visual style is new CSS.

**Analytics row (3 columns)**
- "Risk Overview (All Projects)" — same widget as mockup-01, but a 4-tier legend (Low/Medium/High/Very High) instead of 3-tier — repeats `.risk-matrix-*` classes exactly, matching the real `risk_matrix.html` legend's 4-tier `.status-low/medium/high/very_high` set more closely than mockup-01 did.
- "Validation Trajectory (DFMEA + PFMEA)" with an info icon — same stepper/progress-bar widget as mockup-01 (new pattern, see mockup-01 Section 3), plus a circled-"i" info icon — **new pattern** (no inline info-tooltip icon exists).
- "Top High Risk Items" table, columns **Item | Type | Project | RPN | Risk** — same repeat pattern as mockup-01, with an added "Type" column (plain text cell, no new pattern).

**Bottom row (4 cards)**
- "FMEA Team (Project)" card, link "Manage team →": 5 rows, each with colored circular initials avatar, name (+ "You" suffix on one row), role sub-label, role pill (Owner/Member) — the row layout (name/sub-label/trailing pill) repeats the existing `.cell-item`/`.cell-detail` + `.status.status-*` pattern; the **colored circular initials avatar** is a **new pattern** (no avatar/initials-badge component exists). "+ Add member" link/button at bottom — repeats existing `.button`/link pattern.
- "Characteristics Flow" card, link "Open full view →": a vertical flow diagram of 6 connected/colored boxes (Requirements → Functions → [Product/System Characteristics, Process Characteristics] → Failure Modes → [Controls, Control Plan]) — **new pattern**. No diagram/flowchart component exists anywhere in the app; this needs new inline-SVG or CSS-box-and-arrow markup, each box styled with a distinct pastel background by "type."
- "Recent Projects" card, link "View all →": table columns **Project | Type | Status | Updated** — repeats existing `.table-shell`/`<table>` + `.status.status-*` pattern (same rows as mockup-01's card, presented here as a plain table instead of a `.related-list`).
- "Recent Activity" card, link "View all →": same feed as mockup-01 — same repeat/gap notes.

**Right-hand slide-in panel "Engineering Context (from Open-EQMS)"**
- Close "X" button — **new pattern**, no drawer/panel-close affordance exists anywhere (`.icon-button` exists generically, the close semantics/positioning are new).
- Internal tab row "System" / "Product" / "Process" (active) — same new tab-strip pattern as the top-level tab bar above, at a smaller scale.
- "Process Flow" section header, link "Open in Process Planning ↗" — plain text/link, no new pattern.
- Dropdown selector "Headlamp Assembly Process" (chevron) — **new pattern for a dropdown widget**, though functionally it should be a plain `<select>` if built as a GET-form filter (see Section 3).
- Vertical numbered-step list (radio-style markers), rows "10 Incoming Material" ... "60 Packaging", with step "30 Injection Moulding" highlighted/selected (light-blue background, filled marker, trailing arrow) — this **repeats the existing `.process-steps`/`.process-step`/`.process-step-index` pattern almost exactly**, including the `.is-active` selected-row styling — this is the single closest 1:1 match to an existing, already-shipped page (`process_flow.html`) anywhere in this whole mockup set.
- "Process Characteristics (Step 30)" table, columns **Characteristic | Target/Spec | Unit** — repeats the existing `.table-shell`/`<table>` pattern from `process_flow.html`'s own "Process Characteristics" section; that real page currently renders characteristics generically via `.attribute-table` (a key/value dump of the JSON `attributes` field), not as fixed "Target/Spec"/"Unit" columns. Link "View all process characteristics →" — repeats existing link pattern (could point at `fmea:process_characteristic_list` or `fmea:process_flow`).
- "Linked Product Characteristics (affected)" table, columns **Characteristic | Type | Criticality** — repeats `.table-shell`/`<table>` pattern; this exact table (same section title, "Linked Product Characteristics") already exists in `process_flow.html` today with columns **Product Characteristic | From Process Characteristic | Status** — a different column set than this mockup shows. Criticality/Type pills would reuse `.status.status-*` styling. Link "View all product characteristics →" — repeats existing link pattern.

**Footer status bar** — same as mockup-01 (new pattern, not built anywhere yet), with "Version 1.0.0" relocated into the footer instead of the sidebar.

### 3. GUI Coding Requirements

**Route + template**: No existing route matches this screen as a whole (a Home dashboard with a docked Engineering Context drawer). Propose extending the existing `fmea:dashboard` view/template (`dashboard.html`) to optionally render the drawer, rather than a new route, since the main content is the same Home page as mockup-01. If the drawer needs its own addressable URL (e.g. for direct-linking to a specific System/Product/Process tab), propose `fmea:engineering_context` at `django_app/fmea_app/templates/fmea_app/engineering_context.html`, included/rendered as a side panel. The drawer's inner "Process" tab content is functionally a condensed re-presentation of the already-existing `fmea:process_flow` view (`process_flow.html`, per-`Process` via `stable_id`) — the step list, "Process Characteristics" table, and "Linked Product Characteristics" table in the drawer should reuse that view's query logic (or link out to it via "Open in Process Planning ↗" / "View all process characteristics →" rather than duplicating the query).

**Layout structure**:
- Main content region keeps `.content-shell` as in mockup-01, with a new tab strip (`.toolbar`-adjacent, new markup — see below) inserted between the KPI row and the analytics `.grid`.
- The 3-column analytics row and 4-card bottom row stay `.grid` > `.panel.span-4`/`.panel.span-3` as in mockup-01.
- The right-hand drawer is a new fixed/sticky-width column outside the normal `.grid` flow — proposed markup: a `<aside class="context-panel">` sibling to `.content-shell` inside `.workspace`, toggled by a new `[data-context-panel-toggle]` attribute (same minimal-JS pattern as `data-sidebar-toggle`) that adds/removes a class controlling its visibility and the main content's effective width.
- Inside the drawer: internal tab row (new, same tab-strip CSS as the top-level tabs), then a `.panel`-style stack (`.stack`) containing the dropdown, the `.process-steps`/`.process-step` list (reused verbatim from `process_flow.html`), and two `.table-shell` tables below it.

**New CSS/JS needed**:
- Tab strip (top-level "Project Dashboard/DFMEA/PFMEA/System FMEA" and the drawer's internal "System/Product/Process"): no tab-panel-swap component exists. Build as a row of plain links with an `.is-active` underline state (each tab navigates to a distinct URL or query-string view, full page reload — consistent with this app's server-rendered, no-AJAX approach), styled with new CSS (proposed `.tab-strip`/`.tab-link`/`.tab-link.is-active`). Do not build this as client-side JS panel-swapping; that would be new architecture beyond this app's "plain templates + full reload" pattern.
- Right-hand drawer open/close: new `<aside>` region plus a small vanilla-JS toggle in `app.js` (`[data-context-panel-toggle]`), following the existing `data-sidebar-toggle`/`data-theme-toggle` style — no framework, no modal library.
- Collapsible sidebar sub-group ("System / Product / Process" chevron): new CSS/JS, proposed `[data-nav-group-toggle]` toggling a `.nav-subgroup.is-expanded` class, same minimal-toggle style.
- Avatar/initials badges (FMEA Team roster): new component, proposed `.avatar` with per-user background-color variants.
- Characteristics Flow diagram: new inline-SVG or CSS box/arrow diagram, proposed `.flow-diagram`/`.flow-box` with color modifiers per box "type" (gray/green/blue/purple/yellow/teal), consistent across every mockup that reuses this diagram.
- Info-tooltip icon ("i" circle): new small hover/click affordance, proposed `.info-icon` with a `title` attribute at minimum (no JS needed for a plain native tooltip) or a small popover if richer content is wanted.

**Per-widget data binding**:
- Tabs "DFMEA"/"PFMEA"/"System FMEA": (a) real — each is an `FMEA` row scoped by `fmea_type` under the current `FMEAProject`.
- Sidebar "System"/"Product"/"Process" context items and drawer tabs "Product"/"Process": (a) real — map to the existing `Product` and `Process` models (both FK'd to `FMEA`). The "System" tab/item specifically: (c) no `System` model exists in the codebase today — render as static/placeholder until that entity exists.
- "Process" sidebar item's "Enabled" pill: (c) no enable/configured flag exists on `Process`/`FMEA` — static placeholder.
- Process Flow dropdown + numbered step list (10/20/30...): (a) real — `Operation.name`/`Operation.sequence` ordered under the selected `Process`, exactly as the existing `process_flow.html` already renders via `operations`/`selected_operation`.
- "Process Characteristics (Step 30)" table: `Characteristic` column is (a) real (`ProcessCharacteristic.name`); "Target/Spec" and "Unit" as separate structured columns are (c) not confirmed as real fields — the only backing data is a generic `attributes` JSONField with no established key convention, so render those two columns as static/placeholder content until either an `attributes` key convention is agreed or dedicated fields are added.
- "Linked Product Characteristics (affected)" table: `Characteristic` column is (a) real (`ProductCharacteristic.name`). "Criticality" has no dedicated field — the closest real data is the boolean `ProductCharacteristic.is_special`, which is a 2-value flag, not the graded scale shown, so render "Criticality" as (c) placeholder pending a real field. "Type" (Safety/Optical/Decorative) has no backing field at all — (c) placeholder. The *link* between a process step and "affected" product characteristics is not a direct relationship in the model (`ProductCharacteristic` links to `Requirement`, not to `Operation`); the existing `process_flow.html` page derives its analogous table through the real `CauseInfluence` linking mechanism, so any real version of this table should reuse that same query rather than inventing a new relationship.
- Characteristics Flow diagram: (a) real, as a static diagram — every relationship it depicts (`Requirement.function`, `ProductCharacteristic.requirement`, `ProcessCharacteristic.operation`, `FailureMode.function`/`.requirement`, `PreventionControl.failure_cause`/`DetectionControl.failure_cause`) is a real FK. "Control Plan (Open-EQMS)" box: (c) no Control Plan entity exists in this codebase — render as static placeholder/label.
- "FMEA Team (Project)" roster: (a) real — `ProjectMembership.role` joined to Django's `User`. "Owner"/"Member" pill: (a) real field value (`ProjectMembership.role` is a plain label, displayable as-is); note it carries no enforced permission behavior, so gating "Add member" on it would be new logic, not something already backed.
- Recent Projects / Recent Activity: same binding as mockup-01 — Recent Projects is (b) computed aggregate (ordering by recency, pending confirmation of a real timestamp field); Recent Activity is (c) placeholder (no generic activity log exists).
- App-launcher (9-dot) icon: (c) no module registry exists — static/placeholder link list if built now.

**Filtering/interaction**: The Process Flow dropdown and step selection should follow this app's one real filtering pattern: a server-side GET form with `<select>`/link parameters and full page reload — exactly as `process_flow.html` already implements step selection via `?operation_id=...`. Do not build the dropdown or step list as client-side/AJAX-driven; there is no precedent for that anywhere in this codebase.

**Sidebar entry**: The "CONTEXT (from Open-EQMS)" group is new — it would sit as its own `.nav-group` with `.nav-group-title` "CONTEXT", placed between "FMEA WORKSPACE" and "FMEA ANALYSIS" per the canonical group ordering. "Process Flow" and "Process Characteristics" links inside it can point at the already-existing `fmea:process_flow` and `fmea:process_characteristic_list` routes.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 03 — Preventive FMEA (PM-FMEA) Tab: GUI Coding Requirements

### 1. Features & Content

1. A two-tier tab hierarchy per FMEA: top-level FMEA-type tabs (DFMEA/PFMEA/System FMEA/Preventive FMEA) plus a second row of workflow sub-tabs (Overview/FMEA Team/Scope & Configuration/Links/Reviews/Baseline/History) within the selected type.
2. A maintenance-flavored overview equivalent to the DFMEA/PFMEA dashboard: an "assets covered" donut breakdown by risk tier, in place of the severity x occurrence matrix.
3. A maintenance-lifecycle validation trajectory (Concept → Design → Install → Commission → PV → Operation → Monitor) with readiness/coverage bars, mirroring the DFMEA/PFMEA trajectory pattern.
4. A ranked table of top high-risk maintenance items, joined to an asset/machine identifier.
5. Project team roster and a maintenance-specific "Characteristics Flow" diagram (Product → Process → Maintenance).
6. The same right-hand Engineering Context drawer as mockup-02, extended with a 4th "Characteristics" tab and two new PM-FMEA-specific sections (Linked Asset, Maintenance Status) under its Process tab.
7. A settings entry point ("FMEA Workspace Settings") alongside the tab bar.

### 2. Full Wireframe Widget Checklist

**Header/Sidebar** — same chrome as mockup-02. Sidebar's "FMEA ANALYSIS" group gains a new active item "Preventive FMEA (PM-FMEA)" — repeats the existing `.nav-link`/`.nav-link.is-active` pattern, new destination only.

**Page header**
- Breadcrumb-style heading "FMEA Workspace – New Headlamp X1" (blue link-styled) — repeats the existing `.toolbar` > `<h1>` pattern, styled as a link; new content shape (breadcrumb-like) but not a new component.
- 5 stat cards — same set/pattern as mockups 01–02.

**Top-level tab bar**
- "DFMEA" / "PFMEA" / "System FMEA" / "Preventive FMEA (PM-FMEA)" (active, blue underline) — repeats the new tab-strip pattern introduced in mockup-02 (Section 3 there).
- "⚙ FMEA Workspace Settings" outline button beside the tabs — repeats existing `.button` pattern with an icon glyph; destination page is new.

**Second-level tab bar**
- "Overview" (active) / "FMEA Team" / "Scope & Configuration" / "Links (Open-EQMS)" / "Reviews" / "Baseline" / "History" — repeats the same new tab-strip pattern, nested one level deeper (a second row of the same component).

**Analytics row (3 columns)**
- "Preventive FMEA Overview" card (info icon): a donut/ring chart, center text "124 of 156", 4-item colored legend (Low Risk 68 (55%) / Medium Risk 34 (27%) / High Risk 16 (13%) / Not Analyzed 12 (10%)), link "Open PM-FMEA →" — **new pattern**. No donut/pie or ring-chart affordance exists anywhere in this app today.
- "PM-FMEA Validation Trajectory" card: 7-node stepper (Concept/Design/Install/Commission/PV/Operation/Monitor) with per-node status coloring, "Maintenance Readiness" bar 78% green, "PM-FMEA Coverage" bar 64% blue, 5-item legend, link "Open PM-FMEA Trajectory →" — repeats the same new trajectory-stepper pattern from mockup-01/02 (still new relative to the codebase, but a *repeat* of the pattern already flagged there), with the progress bars repeating the existing `<progress class="status-progress">` pattern.
- "Top High Risk Maintenance Items" table, link "View all →": columns **Item | Asset / Machine | RPN | Risk** — repeats the existing `.table-shell`/`<table>` + `.status.status-*` pattern; "Asset / Machine" is a new column relative to mockup-01/02's equivalent table.

**Bottom row (4 cards)**
- "FMEA Team (Project)" card — identical widget/roster to mockup-02, same repeat notes (avatar badges new, list layout existing).
- "Characteristics Flow (Product → Process → Maintenance)" card, link "Open full view →": vertical flow diagram, Product/System Characteristics → Process Characteristics → 3-way split (PFMEA / PM-FMEA / Control Plan) → converge into "Maintenance Tasks / Plans" — repeats the new flow-diagram pattern introduced in mockup-02, with a different box graph shape (4 tiers instead of mockup-02's 3-tier fan-out/converge).
- "Recent Projects" card, link "View all →": table columns **Project | Type | Status | Updated**, with combined type badges like "DFMEA + PFMEA + PM-FMEA" — repeats existing `.table-shell` + `.status.status-*` pattern; the multi-type badge text is a plain string concatenation, no new component.
- "Recent Activity" card, link "View all →": maintenance-flavored rows (PM task created, maintenance risk updated, PV plan linked, action completed, FMEA review completed) — repeats the same `.related-list`/`activity-item`-style pattern as prior mockups, new data only.

**Right-hand "Engineering Context (Open-EQMS)" panel**
- Tab row: System / Product / Process (active) / **Characteristics** (4th tab, new relative to mockup-02's 3-tab panel) — repeats the drawer's internal tab-strip pattern from mockup-02, one more tab.
- "Process Flow" header, "Open in Process Planning ↗" link, "Select Process" sub-label, dropdown "Headlamp Assembly Process" — identical to mockup-02.
- Numbered step list (10–60, step 30 selected/highlighted with arrow) — identical to mockup-02; still the closest 1:1 match to the existing real `process_flow.html` step-list markup.
- "Process Characteristics (Step 30)" table (Characteristic | Target/Spec | Unit) — identical to mockup-02.
- "Linked Asset for Step 30" section (new vs. mockup-02): factory/building icon, asset name "Injection Molding Machine 03", code "IMM-03", status pill "Operational" (light green, with status dot), "Location: Plant 1 / Line A", link "Open Asset in Maintenance →" — **new pattern**. No asset/equipment display card exists anywhere; the status pill itself would reuse `.status.status-*` styling, but the icon+name+code+location card layout is new.
- "Maintenance Status" section (new vs. mockup-02): "PM Compliance" 92% (green, with a green progress bar), "Overdue WO" 3 (red), "Next PM" 12 May 2025 (blue) — repeats the existing `<progress>` bar pattern for PM Compliance; the compact 3-metric mini-stat row is a variant of the existing `.stat-tile` pattern at smaller scale, not fully new.

**Footer status bar** — same as prior mockups (still not built anywhere yet).

### 3. GUI Coding Requirements

**Route + template**: No existing route corresponds to "Preventive FMEA (PM-FMEA)" — the real `FMEA.fmea_type` field's choices are design/process/product/software/system; there is no "preventive" value today. If/when a PM-FMEA concept is approved, propose route `fmea:pmfmea_overview` (or reuse `fmea:fmea_detail` with `fmea_type=preventive` once that value exists) and template `django_app/fmea_app/templates/fmea_app/pmfmea_overview.html`, following the same `{% extends "fmea_app/base.html" %}` pattern as every other page. Until then, this page has no real destination to build against.

**Layout structure**:
- Top-level and second-level tab bars: two stacked instances of the new tab-strip component introduced in mockup-02 (`.tab-strip`/`.tab-link`), the second row visually nested/indented under the first.
- Analytics row: `.grid` > three `.panel.span-4` cards, as in mockups 01–02.
- Bottom row: `.grid` > four `.panel.span-3` cards, as in mockup-02.
- Right-hand drawer: same `<aside class="context-panel">` structure as mockup-02, with a 4th tab added to its internal tab strip and two additional `.stack`-arranged sections ("Linked Asset for Step 30", "Maintenance Status") appended below the existing Process Characteristics table, conditionally rendered only when the PM-FMEA top-level tab is active.

**New CSS/JS needed**:
- Donut/ring chart ("Assets Covered", 124 of 156): use Chart.js (the just-decided charting library, vendored locally, no CDN) in doughnut-chart mode — this is exactly the kind of widget Chart.js was chosen for. Needs a `<canvas>` element plus a small vanilla-JS initialization script reading data attributes or an inline JSON blob rendered by Django, no build step.
- Asset/equipment display card ("Linked Asset for Step 30"): new component, proposed `.asset-card` with an icon slot, name/code line, status pill (reusing `.status.status-*`), and a location line.
- Everything else on this page repeats patterns already flagged as new in mockup-01/02 (trajectory stepper, flow diagram, tab strip, avatar badges) — no additional new primitives beyond the donut chart and asset card.

**Per-widget data binding**:
- The entire "Preventive FMEA (PM-FMEA)" tab and everything under it: (c) no real data source yet. `FMEA.fmea_type` has no "preventive" choice, and none of the maintenance-specific concepts this screen implies — Asset, WorkOrder, MaintenancePlan, a maintenance-risk analog to `FailureMode`/`RiskEvaluation` — exist anywhere in the model. Every widget below should render as static/placeholder content until those entities exist; nothing on this page currently has real data behind it.
- "FMEA Team (Project)" roster: (a) real — `ProjectMembership`/`User`, same as mockup-02 (this sub-tab is the one part of this screen backed by real data today).
- "Scope & Configuration" sub-tab: (a) real, if built as a basic edit form against `FMEA.scope`/`FMEA.description`.
- "Characteristics Flow" diagram's first two/three boxes (Product/System Characteristics, Process Characteristics, PFMEA fan-out): (a) real, same relationship chain as mockup-02's diagram. "PM-FMEA (Maintenance Risk)" and "Maintenance Tasks / Plans" boxes: (c) placeholder, no backing entity.
- "Baseline"/"History" sub-tabs: (c) no versioning/snapshot entity exists for an `FMEA` — placeholder only.
- "Reviews" sub-tab: (c) same as "Reviews Due" elsewhere — no review-scheduling entity exists.
- Right-panel Process tab (dropdown, step list, Process Characteristics table): same binding as mockup-02 — (a) real for the step list (`Operation.name`/`.sequence`), (c) placeholder for Target/Spec/Unit columns pending an `attributes` convention.
- "Linked Asset for Step 30" and "Maintenance Status" sections: (c) no Asset/WorkOrder entity exists — static/placeholder content.
- Recent Projects/Activity, stat cards: same bindings as mockup-01/02 (mix of (a)/(b) for the DFMEA/PFMEA-real portions, (c) for anything PM-FMEA-specific).

**Filtering/interaction**: Same as mockup-02 — the Process Flow dropdown/step selection is a server-side GET form + full reload, following `process_flow.html`'s existing pattern. Tabs (both tiers) are plain navigation links, not client-side panel swaps.

**Sidebar entry**: "Preventive FMEA (PM-FMEA)" belongs under the existing "FMEA ANALYSIS" group alongside DFMEA/PFMEA/System FMEA, once a real destination exists for it.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 04 — Consolidated Home: GUI Coding Requirements

### 1. Features & Content

1. A "superset" Home dashboard layering the mockup-01/02/03 content into one page: 6 KPI cards, the 3-column analytics row, a 3-column-plus context/ops row, and a new full-width bottom summary strip — all beside the docked Engineering Context drawer.
2. Sidebar navigation extended with two additional deep-link-out groups ("OPERATIONS", "MAINTENANCE") pointing at sibling Open-EQMS modules.
3. A rollup "Engineering Context Summary" tile grid (Product/Process Characteristics counts, Process Steps, Machines/Assets, Control Plans, unlinked-characteristics warning).
4. A combined DFMEA + PFMEA + PM-FMEA validation trajectory and coverage view.
5. A single ranked "Top High Risk Items" table interleaving DFMEA/PFMEA and PM-FMEA rows.
6. An "Operations & Maintenance Status" snapshot of today's production orders and maintenance work orders.
7. A bottom-of-page "Project Health" strip: an overall health gauge, a 30-day risk trend line chart, an actions summary, coverage bars, a data-integrity (linked/unlinked/broken-link) summary, and an upcoming-reviews list.

### 2. Full Wireframe Widget Checklist

**Header/Sidebar** — same chrome as mockup-02/03. Sidebar gains: "FMEA ANALYSIS" group's "Preventive FMEA (PM-FMEA)" item now carries a yellow-outlined "NEW" badge (new pattern: a small badge chip on a nav link, not present elsewhere); a new "OPERATIONS" group (Process Planning, Production Execution, Work Tracking, Traceability — each with an external-link icon); a new "MAINTENANCE" group (Assets & Equipment, Maintenance Plans, Preventive Maintenance, Preventive FMEA (PM-FMEA), Maintenance Work Orders — each with an external-link icon). The external-link icon on a nav item repeats the same treatment already used for "Process Flow"/"Process Characteristics" in mockup-02's sidebar (new icon, but a repeated visual convention within these mockups, not invented fresh here).

**Page header** — "Welcome back, Janez!" + subtext ("...across engineering, quality, operations and maintenance") + same button row as prior mockups.

**KPI row (6 stat cards)** — same 5 cards as mockup-01, plus: "Unlinked Items" 5 / "Need attention" / "View details →" (chain/link icon) — repeats the existing stat-tile pattern, new metric. Same 5-into-12-column layout gap noted in mockup-01 Section 3, now for 6 cards (6 x span-2 would divide evenly, but span-2 does not exist in the current class set — same new-layout flag applies).

**Analytics row (3 columns)**
- "Risk Overview (All Projects)" — same widget/pattern as mockup-02 (4-tier legend), different cell values.
- "Validation Trajectory (DFMEA + PFMEA + PM-FMEA)" — same trajectory-stepper pattern as mockup-01/02/03, now with a 3rd coverage bar ("PM-FMEA (Maintenance) Coverage" 54%, purple) added below the existing two — repeats the `<progress>` bar pattern a third time.
- "Top High Risk Items" table, columns **Item | Type | Project | RPN | Risk** — same widget as mockup-02, now interleaving "FM-" and "PM-" coded rows in one ranked list — same table pattern, no new component.

**Middle row (4 cards)**
- "Engineering Context Summary" card, link "Open Engineering Context →": a 2x3 grid of 6 mini-stat tiles (icon + label + bold value): Product Characteristics 84, Process Characteristics 37, Process Steps/Operations 22, Machines/Assets 16, Control Plans 22, Characteristics without Links 5 (amber warning-triangle icon) — repeats the existing `.stat-tile` component at a smaller/denser scale (a 2x3 sub-grid of tiles inside one card, rather than one tile per top-level card) — a *sizing/layout* variant of an existing component, not a wholly new one. The warning-triangle icon on the last tile is new (icon-in-tile is not used elsewhere today).
- "Preventive FMEA (PM-FMEA)" card, subtitle "Maintenance Risk Overview": donut chart, center "124" (sub-line not reliably legible in the source crop), 4-item legend — repeats the new donut-chart pattern introduced in mockup-03 (Chart.js).
- "Operations & Maintenance Status" card: "Production (Today)" row of 3 mini-cards (Orders 12, In Progress 7, Completed 5), "Maintenance (Today)" row of 3 mini-cards (PM Due 8, In Progress 4, Overdue 3 in red), link "Open Operations Dashboard →" — repeats the mini-stat-tile pattern (same as Engineering Context Summary above), two rows of three.
- "Recent Activity" card, link "View all →" — same feed pattern as prior mockups, new/partial content.

**Right-hand "Engineering Context (Open-EQMS)" panel** — identical to mockup-02/03's panel (System/Product/"Process" active/Characteristics tabs, Process Flow dropdown + step list, Process Characteristics table, Linked Product Characteristics table) — same repeat notes as those mockups; no "Linked Asset"/"Maintenance Status" sections shown in this crop (those are PM-FMEA-tab-specific, per mockup-03).

**Bottom-of-page 6-column band ("Project Health (Summary)")**
- "Overall Health" circular gauge, 78%, sub-label "Good" (green) — **new pattern**. No circular-gauge component exists anywhere; closest existing primitive is the linear `<progress>` bar, not a radial gauge.
- "Risk Trend (vs last 30 days)" multi-line chart: y-axis band labels High/Medium/Low, x-axis -30d/-20d/-10d/Today, 3 colored line series (red/amber/green) with point markers — **new pattern**. Use Chart.js line-chart mode; no chart of any kind is wired into any page today.
- "Actions" mini-panel: Total 56, Overdue 8 (red), Due Soon 12 (amber) — repeats the mini-stat-tile pattern used elsewhere on this page.
- "Coverage" mini-panel: 3 labeled horizontal bars (DFMEA 78% green, PFMEA 62% blue, PM-FMEA 54% purple) — repeats the existing `<progress>` bar pattern, 3 in a row.
- "Links (Data Integrity)" mini-panel: Linked Items 92% (green), Unlinked Items 5, Broken Links 3 (red) — repeats the mini-stat-tile pattern.
- "Next Reviews" mini-panel: 3 rows, each "<FMEA type> Review — <date>" (blue) — repeats the `.related-list`/`.cell-item` row pattern at small scale.

**Footer status bar** — same as prior mockups (not built anywhere yet).

### 3. GUI Coding Requirements

**Route + template**: Same as mockup-01 — this is the existing `fmea:dashboard` route/`dashboard.html` template, taken to its most expanded/composed form. There is no separate "consolidated home" route; this mockup represents the ceiling of what the one real Home page could eventually show as more Open-EQMS modules and FMEA types come online. Build incrementally against the existing `dashboard.html`, not as a new page.

**Layout structure**:
- Same `.app-shell`/`.workspace`/`.content-shell` skeleton, same tab-strip and drawer additions as mockup-02.
- KPI row: `.grid.section-block` with 6 stat-tile includes; same span-divisibility gap as mockup-01, now needing either 2 rows of 3 (`span-4` each) or a new flex-based `.stat-row` variant sized for 6 (or, generically, N) equal columns.
- "Engineering Context Summary" and "Operations & Maintenance Status" mini-tile grids: proposed nested `.grid` (or a new `.tile-grid` utility) inside a `.panel`, using smaller `.stat-tile.compact`-style tiles — flag as a new size variant of the existing stat-tile, not a new component family.
- Bottom "Project Health" band: a new full-width `.grid.span-12` row of 6 narrow `.panel` cells, each `.span-2`-equivalent (again hitting the same 12-column-divisibility gap noted above — 6 columns divides evenly at span-2, but span-2 does not exist in the current CSS; this row alone justifies adding a `span-2` class to the grid system, or building it with `display:flex` instead of the `.grid`/`.span-N` system).

**New CSS/JS needed**:
- Circular "Overall Health" gauge: new component. Chart.js can render this as a doughnut chart with a single-segment "cutout" trick (a common Chart.js technique for gauge-style displays), reusing the same charting library rather than inventing a separate SVG gauge widget.
- "Risk Trend" line chart: Chart.js line-chart mode, new `<canvas>` + minimal init script (same pattern as the PM-FMEA donut in mockup-03).
- "NEW" badge chip on a nav link: new small CSS class, proposed `.nav-badge`.
- External-link icon convention repeated across "OPERATIONS"/"MAINTENANCE" groups: same new icon treatment flagged in mockup-02, now applied to two more full nav groups.
- Mini-stat-tile grids (Engineering Context Summary, Operations & Maintenance Status, Project Health band): new compact size variant of `.stat-tile`, proposed `.stat-tile.compact` or a dedicated `.mini-tile` class, plus an icon slot not present in the current `_stat_tile.html` include.

**Per-widget data binding**:
- Stat cards 1–5: same bindings as mockup-01 ((a) for FMEA Projects/Active Analyses counts, (b) for High Risk Items/Actions Overdue aggregates, (c) for the "5 new since last review" and critical/normal splits, (c) for Reviews Due).
- "Unlinked Items" stat (5): (b) computed aggregate over real nullable FK fields (e.g. `ProductCharacteristic.requirement`, `FailureMode.function`/`.requirement` are real nullable FKs), but the exact rule defining "unlinked" is not established anywhere — any wired number here is a new, proposed query, not an existing one.
- "Engineering Context Summary" tiles: Product Characteristics/Process Characteristics/Process Steps counts are (b) computed aggregates over real models (`ProductCharacteristic`, `ProcessCharacteristic`, `Operation`), scoped through their real FK chains up to `FMEA.project`. "Machines/Assets" and "Control Plans" counts: (c) no Asset or Control Plan entity exists — static placeholder. "Characteristics without Links": (b) computed aggregate, same caveat as "Unlinked Items" above (rule not established).
- "Preventive FMEA (PM-FMEA)" donut and "Operations & Maintenance Status" card: (c) entirely placeholder — no Asset/WorkOrder/production-order entity exists anywhere in this codebase; if this dashboard is meant to embed data from separate Operations/Maintenance modules, that is a cross-module integration question, not something this template can query directly.
- Top High Risk Items table: the DFMEA/PFMEA rows are (b) computed aggregate (same as mockup-01/02); the PM-FMEA rows and the interleaved-ranking behavior are (c) placeholder, blocked on the same PM-FMEA data gap as mockup-03.
- Validation Trajectory: DFMEA/PFMEA coverage bars are (b) computed aggregate (approximable, formula not established); PM-FMEA coverage bar and all stepper nodes are (c) placeholder.
- "Overall Health" gauge: (c) no composite scoring formula or field exists anywhere — placeholder, and any real version would need an explicit formula decided first (what inputs, what weights).
- "Risk Trend" line chart: (c) no time-series/snapshot data exists to plot — `RiskEvaluation.evaluated_at` is a real timestamp field, but "count of failure modes whose latest-as-of-date-X evaluation fell in each risk tier" is not a query this app performs anywhere today, so render as static placeholder until that aggregation (or a snapshot entity) is built.
- "Actions" mini-panel (Total/Overdue/Due Soon): Total and Overdue are (b) computed aggregate over real `RecommendedAction.status`/`.due_date` fields; Due Soon is the same query shape with a near-future date window — (b).
- "Coverage" mini-panel: same bindings as the Validation Trajectory coverage bars above.
- "Links (Data Integrity)" mini-panel: Linked Items %/Unlinked Items are (b), same caveat as above; "Broken Links" is (c) — no dangling-reference/integrity-check logic exists anywhere.
- "Next Reviews" mini-panel: (c) — same as Reviews Due, no review-scheduling entity exists.
- Right-hand drawer: identical bindings to mockup-02.

**Filtering/interaction**: No new filtering pattern beyond what mockup-02 already introduces (the Process Flow dropdown as a GET-form select). Every stat tile and mini-tile that links out ("View all →", "Open ... →") is a plain navigation link, not a client-side filter.

**Sidebar entry**: "OPERATIONS" and "MAINTENANCE" are new top-level nav groups, sitting after "LINKED EQMS" in the canonical group ordering; every item within them is a deep-link out to a separate Open-EQMS module rather than a page this app owns, so building them means adding external-URL nav links, not new local routes.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 05 — FMEA Projects List: GUI Coding Requirements

### 1. Features & Content

1. A dedicated list page enumerating every FMEA analysis (or project — see the grain note in Section 3) with type, owner, status, progress, and recency.
2. A summary KPI row breaking down the total count by FMEA type (DFMEA/PFMEA/System FMEA/PM-FMEA).
3. A dense per-row action set (open, edit, overflow menu) for jumping into or managing an individual FMEA.
4. Toolbar actions for creating a new project, importing, generating reports, applying a template, and filtering the list.

Note: the source image is a cropped horizontal strip (1132x228px) showing only the header, action row, stat cards, and the top of the table — no footer, pagination, or empty state is visible in this asset, so their presence should not be assumed either way when building.

### 2. Full Wireframe Widget Checklist

**Header/Chrome** — same as mockups 01–04 (logo, hamburger, page title "FMEA Projects", subtitle, project selector, search, bell, help, avatar) — same repeat/new-pattern notes as mockup-01.

**Sidebar (partial, as visible)** — "FMEA WORKSPACE" group (Home, "FMEA Projects" active, FMEA Team), "CONTEXT (from Open-EQMS)" group (collapsible "System / Product / Process" expanded, plus System Characteristics Base, Characteristics Flow/Diagram, Process Flow, Process Characteristics) — same repeat/new-pattern notes as mockup-02 (the collapsible sub-group is new; the rest repeats the existing `.nav-group` pattern).

**Action button row** (top-right of content area)
- "+ New Project" (primary) — repeats existing `.button.primary` pattern; this exact action already exists as a working create form in the real `project_list.html` (`fmea:create_project`), currently rendered as an inline card-form rather than a button that opens elsewhere — see Section 3.
- "Import" (outline, icon) — repeats existing `.button` pattern; a working equivalent already exists (`fmea_review:session_list`, linked as "Import XLSX" in the real page).
- "Reports" (outline, dropdown chevron) — new destination; dropdown-chevron button is the same new pattern flagged in mockup-01.
- "Templates" (outline, dropdown chevron) — new destination, same new dropdown-button pattern.
- "Filters" (outline, filter icon) — new pattern; no filter-panel/drawer trigger exists anywhere today (see Section 3 for the recommended non-drawer alternative).

**KPI row (5 stat cards)**
- "Total Projects" 12 / "Active FMEA projects" — repeats the existing `_components/_stat_tile.html` pattern; the real `project_list.html` already has an equivalent tile ("Total Projects") today.
- "DFMEA" 4 / "Design FMEA projects" — repeats stat-tile pattern; new metric (a per-type breakdown, whereas the real page's other three tiles today are Active/On Hold/Completed by project status, not by FMEA type).
- "PFMEA" 5 / "Process FMEA projects" — same repeat pattern.
- "System FMEA" 2 / "System level FMEA" — same repeat pattern.
- "PM-FMEA" 1 / "Preventive FMEA projects" — same repeat pattern; see Section 3 for the `fmea_type` data gap.

**Projects table**
- Columns: **Project Name | Project Code | FMEA Type | Related Product / Process | Owner | Status | Progress | Last Updated | Actions** — repeats the existing `.table-shell`/`<table>` pattern already used for the real page's "Project Register" table (which today has columns Name/Project Code/Status/FMEAs/Type Breakdown/Last Updated — a different, project-grained column set than this mockup's FMEA-grained one; see Section 3).
- "Project Name" cell — plain link, repeats existing `<a href="...">{{ name }}</a>` pattern.
- "Project Code" cell — plain text, repeats existing pattern.
- "FMEA Type" cell — colored pill (DFMEA blue / PFMEA green / System FMEA purple / PM-FMEA orange) — repeats the existing `.status.status-*` badge pattern (new color-to-type mapping, not a new component).
- "Related Product / Process" cell — plain text, repeats existing pattern.
- "Owner" cell — avatar initials + name — repeats the new avatar-badge pattern flagged in mockup-02 (no avatar component exists yet).
- "Status" cell — pill ("In Progress" blue, "Review" lavender) — repeats the existing `.status.status-*` badge pattern, reusing the real `get_status_display`/`get_lifecycle_display` convention already used elsewhere.
- "Progress" cell — horizontal bar + "N%" label — repeats the existing `<progress class="status-progress">` pattern already used in the real `dashboard.html` ("Cause Influences by Status"), applied per-row here rather than per-status-group.
- "Last Updated" cell — plain formatted date/time — repeats the existing `{{ value|date:"Y-m-d H:i" }}` pattern already used in `project_list.html`'s "Last Updated" column.
- "Actions" cell — 3 icons (external-link/open, pencil/edit, "..." overflow) — the open/edit destinations repeat existing plain-link patterns; the "..." overflow menu is a **new pattern** (no dropdown/context-menu component exists anywhere).

### 3. GUI Coding Requirements

**Route + template**: This screen already exists in the codebase — route `fmea:project_list` (`path("fmea/projects/", views.project_list, name="project_list")`), template `django_app/fmea_app/templates/fmea_app/project_list.html`. This mockup is a redesign of that existing page, not a new route: the real page today shows 4 status-based stat tiles (Total/Active/On Hold/Completed) and a project-grained "Project Register" table (Name/Project Code/Status/FMEAs/Type Breakdown/Last Updated), while this mockup shows type-based stat tiles (Total/DFMEA/PFMEA/System/PM-FMEA) and an FMEA-grained table (one row per individual `FMEA` analysis, with its own Type/Owner/Progress/Related-entity columns). Building this mockup means deciding which grain the page should use — or adding a toggle between "by project" and "by FMEA" views — before extending `project_list.html`, since the two column sets do not merge cleanly onto one query.

**Layout structure**:
- Page header: existing `.toolbar` > `<h1>`/`<p class="muted">` + `.button-row`, as already used in `project_list.html`.
- KPI row: `.grid.section-block` with five `{% include "fmea_app/_components/_stat_tile.html" %}` calls (this mockup's 5-across layout hits the same 12-column-divisibility gap noted in mockup-01 — either wrap 3+2 at `span-4`, or add a new equal-width flex row variant).
- Table: `.panel.span-8`-or-wider (or `.span-12` if the create-project form is moved elsewhere) containing `.table-shell` > `<table>`, following the exact structure already in `project_list.html`.
- "+ New Project" as a primary toolbar button implies moving project creation out of the current inline "Create Project" panel-form (`.panel.span-4` beside the table today) into a separate destination — either a dedicated create page/route or a modal/drawer. Since no modal/drawer component exists in this app (see below), the simplest change consistent with the existing architecture is a dedicated create-project page at a new URL, reusing the existing `fmea_form`/`project_form` Django form and `{% csrf_token %}` POST pattern already used inline today.

**New CSS/JS needed**:
- "..." overflow action menu per row: no dropdown/context-menu component exists anywhere in this app. Needs new minimal markup/CSS (proposed `.row-menu` triggered by a `[data-row-menu-toggle]` button, same vanilla-JS open/close-on-click pattern as `data-sidebar-toggle`/`data-theme-toggle`, no framework) — or, more consistent with this app's server-rendered style, replace it with a small set of always-visible icon links (open/edit/archive) instead of a hidden menu, avoiding new JS entirely.
- "Filters" button opening a panel: if built as a real drawer/popover, this is new (no drawer component exists — see mockup-02's proposed `.context-panel` pattern, reusable here). The lower-effort, architecture-consistent alternative is a `.panel.compact` GET-form (as already used in `risk_matrix.html`) with `<select>` filters for Type/Status/Owner, submitted via full page reload — recommended over a new drawer component, since it needs no new JS at all.
- Avatar/initials badge for "Owner": same new component flagged in mockup-02.
- "Reports"/"Templates" dropdown-chevron buttons: same new small-popover pattern flagged in mockup-01.

**Per-widget data binding**:
- "Total Projects" stat: (a) real — `FMEAProject.objects.filter(status=<active>).count()`, already computed by the real page today (as `project_count`).
- "DFMEA"/"PFMEA"/"System FMEA" stats: (b) computed aggregate — `FMEA.objects.values("fmea_type").annotate(Count(...))` grouped by the real `FMEA.fmea_type` field.
- "PM-FMEA" stat: (c) no "preventive" value exists in `FMEA.fmea_type`'s real choices (design/process/product/software/system) — render as static/placeholder until that type exists.
- Table "Project Name"/"Project Code": (a) real if the row represents `FMEAProject` (`FMEAProject.name`/`.project_code`, exactly as the existing page already renders); if the row instead represents one `FMEA` (as this mockup's per-row FMEA Type/Progress columns suggest), "Project Code" has no equivalent field on `FMEA` itself — that grain choice needs resolving first (see Layout structure above) before this column can be considered bound to real data.
- "FMEA Type" cell: (a) real — `FMEA.fmea_type` / `get_fmea_type_display`, for DFMEA/PFMEA/System rows; (c) placeholder for a PM-FMEA row, same gap as the stat card.
- "Related Product / Process" cell: (b) computed — resolvable via the real `FMEA.products`/`FMEA.processes` reverse FKs, but showing a single name implies a "pick one" convention not defined anywhere (an `FMEA` can have multiple related `Product`/`Process` rows). For a "System FMEA" row: (c) no `System` model exists — placeholder. For a "PM-FMEA" row ("CNC-01 Milling Machine"): (c) no Asset/Machine entity exists — placeholder.
- "Owner" cell: (b) computed — no direct "owner" field exists on `FMEA`/`FMEAProject`; the closest real data is `ProjectMembership` filtered to a role convention (e.g. `role == "Owner"`), which is derivable but not a stored field today.
- "Status" cell: (a) real — `FMEA.lifecycle` / `get_lifecycle_display`, same pattern already used in `project_list.html` for `FMEAProject.status`.
- "Progress" cell: (c) no stored completion-percentage field exists on `FMEA` — any number shown is a new, proposed formula (e.g. % of `FailureMode`s with at least one `RiskEvaluation`), not an existing computation, so render as static/placeholder until a specific formula is decided and implemented as a real aggregate.
- "Last Updated" cell: unconfirmed — the real `project_list.html` already renders a `row.last_updated` value today, so if an equivalent timestamp field is confirmed to exist, this is (a) real; otherwise treat as (c) placeholder pending confirmation.
- Row "open"/"edit" actions: (a) real — ordinary navigation into the existing detail/update views for `FMEA`/`FMEAProject`. The "..." overflow menu's contents are not specified by the mockup and cannot be bound to anything until its actions are defined.
- "+ New Project": (a) real — creates an `FMEAProject` via the existing `fmea:create_project` form/view.
- "Import": (a) real — the existing `fmea_review:session_list` XLSX-ingestion flow already provides this.
- "Reports"/"Templates": (c) no report-generation or template-library entity exists — placeholder.

**Filtering/interaction**: "Filters" should be built as this app's one real filtering pattern — a server-side GET form with `<select>` inputs (Type/Status/Owner) and a submit button, following `risk_matrix.html`'s `method` selector exactly — not as client-side/AJAX filtering or a live-updating drawer. The FMEA-type stat cards, if made clickable as filter shortcuts (as the source spec suggests they visually imply), should link to this same GET-form URL with the relevant query parameter pre-set, not trigger any JS.

**Sidebar entry**: "FMEA Projects" already exists as the second item in the sidebar's first (ungrouped) section, pointing at `fmea:project_list` — no new sidebar entry is needed; this mockup redesigns the destination page, not its nav placement. Per the canonical grouping used across these mockups, it would sit under "FMEA WORKSPACE" once that named group exists.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 06 — FMEA Team: GUI Coding Requirements

### 1. Features & Content

1. View a project-scoped roster of FMEA team members (currently scoped to "Project: New Headlamp X1").
2. See four summary counts at a glance: total members, administrators, FMEA leaders, contributors.
3. Browse each member's identity, job-title role, FMEA-specific role badge, number of projects they're on, status, and last-active timestamp in a table.
4. Reference a static legend panel explaining what each of the five FMEA role labels means.
5. Add a new member to the project team (button only, no form shown).
6. Edit a member row or open a per-row action menu (pencil + "…" icons, no destination shown).
7. Open a separate "Roles & Permissions" area (button only, no destination shown).
8. Export the roster and filter the table (buttons only, no destinations/behavior shown).

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- "Open FMEA" / "Open-EQMS Family" logo lockup with pinwheel icon — repeats the app-shell header established across the whole app (same as mockup-01 base shell).
- Sidebar-collapse hamburger icon — repeats existing pattern, tied to the sidebar-collapse toggle already in `app.js`.
- Page title "FMEA Team" + subtitle "Manage team members, roles and permissions." — repeats the standard page-header pattern.
- "Project: New Headlamp X1" dropdown selector (top right) — repeats existing header-chrome pattern seen elsewhere in the app.
- "Search (Ctrl+K)" box with magnifier icon — repeats existing header-chrome pattern; no live/AJAX behavior implied here, just the box itself.
- Notification bell with unread-dot badge — repeats existing header-chrome pattern.
- Help icon (circle "?") — repeats existing header-chrome pattern.
- User avatar "JD" (purple circle) — repeats existing header-chrome pattern, but is also the first appearance of the initials-avatar visual used again for row owners on this page — see "new pattern" note below.

**Sidebar**
- "FMEA WORKSPACE" group: Home, FMEA Projects, FMEA Team (active/highlighted) — repeats `.nav-group`/`.nav-link` pattern.
- "CONTEXT (from Open-EQMS)" group: "System / Product / Process" (chevron, expandable) with four indented sub-items (System Characteristics Base, Characteristics Flow / Diagram, Process Flow, Process Characteristics) — repeats existing `.nav-group` pattern; the expand/collapse chevron behavior is shared across this whole mockup batch, not new to this page specifically.

**KPI row (4 cards)**
- `.stat-tile.span-3` × 4: Total Members (18, "Active users"), Administrators (3, "System administrators"), FMEA Leaders (5, "FMEA project leaders"), Contributors (10, "Team contributors") — each with a small colored icon badge. Repeats the existing `.stat-tile`/`.stat-label`/`.stat-value`/`.stat-detail` pattern exactly (4 × span-3 = 12 columns, fits the grid cleanly).

**Action toolbar row** (right-aligned, above table)
- "+ Add Member" solid button, "Roles & Permissions" outline button (doc icon), "Export" outline button (download icon), "Filters" outline button (filter icon) — repeats existing `.button`/`.button-row`/`.toolbar` pattern.

**Main table** (left, ~70% width)
- `.table-shell` wrapping a `<table>` with columns: Name, Email, Role, FMEA Role, Projects, Status, Last Active, Actions — repeats the existing table pattern.
- Per-row initials avatar (colored circle, e.g. "JD" purple, "MK" green) next to Name — **new pattern**: no avatar/initials-badge CSS class exists in today's vocabulary; needs a new small class (e.g. `.avatar-badge`) with a rotating background-color set.
- "FMEA Role" pill (FMEA Leader / Contributor / PM-FMEA Responsible, each a distinct pastel color) — closest existing pattern is `.status`/`.status-*`, but none of today's defined modifiers match these values; needs new `.status-*` (or a parallel `.badge-*`) modifier set.
- "Status" pill ("Active", green) — reuses the `.status`/`.status-*` pattern; needs a new modifier (no `.status-active` is currently defined in the enumerated class list).
- Row actions: pencil icon (edit) + "…" overflow icon — pencil repeats `.icon-button` pattern; the "…" opening a dropdown action menu is a **new interaction pattern** (no dropdown-menu JS exists in `app.js` today).
- No pagination control is visible in this crop even though the KPI card implies 18 total members.

**Right-side reference panel** ("Team Roles", ~25% width)
- Heading "Team Roles" + five rows, each an icon + bold role name + one-line description (Administrator, FMEA Leader, PM-FMEA Responsible, Contributor, Viewer) — reuses `.panel`/`.panel-heading` and a list pattern close to `.related-list`; the colored icon-per-role visual is the same **new** icon-badge pattern flagged for the table's FMEA Role pills — it should share one implementation, not two.

No footer status bar is visible in this mockup crop.

### 3. GUI Coding Requirements

**Route + template**: `fmea:fmea_team` → `django_app/fmea_app/templates/fmea_app/fmea_team.html`.

**Layout structure**: `.app-shell` with the standard `.sidebar` (`.sidebar-nav` > `.nav-group` × 2) and `.workspace`/`.content-shell`. Inside `.content-shell`: a page-header block (title/subtitle), a `.grid` of four `.stat-tile.span-3`, a `.toolbar`/`.button-row` for the four action buttons, then a `.split` with the `.table-shell` on the wide side and a `.panel` (Team Roles) on the narrow side, matching the `.span-*` column system already in use elsewhere.

**New patterns needed** (no existing equivalent):
- Initials-avatar badge — new `.avatar-badge` CSS class (colored circle + centered initials text), reused for the header user avatar, table rows, and (in later mockups) owner fields throughout the app.
- Row overflow ("…") action menu — a small new vanilla-JS dropdown toggle in the same minimal style as `app.js` (show/hide a `<ul>` on click, close on outside-click), plus new CSS for the menu panel. No AJAX; the menu's items would be plain links/form-submits.
- FMEA Role and Status pill color variants — new `.status-*` modifier classes for values not in today's enumerated set (`fmea_leader`, `contributor`, `pm_fmea_responsible`, `active`, etc.).

**Per-widget data binding**:
- Name — binds to real `ProjectMembership.user` (Django auth user), already available.
- Email — binds to real `User.email` (Django's built-in field), already available, just not yet surfaced in any template.
- Role (job title, e.g. "Quality Engineer") — binds to real `ProjectMembership.role`, already available.
- Total Members KPI (18) — binds to a computed aggregate: `count(ProjectMembership.objects.filter(project=<project>))`.
- Administrators / FMEA Leaders / Contributors KPIs (3 / 5 / 10) — computed aggregates grouping `ProjectMembership.role` by value; this assumes the roster is populated with a consistent set of role strings, which nothing currently enforces (`role` has no choices/enum today).
- Projects column (per-member count) — computed aggregate: count of `ProjectMembership` rows for that user.
- FMEA Role badge — no real data source yet; `ProjectMembership` has only one `role` field today, and this column shows a second, distinct role-like value. Render as static/placeholder content until either a second field (e.g. `ProjectMembership.fmea_role`) or a separate entity exists.
- Status column — no real data source yet; no status/active-flag field is defined on `ProjectMembership` (Django's `User.is_active` is a real, close field, but it's a single boolean and the mockup implies more states). Placeholder until a status field exists.
- Last Active column — no real data source yet; no activity-tracking field exists on `ProjectMembership` or `User` beyond `last_login`. Placeholder until that instrumentation exists.
- Team Roles reference panel and "Roles & Permissions" button — no real data source yet; there is no role/permission-capability catalog model anywhere today. Render as static content until such a catalog entity exists.
- Row actions (pencil/"…") and "+ Add Member" — the underlying create/edit operations target real `ProjectMembership` rows (project, user, role), so the CRUD forms themselves can be built now; only the FMEA Role/Status/Last Active fields inside those forms would need the new fields above before they can be saved meaningfully.

**Filtering/interaction**: "Filters" button opens a GET-form panel with `<select>`s (e.g. by Role, FMEA Role, Status) submitted to this same route, matching the app's one filtering pattern (server-side GET + full reload) — no client-side filtering.

**Sidebar entry**: Already present under "FMEA WORKSPACE" as "FMEA Team" — no new nav group needed.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 07 — System / Product / Process: GUI Coding Requirements

### 1. Features & Content

1. Browse a hierarchical tree of systems and subsystems for the current project (System Hierarchy panel).
2. Browse the same systems as a flat table with code, type, parent, status, owner, and last-updated columns.
3. View full detail of a selected system, including a reference illustration image.
4. Switch between three parallel views — Systems, Products, Processes — via a tab strip; Products and Processes are implied to reuse the same tree/table/detail layout shape.
5. Create a new system, import/export the list, and filter it (buttons present, no destinations shown).

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- "Open FMEA" / "Open-EQMS Family" logo + hamburger icon — repeats the app-shell header pattern.
- Page title "System / Product / Process" + subtitle "Define and manage systems, products and processes from Open-EQMS." — repeats standard page-header pattern.
- Top-right action buttons: "+ New System" (solid), "Import", "Export", "Filters" (outline) — repeats existing `.button`/`.button-row` pattern. Note: unlike mockups 06/08/09/10, this crop shows no project selector, search box, notification bell, help icon, or user avatar — treat that as this specific screenshot, not a confirmed different header contract.

**Tab strip**
- "Systems" (active, blue underline), "Products", "Processes" — closest existing analog is the `.process-step`/`.process-steps` link-based step-nav, but that pattern shows numbered steps, not an underline-tab look. **New pattern**: needs new tab-styling CSS (underline-active state) layered on the same "plain links, full page reload" mechanic as `.process-steps` — not a client-side JS panel swap.

**Sidebar**
- "FMEA WORKSPACE": Home, FMEA Projects, FMEA Team.
- "CONTEXT (from Open-EQMS)": "System / Product / Process" (active, chevron expanded), same four sub-items as mockup-06. Repeats existing `.nav-group` pattern.

**"System Hierarchy" tree panel (left, ~20%)**
- Heading "System Hierarchy".
- Indented tree: "Headlamp X1 System" (root, folder icon, selected/highlighted) with 5 children (Electrical, Housing, Optical, Thermal, Mounting System), each with a folder icon. **New pattern**: no tree/indented-hierarchy component exists anywhere in the current CSS vocabulary (closest is `.related-list`, which is flat, not nested). Needs a new class family (e.g. `.tree-panel`, `.tree-node`, `.tree-node-active`) for indentation and a selected-state highlight.

**"Systems" table (center, ~50%)**
- `.table-shell` with columns: System Name, Code, Parent System, Status, Owner, Last Updated, Actions — repeats existing table pattern.
- Status pill (Active = green, Review = purple/lavender) — reuses `.status`/`.status-*` pattern; "Review" needs a new modifier (not in today's enumerated set).
- Owner avatar (initials circle, e.g. "JD", "AN") — reuses the initials-avatar pattern flagged as new in mockup-06.
- Row actions: pencil + "…" — reuses the pencil/overflow-menu pattern flagged as new in mockup-06.

**"System Details" panel (right, ~30%)**
- Heading "System Details".
- Field list: System Name, Code, Type, Status (badge), Owner, Description, Created, Last Updated — reuses the existing `.panel`/`.attribute-table` field-list pattern (same shape as `.cell-detail` usage elsewhere).
- Embedded reference image (gray-toned technical illustration) inside a bordered frame — **new pattern**: no image/attachment display exists anywhere in the app today; this requires both new markup (an image frame element) and, to be real, a file/image storage subsystem that doesn't exist.

No footer status bar is visible in this mockup crop.

### 3. GUI Coding Requirements

**Route + template**: `fmea:system_product_process` → `django_app/fmea_app/templates/fmea_app/system_product_process.html`, with the active tab selected by a `?tab=systems|products|processes` GET parameter (server-rendered, full reload per tab — consistent with this app's pattern; no client-side tab-panel-swap JS).

**Layout structure**: `.app-shell` shell as usual. Inside `.content-shell`: page header, action `.button-row`, new tab-strip nav, then a three-column `.grid` (`.span-3` tree panel, `.span-6` table, `.span-3` detail panel — proportions approximate the ~20/50/30 split shown).

**New patterns needed** (no existing equivalent):
- Underline tab strip — new CSS on top of the existing link-based nav mechanic (see above).
- Hierarchy tree widget — new `.tree-panel`/`.tree-node` classes for indentation + a selected-node highlight; since the app avoids client JS beyond theme/sidebar/nav-highlighting, the tree can render fully expanded server-side (no expand/collapse JS needed) unless collapsing individual branches is required, in which case a small new vanilla-JS toggle (mirroring the sidebar-collapse pattern) would be needed.
- Image display frame in the detail panel — new CSS only for the frame; the image itself needs a new file/attachment storage subsystem before it can hold real content (none exists in the app today).
- Owner avatar — reuses the new `.avatar-badge` class introduced in mockup-06's requirements.

**Per-widget data binding**:
- Entire "System Hierarchy" tree, and the System Name/Code/Type/Parent/Status/Owner/Description/Image fields — no real data source yet: no `System` model exists anywhere in the codebase. Everything on this page under the "Systems" tab renders as static/placeholder content until a `System` entity (with at least `name`, `code`, `type`, self-referential `parent`, `status`, `owner`, `description`) exists.
- "Products" tab — Name/Description/Part Number bind to real `Product.name` / `Product.description` / `Product.part_number`, already available. The hierarchy tree, Status badge, Owner, and Parent-System column shown for this tab are not real: `Product` has no System link, no status field, and no owner field today — placeholder until those are added.
- "Processes" tab — Name/Description/Code bind to real `Process.name` / `Process.description` / `Process.process_code`, already available. Same gaps as Products: no System link, status, owner, or hierarchy fields exist on `Process` today — placeholder until added.
- Owner avatar (any tab) — no real data source yet; no owner-assignment field exists on `Product`, `Process`, or (since it doesn't exist) `System`.
- Status badge (Active/Review) — no real data source yet; no status field or review workflow exists on any of these models today.

**Filtering/interaction**: "Filters" button would open a GET-form panel with `<select>`s submitted to this route, matching the app's one filtering pattern — no client-side filtering. Clicking a tree node would be a plain link (`?system_id=...`) that reloads the page with that node selected, not an AJAX partial update.

**Sidebar entry**: Already present under "CONTEXT (from Open-EQMS)" as "System / Product / Process" — no new nav group needed.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 08 — System Characteristics Base: GUI Coding Requirements

### 1. Features & Content

1. Browse a searchable, paginated catalog of system characteristics (142 total) in a dense table.
2. See six summary KPIs at a glance (total, critical, monitored, linked-to-FMEA, organizations, last updated).
3. Re-slice the same catalog via seven tabs (All / By System / By Type / By Category / By Importance / By Monitoring / By FMEA Link).
4. Filter the table via a search box plus five dropdowns (System, Type, Category, Importance, Monitoring) and a "More Filters" expansion.
5. View full detail of a selected characteristic in a side panel (spec reference, description, monitoring method, who last updated it).
6. Jump from a characteristic's "Linked to FMEA" count to the FMEA(s) that reference it.
7. View four aggregate breakdown panels at the bottom (three donuts + one ranked bar list).
8. Create a new characteristic, import/export the list (buttons present, no destinations shown).
9. View a characteristic's full change history (button present, no destination shown).

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Logo lockup, hamburger, page title "System Characteristics Base" + subtitle, project selector, search box, notification bell with "0" badge, help icon, avatar "JD" — all repeat the standard app-shell header pattern (same as mockup-06).
- Action buttons: "+ New Characteristic" (solid), "Import" (outline), "Export" (outline, dropdown chevron), "Filters" (outline, dropdown chevron) — repeats `.button-row` pattern; the dropdown-chevron variant on Export/Filters is a minor new affordance (an outline button that opens a small menu instead of navigating) — same new dropdown-menu mechanic flagged in mockup-06's "…" overflow action.

**Sidebar (fuller than mockups 06/07)**
- "FMEA WORKSPACE": Home, FMEA Projects, FMEA Team.
- "CONTEXT (from Open-EQMS)": System / Product / Process (expanded), with "System Characteristics Base" active.
- "FMEA ANALYSIS": DFMEA, PFMEA, System FMEA, Preventive FMEA (PM-FMEA).
- "VALIDATION & CHANGE": Validation Trajectory, Evidence & Tests, Change Impact — this nav group does not exist in the app today and would need to be added to the shared sidebar template (a page-shell change, not specific to this page).
- "ANALYSIS": AP / Detection, Risk Matrix, XDA Investigations.
- "Collapse" control at bottom — repeats existing sidebar-collapse behavior already in `app.js`.

**KPI row (6 cards)**
- `.stat-tile.span-2` × 6: Total Characteristics (142), Critical Characteristics (28, "19.7% of total"), Monitored Characteristics (96, "67.6%"), Linked to FMEA (118, "83.1%"), Organizations (3, "Sources"), Last Updated (12 May 2025 / 10:30) — repeats the `.stat-tile` pattern (6 × span-2 = 12, fits the grid cleanly, denser than mockup-06's 4-card row).

**Tab strip**: "All Characteristics" (active), "By System", "By Type", "By Category", "By Importance", "By Monitoring", "By FMEA Link" — same new underline-tab styling flagged in mockup-07, applied here with 7 tabs instead of 3.

**Filter/toolbar row**
- Search box "Search characteristics..." — plain text input in a GET form, not a live/AJAX search.
- Dropdowns: System ("All Systems"), Type ("All Types"), Category ("All Categories"), Importance ("All"), Monitoring ("All") — all repeat the existing GET-form `<select>` filter pattern.
- "More Filters" button (sliders icon) — implies an expandable panel of additional GET-form fields; can be built as a collapsible `.panel` section (new small vanilla-JS show/hide toggle, same minimal style as `app.js`), still submitting via the same GET form.

**Main table**
- Checkbox column (row select) — **new pattern**: no bulk-select/checkbox-column precedent exists in today's CSS vocabulary; would need a new "select all" header checkbox plus a small vanilla-JS toggle to check/uncheck all rows (no AJAX — any bulk action would still be a normal form POST over the checked IDs).
- Columns: Characteristic ID (sortable, blue link text), Characteristic Name, System / Subsystem, Type, Category, Importance (color pill), Monitoring (color pill), Nominal Value / Target, Unit, Linked to FMEA (blue link text), Last Updated, Actions (pencil + "…") — table body repeats `.table-shell` pattern; Importance/Monitoring pills reuse `.status`/`.status-*` (new modifiers needed, as in mockup-06/07); Actions reuse the pencil/overflow pattern from mockup-06.
- Sortable column header (ID column has a sort arrow) — **new pattern**: no column-sort affordance exists elsewhere in the app; if built, sorting would be a plain link toggling a `?sort=` GET parameter (full reload), not client-side JS sort.

**Pagination footer**
- "Showing 1 to 8 of 142 characteristics" + page-number links (« 1 2 3 4 5 … 18 ») — **new pattern**: no pagination component exists elsewhere in the app today. Buildable with Django's built-in `Paginator` and plain `?page=` links, no JS needed.

**Detail panel (right)**
- Heading "Characteristic Details", ID + status pill, then a field list (Characteristic Name, System / Subsystem, Type, Category, Importance badge, Nominal Value / Target, Unit, Monitoring Method, Specification / Reference, Linked to FMEA link, Description, Last Updated, Updated By avatar) — reuses the existing `.panel`/field-list pattern from mockup-07's "System Details" panel.
- "View Full History" button (outline, clock icon) — button itself reuses `.button`; its destination (a history/audit view) does not exist.

**Bottom analytics row (4 panels, full width)**
- Three donut charts ("Characteristics by Importance", "Characteristics by Type", "Monitoring Status"), each with a center total label and a colored-dot legend with counts/percentages — **new pattern**: this is the first real usage anywhere in the app of the just-decided Chart.js donut type (vendored locally, not yet wired into any page).
- One ranked horizontal bar list ("Top Systems": Optical 58, Electrical 32, Housing 20, Mounting 16, Thermal 10, Other 6, then a Total row) — can be built either as a simple CSS/HTML bar-list (no chart library, just styled `<div>` bars sized by percentage) or as a Chart.js horizontal bar; the plain CSS approach is simpler and matches the "no framework" spirit better for a static ranked list like this.

**Footer status bar**
- "Database: OpenEQMS_Local" | "User: Janez Demo (Quality Engineer)" | "Role: Project Owner" | "Workspace: Global" | "Version: 1.0.0" | "System Status" (green dot) — **new pattern**: no footer status bar exists in mockups 06/07's crops. Mostly static/environment chrome; would be a new shared template partial if reused across other "VALIDATION & CHANGE"/"ANALYSIS" pages.

### 3. GUI Coding Requirements

**Route + template**: `fmea:system_characteristics_base` → `django_app/fmea_app/templates/fmea_app/system_characteristics_base.html`.

**Layout structure**: `.app-shell` shell; `.content-shell` with page header, a `.grid` of six `.stat-tile.span-2`, new tab-strip nav, a `.panel.compact` GET-filter row, then a `.split` (`.table-shell` ~span-8 + detail `.panel` ~span-4), a new pagination block below the table, a full-width `.grid` of four chart/list panels, and a new footer-status-bar partial.

**New patterns needed** (no existing equivalent): "VALIDATION & CHANGE" sidebar nav group (shared shell change); underline tab strip (7-way, same mechanic as mockup-07); checkbox bulk-select column with "select-all" toggle (new small JS); sortable column header (plain-link, no JS); pagination component (Django Paginator + links, no JS); first real Chart.js donut usage (three instances) plus a plain CSS ranked-bar list; footer status bar partial.

**Per-widget data binding**:
- Characteristic Name, Description — bind to real `ProductCharacteristic.name`/`.description` and/or `ProcessCharacteristic.name`/`.description`, already available, though neither model is scoped as a unified "system characteristic" the way this table implies.
- Total Characteristics / Critical / Monitored / Linked to FMEA / Last Updated KPIs — no real data source yet: there is no unified System Characteristics entity spanning `ProductCharacteristic`/`ProcessCharacteristic`, and the Critical/Monitored breakdowns further depend on the Type/Category/Importance/Monitoring classification described below, which is not backed by an approved model. Render as static/placeholder until that entity and classification scheme exist.
- Organizations KPI (3, "Sources") — no real data source yet; no multi-organization/tenancy model exists anywhere in the codebase.
- System / Subsystem column — no real data source yet; no `System` model exists (see mockup-07) and neither characteristic model has a system-like FK.
- Type / Category / Importance / Monitoring columns and their tabs/donuts — no real data source yet; `ProductCharacteristic.primary_classification_id` exists as a field but is explicitly not backed by any approved `ClassificationScheme`/`ClassificationTerm` model, so there is no real controlled-vocabulary data behind these columns today.
- Nominal Value / Target, Unit — no real data source yet; neither characteristic model has a dedicated structured field for this (`ProcessCharacteristic.attributes` is a generic JSONField that could hold it, but nothing populates it that way today).
- Linked to FMEA count/link — binds to a computed aggregate over the real relationship chain `ProductCharacteristic.requirement` → `Requirement.function` → `Function` → failure-mode/action data, once the base characteristic entity above is real; until then there is nothing consistent to count.
- Monitoring Method, Specification / Reference, Updated By, Last Updated (detail panel), "View Full History" — no real data source yet; none of these fields exist on either characteristic model, and no audit/change-history model exists anywhere.
- Bottom donuts and Top Systems bar list — bind to computed aggregates (GROUP BY/COUNT), but only once their underlying Type/Category/Importance/Monitoring/System fields above are real; currently placeholder.
- Footer status bar "User" / "Role" — bind to real `request.user` and `ProjectMembership.role`. "Database" / "Workspace" / "Version" / "System Status" — no real data source yet, purely informational chrome with no confirmed backing.

**Filtering/interaction**: Search box + System/Type/Category/Importance/Monitoring dropdowns submit as a single GET form to this route (server-side filter + full reload), matching the app's one filtering pattern; "More Filters" expands additional fields in the same form, not a separate AJAX request.

**Sidebar entry**: Already present under "CONTEXT (from Open-EQMS)" as "System Characteristics Base." This page's own sidebar crop additionally reveals the "VALIDATION & CHANGE" group, which does not exist yet and would need to be added once its member pages (mockups 10/13/14) are built.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 09 — Characteristics Flow / Diagram: GUI Coding Requirements

### 1. Features & Content

1. Browse a searchable, filterable list of characteristics as candidate graph nodes (checkbox table, 142 total).
2. Visualize relationships between characteristics as an interactive force-directed graph, radiating outward from one selected root node.
3. Inspect a selected relationship's detail: from/to characteristic, relationship type, strength, link type (manual/auto), matched rule, creator.
4. See seven summary KPIs about links (total/linked characteristics, manual links, auto links, critical links, warnings, last validated).
5. See a link-statistics breakdown panel (manual/auto totals, impact-level totals, orphan count) with a jump to orphaned characteristics.
6. Configure and trigger an automatic/rule-and-AI-assisted link-suggestion engine, with an optional manual-review queue before links are committed.
7. Switch between four views of the same underlying link data via tabs (Link Matrix, Link Network, Link Rules, Impact Paths) — this screen shows the Link Network view.
8. Adjust graph presentation controls: view-mode toggle, layout algorithm, traversal depth, an importance/strength threshold slider, and zoom/pan/lock.
9. Reference legends for relationship-type codes (Drives/Influences/Affected By/Constrained By/Supports/Required By), importance levels, and characteristic type/category codes.
10. Create a new link manually and run a validation check over existing links (buttons present, no destinations shown).

### 2. Full Wireframe Widget Checklist

**Header/Chrome**: logo, hamburger, page title "Characteristics Flow / Diagram" + subtitle, project selector, search box, notification bell "0", help icon, avatar "JD" — repeats the standard header (same as mockups 06/08). Action buttons: "+ New Link" (solid), "Auto Link" (outline), "Validate" (outline), "Options" (outline, chevron), "Filters" (outline, chevron) — repeats `.button-row` pattern.

**Sidebar**: same groups as mockup-08 (FMEA WORKSPACE, CONTEXT — "Characteristics Flow / Diagram" active, FMEA ANALYSIS, VALIDATION & CHANGE, ANALYSIS), "Collapse" at bottom.

**KPI row (7 cards)**: Total Characteristics (142), Linked Characteristics (118, 83.1%), Manual Links (36, 30.5%), Auto Links (82, 69.5%), Critical Links (24), Warnings (7), Last Validated (12 May 2025 / 10:25) — repeats `.stat-tile` pattern, but 7 cards do not divide evenly into the existing 12-column span system (unlike the 4-card and 6-card rows in mockups 06/08). Would need either a wrapped two-row layout, narrower cards via a new `.span-*` variant, or a horizontally-scrolling row — a small new layout accommodation, not a new component.

**Tab strip**: "Link Matrix" (implied grid/matrix view, not shown here), "Link Network" (active — this screen), "Link Rules" (implied rules editor), "Impact Paths" (implied critical-path view) — same new underline-tab pattern flagged in mockups 07/08.

**Left "Characteristics List" panel**
- Toolbar: "View:" segmented icon-toggle (grid/frame icon, network icon [selected], list icon) + chevron — **new pattern**: no segmented-toggle-button component exists today; would need new CSS (a button group with an active state) and a small vanilla-JS click handler to swap the `?view=` GET parameter (still a full reload, not a live panel swap).
- "Layout:" dropdown ("Auto (Force)"), "Depth:" dropdown ("3 Levels") — reuse the GET-form `<select>` pattern.
- Row of 5 colored dots + a threshold slider + arrow icon (importance/strength filter) — **new pattern**: no range-slider control exists anywhere in the app; would need a new styled `<input type="range">` submitted via the same GET form (on blur/submit, not live-drag filtering, to stay consistent with the app's no-AJAX rule).
- Search box "Search characteristics...", "Type: All" / "Category: All" dropdowns, "More Filters" link — reuses the GET-form filter pattern from mockup-08.
- Table: checkbox, ID, Characteristic (CR), Type, Category, Importance — reuses `.table-shell` and the checkbox-column pattern flagged as new in mockup-08; Type/Category render as small colored icon-badges (reuses the new avatar/icon-badge pattern from mockup-06); Importance renders as a single colored dot (reuses `.status-*` color language).
- Pagination "Showing 1 to 15 of 142" — reuses the new pagination pattern from mockup-08.

**Center "Link Network" graph canvas**
- Zoom in/out, fit-to-screen, lock icons (left edge) — **new pattern**, no canvas-control precedent anywhere in the app.
- Force-directed graph: one highlighted center node (selected characteristic) with straight labeled edges radiating to up to 7 surrounding nodes, each with its own colored icon and a two-line label (code / short name); edges carry short relationship-code pill labels (DR/IN/AF/CO/SUP/REQ). **This is the single largest new-pattern item in this entire mockup batch — there is zero precedent anywhere in this app for a graph/node-and-edge canvas of any kind.**
- Relationship-type legend strip below the canvas (DR/IN/AF/CO/SUP/REQ + full words) — new small legend component, similar in spirit to a `.risk-matrix-legend` but for a different code set.

**Right stacked panels**
- "Link Details" panel (From, To, Relationship badge, Strength dot+text, Link Type, Rule Matched, Created, Created By avatar) — reuses the existing `.panel`/field-list pattern.
- "Impact / Importance" panel (Path Impact badge, Risk Propagation, Critical Path indicator, Recommendations text) — reuses the same field-list pattern.
- "Link Statistics" panel (Total/Manual/Auto/High/Medium/Low Impact Links, Orphan Characteristics count, "View Orphans" button) — reuses the field-list + `.button` pattern.
- "Importance" legend panel (5 colored dots: Critical/High/Medium/Low/None) — reuses the small legend pattern.

**Below-the-fold row (2 panels, full width)**
- "Legend (Types)" panel — two groups of icon+code+label pairs (SPC/LEG/SAFE/CRT, then a "Functional" sub-group of OPT/MEC/ELE/SW/CHE/DEC) — reuses the small legend/icon-badge pattern; note the mockup itself shows an apparent code/label mismatch (MEC labeled "Electrical"; both CHE and DEC labeled "Chemical") that should be re-verified against source content before being treated as ground truth, rather than silently corrected.
- "Auto Link Options" panel — "Linking Mode" dropdown ("Smart (Rules + AI)"), "Max Depth" dropdown, "Min Confidence" dropdown, "Relationship Types" dropdown, "Create Manual Review Queue" toggle (with two avatar icons), "Generate / Update Links" button — dropdowns/button reuse existing form/button patterns; the on/off toggle switch is a **new pattern** (no toggle-switch component exists today, only checkboxes/selects) and would need new CSS plus, if it needs to visually animate, minimal new JS (a plain checkbox styled as a switch works without JS).

**Footer status bar**: same as mockup-08 (Database/User/Role/Workspace/Version/System Status) — new pattern first flagged there.

### 3. GUI Coding Requirements

**Route + template**: `fmea:characteristics_flow_diagram` → `django_app/fmea_app/templates/fmea_app/characteristics_flow_diagram.html`, with the active tab selected by a `?tab=link_matrix|link_network|link_rules|impact_paths` GET parameter (server reload per tab, no client panel-swap).

**Layout structure**: `.app-shell` shell; `.content-shell` with page header, a wrapped/scrolling `.grid` of seven `.stat-tile`, new tab strip, then a three-column working area (`.span-3` Characteristics List, `.span-6` graph canvas, `.span-3` stacked right panels), a full-width `.grid` of two panels below the fold (Legend/Auto Link Options), and the footer status bar partial.

**New patterns needed, explicitly** (this mockup needs more of these than any other in the batch):
- **Force-directed graph canvas** — no precedent anywhere in the app. Chart.js (recently decided, vendored locally) explicitly does not cover force-directed graphs, only line/bar/donut. Building this would require vendoring a separate, dedicated graph-rendering library locally (consistent with how Chart.js was vendored, not loaded from a CDN) plus substantial new vanilla JS to: initialize the canvas, compute or receive node/edge layout, render node/edge/label markup, and handle node click-to-select, zoom, pan, and layout lock. None of this exists in `app.js` today, whose only behaviors are theme toggle, sidebar collapse, and active-nav-link highlighting.
- **Segmented view-toggle control** — new CSS button-group + a small click handler to switch the `?view=` GET parameter.
- **Range-slider filter control** — new styled `<input type="range">`, submitted through the existing GET-form mechanic (not live-drag AJAX filtering).
- **Toggle switch** ("Create Manual Review Queue") — new CSS on a checkbox input; no JS required unless animation is desired.
- Checkbox bulk-select column, pagination, tab strip, footer status bar — same new patterns already flagged in mockups 07/08, reused here.

**Per-widget data binding**: nothing on this page maps to a real, already-built field or aggregate. Every widget below renders as static/placeholder content until the listed new backend piece exists:
- Characteristics List table (ID, Characteristic, Type, Category, Importance) — no real data source yet; same gap as mockup-08 (no unified System Characteristics entity, and Type/Category/Importance depend on the not-yet-approved `ClassificationScheme`/`ClassificationTerm` model). The `CR-###` ID scheme itself is not confirmed to map to `ProductCharacteristic`/`ProcessCharacteristic` as they exist today.
- The entire Link Network graph, Link Matrix/Link Rules/Impact Paths views, and all relationship types (Drives/Influences/Affected By/Constrained By/Supports/Required By) — no real data source yet; no relationship/edge entity for characteristics exists anywhere. `CauseInfluence` (the built Ishikawa backend) is a different, narrower model and is not a substitute. A new entity (e.g. a proposed `CharacteristicLink`, with `from_characteristic`, `to_characteristic`, `relationship_type`, `strength`, `link_type`, `rule_matched`, `created_at`, `created_by`) would be needed before any of this could hold real data.
- "Auto Link" / "Auto Link Options" panel (Linking Mode, Min Confidence, Rule Matched values) — no real data source yet; no rules engine and no AI-assisted link-suggestion/confidence-scoring capability exists anywhere in the codebase.
- KPI row (Total/Linked/Manual/Auto/Critical Links, Warnings, Last Validated) and "Link Statistics" panel — bind to a computed aggregate over the proposed `CharacteristicLink`-equivalent entity above, but only once that entity exists; currently there is nothing to count.
- "Warnings" count and "Validate" button — no real data source yet; imply a data-quality/consistency-check rule engine that does not exist.
- Legend panels (relationship types, importance, type/category codes) — static reference content; can render now as fixed legend data, independent of whether the underlying model exists, though the codes should match whatever entity is eventually approved.
- Footer status bar "User"/"Role" — bind to real `request.user` / `ProjectMembership.role`; the rest of the footer is placeholder, as in mockup-08.

**Filtering/interaction**: Search box, Type/Category dropdowns, Layout/Depth dropdowns, and the threshold slider all submit through one GET form to this route (server-side filter + full reload) — no client-side/AJAX filtering, and no live graph re-layout on drag beyond what the vendored graph library itself renders once the page has loaded with a given node/edge dataset.

**Sidebar entry**: Already present under "CONTEXT (from Open-EQMS)" as "Characteristics Flow / Diagram" — no new nav group needed (VALIDATION & CHANGE, shown in this page's sidebar crop, is the same not-yet-existing group flagged in mockup-08, needed regardless of this specific page).

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 10 — Evidence & Tests: GUI Coding Requirements

### 1. Features & Content

1. Browse a searchable, paginated catalog of validation tests/evidence items (48 total), each tied to a DFMEA Function/Failure Mode pair.
2. See seven summary KPIs about the test pipeline (total, planned, in execution, completed, linked-to-DFMEA, overdue, last updated).
3. Re-slice the same catalog via five tabs (All / By DFMEA Item / By Test Type / By Status / By Priority).
4. Filter the table via a search box plus six dropdowns (DFMEA Link, Test Type, Status, Priority, Responsible, Planned Date).
5. View full detail of a selected test/evidence record in a dismissible side panel: objective, method, nominal/target, acceptance criteria, measured result with pass/fail outcome, planned/executed dates, owner, and file attachments.
6. Jump from a test record to the underlying DFMEA item ("Open DFMEA Item" link) and view its file attachments.
7. View four aggregate breakdown panels at the bottom (status, test type, priority, DFMEA-link ratio).
8. Create a new evidence/test record, import/export the list (buttons present, no destinations shown).
9. View a test record's full change history (button present, no destination shown).

### 2. Full Wireframe Widget Checklist

**Header/Chrome**: logo, hamburger, page title "Evidence & Tests" + subtitle, "Project: Headlamp X1 - DFMEA" dropdown (note this combines project and FMEA-type in one label, unlike mockup-06/08's plain project name), search box, notification bell "0", help icon, avatar "JD" — repeats the standard header. Action buttons: "+ New Evidence / Test" (solid), "Import", "Export" (chevron), "Filters" (chevron) — repeats `.button-row` pattern.

**Sidebar** (a different grouping/order than mockups 08/09 — shown as-is, not reconciled across mockups):
- "FMEA WORKSPACE": Home, FMEA Projects, FMEA Team.
- "CONTEXT (from Open-EQMS)": all five context items.
- "FMEA PROJECT": DFMEA, PFMEA, System FMEA, Preventive FMEA (PM-FMEA).
- "FMEA ANALYSIS": Functions, Failure Modes, Effects, Causes, Prevention Controls, Detection Controls, Actions.
- "VALIDATION & CHANGE": "Evidence & Tests" (active), Validation Trajectory, Change Impact — the not-yet-existing nav group also flagged in mockups 08/09.
- "ANALYSIS": AP / Detection, Risk Matrix, XDA Investigations.

**KPI row (7 cards)**: Total Evidence / Tests (48), Planned (15, 31.3%), In Execution (12, 25.0%), Completed (16, 33.3%), Linked to DFMEA (44, 91.7%), Overdue (5, 10.4%), Last Updated (12 May 2025 / 10:25) — same 7-card layout accommodation flagged as new in mockup-09 (doesn't divide evenly into the 12-column span system).

**Tab strip**: "All Evidence / Tests" (active), "By DFMEA Item", "By Test Type", "By Status", "By Priority" — reuses the underline-tab pattern from mockups 07/08/09.

**Filter row**: Search box "Search...", dropdowns — DFMEA Link, Test Type, Status, Priority, Responsible, Planned Date (all "All") — plus "More Filters" button — reuses the GET-form filter pattern from mockup-08, with a Planned Date `<select>` that would likely need a date-range variant (still a plain form field, not a JS date picker, unless one is deliberately added).

**Main table**
- Checkbox column — reuses the new bulk-select pattern from mockup-08.
- Columns: ID, Evidence / Test Name, "DFMEA Link / Function / Failure Mode" (two-line cell: bold ID line + lighter descriptive line), Test Type (gray pill), Method, Status (pill), Priority (colored dot + text), Planned Date, Owner (avatar), Linked (icon), Actions.
- Two-line "ID + descriptive text" cell pattern — **new pattern**: no existing cell today combines a bold link-styled top line with a lighter secondary line; would need a small new `.cell-detail`-style two-line variant.
- Status pill (Completed=green, In Execution=blue, Planned=gray/lavender; donut legend also shows On Hold=orange, Cancelled=red) — reuses `.status`/`.status-*`, needs new modifiers.
- Priority (colored dot + text, not a pill) — reuses the dot-plus-text pattern already seen for Importance dots in mockups 08/09.
- Owner avatar — reuses the `.avatar-badge` pattern from mockup-06.
- "Linked" column (green chain-link icon) — reuses `.icon-button`-style iconography; new icon, not a new component.
- Row actions: link icon, eye icon, "…" overflow — **new pattern**: this extends mockup-06's pencil+overflow pair to three icons (link/eye/overflow); same `.icon-button`/`.inline-actions` CSS pattern, just more icons, no new component needed.

**Pagination footer**: "Showing 1 to 10 of 48 items" + page-number links + a "10 / page" page-size dropdown — reuses the pagination pattern from mockup-08, plus a **new page-size selector** (a `<select>` submitting `?page_size=` via the same GET form, no JS needed).

**Detail panel (right)** — "Evidence / Test Details", with an explicit "X" close icon top-right.
- Dismissible panel behavior — **new pattern**: mockups 07/08's detail panels are always-shown/static; this is the first panel in the batch with a visible close affordance, implying it can be hidden. Buildable with a small new vanilla-JS toggle (`el.hidden = true` on click, matching this codebase's stated toggle style), no framework needed.
- Field list: ID+Status badge, DFMEA Link (two-line), Test Type badge, Method, Objective, Nominal/Target, Acceptance Criteria, Result value + Pass/Fail badge, Planned Date, Executed Date, Owner avatar, "Evidence" (three small file-type icons + "3 files"), "Linked to DFMEA" ("Open DFMEA Item" link), Created (clock icon + date), Last Updated (link icon + date/by-name) — reuses the existing field-list `.panel` pattern for everything except:
- File-attachment icons (paperclip/document/PDF) + "3 files" — **new pattern**: no file/attachment display or upload exists anywhere in the app; would need new markup for a file-chip list and, to be real, a file-storage subsystem that doesn't exist.
- "View Full History" button — reuses `.button`; destination view does not exist.

**Bottom analytics row (4 panels)**: "Status Overview" donut, "By Test Type" donut, "By Priority" horizontal bar, "Linked to DFMEA" donut — reuses the Chart.js donut pattern and the plain-CSS/Chart.js bar option, both introduced in mockup-08. Note the mockup itself is inconsistent here: Test Type badges render as plain gray pills in the table but as color-coded segments in the donut legend — worth flagging as a design inconsistency to resolve (pick one color treatment), not something to silently "fix" without checking with source content.

**Footer status bar**: same pattern as mockups 08/09.

### 3. GUI Coding Requirements

**Route + template**: `fmea:evidence_and_tests` → `django_app/fmea_app/templates/fmea_app/evidence_and_tests.html`.

**Layout structure**: `.app-shell` shell; `.content-shell` with page header, wrapped `.grid` of seven `.stat-tile`, underline tab strip, GET-filter `.panel.compact`, `.split` (`.table-shell` ~span-8 + dismissible detail `.panel` ~span-4), pagination + page-size selector, full-width `.grid` of four chart/bar panels, footer status bar partial.

**New patterns needed**: dismissible detail panel (small new JS show/hide, first use of this behavior in the batch); two-line ID+description table cell; three-icon row-actions group (link/eye/overflow — extends mockup-06's pattern); page-size selector; file-attachment chip display (markup only — real files need a new storage subsystem); all patterns already flagged in mockups 07–09 (underline tabs, checkbox bulk-select, pagination, footer status bar, Chart.js donuts/bars) reused here.

**Per-widget data binding**:
- Baseline: today's `Evidence` model is only `FK to RecommendedAction, name, description, reference_uri`, and `EffectivenessVerification` is only `FK to RecommendedAction, result, verified_at`. Neither has a direct Failure Mode link, Test Type, Method, Objective, Acceptance Criteria, a Planned/Executed date pair, Priority, a person-Owner, a Status workflow, or file attachments — so nearly everything on this page needs a new, richer entity (referred to below as a proposed `ValidationTest`) rather than a reuse of these two models as they stand.
- Evidence/Test Name, Objective, Nominal/Target, Acceptance Criteria — no real data source yet; closest existing fields are `Evidence.name`/`.description`/`.reference_uri`, but those hang off `RecommendedAction`, not a Function/Failure Mode pair, and don't carry these as distinct structured fields.
- "DFMEA Link" (F-01/FM-01, two-line cell) — no real data source yet; `FailureMode.function` and `Function` are real models, but no field on `Evidence`/`EffectivenessVerification` links directly to a Failure Mode/Function pair today (the existing chain runs through `RecommendedAction`'s nullable `failure_mode`/`failure_cause` fields, which don't guarantee this pairing).
- Test Type, Method, Status (with On Hold), Priority — no real data source yet; none of these fields exist on `Evidence`, `EffectivenessVerification`, or `RecommendedAction`. Note `RecommendedAction.status` is a different, already-defined enum (open/in_progress/completed/verified/cancelled, no "on_hold" value) and should not be reused for this different concept.
- Planned Date / Executed Date — no real data source yet; `EffectivenessVerification.verified_at` is a single timestamp, not a planned/executed pair; `RecommendedAction.due_date` is a real but separate single-date field belonging to actions, not tests.
- Owner (named person + avatar) — no real data source yet; `RecommendedAction.responsible_role` is a FK to `ResponsibleRole`, which is a name/description catalog only, not a person/user roster — a genuine person-owner field does not exist today.
- Result value + Pass/Fail badge — `EffectivenessVerification.result` is a real field, but its shape isn't confirmed to support a numeric measured value plus a separate derived pass/fail classification; treat as a field that exists but needs new structure/validation before it can back this widget as shown.
- Evidence attachments (3 files) — no real data source yet; no file/attachment/document storage exists anywhere in the codebase, for this page or any other.
- Created, Last Updated, "by <name>", "View Full History" — no real data source yet; no audit-trail/change-history model exists for any of these entities today.
- "Linked" column / "Linked to DFMEA" / "Open DFMEA Item" link — binds to a computed aggregate (is the new direct Failure-Mode/Function FK populated), but only once that FK exists on the new entity; currently nothing to compute.
- KPI row and all four bottom charts — bind to computed aggregates over the proposed `ValidationTest`-equivalent entity, its Status enum, and its DFMEA-link FK, none of which exist yet; "Overdue" additionally needs a Planned Date-before-today plus Status-not-Completed comparison.
- Footer status bar "User"/"Role" — bind to real `request.user` / `ProjectMembership.role`; the rest is placeholder, as in mockups 08/09.

**Filtering/interaction**: Search box plus the six dropdowns submit as one GET form to this route (server-side filter + full reload), matching the app's one filtering pattern; the dismissible detail panel's open/close is the one piece of this page that is genuinely new client-side behavior (a plain visibility toggle, not data fetching).

**Sidebar entry**: Belongs under "VALIDATION & CHANGE," the same not-yet-existing nav group flagged in mockups 08/09; "Evidence & Tests" would be its active entry once that group is added.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 11 — DFMEA: GUI Coding Requirements

> **Scope note (read first):** A narrowed, real version of this screen's core table is already approved and instructed for implementation — `Codex_Instruction_DFMEA_PFMEA_Worksheets_SliceD.md` (status: approved 2026-09-04, not yet built). Slice D covers only the Tier A/B worksheet: a single read-only table at `/dfmea/`, reusing the existing `_build_worksheet_rows`/`_worksheet_row` view helpers unchanged, split by `FMEA.fmea_type != "process"`. It explicitly excludes KPI cards, tabs, per-factor S/O/D Class badges, an Element/Part column, any chart, the right-hand detail drawer, and Structure Tree/Interface Matrix/Parameter Diagram. Everything below documents the **full mockup** as shown, so it clearly separates "already-approved Slice D scope" from "everything else the mockup shows beyond that."

### 1. Features & Content

1. Cross-cutting DFMEA worksheet: one flat table listing every failure mode across all design-type FMEAs in the project (function, failure mode, effect(s), cause(s), S/O/D ratings, current controls, RPN, linked-actions count, status). **This is the part Slice D already covers**, in a simpler column form (no Element/Part, no Class badges, no Initial/Current RPN split — see the binding notes below).
2. At-a-glance KPI summary row: item count, high-risk count, open/overdue action counts, average initial vs. current RPN, last-updated timestamp.
3. Tab-switchable alternate views of the same DFMEA item set: the table itself, plus Structure Tree, Interface Matrix, Parameter Diagram, RPN Overview, and Action Tracker.
4. Server-side filter/search toolbar narrowing the table by element, function, status, RPN band, and type, plus a free-text search box.
5. Row-selection detail drawer showing one failure mode's full field set, S/O/D rating tiles, Initial/Current RPN, a responsible person, and a link to a fuller detail view.
6. Three secondary visual summaries beneath the table: an RPN trend line chart over recent weeks, a "top 5 highest current RPN" mini table with trend arrows, and an actions-by-status donut.
7. Two further right-rail summaries stacked below the drawer: an RPN risk-band donut (4-tier: Very High/High/Medium/Low) and a 3-metric DFMEA progress bar set.
8. Persistent footer showing environment/session metadata (database, user, role, workspace, version, system status) — identical shell chrome to every other page in the app.

### 2. Full Wireframe Widget Checklist

**Header/Chrome (top bar)** — existing pattern, reused verbatim from the app shell:
- Logo block ("Open FMEA" + "Open-EQMS Family" subtitle), sidebar collapse/hamburger icon — existing.
- Page title "DFMEA" + purple "Design FMEA" pill badge, subtitle line — existing title-bar pattern, new copy only.
- Project selector dropdown ("Project: New Headlamp X1") — existing pattern if used elsewhere, otherwise new `<select>`.
- Global search box ("Search (Ctrl+K)"), notification bell (badge), help icon, user avatar "JD" — existing shell chrome.
- Action row: "+ New DFMEA Item" (primary button), "Import", "Export" (dropdown), "Reports" (dropdown), "View Options" (dropdown), "Filters" (icon+label) — buttons/dropdowns are an existing pattern (`.button`, `.button-row`); the "Import"/"Reports"/"View Options" dropdown-menu behavior itself (a click-to-open menu, not a plain `<select>`) has no existing analog — new.

**Sidebar** — existing `.sidebar`/`.nav-group` pattern, reused verbatim; content is the app's real, already-defined nav tree (FMEA WORKSPACE, CONTEXT, FMEA PROJECT, FMEA ANALYSIS — including the two Slice D links DFMEA/PFMEA, VALIDATION & CHANGE, ANALYSIS groups). No new sidebar mechanics for this page.

**KPI row** — 7 `.stat-tile` cards: DFMEA Items (86, "All items"), High Risk RPN≥100 (14, "16.3% of total"), Actions Open (23, "26.7%"), Actions Overdue (6, "7.0%"), Avg. Initial RPN (184, "Before actions"), Avg. Current RPN (62, "After actions"), Last Updated (12 May 2025, "10:25"). Existing `.stat-tile span-3`/`.grid` pattern (used today on other stat rows); 7 cards across a 12-column grid needs a new span breakdown (e.g. wrapping row or narrower spans) since 7×3 > 12 — layout detail, not a new component.

**Tab strip** — DFMEA Table (active) / Structure Tree / Interface Matrix / Parameter Diagram / RPN Overview / Action Tracker. **New pattern.** The closest existing thing (`.process-step`/`.process-steps`) is a link-based step picker, not a true tab-panel content-swap — see Section 3.

**Filter/search bar** — search box "Search DFMEA items...", dropdowns Element/Function/Status/RPN/Type ("All" default), "More Filters" icon+label. Existing `.panel.compact` GET-form + `<select>` pattern, reused; "More Filters" implying a slide-out/modal with extra fields is new.

**Main table** (`.table-shell`/`<table>`, matches the existing `.worksheet`/`.worksheet-wrap` dense-table pattern) — columns: checkbox | ID | Element/Part | Function | Failure Mode | Effect(s) | Cause(s) | Severity(S): Rating+Class | Occurrence(O): Rating+Class | Current Controls: Prevention(P) Rating+Class, Detection(D) Rating+Class | RPN: Initial, Current | Actions | Status. 8 of 86 rows shown (DF-001…DF-008). Row checkboxes for multi-select — new (no existing bulk-select pattern).

**Pagination** — "Showing 1 to 8 of 86 items", numbered page buttons + prev/next arrows. No existing pagination widget in the app's confirmed CSS vocabulary — new, built on Django's `Paginator`.

**Secondary panels row (3 columns)**:
- "RPN Trend" line chart — two series (Initial/Current RPN Avg.), X-axis Wk 14–22, Y-axis 0–250, labeled points. New — needs Chart.js (`<canvas>`).
- "Top 5 Highest Current RPN" mini table — ID/Item/Function/Current RPN/Trend-arrow columns, 5 rows. Reuses `.table-shell` table pattern; the trend-arrow icon is new (needs a computed direction value).
- "Actions by Status" donut — center total "30", legend Open/In Progress/Closed/Cancelled with counts+percentages. New — Chart.js donut.

**Right-rail drawer stack** (below/beside the table, spans full content height):
- "Item Details" drawer with "×" close: title+status badge, 4-field list (Element/Part, Function, Failure Mode, Effect(s)), 3 colored S/O/D rating tiles, Initial/Current RPN pair, Responsible (avatar+name), Last Updated, "View Full Details" link. **New** — no existing drawer/detail-panel pattern.
- "RPN Risk Summary" donut — center total "86", legend Very High/High/Medium/Low with counts+percentages. New — Chart.js donut.
- "DFMEA Progress" — 3 labeled horizontal progress bars (Items with Actions 53%, Actions Completed 74%, High Risk Closed 43%). New — no existing progress-bar component in the confirmed CSS vocabulary.

**Footer** — "Database: OpenEQMS_Local" | "User: Janez Demo (Quality Engineer)" | "Role: Project Owner" | "Workspace: Global" | "Version: 1.0.0" | "System Status" green dot. Existing shell footer, reused verbatim.

### 3. GUI Coding Requirements

**Route + template**: Slice D already claims `fmea:dfmea_worksheet` at `/dfmea/`, template `django_app/fmea_app/templates/fmea_app/dfmea_worksheet.html`, for the core table only. Extending that same route/template to the full mockup (KPI row, tabs, drawer, charts) would follow directly from Slice D's file once built; it is not a separate route.

**Layout structure**:
- Header/sidebar/footer: use the existing `app_shell` base template unchanged — no new region.
- KPI row: `<div class="grid section-block">` of 7 `.stat-tile` cards.
- Tab strip: **new** — no existing tab-panel-swap component. Build a small vanilla-JS pattern matching `app.js`'s minimal style: a `<nav>` of `<button>`/`<a>` elements with `data-tab-target` attributes, a set of `<section data-tab-panel>` content blocks (one already server-rendered per tab, or six sibling `<div hidden>` blocks), and a ~15-line JS function toggling `hidden`/`aria-selected` on click — no page reload for the tab switch itself, though each tab's *content* would still be driven by the same GET-rendered page (all six panels' markup ships in the initial HTML; JS only shows/hides).
- Filter bar: `<form class="panel compact section-block" method="get">` with `<select name="...">`s — existing pattern, full-page GET reload on change/submit, consistent with the rest of the app.
- Main table: `.table-shell > table` inside the "DFMEA Table" tab panel — existing dense-table pattern.
- Pagination: **new** — a small `<nav class="pagination">` partial driven by Django's `Paginator`, page-number links as plain `<a href="?page=N">` (server-side, no AJAX), following the same GET-param convention as the filter form.
- Secondary charts row: `<div class="grid section-block">` with 3 `.panel` cards, each containing a `<canvas>` (line/donut) or a `.table-shell` mini table.
- Right-hand drawer stack: **new** — a fixed/sticky-positioned column (`<aside class="detail-rail">`) alongside the table, containing three stacked `.panel` blocks (Item Details, RPN Risk Summary, DFMEA Progress). Since no AJAX exists anywhere in the app, the realistic no-JS-framework approach is to server-render each visible row's detail fields into the page already (e.g. as `data-*` attributes on each `<tr>`, or as hidden `<template>` blocks keyed by row ID) and use a small vanilla-JS click handler on row/checkbox selection to copy that row's fields into the visible drawer fields — no network round-trip needed. The "×" close just toggles the drawer's `hidden` attribute.
- Structure Tree / Interface Matrix / Parameter Diagram tabs: **new, no existing pattern of any kind.** Each would need bespoke markup (an indented/nested list or SVG tree for Structure Tree; an `<table>` grid for Interface Matrix; a labeled-box SVG diagram for Parameter Diagram) built from scratch, with no vanilla-JS behavior beyond what a static diagram needs.

**Per-widget data binding**:
- DFMEA Items count, Function/Failure Mode/Effect(s)/Cause(s)/S/O ratings/D rating table columns, DFMEA Table tab, Function filter: (a) binds to real `FailureMode`/`Function`/`FailureEffect`/`FailureCause`/`RiskEvaluation` fields, already available (this is exactly what Slice D's table exposes).
- High Risk (RPN≥100), Actions Open/Overdue, Avg. Initial/Current RPN, Actions column, RPN Overview/Action Tracker tabs, RPN Trend chart, Top-5-RPN table, Actions-by-Status donut, RPN Risk Summary donut, DFMEA Progress bars: (b) binds to a computed aggregate over real data — first-vs-latest `RiskEvaluation` per failure mode, an overdue-action computation (`due_date < today AND status not in terminal states`), and RPN-banding/rollup logic that would need to be written (none of it exists as a query today).
- Element/Part column, Filter: Element: (c) no direct field — the closest real path is `FailureMode.function.product.name`, which only resolves when the function is product-linked (not operation-linked); render as static/placeholder until an explicit Element/Part concept is decided.
- Severity/Occurrence/Detection Class badges (H/M/L): (c) no per-factor banding function exists (only a combined S×O function) — render as placeholder chips until that logic exists.
- Current Controls: Prevention (P) Rating/Class: (c) no backing field — `RiskEvaluation` has no fourth factor and `PreventionControl` has no rating; render as static/placeholder until a Prevention rating field exists.
- Status column (Open/In Progress/Closed): (c) `FailureMode` has no status field; if intended as a rollup of linked `RecommendedAction.status`, that's (b) once written — otherwise (c) pending a decision.
- Item Details drawer — S/O/D tiles, Initial/Current RPN: same basis as the table columns above.
- Item Details drawer — Responsible (avatar+name): (c) no person-owner field exists on `FailureMode`; render as static/placeholder until a responsible-person concept exists (`RiskEvaluation.actor` is a different concept — "who last evaluated," not "who owns this item").
- Structure Tree, Interface Matrix, Parameter Diagram tabs: (c) no backing entity of any kind — render as static/placeholder content (or omit the tab) until those models exist.
- Last Updated (KPI + drawer): (c) no confirmed audit-timestamp field on `FailureMode`/`RiskEvaluation`/`FMEA` — render as static/placeholder pending confirmation of whether such a field exists.
- Footer (Database/User/Role/Workspace/Version/System Status): (c) environment/session metadata, not FMEA domain data — render as static content, not tied to any model.

**Filtering/interaction**: every dropdown filter and the search box are a server-side GET form + `<select>`/`<input>` + full page reload, matching every other filtered list in this app — no client-side/AJAX filtering. Tab switching is the one exception noted above (client-side show/hide of already-rendered content, not a data refetch).

**Sidebar entry**: belongs under the existing "FMEA ANALYSIS" nav group (already added by Slice D), as the "DFMEA" link.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 12 — PFMEA: GUI Coding Requirements

> **Scope note (read first):** As with Mockup 11, a narrowed, real version of this screen's core table is already approved and instructed — `Codex_Instruction_DFMEA_PFMEA_Worksheets_SliceD.md` (approved 2026-09-04, not yet built). Slice D's PFMEA half is `/pfmea/` (`fmea:pfmea_worksheet`), FMEAs where `fmea_type == "process"`, reusing `_build_worksheet_rows`/`_worksheet_row` unchanged, one read-only table, no KPI cards, no per-factor Class badges, no tabs, no charts, no drawer, no Control Plan Link. Everything below documents the full mockup, distinguishing that already-approved core from everything else it shows.

### 1. Features & Content

1. Cross-cutting PFMEA worksheet: one flat table listing every failure mode across all process-type FMEAs (process step, function, failure mode, effect(s), S/O/D ratings, current-controls counts, RPN, actions, status). **This is the part Slice D already covers**, in a simpler column form.
2. At-a-glance KPI summary row: item count, high-risk count, open/overdue action counts, average initial vs. current RPN, last-updated timestamp — same 7-card layout as Mockup 11.
3. Tab-switchable alternate views of the same PFMEA item set: the table itself, Process Structure, Interface Matrix, Control Plan Link, Parameter Diagram, RPN Overview, Action Tracker (one more tab than DFMEA — "Control Plan Link").
4. Server-side filter/search toolbar narrowing the table by process, process step, status, RPN band, and type.
5. Row-selection detail drawer with the item's full field set, S/O/D tiles, Initial/Current RPN, responsible person, and a link to a fuller detail view.
6. Three secondary visual summaries beneath the table: RPN trend line chart, "top 5 highest current RPN" mini table, actions-by-status donut.
7. Two further right-rail summaries: an RPN risk-band donut and a 3-metric PFMEA progress bar set.
8. Persistent footer with environment/session metadata — identical shell chrome to every other page.

### 2. Full Wireframe Widget Checklist

**Header/Chrome** — identical shell pattern to Mockup 11: logo block, page title "PFMEA" + purple "Process FMEA" badge, subtitle, project selector, search, notification bell (badge "9"), help icon, avatar. Action row: "+ New PFMEA Item", Import, Export (dropdown), Reports (dropdown), View Options (dropdown), Filters — same existing/new split as Mockup 11.

**Sidebar** — identical structure/groups to Mockup 11; "PFMEA" is the active item under FMEA PROJECT.

**KPI row** — 7 `.stat-tile` cards: PFMEA Items (112), High Risk RPN≥100 (18, 16.1%), Actions Open (27, 24.1%), Actions Overdue (7, 6.3%), Avg. Initial RPN (176), Avg. Current RPN (58), Last Updated (12 May 2025, 10:30). Same layout treatment as Mockup 11.

**Tab strip** — PFMEA Table (active) / Process Structure / Interface Matrix / **Control Plan Link** / Parameter Diagram / RPN Overview / Action Tracker. Same new tab-swap pattern as Mockup 11, one extra tab.

**Filter/search bar** — search "Search PFMEA items...", dropdowns Process/Process Step/Status/RPN/Type ("All" default), "More Filters". Same existing GET-form pattern as Mockup 11, different field set.

**Main table** (`.table-shell`/`<table>`, matches `.worksheet`/`.worksheet-wrap`) — columns: checkbox | ID | Process Step (two-line cell: "10 - Incoming Insp." over "Material Receiving") | Process Function | Failure Mode | Effect(s) | Severity(S): Rating+Class | Occurrence(O): Rating+Class | Detection(D): Rating+Class | Current Controls: P (plain number), D (plain number) | RPN: Initial, Current | Actions | Status. 10 of 112 rows shown (PF-001…PF-010). Note the Current Controls P/D columns here are plain, uncolored numbers — visually a lighter-weight treatment than DFMEA's colored Prevention/Detection rating+class pair in the same table slot; this inconsistency between the two mockups is worth flagging to whoever finalizes the shared template, not silently resolved here.

**Pagination** — "Showing 1 to 10 of 112 items", numbered page buttons, prev/next, **plus a "10 / page" page-size dropdown** (not present in Mockup 11's pagination). Same new pagination component as Mockup 11, with one added control.

**Secondary panels row (3 columns)** — RPN Trend line chart (same series/axis pattern as Mockup 11), Top 5 Highest Current RPN mini table (ID/Process Step/Failure Mode/Current RPN/Trend), Actions by Status donut (center "27", Open/In Progress/Closed/Cancelled legend). Same widgets and same new-Chart.js requirement as Mockup 11.

**Right-rail drawer stack**:
- "Item Details" drawer: title+status badge, fields (Process Step, Function, Failure Mode, Effect(s)), S/O/D tiles, Initial/Current RPN, Responsible (avatar+name), Last Updated, "View Full Details" link. Same new drawer pattern as Mockup 11.
- "RPN Risk Summary" donut (center "112", Very High/High/Medium/Low legend).
- "PFMEA Progress" — 3 bars (Items with Actions 51%, Actions Completed 67%, High Risk Closed 39%).

**Footer** — identical shell footer to every other page.

### 3. GUI Coding Requirements

**Route + template**: Slice D already claims `fmea:pfmea_worksheet` at `/pfmea/`, template `django_app/fmea_app/templates/fmea_app/pfmea_worksheet.html`, for the core table only. The full mockup's extra regions would extend that same route/template once Slice D ships, following the shared-template idea below rather than a separate page.

**Layout structure**: Same regions and same new-vs-existing pattern breakdown as Mockup 11 (KPI grid, new tab-swap JS, existing GET filter form, `.table-shell` table, new pagination component, new secondary-charts row, new right-hand drawer stack built from server-rendered row data + a small show/hide handler, no AJAX). One page-shape observation worth stating plainly: DFMEA and PFMEA are structurally identical pages differing only in column set and tab list, which strongly suggests one shared template (parameterized by `fmea_type`) rather than two independently maintained ones — a template-reuse decision for whoever builds this, not a data-model question.

The one new pattern specific to this mockup: **Control Plan Link tab.** On screen it is just another tab in the strip (same tab-swap mechanics as the rest); its content would be a linked-record view pointing at a Control Plan concept. No new interaction pattern beyond the tab-swap already described.

**Per-widget data binding**:
- PFMEA Items count, Process Function/Failure Mode/Effect(s)/S/O/D rating columns, PFMEA Table tab, Process/Process Step filters: (a) binds to real `FailureMode`/`Function`/`FailureEffect`/`RiskEvaluation`/`Process`/`Operation` fields, already available.
- Process Step primary line (`"{sequence} - {name}"`): (b) a computed aggregate/formatting over real `Operation.sequence`/`Operation.name` — needs new formatting logic, not a new field.
- Process Step secondary line: (b) if it is `Operation.process.name` reused as a subtitle (a real join); (c) if a distinct "work element" concept one level below Operation is intended instead — render as static/placeholder until that's decided.
- Process Structure tab: (b) `Process`→`Operation` is a real two-level hierarchy today; a tree view over it is a new nested query/view, not a new model.
- High Risk, Actions Open/Overdue, Avg. Initial/Current RPN, RPN Overview/Action Tracker tabs, RPN Trend chart, Top-5-RPN table, Actions-by-Status donut, RPN Risk Summary donut, PFMEA Progress bars: (b) same computed-aggregate basis as Mockup 11.
- Current Controls: P / D plain-number columns: (b) most plausibly a count of `PreventionControl`/`DetectionControl` records reachable from the failure mode via its causes (`FailureCause.prevention_controls`/`.detection_controls`, aggregated across all causes) — a real relationship chain, needs new aggregation logic since controls attach to `FailureCause`, not directly to `FailureMode`.
- S/O/D Class badges: (c) same gap as Mockup 11 — only a combined S×O banding function exists today; render as placeholder until per-factor banding logic exists.
- Status column: (c) same as Mockup 11 — no `FailureMode.status` field; render as static/placeholder unless built as an action-status rollup, which would make it (b).
- Interface Matrix, Parameter Diagram tabs: (c) no backing entity of any kind — render as static/placeholder until those models exist.
- **Control Plan Link tab**: (c) no Control Plan entity exists anywhere in the domain model today — render as static/placeholder content until a Control Plan model exists. (This project's DNA reference does carry a standing rule about Control Plans never being silently/automatically modified once they exist — that rule concerns automated changes, not this tab's ordinary human-driven display/linking; it isn't a reason to treat this tab differently from any other placeholder in this document.)
- Item Details drawer — Responsible (avatar+name): (c) same person-owner gap as Mockup 11.
- Last Updated, footer: (c) same as Mockup 11.

**Filtering/interaction**: same server-side GET-form-per-filter pattern as Mockup 11; no client-side/AJAX filtering anywhere. Tab switching is client-side show/hide of already-rendered panels, same as Mockup 11.

**Sidebar entry**: belongs under the existing "FMEA ANALYSIS" nav group (already added by Slice D), as the "PFMEA" link.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 13 — Change Impact: GUI Coding Requirements

### 1. Features & Content

1. A change log listing design/process/requirement changes with type, source, reason, impact level, affected-item counts, status, owner, and date.
2. At-a-glance KPI summary row: total changes, count under analysis, impacts identified, high/critical-impact count, actions-required count, closed count, last-updated timestamp.
3. Tab-switchable alternate views of the same change set: the log itself, Impact Matrix, Affected FMEA Items, Action Plan, Change History.
4. Server-side filter/search toolbar narrowing the log by change type, source, status, impact level, and a date range.
5. Row-selection detail drawer with a change's full field set (title, type, source, reason, description, status, impact level, owner, dates) plus an embedded 4-metric summary sub-panel (DFMEA/PFMEA item counts, high/critical count, action count).
6. Four secondary visual summaries beneath the table: an impact-level distribution donut, a change-type distribution donut, a multi-series "changes over time" line chart, and a "top affected areas" bar list.
7. Persistent footer with environment/session metadata — identical shell chrome to every other page.

### 2. Full Wireframe Widget Checklist

**Header/Chrome** — logo block, page title "Change Impact" (no type badge, unlike Mockups 11/12), subtitle, project selector, search, notification bell (badge "3"), help icon, avatar. Action row: "+ New Change" (primary), Import, Export (dropdown), Reports (dropdown), Filters — no "View Options" here (one fewer action than Mockups 11/12). Existing shell chrome + existing/new button-dropdown split, same as prior mockups.

**Sidebar** — same nav tree as prior mockups; "Change Impact" is the active item, shown as a sibling of Evidence & Tests and Validation Trajectory under a "VALIDATION & CHANGE" group.

**KPI row** — 7 `.stat-tile` cards: Total Changes (24, "All time"), Under Analysis (8, 33.3%), Impacts Identified (18, 75.0%), High/Critical Impact (7, 29.2%), Actions Required (15, 62.5%), Closed (9, 37.5%), Last Updated (12 May 2025, 10:35). Same `.grid`/`.stat-tile` pattern as prior mockups.

**Tab strip** — Change Log (active) / Impact Matrix / Affected FMEA Items / Action Plan / Change History. Same new tab-swap pattern as Mockups 11/12.

**Filter/search bar** — search "Search changes...", dropdowns Change Type/Source/Status/Impact Level ("All" default), a date-range picker (two-ended, "01/01/2024 – 12/05/2025"), "More Filters". The date-range picker is a new control not seen in Mockups 11/12's filter bars (those use only `<select>`s).

**Main table** (`.table-shell`/`<table>`) — columns: checkbox | ID | Change Title | Type | Source | Reason | Impact Level | Affected DFMEA (count) | Affected PFMEA (count) | Status | Owner (avatar) | Date | Actions (eye icon + "…" overflow menu). 8 of 24 rows shown (CHG-024…CHG-017). "—" dash shown for a zero/none count (CHG-019's Affected DFMEA). Impact Level uses a 5-step scale (Critical/High/Medium/Low/None) — a different, more granular color vocabulary than the DFMEA/PFMEA H/M/L scheme, worth keeping visually distinct rather than reusing the same 3-step classes. Status badges introduce a purple "Under Analysis" state alongside the blue/orange/green/gray already used elsewhere.

**Pagination** — "Showing 1 to 8 of 24 changes", numbered page buttons + next. Same new pagination component as prior mockups.

**Secondary panels row (4 columns)**:
- "Impact Level Distribution" donut, center total "24", legend Critical/High/Medium/Low/None with counts+percentages.
- "Change Type Distribution" donut, center total "24", legend Design/Process/Supplier/Regulatory/Other.
- "Changes Over Time" line chart, three series (Identified/Closed/Open), X-axis Dec 24–May 25.
- "Top Affected Areas" — a labeled horizontal bar *list* (not a full chart), caption "(Number of changes)": Optical Performance 10, Housing/Enclosure 8, Electrical 7, Mechanical/Assembly 6, Thermal Management 4, Other 3.

**Right-rail drawer** (single panel this time — no stacked secondary panels below it, unlike Mockups 11/12):
- "Change Details" drawer with "×" close: title+impact badge, field list (Title, Type, Source, Reason, Description, Status badge, Impact Level badge, Owner avatar+name, Date Identified, Last Updated), an embedded "Summary" sub-panel of 4 mini-stats in a row (DFMEA Items, PFMEA Items, High/Critical, Actions), "View Full Details" link.

**Footer** — identical shell footer to every other page.

### 3. GUI Coding Requirements

**Route + template**: propose `fmea:change_impact` at `/changes/`, template `django_app/fmea_app/templates/fmea_app/change_impact.html`, following the existing `fmea:<snake_case>` / `<snake_case_name>.html` convention. No approved instruction exists for this page (unlike Mockups 11/12) — this is a from-scratch proposal, not a claim that it's scheduled.

**Layout structure**: Same shell composition as Mockups 11/12 (header/sidebar/footer from the base template, `.grid` KPI row, new tab-swap JS pattern, existing GET-form filter bar with one new control — a date-range picker, which has no existing analog in this app and would need two `<input type="date">` fields or a small vendored date-range widget, `.table-shell` table, new pagination component, a 4-column secondary-panels grid, and a single new right-hand drawer panel populated the same server-rendered-data + show/hide-JS way described for Mockups 11/12, minus the two extra stacked panels those pages have below the drawer).

**Per-widget data binding**: Per this codebase's real domain model, **no `Change` entity exists in any form** — the nearest real models, `FMEARevision`/`FMEADocument`, track FMEA-*document* revisions (e.g. "this FMEA went from v1.0 to v1.1"), which is a different concept from an external design/requirement change with its own lifecycle and downstream impact tracking against `FailureMode`/`FailureEffect`/`FailureCause`/`RecommendedAction`. As a result, every widget on this page is (c): no real data source yet — render as static/placeholder content until a `Change` entity (and its linkage to `FailureMode`) exists. Specifically:
- Every KPI card, every table column, every filter, every tab, and every secondary chart/list needs a new `Change` model with fields such as: `title`, `change_type`, `source`, `reason`, `description`, `impact_level`, `status`, `owner`, `date_identified`, `updated_at`.
- "Affected DFMEA"/"Affected PFMEA" counts and the Impact Matrix/Affected FMEA Items tabs additionally need a many-to-many (or through-table) relationship from `Change` to `FailureMode` (or to `FMEA`/`Product`/`Process`, depending on the intended granularity of "affected") — no such relationship exists today in any form.
- "Action Plan" as a tab name would most plausibly connect to the real `RecommendedAction` model, but the linkage itself (a FK from `RecommendedAction` to a change-like entity) doesn't exist today either.
- "Change Details" drawer's Summary sub-panel additionally needs each linked failure mode's own risk level and action count rolled up through that same not-yet-existing linkage.

None of the above is proposed as a finished schema — it is stated only to make plain what a builder would need to add before this page could show real data; the specific fields, required-ness, and any status-transition rules are open questions for whoever scopes that model, not settled here.

**Filtering/interaction**: same server-side GET-form-per-filter pattern as every other page in this app, once real data exists to filter; no client-side/AJAX filtering. Tab switching would be the same client-side show/hide pattern described for Mockups 11/12.

**Sidebar entry**: the mockup shows this under a "VALIDATION & CHANGE" nav group, which does not exist in the app's sidebar today — it would need to be added as a new group (alongside Evidence & Tests and Validation Trajectory, both also not yet built as standalone pages) rather than placed in an existing group.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 14 — Validation Trajectory: GUI Coding Requirements

### 1. Features & Content

1. A lifecycle-phase "trajectory" view showing, per validation/test, how far it has progressed through six fixed phases (Concept → Design → Prototype → Verification → Validation → Release).
2. At-a-glance KPI summary row: total validations, planned/in-execution/completed/overdue counts, count linked to FMEA items, last-updated timestamp.
3. Tab-switchable alternate views of the same validation set: the trajectory timeline itself, Validation Table, Validation Plan, Test Plan, Coverage Matrix, History.
4. Server-side filter/search toolbar (dropdown-only, no free-text box) narrowing by FMEA type, FMEA item, validation type, status, lifecycle phase, and a date range.
5. Row-selection detail drawer with a validation's full field set (name, type, linked FMEA items, objective, method, acceptance criteria, planned/actual dates, responsible person, status, a progress bar, evidence-file count, and an outbound link to a test plan).
6. Three secondary visual summaries: a validations-by-status donut, a validation-type distribution donut, and a validation-coverage-by-FMEA-type horizontal bar chart.
7. A fourth secondary widget: an "Upcoming Validations" list with a "View All" link.
8. Persistent footer with environment/session metadata — identical shell chrome to every other page.

### 2. Full Wireframe Widget Checklist

**Header/Chrome** — logo block, page title "Validation Trajectory", subtitle, project selector, search, notification bell (badge "2"), help icon, avatar. Action row: "+ New Validation" (primary), Import, Export (dropdown), Reports (dropdown), Filters. Same existing/new split as prior mockups.

**Sidebar** — same nav tree as prior mockups; "Validation Trajectory" is the active item under a "VALIDATION & CHANGE" group (siblings: Evidence & Tests, Change Impact).

**KPI row** — 7 `.stat-tile` cards: Total Validations (68, "All time"), Planned (26, 38.2%), In Execution (18, 26.5%), Completed (20, 29.4%), Overdue (4, 5.9%), Linked to FMEA Items (56, 82.4%), Last Updated (12 May 2025, 10:45). Same `.grid`/`.stat-tile` pattern as prior mockups.

**Tab strip** — Trajectory View (active) / Validation Table / Validation Plan / Test Plan / Coverage Matrix / History. Same new tab-swap pattern as prior mockups.

**Filter/search bar** — no free-text search box here (unlike Mockups 11–13); dropdowns FMEA Type/FMEA Item/Validation Type/Status/Lifecycle Phase ("All" default), a date-range picker, "More Filters". Same existing GET-form pattern, same new date-range control noted in Mockup 13.

**"Trajectory Timeline"** — the page's signature widget, a swim-lane/Gantt-like visualization with **no existing analog anywhere in this app or its CSS vocabulary**:
- Six phase-column headers (Concept/Design/Prototype/Verification/Validation/Release), each with an icon and a "completed/total" fraction beneath it (e.g. "Design 8/10").
- A row list — ID | Validation/Test name | Linked FMEA Item(s) — paired with a horizontal 6-node status path per row spanning the six phase columns. Each node is one of: green filled circle+check (Completed), blue filled circle (In Execution), orange diamond (Planned), gray open circle (Not Started), red circle+"!" (Overdue), or a larger filled diamond (Milestone, used once). Line segments between nodes are solid when connecting two "settled" states and dashed when projecting into not-yet-happened phases.
- 10 of 68 rows shown (VAL-001…VAL-010).
- A legend row beneath the timeline mapping each shape/color to its meaning.

**Right-rail — "Validation Details" drawer**: richer than the drawers in Mockups 11–13 — mixes a plain field list (Validation Name, Validation Type, Linked FMEA Items, Objective, Method, Acceptance Criteria, Planned Start/Finish, Actual Start, Responsible avatar+name, Status badge) with a **progress bar** ("60%"), a small **file-attachment reference** ("2 files" + file-type icons), and an **outbound link** to a Test Plan ("TP-002", with an external-link icon), plus "View Full Details".

**Secondary panels row (3 charts + 1 list)**:
- "Validations by Status" donut, center total "68", legend Completed/In Execution/Planned/Overdue.
- "Validation Type Distribution" donut, center total "68", legend Performance/Reliability/Safety/Compliance/Durability/Other.
- "Validation Coverage (by FMEA Type)" horizontal bar chart, X-axis 0–100%, caption "Coverage = Completed / Total Linked Items": DFMEA 32/38 (84.2%), PFMEA 18/22 (81.8%), System FMEA 6/8 (75.0%), PM-FMEA 0/2 (0.0%).
- "Upcoming Validations" list — columns ID | Validation/Test | Planned Start | FMEA Item(s), 4 rows, "View All (26)" link.

**Footer** — identical shell footer to every other page.

### 3. GUI Coding Requirements

**Route + template**: propose `fmea:validation_trajectory` at `/validation-trajectory/`, template `django_app/fmea_app/templates/fmea_app/validation_trajectory.html`, following the app's `fmea:<snake_case>` / `<snake_case_name>.html` convention. No approved instruction exists for this page — a from-scratch proposal only.

**Layout structure**: Same shell composition as prior mockups (header/sidebar/footer, `.grid` KPI row, new tab-swap JS, GET-form filter bar with the new date-range control, new pagination-less list-plus-timeline layout, secondary-panels grid, new right-hand drawer). The **Trajectory Timeline needs an entirely new widget with no precedent in this codebase** — it is materially more complex than a donut/line/bar chart and is not a good fit for Chart.js (which per this project's charting decision covers line/bar/donut only). A workable vanilla-JS/CSS approach: render each row's 6-phase path as a CSS flex/grid row of fixed-width "node" cells, each node a small `<span>` styled by a `data-status` attribute (`completed`/`in_execution`/`planned`/`not_started`/`overdue`/`milestone`) driving its color/shape via CSS, with connecting line segments drawn as `::before`/`::after` pseudo-elements toggled `solid`/`dashed` by the same data attribute on the *next* node — no JS needed for the visualization itself, only for phase-column filtering (hooked into the existing "Lifecycle Phase" `<select>`, submitted the same server-side GET way as every other filter). The phase-header fractions ("8/10") are server-computed aggregates rendered directly into the header markup.

**Per-widget data binding**: Per this codebase's real domain model, the closest existing entity is `Evidence`/`EffectivenessVerification`, which is a small model keyed to `RecommendedAction` — it has no lifecycle-phase concept, no per-phase status, and no direct link to `FailureMode`. As a result nearly every widget on this page is (c), with one narrow exception:
- Evidence file count ("2 files") on the drawer: (c) `Evidence` is a real model name today, so a *count* of linked evidence records could become (b) once `Evidence` gains a proper FK to whatever new validation entity is built — but the file-attachment/download behavior implied by "2 files" is separately new regardless, since no file/image storage exists anywhere in this codebase yet.
- All 7 KPI cards, all 6 tabs, all filters (FMEA Type/FMEA Item/Validation Type/Status/Lifecycle Phase/Date Range), the entire Trajectory Timeline (phase-header fractions, per-row 6-node status path, milestone/overdue markers), the full Validation Details drawer (Name/Type/Objective/Method/Acceptance Criteria/dates/Responsible/Status/Progress/Test Plan link), and all four bottom aggregation widgets: (c) no real data source yet — render as static/placeholder content until a validation/lifecycle-tracking entity exists.

To make the placeholder gap concrete rather than abstract: showing real data here would need, at minimum, a new entity capturing a validation's identity (`name`, `validation_type`, `objective`, `method`, `acceptance_criteria`, planned/actual dates, a responsible person, an overall status), a per-phase status record (six phase-status values or a related child table, plus an `is_milestone` flag) to drive the timeline, a many-to-many link to `FailureMode` (spanning both DFMEA and PFMEA items, per the mockup's mixed DF-/PF- codes), and a second linked entity for "Test Plan" (referenced by the drawer's "TP-002" link but not detailed by this mockup). None of this is proposed as a finished schema — it's stated only so the size of the gap is visible, not as an authored design.

**Filtering/interaction**: same server-side GET-form-per-filter pattern as every other page in this app, once real data exists to filter; no client-side/AJAX filtering. Tab switching is the same client-side show/hide pattern described for Mockups 11–13.

**Sidebar entry**: the mockup shows this under a "VALIDATION & CHANGE" nav group, which does not exist in the app's sidebar today — same gap noted for Mockup 13; it would need to be added as a new group.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 15 — Failure Modes: GUI Coding Requirements

### 1. Features & Content

1. A standalone, cross-cutting failure-mode list (today this data only appears embedded inside `fmea_detail.html`'s worksheet section, not as its own page) — ID, name, description, function/element, S/O/D/RPN, trend, status.
2. At-a-glance KPI summary row: failure-mode count, high-risk count, count sourced "from complaints," count linked to actions, a catalog-entry count, last-updated timestamp.
3. Tab-switchable alternate views of the same failure-mode set: the list itself, Failure Mode Matrix, Error Catalog, Complaint Link, Trend & Analysis.
4. Server-side filter/search toolbar narrowing by FMEA type, function, element, source, severity, and occurrence, plus a second toolbar row of bulk/AI-assist actions (AI Suggest, Link to Catalog, Link to Complaint, Quick Add).
5. Row-selection detail drawer with its own internal sub-tabs (Overview/Links/Complaints/Catalog/History), an image gallery with a defect-location marker, a linked-complaints mini table, an AI "similar failure modes" list, and a suggested-actions checklist feeding into an "Add to Action Plan" action.
6. Four secondary visual summaries: a source-distribution donut, a severity-vs-occurrence scatter/bubble chart, a top-failure-mode-categories bar chart, and a real-complaints trend line chart.
7. Persistent footer with environment/session metadata — identical shell chrome to every other page.

### 2. Full Wireframe Widget Checklist

**Header/Chrome** — logo block, page title "Failure Modes" with a small circled "?" info icon, subtitle, project selector ("Project: New Headlamp X1 - DFMEA"), search, notification bell (badge "3"), help icon, avatar. Action row: "+ New Failure Mode" (primary), Import, Export (dropdown), Reports (dropdown), View Options (dropdown), Filters. Same existing/new split as prior mockups.

**Sidebar** — same nav tree as prior mockups; "Failure Modes" is the active item under the existing "FMEA ANALYSIS" group (siblings: Functions, Effects, Causes, Prevention Controls, Detection Controls, Actions).

**KPI row** — 6 `.stat-tile` cards (one fewer than Mockups 11/12): Failure Modes (186, "All items"), High Risk RPN≥100 (42, 22.6%), From Complaints (38, "20.4% (real cases)"), Linked to Actions (134, 72.0%), Catalog Entries (2,456, "Available"), Last Updated (12 May 2025, 10:45). Same `.grid`/`.stat-tile` pattern as prior mockups.

**Tab strip** — Failure Modes List (active) / Failure Mode Matrix / Error Catalog / Complaint Link / Trend & Analysis. Same new tab-swap pattern as prior mockups.

**Filter/search bar** — search "Search failure modes...", dropdowns FMEA Type/Function/Element/Source/Severity/Occurrence ("All" default), "More Filters". **Second toolbar row** beneath it: "AI Suggest" (sparkle icon), "Link to Catalog", "Link to Complaint", "Quick Add" — a row of action buttons with no existing analog as a group (individual buttons reuse `.button`, but a dedicated second bulk/AI-action row is new).

**Main table** (`.table-shell`/`<table>`) — columns: checkbox | ID | Failure Mode (with a small orange warning-triangle icon per row) | Description | Function/Element | Source (badge: Design/Catalog/Complaints/combined) | Catalog (code, e.g. "EC-1204") | Complaints (count) | S | O | D | RPN | Trend (arrow icon) | Status | Actions (row of small icon buttons). 10 of 186 rows shown (FM-001…FM-010). Row FM-001 is checked and mirrored in the open drawer.

**Pagination** — "Showing 1 to 10 of 186 failure modes", numbered page buttons, "10 / page" size dropdown. Same new pagination component as Mockup 12.

**Secondary panels row (4 columns)**:
- "Source Distribution" donut, center total "186", legend Design/Complaints/Catalog/Suppliers/Other.
- "Severity vs Occurrence" scatter/bubble chart — X-axis Occurrence 1–10, Y-axis Severity (non-standard gridline scale as drawn), bubbles colored by risk tier and sized by a second value (likely RPN or a count), one bubble highlighted with a callout ("FM-001 / RPN: 180").
- "Top Failure Mode Categories" horizontal bar chart: Optical/Mechanical/Electrical/Thermal/Software/Chemical/Other with counts+percentages.
- "Trend (Real Complaints)" line chart, two series ("Design FM", "Complaint FM"), X-axis Jan–May.

**Right-rail — "Failure Mode Details" drawer** (richest drawer of the batch):
- Header: "FM-001" + "High Risk" badge, "×" close.
- **Internal sub-tabs**: Overview (active) / Links / Complaints / Catalog / History — a second, nested tab-swap inside the drawer, distinct from the page-level tab strip.
- Overview fields: Failure Mode, Description, Function (linked), Element, FMEA Type, Source (badge), Catalog Entry (linked + "View" button), Complaints (count badge + "View" button), First Seen, Last Updated, Status badge, Owner (avatar+name).
- **Image gallery**: one large hero image with a red crosshair/target annotation marker overlaid on a defect location, plus 3 smaller thumbnails. Buttons beneath: "+ Link to Catalog", "+ Link Complaint", "Edit".
- "Top Linked Complaints" mini table (ID/Vehicle/Symptom/Date, 3 rows) + "View All" link.
- "Similar Failure Modes (AI)" list — 3 rows, each an ID/name + a percentage similarity score.
- "Recommended Actions" panel (lightbulb icon) — an unchecked checklist of 3 suggested action texts + "+ Add to Action Plan" button.

**Footer** — identical shell footer to every other page.

### 3. GUI Coding Requirements

**Route + template**: propose `fmea:failure_modes` at `/failure-modes/`, template `django_app/fmea_app/templates/fmea_app/failure_modes.html`, following the app's `fmea:<snake_case>` / `<snake_case_name>.html` convention. No approved instruction exists for this standalone page yet — this codebase's real `FailureMode` CRUD lives inside `fmea_detail.html`'s worksheet section today, not as its own list page, so this would be a genuinely new view over already-real data, distinct in kind from Mockups 13/14 (which need a new model) and closer in kind to what Slice D does for DFMEA/PFMEA.

**Layout structure**: Same shell composition as prior mockups (header/sidebar/footer, `.grid` KPI row, new tab-swap JS for the page-level tab strip, GET-form filter bar plus the new second bulk/AI-action toolbar row, `.table-shell` table, new pagination component, 4-column secondary-panels grid, new right-hand drawer). Two additional new patterns specific to this mockup:
- **Drawer-internal sub-tabs** (Overview/Links/Complaints/Catalog/History): the same tab-swap JS pattern proposed for the page-level tabs, scoped to the drawer's DOM subtree (a second, independent `data-tab-target`/`data-tab-panel` group) — no new mechanism needed, just a second instance of the same small script.
- **Image gallery with annotation marker**: entirely new, no existing pattern anywhere in this app. Would need: a hero-image `<img>` with an absolutely-positioned marker `<span>` placed via stored normalized (x%, y%) coordinates, a thumbnail strip of `<img>` elements with a click-to-swap-hero handler (vanilla JS, no framework needed), and — separately — real file-upload/storage plumbing, since this app has no file/image storage capability today at all (not even for evidence attachments elsewhere in the app).

**Per-widget data binding**:
- Failure Modes count, ID/Description/Failure Mode name/Function columns, Failure Modes List tab, Function/Severity/Occurrence filters, Quick Add: (a) binds to real `FailureMode`/`Function`/`RiskEvaluation` fields, already available.
- High Risk KPI, Linked to Actions KPI, Failure Mode Matrix tab, Trend arrow column, Severity-vs-Occurrence scatter (the real S/O values powering it), the final "Add to Action Plan" commit step: (b) binds to a computed aggregate over real data (first-vs-latest `RiskEvaluation`, an actions-linked count, direction-of-change vs. a prior evaluation) — the plotting/bucketing itself is new visualization work, but the underlying values are real. The commit step specifically is (a) once reached: checking a suggested action and clicking "Add to Action Plan" would create a real `RecommendedAction` row.
- Element column/filter: (c) same gap noted in Mockups 11/12 — no direct `FailureMode`→`Product` field; at best derivable via `function.product.name`, which doesn't always resolve.
- Status column: (c) no `FailureMode.status` field; render as static/placeholder unless built as an action-status rollup (which would make it (b)).
- From Complaints KPI, Catalog Entries KPI, Error Catalog tab, Complaint Link tab, Source badge/column/filter/donut, Catalog column, Complaints column, Top Failure Mode Categories chart, Trend (Real Complaints) chart, drawer sub-tabs Links/Complaints/Catalog/History, Top Linked Complaints table, image gallery + annotation, Owner field: (c) no real data source yet — render as static/placeholder content until an Error Catalog entity, a Complaint entity, a Source classification field, a category field, an owner/person field, and file/image storage all exist (none do today).
- "AI Suggest" toolbar action and "Similar Failure Modes (AI)" list: (c) no similarity/matching capability exists — this project has an unwired Ishikawa-classification prompt spec, but that is a distinct, different AI capability from a name/description similarity search; render as static/placeholder until such a capability is built and an Error Catalog exists for it to search against.
- "Recommended Actions" suggestion checklist (before commit): (c) the suggested items themselves have no generating mechanism yet; only the final commit step (checked above) has a real target model.
- Last Updated, footer: (c) same unconfirmed-audit-field and environment-metadata gaps noted in prior mockups.

**Filtering/interaction**: same server-side GET-form-per-filter pattern as every other page in this app; no client-side/AJAX filtering. Both levels of tab switching (page-level and drawer-internal) are client-side show/hide of already-rendered content, same pattern as prior mockups.

**Sidebar entry**: belongs under the existing "FMEA ANALYSIS" nav group, as a new "Failure Modes" link (the group itself already exists per Slice D; this would be its first sibling entry beyond DFMEA/PFMEA).

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 16 — Causes: GUI Coding Requirements

### 1. Features & Content

1. Browse all causes across the current FMEA project in a paginated, sortable table (214 causes, 10/page).
2. See at-a-glance volume/quality stats for causes via a 6-tile KPI row (total, catalog vs. user-defined split, linked-to-FMEA count, high-influence count, last-updated timestamp).
3. Filter the causes table by source, cause type, category, status, and FMEA-link state via server-side dropdowns, plus free-text search.
4. Switch between five sub-views of cause data via tabs: the main list, a reusable cause catalog, a failure-modes-linked view, a cause-relationships view, and a change history view.
5. Inspect one cause in depth in a persistent right-hand detail rail (identity, classification, influence score, status, responsible person, timestamps, notes) without leaving the list.
6. See summary analytics for the whole cause set: breakdown by type (donut), breakdown by category (bar), influence-score distribution (donut), and a ranked "top causes by linked failure-mode count" mini table.
7. See a cross-entity "Connections Overview" strip chaining cause counts through FMEA items, failure modes, and various investigation-record types (complaints, XDA, 8D, RCA, 5-Why).
8. Trigger common cause-related actions from a "Quick Actions" panel (new cause, add to catalog, link to FMEA, create action, start 8D, open XDA).
9. Create, edit, import, export, and generate reports for causes via header-level action buttons.

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Brand block "Open FMEA / Community Edition" — existing pattern (sidebar top).
- Page title "Causes" + "?" info icon — existing header pattern.
- Subtitle line under title — existing pattern.
- Project selector pill "Project: Headlamp X1 - PFMEA" with chevron — existing pattern (global chrome, not page-specific).
- Global search box "Search (Ctrl+K)" — existing pattern.
- Notification bell with red badge "1" — existing pattern.
- Help "?" icon — existing pattern.
- User avatar "JD" with presence dot — existing pattern.
- Action-button row: "+ New Cause" (primary), "Import" (dropdown), "Export" (dropdown), "Reports" (dropdown), "Filters" (dropdown) — existing `.button`/`.button-row`/`.toolbar` pattern; dropdown behavior on Import/Export/Reports/Filters is new (no existing dropdown-menu JS in `app.js`).

**KPI row**
- 6 `.stat-tile` cards in a `.grid`: Total Causes, From Catalog, New (User Defined), Linked to FMEA Items, High Influence (≥7), Last Updated — existing `.stat-tile`/`.stat-label`/`.stat-value`/`.stat-detail` pattern; icons are new decorative glyphs (no icon system confirmed in app today, note as new).

**Tabs**
- 5-way tab strip: Causes List (active), Cause Catalog, Linked Failure Modes, Cause Relationships, History — closest existing pattern is `.process-step`/`.process-steps` (a link-based step picker); a true tab-panel-swap does not exist, so this is a new pattern applied to `.process-steps` styling (each tab is a full page link, not a JS panel swap).

**Filter/toolbar row**
- Text search box "Search causes..." — new text `<input>` in a `.toolbar`.
- 5 `<select>` filters: Source, Cause Type, Category, Status, Linked to FMEA — existing server-side `<select>` filter pattern (`.panel.compact` GET form).
- "More Filters" button (funnel icon) — new; implies an additional filter drawer/panel not itself specified in the mockup.

**Main table (left ~2/3)**
- `.table-shell` wrapping a `<table>` with header row: checkbox (select-all), ID, Cause Description, Cause Type, Category, Source, Linked FM, Influence (1-10), Status, Last Updated, Actions — existing `.table-shell` pattern; per-row checkbox and select-all are new (no bulk-select pattern confirmed elsewhere).
- 10 data rows, each: row checkbox, ID text, description (`.cell-item`/`.cell-detail`), Cause Type text, Category text, Source badge (`.status`-style pill, green "Catalog" / purple "User"), Linked FM as comma-separated link list (`.cell-list`), Influence integer, Status badge (`.status-accepted`-style green "Active" / amber "Under Review" using existing status-color vocabulary), Last Updated date, Actions cell (eye/view icon + "…" overflow menu — overflow menu is new, no per-row context-menu JS exists today).
- Pagination footer: "Showing 1 to 10 of 214 causes" text, page-number links "‹ 1 2 3 … 22 ›", "10 / page" page-size `<select>` — existing pagination pattern (Django `Paginator` + GET params).

**Analytics row (4 widgets, full width)**
- "Causes by Type" donut chart (Chart.js donut, center total label, side legend list with counts/percents) — new: no page today wires Chart.js.
- "Causes by Category (Top 8)" horizontal bar chart (Chart.js bar, horizontal orientation) — new.
- "Influence Distribution" donut chart (3-band: High/Medium/Low with red/amber/green) — new, reuses `.risk-band-*` color vocabulary conceptually.
- "Top Causes by Linked FM" mini `.table-shell` (Cause ID / Description / Linked FM Count) + "View All" link — existing table pattern + existing link pattern.

**Connections Overview strip (bottom left)**
- 7 stat chips joined by 6 arrow icons (Linked to FMEA Items → Linked Failure Modes → Complaints/Claims → XDA Investigations → 8D Cases → RCA Analyses → 5 Why Analyses) — new composite widget; no chained-chip-with-arrows pattern exists today (closest primitive is `.stat-tile`, but arrows between tiles are new CSS).

**Quick Actions panel (bottom right)**
- 6 icon buttons: New Cause, Add to Catalog, Link to FMEA, Create Action, Start 8D, Open XDA — existing `.icon-button`/`.button-row` pattern for the buttons themselves; the panel layout (icon grid in a `.panel`) is a straightforward reuse.

**Detail panel (right rail, persistent, ~1/3 width)**
- Panel header: "Cause Details" title + "X" close icon — new: no persistent right-rail pattern exists anywhere in the app today (existing panels are inline `.panel` blocks in normal document flow, not a fixed/sticky side rail).
- Record header: "C-0003" large id + "User Defined" badge pill.
- "Cause Information" label/value block (Description, Cause Type, Category, Source, Influence with color, Status pill, Responsible avatar+name, Created, Last Updated, Notes) — existing `.attribute-table`/label-value pattern.
- "Linked To" block (Failure Modes/FMEA Items/Complaints/Related XDA/8D/RCA/5-Why/Ishikawa/FTA, each with count + "View" link or external-link icon) — existing `.related-list` pattern for the list; external-link icon rows are a minor visual addition.
- Two footer buttons: "Edit Cause", "Create Action" — existing `.button-row` pattern.

**Footer**
- Status bar: Database/User/Role/Workspace/Version/System Status (green dot) — existing global footer pattern (not page-specific).

**Sidebar**
- Full nav tree as described in the spec (FMEA WORKSPACE, CONTEXT, FMEA ANALYSIS, FMEA ELEMENTS with "Causes" active, SUPPORTING APPS, ANALYSIS TOOLS, Settings, Collapse) — existing `.sidebar`/`.sidebar-nav`/`.nav-group`/`.nav-group-title`/`.nav-link` pattern; active-link highlighting already exists in `app.js`.

### 3. GUI Coding Requirements

**Route + template**: `fmea:causes_list` → `django_app/fmea_app/templates/fmea_app/causes_list.html`. (A dedicated detail-panel partial, e.g. `causes_detail_panel.html`, could be included for the right rail to allow future reuse from a "Linked Failure Modes" tab.)

**Layout structure**:
- Use `.content-shell` for the page body.
- KPI row: `.grid` of 6 `.stat-tile.span-2` (or nearest divisor of 12).
- Tabs: reuse `.process-steps`/`.process-step` styling as a 5-item link row (each tab is a distinct URL/view, not a client-side panel swap — consistent with this app having no JS panel-swap capability).
- Filter row: a `.panel.compact` GET `<form method="get">` with the search input and 5 `<select name="...">` filters, submitting to the same view.
- Main body: `.split` (or `.grid` with `.span-8`/`.span-4`) — left `.span-8` holding the `.table-shell` + pagination, right `.span-4` holding the new persistent detail rail.
- **New pattern needed — persistent right-hand detail rail**: nothing in the existing CSS provides a sticky/fixed side panel that stays visible next to a table; today's `.panel` blocks all flow normally in the document. Add a new CSS class (e.g. `.detail-rail`) using `position: sticky; top: <header-height>` inside the right grid column, styled with the existing `.panel`/`.panel-heading` look. No new JS is required to *display* it (it can render server-side, pre-populated for whichever cause the query string selects); a "select row → repopulate rail" interaction would need either (a) a full page reload with a `?cause_id=` GET param re-rendering the same template with a different selected cause (consistent with this app's server-render/GET-reload philosophy), or (b) new client-side JS to swap panel content without reload — recommend (a) to stay consistent with the rest of the app.
- Analytics row: `.grid` of 4 `.panel.span-3` cards, each containing a `<canvas>` for Chart.js.
- **New pattern needed — charts**: Chart.js is vendored but wired into zero pages today. Each donut/bar card needs a `<canvas id="...">` plus a small inline `<script>` block (in the same minimal vanilla-JS spirit as `app.js`) that reads a JSON data blob (rendered server-side via `{{ chart_data|json_script:"causes-by-type-data" }}` or similar) and calls `new Chart(ctx, {...})`. The horizontal "Causes by Category" bar is Chart.js's stock `bar` type with `indexAxis: 'y'` — no new library needed for that one.
- Connections Overview strip: a `.panel` containing a flex row of `.stat-tile`-styled chips separated by an arrow glyph/icon — new minimal CSS only (no JS), no existing "chip chain" component.
- Quick Actions panel: `.panel` with a `.grid` of `.icon-button` elements — existing components, new grid arrangement only.
- Footer: reuse existing global status-bar partial.
- Sidebar: reuse existing `.sidebar` partial; this mockup's own FMEA ELEMENTS grouping (bundling Prevention/Detection Controls and Actions with Functions/Failure Modes/Effects/Causes) can be followed as one candidate structure.

**Per-widget data binding**:
- Total Causes KPI — binds to real aggregate: `FailureCause.objects.count()` (scoped to project's FMEAs).
- Cause Description / ID / basic list rows — binds to real `FailureCause.name`/`.description` and primary key.
- Linked FM column (single value case) / "Linked Failure Modes" tab — binds to real `FailureCause.failure_mode` FK (reverse or forward, one hop) for the *current* single-FK model; the mockup's *multi*-FM-per-cause display is placeholder — no real data source yet, needs a catalog/many-to-many relationship that doesn't exist.
- From Catalog / New (User Defined) split, Source column/badge/filter — no real data source yet — render as static/placeholder content until a proposed `source` field and a genuine Cause Catalog entity exist.
- Cause Type / Category columns and filters — no real data source yet — needs proposed `cause_type`/`category` fields.
- Influence (1-10) column, High Influence KPI, Influence Distribution donut — no real data source yet — needs a proposed `influence` integer field.
- Status column/badge/filter — no real data source yet — needs a proposed `status` field and workflow.
- Responsible field — no real data source yet — needs a proposed owner field (precedent: `RecommendedAction.responsible_role` on a different model).
- Created / Last Updated in detail panel and table — no real data source yet — needs proposed audit/timestamp fields.
- Notes field — no real data source yet — proposed free-text field distinct from Description.
- Complaints/Claims, Related XDA, 8D, RCA, 5-Why, Ishikawa, FTA cross-links — no real data source yet — none of these entities exist.
- Causes by Type donut / Causes by Category bar — computed aggregate over real data, but blocked until the proposed `cause_type`/`category` fields exist.
- Connections Overview chain — "Linked to FMEA Items"/"Linked Failure Modes" nodes could become real aggregates once the FK/M2M relationship is clarified; the remaining nodes (Complaints, XDA, 8D, RCA, 5-Why) have no real data source yet.
- Quick Actions: "New Cause" and "Create Action" trigger real create flows (`FailureCause`, `RecommendedAction.failure_cause`); "Add to Catalog", "Start 8D", "Open XDA" have no real data source yet.
- Edit Cause button — binds to real fields (`name`/`description`) today; other fields on the edit form are placeholder until they exist.
- Cause Catalog / Cause Relationships / History tabs — no real data source yet, each needs a new model.

**Filtering/interaction**: all 5 dropdown filters plus the search box submit via a server-side `<form method="get">` to the same view, re-rendering the full page with filtered querysets — no client-side/AJAX filtering, consistent with the rest of the app. Pagination and page-size selection are likewise GET-param-driven full reloads.

**Sidebar entry**: belongs under **FMEA ELEMENTS**, as this mockup itself shows ("Causes" active in that group, alongside Functions, Failure Modes, Effects, Prevention Controls, Detection Controls, Actions). Note: this differs from mockup-17's sidebar, which pulls Prevention/Detection Controls and Actions out into a separate "RISK & ACTIONS" group — not reconciled here.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 17 — Risk Trajectory & Propagation: GUI Coding Requirements

### 1. Features & Content

1. Track high-risk-item counts at a glance via a 6-tile KPI row (initial vs. current high-risk counts, average AP reduction, PM-PFMEA-controlled count, revalidation-due count, uncontrolled-propagation-path count).
2. Browse a table of risk trajectories, one row per FMEA item, showing risk evolution across a fixed sequence of lifecycle-phase columns (each cell an inline mini sparkline) plus a trend indicator.
3. Switch between six views via tabs: trajectory table, propagation view, risk heat map, PM-PFMEA impact, risk summary, and history; plus "Baseline" and "Compare" mode buttons.
4. Filter the trajectory table by view mode, FMEA type, lifecycle phase, status, and a "High risks only" checkbox.
5. See a mid-page "Risk Propagation Preview" — a 5-node horizontal chain diagram (failure mode → local effect → next-level effect → system effect → end effect) with per-node severity and a propagation-probability gauge, for the currently selected risk item.
6. See a "How Risk Was Reduced" table listing the specific actions/controls that drove S/O/D changes for the selected item.
7. See project-wide risk-reduction analytics: PM-PFMEA impact split (donut), average occurrence before/after (bar pair), average detection before/after (bar pair), residual risk distribution (donut).
8. Inspect one risk item in depth in a persistent right-hand "Risk Details" rail: initial-vs-current S/O/D/RPN/AP comparison, reduction %, primary cause, linked function/effects, linked PM-PFMEA item, action-status counts, and a ranked "Top Residual Risks" mini table.

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Brand block, page title "Risk Trajectory & Propagation" + info icon, subtitle line — existing header pattern.
- Project selector, search box, bell (badge "3"), help icon, avatar — existing global chrome, reused.

**KPI row**
- 6 `.stat-tile` cards: Initial High Risks, Current High Risks, AP Reduced, PM-PFMEA Controlled, Revalidation Required, Uncontrolled Propagation — existing `.stat-tile` pattern; icons are new decorative glyphs.

**Tabs + mode controls**
- 6-way tab strip: Risk Trajectory (active), Risk Propagation, Risk Heat Map, PM-PFMEA Impact, Risk Summary, History — same `.process-steps`-as-tabs adaptation as mockup-16.
- "Baseline" and "Compare" buttons to the right of the tabs — existing `.button` styling; the underlying diff/snapshot behavior is new (see Section 3).

**Filter row**
- "View:" dropdown ("Risk Trajectory (by FMEA Item)"), "FMEA Type: All", "Lifecycle Phase: All", "Status: All" — existing server-side `<select>` filter pattern.
- Checkbox "Show only High risks" — new plain `<input type="checkbox">` in the filter form (no existing checkbox-filter precedent, but trivial addition to the GET form).
- "More Filters" button — new, implies an unspecified additional filter drawer.
- Zoom-in/zoom-out/export icon trio above the table — new; implies enlarging the sparkline cells into a full chart (client-side or link-through — see Section 3).

**Risk Trajectory table**
- `.table-shell` with columns: ID, FMEA Item, Type, [6 lifecycle-phase columns each containing an inline mini line-chart], Trend arrow — existing table shell for the structural columns; the inline-sparkline-per-cell pattern is entirely new (no sparkline widget exists anywhere today).
- 5 data rows (FM-021, FM-034, FM-041, FM-052, FM-063), each with colored-dot sparkline series and a color-coded trend arrow.
- Pagination footer — existing pattern.

**Mid-page panels (2, side by side)**
- "Risk Propagation Preview (FM-021)" panel: 5 connected boxes (chain diagram) each with a Severity value, plus a horizontal gradient gauge bar with tick labels and a 3-item legend (Low/Medium/High), plus "Open Full Propagation" button — entirely new composite widget; no chain-diagram or gradient-gauge primitive exists in the current CSS/JS.
- "How Risk Was Reduced (FM-021)" table: `.table-shell` with columns Action/Control, Type, Implemented In, Impact, O, D, plus a small legend row (↓↓/↓/— symbols) — existing table shell + new legend row.

**Bottom analytics row (4 widgets)**
- "PM-PFMEA Impact Summary" donut chart — new Chart.js donut.
- "Impact on Occurrence (O)" — two horizontal bars (Initial vs Current) + reduction % text — new Chart.js horizontal bar (2-value) or hand-built bar pair.
- "Impact on Detection (D)" — same pattern as above.
- "Residual Risk Distribution" donut chart — new Chart.js donut.

**Detail panel (right rail, persistent)**
- Header: "FM-021" + "High" badge, subheading with name + FMEA-type badge + status badge — existing badge/pill pattern (`.status-*`, `.risk-*`).
- "Risk Overview" two-column comparison table (Initial vs Current: S/O/D/RPN/AP) — existing `.attribute-table` pattern extended to two value columns.
- "Reduction" block: RPN Reduction progress bar (85.0%) + AP Improvement text ("High → Medium") — progress bar is new (no progress-bar component exists today; could reuse the horizontal-bar-gauge CSS built for the propagation-probability gauge above).
- Primary Cause, Linked Function — existing `.related-list`/label-value pattern.
- Linked Effects list (3 items with level tags) — existing list pattern; level tags ("Local"/"Next level"/"System") are new decorative labels.
- Linked PM-PFMEA (name + View link) — existing pattern.
- "Actions Impacting This Risk" counts (Total/Closed/In Progress/Open) — existing stat-style inline block.
- Buttons: "View Propagation", "View History", "Edit Risk" — existing `.button-row`.
- "Top Residual Risks" mini table + "View All High/Medium Risks" button — existing mini-table + link pattern.

**Footer**: standard status bar — existing pattern.

**Sidebar**: FMEA WORKSPACE, CONTEXT, FMEA ANALYSIS (with FMEA Matrix), FMEA ELEMENTS (Functions/Failure Modes/Effects/Causes only), RISK & ACTIONS (Prevention Controls/Detection Controls/Actions), VALIDATION & CHANGE (Evidence & Tests/Validation Trajectory/Risk Trajectory active/Change Impact), Settings, Collapse — existing `.sidebar` pattern; no ANALYSIS TOOLS group here.

### 3. GUI Coding Requirements

**Route + template**: `fmea:risk_trajectory` → `django_app/fmea_app/templates/fmea_app/risk_trajectory.html`.

**Layout structure**:
- `.content-shell` root; KPI row as `.grid` of 6 `.stat-tile.span-2`.
- Tabs as `.process-steps` adaptation, with "Baseline"/"Compare" as two `.button`s inline to the right (`.split` or flex row).
- Filter row as a `.panel.compact` GET `<form>`.
- Trajectory table: `.table-shell`. **New pattern needed — inline sparkline cells**: no existing widget draws a small multi-point line inside a table cell. Two viable approaches in this app's vanilla-JS spirit: (a) render each sparkline as a tiny inline SVG built server-side in the template (a `<svg>` with `<polyline>`/`<circle>` points computed from the row's S/O/D/RPN values per phase — no JS needed, pure template logic), or (b) a small shared JS helper (`sparkline.js`, loaded once) that reads a `data-points="240,144,72,48,36,36"` attribute per `<td>` and draws a `<canvas>` sparkline on page load. Recommend (a) for consistency with this app having no charting JS wired in anywhere yet outside the newly-decided Chart.js donuts/bars.
- Mid-page two-panel row: `.grid` with two `.panel.span-6`.
  - **New pattern needed — propagation chain diagram**: no box-and-arrow chain component exists. Build as a flex row of `.panel`-styled boxes (or a plain bordered `<div>` each) separated by an arrow character/icon, each box showing name + a `.status`-style Severity chip below it — pure CSS, no JS required for a static chain like this.
  - **New pattern needed — gradient gauge bar**: no gauge/meter component exists. Build as a `<div>` with a CSS `linear-gradient` background (green→amber→red), tick marks as absolutely-positioned small `<span>` labels, and a marker element positioned via inline `style="left: X%"` computed server-side from the propagation-probability value.
  - "How Risk Was Reduced" table: `.table-shell` + a small legend row below it (plain text/icons, no new component).
- Bottom analytics row: `.grid` of 4 `.panel.span-3`, each with a `<canvas>` for Chart.js donuts, and the two "Impact on O/D" cards using Chart.js horizontal bars (2 bars each) — same Chart.js wiring pattern as mockup-16 (server-rendered JSON via `json_script` + small inline `<script>` per canvas).
- Detail rail: same **new persistent right-rail pattern** as mockup-16 (`.detail-rail` with `position: sticky`), spanning from below the header down past the mid panels. The "RPN Reduction" progress bar reuses the gradient-gauge CSS built above, simplified to a single-color fill.
- Sidebar: reuse existing `.sidebar` partial with this mockup's own grouping (RISK & ACTIONS, VALIDATION & CHANGE) as one candidate.

**Per-widget data binding**:
- Current High Risks / trajectory "Current" phase column — binds to a computed aggregate: latest `RiskEvaluation` per `FailureMode` (via existing `-evaluated_at` ordering + `.first()`), filtered/thresholded at RPN ≥ 100.
- Initial High Risks / trajectory "baseline" phase values — binds to a computed aggregate, but the query itself (earliest `RiskEvaluation` per failure mode) does not exist yet and needs to be written; the *data* it draws on (`RiskEvaluation.severity/occurrence/detection/result`) is real.
- AP Reduced (66%) — no real data source yet as specified — `RiskEvaluation.result` carries a categorical AP-style classification, not the numeric proxy this KPI implies; needs a defined scoring rule before this becomes a real aggregate.
- PM-PFMEA Controlled KPI, PM-PFMEA Impact donut, "Linked PM-PFMEA" panel field — no real data source yet — no cross-FMEA link between a PFMEA's `FailureMode` and a PM-FMEA item exists.
- Revalidation Required KPI — no real data source yet — no evidence/test-expiry model confirmed in the grounded domain model for this batch.
- Uncontrolled Propagation KPI — no real data source yet — no propagation-path model exists.
- Lifecycle-phase columns (Concept/DV/PV/PPAP/SOP/Current) — no real data source yet — `RiskEvaluation` has no lifecycle-phase field; would need a proposed field or join model plus a fixed phase vocabulary.
- Trend arrow column — computed aggregate once the phase-history data above exists; not available today.
- Risk Propagation Preview chain + per-node Severity — no real data source yet — `FailureEffect` has no propagation-chain relationship and no per-effect severity field.
- Propagation Probability gauge — no real data source yet — no defined formula exists anywhere in the model.
- "How Risk Was Reduced" table rows for `RecommendedAction`/`PreventionControl`/`DetectionControl` entities themselves — bind to real data (`RecommendedAction`, `PreventionControl.failure_cause`, `DetectionControl.failure_cause`); the "Implemented In" phase tag and the O/D before→after delta columns — no real data source yet.
- Impact on Occurrence (O) / Impact on Detection (D) bars — binds to a computed aggregate: average `RiskEvaluation.occurrence`/`.detection` across earliest vs. latest evaluation per failure mode, project-wide (new query, real fields).
- Residual Risk Distribution donut — binds to a computed aggregate over the latest `RiskEvaluation.result` classification per failure mode.
- Risk Details panel — Risk Overview (S/O/D/RPN/AP, Current) — binds to real `RiskEvaluation.severity/.occurrence/.detection/.result`, already available via `.first()`. The "Initial" column needs the same new earliest-query as above.
- RPN Reduction % / AP Improvement — computed aggregate (simple arithmetic) once Initial and Current values are both available.
- Primary Cause — binds to real `FailureMode.causes` reverse relation.
- Linked Function — binds to real `FailureMode.function` FK.
- Linked Effects list — base list binds to real `FailureMode.effects`; the "(Local)"/"(Next level)"/"(System)" level tags have no real data source yet.
- Actions Impacting This Risk counts — computed aggregate over real `RecommendedAction.status`, grouped by failure mode/cause (note: mockup's "Closed" bucket needs a defined mapping, e.g. `completed`+`verified` → "Closed", since no literal `closed` status exists in the real enum).
- Top Residual Risks mini table — computed aggregate: latest `RiskEvaluation` per failure mode, sorted by RPN descending.
- Baseline / Compare buttons — no real data source yet — no explicit baseline-snapshot concept exists on `RiskEvaluation` (only chronological evaluations).

**Filtering/interaction**: View/FMEA Type/Lifecycle Phase/Status dropdowns and the "Show only High risks" checkbox all submit via a server-side GET form reload — no client-side/AJAX filtering. Zoom icons above the table, if built, would most plausibly link through to a separate full-chart view/page rather than an in-place JS zoom, consistent with this app having no client-side chart-manipulation JS.

**Sidebar entry**: belongs under a new **VALIDATION & CHANGE** group as this mockup shows it (alongside Evidence & Tests, Validation Trajectory, Change Impact). Note this differs sharply from mockup-16, which has no such group and instead files Risk Trajectory nowhere comparable, and from mockup-18/19, which use yet other group names/compositions ("RISK & ACTIONS" holding different member sets) — not reconciled here.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 18 — Effects: GUI Coding Requirements

### 1. Features & Content

1. Browse all effects across the current FMEA project with a paginated table (implied by the "Effects List" tab; the default view here is a dashboard, not a list).
2. See at-a-glance volume/severity/propagation stats via a 7-tile KPI row (total effects, high-severity count, "affects system" count, total propagation paths, improved count, worsened count, last-updated).
3. Switch between six views via tabs: Effects Impact Dashboard (active/default), Effects List, Effect Catalog, Linked Failure Modes, Effect Relationships, History.
4. Filter the dashboard by FMEA type, lifecycle phase, view mode, and a "Compare To: Baseline" mode.
5. See a numbered, ordered sequence of seven impact-analysis widgets: an AP/RPN trend-over-lifecycle-phase line chart; a stacked-bar breakdown of improved/no-change/worsened effects by target category (system functions, requirements, characteristics, components, processes, customers, safety); a diverging-bar breakdown by effect level (Local through End Effect); two ranked "top movers" tables (most-improved and most-worsened effects); a 5-stage Sankey-style flow diagram showing how effects propagate and shift risk category stage-to-stage; and a diverging-bar breakdown of AP impact per top-10 requirement.
6. Inspect one effect in depth in a persistent right-hand "Effect Details" rail: classification, severity, source, linked entities (failure modes, FMEA items, causes, functions, requirements, next-level/end effects), and a "Quick Impact" mini trajectory chart.
7. Create, edit, import, export, and generate reports for effects via header-level action buttons.

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Brand block, page title "Effects" + info icon + a pin/star icon (not seen on mockup-16/17), subtitle line — existing header pattern, with a new "pin" icon element.
- Project selector, search box, bell (badge "6"), help icon, avatar — existing global chrome.
- Action row: "+ New Effect", Import, Export, Reports, Filters — existing pattern.

**KPI row**
- 7 `.stat-tile` cards: Total Effects, High Severity (S ≥ 7), Affects System, Propagation Paths, Improved (↓ AP/RPN), Worsened (↑ AP/RPN), Last Updated — existing `.stat-tile` pattern, one card wider than the 6-card rows on other pages (still fits `.grid`).

**Tabs**
- 6-way tab strip: Effects Impact Dashboard (active), Effects List, Effect Catalog, Linked Failure Modes, Effect Relationships, History — same `.process-steps` adaptation.

**Filter row**
- "FMEA Type: All", "Lifecycle Phase: All", "View: Impact Overview", "Compare To: Baseline" dropdowns, "More Filters" button — existing server-side `<select>` filter pattern.

**Dashboard grid — 7 numbered widgets**
1. "Impact on Risk Priority (AP)" — dual-Y-axis multi-line chart (3 series) with % callout badges and a "Compared to Baseline" caption — new Chart.js line chart with dual axes; the callout badges are new decorative elements positioned beside the chart.
2. "Impact Distribution by Target" — horizontal stacked bar chart, 3-segment legend (Improved/No Change/Worsened), 7 category rows — new Chart.js stacked horizontal bar.
3. "Impact by Effect Level" — diverging bar chart (Increase/Decrease/Net, 5 level rows) — new: this is a diverging (bidirectional, ± from center) bar layout. Chart.js's stock `bar` type supports negative values on a shared axis (bars extend left/right from zero), so this is achievable with Chart.js directly — no separate library needed, but it is not the plain single-direction bar covered by prior pages; confirm at build time.
4. "Top Effects by AP Improvement" — `.table-shell` (Effect/Initial AP/Current AP/Change/Trend) + "View All" button — existing table + link pattern.
5. "Top Effects with Increased Risk" — same table pattern as widget 4.
6. "Effect Propagation Overview (All Effects)" — 5-stage Sankey-style flow diagram with stacked/segmented stage blocks and ribbon connectors between stages, plus a "Propagation Paths" count row and "Open Propagation Explorer" button — entirely new; **not** a Chart.js donut/line/bar and **not** covered by the existing charting-library decision. No Sankey/ribbon-flow primitive exists anywhere in this codebase.
7. "Impact on Key Requirements (Top 10)" — diverging stacked bar chart per requirement (Improved/No Change/Increased/Net) — same diverging-bar approach as widget 3, applied per-requirement-row.

**Detail panel (right rail, persistent)**
- Header "E-004" + "Active" badge + "Local Effect" badge — existing badge pattern.
- "Effect Information" label/value block (Description, Effect Type, Effect Level, Severity, End Effect, Source, Created, Last Updated, Notes) — existing `.attribute-table` pattern.
- "Linked To" block (Failure Modes/FMEA Items/Causes/Functions/Requirements/Next Level Effects/End Effect, each with count + View link) — existing `.related-list` pattern.
- Action buttons: "View Propagation", "Create Action", "Edit Effect" — existing `.button-row`.
- "Quick Impact" block: Initial AP/Current AP/Change text + small inline trajectory line chart with dot markers + "View Full Trajectory" button — new small Chart.js line (or inline SVG sparkline, same approach recommended in mockup-17) embedded inside the detail rail.

**Footer**: standard status bar — existing pattern.

**Sidebar**: FMEA WORKSPACE, CONTEXT, FMEA ANALYSIS (with FMEA Matrix), FMEA ELEMENTS (all seven: Functions/Failure Modes/Effects active/Causes/Prevention/Detection/Actions together), RISK & ACTIONS (Risk Trajectory + Change Impact only, here), VALIDATION & CHANGE (Evidence & Tests + Validation Trajectory only, here — no Risk Trajectory/Change Impact), Settings, Collapse — existing `.sidebar` pattern; no ANALYSIS TOOLS group.

### 3. GUI Coding Requirements

**Route + template**: `fmea:effects_dashboard` → `django_app/fmea_app/templates/fmea_app/effects_dashboard.html`. (A separate `fmea:effects_list` / `effects_list.html` would serve the plain "Effects List" tab, mirroring the worksheet-style rendering already used for effects inside `fmea_detail.html`, but as a new standalone cross-cutting page — same category of build as the already-built Engineering Context page, not a new display of already-worksheet-shown data.)

**Layout structure**:
- `.content-shell` root; KPI row as `.grid` of 7 `.stat-tile` cards.
- Tabs as `.process-steps` adaptation.
- Filter row as `.panel.compact` GET `<form>`.
- Dashboard grid: `.grid` rows — widgets 1–2 as two `.panel.span-6`; widgets 3–4–5 as three `.panel.span-4`; widgets 6–7 as two `.panel.span-6` (or `.span-12` each, stacked, given their density).
- Widgets 1, 2, 4, 5, 7 use the standard **new Chart.js wiring pattern** established in mockup-16/17 (server-rendered JSON via `json_script` + a small inline `<script>` per `<canvas>`); widget 3 and 7's diverging-bar shape uses Chart.js's stock `bar` config with a value range spanning negative-to-positive.
- **New pattern needed — Sankey/ribbon flow diagram (widget 6)**: explicitly out of scope for the existing line/bar/donut Chart.js decision. Two paths: (a) a separate charting-library decision (e.g., a dedicated Sankey/D3 library) would need to be made first and vetted against the CDN allowlist/vendoring approach this project uses for Chart.js, or (b) a hand-built inline SVG per the stage/band/ribbon geometry, computed server-side from the stage counts and rendered as static markup (consistent with this app's plain-template, no-framework approach, at the cost of no interactivity). Flag this as needing its own scoping decision before implementation, independent of this document.
- Detail rail: same **new persistent right-rail pattern** (`.detail-rail`, `position: sticky`) as mockup-16/17, containing the "Quick Impact" mini chart as a small embedded `<canvas>` or inline-SVG sparkline.
- Sidebar: reuse existing `.sidebar` partial with this mockup's own grouping as one candidate.

**Per-widget data binding**:
- Total Effects KPI — binds to real aggregate: `FailureEffect.objects.count()`.
- Effects List rows / detail-panel Description — binds to real `FailureEffect.name`/`.description`.
- High Severity (S ≥ 7) KPI, detail-panel Severity field — no real data source yet — `FailureEffect` has no severity field; severity today lives only on `RiskEvaluation`, scoped to `FailureMode`, not to an individual effect.
- Affects System KPI, Effect Type field, Effect Level field, End Effect flag — no real data source yet — no such classification fields exist on `FailureEffect`.
- Propagation Paths KPI, widget 6 Sankey, "Next Level Effects"/"End Effect" detail-panel links — no real data source yet — no propagation-chain relationship exists on `FailureEffect`.
- Improved / Worsened KPIs — no real data source yet — blocked on attributing AP/RPN to an individual effect (which requires the Severity-per-effect gap above to be resolved first).
- Effects List / Linked Failure Modes tabs — Effects List binds to real `FailureEffect` fields; Linked Failure Modes binds to a computed aggregate over the real `failure_mode` FK (reverse relation), noting the mockup's later "7 linked failure modes for one effect" panel value implies a many-to-many the real single FK doesn't support — that specific display is placeholder pending a catalog/M2M redesign.
- Effect Catalog / Effect Relationships / History tabs — no real data source yet — no catalog entity, no effect-to-effect relationship model, no audit/history model.
- Widget 1 (AP/RPN trend line) — no real data source yet — needs both the lifecycle-phase-gate tracking flagged absent in mockup-17 and per-effect AP/RPN attribution.
- Widget 2 (Impact Distribution by Target) — mixed: the "System Functions" and "Requirements" rows bind to a computed aggregate via the real `FailureMode.function` and `FailureMode.requirement` FKs (once trend/AP data exists); "Characteristics", "Components", "Customers", "Safety" rows have no real data source yet (no modeled relationship to `FailureEffect`/`FailureMode`).
- Widget 3 (Impact by Effect Level) — no real data source yet — depends on the 5-level effect-hierarchy gap.
- Widgets 4 & 5 (Top movers tables) — no real data source yet — same per-effect AP-tracking gap as the Improved/Worsened KPIs.
- Widget 6 (Sankey) — no real data source yet, as above, plus its own separate charting-technology gap.
- Widget 7 (Impact on Key Requirements) — binds to a computed aggregate over real relationships: `FailureEffect → FailureMode → Requirement` join (both `Requirement` and `FailureMode.requirement` are real), bucketed by AP-trend once trend data exists.
- Detail panel Effect Type/Level/Severity/End Effect/Source — all no real data source yet, except Source ("Design FMEA") which could plausibly bind to a computed/derived value from `failure_mode.fmea`'s FMEA-type attribute (a real field) once a display-layer label mapping is written.
- Created/Last Updated (with actor), Notes — no real data source yet.
- Linked To: Failure Modes (multi-count), FMEA Items — no real data source yet as a multi-linked display (same single-FK-vs-shown-multi gap as mockup-16's Causes).
- Linked To: Causes — no real data source yet — no direct `FailureCause`↔`FailureEffect` relationship exists in the model.
- Linked To: Functions, Requirements — bind to real data via `failure_mode.function`/`.requirement` (one-hop join).
- Linked To: Next Level Effects / End Effect — no real data source yet.
- Quick Impact block — no real data source yet — combines the per-effect-AP gap and the lifecycle-phase gap.
- "Create Action" button — binds to real `RecommendedAction.failure_mode`/`.failure_cause` FKs, with a caveat: since `RecommendedAction` has no `failure_effect` FK, an action created from an Effect screen would need to resolve back to the effect's parent failure mode.

**Filtering/interaction**: FMEA Type/Lifecycle Phase/View/Compare-To dropdowns submit via a server-side GET form reload — no client-side/AJAX filtering.

**Sidebar entry**: belongs under **FMEA ELEMENTS** as this mockup shows it (all seven element types together, "Effects" active). Note this differs from mockup-17, which pulls Prevention/Detection Controls and Actions out of FMEA ELEMENTS into "RISK & ACTIONS" — and from mockup-16, whose FMEA ELEMENTS composition matches this one but whose top-level group names/counts differ elsewhere on the page (e.g. a full ANALYSIS TOOLS section absent here) — not reconciled.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 19 — Preventive Controls: GUI Coding Requirements

### 1. Features & Content

1. Browse all preventive controls across the current FMEA project in a paginated table with row thumbnail photos (156 controls).
2. See at-a-glance stats via a 6-tile KPI row (total, effective count, average occurrence-reduction achieved, high-impact count, linked-to-operations count, last-updated).
3. Switch between five sub-views via tabs: Controls Overview, Controls List (active), Control Categories, Linked Failure Modes, History.
4. Filter the list by category, type, control type, effectiveness, and linked-to state, plus free-text search.
5. Browse/filter controls by category using a left-hand category nav list (with per-category counts) that doubles as a page-scoped filter, plus a "+ New Category" affordance for managing the category set itself.
6. Inspect one control in depth in a persistent right-hand "Control Details" rail: classification (category/type/control type), description, effectiveness, implementation location, owner, status, timestamps, review-due date, linked entities (failure modes/causes/functions/operations controls), a "Resource Used" sub-block (equipment identity, quantity, location, calibration interval, reference ID, thumbnail), and an attached-document row.
7. See summary analytics: breakdown by control type (donut), effectiveness-vs-occurrence-reduction correlation (scatter), linked-vs-not-linked-to-operations split (donut), and a ranked "top controls by occurrence reduction" table.
8. Toggle between grid and list view of the controls table (view-mode toggle icons).
9. Create, edit, import, export, and generate reports for preventive controls via header-level action buttons.

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Brand block, page title "Preventive Controls" + info icon, subtitle line — existing header pattern.
- Project selector, search box, bell (badge "2"), help icon, avatar — existing global chrome.
- Action row: "+ New Control", Import, Export, Reports, Filters — existing pattern.

**KPI row**
- 6 `.stat-tile` cards: Total Controls, Effective Controls, Occurrence Reduction, High Impact Controls, Linked to Operations, Last Updated — existing `.stat-tile` pattern.

**Tabs**
- 5-way tab strip: Controls Overview, Controls List (active), Control Categories, Linked Failure Modes, History — same `.process-steps` adaptation as prior mockups.

**Filter row**
- Search box "Search controls..." + 5 `<select>` filters (Category, Type, Control Type, Effectiveness, Linked To), "More Filters" button — existing server-side filter pattern.

**Left panel — Control Categories (region 1)**
- Vertical list: "All Categories" (selected, highlighted) + 10 named categories, each with a count — existing `.nav-link`-style list styling repurposed as an in-page filter list (new: no existing "selectable filter list" component distinct from the sidebar nav; would reuse the same visual language but needs its own click-through-as-GET-filter behavior).
- "+ New Category" button at bottom — existing `.button` pattern.

**Center — Preventive Controls List (region 2)**
- "View:" grid/list toggle icon pair, top right of this panel — new; no existing view-mode-toggle component (would need new minimal JS, similar in spirit to the sidebar-collapse toggle in `app.js`, to swap a CSS class and re-render row layout — or, more simply, a GET param that re-renders server-side in one of two template partials).
- `.table-shell` with columns: [thumbnail image], Control Name, Category, Type, Control Type, Linked To, Effectiveness, Operations Link, Resource Used, Actions ("…" menu) — existing table shell; the thumbnail-image column is new (no image-in-table-cell pattern used elsewhere in the app).
- 6 data rows with badges/pills for Category (light-blue/lavender chip), plain text for Type/Control Type, colored text for Effectiveness (green/amber) — existing `.status`-style badge vocabulary extended with a new "category chip" visual variant.
- Pagination footer — existing pattern.

**Right rail — Control Details (region 3, persistent)**
- Header "PC-0234" + "Active" badge + "Process Control" badge — existing badge pattern.
- Thumbnail photo + title — new image element in the rail.
- "Control Information" label/value block (Category, Type, Control Type, Description, Effectiveness, Implemented In, Owner avatar+name, Status pill, Created, Last Updated, Review Due) — existing `.attribute-table` pattern.
- "Linked To" block (Failure Modes/Causes/Functions/Operations Controls, each count + View link) — existing `.related-list` pattern.
- "Resource Used" sub-block (Resource, Quantity, Location, Calibration/Check, Reference/ID, thumbnail) — new composite widget; no equipment/resource-record display pattern exists elsewhere.
- "Attached Documents" — a PDF file row with external-link icon — new; no file/attachment UI pattern exists elsewhere in the app.
- Buttons: "Edit Control", "View History" — existing `.button-row`.

**Analytics row (4 widgets, below the 3-column body)**
- "Controls by Type" donut chart — new Chart.js donut.
- "Effectiveness vs Occurrence Reduction" scatter chart — new Chart.js scatter (a chart type distinct from the line/bar/donut set explicitly decided; needs confirming Chart.js's stock `scatter` type is in scope, or flagging as an additional type beyond the current decision).
- "Linked to Operations Controls" donut chart + "View Operations Controls" button — new Chart.js donut.
- "Top Controls by Occurrence Reduction" `.table-shell` + "View All" button — existing table pattern.

**Footer**: standard status bar — existing pattern.

**Sidebar**: FMEA WORKSPACE, ANALYSIS (System FMEA/DFMEA/PFMEA/PM-PFMEA/FMEA Matrix), FMEA ELEMENTS (Functions/Failure Modes/Effects/Causes/Preventive Controls active/Detection Controls/Actions), RISK & INSIGHTS (Risk Trajectory/Risk Propagation/Change Impact), VALIDATION (Evidence & Tests/Validation Trajectory), Settings, Collapse — existing `.sidebar` pattern; no CONTEXT group and no ANALYSIS TOOLS group here.

### 3. GUI Coding Requirements

**Route + template**: `fmea:preventive_controls_list` → `django_app/fmea_app/templates/fmea_app/preventive_controls_list.html`. (Preventive Controls today render as a section within the `.worksheet`/`.worksheet-wrap` pattern inside `fmea_detail.html`; a standalone page like this is a new cross-cutting page in the same category as the already-built Engineering Context page, not a new display of already-worksheet-shown data.)

**Layout structure**:
- `.content-shell` root; KPI row as `.grid` of 6 `.stat-tile.span-2`.
- Tabs as `.process-steps` adaptation.
- Filter row as `.panel.compact` GET `<form>`.
- Three-column body: `.grid` with left `.span-2`/`.span-3` (Category list), center `.span-6`/`.span-7` (table), right `.span-3`/`.span-4` (the **new persistent detail rail** pattern, `position: sticky`, same as mockups 16–18).
- Category list: a `.panel` containing a vertical list of `.nav-link`-styled `<a>` elements, each linking to the same view with a `?category=` GET param (selected state via a `selected`/active CSS class matching the current query param) — no new JS needed, purely server-driven like the rest of the app's filtering.
- **New pattern needed — grid/list view toggle**: simplest implementation consistent with this app's server-render approach is a `?view=grid|list` GET param controlling which of two `{% if %}` branches (or two included partials) the template renders — avoids new client-side JS entirely, at the cost of a full reload per toggle (acceptable given the app's existing GET-reload-everywhere philosophy).
- Table: `.table-shell` with an `<img>` thumbnail cell (would need a defined static/media path convention for control-resource photos — not addressed by any existing model field).
- Analytics row: `.grid` of 4 `.panel.span-3`, using the standard Chart.js wiring pattern (server JSON via `json_script` + inline `<script>` per canvas); the scatter chart needs Chart.js's `scatter` chart type, which is a distinct configuration from line/bar/donut and should be confirmed as in-scope before building.
- Detail rail "Resource Used" and "Attached Documents" sub-blocks: render as nested `.attribute-table`/list blocks within the same `.detail-rail` panel; the attached-document row is a plain `<a>` with an icon — no upload/preview capability implied by this static row alone.

**Per-widget data binding**:
- Total Controls KPI — binds to real aggregate: `PreventionControl.objects.count()`.
- Control Name / Description (list + detail panel) — binds to real `PreventionControl.name`/`.description`.
- Effective Controls, Occurrence Reduction, High Impact Controls KPIs — no real data source yet — `PreventionControl` has no effectiveness field and no linkage attributing a specific `RiskEvaluation.occurrence` change to an individual control.
- Linked to Operations KPI — no real data source yet — no Operations module/entity exists anywhere in the codebase.
- Control Categories panel (list + counts + "+ New Category") — no real data source yet — no `category` field or category-management model exists on `PreventionControl`.
- Type column, Control Type column — no real data source yet — two further independent classification axes with no backing fields.
- Linked To (Failure Modes, Causes, Functions) — binds to a computed aggregate over real relationships: `PreventionControl.failure_cause` is a real FK (direct, Causes), with Failure Modes and Functions reachable via one/two further joins (`failure_cause.failure_mode`, then `.function`).
- Effectiveness column/badge — no real data source yet, same gap as the Effective Controls KPI.
- Operations Link column/section — no real data source yet — Operations module absent.
- Resource Used column/section — no real data source yet — no Resource/Equipment model exists in the codebase.
- Attached Documents — no real data source yet — no file/attachment storage capability exists anywhere in the app.
- Owner field — no real data source yet — no owner field on `PreventionControl` (precedent: `RecommendedAction.responsible_role` on a different model).
- Status field/badge — no real data source yet — no status field on `PreventionControl`.
- Created/Last Updated, Review Due — no real data source yet — no audit/timestamp fields, no review-cadence concept.
- Controls by Type donut, Effectiveness vs Occurrence Reduction scatter, Linked to Operations donut, Top Controls by Occurrence Reduction table — no real data source yet, each blocked on one or more of the fields above.
- Controls Overview / Control Categories / Linked Failure Modes / History tabs — Linked Failure Modes binds to a computed aggregate over the real `failure_cause` join; the other three have no real data source yet.
- "+ New Control" / "Edit Control" forms — bind to real fields (`name`/`description`) today; every other field on the form is placeholder until it exists.

**Filtering/interaction**: Category/Type/Control Type/Effectiveness/Linked-To dropdowns, the search box, and the category-list clicks all submit via a server-side GET form reload — no client-side/AJAX filtering. The grid/list view toggle, if built, should follow the same GET-param-reload approach rather than introducing new client-side state.

**Sidebar entry**: belongs under **FMEA ELEMENTS**, as this mockup shows it ("Preventive Controls" active alongside the other six element types). Note two inconsistencies worth flagging as-is (not reconciled): (a) this mockup's sidebar item label reads "Preventive Controls," matching the page title, while mockups 16–18 all use "Prevention Controls" for the equivalent item; (b) this mockup uses top-level group names "ANALYSIS," "RISK & INSIGHTS," and "VALIDATION" that don't match any of mockups 16–18's group names.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 20 — Detection Controls: GUI Coding Requirements

### 1. Features & Content

1. Browse all detection controls across the current FMEA project in a paginated table with row thumbnail photos (142 controls).
2. See at-a-glance stats via a 6-tile KPI row (total, effective count, average detection improvement, high-impact count, total FM/cause link count, last-updated).
3. Switch between seven sub-views via tabs: Overview, Controls List (active), Control Categories, Linked Failure Modes, Cause Relationships, D Improvement Trend, History.
4. Filter the list by category, type, detection method, implemented state, and linked-to state, plus free-text search.
5. Browse/filter controls by category using a left-hand category nav list (with per-category counts) plus a "+ New Category" affordance.
6. Inspect one control in depth in a persistent right-hand "Control Details" rail: classification (category/type/detection method), description, effectiveness, implementation location, owner, status, timestamps, review-due date, linked entities, a "Resource Used" sub-block, and an attached-document row, plus a "Clone" action.
7. See summary analytics: breakdown by control type (donut), detection-improvement distribution by initial D-rating (stacked bar), a ranked "top controls by D improvement" table, and effectiveness distribution (donut).
8. See two additional full-width tables: controls' links to an "Operations Controls" concept, and a "Resource Utilization" ranking of equipment/software used across controls.
9. Toggle between grid and list view of the controls table.
10. Create, edit, import, export, and generate reports for detection controls via header-level action buttons.

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Brand block, page title "Detection Controls" + info icon, subtitle line — existing header pattern.
- Project selector showing "Project: Headlamp X1 - DFMEA" (a different FMEA-type context than mockups 16/17/18/19's "PFMEA"), search box, bell (badge "4"), help icon, avatar — existing global chrome.
- Action row: "+ New Detection Control", Import, Export, Reports, Filters — existing pattern.

**KPI row**
- 6 `.stat-tile` cards: Total Controls, Effective Controls, Detection Improvement, High Impact Controls, Linked FM / Causes, Last Updated — existing `.stat-tile` pattern.

**Tabs**
- 7-way tab strip: Overview, Controls List (active), Control Categories, Linked Failure Modes, Cause Relationships, D Improvement Trend, History — same `.process-steps` adaptation; two more tabs than mockup-19's equivalent (Cause Relationships, D Improvement Trend).

**Filter row**
- Search box "Search detection controls..." + 5 `<select>` filters (Category, Type, Method, Implemented, Linked To) — existing server-side filter pattern. Note: includes a "Method" filter axis not present on mockup-19's filter row.

**Left panel — Detection Control Categories (region 1)**
- Vertical list: "All Categories" (selected) + 8 named categories with counts — same new "selectable filter list" pattern as mockup-19.
- "+ New Category" button — existing `.button` pattern.

**Center — Detection Controls List (region 2)**
- Grid/list view-toggle icons, top right — same new pattern as mockup-19.
- `.table-shell` with columns: [thumbnail], Control Name, Category, Type, Detection Method, Linked To, Effectiveness, Resource Used, Operations Link, Actions — existing table shell + new thumbnail column, same as mockup-19, with **column order reversed** relative to mockup-19 (Resource Used before Operations Link here; the opposite there) — noted, not reconciled.
- 6 data rows with the same badge/chip vocabulary as mockup-19.
- Pagination footer — existing pattern.

**Right rail — Control Details (region 3, persistent)**
- Header "DC-0234" + "Active" badge + "Inspection Control" badge — existing badge pattern.
- Thumbnail photo + title — new image element.
- "Control Information" block (Category, Type, Control Type, Description, Detection Method, Effectiveness, Implemented In, Owner, Status, Created, Last Updated, Review Due) — existing `.attribute-table` pattern; note both "Control Type" and "Detection Method" appear as separate fields here.
- "Linked To" block (Failure Modes/Causes/Functions/Operations Controls) — existing `.related-list` pattern.
- "Resource Used" sub-block (thumbnail + Resource, Location, Calibration/Check, Reference/ID — no Quantity field shown here, unlike mockup-19's equivalent block) — same new composite widget as mockup-19, minus one field.
- "Attached Documents" — new file-row pattern, same as mockup-19.
- Buttons: "Edit Control", "View History", "Clone" — existing `.button-row`; "Clone" is a new action not present on mockup-19's panel.

**Analytics widgets — first row (4 widgets, numbered 3–6)**
- "Controls by Type" donut chart — new Chart.js donut.
- "Detection Improvement (D Rating)" stacked bar chart (X-axis Initial D Rating 1–10, 4-segment legend: ≥2 Improvement/1 Improvement/No Change/Worse) — new Chart.js stacked bar.
- "Top Controls by D Improvement" `.table-shell` + "View All" button — existing table pattern.
- "Controls Effectiveness Distribution" donut chart — new Chart.js donut.

**Analytics widgets — second row (2 full-width widgets, numbered 7–8)**
- "Links to Operations Controls" `.table-shell` (Operations Control/Description/Linked Detection Controls/Purpose) + "View Operations Controls" button — existing table pattern, new content domain.
- "Resource Utilization (Top 6)" `.table-shell` (Resource/Type/Used In Controls/Utilization with an inline progress bar + %) + "View All Resources" button — existing table pattern + a new inline progress-bar-in-cell element (no such component exists elsewhere).

**Footer**: standard status bar — existing pattern (visible but cut off in the source image; assumed identical to other pages).

**Sidebar**: rendered as garbled/illegible pseudo-text in the source image (an apparent rendering artifact, confirmed at native resolution) — group headers approximately read "FMEA WORKSPACE" (misspelled in the render), an "ANALYSIS"-like heading, and a legible "FMEA ELEMENTS"; individual item labels under those headers are unreadable distorted glyphs. This is flagged as a defect in how this specific mockup image was produced, not a deliberate naming choice — do not treat any inferred label under this heading as confirmed.

### 3. GUI Coding Requirements

**Route + template**: `fmea:detection_controls_list` → `django_app/fmea_app/templates/fmea_app/detection_controls_list.html`. (Same category of new build as mockup-19's Preventive Controls page and the already-built Engineering Context page — Detection Controls today render only as a worksheet section inside `fmea_detail.html`.)

**Layout structure**: identical structural approach to mockup-19 — `.content-shell` root, KPI `.grid` row, `.process-steps`-adapted tabs, `.panel.compact` GET filter form, three-column body (`.span-2/3` category list, `.span-6/7` table, `.span-3/4` **persistent detail rail** with `position: sticky`), then a 4-across analytics `.grid` row using the standard Chart.js wiring pattern, then a 2-across full-width `.grid` row for the Operations-links and Resource-Utilization tables.
- Grid/list view toggle: same recommended `?view=grid|list` GET-param approach as mockup-19, for consistency between the two sibling pages.
- "Detection Improvement (D Rating)" stacked bar: standard Chart.js stacked `bar` config (4 datasets stacked per X-axis category) — no new charting technology beyond what mockup-19's donut/scatter already required for this feature area.
- **New pattern needed — inline progress bar in a table cell** (Resource Utilization widget): no existing component renders a percentage bar inside a `.table-shell` cell. Build as a small `<div class="progress-track"><div class="progress-fill" style="width: X%"></div></div>` pair, pure CSS, computed server-side per row — no JS required.
- "Clone" button: a new `<form>`/POST action against the detail rail's record, distinct from Edit — server-side view that duplicates the two real fields (`name`, `description`) and re-prompts for `failure_cause`; needs its own view/URL (e.g., `fmea:detection_control_clone`).

**Per-widget data binding**:
- Total Controls KPI — binds to real aggregate: `DetectionControl.objects.count()`.
- Control Name / Description — binds to real `DetectionControl.name`/`.description`.
- Effective Controls, Detection Improvement, High Impact Controls KPIs — no real data source yet — `DetectionControl` has no effectiveness field and no mechanism linking it to a before/after `RiskEvaluation.detection` value.
- Linked FM / Causes KPI — binds to a computed aggregate over real relationships: `DetectionControl.failure_cause` is a real FK (direct, Causes), with Failure Modes reachable via `failure_cause.failure_mode`.
- Detection Control Categories panel — no real data source yet — no `category` field exists on `DetectionControl`.
- Type column, Detection Method column — no real data source yet — two further classification axes with no backing fields.
- Linked To (Failure Modes, Causes, Functions) — binds to a computed aggregate via the same real `failure_cause` FK chain as above.
- Effectiveness column/badge — no real data source yet, same gap as the Effective Controls KPI.
- Resource Used column/section — no real data source yet — same standing Resource/Equipment model gap as mockup-19.
- Operations Link column/section, "Links to Operations Controls" table — no real data source yet — Operations module absent.
- Attached Documents — no real data source yet — no file/attachment capability exists anywhere in the app.
- Owner, Status, Created/Last Updated, Review Due — no real data source yet — no such fields exist on `DetectionControl`.
- Controls by Type donut, Controls Effectiveness Distribution donut — no real data source yet, blocked on Type/Effectiveness fields.
- Detection Improvement (D Rating) stacked bar, Top Controls by D Improvement table, D Improvement Trend tab — no real data source yet — needs per-control before/after Detection-rating tracking (D lives only on `RiskEvaluation`, scoped to a failure mode's evaluation history, not to an individual control).
- Resource Utilization (Top 6) table — no real data source yet — blocked on the Resource/Equipment model gap, plus an undefined "Utilization %" metric with no basis in any confirmed model.
- Overview / Control Categories / Cause Relationships / History tabs — no real data source yet on all four (Overview restates the blocked KPIs/charts above; Cause Relationships has no backing relationship model beyond the single `failure_cause` FK; Control Categories needs a new field/model; History needs a new audit-log model).
- Linked Failure Modes tab — binds to a computed aggregate over the real `failure_cause` FK chain.
- "+ New Detection Control" / "Edit Control" forms — bind to real fields (`name`/`description`) today; every other field is placeholder until it exists.
- "Clone" button — feasible against real data without new fields: duplicates the two real fields (`name`/`description`) and the real `failure_cause` FK; exact copy-vs-reset behavior for any future fields would need scoping once those fields exist.

**Filtering/interaction**: Category/Type/Method/Implemented/Linked-To dropdowns, the search box, and the category-list clicks all submit via a server-side GET form reload — no client-side/AJAX filtering. Same recommendation as mockup-19 for the grid/list toggle.

**Sidebar entry**: cannot be confirmed for this specific mockup — the source image's sidebar text is illegible/garbled (see Section 2). Based on the legible "FMEA ELEMENTS" header and this page's content, it plausibly belongs there, matching mockups 16/18/19's placement of Detection Controls — but this is inference from context, not a reading of the image, and should be verified against a clean version of this mockup before treating it as settled. Recommend flagging the garbled image to the mockup author for re-export.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 21 — Process Control Characteristics: GUI Coding Requirements

### 1. Features & Content (what this screen does, in plain capability terms)

1. Lists process control characteristics (control records) in a searchable, filterable, paginated table — one row per control point in the process (what is controlled, how, by which resource, at what trigger).
2. Surfaces six top-of-page KPI counts summarizing the control population (total, active, not-effective, needs-review, no-reaction-plan, and a sixth likely-"linked to PFMEA" count).
3. Shows a persistent detail/inspector panel for one selected control characteristic, organized into five sub-tabs (General / Method & Resource / Reaction Plan / Links / History).
4. Visualizes a single control's flow through a 5-step "Process Control Flow" diagram (Process Step → Control Characteristic → Resource/Method → Result → Reaction).
5. Breaks down the control population by Control Type and by Effectiveness in two donut charts.
6. Shows which PFMEAs have the most controls linked to them, with drill-through to a full linked-PFMEA list.
7. Provides row-level create/edit/import/export/reporting entry points (buttons only — no field-level behavior shown beyond that).

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Logo lockup ("Open FMEA" + "Community Edition" subtitle) — repeats app-wide pattern.
- Hamburger/menu icon — repeats app-wide pattern.
- Page title "Process Control Characteristics" + circular "?" help icon — repeats pattern (title + help icon used on other pages, e.g. Mockup 22).
- Subtitle line under the title — repeats pattern.
- "Project: Headlamp X1 - PFMEA" dropdown, top right — repeats pattern seen on Mockups 22/23 (see standing note below on this selector).
- Search box "Search (Ctrl+K)" — repeats pattern.
- Bell/notification icon with red badge "7" — repeats pattern.
- Circular "?" help icon (header-level, distinct from the title's help icon) — repeats pattern.
- Avatar "JD" with green online dot — repeats pattern.
- Primary button "+ New Control Characteristic" (blue) — new instance of the existing "+ New X" primary-button pattern used elsewhere in the app.
- Secondary buttons with chevrons: "Import ⌄", "Export ⌄", "Reports ⌄", "Filters ⌄" — repeats existing toolbar-button pattern.
- Footer status bar: Database / User / Role / Workspace / Version / System-Status-dot — repeats app-wide footer pattern.

**Sidebar**
- Dark, collapsible sidebar with "← Collapse" control — repeats pattern.
- Nav groups as literally listed in the spec (FMEA WORKSPACE, CONTEXT, FMEA ANALYSIS, FMEA ELEMENTS, RISK & INSIGHTS, VALIDATION & CHANGE) with "Process Control Characteristics" active/highlighted under CONTEXT — repeats existing `.sidebar-nav` / `.nav-group` / `.nav-group-title` / `.nav-link` pattern; this page's own nav entry does not exist in the sidebar yet (new link to add).

**KPI row**
- 6 stat tiles: Total Controls (132), Active (118, 89.4%), Not Effective (6, 4.5%), Needs Review (8, 6.1%), No Reaction Plan (5, 3.8%), and an unlabeled 6th tile (126, 95.5%) — repeats the `.stat-tile` pattern used elsewhere, but with icon chips (shield/check-circle/warning-triangle/clock/no-entry/chain-link) not present in the plain `.stat-tile` examples in this codebase today — new visual variant (icon + label + value + sub-caption) needed.

**Filter/toolbar row**
- Search input "Search control characteristics…" — new instance of existing search-input pattern.
- Dropdowns: "Process / Operation: All", "Control Type: All", "Status: All", "Linked to PFMEA: All" — repeats the server-side `<select>` filter pattern.
- "⋯ More Filters" button — repeats existing toolbar-button pattern (behavior beyond a button is unspecified in the mockup).

**Main table**
- Columns: checkbox, ID, Process / Operation, Control Characteristic, Control Type, Method, Resource / Equipment, Frequency / Trigger, PFMEA Links, Status, Effectiveness — repeats `.table-shell` + `<table>` pattern.
- Control Type colored pill badges (Administrative/Measurement/Detection/Monitoring/Poka-Yoke/Test) — new badge variants; repeats the existing `.status`/`.status-*` badge mechanism but needs new modifier classes (no `.status-*` class today maps to these six values).
- Status pills (Active green, Review orange/red) — "Active" can likely reuse an existing green status class; "Review" has no existing `.status-*` equivalent among the confirmed classes — new modifier needed.
- Effectiveness shown as colored dot + text (Effective/Partially Effective) — new small-dot-plus-label pattern, not an existing component.
- ID values as blue hyperlinks — repeats existing link-styled-ID pattern (e.g., FM-IDs in Mockup 23).
- Pagination footer: "Showing 1 to 10 of 132…", page-number buttons, prev/next chevrons, "10 / page" dropdown — repeats existing pagination pattern.

**Diagrams / Charts row**
- "Process Control Flow" diagram: 5 connected boxes (Process Step / Control Characteristic / Resource-Method / Result / Reaction), each with an icon, heading, and body text, joined by arrows — **no existing equivalent**; new diagram component.
- "Control Type Distribution" donut chart, center total + 6-item legend — new chart instance; donut is within the just-decided Chart.js policy (line/bar/donut), so no library gap, but no donut is wired into any page today.
- "Effectiveness Overview" donut chart, center total + 4-item legend — same as above.
- "Top PFMEA Links (by count)" table: PFMEA / Linked Controls / Top Cause-FM columns, 5 rows, "View All PFMEA Links" button — repeats `.table-shell` pattern plus a button, new content only.

**Detail/Inspector panel (right-docked)**
- Header "Control Characteristic Details" + close "X" — **no existing right-docked detail-panel component in this codebase**; new layout region.
- ID + status pill (top-right of panel) — repeats badge pattern.
- Control-type badge (gold "Poka-Yoke" pill) — same new badge variant as above.
- Bold title + description text — new but simple.
- Sub-tabs: General / Method & Resource / Reaction Plan / Links / History, with "General" active (blue underline) — **no existing tab-panel-swap component**; closest existing analog is `.process-step` / `.process-steps` (a link-based stepper), which is not the same interaction (it navigates, it doesn't swap panel content in place).
- Label/value list under General (Process/Operation, Operation Step, What is Controlled, Control Type, Control Method, Trigger, Status, Effectiveness, Owner+avatar, Created by/date, Last Updated by/date, Review Due) — repeats `.attribute-table` / label-value list pattern used elsewhere.
- Buttons: "✎ Edit", "↻ View Full History" — repeats `.button` pattern.

### 3. GUI Coding Requirements

- **Route + template**: `fmea:process_control_characteristics` → `django_app/fmea_app/templates/fmea_app/process_control_characteristics.html`, following the app's `fmea:<snake_case>` / `templates/fmea_app/<snake_case_name>.html` convention (matching e.g. `fmea:risk_matrix` → `risk_matrix.html`).

- **Layout structure**:
  - Page shell: standard header + sidebar + main content column, matching every other page in the app (`.sidebar`, `.content-shell`).
  - Main column: title/subtitle/action-button row → KPI row (`.grid` of `.stat-tile.span-*`, extended with an icon-chip variant — new CSS needed for the colored icon square to the left of the label/value, since no confirmed `.stat-tile` example includes an icon) → filter toolbar (`.panel.compact` `<form method="get">` per the app's confirmed filter-form pattern) → `.table-shell` table with pagination → a `.grid` row of panels: Process Control Flow diagram panel (new), Control Type Distribution donut panel (new chart, `.panel`), Effectiveness Overview donut panel (new chart, `.panel`), Top PFMEA Links table panel (`.table-shell` inside a `.panel`).
  - **New pattern #1 — right-docked detail/inspector panel**: no existing layout primitive for a persistent right-hand panel that runs the page's full height beside a main content column. Needs new CSS (a 3-column flex/grid shell: sidebar, main, detail-panel, similar in spirit to `.split` but page-level rather than within-panel) and new JS in the spirit of `app.js` (a single click-delegate handler on table rows/ID links that shows the panel and swaps its content — since there's no AJAX in this app, the simplest version re-renders the whole page with the selected ID as a GET query param and the panel's content computed server-side, consistent with the app's server-rendered/full-reload discipline).
  - **New pattern #2 — sub-tabs within the detail panel**: no existing tab-panel-swap widget. Two options consistent with this app's plain-vanilla-JS spirit: (a) pure CSS/JS show-one-hide-rest tabs scoped to the panel (a small `app.js`-style addition: click a tab link, toggle `[hidden]` on the matching content block, no page reload — this is the only place in this app where such a widget would be needed, so it should be scoped narrowly, not generalized prematurely), or (b) treat each tab as its own GET parameter and re-render server-side (fully consistent with the app's existing "no client-side interactivity beyond theme/sidebar/nav-highlight" rule, at the cost of a full reload per tab click). Recommend (b) to avoid introducing a new client-side pattern the rest of the app doesn't have.
  - **New pattern #3 — Process Control Flow diagram**: a static row of 5 boxes connected by arrows; buildable as plain HTML/CSS (flex row of bordered `.panel`-like boxes with an arrow glyph or CSS pseudo-element between them, each box's icon from the same icon set already used for the KPI tiles) — no charting library needed, this is not a data visualization, just laid-out content.
  - Donut charts: use the vendored Chart.js (`type: 'doughnut'`), one `<canvas>` per chart, matching the just-decided line/bar/donut policy — first real usage of Chart.js in the app, so this page would also be the place that establishes the canvas-init JS pattern (a small init function per chart, called on page load, no framework).

- **Per-widget data binding**:
  - Table columns ID, Process/Operation, Control Characteristic (name) — binds to real `ProcessCharacteristic.operation`, `ProcessCharacteristic.name` (already available).
  - "PFMEA Links" count column and "Top PFMEA Links (by count)" table — binds to a computed aggregate over real data (proposed: a query joining `ProcessCharacteristic` through its related `FailureCause`/`FailureMode`/`RiskEvaluation` chain — no such aggregation exists today, would need to be written).
  - Control Type, Method, Resource/Equipment, Frequency/Trigger, Status, Effectiveness, Owner, Review Due, Created-by/Last-Updated-by audit fields, the Reaction Plan sub-tab, and the Process Control Flow diagram's Result/Reaction nodes — no real data source yet; render as static/placeholder content until these fields exist on `ProcessCharacteristic` (today it has only `operation`, `name`, `description`, `cause_category_id`, and a generic `attributes` JSONField with no structured columns for any of this).
  - All 6 KPI tiles, the Control Type Distribution donut, and the Effectiveness Overview donut — no real data source yet; every one depends on the `status`/`control_type`/`effectiveness` fields above not existing yet.
  - "History" sub-tab and "View Full History" — no real data source yet; no audit/change-log entity is documented for `ProcessCharacteristic`.

- **Filtering/interaction**: all four filter dropdowns and the search box submit via a server-side `GET` form with a full page reload, matching the app's existing filter pattern (`<form class="panel compact" method="get">` + `<select name="...">` + `{% if x == y %}selected{% endif %}`) — no AJAX/client-side filtering exists anywhere in this app and none should be introduced here.

- **Sidebar entry**: belongs under **CONTEXT**, as shown in the mockup ("Process Control Characteristics" alongside System/Product/Process, System Characteristics Base, Characteristics Flow/Diagram) — this entry does not exist in the sidebar today and would need to be added.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 22 — Actions: GUI Coding Requirements

### 1. Features & Content (what this screen does, in plain capability terms)

1. Lists open/in-progress recommended actions in a searchable, filterable, paginated table, with each row's linked failure mode/cause, responsible party, dates, status, and progress.
2. Surfaces six top-of-page KPI counts summarizing the action population (total, open, overdue, completed, total RPN reduction, average RPN reduction %).
3. Offers a 6-tab view switcher (Overview / List / Calendar / Categories / Risk Reduction / History) — this mockup is the "Overview" tab's content.
4. Breaks down the action population by Status, Priority, and Type in three donut charts.
5. Tracks aggregate risk-reduction impact (Initial vs. Current RPN) over program phases in a line chart, plus a leaderboard table of the actions with the largest individual RPN reductions.
6. Shows a Gantt-style timeline of open/in-progress actions across calendar months.
7. Shows a persistent detail/inspector panel for one selected action, including a photo thumbnail, full field list, a dedicated risk-reduction sub-block, and file attachments.
8. Provides row-level create/edit/import/export/reporting entry points (buttons only — no field-level behavior shown beyond that).

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Logo lockup, hamburger icon — repeats app-wide pattern.
- Page title "Actions" + circular "?" help icon, subtitle line — repeats pattern.
- "Project: Headlamp X1 - PFMEA" dropdown, search icon, bell (badge "0"), help icon, avatar "JD" — repeats pattern.
- Primary "+ New Action" button; secondary "Import ⌄" / "Export ⌄" / "Reports ⌄" / "Filters ⌄" — repeats pattern.
- Footer status bar (Database/User/Role/Workspace/Version/Status) — repeats app-wide pattern.

**Sidebar**
- Light-theme sidebar (this page renders light, unlike Mockups 21/23) with groups FMEA WORKSPACE, ANALYSIS, FMEA ELEMENTS (Actions active/highlighted here), RISK & INSIGHTS, VALIDATION — repeats `.sidebar-nav` pattern; "Actions" entry does not exist in the sidebar today.

**KPI row**
- 6 stat tiles: Total Actions (68), Open Actions (21, 30.9%), Overdue Actions (7, 10.3%), Completed Actions (47, 69.1%), Risk Reduction RPN (1,258), Avg. RPN Reduction (53%) — same new icon-chip stat-tile variant flagged in Mockup 21.

**Tab bar**
- "Actions Overview" (active), "Actions List", "Action Calendar", "Action Categories", "Risk Reduction", "History" — **no existing tab-panel-swap or multi-page-tab-strip component**; closest analog is `.process-step`/`.process-steps` (a link-based stepper), which navigates rather than swapping in place — treat these as separate routes/pages (List, Calendar, Categories, Risk Reduction, History each a distinct URL), styled to look like tabs, consistent with the "full page reload" discipline this app already follows.

**Filter/toolbar row**
- Search "Search actions…"; dropdowns Status/Type/Linked To/Priority/Responsible: All; "⋯ More Filters" — repeats server-side filter-form pattern.

**Section 1 — Actions by Status donut**
- Center total "68", 5-item legend (Open/In Progress/Completed/Cancelled/On Hold with counts+%), "View Details" link — new Chart.js donut instance (see enum-mismatch flag in Section 3 below).

**Section 2 — Actions by Priority donut**
- Center total "68", 4-item legend (High/Medium/Low/None), "View Details" link — new donut instance.

**Section 3 — Risk Reduction Summary (RPN)**
- 4 stat sub-values (Total Initial RPN, Total Current RPN, Total RPN Reduction, Reduction %) — new small stat-row, simple.
- Line chart: two series (Initial RPN red, Current RPN green) across 7 program-phase X-axis buckets (Concept/Design/DV/PV/PPAP/SOP/Serial Prod.) with data-point labels — new Chart.js line-chart instance.
- "View Trend" link — repeats link pattern.

**Section 4 — Open & In Progress Actions table**
- Columns: checkbox, ID, Action Title, Linked To, Type, Priority, Responsible, Planned Start, Due Date, Status, % Complete, RPN Reduction (Exp.), Days Overdue, Actions (⋯) — repeats `.table-shell` pattern.
- Type badges (Design/Process/Detection/Supplier/Human Action, distinct colors) — new badge modifier set, no existing `.status-*` maps to these values.
- Priority as colored text (High red / Medium amber / Low green), not a pill — simplest possible new styling, a text-color utility rather than a badge component.
- Status pills ("In Progress" orange, "Open" blue/gray) — "Open" may reuse existing status styling; "In Progress" likely maps to an existing `.status-progress` class already confirmed in this app's CSS.
- % Complete as a horizontal progress bar + % label — **no existing progress-bar component confirmed in this codebase**; new small CSS component (a `<div>` with a width-percentage inner bar).
- Responsible shown as circular avatar-initials + name — repeats the avatar-initials pattern already used for Owner in Mockup 21 and for JD/MK/etc. throughout.
- Pagination footer — repeats existing pattern.

**Section 5 — Action Timeline (Gantt)**
- Y-axis: 6 action rows (truncated titles); X-axis: 5 month columns (Mar–Jul 2025); one horizontal bar per row spanning its planned-start→due-date window, with start/end date labels and a %-complete label on at least one bar; 5-color legend (Open/In Progress/Completed/Overdue/On Hold dots) — **no existing Gantt/timeline component anywhere in this app**, and a Gantt chart is explicitly outside the just-decided Chart.js scope (line/bar/donut only); flagged as new.

**Section 6 — Actions by Type donut**
- Center total "68", 6-item legend (Design/Process/Detection/Supplier/Human/Other), "View Details" link — new donut instance.

**Section 7 — Top Risk Reductions (By Action) table**
- Columns: Action ID, Action Title, Initial RPN, Current RPN, Reduction, % Red.; 5 rows; "View All" button — repeats `.table-shell` + button pattern.

**Detail/Inspector panel (right-docked)**
- Header "Action Details" + close "X" — same new right-docked-panel pattern flagged in Mockup 21.
- ID, status pill ("In Progress"), priority pill ("High"), red overdue text line — repeats badge patterns, new "days overdue" text treatment.
- Two small pill labels ("Design Action" type, "Permanent" classification) — new badge usage.
- Small product-photo thumbnail — **no existing image-thumbnail-in-detail-panel pattern**; new, and depends on file/image storage (see Section 3).
- Bold title + description — repeats simple text pattern.
- Label/value list: Linked To, Linked Cause, Function, Category, Type, Responsible, Support Team, Owner, Created, Planned Start, Due Date, Actual Finish, Effectiveness, Status, % Complete — repeats `.attribute-table`/label-value pattern; note the mockup itself renders "Actual Finish" as a progress bar and "Status" with a duplicated label ("Status | In Progress") — both are almost certainly mockup rendering artifacts, not intended widget designs; a real build should render Actual Finish as a date and Status as a single badge.
- "Risk Reduction (RPN)" sub-block: Initial/Current/Reduction/Reduction % — repeats the same small stat-row pattern as Section 3.
- "Attachments" sub-section: 3 file rows with external-link icons — **no existing file-attachment-list component or upload/storage capability anywhere in this app**; wholly new.
- Buttons: "✎ Edit", "⊗ Close Action", "⋯ More" — repeats `.button`/`.icon-button` pattern.

### 3. GUI Coding Requirements

- **Route + template**: `fmea:actions` (Overview) → `django_app/fmea_app/templates/fmea_app/actions.html`, with the tab bar's other five tabs as sibling routes/templates following the same convention: `fmea:actions_list` → `actions_list.html`, `fmea:actions_calendar` → `actions_calendar.html`, `fmea:actions_categories` → `actions_categories.html`, `fmea:actions_risk_reduction` → `actions_risk_reduction.html`, `fmea:actions_history` → `actions_history.html`.

- **Layout structure**:
  - Standard header + sidebar + main content shell, matching every other page.
  - Main column: title/subtitle/buttons row → KPI row (icon-chip `.stat-tile` variant, per Mockup 21) → tab-strip row (styled links to the sibling routes above, active-state class on the current one — same underlying mechanism as the sidebar's active-link highlighting in `app.js`, reused rather than reinvented) → filter form (`.panel.compact` GET form) → a `.grid` row of 3 panels (Status donut, Priority donut, Risk Reduction Summary block+line chart) → `.table-shell` Open & In Progress table with pagination → a `.grid` row of 3 panels (Gantt timeline, Type donut, Top Risk Reductions table).
  - Same right-docked detail/inspector panel pattern as Mockup 21 — new CSS/JS, described there, reused here rather than re-invented per page.
  - Donut and line charts: vendored Chart.js, `type: 'doughnut'` and `type: 'line'`, one `<canvas>` per chart — within the already-decided policy.
  - **New pattern — progress bar**: small reusable CSS component (a bounded `<div>` with an inner width-percentage fill), used for both the table's "% Complete" column and the detail panel's "% Complete"/mis-rendered "Actual Finish" fields.
  - **New pattern — Gantt/timeline chart**: explicitly not covered by the Chart.js line/bar/donut decision. Two implementation paths worth naming for a future scoping discussion: (a) a hand-built CSS grid (month columns × action rows, each bar an absolutely-positioned `<div>` spanning from planned-start to due-date, computed server-side from date fields), staying within the "no new charting library" spirit of every prior slice in this app, or (b) pulling in a dedicated Gantt library — which would be a new tooling decision beyond the recent Chart.js one and should be flagged as such rather than assumed.
  - **New pattern — file attachment list**: a simple `<ul>` of file rows with name + external-link icon; depends entirely on attachment storage existing first (see data binding below) — the display list itself is trivial once files exist somewhere to point at.

- **Per-widget data binding**:
  - Table columns Action Title, Linked To, Responsible, Due Date, Status — binds to real `RecommendedAction.name`, `.failure_mode`/`.failure_cause`, `.responsible_role`, `.due_date`, `.status` (already available).
  - Detail panel "Linked Cause: C-011" — binds to real `RecommendedAction.failure_cause`, distinct from `.failure_mode` (already available), though the mockup shows both a "Linked To" (failure mode) and "Linked Cause" on the same row simultaneously — needs clarifying whether that means two separate FK reads or a cause→its-failure-mode pass-through, since the model links to at most one of `failure_mode`/`failure_cause` per row.
  - "Days Overdue" column — binds to a computed aggregate over real data (`today − due_date` for non-terminal-status actions; no such computed field exists yet, straightforward to add).
  - Status badges/donut (Open/In Progress/Completed/Cancelled/On Hold) — **flag: real enum mismatch, not just a gap.** The real `ActionStatus` enum is open/in_progress/completed/verified/cancelled; this mockup shows "On Hold" in place of "Verified." This needs a reconciliation decision (rename, add a 6th state, or treat as a mockup error) before building, separate from ordinary "add a field" work.
  - Priority, Type/Category, Support Team, Owner, Planned Start, Actual Finish, % Complete, Effectiveness, "Permanent" classification, Function label, Created-by/at audit fields — no real data source yet; render as static/placeholder content until these fields exist on `RecommendedAction` (today it has only name, description, failure_mode-or-failure_cause link, responsible_role, status, due_date).
  - "Responsible: Marko K." with personal avatar — binds to real `RecommendedAction.responsible_role`, but note `ResponsibleRole` is documented as a name/description catalog, not a per-person roster; using it to show named individuals with avatars either stretches its intended meaning or implies a separate person/user roster that doesn't exist — worth a scoping question rather than assuming.
  - Risk Reduction (RPN) figures — summary block, per-action table, and detail-panel sub-block — binds to a computed aggregate over real data: `RecommendedAction` and `RiskEvaluation` are indirectly linkable via `FailureMode`/`FailureCause`, so before/after RPN is computable from existing `RiskEvaluation` rows, but no such correlation query exists today. The RPN-trend-by-program-phase line chart additionally needs a new "program phase" tag field on `RiskEvaluation`/`FailureMode` that doesn't exist yet — placeholder until that exists.
  - Action Timeline Gantt chart — no real data source yet on two counts: it needs `planned_start`/`actual_finish`/`percent_complete` fields that don't exist, and the widget type itself needs a separate charting-approach decision (see above).
  - Attachments (file rows) — no real data source yet; no file/attachment storage model exists anywhere in the app today.
  - "Action Categories" tab and "History" tab — no real data source yet; no `ActionType`/category catalog and no audit/change-log model exist for `RecommendedAction`.

- **Filtering/interaction**: all filter dropdowns and search submit via a server-side `GET` form with full page reload, matching this app's existing pattern — no AJAX/client-side filtering.

- **Sidebar entry**: this mockup shows "Actions" under FMEA ELEMENTS. That group doesn't exist in the app's current canonical sidebar; it's a candidate for a future FMEA ELEMENTS group, or a standalone Actions entry could be added under an existing group as an interim step — either way, the nav entry does not exist today and would need to be added.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.
## Mockup 23 — Risk Matrix: GUI Coding Requirements

### 1. Features & Content (what this screen does, in plain capability terms)

1. **Already built and live**: renders a 10×10 Severity×Occurrence heat-map grid, system-wide across all FMEAs, with method-filterable cell placement and coloring, plus numbered markers for plotted risks and a drill-down per cell.
2. **Already built and live**: lists the plotted risks in a full table (ID, Failure Mode, Effect, S, O, D, RPN, Risk Level, Current Controls, Linked FMEA, Location) with pagination.
3. **Already built and live**: shows aggregate Risk Level counts (Extreme/High/Medium/Low) and a Total Risks count alongside the grid.
4. **Not yet built**: a 6-tab view switcher (Matrix View / Risk Trajectory & Propagation / Risk Heat Map / PM-FMEA Impact / Risk Summary / History) — this mockup is the "Matrix View" tab; only the matrix itself exists today, the other five lenses do not.
5. **Not yet built**: a persistent "Selected Risk" inspector panel showing full detail for one plotted risk — stat boxes, its current controls, a Cause→Failure Mode→Effect "Risk Path" diagram, linked FMEA/system/process context, a drill-through to its linked actions, and a "Last 3 Changes" history log.
6. **Design conflict, not a gap**: the mockup's header shows a per-FMEA "Project" scope selector, which conflicts with the Risk Matrix's already-decided and already-built system-wide (non-project-scoped) design.

### 2. Full Wireframe Widget Checklist

**Header/Chrome**
- Logo lockup — repeats app-wide pattern.
- Page title "Risk Matrix" (no help icon here, unlike Mockups 21/22), subtitle line — repeats pattern, already built.
- "Project: Headlamp X1 - PFMEA" dropdown — present in the mockup; **conflicts with the already-built system-wide design** (see Section 3).
- Search icon (icon-only, no text box, unlike 21/22), bell icon (no badge), help icon, avatar "JD" — repeats pattern.
- Buttons: "▽ Filters", "⊞ View Options", "⤓ Export ⌄" — "Filters" partially exists today (the live view supports a `method` selector); "View Options" and "Export" are not confirmed built.
- **No footer status bar on this page** — matches the live page (confirmed absent), unlike Mockups 21/22.

**Sidebar**
- "Risk Matrix" already exists and is highlighted/active under **RISK**, per the already-completed slice's sidebar addition — already built.
- Note: this mockup's sidebar also shows some group/order differences from Mockups 21/22 (e.g., "Consolidated Home" at top, an "Engineering Context panel" item, a "RISK" group vs. "RISK & INSIGHTS" elsewhere) — these are cosmetic inconsistencies across mockups, not something this page's build needs to reconcile beyond noting them.

**Tab bar**
- "Matrix View" (active), "Risk Trajectory & Propagation", "Risk Heat Map", "PM-FMEA Impact", "Risk Summary", "History" — only "Matrix View" exists as a real page today; the other five are not built. Same "no tab-panel-swap component exists" note as Mockup 22 applies if these are ever built — they'd be separate routes styled as tabs, not an in-page tab widget.

**Risk Matrix grid (main widget)**
- 10×10 grid, X-axis "Occurrence (O)" 1–10 with band labels, Y-axis "Severity (S)" 10–1 with band labels, heat-colored cells (green→yellow→orange→red), numbered black circular badges marking plotted risks, footnote "RPN = S × O × D" — **already built and live**, matches the real `risk_matrix` view's confirmed 10×10, method-filterable, severity×occurrence-banded grid.

**Risk Level (RPN) legend card**
- 4 rows: Extreme (RPN≥240, count 5), High (120≤RPN<240, count 3), Medium (40≤RPN<120, count 1), Low (RPN<40, count 1) — **already built**: aggregate counts over the same `RiskEvaluation` data powering the grid.

**Total Risks card**
- Large number "10" + "View as List" link — **already built** (the count is real; "View as List" likely just scrolls to or highlights the already-present table below, since the table is already on the same page).

**Risks in Matrix table**
- Columns: ID, Failure Mode, Effect, S, O, D, RPN, Risk Level, Current Controls, Linked FMEA, Location; pagination footer — **already built** for ID/Failure Mode/Effect/S/O/D/RPN/Risk Level (direct reads of `RiskEvaluation`+`FailureMode`). "Current Controls" (PC-xx/DC-xx) and "Linked FMEA"/"Location" columns are not confirmed wired into this exact table today — see Section 3.

**Selected Risk panel (right-docked)**
- Header "Selected Risk" + close "X" — same new right-docked-panel pattern flagged in Mockups 21/22; not built today (the live drill-down is confirmed to exist per the architecture review, but whether it takes this exact persistent-panel shape vs. a separate cell/drill-down page is not confirmed from the docs read here — treat the panel chrome itself as not-yet-built even though its underlying data is real).
- FM-002 heading + Extreme badge, title, "Effect: …" subtitle — real data, panel chrome new.
- 4 stat boxes (S/O/D/RPN, RPN highlighted) — real data (`RiskEvaluation.severity/occurrence/detection` + computed RPN from `.result`), panel chrome new.
- "Current Controls" sub-section (PC-02/DC-03 rows with Preventive/Detection badges) — real underlying control entities exist (touched on in Mockup 21), but this specific "controls for this risk" join/display is not confirmed built.
- "Risk Path" diagram (Cause → Failure Mode → Effect, middle node highlighted) — **no existing diagram component**; same new-diagram-pattern note as Mockup 21's Process Control Flow diagram.
- "Linked" sub-section (FMEA Type, Process/Operation, System/Product/Process, Design Responsibility) — traceable via existing FKs but not confirmed built as an aggregated display.
- "Actions" sub-section: "View Actions (2)" button — count/drill-through not confirmed built, though computable from existing `RecommendedAction` links.
- "History (Last 3 Changes)" sub-section: 3 dated rows with actor initials, "View Full History" button — not confirmed built; reconstructable from existing timestamped/attributed `RiskEvaluation` rows (each new evaluation is a new row, never overwritten) but no diff/change-log display exists today.

### 3. GUI Coding Requirements

- **Route + template (real, already existing — do not propose new ones)**: `GET /risk-matrix/` → view `risk_matrix` → template `django_app/fmea_app/templates/fmea_app/risk_matrix.html`; drill-down `GET /risk-matrix/cell/?method=...&severity=N&occurrence=N` → view `risk_matrix_cell` → `risk_matrix_cell.html`; `GET /risk-matrix/top/?method=...` → view `risk_matrix_top` → `risk_matrix_top.html`. Query logic lives in `fmea_app/risk_matrix.py` (or `services.py`), banding in `fmea_evaluation/calculators.py::classify_severity_occurrence`. Cite `Codex_Instruction_RiskMatrix_Slice.md` (implemented) and `OpenFMEA_RiskMatrix_ArchitectureReview.md` (design authority) as the grounding for all of this — this is not proposed, it is built.

- **Layout structure**:
  - The grid, legend, Total Risks card, and Risks-in-Matrix table are already laid out per the live template — this document does not re-specify their structure, only the additions this mockup shows beyond them.
  - **New — Selected Risk right-docked panel**: same pattern as flagged in Mockups 21/22 (no existing right-docked persistent detail-panel primitive in this app); would need the same new CSS shell (sidebar/main/detail-panel 3-column layout) and the same server-side "selected ID as GET param, panel content computed and rendered server-side" approach, consistent with this app's full-reload discipline — no AJAX.
  - **New — Risk Path diagram**: 3 connected boxes (Cause → Failure Mode → Effect, middle box highlighted), same static HTML/CSS approach as Mockup 21's Process Control Flow diagram — no charting library needed.
  - **New — 5 additional tabs** (Risk Trajectory & Propagation, Risk Heat Map, PM-FMEA Impact, Risk Summary, History): each would be a separate route/template styled as a tab-strip entry, per the "no in-page tab-swap widget" note used elsewhere in this batch — not built today, only "Matrix View" exists.
  - **Chart-type note**: the matrix grid itself is a plain HTML-table-with-background-colors widget per the architecture review (explicitly not a Chart.js type, and deliberately not one) — this is already solved, not a gap.

- **Per-widget data binding**:
  - 10×10 grid, cell coloring, numbered risk markers, Risks-in-Matrix table's ID/Failure Mode/Effect/S/O/D/RPN/Risk Level columns, Risk Level legend counts, Total Risks count, and the Selected Risk panel's S/O/D/RPN stat boxes and Failure Mode/Effect title — **binds to real `RiskEvaluation.severity`/`.occurrence`/`.detection`/`.result` (RPN/classification) joined to `FailureMode`, already available via the existing `risk_matrix` view.**
  - "Current Controls" (table column + panel sub-section) — binds to a computed aggregate over real data: plausibly a join from `ProcessCharacteristic`/control records (see Mockup 21) to this `FailureMode`/`RiskEvaluation`, but this exact "controls for this risk" display is not confirmed wired in today — needs new query logic even though no new entity is required.
  - "Linked FMEA" and "Location" table columns, and the panel's "Linked" sub-section (FMEA Type, Process/Operation, System/Product/Process, Design Responsibility) — binds to a computed aggregate over real data, traceable through the failure mode's existing operation/system linkage, not confirmed built as this aggregated view.
  - "Risk Path" diagram — binds to a computed aggregate over real data: `RiskEvaluation.failure_mode` plus the failure mode's existing `FailureCause`/effect relationships, join exists in principle, this specific 3-node display is not confirmed built.
  - "View Actions (N)" count — binds to a computed aggregate over real data: `RecommendedAction.failure_mode`/`.failure_cause` already link actions to a failure mode, so counting/filtering is a straightforward query against existing data, just not confirmed built as this drill-through.
  - "History (Last 3 Changes)" — binds to a computed aggregate over real data: `RiskEvaluation` rows are timestamped (`evaluated_at`) and attributed (`actor`) and are never overwritten, so a change list is reconstructable by ordering and diffing consecutive rows for a failure mode — no dedicated diff/change-log computation exists today, this is new aggregation logic on top of real data, not a new model.
  - "Risk Trajectory & Propagation", "Risk Heat Map", "PM-FMEA Impact", "Risk Summary" tabs — binds to a computed aggregate over real data for trend/alternate-aggregation views of already-real `RiskEvaluation` rows; "propagation" specifically, if it means cross-failure-mode causal impact rather than simple FK traversal, has no real data source yet and would need new modeling.

- **Filtering/interaction**: the live page's method selector (`classic-rpn` / `aiag-vda-ap-poc`) is already a server-side `GET` query-param selector with full page reload, matching this app's standard filter pattern exactly — any new filters this mockup implies ("▽ Filters", "⊞ View Options") should follow the same pattern, not introduce AJAX.

- **Sidebar entry**: already exists — "Risk Matrix" is live under **RISK**, added as the one deliberate sidebar addition in the already-completed slice; no new nav entry is needed for the Matrix View tab itself, only (if built) for the 5 additional tab routes.

- **Design conflict to flag again, briefly**: the mockup's "Project: Headlamp X1 - PFMEA" header dropdown implies per-FMEA scoping of the matrix/table/panel, which conflicts with the already-implemented, deliberately system-wide (no per-project scoping) design confirmed in `Codex_Instruction_RiskMatrix_Slice.md` (system-wide scope was explicitly confirmed by the user on 2026-09-01, and no `Project` entity exists in the domain model). This needs reconciliation — either read the selector as unrelated global navigation chrome, not matrix scoping, or revisit the system-wide decision — rather than being treated as an unbuilt feature to add.

This specifies how the GUI could be structured and coded; it does not authorize building it, and any widget marked as needing new backend data stays subject to this project's standing architecture-review process before that data is wired in.

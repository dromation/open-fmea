# Open-FMEA — Per-Mockup GUI/Wireframe/Architecture Specifications (all 23 reference mockups)

Status: **Specification/documentation only, 2026-09-04. Not an implementation instruction or authorization to build anything.** Written per explicit user direction: "review each mockup and create for each mockup a list of GUI contents (widgets), wireframes and UI/UX, and create for each mockup an architecture with data logic what should it do and behave."

This document does NOT change DNA rule 8 ("no entity/feature is built ahead of its own architecture review's approval... the approved scope is the narrowest one stated, not the full ambition of the review"). Every one of the 23 sections below ends with an explicit non-authorization sentence for exactly this reason. Treat this as the detailed design-prep layer underneath `OpenFMEA_DNA_CoreReference.md` Section 10's per-mockup audit (Tier A/B/C/D findings) and the "GUI Roadmap Index" table — this document doesn't replace either, it goes one level deeper: every widget on every mockup, described exhaustively, with its exact data-model mapping and proposed behavior.

## Methodology

All 23 mockup images (`architecture/mockups/mockup-01-...png` through `mockup-23-risk-matrix.png` in both `open_fmea` and `open_fmea_training_set`) were read directly — not assumed from earlier prose summaries — with dense regions (small text, legends, detail panels) cropped and zoomed for literal accuracy. Every architecture/data-logic claim was checked against the real Django domain model (`models.py`, confirmed field-by-field earlier in this engagement), not invented. Where a mockup's text was illegible or its own internal numbers didn't reconcile (e.g. a legend total not matching a chart), that is flagged explicitly in the relevant section rather than silently corrected or guessed — consistent with this project's "never trust, always verify" discipline applied to design inputs as much as implementation reports.

Each section below follows the same four-part structure:
1. **GUI Contents / Widgets** — exhaustive, literal inventory of every visible UI element.
2. **Wireframe & UI/UX** — structural layout, visual hierarchy, color/status coding, implied interactions.
3. **Architecture & Data Logic** — every widget mapped to the real domain model (Tier A: real & built; Tier B: real data, needs new query/aggregation logic; Tier C: real field, far short of what's shown; Tier D: genuinely new, no backing at all), with proposed schemas/behavior marked explicitly as *proposed*, not fact, wherever something new is described.
4. **Non-authorization note.**

## Quick-reference index

| # | Mockup | Dominant tier | One-line status |
|---|---|---|---|
| 1 | Base App Shell (Home dashboard) | **Built** (shell) + Tier D (Reviews Due, activity log, Knowledge & References) | Real shell/KPIs; several home-page widgets are new |
| 2 | Engineering Context Panel | Tier A (Product/Process) + Tier D (System, FMEA Team) | Process Flow/Characteristics already built; System panel is new |
| 3 | Preventive FMEA (PM-FMEA) Tab | Tier D throughout | Held per the standing 2026-09-01 PM-FMEA decision |
| 4 | Consolidated Home | Tier D-heavy | Health score, risk trend, Operations/Maintenance status all new |
| 5 | FMEA Projects List | **Built** (Phase 2a) + grain ambiguity flagged | Real page; mockup's row grain vs. `FMEAProject` needs reconciling |
| 6 | FMEA Team | Tier A (roster) + Tier D (RBAC) | Real roster; permissions/role-enforcement system is new |
| 7 | System / Product / Process | Tier D-dominant | No `System` model exists — central gap, review just written |
| 8 | System Characteristics Base | Tier D-dominant | Needs System hierarchy + ClassificationScheme, neither approved |
| 9 | Characteristics Flow / Diagram | Tier D throughout | Largest net-new concentration: graph entity, graph library, AI auto-link |
| 10 | Evidence & Tests | Tier D-dominant | Confirms a new `ValidationTest`-shaped entity is needed, not today's `Evidence` |
| 11 | DFMEA | Tier A/B core + Tier D extras | Slice D (approved) covers the Tier A/B worksheet core |
| 12 | PFMEA | Tier A/B core + Tier D extras | Same as DFMEA; Control Plan Link tab specially gated |
| 13 | Change Impact | Tier D throughout | No `Change` entity anywhere; proposed schema included |
| 14 | Validation Trajectory | Tier D-dominant | Same underlying gap as Evidence & Tests (folded into one review) |
| 15 | Failure Modes | Mixed — Tier A/B core, Tier D extras | Catalog, complaints, AI similarity all new |
| 16 | Causes | Tier A sliver + Tier D-dominant | Flags a real model conflict: one cause linked to multiple failure modes |
| 17 | Risk Trajectory & Propagation | Tier A/B core + Tier D extras | Lifecycle-gate tracking and propagation chain are new |
| 18 | Effects | Mixed | Confirms 5-level effect-propagation hierarchy is new; Sankey needs its own charting decision |
| 19 | Preventive Controls | Tier A sliver + Tier D-dominant | Three parallel taxonomies, Resource/Equipment tracking all new |
| 20 | Detection Controls | Same pattern as #19 | Structurally parallel to Preventive Controls |
| 21 | Process Control Characteristics | Tier D, specially gated | This is the Control Plan concept — DNA rule 7 applies |
| 22 | Actions | Mixed, with a real enum mismatch flagged | "On Hold" status shown doesn't exist in `ActionStatus` |
| 23 | Risk Matrix | **Built** (base) + a real design conflict flagged | Per-FMEA "Project" selector contradicts the system-wide design decision |

---

## Mockup 01 — Base App Shell (source: mockup-01-base-app-shell.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Branding / header**
- Top-left logo lockup: multicolor "X"-shaped icon mark + wordmark "Open FMEA" + subtitle line "Open-EQMS Family".
- Top bar: hamburger/menu icon, page title "Home", a project-selector dropdown reading "Project: New Headlamp X1" (chevron), a search box with placeholder "Search (Ctrl+K)" (magnifying-glass icon), a bell/notification icon with a red badge count "8", a "?" help icon, and a circular user-avatar badge "JD".

**Left sidebar** (grouped, with section labels in small caps)
- Group "FMEA WORKSPACE": Home (highlighted/active, blue pill), FMEA Projects, DFMEA, PFMEA, System FMEA — each with a leading icon.
- Group "FMEA DATA": Functions, Requirements, Characteristics, Failure Modes, Causes, Controls, Actions — each with a leading icon.
- Group "ANALYSIS": AP / Detection, Risk Matrix, Validation Trajectory, Evidence & Tests, Change Impact.
- Group "INTEGRATION": XDA Investigations, CAPA, Control Plans, SPC / ITRA-DT, Documents & Links.
- Below the groups (separated by a divider): Settings, "Collapse Menu" (with a left-arrow icon).
- Sidebar footer: "Version 1.0.0 • Open-EQMS".

**Page header content area**
- Heading "Welcome back, Janez!"
- Subtext "Here's the current status of your FMEA activities."
- Right-aligned button row: "+ New FMEA" (solid blue/primary), "Open Project" (outline, folder icon), "Import" (outline, upload icon), "Reports" (outline), "Templates" (outline), "AI Assistant" (outline, sparkle icon).

**Row of 5 stat/KPI cards**
1. Icon (blue folder). Label "FMEA Projects". Value **12**. Caption "Active projects". Link "View all projects →".
2. Icon (green heartbeat/pulse in circle). Label "Active Analyses". Value **7**. Caption "In progress". Link "View all analyses →".
3. Icon (amber/yellow warning triangle). Label "High Risk Items". Value **23**. Caption "5 new since last review". Link "View high risks →".
4. Icon (red shield with check). Label "Actions Overdue". Value **8**. Caption "2 critical • 6 normal". Link "Go to actions →".
5. Icon (purple checklist/clipboard-check). Label "Reviews Due". Value **4**. Caption "Next within 7 days". Link "View reviews →".

**Three-column analytics row**
- Card "Risk Overview (All Projects)": a heat-map style grid/table. Column axis labeled "Severity" with header values 1–5. Row axis labeled "Occurrence" (rotated label) with row values 5,4,3,2,1 (top to bottom). Each of the 25 cells contains an integer count and a background color. Literal cell values (Occurrence row → Severity 1,2,3,4,5):
  - Occurrence 5: 0, 1, 3, 6, 4
  - Occurrence 4: 0, 2, 5, 6, 2
  - Occurrence 3: 1, 3, 6, 3, 1
  - Occurrence 2: 0, 1, 2, 2, 0
  - Occurrence 1: 0, 0, 1, 0, 0
  - Legend below grid: green dot "Low (1-2)", yellow dot "Medium (3-6)", red dot "High (8-25)" — note: only 3 tiers/colors are labeled in this legend even though the grid visually appears to use an orange shade too (orange cells are not separately called out in the legend text on this mockup).
  - Link "Open Risk Matrix →".
- Card "Validation Trajectory Overview", subtitle "Project: New Headlamp X1 (DFMEA + PFMEA)":
  - A horizontal 7-step stepper/timeline with circular icon nodes and labels: Concept (green filled check), Design (green filled check), Prototype (green filled check), DV (blue open/outlined circle), Pilot (a filled dark/purple circle, no check), PPAP (yellow open circle), Serial (gray open circle).
  - "DFMEA Validation Coverage" — horizontal progress bar, green fill, labeled **78%**.
  - "PFMEA Validation Coverage" — horizontal progress bar, blue fill, labeled **62%**.
  - Legend row: green dot "Completed", blue dot "In Progress", yellow dot "Planned", red dot "Overdue", gray dot "Not Started".
  - Link "Open Validation Trajectory →".
- Card "Top High Risk Items", link "View all →" (top-right):
  - Table with columns: **Item | Project | RPN | Risk**. The "Item" column visually contains both a code (e.g. "FM-021") and a short description (e.g. "Beam distortion") stacked/inline under one header.
  - Rows:
    - FM-021, Beam distortion | Headlamp X1 DFMEA | 210 | High (red pill)
    - FM-034, LED overheating | Headlamp X1 DFMEA | 192 | High (red pill)
    - FM-067, Water ingress | Headlamp X1 PFMEA | 168 | High (red pill)
    - FM-045, Adhesive weak point | Headlamp X1 DFMEA | 150 | High (red pill)
    - FM-089, Assembly misalignment | Headlamp X1 PFMEA | 120 | Medium (amber/orange pill)
  - Link "Go to High Risk Items →".

**Bottom three-column row**
- Card "Recent Projects", link "View all →". Rows, each with a leading colored icon, project name, a sub-label for FMEA type, a status pill, and "Updated X ago":
  - (blue icon) New Headlamp X1 / "DFMEA + PFMEA" / status pill "In Progress" (blue) / Updated 2h ago
  - (document icon) Rear Light Y2 / "DFMEA" / status pill "In Review" (lavender/purple) / Updated 1d ago
  - (document icon) Control Unit Z3 / "DFMEA" / status pill "Draft" (gray) / Updated 2d ago
  - (chain/link icon) Lens Module L1 / "PFMEA" / status pill "In Progress" (blue) / Updated 3d ago
  - (shield icon) Cooling System C2 / "DFMEA + PFMEA" / status pill "In Review" (lavender/purple) / Updated 5d ago
  - Link "Open FMEA Projects →".
- Card "Recent Activity", link "View all →". Feed rows, each with a leading icon, a bold description line, a gray sub-line (which FMEA), and a relative timestamp:
  - (gear/settings icon) "Design change DC-015 linked to FM-021" / "New Headlamp X1 DFMEA" / 1h ago
  - (link icon) "Validation test result added for SC-018" / "New Headlamp X1 DFMEA" / 3h ago
  - (document icon) "Action A-117 marked complete" / "Rear Light Y2 DFMEA" / 5h ago
  - (link icon) "New cause added to FM-034" / "New Headlamp X1 DFMEA" / 1d ago
  - (green checkmark icon) "FMEA review completed" / "Control Unit Z3 DFMEA" / 2d ago
- Card "Knowledge & References", link "View all →". Rows with icon, name, type sub-label, "Updated X ago":
  - (document icon) FMEA Handbook (AIAG & VDA) / Document / Updated 5d ago
  - (document icon) DFMEA Best Practices / Document / Updated 10d ago
  - (document icon) PFMEA Guideline / Document / Updated 12d ago
  - (yellow database icon) Lessons Learned Database / Knowledge Base / Updated today
  - (document icon) Failure Mode Library / Library / Updated 2d ago

**Footer status bar**
- "Database: OpenEQMS_Local" (database icon), "User: Janez Demo (Quality Engineer)" (person icon), "Role: Project Owner" (link/role icon), "Workspace: Global" (globe/org icon), "Notifications 8" (bell icon, green badge), "System Status" (green dot).

### 2. Wireframe & UI/UX

- Overall layout is a classic app shell: fixed dark-navy left sidebar (~220–260px), full-height, scrollable if needed; a light-gray/white main content area filling the rest; a slim top bar spanning the main content area only (not over the sidebar); a slim footer status bar spanning full width at the very bottom.
- Sidebar groups items under small-caps gray section headers with generous vertical spacing; the active item ("Home") is a filled blue pill, all others are plain icon+label rows on the dark background.
- Main content is a single scrolling column of horizontally-stacked card rows: a page-header row (title/subtitle + action buttons), a 5-up stat-card row, a 3-column analytics row (matrix / trajectory / top-risk table), then a 3-column "recent" row (projects / activity / knowledge). Column widths are roughly equal thirds in both 3-column rows.
- Visual hierarchy: the 5 stat cards use large bold numerals (largest text on the page besides the welcome heading) with a small icon and colored accent per card, drawing the eye first; the risk matrix and validation trajectory cards use color coding as the next-strongest visual signal; list/table rows are plain text with a colored status pill as the only accent.
- Color/status coding: risk severity uses green→yellow→red heat coloring on the matrix and on the "Risk" column pills (red = High, amber = Medium); validation trajectory stages use green (done) / blue (in progress) / yellow (planned) / gray (not started) / red (overdue, defined in legend but not present as a node color in this instance); project/action status pills use blue ("In Progress"), lavender ("In Review"), gray ("Draft").
- Typography: card titles are bold/dark; stat numerals are extra-bold and large; captions and metadata (timestamps, sub-labels) are smaller and gray; all "View all / Open X →" links are blue and clearly clickable.
- Implied interactions: every card title area with a trailing "→" link or "View all" is a navigation link into a dedicated full page (e.g. Risk Matrix page, Validation Trajectory page, FMEA Projects list). Each stat card's caption link jumps to a filtered list (e.g. "View high risks" → Failure Modes or Risk Matrix filtered to High). Each row in "Recent Projects" is presumably clickable through to that FMEA's workspace. The project selector dropdown in the header implies switching the whole dashboard's data scope to a different FMEAProject. The bell icon implies a notifications drawer/panel. No hover or modal states are directly depicted, but the stepper nodes in "Validation Trajectory" look interactive/clickable given they resemble a workflow control.

### 3. Architecture & Data Logic — what this should do and how it should behave

- **Logo/branding, nav labels, header chrome (search, bell, help, avatar)** — UI-only; not domain-data. The avatar/username can bind to Django's built-in `User` (Tier A once wired), but "help" and generic search have no backing search index defined anywhere — **Tier D** for a real cross-entity search (`Search (Ctrl+K)` implies a global search across FMEA/FailureMode/Cause/Action/etc.; no search index/service exists).
- **Sidebar nav items** — each corresponds 1:1 to an existing model area already described in the grounding (FMEA, Product/Process/Function, FailureMode, FailureCause, PreventionControl/DetectionControl, RecommendedAction) — **Tier A**, this is routing/IA only, no new logic. "Controls" as a single combined nav item would need to fan out to both `PreventionControl` and `DetectionControl` — trivial, **Tier A**.
- **Stat card 1 — FMEA Projects (12, "Active projects")**: `FMEAProject.objects.filter(status=<active>).count()`. `FMEAProject.status` is a real field. **Tier A.**
- **Stat card 2 — Active Analyses (7, "In progress")**: most plausibly `FMEA.objects.filter(lifecycle=<in_progress>).count()`, using the real `FMEA.lifecycle` (`FMEALifecycle` enum) field. **Tier A** (simple filter+count).
- **Stat card 3 — High Risk Items (23, "5 new since last review")**: the base count requires, per `FailureMode`, selecting the *latest* `RiskEvaluation` (`.order_by("-evaluated_at","-id").first()` per the model's own default ordering) and testing its `result` JSON's `classification` (or numeric `score`) against a "High" threshold, then counting matches across all FMEAs — **Tier B** (real fields, needs new aggregation query: latest-evaluation-per-failure-mode + classification filter + count). The "5 new since last review" delta needs a stored baseline/snapshot of a prior count to diff against — no such history/snapshot entity exists — **Tier D** for that sub-metric specifically.
- **Stat card 4 — Actions Overdue (8, "2 critical • 6 normal")**: base "overdue" count = `RecommendedAction.objects.filter(due_date__lt=today).exclude(status__in=[completed, verified, cancelled]).count()`, using real `due_date`/`status` fields — **Tier B** (needs new query logic; also implies overdue is a *derived* state, not a stored status value — see behavioral note below). The "critical / normal" split has no backing severity/priority field on `RecommendedAction` — **Tier D**: would need a new field (proposed `RecommendedAction.priority` choice field, e.g. critical/normal) with its own validation/assignment rule.
- **Stat card 5 — Reviews Due (4, "Next within 7 days")**: no review/audit-cadence entity exists anywhere in the grounded model (no scheduled-review date on `FMEA` or `FMEAProject`). **Tier D** — would need a new entity, proposed `FMEAReview` (fmea FK, scheduled_date, status [scheduled/completed/overdue], reviewer(s), notes), with a scheduling/creation flow, an "overdue" derivation from scheduled_date vs today, and presumably a permission rule on who can schedule/complete a review.
- **Risk Overview matrix**: requires, for every `FailureMode`'s latest `RiskEvaluation`, grouping counts by `(severity, occurrence)` pair into a 5×5 grid — real `severity`/`occurrence` integer fields on `RiskEvaluation`, but the grouping/counting query does not exist today. **Tier B.** The color-banding thresholds shown in the legend ("Low 1-2", "Medium 3-6", "High 8-25") look like RPN-style score bins being applied to what is nominally a severity×occurrence *cell*, not a computed RPN — this exact binning rule is not defined anywhere and should be treated as **proposed** logic pending an architecture decision (which score the color reflects: cell count, or an RPN computed from severity×occurrence×detection for evaluations landing in that cell).
- **Validation Trajectory Overview (stepper + coverage bars)**: the grounding explicitly states no lifecycle-phase-tracking model exists (no Concept/Design/Prototype/DV/Pilot/PPAP/Serial phase entity). **Tier D** — would need a new entity, proposed `FMEALifecycleStage` or similar, tracking per-FMEA (or per-project) phase name, order, and status (completed/in-progress/planned/overdue/not-started), plus a policy for how a stage's status transitions (manual mark-complete? automatically derived from validation coverage crossing a threshold?). The two coverage percentages ("DFMEA Validation Coverage 78%", "PFMEA Validation Coverage 62%") could be *approximated* today from real data — e.g. percentage of `FailureMode` rows (scoped to `FMEA.fmea_type`) that have at least one `RiskEvaluation`, or percentage of `RecommendedAction`s with `status=verified`/backed by an `EffectivenessVerification` — but the exact formula shown is not specified by any existing field, so this is **Tier B** at best (derivable, needs new aggregation) and should not be assumed identical to the stage-tracking concept above.
- **Top High Risk Items table**: for each `FailureMode`, latest `RiskEvaluation.result["score"]` (RPN), joined through `FailureMode.fmea → FMEA.project → FMEAProject.name` and `FMEA.fmea_type` for the "Project" column label, filtered/sorted descending by score, classification mapped to a "Risk" pill via `result["classification"]`. All real fields, but the join/aggregation/sort does not exist as a query today. **Tier B.**
- **Recent Projects card**: listing `FMEAProject` (or `FMEA`) rows ordered by most-recently-updated, with a status pill from `FMEA.lifecycle`/`FMEAProject.status`. The grounded field list for `FMEAProject`/`FMEA` does not confirm an `updated_at`/timestamp field exists — if standard Django auto-timestamps are present this is **Tier B** (needs an ordering query); if no timestamp field exists at all, this becomes **Tier C** (real entity, but "Updated 2h ago" recency display is not backed without adding a timestamp field). Flagged as **unconfirmed — verify before scoping.**
- **Recent Activity feed**: implies a unified, cross-entity activity/audit log (design changes, validation test results, action completions, new causes, review completions) with actor/time/target. `RiskEvaluation` does carry `actor` and `trigger` fields, which could back a narrow slice of this feed (risk-evaluation-related events only) — **Tier B/A** for that slice. But the feed as shown spans several entities that have no logging at all today, and one row ("Design change DC-015 linked to FM-021") implies a `Change`-type entity, which the grounding explicitly states **does not exist**. **Tier D** overall — would need a new generic `ActivityLogEntry` model (actor, verb, target content-type/id, fmea FK, description, created_at) populated by signal handlers/hooks across the relevant models, plus (separately, out of scope here) a `Change` entity for the design-change linkage example.
- **Knowledge & References card**: implies document/library/knowledge-base storage (FMEA Handbook, Best Practices, Guidelines, Lessons Learned Database, Failure Mode Library) with type tagging and update timestamps. The grounding explicitly states no file/attachment/document storage and no "Catalog" library entity exist. **Tier D** — would need a new `KnowledgeReference` (or similar) entity: title, type (Document/Knowledge Base/Library), a URI or uploaded file, updated_at, and presumably a CRUD/ownership model for who can publish/update these.
- **Footer status bar**: "User"/"Role" can bind to Django's auth `User` plus a role label — but grounding is explicit that no real per-user role/permission system exists (`ProjectMembership.role` is a plain label, not enforced). Showing "Role: Project Owner" as if it grants effective permissions is **Tier C** (a role *label* exists via `ProjectMembership.role`, but it is far short of an enforced role/permission concept implied by displaying it in a system-status bar). "Database: OpenEQMS_Local" and "System Status" are infrastructure/environment labels, not domain data — out of model scope entirely (not tiered).

**Behavioral logic implied:**
- Entering a new `RiskEvaluation` for a `FailureMode` should, if this dashboard is live-computed, immediately shift: the High Risk Items count, the Risk Overview matrix cell counts, the Top High Risk Items table membership/order, and (if wired) the DFMEA/PFMEA coverage percentages. None of this is automatic today — it would need to be computed at request time (or cached/recomputed on save via a signal), since `RiskEvaluation` has no denormalized "is this the latest" flag; "latest" must always be derived via ordering.
- "Actions Overdue" is a **derived state** (due_date passed while status is still open/in_progress), not a stored value — it must be recomputed on every view, or backed by a scheduled job that flips a computed flag; `ActionStatus` itself has no "overdue" value (confirmed: enum is open/in_progress/completed/verified/cancelled).
- Status pills on "Recent Projects" (Draft/In Progress/In Review) imply a state machine on `FMEA.lifecycle` (or a project-level status) with defined transitions — the grounding confirms `FMEALifecycle` is a real enum, but the specific transition rules (who can move Draft→In Progress→In Review, whether In Review can revert to Draft) are not specified anywhere and should be treated as **proposed** if scoped later.
- Every "View all →" / card-title link is a cross-entity navigation implying dedicated list pages exist for: FMEA Projects, Analyses, High Risk Items, Actions, Reviews, Risk Matrix, Validation Trajectory, Recent Activity, Knowledge & References — several of these destination pages themselves are Tier D concepts (Reviews, Knowledge & References) since their source data doesn't exist yet.

**Tier summary:** Tier A — sidebar nav/IA, FMEA Projects count, Active Analyses count. Tier B — High Risk Items base count, Actions Overdue base count, Risk Overview matrix aggregation, Top High Risk Items table, Recent Projects ordering (pending timestamp confirmation), validation coverage percentages (as an approximation, not as shown). Tier C — Role display (label exists, no enforcement), Recent Projects timestamp (unconfirmed field). Tier D — "5 new since last review" delta, critical/normal action split, Reviews Due (no entity), Validation Trajectory stage tracking (no entity), Recent Activity feed (no generic log; Change entity referenced doesn't exist), Knowledge & References (no document/library entity), global search index, enforced role/permission system.

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 02 — Engineering Context Panel (source: mockup-02-engineering-context-panel.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Header** (same shell as mockup-01, with one difference): hamburger icon, title "Home", project selector "Project: New Headlamp X1" (chevron), search box "Search (Ctrl+K)", bell icon badge "8", a 9-dot "app launcher" grid icon (in place of mockup-01's "?" help icon), circular avatar "JD".

**Left sidebar**, grouped:
- "FMEA WORKSPACE": Home (active, blue), FMEA Projects, FMEA Team.
- "CONTEXT (from Open-EQMS)": a collapsible group header "System / Product / Process" (chevron, expanded), with sub-items System, Product, Process — Process has a green pill badge reading "Enabled" to its right. Below that, at the same outer level: System Characteristics, Characteristics Flow, Process Flow (external-link icon), Process Characteristics (external-link icon).
- "FMEA ANALYSIS": DFMEA, PFMEA, System FMEA, Functions, Failure Modes, Effects, Causes, Prevention Controls, Detection Controls, Actions.
- "VALIDATION & CHANGE": Validation Trajectory, Evidence & Tests, Change Impact.
- "ANALYSIS": AP / Detection, Risk Matrix, XDA Investigations.
- "LINKED EQMS": Control Plans, SPC / ITRA-DT, CAPA, Documents & Links.
- Divider, then Settings, Collapse.

**Page header**: "Welcome back, Janez!" / "Here's the status of your FMEA projects and engineering context." Button row: "+ New FMEA" (primary), "Open Project", "Import", "Reports" (dropdown chevron), "Templates" (dropdown chevron), "AI Assistant".

**5 stat cards** (identical set to mockup-01): FMEA Projects 12 / Active projects; Active Analyses 7 / In progress; High Risk Items 23 / 5 new since last review; Actions Overdue 8 / 2 critical • 6 normal; Reviews Due 4 / Next within 7 days — each with its "View..." link.

**Tab bar**: "Project Dashboard" (active, blue underline), "DFMEA", "PFMEA", "System FMEA".

**3-column analytics row** (under the tabs):
- "Risk Overview (All Projects)" — same 5×5 Severity(1–5)×Occurrence(1–5) heat-map grid as mockup-01, but with different values and a 4-tier legend:
  - Occurrence 5: 0, 1, 3, 7, 5
  - Occurrence 4: 0, 2, 5, 6, 2
  - Occurrence 3: 1, 3, 6, 3, 1
  - Occurrence 2: 0, 1, 2, 2, 0
  - Occurrence 1: 0, 0, 1, 0, 0
  - Legend: green "Low (1-2)", yellow "Medium (3-6)", orange "High (7-12)", red "Very High (13-25)" — note this mockup's legend has 4 distinct tiers (unlike mockup-01's 3-tier legend).
  - Link "Open Risk Matrix →".
- "Validation Trajectory (DFMEA + PFMEA)" with a circled-"i" info icon:
  - 7-node horizontal stepper: Concept (green check), Design (green check), Prototype (green check), "DV / Design Verification" (green check), "PV / Process Validation" (blue open circle), PPAP (yellow open circle), Serial (gray open circle).
  - "DFMEA Validation Coverage" progress bar, green, **78%**.
  - "PFMEA Validation Coverage" progress bar, blue, **62%**.
  - Legend: green "Completed", blue "In Progress", yellow "Planned", red "Overdue", gray "Not Started".
  - Link "Open Validation Trajectory →".
- "Top High Risk Items", link "View all →": table columns **Item | Type | Project | RPN | Risk**. Rows:
  - FM-021 Beam distortion | DFMEA | Headlamp X1 | 210 | High (red)
  - FM-034 LED overheating | DFMEA | Headlamp X1 | 192 | High (red)
  - FM-067 Water ingress | PFMEA | Headlamp X1 | 168 | High (red)
  - FM-045 Adhesive weak point | PFMEA | Headlamp X1 | 150 | High (red)
  - FM-089 Assembly misalignment | PFMEA | Headlamp X1 | 120 | Medium (amber)
  - Link "Go to High Risk Items →".

**Bottom row (4 cards)**:
- "FMEA Team (Project)", link "Manage team →": list of 5 members, each with a colored circular initials avatar, name ("You" suffix on the first), role sub-label, and a role pill on the right:
  - JD (purple avatar) Janez Demo (You) — "FMEA Leader" — pill "Owner"
  - MK (green avatar) Marko Kovac — "Design Engineer" — pill "Member"
  - AN (orange avatar) Ana Novak — "Process Engineer" — pill "Member"
  - PT (blue avatar) Peter Turk — "Quality Engineer" — pill "Member"
  - LS (indigo avatar) Luka Sterle — "Manufacturing Engineer" — pill "Member"
  - "+ Add member" link/button at bottom.
- "Characteristics Flow", link "Open full view →": a vertical flow diagram of 6 boxes connected by arrows:
  - "Requirements (Open-EQMS)" → "Functions (Open-EQMS)" (this box shows overlapping/ghosted duplicate text rendering, literally showing "Functions" layered over "Functions (Open-EQMS)") → splits into two parallel boxes "Product / System Characteristics (Open-EQMS)" (green) and "Process Characteristics (Open-EQMS)" (blue) → both converge into "Failure Modes (FMEA)" (purple) → splits again into "Controls (FMEA)" (yellow) and "Control Plan (Open-EQMS)" (teal).
  - Link "View all links →" at the bottom.
- "Recent Projects", link "View all →": columns Project | Type | Status | Updated. Rows:
  - New Headlamp X1 | DFMEA + PFMEA | "In Progress" (blue) | 2h ago
  - Rear Light Y2 | DFMEA | "In Review" (lavender) | 1d ago
  - Control Unit Z3 | DFMEA | "Draft" (gray) | 2d ago
  - Lens Module L1 | PFMEA | "In Progress" (blue) | 3d ago
  - Cooling System C2 | DFMEA + PFMEA | "In Review" (lavender) | 5d ago
  - Link "Open FMEA Projects →".
- "Recent Activity", link "View all →": same 5-row feed as mockup-01 (Design change DC-015 linked to FM-021 / 1h ago; Validation test result added for SC-018 / 3h ago; Action A-117 marked complete / 5h ago; New cause added to FM-034 / 1d ago; FMEA review completed / 2d ago), each with icon + sub-FMEA label.

**Right-hand slide-in panel "Engineering Context (from Open-EQMS)"** (with a close "X"):
- Tab row: "System", "Product", "Process" (active, blue underline).
- "Process Flow" section header with link "Open in Process Planning ↗".
- A dropdown selector reading "Headlamp Assembly Process" (chevron).
- A vertical numbered-step list (radio-style circular markers), each row "step-number  Step name":
  - 10 Incoming Material
  - 20 Sub-Assembly
  - 30 Injection Moulding — this row is highlighted (light-blue background, filled/selected radio marker) and has a trailing "→" arrow, indicating it's the selected step.
  - 40 Post-Processing
  - 50 Inspection
  - 60 Packaging
- "Process Characteristics (Step 30)" section: a 3-column table **Characteristic | Target / Spec | Unit**:
  - Injection pressure | 820 ± 20 | bar
  - Melt temperature | 285 ± 5 | °C
  - Holding pressure | 600 ± 20 | bar
  - Cooling time | 18 ± 2 | s
  - Mould temperature | 90 ± 3 | °C
  - Link "View all process characteristics →".
- "Linked Product Characteristics (affected)" section: a 3-column table **Characteristic | Type | Criticality**:
  - Lens geometry | Safety | "Critical" (red pill)
  - Optical transparency | Optical | "Critical" (red pill)
  - Surface quality | Decorative | "High" (amber pill)
  - Link "View all product characteristics →".

**Footer status bar**: same as mockup-01 (Database: OpenEQMS_Local, User: Janez Demo (Quality Engineer), Role: Project Owner, Workspace: Global, Notifications 8, System Status dot). Note: the "Version 1.0.0" label appears here in the footer bar rather than the sidebar footer.

### 2. Wireframe & UI/UX

- Same base app-shell layout as mockup-01 (dark sidebar, light main content, top bar, footer bar), but the main content is now further organized under a tab strip ("Project Dashboard / DFMEA / PFMEA / System FMEA") sitting directly beneath the stat-card row, and a persistent right-hand drawer/panel ("Engineering Context") is docked open, narrowing the effective width of the 3-column analytics/bottom rows.
- The right panel is itself internally tabbed (System/Product/Process) and, within the active "Process" tab, is a two-level master-detail: a dropdown chooses which process flow, a vertical stepper/list picks the step within that flow, and selecting a step drives two tables below it (that step's own characteristics, and the *linked* product characteristics it affects). This is a drill-down / master-detail interaction pattern, not a static display.
- Visual hierarchy: the right panel uses the same card/typography conventions as the main content (bold section headers, small-caps-free), with the selected process step given a highlighted row (light-blue fill + colored radio dot + arrow) to show current selection state — implying the other rows are clickable and would re-highlight/re-populate the two tables below on click.
- Color coding: risk pills reuse red=High/amber=Medium; criticality pills reuse red="Critical"/amber="High"; team-member avatars are each a distinct flat color (no evident semantic meaning beyond visual differentiation) with role pills distinguishing "Owner" (green) from "Member" (gray).
- The Characteristics Flow diagram uses a distinct pastel color per box to indicate box "type": gray (Requirements/Functions), green (Product/System Characteristics), blue (Process Characteristics), purple (Failure Modes), yellow (Controls), teal (Control Plan) — implying a legend/typing convention that should be kept consistent wherever this diagram reappears.
- Implied interactions: clicking a sidebar "Context" sub-item (System/Product/Process) presumably opens/updates this same right panel to that tab; the panel's own tab strip duplicates that navigation. The process-step list is a selectable list (only one step "selected" at a time, shown via the highlighted state) whose selection re-renders "Process Characteristics (Step N)" and "Linked Product Characteristics". "Open in Process Planning ↗" and "Open full view →" links imply this panel is a *summary* of a larger, separate Process Planning experience elsewhere (likely outside this FMEA app entirely, in the Open-EQMS suite). The panel's "X" closes it back to a full-width main content view (as in mockup-01).

### 3. Architecture & Data Logic — what this should do and how it should behave

- **Sidebar "System / Product / Process" context group + right-panel tabs (System/Product/Process)**: maps to the real `Product` and `Process` models (both FK'd to `FMEA`). **Tier A** for Product/Process tabs as navigation into existing entities. There is **no `System` model anywhere in the codebase** per the grounding — the "System" tab/sidebar item is **Tier D**: it implies a new entity above Product/Process (a proposed `System` model that Products and/or Processes would optionally belong to), which is explicitly called out as not-yet-approved.
- **"Process" sub-item "Enabled" badge**: implies a per-context enable/disable toggle or a completeness flag ("this context has data configured"). No such flag exists on `Process`/`FMEA` today. **Tier D** (proposed boolean/derived flag — proposed as either a stored `Process.is_configured` field or a derived check such as "has ≥1 Operation with ≥1 ProcessCharacteristic").
- **Process Flow dropdown + numbered step list (10/20/30/.../60)**: maps well to `Operation` (FK to `Process`, has `sequence`) rendered ordered by `sequence`, with the two-digit numbering ("10", "20"...) plausibly being `Operation.sequence` values directly, and each row's label being `Operation.name`. **Tier A** — real fields (`Process.name` for the dropdown, `Operation.sequence`/`Operation.name` for the list), just needs a view/template to surface an existing relationship as this stepper widget.
- **"Process Characteristics (Step 30)" table (Characteristic / Target-Spec / Unit)**: maps to `ProcessCharacteristic` (FK to `Operation`), which has `name` and `description` plus a generic `attributes` JSONField. **Tier A/B** — `name` is real (Tier A); "Target / Spec" and "Unit" as separate structured columns are not confirmed as their own fields (only a generic `attributes` JSON exists) — extracting/displaying them requires either (a) a convention for keys inside `attributes` (Tier B, needs new parsing/display logic against existing JSON) or (b) promoting Target/Spec/Unit to first-class fields on `ProcessCharacteristic` (Tier D if the JSON convention doesn't already hold this shape — flag as **proposed** either way, since the grounding does not confirm any convention for `attributes`' contents).
- **"Linked Product Characteristics (affected)" table (Characteristic / Type / Criticality)**: maps to `ProductCharacteristic` (FK to `Requirement`), which has `name`, `description`, `is_special` (bool). **Tier A** for `name` (real field). "Criticality" pill (Critical/High) is not a stored field — the closest real field is the boolean `is_special`, which is a 2-value flag, not a graded criticality scale — **Tier C** (a real, related boolean field exists but falls short of the multi-level "Critical/High/..." scale shown). "Type" (Safety/Optical/Decorative) has no backing field on `ProductCharacteristic` at all in the grounded model — **Tier D**, proposed new field/enum (e.g. `ProductCharacteristic.characteristic_type`). The *link* itself — which product characteristics are "affected" by a given process step — is not modeled directly: `ProductCharacteristic` links to `Requirement`, not to `Operation`/`ProcessCharacteristic`; deriving "affected by process step 30" would require walking `ProcessCharacteristic → Operation → (via Function/Requirement chain) → ProductCharacteristic`, which is not a direct relationship in the grounded schema and may not resolve for most real records — **Tier B/D boundary**, flagged as needing an explicit architecture decision on how Product↔Process characteristic linkage is actually modeled (the grounding's own `CauseCategoryScheme`/`CauseInfluence` Ishikawa backend is the closest existing cross-linking mechanism, but it connects `ProcessCharacteristic`/`FailureCause`, not `ProcessCharacteristic`/`ProductCharacteristic` directly).
- **Characteristics Flow diagram**: a static visual summary of exactly the real relationship chain `Requirement → Function → (Product/Process)Characteristic → FailureMode → (PreventionControl/DetectionControl)`, plus two "Open-EQMS"-sourced boxes (Control Plan) that are outside this app's own models. **Tier A** for the FMEA-side boxes as a *diagram* (all relationships it depicts exist as real FKs: `Requirement.function`, `Function.product`/`Function.operation`, `ProductCharacteristic.requirement`, `ProcessCharacteristic.operation`, `FailureMode.function`/`FailureMode.requirement`, `PreventionControl.failure_cause`/`DetectionControl.failure_cause`) — rendering it as an interactive diagram (vs. a static image) is new UI work, not new data logic. "Control Plan (Open-EQMS)" is **Tier D** from this app's perspective (no Control Plan entity exists in this codebase; it is presumably a separate Open-EQMS module referenced only by name).
- **FMEA Team (Project) card**: maps to `ProjectMembership` (project FK, user FK, role label) joined to Django's `User` for name/initials. **Tier A** for listing members/roles (real fields: `ProjectMembership.role`, `user.username`/`get_full_name`). The "Owner" vs "Member" *pill* implies `role` is being read as a controlled value ("Owner"/"Member"/etc.) rather than a free label — since `ProjectMembership.role` is explicitly a **plain label with no enforcement**, treating it as a fixed enum with UI-level meaning (e.g. gating "Manage team" or "Add member" actions) is **Tier C** — the field exists but the role-based behavior implied by the UI (only an Owner can manage the team, presumably) is not backed by any permission system. "Add member" as a working action is **Tier A** (straightforward create on `ProjectMembership`) provided no permission gate is required; if a permission gate is required, that gate is **Tier D**.
- **Recent Projects / Recent Activity / Top High Risk Items / stat cards / Risk Overview / Validation Trajectory**: identical widgets and identical tiering to mockup-01's Section 3 — see that file. (Risk Overview's 4-tier legend variant here vs. mockup-01's 3-tier legend is a presentation-only discrepancy layered on the same Tier B aggregation.)
- **App-launcher (9-dot) icon in the header**: implies navigation to sibling Open-EQMS modules (a suite switcher). No such module registry exists in the grounded model; this is infrastructure/navigation, not domain data (not tiered against the FMEA model, but worth flagging as **Tier D** if it needs to be data-driven rather than a hardcoded link list).

**Behavioral logic implied:**
- Selecting a different step in the Process Flow list should re-query and re-render both "Process Characteristics (Step N)" and "Linked Product Characteristics (affected)" — a client-side or server-side master-detail refresh keyed on the selected `Operation.id`.
- Switching the right panel's top tab (System/Product/Process) should swap its entire content region to context appropriate to that entity — the "System" tab has no data source to switch to today (Tier D blocks it).
- The "Enabled" badge next to "Process" in the sidebar implies some contexts can be toggled on/off per project/FMEA — the transition rule (who enables it, what "disabled" hides) is undefined and should be treated as proposed if pursued.
- `ProjectMembership.role` driving both a display pill and (implicitly) an "Add member" permission gate is a state-machine-adjacent concern: today it's just a string, so any access-control behavior inferred from the mockup should be explicitly scoped as new work, not assumed to already exist.

**Tier summary:** Tier A — Product/Process context tabs, Process Flow step list (Operation.sequence/name), Process Characteristics names, Product Characteristics names, Characteristics Flow diagram relationships (as a static diagram), FMEA Team roster listing, Recent Projects/Activity/stat cards/Top High Risk table (same as mockup-01). Tier B — Target/Spec/Unit extraction from ProcessCharacteristic.attributes JSON (pending a key convention), Product↔Process characteristic "affected" linkage query, Risk Overview matrix aggregation. Tier C — ProductCharacteristic "Criticality" pill (only a boolean is_special exists), ProjectMembership.role treated as an enforced role. Tier D — "System" entity/tab entirely, "Enabled" context toggle, ProductCharacteristic "Type" field, Control Plan entity, app-launcher module registry, plus all Tier D items carried over from mockup-01 (Reviews Due, Recent Activity generic log, Change entity, Knowledge & References, enforced role/permission system).

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 03 — Preventive FMEA (PM-FMEA) Tab (source: mockup-03-preventive-fmea-pmfmea-tab.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Header/sidebar**: same shell chrome as mockup-02 (logo, hamburger, "Home" title, project selector "Project: New Headlamp X1", search, bell "8", "?" help icon, avatar "JD"). Sidebar groups:
- "FMEA WORKSPACE": Home, FMEA Projects, FMEA Team.
- "CONTEXT (from Open-EQMS)": collapsible "System / Product / Process" (expanded) with sub-items System, Product, Process; then System Characteristics, Characteristics Flow, Process Flow (external-link icon), Process Characteristics (external-link icon).
- "FMEA ANALYSIS": DFMEA, PFMEA, System FMEA, **Preventive FMEA (PM-FMEA)** (this item is highlighted/active, blue background), Functions, Failure Modes, Causes, Prevention Controls, Detection Controls, Actions.
- "VALIDATION & CHANGE": Validation Trajectory, Evidence & Tests, Change Impact.
- "ANALYSIS": AP / Detection, Risk Matrix, XDA Investigations.
- "LINKED EQMS": Control Plans, SPC / ITRA-DT, CAPA, Documents & Links.
- Settings, Collapse.

**Page header**: breadcrumb-style heading "FMEA Workspace – New Headlamp X1" (blue link-styled). Stat cards row (same 5 as mockups 1–2: FMEA Projects 12, Active Analyses 7, High Risk Items 23, Actions Overdue 8, Reviews Due 4).

**Top-level tab bar**: "DFMEA", "PFMEA", "System FMEA", "**Preventive FMEA (PM-FMEA)**" (active, blue underline). A secondary outline button "⚙ FMEA Workspace Settings" sits to the right of the tabs.

**Second-level tab bar** (sub-tabs within Preventive FMEA): "Overview" (active), "FMEA Team", "Scope & Configuration", "Links (Open-EQMS)", "Reviews", "Baseline", "History".

**3-column analytics row**:
- "Preventive FMEA Overview" (with circled-"i" info icon):
  - "Assets Covered" donut/ring chart, center text **"124 of 156"**.
  - Legend beside the donut: green dot "Low Risk 68 (55%)", yellow dot "Medium Risk 34 (27%)", red dot "High Risk 16 (13%)", gray dot "Not Analyzed 12 (10%)".
  - Link "Open PM-FMEA →".
- "PM-FMEA Validation Trajectory":
  - 7-node horizontal stepper: Concept (green check), Design (green check), Install (green check), "Commission" (blue open circle), "PV / Performance Validation" (yellow open circle), Operation (gray open circle), Monitor (gray open circle).
  - "Maintenance Readiness" progress bar, green, **78%**.
  - "PM-FMEA Coverage" progress bar, blue, **64%**.
  - Legend: green "Completed", blue "In Progress", yellow "Planned", red "Overdue", gray "Not Started".
  - Link "Open PM-FMEA Trajectory →".
- "Top High Risk Maintenance Items", link "View all →": table columns **Item | Asset / Machine | RPN | Risk**. Rows:
  - PM-021 Spindle bearing wear | CNC-01 | 210 | High (red)
  - PM-034 Hydraulic leak | Press-02 | 192 | High (red)
  - PM-067 Cooling system failure | Chiller-01 | 168 | High (red)
  - PM-045 Belt tension loss | Conv-03 | 150 | High (red)
  - PM-089 Filter clogging | Air Comp-01 | 120 | Medium (amber)
  - Link "Go to PM-FMEA Items →".

**Bottom row (4 cards)**:
- "FMEA Team (Project)", link "Manage team →": same 5-member roster as mockup-02 (JD Janez Demo (You) – FMEA Leader – Owner; MK Marko Kovac – Design Engineer – Member; AN Ana Novak – Process Engineer – Member; PT Peter Turk – Quality Engineer – Member; LS Luka Sterle – Manufacturing Engineer – Member). "+ Add member" link.
- "Characteristics Flow (Product → Process → Maintenance)", link "Open full view →": vertical flow diagram: "Product / System Characteristics (Open-EQMS)" (blue) → "Process Characteristics (Open-EQMS)" (green) → splits three ways into "PFMEA (Process Risk)" (purple), "PM-FMEA (Maintenance Risk)" (yellow), "Control Plan (Open-EQMS)" (teal) → all three converge into "Maintenance Tasks / Plans (Open-EQMS Maintenance)" (gray).
- "Recent Projects", link "View all →": columns Project | Type | Status | Updated. Rows:
  - New Headlamp X1 | "DFMEA + PFMEA + PM-FMEA" | "In Progress" (blue) | 2h ago
  - Rear Light Y2 | "DFMEA + PM-FMEA" | "In Review" (lavender) | 1d ago
  - Control Unit Z3 | "DFMEA + PFMEA" | "Draft" (gray) | 2d ago
  - Lens Module L1 | "PFMEA + PM-FMEA" | "In Progress" (blue) | 3d ago
  - Cooling System C2 | "DFMEA + PFMEA + PM-FMEA" | "In Review" (lavender) | 5d ago
  - Link "Open FMEA Projects →".
- "Recent Activity", link "View all →": rows —
  - (document/PM icon) "PM task 'Bearing inspection' created" / "CNC-01" / 1h ago
  - (red/maintenance icon) "Maintenance risk PM-021 updated" / "CNC-01" / 2h ago
  - (link icon) "PV plan linked to IMM-03" / "Injection Moulding Machine 03" / 4h ago
  - (document icon) "Action A-117 completed" / "Press-02" / 5h ago
  - (green checkmark icon) "FMEA review completed" / "Headlamp Assembly Process" / 1d ago

**Right-hand "Engineering Context (Open-EQMS)" panel** (with close "X"):
- Tab row: "System", "Product", "Process" (active), "**Characteristics**" (a 4th tab, not present in mockup-02's panel).
- "Process Flow" header, link "Open in Process Planning ↗". Sub-label "Select Process". Dropdown "Headlamp Assembly Process".
- Numbered step list identical to mockup-02: 10 Incoming Material, 20 Sub-Assembly, **30 Injection Moulding** (selected/highlighted, arrow), 40 Post-Processing, 50 Inspection, 60 Packaging.
- "Process Characteristics (Step 30)" table (Characteristic | Target/Spec | Unit): Injection pressure 820±20 bar; Melt temperature 285±5 °C; Holding pressure 600±20 bar; Cooling time 18±2 s; Mould temperature 90±3 °C. Link "View all process characteristics →".
- "**Linked Asset for Step 30**" section (new vs. mockup-02): a card showing a purple factory/building icon, asset name "Injection Molding Machine 03", asset code "IMM-03", a status pill "Operational" (light green) with a green status dot, "Location: Plant 1 / Line A", link "Open Asset in Maintenance →".
- "**Maintenance Status**" section (new vs. mockup-02):
  - "PM Compliance" — value **92%** (green) with a green horizontal progress bar.
  - "Overdue WO" — value **3** (red).
  - "Next PM" — value **12 May 2025** (blue).

**Footer status bar**: same as prior mockups (Database: OpenEQMS_Local, User: Janez Demo (Quality Engineer), Role: Project Owner, Workspace: Global, Version 1.0.0, Notifications 8, System Status dot).

### 2. Wireframe & UI/UX

- Same app shell as mockups 1–2, but now demonstrates a full drill-down: top-level FMEA-type tabs (DFMEA/PFMEA/System FMEA/**Preventive FMEA**) sit above a second row of workflow sub-tabs (Overview/FMEA Team/Scope & Configuration/Links/Reviews/Baseline/History) — a two-tier tab hierarchy per FMEA. This sub-tab set (especially "Baseline" and "History") implies each FMEA type carries its own change-tracking/versioning workflow, not just an analysis worksheet.
- The 3-column analytics row swaps its middle/left widgets for maintenance-flavored equivalents (donut "Assets Covered" instead of a severity×occurrence matrix; trajectory stages renamed to a maintenance-lifecycle set: Concept/Design/Install/Commission/PV (Performance Validation)/Operation/Monitor) — showing the app intends to reuse the same card layout/visual language across FMEA types while substituting the underlying metric.
- The right-hand Engineering Context panel gains a 4th tab ("Characteristics") not present in mockup-02, and its Process tab gains two entirely new sections below "Process Characteristics" — "Linked Asset for Step 30" and "Maintenance Status" — that do not appear when DFMEA/PFMEA tabs are active elsewhere, implying the panel's content is context-sensitive to which top-level FMEA tab is currently open (PM-FMEA context surfaces asset/maintenance data; DFMEA/PFMEA context does not).
- Visual hierarchy and color coding follow the same conventions established in mockups 1–2 (red/amber/green/gray for risk tiers; green/blue/yellow/gray/red for trajectory-stage status), reused here for maintenance risk and maintenance readiness — reinforcing a single shared design system across FMEA sub-types.
- Implied interactions: the donut chart segments are presumably clickable/filterable (click "High Risk" to filter the PM-FMEA worksheet to 16 high-risk maintenance items); "Open Asset in Maintenance →" implies a deep link out to a separate Maintenance/Asset module; the "Linked Asset" and "Maintenance Status" panels update based on which Process step (10/20/30/...) is selected, same master-detail pattern as mockup-02.

### 3. Architecture & Data Logic — what this should do and how it should behave

- **"Preventive FMEA (PM-FMEA)" as an FMEA type at all**: the grounded `FMEA.fmea_type` choices are design/process/product/software/system — **there is no "preventive" value**. This entire tab, and everything under it, is **Tier D**: it requires either (a) adding a new `fmea_type` choice plus all the maintenance-specific fields the UI implies, or (b) a materially different modeling decision (e.g., a distinct `PMFMEA` concept layered on `FMEA`). Flagging explicitly per the instructions: nothing below in this section should be read as confirming PM-FMEA is already partially built — only the generic `FMEA`/`FailureMode`/`RiskEvaluation`/`RecommendedAction` machinery is real, and PM-FMEA-specific concepts (assets, maintenance tasks, work orders, PM compliance) have **no backing entity of any kind**.
- **Sub-tabs Overview / FMEA Team / Scope & Configuration / Links / Reviews / Baseline / History**: "FMEA Team" maps to `ProjectMembership` (**Tier A**, same as mockup-02's team card). "Scope & Configuration" could map to `FMEA.scope`/`FMEA.description` (**Tier A** for a simple detail/edit form). "Links (Open-EQMS)" implied cross-references to Open-EQMS entities — **Tier B/D** depending which links (real FK chains like Product/Process are Tier A-adjacent; Control Plan/Maintenance links are Tier D since those entities don't exist here). "Reviews" — same as "Reviews Due" stat card in mockup-01, **Tier D**, no review entity exists. "Baseline" and "History" imply a versioning/snapshot mechanism for an entire `FMEA` (freeze-and-compare) — no such versioning model exists anywhere in the grounding. **Tier D** — would need a new entity, proposed `FMEABaseline`/`FMEASnapshot` (fmea FK, created_at, created_by, a serialized copy or diffable snapshot of the worksheet), plus comparison/diff logic.
- **"Preventive FMEA Overview" donut ("Assets Covered", 124 of 156, Low/Medium/High/Not Analyzed)**: assumes an `Asset`/`Machine` entity that `FailureMode`-equivalent maintenance rows would attach to, and a risk classification per asset. Grounding explicitly states **no Asset/WorkOrder/Resource/Equipment/calibration entity exists**. **Tier D** in full — would need a new `Asset` model (name, code, location, status) and a maintenance-analog to `FailureMode`/`RiskEvaluation` scoped to assets (or a repurposing of the existing `FailureMode`/`RiskEvaluation` models against a new `Asset`-linked `Process`/`Operation`, which is itself an open architecture question, not a given).
- **"PM-FMEA Validation Trajectory" (Concept/Design/Install/Commission/PV/Operation/Monitor stepper + Maintenance Readiness % + PM-FMEA Coverage %)**: same category as mockup-01/02's Validation Trajectory — **Tier D**, no lifecycle-stage entity exists, and here it's compounded by also needing the not-yet-existing Asset/maintenance-risk data to compute "coverage" against.
- **"Top High Risk Maintenance Items" table (Item / Asset-Machine / RPN / Risk)**: same computation pattern as mockup-01's "Top High Risk Items" (latest-RiskEvaluation-per-FailureMode, sorted, joined) **but** joined to an Asset/Machine column that has no backing field — `FailureMode` has no FK to any asset-like entity (only `function`/`requirement` FKs). **Tier D** for the Asset/Machine join and for the very existence of "PM-###" coded items as a distinct row type; the underlying RPN/Risk pill computation, if PM-FMEA rows are eventually modeled as ordinary `FailureMode`+`RiskEvaluation` rows, would be **Tier B** by analogy to mockup-01, but that modeling choice is not made anywhere in the grounding.
- **FMEA Team card, Recent Projects card, Recent Activity card, stat cards**: same widgets/tiering as mockup-01/02 (**Tier A** for team roster and project listing scaffolding; **Tier B** for aggregate counts; **Tier D** for the generic activity log / "5 new since last review"-style deltas). New here: Recent Projects rows show combined type badges like "DFMEA + PFMEA + PM-FMEA" — this presumes an FMEA can carry multiple `fmea_type` values or that multiple `FMEA` rows (one per type) are grouped per `FMEAProject` and their type badges concatenated for display; the latter is consistent with the real schema (`FMEA.project` FK, multiple `FMEA`s per `FMEAProject`) and is **Tier A/B** (needs a "group FMEAs by project, list distinct types" query) **once PM-FMEA exists as a real type** — until then it's blocked by the Tier D item above.
- **Characteristics Flow (Product → Process → Maintenance) diagram**: reuses the real relationship chain from mockup-02 (`ProductCharacteristic`←`Requirement`←`Function`, `ProcessCharacteristic`←`Operation`) for its first two boxes — **Tier A** for those. The fan-out to "PFMEA (Process Risk)" is **Tier A** (real, via `FailureMode`/`RiskEvaluation` scoped to process-type FMEAs). The fan-out to "PM-FMEA (Maintenance Risk)" and convergence into "Maintenance Tasks / Plans (Open-EQMS Maintenance)" are **Tier D** — neither the PM-FMEA risk concept nor a Maintenance Task/Plan entity exists in this codebase (Maintenance is explicitly named as a separate, unbuilt "Open-EQMS Maintenance" module here).
- **Right panel "Characteristics" 4th tab**: not detailed in this screenshot (panel shows "Process" tab active); by name it likely surfaces `ProductCharacteristic`/`ProcessCharacteristic` in a combined view — **Tier A/B**, real fields, needs a new combined query/view, consistent with mockup-02's tiering for those tables.
- **"Linked Asset for Step 30" (Injection Molding Machine 03, IMM-03, Operational status, Location: Plant 1 / Line A)**: implies `Operation` (or `ProcessCharacteristic`) has a link to a physical asset/machine. No such FK or Asset entity exists. **Tier D** — proposed new `Asset` model (name, code, status [operational/down/maintenance], location) plus a new FK from `Operation` (or a join table) to `Asset`.
- **"Maintenance Status" (PM Compliance 92%, Overdue WO 3, Next PM 12 May 2025)**: implies a `WorkOrder`/`MaintenancePlan` entity with scheduled vs. completed PM tasks per asset, and a compliance-percentage computation. Grounding explicitly states no such entity exists. **Tier D** — proposed new entities `MaintenancePlan`/`WorkOrder` (asset FK, scheduled_date, status, type=PM/corrective) with PM Compliance derived as completed-on-time PM work orders ÷ total scheduled PM work orders in a period, and "Overdue WO" derived as open work orders past their due date (same derived-state pattern as `RecommendedAction` overdue logic elsewhere).

**Behavioral logic implied:**
- Selecting a Process step (as in mockup-02) should, when the PM-FMEA tab is active, additionally refresh the new "Linked Asset for Step 30" and "Maintenance Status" sections — meaning the Engineering Context panel's content is not just tab-scoped but also FMEA-type-scoped (different bottom sections shown depending on whether DFMEA/PFMEA/System/PM-FMEA is the active top-level tab).
- The donut chart's "Not Analyzed 12 (10%)" segment implies assets can exist without any risk analysis performed yet — a distinct state from Low/Medium/High that would need its own detection logic (e.g., asset has zero linked FailureMode/RiskEvaluation rows) once the underlying Asset/maintenance-risk model is built.
- "PM Compliance" and "Overdue WO" are clearly derived/computed values (percentages, counts against due dates) rather than stored fields — consistent with how `RecommendedAction` overdue-ness is derived elsewhere in this spec set, and should follow the same "compute at read time, don't store" pattern once the backing entities exist.
- "Baseline"/"History" sub-tabs imply a save-a-version / compare-versions workflow with its own creation trigger (manual "create baseline" action, presumably) and read-only historical views — a distinct CRUD/workflow shape from the rest of the app's live-editable worksheets.

**Tier summary:** Tier A — FMEA Team roster, Scope & Configuration basic fields, Characteristics Flow diagram's first two/three boxes (Product/Process Characteristics, PFMEA fan-out), Right-panel Process step list and Process Characteristics table (same as mockup-02), Recent Projects/Activity scaffolding. Tier B — combined FMEA-type badges per project (once PM-FMEA type exists), Links (Open-EQMS) for real FK chains, Top High Risk Items RPN computation (by analogy, once PM-FMEA rows are modeled). Tier C — none distinctly new beyond mockup-01/02's carryovers. Tier D — the entire "Preventive FMEA (PM-FMEA)" concept and `fmea_type` value, Baseline/History versioning, Reviews, Assets Covered donut and all asset/maintenance-risk data, PM-FMEA Validation Trajectory, Top High Risk Maintenance Items' Asset/Machine join, "Linked Asset for Step 30", "Maintenance Status" (PM Compliance/Overdue WO/Next PM), Maintenance Tasks/Plans box in the flow diagram.

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 04 — Consolidated Home (source: mockup-04-consolidated-home.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Header**: logo lockup, hamburger, title "Home", project selector "Project: New Headlamp X1", search "Search (Ctrl+K)", bell badge "8", "?" help icon, avatar "JD".

**Left sidebar**, grouped (most groups now expanded/collapsed with external-link icons on several context items):
- "FMEA WORKSPACE": Home (active), FMEA Projects, FMEA Team.
- "CONTEXT (from Open-EQMS)": collapsible "System / Product / Process", System Characteristics, Characteristics Flow, Process Flow, Process Characteristics.
- "FMEA ANALYSIS": DFMEA, PFMEA, System FMEA, "**Preventive FMEA (PM-FMEA)**" with a yellow-outlined "NEW" badge, Functions, Failure Modes, Causes, Prevention Controls, Detection Controls, Actions.
- "VALIDATION & CHANGE": Validation Trajectory, Evidence & Tests, Change Impact.
- "LINKED EQMS": Control Plans, SPC / ITRA-DT, CAPA, Documents & Links.
- "**OPERATIONS**" (new group, each item has an external-link icon): Process Planning, Production Execution, Work Tracking, Traceability.
- "**MAINTENANCE**" (new group, each item has an external-link icon): Assets & Equipment, Maintenance Plans, Preventive Maintenance, Preventive FMEA (PM-FMEA), Maintenance Work Orders.
- Divider, Settings, Collapse.

**Page header**: "Welcome back, Janez!" / "Here's what's happening across engineering, quality, operations and maintenance." Button row: "+ New FMEA", "Open Project", "Import", "Reports" (chevron), "Templates" (chevron), "AI Assistant".

**Row of 6 stat cards** (one more than prior mockups):
1. FMEA Projects — 12 — "Active projects" — "View all projects →"
2. Active Analyses — 7 — "In progress" — "View all analyses →"
3. High Risk Items — 23 — "5 new since last review" — "View high risks →"
4. Actions Overdue — 8 — "2 critical • 6 normal" — "Go to actions →"
5. Reviews Due — 4 — "Next within 7 days" — "View reviews →"
6. **Unlinked Items — 5 — "Need attention" — "View details →"** (new card, chain/link icon)

**3-column analytics row**:
- "Risk Overview (All Projects)": 5×5 Severity×Occurrence grid, values:
  - Occurrence 5: 0, 1, 3, 7, 5
  - Occurrence 4: 1, 2, 5, 6, 2
  - Occurrence 3: 2, 3, 6, 3, 1
  - Occurrence 2: 0, 1, 2, 1, 0
  - Occurrence 1: 0, 0, 1, 0, 0
  - Legend: green "Low (1-2)", yellow "Medium (3-6)", orange "High (7-12)", red "Very High (13-25)". Link "Open Risk Matrix →".
- "Validation Trajectory (DFMEA + PFMEA + PM-FMEA)": 7-node stepper: Concept (green check), Design (green check), Prototype (green check), "DV / Design Verification" (blue open circle), "PV / Process Validation" (yellow open circle), Operation (gray open circle), Monitor (gray open circle). Below: "DFMEA Validation Coverage" bar 78% (green); "PFMEA Validation Coverage" bar 62% (blue); "PM-FMEA (Maintenance) Coverage" bar **54%** (purple). Legend: Completed/In Progress/Planned/Overdue/Not Started. Link "Open Validation Trajectory →".
- "Top High Risk Items", link "View all →": table columns **Item | Type | Project | RPN | Risk**. Rows:
  - FM-021 Beam distortion | DFMEA | Headlamp X1 | 210 | High (red)
  - FM-034 LED overheating | DFMEA | Headlamp X1 | 192 | High (red)
  - FM-067 Water ingress | PFMEA | Headlamp X1 | 168 | High (red)
  - PM-021 Spindle bearing wear | PM-FMEA | Headlamp X1 | 210 | High (red)
  - PM-034 Hydraulic leak | PM-FMEA | Headlamp X1 | 192 | High (red)
  - Link "Go to High Risk Items →". (Note: this table now interleaves DFMEA/PFMEA "FM-" items with PM-FMEA "PM-" items in one ranked list.)

**Middle row (4 cards)**:
- "Engineering Context Summary", link "Open Engineering Context →": a 2×3 grid of 6 mini-stat tiles, each with an icon, label, and bold value:
  - Product Characteristics — **84**
  - Process Characteristics — **37**
  - Process Steps / Operations — **22**
  - Machines / Assets — **16**
  - Control Plans — **22**
  - Characteristics without Links — **5** (warning-triangle icon, amber)
- "Preventive FMEA (PM-FMEA)" card, subtitle "Maintenance Risk Overview": a donut chart, center text large **"124"** with a smaller sub-line beneath it that is rendered too small/blurred to read reliably at this resolution (by analogy to mockup-03's identical-looking donut, it is likely "of 156" but this is not confirmed legible here — flagging rather than asserting it). Legend: green "Low Risk" dot, yellow "Medium Risk" dot, red "High Risk" dot, gray "Not Analyzed" dot (the percentage/count values beside each legend label are present in mockup-03's equivalent card at 68 (55%)/34 (27%)/16 (13%)/12 (10%) but are cut off/not fully visible in this crop of mockup-04). Link "Open PM-FMEA →".
- "Operations & Maintenance Status": 
  - "Production (Today)" row of 3 mini-cards: "Orders 12", "In Progress 7", "Completed 5" (each with an icon).
  - "Maintenance (Today)" row of 3 mini-cards: "PM Due 8", "In Progress 4", "Overdue 3" (each with an icon, Overdue in red).
  - Link "Open Operations Dashboard →".
- "Recent Activity", link "View all →": rows (icons + text + sub-label + timestamp), partially legible:
  - "D... [Design change] ... linked to FM-021" — 1h ago
  - "M... [Maintenance risk] PM-021 ... updated" / "CNC-01" — 2h ago
  - "P... [PV plan] created for Injection Moulding" — 4h ago
  - "A... [Action A-117] completed" / "Press-02" — 5h ago
  - "F... [FMEA review] completed" / "Headlamp..." — 1d ago

**Right-hand "Engineering Context (Open-EQMS)" panel** (with close "X"):
- Tab row: System, Product, "Process" (active), Characteristics.
- "Process Flow" header, link "Open in Process Planning ↗". Dropdown "Headlamp Assembly Process". Numbered step list: 10 Incoming Material, 20 Sub-Assembly, **30 Injection Moulding** (selected, highlighted, arrow), 40 Post-Processing, 50 Inspection, 60 Packaging.
- "Process Characteristics (Step 30)" table (Characteristic | Target/Spec | Unit): Injection pressure 820±20 bar; Melt temperature 285±5 °C; Holding pressure 600±20 bar; Cooling time 18±2 s; Mould temperature 90±3 °C. Link "View all process characteristics →".
- "Linked Product Characteristics (affected)" table (Characteristic | Type | Criticality): Lens geometry / Safety / "Critical" (red); Optical transparency / Optical / "Critical" (red); Surface quality / Decorative / "High" (amber). Link "View all product characteristics →".

**Bottom-of-page 6-column band** (a distinct final row, condensed mini-cards spanning full width):
- "Project Health (Summary)": a circular gauge/donut labeled "Overall Health" **78%**, with sub-label "Good" (green).
- "Risk Trend (vs last 30 days)": a small multi-line chart, y-axis categories "High / Medium / Low" (as labeled band lines, not numeric), x-axis "-30d / -20d / -10d / Today"; three colored line series — red (High), amber/yellow (Medium), green (Low) — each with plotted point markers, red line trending down and green line trending up toward "Today".
- "Actions" mini-panel: "Total 56", "Overdue 8" (red), "Due Soon 12" (amber).
- "Coverage" mini-panel: three labeled horizontal bars — "DFMEA" 78% (green), "PFMEA" 62% (blue), "PM-FMEA" 54% (purple).
- "Links (Data Integrity)" mini-panel: "Linked Items 92%" (green), "Unlinked Items 5" (green-ish/neutral), "Broken Links 3" (red).
- "Next Reviews" mini-panel: "DFMEA Review — 12 May 2025" (blue), "PFMEA Review — 15 May 2025" (blue), "PM-FMEA Review — 18 May 2025" (blue).

**Footer status bar**: Database: OpenEQMS_Local, User: Janez Demo (Quality Engineer), Role: Project Owner, Workspace: Global, Version 1.0.0, Notifications 8, System Status dot.

### 2. Wireframe & UI/UX

- This is the densest, most "everything at once" variant of the Home dashboard: it layers the mockup-02/03 Engineering-Context-panel pattern with a *fourth* content row not seen in earlier mockups (the full-width "Project Health (Summary)" band at the very bottom), and adds a sixth stat card and a sixth sidebar group ("OPERATIONS") plus a seventh ("MAINTENANCE") beyond what mockup-03 showed.
- Structurally it is: header → 6-up stat cards → 3-column analytics row (Risk Overview / Validation Trajectory / Top High Risk Items) → 3-column "context & ops" row (Engineering Context Summary / PM-FMEA donut / Operations & Maintenance Status) plus a 4th column-equivalent "Recent Activity" card → bottom full-width 6-panel "Project Health" strip — all to the left of a persistently docked right-hand Engineering Context panel.
- Visual hierarchy reuses the same conventions as mockups 1–3 (bold large numerals on stat cards, red/amber/green/gray semantic coloring throughout), but introduces two new chart types not seen before: a circular "Overall Health" gauge (78%, "Good") and a small multi-series line chart ("Risk Trend") plotting risk-tier counts over a trailing 30-day window — both are new visualization affordances beyond the bar/donut/matrix/stepper types used elsewhere.
- The sidebar's "OPERATIONS" and "MAINTENANCE" groups have every single item marked with an external-link icon, visually signaling (consistent with "Process Flow"/"Process Characteristics" in earlier mockups) that these are deep-links out to separate Open-EQMS modules rather than pages native to this FMEA app.
- Implied interactions: same drill-down/master-detail pattern in the right panel as mockups 2–3; the "Engineering Context Summary" tiles and "Operations & Maintenance Status" mini-cards are presumably each clickable through to their respective source lists/modules; the Risk Trend line chart likely supports hover-for-value tooltips at each plotted point (implied by the visible point markers) though no tooltip is shown open in this static mockup.

### 3. Architecture & Data Logic — what this should do and how it should behave

- **6th stat card "Unlinked Items" (5, "Need attention")**: implies a query across characteristic/requirement/failure-mode chains for records missing an expected relationship (e.g. `ProductCharacteristic` with no `requirement`, or `Requirement` with no linked `ProductCharacteristic`, or `FailureMode` with neither `function` nor `requirement` set — all of these FKs are nullable per the grounding). **Tier B** — real nullable FK fields exist to query against (`ProductCharacteristic.requirement`, `FailureMode.function`, `FailureMode.requirement`, `ProcessCharacteristic.cause_category_id`, etc.), but "unlinked" as a single cross-model aggregate count needs new query logic defining exactly which relationships count toward it (not specified — treat the precise rule as **proposed**).
- **Risk Overview matrix, Top High Risk Items, stat cards 1–5**: same as mockups 1–3 — **Tier A** (FMEA Projects/Active Analyses counts) / **Tier B** (High Risk Items latest-evaluation aggregation, Actions Overdue query, matrix grouping, top-risk table join) / **Tier D** (Reviews Due, "5 new since last review" delta, critical/normal split). New here: the Top High Risk Items table interleaves "FM-" and "PM-" coded rows into one ranked list — this presumes a unified query across both real `FailureMode` rows and not-yet-existing PM-FMEA rows; the DFMEA/PFMEA half is **Tier B**, the PM-FMEA half is **Tier D** (blocked on mockup-03's PM-FMEA entity gap), and the *merge/rank-together* logic itself is **Tier D** until PM-FMEA exists as real data.
- **Validation Trajectory (DFMEA + PFMEA + PM-FMEA) with 3 coverage bars**: same **Tier D** status as mockups 1–3 for the stage-tracking stepper (no lifecycle-phase entity); the DFMEA/PFMEA coverage % are **Tier B** (approximable via new aggregation, per mockup-01's note); the PM-FMEA coverage % is **Tier D** (depends on the not-yet-existing PM-FMEA/Asset data).
- **Engineering Context Summary tiles**:
  - "Product Characteristics 84" → `ProductCharacteristic.objects.count()` (scoped to the current project/FMEA's products). Real field/model. **Tier A/B** (simple count, needs project-scoping join through `ProductCharacteristic.requirement → Requirement.function → Function.product → Product.fmea → FMEA.project`).
  - "Process Characteristics 37" → `ProcessCharacteristic.objects.count()`, scoped similarly through `Operation.process → Process.fmea`. **Tier A/B**, same pattern.
  - "Process Steps / Operations 22" → `Operation.objects.count()`, scoped through `Process.fmea`. **Tier A/B**.
  - "Machines / Assets 16" → no `Asset`/`Machine` model exists. **Tier D**.
  - "Control Plans 22" → no Control Plan entity exists in this codebase (referenced elsewhere only as an external "Open-EQMS" box). **Tier D**.
  - "Characteristics without Links 5" → same class of query as the "Unlinked Items" stat card above. **Tier B** (proposed rule needed).
- **"Preventive FMEA (PM-FMEA)" donut card (Maintenance Risk Overview)**: identical widget to mockup-03's "Preventive FMEA Overview" donut. **Tier D** in full — no Asset/maintenance-risk backing data (see mockup-03 Section 3 for the detailed breakdown).
- **"Operations & Maintenance Status" (Production: Orders/In Progress/Completed; Maintenance: PM Due/In Progress/Overdue)**: implies both a production-order entity (Operations module) and a work-order entity (Maintenance module) with status fields, entirely outside this grounded model (no `Asset`/`WorkOrder`/`Resource`/`Equipment` entity exists; no production-order entity exists either). **Tier D** in full — this card's data would come from separate Open-EQMS modules (Operations, Maintenance) this FMEA app does not own; if this dashboard is meant to embed their data, that requires a cross-module integration/API contract that is itself a new architecture decision, not merely a new local model.
- **Recent Activity card**: same as mockups 1–3 — **Tier D** for a generic cross-entity activity log (only `RiskEvaluation.actor`/`trigger` offer a narrow **Tier B/A** slice); the "Maintenance risk PM-021 updated" and "PV plan created for Injection Moulding" rows additionally depend on the not-yet-existing PM-FMEA data (**Tier D**).
- **Right-hand Engineering Context panel (Process tab, step list, Process/Product Characteristics tables)**: identical to mockup-02's panel — **Tier A** for the step list and characteristic names, **Tier B** for Target/Spec/Unit extraction from `ProcessCharacteristic.attributes` JSON, **Tier C** for "Criticality" pill (only `ProductCharacteristic.is_special` boolean exists), **Tier D** for "Type" field on ProductCharacteristic and for the Product↔Process "affected" linkage query (see mockup-02 Section 3 for full detail — not re-derived here).
- **Bottom "Project Health (Summary)" band**:
  - "Overall Health 78% / Good" gauge — a single composite health score with no defined formula anywhere in the grounding. **Tier D** — would need a new computed metric (proposed: a weighted blend of validation coverage %, % actions on-time, % high-risk items trending down, etc.) whose exact weighting is an open architecture decision, not inferable from the mockup alone.
  - "Risk Trend (vs last 30 days)" line chart — requires a time-series of risk-tier counts sampled daily (or similar) over a rolling window. No historical/snapshot model of risk counts exists (same gap noted for the "5 new since last review" delta in mockup-01). **Tier D** — would need a new time-series entity, proposed `RiskSnapshot` (date, project/fmea scope, low_count, medium_count, high_count), populated by a scheduled job, OR a live recomputation strategy if evaluations' own `evaluated_at` timestamps are replayed historically (possible in principle since `RiskEvaluation.evaluated_at` is real, but doing so as a live "count of records whose *latest-as-of-date-X* evaluation was in each tier" is materially more complex than a simple query — still **Tier D** as a feature, though the raw timestamp data to eventually support it does exist).
  - "Actions" mini-panel (Total 56 / Overdue 8 / Due Soon 12) — "Total" and "Overdue" are the same **Tier A/Tier B** aggregations described in mockup-01 (`RecommendedAction.objects.count()`; overdue via `due_date`/`status` filter). "Due Soon" (implying a near-future due_date window, e.g. next 7 days) is the same query shape — **Tier B**.
  - "Coverage" mini-panel (DFMEA/PFMEA/PM-FMEA bars) — same tiering as the Validation Trajectory coverage bars above (**Tier B** for DFMEA/PFMEA, **Tier D** for PM-FMEA).
  - "Links (Data Integrity)" mini-panel (Linked Items 92%, Unlinked Items 5, Broken Links 3) — "Unlinked Items" ties to the same query discussed above (**Tier B**, proposed rule). "Linked Items %" is the complement of that same query (**Tier B**). "Broken Links" implies detecting *dangling* or inconsistent references (e.g., a `RecommendedAction.failure_cause` pointing to a cause whose parent `FailureMode` no longer matches context, or orphaned rows after a nullable FK's target was deleted under `SET_NULL`) — this is a data-integrity check with no defined rule in the grounding. **Tier D** (proposed: a scheduled integrity-check job flagging specific inconsistency patterns, rules TBD).
  - "Next Reviews" mini-panel — same **Tier D** as "Reviews Due" stat card; no review-scheduling entity exists, now also implying reviews would need to be scoped per-FMEA-type (DFMEA Review/PFMEA Review/PM-FMEA Review), reinforcing the proposed `FMEAReview` entity would need an `fmea` FK to scope correctly.

**Behavioral logic implied:**
- This mockup is explicitly a superset/rollup of mockups 1–3, implying the Home dashboard is meant to be *composable*: as more Open-EQMS modules (Operations, Maintenance) and more FMEA types (PM-FMEA) come online, additional cards/sidebar groups appear on the same page — meaning the underlying dashboard view/API should be designed to tolerate partial data (some modules/entities not yet present) without breaking, since several of its cards currently have zero backing data.
- The "Unlinked Items"/"Characteristics without Links"/"Broken Links" trio implies a recurring, possibly scheduled, data-integrity/completeness check spanning multiple entities — this is materially different from the rest of the dashboard's "count/aggregate existing rows" pattern and deserves its own dedicated query/service layer if pursued, rather than being bolted onto per-page view logic.
- "Project Health" as a single 78% score implies a defined, presumably configurable, scoring formula that rolls up multiple sub-metrics — this should be treated as a distinct architecture decision (what inputs, what weights, recomputed how often) before any implementation, not merely a display concern.

**Tier summary:** Tier A — FMEA Projects/Active Analyses counts, Engineering Context Summary base counts for Product/Process Characteristics and Process Steps (pending project-scoping join), right-panel Process step list and characteristic name columns. Tier B — High Risk Items/Actions Overdue/Risk Matrix/Top-High-Risk-Items aggregations (DFMEA/PFMEA portion), DFMEA/PFMEA validation coverage %, Unlinked Items / Characteristics-without-Links / Linked-Items% queries (rule TBD), Actions Total/Overdue/Due-Soon, Target/Spec/Unit extraction from JSON attributes. Tier C — ProductCharacteristic "Criticality" pill, ProjectMembership.role as enforced role (carried over). Tier D — the entire PM-FMEA slice everywhere it appears (donut, coverage bar, trajectory stages, Top-High-Risk-Items PM- rows, Recent Activity PM rows), Machines/Assets count, Control Plans count, Operations & Maintenance Status card in full, Overall Health gauge, Risk Trend time-series chart, Broken Links integrity check, Next Reviews / Reviews Due, "5 new since last review" delta, generic Recent Activity log, ProductCharacteristic "Type" field, Product↔Process characteristic linkage query.

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 05 — FMEA Projects List (source: mockup-05-fmea-projects-list.png)

### 1. GUI Contents / Widgets (exhaustive list)

Note: the source image is a short horizontal strip (1132×228px, i.e. it is cropped to only the top portion of the page — no footer status bar or lower content is visible/available in this asset).

**Header**: logo lockup "Open FMEA" / "Open-EQMS Family"; hamburger icon; page title "**FMEA Projects**"; subtitle "Manage all projects and their analyses."; project selector "Project: New Headlamp X1" (chevron); search box "Search (Ctrl+K)"; bell icon with red badge "8"; "?" help icon; avatar "JD".

**Left sidebar** (partial, top of list visible):
- "FMEA WORKSPACE": Home, "**FMEA Projects**" (active/highlighted, blue), FMEA Team.
- "CONTEXT (from Open-EQMS)": collapsible "System / Product / Process" (expanded) with sub-items: System Characteristics Base, Characteristics Flow / Diagram, Process Flow, Process Characteristics. (List is cut off below this point by the image crop; further groups are not visible in this asset.)

**Action button row** (top right of content area): "+ New Project" (solid blue/primary), "Import" (outline, icon), "Reports" (outline, dropdown chevron), "Templates" (outline, dropdown chevron), "Filters" (outline, filter icon).

**Row of 5 stat/summary cards**:
1. Folder icon (blue). "Total Projects". Value **12**. Caption "Active FMEA projects".
2. Icon (blue, document/shield). "DFMEA". Value **4**. Caption "Design FMEA projects".
3. Icon (green, cycle/process). "PFMEA". Value **5**. Caption "Process FMEA projects".
4. Icon (purple, network/nodes). "System FMEA". Value **2**. Caption "System level FMEA".
5. Icon (orange, grid). "PM-FMEA". Value **1**. Caption "Preventive FMEA projects".

**Projects table**, columns: **Project Name | Project Code | FMEA Type | Related Product / Process | Owner | Status | Progress | Last Updated | Actions**.
Rows (4 visible):
1. "New Headlamp X1 - DFMEA" | DFMEA-001 | pill "DFMEA" (blue) | Headlamp X1 | avatar "JD" Janez Demo | pill "In Progress" (blue) | progress bar 68% with "68%" label | "12 May 2025 10:30" | action icons (external-link, pencil/edit, "..." overflow menu)
2. "Injection Moulding Process - PFMEA" | PFMEA-002 | pill "PFMEA" (green) | Injection Moulding Process | avatar "MK" (green) Marko Kovac | pill "In Progress" (blue) | progress bar 74% with "74%" label | "11 May 2025 15:45" | action icons
3. "Headlamp X1 - System FMEA" | SYSFMEA-001 | pill "System FMEA" (purple) | Headlamp X1 System | avatar "AN" (orange) Ana Novak | pill "Review" (lighter blue/lavender) | progress bar 52% with "52%" label | "10 May 2025 09:20" | action icons
4. "CNC Machine Preventive FMEA" | PMFMEA-001 | pill "PM-FMEA" (orange) | CNC-01 Milling Machine | avatar "PT" (purple) Peter Turk | pill "In Progress" (blue) | progress bar 41% with "41%" label | "09 May 2025 14:10" | action icons

### 2. Wireframe & UI/UX

- Standard app-shell layout consistent with mockups 1–4: dark left sidebar, light main content area, top bar. Only the top slice of the page is captured in this image (stat cards + start of the table), so no pagination control, empty state, or footer bar can be confirmed from this asset — their presence/absence should not be assumed either way.
- Main content structure, top to bottom: page title + subtitle → right-aligned primary/secondary action buttons → a 5-up row of summary stat cards (mirroring the FMEA-type breakdown) → a data table listing every FMEA project as one row per analysis.
- Visual hierarchy: the 5 stat cards each pair a colored icon with a bold count, functioning as both a summary and (implicitly) a set of filter shortcuts for the table below (clicking "PFMEA" would plausibly filter the table's FMEA Type column to PFMEA). The table itself is the primary content, dense and information-rich, with a right-aligned in-row "Progress" bar giving an at-a-glance completion visual per row alongside its numeric percentage.
- Color coding: FMEA Type pills are each assigned a distinct color (DFMEA=blue, PFMEA=green, System FMEA=purple, PM-FMEA=orange), consistently reused from the icon color on the matching stat card above. Status pills use blue for "In Progress" and a lighter blue/lavender for "Review" (no "Draft"/red/gray status appears among these 4 rows, though other mockups establish "Draft"=gray and similar statuses exist elsewhere in the app). Owner avatars are colored circular initials, one distinct flat color per person, consistent with the same people/colors seen in mockups 2–3's "FMEA Team" card (Janez=purple/blue, Marko=green, Ana=orange), except Peter Turk appears with a purple avatar here versus a blue avatar in the FMEA Team card — a minor inconsistency worth flagging literally rather than reconciling.
- Implied interactions: each row is very likely clickable through to that FMEA's own workspace (consistent with mockups 2/3's "FMEA Workspace – New Headlamp X1" breadcrumb destination). The trailing action icons per row (external-link/open, pencil/edit, "..." overflow) imply at least three per-row actions: open, edit, and a menu (likely containing duplicate/archive/delete or similar, not enumerated in the mockup). "Filters" as a button (rather than inline column filters) implies a filter panel/drawer pattern, not shown open here. Column headers are plain text with no visible sort-arrow glyphs, so sortability cannot be confirmed from this image — flagging rather than assuming.

### 3. Architecture & Data Logic — what this should do and how it should behave

- **Stat card 1 — Total Projects (12, "Active FMEA projects")**: `FMEAProject.objects.filter(status=<active>).count()`. Real field `FMEAProject.status`. **Tier A.**
- **Stat cards 2–5 — DFMEA (4) / PFMEA (5) / System FMEA (2) / PM-FMEA (1)**: a breakdown of `FMEA` rows grouped by `FMEA.fmea_type`. For DFMEA/PFMEA/System, this is a real field and a simple `.values("fmea_type").annotate(Count(...))`-style grouping — **Tier A/B** (real field, needs a small grouping query, effectively trivial). For **PM-FMEA specifically, `fmea_type` has no "preventive" choice in the grounded model** (confirmed choices: design/process/product/software/system) — the PM-FMEA count card is **Tier D**, blocked on the same fmea_type gap identified in mockup-03.
- **Projects table — Project Name, Project Code, FMEA Type, Owner, Status, Last Updated columns**: map respectively to `FMEA.name` (or `FMEAProject.name`, ambiguous which — see below), `FMEAProject.project_code` (the grounding only lists `project_code` on `FMEAProject`, not on `FMEA`; if each table row represents one `FMEA` rather than one `FMEAProject`, then "Project Code" as shown per-FMEA-row is **Tier C**, since the real `project_code` field lives one level up on `FMEAProject`, not on the individual `FMEA` — this table structure conflates "project" and "individual FMEA analysis" into one row, which is an important modeling ambiguity to flag rather than resolve unilaterally), `FMEA.fmea_type` (real, **Tier A** for DFMEA/PFMEA/System rows, **Tier D** for the PM-FMEA row), an owner (no explicit "owner" field is listed for `FMEA` or `FMEAProject` in the grounding — the closest real construct is `ProjectMembership` with a `role` label, so an "Owner" column would need either a new field or a convention of reading the `ProjectMembership` row where `role == "Owner"` — **Tier B/C**: derivable from `ProjectMembership` if a convention is adopted, but not a direct field today), `FMEA.lifecycle` for the Status pill (real field/enum, **Tier A**), and a "Last Updated" timestamp (not confirmed as an existing field on `FMEA`/`FMEAProject` per the grounding — **Tier C**, flagged as unconfirmed exactly as in mockup-01).
- **"Related Product / Process" column**: for a DFMEA row this would resolve via `FMEA.products` (reverse of `Product.fmea` FK) — a DFMEA can have multiple related `Product` rows, so showing one name here implies either a single-product convention or a "primary product" concept not defined in the grounding. For a PFMEA row it resolves via `FMEA.processes` (reverse of `Process.fmea` FK), same multiplicity caveat. For the "System FMEA" row ("Headlamp X1 System") there is no `System` model in the grounded schema at all — **Tier D** for that specific row's related-entity link (same gap as mockups 2–4). For the "PM-FMEA" row ("CNC-01 Milling Machine") there is no Asset/Machine entity — **Tier D**, same gap as mockup-03. Overall: **Tier B** for the DFMEA/PFMEA cases (real FK, needs a "pick one related Product/Process to display" convention), **Tier D** for the System FMEA and PM-FMEA cases.
- **"Progress" column (percentage + bar)**: no stored progress/completion percentage field exists on `FMEA` in the grounded model. This would need to be derived — plausible candidates (none confirmed/specified): percentage of `FailureMode`s with at least one `RiskEvaluation`, or percentage of `RecommendedAction`s at `status=verified`, or a weighted blend of worksheet-section completeness (Functions/Requirements entered → Failure Modes entered → Causes/Effects entered → Controls entered → Risk Evaluated → Actions closed). **Tier B** at best if a specific, simple formula is chosen (e.g. "% of FailureModes with ≥1 RiskEvaluation"), but as shown (a single unexplained completion percentage) it is closer to **Tier D**, since no such formula or field is defined anywhere in the grounding — flagging as **proposed, needs an explicit formula decision** rather than assuming one.
- **Row action icons (open/edit/overflow menu "...")**: "open" and "edit" are standard CRUD navigation into an existing `FMEA`/`FMEAProject` record — **Tier A** (no new backend needed beyond existing update views). The "..." overflow menu's contents are not shown/enumerable from this mockup; whatever it contains (e.g. duplicate, archive, delete, export) would need to be scoped separately per action — not tiered here since the actions themselves aren't visible.
- **"+ New Project" button**: creates a new `FMEAProject` (and/or a new `FMEA` under one, depending on how "Project" vs. "FMEA" scoping is resolved architecturally — see the Project Code ambiguity above). **Tier A** for a basic create form against `FMEAProject.name`/`project_code`/`status`/`description`.
- **"Import" / "Reports" / "Templates" / "Filters" buttons**: "Import" implies a bulk-ingestion flow — the grounding does reference a real, already-scoped local-AI XLSX ingestion capability elsewhere in this project's architecture docs (outside this mockup's own grounding list), so this is plausibly **Tier A/B** depending on which ingestion path is intended, but cannot be confirmed as wired into this specific screen from the mockup alone. "Reports" and "Templates" as dropdowns imply generated-report/document-template features with no backing entity described in the grounding — **Tier D** (no report-generation or template-library entity exists). "Filters" implies filtering the table by columns shown (Type, Status, Owner) — all real fields once the ambiguities above are resolved, so **Tier B** (needs new filter/query UI, no new modeling).

**Behavioral logic implied:**
- The FMEA Type pill and stat-card counts imply a straightforward, already-real classification (`FMEA.fmea_type`) driving both a global summary and per-row display — except that the mockup shows a 5th type ("PM-FMEA") that does not exist in the enum, meaning any implementation of this exact screen must either extend `fmea_type` or explicitly exclude/stub the PM-FMEA row and card until that type is approved.
- Status pills ("In Progress"/"Review") imply the same `FMEALifecycle` state-machine referenced in mockups 1–4; this table would need to reflect lifecycle transitions live (e.g., editing the worksheet and marking it complete should move a row from "In Progress" to "Review" without a page reload elsewhere breaking sync) — transition rules themselves are not specified in the grounding and should be scoped separately.
- "Last Updated" sorting/display (if the column is meant to reflect true recency) depends on the same unconfirmed timestamp-field question raised in mockup-01 — this should be resolved (confirm or add `updated_at` on `FMEA`/`FMEAProject`) before this column can be considered fully backed.
- The Project Code / Project Name / FMEA Type combination per row, one row per individual analysis rather than one row per `FMEAProject`, suggests the intended information architecture for this screen is "list of FMEA analyses" (rows = `FMEA` instances) with `FMEAProject` context folded in as a label — this is a reasonable reading of the real schema (`FMEA.project` FK, multiple `FMEA`s per `FMEAProject`) but is worth confirming explicitly before building, since the page title itself says "FMEA Projects" (suggesting rows = `FMEAProject`) while the columns (FMEA Type, per-row Progress) suggest rows = `FMEA`. This naming/grain ambiguity is flagged, not resolved, here.

**Tier summary:** Tier A — Total Projects count, DFMEA/PFMEA/System FMEA stat-card counts, FMEA Type pill and Status pill for DFMEA/PFMEA/System rows, row open/edit actions, "+ New Project" basic create flow. Tier B — Owner column (derivable from ProjectMembership with a convention), Related Product/Process column for DFMEA/PFMEA rows (real FK, needs a "primary" convention), Filters functionality, Progress % (if a specific simple formula is adopted). Tier C — Project Code shown per-FMEA-row (real field lives on FMEAProject, not FMEA — grain mismatch), Last Updated timestamp (unconfirmed field). Tier D — PM-FMEA stat card and row entirely (fmea_type gap), System FMEA's and PM-FMEA's "Related Product/Process" targets (no System or Asset entity), Progress % as an unexplained single number (no defined formula), Reports/Templates features (no backing entity).

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 06 — FMEA Team (source: mockup-06-fmea-team.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Header bar**
- Logo lockup: "Open FMEA" wordmark with a multicolor pinwheel/X icon, subtitle "Open-EQMS Family"
- Hamburger/menu icon (sidebar collapse toggle)
- Page title: "FMEA Team"
- Page subtitle: "Manage team members, roles and permissions."
- Top-right: "Project: New Headlamp X1" dropdown selector
- Search box: "Search (Ctrl+K)" placeholder with magnifier icon
- Notification bell icon with a red badge dot (unread count not numbered, just a dot)
- Help/question-mark icon (circle)
- User avatar: circular "JD" initials badge (purple)

**Left sidebar navigation**
- Section header "FMEA WORKSPACE": items "Home", "FMEA Projects", "FMEA Team" (this item highlighted/active with solid blue background)
- Section header "CONTEXT (from Open-EQMS)": item "System / Product / Process" (with a chevron indicating it expands/collapses), and four indented sub-items: "System Characteristics Base", "Characteristics Flow / Diagram", "Process Flow", "Process Characteristics"

**Stat/KPI cards row (4 cards)**
1. Icon (two-person/blue), label "Total Members", value "18", caption "Active users"
2. Icon (shield/blue), label "Administrators", value "3", caption "System administrators"
3. Icon (star/orange), label "FMEA Leaders", value "5", caption "FMEA project leaders"
4. Icon (single person/green), label "Contributors", value "10", caption "Team contributors"

**Action buttons (above table, right-aligned)**
- "+ Add Member" (solid blue button)
- "Roles & Permissions" (outline button, document icon)
- "Export" (outline button, download icon)
- "Filters" (outline button, filter icon)

**Team member table**
- Columns, in order: Name, Email, Role, FMEA Role, Projects, Status, Last Active, Actions
- 5 visible rows:
  1. Avatar "JD" (purple) — Janez Demo — janez.demo@openeqms.local — Quality Engineer — FMEA Role badge "FMEA Leader" (light blue pill) — Projects: 5 — Status badge "Active" (light green pill) — Last Active: 12 May 2025 11:20 — Actions: pencil icon, "…" overflow menu icon
  2. Avatar "MK" (green) — Marko Kovac — marko.kovac@openeqms.local — Process Engineer — FMEA Role badge "Contributor" (light green/teal pill) — Projects: 6 — Status: Active — Last Active: 11 May 2025 09:15 — Actions
  3. Avatar "AN" (orange) — Ana Novak — ana.novak@openeqms.local — Design Engineer — FMEA Role badge "FMEA Leader" (light blue pill) — Projects: 4 — Status: Active — Last Active: 11 May 2025 16:40 — Actions
  4. Avatar "PT" (purple) — Peter Turk — peter.turk@openeqms.local — Maintenance Engineer — FMEA Role badge "PM-FMEA Responsible" (light orange/peach pill) — Projects: 3 — Status: Active — Last Active: 11 May 2025 08:50 — Actions
  5. Avatar "LS" (blue) — Luka Sterle — luka.sterle@openeqms.local — Manufacturing Engineer — FMEA Role badge "Contributor" (light green/teal pill) — Projects: 2 — Status: Active — Last Active: 10 May 2025 14:25 — Actions
- No pagination control is visible in this crop (table may continue beyond the 18 total members implied by the stat card, but no "Showing X of 18" or page controls are shown).

**Right-side "Team Roles" reference panel**
- Heading "Team Roles"
- Five role-definition rows, each with an icon, a bold role name, and a one-line description:
  - Administrator (shield icon, blue) — "Full system access and configuration."
  - FMEA Leader (star/badge icon, blue) — "Lead FMEA projects and approve results."
  - PM-FMEA Responsible (icon, orange) — "Responsible for preventive FMEA and maintenance."
  - Contributor (person icon, green) — "Contribute to FMEA analyses and actions."
  - Viewer (eye icon, gray) — "Read-only access to projects and results."

### 2. Wireframe & UI/UX

**Layout**: Fixed dark-navy left sidebar (full height) + light-gray main content area. Header spans the top of the content area (title/subtitle left, project selector/search/notifications/avatar right). Below the header, a 4-card KPI row spans most of the content width. Below that, a two-column split: a wide data table on the left (~70% width) and a narrower "Team Roles" reference card fixed to the right (~25% width), both starting at the same vertical position as the "Add Member"/action-button row.

**Visual hierarchy**: The 4 KPI cards use large bold numbers as the dominant visual element, with small icon badges (colored, rounded-square backgrounds) to the left of each label — this is the "at a glance" summary tier. The table is the primary/detailed working surface. The right "Team Roles" panel is a static legend/reference, visually quieter (no numbers, just icon + text), explaining what each FMEA Role badge color in the table means.

**Color/status coding**: FMEA Role badges use distinct pastel pill colors per role (blue = FMEA Leader, teal/green = Contributor, peach/orange = PM-FMEA Responsible — matching the icon colors in the Team Roles legend). Status badges use green = Active uniformly (no other status value is shown in this mockup, so it's unclear if Inactive/Pending have distinct colors). Avatar circles are colored per-person (not semantically tied to role) — purple, green, orange, blue — appearing to be a rotating palette for visual distinction rather than a role indicator.

**Typography**: Page title is large/bold; KPI numbers are large/bold (the dominant number on each card); table headers are small-caps-weight gray labels; row text is regular weight with the person's Name in slightly bolder weight than Email/Role columns.

**Interaction patterns implied**: "FMEA Team" sidebar item is a persistent nav link (already active/current page). "Project: New Headlamp X1" dropdown implies the whole Team roster view is scoped per-project (switching projects would presumably reload a different member list/counts). Table rows imply click-through or the pencil icon opens an edit-member drawer/modal; "…" opens a per-row action menu (likely Remove/Change Role/Deactivate). "+ Add Member" implies a modal/drawer to invite or add an existing Open-EQMS user to this project's roster with a role assignment. "Roles & Permissions" button implies a separate settings screen defining what each role can do. "Filters" implies filtering the table by Role/FMEA Role/Status.

### 3. Architecture & Data Logic

- **Total Members / KPI card (18)**: Real, field, not yet exposed as an aggregate. Derivable from real data, needs new query/aggregation logic — `count(ProjectMembership.objects.filter(project=<current project>))`. `ProjectMembership` exists with `project` FK and `user` FK, so a per-project member count is a straightforward COUNT query against an existing table; no new model needed.
- **Administrators / FMEA Leaders / Contributors KPI cards (3 / 5 / 10)**: Derivable from real data, needs new query/aggregation logic — `ProjectMembership.role` is described as "a plain label" (free-text/plain field), so this would be `count(...).filter(role="Administrator")` style grouping, IF the roster is consistently populated with these exact role strings. Genuinely new in the sense that there is no controlled vocabulary/enum for `role` today — nothing enforces that only "Administrator", "FMEA Leader", "PM-FMEA Responsible", "Contributor", "Viewer" are legal values, so this card's counts assume a **proposed** constrained set of role choices that isn't backed by a real choices/enum on `ProjectMembership.role` yet.
- **Name / Email / Role (Job title, e.g. "Quality Engineer") columns**: Real, already built for Name and Role — `ProjectMembership.user` (Django auth user) gives Name; `ProjectMembership.role` gives the "Role" column text ("Quality Engineer" etc., consistent with "a plain label"). Email is Genuinely new / Real field, not yet exposed — Django's built-in User model has an `email` field, so this is likely Real, already built at the framework level, just needs a view/template to surface `user.email`.
- **"FMEA Role" column (FMEA Leader / Contributor / PM-FMEA Responsible pills)**: This is a second, distinct role-like value from the "Role" column (which held a job title like "Quality Engineer"). Genuinely new — no backing entity/field exists for a second, FMEA-specific role dimension per membership. `ProjectMembership` has only one `role` field per the grounding. A proposed model change would need either a second field (e.g. `ProjectMembership.fmea_role`, a choices field) or a distinct concept entirely from the general "Role" (job title) column — needs architecture review to decide whether this is the SAME field as "Role" (mockup just showing it twice, differently styled) or a genuinely separate field, since the mockup displays both a plain-text "Role" and a badge-styled "FMEA Role" side by side for the same row.
- **"Projects" column (count per member)**: Derivable from real data, needs new query/aggregation logic — count of `ProjectMembership` rows for that `user` across all `FMEAProject`s (or count of `FMEA`s the user's `team` JSONField lists them in — ambiguous which relationship, see below), grouped by user.
- **"Status" column (Active)**: Genuinely new — no `status`/active-flag field is described on `ProjectMembership` or on the Django user beyond the built-in `is_active` boolean. If reusing Django's `User.is_active`, this would be Real field, not yet exposed in GUI; but the mockup implies a richer state, potentially with more values than just Active (e.g. Pending/Deactivated), which is not confirmed to exist — treat as proposed until confirmed.
- **"Last Active" column (timestamps)**: Genuinely new — no last-login/last-activity tracking field is described on `ProjectMembership`. Django's built-in `User.last_login` could partially back this (Real field, not yet exposed) but "Last Active" implies more granular activity tracking (any action, not just login) which would need new instrumentation — proposed.
- **Row Actions (pencil / "…")**: Genuinely new UI behavior — edit-membership and per-row action menu (e.g., change role, remove from project) would be CRUD operations against `ProjectMembership`. Since the grounding states "No login/permission enforcement tied to this — it's a roster only," any "role" changes made here today would NOT actually gate access to anything in the app; this is purely descriptive/roster data, not an enforced permission system, despite the "Roles & Permissions" button implying otherwise.
- **"+ Add Member" button**: Derivable/buildable on real data — creates a new `ProjectMembership` row (project, user, role). Proposed CRUD flow: search/select an existing Open-EQMS user, assign a `role` (and possibly the new `fmea_role` field discussed above), save. Needs validation that (user, project) is unique to avoid duplicate memberships (no uniqueness constraint is confirmed to exist on `ProjectMembership` today).
- **"Roles & Permissions" button and the "Team Roles" reference panel (Administrator/FMEA Leader/PM-FMEA Responsible/Contributor/Viewer with descriptions)**: Genuinely new — no permission/role-capability model exists anywhere in the codebase per the grounding ("no real user-role/permission system... Django auth installed but barely used"). This entire panel and button describe a proposed RBAC (role-based access control) system: a fixed catalog of role names, each mapped to a description of what it can do, and (implied but not shown) actual enforcement logic gating create/edit/approve/view actions by role. This is the single largest gap on this page — scoping it would require: a `Role` catalog (name, description, capability set), enforcement middleware/permission checks throughout every FMEA CRUD view, and a UI to manage it (this button). None of that exists today.
- **"Export" button**: Genuinely new — no export mechanism is described for `ProjectMembership`/team rosters; would need a proposed CSV/XLSX export view over the same query as the table.
- **"Filters" button**: Derivable from real data, needs new query/aggregation logic — filtering the existing table query by `role`/status/etc.; straightforward once the underlying fields above are settled, but the filter UI itself doesn't exist yet.
- **Cross-entity relationship implied**: This page is explicitly scoped "Project: New Headlamp X1" — i.e., the team roster is per-`FMEAProject`, consistent with `ProjectMembership.project` FK. No relationship to a specific `FMEA` (as opposed to `FMEAProject`) is implied on this page.

**Tier summary:** Tier A — Name (via `ProjectMembership.user`), job-title "Role" (`ProjectMembership.role`), and Total Members count (COUNT over `ProjectMembership`) are real and just need display/query wiring. Tier B — Administrators/FMEA Leaders/Contributors breakdown counts, per-user Projects count, and table Filters need new query/aggregation logic layered on existing `ProjectMembership`/`User` data. Tier C — Email (framework field, not yet surfaced) is a real field far short of nothing but simply needs a template change. Tier D — the distinct "FMEA Role" badge dimension (if not the same field as "Role"), Status, Last Active, the "Roles & Permissions" RBAC system and its enforcement, and Export are all genuinely new, with no backing entity/field/enforcement mechanism in the current model.

### 4. Explicit non-authorization note
This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 07 — System / Product / Process (source: mockup-07-system-product-process.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Header bar**
- "Open FMEA" / "Open-EQMS Family" logo lockup, hamburger icon
- Page title: "System / Product / Process"
- Subtitle: "Define and manage systems, products and processes from Open-EQMS."
- Top-right action buttons: "+ New System" (solid blue), "Import" (outline, icon), "Export" (outline, icon), "Filters" (outline, icon)

**Tab strip**
- Three tabs: "Systems" (active/underlined, blue text), "Products", "Processes"

**Left sidebar navigation**
- "FMEA WORKSPACE": Home, FMEA Projects, FMEA Team
- "CONTEXT (from Open-EQMS)": "System / Product / Process" (active, highlighted blue, chevron expanded), sub-items: "System Characteristics Base", "Characteristics Flow / Diagram", "Process Flow", "Process Characteristics"

**"System Hierarchy" tree panel (left of main table)**
- Heading "System Hierarchy"
- Tree: "Headlamp X1 System" (root, folder icon, expanded/highlighted — currently selected) with 5 indented children, each with a folder icon: "Electrical System", "Housing System", "Optical System", "Thermal System", "Mounting System"

**"Systems" data table (center)**
- Columns: System Name, Code, Type, Parent System, Status, Owner, Last Updated, Actions
- 6 rows:
  1. Headlamp X1 System — SYS-001 — Type: System — Parent System: "—" (none) — Status badge "Active" (green) — Owner: avatar "JD" Janez Demo — Last Updated: 12 May 2025 10:30 — Actions: pencil + "…"
  2. Electrical System — SYS-001-EL — Type: Subsystem — Parent: Headlamp X1 System — Status: Active (green) — Owner: avatar "AN" Ana Novak — Last Updated: 11 May 2025 16:20 — Actions
  3. Housing System — SYS-001-HO — Subsystem — Parent: Headlamp X1 System — Active (green) — Owner: avatar "MK" Marko Kovac — 11 May 2025 11:10 — Actions
  4. Optical System — SYS-001-OP — Subsystem — Parent: Headlamp X1 System — Status badge "Review" (purple/lavender pill, distinct from the green Active pill) — Owner: avatar "AN" Ana Novak — 10 May 2025 15:40 — Actions
  5. Thermal System — SYS-001-TH — Subsystem — Parent: Headlamp X1 System — Active (green) — Owner: avatar "LK" Luka Sterle — 10 May 2025 09:55 — Actions
  6. Mounting System — SYS-001-MO — Subsystem — Parent: Headlamp X1 System — Active (green) — Owner: avatar "PT" Peter Turk — 09 May 2025 14:05 — Actions

**"System Details" panel (right)**
- Heading "System Details" (for the selected/root row, Headlamp X1 System)
- Fields: System Name — Headlamp X1 System; Code — SYS-001; Type — System; Status — badge "Active" (green); Owner — Janez Demo; Description — "Complete headlamp system for vehicle platform X1."; Created — 02 May 2025 08:10; Last Updated — 12 May 2025 10:30
- A rendered 3D/technical illustration image of a headlamp assembly (gray-toned exploded/cutaway mechanical render) shown to the right of the field list, inside a bordered image frame

### 2. Wireframe & UI/UX

**Layout**: Dark sidebar + light content area, same shell as mockup-06. Below header: a horizontal tab strip (Systems/Products/Processes) governs which entity table is shown. Below tabs, a three-column layout: narrow tree panel (left, ~20%) | data table (center, ~50%) | detail panel with image (right, ~30%). The tree panel and detail panel bracket the table, forming a master(tree)–list(table)–detail(panel) pattern.

**Visual hierarchy**: The selected tree node ("Headlamp X1 System") is highlighted with a light-blue background band, and its row is presumably also the one whose data populates the right-hand "System Details" panel — establishing the tree as the primary navigation/filter control and the table as a flat listing that can be scoped by tree selection. The table's Status column color codes draw the eye: green "Active" pills read as normal/healthy, the single purple "Review" pill on Optical System stands out as needing attention.

**Color/status coding**: Status column — green pill = "Active"; purple/lavender pill = "Review" (an in-progress/pending-review state, visually distinct from both a "danger" red and the "success" green, suggesting a neutral/informational third state rather than a warning).

**Typography**: Page title bold/large; table header row small-caps gray; System Name column bolder than other cells; tree root node bold, children regular weight.

**Interaction patterns implied**: Clicking a tree node filters/selects that system and repopulates the right-hand Details panel (and possibly filters the table to that node's subtree). Clicking "Systems"/"Products"/"Processes" tabs swaps the entire table+tree(+details) content to the respective entity type — implying Products and Processes each get their own hierarchy/list/detail view, structurally identical to what's shown for Systems. The pencil icon opens an edit form; "…" opens a row action menu. "+ New System" implies a create-system modal/drawer capturing at minimum Name, Code, Type, Parent System, Owner, Description, and an image. "Import"/"Export" imply bulk file-based CRUD. The Details panel likely has additional edit affordances not visible (no visible Edit button in this crop, but the pencil in the table row likely opens the same form).

### 3. Architecture & Data Logic

- **The entire "System Hierarchy" tree, the "Systems" tab, System Name/Code/Type/Parent System/Status/Owner/Description/image fields**: Genuinely new — no `System` model exists anywhere in the codebase. This is explicitly called out in the grounding as the single biggest gap relevant to this mockup batch. Proposed model: a `System` entity with (at minimum) `name`, `code` (e.g. "SYS-001"), `type` (System/Subsystem, likely an enum), `parent` (self-referential FK, nullable, to support the tree/hierarchy), `status` (enum: at least Active/Review seen here — needs a defined status set and transitions), `owner` (FK to a user), `description`, and possibly an `image`/attachment field (no file/attachment storage exists anywhere per the grounding, so the headlamp render image is itself a second new capability: file/image upload and storage, not currently backed by anything). This would need full CRUD (create/edit/delete), a parent-child hierarchy query for the tree view, and validation (e.g., preventing circular parent references, enforcing unique `code` per project/tenant).
- **"Products" tab**: Real, already built as an entity (`Product` model exists: `fmea` FK, `name`, `description`, `part_number`), but Real field, not yet exposed in GUI is not quite accurate either — Product today has no parent/child hierarchy and no `System` link, so a "Products" tab styled identically to this Systems tab (with a hierarchy tree, Parent/Status/Owner columns, etc.) is Genuinely new for everything except Name/Description/Part Number. The tab would need: (a) exposing existing `Product.name`/`description`/`part_number` (Tier A/real), and (b) a new FK from `Product` to the proposed `System` (to place products under systems) plus new `status`/`owner` fields that don't exist on `Product` today (Tier D).
- **"Processes" tab**: Similarly, `Process` is Real, already built (`fmea` FK, `name`, `description`, `process_code`), but has no `System` link and no `status`/`owner`/hierarchy fields — same split as Products: existing Name/Description/Code fields are real (Tier A), everything else shown in this mockup's table shape (Parent, Status, Owner, tree hierarchy under Systems) is Genuinely new (Tier D).
- **Owner avatars (JD/AN/MK/LK/PT)**: Would map to Django's built-in `User` model once a `System.owner` FK is proposed and added — Real field, not yet exposed in the sense that Django users exist, but there is no field on any current model to assign a "system owner"; this is part of the proposed `System` entity above.
- **Status transitions (Active → Review)**: Behaviorally implied but not defined anywhere — proposed logic would need to specify what triggers a system moving into "Review" status (e.g., a pending change, a characteristic edit awaiting approval) and who can approve it back to "Active." No such workflow exists today, and no state-machine or approval model is present in the codebase.
- **Cross-entity relationships implied by this page**: The tree/table strongly implies that once a `System` model exists, `Product` and `Process` would both gain a FK to `System` (so a Product/Process can be scoped "under" a system, as System Characteristics Base does explicitly in mockup-08's "System / Subsystem" column). This System→Product/Process relationship is the structural prerequisite for mockups 08 and 09 in this batch, none of which can be built without it first being approved and implemented.
- **"Linked to FMEA" implied elsewhere**: Not shown directly on this page, but the existence of `FMEA.products`/`FMEA.processes` (via `Product.fmea`/`Process.fmea` FKs) means that once Systems exist and Products/Processes link to them, an FMEA-linkage count (as seen in mockup-08) becomes derivable — but only after the System model itself is built.

**Tier summary:** Tier A — none of the widgets on this page map cleanly to a fully-built, fully-exposed real field; the closest are `Product`/`Process` Name/Description/Code, which are real but appear in a structurally different (System-scoped, hierarchical) shape here. Tier C — Product/Process Name, Description, and Code fields are real but the page shown is far short of what's displayed (no hierarchy, no Status, no Owner, no System link on either model today). Tier D — the entire `System` entity (hierarchy, code, type, parent, status, owner, description, image), the System↔Product and System↔Process linking FKs, the status/review workflow, and image/attachment storage are all genuinely new with no backing entity anywhere in the current codebase.

### 4. Explicit non-authorization note
This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 08 — System Characteristics Base (source: mockup-08-system-characteristics-base.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Header bar**
- "Open FMEA" / "Open-EQMS Family" logo, hamburger icon
- Page title: "System Characteristics Base"
- Subtitle: "Define and manage system characteristics and their properties."
- Top-right: "Project: New Headlamp X1" dropdown, "Search (Ctrl+K)" box, bell icon with "0" badge, help icon, avatar "JD"
- Action buttons: "+ New Characteristic" (solid blue), "Import" (outline), "Export" (outline, with dropdown chevron), "Filters" (outline, with dropdown chevron)

**Left sidebar navigation (fuller than mockups 06/07 — reveals full app nav tree)**
- "FMEA WORKSPACE": Home, FMEA Projects, FMEA Team
- "CONTEXT (from Open-EQMS)": System / Product / Process (chevron expanded), sub-items: "System Characteristics Base" (active/highlighted), "Characteristics Flow / Diagram", "Process Flow", "Process Characteristics"
- "FMEA ANALYSIS": DFMEA, PFMEA, System FMEA, "Preventive FMEA (PM-FMEA)"
- "VALIDATION & CHANGE": Validation Trajectory, Evidence & Tests, Change Impact
- "ANALYSIS": AP / Detection, Risk Matrix, XDA Investigations
- Bottom: "Collapse" control

**Stat/KPI cards row (6 cards)**
1. icon (blue document), "Total Characteristics", "142", "All system characteristics"
2. icon (orange shield), "Critical Characteristics", "28", "19.7% of total"
3. icon (green target), "Monitored Characteristics", "96", "67.6% of total"
4. icon (blue pencil/link), "Linked to FMEA", "118", "83.1% of total"
5. icon (purple people), "Organizations", "3", "Sources"
6. icon (gray clock), "Last Updated", "12 May 2025", "10:30"

**Tab strip**: "All Characteristics" (active, blue underline), "By System", "By Type", "By Category", "By Importance", "By Monitoring", "By FMEA Link"

**Filter row**: Search box "Search characteristics...", dropdowns — System: "All Systems", Type: "All Types", Category: "All Categories", Importance: "All", Monitoring: "All" — plus a "More Filters" button (sliders icon)

**"All Characteristics" data table**
- Columns: checkbox, Characteristic ID (with sort arrow), Characteristic Name, System / Subsystem, Type, Category, Importance, Monitoring, Nominal Value / Target, Unit, Linked to FMEA, Last Updated, Actions
- 8 visible rows (SC-0001 through SC-0008):
  1. SC-0001, Luminous Flux, Optical System, Performance, Light Output, Importance badge "Critical" (red), Monitoring badge "Monitored" (green), 1200 ± 60, lm, "3 FMEA" (blue link text), 12 May 2025, actions (pencil + "…")
  2. SC-0002, Color Temperature, Optical System, Performance, Color, "High" (orange), Monitored (green), 5700 ± 300, K, "2 FMEA", 12 May 2025, actions
  3. SC-0003, Beam Pattern (Cut-off), Optical System, Functional, Beam Control, "Critical" (red), Monitored (green), Per Spec, "—" (no unit), "3 FMEA", 11 May 2025, actions
  4. SC-0004, Power Consumption, Electrical System, Performance, Electrical, "High" (orange), Monitored (green), 48 ± 2, W, "2 FMEA", 11 May 2025, actions
  5. SC-0005, Operating Voltage, Electrical System, Functional, Electrical, "High" (orange), Monitored (green), 13.5 ± 0.5, V, "2 FMEA", 10 May 2025, actions
  6. SC-0006, Ingress Protection, Housing System, Functional, Durability, "Critical" (red), Monitored (green), IP67, "—", "2 FMEA", 10 May 2025, actions
  7. SC-0007, Vibration Resistance, Mounting System, Durability, Mechanical, "Medium" (amber/yellow), Monitored (green), Per Spec, "—", "1 FMEA", 09 May 2025, actions
  8. SC-0008, Connector Retention Force, Electrical System, Durability, Mechanical, "Medium" (amber), Monitored (green), ≥ 80, N, "1 FMEA", 09 May 2025, actions
- Pagination footer: "Showing 1 to 8 of 142 characteristics", page controls: «, 1 (active), 2, 3, 4, 5, …, 18, »

**"Characteristic Details" right panel** (for SC-0001, the selected row)
- Heading "Characteristic Details", "SC-0001" with a "Monitored" badge (green) beside it
- Fields: Characteristic Name — Luminous Flux; System / Subsystem — Optical System; Type — Performance; Category — Light Output; Importance — badge "Critical" (red); Nominal Value / Target — 1200 ± 60 lm; Unit — lm; Monitoring Method — Photometric Test; Specification / Reference — HDL-OPT-001 Rev. B; Linked to FMEA — "3 FMEA" (blue link); Description — "Total luminous flux emitted by the headlamp in high beam mode at 25°C."; Last Updated — 12 May 2025 10:30; Updated By — avatar "JD" Janez Demo
- Button: "View Full History" (outline, clock/history icon)

**Bottom analytics row (4 panels)**
1. "Characteristics by Importance" — donut chart, center label "142 Total"; legend: Critical (red dot) 28 (19.7%), High (orange dot) 46 (32.4%), Medium (yellow dot) 42 (29.6%), Low (green dot) 26 (18.3%)
2. "Characteristics by Type" — donut chart, center "142 Total"; legend: Performance (violet dot) 54 (38.0%), Functional (teal dot) 40 (28.2%), Durability (orange dot) 28 (19.7%), Safety (yellow dot) 12 (8.5%), Other (gray dot) 8 (5.6%)
3. "Monitoring Status" — donut chart, center "142 Total"; legend: Monitored (green dot) 96 (67.6%), Calculated (blue dot) 24 (16.9%), Not Monitored (gray dot) 22 (15.5%)
4. "Top Systems" — ranked horizontal bar list (not a donut): Optical System 58, Electrical System 32, Housing System 20, Mounting System 16, Thermal System 10, Other Systems 6; divider line then "Total 142"

**Footer status bar**: "Database: OpenEQMS_Local" | "User: Janez Demo (Quality Engineer)" | "Role: Project Owner" | "Workspace: Global" | "Version: 1.0.0" | "System Status" with a green status dot (right-aligned)

### 2. Wireframe & UI/UX

**Layout**: Same dark-sidebar + light-content shell. Header → 6-card KPI row (denser than mockup-06's 4-card row, smaller cards to fit six across) → tab strip → filter/search row → two-column split (data table left ~75%, "Characteristic Details" panel right ~25%, matching the master-detail pattern of mockup-07) → pagination → a full-width 4-panel analytics row at the very bottom (three donuts + one ranked bar list) → a persistent footer status/debug bar.

**Visual hierarchy**: The 6 KPI cards are the top-level summary, using icon-color coding to hint at meaning (orange=critical/warning, green=success/monitored, blue=informational/linked, purple=organizational). The table is the dense working view; its Importance and Monitoring columns use the same color language as the KPI cards and bottom donuts, reinforcing one consistent semantic palette across the whole page: red=Critical, orange=High, amber/yellow=Medium, green=Low/Monitored/Active, gray=Other/Not-Monitored/None. The right Details panel mirrors and expands the selected row, and the bottom analytics row provides a second, chart-based summary layer beneath the table — a common "table + drill-in panel + aggregate dashboard" composite pattern repeated across this app's list pages (same skeleton as mockup-06 and mockup-07, but with an added analytics row).

**Color/status coding**: Importance: red = Critical, orange = High, amber/yellow = Medium (implied Low = green, per the donut legend, though no Low-importance row is visible in the 8 shown). Monitoring: green pill = "Monitored" (only value visible in the visible rows; donut legend confirms "Calculated" (blue) and "Not Monitored" (gray) also exist as values). "Linked to FMEA" values render as blue hyperlink-style text ("3 FMEA", "2 FMEA", "1 FMEA"), implying they're clickable.

**Typography**: Page title/KPI numbers bold and large; table headers small gray caps; Characteristic ID column rendered in blue (link-styled) suggesting each ID is clickable through to the detail panel or a dedicated page; row-critical Importance/Monitoring values are the only saturated colors in an otherwise mostly-gray-and-black table, drawing the eye directly to risk/status.

**Interaction patterns implied**: Clicking a table row (or its ID) populates/updates the right "Characteristic Details" panel (already showing SC-0001, matching the first row — implying default-selects the first row). Clicking "3 FMEA" navigates to or filters the linked FMEA(s). Tabs ("By System", "By Type", etc.) re-slice the same 142-row dataset by a different grouping/pivot — likely reusing this exact table shape with a different left-most grouping column or a different default filter pre-applied. "More Filters" implies an expandable advanced-filter drawer. "View Full History" implies an audit-log/version-history view per characteristic. The donuts and bar list are presumably clickable/hoverable to filter the table (standard dashboard drill-down pattern), though no explicit affordance (cursor, hover state) is visible to confirm this.

### 3. Architecture & Data Logic

- **Characteristic ID, Characteristic Name, Description**: Real, already built — maps to `ProductCharacteristic.name`/`.description` (product-side) and/or `ProcessCharacteristic.name`/`.description` (process-side). However, neither of those models has a `system`/`subsystem` FK, and neither is scoped as a unified "System Characteristics Base" spanning both — see System/Subsystem below.
- **"System / Subsystem" column and "By System" tab**: Genuinely new — depends entirely on the proposed `System` model from mockup-07 (which doesn't exist) plus a new FK from characteristics to it. Neither `ProductCharacteristic` nor `ProcessCharacteristic` links to any system-like entity today.
- **"Type" column (Performance / Functional / Durability / Safety / Other)**: Real field, not yet exposed in GUI is plausible only if this maps to `ProductCharacteristic.primary_classification_id` — but the grounding explicitly states that field is "NOT backed by any `ClassificationScheme`/`ClassificationTerm` model" and that model "is explicitly NOT approved/built." So despite a field existing on the model, there is no real classification data behind it — this is effectively Genuinely new (Tier D): the Type/Category/Importance/Monitoring columns as a controlled, structured taxonomy require the not-yet-approved `ClassificationScheme`/`ClassificationTerm` model.
- **"Category" column (Light Output / Color / Beam Control / Electrical / Durability / Mechanical)**: Same as Type — grounding explicitly calls out Category as part of the not-approved classification territory. Genuinely new.
- **"Importance" column (Critical/High/Medium/Low)**: Same not-approved-classification territory per the grounding ("Type/Category/Importance/Monitoring-status columns are all this same not-approved territory"). Genuinely new.
- **"Monitoring" column (Monitored/Calculated/Not Monitored)**: Same — Genuinely new, part of the unapproved classification scheme.
- **"Nominal Value / Target" and "Unit"**: Not named as existing fields anywhere in the grounding for either `ProductCharacteristic` or `ProcessCharacteristic` (which only have name/description/is_special/primary_classification_id, and name/description/cause_category_id/attributes respectively). `ProcessCharacteristic.attributes` is a generic JSONField, so nominal value/unit could in principle live there as unstructured data — Derivable from real data, needs new query/aggregation logic if repurposing `attributes`, or Genuinely new if a dedicated field is preferred; either way there's no defined, structured field for it today, so mark as proposed.
- **"Linked to FMEA" column/count ("3 FMEA" etc.) and the "Linked to FMEA" KPI card (118, 83.1%)**: Derivable from real data, needs new query/aggregation logic — `ProductCharacteristic.requirement` FK chains to `Requirement.function` → `Function` → `FailureMode`/`RecommendedAction` etc., so a count of distinct FMEAs touched by a characteristic's requirement chain is computable from existing relationships, once System Characteristics Base itself exists as a unified concept. This is Tier B logic riding on top of Tier D data.
- **"Organizations" KPI card (3, "Sources")**: Genuinely new — no multi-organization/tenancy model exists anywhere in the codebase per the grounding. This card implies characteristics are sourced from multiple organizations/systems (Open-EQMS being one), which is out of scope for the current single-tenant model.
- **"Monitoring Method" / "Specification / Reference" (in the Details panel)**: Genuinely new — no such fields exist on either characteristic model; would need to be added to whatever new/extended System Characteristic entity is proposed.
- **"Updated By" / "Last Updated" / "View Full History"**: Genuinely new — no audit-trail/version-history model is described anywhere in the grounding for characteristics; would need new change-tracking infrastructure (e.g., a generic revision/history table) to back a "View Full History" button.
- **Bottom donuts (by Importance / by Type / by Monitoring) and "Top Systems" bar list**: Derivable from real data, needs new query/aggregation logic — straightforward GROUP BY/COUNT aggregations, but only once the underlying Type/Category/Importance/Monitoring/System fields above are real, which they are not today. All four charts are Tier D-dependent Tier B logic.
- **Footer status bar (Database/User/Role/Workspace/Version/System Status)**: Mostly informational/system-level chrome. "User: Janez Demo (Quality Engineer)" and "Role: Project Owner" imply Real, already built data via Django's User model and the same `ProjectMembership.role` discussed in mockup-06, though "Project Owner" as a role value is not confirmed among any known role set. "Database: OpenEQMS_Local" / "Workspace: Global" / "Version: 1.0.0" / "System Status" imply Genuinely new system/environment metadata surfacing with no current backing.

**Tier summary:** Tier A — Characteristic Name/Description exist today via `ProductCharacteristic`/`ProcessCharacteristic`, just not unified or displayed this way. Tier B — Linked-to-FMEA counts, the three donut charts, and the Top Systems bar list are all real-data aggregations that become buildable once their inputs exist. Tier C — none cleanly fit (the closest, `primary_classification_id`, is explicitly a stub field with no backing scheme, so it lands in Tier D rather than C). Tier D — System/Subsystem linkage, Type/Category/Importance/Monitoring (the entire not-approved classification scheme), Nominal Value/Target/Unit, Monitoring Method, Specification/Reference, Organizations, and the full change-history/"View Full History" audit trail are all genuinely new with no backing entity or approved model.

### 4. Explicit non-authorization note
This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 09 — Characteristics Flow / Diagram (source: mockup-09-characteristics-flow-diagram.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Header bar**
- "Open FMEA" / "Open-EQMS Family" logo, hamburger icon
- Page title: "Characteristics Flow / Diagram"
- Subtitle: "Define and manage relationships between system characteristics."
- Top-right: "Project: New Headlamp X1" dropdown, "Search (Ctrl+K)" box, bell icon "0" badge, help icon, avatar "JD"
- Action buttons: "+ New Link" (solid blue), "Auto Link" (outline, icon), "Validate" (outline, icon), "Options" (outline, dropdown chevron), "Filters" (outline, dropdown chevron)

**Left sidebar navigation**: same structure as mockup-08 ("FMEA WORKSPACE", "CONTEXT (from Open-EQMS)" with "Characteristics Flow / Diagram" active/highlighted, "FMEA ANALYSIS", "VALIDATION & CHANGE", "ANALYSIS"), "Collapse" at bottom.

**Stat/KPI cards row (7 cards)**
1. icon (blue folder/doc), "Total Characteristics", "142", "All in base"
2. icon (blue link), "Linked Characteristics", "118", "83.1% of total"
3. icon (hand/pointer, dark), "Manual Links", "36", "30.5% of linked"
4. icon (green robot), "Auto Links", "82", "69.5% of linked"
5. icon (red shield), "Critical Links", "24", "High impact paths"
6. icon (orange warning triangle), "Warnings", "7", "Check recommended"
7. icon (gray clock), "Last Validated", "12 May 2025", "10:25"

**Tab strip**: "Link Matrix" (active, blue underline), "Link Network", "Link Rules", "Impact Paths"

**Left "Characteristics List" panel**
- Toolbar: "View:" with three icon toggle buttons (a grid/frame icon, a network/molecule icon — currently selected/highlighted blue, and a third small document/list icon) plus a dropdown chevron; "Layout:" dropdown set to "Auto (Force)"; "Depth:" dropdown set to "3 Levels"; a row of 5 small colored dots (red, orange, amber/gold, lighter yellow, green) followed by a horizontal slider control and a right-arrow icon (appears to be an importance/strength threshold filter slider)
- Search box "Search characteristics...", "Type: All" dropdown, "Category: All" dropdown, "More Filters" link (icon)
- Table columns: checkbox, ID, "Characteristic (CR)", Type, Category, Importance
- 15 rows shown (CR-001 through CR-015), each with: checkbox; blue-link-styled ID (CR-001…CR-015); short code name (e.g. "LMN-FLX", "COL-TMP", "BRM-PTN", "PWR-CNS", "OPR-VLT", "ING-PRT", "VIB-RES", "CON-RET", "SW-VER", "SIG-COM", "CHE-RES", "DEC-FIN", "SAFE-TMP", "LEGAL-EMC", "SPEC-001"); a "Type" cell showing a small colored circular icon-badge overlapping a short text label that is not reliably legible at this resolution (renders as roughly "HC" or "NC" — cannot confirm the exact code from the image); a "Category" cell showing a 3-letter code (OPT, ELE, MEC, SW, CHE, DEC, SAFE, LEG, SPC seen across rows); an "Importance" cell showing a single colored dot (red = filled solid for most early rows, amber for a couple, one hollow/outlined amber-yellow circle for CR-007/CR-008)
- Pagination: "Showing 1 to 15 of 142", page controls «, 1 (active), 2, 3, …, 10, »

**Center "Link Network" force-directed graph canvas**
- Canvas zoom/pan controls (left edge): "+", "+", "−", a fit-to-screen icon, a lock icon
- Graph: one central highlighted node "CR-001 / LMN-FLX" (blue-filled circle with a sun/star-burst icon, visually distinguished as the selected/root node) connected by straight labeled edges to 7 surrounding nodes, arranged radially:
  - "CR-013 / SAFE-TMP" (top) — red shield icon — edge label "REQ"
  - "CR-002 / COL-TMP" (upper-left) — orange circle, magnifying-glass/head icon — edge label "DR"
  - "CR-003 / BRM-PTN" (upper-right) — orange circle, headlight icon — edge label "DR"
  - "CR-012 / DEC-FIN" (left) — green circle, sparkle icon — edge label "AF"
  - "CR-004 / PWR-CNS" (right) — orange circle, lightning-bolt icon — edge label "SUP"
  - "CR-005 / OPR-VLT" (lower-left) — amber/gold circle, "V" icon — edge label "IN"
  - "CR-006 / ING-PRT" (bottom) — amber/gold circle, shield-check icon — edge label "CO"
  - "CR-007 / VIB-RES" (lower-right) — amber/gold circle, heartbeat/pulse icon — edge label "IN"
- A relationship-type legend strip below the canvas: "DR Drives", "IN Influences", "AF Affected By", "CO Constrained By", "SUP Supports", "REQ Required By" (each a 2-3 letter badge + full word)

**Right "Link Details" panel** (for the selected edge/link, CR-001 → CR-003)
- Heading "Link Details"
- "From": CR-001 LMN-FLX / "Luminous Flux"
- "To": CR-003 BRM-PTN / "Beam Pattern"
- "Relationship": badge "DR" + "Drives"
- "Strength": red dot + "High"
- "Link Type": "Auto"
- "Rule Matched": "OPT-DR-01"
- "Created": "11 May 2025 15:42"
- "Created By": avatar "MK" Marko Kovac

**"Impact / Importance" panel (below Link Details)**
- "Path Impact": badge "High" (red/pink)
- "Risk Propagation": "Yes"
- "Critical Path": a red checkmark/circle icon (value partially visible, appears to be a checked/positive indicator)
- "Recommendations": "Review control plan"

**"Link Statistics" panel**
- "Total Links": 118
- "Manual Links": 36 (30.5%)
- "Auto Links": 82 (69.5%)
- "High Impact Links": 24 (20.3%)
- "Medium Impact Links": 54 (45.8%)
- "Low Impact Links": 40 (33.9%)
- "Orphan Characteristics": 4
- Button: "View Orphans"

**"Importance" legend panel**: Critical (red dot), High (orange dot), Medium (amber dot), Low (green dot), None (gray dot)

**"Legend (Types)" panel (bottom-center, spans two groupings)**
- Group 1 (non-functional/special types): "SPC — Special" (blue icon), "LEG — Legal" (blue icon), "SAFE — Safety" (red shield icon), "CRT — Critical" (red icon)
- Group 2, under a "Functional" sub-heading, three columns of code+label pairs (rendered partly grayed-out/low-contrast in the image): "OPT — Optical" (icon), "MEC — Electrical" (text appears to read "Electrical" though the code is MEC, i.e. an apparent code/label mismatch as displayed), "ELE — Electric[al]" (cut off), "SW — Software", "CHE — Chemical", "DEC — Chemical" (a second entry also labeled "Chemical", distinct code — the image shows this exact apparent duplication/mismatch; not a misread, it is what the mockup displays)

**"Auto Link Options" panel (bottom-left)**
- Heading "Auto Link Options"
- "Linking Mode" dropdown: "Smart (Rules + AI)"
- "Max Depth" dropdown: "3 Levels"
- "Min Confidence" dropdown: "Medium (60%)"
- "Relationship Types" dropdown: "All Selected (6)"
- "Create Manual Review Queue" toggle (on/blue) with two small icon avatars beside it
- Button: "Generate / Update Links" (solid blue, icon)

**Footer status bar**: "Database: OpenEQMS_Local" | "User: Janez Demo (Quality Engineer)" | "Role: Project Owner" | "Workspace: Global" | "Version: 1.0.0" | "System Status" (green dot)

### 2. Wireframe & UI/UX

**Layout**: Same shell. Header → 7-card KPI row (the densest KPI row in this batch) → 4-tab strip → a three-column working area: left "Characteristics List" table (~20%), center force-directed graph canvas (~50%), right stacked detail/stats panels (Link Details, Impact/Importance, Link Statistics, Importance legend — ~30%) → below the fold, two more full-width panels side by side ("Legend (Types)" and "Auto Link Options") → footer status bar.

**Visual hierarchy**: The graph canvas is the visual centerpiece — a hub-and-spoke radial layout with one large, distinctly-colored (blue) "selected" node at the center and 7 satellite nodes around it, each colored/iconed by its own Type/Category classification (matching the color language from mockup-08: red=critical/safety, orange=high, amber/gold=medium). Edge labels are short 2-3 letter relationship codes rendered as small pill badges directly on the connecting lines, decoded by the legend strip beneath the canvas. The left table and right panels are secondary, denser, text-first supporting views — clicking a table row presumably re-centers the graph on that node, and clicking a graph edge presumably populates the "Link Details" panel (which currently shows the CR-001→CR-003 edge).

**Color/status coding**: Node icon-circle colors correspond to characteristic Category/Type (red=Safety/shield, orange=several functional categories, amber/gold=three more categories, green=Decorative/Finish, blue=the currently-selected root node only). Edge relationship codes are gray pill badges regardless of relationship type (color is not used to distinguish DR vs IN vs AF etc. — only the text label differs). Importance uses the same red/orange/amber/green/gray 5-level scale seen in mockup-08. Link "Strength" (in the Link Details panel) uses a red dot for "High" — potentially the same red used for "Critical" Importance, which could be a slight semantic overload worth flagging (Strength and Importance appear to be two different scales sharing one color).

**Typography**: KPI numbers bold/large; graph node labels are two-line (Code / Short-name) bold-ish sans-serif directly under each node; edge-label badges use small bold monospace-like lettering (DR/IN/AF/CO/SUP/REQ) inside light-gray rounded-rect chips.

**Interaction patterns implied**: "View:" toggle switches between a table/grid view, the network/graph view (currently active), and a third view (icon suggests possibly a list or matrix view, matching the "Link Matrix" tab name). "Layout: Auto (Force)" explicitly names this a force-directed graph layout algorithm, with "Depth: 3 Levels" controlling how many relationship hops radiate outward from the selected node — implying the graph is re-computed/re-laid-out per selected root node rather than showing the entire 142-characteristic graph at once. The colored-dot + slider control likely filters displayed links by importance/strength threshold. Zoom/pan/lock controls on the canvas imply standard interactive graph-canvas manipulation (drag nodes, zoom, pan, lock layout). "Auto Link" / "Validate" buttons and the full "Auto Link Options" panel (Linking Mode "Smart (Rules + AI)", Min Confidence "Medium (60%)") imply an AI-assisted or rules-based automatic relationship-suggestion engine that proposes links between characteristics, optionally queued for manual review before being committed ("Create Manual Review Queue" toggle). "Generate / Update Links" runs that engine. Clicking "View Orphans" presumably filters to the 4 characteristics with zero links. Tabs "Link Matrix" (implied to be a grid/matrix cross-reference view, not currently shown — this screen shows the Network view instead, so the tab labeling and visible content may be slightly inconsistent in the mockup, worth flagging) / "Link Network" / "Link Rules" (implied: a rules-editor for what drives "Rule Matched: OPT-DR-01") / "Impact Paths" (implied: a dedicated critical-path/propagation analysis view) each likely swap the center canvas to a different visualization of the same underlying link data.

### 3. Architecture & Data Logic

- **"Characteristics List" table (ID, Characteristic (CR), Type, Category, Importance)**: Same status as mockup-08's characteristics table — Genuinely new for System/Subsystem-scoped characteristics as a unified entity (no `System` model), and Type/Category/Importance again fall into the explicitly not-approved `ClassificationScheme`/`ClassificationTerm` territory per the grounding. Whatever underlying characteristic entity these CR-### rows represent is not confirmed to be `ProductCharacteristic` or `ProcessCharacteristic` as they exist today (those don't carry a `CR-###` ID scheme or these Type/Category codes).
- **The entire "Link Network" force-directed graph, "Link Matrix" grid, "Link Rules", "Impact Paths" tabs, and the relationship types (Drives/Influences/Affected By/Constrained By/Supports/Required By)**: Genuinely new. The grounding is explicit and unambiguous on this point: "any new relationship/edge/graph entity for a characteristics-flow diagram" does not exist, and "Mockup 9's force-directed graph, if it has one, would need a NEW relationship/edge entity, not a reuse of CauseInfluence" — `CauseInfluence` is confirmed to be a different, narrower Ishikawa cause-and-effect model, not a general characteristics-relationship graph. Proposed scope for a new entity (e.g. `CharacteristicLink`): `from_characteristic` FK, `to_characteristic` FK, `relationship_type` (enum: Drives/Influences/Affected By/Constrained By/Supports/Required By), `strength` (enum: Critical/High/Medium/Low/None, mirroring Importance), `link_type` (Manual/Auto), `rule_matched` (nullable FK/string to a rules table, itself new), `created_at`, `created_by`. This would need full CRUD, an underlying graph-query layer (traverse N hops from a root node, matching "Depth: 3 Levels"), and a rendering library capable of force-directed graph layout — the grounding confirms no graph-rendering/force-directed-layout library exists in the project (the just-approved Chart.js decision covers only line/bar/donut, explicitly not force-directed graphs or Sankey).
- **"Auto Link" / "Auto Link Options" panel (Linking Mode "Smart (Rules + AI)", Min Confidence "Medium (60%)", "Rule Matched: OPT-DR-01")**: Genuinely new, and specifically flagged by the grounding: "no AI 'auto-link'/confidence-scoring capability" exists. This implies a substantial new subsystem: a rules engine (to produce deterministic "Rule Matched" values like "OPT-DR-01") and/or an AI-based suggestion service (to produce confidence scores), plus a review-queue workflow ("Create Manual Review Queue" toggle) for human approval of AI/rule-suggested links before they become real `CharacteristicLink` records. This is one of the largest net-new capabilities implied across the whole mockup batch and would need its own dedicated architecture review (prompt design, confidence thresholds, audit trail of suggested-vs-accepted links, and how "Rule Matched" codes like OPT-DR-01 are authored/maintained) — none of it exists today, and nothing here should be read as pre-approving that scope.
- **KPI cards (Total/Linked Characteristics, Manual/Auto Links, Critical Links, Warnings, Last Validated)**: Derivable from real data, needs new query/aggregation logic — but only once the underlying `CharacteristicLink`-equivalent entity above exists; today there is nothing to count. "Warnings" (7, "Check recommended") and the "Validate" button additionally imply a data-quality/consistency-check rule engine (e.g., detecting orphaned or contradictory links) that also does not exist.
- **"Link Statistics" panel and "Orphan Characteristics" / "View Orphans"**: Derivable from real data, needs new query/aggregation logic, same dependency as above — an "orphan" is simply a characteristic with zero rows in the new link table; trivial once that table exists, impossible before.
- **Legend (Types) panel apparent code/label inconsistencies (MEC labeled "Electrical", two entries both labeled "Chemical" for CHE and DEC)**: Worth flagging explicitly as a mockup content issue rather than silently "fixing" it in any future build — if this taxonomy is carried forward, the Type/Category code-to-label mapping shown in the image should be re-verified with the source/design team before being treated as ground truth, since it does not internally reconcile as displayed.
- **Footer status bar**: same as mockup-08 — informational chrome, partially real (User/Role via Django auth + `ProjectMembership.role`), partially new (Database/Workspace/Version/System Status labels have no confirmed backing source).

**Tier summary:** Tier A — none; nothing on this page is a fully real, already-built, already-displayed field. Tier B — the KPI/statistics aggregations (Total/Linked/Manual/Auto/Critical Links, Orphans) become straightforward COUNT/GROUP BY logic, but only downstream of Tier D work. Tier C — none identified (Type/Category/Importance again land in Tier D rather than C, per the grounding's explicit classification-scheme caveat, same as mockup-08). Tier D — the entire characteristics-relationship/edge model, the force-directed graph itself and its rendering library, the Link Matrix/Link Rules/Impact Paths views, the rules engine, and the AI-assisted auto-link/confidence-scoring subsystem are all genuinely new with zero backing in the current codebase — this mockup is the largest concentration of net-new, unapproved scope in the batch.

### 4. Explicit non-authorization note
This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 10 — Evidence & Tests (source: mockup-10-evidence-and-tests.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Header bar**
- "Open FMEA" / "Open-EQMS Family" logo, hamburger icon
- Page title: "Evidence & Tests"
- Subtitle: "Plan, execute and track validation tests and evidence for DFMEA."
- Top-right: "Project: Headlamp X1 - DFMEA" dropdown, "Search (Ctrl+K)" box, bell icon "0" badge, help icon, avatar "JD"
- Action buttons: "+ New Evidence / Test" (solid blue), "Import" (outline), "Export" (outline, dropdown chevron), "Filters" (outline, dropdown chevron)

**Left sidebar navigation** (a different grouping/order than mockups 08/09 — noted as shown, not reconciled across mockups):
- "FMEA WORKSPACE": Home, FMEA Projects, FMEA Team
- "CONTEXT (from Open-EQMS)": System / Product / Process, System Characteristics Base, Characteristics Flow / Diagram, Process Flow, Process Characteristics
- "FMEA PROJECT": DFMEA, PFMEA, System FMEA, "Preventive FMEA (PM-FMEA)"
- "FMEA ANALYSIS": Functions, Failure Modes, Effects, Causes, Prevention Controls, Detection Controls, Actions
- "VALIDATION & CHANGE": "Evidence & Tests" (active/highlighted), Validation Trajectory, Change Impact
- "ANALYSIS": AP / Detection, Risk Matrix, XDA Investigations
- Bottom: "Collapse"

**Stat/KPI cards row (7 cards)**
1. icon (blue clipboard), "Total Evidence / Tests", "48", "All items"
2. icon (purple calendar), "Planned", "15", "31.3%"
3. icon (green play/triangle), "In Execution", "12", "25.0%"
4. icon (green check-circle), "Completed", "16", "33.3%"
5. icon (blue link), "Linked to DFMEA", "44", "91.7%"
6. icon (red/orange clock), "Overdue", "5", "10.4%"
7. icon (gray clock), "Last Updated", "12 May 2025", "10:25"

**Tab strip**: "All Evidence / Tests" (active, blue underline), "By DFMEA Item", "By Test Type", "By Status", "By Priority"

**Filter row**: Search box "Search...", dropdowns — "DFMEA Link: All", "Test Type: All", "Status: All", "Priority: All", "Responsible: All", "Planned Date: All" — plus "More Filters" button (calendar/sliders icon)

**"All Evidence / Tests" data table**
- Columns: checkbox, ID, Evidence / Test Name, "DFMEA Link / Function / Failure Mode" (two-line cell), Test Type, Method, Status, Priority, Planned Date, Owner, Linked, Actions
- 10 visible rows (EVT-001 through EVT-010):
  1. EVT-001, Luminous Flux Verification, DFMEA Link "F-01 / FM-01" / "Provide forward illumination / Low flux", Test Type "Validation" (gray pill), Method "Photometric Test / Lab", Status "Completed" (green pill), Priority "High" (red dot + text), Planned Date 08 May 2025, Owner avatar "MK", Linked (chain-link icon, green), Actions (link icon, eye icon, "…")
  2. EVT-002, Color Temperature Check, "F-01 / FM-01" / "Provide forward illumination / Wrong color", Validation, "Colorimeter / Lab", Status "In Execution" (blue pill), Priority "Medium" (orange dot), 14 May 2025, Owner "AN", Linked icon, Actions
  3. EVT-003, Vibration Durability Test, "F-02 / FM-03" / "Resist vibration / Housing crack", "Reliability" (gray pill), "Vibration Test / Lab", Status "Planned" (gray/lavender pill), Priority "High" (red dot), 20 May 2025, Owner "PT", Linked, Actions
  4. EVT-004, Ingress Protection Verification, "F-02 / FM-04" / "Resist water / Water ingress", Validation, "IP Test (IP67) / Lab", Planned, Priority "High" (red dot), 22 May 2025, Owner "LK", Linked, Actions
  5. EVT-005, Thermal Cycling Test, "F-03 / FM-02" / "Dissipate heat / Overheat", Reliability, "Thermal Cycling / Lab", In Execution, Priority "High" (red dot), 16 May 2025, Owner "MK", Linked, Actions
  6. EVT-006, Connector Retention Force, "F-04 / FM-05" / "Secure connection / Loose connector", "Verification" (gray pill), "Pull Test / Lab", Completed, Priority "Medium" (orange dot), 07 May 2025, Owner "AN", Linked, Actions
  7. EVT-007, EMC Immunity Test, "F-05 / FM-06" / "Resist EMI / Flicker", Validation, "EMC Test / Lab", Planned, Priority "Medium" (orange dot), 26 May 2025, Owner "PT", Linked, Actions
  8. EVT-008, Software Function Check, "F-06 / FM-02" / "Control light pattern / Wrong pattern", Verification, "Functional Test / In-House", Completed, Priority "Medium" (orange dot), 06 May 2025, Owner "LK", Linked, Actions
  9. EVT-009, Chemical Resistance Test, "F-07 / FM-03" / "Resist chemicals / Lens damage", Validation, "Chemical Test / Lab", Planned, Priority "Low" (green dot), 28 May 2025, Owner "MK", Linked, Actions
  10. EVT-010, Endurance Test (Life), "F-01 / FM-07" / "Provide forward illumination / Short life", Reliability, "Life Test / Lab", Planned, Priority "High" (red dot), 05 Jun 2025, Owner "PT", Linked, Actions
- Pagination: "Showing 1 to 10 of 48 items", page controls «, 1 (active), 2, 3, 4, 5, …, plus a "10 / page" page-size dropdown

**"Evidence / Test Details" right panel** (for EVT-001, X close icon top-right)
- Heading "Evidence / Test Details"
- "EVT-001" with badge "Completed" (green)
- "DFMEA Link": "F-01 / FM-01" / "Provide forward illumination / Low flux"
- "Test Type": badge "Validation"
- "Method": "Photometric Test (Lab)"
- "Objective": "Verify luminous flux meets requirement."
- "Nominal / Target": "1200 lm ± 60"
- "Acceptance Criteria": "Measured value within target range."
- "Result": "1245 lm" + badge "Pass" (green)
- "Planned Date": "08 May 2025"
- "Executed Date": "08 May 2025"
- "Owner": avatar "MK", Marko Kovac
- "Evidence": three small file-type icons (paperclip, a document icon, a PDF-style icon) + "3 files"
- "Linked to DFMEA": "Open DFMEA Item" (blue link text)
- "Created": clock icon + "05 May 2025 09:15"
- "Last Updated": link icon + "12 May 2025 10:25" / "by Marko Kovac"
- Button: "View Full History" (outline, icon)

**Bottom analytics row (4 panels)**
1. "Status Overview" — donut chart, center "48 Total"; legend: Completed (green) 16 (33.3%), In Execution (blue) 12 (25.0%), Planned (gray) 15 (31.3%), On Hold (orange) 3 (6.3%), Cancelled (red) 2 (4.2%)
2. "By Test Type" — donut chart, center "48 Total"; legend: Validation (blue) 20 (41.7%), Verification (teal) 12 (25.0%), Reliability (purple) 9 (18.8%), Acceptance (amber) 4 (8.3%), Other (gray) 3 (6.2%)
3. "By Priority" — horizontal bar chart (not a donut): High (red bar) 22 (45.8%), Medium (orange bar) 18 (37.5%), Low (green bar) 6 (12.5%), None (gray bar) 2 (4.2%)
4. "Linked to DFMEA" — donut chart, center "48 Total"; legend: Linked (green) 44 (91.7%), Not Linked (red) 4 (8.3%)

**Footer status bar**: "Database: OpenEQMS_Local" | "User: Janez Demo (Quality Engineer)" | "Role: Project Owner" | "Workspace: Global" | "Version: 1.0.0" | "System Status" (green dot)

### 2. Wireframe & UI/UX

**Layout**: Same shell as the rest of the batch. Header → 7-card KPI row → 5-tab strip → filter row → two-column split (table ~75% left, "Evidence / Test Details" panel ~25% right, with an explicit close "X" affordance on the panel implying it's a dismissible drawer overlay rather than a permanently-docked pane) → pagination with a page-size selector → 4-panel bottom analytics row (2 donuts, 1 bar chart, 1 donut) → footer status bar. Structurally this is the same "KPI row → tabbed table+filters → master/detail → aggregate dashboard" template used in mockups 08 and 09.

**Visual hierarchy**: KPI cards again front-load the summary (Planned/In Execution/Completed as a pipeline-stage breakdown, plus Overdue as a flagged-risk metric in red/orange). The table's Status and Priority columns carry the same red/orange/green semantic coding used throughout the batch. The Details panel is the richest single-record view in the whole batch — 15+ distinct fields including a Result-vs-Acceptance-Criteria pass/fail outcome and file attachments, suggesting this page is meant to be the most "document-heavy" / evidentiary record type in the app.

**Color/status coding**: Status pills: green = Completed, blue = In Execution, gray/lavender = Planned; donut legend additionally shows orange = On Hold and red = Cancelled (neither visible among the 10 sample rows). Priority: red dot = High, orange dot = Medium, green dot = Low (None = gray, per the bar chart). Test Type badges (Validation/Verification/Reliability) render as neutral gray pills in the table (not color-coded) but ARE color-coded (blue/teal/purple/amber/gray) in the "By Test Type" donut — an inconsistency between table-cell and chart-legend coloring for the same field, worth flagging. "Result" + "Pass" badge (green) implies a pass/fail (and presumably also a "Fail" red-badge state, not shown) outcome field distinct from "Status."

**Typography**: KPI numbers bold/large; table ID column blue/link-styled; two-line "DFMEA Link / Function-Failure Mode" cells use a bold top line (link IDs) and a lighter/gray second line (descriptive text) — a pattern for showing an ID-plus-context pair compactly.

**Interaction patterns implied**: Clicking a table row opens/updates the "Evidence / Test Details" panel (dismissible via the X). "Open DFMEA Item" link navigates to the underlying Failure Mode/Function record in the DFMEA worksheet — implying a direct cross-page link from a test record back into the FMEA structure. The three file icons under "Evidence" imply an attachment viewer/uploader (click to preview or download each of the 3 files). "View Full History" implies a per-record audit/version log, same pattern as mockup-08. Tabs re-slice the same 48-item dataset by DFMEA Item / Test Type / Status / Priority. "+ New Evidence / Test" implies a create form capturing at minimum: Name, DFMEA Link (Function+Failure Mode), Test Type, Method, Objective, Nominal/Target, Acceptance Criteria, Planned Date, Owner/Responsible, and later Result + Executed Date + Evidence file uploads once the test runs — i.e., a two-phase lifecycle (planned → executed/completed) with status transitions (at minimum Planned → In Execution → Completed, plus On Hold and Cancelled as branch states per the donut legend).

### 3. Architecture & Data Logic

- **Baseline reality check (per grounding)**: today's `Evidence` model is only `FK to RecommendedAction, name, description, reference_uri` and `EffectivenessVerification` is only `FK to RecommendedAction, result, verified_at`. Neither has a direct FailureMode link, a Test Type, a Method, an Objective, an Acceptance Criteria, a Planned/Executed date pair, a Priority, an Owner-as-person, a Status workflow, or file attachments. The grounding explicitly instructs: if this mockup shows a much richer entity than that, it is Tier D — a new `ValidationTest`/`TestPlan`-shaped entity, not the same as today's `Evidence`/`EffectivenessVerification`. That is exactly what this mockup shows, so the entire "Evidence / Test" record type on this page should be scoped as genuinely new.
- **"Evidence / Test Name" and "Objective"/"Acceptance Criteria" text fields**: Genuinely new — closest existing analog is `Evidence.name`/`.description` and `Evidence.reference_uri`, but those hang off `RecommendedAction`, not off a Failure Mode/Function pair directly, and carry none of Objective/Acceptance Criteria/Nominal-Target as distinct structured fields. Proposed: a new entity (e.g. `ValidationTest`) with `name`, `objective`, `nominal_target`, `acceptance_criteria` as first-class fields.
- **"DFMEA Link" (F-01/FM-01, Function/Failure Mode)**: Real relationship path exists in part — `FailureMode.function` FK and `Function` model are real — but there is no field on today's `Evidence`/`EffectivenessVerification` linking directly to a `FailureMode`/`Function` pair (`Evidence` only links to `RecommendedAction`). Genuinely new — the proposed `ValidationTest` entity would need a direct FK to `FailureMode` (and/or `Function`) to reproduce this two-line "F-01 / FM-01" cell, since today's chain (`Evidence` → `RecommendedAction` → `failure_mode`/`failure_cause`, both nullable) is an indirect, optional path that doesn't guarantee a Function/Failure-Mode pair the way this column implies.
- **"Test Type" (Validation/Verification/Reliability/Acceptance/Other)**: Genuinely new — no such enumerated field exists on `Evidence` or `EffectivenessVerification` today.
- **"Method" (Photometric Test/Lab, Colorimeter/Lab, etc.)**: Genuinely new — no method/location field exists today.
- **"Status" (Planned/In Execution/Completed/On Hold/Cancelled)**: Genuinely new as its own workflow. Note this is a DIFFERENT status set from `RecommendedAction.status` (ActionStatus: open/in_progress/completed/verified/cancelled — the grounding explicitly notes "no 'on_hold' value exists" there). This mockup's test-status vocabulary (with an explicit "On Hold" value) does not match ActionStatus, confirming it needs its own separate status enum on the new entity, not a reuse of `ActionStatus`.
- **"Priority" (High/Medium/Low/None)**: Genuinely new — no priority field exists on `Evidence`, `EffectivenessVerification`, or `RecommendedAction` per the grounding.
- **"Planned Date" / "Executed Date"**: Genuinely new — `EffectivenessVerification` has only a single `verified_at` timestamp, not a planned-vs-executed date pair. `RecommendedAction.due_date` is a real, separate field but belongs to actions, not to this test entity, and is a single date, not a planned/executed pair.
- **"Owner" (person avatar, e.g. Marko Kovac)**: Real field, not yet exposed in GUI is close but not quite right — `RecommendedAction.responsible_role` is a FK to `ResponsibleRole`, and the grounding is explicit that `ResponsibleRole` "is a name/description catalog only — NOT a person/user roster." So an Owner shown as an actual named person (with avatar) is Genuinely new: it would need a new person-FK field (e.g. to Django's `User`), distinct from the existing role-catalog concept.
- **"Linked" column / "Linked to DFMEA" field and its "Open DFMEA Item" link**: Derivable from real data, needs new query/aggregation logic once the new direct FailureMode/Function FK above exists (simply: is that FK populated). Until that FK is added, there is nothing to compute this from.
- **"Result" value + "Pass"/(implied "Fail") badge**: Real field, not yet exposed in GUI, partially — `EffectivenessVerification.result` exists as a field, but its shape/semantics aren't specified beyond "result" in the grounding, and this mockup wants a numeric measured value ("1245 lm") PLUS a separate pass/fail classification badge, which is richer than a single opaque `result` field is confirmed to support. Best read as: reuse-candidate field, needs new structure/validation logic to store both a measured value and a derived pass/fail classification (e.g., by comparing to `acceptance_criteria`).
- **"Evidence" attachments (3 files, paperclip/doc/PDF icons)**: Genuinely new, and specifically flagged by the grounding: "no file/attachment/document storage anywhere" exists in the codebase. This is a foundational gap — supporting file evidence at all (for this page or any other) requires a new file-storage subsystem (upload endpoint, storage backend, per-file metadata, access control) before this "3 files" attachment UI can be real.
- **"Created" / "Last Updated" / "by Marko Kovac" / "View Full History"**: Genuinely new — same audit-trail gap identified in mockups 08 and 09; no change-history/versioning model exists for any of these entities today.
- **KPI cards (Total/Planned/In Execution/Completed/Linked to DFMEA/Overdue/Last Updated)**: Derivable from real data, needs new query/aggregation logic — trivial COUNT/GROUP BY once the new `ValidationTest`-equivalent entity, its Status enum, and its DFMEA-link FK all exist; "Overdue" specifically needs a Planned Date < today AND Status != Completed comparison, both of which are new fields.
- **Bottom donuts/bar chart (Status Overview, By Test Type, By Priority, Linked to DFMEA)**: Derivable from real data, needs new query/aggregation logic, same dependency chain as the KPI cards — all four are straightforward aggregations once the underlying new fields exist, none possible before.

**Tier summary:** Tier A — none of the widgets on this page map to a fully real, already-displayed field as shown; the closest existing entities (`Evidence`, `EffectivenessVerification`) are both far narrower than what's depicted. Tier B — the KPI cards and all four bottom charts are real-data aggregations, but only once their Tier D inputs exist. Tier C — `EffectivenessVerification.result` is a real field far short of the Result+Nominal/Target+Acceptance-Criteria+Pass/Fail structure shown; `RecommendedAction.due_date` is a real but singular date field far short of the Planned/Executed date pair shown. Tier D — the entire richer test-record shape (direct FailureMode/Function link, Test Type, Method, Objective, Acceptance Criteria, Status workflow with On Hold, Priority, person-Owner, file attachments, and full audit history) is genuinely new, matching the grounding's explicit prediction that this page implies a new `ValidationTest`/`TestPlan`-shaped entity rather than a reuse of today's minimal `Evidence`/`EffectivenessVerification` models. The missing file/attachment storage subsystem in particular is a cross-cutting gap, not specific to this page alone.

### 4. Explicit non-authorization note
This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 11 — DFMEA (source: mockup-11-dfmea.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Top bar**
- Logo block: "Open FMEA" wordmark + "Open-EQMS Family" subtitle, hamburger/collapse icon.
- Page title "DFMEA" with a purple "Design FMEA" pill badge next to it.
- Subtitle line: "Design Failure Mode and Effects Analysis for product / system design."
- Project selector dropdown: "Project: New Headlamp X1".
- Global search box with placeholder "Search (Ctrl+K)".
- Notification bell icon (badge shows "0" or is empty — not fully legible).
- Help "?" icon.
- User avatar "JD".
- Action button row: "+ New DFMEA Item" (primary blue), "Import", "Export" (dropdown), "Reports" (dropdown), "View Options" (dropdown), "Filters" (icon+label).

**Left sidebar** (grouped, section headers in caps)
- FMEA WORKSPACE: Home, FMEA Projects (active), FMEA Team
- CONTEXT (from Open-EQMS): System / Product / Process, System Characteristics Base, Characteristics Flow / Diagram, Process Flow, Process Characteristics
- FMEA PROJECT: DFMEA (active/selected), PFMEA, System FMEA, Preventive FMEA (PM-FMEA)
- FMEA ANALYSIS: Functions, Failure Modes, Effects, Causes, Prevention Controls, Detection Controls, Actions
- VALIDATION & CHANGE: Evidence & Tests, Validation Trajectory, Change Impact
- ANALYSIS: AP / Detection, Risk Matrix, XDA Investigations
- Bottom: "Collapse" control with icon

**Stat/KPI cards row (7 cards)**
1. "DFMEA Items" — 86 — "All items" (clipboard icon)
2. "High Risk (RPN ≥ 100)" — 14 — "16.3% of total" (shield icon)
3. "Actions Open" — 23 — "26.7% of total" (document icon)
4. "Actions Overdue" — 6 — "7.0% of total" (clock icon)
5. "Avg. Initial RPN" — 184 — "Before actions" (purple bar-chart icon)
6. "Avg. Current RPN" — 62 — "After actions" (green trend icon)
7. "Last Updated" — 12 May 2025 — "10:25" (calendar icon)

**Tabs:** DFMEA Table (active), Structure Tree, Interface Matrix, Parameter Diagram, RPN Overview, Action Tracker

**Filter/search bar (below tabs):** search box "Search DFMEA items...", dropdowns "Element: All", "Function: All", "Status: All", "RPN: All", "Type: All", "More Filters" icon+label.

**Main table** — columns (checkbox column first):
ID | Element / Part | Function | Failure Mode | Effect(s) | Cause(s) | Severity (S): Rating, Class | Occurrence (O): Rating, Class | Current Controls: Prevention (P) Rating/Class, Detection (D) Rating/Class | RPN: Initial, Current | Actions | Status

Rows DF-001 through DF-008 shown (of 86 total), each with all columns populated, e.g.:
- DF-001 | Housing (Lens) | Provide light transmission | Lens crack | Reduced light output, water ingress | Impact, stress concentration | S 8/H | O 4/M | P 3/L, D 4/M | Initial 128 / Current 48 | Actions "2/1" | Status "Open"
- DF-002 | LED Module | Generate light | LED failure (no light) | No illumination | Over-current, thermal stress | S 9/H | O 3/L | P 4/M, D 3/L | 108/36 | "1/0" | Open
- DF-003 | Heatsink | Dissipate heat | Insufficient cooling | Shorter life, lumen drop | Design margin low, clogging | S 7/H | O 4/M | P 3/L, D 4/M | 112/56 | "2/1" | Open
- DF-004 | Driver PCB | Supply stable current | Driver failure | Flicker, dimming, no light | Component failure, overload | S 9/H | O 3/L | P 4/M, D 3/L | 108/27 | "1/0" | In Progress
- DF-005 | Connector | Provide electrical connection | Loose connection | Intermittent light | Vibration, poor engagement | S 6/M | O 5/H | P 3/L, D 5/H | 150/75 | "2/1" | Open
- DF-006 | Seal (Gasket) | Prevent water ingress | Seal damage | Water ingress, corrosion | Assembly damage, ageing | S 8/H | O 4/M | P 3/L, D 4/M | 128/48 | "1/1" | In Progress
- DF-007 | Reflector | Direct light pattern | Reflector misalignment | Wrong beam pattern | Assembly error, tolerance stack | S 7/H | O 3/L | P 2/L, D 4/M | 84/24 | "1/0" | Closed
- DF-008 | Mounting Bracket | Fix headlamp position | Bracket break | Headlamp loose | Material weakness, impact | S 8/H | O 3/L | P 3/L, D 4/M | 96/32 | "1/0" | Open

Status badges seen: "Open" (blue), "In Progress" (amber/orange), "Closed" (gray). Class badges: "H" (red/pink chip), "M" (amber/orange chip), "L" (green chip). RPN numbers: Initial shown in red text, Current shown in orange or green text depending on value.

**Pagination:** "Showing 1 to 8 of 86 items", page buttons 1 (active) 2 3 4 5 … 11, prev/next arrows.

**Lower-left panel — "RPN Trend"**: line chart, two series "Initial RPN (Avg.)" (red) and "Current RPN (Avg.)" (green), X-axis Wk 14/16/18/20/22, Y-axis 0–250, data-point labels visible: red ≈212, 198, 185, 172, 162; green ≈98, 90, 78, 68, 62.

**Lower-middle panel — "Top 5 Highest Current RPN"**: mini-table, columns ID / Item / Function / Current RPN / Trend (arrow icon). Rows: DF-005 Connector/Provide electrical connection 75 (up), DF-003 Heatsink/Dissipate heat 56 (up), DF-001 Housing(Lens)/Provide light transmission 48 (flat), DF-006 Seal(Gasket)/Prevent water ingress 48 (flat), DF-002 LED Module/Generate light 36 (down).

**Lower-right panel — "Actions by Status"**: donut chart, center label "30 / Total". Legend: Open 17 (56.7%, blue), In Progress 7 (23.3%, orange), Closed 6 (20.0%, green), Cancelled 0 (0.0%, gray).

**Far-right detail drawer — "Item Details"** (with "×" close icon):
- Title "DF-001" with "Open" status badge (blue).
- Field list: Element/Part = Housing (Lens); Function = Provide light transmission; Failure Mode = Lens crack; Effect(s) = Reduced light output, water ingress.
- Three colored square rating tiles: "S 8" (red), "O 4" (orange), "D 4" (orange). (No "P" tile shown here — only S/O/D.)
- "Initial RPN" 128 (red, bold) and "Current RPN" 48 (green, bold), side by side.
- "Responsible": avatar "MK" + name "Marko Kovac".
- "Last Updated": 12 May 2025 10:25.
- Link: "View Full Details" (with icon).

**"RPN Risk Summary"** donut, center "86 / Total". Legend: Very High (≥200) red dot 4 (4.7%); High (100–199) orange dot 14 (16.3%); Medium (50–99) amber/yellow dot 28 (32.6%); Low (1–49) green dot 40 (46.5%).

**"DFMEA Progress"** — three horizontal progress bars with % labels: "Items with Actions" 53%; "Actions Completed" 74%; "High Risk Closed" 43%.

**Footer bar:** "Database: OpenEQMS_Local" | user icon "User: Janez Demo (Quality Engineer)" | link icon "Role: Project Owner" | "Workspace: Global" | "Version: 1.0.0" | right-aligned "System Status" with a green dot.

### 2. Wireframe & UI/UX

Structure is a classic app-shell: fixed left sidebar (grouped nav with section labels, an active-state blue highlight on the current item), a fixed top bar (breadcrumb-less — title + badge + subtitle on the left, global controls on the right), and a scrollable main content column. The main column stacks: (a) a 7-up KPI card row, (b) a tab strip switching between six analysis views, (c) a filter/search toolbar, (d) the primary data table, (e) pagination, (f) a 3-column row of secondary charts/lists (trend line, top-5 list, donut), and (g) a persistent thin footer with environment/session metadata. A docked right-hand drawer ("Item Details") runs the full height of the content area alongside the table and is populated by the currently checked/selected table row (DF-001 is checked via its row checkbox, and its data mirrors the drawer) — implying selecting a row's checkbox or clicking the row opens/updates this drawer rather than navigating away. Below the drawer, two more summary widgets (RPN Risk Summary donut, DFMEA Progress bars) sit stacked, so the right rail effectively has three stacked panels (Item Details, RPN Risk Summary, DFMEA Progress) running parallel to the KPI+table+trend region on the left.

Visual hierarchy: the KPI cards are the largest, boldest numerals on the page (drawing the eye first), followed by the RPN numbers in the table (red/orange/green colored, bold) which are clearly the page's primary risk signal. Status and Class values are compact colored pill/chip badges — a consistent red=High/Critical, amber-orange=Medium, green=Low, blue=Open/informational, gray=Closed/neutral color coding is used throughout (chips, RPN text, donut slices, progress-bar accents). Table row text is left-aligned and dense (small type), while the right-drawer repeats the same fields in a larger, more spaced-out, label/value list layout — a "compact list → expanded detail" pattern typical of list/detail UIs.

Interaction patterns implied: row checkboxes (multi-select, presumably for bulk export/actions), clickable column-header sort (not visually indicated but implied by table convention), each dropdown filter (Element/Function/Status/RPN/Type) is a select control that would refine the table client- or server-side, "More Filters" implies a slide-out/modal with additional filter fields, tabs swap the entire main content region (Structure Tree, Interface Matrix, Parameter Diagram, RPN Overview, Action Tracker are presumably alternate visualizations/editors of the same underlying FMEA data), "View Full Details" in the drawer implies a full-page/modal detail view beyond the drawer's summary, and the small trend arrows in "Top 5 Highest Current RPN" imply a computed direction-of-change indicator per row. The drawer's "×" implies it can be dismissed, likely collapsing the table back to full width.

### 3. Architecture & Data Logic

- **DFMEA Items (86)** — Real, already built. Count of `FailureMode` objects for FMEA records where `FMEA.fmea_type == "design"` (or scoped to the currently selected `FMEA`/`FMEAProject`). Straightforward `.count()`.
- **High Risk (RPN ≥ 100) (14)** — Derivable from real data, needs new query/aggregation logic. Requires resolving each `FailureMode`'s current risk score from `RiskEvaluation.result` (a JSONField holding `{"score": N, ...}` for RPN-style evaluations) on the latest evaluation per failure mode, then counting where score ≥ 100. JSON-field filtering/aggregation across a "latest per group" set is new query work.
- **Actions Open (23) / Actions Overdue (6)** — Real field, not yet exposed as this aggregate. `RecommendedAction.status` (`ActionStatus.open`) is real; "Open" count is a straightforward filtered count once scoped to this FMEA's failure modes/causes. "Overdue" is derivable from real data but needs new business logic: no `is_overdue` field exists — it must be computed as `due_date < today AND status not in (completed, verified, cancelled)`.
- **Avg. Initial RPN (184) / Avg. Current RPN (62)** — Derivable from real data, needs new query/aggregation logic. No dedicated "initial RPN" field exists on `RiskEvaluation`; per the grounding, getting first-vs-latest per failure mode requires `.order_by("evaluated_at").first()` (earliest) vs the default-ordered `.first()` (latest), then averaging `severity × occurrence × detection` (or the JSON `result.score`) across all failure modes in scope.
- **Last Updated (12 May 2025 10:25)** — Ambiguous against the grounding: no audit-timestamp field is confirmed to exist on `FailureMode`/`RiskEvaluation`/`FMEA` in the given model list. If standard Django `updated_at`/`auto_now` fields exist on these models this is Tier B (max() aggregation); if not, this is genuinely new (Tier D) — flagged as an open question for the architecture review rather than assumed.
- **Tabs — DFMEA Table**: Real, already built (the table itself, per column mapping below).
- **Tabs — Structure Tree / Interface Matrix / Parameter Diagram**: Genuinely new — no backing entity/field exists. Per the grounding, there is no `System`/parent-hierarchy model, no element/part-structure model, no interface/interaction model, and no Parameter Diagram (P-Diagram) concept anywhere in the codebase. Building these would require new models (e.g., a structure/element hierarchy tree, an interface-relationship model between elements, and a P-Diagram model capturing inputs/noise-factors/control-factors/outputs) — classic DFMEA concepts with zero existing groundwork, as called out explicitly in the grounding notes.
- **Tabs — RPN Overview / Action Tracker**: Derivable from real data, needs new query/aggregation logic (RPN Overview) and Real, already built with new list/filter view (Action Tracker over `RecommendedAction`).
- **Filter: Element (dropdown)** — Genuinely new / ambiguous. See "Element / Part" column below — no direct model field backs this filter as shown.
- **Filter: Function** — Real, already built (`Function.name`).
- **Filter: Status** — See "Status" column below; likely a derived rollup, not a direct field.
- **Filter: RPN** — Derivable from real data, needs new bucket/range-filter logic against the computed RPN.
- **Filter: Type** — Ambiguous; if this maps to `FMEA.fmea_type` it's Tier A, but that field is FMEA-level, not per-row, so its purpose on a row-filterable dropdown here is unclear from the mockup alone.
- **Table column — ID**: Real, already built (`FailureMode.pk` or a formatted code).
- **Table column — Element / Part**: Genuinely new / not directly backed. The grounding is explicit: "No FK to `Product` directly — no 'Element/Part' field exists" on `FailureMode`. The closest real path is `FailureMode.function.product.name` (since `Function.product` is a nullable FK) — but that only resolves when the failure mode's function is a product-function rather than an operation-function, so it is at best Tier B (derivable via a join, with a real gap: no such value when `function` is null or is an operation-function) and at worst genuinely new if a dedicated "Element/Part" concept distinct from `Product` is intended.
- **Table column — Function**: Real, already built (`FailureMode.function.name`).
- **Table column — Failure Mode**: Real, already built (`FailureMode.name`).
- **Table column — Effect(s)**: Real, already built (`FailureMode.effects` related manager → `FailureEffect.name`, joined/concatenated for display).
- **Table column — Cause(s)**: Real, already built (`FailureMode.causes` related manager → `FailureCause.name`).
- **Table column — Severity (S) Rating**: Real, already built (`RiskEvaluation.severity`, most plausibly from the earliest evaluation per failure mode given the RPN reconciliation below).
- **Table column — Severity/Occurrence/Detection Class (H/M/L badges)**: Real field but far short of what's shown / needs new logic. The grounding states only a combined `classify_severity_occurrence` (S×O product) banding function exists — there is no per-factor S-only, O-only, or D-only H/M/L banding function today. Showing an independent Class per factor requires new threshold logic to be defined.
- **Table column — Occurrence (O) Rating**: Real, already built (`RiskEvaluation.occurrence`).
- **Table column — Current Controls: Prevention (P) Rating/Class**: Genuinely new — no backing field. `RiskEvaluation` only has three factor fields (`severity`, `occurrence`, `detection`); there is no fourth "Prevention" rating field, and `PreventionControl` itself has only `name`/`description` (no effectiveness rating). Introducing a numeric, classed Prevention factor is a material model change (a 3-factor → 4-factor risk model) worth flagging distinctly for review, since it changes the RPN formula's shape.
- **Table column — Current Controls: Detection (D) Rating/Class**: Real, already built for the raw rating (`RiskEvaluation.detection`); the Class banding has the same Tier B gap noted above.
- **Table column — RPN Initial / Current**: Derivable from real data, needs new query/aggregation logic. Reconciling the sample numbers (e.g., DF-001: S=8, O=4, D=4 → 8×4×4 = 128, matching the shown "Initial RPN") strongly suggests the row's S/O/D values are the *earliest* `RiskEvaluation` per failure mode, and "Current RPN" is pulled from the *latest* evaluation's own (not separately displayed) S/O/D — this needs the first-vs-latest query pattern noted above, plus a decision on whether Current RPN is a stored `result.score` or recomputed. This reconciliation is inferred from the sample data, not stated on-screen, and should be confirmed rather than assumed correct.
- **Table column — Actions ("2/1")**: Derivable from real data, needs new query/aggregation logic. Likely "total actions / completed actions" per failure mode, requiring a join across `RecommendedAction.failure_mode` and (since the FK is nullable both ways) potentially `RecommendedAction.failure_cause` → cause → failure_mode as well.
- **Table column — Status (Open/In Progress/Closed)**: Genuinely new / derived rollup. `FailureMode` has no `status` field in the grounding model. The most plausible real basis is a rollup of the failure mode's linked `RecommendedAction.status` values (e.g., any open → "Open", all completed/verified → "Closed") — this is Tier B (derivable, needs new rollup logic) under that reading, but is Tier D if a literal `FailureMode.status` field is intended instead.
- **RPN Trend chart**: Derivable from real data but the product definition is unclear. Raw `RiskEvaluation.evaluated_at` timestamps exist to build a weekly time series, but it's not obvious why an "Initial RPN (Avg.)" line would trend downward over calendar weeks (a true "initial" baseline shouldn't move); this likely needs a clarified product definition of what "Initial" vs "Current" mean when charted across time, in addition to the query work — flagged as an open question for the architecture review, not assumed correct.
- **Top 5 Highest Current RPN (with Trend arrows)**: Derivable from real data, needs new query/aggregation logic — top-N by latest RPN, plus a new "direction vs previous evaluation" computation for the arrow.
- **Actions by Status donut**: Real field, not yet exposed as this aggregate, with a mapping gap: the donut's four buckets (Open/In Progress/Closed/Cancelled) don't line up 1:1 with `ActionStatus`'s five choices (open/in_progress/completed/verified/cancelled) — "Closed" appears to merge `completed`+`verified`, which is new rollup logic (Tier B).
- **Item Details drawer — S/O/D tiles, Initial/Current RPN**: Same basis as the table columns above.
- **Item Details drawer — Responsible (avatar + name)**: Genuinely new — no backing entity/field exists on `FailureMode` for an assigned person. `ResponsibleRole` is explicitly "a name/description catalog only, not a person roster," so it cannot supply "Marko Kovac." `RiskEvaluation.actor` exists and could plausibly supply "who last evaluated this," but that is a different concept from a persistent "owner" of the failure mode — treat as Tier D unless the intent is simply "latest evaluation's actor," which would make it Tier B.
- **RPN Risk Summary donut (4-tier banding by absolute RPN)**: Derivable from real data, needs new query/aggregation logic — a new classification function bucketing computed RPN by the numeric thresholds shown (≥200 / 100–199 / 50–99 / 1–49), distinct from the existing combined-S×O `classify_severity_occurrence` function.
- **DFMEA Progress bars**: Derivable from real data, needs new query/aggregation logic for each of the three percentages (failure modes with ≥1 linked action; actions completed/verified out of total; high-risk failure modes whose rollup status is resolved).
- **Footer (Database/User/Role/Workspace/Version/System Status)**: Genuinely new — this reads as environment/session/ops metadata rather than FMEA domain data; no corresponding model is implied by the grounding.

**Behavioral logic implied:** Status badges imply a state machine (Open → In Progress → Closed, plus Cancelled for actions) that is only explicitly backed for `RecommendedAction.status`; a parallel state for `FailureMode` itself is implied by the table/drawer but not backed by any real field. RPN "Initial vs Current" implies a snapshot-at-creation vs recompute-on-latest-evaluation behavior, meaning every new `RiskEvaluation` a user logs should trigger the "Current" side of every dependent aggregate (KPI cards, trend chart, donuts) to recompute — this cascading recompute is real-time-dashboard behavior that needs to be designed, not just queried once. Cross-entity relationships implied throughout: `FailureMode` → `Function` → `Product`/`Operation`; `FailureMode` → `FailureEffect`/`FailureCause` → `PreventionControl`/`DetectionControl`; `FailureMode`/`FailureCause` → `RecommendedAction`; `FailureMode` → `RiskEvaluation` (multiple, time-ordered).

**Tier summary:** Tier A — ID, Function, Failure Mode, Effect(s), Cause(s), raw S/O/D ratings, DFMEA Table tab, Function filter. Tier B — DFMEA Items/High Risk/Actions Open/Actions Overdue/Avg RPN KPI cards, Element/Part column (via Function→Product join, with gaps), per-factor S/O/D Class banding, Actions count column, RPN Overview & Action Tracker tabs, RPN Trend chart (pending product definition), Top 5 Highest RPN, Actions by Status donut rollup, RPN Risk Summary donut, DFMEA Progress bars, Status column (if read as an action-status rollup). Tier C — Detection(D) rating (real field, but the per-factor classification scheme shown is well short of what exists). Tier D — Structure Tree, Interface Matrix, Parameter Diagram tabs; Current Controls "Prevention (P)" rating/class (no backing field, changes the RPN factor model); Responsible/owner person on a failure mode; footer environment metadata; Status column (if read as a literal new `FailureMode.status` field rather than a rollup).

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 12 — PFMEA (source: mockup-12-pfmea.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Top bar:** same shell pattern as Mockup 11 — logo block, page title "PFMEA" with purple "Process FMEA" badge, subtitle "Process Failure Mode and Effects Analysis for manufacturing / assembly processes.", Project selector "Project: New Headlamp X1", search "Search (Ctrl+K)", notification bell (badge "9"), help icon, avatar "JD". Action row: "+ New PFMEA Item" (primary blue), "Import", "Export" (dropdown), "Reports" (dropdown), "View Options" (dropdown), "Filters".

**Left sidebar:** identical structure/groups to Mockup 11, except "PFMEA" is the active/highlighted item under FMEA PROJECT (DFMEA, System FMEA, Preventive FMEA (PM-FMEA) shown as siblings, not active).

**Stat/KPI cards row (7 cards):**
1. "PFMEA Items" — 112 — "All items"
2. "High Risk (RPN ≥ 100)" — 18 — "16.1% of total"
3. "Actions Open" — 27 — "24.1% of total"
4. "Actions Overdue" — 7 — "6.3% of total"
5. "Avg. Initial RPN" — 176 — "Before actions"
6. "Avg. Current RPN" — 58 — "After actions"
7. "Last Updated" — 12 May 2025 — "10:30"

**Tabs:** PFMEA Table (active), Process Structure, Interface Matrix, Control Plan Link, Parameter Diagram, RPN Overview, Action Tracker

**Filter/search bar:** search "Search PFMEA items...", dropdowns "Process: All", "Process Step: All", "Status: All", "RPN: All", "Type: All", "More Filters".

**Main table** — columns (checkbox first):
ID | Process Step (subheader "Operation / Work Element") | Process Function (subheader "What is done?") | Failure Mode (subheader "How can it fail?") | Effect(s) (subheader "What is the impact?") | Severity (S): Rating, Class | Occurrence (O): Rating, Class | Detection (D): Rating, Class | Current Controls: P (plain number, no color), D (plain number, no color) | RPN: Initial, Current | Actions | Status

Confirmed exact rows PF-001–PF-010 (of 112 total):
- PF-001 | "10 - Incoming Insp." / "Material Receiving" | Verify material | Wrong material | Process stop, scrap | S 8/H | O 4/M | D 3/L | P 2, D 3 | 96/32 | "1/1" | Open
- PF-002 | "20 - Cutting" / "Cutting Tube" | Cut to length | Wrong length | Assembly issue | S 7/H | O 5/M | D 4/M | P 3, D 3 | 140/60 | "2/2" | In Progress
- PF-003 | "30 - Bending" / "Tube Bending" | Bend to angle | Wrong angle | Fit / function issue | S 8/H | O 4/M | D 4/M | P 3, D 4 | 128/48 | "1/2" | Open
- PF-004 | "40 - Welding" / "MIG Welding" | Join parts | Poor weld | Leakage, strength | S 9/H | O 4/M | D 4/M | P 2, D 3 | 144/54 | "2/3" | In Progress
- PF-005 | "50 - Cleaning" / "Ultrasonic Clean" | Remove contaminants | Contamination left | Paint / coating defect | S 6/M | O 3/L | D 3/L | P 2, D 3 | 54/18 | "1/1" | Closed
- PF-006 | "60 - Coating" / "Powder Coating" | Apply coating | Thin coating | Corrosion / appearance | S 7/H | O 3/L | D 3/L | P 2, D 4 | 63/21 | "1/1" | Open
- PF-007 | "70 - Assembly" / "Sub-Assembly" | Assemble parts | Loose fit | Noise, rattle | S 6/M | O 5/M | D 4/M | P 3, D 3 | 120/45 | "1/1" | In Progress
- PF-008 | "80 - Functional Test" / "Electrical Test" | Verify function | Intermittent | Field failure | S 9/H | O 3/L | D 4/M | P 3, D 4 | 108/36 | "1/2" | Open
- PF-009 | "90 - Visual Insp." / "Final Visual" | Check appearance | Scratch / dent | Customer complaint | S 4/M | O 4/M | D 3/L | P 2, D 3 | 48/16 | "1/1" | Closed
- PF-010 | "100 - Packing" / "Packaging" | Protect product | Wrong packing | Damage in transit | S 5/M | O 3/L | D 3/L | P 2, D 3 | 45/15 | "1/1" | Closed

Note: in every row, Initial RPN exactly equals the displayed S × O × D (e.g., PF-001: 8×4×3=96 ✓; PF-004: 9×4×4=144 ✓), confirming the displayed S/O/D rating row is used for the Initial RPN calc; Current RPN does not equal S×O×D from the same displayed triple, implying it comes from a different (later) evaluation whose own S/O/D are not separately broken out in this table.

**Pagination:** "Showing 1 to 10 of 112 items", page buttons 1(active) 2 3 4 5 … 12, prev/next, and a "10 / page" page-size dropdown.

**Lower-left — "RPN Trend"** line chart: series "Initial RPN (Avg.)" (red) and "Current RPN (Avg.)" (green), X-axis Wk 14/16/18/20/22, Y-axis 0–250; labeled points red ≈214, 192, 178, 160, 148; green ≈98, 85, 74, 63, 58.

**Lower-middle — "Top 5 Highest Current RPN"** mini-table, columns ID/Process Step/Failure Mode/Current RPN/Trend: PF-002 "20 - Cutting"/Wrong length 60 (up), PF-004 "40 - Welding"/Poor weld 54 (up), PF-003 "30 - Bending"/Wrong angle 48 (up), PF-007 "70 - Assembly"/Loose fit 45 (flat), PF-008 "80 - Functional Test"/Intermittent 36 (down).

**Lower-right — "Actions by Status"** donut, center "27 / Total". Legend: Open 15 (55.6%, blue), In Progress 8 (29.6%, orange), Closed 4 (14.8%, green), Cancelled 0 (0.0%, gray).

**Far-right — "Item Details" drawer:**
- "PF-004" with "In Progress" badge (orange).
- Fields: Process Step = "40 - Welding / MIG Welding"; Function = Join parts; Failure Mode = Poor weld; Effect(s) = Leakage, reduced strength.
- Rating tiles: "S 9" (red), "O 4" (orange), "D 4" (orange).
- "Initial RPN" 144 (red, bold), "Current RPN" 54 (green, bold).
- "Responsible": avatar "LK" + "Luka Sterle".
- "Last Updated": 12 May 2025 10:25.
- Link "View Full Details".

**"RPN Risk Summary"** donut, center "112 / Total". Legend: Very High (≥200) red 5 (4.5%); High (100–199) orange 18 (16.1%); Medium (50–99) amber 41 (36.6%); Low (1–49) gray/green 48 (42.9%).

**"PFMEA Progress"** — three progress bars: "Items with Actions" 51%; "Actions Completed" 67%; "High Risk Closed" 39%.

**Footer:** same as Mockup 11 — "Database: OpenEQMS_Local" | "User: Janez Demo (Quality Engineer)" | "Role: Project Owner" | "Workspace: Global" | "Version: 1.0.0" | "System Status" green dot.

### 2. Wireframe & UI/UX

Layout is structurally identical to the DFMEA page (Mockup 11) — same shell, same 7-up KPI row, same tab-strip-then-filter-bar-then-table pattern, same 3-column secondary-chart row, same right-hand stacked drawer (Item Details → RPN Risk Summary → PFMEA Progress), same footer. This strongly implies DFMEA and PFMEA share one generic "FMEA worksheet" page template/component, parameterized by `fmea_type`, rather than being two independently built pages. The main structural difference is column composition: PFMEA promotes "Detection (D)" to a full first-class Rating/Class column (matching S and O), and demotes "Current Controls" to two small plain (uncolored, unclassed) numeric columns "P" and "D" — visually much less prominent than DFMEA's colored Prevention/Detection rating+class pair in the same slot. This suggests, in PFMEA, "Current Controls: P / D" is meant as a lightweight count/reference (e.g., number of linked controls) rather than a risk rating, whereas DFMEA's version is styled as a genuine graded rating — a real inconsistency between the two mockups worth flagging to the design/architecture review rather than resolving unilaterally.

Visual hierarchy and color coding match Mockup 11 exactly: red=High/Critical, amber/orange=Medium, green=Low for Class chips; red/orange/green for RPN Initial/Current numerals; blue=Open, orange=In Progress, green=Closed status badges. The "Process Step" column visually nests two lines per cell (a coded/sequenced primary line, e.g. "40 - Welding", over a smaller secondary line, e.g. "MIG Welding") — implying a two-level label even though the underlying hierarchy may only be one real level deep (see Section 3).

Interaction patterns mirror Mockup 11: row selection populates the Item Details drawer, tabs swap the whole content pane, dropdown filters refine the table, "View Full Details" implies a deeper detail view, and the "Control Plan Link" tab (present here, absent in DFMEA) implies a distinct cross-linking screen to an external/adjacent Control Plan artifact rather than an editable sub-table.

### 3. Architecture & Data Logic

- **PFMEA Items (112) / High Risk / Actions Open / Actions Overdue / Avg Initial & Current RPN / Last Updated KPI cards**: same basis and same tiers as the equivalent DFMEA cards in Mockup 11 (Tier A count scoped to `fmea_type == "process"`; Tier B for High Risk, Actions Overdue, and the RPN averages; Last Updated flagged as unconfirmed pending audit-timestamp field verification).
- **Tabs — PFMEA Table**: Real, already built (per column mapping below).
- **Tabs — Process Structure**: Derivable from real data, needs new query/aggregation logic — unlike DFMEA's "Structure Tree" (which needs a nonexistent Product/element hierarchy), Process/Operation *is* a real two-level hierarchy today (`Process` → `Operation` with `sequence`), so a tree view here is Tier B: real relationships, needs a new nested-tree query/view, not a new model.
- **Tabs — Interface Matrix / Parameter Diagram**: Genuinely new — no backing entity/field exists, per the grounding (no interface/interaction model, no P-Diagram concept anywhere in the codebase), same as DFMEA.
- **Tabs — Control Plan Link**: Genuinely new, and explicitly policy-gated. The grounding calls out a standing rule distinct from an ordinary Tier D gap: "Approved Control Plans are never silently modified — any Control Plan change is a reviewed, human-approved workflow." So this tab is not just "build a Control Plan model" — it needs a deliberate, human-approval-gated change workflow designed in from the start, separate from the normal CRUD scoping given to other new entities in this document.
- **Tabs — RPN Overview / Action Tracker**: same as DFMEA (Tier B / Tier A+B respectively).
- **Filters — Process, Process Step**: Real, already built (`Process.name`/`process_code`, `Operation.name`/`sequence`).
- **Filters — Status, RPN, Type**: same ambiguity/Tier as DFMEA's equivalents.
- **Table column — Process Step ("10 - Incoming Insp." / "Material Receiving")**: Derivable from real data, needs new formatting/query logic for the primary line (`f"{Operation.sequence} - {Operation.name}"`, Tier A/B). The secondary line is ambiguous: if it is `Operation.process.name` (the parent `Process`'s name) reused as a subtitle, it's Tier B (real relationship, needs join/formatting); if a distinct "work element" concept below Operation is intended (a third hierarchy level), that is genuinely new — no such model exists in the grounding.
- **Table column — Process Function**: Real, already built (`FailureMode.function.name`, via `Function.operation` FK).
- **Table column — Failure Mode**: Real, already built (`FailureMode.name`).
- **Table column — Effect(s)**: Real, already built (`FailureMode.effects` → `FailureEffect.name`).
- **Table column — Severity (S) / Occurrence (O) / Detection (D) Rating**: Real, already built (`RiskEvaluation.severity` / `.occurrence` / `.detection`), most plausibly the earliest evaluation per failure mode (see Initial-RPN reconciliation in Section 1).
- **Table column — S/O/D Class badges**: Real field but far short of what's shown — same gap as DFMEA: only a combined S×O banding function (`classify_severity_occurrence`) exists; there is no confirmed per-factor S-only/O-only/D-only banding logic, so each Class chip here needs new threshold logic defined.
- **Table column — Current Controls: P / D (plain counts)**: Derivable from real data, needs new query/aggregation logic. Most plausible reading (see Section 2): a count of `PreventionControl` and `DetectionControl` records reachable from this failure mode via its `causes` (`FailureCause.prevention_controls` / `.detection_controls`, aggregated across all causes of the failure mode) — a real relationship chain, but requires new aggregation since controls attach to `FailureCause`, not directly to `FailureMode`.
- **Table column — RPN Initial / Current**: Derivable from real data, needs new query/aggregation logic — same first-vs-latest `RiskEvaluation` pattern as DFMEA, empirically consistent here (Initial = S×O×D of the displayed row for all 10 sample rows).
- **Table column — Actions ("1/1", "2/2", "1/2", etc.)**: Derivable from real data, needs new query/aggregation logic — total vs. completed `RecommendedAction` rows linked (directly or via `failure_cause`) to the failure mode.
- **Table column — Status**: Genuinely new / derived rollup — same gap as DFMEA (`FailureMode` has no `status` field in the grounding; most plausible basis is a rollup over linked `RecommendedAction.status`).
- **RPN Trend / Top 5 Highest Current RPN / Actions by Status donut / RPN Risk Summary donut / PFMEA Progress bars**: same basis and same tiers as the DFMEA equivalents in Mockup 11 (Tier B throughout, with the RPN Trend chart's "Initial vs time" semantics flagged as an open product-definition question, and Actions-by-Status needing a `completed`+`verified` → "Closed" rollup mapping).
- **Item Details — Responsible (avatar + name)**: same Tier D/B ambiguity as DFMEA — no person-owner field exists on `FailureMode`; `RiskEvaluation.actor` is the closest real candidate if "Responsible" means "who last evaluated this."
- **Footer**: Genuinely new, same as DFMEA — reads as environment/session metadata, not FMEA domain data.

**Behavioral logic implied:** Identical state-machine and cascading-recompute implications as DFMEA (Section 3 of Mockup 11 applies verbatim). Additionally, the presence of a distinct "Control Plan Link" tab implies a cross-entity, cross-workflow relationship between a PFMEA item (specifically its current detection/prevention controls) and an external Control Plan record, gated by an approval workflow rather than free CRUD — this is a materially different behavior class from the rest of the new entities discussed here and should be scoped separately in any future architecture review.

**Tier summary:** Tier A — Process Function, Failure Mode, Effect(s), raw S/O/D ratings, PFMEA Table tab, Process/Process Step filters. Tier B — KPI cards (except plain item count), Process Step column formatting, Process Structure tab, S/O/D Class banding, Current Controls P/D counts, RPN Initial/Current, Actions count column, RPN Overview & Action Tracker tabs, RPN Trend/Top-5/Actions-by-Status/RPN Risk Summary/Progress-bar widgets, Status column (if a rollup). Tier C — none distinctly beyond what's noted as Tier B/D above (the D rating itself is Tier A; it's only the classing that's short). Tier D — Interface Matrix and Parameter Diagram tabs; the "work element" third hierarchy level (if intended as more than `Process.name`); Responsible/owner person field; footer environment metadata; and, called out separately from ordinary Tier D gaps, the Control Plan Link tab's approval-gated change workflow.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 13 — Change Impact (source: mockup-13-change-impact.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Top bar:** logo block, page title "Change Impact" (no type badge, unlike Mockups 11/12), subtitle "Identify, analyze and track the impact of design or requirement changes on FMEA and related items.", Project selector "Project: New Headlamp X1", search "Search (Ctrl+K)", notification bell (badge "3"), help icon, avatar "JD". Action row: "+ New Change" (primary blue), "Import", "Export" (dropdown), "Reports" (dropdown), "Filters" (icon+label — no "View Options" here).

**Left sidebar:** same groups as prior mockups; "Change Impact" is the active/highlighted item under VALIDATION & CHANGE (siblings: Evidence & Tests, Validation Trajectory).

**Stat/KPI cards row (7 cards):**
1. "Total Changes" — 24 — "All time" (refresh/circular-arrows icon)
2. "Under Analysis" — 8 — "33.3%" (hourglass icon, purple)
3. "Impacts Identified" — 18 — "75.0%" (warning-triangle icon, orange)
4. "High / Critical Impact" — 7 — "29.2%" (target/circle icon, red)
5. "Actions Required" — 15 — "62.5%" (flag icon, green)
6. "Closed" — 9 — "37.5%" (checkmark icon, green)
7. "Last Updated" — 12 May 2025 — "10:35" (calendar icon)

**Tabs:** Change Log (active), Impact Matrix, Affected FMEA Items, Action Plan, Change History

**Filter/search bar:** search "Search changes...", dropdowns "Change Type: All", "Source: All", "Status: All", "Impact Level: All", a date-range picker "01/01/2024 – 12/05/2025", "More Filters".

**Main table** — columns (checkbox first): ID | Change Title | Type | Source | Reason | Impact Level | Affected DFMEA | Affected PFMEA | Status | Owner | Date | Actions (eye icon + "…" overflow menu)

Confirmed exact rows CHG-024 down to CHG-017 (8 of 24 total):
- CHG-024 | "Lens material change PC → PC+ASA" | Design | Engineering | Improve UV resistance | High (red) | 12 | 9 | Under Analysis (purple) | avatar "MK" | 12 May 2025
- CHG-023 | "LED supplier change" | Supplier | Procurement | Supply continuity | Medium (orange) | 6 | 8 | In Progress (orange) | "AN" | 08 May 2025
- CHG-022 | "Lens geometry update (Optical performance)" | Design | Engineering | Improve light pattern | High (red) | 18 | 14 | Under Analysis (purple) | "LK" | 06 May 2025
- CHG-021 | "Change in legal requirement ECE R112" | Regulatory | Regulatory | New requirement | Critical (dark red) | 24 | 17 | In Progress (orange) | "JD" | 02 May 2025
- CHG-020 | "PCB layout revision" | Design | Engineering | Reduce EMI | Medium (orange) | 9 | 7 | Under Analysis (purple) | "PT" | 28 Apr 2025
- CHG-019 | "Welding parameter update" | Process | Manufacturing | Quality improvement | Low (green) | — (dash/none) | 11 | In Progress (orange) | "MK" | 25 Apr 2025
- CHG-018 | "Connector type change" | Design | Engineering | Space optimization | High (red) | 10 | 12 | Open (blue) | "LK" | 20 Apr 2025
- CHG-017 | "Coating specification change" | Material | Engineering | Corrosion resistance | Medium (orange) | 7 | 9 | Open (blue) | "AN" | 18 Apr 2025

**Pagination:** "Showing 1 to 8 of 24 changes", page buttons 1(active) 2 3 … next.

**Bottom row, 4 panels:**
1. "Impact Level Distribution" donut, center "24 / Total". Legend: Critical red 2 (8.3%), High orange 5 (20.8%), Medium amber 9 (37.5%), Low green 6 (25.0%), None gray 2 (8.3%).
2. "Change Type Distribution" donut, center "24 / Total". Legend: Design blue 13 (54.2%), Process purple 3 (12.5%), Supplier orange 3 (12.5%), Regulatory red 2 (8.3%), Other gray 3 (12.5%).
3. "Changes Over Time" line chart, three series "Identified" (blue), "Closed" (green), "Open" (orange), X-axis Dec 24/Jan 25/Feb 25/Mar 25/Apr 25/May 25, Y-axis gridlines to ~20 though the Identified line's endpoint is labeled 24; general shape is three upward-trending lines over the 6 months, Identified highest (ending ≈24), Open in the middle, Closed lowest (starting ≈2, ending ≈15) — exact interior values are small and not all fully legible, so only the endpoints and general ordering are stated with confidence.
4. "Top Affected Areas" horizontal bar list (not a full chart, a labeled bar list) with caption "(Number of changes)": Optical Performance 10, Housing/Enclosure 8, Electrical 7, Mechanical/Assembly 6, Thermal Management 4, Other 3.

**Far-right — "Change Details" drawer** (with "×" close icon):
- "CHG-022" with "High Impact" badge (red).
- Fields: Title = "Lens geometry update (Optical performance)"; Type = Design Change; Source = Engineering; Reason = Improve light pattern and uniformity; Description = "Updated lens curvature and thickness to improve beam pattern and uniformity."; Status = "Under Analysis" (purple badge); Impact Level = "High" (red badge); Owner = avatar "LK" + "Luka Sterle"; Date Identified = 06 May 2025 14:20; Last Updated = 12 May 2025 10:35.
- Sub-panel "Summary": four mini-stats in a row — "DFMEA Items" 18, "PFMEA Items" 14, "High/Critical" 5, "Actions" 9.
- Link "View Full Details" (with icon).

**Footer:** same shell as prior mockups.

### 2. Wireframe & UI/UX

Same overall app-shell template as Mockups 11/12: fixed sidebar, top bar with title/subtitle/global controls, 7-up KPI row, tab strip, filter bar, primary table, pagination, then a secondary-widgets row (here 4 panels instead of 3), plus a right-hand drawer. Unlike Mockups 11/12, the drawer here is single (no stacked RPN Risk Summary/Progress panels below it) but contains an embedded 4-cell mini-stat "Summary" sub-panel of its own — this is a smaller, single-purpose detail drawer rather than a 3-panel stacked rail.

Color coding: Impact Level uses a 5-step red family (Critical = darkest/most saturated red, High = red, Medium = orange/amber, Low = green, None = gray) — a different, more granular scale than the DFMEA/PFMEA H/M/L three-step scheme, worth noting as its own severity vocabulary. Status badges use purple ("Under Analysis") in addition to the blue/orange/green/gray already seen elsewhere — purple appears to be reserved for an "in analysis, not yet actioned" state distinct from "In Progress" (orange, implying action work has started) and "Open" (blue, implying logged but not yet analyzed) — a 3+ state progression (Open → Under Analysis → In Progress → Closed) is implied though not explicitly diagrammed.

Interaction pattern: clicking a table row (or its "eye" icon) populates the Change Details drawer, mirroring the DFMEA/PFMEA pattern; the "…" overflow menu per row implies row-level actions (edit/delete/duplicate, not shown). "Affected DFMEA"/"Affected PFMEA" columns showing plain counts (with a "—" dash for zero/none, as in CHG-019) strongly imply each Change can be linked to zero or more DFMEA and PFMEA items, and that the count is clickable/navigable toward the "Affected FMEA Items" tab. The "Impact Matrix" tab name implies a cross-tab visualization (e.g., changes × FMEA items, or changes × impact level) distinct from the flat Change Log table.

### 3. Architecture & Data Logic

The grounding is explicit and unambiguous here: **no `Change` entity exists anywhere in the codebase.** The closest real models — `FMEARevision`/`FMEADocument` — track FMEA-*document*-level revisions (e.g., "this FMEA document went from v1.0 to v1.1"), which is a fundamentally different concept from an external design/requirement change with its own lifecycle and downstream impact-tracking against FailureModes/Effects/Causes/Actions. They are explicitly called out as not a valid substitute, so almost everything on this page is Tier D.

- **Every KPI card (Total Changes, Under Analysis, Impacts Identified, High/Critical Impact, Actions Required, Closed, Last Updated)**: Genuinely new — no backing entity/field exists. All require a new `Change` model to even begin counting.
- **All 5 tabs (Change Log, Impact Matrix, Affected FMEA Items, Action Plan, Change History)**: Genuinely new — each implies its own view over the same non-existent `Change` model (Change History in particular implies the new model needs its own revision/audit trail, separate from `FMEARevision`).
- **Filters (Change Type, Source, Status, Impact Level, Date Range)**: Genuinely new — each implies a field/choice-set on the proposed `Change` model (see proposed schema below).
- **Table columns — ID, Change Title, Type, Source, Reason, Impact Level, Status, Owner, Date**: Genuinely new — direct fields on a proposed `Change` model.
- **Table columns — Affected DFMEA / Affected PFMEA (counts)**: Genuinely new — implies a many-to-many (or through-table) relationship from `Change` to `FailureMode` (or to `FMEA`/`Product`/`Process`, depending on the intended granularity of "affected"), which does not exist today in any form.
- **Impact Level Distribution / Change Type Distribution donuts, Changes Over Time line chart, Top Affected Areas bar list**: Genuinely new — all are aggregations over the proposed `Change` model and its proposed impact-area/linkage fields; none has any real data to aggregate today.
- **Change Details drawer (all fields, including the Summary mini-stats DFMEA Items/PFMEA Items/High-Critical/Actions)**: Genuinely new — the Summary sub-panel in particular implies the proposed `Change`↔`FailureMode` linkage must also support rolling up each linked failure mode's own risk level and action count, compounding the new-model surface.

**Proposed (not authorized) new entity**, named descriptively as implied by the mockup, marked explicitly as proposed rather than fact: a `Change` model with fields such as — `title`, `change_type` (choice: Design / Process / Supplier / Regulatory / Material / Other), `source` (free text or choice: Engineering / Procurement / Manufacturing / Regulatory / etc.), `reason` (short text), `description` (long text), `impact_level` (choice: Critical / High / Medium / Low / None), `status` (choice, implying a state machine: Open → Under Analysis → In Progress → Closed, plus possibly Cancelled — not confirmed anywhere, proposed only), `owner` (FK to a person — same "no person-roster model" gap noted in Mockups 11/12 applies here too), `date_identified` (datetime), `updated_at` (datetime), and a many-to-many/through relationship to `FailureMode` (or a broader linkage to `FMEA`/`Product`/`Process`) to back the "Affected DFMEA/PFMEA" counts and the Impact Matrix/Affected FMEA Items tabs. A full scoping (required fields, who can create/edit, validation rules such as "Impact Level required before status can leave Under Analysis," status-transition rules, and whether Change rows can themselves spawn `RecommendedAction` rows to back "Action Plan"/"Actions Required") is out of scope for this cataloging pass and would need its own architecture review.

**Behavioral logic implied:** A change-management lifecycle is strongly implied (identification → analysis → impact assessment → action planning → closure), gated by an Impact Level classification that appears to influence downstream urgency (High/Critical Impact is its own KPI, separate from plain Impact Level counts). The "Affected DFMEA/PFMEA" linkage implies that creating or updating a Change should be able to fan out and flag/annotate specific `FailureMode` rows in the DFMEA/PFMEA worksheets (a cross-page notification or badge is implied but not shown in this mockup) — this cross-entity fan-out is itself new behavior with no current analog. "Action Plan" as a tab name implies Changes can generate or link to `RecommendedAction` rows, which — if so — is a plausible connection to real data (`RecommendedAction` exists) but the linkage itself is new (no FK from `RecommendedAction` to any change-like entity exists today).

**Tier summary:** Tier D — the entire page. There is no Tier A, B, or C content on this mockup: every widget, column, filter, chart, and drawer field ultimately depends on a `Change` entity (and its linkage to `FailureMode`/`FMEA`) that does not exist in any form in the current domain model, and the nearest real analogs (`FMEARevision`/`FMEADocument`) are explicitly a different concept, not a valid substitute.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 14 — Validation Trajectory (source: mockup-14-validation-trajectory.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Top bar:** logo block, page title "Validation Trajectory", subtitle "Plan, execute and track validation activities across FMEA items and product/process lifecycle.", Project selector "Project: New Headlamp X1", search "Search (Ctrl+K)", notification bell (badge "2"), help icon, avatar "JD". Action row: "+ New Validation" (primary blue), "Import", "Export" (dropdown), "Reports" (dropdown), "Filters".

**Left sidebar:** same groups as prior mockups; "Validation Trajectory" is the active/highlighted item under VALIDATION & CHANGE (siblings: Evidence & Tests, Change Impact).

**Stat/KPI cards row (7 cards):**
1. "Total Validations" — 68 — "All time" (checklist icon)
2. "Planned" — 26 — "38.2%" (calendar icon, purple)
3. "In Execution" — 18 — "26.5%" (play-triangle icon, purple/blue)
4. "Completed" — 20 — "29.4%" (checkmark icon, green)
5. "Overdue" — 4 — "5.9%" (clock icon, red/orange)
6. "Linked to FMEA Items" — 56 — "82.4%" (link/chain icon, blue)
7. "Last Updated" — 12 May 2025 — "10:45" (calendar icon)

**Tabs:** Trajectory View (active), Validation Table, Validation Plan, Test Plan, Coverage Matrix, History

**Filter/search bar (no free-text search box shown here, only dropdowns):** "FMEA Type: All", "FMEA Item: All", "Validation Type: All", "Status: All", "Lifecycle Phase: All", a date-range picker "01/01/2024 – 12/05/2025", "More Filters".

**"Trajectory Timeline"** — a swim-lane style chart, the page's signature widget:
- Six lifecycle-phase column headers, each with an icon and a "completed/total" fraction beneath it: "Concept" (green check icon) 4/4; "Design" (blue check icon) 8/10; "Prototype" (purple icon) 6/8; "Verification" (orange check icon) 5/7; "Validation" (teal check-in-box icon) 4/6; "Release" (blue icon) 3/3.
- Row list, columns ID | Validation / Test | Linked FMEA Item(s), then a horizontal 6-node status path spanning the six phase columns, for VAL-001 through VAL-010 (of 68 total; only 10 rows visible before scrolling):
  - VAL-001 | Optical Performance Test | DF-001, DF-002 | all 6 nodes green/completed (fully done through Release)
  - VAL-002 | Thermal Cycling Test | DF-003, PF-004 | green through Concept/Design/Prototype, blue "in execution" node at Verification, dashed orange line to an orange diamond node at Validation, dashed gray line to an open/gray circle at Release
  - VAL-003 | Vibration Durability Test | PF-007 | green through Concept/Design/Prototype/Verification, blue node at Validation, gray open circle at Release
  - VAL-004 | Ingress Protection Test | DF-004, PF-005 | green through Concept/Design/Prototype/Verification, dashed to a red circle with "!" (Overdue) at Validation, dashed gray to open circle at Release
  - VAL-005 | EMC Immunity Test | DF-006, PF-010 | green through Concept/Design/Prototype, orange nodes at Verification/Validation/Release
  - VAL-006 | Light Pattern Validation | DF-001 | green through Concept/Design/Prototype/Verification, blue node at Validation, gray open circle at Release
  - VAL-007 | Lens Material Verification | DF-002 | blue nodes at Concept/Design, orange nodes at Prototype/Verification/Validation/Release
  - VAL-008 | Welding Strength Test | PF-004 | orange nodes at Concept/Design/Prototype/Verification, gray open circles at Validation/Release
  - VAL-009 | Corrosion Resistance Test | PF-008 | orange nodes at Concept/Design/Prototype/Verification, gray open circles at Validation/Release
  - VAL-010 | Final Product Validation | "All Critical Items" | green through all phases, ending in a filled diamond marker at Release (milestone)
- Legend row beneath the timeline: green circle+check = "Completed"; blue circle = "In Execution"; orange diamond = "Planned"; a square/dashed icon = "Not Started"; a filled diamond = "Milestone"; red circle+"!" = "Overdue".

**Far-right — "Validation Details" drawer:**
- "VAL-002" with "In Execution" badge (blue).
- Fields: Validation Name = Thermal Cycling Test; Validation Type = Reliability Test; Linked FMEA Items = DF-003, PF-004; Objective = "Verify headlamp performance under thermal cycling"; Method = IEC 60068-2-14; Acceptance Criteria = "No functional failure, no degradation > 10%"; Planned Start = 28 Apr 2025; Planned Finish = 30 May 2025; Actual Start = 28 Apr 2025; Responsible = avatar "MK" + "Marko Kovac"; Status = "In Execution" badge (blue); Progress = a horizontal progress bar labeled "60%"; Evidence = two small file-type icons + "2 files"; Test Plan = "TP-002" (blue link, with an external-link icon); Last Updated = 12 May 2025 10:30.
- Link "View Full Details".

**Bottom row, 3 panels + 1 list:**
1. "Validations by Status" donut, center "68 / Total". Legend: Completed green 20 (29.4%), In Execution blue 18 (26.5%), Planned orange 26 (38.2%), Overdue red 4 (5.9%).
2. "Validation Type Distribution" donut, center "68 / Total". Legend: Performance blue 16 (23.5%), Reliability purple 18 (26.5%), Safety green 10 (14.7%), Compliance orange 8 (11.8%), Durability light-blue/gray 9 (13.2%), Other gray 7 (10.3%).
3. "Validation Coverage (by FMEA Type)" horizontal bar chart, X-axis 0%–100%, caption "Coverage = Completed / Total Linked Items": DFMEA blue bar 32/38 (84.2%); PFMEA green bar 18/22 (81.8%); System FMEA purple bar 6/8 (75.0%); PM-FMEA gray bar 0/2 (0.0%).
4. "Upcoming Validations" list, columns ID | Validation/Test | Planned Start | FMEA Item(s): VAL-011 Drop Test 15 May 2025 PF-006; VAL-012 Chemical Resistance 22 May 2025 DF-002; VAL-013 Photometric Test 27 May 2025 DF-001; VAL-014 Connector Retention Test 02 Jun 2025 PF-009. Link "View All (26)".

**Footer:** same shell as prior mockups.

### 2. Wireframe & UI/UX

Overall shell matches the other pages (sidebar, top bar, 7-up KPI row, tab strip, filter bar, footer), but the primary content widget is structurally unique: instead of a conventional data grid, "Trajectory Timeline" is a Gantt-like/swim-lane visualization — an ID/name/linked-items list on the left acting as row labels, paired with a 6-stage horizontal status path per row on the right, and shared phase-column headers with aggregate fraction counts running across the top like a mini funnel. This is a materially more complex custom chart than anything in Mockups 11–13 (not a standard donut/line/bar) — it resembles a horizontal multi-stage stepper repeated per row, color- and shape-coded per node, with dashed segments distinguishing "not yet reached" stretches of the path from solid "already traversed" stretches.

Color/shape coding: green filled circle + check = Completed (phase fully done for that item); blue filled circle + check = In Execution (the item's current phase); orange diamond + check = Planned (scheduled but this specific phase not yet reached, or in a lighter "on track" planned state); gray open circle = Not Started; red filled circle + "!" = Overdue (a flag distinct from plain "planned/not started," implying a deadline was missed at that specific phase); a larger filled diamond = a Milestone marker (used once, at VAL-010's Release phase, implying certain validations are flagged as program milestones distinct from ordinary validations). Line segments between nodes are solid when connecting two "settled" (completed/in-execution) states and dashed when projecting into "not yet happened" future phases — a visual device implying a plan vs. actual distinction along the row.

The right-hand drawer here is richer than in prior mockups — it mixes label/value fields with a progress bar, file-attachment references, and an outbound link to a "Test Plan" (TP-002), implying validations can be linked one level deeper into their own execution/test-plan documents. Interaction patterns implied: clicking a row (or a specific phase node) in the timeline likely opens/updates this drawer; the phase-column headers likely double as a phase filter (consistent with the "Lifecycle Phase: All" dropdown in the filter bar); "View All (26)" on Upcoming Validations implies a link to a filtered/sorted view (likely the Validation Table tab); the Evidence "2 files" implies clicking opens a file list/upload dialog.

### 3. Architecture & Data Logic

Per the grounding, today's closest real model is `Evidence`/`EffectivenessVerification` (FK to `RecommendedAction`, minimal fields), explicitly noted as "much smaller than what a rich Validation Trajectory page would need." So this page sits mostly in Tier D, with a narrow Tier C toehold where the existing model touches the same conceptual space.

- **All 7 KPI cards (Total Validations, Planned, In Execution, Completed, Overdue, Linked to FMEA Items, Last Updated)**: Genuinely new — no `Validation` entity exists to count, bucket, or aggregate. `EffectivenessVerification` is keyed to `RecommendedAction`, not to a lifecycle-phase-aware validation record, so it cannot supply "Planned/In Execution/Overdue" states or a 6-phase breakdown.
- **All 6 tabs (Trajectory View, Validation Table, Validation Plan, Test Plan, Coverage Matrix, History)**: Genuinely new — each is a different view over the same non-existent `Validation`/`TestPlan` model(s); "Test Plan" as its own tab plus a "TP-002" link in the drawer implies a *second* new entity (a Test Plan) distinct from the Validation record itself.
- **Filters (FMEA Type, FMEA Item, Validation Type, Status, Lifecycle Phase, Date Range)**: Genuinely new — each implies a field/choice-set on the proposed `Validation` model.
- **Trajectory Timeline — phase headers with completed/total fractions**: Genuinely new — requires a `Validation` model with a lifecycle-phase-aware status (a 6-stage state per item, not just a single overall status), which is exactly the "lifecycle-phase-tracking entity" the grounding says has zero existing groundwork.
- **Trajectory Timeline — per-row 6-node status path (Completed/In Execution/Planned/Not Started/Overdue/Milestone)**: Genuinely new — this needs, at minimum, a per-validation record of status-per-phase (either 6 discrete phase-status fields, or a related "phase history" child table), plus a `is_milestone` flag. None of this exists today in any form.
- **Trajectory Timeline — Linked FMEA Item(s) column**: Genuinely new relationship — implies a many-to-many from the proposed `Validation` model to `FailureMode` (seen linking to both DF-xxx and PF-xxx codes, i.e., across FMEA types), which does not exist today; `EffectivenessVerification`'s only real FK is to `RecommendedAction`, not to `FailureMode` directly.
- **Validation Details drawer — Validation Name, Type, Objective, Method, Acceptance Criteria, Planned/Actual Start-Finish dates, Responsible, Status, Progress %**: Genuinely new — none of these fields exist on `Evidence`/`EffectivenessVerification` today; `RecommendedAction` (the thing `EffectivenessVerification` is keyed to) has `responsible_role` (a role catalog FK, not a person) and `due_date`, but nothing resembling Planned Start/Finish, Actual Start, Method, or Acceptance Criteria.
- **Validation Details drawer — Responsible (avatar + person name)**: Genuinely new — same person-vs-role-catalog gap noted in Mockups 11–13 (`ResponsibleRole` is a catalog, not a person roster).
- **Validation Details drawer — Evidence "2 files"**: Real field, not yet exposed / far short of what's shown. `Evidence` is a real model name in the grounding, so a *count* of evidence records linked could be Tier B if `Evidence` gains a proper FK to the new `Validation` entity — but the grounding separately notes "no image/file storage or image-annotation capability anywhere," so the file-attachment/download aspect implied by "2 files" (as opposed to just a count of Evidence rows) is genuinely new regardless.
- **Validation Details drawer — Test Plan link (TP-002)**: Genuinely new — implies a second new entity (`TestPlan`) plus a FK/relationship from `Validation` to it.
- **Validations by Status / Validation Type Distribution donuts, Validation Coverage bar chart, Upcoming Validations list**: Genuinely new — all are aggregations over the proposed `Validation` model; none has real data to aggregate today. The Coverage bar chart specifically implies the proposed `Validation`↔`FailureMode` linkage must be groupable by the linked failure mode's parent `FMEA.fmea_type`, compounding the new-model surface (a query across two levels of a not-yet-existent relationship).

**Proposed (not authorized) new entities**, marked explicitly as proposed: a `Validation` (or `ValidationTest`) model with fields such as `name`, `validation_type` (choice: Performance / Reliability / Safety / Compliance / Durability / Other), `objective`, `method`, `acceptance_criteria`, `planned_start`/`planned_finish`/`actual_start`/`actual_finish` dates, `responsible` (person — same gap as elsewhere), `overall_status` (choice implying a state machine: Planned → In Execution → Completed, plus Overdue as a computed/flagged state rather than a stored one, similar to the Actions-Overdue pattern in Mockups 11/12), a `progress_percent`, a many-to-many to `FailureMode`, and a `is_milestone` flag; plus six phase-status child fields or a related `ValidationPhaseStatus` child table (one row per phase per validation, holding phase name, status, and dates) to back the Trajectory Timeline; plus a separate `TestPlan` model (referenced but not detailed by this mockup) that `Validation` would link to. A full scoping (creation flow, required fields, who can transition status, validation rules for phase-order enforcement, and how "Overdue" is computed/flagged) is out of scope for this cataloging pass.

**Behavioral logic implied:** A strict phase-order state machine across 6 lifecycle phases (Concept → Design → Prototype → Verification → Validation → Release) is implied per validation record, with the current phase shown "in execution" (blue) and later phases either "planned" (orange, scheduled) or "not started" (gray). The Overdue marker (red, VAL-004 at the Validation phase) implies a deadline-vs-today comparison per phase, computed rather than stored — mirroring the Actions-Overdue pattern already noted for Mockups 11/12. The Milestone flag (VAL-010) implies certain validations gate a broader program checkpoint, which could plausibly cascade into other pages (e.g., blocking a Release-phase Change from closing) but no such cross-entity behavior is shown here. Cross-entity relationships implied: `Validation` → `FailureMode` (M2M, cross-FMEA-type), `Validation` → `TestPlan` (FK), `Validation` → `Evidence` (relationship, plus new file-storage capability), and (not shown but implied by "Test Plan" as a tab) `Validation` → `RecommendedAction` possibly via the existing `EffectivenessVerification` bridge — worth exploring in a future review rather than assumed here.

**Tier summary:** Tier C — the single narrow case of "Evidence" as a linked-record *count*, since `Evidence` is a real model name today even though it isn't wired to a lifecycle-aware `Validation` entity and carries none of the file-attachment behavior implied by "2 files." Tier D — everything else on this page: all KPI cards, all 6 tabs, all filters, the entire Trajectory Timeline widget (phase headers, per-row 6-node status path, milestone/overdue markers), the full Validation Details drawer (Name/Type/Objective/Method/Acceptance Criteria/dates/Responsible/Status/Progress/Test Plan link), and all four bottom aggregation widgets. There is no Tier A or Tier B content on this mockup.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 15 — Failure Modes (source: mockup-15-failure-modes.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Top bar:** logo block, page title "Failure Modes" with a small circled "?" info icon beside it, subtitle "Manage, classify and analyze potential and real failure modes with links to catalog and complaints.", Project selector "Project: New Headlamp X1 - DFMEA", search "Search (Ctrl+K)", notification bell (badge "3"), help icon, avatar "JD". Action row: "+ New Failure Mode" (primary blue), "Import", "Export" (dropdown), "Reports" (dropdown), "View Options" (dropdown), "Filters".

**Left sidebar:** same groups as prior mockups; "Failure Modes" is the active/highlighted item under FMEA ANALYSIS (siblings: Effects, Causes, Prevention Controls, Detection Controls, Actions).

**Stat/KPI cards row (6 cards — one fewer than the DFMEA/PFMEA pages):**
1. "Failure Modes" — 186 — "All items" (document icon, blue)
2. "High Risk (RPN ≥ 100)" — 42 — "22.6% of total" (shield icon, orange)
3. "From Complaints" — 38 — "20.4% (real cases)" (magnifier/search icon, red)
4. "Linked to Actions" — 134 — "72.0%" (flag icon, purple)
5. "Catalog Entries" — 2,456 — "Available" (book icon, teal)
6. "Last Updated" — 12 May 2025 — "10:45" (calendar icon)

**Tabs:** Failure Modes List (active), Failure Mode Matrix, Error Catalog, Complaint Link, Trend & Analysis

**Filter/search bar:** search "Search failure modes...", dropdowns "FMEA Type: All", "Function: All", "Element: All", "Source: All", "Severity: All", "Occurrence: All", "More Filters". A second toolbar row beneath it: "AI Suggest" (sparkle icon, purple-accented), "Link to Catalog", "Link to Complaint", "Quick Add".

**Main table** — columns (checkbox first): ID | Failure Mode (each row also carries a small orange warning-triangle icon) | Description | Function / Element | Source | Catalog | Complaints | S | O | D | RPN | Trend (arrow icon) | Status | Actions (row of small icon buttons)

Confirmed exact rows FM-001–FM-010 (of 186 total):
- FM-001 | Lens crack | "Crack in outer lens leading to reduced light output" | Provide illumination / Housing | "Design + Compl." (two-part badge) | EC-1204 | 7 (red, bold) | S9 O5 D4 | RPN 180 (red) | trend up | Open
- FM-002 | Water ingress | Water inside housing | Protect components / Seal | Catalog (green badge) | EC-1456 | 12 (red) | S8 O6 D4 | RPN 192 (red) | trend up | Open
- FM-003 | LED not light | LED no illumination | Generate light / LED Module | Complaints (red badge) | EC-0987 | 24 (red) | S9 O4 D3 | RPN 108 (orange) | trend up | Open
- FM-004 | Overheating | Excess temperature | Dissipate heat / Heatsink | Design (blue badge) | EC-0765 | 3 | S7 O5 D4 | RPN 140 (orange) | trend up | In Progress
- FM-005 | Condensation | Fogging on lens | Protect components / Housing | Catalog (green badge) | EC-1332 | 15 (red) | S7 O6 D4 | RPN 168 (red) | trend up | Open
- FM-006 | Loose connector | Connector loosen | Provide electrical / Connector | Complaints (red badge) | EC-2011 | 18 (red) | S8 O5 D5 | RPN 200 (red) | trend up | Open
- FM-007 | PCB failure | Electronic failure | Control electronics / Driver | Design (blue badge) | EC-0678 | 5 | S8 O4 D4 | RPN 128 (orange) | trend arrow (direction not fully certain — appears to differ from the others; not confidently legible) | In Progress
- FM-008 | Color mismatch | Optical deviation | Provide appearance / Lens | Complaints (red badge) | EC-1420 | 9 | S6 O5 D6 | RPN 180 (red) | trend arrow (not fully certain, appears different from the up-arrows elsewhere) | Open
- FM-009 | Noise / Rattle | Acoustic noise | Mechanical fixation / Bracket | Catalog (green badge) | EC-1888 | 6 | S5 O6 D6 | RPN 180 (red) | trend up | Open
- FM-010 | Software bug | Incorrect light control | Control software / ECU | Complaints (red badge) | EC-2105 | 11 (red) | S8 O5 D5 | RPN 200 (red) | trend up | Open

Row FM-001 is checked (its checkbox is ticked) and its data is mirrored in the open detail drawer. Source badges seen: "Design" (blue), "Catalog" (green), "Complaints" (red), and a combined "Design + Compl." two-tone badge (FM-001 only). Status badges: "Open" (blue), "In Progress" (orange).

**Pagination:** "Showing 1 to 10 of 186 failure modes", page buttons 1(active) 2 3 4 5 … 19, next, plus a "10 / page" page-size dropdown.

**Bottom row, 4 panels:**
1. "Source Distribution" donut, center "186 / Total". Legend: Design blue 68 (36.6%), Complaints red 38 (20.4%), Catalog green 46 (24.7%), Suppliers olive/yellow 18 (9.7%), Other gray 16 (8.6%).
2. "Severity vs Occurrence" scatter/bubble chart. X-axis "Occurrence (O)" 1–10, Y-axis "Severity (S)" with gridline labels 1/4/7/10/13/16 (an unusual, non-standard axis scale for a 1–10 severity rating — reported as shown, not corrected). Bubbles are colored green/orange/red (apparently low/medium/high risk) and vary in size (likely encoding RPN or a count of failure modes at that S/O combination). One bubble is highlighted with a red circle/halo and a callout label "FM-001 / RPN: 180", pointing to a bubble around O≈5, S≈9.
3. "Top Failure Mode Categories" horizontal bar chart: Optical blue 42 (22.6%), Mechanical blue 36 (19.4%), Electrical blue 28 (15.1%), Thermal blue 24 (12.9%), Software green 18 (9.7%), Chemical green 14 (7.5%), Other gray 24 (12.9%).
4. "Trend (Real Complaints)" line chart, two series "Design FM" (blue) and "Complaint FM" (orange), X-axis Jan–May. Both lines trend upward over the period; a few point labels are legible (Jan starts low, around 12 for one series; the two lines end close together around the low-to-mid 30s by May, with the orange "Complaint FM" line appearing to end at/near the top around 38) — exact interior values are small text and not all confidently legible, so only the general upward trend and approximate endpoints are stated.

**Far-right — "Failure Mode Details" drawer** (with "×" close icon):
- "FM-001" with "High Risk" badge (red).
- Sub-tabs within the drawer: Overview (active), Links, Complaints, Catalog, History.
- Fields (Overview tab): Failure Mode = Lens crack; Description = "Crack in outer lens leading to reduced light output"; Function = "Provide illumination (F-001)" (blue link); Element = Lens / Housing; FMEA Type = DFMEA; Source = "Design + Complaints" (two-part badge); Catalog Entry = "EC-1204 - Optical defects" (blue link) + a "View" button; Complaints = "7 linked cases" (red badge) + a "View" button; First Seen = 12 Mar 2025; Last Updated = 12 May 2025 10:42; Status = "Open" (blue badge); Owner = avatar "MK" + "Marko Kovac".
- An image gallery: one large hero image (a stylized rendered headlamp) with a red circular crosshair/target-style annotation marker overlaid on the lens region (marking the defect location), plus 3 smaller thumbnail images beside it (alternate angle shots of the same headlamp).
- Buttons beneath the gallery: "+ Link to Catalog", "+ Link Complaint", "Edit" (pencil icon).
- "Top Linked Complaints" mini-table with a "View All" link, columns ID | Vehicle | Symptom | Date: REC-2045 | X1-4582 | Lens crack | 28 Apr 2025; REC-1987 | X1-4431 | Fogging + crack | 21 Apr 2025; REC-1866 | X1-4210 | Lens crack | 15 Apr 2025.
- "Similar Failure Modes (AI)" list: EC-1204 "Optical cracks" 92%; EC-1255 "Lens deformation" 78%; EC-1188 "Surface scratches" 74% (each a percentage similarity score, blue-linked IDs).
- "Recommended Actions" panel (lightbulb icon), an unchecked checklist: "Add material validation test", "Optimize lens wall thickness", "Check coating process"; button "+ Add to Action Plan".

**Footer:** same shell as prior mockups.

### 2. Wireframe & UI/UX

Overall shell matches the other pages (sidebar, top bar, tab strip, filter bar, table, pagination, bottom widget row, right drawer, footer), but this page layers on the most additional structure of the batch: a second toolbar row of bulk/AI actions above the table (AI Suggest / Link to Catalog / Link to Complaint / Quick Add), a drawer with its own internal sub-tab navigation (Overview/Links/Complaints/Catalog/History) rather than a single flat field list, an embedded image gallery with defect-location annotation inside the drawer, and two "intelligence" panels (Similar Failure Modes (AI), Recommended Actions) that go beyond simple data display into suggestion/recommendation UX.

Visual hierarchy: the KPI cards remain the largest numerals; within the table, the RPN column (red/orange text) and the "Complaints" count column (red, bold when non-trivial) compete for visual weight as the two most emphasized data points per row, alongside the small warning-triangle icon prefixing every Failure Mode name (implying every row is inherently flagged as a risk item, more so than in the DFMEA/PFMEA tables). Source badges use a distinct 3(+1)-color coding — blue=Design, green=Catalog, red=Complaints, plus a combined two-tone badge when a failure mode has more than one source — separate from, and in addition to, the existing red/orange/green risk-level coding used for S/O/D and RPN elsewhere in the app; this is a categorical (not severity) color scheme and should not be confused with the H/M/L risk-class palette.

Interaction patterns: row checkbox selection opens/updates the right drawer (as in Mockups 11/12); the drawer's internal sub-tabs (Overview/Links/Complaints/Catalog/History) imply four more nested detail screens beyond the default Overview shown; the "View" buttons next to Catalog Entry and Complaints imply drill-through navigation to the Error Catalog / Complaint Link tabs pre-filtered to this failure mode; the annotated hero image with a crosshair marker implies a click-to-place-marker image-annotation interaction (for indicating where on a physical part the failure occurs) plus a thumbnail strip for browsing multiple reference images; "AI Suggest" and "Similar Failure Modes (AI)" both imply an on-demand AI call from the GUI (either to suggest a new failure mode's likely causes/effects, or to find similar existing ones by name/description similarity); "Recommended Actions" checkboxes with an "+ Add to Action Plan" button imply a suggest-then-confirm flow where AI- or rule-generated action suggestions are not real `RecommendedAction` rows until a user explicitly selects and commits them.

### 3. Architecture & Data Logic

This mockup is the most mixed of the batch: the core failure-mode fields are real and well-supported, while the catalog/complaint/AI layer around them is almost entirely new.

- **Failure Modes (186)**: Real, already built. `FailureMode.objects.count()`, scoped to the project.
- **High Risk (RPN ≥ 100) (42)**: Derivable from real data, needs new query/aggregation logic — same first/latest-`RiskEvaluation` + JSON-score filtering pattern as Mockups 11/12.
- **From Complaints (38, "real cases")**: Genuinely new — no complaint entity or complaint-linking capability exists anywhere in the codebase per the grounding, so neither the count nor the qualifier "real cases" (implying a design-time-hypothesized vs. field-confirmed distinction) can be computed today.
- **Linked to Actions (134)**: Derivable from real data, needs new query/aggregation logic — count of distinct `FailureMode` rows with ≥1 linked `RecommendedAction` (directly or via `failure_cause`).
- **Catalog Entries (2,456, "Available")**: Genuinely new — no "Error Catalog" master library entity distinct from a FMEA's own `FailureMode` rows exists per the grounding; this implies an entirely separate reference-data model (see below), not scoped to any one project.
- **Last Updated**: same unconfirmed-audit-field caveat as Mockups 11/12.
- **Tabs — Failure Modes List**: Real, already built (per column mapping below).
- **Tabs — Failure Mode Matrix**: Derivable from real data, needs new query/aggregation logic (likely a cross-tab of failure modes by Function × Element or by S/O bucket, similar in spirit to the Severity-vs-Occurrence scatter already on this page).
- **Tabs — Error Catalog**: Genuinely new — the standalone master library the grounding calls out as not existing.
- **Tabs — Complaint Link**: Genuinely new — no complaint entity exists.
- **Tabs — Trend & Analysis**: Derivable from real data in part (RPN/severity trend logic, Tier B) but depends on Complaints data for the "Trend (Real Complaints)" half, which is Tier D.
- **Filters — FMEA Type**: Real, already built (`FMEA.fmea_type`).
- **Filters — Function**: Real, already built (`Function.name`).
- **Filters — Element**: Genuinely new / ambiguous, same as the "Element/Part" gap discussed in Mockups 11/12 — no direct `FailureMode`→`Product` field; at best derivable via `function.product.name`.
- **Filters — Source**: Genuinely new — depends on the proposed Source classification (Design/Catalog/Complaints/Suppliers) which has no backing field on `FailureMode` today.
- **Filters — Severity, Occurrence**: Real, already built (`RiskEvaluation.severity`/`.occurrence`, with the usual first-vs-latest ambiguity).
- **Toolbar — AI Suggest**: Genuinely new — distinct from, and not to be conflated with, the existing (unwired) `classify_ishikawa_category` prompt spec; the grounding explicitly flags any AI similarity/matching capability like this as a different, unspecced capability.
- **Toolbar — Link to Catalog, Link to Complaint**: Genuinely new — both depend on the proposed Catalog and Complaint entities below.
- **Toolbar — Quick Add**: Real, already built in spirit (a lightweight `FailureMode` creation flow), though the specific "quick" UX (fewer required fields, inline vs. modal) is a UI decision, not a data-model gap.
- **Table column — ID, Description**: Real, already built (`FailureMode.pk`/code, `FailureMode.description`).
- **Table column — Failure Mode**: Real, already built (`FailureMode.name`).
- **Table column — Function / Element**: Function half real (`FailureMode.function.name`); Element half genuinely new/ambiguous, same as Mockups 11/12.
- **Table column — Source (Design/Catalog/Complaints/combined)**: Genuinely new — no categorical "origin" field exists on `FailureMode`; this would need a new field (or a derived value from whether the failure mode has any linked Catalog entry and/or any linked Complaint, once those entities exist) — proposed, not confirmed.
- **Table column — Catalog (EC-1204 etc.)**: Genuinely new — depends entirely on the proposed Error Catalog entity and a `FailureMode` → catalog-entry link, neither of which exists.
- **Table column — Complaints (count)**: Genuinely new — depends entirely on the proposed Complaint entity and linkage, neither of which exists.
- **Table column — S, O, D, RPN**: Real, already built (`RiskEvaluation.severity`/`.occurrence`/`.detection`), with the same first-vs-latest and RPN-computation caveats noted in Mockups 11/12 (not re-verified arithmetically here, but presumed consistent with that pattern).
- **Table column — Trend (arrow)**: Derivable from real data, needs new query/aggregation logic — direction-of-change vs. a prior evaluation, same as the "Top 5 Highest Current RPN" trend arrows in Mockups 11/12.
- **Table column — Status**: Genuinely new / derived rollup — same gap as Mockups 11/12 (no `FailureMode.status` field; most plausible basis is an action-status rollup).
- **Source Distribution donut**: Genuinely new — depends on the proposed Source field.
- **Severity vs Occurrence scatter**: Derivable from real data, needs new query/aggregation logic — real `RiskEvaluation.severity`/`.occurrence` values, but plotting/bucketing them as a bubble chart (with bubble size and the "unusual axis scale" noted in Section 1) is new visualization work, and the color-by-risk-tier overlay reuses the same not-yet-built per-factor/combined banding discussed in Mockups 11/12.
- **Top Failure Mode Categories bar chart**: Genuinely new — "Optical/Mechanical/Electrical/Thermal/Software/Chemical/Other" is a categorical taxonomy with no backing field on `FailureMode` (distinct from `fmea_type` and from the proposed Source field); would need a new `category` field or derivation.
- **Trend (Real Complaints) line chart**: Genuinely new — entirely dependent on the proposed Complaint entity for its "Complaint FM" series; the "Design FM" series alone could be Tier B (count of failure modes created/sourced from design analysis, over time) if a creation-date and Source field existed, but as a whole the widget is Tier D.
- **Failure Mode Details drawer — Overview fields (Failure Mode, Description, Function, Element, FMEA Type, Status)**: same tiers as the equivalent table columns above.
- **Failure Mode Details drawer — Source, Catalog Entry, Complaints, sub-tabs Links/Complaints/Catalog/History**: Genuinely new, same as above — each depends on the proposed Catalog and/or Complaint entities.
- **Failure Mode Details drawer — First Seen, Last Updated**: same unconfirmed-audit-field caveat as elsewhere.
- **Failure Mode Details drawer — Owner (avatar + name)**: Genuinely new — same person-vs-role-catalog gap as Mockups 11–14.
- **Failure Mode Details drawer — Image gallery with annotation marker**: Genuinely new — the grounding explicitly states no image/file storage or image-annotation capability exists anywhere in the codebase; this needs new file-storage infrastructure plus a coordinate/marker data model (e.g., x/y or normalized position + note, tied to an image record tied to the failure mode).
- **Failure Mode Details drawer — Top Linked Complaints table**: Genuinely new — depends entirely on the proposed Complaint entity (with fields like vehicle identifier, symptom, date implied by the columns shown).
- **Failure Mode Details drawer — Similar Failure Modes (AI)**: Genuinely new — explicitly called out in the grounding as a different, unspecced AI capability, distinct from the existing unwired `classify_ishikawa_category` prompt spec; would need its own similarity-matching design (embedding-based or otherwise) against the proposed Error Catalog.
- **Failure Mode Details drawer — Recommended Actions checklist**: Genuinely new as a *suggestion* mechanism (AI- or rule-generated candidate actions not yet persisted), though once a user checks a box and clicks "+ Add to Action Plan," the resulting persisted row would use the real `RecommendedAction` model (Tier A for that final step only).

**Proposed (not authorized) new entities**, marked explicitly as proposed: an `ErrorCatalog`/`CatalogEntry` model (master reference library of known failure modes, independent of any one FMEA project, given the "2,456 Available" scale) with fields like `code` (e.g., "EC-1204"), `name`/`title`, `category`, `description`; a `Complaint` model (customer/field complaint record) with fields like `record_id` (e.g., "REC-2045"), `vehicle`/`unit identifier`, `symptom`, `date`, and a link back to one or more `FailureMode` rows; a `Source` classification field (or derived property) on `FailureMode` reflecting whether it originated from design analysis, the Error Catalog, a Complaint, or a supplier; and an image/annotation model (image file + normalized marker position + optional note) linked to `FailureMode`, requiring new file-storage capability. A full scoping (who can create Catalog/Complaint records, validation rules, whether Complaints can be bulk-imported, and how the AI-suggestion features would be triggered/rate-limited/reviewed) is out of scope for this cataloging pass and would need its own architecture review.

**Behavioral logic implied:** A failure mode's "Source" appears to function as provenance metadata that can accumulate (FM-001 shows "Design + Complaints," implying a failure mode originally logged from design analysis can later be confirmed/reinforced by real field complaints, and the badge updates to reflect both) — this is new multi-value/combining logic, not a simple single-choice field. The "High Risk" badge on the drawer (distinct from the table's per-row RPN color) implies a threshold-crossing flag (consistent with the "RPN ≥ 100" KPI definition) that could be computed rather than stored. The Recommended Actions checklist implies a proposal → review → commit workflow distinct from directly creating a `RecommendedAction`. The AI-driven "Similar Failure Modes" and "AI Suggest" features imply a search/matching service that would need to run against the Error Catalog, which itself must exist and be populated before that AI feature could return anything meaningful — a build-order dependency worth flagging for any future roadmap discussion.

**Tier summary:** Tier A — ID, Failure Mode name, Description, Function, raw S/O/D/RPN values, Failure Modes List tab, Function/Severity/Occurrence filters, Quick Add. Tier B — High Risk KPI, Linked to Actions KPI, Failure Mode Matrix tab, Trend & Analysis tab (partially), Trend arrow column, Severity vs Occurrence scatter, Element column/filter (via Function→Product join, with gaps), Status column (if a rollup), the final "Add to Action Plan" commit step. Tier C — none distinctly separate from the Tier B/D items above. Tier D — From Complaints KPI, Catalog Entries KPI, Error Catalog tab, Complaint Link tab, Source field/badge/filter/donut, Catalog and Complaints table columns, Top Failure Mode Categories chart, Trend (Real Complaints) chart (Complaint half), the drawer's Links/Complaints/Catalog/History sub-tabs, Owner/Responsible person field, the entire image gallery and annotation feature, Top Linked Complaints table, Similar Failure Modes (AI), Recommended Actions suggestion mechanism, AI Suggest toolbar action, Link to Catalog / Link to Complaint actions.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 16 — Causes (source: mockup-16-causes.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Global chrome**
- Left brand block: "Open FMEA" logo mark + "Community Edition" subtitle.
- Top header: page title "Causes" with a small info "?" icon and (in this mockup) no pin/star icon next to it; subtitle line "Manage causes, link to failure modes and catalog for reusability and knowledge building."
- Top-right controls: project selector pill "Project: Headlamp X1 - PFMEA" (dropdown chevron), global search box "Search (Ctrl+K)" with magnifier icon, notification bell with a red badge showing "1", a "?" help icon, and a circular user avatar "JD" with a small green presence dot.
- Primary action row (top right, below header): "+ New Cause" (solid blue button), "Import" (dropdown), "Export" (dropdown), "Reports" (dropdown), "Filters" (dropdown).

**KPI/stat cards (6, single row)**
1. Total Causes — 214 — subtext "All time" (icon: blue person-network glyph)
2. From Catalog — 152 — subtext "71.0%" (icon: green open-book glyph)
3. New (User Defined) — 62 — subtext "29.0%" (icon: purple "NEW" burst/seal glyph)
4. Linked to FMEA Items — 186 — subtext "87.0%" (icon: orange network/node glyph)
5. High Influence (≥7) — 58 — subtext "27.1%" (icon: amber shield/exclamation glyph)
6. Last Updated — "12 May 2025" — subtext "10:52" (icon: blue calendar glyph)

**Tabs (5)**: Causes List (active/underlined), Cause Catalog, Linked Failure Modes, Cause Relationships, History.

**Filter/search row** (above table): "Search causes..." text box; dropdowns — Source: All, Cause Type: All, Category: All, Status: All, Linked to FMEA: All; "More Filters" button (funnel icon).

**Causes List table** — columns exactly: checkbox (select-all), ID, Cause Description, Cause Type, Category, Source, Linked FM, Influence (1-10), Status, Last Updated, Actions (eye/view icon + "…" overflow menu).
- 10 visible rows (C-0001 … C-0010), each with a row checkbox. Sample rows read exactly:
  - C-0001 — "Wrong torque at screw connection" — Process — Assembly — [Catalog badge] — FM-004, FM-015 — 8 — Active — 12.05.2025
  - C-0002 — "Material out of specification" — Material — Material — [Catalog] — FM-007, FM-018 — 9 — Active — 12.05.2025
  - C-0003 — "Seal design not appropriate" — Design — Design — [User badge] — FM-002, FM-012 — 8 — Active — 11.05.2025
  - C-0004 — "Inadequate process parameters" — Process — Process — [Catalog] — FM-009 — 7 — Active — 11.05.2025
  - C-0005 — "Supplier quality issue" — External — Supplier — [Catalog] — FM-006, FM-011 — 9 — **Under Review** (amber pill) — 10.05.2025
  - C-0006 — "Operator not trained" — Human — Human — [Catalog] — FM-010, FM-016 — 7 — Active — 10.05.2025
  - C-0007 — "Wrong electrical connection" — System — Electrical — [User] — FM-005 — 8 — Active — 09.05.2025
  - C-0008 — "Software algorithm error" — Software — Logic / Software — [Catalog] — FM-013 — 9 — Active — 09.05.2025
  - C-0009 — "Insufficient design validation" — Design — Validation — [User] — FM-003 — 8 — Active — 08.05.2025
  - C-0010 — "Environmental contamination" — External — Environment — [Catalog] — FM-008, FM-017 — 6 — Active — 08.05.2025
- Source badge is a small pill: green "[ Catalog" (bracket/book icon) or purple "User" ("User Defined").
- Status badge: green "Active" pill or amber "Under Review" pill — only two distinct values shown.
- Pagination footer: "Showing 1 to 10 of 214 causes"; page controls "‹ 1 2 3 … 22 ›"; "10 / page" page-size dropdown.

**Four analytics widgets (row below table)**
1. "Causes by Type" — donut chart, center label "214 / Total", legend/list to the right: Process 62 (29.0%), Design 39 (18.2%), Material 28 (13.1%), System 23 (10.7%), Human 21 (9.8%), Software 16 (7.5%), External 15 (7.0%), Other 10 (4.7%).
2. "Causes by Category (Top 8)" — horizontal bar chart, x-axis "Number of Causes" (0–40): Assembly 34, Design 32, Material 28, Process 24, Electrical 18, Supplier 15, Environment 12, Software 10.
3. "Influence Distribution" — donut chart, center label "214 / Total", legend: High (7-10) 58 (27.1%) red, Medium (4-6) 96 (44.9%) amber, Low (1-3) 60 (28.0%) green.
4. "Top Causes by Linked FM" — small table, columns Cause ID / Cause Description / Linked FM Count: C-0001 "Wrong torque at screw connection" 8; C-0002 "Material out of specification" 7; C-0005 "Supplier quality issue" 6; C-0003 "Seal design not appropriate" 5; C-0004 "Inadequate process parameters" 4; "View All" link.

**"Connections Overview" strip** (bottom left): a left-to-right chain of 6 stat chips joined by arrow icons: 186 "Linked to FMEA Items" → 142 "Linked Failure Modes" → 38 "Complaints / Claims" → 34 "XDA Investigations" → 29 "8D Cases" → 27 "RCA Analyses" → 26 "5 Why Analyses" (7 chips total, 6 arrows).

**"Quick Actions" panel** (bottom right, beside Connections Overview): 6 icon buttons — New Cause, Add to Catalog, Link to FMEA, Create Action, Start 8D, Open XDA.

**Right-hand "Cause Details" slide-over panel** (open for C-0003), with an "X" close icon:
- Header: "C-0003" (large) + "User Defined" badge (purple pill, top right).
- "Cause Information" block (label/value pairs): Description "Seal design not appropriate"; Cause Type "Design"; Category "Design"; Source "User Defined" (blue link-styled text); Influence (1-10) "8 (High)" in red; Status "Active" (green pill); Responsible — round avatar "MK" + "Marko Kovac" (blue link text); Created "11.05.2025 14:32"; Last Updated "12.05.2025 10:52"; Notes "Seal cross section too small for pressure."
- "Linked To" block: Failure Modes 2 (View), FMEA Items 2 (View), Complaints / Claims 1 (View), Related XDA "XDA-2025-017" (external-link icon), Related 8D "8D-2025-006", RCA Analysis "RCA-2025-009", 5 Why Analysis "5WHY-2025-011", Ishikawa Diagram "ISH-2025-006", FTA (Fault Tree) "FTA-2025-004".
- Two buttons at panel bottom: "Edit Cause", "Create Action".

**Footer status bar** (page bottom): "Database: OpenFFMEA_Local" (rendered with a doubled "F" in the source image — likely a mockup typo, noted rather than corrected), "User: Janez Demo (Quality Engineer)", "Role: FMEA Editor", "Workspace: Global", "Version: 1.0.0", "System Status" with a green dot.

**Left sidebar** (see Section 2 for full structure) — active item is "Causes" (highlighted blue).

### 2. Wireframe & UI/UX

**Layout**: Fixed dark-navy left sidebar (~200px) → main content area (fluid) with header, KPI row, tabbed sub-nav, filter bar, a large two-column zone (causes table left ~2/3, "Cause Details" panel right ~1/3 as a persistent right rail, not a modal/drawer overlay — it sits inline beside the table), then a full-width row of 4 analytics cards, then a two-column bottom row (Connections Overview left, Quick Actions right), then the thin status footer bar.

**Sidebar structure** (top to bottom): "Open FMEA / Community Edition" logo block; group **FMEA WORKSPACE** (Home, FMEA Projects, FMEA Team); group **CONTEXT (from Open-EQMS)** (System / Product / Process — expandable, shown expanded with sub-items System Characteristics Base, Characteristics Flow / Diagram, Functions); group **FMEA ANALYSIS** (DFMEA, PFMEA, System FMEA, Preventive FMEA (PM-FMEA)); group **FMEA ELEMENTS** (Functions, Failure Modes, Effects, Causes [active/highlighted], Prevention Controls, Detection Controls, Actions); group **SUPPORTING APPS** (Validation Trajectory, Change Impact); group **ANALYSIS TOOLS** (XDA / Investigation, 8D Problem Solving, 5 Why Analysis, Ishikawa Diagram, FTA (Fault Tree), RCA Analysis); then Settings and Collapse at the very bottom.

**Visual hierarchy**: KPI numbers are the largest, boldest text on the page (dominant); page title is bold but smaller; the "Causes" sidebar item is filled solid blue to mark current location; the right-hand detail panel uses the same visual weight as the main table, signaling it's a peer/permanent panel, not a transient overlay. Color coding: green = "Catalog"/"Active"/"Improved"/low values-are-good; purple = "User Defined"; amber/orange = "Under Review" or medium-risk; red = "High" influence text and "High" risk band. Chart color palettes reuse this same green/amber/red semantic plus a rotating categorical set (blue, purple, teal, gray) for non-ordinal breakdowns like Type/Category.

**Interaction patterns implied**: clicking a table row's ID or eye icon opens/refreshes the right "Cause Details" panel for that row (already shown open, populated with C-0003, whose row is presumably highlighted, though the screenshot doesn't visibly highlight a selected row). The "…" per-row menu implies a contextual action list (edit/delete/duplicate/link, etc. — not shown expanded). "View" links inside the detail panel and the mini "Top Causes" table imply drill-through navigation to filtered sub-views (e.g., "Failure Modes: 2 [View]" would jump to a Failure-Modes-filtered-by-cause view). "View All" under the mini table implies expanding to the full ranked list. Dropdown filters (Source/Cause Type/Category/Status/Linked to FMEA) are standard select inputs; "More Filters" implies an additional filter drawer/panel not shown. Chart legends with counts likely act as togglable series filters (a common donut/bar-chart convention), though no hover/active state is visible in this static mockup.

**Sidebar grouping note**: this mockup groups Prevention Controls, Detection Controls, and Actions together under "FMEA ELEMENTS" alongside Functions/Failure Modes/Effects/Causes. It also uses distinct top-level group names — "FMEA ANALYSIS", "SUPPORTING APPS", "ANALYSIS TOOLS" — and includes a full "CONTEXT (from Open-EQMS)" group and complete "ANALYSIS TOOLS" group (XDA, 8D, 5 Why, Ishikawa, FTA, RCA) that are absent or reorganized in other mockups in this batch (see mockup-17/18/19/20 for differing groupings — not reconciled here, only what this image shows is described).

### 3. Architecture & Data Logic

- **Total Causes (214)** — Real, already built. `FailureCause.objects.count()` (likely scoped to the current project's FMEAs). Tier A.
- **Cause Description column / detail-panel Description** — Real, already built. `FailureCause.description` (and/or `.name`). Tier A.
- **From Catalog / New (User Defined) split, and the "Source" column/badge/filter** — Genuinely new. No `Source` (Catalog vs. User-defined) field exists on `FailureCause`. Would need a proposed `source` field (choices: `catalog` / `user_defined`), and, more importantly, a genuine **Cause Catalog** entity distinct from a FMEA's own `FailureCause` rows (explicitly confirmed absent from the codebase) so that a catalog entry can be *reused* across multiple FMEAs/failure modes. Tier D.
- **Cause Type / Category columns and filters** — Genuinely new. No `cause_type` or `category` field exists on `FailureCause`; the mockup treats these as two independent classification axes (e.g., "Process" type + "Assembly" category). Both proposed, choice-field or lookup-table backed. Tier D.
- **Influence (1-10) column, "High Influence (≥7)" KPI, and Influence Distribution donut** — Genuinely new. No `influence` field exists on `FailureCause`. Proposed integer field (1–10) plus validation, and threshold-based aggregation for the KPI/donut. Tier D.
- **Status column/badge ("Active"/"Under Review") and its filter** — Genuinely new. No `status` field exists on `FailureCause`. Implies a small state machine (at minimum Active ↔ Under Review, likely plus Draft/Retired/Deprecated in a fuller scheme) with unspecified transition rules and permissions — needs scoping. Tier D.
- **"Linked FM" column, "Linked to FMEA Items" KPI, and "Top Causes by Linked FM"** — This is a significant architecture finding: the mockup shows a single cause (e.g., C-0001) linked to *multiple* failure modes ("FM-004, FM-015") and a cause detail panel showing "Failure Modes: 2". The real `FailureCause` model has a single, mandatory `failure_mode` ForeignKey — a cause belongs to exactly one failure mode, not many. Reproducing this UI faithfully therefore requires re-architecting the relationship (a catalog-style cause that can be *applied* to many failure modes via a many-to-many join, separate from a "local" one-off cause) — it is not achievable by adding a field to the existing FK-based model. Tier D.
- **Responsible (person) field in the detail panel** — Genuinely new. No `responsible`/owner field exists on `FailureCause` (contrast with `RecommendedAction.responsible_role`, a real FK on a *different* model that could serve as a design precedent). Tier D.
- **Created / Last Updated (timestamps + actor) in the detail panel and table** — Genuinely new. No audit/timestamp fields (`created_at`, `updated_at`, actor) are confirmed on `FailureCause`. Tier D.
- **Notes field in the detail panel** (distinct from Description) — Genuinely new, proposed free-text field. Tier D.
- **"Complaints / Claims" (1), "Related XDA", "Related 8D", "RCA Analysis", "5 Why Analysis", "Ishikawa Diagram", "FTA (Fault Tree)" cross-links** — Genuinely new on every count. None of these investigation/quality-record entities (Complaints/Claims, XDA/Investigation, 8D, RCA Analysis, 5 Why Analysis, Ishikawa Diagram, FTA) exist anywhere in the codebase per the confirmed grounding. Each would need its own model plus a linking relationship back to `FailureCause`. Tier D.
- **Causes by Type donut / Causes by Category bar** — Derivable only once the proposed `cause_type`/`category` fields exist; the aggregation query itself (group-by-count) is straightforward once the field is real. Tier D (blocked on the new fields above).
- **"Connections Overview" chain** — "Linked to FMEA Items" and "Linked Failure Modes" nodes are (once the catalog/M2M relationship above is built) Tier B aggregations over real relationships; "Complaints / Claims", "XDA Investigations", "8D Cases", "RCA Analyses", "5 Why Analyses" nodes are Tier D (no backing entities at all).
- **Quick Actions**: "New Cause" (Tier A — creates a `FailureCause`), "Create Action" (Tier A — `RecommendedAction.failure_cause` FK is real), "Link to FMEA" (Tier B/D depending on whether it means the existing single FK or the new catalog M2M), "Add to Catalog", "Start 8D", "Open XDA" (all Tier D — no catalog/8D/XDA entities exist).
- **"Edit Cause" button** — Real, already built as a CRUD affordance on the two existing fields (`name`/`description`); editing any of the mockup's other displayed fields is naturally blocked on those fields existing first. Tier A (for the real fields) / Tier D (for the rest).
- **Cause Catalog / Cause Relationships / History tabs** — All three genuinely new: no catalog entity, no cause-to-cause relationship model, and no change-history/audit-log model for `FailureCause`. Tier D.
- **Linked Failure Modes tab** — Derivable from the real `failure_mode` FK (a simple reverse list), though it becomes more interesting (and Tier D) once the catalog M2M pattern above is introduced. Tier B today under the current 1:1 model.

**Behavioral logic implied**: a Status badge implies a workflow (Active ⇄ Under Review, at minimum) with an unstated trigger (who moves a cause into "Under Review" and why — e.g., pending engineering sign-off) — none of this exists today. The Source badge ("Catalog" vs. "User") implies a promotion workflow where a user-defined cause can later be "Added to Catalog" (see Quick Actions) — this is a proposed CRUD/lifecycle flow (creation → review → promotion to catalog → reuse across FMEAs) that would need to be scoped in full (required fields for a catalog entry, who can promote/edit it, whether promoting duplicates or converts the record, versioning if a catalog entry's description changes after being applied elsewhere).

**Tier summary:** Tier A — cause description text and basic create/edit CRUD (`FailureCause.name`/`.description`), cause count KPI, and the single-FK "Linked Failure Modes" relationship. Tier B — reverse-relationship aggregations built on the existing `failure_mode` FK (once scoped properly). Tier C — none identified; nothing here is a real field that's merely under-displayed. Tier D — Source/Catalog concept and catalog reuse (M2M), Cause Type, Category, Influence score, Status/workflow, Responsible, timestamps/audit trail, Notes, and every cross-link to Complaints/Claims, XDA, 8D, RCA, 5 Why, Ishikawa, and FTA.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 17 — Risk Trajectory & Propagation (source: mockup-17-risk-trajectory-propagation.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Global chrome**: same brand block as other mockups; page title "Risk Trajectory & Propagation" with info icon; subtitle "Track how risks change over time and how they propagate through system functions. See how actions (including PM-PFMEA) reduce risk."; top-right project selector "Project: Headlamp X1 - PFMEA", search box, notification bell (badge "3"), help icon, avatar "JD".

**KPI/stat cards (6, single row)**
1. Initial High Risks — 23 — "RPN ≥ 100" (red shield icon)
2. Current High Risks — 8 — "RPN ≥ 100" (orange shield/trend icon)
3. AP Reduced — 66% — "Average reduction" (green trend-network icon)
4. PM-PFMEA Controlled — 15 — "Risks with PM control" (blue node-network icon)
5. Revalidation Required — 6 — "Tests due / expired" (purple refresh/cycle icon)
6. Uncontrolled Propagation — 3 — "Paths at risk" (amber shield-alert icon)

**Tabs (6)**: Risk Trajectory (active), Risk Propagation, Risk Heat Map, PM-PFMEA Impact, Risk Summary, History. To the right of the tabs: "Baseline" button and "Compare" button.

**Filter row**: "View:" dropdown = "Risk Trajectory (by FMEA Item)"; "FMEA Type: All"; "Lifecycle Phase: All"; "Status: All"; checkbox "Show only High risks"; "More Filters" button. A small zoom-in / zoom-out / export icon trio sits above the table's right edge.

**Risk Trajectory table** — columns: ID, FMEA Item, Type, then a set of lifecycle-phase columns each containing an inline mini line-chart (connected colored dots) rather than a single value: "Concept / Design Baseline", "Design Verification (DV)", "Process Validation (PV)", "Pre-Production (PPAP)", "Serial Production (SOP)", "Current (12 May 2025)"; final column "Trend" (down/right arrow icon, color-coded).
- 5 visible rows:
  - FM-021 — "LED overcurrent (LED Driver)" — DFMEA — 240→144→72→48→36→36 — ↘ (down)
  - FM-034 — "Seal leakage (Housing)" — PFMEA — 180→150→120→80→40→40 — ↘
  - FM-041 — "Connector pin corrosion (Connector)" — PFMEA — 216→216→144→144→108→108 — → (flat)
  - FM-052 — "Incorrect aim adjustment (Adjuster)" — PFMEA — 160→100→60→30→24→24 — ↘
  - FM-063 — "Body deformation (Housing)" — DFMEA — 128→128→96→96→96→96 — → (flat)
- Each dot in the mini-line is color-coded (red = high RPN, amber/orange = medium, green = low), and the connecting line segments shift color as the value crosses bands.
- Pagination: "Showing 1 to 5 of 23 risk trajectories"; page controls "‹ 1 2 3 … 5 ›"; "10 / page" selector.

**"Risk Propagation Preview (FM-021)" panel** (mid-page, left): a horizontal chain of 5 boxes connected by arrows: "LED overcurrent (Failure Mode)" → "LED overheating (Local Effect)" → "Reduced LED lifetime (Next-Level Effect)" → "Loss of illumination (System Effect)" → "Safety requirement not fulfilled (End Effect)"; each box has a Severity value below it: S:7, S:6, S:7, S:9, S:9. Below that, a "Propagation Probability" horizontal gradient gauge bar labeled with tick marks at 10%, 30%, 40%, 60%, 70% and a legend: green dot "Low (<20%)", amber dot "Medium (20–60%)", red dot "High (>60%)". Button: "Open Full Propagation".

**"How Risk Was Reduced (FM-021)" table** (mid-page, right): columns Action/Control (ID + name), Type, Implemented In, Impact, O, D.
- Rows: A-021 "Heat sink redesign" / Design Action / DV / "Occurrence ↓↓" / 6→3 / 5
- A-034 "Current limit algorithm" / Design Action / DV / "Occurrence ↓↓" / 3→1 / 5
- A-045 "Thermal monitoring" / Detection Control / PV / "Detection ↓↓" / 1 / 5→2
- PM-021 "Coolant flow check" / PM-PFMEA / SOP / "Occurrence ↓" / 1→2 / 2
- DT-055 "Thermal cycling test" / Validation Test / PV / "Detection ↓" / 1 / 2→1
- Legend below table: "↓↓ Significant", "↓ Moderate", "— No Change".

**Bottom analytics row (4 widgets)**
1. "PM-PFMEA Impact Summary" — donut, center "15 / Risks", legend: Significant Impact 6 (40.0%) green, Moderate Impact 5 (33.3%) amber, Low Impact 3 (20.0%) blue, No Impact 1 (6.7%) gray.
2. "Impact on Occurrence (O)" — two horizontal bars: "Average O (Initial)" 5.2 (red bar), "Average O (Current)" 2.1 (green bar); "Reduction 59.6%" (green text).
3. "Impact on Detection (D)" — two horizontal bars: "Average D (Initial)" 5.6, "Average D (Current)" 2.4; "Improvement 57.1%".
4. "Residual Risk Distribution" — donut, center "23 / Risks", legend: Low (AP ≤ Low) 9 (39.1%) green, Medium 8 (34.8%) amber, High 6 (26.1%) red.

**Right-hand "Risk Details" slide-over panel** (for FM-021), with "X" close:
- Header: "FM-021" (large) + "High" badge (red pill). Subheading "LED overcurrent (LED Driver)" + "DFMEA" badge + "Active" badge.
- "Risk Overview" two-column table: columns "Initial (Baseline)" / "Current (12 May 2025)": S 9/9, O 6/2, D 5/2, RPN 240/36, AP High/Medium.
- "Reduction" block: "RPN Reduction" progress bar labeled "85.0%"; "AP Improvement" — "High → Medium".
- "Primary Cause": C-0003 "Seal design not appropriate".
- "Linked Function": F-012 "Control LED current".
- "Linked Effects": E-021 "LED overheating (Local)"; E-034 "Reduced LED lifetime (Next level)"; E-050 "Loss of illumination (System)".
- "Linked PM-PFMEA": PM-021 "LED Driver Cooling System" (View).
- "Actions Impacting This Risk": Total Actions 4, Closed 2, In Progress 1, Open 1.
- Buttons: "View Propagation", "View History", "Edit Risk" (solid blue).
- "Top Residual Risks" mini table: columns ID / FMEA Item / RPN (Current) / AP: FM-041 "Connector pin corrosion" 108 High; FM-063 "Body deformation" 96 High; FM-088 "Light pattern deviation" 72 Medium; FM-034 "Seal leakage" 40 Medium; FM-021 "LED overcurrent" 36 Medium. Button "View All High / Medium Risks".

**Footer status bar**: Database: OpenFMEA_Local, User: Janez Demo (Quality Engineer), Role: FMEA Editor, Workspace: Global, Version: 1.0.0, System Status (green dot).

### 2. Wireframe & UI/UX

**Layout**: same dark sidebar + light content shell as other pages. Header → KPI row → tabs+compare controls → filter row → trajectory table (full width) → two side-by-side mid panels (Propagation Preview left, How Risk Was Reduced right) → 4-across bottom analytics row → persistent right-hand Risk Details rail (spans from below the header down past the mid panels) → footer. The right rail is again a permanent inline panel, not a modal.

**Sidebar structure**: "FMEA WORKSPACE" (Home, FMEA Projects, FMEA Team); "CONTEXT (from Open-EQMS)" (System / Product / Process expandable, with sub-items System Characteristics Base, Characteristics Flow / Diagram, Functions); "FMEA ANALYSIS" (DFMEA, PFMEA, System FMEA, Preventive FMEA (PM-FMEA), **FMEA Matrix** — a fifth item not present in mockup-16's equivalent group); "FMEA ELEMENTS" (Functions, Failure Modes, Effects, Causes — notably **without** Prevention Controls / Detection Controls / Actions this time); "RISK & ACTIONS" (Prevention Controls, Detection Controls, Actions — these three moved into a new group here); "VALIDATION & CHANGE" (Evidence & Tests, Validation Trajectory, Risk Trajectory [active, highlighted], Change Impact); Settings, Collapse. There is **no "ANALYSIS TOOLS" group** in this mockup (XDA/8D/5-Why/Ishikawa/FTA/RCA are entirely absent from the sidebar here).

**Visual hierarchy**: KPI numbers dominate; the red/amber/green severity coloring is the primary semantic thread running through the trajectory sparklines, the propagation-chain severity tags, the "How Risk Was Reduced" arrows, and all four bottom donuts/bars — a consistent risk-color language (red=high/worsening, amber=medium, green=low/improved) used far more pervasively here than in mockup-16. The propagation gauge is a distinct, custom horizontal gradient-bar widget (green→amber→red continuous gradient with tick labels), not a standard chart type.

**Interaction patterns implied**: selecting a table row (or its Trend arrow) presumably drives which FMEA item populates the Risk Propagation Preview, How Risk Was Reduced table, and the right-hand Risk Details rail — all three currently show FM-021, suggesting a single "selected risk" state shared across the page. "Baseline" and "Compare" buttons imply a mode toggle/diff view against a saved baseline snapshot. "Open Full Propagation" and "View Propagation" link to the separate "Risk Propagation" tab (fuller version of the mini diagram). "View History" implies an audit/change-log view. Zoom icons above the table suggest the trajectory sparklines can be enlarged into a full chart. Clicking a "View" link (e.g. next to Linked PM-PFMEA) implies drill-through navigation.

**Sidebar grouping note**: this mockup's sidebar groups Prevention/Detection Controls and Actions under a new "RISK & ACTIONS" heading (distinct from mockup-16, which put them under "FMEA ELEMENTS"), adds "FMEA Matrix" to the analysis group, folds Risk Trajectory and Change Impact into a "VALIDATION & CHANGE" group together with Evidence & Tests and Validation Trajectory (mockup-16's "SUPPORTING APPS" group had only Validation Trajectory and Change Impact, with no Evidence & Tests or Risk Trajectory entry), and drops the "ANALYSIS TOOLS" group entirely. Described as-is; not reconciled with other mockups.

### 3. Architecture & Data Logic

- **Initial High Risks / Current High Risks (23 / 8, RPN ≥ 100)** — Derivable from real data, needs new query/aggregation logic. `RiskEvaluation.result` (JSON, carries `{"score": N, ...}`) already stores RPN-style scores per `failure_mode`; "Current" = latest evaluation per failure mode (the model's default ordering `-evaluated_at, -id` makes `.first()` trivial), but "Initial" requires a separate earliest-per-failure-mode query not currently built. Thresholding at RPN ≥ 100 is a simple filter once both queries exist. Tier B.
- **AP Reduced (66% average reduction)** — Derivable from real data, needs new query/aggregation logic, but with an undefined computation: `RiskEvaluation.result` can carry an AP-style classification (High/Medium/Low), which is categorical, not numeric — "66% average reduction" implies either (a) a numeric proxy score behind AP that isn't specified in the model, or (b) counting how many risks moved down at least one AP tier. This needs a defined scoring/business rule before it can be built. Tier B (with an open design question).
- **PM-PFMEA Controlled (15, "risks with PM control")** — Genuinely new. There is no field or relationship anywhere linking a production FMEA's `FailureMode`/`RiskEvaluation` to a corresponding Preventive-Maintenance FMEA (PM-FMEA) item. `Fmea` likely has a type distinguishing DFMEA/PFMEA/PM-FMEA, but no cross-FMEA "this risk is mitigated by that PM-FMEA item" relationship exists. Tier D.
- **Revalidation Required (6, "tests due / expired")** — Cannot be confirmed against the grounded model list provided for this batch: no Evidence/Test model with due-date/expiry fields is included in the confirmed domain model given here. If such a model exists elsewhere in the app (the sidebar's "Evidence & Tests" nav item suggests one may), its field-level shape is outside this grounding and must be verified separately before this KPI can be scoped. Treated conservatively as Tier D pending that verification.
- **Uncontrolled Propagation (3, "paths at risk")** — Genuinely new. No propagation-path model exists (see below); "uncontrolled" implies a computed status over propagation paths that themselves don't exist yet. Tier D.
- **Risk Trajectory table's phase columns (Concept/Design Baseline, DV, PV, PPAP, SOP, Current)** — Genuinely new for the phase structure. `RiskEvaluation` has no lifecycle-phase field at all (explicitly confirmed absent); only "latest" (`Current`) is retrievable today via `.first()`. Reproducing a named-phase-gate history (a distinct S/O/D/RPN snapshot per phase, in a fixed sequence) requires a new field on `RiskEvaluation` (e.g., proposed `lifecycle_phase` choice field) or a separate join model, plus a defined, fixed vocabulary of phases (this mockup uses 6: Concept/Design Baseline, DV, PV, PPAP, SOP, Current — note mockup-18 uses a *different* 7-phase list for the same concept, see that file). Tier D.
- **Trend arrow column** — Derivable once the phase-history data exists (a simple slope/direction calculation); blocked on the Tier D item above. Tier B once unblocked.
- **Risk Propagation Preview diagram (Failure Mode → Local Effect → Next-Level Effect → System Effect → End Effect, with a Severity per node)** — Genuinely new. `FailureEffect` is a flat list per `FailureMode` with no propagation-chain relationship (explicitly confirmed absent) and no per-effect Severity field. This diagram requires a new self-referencing or leveled effect model. Tier D.
- **"Propagation Probability" gauge (%)** — Genuinely new metric with no defined computation basis anywhere in the model (not derivable from S/O/D at all as specified). Would need its own proposed formula/heuristic to be scoped. Tier D.
- **"How Risk Was Reduced" table** — Mixed. The entity rows themselves are real where they map to `RecommendedAction` (A-021, A-034), `DetectionControl`/`PreventionControl` (A-045), and possibly a PM-FMEA item (PM-021) and a validation test (DT-055, unconfirmed model). But "Implemented In" (a lifecycle-phase tag per action/control) and the O/D "before → after" delta per action are genuinely new — neither `RecommendedAction` nor `PreventionControl`/`DetectionControl` carries a phase tag or an occurrence/detection-delta field. Tier D for the phase tag and O/D deltas; Tier A for the base entities existing at all.
- **PM-PFMEA Impact Summary donut** — Blocked on the PM-FMEA cross-link above. Tier D.
- **Impact on Occurrence (O) / Impact on Detection (D) bars** — Derivable from real data, needs new query/aggregation logic: average `RiskEvaluation.occurrence`/`.detection` across the earliest vs. latest evaluation per failure mode, aggregated project-wide. Tier B.
- **Residual Risk Distribution donut** — Derivable from real data: bucket the latest `RiskEvaluation.result` classification (or a proposed AP-band mapping) across all failure modes. Tier B.
- **Risk Details panel — Risk Overview (S/O/D/RPN/AP, Initial vs. Current)** — Real, largely already built. Maps directly to `RiskEvaluation.severity`, `.occurrence`, `.detection`, and `.result` (score + classification). "Current" is a solved query (`.first()`); "Initial" needs the same new earliest-query as the KPI above. Tier A (fields) / Tier B (the "Initial" query specifically).
- **RPN Reduction % / AP Improvement** — Derivable, simple arithmetic once Initial and Current are both available. Tier B.
- **Primary Cause** — Real, already built: `FailureMode.causes` (reverse of `FailureCause.failure_mode`). Tier A.
- **Linked Function** — Real, already built: `FailureMode.function` FK. Tier A.
- **Linked Effects list** — The base relationship (`FailureMode.effects`) is real (Tier A), but the "(Local)" / "(Next level)" / "(System)" level tags shown next to each effect require the same propagation-level model flagged as Tier D above.
- **Linked PM-PFMEA** — Genuinely new (same PM-FMEA cross-link gap). Tier D.
- **Actions Impacting This Risk (Total/Closed/In Progress/Open counts)** — Derivable from real data: `RecommendedAction.status` (a real `ActionStatus` enum: open/in_progress/completed/verified/cancelled) grouped by `failure_mode`/`failure_cause`. Note the mockup's "Closed" bucket has no exact match in the real enum — it would need to be defined as a mapping (e.g., `completed` + `verified` → "Closed") rather than a literal status value. Tier B.
- **Top Residual Risks table** — Derivable from real data: latest `RiskEvaluation` per failure mode, sorted by RPN descending. Tier B.
- **Baseline / Compare buttons** — Genuinely new UI/behavior: implies persisting a named "baseline" snapshot of risk state and diffing current against it — no baseline/snapshot concept exists on `RiskEvaluation` today (only a chronological list of evaluations, from which "first" already approximates a baseline, but an explicit user-set baseline marker does not exist). Tier D.

**Behavioral logic implied**: the Trend arrow and RPN-reduction coloring imply an automatic recompute whenever a new `RiskEvaluation` is logged for a `FailureMode` (already true today per-evaluation, but the phase-gate view implies recomputing/display at fixed lifecycle checkpoints, which is new). The AP badge transition ("High → Medium") implies a classification recompute tied to score thresholds — the classification logic itself likely already exists inside `RiskEvaluation.result`, but exposing "Initial vs Current" transitions as a first-class UI concept is new. Cross-entity relationships implied but unbuilt: FailureMode/RiskEvaluation ↔ PM-FMEA item; FailureEffect ↔ FailureEffect (propagation chain); RecommendedAction/PreventionControl/DetectionControl ↔ lifecycle phase.

**Tier summary:** Tier A — core S/O/D/RPN/AP fields, Primary Cause and Linked Function/Effects base relationships, Total Actions/status data existing on `RecommendedAction`. Tier B — Initial-vs-Current aggregation queries, RPN Reduction %, Impact on O/Impact on D averages, Residual Risk Distribution, Top Residual Risks, Actions-by-status counts, Trend arrows (once phase data exists). Tier C — none identified. Tier D — lifecycle-phase-gate tracking on `RiskEvaluation` (the whole trajectory-by-phase table and Quick Impact concept), the Failure Mode→Local→Next-Level→System→End Effect propagation chain and its per-node severity, Propagation Probability %, PM-PFMEA cross-linking (KPI, panel field, and impact summary), Uncontrolled Propagation paths, Revalidation Required (pending model verification), and the Baseline/Compare snapshot mechanism.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 18 — Effects (source: mockup-18-effects.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Global chrome**: brand block; page title "Effects" with info icon and a small pin/star icon beside it (not present on mockup-16/17's title); subtitle "Analyze how effects impact system, requirements, functions and risks. See propagation, trends and improvement impact."; top-right project selector "Project: Headlamp X1 - PFMEA", search box, bell (badge "6"), help icon, avatar "JD"; action row "+ New Effect" (solid blue), "Import", "Export", "Reports", "Filters".

**KPI/stat cards (7, single row)**
1. Total Effects — 211 — "All time"
2. High Severity (S ≥ 7) — 157 — "74.4%"
3. Affects System — 128 — "60.7%"
4. Propagation Paths — 343 — "Total paths"
5. Improved (↓ AP/RPN) — 186 — "88.2% of total" (green down-arrow icon)
6. Worsened (↑ AP/RPN) — 11 — "5.2% of total" (orange up-arrow icon)
7. Last Updated — "12 May 2025" — "10:52"

**Tabs (6)**: Effects Impact Dashboard (active), Effects List, Effect Catalog, Linked Failure Modes, Effect Relationships, History.

**Filter row**: "FMEA Type: All", "Lifecycle Phase: All", "View: Impact Overview" dropdown, "Compare To: Baseline" dropdown, "More Filters" button.

**Numbered dashboard widgets, main grid:**

1. **"1. Impact on Risk Priority (AP)"** — multi-line chart, dual Y-axis (left "AP / RPN" 0–100, right "High AP Count" 0–60), X-axis lifecycle phases: Concept, Design, DV, PV, PPAP, SOP, Serial Prod. Three series with legend dots: blue "AP (Avg)" (69→72→64→38→26→21→18), purple "RPN (Avg)" (163→102→118→72→48→32→24), red "High AP Count" (47→38→29→18→11→9→6 — read approximately, values partly overlapped/hard to disambiguate in the source). Callout badges on the right: "↓78%" (blue), "↓88%" (purple), "↓91%" (red). Caption "Compared to Baseline".
2. **"2. Impact Distribution by Target"** ⓘ — horizontal stacked bar chart, legend: green "Improved (↓)", gray "No Change", red "Worsened (1)". Rows (category / values, left-to-right green→gray→red): System Functions 56/16/(small red segment); Requirements ~48/22/(small); Characteristics ~62/14/(small)+"1" marker outside bar; Components 71/10/(small)+"1"; Processes ~41/12/none; Customers 5/0/0; Safety 7/0/0. X-axis "Number of Effects" 0–100.
3. **"3. Impact by Effect Level"** — diverging bar chart, legend: red "Increase (↑ AP/RPN)", green "Decrease (↓ AP/RPN)", blue "Net". Rows: "Local Effect (Level 1)" +48 / −76 / Net −28; "Subsequent (Level 2)" +32 / −62 / Net −30; "Subsequent (Level 3)" +21 / −47 / Net −26; "System Effect (Level 4)" +15 / −37 / Net −22; "End Effect (Level 5)" +7 / −22 / Net −15. X-axis ranges roughly −60 to +60 "Average AP Change".
4. **"4. Top Effects by AP Improvement"** ⓘ — table, columns Effect / Initial AP / Current AP / Change / Trend: E-004 "LED overheating" High(82)→Medium(26) ↓56 ↓; E-002 "Reduced light output" High(76)→Medium(24) ↓52 ↓; E-005 "Reduced LED lifetime" High(70)→Low(18) ↓52 ↓; E-001 "Loss of illumination" High(86)→Medium(30) ↓56 ↓; E-007 "Corrosion of connector pins" Medium(48)→Low(14) ↓34 ↓. "View All" button.
5. **"5. Top Effects with Increased Risk"** — same column layout: E-008 "Intermittent operation" Medium(32)→High(45) ↑13 ↑; E-041 "EMC interference" Medium(28)→Medium(36) ↑8 ↑; E-017 "Flicker / Light instability" Low(20)→Medium(27) ↑7 ↑; E-050 "Noise / Vibration" Low(18)→Medium(24) ↑6 ↑; E-003 "Overheating (Driver)" Medium(30)→Medium(35) ↑5 ↑. "View All" button.
6. **"6. Effect Propagation Overview (All Effects)"** — a 5-stage Sankey-style flow diagram. Stage headers with totals: "Local Effects (L1)" 82, "Subsequent L2" 76, "Subsequent L3" 61, "System Effects (L4)" 33, "End Effects (L5)" 21. Each stage is a stacked block split into three colored bands (red "Increases Risk", gray "No Change", green "Decreases Risk") with counts/percents: L1 = 82(28%)/11(13%)/48(58%); L2 = 17(22%)/9(12%)/50(66%); L3 = 11(18%)/6(10%)/44(72%); L4 = 4(12%)/3(9%)/26(79%); L5 = 3(14%)/1(9%)/17(81%). Ribbon-style flow connectors link each stage's bands to the next stage's bands, crossing where risk category changes. Below: "Propagation Paths" counts between stages: 176, 128, 64, 37. Button "Open Propagation Explorer".
7. **"7. Impact on Key Requirements (Top 10)"** — diverging stacked bar chart per requirement, legend: green "AP Improved", gray "No Change", red "AP Increased", blue "Net Change". Rows (Requirement ID / description / bar / Net): REQ-L-001 "Luminous flux ≥ 1000 lm" ↓12; REQ-L-002 "Light uniformity" ↓8; REQ-L-003 "LED lifetime ≥ 10,000 h" ↓10; REQ-S-001 "No loss of illumination" ↓6; REQ-E-001 "EMC compliance" 0 (net change "0"); REQ-M-001 "Operating temp. -40° to +85°C" ↓5; REQ-IP-001 "IP67 water ingress protection" ↓5; REQ-V-001 "Vibration resistance" ↓3; REQ-C-001 "Connector durability" ↓3; REQ-SAF-001 "Functional safety ASIL-B" ↓2. X-axis "Number of Effects" 0–15.

**Right-hand "Effect Details" slide-over panel** (for E-004), "X" close:
- Header "E-004" + "Active" badge (green), and below it a "Local Effect" badge (blue-purple pill).
- "Effect Information": Description "LED overheating"; Effect Type "Local Effect"; Effect Level "Component"; Severity (S) "8 (High)" red; End Effect "No"; Source "Design FMEA"; Created "09.05.2025 14:21 by Janez Demo"; Last Updated "12.05.2025 10:52 by Jan Demo"; Notes "Overheating occurs when LED junction temperature exceeds limit."
- "Linked To": Failure Modes 7 (View); FMEA Items 2 (View); Causes 6 (View); Functions 1 (View); Requirements 2 (View); Next Level Effects 2 (View); End Effect "Loss of illumination (E-001)" (View).
- "Actions" section header (buttons below, partly cut in the base screenshot but visible in crop): "View Propagation", "Create Action", "Edit Effect".
- "Quick Impact" block: Initial AP "High (82)"; Current AP "Medium (26)"; Change "↓56 (68%)"; a small inline line chart (Concept 72 → Design 54 → DV 38 → PV 26 → PRAP[sic, "PPAP" mis-typeset] 21 → SOP 18 → Serial [value cut off]) with dot markers; button "View Full Trajectory".

**Footer status bar**: Database: OpenFMEA_Local, User: Janez Demo (Quality Engineer), Role: FMEA Editor, Workspace: Global, Version: 1.0.0, System Status (green dot).

### 2. Wireframe & UI/UX

**Layout**: same shell pattern — sidebar, header, KPI row (7 cards, tighter than the 6-card rows elsewhere), tab bar, filter row, then a dense analytics grid: row of widgets 1–2 (two large cards), row of widgets 3–4–5 (three cards), row of widgets 6–7 (two large cards, the Sankey and the requirements chart), with the persistent "Effect Details" right rail running alongside the whole dashboard. Footer bar at the very bottom.

**Sidebar structure**: "FMEA WORKSPACE" (Home, FMEA Projects, FMEA Team); "CONTEXT (from Open-EQMS)" (System / Product / Process expandable: System Characteristics Base, Characteristics Flow / Diagram, Functions); "FMEA ANALYSIS" (DFMEA, PFMEA, System FMEA, Preventive FMEA (PM-FMEA), FMEA Matrix); "FMEA ELEMENTS" (Functions, Failure Modes, Effects [active/highlighted], Causes, Prevention Controls, Detection Controls, Actions — all seven together, unlike mockup-17); "RISK & ACTIONS" (here containing only Risk Trajectory, Change Impact — Prevention/Detection/Actions are back in FMEA ELEMENTS instead); "VALIDATION & CHANGE" (Evidence & Tests, Validation Trajectory — no Risk Trajectory or Change Impact here, since those moved to RISK & ACTIONS); Settings, Collapse. No "ANALYSIS TOOLS" group (XDA/8D/5-Why/Ishikawa/FTA/RCA absent), matching mockup-17 but not mockup-16.

**Visual hierarchy**: this is the densest of the five pages — seven numbered widgets on one screen plus a persistent detail rail. Numbering ("1.", "2.", … "7.") on each widget title is a distinctive pattern not seen on mockup-16/19/20, implying a guided/ordered reading path down the impact-analysis story (trend → distribution → level breakdown → top movers both directions → propagation flow → requirements impact). Color language: green = improved/decreased-risk/high-effectiveness, red = worsened/increased-risk/high-severity, gray = no-change, blue = "Net" trend line — applied uniformly across every chart on the page (line chart, stacked bars, diverging bars, Sankey ribbons, table trend arrows).

**Interaction patterns implied**: selecting a row in widgets 4 or 5 ("Top Effects by AP Improvement" / "...with Increased Risk") likely populates the Effect Details rail (currently showing E-004, which is indeed the first row of widget 4) — same shared-selection pattern as mockup-17's risk rail. "Open Propagation Explorer" and "View Propagation" link out to a fuller version of the Sankey/chain view (paralleling mockup-17's "Open Full Propagation"). "View Full Trajectory" in the Quick Impact block links to a per-effect version of the phase-based line chart. "View Requirement Impact" (button under widget 7, visible in the full-page screenshot) implies drill-through to a requirements-scoped view.

**Sidebar grouping note**: differs from both mockup-16 (which keeps Prevention/Detection/Actions inside FMEA ELEMENTS and has a full ANALYSIS TOOLS section) and mockup-17 (which moves Prevention/Detection/Actions into a "RISK & ACTIONS" group alongside Risk Trajectory itself). Here, RISK & ACTIONS holds only Risk Trajectory + Change Impact, and Prevention/Detection/Actions sit back in FMEA ELEMENTS. Not reconciled — described as shown.

### 3. Architecture & Data Logic

- **Total Effects (211)** — Real, already built. `FailureEffect.objects.count()`. Tier A.
- **Effects List, Description** — Real, already built. `FailureEffect.name`/`.description`. Tier A.
- **High Severity (S ≥ 7) KPI, and the Severity (S) field shown in the Effect Details panel** — Genuinely new. `FailureEffect` has no severity field at all; severity today lives only on `RiskEvaluation`, scoped to `FailureMode`, not to an individual `FailureEffect`. Displaying/aggregating a per-effect severity requires a new field on `FailureEffect` (proposed `severity`) or a defined rule for deriving it from the parent failure mode's latest `RiskEvaluation.severity` (which would make every effect of a given failure mode share one severity — not obviously what the mockup intends, since effects clearly show independent S values in the propagation chain, e.g. E-004 = 8 vs. later-stage effects at 6/7/9). Tier D.
- **Affects System (128) KPI, Effect Type field ("Local Effect"), Effect Level field ("Component"), End Effect Yes/No flag** — Genuinely new. No such classification fields exist on `FailureEffect`. Tier D.
- **Propagation Paths (343) KPI, Effect Propagation Overview Sankey (widget 6), and "Next Level Effects"/"End Effect" links in the detail panel** — Genuinely new. This is the clearest evidence in the whole batch for the missing Local Effect → Next-Level Effect → System Effect → End Effect propagation-chain relationship (explicitly confirmed absent). Would need a proposed self-referential structure on `FailureEffect` (e.g., `next_level_effect` FK to self, plus a derived/level field) or a separate `EffectLevel`/`EffectChain` model. Tier D.
- **Improved / Worsened (↓ AP/RPN) KPIs** — Would be derivable once AP/RPN can be attributed to a specific `FailureEffect` (they currently attribute only to a `FailureMode` via `RiskEvaluation`) — blocked on the Severity-per-effect gap above. Tier D (dependent on Tier D item).
- **Effects Impact Dashboard / Effects List / Linked Failure Modes tabs** — Effects List (Tier A, basic list), Linked Failure Modes (Tier B, reverse of the real `failure_mode` FK — but see the M2M caveat below).
- **Effect Catalog / Effect Relationships / History tabs** — Genuinely new on all three: no catalog entity for effects (mirrors the Cause Catalog gap in mockup-16), no effect-to-effect relationship model beyond the still-unbuilt propagation chain, and no audit/history model for `FailureEffect`. Tier D.
- **Widget 1 "Impact on Risk Priority (AP)" line chart** — Genuinely new: requires both the lifecycle-phase-gate tracking flagged as absent on `RiskEvaluation` in mockup-17, *and* attributing that phase-tracked AP/RPN down to individual effects (same Severity-per-effect gap). Note this widget uses a 7-phase axis (Concept, Design, DV, PV, PPAP, SOP, Serial Prod.) that differs from mockup-17's 6-phase axis (Concept/Design Baseline, DV, PV, PPAP, SOP, Current) — an internal inconsistency in how many/which lifecycle gates the mockups assume. Tier D.
- **Widget 2 "Impact Distribution by Target"** — Mixed. The "Requirements" row is Tier B: `Requirement` is a real model and `FailureMode.requirement` is a real FK, so effects-count-by-requirement-with-improved/worsened-bucket is derivable via a join (`FailureEffect → FailureMode → Requirement`) once trend data exists. The "System Functions" row is also Tier B via `FailureMode.function`. "Characteristics", "Components", "Customers", and "Safety" as impact targets have no modeled relationship to `FailureEffect` or `FailureMode` at all in the confirmed grounding — Tier D for those four rows.
- **Widget 3 "Impact by Effect Level"** — Genuinely new; this is the second clear confirmation (after widget 6) that the mockups assume a 5-level effect hierarchy (Local/Subsequent×2/System/End) which does not exist on `FailureEffect`. Tier D.
- **Widgets 4 & 5 "Top Effects by AP Improvement" / "...with Increased Risk"** — Genuinely new for the same reason as the Improved/Worsened KPIs: needs per-effect AP tracked over time. Tier D.
- **Widget 6 "Effect Propagation Overview" Sankey diagram** — Genuinely new on the data side (propagation chain, as above) *and* a distinct charting concern: this is a true multi-stage Sankey/flow diagram with ribbon connectors between stacked segments — explicitly **not** covered by the Chart.js line/bar/donut charting-library decision already made for this project, and would need its own separate charting-approach decision (custom SVG, a dedicated Sankey library, or similar) before implementation could even be scoped technically. Tier D.
- **Widget 7 "Impact on Key Requirements (Top 10)"** — Derivable from real data, needs new query/aggregation logic: `Requirement` and `FailureMode.requirement` are both real, so joining `FailureEffect → FailureMode → Requirement` and bucketing by AP-trend-improved/no-change/increased is a genuine aggregation over an existing relationship, not a new field. This is the strongest Tier B item on the page. Tier B.
- **Effect Details panel — Description** — Real (Tier A, as above). Effect Type/Level/Severity/End Effect/Source — all Tier D (new fields, as above), except **Source ("Design FMEA")**, which is plausibly derivable from `failure_mode.fmea`'s existing FMEA-type attribute — Tier B if mapped that way, though the mockup's exact wording ("Design FMEA" vs. a raw `fmea_type` value) implies some display-layer translation.
- **Created / Last Updated (with actor)** — Genuinely new; no audit/timestamp fields confirmed on `FailureEffect`. Tier D.
- **Notes field** — Genuinely new, proposed free-text field distinct from Description. Tier D.
- **Linked To: Failure Modes (7), FMEA Items (2)** — Same architecture finding as mockup-16's Causes page: the real `FailureEffect.failure_mode` is a single mandatory FK (an effect belongs to exactly one failure mode), yet this panel shows one effect (E-004) linked to 7 different failure modes. Faithfully building this requires the same catalog/many-to-many re-architecture flagged for Causes. Tier D.
- **Linked To: Causes (6)** — Genuinely new relationship entirely: `FailureCause` and `FailureEffect` are both independent children of `FailureMode` with no direct link to each other in the confirmed model. Tier D.
- **Linked To: Functions (1)** — Real, derivable via `failure_mode.function` (one hop). Tier B.
- **Linked To: Requirements (2)** — Real, derivable via `failure_mode.requirement` (one hop). Tier B.
- **Linked To: Next Level Effects / End Effect** — Genuinely new; the propagation-chain gap again. Tier D.
- **Quick Impact block (Initial/Current AP, Change, inline trajectory line)** — Genuinely new; combines the per-effect-AP gap and the lifecycle-phase gap. Tier D.
- **"Create Action" button** — Real, already built: `RecommendedAction.failure_mode`/`.failure_cause` FKs exist (note: `RecommendedAction` has no `failure_effect` FK in the confirmed model, so "Create Action" from an Effect would need to resolve back to the effect's parent failure mode). Tier A (with a caveat on the exact linkage path).

**Behavioral logic implied**: the "Improved"/"Worsened" bucketing (green/red) across nearly every chart on this page implies a single, consistently-applied trend classification rule (comparing an effect's or requirement's earliest vs. latest associated AP/RPN) that does not exist today at the effect level — it would need to be defined once and reused across widgets 1, 2, 3, 4, 5, and 7 for consistency. The propagation chain (widgets 3 and 6, plus the detail panel's Next Level Effects/End Effect) implies a graph traversal capability (walking Local → Subsequent → System → End) that has no backing structure to traverse.

**Tier summary:** Tier A — Total Effects count, Effect description/name display, basic Create Action linkage. Tier B — Linked Functions and Linked Requirements (via the real `FailureMode.function`/`.requirement` FKs), the Impact on Key Requirements widget (widget 7), the Requirements/System Functions rows of the Impact Distribution widget, and Source-as-derived-from-FMEA-type. Tier C — none identified. Tier D — Severity/Effect Type/Effect Level/End Effect fields on `FailureEffect`, the entire 5-level propagation-chain relationship (widgets 3 and 6, plus Next Level Effects/End Effect links), per-effect AP/RPN trend tracking and every widget built on it (1, 4, 5, Quick Impact), the Cause↔Effect direct relationship, the Effect Catalog/M2M reuse pattern for Linked Failure Modes, History/audit trail, and Notes/timestamps. The Sankey diagram (widget 6) additionally needs its own charting-library decision beyond the existing Chart.js line/bar/donut choice.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 19 — Preventive Controls (source: mockup-19-preventive-controls.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Global chrome**: brand block; page title "Preventive Controls" with info icon; subtitle "Manage prevention controls that reduce the likelihood of causes and failure modes."; top-right project selector "Project: Headlamp X1 - PFMEA", search box, bell (badge "2"), help icon, avatar "JD"; action row "+ New Control" (solid blue), "Import", "Export", "Reports", "Filters".

**KPI/stat cards (6, single row)**
1. Total Controls — 156 — "All time"
2. Effective Controls — 102 — "65.4% of total"
3. Occurrence Reduction — 62% — "Average achieved"
4. High Impact Controls — 38 — "Reduce AP by ≥ Medium"
5. Linked to Operations — 72 — "46.2% of controls"
6. Last Updated — "12 May 2025" — "10:52"

**Tabs (5)**: Controls Overview, Controls List (active), Control Categories, Linked Failure Modes, History.

**Filter row**: "Search controls..." box; dropdowns — Category: All, Type: All, Control Type: All, Effectiveness: All, Linked To: All; "More Filters" button.

**"1. Control Categories"** left-hand panel (list, acts as a filter/nav within the page): "All Categories" 156 (selected/highlighted); Design Controls 28; Process Controls 41; Supplier Controls 18; Material Controls 12; Inspection Controls 22; Testing Controls 11; Maintenance Controls 9; Training / People 7; Environmental Controls 4; IT / Software Controls 2; Other Controls 2. "+ New Category" button at the bottom.

**"2. Preventive Controls List"** table (with a thumbnail photo per row) — columns: [thumbnail image], Control Name, Category, Type, Control Type, Linked To, Effectiveness, Operations Link, Resource Used, Actions ("…" menu). A "View:" toggle (grid/list icon pair) sits at the top right of this panel.
- 6 visible rows:
  - "Poka-Yoke bracket presence sensor" — Category badge "Process Controls" — Type "Poka-Yoke" — Control Type "Detection Prevention" — Linked To "FM-023, C-011" — Effectiveness "High (85%)" — Operations Link "OC-042 Assembly Verification" — Resource Used "Vision Sensor Keyence IV3 / Controller IV3"
  - "Assembly fixture with locator pins" — "Design Controls" — "Mistake Proofing" — "Physical Prevention" — "FM-023" — "High (90%)" — "OC-015 Fixture Setup" — "Fixture F-23 / Locator Pins (2x) Steel"
  - "Screw tightening torque control" — "Process Controls" — "Parameter Control" — "Process Prevention" — "FM-017" — "Medium (65%)" — "OC-031 Fastening Operation" — "Torque Wrench Stahlwille 730 (2–10 Nm)"
  - "Incoming material inspection" — "Supplier Controls" — "Inspection" — "Inspection Prevention" — "C-005" — "High (80%)" — "OC-006 Receiving Inspection" — "Caliper Mitutoyo 500-196 Gauge"
  - "Storage environment control" — "Environmental Controls" — "Condition Control" — "Environmental Prevention" — "C-012" — "Medium (60%)" — "OC-008 Warehouse Control" — "Temp/Humidity Sensor Elpro EHT"
  - "Operator training & certification" — "Training / People" — "Training" — "Human Error Prevention" — "C-008" — "Medium (60%)" — "OC-012 Operator Qualification" — "Training Module LMS-TM-12"
- Pagination: "Showing 1 to 6 of 156 controls"; page controls "‹ 1 2 3 … 26 ›"; "10 / page" selector.

**Bottom analytics row (4 widgets)**
1. "4. Controls by Type" — donut, center "156 / Total", legend: Physical Prevention 52 (33.3%) green, Detection Prevention 38 (24.4%) blue, Process Prevention 41 (26.3%) purple, Human Prevention 15 (9.6%) red, Others 10 (6.4%) gray.
2. "5. Effectiveness vs Occurrence Reduction" — scatter chart, X-axis "Occurrence Reduction (%)" (labels render as "0%, 0%, 0%, 100%" — appears to be a rendering artifact in the source image; not legible as clean increments), Y-axis "Effectiveness (%)" 0–100%. Legend: green "High", amber "Medium", red "Low", gray "Not Measured". ~20 scattered dots colored by band, roughly trending upward left-to-right (higher occurrence reduction correlates with higher effectiveness).
3. "6. Linked to Operations Controls" — donut, center "72 / Controls", legend: blue "Linked" 72 (46.2%), gray "Not Linked" 84 (53.8%). Button "View Operations Controls".
4. "7. Top Controls by Occurrence Reduction" — table, columns Control / Effectiveness / Occurrence Reduction: "Assembly fixture with locator pins" High (90%) 78%; "Poka-Yoke bracket presence sensor" High (80%) 72%; "Screw tightening torque control" Medium (65%) 58%; "Incoming material inspection" High (80%) 55%; "Storage environment control" Medium (60%) 48%. "View All" button.

**Right-hand "3. Control Details" slide-over panel** (for PC-0234), "X" close:
- Header "PC-0234" + "Active" badge (green), and "Process Control" badge below it.
- Thumbnail photo + title "Poka-Yoke bracket presence sensor".
- "Control Information": Category "Process Controls"; Type "Poka-Yoke"; Control Type "Detection Prevention"; Description "Vision sensor verifies presence of bracket before assembly can continue."; Effectiveness "High (85%)"; Implemented In "Assembly Line #3"; Owner — avatar "MK" + "Marko K."; Status "Active" (green pill); Created "03.03.2025 by Janez Demo"; Last Updated "12.05.2025 10:52 by Jan Demo"; Review Due "12.08.2025".
- "Linked To": Failure Modes 2 (View); Causes 2 (View); Functions 1 (View); Operations Controls 1 (View).
- "Resource Used": Resource "Vision Sensor Keyence IV3"; Quantity "1"; Location "Assembly Line #3"; Calibration / Check "Every 6 months"; Reference / ID "RS-00123"; plus a small thumbnail image of the resource.
- "Attached Documents": a PDF file row — "Installation_Manual_IV3.pdf" with an external-link icon.
- Buttons: "Edit Control", "View History".

**Footer status bar**: Database: OpenFMEA_Local, User: Janez Demo (Quality Engineer), Role: FMEA Editor, Workspace: Global, Version: 1.0.0, System Status (green dot).

### 2. Wireframe & UI/UX

**Layout**: sidebar + header + KPI row + tabs + filter row, then a 3-region main body: left "Control Categories" nav-list panel (narrow), center "Preventive Controls List" table with row thumbnails (widest), right persistent "Control Details" rail — a three-column split rather than the two-column (table + detail rail) layout used on the Causes/Effects pages. Below that, a full-width row of 4 analytics widgets.

**Sidebar structure**: "FMEA WORKSPACE" (Home, FMEA Projects, FMEA Team); **"ANALYSIS"** (not "FMEA ANALYSIS" as in mockup-16/17) containing System FMEA, DFMEA, PFMEA, PM-PFMEA (abbreviated differently than mockup-16/17's "Preventive FMEA (PM-FMEA)"), FMEA Matrix; "FMEA ELEMENTS" (Functions, Failure Modes, Effects, Causes, **Preventive Controls** [active/highlighted], Detection Controls, Actions); **"RISK & INSIGHTS"** (Risk Trajectory, Risk Propagation, Change Impact — a third grouping name/composition not seen in mockup-16, -17, or -18); **"VALIDATION"** (not "VALIDATION & CHANGE") containing Evidence & Tests, Validation Trajectory. No "CONTEXT (from Open-EQMS)" group and no "ANALYSIS TOOLS" group appear anywhere in this sidebar. Settings, Collapse at the bottom.

**Sidebar label note**: this mockup's sidebar item reads **"Preventive Controls"**, matching this page's own title — but mockup-16, -17, and -18 all use **"Prevention Controls"** for the equivalent sidebar item. This is a direct label inconsistency between mockups, not a typo introduced in this analysis — flagged as-is per instructions, not reconciled.

**Visual hierarchy**: row thumbnails (product/equipment photos) are a distinctive addition on this page not present on Causes/Effects — they visually anchor each table row and reappear in the Control Details panel and its Resource Used sub-block. Color coding: green = High effectiveness/Active status/Physical Prevention category; amber = Medium effectiveness; badges for Category, Control Type, and Status each use a differently-styled pill (light-blue/lavender for Category, plain text for Type, plain text for Control Type, green/amber text for Effectiveness) — three or four distinct classification "chip" styles stacked in one row, signaling several independent taxonomies applied to the same record.

**Interaction patterns implied**: clicking a table row (or its thumbnail) opens/refreshes the Control Details rail — currently showing the first row's record (PC-0234, "Poka-Yoke bracket presence sensor"). Category-panel items are likely clickable filters that narrow the table to that category (the currently-selected "All Categories" pill is visually highlighted, consistent with a single-select filter list). "View Operations Controls" and "View All" buttons imply drill-through to filtered sub-views. The scatter chart's dots plausibly support hover-for-detail (control name/values), though no tooltip is visible in this static state. The two small grid/list toggle icons above the table imply a card-view alternative to the current table view.

### 3. Architecture & Data Logic

- **Total Controls (156)** — Real, already built. `PreventionControl.objects.count()`. Tier A.
- **Control Name / Description** — Real, already built. `PreventionControl.name` / `.description`. Tier A.
- **Effective Controls (102, 65.4%), Occurrence Reduction (62% average), High Impact Controls (38)** — All genuinely new. `PreventionControl` has no `effectiveness`, no measured occurrence-reduction metric, and no linkage to a before/after `occurrence` value on any `RiskEvaluation`. Each KPI needs a new field (proposed `effectiveness_pct`) plus a defined "effective"/"high impact" threshold rule, and — for Occurrence Reduction specifically — a defined method for attributing a change in `RiskEvaluation.occurrence` to a specific control (the model today only ties occurrence to a `FailureMode`/evaluation, not to an individual control). Tier D.
- **Linked to Operations (72, 46.2%)** — Genuinely new. There is no Operations module/entity anywhere in the codebase (production orders, work tracking, "Operations Link" concept are all confirmed absent). Tier D.
- **Control Categories panel (Design/Process/Supplier/Material/Inspection/Testing/Maintenance/Training-People/Environmental/IT-Software/Other, with counts)** — Genuinely new. No `category` field exists on `PreventionControl`. Would need a proposed enumerated/lookup field plus a "New Category" management flow (the "+ New Category" button implies categories are themselves user-manageable records, not a hardcoded choice list — a further scoping question: is Category a simple choice field or its own lookup model?). Tier D.
- **Type column (Poka-Yoke / Mistake Proofing / Parameter Control / Inspection / Condition Control / Training)** — Genuinely new, a second classification axis distinct from Category. No field exists. Tier D.
- **Control Type column ("Detection Prevention" / "Physical Prevention" / "Process Prevention" / "Inspection Prevention" / "Environmental Prevention" / "Human Error Prevention")** — Genuinely new, a *third* independent classification axis on the same record (Category, Type, and Control Type are all distinct in this mockup). No field exists for any of them. Tier D.
- **Linked To column / panel section (Failure Modes, Causes, Functions)** — Derivable from real data via joins: `PreventionControl.failure_cause` is a real FK, so Causes is Tier A/B directly; Failure Modes and Functions require one/two additional hops (`failure_cause.failure_mode`, then `.function`) — straightforward join logic, no new fields needed. Tier B.
- **Effectiveness column/badge ("High (85%)" etc.)** — Genuinely new, same gap as the Effective Controls KPI above (no effectiveness field on `PreventionControl`). Tier D.
- **Operations Link column/section** — Genuinely new (Operations module absent, as above). Tier D.
- **Resource Used column/section (Resource, Quantity, Location, Calibration / Check, Reference / ID)** — Genuinely new. This is exactly the standing "Resource/Equipment/calibration-tracking entity" gap confirmed absent from the codebase (no gauge/equipment model with Quantity/Location/Calibration-interval/Reference-ID fields exists anywhere). Would need a new `Resource`/`Equipment` model plus a link from `PreventionControl` to it (likely many-to-one or many-to-many, since one resource — e.g., a specific torque wrench — could plausibly be used by multiple controls). Tier D.
- **Attached Documents (PDF row)** — Genuinely new. No file/attachment/document-storage capability exists anywhere in the app per the confirmed grounding. Tier D.
- **Owner field (avatar + name) in the detail panel** — Genuinely new. No owner/responsible field exists on `PreventionControl` (parallel precedent: `RecommendedAction.responsible_role` is real on a different model). Tier D.
- **Status field/badge ("Active")** — Genuinely new. No status field on `PreventionControl`; implies an unspecified lifecycle (at minimum Active vs. something else — Draft/Retired/Under Review are plausible but unconfirmed). Tier D.
- **Created / Last Updated (with actor), Review Due** — Genuinely new. No audit/timestamp fields, and no "review cadence" concept, exist on `PreventionControl`. Tier D.
- **Controls by Type donut, Effectiveness vs Occurrence Reduction scatter, Linked to Operations donut, Top Controls by Occurrence Reduction table** — All Tier D, each blocked on one or more of the new fields above (Type, Effectiveness, Occurrence Reduction, Operations linkage).
- **Controls Overview / Control Categories / Linked Failure Modes / History tabs** — Linked Failure Modes is Tier B (derivable join, as above); Controls Overview is likely a restatement of the same KPIs/charts (Tier D, same blockers); Control Categories tab is Tier D (new category model); History is Tier D (no audit/change-log model exists for `PreventionControl`).
- **"+ New Control" / "Edit Control" buttons** — Real, already built for the two existing fields (`name`/`description`); every other field editable through this form is blocked on that field existing first. Tier A (for the real fields) / Tier D (for the rest).

**Behavioral logic implied**: the Status badge ("Active") implies a lifecycle with unspecified transitions and, combined with "Review Due" (12.08.2025), implies a scheduled-review workflow (who is notified, what happens if the review lapses) — none of this exists today and would need full scoping (required fields, who can change status, validation, whether a lapsed review auto-flags the control as non-conformant). The Resource Used block implies calibration-interval tracking with its own due/overdue state, distinct from but structurally similar to the Review Due concept — likely warrants a shared "scheduled maintenance/review" pattern if both are built. The three-axis classification (Category/Type/Control Type) implies validation rules about which Type values are valid for which Category (e.g., "Poka-Yoke" Type only makes sense under certain Categories) — an unspecified but implied constraint that would need definition.

**Tier summary:** Tier A — Control Name/Description display and basic create/edit CRUD on those two fields, Total Controls count. Tier B — Linked To (Failure Modes/Causes/Functions) via the real `failure_cause` FK chain, and the Linked Failure Modes tab. Tier C — none identified; nothing here is a real field merely under-displayed — `PreventionControl`'s only real fields (`name`, `description`) are already surfaced at their full fidelity. Tier D — Effectiveness, Occurrence Reduction, Category, Type, Control Type, Operations linkage, Resource/Equipment tracking (Resource Used block), file attachments, Owner, Status/lifecycle, timestamps/audit trail, Review Due scheduling, and every chart/KPI built on top of these (Effective Controls, Occurrence Reduction, High Impact Controls, Linked to Operations, Control Categories panel, Controls by Type, Effectiveness vs Occurrence Reduction, Linked to Operations Controls, Top Controls by Occurrence Reduction, and the History tab).

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 20 — Detection Controls (source: mockup-20-detection-controls.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Global chrome**: brand block; page title "Detection Controls" with info icon; subtitle "Manage detection controls that help to detect failure modes or causes before they reach the customer."; top-right project selector "Project: Headlamp X1 - DFMEA" (note: DFMEA here, vs. "PFMEA" on mockups 16/17/18/19 — this page shows a different project-context FMEA type), search box, bell (badge "4"), help icon, avatar "JD"; action row "+ New Detection Control" (solid blue), "Import", "Export", "Reports", "Filters".

**KPI/stat cards (6, single row)**
1. Total Controls — 142 — "All time"
2. Effective Controls — 97 — "68.3% of total"
3. Detection Improvement — 58% — "Average improvement"
4. High Impact Controls — 31 — "Reduce D by ≥ 2"
5. Linked FM / Causes — 189 — "Total links"
6. Last Updated — "12 May 2025" — "10:52"

**Tabs (7)**: Overview, Controls List (active), Control Categories, Linked Failure Modes, Cause Relationships, D Improvement Trend, History.

**Filter row**: "Search detection controls..." box; dropdowns — Category: All, Type: All, Method: All, Implemented: All, Linked To: All; "More Filters" button.

**"1. Detection Control Categories"** left panel (list): "All Categories" 142 (selected); Inspection Controls 46; Test Controls 28; Monitoring Controls 24; Measurement Controls 18; Analytical / Software 12; Auditing Controls 7; Human Verification 5; Other Controls 2. "+ New Category" button.

**"2. Detection Controls List"** table (with a thumbnail photo per row) — columns: [thumbnail], Control Name, Category, Type, Detection Method, Linked To, Effectiveness, Resource Used, Operations Link, Actions ("…" menu). Grid/list view-toggle icons top right.
- 6 visible rows:
  - "AOI – Solder joint inspection" — "Inspection Controls" — "Automated" — "Optical inspection" — "FM-023, C-011" — "High (90%)" — "AOI Machine Model XS00 / Vision System" — "OC-041 Soldering Line Inspection"
  - "Electrical continuity test" — "Test Controls" — "Manual" — "Electrical test" — "FM-017" — "High (85%)" — "Multimeter Fluke 117" — "OC-023 Electrical Test Station"
  - "Temperature cycling test" — "Test Controls" — "Automated" — "Environmental test" — "FM-031" — "Medium (65%)" — "Temp Chamber ESPEC SH-642" — "OC-051 Environmental Lab"
  - "Microscopic visual inspection" — "Inspection Controls" — "Manual" — "Visual inspection" — "FM-008" — "Medium (60%)" — "Stereo Microscope Olympus SZ61" — "OC-015 Assembly Verification"
  - "Dimension verification (Critical)" — "Measurement Controls" — "Manual" — "Dimension check" — "FM-002, FM-045" — "High (80%)" — "Digital Caliper Mitutoyo 500-196" — "OC-032 Dimensional Check"
  - "SPC – Process trend analysis" — "Analytical / Software" — "Automated" — "Statistical analysis" — "FM-041" — "High (88%)" — "SPC Software Minitab 21" — "OC-060 SPC Monitoring"
- Pagination: "Showing 1 to 6 of 142 controls"; page controls "‹ 1 2 3 … 24 ›"; "10 / page" selector.

**Bottom analytics widgets (row of 4, "3"–"6")**
1. "3. Controls by Type" — donut, center "142 / Total", legend: Automated 58 (40.8%) blue, Manual 52 (36.6%) green, Semi-automated 18 (12.7%) amber, Software / Analytical 12 (8.5%) purple/orange (two similarly-colored entries), Other 2 (1.4%) brown/red.
2. "4. Detection Improvement (D Rating)" — stacked bar chart, X-axis "Initial D Rating" 1–10, Y-axis "Number of Controls" 0–60, legend: green "≥ 2 Improvement", amber "1 Improvement", gray "No Change", red "Worse". Bars generally increase in height from rating 1 through 10, tallest (~55) at rating 10.
3. "5. Top Controls by D Improvement" — table, columns Control / Initial D / Current D / Improvement: "AOI – Solder joint inspection" 7→2 ↓5; "Temperature cycling test" 8→3 ↓5; "SPC – Process trend analysis" 6→2 ↓4; "Electrical continuity test" 6→3 ↓3; "Dimension verification (Critical)" 7→4 ↓3. "View All" button.
4. "6. Controls Effectiveness Distribution" — donut, center "142 / Total", legend: High (≥ 80%) 65 (45.8%) green, Medium (50–79%) 54 (38.0%) amber, Low (< 50%) 15 (10.6%) red, Not Data 8 (5.6%) gray.

**Second bottom row (widgets 7–8, full width)**
- **"7. Links to Operations Controls"** — table, columns Operations Control / Description / Linked Detection Controls / Purpose: OC-041 "Assembly Line Verification" — "Verification of critical solder joints using AOI and manual inspection" — 6 — "Detect assembly defects before EOL"; OC-032 "Dimensional Check" — "Verify critical dimensions using calibrated measuring equipment" — 5 — "Detect dimensional deviations early"; OC-060 "SPC Monitoring" — "Monitor process characteristics and detect trends / out of control" — 4 — "Detect trends / drift and variation"; OC-015 "Assembly Verification" — "Visual and functional verification during assembly" — 7 — "Detect assembly errors and missing components". Button "View Operations Controls".
- **"8. Resource Utilization (Top 6)"** — table, columns Resource / Type / Used In Controls / Utilization (with a horizontal progress-bar + %): AOI Machine Model XS00 (Equipment) 12 — 85%; Stereo Microscope Olympus SZ61 (Equipment) 9 — 72%; Digital Caliper Mitutoyo 500-196 (Equipment) 8 — 67%; Multimeter Fluke 117 (Equipment) 6 — 52%; SPC Software Minitab 21 (Software) 4 — 48%; Temp Chamber ESPEC SH-642 (Equipment) 3 — 35%. Button "View All Resources".

**Right-hand "Control Details" slide-over panel** (for DC-0234), "X" close:
- Header "DC-0234" + "Active" badge (green), "Inspection Control" badge below.
- Thumbnail photo + title "Poka-Yoke bracket presence sensor" (same record/photo as PC-0234 in mockup-19 — the mockups reuse the same sample entity across both the Preventive and Detection Controls screens, which in the real 1-cause-can-have-both-a-prevention-and-a-detection-control model is plausible but notable).
- "Control Information": Category "Inspection Controls"; Type "Poka-Yoke (Presence Sensor)"; Control Type "Detection Prevention"; Description "Vision sensor verifies presence of bracket before assembly can continue."; Detection Method "Vision Sensor (Keyence IV3)"; Effectiveness "High (85%)"; Implemented In "Assembly Line #3"; Owner — avatar "MK" + "Marko K."; Status "Active"; Created "03.03.2025 by Janez Demo"; Last Updated "12.05.2025 10:52 by Jan Demo"; Review Due "12.08.2025".
- "Linked To": Failure Modes 2 (View); Causes 2 (View); Functions 1 (View); Operations Controls 1 (View).
- "Resource Used": thumbnail + Resource "Vision Sensor Keyence IV3"; Location "Assembly Line #3"; Calibration / Check "Every 6 months"; Reference / ID "VS-00123".
- "Attached Documents": "DC-0234_Installation_Manual.pdf" with external-link icon.
- Buttons: "Edit Control", "View History", "Clone".

**Footer status bar**: same pattern as other pages (Database/User/Role/Workspace/Version/System Status) — visible but cut at the very bottom edge of the captured image.

### 2. Wireframe & UI/UX

**Layout**: same three-region body as mockup-19 (left category-filter panel, center table with thumbnails, right persistent detail rail), followed by a 4-across analytics row and then a 2-across full-width row (Links to Operations Controls / Resource Utilization) — one more analytics row than mockup-19's single 4-across row.

**Sidebar structure — important caveat**: the left-sidebar navigation text in this specific mockup image renders as **garbled/illegible pseudo-text** (an apparent AI-image-generation artifact — verified at native resolution, not a crop/scaling issue). What is confidently legible: the group headers "FMEA WORRSPACE" (itself misspelled/garbled), an "ANAYSIƆS"-like heading (garbled), and "FMEA ELEMENTS" (legible). Under those headers the individual item labels are rendered as unreadable distorted glyphs (approximating shapes like "Setigin FMEA", "inspectia", "FMMEA", "PMEA PMɜrx", "FIƆEA Mɘmɔlys" under the analysis-type heading, and "Frɵɔctions", "Ronting Rɔɗɑs", "Ϧoɗɘs", "Human Verificatios", "Oɔctions" under FMEA ELEMENTS). Given this page's context (a Detection Controls page under a DFMEA project), these plausibly correspond to Design FMEA / Inspection / PFMEA / PM-FMEA / FMEA Matrix, and Functions / Failure Modes / Causes / Human Verification / Actions respectively — but this is an inference from context, not a reading, and should not be treated as confirmed label text. This illegibility is itself worth flagging to the mockup author since it may indicate a rendering defect in how this particular image was produced, separate from the deliberate inter-mockup naming inconsistencies documented elsewhere in this batch.

**Visual hierarchy and color coding**: identical semantic language to mockup-19 (green=high effectiveness/Active, amber=medium, red=low/worse, gray=no-change/not-measured), extended here with a distinct D-Rating stacked-bar convention (green "≥2 Improvement" down to red "Worse") mirroring mockup-17/18's severity/AP color logic. Thumbnails, multi-axis classification chips (Category/Type/Detection Method), and the Resource Used sub-panel are visually identical in structure to mockup-19, reinforcing that Preventive and Detection Controls are designed as sibling/parallel pages.

**Interaction patterns implied**: identical pattern to mockup-19 — row selection populates the right detail rail; category list acts as a filter; "View All"/"View Operations Controls"/"View All Resources" imply drill-through views. The new "Clone" button (not present on mockup-19's equivalent panel) implies a duplicate-record convenience action. The "D Improvement Trend" tab (not present on mockup-19) implies a dedicated trend-over-time view parallel to mockup-17's Risk Trajectory tab, but scoped to Detection ratings specifically.

**Sidebar/column-order inconsistency notes** (as instructed, described without reconciling):
- The Controls List table column order differs between the two "sibling" pages: mockup-19 (Preventive) orders the last two columns as **Operations Link, Resource Used**; this mockup (Detection) orders them **Resource Used, Operations Link** — reversed.
- The filter row here includes a "Method: All" dropdown in addition to "Type: All" — a filter axis not present on mockup-19's filter row (which stops at Control Type), even though both pages show a near-identical three-axis classification (Category/Type/Control Type here called "Detection Method") on their respective detail panels. The exact relationship between "Type" and "Method" as separate filterable axes is not resolved by this image.
- This page has 7 tabs (adding "Cause Relationships" and "D Improvement Trend" relative to mockup-19's 5 tabs) and 8 numbered analytics widgets (vs. mockup-19's 4) — the two pages are structurally parallel but not symmetric in scope as drawn.

### 3. Architecture & Data Logic

- **Total Controls (142)** — Real, already built. `DetectionControl.objects.count()`. Tier A.
- **Control Name / Description** — Real, already built. `DetectionControl.name` / `.description`. Tier A.
- **Effective Controls (97, 68.3%), Detection Improvement (58% average), High Impact Controls (31, "Reduce D by ≥ 2")** — All genuinely new. `DetectionControl` has no `effectiveness` field and no mechanism linking it to a before/after `RiskEvaluation.detection` value; "Reduce D by ≥ 2" implies per-control before/after Detection-rating tracking that doesn't exist. Same shape of gap as Preventive Controls' Occurrence Reduction KPI in mockup-19. Tier D.
- **Linked FM / Causes (189, "Total links")** — Partially derivable: `DetectionControl.failure_cause` is a real FK, so "Causes" links and (via `failure_cause.failure_mode`) "Failure Modes" links are both derivable through a join with new aggregation logic. Tier B.
- **Detection Control Categories panel (Inspection/Test/Monitoring/Measurement/Analytical-Software/Auditing/Human Verification/Other, with counts)** — Genuinely new. No `category` field exists on `DetectionControl` (mirrors the identical gap on `PreventionControl` in mockup-19). Tier D.
- **Type column (Automated / Manual / Semi-automated / Software-Analytical)** — Genuinely new, second classification axis. Tier D.
- **Detection Method column ("Optical inspection" / "Electrical test" / "Environmental test" / "Visual inspection" / "Dimension check" / "Statistical analysis")** — Genuinely new, a third classification axis, playing the analogous role to "Control Type" on the Preventive Controls page. Tier D.
- **Linked To column/section (Failure Modes, Causes, Functions)** — Derivable via the real `failure_cause` FK and its own chain to `failure_mode`/`function`, same as mockup-19. Tier B.
- **Effectiveness column/badge** — Genuinely new, same gap as the Effective Controls KPI. Tier D.
- **Resource Used column/section (Resource, Location, Calibration / Check, Reference / ID)** — Genuinely new; the identical standing Resource/Equipment gap flagged in mockup-19, reused here for detection-side equipment (AOI machines, microscopes, calipers, multimeters, SPC software). Tier D.
- **Operations Link column/section, "Links to Operations Controls" table (widget 7)** — Genuinely new; the confirmed-absent Operations module. Tier D.
- **Attached Documents (PDF)** — Genuinely new; no file/attachment capability exists anywhere in the app. Tier D.
- **Owner, Status, Created/Last Updated, Review Due (detail panel)** — All genuinely new, identical gaps to `PreventionControl`'s equivalent fields (no such fields exist on `DetectionControl` either). Tier D.
- **Controls by Type donut (widget 3), Controls Effectiveness Distribution donut (widget 6)** — Tier D, blocked on Type and Effectiveness fields respectively.
- **Detection Improvement (D Rating) stacked bar chart (widget 4), Top Controls by D Improvement table (widget 5)** — Tier D; both need per-control before/after Detection-rating tracking, which does not exist (D lives only on `RiskEvaluation`, scoped to a failure mode's evaluation history, not to an individual `DetectionControl`).
- **Resource Utilization (Top 6) table (widget 8)** — Tier D; blocked on the Resource/Equipment model gap, plus a derived "Utilization %" metric with no defined basis in any confirmed model.
- **Overview / Control Categories / Linked Failure Modes / Cause Relationships / D Improvement Trend / History tabs** — Linked Failure Modes is Tier B (derivable join, as above); Cause Relationships is genuinely new (no cause-to-cause or cause-to-control relationship model beyond the existing single `failure_cause` FK); D Improvement Trend needs the same per-control D-tracking gap as widget 4 (Tier D); Control Categories is Tier D (new category field/model); History is Tier D (no audit/change-log model for `DetectionControl`).
- **"+ New Detection Control" / "Edit Control" buttons** — Real, already built for `name`/`description`. Tier A (for those fields) / Tier D (for everything else on the form).
- **"Clone" button** — Not a new-field concern; a proposed convenience action that duplicates an existing `DetectionControl` record (copying its two real fields, `name`/`.description`, and presumably re-prompting for the `failure_cause` link). Feasible against the current model without new fields, though its exact behavior (what gets copied vs. reset) would need to be scoped. Tier A/B (a UI/workflow addition on top of existing fields, not blocked on any new field).

**Behavioral logic implied**: identical pattern to mockup-19 — a Status/lifecycle badge and a Review Due date implying a scheduled-review workflow, both unbuilt. The D Improvement Trend tab and widget 4/5 imply the same kind of before/after tracking as the Risk Trajectory concept in mockup-17, but scoped narrowly to a control's own Detection contribution rather than the full S/O/D/RPN picture — this suggests that if the lifecycle-phase-gate/trajectory-tracking capability from mockup-17 is ever built at the `RiskEvaluation` level, a parallel "attribute this trend to the specific control that caused it" capability would still be a separate, additional piece of work (RiskEvaluation trend ≠ per-control trend attribution).

**Tier summary:** Tier A — Control Name/Description display and basic create/edit CRUD, Total Controls count, and a Clone action built on existing fields. Tier B — Linked FM/Causes/Functions via the real `failure_cause` FK chain, and the Linked Failure Modes tab. Tier C — none identified; `DetectionControl`'s only real fields (`name`, `description`) are already surfaced at full fidelity. Tier D — Effectiveness, Detection Improvement, Category, Type, Detection Method, per-control D-rating before/after tracking (and everything built on it: Detection Improvement chart, Top Controls by D Improvement, D Improvement Trend tab), Operations linkage (KPI, column, and Links to Operations Controls table), Resource/Equipment tracking (Resource Used block and Resource Utilization table), file attachments, Owner, Status/lifecycle, timestamps/audit trail, Review Due, Cause Relationships tab, and History. The left-sidebar item labels in this specific mockup are additionally unreadable due to an apparent image-rendering artifact and could not be confirmed at all.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 21 — Process Control Characteristics (source: mockup-21-process-control-characteristics.png)

> Note: this mockup renders in a dark theme, unlike most of the other mockups in this batch. That is expected for this file, not a transcription error.

### 1. GUI Contents / Widgets (exhaustive list)

**Global chrome**
- Top-left logo lockup: "Open FMEA" wordmark (colored X-mark icon) with "Community Edition" subtitle beneath it.
- Hamburger/menu icon (☰) to the right of the logo.
- Page title "Process Control Characteristics" with a small circular "?" help icon beside it.
- Page subtitle text: "Define and manage process control characteristics — what is controlled in the process, how, by which resource, and what action is taken if not OK."
- Top-right header controls: a "Project:" dropdown reading "Project: Headlamp X1 - PFMEA"; a search box with placeholder "Search (Ctrl+K)"; a bell/notification icon with a red numeric badge "7"; a circular "?" help icon; a circular user avatar "JD" with a small green online-status dot.
- Header action button row: primary blue button "+ New Control Characteristic"; secondary buttons "Import ⌄", "Export ⌄", "Reports ⌄", "Filters ⌄" (each with a dropdown chevron, "Import"/"Export" also carry small download/upload icons).
- Bottom status bar (footer, full width): "Database: OpenFMEA_Local" | "User: Janez Demo (Quality Engineer)" | "Role: FMEA Editor" | "Workspace: Global" | "Version: 1.0.0" | "System Status" with a green dot, right-aligned.

**Left sidebar navigation** (dark, collapsible via "← Collapse" at the bottom), grouped under section labels:
- FMEA WORKSPACE: Home, FMEA Projects, FMEA Team
- CONTEXT (from Open-EQMS): System / Product / Process, System Characteristics Base, Characteristics Flow / Diagram, **Process Control Characteristics** (highlighted/active — blue background, currently selected page)
- FMEA ANALYSIS: DFMEA, PFMEA, System FMEA, Preventive FMEA (PM-FMEA), FMEA Matrix
- FMEA ELEMENTS: Functions, Failure Modes, Effects, Causes, Preventive Controls, Detection Controls, Actions
- RISK & INSIGHTS: Risk Trajectory & Propagation (with sub-items visible below it: Risk Trajectory, Risk Propagation, Risk Heat Map, PM-PFMEA Impact, Risk Summary, History), Change Impact
- VALIDATION & CHANGE: Evidence & Tests, Validation Trajectory
- Bottom of sidebar: "Settings" (implied) and "← Collapse" control.

**KPI / stat tiles row** (6 cards, each with an icon, a label, a large number, and a sub-caption):
1. Shield icon (blue) — "Total Controls" — **132** — "All status"
2. Check-circle icon (green) — "Active" — **118** — "89.4%"
3. Warning-triangle icon (amber) — "Not Effective" — **6** — "4.5%"
4. Clock icon (purple) — "Needs Review" — **8** — "6.1%"
5. Circular-alert/no-entry icon (red) — "No Reaction Plan" — **5** — "3.8%"
6. Chain-link icon (blue) — value **126**, sub-caption "95.5%" — the text label for this 6th tile is not legible/visible in the image (it appears clipped at the right edge of the row, immediately left of the detail panel); based on position and icon it likely denotes something like "linked to PFMEA," but this is not confirmed by legible text.

**Filter/toolbar row** (below KPIs): search box "Search control characteristics…"; dropdowns "Process / Operation: All", "Control Type: All", "Status: All", "Linked to PFMEA: All"; a "⋯ More Filters" button.

**Main data table** — columns exactly as shown: checkbox, ID, Process / Operation, Control Characteristic, Control Type, Method, Resource / Equipment, Frequency / Trigger, PFMEA Links, Status, Effectiveness.

Visible rows (10 of 132):
| ID | Process/Operation | Control Characteristic | Control Type | Method | Resource/Equipment | Frequency/Trigger | PFMEA Links | Status | Effectiveness |
|---|---|---|---|---|---|---|---|---|---|
| PCC-001 | 10 - Incoming Material | Material ID / Lot Verification | Administrative | Barcode Scan | Handheld Scanner | Each lot / Before use | 3 | Active | Effective |
| PCC-002 | 20 - Cutting | Cut Length Check | Measurement | Digital Caliper | Mitutoyo CD-15CPX | Each piece / In-process | 2 | Active | Effective |
| PCC-003 | 30 - Drilling | Hole Position Check | Measurement | Go / No-Go Gauge | Custom Gauge | Each piece / In-process | 2 | Active | Effective |
| PCC-004 | 40 - Welding | Weld Presence | Detection | Vision Sensor | Keyence IV3 | Each cycle / End | 3 | Active | Effective |
| PCC-005 | 40 - Welding | Weld Parameter OK | Monitoring | Weld Monitor | Fronius TPM5000 | Each cycle / During | 1 | Active | Partially Effective |
| PCC-006 | 50 - Assembly | Component Presence | Poka-Yoke | Presence Sensor | Banner QS18 | Before cycle release | 4 | Active | Effective |
| PCC-007 | 50 - Assembly | Torque Check - Bolt M8 | Measurement | Torque Tool | Atlas Copco STwrench | Each bolt / In-process | 2 | Active | Effective |
| PCC-008 | 60 - Functional Test | Function Test Pass | Test | Automated Test | Test Station 02 | Each unit / End | 2 | Active | Effective |
| PCC-009 | 70 - Packaging | Label / QR Verification | Detection | Vision Reader | Keyence IV2 | Each unit / End | 2 | Active | Effective |
| PCC-010 | 80 - Final Inspection | Dimensional Check | Measurement | CMM | Zeiss O-Inspect | Each lot / Sampling | 3 | Review | Partially Effective |

- Control Type badges are color-coded pills: Administrative (blue), Measurement (green), Detection (purple), Monitoring (cyan/light-blue), Poka-Yoke (gold/amber), Test (blue, visually similar shade to Administrative).
- Status badges: "Active" (green pill), "Review" (orange/red pill, only PCC-010 shown in this state).
- Effectiveness is shown as a colored dot + text: green dot "Effective", amber dot "Partially Effective".
- ID values (PCC-001 …) are rendered as blue hyperlinks.
- Pagination footer: "Showing 1 to 10 of 132 control characteristics", prev/next chevrons, page number buttons "1 2 3 4 … 14", and a "10 / page" dropdown.

**"Process Control Flow" diagram** (bottom-left panel) — a 5-node horizontal flow diagram connected by arrows, each node a distinct colored bordered box with an icon and heading:
1. Blue box, clipboard icon, heading "Process Step" — body "50 - Assembly / Install bracket"
2. → Green box, shield icon, heading "Control Characteristic" — body "Component Presence (PCC-006)"
3. → Purple box, wrench/tool icon, heading "Resource / Method" — body "Presence Sensor / Banner QS18"
4. → Amber/gold box, warning icon, heading "Result" — body "Detected = OK / Not detected = NOK"
5. → Red box, alert icon, heading "Reaction" — body "Block cycle / Create deviation / Quarantine unit"

**"Control Type Distribution" donut chart** (bottom-left, below the flow diagram) — center label "132 / Total"; legend: Poka-Yoke 32 (24.2%, green dot), Measurement 34 (25.8%, yellow dot), Detection 29 (22.0%, magenta/pink dot), Monitoring 18 (13.8%, purple dot), Test 11 (8.3%, red dot), Administrative 8 (6.1%, gray dot).

**"Effectiveness Overview" donut chart** (bottom-center) — center label "132 / Total"; legend: Effective 104 (78.8%, green), Partially Effective 16 (12.1%, amber/yellow), Not Effective 6 (4.5%, red), Unknown 6 (4.5%, gray).

**"Top PFMEA Links (by count)" table** (bottom-right of the two chart panels) — columns: PFMEA, Linked Controls, Top Cause/FM. Rows: PFMEA-001 / 24 / "Missing bracket"; PFMEA-002 / 18 / "Incorrect torque"; PFMEA-003 / 16 / "Weld not present"; PFMEA-004 / 14 / "Wrong orientation"; PFMEA-005 / 12 / "Wrong material". Button below: "View All PFMEA Links".

**Right-hand "Control Characteristic Details" panel** (persistent detail/inspector panel, docked right, with a close "X"):
- Header "Control Characteristic Details" with close (X).
- ID "PCC-006", status pill "Active" (green, top-right of the panel).
- Control-type badge "Poka-Yoke" (gold pill).
- Bold title "Component Presence".
- Description text: "Ensure component is present before assembly."
- Sub-tabs: "General" (active, blue underline), "Method & Resource", "Reaction Plan", "Links", "History".
- Under the "General" tab, a label/value list:
  - Process / Operation: 50 - Assembly
  - Operation Step: Install retaining bracket
  - What is Controlled: Bracket installed
  - Control Type: Poka-Yoke
  - Control Method: Presence Sensor
  - Trigger: Before cycle release
  - Status: Active
  - Effectiveness: Effective (green dot)
  - Owner: Marko K. (with small circular avatar initials "MK")
  - Created: 12.03.2025 by Janez Demo
  - Last Updated: 12.05.2025 10:32 by Jan Demo
  - Review Due: 12.08.2025
- Two buttons at the bottom of the panel: "✎ Edit" and "↻ View Full History".

### 2. Wireframe & UI/UX

**Structural layout**: Fixed left sidebar (dark, ~190px, collapsible) → fluid main content column → fixed right detail/inspector panel (dark, ~330px, dismissible with X). Header spans the full width above the sidebar/content/panel split; a thin footer status bar spans the full width beneath everything.

Main content column, top to bottom:
1. Page title + subtitle + header action buttons (single row).
2. Row of 6 KPI stat tiles (equal-width cards in a horizontal row).
3. Filter/search toolbar (single row: search box + 4 dropdown filters + "More Filters").
4. Full-width data table with checkbox-select rows, sortable-looking column headers, and pagination footer.
5. A three-panel row: "Process Control Flow" diagram (left, widest), "Effectiveness Overview" donut + "Top PFMEA Links" table (right column, stacked implicitly as two cards) — and directly beneath the flow diagram, a "Control Type Distribution" donut (so the bottom band is effectively a 2-column layout: left column = flow diagram over control-type donut; right column = effectiveness donut beside/above the top-links table).

The right detail panel is a persistent master-detail pattern: selecting a row in the main table (e.g., clicking "PCC-006") populates this panel with that record's full detail, organized into sub-tabs.

**Visual hierarchy**: Dark near-black background throughout; the active/selected sidebar item ("Process Control Characteristics") is highlighted with a filled blue background. KPI numbers are large and bold (white on dark), with small colored icon chips to their left giving each tile an at-a-glance category color. Status and effectiveness are consistently color-coded (green = good/active/effective, amber = attention/partially effective, red = not effective/no reaction plan, purple = needs review) across KPI tiles, table badges, and the donut charts — the same semantic palette is reused everywhere on the page. Row IDs and the "View All"/"View Full History" actions are rendered in link-blue to signal clickability. The detail panel's status pill and control-type badge visually echo the same badge styles used in the table, reinforcing that the panel is "this one row, expanded."

**Implied interactions**: Table rows and ID links are clickable and drive the right detail panel's content. The panel's five sub-tabs (General/Method & Resource/Reaction Plan/Links/History) imply a tabbed-detail pattern where each tab reveals a different facet of the same record without navigating away. "Edit" implies an inline-edit or modal/form flow. "View Full History" implies an audit-log drill-down (consistent with the "History" sub-tab). Filter dropdowns and "More Filters" imply a filter panel/drawer. "New Control Characteristic" implies a creation modal or dedicated form. Checkboxes in the table imply bulk selection tied to Export/Reports actions. Donut chart legends and the "View Details"-style links (e.g., "View All PFMEA Links") imply drill-through from summary chart to filtered list.

### 3. Architecture & Data Logic

- **Table rows (ID, Process/Operation, Control Characteristic name, PFMEA Links count)** — *Real, already built*: `ProcessCharacteristic.operation` (FK to the process operation), `ProcessCharacteristic.name`. The "PFMEA Links" count and "Top PFMEA Links" table are **Derivable from real data, needs new query/aggregation logic** — counting `RiskEvaluation`/`FailureMode`/`FailureCause` records that trace back to this `ProcessCharacteristic` via existing relationships is plausible but no such aggregation exists today.
- **Control Type (Administrative/Measurement/Detection/Monitoring/Poka-Yoke/Test), Method, Resource/Equipment, Frequency/Trigger, Status, Effectiveness, Owner, Review Due, "Reaction Plan" sub-tab, and the "Process Control Flow" diagram's Result/Reaction nodes** — **Genuinely new — no backing entity/field exists.** `ProcessCharacteristic` today has only `operation`, `name`, `description`, `cause_category_id`, and a generic `attributes` JSONField with no structured columns for any of these concepts. Realizing this mockup would require, at minimum, proposed new structured fields/enums such as `control_type` (enum: Administrative/Measurement/Detection/Monitoring/Poka-Yoke/Test), `method` (text/catalog), `resource_equipment` (text or FK to an equipment catalog), `frequency_trigger` (text or structured cadence), `status` (enum: Active/Review/etc.), `effectiveness` (enum: Effective/Partially Effective/Not Effective/Unknown), `owner` (FK to a person/role), `review_due` (date), and a structured reaction-plan sub-model (what action is taken if the check fails — the "Result"/"Reaction" nodes in the flow diagram).
- **KPI tiles (Total Controls, Active, Not Effective, Needs Review, No Reaction Plan, and the unlabeled 6th tile)** — all depend on the new `status`/`effectiveness`/reaction-plan fields above, so all are **Genuinely new**, contingent on those fields existing first (would then be simple counts/aggregations once the fields exist).
- **"Control Type Distribution" and "Effectiveness Overview" donut charts** — same dependency: **Genuinely new**, contingent on the proposed `control_type` and `effectiveness` fields.
- **Detail panel General tab fields (Created by, Last Updated by)** — audit/history is **Genuinely new**; no created/updated actor+timestamp fields are documented on `ProcessCharacteristic`, and no history model is described for it. The "History" sub-tab and "View Full History" button imply a full change-log/audit-trail entity that does not exist.
- **Cross-entity relationship implied**: the flow diagram and "PFMEA Links" both imply that a `ProcessCharacteristic` should be traceable through to `FailureMode`/`FailureCause`/`RiskEvaluation` records — plausible via existing FKs (`FailureCause`/`FailureMode` likely reference the same operation or characteristic chain) but the join/aggregation logic is not built.

**Standing project rule — Control Plan concept is specially gated.** This entire mockup is, in substance, a Control Plan: a structured, per-control record of control type, method, resource, trigger, and reaction-if-not-OK. Per project policy, **"Approved Control Plans are never silently modified — any Control Plan change is a reviewed, human-approved workflow."** Building any part of this mockup beyond passive display therefore isn't just "new fields" in the ordinary Tier D sense — it requires designing an approval/review state machine (e.g., Draft → Under Review → Approved, with edits to an Approved record routed through a change-request/approval flow rather than direct save) before any create/edit CRUD is built. This should be flagged strongly and separately in any future scoping discussion, not folded silently into a generic "add fields" task.

**Tier summary:** Tier A — none of substance beyond the bare `operation`/`name` linkage already read from `ProcessCharacteristic`. Tier B — PFMEA-link counts/"Top PFMEA Links" aggregation. Tier C — the base `ProcessCharacteristic` model exists but falls far short of what's shown (only name/description/operation/attributes JSON today vs. a fully structured control-plan record shown here). Tier D — Control Type enum, Method, Resource/Equipment, Frequency/Trigger, Status, Effectiveness, Owner, Review Due, Reaction Plan, the Process Control Flow diagram's Result/Reaction data, all derived KPI tiles and donut charts, and the audit/history trail — all genuinely new, and specifically **gated by the standing "Approved Control Plans are never silently modified" rule**, meaning this is not just unbuilt but requires an approval-workflow design before any edit capability is authorized.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 22 — Actions (source: mockup-22-actions.png)

### 1. GUI Contents / Widgets (exhaustive list)

**Global chrome**
- Top-left logo lockup: "Open FMEA" wordmark with "Community Edition" subtitle.
- Hamburger menu icon.
- Page title "Actions" with a circular "?" help icon.
- Subtitle: "Manage action plans and track completion to reduce risk and improve process effectiveness."
- Top-right header: "Project: Headlamp X1 - PFMEA" dropdown; search icon; bell/notification icon with a red badge "0"; circular "?" help icon; circular avatar "JD" (green online dot).
- Header buttons: primary blue "+ New Action"; secondary "Import ⌄", "Export ⌄", "Reports ⌄", "Filters ⌄".
- Bottom status bar: "Database: OpenFMEA_Local" | "User: Janez Demo (Quality Engineer)" | "Role: FMEA Editor" | "Workspace: Global" | "Version: 1.0.0" | "System Status" (green dot).

**Left sidebar** (light theme here, unlike mockup 21), grouped:
- FMEA WORKSPACE: Home, FMEA Projects, FMEA Team
- ANALYSIS: System FMEA, DFMEA, PFMEA, PM-PFMEA, FMEA Matrix
- FMEA ELEMENTS: Functions, Failure Modes, Causes, Preventive Controls, Detection Controls, **Actions** (highlighted/active)
- RISK & INSIGHTS: Risk Trajectory, Risk Propagation, Change Impact
- VALIDATION: Evidence & Tests, Validation Trajectory
- Bottom: Settings, "← Collapse".

**KPI / stat tiles row** (6 cards):
1. Clipboard icon (blue) — "Total Actions" — **68** — "All time"
2. Clock icon (amber) — "Open Actions" — **21** — "30.9% of total"
3. Warning-triangle icon (red) — "Overdue Actions" — **7** — "10.3% of total"
4. Check-circle icon (green) — "Completed Actions" — **47** — "69.1% of total"
5. Down-arrow icon (green) — "Risk Reduction (RPN)" — **1,258** — "Sum of reduction"
6. Trending/chart icon (purple) — "Avg. RPN Reduction" — **53%** — "Average"

**Tabs (horizontal, below KPIs)**: "Actions Overview" (active, blue underline), "Actions List", "Action Calendar", "Action Categories", "Risk Reduction", "History".

**Filter/toolbar row**: search box "Search actions…"; dropdowns "Status: All", "Type: All", "Linked To: All", "Priority: All", "Responsible: All"; "⋯ More Filters" button.

**Section 1 — "Actions by Status" donut chart**: center label "68 / Total". Legend (with counts/percentages as literally shown, note the counts do not sum to 68 — see Section 3 flag): Open 21 (30.9%, blue), In Progress 14 (20.6%, orange), Completed 47 (69.1%, green), Cancelled 3 (4.4%, gray), On Hold 2 (2.9%, purple). "View Details" link below.

**Section 2 — "Actions by Priority" donut chart**: center "68 / Total". Legend: High 20 (29.4%, red), Medium 31 (45.6%, orange), Low 15 (22.1%, green), None 2 (2.9%, gray). "View Details" link.

**Section 3 — "Risk Reduction Summary (RPN)" panel**: four stat sub-values — Total Initial RPN **2,378**, Total Current RPN **1,120**, Total RPN Reduction **1,258**, Reduction **52.9%** (down arrow, green). Below it, a **line chart** plotting two series (Initial RPN in red, Current RPN in green) across an X-axis of program phases: Concept, Design, DV, PV, PPAP, SOP, Serial Prod. Data-point labels visible along the descending line: 2,378 → 2,128 → 1,876 → 1,664 → 1,432 → 1,280 → 1,120. "View Trend" link.

**Section 4 — "Open & In Progress Actions" table**, columns exactly as shown: checkbox, ID, Action Title, Linked To, Type, Priority, Responsible, Planned Start, Due Date, Status, % Complete, RPN Reduction (Exp.), Days Overdue, Actions (⋯).

Visible rows (6 of 21):
| ID | Action Title | Linked To | Type | Priority | Responsible | Planned Start | Due Date | Status | % Complete | RPN Reduction | Days Overdue |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-2025-014 | Add bracket to protect presence sensor | FM-023 | Design Action | High | Marko K. (MK) | 20.03.2025 | 30.04.2025 | In Progress | 65% | ↓130 | 108 |
| A-2025-018 | Increase torque specification for screw | FM-017 | Process Action | High | Sara P. (SP) | 25.03.2025 | 15.04.2025 | In Progress | 40% | ↓90 | 93 |
| A-2025-022 | Add functional test at end of line | FM-031 | Detection Action | Medium | Janez D. (JD) | 10.04.2025 | 30.05.2025 | Open | 0% | ↓80 | 23 |
| A-2025-025 | Supplier quality improvement plan | C-005 | Supplier Action | Medium | Luka G. (LG) | 15.04.2025 | 15.06.2025 | Open | 0% | ↓70 | — |
| A-2025-026 | Poka-Yoke fixture for wiring connector | FM-045 | Design Action | High | Marko K. (MK) | 01.03.2025 | 31.03.2025 | In Progress | 90% | ↓160 | — |
| A-2025-031 | Operator training on installation | FM-008 | Human Action | Low | Ana T. (AT) | 05.05.2025 | 20.06.2025 | Open | 0% | ↓30 | — |

- Type badges are colored pills: Design Action (blue), Process Action (purple), Detection Action (teal), Supplier Action (?, orange-ish), Human Action (green-ish) — exact hue per type not fully certain from the image but each type has a distinct colored pill.
- Priority text: High (red), Medium (amber/orange), Low (green) — shown as colored text, not pill badges, in this table.
- Status badges: "In Progress" (orange pill), "Open" (blue/gray pill).
- % Complete rendered as a horizontal progress bar with % label.
- Responsible shown as small circular avatar-initials + first-name/last-initial.
- Pagination: "Showing 1 to 6 of 21 open/in progress actions", page numbers "1 2 3 4", prev/next, "10 / page" dropdown.

**Section 5 — "Action Timeline (All Open & In Progress)" — a Gantt-style chart.** Y-axis rows (one per action, label truncated with "…"): A-2025-014 "Add bracket to pro…", A-2025-018 "Increase torque sp…", A-2025-022 "Add functional test…", A-2025-025 "Supplier quality imp…", A-2025-026 "Poka-Yoke fixture f…", A-2025-031 "Operator training o…". X-axis: Mar 2025, Apr 2025, May 2025, Jun 2025, Jul 2025. Each row has a horizontal bar spanning its planned-start-to-due-date window, labeled with start/end dates (e.g., "20 Mar" … "30 Apr", with a "90%" label on one bar; "25 Mar"/"15 Apr"; "10 Apr"/"30 May"; "15 Apr"/"15 Jun"; "01 Mar"/"31 Mar" green bar; "05 May"/"20 Jun"). Legend: Open (blue dot), In Progress (orange dot), Completed (green dot), Overdue (red dot), On Hold (purple dot).

**Section 6 — "Actions by Type" donut chart**: center "68 / Total". Legend: Design Action 22 (32.4%), Process Action 18 (26.5%), Detection Action 10 (14.7%), Supplier Action 7 (10.3%), Human Action 6 (8.8%), Other 5 (7.4%). "View Details" link.

**Section 7 — "Top Risk Reductions (By Action)" table**, columns: Action ID, Action Title, Initial RPN, Current RPN, Reduction, % Red. Rows: A-2025-026 "Poka-Yoke fixture for wiring" 320/120/200/62%; A-2025-014 "Add bracket to protect sensor" 240/110/130/54%; A-2025-018 "Increase torque specification" 180/90/90/50%; A-2025-022 "Add functional test at EOL" 160/80/80/50%; A-2025-025 "Supplier quality improvement plan" 140/70/70/50%. "View All" button below.

**Right-hand "Action Details" panel** (persistent inspector, dismissible with X):
- Header "Action Details" + close (X).
- ID "A-2025-014"; status badges to the right: "In Progress" (orange pill), "High" (red pill), and a red-text line "⏱ 108 days overdue".
- Two small pill tabs/labels beneath the ID row: "Design Action" (blue pill) and "Permanent" (gray pill) — "Permanent" appears to denote an action-permanence classification (e.g., vs. an interim/temporary action) with no other value shown in this mockup.
- A small product-photo thumbnail (a bracket component).
- Bold title: "Add bracket to protect presence sensor".
- Description: "Install protective bracket to prevent damage and misdetection during assembly handling."
- Label/value list:
  - Linked To: FM-023 - Sensor misdetection
  - Linked Cause: C-011 - Physical damage during assembly
  - Function: Detect bracket presence
  - Category: Design
  - Type: Design Action
  - Responsible: Marko K. (avatar)
  - Support Team: Design Engineering
  - Owner: Quality Engineering
  - Created: 12.03.2025 by Janez Demo
  - Planned Start: 20.03.2025
  - Due Date: 30.04.2025
  - Actual Finish: (rendered as a blue progress bar reading "65%" rather than a date — appears to be a mockup layout/data-binding artifact; the label "Actual Finish" is followed by a % progress bar, not a finish date)
  - Effectiveness: "Expected: Hign released. Waiting for" — text is visibly truncated/cut off and contains an apparent typo ("Hign"); the full intended string cannot be read from the image.
  - Status: rendered oddly as "Status | In Progress" (the word "Status" appears to repeat as part of the value text — likely a mockup rendering artifact).
  - % Complete: a second progress bar, showing ~65-66%.
- "Risk Reduction (RPN)" sub-section: Initial RPN 240, Current RPN 110, Reduction 130, Reduction % 54% (down arrow, green).
- "Attachments" sub-section, three file rows each with an external-link icon: "Bracket_Design_v2.step", "DFMEA_Change_Impact.pdf", "Prototype_Test_Results.pdf".
- Bottom buttons: "✎ Edit", "⊗ Close Action", "⋯ More".

### 2. Wireframe & UI/UX

**Structural layout**: Fixed left sidebar → fluid main content → fixed right "Action Details" inspector panel (dismissible), matching the same three-column shell pattern as the other Actions/Risk pages in this set. Full-width header above, full-width footer status bar below.

Main content, top to bottom:
1. Title/subtitle + action buttons.
2. 6-tile KPI row.
3. Tab bar (Overview/List/Calendar/Categories/Risk Reduction/History) — this page is the "Overview" tab's content.
4. Filter toolbar.
5. A 3-column row of summary widgets: "Actions by Status" donut, "Actions by Priority" donut, "Risk Reduction Summary" stat block + line chart.
6. Full-width "Open & In Progress Actions" table with pagination.
7. A 3-column row: "Action Timeline" Gantt chart (widest, ~half width), "Actions by Type" donut, "Top Risk Reductions" table.

The right detail panel mirrors the master-detail pattern seen in mockup 21/23: selecting an action (e.g., A-2025-014) populates the panel with a photo, full field list, a dedicated RPN-reduction sub-block, and file attachments.

**Visual hierarchy**: KPI numbers are large/bold; colored icon chips categorize each tile (blue=volume, amber=open/pending, red=risk/overdue, green=success/reduction, purple=trend). Status/priority color coding is consistent site-wide: red=High/Overdue, amber/orange=Medium/In Progress, green=Low/Completed, blue=Open/Design, purple=trend/analytics, gray=Cancelled/None. The Gantt chart uses the same 5-color legend (Open/In Progress/Completed/Overdue/On Hold) as the "Actions by Status" donut, reinforcing one shared status taxonomy across chart types. RPN figures are consistently shown with a green down-arrow to signal "risk went down = good."

**Implied interactions**: Clicking a table row opens/updates the "Action Details" panel. The tab bar switches the entire body content (List = flat table view; Calendar = date-based view of due/planned dates; Categories = breakdown/management of action-type taxonomy; Risk Reduction = the RPN analytics in more depth; History = an audit/change log). "View Details"/"View Trend"/"View All" links imply drill-through from a summary widget to a filtered, fuller view of the same data. The Gantt bars are likely hover/click targets that surface the same detail panel. "Close Action" implies a status-transition action (moving the action to Completed/Cancelled) with probable confirmation. Attachment rows with external-link icons imply file download/open-in-new-tab behavior.

### 3. Architecture & Data Logic

- **Table rows (ID, Action Title, Linked To, Responsible, Due Date, Status)** — *Real, already built*: `RecommendedAction.name` (Action Title), `RecommendedAction.failure_mode` / `RecommendedAction.failure_cause` (Linked To — the model supports linking to either, nullable), `RecommendedAction.responsible_role` (Responsible), `RecommendedAction.due_date`, `RecommendedAction.status`.
- **"Linked Cause: C-011" field in the detail panel** — *Real, already built*: this is `RecommendedAction.failure_cause`, distinct from `failure_mode` — both nullable FKs already exist on the model, so an action showing both a `Linked To` (failure mode) and a `Linked Cause` (failure cause) simultaneously is plausible only if the UI resolves both relationships, which today's schema supports structurally (though a single `RecommendedAction` row links to at most one of `failure_mode` or `failure_cause` per the grounding — showing both together as in this mockup would need clarification of whether that's two separate FK reads or an inferred pass-through, e.g. cause → its failure mode).
- **Days Overdue (108, 93, 23…)** — *Derivable from real data, needs new query/aggregation logic*: `due_date` exists; overdue-days is `today − due_date` for any action not in a terminal status — no such computed field/annotation exists yet.
- **Status badges/donut (Open, In Progress, Completed, Cancelled, On Hold)** — **flag: real status enum mismatch.** The real `ActionStatus` enum is open / in_progress / completed / verified / cancelled. This mockup shows **"On Hold" in place of "Verified."** This is not merely an unbuilt field — it is a direct mismatch with the existing enum's 5th value and should be called out explicitly as a design decision to reconcile (rename/add a status, or treat "On Hold" as an additional 6th state) before any implementation.
- **Priority (High/Medium/Low/None), Type (Design/Process/Detection/Supplier/Human Action/Other), Category, Support Team, Owner, Planned Start, Actual Finish, % Complete, Effectiveness, "Permanent" classification, Function field, Created-by/Created-at audit fields** — *Genuinely new — no backing entity/field exists.* Today's `RecommendedAction` model has exactly: name, description, failure_mode-or-failure_cause link, responsible_role, status, due_date. Every one of these would need a proposed new field: `priority` (enum), `action_type` (enum/catalog), `category` (unclear if distinct from `action_type` — the mockup shows both "Category: Design" and "Type: Design Action" with the same value, possibly redundant), `support_team` (FK or text, distinct from `responsible_role`), `owner` (FK, distinct from `responsible_role`/`support_team`), `planned_start` (date), `actual_finish` (date — though the mockup itself renders this inconsistently, as a % bar rather than a date, so its exact intended shape is unclear), `percent_complete` (int), `effectiveness` (enum, mirroring the pattern proposed for mockup 21's control effectiveness), `is_permanent`/action-permanence flag (boolean or enum vs. "Interim"), `created_by`/`created_at` audit fields. "Function: Detect bracket presence" is plausibly **Derivable from real data** if it means the `Function` linked (via `FailureMode`) to this action's failure mode — traversable through existing FKs, but no such join/display exists today.
- **"Responsible: Marko K." shown with a personal avatar** — *Real field, not yet exposed as shown*: `RecommendedAction.responsible_role` exists, but `ResponsibleRole` is described as a name/description catalog, not a person roster tied to login. The mockup's use of individual named people with avatars (Marko K., Sara P., Janez D., Luka G., Ana T.) implies either `ResponsibleRole` rows are literally per-person catalog entries (workable today, but semantically stretches "role"), or a deeper user/roster linkage that does not exist — worth flagging as a scope question for a future review.
- **Risk Reduction (RPN) figures — Initial RPN, Current RPN, Reduction, Reduction %, and the RPN trend line chart, at both the summary level (Section 3) and per-action level (Section 7, and the detail panel's "Risk Reduction (RPN)" block)** — *Derivable from real data, needs new query/aggregation logic.* Both `RecommendedAction` and `RiskEvaluation` exist and are indirectly linkable via `FailureMode`/`FailureCause`, so "RPN before this action" vs. "RPN after this action" is computable by finding the `RiskEvaluation` rows for the linked failure mode/cause before and after the action's completion — but no such correlation/aggregation logic exists today. The RPN-trend-by-program-phase line chart (Concept/Design/DV/PV/PPAP/SOP/Serial Prod.) additionally implies a **new field**: no "program phase" tag exists on `RiskEvaluation` or `FailureMode` today, so bucketing evaluations into named APQP-style milestones is Tier D on top of the Tier B trend logic. Chart-type note: a **line chart** is within the just-decided Chart.js policy (line/bar/donut), so no charting-library gap here for Sections 1–3, 6.
- **"Action Timeline" Gantt chart (Section 5)** — *Genuinely new*, on two counts: (1) it depends on `planned_start`/`actual_finish`/`percent_complete` fields that don't exist yet, and (2) a Gantt chart is **not a standard Chart.js type** and falls outside the charting-library decision just made (which covers line/bar/donut only) — this needs a separate charting approach/library decision.
- **Attachments (Bracket_Design_v2.step, DFMEA_Change_Impact.pdf, Prototype_Test_Results.pdf)** — *Genuinely new*: no file/attachment storage exists anywhere in the app today. Would need a new attachment model (file, filename, content-type, uploaded-by, uploaded-at, FK to `RecommendedAction`) plus upload/storage/download plumbing, and validation (file-type/size limits) as part of any future scoping.
- **"Action Categories" tab** — *Genuinely new*: implies a manageable catalog/taxonomy of action types, which doesn't exist (no `ActionType`/category model today).
- **"History" tab and "View Full History"-style implied audit trail for actions** — *Genuinely new*: no change-log/audit model is documented for `RecommendedAction`.
- **Data-consistency note**: the "Actions by Status" donut's legend counts (21+14+47+3+2 = 87) do not sum to its own "68 Total" center label or to the page's "Total Actions: 68" KPI — this is very likely a mockup data-generation inconsistency (illustrative numbers, not computed), worth flagging as a caveat rather than a spec to replicate literally.

**Tier summary:** Tier A — Action Title, Linked To (failure_mode/failure_cause), Responsible (role), Due Date, Status (core CRUD fields already on `RecommendedAction`). Tier B — Days Overdue computation, RPN-reduction correlation (summary, per-action table, and detail-panel RPN block) via existing `RecommendedAction`↔`RiskEvaluation` linkage, and the "Function" field via FK traversal. Tier C — `ResponsibleRole` exists but falls short of the person-roster-with-avatar shown; the base RPN-history data exists (`RiskEvaluation` rows are themselves a history) but the program-phase-bucketed trend view is well beyond it. Tier D — Priority, Type/Category, Support Team, Owner, Planned Start, Actual Finish, % Complete, Effectiveness, Permanent/Interim flag, Created-by/at audit fields, file Attachments, the Action Categories tab, the Actions "History" audit tab, the program-phase tag needed for the RPN trend chart, and the Action Timeline Gantt chart (both for its missing date fields and because Gantt is outside the just-decided Chart.js line/bar/donut policy). **Also flag explicitly**: the mockup's status set (Open/In Progress/Completed/Cancelled/On Hold) does not match the real `ActionStatus` enum (open/in_progress/completed/verified/cancelled) — "On Hold" replaces "Verified" — a genuine enum mismatch to resolve, not just a gap.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---

## Mockup 23 — Risk Matrix (source: mockup-23-risk-matrix.png)

> Note: this mockup also renders in a dark theme (like mockup 21), differing from the light-themed mockup 22 elsewhere in this batch.

### 1. GUI Contents / Widgets (exhaustive list)

**Global chrome**
- Top-left logo lockup: "Open FMEA" wordmark with "Community Edition" subtitle.
- Page title "Risk Matrix" (no help icon visible next to it, unlike mockups 21/22).
- Subtitle: "Visualize and evaluate risks based on Severity (S), Occurrence (O) and Detection (D)."
- Top-right header: "Project: Headlamp X1 - PFMEA" dropdown; a search (magnifying-glass) icon (icon-only, no visible text search box unlike mockups 21/22); bell/notification icon (no numeric badge visible); circular "?" help icon; circular avatar "JD" (blue circle, small green online dot).
- Header buttons (right of subtitle, above the tab bar): "▽ Filters", "⊞ View Options", "⤓ Export ⌄".
- No bottom status bar is present on this page (unlike mockups 21/22) — the page ends with the sidebar's "← Collapse" control at the very bottom-left; no footer database/user/role/workspace/version bar is visible.

**Left sidebar**, grouped (dark theme, note the group labels/order differ slightly from mockups 21/22's sidebar — described as literally shown here):
- Top-level: Consolidated Home
- WORKSPACE: FMEA Projects list, FMEA Team
- CONTEXT: Engineering Context panel, System / Product / Process, System Characteristics Base, Process Control Characteristics, Characteristics Flow / Diagram
- FMEA ANALYSIS: DFMEA, PFMEA, Preventive FMEA (PM-FMEA) tab
- FMEA ELEMENTS: Failure Modes, Effects, Causes, Preventive Controls, Detection Controls
- RISK: **Risk Matrix** (highlighted/active, filled blue background), Risk Trajectory & Propagation
- VALIDATION & CHANGE: Evidence & Tests, Validation Trajectory, Change Impact
- Bottom: "← Collapse".

**Tab bar** (below title/subtitle): "Matrix View" (active, blue underline), "Risk Trajectory & Propagation", "Risk Heat Map", "PM-FMEA Impact", "Risk Summary", "History".

**"Risk Matrix (S × O)" grid** (main widget, left/center of page):
- X-axis header "Occurrence (O)" spanning 10 columns labeled 1 "Very Low", 2 "Low", 3 "Low", 4 "Medium", 5 "Medium", 6 "High", 7 "High", 8 "High", 9 "Very High", 10 "Very High".
- Y-axis header "Severity (S)" spanning 10 rows labeled (top to bottom) 10 "Very High", 9 "High", 8 "High", 7 "High", 6 "Medium", 5 "Medium", 4 "Low", 3 "Low", 2 "Very Low", 1 "Very Low".
- 10×10 grid of colored cells (green → yellow → orange → red heat gradient, increasing toward the top-right / high-S-high-O corner), forming a classic risk heat-map.
- Numbered black circular badges (white-on-black numbers 1–10) placed on specific cells, presumably marking the 10 plotted risks (FM-001…FM-010) at their Severity×Occurrence coordinates:
  - Badge "3" at S=10, O=6
  - Badges "1" and "2" together at S=10, O=8
  - Badge "5" at S=10, O=10
  - Badge "4" at S=9, O=5
  - Badge "6" at S=8, O=5
  - Badge "7" at S=8, O=7
  - Badge "8" at S=8, O=9
  - Badge "10" at S=5, O=4
  - Note: cross-checking against the table below, badges 2, 4, 6, and 8 land exactly on their listed FM's S/O values, but badges 1, 3, 7, and 10 are each offset by one row and/or column from their corresponding table row (e.g., badge "1" sits at S=10 while FM-001's table row lists S=9). This is likely mockup drawing imprecision rather than an intentional design detail, but is noted here rather than silently corrected.
- Footnote text beneath the grid: "RPN = Severity (S) × Occurrence (O) × Detection (D)".

**"Risk Level (RPN)" legend card** (right of the grid): four rows, each a colored dot + label/range + count:
- Red dot — "Extreme" — "RPN ≥ 240" — count **5**
- Orange dot — "High" — "120 ≤ RPN < 240" — count **3**
- Yellow dot — "Medium" — "40 ≤ RPN < 120" — count **1**
- Green dot — "Low" — "RPN < 40" — count **1**

**"Total Risks" card** (below the legend card): large number **10**, with a "View as List" link beneath it.

**"Risks in Matrix" table** (full-width, below the grid), columns exactly as shown: ID, Failure Mode, Effect, S, O, D, RPN, Risk Level, Current Controls, Linked FMEA, Location.

All 10 rows visible:
| ID | Failure Mode | Effect | S | O | D | RPN | Risk Level | Current Controls | Linked FMEA | Location |
|---|---|---|---|---|---|---|---|---|---|---|
| FM-001 | Lamp not illuminating | No light output | 9 | 8 | 7 | 504 | Extreme | PC-01, DC-01 | PFMEA | Assembly |
| FM-002 | Water ingress | Electrical failure | 10 | 8 | 6 | 480 | Extreme | PC-02, DC-03 | PFMEA | Housing |
| FM-003 | Lens cracking | Reduced visibility | 9 | 6 | 7 | 378 | Extreme | PC-03, DC-04 | PFMEA | Lens |
| FM-004 | Connector loose | Intermittent light | 9 | 5 | 6 | 270 | Extreme | PC-04, DC-02 | PFMEA | Connector |
| FM-005 | LED overheating | Shortened life | 8 | 9 | 4 | 288 | Extreme | PC-05, DC-05 | PFMEA | LED Module |
| FM-006 | Reflector misalignment | Poor light pattern | 8 | 5 | 5 | 200 | High | PC-06, DC-06 | PFMEA | Reflector |
| FM-007 | Seal not seated | Water ingress | 7 | 7 | 5 | 245 | Extreme | PC-07, DC-07 | PFMEA | Seal |
| FM-008 | Label incorrect | Regulatory issue | 8 | 9 | 3 | 216 | High | PC-08, DC-08 | PFMEA | Labeling |
| FM-009 | Screw missing | Vibration / noise | 6 | 4 | 6 | 144 | High | PC-09, DC-09 | PFMEA | Assembly |
| FM-010 | Dimension out of spec | Fitment issue | 5 | 3 | 4 | 60 | Medium | PC-10, DC-10 | PFMEA | Housing |

- Risk Level badges: "Extreme" (red pill), "High" (orange pill), "Medium" (yellow pill).
- FM-ID values are blue hyperlinks.
- Pagination footer: "Showing 1 to 10 of 10 risks", prev/next chevrons, page "1", "10 / page" dropdown.

**Right-hand "Selected Risk" panel** (persistent inspector, dismissible with X):
- Header "Selected Risk" + close (X).
- "FM-002" (blue link/heading) with an "Extreme" badge (red pill) to its right.
- Bold title "Water ingress"; subtitle "Effect: Electrical failure".
- Four stat boxes in a row: S = 10, O = 8, D = 6, RPN = 480 (the RPN box is visually highlighted with a blue outline/border, distinguishing it as the key computed value).
- "Current Controls" sub-section: two rows — "PC-02 — Gasket installed and compressed" with a "Preventive" badge (green); "DC-03 — Water leak test (100%)" with a "Detection" badge (green).
- "Risk Path" sub-section: a 3-node horizontal diagram connected by arrows — box "Cause / Seal damage" → box "Failure Mode / Water ingress" (this middle box has a highlighted/bordered outline) → box "Effect / Electrical failure".
- "Linked" sub-section, label/value list: FMEA Type: PFMEA; Process / Operation: Housing Assembly; System / Product / Process: Headlamp X1; Design Responsibility: EE Team.
- "Actions" sub-section: a full-width blue button "View Actions (2)".
- "History (Last 3 Changes)" sub-section, three dated rows with an actor initials tag at the end of each line:
  - 12.05.2025 — "Severity changed: 9 → 10" — JD
  - 10.05.2025 — "Detection changed: 7 → 6" — AB
  - 09.05.2025 — "Risk created" — JD
  - "View Full History" button beneath the list.

### 2. Wireframe & UI/UX

**Structural layout**: Fixed left sidebar → fluid main content → fixed right "Selected Risk" inspector panel (dismissible), the same three-column shell as mockups 21/22. Header spans the top; unlike the other two mockups in this set, there is **no bottom status/footer bar** on this page.

Main content, top to bottom:
1. Title/subtitle, header action buttons (Filters/View Options/Export), tab bar.
2. A two-column row: the 10×10 Risk Matrix grid (left, dominant/widest element on the page) beside a narrow right-hand column stacking the "Risk Level (RPN)" legend card above the "Total Risks" card.
3. Full-width "Risks in Matrix" table with pagination.

The "Selected Risk" panel is a fourth, always-present column to the far right of the whole layout (not stacked under the matrix/table — it runs the full height of the page beside them), populated by clicking a numbered badge in the matrix or an FM-ID row in the table.

**Visual hierarchy**: The 10×10 heat-map grid is the single largest, most visually dominant element on the page — its green-to-red gradient immediately communicates risk concentration in the top-right (high Severity × high Occurrence) region without needing to read numbers. Numbered badges on the grid are high-contrast black circles with white numerals, standing out against every cell color. The "Risk Level (RPN)" legend uses the exact same 4-color semantic scale (red/orange/yellow/green = Extreme/High/Medium/Low) as the grid cells and the table's Risk Level badges, so the color coding is consistent across the chart, the legend, and the table simultaneously — a viewer can map a cell's color to a risk tier without consulting the legend. In the "Selected Risk" panel, the RPN stat box is given a distinct blue border/highlight among the four S/O/D/RPN boxes, emphasizing it as the single most important derived number. The "Risk Path" diagram's middle "Failure Mode" node is similarly outlined/highlighted, marking it as the anchor entity the panel is built around.

**Implied interactions**: Clicking a numbered badge on the matrix, or an FM-ID link in the table, populates the "Selected Risk" panel (as shown, FM-002 is currently selected). "View as List" under "Total Risks" implies switching the table to show all matrix risks (possibly redundant with the table already shown below — may imply a modal or a scroll-to/filter action instead). Tabs (Risk Trajectory & Propagation, Risk Heat Map, PM-FMEA Impact, Risk Summary, History) imply the "Matrix View" is one of several lenses on the same underlying risk data — a trend-over-time view, an alternate heat-map visualization, a program-impact view, a rolled-up summary view, and an audit/history log. "View Actions (2)" implies drill-through to the Actions page (mockup 22), pre-filtered to the two actions linked to this failure mode. "View Full History" implies an expanded audit-log view beyond the "Last 3 Changes" preview. The Current-Controls rows (PC-02, DC-03) are presumably clickable through to Process/Detection Control records.

### 3. Architecture & Data Logic

**Base functionality is already real and built.** Per the confirmed grounding, the Risk Matrix page already exists as a real, verified feature: a system-wide, method-filterable Severity×Occurrence grid with drill-down and a "top risks" list, backed by `RiskEvaluation` (`severity`, `occurrence`, `detection`, `result` JSONField, `method`, `evaluated_at`, `failure_mode`). For this mockup specifically:

- **The 10×10 grid itself, its color-coded heat cells, the numbered risk markers plotted by S/O, and the "Risks in Matrix" table (ID, Failure Mode, Effect, S, O, D, RPN, Risk Level)** — *Real, already built*: reads `RiskEvaluation.severity`, `.occurrence`, `.detection`, and the RPN/classification out of `RiskEvaluation.result`, joined to `FailureMode` for the Failure Mode/Effect text — cite the existing `risk_matrix` view.
- **"Risk Level (RPN)" legend counts (Extreme/High/Medium/Low with counts) and "Total Risks" (10)** — *Real, already built*: these are aggregate counts over the same `RiskEvaluation` rows already powering the grid/table, consistent with the already-verified drill-down/top-risks functionality.
- **"Selected Risk" panel's S/O/D/RPN stat boxes, Failure Mode/Effect title** — *Real, already built*: direct reads of the selected `RiskEvaluation` row (and its `FailureMode`), consistent with the drill-down capability already confirmed to exist.
- **"Current Controls" (PC-02/DC-03 with Preventive/Detection badges)** — *Real field, not yet exposed in this exact shape*: plausibly reads `ProcessCharacteristic`/control-linkage data already touched on in mockup 21, joined to this `FailureMode`/`RiskEvaluation` — the underlying control records exist as entities, but a "current controls for this risk" join/display in the Risk Matrix panel is not confirmed built.
- **"Risk Path" diagram (Cause → Failure Mode → Effect)** — *Derivable from real data, needs new query/aggregation logic*: `RiskEvaluation.failure_mode` links to the failure mode, and Cause/Effect are presumably reachable via existing `FailureCause`/effect relationships on that failure mode — the join exists in principle but this specific 3-node display is not confirmed built.
- **"Linked" sub-section (FMEA Type, Process/Operation, System/Product/Process, Design Responsibility)** — *Derivable from real data, needs new query/aggregation logic*: traceable through the failure mode's operation/system linkage, but the aggregated "Linked" summary view is not confirmed to exist as such.
- **"View Actions (2)" button and action count** — *Derivable from real data, needs new query/aggregation logic*: `RecommendedAction.failure_mode`/`.failure_cause` already link actions to this failure mode, so counting/filtering to "actions linked to FM-002" is a straightforward query against existing data, just not confirmed built as this specific drill-through.
- **"History (Last 3 Changes)" (Severity changed: 9→10, Detection changed: 7→6, Risk created, each with actor initials and date)** — *Derivable from real data, needs new query/aggregation logic*: because `RiskEvaluation` rows are themselves timestamped (`evaluated_at`) and attributed (`actor`), and are never overwritten (each new evaluation is a new row), a true "history of changes" for a failure mode is reconstructable by listing its `RiskEvaluation` rows in order and diffing consecutive severity/occurrence/detection values — but no dedicated "diff/change-log" computation or display exists today; this is aggregation logic on top of real data, not a new model.
- **"Risk Trajectory & Propagation" and "PM-FMEA Impact" tabs** — align with the explicit grounding note that RiskEvaluation rows are already a de-facto history, but no dedicated "trajectory" aggregation/query exists yet — *Derivable from real data, needs new query/aggregation logic* for trend-over-time views; "propagation" (how a risk change on one failure mode affects related/downstream failure modes) is *Genuinely new* if it implies cross-failure-mode causal linkage beyond simple FK traversal.
- **"Risk Heat Map" and "Risk Summary" tabs** — likely alternate aggregations/visualizations of the same already-real `RiskEvaluation` data; *Derivable from real data, needs new query/aggregation logic* pending confirmation of what each specifically renders.
- **Chart-type note**: the matrix/heat-map itself is a custom grid widget, not one of the standard Chart.js chart types (line/bar/donut) covered by the just-decided charting policy — but since the Risk Matrix is already real and built today, this is presumably already solved with existing implementation, not a new gap to flag.

**Explicit design-contradiction flag — per-FMEA "Project" scope selector.** The header shows a **"Project: Headlamp X1 - PFMEA" dropdown** at the top of this Risk Matrix page, implying the matrix/table/panel are scoped to one project/FMEA. This **directly conflicts with the already-implemented decision that the Risk Matrix is deliberately system-wide, with no per-project scoping** (only method-filterable). This is a genuine design contradiction between what has already been built and what this mockup visually implies, not merely an unbuilt feature — it should be called out explicitly for reconciliation (e.g., either the mockup's project selector is dropped/reinterpreted as a global navigation element unrelated to matrix scoping, or the system-wide-by-design decision is revisited) rather than treated as a routine gap to fill in.

**Tier summary:** Tier A — the core Risk Matrix grid, heat-map coloring, numbered risk markers, "Risks in Matrix" table, Risk Level/Total Risks aggregate counts, and the Selected-Risk-panel's S/O/D/RPN/Failure-Mode/Effect fields are all real and already built (cite the existing `risk_matrix` view and `RiskEvaluation` model). Tier B — Risk Path (Cause→FM→Effect) display, the "Linked" summary sub-section, "View Actions" count/drill-through, and the History-of-changes reconstruction from `RiskEvaluation` rows, all derivable from existing linked data via new query/aggregation logic; likewise the Risk Trajectory/Heat Map/Summary tabs as alternate aggregations of already-real data. Tier C — "Current Controls" display is plausible from existing control entities but not confirmed wired into this panel. Tier D — none of substance beyond what's covered above (no wholly new entity is required for this mockup — everything traces back to real, already-modeled entities), **except** that "Risk Propagation" (if it means cross-failure-mode causal impact modeling) would be Tier D. **Separately and explicitly flagged**: the per-FMEA "Project" scope selector shown in the header **contradicts** the already-implemented, deliberate system-wide (non-project-scoped) design of the Risk Matrix — a real design conflict to resolve, not a gap to close.

### 4. Explicit non-authorization note

This is a specification only — cataloged for future reference, not an implementation instruction or authorization to build.

---


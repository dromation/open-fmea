# Open FMEA – Data Flow, Validation & Learning Pipeline

## Core rule

A supplied GUI mockup is a **controlled validation baseline**, not merely a design suggestion.

If a later build:
- changes layout unexpectedly,
- loses a widget,
- makes a control non-functional,
- breaks responsive behavior,
- shows a wrong computed value,
- breaks a data link,
- or no longer matches an accepted mockup,

that finding is treated as a **software failure mode / validation failure**.

## Release loop

```text
Mockup baseline
    ↓
Rendered Open FMEA page
    ↓
Visual parity test + Functional test + Responsive test
    ↓
PASS ───────────────→ accepted baseline/release
    ↓ FAIL
Validation finding
    ↓
Software failure mode
    ↓
Change Impact
    ↓
Corrective change
    ↓
Affected tests + regression tests
    ↓
Human approval
    ↓
Learning case
    ↓
AI / case-memory corpus
```

## Separation of concerns

```text
UI / HTML
   ↓ commands / queries
Data-flow pipeline
   ↓
open_fmea.container  ← authoritative state
   ↕
SQLite / SQL         ← relational backend / migration / reporting
   ↕
JSON                 ← interchange
   ↕
JSONL                ← learning / RAG / external training corpus
   ↕
TXT / MD             ← human-authored knowledge sources
```

The AI layer may retrieve, compare, rank, explain and recommend. It does **not** silently approve or overwrite authoritative FMEA records.

## Required validation dimensions for every mockup

1. **Visual parity** — information hierarchy, widgets, panels, tables, legends, controls and key layout.
2. **Functional parity** — every visible control has an expected command/query behavior.
3. **Data parity** — counts, charts and drill-downs derive from the same authoritative objects.
4. **Responsive parity** — resize does not remove or overlap primary functionality.
5. **Traceability** — visual items can be traced back to records/links.
6. **Change impact** — a changed component identifies affected pages, calculations, links and tests.
7. **Regression** — previously accepted mockups must remain accepted unless a controlled baseline change is approved.

## Historical Open FMEA failures now used for learning


### CASE-HIST-001 — GUI shell visible but workspace blank
- Failure mode: Static shell renders while main application content fails to render.
- Cause: Version/schema/runtime integration regression; older state may override newer expected data shape.
- Detection: Observed functional regression in historical Open FMEA builds.
- Corrective direction: Add migration/default merge, diagnostics and render error boundary.
- Validation: VAL-GUI-HOME-001, VAL-GUI-RESP-001

### CASE-HIST-002 — Feature-complete appearance without feature-complete behavior
- Failure mode: Widgets/buttons are visible but do not execute the expected data operation.
- Cause: Presentation implementation progressed faster than shared command/data-flow wiring.
- Detection: Functional review across v1.2/v1.3 evolution.
- Corrective direction: Shared CRUD/import/export/history/transaction runtime.
- Validation: VAL-GUI-PROJ-001, VAL-GUI-TEAM-001, VAL-GUI-PS-001

### CASE-HIST-003 — GUI regression after adding new functionality
- Failure mode: A later build introduces features but moves away from supplied mockup layout or breaks previously accepted GUI behavior.
- Cause: No immutable per-page mockup baseline and no mandatory regression gate before release.
- Detection: Current user review of later Open FMEA builds.
- Corrective direction: Treat every mockup as a validation baseline; every GUI change requires mockup parity + functional + responsive regression.
- Validation: VAL-GUI-RESP-001

### CASE-HIST-004 — Visualization not connected to decision drill-down
- Failure mode: Risk matrix or chart exists visually but does not expose the underlying records or correct time interpretation.
- Cause: Visualization built as dashboard element rather than query over source-of-truth objects.
- Detection: User review and subsequent risk/timeline requirements.
- Corrective direction: All visual widgets must be reversible to their source record set and explicit time basis.
- Validation: VAL-GUI-RISK-001, VAL-GUI-TRAJ-001, VAL-GUI-CHANGE-001

## Mockup validation registry

### VAL-GUI-HOME-001 — Home
Baseline: Home mockup
- Left navigation, topbar, KPI cards, risk overview, validation trajectory, high-risk panel and engineering context remain visible in intended hierarchy.
- Widgets resize with browser width without overlapping or disappearing.
- Primary controls remain clickable after browser resize.
- All displayed KPI values are computed or traceable to container records.

### VAL-GUI-PROJ-001 — FMEA Projects
Baseline: FMEA Projects mockup
- Project KPI cards, project table/list, type/status/progress/owner/updated/actions match mockup information architecture.
- New/Open/Edit/Duplicate/Delete/Search/Filter actions work.
- Project selection changes active project context without corrupting other pages.
- Responsive layout preserves all project actions.

### VAL-GUI-TEAM-001 — FMEA Team
Baseline: FMEA Team mockup
- Team KPIs, members, roles and role description panel are represented.
- Add/Edit/Assign/Delegate/Remove are functional and audited.
- Role/authority changes propagate to team context and transaction log.
- Responsive layout does not hide member actions.

### VAL-GUI-SPP-001 — System / Product / Process
Baseline: System / Product / Process mockup
- Systems/Products/Processes are navigable as a hierarchy.
- Selected item shows details and linked characteristics/FMEA context.
- Create/Edit/Duplicate/Delete preserve parent-child integrity.
- Broken links are detected instead of silently ignored.

### VAL-GUI-CHAR-001 — System Characteristics Base
Baseline: System Characteristics Base mockup
- Characteristic KPI cards, tabs/filters/table/detail panel and bottom summaries follow mockup hierarchy.
- New/Edit/Duplicate/Delete/Filter/Search work.
- Characteristic links resolve to System/Product/Process and FMEA objects.
- Critical/Special/Key classifications remain visually and semantically distinct.

### VAL-GUI-RISK-001 — Risk Matrix
Baseline: Risk Matrix mockup + later corrections
- Matrix fills available browser width at normal widths and uses local scroll only at narrow widths.
- Each S/O cell shows the number of risks in that bucket.
- Clicking a cell/count lists only risks belonging to that S/O combination.
- Counts equal live DFMEA/PFMEA source records.
- Changing S/O/D updates RPN and re-buckets the risk.

### VAL-GUI-TRAJ-001 — Risk Trajectory
Baseline: Risk Trajectory mockup + time-selection correction
- Lifecycle and calendar time bases are selectable.
- User can select day/week/month/range or From/To where supported.
- Trajectory points link back to source risk.
- Time filtering does not alter authoritative source records.

### VAL-GUI-CHANGE-001 — Change Impact
Baseline: Change Impact mockup + legend/time corrections
- Both donut/pie charts have legends with values and percentages.
- Changes Over Time provides day/week view, a selectable range and a legend.
- Chart counts equal change records in the selected period.
- Change records link affected FMEA items and validation evidence.

### VAL-GUI-DFMEA-001 — DFMEA
Baseline: DFMEA mockup
- DFMEA table, ratings, controls, RPN, actions and detail panel preserve mockup structure.
- S/O/D editing recalculates risk deterministically.
- Linked effects/causes/controls/actions are reusable source objects.
- No duplicated authoritative objects are created by changing views.

### VAL-GUI-PFMEA-001 — PFMEA
Baseline: PFMEA mockup
- PFMEA process-step/function/failure/effect/cause/control structure follows mockup.
- Risk changes propagate to matrix, trajectory and action views.
- Process control and Poka-Yoke links are resolvable.
- Changes are audited.

### VAL-GUI-PS-001 — Problem Solving
Baseline: Ishikawa / WHY / 8D / Poka-Yoke design
- Ishikawa supports 5M/6M categories and links causes.
- 3WHY/5WHY chain is editable and traceable.
- 8D D0-D8 data persists and links containment/root cause/action/validation.
- Poka-Yoke links prevention/detection/reaction/evidence.
- Method outputs can become learning cases only after user confirmation.

### VAL-GUI-RESP-001 — All pages
Baseline: All supplied mockups
- No primary widget disappears because of viewport resizing.
- No global horizontal overflow caused by a single widget.
- Dense tables/graphs use local overflow where necessary.
- Layout remains usable across 320, 480, 768, 1024, 1366, 1920 and 2560 px widths.

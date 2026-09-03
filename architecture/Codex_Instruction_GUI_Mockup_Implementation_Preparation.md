# Codex Implementation Preparation — 23 Pixel-Matched GUI Screens

Status: preparation only. Do not implement from this document by rendering the PNG files as pages. The user clarified that the reference GUI screens must be prepared for implementation, not inserted into the running app as static screenshots.

Source images: `architecture/mockups/mockup-01-...png` through `architecture/mockups/mockup-23-risk-matrix.png`.

## 0. Binding Interpretation

The mockups are visual specifications. A finished implementation should recreate their layout, spacing, navigation, tables, panels, tabs, charts, badges, and detail panes as real Django templates and CSS, backed by real view models where domain data exists.

Do not implement "pixel identical" by serving the PNG as the page body. That gives visual identity but no application behavior, no accessibility, no data binding, and no useful path to a functional Open-FMEA app.

For backend-missing areas, implement only one of these, explicitly chosen per slice:

- Read-only UI prototype backed by non-persisted view-model data in the view, clearly isolated from domain persistence.
- Functional GUI backed by real Django/domain models after the relevant architecture decision exists.

Never create fake domain records, fake approvals, fake risk values, or fake AI decisions.

## 1. Global Implementation Rules

1. Reuse the existing Django app. Do not introduce a SPA rewrite.
2. Keep the shared shell and theme system in `theme.css` / `base.html`; extend tokens/components instead of duplicating one-off CSS per page.
3. Every page must be reachable through real Django routes and templates, not through image embedding.
4. No CDN dependencies at runtime. Any chart/icon/JS dependency must be bundled and must survive EXE packaging.
5. Tables must use real HTML tables where the mockup shows table data.
6. Charts and diagrams must be real HTML/SVG/canvas components, not screenshots.
7. If a field has no backend model yet, do not persist it silently. Keep it as isolated UI view-model data until its model slice is approved.
8. Keep image files as references under `architecture/mockups/`; do not move them into `static/` as runtime UI assets.
9. Each slice must include screenshot verification at `1536x1024` where the source mockup is full-size; three cropped mockups use their native sizes.
10. Each slice must pass `python -B manage.py check`, `python -B manage.py makemigrations --check --dry-run`, and the full pytest suite in both `open_fmea` and `open_fmea_training_set`.

## 2. Required Visual Acceptance

For each implemented page:

- Same first-viewport composition as the matching mockup.
- Same sidebar grouping and active-item position for that page.
- Same panel density, table density, tab placement, stat-card count, badge shapes, and major chart positions.
- Text may bind to real data, but visual rhythm must remain the same when values change.
- No text overlap at desktop `1536x1024`.
- No visible "not implemented" banners inside the production UI unless the slice is explicitly a UI prototype.

Recommended verification:

1. Render the target route at `1536x1024`.
2. Capture a screenshot.
3. Compare against the corresponding `architecture/mockups/*.png`.
4. Record deliberate differences in the slice report. Differences caused by real data are acceptable; layout drift is not.

## 3. Page Inventory And Target Routes

| # | Mockup | Target route | Backend status | Implementation type |
|---|---|---|---|---|
| 01 | Base App Shell | shared shell | Existing shell | Restyle shared shell only |
| 02 | Engineering Context Panel | `/engineering-context/` | Partial: Process/Operation/ProductCharacteristic/ProcessCharacteristic exist | Functional read-only first |
| 03 | Preventive FMEA / PM-FMEA | `/fmeas/preventive/` | Missing PM-FMEA/Asset/Maintenance model | UI prototype until model approved |
| 04 | Consolidated Home | `/` | Dashboard data exists partially | Functional dashboard restyle |
| 05 | FMEA Projects List | `/projects/` | `FMEAProject`, `FMEA` exist | Functional page |
| 06 | FMEA Team | `/projects/<stable_id>/team/` | Missing project membership model | Needs model slice or UI prototype |
| 07 | System / Product / Process | `/context/system-product-process/` | Product/Process exist; System missing | Partial functional page |
| 08 | System Characteristics Base | `/system-characteristics/` | System + classification catalog missing | Needs model slice or UI prototype |
| 09 | Characteristics Flow / Diagram | `/characteristics-flow/` | Product/Process characteristics and CauseInfluence exist | Functional first diagram possible |
| 10 | Evidence & Tests | `/validation/evidence-tests/` | Needs `ValidationTest` decisions | Do not implement functionally yet |
| 11 | DFMEA | `/fmeas/dfmea/` or FMEA-type scoped detail | `FMEA.fmea_type` exists | Functional filtered dashboard |
| 12 | PFMEA | `/fmeas/pfmea/` or FMEA-type scoped detail | `FMEA.fmea_type` exists | Functional filtered dashboard |
| 13 | Change Impact | `/validation/change-impact/` | Missing Change entity | UI prototype until model approved |
| 14 | Validation Trajectory | `/validation/trajectory/` | Same `ValidationTest` family as #10 | Do not implement functionally yet |
| 15 | Failure Modes | `/elements/failure-modes/` | `FailureMode` exists | Functional page |
| 16 | Causes | `/elements/causes/` | `FailureCause`, `CauseInfluence` exist | Functional page |
| 17 | Risk Trajectory & Propagation | `/risk/trajectory/` | Needs risk history / propagation model | UI prototype first |
| 18 | Effects | `/elements/effects/` | `FailureEffect` exists; propagation chain missing | Functional list + prototype diagrams |
| 19 | Preventive Controls | `/elements/preventive-controls/` | `PreventionControl` exists; richer fields missing | Functional list + prototype detail |
| 20 | Detection Controls | `/elements/detection-controls/` | `DetectionControl` exists; richer fields missing | Functional list + prototype detail |
| 21 | Process Control Characteristics | `/context/process-control-characteristics/` | `ProcessCharacteristic` exists; Control Plan model missing | Functional list + gated control-plan visuals |
| 22 | Actions | `/elements/actions/` | `RecommendedAction` exists | Functional page |
| 23 | Risk Matrix | `/risk-matrix/` | Existing Risk Matrix exists | Restyle existing functional page |

## 4. Recommended Slice Order

### Slice A — Shared Shell And Navigation

Goal: make the application shell match the mockup family.

Scope:

- Sidebar grouping and labels from the canonical navigation structure.
- Header density, project selector area, environment/status controls, light/dark compatibility.
- No fake pages with inert dead links. If a nav item is visible, route it either to a real implemented page or to an explicitly-scoped UI prototype page.

Files likely touched:

- `django_app/fmea_app/templates/fmea_app/base.html`
- `django_app/fmea_app/templates/fmea_app/_sidebar.html`
- `django_app/fmea_app/templates/fmea_app/_header.html`
- `django_app/fmea_app/static/fmea_app/css/theme.css`
- `django_app/fmea_app/static/fmea_app/js/app.js`
- `tests/test_gui_navigation_scope.py`

### Slice B — Home, Projects, Team Skeleton

Goal: implement mockups 04, 05, and the non-auth version of 06.

Backend:

- Use real `FMEAProject` and `FMEA` for Projects.
- For Team, do not build login/permissions. Either create a narrow `ProjectMembership` model slice first, or keep this page as UI prototype data only.

Pages:

- `/`
- `/projects/`
- `/projects/<stable_id>/team/`

### Slice C — Context And Characteristics

Goal: implement mockups 02, 07, 08, 09, 21 as a coherent context area.

Backend:

- Use existing `Product`, `Process`, `Operation`, `ProductCharacteristic`, `ProcessCharacteristic`, `CauseInfluence`.
- Do not invent a full `System` hierarchy or Control Plan model in this slice.
- Characteristics Flow can be SVG/HTML first, backed by real relationships where available.

### Slice D — FMEA Type Dashboards

Goal: implement mockups 03, 11, 12.

Backend:

- Use `FMEA.fmea_type` for DFMEA/PFMEA filters.
- Preventive FMEA / PM-FMEA remains gated unless the `preventive` FMEA type and any Asset/Maintenance dependencies are explicitly approved.

### Slice E — FMEA Element Pages

Goal: implement mockups 15, 16, 18, 19, 20, 22.

Backend:

- Use real `FailureMode`, `FailureCause`, `FailureEffect`, `PreventionControl`, `DetectionControl`, `RecommendedAction`.
- Where mockups show richer catalog, complaint, owner, file, equipment, or analytics fields, render only if model support exists; otherwise isolate as prototype sections until approved.

This slice can be split further:

- E1 Failure Modes + Causes
- E2 Effects + propagation placeholders
- E3 Preventive/Detection Controls
- E4 Actions

### Slice F — Risk Views

Goal: implement mockups 17 and 23.

Backend:

- Restyle existing `/risk-matrix/` for mockup 23.
- Do not silently change the existing system-wide Risk Matrix decision into per-FMEA scoping. If the mockup's project selector is required, make that its own explicit model/query decision.
- Risk trajectory needs risk history; if no history model exists, start as UI prototype only.

### Slice G — Validation And Change

Goal: prepare mockups 10, 13, 14.

Backend:

- Evidence & Tests and Validation Trajectory should share the future `ValidationTest` / `TestPlan` design.
- Change Impact needs a new Change entity and many-to-many affected-item relationship.
- File attachments, owner/person model, lifecycle phases, and charting must be decided before functional implementation.

## 5. Required New Shared Components

Implement these once, then reuse across pages:

- stat cards with compact deltas
- tab strip
- toolbar filters and project selector
- dense data table
- right-side detail panel
- status badge variants
- progress/risk bars
- lifecycle timeline
- small donut/line/bar chart primitives
- node/edge diagram primitive for flow and propagation views
- avatar/owner display primitive
- attachment list primitive, initially disabled unless storage is approved

## 6. Data Binding Matrix

Existing models usable now:

- `FMEAProject`
- `FMEA`
- `Product`
- `Process`
- `Operation`
- `ProductCharacteristic`
- `ProcessCharacteristic`
- `Function`
- `Requirement`
- `FailureMode`
- `FailureEffect`
- `FailureCause`
- `FailureMechanism`
- `PreventionControl`
- `DetectionControl`
- `RecommendedAction`
- `RiskEvaluation`
- `EvaluationDefinition`
- `CauseCategoryScheme`
- `CauseCategory`
- `CauseInfluence`

Models or decisions missing:

- real user/person/role/team membership
- System hierarchy
- ClassificationScheme / ClassificationTerm
- ValidationTest / TestPlan
- Change / affected-item history
- file/media attachment storage
- equipment/resource/calibration model
- complaint/CAPA/8D/5 Why/FTA/RCA/XDA integrations
- risk history / risk trajectory model
- effect propagation chain
- charting library/package decision

## 7. First Codex Prompt To Use

Use this as the first implementation prompt after this preparation:

```text
Implement Slice A only from architecture/Codex_Instruction_GUI_Mockup_Implementation_Preparation.md.

Goal: restyle the shared Django app shell and navigation to match the mockup family without implementing the 23 pages yet.

Rules:
- Do not render PNG mockups as application pages.
- Do not create fake domain records.
- Do not add backend models or migrations.
- Keep all runtime assets local/offline-safe.
- Preserve existing functional routes.
- Add tests proving the shell renders the canonical navigation structure and that any visible page route is real.
- Run manage.py check, makemigrations --check --dry-run, and full pytest in both open_fmea and open_fmea_training_set.
```

## 8. Explicit Reversal Of The Rejected Approach

A prior implementation attempt added routes that rendered the mockup PNGs directly as GUI pages. That was reverted because it did not satisfy the user's intended meaning. Future sessions must not repeat that approach.

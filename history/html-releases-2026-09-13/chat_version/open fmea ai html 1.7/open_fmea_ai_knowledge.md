# Open FMEA AI Knowledge Seed

This file is a human-readable companion to `open_fmea_ai_knowledge.jsonl`.

## Recommended architecture

- **Authoritative state:** `open_fmea.container`
- **Portable AI/case corpus:** `open_fmea_ai_knowledge.jsonl`
- **Human-authored context:** `.md` or `.txt`
- **Backend/desktop structured database:** SQLite
- **Interchange/API:** JSON
- **SQL export:** reporting/migration, not the primary browser runtime
- **Optional local neural models:** ONNX for small classifiers/embeddings; GGUF for an external local LLM runtime.

The single HTML should not silently train or replace authoritative FMEA data. It should:
1. index approved sources,
2. retrieve similar cases,
3. rank suggestions,
4. show provenance,
5. require human acceptance,
6. record feedback,
7. export approved learning cases for external training/RAG.

## Historical Open FMEA lessons included


### CASE-001 — Blank GUI after schema extension
- Failure mode: Only static shell renders; dashboard/navigation content missing.
- Cause: Older browser snapshot overwrote newer embedded data structure; required arrays were absent.
- Action: Schema merge/migration with default fallback and render error boundary.
- Result: Newer versions tolerate older snapshots and surface diagnostics instead of white screen.

### CASE-002 — Risk Matrix lacked traceable contents
- Failure mode: Risk matrix visualized risk zones but did not show how many risks were in a cell or which risks they were.
- Cause: Mockup-focused rendering without data-driven bucket aggregation.
- Action: Aggregate DFMEA/PFMEA by S/O, show count badge, drill down to filtered records.
- Result: Matrix is now a live view of FMEA data rather than a decorative heatmap.

### CASE-003 — Risk trajectory had no selectable time basis
- Failure mode: Trajectory showed lifecycle progression but could not answer time-window questions.
- Cause: Lifecycle mockup implemented without calendar query controls.
- Action: Add lifecycle/calendar mode, period selection and From/To dates.
- Result: Trajectory can support both development phase and calendar analysis.

### CASE-004 — Fixed-size widgets failed browser resizing
- Failure mode: Widgets/matrices/tables do not fit when the browser is resized.
- Cause: Fixed grid widths and minimum sizes inherited from static mockups.
- Action: Responsive auto-fit grids, minmax(0,1fr), local overflow for dense data, breakpoints.
- Result: Primary UI adapts; dense tables/matrices use local scrolling where needed.

### CASE-005 — Change Impact charts lacked explanatory legends/time granularity
- Failure mode: Charts were visually present but decision context was incomplete.
- Cause: Dashboard chart decoration implemented before explicit interpretation requirements.
- Action: Add legend with values/percentages and day/week temporal buckets.
- Result: Change Impact supports interpretation and temporal investigation.

### CASE-006 — Mockup pages existed without complete functional behavior
- Failure mode: Buttons/widgets look complete but actions do not modify or query shared data.
- Cause: Presentation layer developed ahead of universal action/transaction wiring.
- Action: Introduce shared CRUD, filters, transaction log, autosave, import/export and cross-module object links.
- Result: Open FMEA moves from dashboard prototype toward functional engineering application.

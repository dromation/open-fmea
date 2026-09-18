# Open-FMEA Architecture Decision — Charting/Visualization Library

Status: **Decided, 2026-09-04**, per explicit user direction ("adopt one now"). This is a policy decision, not an implementation instruction — no code changes yet. It exists so the next slice that needs a chart (DFMEA/PFMEA RPN trend, Change Impact, Validation Trajectory, Risk Trajectory & Propagation, Failure Modes' severity-vs-occurrence scatter, Effects' impact bars) can be instructed without re-litigating this question, and so every chart-bearing slice from here on uses the same library the same way.

## 1. Decision

**Chart.js** (MIT license, canvas-based, zero runtime dependencies, one UMD file).

Why this one, not an alternative: the app is a server-rendered Django app (no SPA framework, no build step — confirmed by the existing `app.js`/`theme.css` pattern used for the theme toggle), and it ships as an **offline-capable packaged EXE** (`packaging\build_exe.ps1`) with no guaranteed internet access at runtime. That rules out any CDN-hosted library or anything requiring a JS bundler/npm build step at deploy time. Chart.js's single-file UMD build can be vendored directly into `static/` and referenced with a normal `<script src="{% static %}">` tag, exactly like every other static asset in this codebase already works. It covers every chart type seen in the mockups so far except one (see Section 4).

## 2. Scope of this decision

This decision covers **line, bar (including stacked/diverging), and donut/pie charts only** — Chart.js's built-in chart types, which is everything Mockups 11-14, 17, 18, and 22's dashboards actually show (RPN trend lines, Actions-by-status donuts, impact-by-target stacked bars, impact-by-effect-level diverging bars) **except** the two items in Section 4.

## 3. How it gets used, going forward

- Vendor the library once, at `django_app/fmea_app/static/fmea_app/vendor/chartjs/chart.umd.min.js` (or equivalent — exact filename is an implementation detail for whichever slice first needs it), loaded via `{% static %}`, never a CDN URL.
- Each chart-bearing view passes its data to the template as a plain Python dict/list already computed server-side (matching the existing pattern — every current view computes its render data server-side, nothing is fetched client-side today) and injects it via Django's built-in `{{ data|json_script:"some-id" }}`, which safely escapes it as a `<script type="application/json">` block; a small inline `<script>` reads that JSON and calls `new Chart(...)`. No new AJAX/fetch endpoints unless a specific slice's design genuinely needs live refresh (none of the cataloged mockups show that).
- **Test convention going forward:** existing tests (`test_engineering_context.py`, `test_dfmea_pfmea_worksheets.py` when built, etc.) check for the *absence* of `<canvas` as a "no chart" signal on pages that shouldn't have one. Once a page legitimately has a chart, its test should assert the specific `<canvas id="...">` is present **and** that the `json_script` block contains the expected data — not just "a canvas exists somewhere."
- This does not retroactively change any already-approved or already-built slice. `Codex_Instruction_DFMEA_PFMEA_Worksheets_SliceD.md` (approved the same day as this decision) deliberately still excludes charts — that exclusion stands; a chart-bearing dashboard view is a later, separate addition to those same pages, not a rework of Slice D.

## 4. Explicitly NOT covered by this decision

- **Mockup 9's force-directed relationship graph** (Characteristics Flow) and **Mockup 18's Sankey-style propagation flow** are not standard Chart.js chart types. Mockup 9 also remains blocked on System Characteristics Base (Mockup 8) and a new relationship/edge entity regardless of charting — this decision does not unblock it. If/when that slice is picked up, it needs its own small follow-up decision (a Chart.js plugin, or a separate lightweight graph-layout library) — not assumed here.
- This decision does not touch the already-built Risk Matrix, which has no chart today and doesn't need one to keep working.
- No AI-driven chart content (e.g. "Similar Failure Modes" match-percentage visuals) is authorized by this decision — that's a separate, unspecced AI capability question (Mockup 15), untouched here.

## 5. What this unblocks

Per `OpenFMEA_DNA_CoreReference.md`'s 2026-09-04 status-check table: richer DFMEA/PFMEA dashboards (RPN trend, Actions donut), Change Impact, Validation Trajectory, and Risk Trajectory & Propagation all listed charting as one of their blockers. This decision clears that specific blocker for each — each still needs its own architecture review/instruction before implementation (rule 8 still applies; this is a shared-dependency decision, not a blanket go-ahead).

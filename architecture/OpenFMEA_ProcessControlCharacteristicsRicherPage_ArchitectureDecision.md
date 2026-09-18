# Open-FMEA Architecture Decision — Process Control Characteristics: Richer Standalone Page (Mockup 21, second pass)

Status: **Decision, 2026-09-06** — proposing a firm, narrow default for the user to approve or correct. Written in direct response to two independent, converging user-supplied wireframe specs for this mockup (2026-09-05/06), both confirming the same content Slice H's own decision doc had already cataloged and explicitly deferred as "not this increment": KPI tiles, two donuts, the Process Control Flow diagram, a right-docked detail panel with five sub-tabs, and a PFMEA-links rollup. This document picks that deferred content back up now that the user has confirmed it via two independently-produced specs, and proposes the narrowest real version of each piece — no code changes yet.

## 1. What already exists (Slice H, built and independently verified 2026-09-05)

`ProcessCharacteristic` carries all nine control fields real data can already populate: `control_type` (6-value enum), `method` (free text), `resource_equipment` (free text), `frequency_trigger` (free text), `status` (Active/Review/Inactive, default Active), `effectiveness` (Effective/Partially Effective/Not Effective/Unknown, default Unknown), `owner` (FK `ResponsibleRole`), `review_due` (nullable date), `reaction_plan` (free text). `process_characteristic_list`/`process_characteristic_detail` already exist with a GET-form filter (`control_type`, `status`). No KPI row, no chart, no right-docked panel, no PFMEA aggregation — Slice H's own decision doc named all of these as out of scope for that increment, not as rejected forever.

## 2. Decision 1 — KPI row: six tiles, all six map onto real, already-built fields

Total (`.count()`), Active (`status="active"`), Not Effective (`effectiveness="not_effective"`), Needs Review (`status="review"`), No Reaction Plan (`reaction_plan=""` or null), Linked (per Decision 5's PFMEA-link definition below). All six are cheap aggregate queries over data that already exists — no new field needed. The icon-chip visual variant (a colored icon square left of label/value) is new CSS only — no confirmed `.stat-tile` example in this codebase has an icon today; add it as an additive modifier class, not a redesign of the base `.stat-tile`.

## 3. Decision 2 — PFMEA Links: the coarse, already-derivable version only

**No real per-characteristic-to-specific-`FailureMode`/`FailureCause` link exists anywhere in this codebase, and this document does not create one.** `ProcessCharacteristic` reaches an FMEA only indirectly: `operation` → `Operation.process` → `Process.fmea` → `FMEA`. Propose: "linked to PFMEA" means the characteristic's `Operation`'s `Process` belongs to an `FMEA` with `fmea_type == "process"` — a real, already-derivable, whole-FMEA-level fact, computed via `select_related`, not a new join table. "PFMEA Links" count on a characteristic = 1 if that chain resolves to a process-type FMEA, else 0 (today's data model gives no more granularity than "belongs to this PFMEA," never "specifically linked to this failure mode within it"). The "Top PFMEA Links" table (Section 5) is scoped the same way. **A real, finer-grained characteristic-to-specific-cause link is explicitly NOT this decision** — it would be a new join entity, the same category of decision `CharacteristicLink` (Slice L) already was for Mockup 9, and is not proposed here.

## 4. Decision 3 — right-docked detail panel and its five sub-tabs: server-rendered, GET-param only, no new client-side pattern

No right-docked persistent detail panel exists anywhere in this app today. Build it as a three-region page shell (sidebar / main table / detail panel), the detail panel populated server-side from a `?selected=<stable_id>` GET parameter — selecting a row is a normal link, not AJAX. The five sub-tabs (General / Method & Resource / Reaction Plan / Links / History) are **also** plain GET parameters (`&tab=general`), each a full server render, per the exact reasoning already recorded for this same open question when it first surfaced in the original Mockup 21 catalog: this avoids being the first place in the app to introduce client-side tab-swap-without-reload, which nothing else in this codebase does. **General** and **Method & Resource** render real fields already on the model. **Reaction Plan** renders the real `reaction_plan` text field. **Links** renders the PFMEA-link fact from Decision 2 (which FMEA, if any). **History**: no audit/change-log entity exists for `ProcessCharacteristic` anywhere (the same gap already flagged for Risk Matrix's own "History (Last 3 Changes)" panel and for `Change`/`ValidationTest`) — render only the two real timestamps `StableModel` already gives every entity (`created_at`, `updated_at`); do **not** build a "View Full History" beyond that, and do not fabricate a Created-by/Last-Updated-by actor trail that doesn't exist.

## 5. Decision 4 — Process Control Flow diagram: static HTML restating real field values, not new data

The five-box diagram (Process Step → Control Characteristic → Resource/Method → Result → Reaction) is a **presentational restatement of fields that already exist** on the selected characteristic — `operation` (Process Step), the characteristic's own `name` (Control Characteristic), `resource_equipment`/`method` (Resource/Method), and `reaction_plan` (Reaction). **"Result" has no real stored per-instance value** — the mockups show generic pass/fail language ("Detected = OK / Not detected = NOK") describing what the control *checks for*, not a logged outcome of any specific inspection event. Render "Result" as static descriptive text derived from `method`/`control_type` (e.g., restating what the control looks for), not as a fabricated status field — no new model, no new column. Plain HTML/CSS boxes with an arrow glyph between them, matching the pattern already used for exactly this diagram type in the original Mockup 21 catalog — no charting library involved, this is layout, not data visualization.

## 6. Decision 5 — two donut charts, via the already-adopted Chart.js

**Control Type Distribution** and **Effectiveness Overview**: both are `type: 'doughnut'` Chart.js charts over the same filtered `ProcessCharacteristic` queryset already backing the list/KPI row, grouped by `control_type` and `effectiveness` respectively. Same `json_script` + inline `<script>` + `new Chart()` pattern Slice K already established as this app's first real Chart.js usage — no new charting pattern, just the second and third real chart instances.

## 7. Decision 6 — Top PFMEA Links table: PFMEA + linked-control count only, no "Top Cause/FM" column

The mockups show a "Top Cause / FM" column per PFMEA row. **No ranking rule for "top" cause or failure mode exists anywhere in this project** (which cause, by what measure — highest RPN? most controls? most recent?) — inventing one here would misrepresent a judgment call as real data. Propose: the table shows PFMEA name + count of linked `ProcessCharacteristic`s only (both real, per Decision 2's link definition); the "Top Cause/FM" column is dropped from this increment, named here explicitly so it isn't silently reintroduced later without its own ranking decision.

## 8. Scope for this increment

1. Extend `process_characteristic_list` (view + template) with: the six-tile KPI row (Decision 1), the Process/Operation and Linked-to-PFMEA filter additions (extending the existing `control_type`/`status` GET-form filters, same server-side-reload pattern), the two donut charts (Decision 5).
2. New right-docked detail panel, `?selected=<stable_id>[&tab=general|method|reaction|links|history]` on the same route — no new route, an extension of the existing list page (Decisions 3, 4).
3. New "Top PFMEA Links" panel on the same page, per Decision 6.
4. No changes to `process_characteristic_detail`/`process_characteristic_form` — editing stays exactly where Slice H left it.

## 9. Explicitly out of scope

- Any real per-characteristic-to-specific-cause PFMEA link (Decision 2) — coarse whole-FMEA linking only.
- Any audit/history trail beyond the two real `StableModel` timestamps (Decision 4).
- Any Resource/Equipment catalog entity — `resource_equipment` stays free text.
- Any approval workflow or "Control Plan" governance language of any kind — this remains the retracted framing (see `OpenFMEA_DNA_CoreReference.md`'s standing correction); nothing here reopens it.
- Any AI-assisted classification or suggestion.
- A "Top Cause/FM" ranking (Decision 6).
- Any client-side/AJAX tab-swap or panel-swap — every interaction stays a plain GET link and full reload, matching this app's house convention everywhere else.

## Recommendation

**Recommendation: READY FOR IMPLEMENTATION.** Every piece maps to real, already-built data or a plainly-derivable aggregate; the two genuinely new UI primitives (right-docked panel, GET-param tabs) both follow patterns this project already chose deliberately for the same open question, rather than inventing a new one now.

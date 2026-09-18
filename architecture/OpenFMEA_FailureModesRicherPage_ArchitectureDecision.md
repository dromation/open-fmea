# Open-FMEA Architecture Decision — Failure Modes: Richer Standalone Page (Mockup 15)

Status: **Decision, 2026-09-06** — proposing a firm, narrow default for the user to approve or correct. Written in direct response to the user-supplied wireframe spec for this mockup (2026-09-05), which explicitly excluded the left App Shell/sidebar and explicitly stated this GUI must never become a central catalog for complaints/NCRs/incidents/8D/XDA/RCA/5Why/Ishikawa or any other organizational-problem tracking — that belongs to Open-EQMS, not Open-FMEA. This decision keeps that boundary and grounds every proposed widget in fields verified live in the current codebase.

## 1. What already exists (Slice G, built and independently verified 2026-09-05)

`failure_mode_list` (`django_app/fmea_app/views.py:383`) already renders every `FailureMode` across every FMEA as a flat table: FMEA name (linked), Function/Requirement label, Name, Description, Latest Risk Result (via the shared `_latest_risk_result()` helper — reads the newest `RiskEvaluation`, rendering either an RPN score with its classification or a qualitative priority, or "Not evaluated" if none exists), Effects count, Causes count, Actions (direct) count. `FailureMode` itself carries only `fmea` (FK), `function`/`requirement` (nullable FKs, mutually describing "what this failure mode affects"), `name`, `description` — no status field, no severity field of its own (severity lives on `RiskEvaluation`, not on `FailureMode`). No KPI row, no chart, no detail drawer, no chain diagram exist today — Slice G's own scope was the flat browse table only.

Verified live and relevant to this decision: `FailureMode.risk_evaluations` (→ `RiskEvaluation`, ordered newest-first), `.effects` (→ `FailureEffect`), `.causes` (→ `FailureCause`), `.recommended_actions` (→ `RecommendedAction`, nullable-FK'd from both `FailureMode` and `FailureCause` — so a `FailureMode`'s "direct" actions are only those FK'd straight to it, not those FK'd to one of its causes). `RiskEvaluation.result` is a `JSONField`; its classification/priority string is computed by the domain risk-scoring logic already in use by `_latest_risk_result()`, not a new field.

## 2. Decision 1 — KPI row: five tiles, all five map onto real, already-computed values

Total (`.count()` on the same base queryset), Not Evaluated (`risk_evaluations` empty — same "Not evaluated" fact `_latest_risk_result()` already computes), High/Critical Risk (latest evaluation's classification/priority string, reusing `_latest_risk_result()` unmodified — do not reimplement the RPN/priority logic a second time), No Cause Recorded (`causes_count == 0`), No Action Recorded (a failure mode counts as covered by an action either directly or through any of its causes — see Decision 3's coverage definition; this tile is "0 across both paths"). All five reuse existing per-row computations already in `failure_mode_list`; none require a new field or a new query shape, only aggregating what the view already builds per row.

## 3. Decision 2 — filter toolbar extension: server-side GET-form only, same convention as every other list page

Add `fmea` (dropdown of `FMEA.objects.all()`), `risk_level` (derived bucket over the same classification/priority string the KPI tiles use — not a new stored field), and `has_action` (yes/no over the coverage definition in Decision 3) as additional `<select name="...">` fields in the existing GET form, causing a full page reload exactly like every other filter in this app (`control_type`/`status` on Process Characteristics, etc.). No AJAX, no client-side filtering — this app has none anywhere and the established discipline is not to introduce it here.

## 4. Decision 3 — right-docked detail panel: server-rendered, GET-param only, "Actions" tab uses the real direct-or-via-cause coverage definition

Same pattern as Slice N's Process Control Characteristics panel (Decision 3 of that document): `?selected=<stable_id>[&tab=general|effects|causes|actions|risk]` on the existing `failure_mode_list` route, no new route, every tab a plain GET link. **General**: `name`, `description`, FMEA, Function/Requirement — all real. **Effects**: list the real `FailureEffect` rows via `.effects.all()`. **Causes**: list the real `FailureCause` rows via `.causes.all()`. **Actions**: list `RecommendedAction` rows reachable either directly (`.recommended_actions.all()`) or through any linked cause (`RecommendedAction.objects.filter(failure_cause__in=fm.causes.all())`) — state this "direct or via cause" definition explicitly in the rendered panel heading (e.g. "Actions (direct + via causes)") so it is never confused with the flat table's "Actions (direct)" column, which intentionally counts only the direct FK per Slice G's original, unmodified scope. **Risk**: the real `RiskEvaluation` history for this failure mode (`.risk_evaluations.all()`, already ordered newest-first by the model's own `Meta.ordering`) — severity/occurrence/detection/result per row, using `_latest_risk_result()`'s existing classification logic for each, not a new scoring path.

## 5. Decision 4 — FMEA Chain View diagram: static HTML restating the real FK chain, not a new graph

The mockup's "chain" (Function/Requirement → Failure Mode → Effect(s) / Cause(s) → Action(s)) is exactly the FK graph already on the model, one failure mode deep in each direction — not a new traversal, not a force-directed graph, not the same category of decision as the still-open `CharacteristicLink` visualization question from Mockup 9. Render as static, server-generated HTML boxes and arrow glyphs (same convention as Slice N's Process Control Flow diagram) listing the real linked rows above; if a branch is empty (no effects, no causes), render an explicit "None recorded" box rather than omitting the arrow silently, so the diagram never implies data that isn't there.

## 6. Decision 5 — Relationship / Coverage Summary panel: real counts only, no scoring, no fabricated completeness metric

A small panel stating, per the currently-filtered set: how many failure modes have zero causes, zero effects, zero actions (direct or via cause, per Decision 3), and zero risk evaluations. Every number is a `.count()`-style aggregate already available from the same queryset backing the KPI row and table — no weighting, no "completeness score," no invented percentage-of-maturity metric. If the mockup's spec implies a single composite "coverage %" figure, this decision explicitly declines to invent the weighting behind it; propose four plain counts instead, named here so a composite score isn't silently added later without its own decision.

## 7. Decision 6 — Risk Summary / Distribution donut: one Chart.js donut, grouped by the same classification the KPI tiles already use

One `type: 'doughnut'` chart over the filtered queryset, grouped by the same risk classification/priority bucket already computed by `_latest_risk_result()` for the KPI row (Decision 1) and the `risk_level` filter (Decision 2) — one canonical bucketing computed once per request and reused three times (KPI tile, filter option list, chart), not three separate implementations of the same logic. Same `json_script` + inline `<script>` + `new Chart()` pattern as Slice K/Slice N — the vendored local Chart.js file, no CDN, no new library.

## 8. Decision 7 — the Open-EQMS scope boundary, recorded here permanently, not just in this conversation

The user's spec was explicit and unprompted on this point, and it is recorded here as a standing architectural boundary, not merely conversational context: **this page must never become a general catalog of organizational problems.** Specifically, out of scope forever unless a future, separate, explicit decision reopens it: an Error/Defect Catalog entity, a Complaint/NCR link, 8D/XDA/RCA/5-Why/Ishikawa investigation workflows or entities, AI-based similarity/duplicate-detection across failure modes, and any image annotation/markup tooling. Open-FMEA's `FailureMode` stays what it already is — one node in a specific FMEA's engineering risk analysis — and problem/complaint/investigation tracking belongs to Open-EQMS as a separate system. This decision does not build any bridge or integration point to Open-EQMS either; that would itself need its own explicit decision (e.g., a stable-id reference field, a future cross-system link) and is not implied or prepared for here.

## 9. Scope for this increment

1. Extend `failure_mode_list` (view + template) with: the five-tile KPI row (Decision 1), the three new filter fields (Decision 2), the one donut chart (Decision 6), the Relationship/Coverage Summary panel (Decision 5).
2. New right-docked detail panel, `?selected=<stable_id>[&tab=general|effects|causes|actions|risk]` on the same route — no new route (Decisions 3, 4).
3. No changes to the FMEA worksheet's own failure-mode add/edit forms, to `failure_cause_list`/`failure_effect_list`/`prevention_control_list`/`detection_control_list` (Slice G's siblings), or to any FMEA detail/worksheet template — editing stays exactly where it already is.

## 10. Explicitly out of scope

- Error/Defect Catalog, Complaint/NCR link, 8D/XDA/RCA/5-Why/Ishikawa entities or workflows, AI similarity/duplicate detection, image annotation — permanently, per Decision 7, unless a future dedicated decision reopens any one of them.
- Any composite "coverage %"/maturity score (Decision 5) — plain counts only.
- Any new FK/traversal beyond what already exists on the model (Decision 4) — no new "chain" entity, no force-directed rendering.
- Any AJAX/client-side filtering or tab-swap — every interaction stays a plain GET link and full reload.
- Any change to `RecommendedAction`'s "direct" vs. "via cause" real distinction — the flat table's existing "Actions (direct)" column is not touched; the new panel's broader definition is additive and clearly labeled, never a silent redefinition of the existing column.
- Any Open-EQMS integration or cross-system reference field — not proposed, not prepared for, here.

## Recommendation

**Recommendation: READY FOR IMPLEMENTATION.** Every widget reuses real fields, real relationships, and the one risk-classification computation this app already has in exactly one place (`_latest_risk_result()`); the Open-EQMS boundary is recorded as a permanent architectural decision rather than left as an unwritten conversational understanding.

# Open-FMEA Architecture Decision — Risk Trajectory & Propagation (Mockup 17)

Status: **Decision, 2026-09-05** — proposing a firm, narrow default for the user to approve or correct. This is a decision document, not an implementation instruction — no code changes yet.

Author: Claude, acting as Open-FMEA Technical Architect.

## 1. What already exists, read directly from the code before writing this

`RiskEvaluation` (`fmea_app/models.py`) is: `failure_mode` FK, `definition` FK, `method`, `severity`/`occurrence`/`detection` (each `PositiveSmallIntegerField`), `result` (`JSONField`), `evaluated_at` (`DateTimeField`, default `timezone.now`), `actor`, `trigger`, ordered `Meta.ordering = ["-evaluated_at", "-id"]`. Nothing about this model overwrites a prior row — `evaluate_failure_mode()` in `services.py` always calls `.objects.create(**values)` (the `stable_id=`-keyed `update_or_create` branch exists only for import/reconstruction re-runs, not for the normal evaluate-a-failure-mode flow). This means **every risk change made through the normal GUI flow is already a new, timestamped row** — `RiskEvaluation` already *is* a history table, has been since Phase B, with no schema change needed to make that true.

No model or relationship anywhere tracks a lifecycle-phase dimension on a risk evaluation, and no relationship anywhere models one effect causing a next-level effect (`FailureEffect` is a flat list per `FailureMode`, no self-referential or chained FK).

## 2. Decision 1 — Lifecycle gate: a field on `RiskEvaluation`, not a new model

Add `lifecycle_gate` directly to `RiskEvaluation`: a plain, closed Python/Django `choices` enum (`CharField`, following the exact precedent of `FMEA.LIFECYCLE_CHOICES`/`ActionStatus`) with six values — Concept/Design, Design Verification, Process Validation, Pre-Production (PPAP), Serial Production (SOP), Current — defaulting to `"current"`.

Why a field, not a new model: this is exactly the case rule 6 describes as appropriate for a plain enum — a closed, structural vocabulary (six named engineering-lifecycle gates in a fixed, known order) that isn't something an organization would legitimately redefine, unlike `CauseCategoryScheme` (5M+E vs. 4M vs. custom) or the still-not-approved `ClassificationScheme`. And because `RiskEvaluation` already is the history table (Section 1), "trajectory" becomes nothing more than: **all `RiskEvaluation` rows for one `FailureMode`, ordered by `evaluated_at`, each carrying its `lifecycle_gate` tag.** No new entity, no new FK, no new migration beyond one `AddField`.

Backfill: existing rows get `"current"` via the field default (a plain `AddField` with `default="current"` backfills automatically — no data-migration script, no forced manual reclassification of historical rows). New rows created through the normal risk-evaluation flow also default to `"current"` unless the person entering the evaluation explicitly picks a different gate on the form — matching how every other optional classification field in this app behaves (nothing is auto-assigned per rule 5's own general principle: a human sets it, or it takes the honest default).

## 3. Decision 2 — Propagation chain: explicitly deferred, not part of this increment

**Do not build the `Failure Mode → Local Effect → Next-Level Effect → System Effect → End Effect` chain in this increment.** This is a deliberate exclusion, not an oversight, for three reasons:

1. **It is a materially different relationship shape from what exists today.** `FailureEffect` is a flat list per `FailureMode` (`failure_mode` FK, `name`, `description` — no self-reference, no level field, no chain). A propagation chain needs either a self-referential `FailureEffect.next_effect` FK plus a level/tier field, or a wholly new chain/edge entity — a real modeling decision (which shape, how a chain terminates, whether a chain can branch) that deserves its own review, the same way `CauseInfluence`'s edge model got its own connection-logic spec before being built.
2. **This is not a novel finding — it has already surfaced three separate times** (`OpenFMEA_DNA_CoreReference.md`'s Mockup 17 and Mockup 18 entries, and again implicitly in Mockup 23's "Risk Path: Cause → Failure Mode → Effect" panel), each time cataloged and explicitly not actioned. Building it now, as a side effect of the lifecycle-gate slice, would mean designing a cross-cutting relationship model under the time pressure of an unrelated slice instead of deliberately, and would pre-empt a decision that Mockup 18 (Effects) will need to make the same way regardless.
3. **Nothing about the lifecycle-gate/trajectory piece depends on it.** A trajectory view is fully useful — showing exactly what the mockup's RPN-vs-lifecycle-gate axis needs — without any propagation-chain data. Bundling the two would only make this slice larger without making the trajectory piece any more correct.

If/when a propagation chain is picked up, it should get its own architecture review (an effect-level hierarchy), not be retrofitted onto this decision.

## 4. Scope for the first increment

1. `lifecycle_gate` field on `RiskEvaluation` + migration (`AddField`, default `"current"`).
2. An optional `lifecycle_gate` field on the existing risk-evaluation entry form (`RiskEvaluationForm`, used by `evaluate_failure`), defaulting to `"current"` when left unset — not a required field, so the existing evaluate-a-failure-mode flow keeps working unchanged for anyone who doesn't care about gate tagging.
3. A simple trajectory view: per `FailureMode`, a table/list of its `RiskEvaluation` history — gate, method, S/O/D, the stored score/band (read verbatim from `result`, never recomputed — reusing the Risk Matrix's own already-established "never recompute in the display layer" rule), and `evaluated_at` — ordered chronologically (oldest first, the natural reading order for a "trajectory," explicitly the reverse of `RiskEvaluation`'s own default `-evaluated_at` ordering, which optimizes for "give me the latest" rather than "show me the story over time").
4. Reachable from the already-built Risk Matrix: a link from each `FailureMode` row shown in the Risk Matrix's existing cell drill-down (`risk_matrix_cell.html`) into that `FailureMode`'s trajectory page — reusing the drill-down's existing list-of-`FailureMode`s pattern rather than inventing a new one. A small index/landing page lists every `FailureMode` that has at least one evaluation, for the sidebar entry to land on.
5. One new sidebar entry ("Risk Trajectory & Propagation," matching the label already fixed by the canonical nav structure recorded in `OpenFMEA_DNA_CoreReference.md`), placed alongside the existing "Risk Matrix" entry.

## 5. Explicitly out of scope

- **The propagation chain** (Section 3) — no `Local Effect`/`Next-Level Effect`/`System Effect`/`End Effect` fields, no self-referential `FailureEffect` FK, no chain/edge entity, no propagation-probability gradient of any kind.
- **Any chart** — a trend line over the trajectory is a natural later addition once Chart.js is actually wired into a page somewhere else first (the charting-library decision authorizes the library in general; it doesn't by itself authorize a specific chart on a page that has none yet). This increment is a plain table, matching the Risk Matrix's own "no chart/canvas library" precedent.
- **PM-FMEA cross-referencing** — the mockup's "PM-PFMEA cross-reference panel" ties directly into the still-held-off Preventive FMEA/Asset/Maintenance track (the standing 2026-09-01 decision to hold that review). This stays excluded here for the same reason it's excluded everywhere else in this project right now — not reopened by this slice.
- **The mockup's "Risk Details" panel content beyond what a trajectory table already shows** (% reduction, primary cause, linked function/effects, "actions impacting this risk") — each of those is either derivable later from existing data with its own small aggregation-logic decision, or depends on the propagation chain this decision explicitly defers. Not assumed into this first increment.

## 6. What this decision does not propose

No new model, no new domain entity, no change to `FailureEffect`, `FailureMode`, `RiskRating`, or `EvaluationDefinition` beyond the one additive field on `RiskEvaluation`. No change to `classify_rpn`/`classify_severity_occurrence`/`calculate_action_priority`. No per-FMEA or per-project scoping mechanism (the trajectory is per-`FailureMode`, matching the Risk Matrix's own system-wide, no-project-entity precedent). No AI-assisted trend prediction or forecasting.

## Recommendation

**Recommendation: READY FOR IMPLEMENTATION** for the lifecycle-gate/trajectory piece; propagation chain explicitly deferred, not part of this recommendation.

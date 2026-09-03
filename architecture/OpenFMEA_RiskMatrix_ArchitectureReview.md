# Open-FMEA Architecture Review — Risk Matrix

Status: architecture review — grounded in code already implemented and verified in Phase B, not a new capability, not implementation authorization by itself. Written per the user's own stated house rule: every missing GUI section needs a review before it can be built.

Author: Claude, acting as Open-FMEA Technical Architect.

## 1. Why this is the cheapest of the missing mockup sections to build

Unlike Validation Trajectory, CAPA, Control Plans, or the PM-FMEA/Asset track, a Risk Matrix needs **no new domain entity**. I read the actual code before writing this: `RiskRating` (severity/occurrence/detection, each validated to an integer 1–10 — `fmea_domain/rules.py::validate_rating`), `RiskEvaluation` (references a `FailureMode`, an `EvaluationDefinition`, carries `inputs: RiskRating`, a `result` dict, `evaluated_at`, `actor`, `trigger`), and `EvaluationDefinition` all already exist as real, persisted Django models (`fmea_app/models.py` lines 579 and 739) from Phase B — not proposed, not partially built, fully there. `fmea_evaluation/calculators.py` already computes both `classic-rpn` (severity × occurrence × detection, banded low/medium/high at 80/200) and an AIAG-VDA AP-style band. The demo seed data already creates `RiskEvaluation` rows and a `FailureMode` detail page already has a `RiskEvaluationForm` for entering new ratings. I confirmed live in the current database: 2 `RiskEvaluation` rows exist against 1 `FailureMode`.

A Risk Matrix is therefore an aggregation query over data that's already being captured, plus a rendered grid — not a new capability. This is why it was the right first pick.

## 2. What the reference mockup showed, and where it doesn't match the real data

The mockup showed a 5×5 grid (Severity 1–5 across the top, Occurrence 1–5 up the side), each cell colored/counted, with a legend "Low (1-2) / Medium (3-6) / High (7-12) / Very High (13-25)" — i.e., banded by the severity×occurrence product on a 1–5 scale, and captioned "Risk Overview (All Projects)."

Two things don't match what's actually in the domain model:

- **Scale.** `validate_rating` enforces 1–10 for severity/occurrence/detection, matching standard AIAG practice — not 1–5. A matrix built to the mockup's 1–5 axes would either reject valid data or need to bucket real 1–10 ratings down to 1–5 bands, adding a translation step that doesn't exist anywhere in the domain model today. Recommend building the matrix as the real 10×10 grid (or a collapsed band-based summary — see Decision 2) rather than reproducing the mockup's 1–5 axes verbatim.
- **"All Projects."** There is no `Project` entity anywhere in the domain model — only individual `FMEA` objects, each with their own `FailureMode`s. "Risk Overview (All Projects)" in the mockup implies a multi-project rollup that doesn't exist. The honest equivalent today is "Risk Overview (All FMEAs)" — every `FailureMode` across every `FMEA` in the system, not scoped to a project concept that isn't built.

## 3. Proposed design

**Data source:** for each `FailureMode`, its **most recent `RiskEvaluation`** by `evaluated_at` (a `FailureMode` can accumulate a history of evaluations across different triggers/actors/methods — Section 4 of this review covers what happens when more than one method's evaluation exists for the same `FailureMode`). No new field, no new query complexity beyond `order_by("-evaluated_at").first()` per `FailureMode`, or a single `annotate`/window-function equivalent for the whole set — either is a simple query, not new aggregation logic in the sense the GUI-shell instruction's Section 3 constraint was written to exclude.

**Grid:** Severity (1–10) × Occurrence (1–10), each cell showing a count of `FailureMode`s whose most-recent evaluation has that exact (severity, occurrence) pair, colored by a band. Detection is not an axis (matches the mockup, which is a two-axis grid) but is not discarded either — it still contributes to a `FailureMode`'s computed RPN/AP band, shown when you drill into a cell (Section 3, "Drill-down," below).

**Banding:** reuse `fmea_evaluation.calculators.classify_rpn`'s existing thresholds is tempting but wrong here — that function bands the full three-factor RPN (severity × occurrence × detection), not the two-factor severity × occurrence product this grid uses. Recommend a **new, explicitly two-factor banding function** for this view only (`classify_severity_occurrence` or similar, in `fmea_evaluation/calculators.py` alongside the existing ones, not replacing them): thresholds are a genuine open decision (Section 5, Decision 2) — I'm proposing severity×occurrence ≤ 8 = Low, 9–24 = Medium, 25–48 = High, 49–100 = Very High as a starting point (roughly evenly spaced on a log scale across the 1–100 product range), but this is a judgment call, not derived from anything already in the codebase, and should be confirmed rather than assumed.

**Drill-down:** clicking a populated cell shows the list of `FailureMode`s in it (name, parent `FMEA`, the actual computed RPN/AP band from their evaluation's `result` dict) — this reuses the existing `FailureMode`/`RiskEvaluation` data directly, no new query shape beyond "filter by severity and occurrence instead of by ID."

**"Top High Risk Items"** (a separate mockup widget, naturally paired with the matrix): the same underlying query, sorted by computed RPN descending, top N rows — cheap to add alongside the matrix since it's the identical data reshaped, not a second aggregation to design.

## 4. What happens when a `FailureMode` has evaluations from more than one method

The demo seed creates both a `classic-rpn` and an `aiag-vda-ap-poc` `EvaluationDefinition`, and a `FailureMode` could plausibly be evaluated under both. "Most recent by `evaluated_at`" (Section 3) resolves this simply — whichever was entered last wins for matrix placement — but this means the matrix's severity/occurrence axis values, and the RPN/AP band shown on drill-down, can shift depending only on which method was used most recently, not on any change to the actual risk. This is a real property of the design worth stating plainly rather than discovering later: this matrix shows "current best-known rating," not "the classic-RPN view specifically." If the user wants a method-specific matrix instead (e.g., "show me the classic-RPN matrix regardless of whether a newer AP-only evaluation exists"), that's a different, filterable design — flagged as Decision 3 below.

## 5. Decisions Requiring Approval

1. **Scope: system-wide ("All FMEAs"), not per-project** — there is no `Project` entity to scope by. Confirm this is acceptable for a first increment, or say if per-FMEA scoping (a matrix per `FMEA` rather than one global matrix) is actually what's wanted instead.
2. **Banding thresholds for the two-factor severity×occurrence grid** — my proposal (≤8 Low, 9–24 Medium, 25–48 High, 49–100 Very High) is a placeholder judgment call, not derived from any existing standard already in this codebase. Confirm, adjust, or say if a different scheme (e.g., matching a specific AIAG-VDA severity/occurrence-only matrix) should be used instead.
3. **"Most recent evaluation wins" vs. method-specific views** — confirm the Section 4 behavior is acceptable, or specify that the matrix should be filterable/scoped to one evaluation method.
4. **10×10 grid vs. a collapsed summary** — a full 10×10 grid is more cells than the mockup's 5×5 and may be visually dense with a small number of real `FailureMode`s (today: 1). Confirm whether to build the full 10×10 grid now, or a coarser band-only summary (e.g., a 4×4 grid of the bands themselves) as a first increment, with the full 10×10 as a possible later refinement.

## 6. What this review does not propose

No new entity, no new migration, no change to `RiskEvaluation`/`RiskRating`/`EvaluationDefinition`, no change to the existing `classify_rpn`/`calculate_action_priority` functions (a new banding function is additive, per Section 3). No per-project scoping mechanism (Decision 1 exists because that would require inventing one). No chart/canvas library — the grid is plain HTML table cells with CSS background colors, matching the GUI-shell slice's existing "no new charting library" constraint exactly; this was true for the Ishikawa status breakdown already built and stays true here.

## Recommendation

**READY WITH CONDITIONS** — same status language as the Characteristics/Ishikawa review, for the same reason: the underlying data model is completely sound and already built, but Section 5's four decisions are genuine judgment calls I made defaults for, not facts I verified, and should be confirmed before a Codex instruction is written.

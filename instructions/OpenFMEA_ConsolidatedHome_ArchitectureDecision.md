# Open-FMEA Architecture Decision — Consolidated Home (Mockup 4)

Status: **Decided, 2026-09-05**, per explicit user direction. Mockup 4 is the "final vision" home dashboard — the ceiling of everything mockups 1-3 and 5+ eventually compose into on one page. Per `OpenFMEA_MockupGUICodingRequirements.md`, there is no separate "consolidated home" route: this is the existing `fmea:dashboard`/`dashboard.html`, built incrementally, not a new page. This document proposes a firm, narrow slice of that ceiling to build now, using only real, already-existing data plus the just-decided Chart.js library, and firmly excludes everything else.

## 1. What this mockup shows, and the tiering already on record

Per the existing project catalog (`OpenFMEA_MockupGUICodingRequirements.md`, `OpenFMEA_MockupSpecifications_GUIWireframeArchitecture.md`), Mockup 4 combines: stat cards, a Risk Overview matrix (already built elsewhere, `fmea:risk_matrix`), a Validation Trajectory panel, an Engineering Context panel, a PM-FMEA maintenance-risk donut, a new "Operations & Maintenance Status" module, and a "Project Health (Summary)" band (health gauge, 30-day risk trend line chart, Actions mini-panel, Coverage bars, Links/Data-Integrity mini-panel, Next Reviews).

This decision does not re-litigate that catalog. It picks out the pieces that are genuinely derivable from real, already-existing data without inventing new aggregation logic, and builds only those.

## 2. Decision — build now

1. **Stat cards**: extend the existing KPI row on `dashboard.html` with cards for FMEA count (already real — `fmea_count` is already computed and rendered), Project count (`FMEAProject.objects.count()`, already queried in the view but not yet surfaced as its own stat tile — check before adding a duplicate), Failure-Mode count (`FailureMode.objects.count()`), and Action count (`RecommendedAction.objects.count()`). **Extend the existing stat-tile row — do not replace or restyle what's already there** (the "FMEA Projects" and "Pending Review" tiles already on `dashboard.html` stay as-is; new tiles are added alongside them).
2. **Actions summary**: a small panel or stat-tile group — Total, Overdue, Due Soon — computed from real `RecommendedAction.status` and `.due_date`:
   - Total: `RecommendedAction.objects.count()`.
   - Overdue: `due_date < today` and `status` not in a terminal state (`completed`, `verified`, `cancelled` per the real `ActionStatus` enum).
   - Due Soon: `due_date` between today and today+7 (proposed 7-day window, matching the "Reviews Due... Next within 7 days" convention already used elsewhere on this page) and `status` not terminal.
   No new model — a plain queryset computed at render time in the `dashboard` view.
3. **One risk-trend chart**: a simple 30-day trend of `RiskEvaluation` row counts, via Chart.js (line or bar — bar is simpler and equally honest for a daily-count series; recommend bar), first real usage of the just-vendored library. Query: group real `RiskEvaluation.evaluated_at` timestamps by day (or by week if daily granularity is too sparse in the demo dataset — implementer's call, state which was chosen) over the trailing 30 days, count per bucket. This is a real, cheap aggregate over an existing indexed timestamp field — not a "risk-tier-as-of-date-X" replay (that is the much harder query the mockup's actual "Risk Trend" line implies, per Section 3 below) and not a stored snapshot entity. It is deliberately a simpler, honest substitute: "how many risk evaluations were recorded per day," not "how many failure modes are currently in each risk tier, plotted historically."

## 3. Explicitly, firmly excluded

- **The entire "Operations" module** (Process Planning / Production Execution / Work Tracking / Traceability, and the mockup's "Operations & Maintenance Status" card with Production/Maintenance mini-cards). No entity backs any of this. This is **out of scope entirely, not deferred-for-now** — it belongs to a separate Open-EQMS module this app does not own (per `OpenFMEA_MockupGUICodingRequirements.md`'s own note that these are external deep-links, not local routes). It does not get a placeholder card, a "coming soon" tile, or a nav stub in this slice.
- **The "PM-FMEA maintenance-risk donut."** Tied to the standing PM-FMEA hold recorded elsewhere in this project (no `pm_fmea`/"preventive" `fmea_type` value has been approved). Stays excluded until that hold is lifted — not part of this or any near-term slice.
- **A computed "Overall Health" score/gauge.** No formula for this exists anywhere in the grounding, and none is proposed here. It is not derivable without inventing scoring logic (what inputs, what weights) — that is a real, separate architecture decision, not an implementation detail. Flagged as needing its own future decision if ever pursued; this document deliberately does not attempt it.
- **Per-FMEA-type coverage bars** (DFMEA/PFMEA/PM-FMEA validation coverage, the "Coverage" mini-panel). The underlying question — what formula defines "coverage" for a given FMEA — is not settled anywhere in the grounding (`OpenFMEA_MockupGUICodingRequirements.md` calls the DFMEA/PFMEA bars "approximable, formula not established"). Building a placeholder or a guessed formula would misrepresent real progress. Explicitly deferred pending its own aggregation-logic decision.
- **Data-integrity / broken-link counts** (the "Links (Data Integrity)" mini-panel — Linked Items %, Unlinked Items, Broken Links). "Unlinked" and "Broken" have no defined rule anywhere in this project (what counts as an orphaned or dangling reference is undecided). This needs new aggregation logic this document does not attempt to design. Explicitly deferred.
- Everything else Mockup 4 shows that duplicates already-cataloged Tier-D/placeholder items elsewhere (Next Reviews mini-panel, Engineering Context Summary card's Machines/Assets and Control Plans tiles, Risk Overview matrix as an embedded card — the last of these already exists as its own full page at `fmea:risk_matrix` and is out of scope for re-embedding here in this slice).

## 4. Scope of the paired implementation slice

Extend the existing `dashboard` view and `dashboard.html` template only:

1. Add the four stat-tile additions (Section 2.1) to the existing KPI row, reusing `_stat_tile.html`.
2. Add the Actions summary (Total/Overdue/Due Soon) as a new small panel or stat-tile group on the same page.
3. Add one Chart.js bar or line chart (30-day `RiskEvaluation` count trend) as a new `<canvas>` in a new or existing panel on the same page, following the vendoring/`json_script` pattern already fixed by `OpenFMEA_ChartingLibrary_ArchitectureDecision.md`.

**No new routes.** This is entirely additive to the existing `fmea:dashboard` route — no `fmea:consolidated_home` or similar is created, matching the standing note that Mockup 4 is the ceiling of the one real Home page, not a separate page.

## 5. Recommendation

**Recommendation: READY FOR IMPLEMENTATION for the real-data pieces listed.** Operations module and health-score scoring are explicitly NOT part of this recommendation and need their own separate reviews if ever pursued.

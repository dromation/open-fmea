# Open-FMEA Architecture Review — System Hierarchy

Status: **Open for user decision, 2026-09-04.** Written per explicit user direction ("write the review now"). This is a review, not an implementation instruction — nothing here is built or approved for building until the open decisions below are answered, per DNA rule 8. It exists so Mockups 7 (System/Product/Process), 8 (System Characteristics Base), 9 (Characteristics Flow), and DFMEA/PFMEA's "Structure Tree" tab (Mockup 11/12) can eventually get real, narrow instructions instead of staying permanently "cataloged only."

Grounded directly in the real code before writing this: `Product`/`Process`/`Operation`/`FMEA` in `models.py` (all read in full this engagement), confirming **no `System` class exists anywhere today** — only flat `Product`/`Process`/`Operation`, each scoped to one `FMEA` via a direct FK, with no hierarchy above them.

## 1. What the mockups actually show

- **Mockup 7 (System / Product / Process):** a "Systems" tab/tree alongside Product and Process, implying System sits as a peer-or-parent context alongside the two real entities, not a replacement for either.
- **Mockup 8 (System Characteristics Base):** characteristics grouped "by System/Subsystem" — implying at least two levels (System, Subsystem) with characteristics attached somewhere in that tree, plus a "Linked to FMEA" count per characteristic and an "Organizations" stat card (separate, unaddressed multi-tenancy question — explicitly out of scope for this review, see Section 5).
- **Mockup 11/12 (DFMEA/PFMEA "Structure Tree" tab):** an element/part hierarchy for a specific FMEA — this may or may not be the same tree as Mockup 7/8's System hierarchy; see Decision 3.

## 2. What exists today (confirmed from source)

- `Product` — `fmea` FK (`related_name="products"`), `name`, `description`, `part_number`. No parent/child, no System link.
- `Process` — `fmea` FK (`related_name="processes"`), `name`, `description`, `process_code`. No parent/child, no System link.
- `Operation` — `process` FK (`related_name="operations"`), `name`, `description`, `sequence`. No System link.
- `FMEA.fmea_type` already includes a `"system"` choice (alongside `design`/`process`/`product`/`software`) — so an FMEA can already be *labeled* "System" today, but there is nothing structural backing that label; it's just a string choice on the type field, same as every other value.

## 3. Decisions needed (proposed answers below, for confirmation or correction — not assumed)

**Decision 1 — Is `System` a container above `Product`/`Process`, or a peer to them?**
Proposed: a **container**. A `System` (optionally nested — see Decision 2) groups zero or more `Product`s and zero or more `Process`es. This matches Mockup 7's "System / Product / Process" tab grouping and Mockup 8's "grouped by System/Subsystem" characteristics view. Concretely: add a nullable `system` FK to both `Product` and `Process` (nullable so existing data keeps working with no backfill required — see Decision 5).

**Decision 2 — Hierarchy shape: self-referential (arbitrary depth) or fixed two-level (System → Subsystem)?**
Proposed: **self-referential**, one model (`System`) with a nullable `parent` FK to itself. Mockup 8 only ever shows two levels in its screenshots, but a fixed two-level model is a narrower, more brittle design than a self-referential one for roughly the same implementation cost, and automotive/industrial system breakdowns commonly go deeper than two levels in practice. A "Subsystem" is then simply a `System` row whose `parent` is set, not a separate model.

**Decision 3 — Is DFMEA/PFMEA's "Structure Tree" (Mockup 11/12) the same tree as this `System` hierarchy, or a separate concept?**
Proposed: **the same tree**. Mockup 11/12's Structure Tree is described as an "element/part hierarchy" — functionally identical to what Mockup 7/8 call `System`/Subsystem. Treating them as one entity avoids building two parallel hierarchy models for the same real-world concept. If the user has a specific reason they should be separate (e.g. a Structure Tree scoped per-FMEA vs. a System hierarchy shared across FMEAs), flag it — this is a judgment call, not a certainty.

**Decision 4 — What fields does `System` itself carry?**
Proposed, minimal, matching what the mockups actually show (not inventing beyond it): `name`, `description`, `code` (short identifier, same pattern as `Process.process_code`/`FMEAProject.project_code`), `parent` (nullable FK to self), `status` (a simple operational-status field — Mockup 7 shows a status per system row, but doesn't define its value set; proposed: reuse the existing pattern of a small closed choice list, e.g. `active`/`inactive`, pending the user confirming the real value set needed). **Explicitly not included:** Type/Category/Importance/Monitoring-status columns from Mockup 8 — those are the `ClassificationScheme`/`ClassificationTerm` concept, still not approved, and stay out of this review entirely (see Section 5).

**Decision 5 — Backfill: do existing `Product`/`Process` rows need a `System` assigned, or does the field stay optional indefinitely?**
Proposed: **stays optional (nullable) indefinitely.** No forced migration/backfill of existing data. A `Product`/`Process` with no `System` renders exactly as it does today (Engineering Context, `fmea_detail.html`, Process Flow — none of them would need to change for existing data). `System` becomes an optional additional grouping layer, not a mandatory one — consistent with how every other optional relationship in this codebase already works (e.g. `FailureMode.requirement` is nullable).

**Decision 6 — Does an FMEA link to a `System` directly, in addition to via its Products/Processes?**
Proposed: **no direct FK from `FMEA` to `System`** in this first pass. An FMEA already reaches Products/Processes (which would carry the System link per Decision 1), and `FMEA.fmea_type == "system"` already exists as a label independent of this. Adding a direct `FMEA.system` FK on top would be a second, possibly-inconsistent path to the same information — better to defer that until a real need for it shows up (e.g. an FMEA that has a System context but zero Products/Processes yet), rather than build it speculatively now.

## 4. What this review would unblock, once decided and a follow-up instruction is written

Per `OpenFMEA_DNA_CoreReference.md`'s 2026-09-04 status-check table: System Characteristics (Mockup 8) and Characteristics Flow (Mockup 9) both list a `System` hierarchy as one of their blockers; DFMEA/PFMEA's Structure Tree tab does too. This review, once its decisions are confirmed, clears that specific blocker for each. It does **not** by itself unblock:
- **System Characteristics (Mockup 8)** still separately needs `ClassificationScheme`/`ClassificationTerm` (not approved) and the undesigned "Organizations"/multi-tenancy concept (Section 5) before it has a real instruction.
- **Characteristics Flow (Mockup 9)** still separately needs a new relationship/edge entity, a graph-rendering library (a different decision than the Chart.js decision — see `OpenFMEA_ChartingLibrary_ArchitectureDecision.md` Section 4), and an unspecced AI "Auto Link" capability.
- Each of those stays its own gated item — this review only removes the `System`-hierarchy piece of their blocker list, per rule 8's narrow-scope discipline.

Once decided, a narrow first implementation slice (a `System` model + migration + a simple browse/create page, no Characteristics/Flow/Classification content) could follow the same pattern as Engineering Context and Slice D — real data, no speculative features.

## 5. Explicitly out of scope for this review

- `ClassificationScheme`/`ClassificationTerm` (Type/Category/Importance) — still not approved, untouched here.
- The "Organizations" multi-tenancy concept from Mockup 8 — no tenancy/organization model exists anywhere in this codebase; this is a materially different, larger question (would it scope every entity in the app, or just Systems?) that deserves its own review if it's ever pursued, not a side effect of this one.
- Characteristics Flow's relationship/edge entity, graph library, and AI auto-link — Mockup 9's own separate blockers, unaffected by this review.
- Process Control Characteristics / Control Plan (Mockup 21) — gated by DNA rule 7, unrelated to System hierarchy.

# Open-FMEA Architecture Decision — Characteristics Flow / Diagram (Mockup 9)

Status: **Proposed, 2026-09-05** — decision on manual linking only, pending user approval. This is a policy/scope decision, not an implementation instruction; `Codex_Instruction_CharacteristicsFlow_SliceL.md` is the corresponding narrow instruction, written to match this document exactly and gated on the same approval.

## 0. Why this needs a split before anything else

Mockup 9 is the single largest concentration of net-new, higher-risk capability across all 23 mockups: a genuinely new relationship/edge entity (no `CharacteristicLink`-equivalent exists anywhere today), a force-directed graph-rendering library the project has not adopted (`OpenFMEA_ChartingLibrary_ArchitectureDecision.md` Section 4 explicitly excludes it — "not a standard Chart.js chart type" — and states this mockup needs "its own small follow-up decision... not assumed here"), a four-tab surface (Link Matrix / Link Network / Link Rules / Impact Paths), and an AI-assisted "Auto Link" capability with a "Smart (Rules + AI)" mode, confidence-percentage scoring, and a proposed-relationship review queue. Approving all of that in one pass would violate this project's own discipline of narrow, single-decision slices (`OpenFMEA_DNA_CoreReference.md` rule 8: "the approved scope is the narrowest one stated, not the full ambition of the review") and would put an AI system in a position to write suggestions directly into FMEA quality data — the exact thing rule 3 ("AI is never authoritative") and rule 4 ("human review gate, always") exist to prevent from happening carelessly.

This document follows the same split-and-defer pattern already used for DFMEA/PFMEA (`Codex_Instruction_DFMEA_PFMEA_Worksheets_SliceD.md`, which built the worksheet table and explicitly deferred Structure Tree, Interface Matrix, Parameter Diagram, RPN/donut charts, and Control Plan Link as separate future decisions): take the ordinary, low-risk, clearly-real part of the mockup and approve it now; name the ambitious parts explicitly and defer each one as its own future decision, not as an implicit "later" that quietly expands this slice.

## 1. Decision — new entity: `CharacteristicLink`

Approve a new model, `CharacteristicLink`, with:

- `from_characteristic` — FK to `ProductCharacteristic`.
- `to_characteristic` — FK to `ProductCharacteristic`.
- `relationship_type` — closed Python enum: `Drives` / `Influences` / `Affected By` / `Constrained By` / `Supports` / `Required By`.
- `strength` — closed Python enum: `Critical` / `High` / `Medium` / `Low` / `None`.
- `created_at`, `created_by`.

**Both ends point at `ProductCharacteristic` only, for this first increment.** The mockup's own visual language implies characteristics could eventually link across product/process/system boundaries, but no System-level characteristic entity exists yet (Mockup 8, "System Characteristics Base," is itself unbuilt), and a polymorphic from/to link is real added complexity (generic FK or a source/target-type-tagged pair, mirroring the pattern `CauseInfluence` already uses) that has no concrete second case to justify it today. Widening `CharacteristicLink` to a polymorphic link is a plausible, cheap future extension — same shape of decision `CauseInfluence`'s source/target types already went through once (`Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md` widened `CauseInfluence` to add `ProcessCharacteristic`/`ProductCharacteristic` after the fact) — but it is not decided here and should not be built ahead of a concrete need.

**`relationship_type` is a plain Python enum, not a scheme+seeded-rows model.** Per `OpenFMEA_DNA_CoreReference.md` rule 6, a Python enum is appropriate for "a closed, structural vocabulary that isn't organization-configurable" — the six relationship types shown in the mockup (Drives/Influences/Affected By/Constrained By/Supports/Required By) read as a fixed structural vocabulary describing how one characteristic relates to another, not a domain taxonomy an organization would redefine (contrast with the 5M+E cause-category scheme, which genuinely varies by organization and is correctly a `CauseCategoryScheme`/`CauseCategory` model). If a future need to add organization-specific relationship types emerges, that is a separate decision to revisit this choice — not assumed here.

**`strength` lives on the link, not on `ProductCharacteristic`.** The mockup's language ("Critical"/"High"/"Medium"/"Low") echoes the not-yet-approved Importance classification column flagged elsewhere for `ProductCharacteristic` (`OpenFMEA_MockupSpecifications_GUIWireframeArchitecture.md`'s audit of Mockup 8: Importance is explicitly unapproved `ClassificationScheme`/`ClassificationTerm` territory). This decision does not touch that question at all — `strength` is a property of one specific link between two characteristics ("how strongly does A drive B"), a narrower and different claim than "how important is this characteristic in general." Building `CharacteristicLink.strength` creates no dependency on, and does not pre-empt, whatever the future Importance/Classification decision turns out to be.

**`created_by` is free text, matching `RiskEvaluation.actor`.** No real per-user account/role system exists in this app today (confirmed absent elsewhere in this project's audits); `created_by` is a plain `CharField`, not a FK to `settings.AUTH_USER_MODEL`, following the same precedent `RiskEvaluation.actor` already established rather than inventing a different pattern for this one model.

## 2. Explicitly, firmly deferred — NOT decided or approved by this document

The following are named here specifically so they cannot be silently folded into the implementation instruction as "since we're building the model anyway." None of them is approved, scoped, or designed by this document:

**(a) Any AI-assisted "Auto Link" / confidence-scoring capability.** No prompt design, no `AiProvider` task, no confidence-threshold policy, no "Smart (Rules + AI)" mode, no review queue for AI-proposed links — nothing. If this is picked up later it needs its own dedicated architecture review addressing, at minimum: how a proposed link is represented before a human accepts it (per DNA rule 4, "human review gate, always" — an AI-proposed `CharacteristicLink` must not become a real, effective link without an explicit human Accept, exactly like `ImportCandidateRecord`/`FmeaRowGroup` and the planned `CauseInfluence` status transitions already work); what "confidence" means and how it's computed (per DNA rule 3, never documented or treated as a probability); and what "Rules" contributes independently of "AI" in the "Smart (Rules + AI)" mode, since no rules engine of any kind exists in this codebase today.

**(b) Any force-directed graph rendering or graph-layout library.** `OpenFMEA_ChartingLibrary_ArchitectureDecision.md` already adopted Chart.js for line/bar/donut charts and explicitly excluded this exact mockup's graph as out of scope, requiring "its own small follow-up decision (a Chart.js plugin, or a separate lightweight graph-layout library)." This document does not make that follow-up decision. No graph-rendering dependency is approved here.

**(c) The "Link Matrix," "Link Rules," and "Impact Paths" tabs.** "Link Network" (the force-directed graph) is covered by (b) above. "Link Matrix" (a full characteristic-by-characteristic grid view), "Link Rules" (a rules-editor for what relationships are permitted/expected), and "Impact Paths" (multi-hop critical-path analysis across the link graph) are each their own, separate GUI/logic surface with no design decided here. All three are deferred, not part of this increment.

**(d) Any orphan-detection, validation, or "Warnings" logic.** The mockup implies flagging characteristics with no links, or links that look structurally inconsistent. No such validation, query, or warning-surfacing logic is designed or approved here.

## 3. Scope for the first increment

Model + migration for `CharacteristicLink` as decided in Section 1, plus:

- A list page showing all `CharacteristicLink` rows — columns: from-characteristic name, to-characteristic name, relationship type, strength — with standard server-side GET-form filters (by relationship type, by characteristic, matching this app's existing filter idiom — no AJAX).
- A create form: pick from-characteristic, to-characteristic, relationship type, strength. Manual only, one link at a time. No bulk create, no import path.
- A delete action for a single link.

No visualization beyond a plain table. **The "graph" for this increment is a filterable list, nothing more** — this is the deliberate substitution for the mockup's Link Network tab, not a lightweight version of it.

## 4. What this unblocks, and what it does not

This closes the "genuinely new relationship/edge entity" gap identified for Mockup 9 and gives users a real, usable way to record that one characteristic drives, influences, is affected by, is constrained by, supports, or is required by another — something no part of the current app can express today. It does **not** unblock the mockup's visualization (still blocked on a graph-library decision per Section 2(b)) or its AI auto-link feature (still blocked on its own dedicated review per Section 2(a)); those remain exactly as unbuilt and undecided after this document as before it.

## 5. Recommendation

**Recommendation: READY FOR IMPLEMENTATION for manual linking only.** AI auto-link and graph visualization are explicitly NOT recommended for approval in this pass — they need their own dedicated review (prompt design/confidence thresholds/human-review-gate for AI; a specific graph-rendering library choice for visualization) before any instruction is written for them.

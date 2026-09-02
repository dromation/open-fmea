# Open-FMEA Architecture Review — Product/Process Characteristics × Ishikawa 5M+E Cause Model

Status: Draft for Project Manager review — domain design proposal, not an ADR, not implementation authorization

Author: Claude, acting as Open-FMEA Technical Architect

Date: 2026-08-30

Authority: subordinate to `architecture/OpenFMEA_Architecture_and_Portability_Report.md`, `architecture/adr/ADR-0000-adopt-django-poc-and-freeze-legacy.md`, and — one level further up — `Open-EQMS_Architecture_Baseline_v1.0.md` and `PRS-000-master-product-vision.md`. This report proposes an extension to the Open-FMEA domain model; it does not authorize implementation.

This is the required first output per the governing brief's Section 30: an architecture review, grounded in the domain model as it actually exists on `codex/phase-b-django-poc` today (verified directly, not assumed — see Section 1), before any code changes are made.

---

## 1. Proposed Characteristic Domain Model

The core distinction the brief draws — product/system side (`Requirement → Product Characteristic → Failure Mode → Failure Effect`) versus cause/process side (`5M+E Category → Process Characteristic → Potential Cause → Cause Mechanism → Failure Mode`) — maps cleanly onto the domain model already implemented, with one important continuity point: the existing `Characteristic` entity (`domain/fmea_domain/entities.py`) is already the seed of "Product Characteristic." It currently carries `requirement_id`, `is_special`, `name`, `description` — exactly the product-side anchor this brief wants formalized. Nothing about the existing model conflicts with this proposal; it needs extending, not replacing.

Two new first-class concepts are needed that do not exist today: a **Process Characteristic** (cause-side, currently absent entirely) and a set of **configurable classification/taxonomy objects** (classification domains, 5M+E categories, special-characteristic schemes) that the brief explicitly requires be non-hardcoded.

The taxonomy objects follow a pattern the domain model has already validated once: `EvaluationDefinition` already proved that "a configurable method, referenced by id, not hardcoded" works cleanly in this codebase (Section 10 of the architecture report; implemented and reviewed in Phase B). The same pattern — a small library entity plus references to it — is proposed for every classification scheme this brief asks for, rather than inventing a new mechanism per taxonomy.

## 2. Product Characteristic Hierarchy

Proposed: a `ClassificationScheme` (e.g. `"product-characteristic-domain-v1"`) containing `ClassificationTerm` entries, each with an optional `parent_term_id` for hierarchy. The initial seed library populates exactly the tree the brief specifies:

```text
Legal
Safety
Functional
  Mechanical
  Optical
  Electrical
  Software
Decorative / Aesthetic
```

Future terms (Thermal, Chemical, Acoustic, Biological, Hydraulic, Pneumatic, Electromagnetic, Dimensional, Ergonomic, Environmental, Reliability) are added as new `ClassificationTerm` rows under this same scheme — no schema change, matching the brief's non-closed-list requirement directly.

`ProductCharacteristic` (the proposed rename/extension of today's `Characteristic` — see Section 16's naming decision) carries `primary_classification_id` (single, required) and `secondary_classification_ids` (a tuple, optional) — both references into `ClassificationTerm`, satisfying Section 3's multi-classification requirement (the emergency-stop-button-colour example: primary Safety, secondary Legal/Functional/Decorative) without forcing a single mutually-exclusive category.

Legal/Safety classification is explicitly **not** wired to Severity. Per Section 4, classification instead becomes an input to coverage-metric queries (Section 12 below) and to future rule-based checks ("every Safety-classified characteristic must have FMEA coverage") — those checks live in `fmea_domain/rules.py`, not on the entity itself, and Severity remains sourced only from the linked `FailureEffect`, exactly as the brief requires and as the existing `RiskEvaluation`/`RiskRating` model already enforces (Severity is an input captured against a specific `FailureMode` evaluation, never derived from a characteristic's classification).

## 3. Process Characteristic Model

`ProcessCharacteristic` is proposed as one entity type — not ten hardcoded subtypes for Man/Machine/Material/Method/Measurement/Environment. The brief's own field lists (spindle runout, chemical composition, cutting speed, calibration status, competency, temperature) are examples of *values*, not different schemas: each is a name, a nominal/observed/limit/state shape (mirroring `ProductCharacteristic`'s own nominal/limits/tolerance shape for symmetry), and a `cause_category_id` reference into the 5M+E scheme (Section 4 below). Domain-specific detail lives in a typed-but-open `attributes` bag, the same pattern `EvaluationDefinition.configuration`/`rating_scales` already uses, and the same philosophy Baseline Section 5 already establishes for the Object Runtime generally ("business semantics come entirely from configuration... not schema migrations").

`ProcessCharacteristic` links to a `Process`/`Operation` (both already exist in the domain model) and, via the influence-relationship model in Section 5, to one or more `ProductCharacteristic` entries it may affect — never a single hardcoded FK, since one process characteristic (e.g. polymer moisture) can legitimately influence several product-characteristic domains at once (the brief's own Optical/Mechanical/Decorative example).

**Scope note for the first increment:** this proposal models `ProcessCharacteristic` as instance-level data tied to one `Operation` — a real, observed thing at one point in one process — not yet a reusable library item. The architecture report already scoped a future "Controlled FMEA Libraries" capability (standard process steps, measurement methods, reusable characteristics); library-izing `ProcessCharacteristic` belongs there, not in this increment, to avoid scope creep ahead of that already-planned work.

## 4. Ishikawa Taxonomy Model

Proposed: `CauseCategoryScheme` (e.g. `"ishikawa-5m-e-v1"`) containing `CauseCategory` entries — Man, Machine, Material, Method, Measurement, Environment — as the seeded default, again following the `ClassificationScheme`/`EvaluationDefinition` configurability pattern. An organization can define a different scheme (4M, 6M+1E, a custom taxonomy) and point `ProcessCharacteristic.cause_category_id` at it instead, satisfying Section 6 and Section 29's non-hardcoding requirement identically to how classification domains are handled.

Man-category characteristics are explicitly scoped to **observable organizational evidence only** — required/verified competency, certification, training revision, authorization, staffing, shift, instruction acknowledgement — per Section 8's caution. No field for subjective mental-state scoring or health data is proposed, and none should be added later without a specific, separately justified decision; this is a hard boundary worth stating plainly in the domain model's own documentation, not just in this review.

## 5. Cause / Effect Relationship Model

This is the section that most needs a real design decision rather than a restatement of the brief, because the existing domain model already has a generic `Relationship` entity (`source_id`, `target_id`, `relationship_type`, `provenance: dict`) and the question is whether cause/effect influence links reuse it or need their own type.

**Recommendation: a new, dedicated `CauseInfluence` entity, not the generic `Relationship`.** The generic `Relationship` was designed for structural containment/reference links (`fmea_contains_failure_mode`, `product_has_function`, etc.) where a free-form `provenance` dict is enough. Section 16 requires a relationship that carries *first-class, individually meaningful* fields — influence type, direction, strength, confidence, evidence, source, status — that need to be queryable and validated on their own terms (e.g., "show me every `Deny`... no, wrong domain — show me every influence with `status = suspected` and `confidence < 0.5`"), not buried inside an untyped dict. Overloading the generic `Relationship` for this would either force weakly-typed access to important fields or duplicate half of `Relationship`'s own shape inside `provenance`. A dedicated entity is more consistent with how `RiskEvaluation` was already kept distinct from the generic `Relationship` for the same reason.

Proposed `CauseInfluence` fields: `source_id` (a `ProcessCharacteristic`, `CauseMechanism`, or another `CauseInfluence`'s target — chains compose), `target_id` (a `ProductCharacteristic`, `FailureMode`, or `FailureCause`), `influence_type` (free-text/enum-extensible, e.g. `"influences"`, `"deviation"`, `"produces"`), `direction`, `strength` (optional, numeric or qualitative), `status` (**required**, one of `suspected | possible | correlated | experimentally_supported | confirmed_root_cause | rejected` — Section 14's exact list), `confidence`, `evidence_ids` (references to `Evidence`), `source_context` (which investigation produced this — FMEA / 8D / CAPA / complaint — a plain string/reference, not a new entity), `revision`.

This single entity type satisfies both diagrams in Section 1 (`Process Characteristic → influences → Product Characteristic → deviation → Failure Mode → produces → Failure Effect`, and `Process Characteristic → Potential Cause → Cause Mechanism → Failure Mode`) as chained `CauseInfluence` edges between whatever entities sit at each step — it does not need to know in advance which entity types it connects, only that both ends carry a `stable_id`.

**"Potential Cause" versus the existing `FailureCause`:** the brief's Section 21 diagram (`candidate causes → confirmation/rejection → Root Cause`, "confirmed root causes should be reusable by FMEA") indicates a candidate cause discovered during investigation is *not* automatically an FMEA `FailureCause` entry. Recommended resolution: do not introduce a separate `PotentialCause` entity. Instead, a candidate cause during investigation is represented as a `CauseInfluence` targeting a `FailureMode` directly (no `FailureCause` yet exists), carrying `status = suspected/possible/...`. Only when a cause is confirmed does it get promoted into a proper `FailureCause` record (existing entity, unchanged shape), and the `CauseInfluence` is updated to target that `FailureCause` with `status = confirmed_root_cause`. Rejected candidates keep their `CauseInfluence` record with `status = rejected` — visible as investigation history, never presented as an FMEA cause. This is a genuine design decision, flagged explicitly in Section 16 below for approval, with this as the recommended default.

`FailureMechanism` (already in the domain model) is the direct equivalent of the brief's "Cause Mechanism" — no new entity needed, only a note that the terminology differs between this brief and the existing schema; recommend keeping `FailureMechanism` for continuity rather than renaming.

## 6. Cross-Domain Causal-Chain Model

Because `CauseInfluence` is domain-agnostic at the edge level — it connects two `stable_id`s regardless of which `ClassificationTerm` or `CauseCategory` either endpoint carries — cross-domain chains (Method → Mechanical deformation → Optical deviation → Safety effect; Environment EMI → Electrical disturbance → Software malfunction → Safety failure; Measurement calibration failure → false pass → Legal/Safety escape) require no special-case modeling. A chain is simply a sequence of `CauseInfluence` edges where each edge's `target_id` becomes the next edge's `source_id`; the classification tags on the entities along the way are read, not enforced, by chain traversal. This is a structural consequence of the design in Section 5, not an additional feature — worth stating explicitly since Section 18 of the brief calls it out as a major requirement, but the recommended model in Section 5 already satisfies it without further design work.

The LED headlamp example (Section 17 of the brief) is representable end-to-end under this model: `Method` (injection pressure setpoint, a `ProcessCharacteristic` under the Method `CauseCategory`) → `CauseInfluence(status=confirmed_root_cause)` → a `ProductCharacteristic` under the Mechanical classification (lens geometry) → `CauseInfluence` → a `ProductCharacteristic` under Optical classification (optical path) → `CauseInfluence(influence_type="produces")` → `FailureMode` → `FailureEffect` classified Safety. No entity in this chain needs to "know" it is crossing domains.

## 7. FMEA Relationship Mapping

The chain in Section 20 of the brief (`Function → Requirement → Product Characteristic → Failure Mode → Failure Effect → Potential Cause → Process Characteristic → Prevention Control → Detection Control`) is already almost entirely representable with entities that exist today (`Function`, `Requirement`, `Characteristic`/`ProductCharacteristic`, `FailureMode`, `FailureEffect`, `FailureCause`, `PreventionControl`, `DetectionControl`) plus the two new pieces this review adds (`ProcessCharacteristic`, `CauseInfluence`). The only genuinely new link is `Failure Cause ↔ Process Characteristic`, expressed as a `CauseInfluence` from the `ProcessCharacteristic` to the `FailureCause`. This becomes a core, named relationship chain in the domain documentation once approved — it does not require restructuring anything already implemented.

## 8. Problem-Solving Mapping (8D / CAPA / RCA)

Section 21's loop (`Observed Product Characteristic Failure → 5M+E candidates → candidate Process Characteristics → evidence gathering → candidate causes → confirmation/rejection → Root Cause`) is exactly the `CauseInfluence` status lifecycle from Section 5, run in an investigation context rather than a design-time FMEA context. This review does **not** propose a `Problem`/`8D`/`CAPA`/`Complaint` entity now — those remain out of scope, consistent with the original architecture report's phasing (explicitly deferred "Living FMEA" territory). What this review does establish is the causal-chain spine (`ProcessCharacteristic`, `CauseInfluence`, status vocabulary) that a future Problem/8D/CAPA package will attach to, without having to redesign the cause model when that package is eventually built. This is the correct scope boundary: build the reusable spine now, build the investigation workflow later.

## 9. Control Plan Mapping

Full Control Plan modeling (Section 19 of the brief) is **explicitly out of scope for this review** — no `ControlPlan` or `ControlPlanReviewProposal` entity is proposed now. The existing `PreventionControl`/`DetectionControl`/`MeasurementMethod` entities are the natural seed of future Control Plan rows and need no change to support that later. Recommend treating "propose a Control Plan review when a `CauseInfluence` reaches `confirmed_root_cause` against a critical `ProcessCharacteristic`" as a **future rule**, not a structural requirement today — and reaffirming the brief's own instruction that no approved Control Plan may ever be silently modified, only reviewed via an authorized, human-approved workflow once that workflow exists.

## 10. Knowledge / Lessons Learned Mapping

One genuinely new entity is proposed here: `LessonLearned`. Fields: references to the originating `FailureMode`/`CauseInfluence`/`RecommendedAction`/`EffectivenessVerification` that produced it, an applicability signature (the `ClassificationTerm`s and `CauseCategory` involved, so future matching — "similar Product Characteristic + similar Process Characteristic + similar Failure Mode" per Section 22 — has something concrete to match against), a review/approval status, and standard `provenance`/`evidence` fields already established elsewhere in the domain model. `EffectivenessVerification` already exists and feeds directly into this — no change needed there.

Matching "similar historical cause" against new investigations (Section 22) is a **query** over this data, not a new relationship type — and, per the architecture report's own finding, real cross-record search of this kind is exactly the capability the (currently unimplemented) Open-EQMS Query Engine's Semantic Inquiry Layer is aimed at long-term (`SPEC-004` Sections 24–25, contract only, not implemented). For the Django PoC, this remains an ordinary application-level query; nothing here should be built assuming Query Engine access.

## 11. Measurement / MSA Mapping

Section 12's distinction — true product state vs. observed product state vs. measurement-system failure — is modeled as: `MeasurementMethod` (already exists) gains fields for accuracy/precision/repeatability/reproducibility/resolution/bias/linearity/stability/calibration status/calibration validity/measurement uncertainty (an `attributes` bag, same pattern as `ProcessCharacteristic`, since not every measurement method needs every field). A **measurement-system failure** is then representable as its own `CauseInfluence` targeting the `DetectionControl` or `MeasurementMethod` itself (not the product), with `influence_type = "detection_failure"` — keeping it structurally distinguishable from a `CauseInfluence` that targets a `ProductCharacteristic` or `FailureMode` directly (a genuine product failure). This satisfies the brief's requirement to distinguish product failure, detection failure, and measurement-system failure as three different things without adding three different entity types — the distinction lives in what the influence edge targets, not in three parallel schemas.

## 12. Coverage Metric Definitions

All metrics in Section 23 (Legal/Safety characteristic FMEA coverage, characteristic control coverage, characteristic measurement coverage, critical-process-characteristic control coverage, cause-to-control coverage, FMEA-to-Control-Plan coverage) are **computed queries over the graph**, not stored entities or new fields. Each is expressible once `ProductCharacteristic`, `ProcessCharacteristic`, and `CauseInfluence` exist: e.g. "Safety FMEA coverage" = count of `ProductCharacteristic` with `primary_classification = Safety` that have at least one `CauseInfluence`/`FailureMode` link, divided by total Safety-classified characteristics. No new structural design is required to support these; they are Django/domain query helpers to build once the underlying entities exist, and they satisfy the brief's own preference (Section 23) for deterministic, evidence-based counts over opaque AI-generated scores.

## 13. Portable-Data Impact

Every new concept — `ClassificationScheme`/`ClassificationTerm`, `CauseCategoryScheme`/`CauseCategory`, `ProcessCharacteristic`, `CauseInfluence`, `LessonLearned` — is proposed as a `DomainEntity` subtype in `fmea_domain/entities.py`, inheriting the same `stable_id`/`schema_version`/`revision` shape every existing entity already has, and is exported through the same OFEF mechanism (`fmea_importexport/ofef.py`) reviewed in Phase B: added to `_ENTITY_TYPES`, serialized/deserialized the same way, subject to the same `"not": {"required": ["id"]}` JSON Schema guardrail already in place. No new interchange mechanism is needed — this is additive to the existing portable model, exactly as Section 28 of the brief requires, and nothing here is Django-only.

## 14. Django Implementation Impact

Additive, not breaking, with one exception. New Django models mirror the new domain entities using the existing `StableModel` base (already reviewed and sound in Phase B) — no change to that base is needed. The one breaking change under consideration is renaming `Characteristic` → `ProductCharacteristic` for symmetry with the new `ProcessCharacteristic` (Section 3); if adopted, this requires a small data migration for the one demo `Characteristic` row already seeded, not a redesign. Recommend deciding this explicitly (Section 16) rather than letting it happen incidentally during implementation.

## 15. Open-EQMS Future-Integration Impact

No change to the conclusion already reached in the architecture report: none of this depends on any Open-EQMS Runtime capability, because no Python↔Rust integration path exists yet regardless of Runtime maturity. Worth noting for the record: this causal-chain, evidence/confidence-carrying graph model is a natural future fit for `PRS-000` Section 17 ("Know-How Tracking") and Section 21 ("OPEN-FMEA")'s own closed-loop description, and for `SPEC-004`'s long-term Organizational Knowledge Graph ambitions — but none of that is a dependency today, only a direction this design happens to already point toward.

## 16. Risks and Ambiguities

- **Scope risk.** This is a large amount of new taxonomy/entity surface (five new entity types, two new configurable scheme libraries) to add while Phase B's very first vertical slice hasn't been committed yet. Recommend an explicit, narrower first increment: `ClassificationScheme`/`ClassificationTerm`, `ProductCharacteristic` extension, `CauseCategoryScheme`/`CauseCategory`, `ProcessCharacteristic`, and `CauseInfluence` with its status vocabulary. Defer `LessonLearned`, coverage-metric query implementations, and any Control Plan hook to a follow-up slice — matching the "one completed vertical slice over many partial modules" principle both governing documents already established.
- **Naming decision required.** Keep `Characteristic` as-is and add `ProcessCharacteristic` as a sibling, or rename to `ProductCharacteristic` for symmetry (Section 14 impact noted above). Recommended: rename, for long-term clarity, accepting the one-time migration cost now while the dataset is still a demo seed.
- **"Potential Cause" modeling decision required.** Recommended default in Section 5: no separate `PotentialCause` entity; candidate causes are `CauseInfluence` edges targeting a `FailureMode` directly, promoted to reference a `FailureCause` on confirmation. This is a real domain-modeling choice with a plausible alternative (a dedicated staging entity) and should be confirmed, not assumed.
- **`Relationship` vs. `CauseInfluence` duplication risk.** Introducing a second relationship-like entity type alongside the existing generic `Relationship` is a deliberate trade-off (Section 5) — richer typing at the cost of two link mechanisms existing side by side. If this becomes awkward in practice, a later ADR-equivalent could fold `Relationship` extra fields into a common base; not needed for this increment.
- **Evidence linkage is currently narrower than this proposal needs.** Today's `Evidence` entity is tied to `action_id` only. It needs to be reachable from a `CauseInfluence` too. Recommend linking `Evidence` to a `CauseInfluence` via the existing generic `Relationship` mechanism (an `evidence_supports_cause_influence` relationship type) rather than widening `Evidence`'s own schema — consistent with Section 5's reasoning about what belongs in a typed entity versus a generic relationship.

## 17. Decisions Requiring Project Manager Approval

1. Adopt the `CauseInfluence` entity design (Section 5) — including the recommended resolution of "Potential Cause" as a status on `CauseInfluence` rather than a separate entity — as the canonical Open-FMEA cause/effect relationship model.
2. Rename `Characteristic` → `ProductCharacteristic` (Section 14/16), accepting the small migration now.
3. Approve the narrower first-increment scope (Section 16): classification/cause-category schemes, `ProductCharacteristic` extension, `ProcessCharacteristic`, `CauseInfluence` — deferring `LessonLearned`, coverage-metric implementations, and any Control Plan hook to a follow-up slice.
4. Confirm the Man-category boundary (Section 4) — observable organizational evidence only, no subjective/health scoring — as a permanent domain constraint, not just a first-pass caution.
5. Confirm `Evidence` linkage extends via the existing generic `Relationship` mechanism rather than widening `Evidence`'s own schema (Section 16).

## Recommendation

**READY WITH CONDITIONS.**

The proposed model does not conflict with anything implemented in Phase B — it extends the existing entity set using patterns (configurable definition libraries, the `DomainEntity`/OFEF export shape, domain-first design) already proven there, and it satisfies every structural requirement in the governing brief (multi-classification, non-hardcoded taxonomies, cross-domain causal chains, cause-status vocabulary, Ishikawa-as-a-view) without inventing new mechanisms beyond what Phase B already established. Conditions: the five decisions in Section 17 need explicit approval, and the scope for the first implementation increment should be the narrower list in Section 16, not the full set of new entities at once.

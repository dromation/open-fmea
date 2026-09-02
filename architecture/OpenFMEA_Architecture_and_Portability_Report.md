# Open-FMEA Architecture & Portability Report

Status: Draft for Project Manager review — not an ADR, not implementation authorization

Author: Claude, acting as Open-FMEA Technical Architect and Lead Developer

Date: 2026-08-30

Authority: subordinate to `Open-EQMS_Architecture_Baseline_v1.0.md` and `PRS-000-master-product-vision.md` (Section 21, "OPEN-FMEA"). Where this report proposes something those documents do not already cover, it is a proposal requiring approval, not a restatement of ratified architecture.

This report is the required first output per the governing brief: a repository-grounded architecture and portability assessment for Open-FMEA, produced before any Django implementation begins. It does not authorize implementation.

---

## 1. Current Open-EQMS Repository Findings

Repository: `github.com/dromation/open-eqms` (GPL-2.0). Local clone inspected at the working folder's `open-eqms-repo` subdirectory, branch `main`, up to date with `origin/main`.

**Governance structure actually in use**, confirmed by direct inspection rather than assumed:

- `architecture/Open-EQMS_Architecture_Baseline_v1.0.md` — Status: Normative / Approved / Authoritative. The single technical authority. 28 sections covering mission, Runtime component list, object model, process/rule/query engines, event/transaction model, statistics/KPI, content packages, GUI, security, plugins, AI, integration, storage, synchronization, retention, localization, performance, regulatory traceability, technology stack (Rust core), MVP boundary, roadmap, and repository governance rules.
- `architecture/product/PRS-000-master-product-vision.md` — the mandatory product north star. Explicitly **not** implementation authorization; where it exceeds ratified architecture it requires the same requirements → architecture → ADR/SPEC → review → approval path as any other change (`AGENTS.md` rule stated verbatim). **Section 21 of this document is titled "OPEN-FMEA"** and already describes an object list and closed-loop diagram nearly identical to the one in the governing brief for this report (Sections 4-7 below quote it directly). This is a strong, pre-existing signal that Open-FMEA is a recognized, wanted part of the north star, not a speculative side project.
- `AGENTS.md` — 21 binding rules for any agent (human or AI) working in the repository. Key ones for Open-FMEA's own governance: never silently modernize legacy prototype code into new architecture (rule 21); require an ADR for architectural changes (rule 20); keep business methods out of the Runtime (rule 6); use the Query Engine as the only structured-query mechanism (rule 9); preserve offline-first operation and determinism (rules 13-14).
- ADRs (`architecture/adr/`): ADR-0000 (adopt the Baseline; legacy prototype preserved under `legacy/`), ADR-0001 (shared `runtime-contracts` crate), ADR-0002 (shared Unit-of-Work contract), ADR-0003 (shared `Version` contract), ADR-0004 (Security authorization boundary — contract shape only), ADR-0005 (shared `ConsistencyBoundary` contract — shape only). All Approved.
- SPECs committed to the repo (`architecture/spec/`): SPEC-001 (Object Runtime), SPEC-002 (Event Engine), SPEC-003 (Transaction Engine), SPEC-004 (Query Engine, Revision B corrected, **partially implemented only** — see Section 2). **No SPEC-005 or SPEC-006 exists in the committed repository.** Drafts of a Synchronization Engine spec and a Process Engine spec exist only in the surrounding project working folder, uncommitted and unratified — they are not part of repository reality and must not be treated as available.
- Legacy: `legacy/python-kivy-prototype/` holds the pre-Baseline Python/Kivy/Lua prototype, explicitly preserved for history, explicitly not the architectural foundation, with no guaranteed compatibility to the new Runtime. This is the exact precedent this report recommends Open-FMEA follow for its own current Tkinter prototype (Section 19).
- Pre-alpha demo: `apps/open-eqms-demo` is a real, working CLI that composes Object Runtime + Event Engine + Transaction Engine to register a traceable asset and record an accepted calibration end-to-end (the VS-001 slice). It is explicit that this is pre-alpha, in-memory, non-production, and does **not** use the Query Engine.
- Implementation status at last verified record: 108 passing tests across 5 workspace crates (`runtime-contracts` 7, `object-runtime` 28, `event-engine` 24, `transaction-engine` 21, `query-engine` 28 — the query-engine tests cover only its contract/validation layer, not execution). `cargo fmt`, `cargo check`, `cargo clippy -D warnings`, `cargo test`, `git diff --check` all reported passing after every commit in the record inspected.

## 2. Existing Runtime Capabilities Relevant to Open-FMEA (classified)

**AVAILABLE NOW** (implemented, tested, committed):

- `runtime-contracts`: `ObjectId` (opaque string wrapper, no business meaning), `Version` (monotonic `u64`, `initial()` = 1, `next()`), `UnitOfWork` (opaque handle) plus `UnitOfWorkLifecycle`/`UnitOfWorkStaging` traits, `PropertyValueKind`/`PropertyValue` (a typed, discriminated primitive value model — not a loose dict).
- Object Runtime (SPEC-001): a generic Object model matching Baseline Section 5 field-for-field — `ObjectRecord` carries id, type, properties, relations, lifecycle state, ownership/responsible users, permission-scope reference, version, external references, attachment-set reference, comment-thread reference, retention-rule reference. Typed metadata registry (`ObjectTypeDefinition`, `PropertyDefinition`, `RelationDefinition`/`RelationCardinality`) rather than schema migrations. Public API: `register_object_type`, `create_object`, `read_object`, `update_object`, `update_object_in_unit_of_work`, `add_relation`, `remove_relation`, `visit_all_objects`. Pluggable `StorageProvider`/`ObjectIdGenerator` traits — no concrete SQLite/PostgreSQL provider exists yet, only the abstraction and test doubles.
- Event Engine (SPEC-002): immutable, append-only `EventRecord` with `EventId`, `EventTypeRef`, monotonic `AppendSequence`, timestamp, source, `CorrelationId`/`CausationId` for causal chaining, typed payload via `PropertyValue`.
- Transaction Engine (SPEC-003): `TransactionRecord` with `TransactionLevel` (1/2/3, matching Baseline Section 9 exactly), `AppendIndex`, `PriorReference` (hash chain), `RuleEvaluationMetadata`, `SignedRevision`, `CryptographicProvider` trait. `append_transaction`, `append_transaction_in_unit_of_work`, `read_transaction`.

**SPECIFIED BUT NOT IMPLEMENTED:**

- Query Engine execution (SPEC-004): only the query *model* — `QueryDefinition`, predicates/projections/sort/grouping, `QuerySource` capability model, deterministic ordering rules, execution limits/timeout/cancellation — is implemented, as contract types with no execution behavior. Confirmed absent by the repository's own closure record: real engine adapters, actual data reading, aggregation execution, permission filtering, `ContextPackage`, saved-query persistence, cursors, and any `ConsistencyBoundary` implementation. Blocked pending items below.
- Authorization decision contract (ADR-0004): the contract *shape* (caller/action/target, `Allow`/`Deny`/`HiddenDeny`, audit envelope) is approved, but direct inspection of `runtime-contracts/src/lib.rs` shows **no such type exists in code yet** — only `ObjectId`, `Version`, `UnitOfWork`, `PropertyValue`/`PropertyValueKind` are actually defined. The ADR is approved; the code is not written.
- `ConsistencyBoundary` (ADR-0005): same situation — contract shape approved, not yet added to `runtime-contracts`, and the per-engine APIs needed to populate it (Object Runtime "current revision," Event Engine "max append sequence," Transaction Engine "committed-through index") are explicitly out of scope of the ADR itself and unbuilt.
- Concrete storage providers: SQLite and PostgreSQL providers are architecturally required (Baseline Section 18) but not implemented — only the `StorageProvider` trait abstraction and in-memory test doubles exist.
- Synchronization Engine and Process Engine: drafted (SPEC-005, SPEC-006) only outside the committed repository. Not ratified, not committed, not implementable against.

**FUTURE / UNRESOLVED:**

- Security Engine implementation itself (only the authorization *contract shape* is approved; the policy engine is unscoped and unauthorized).
- Rule Engine, Statistics Engine, KPI Engine, Package Loader, GUI Engine — no SPEC, no ADR, no draft exists anywhere in the inspected material.
- Content Package format, signing, and Capability Manifest mechanics (Baseline Section 11 describes the target, nothing is built).
- Any officially sanctioned Rust ↔ Python/non-Rust integration mechanism. None exists. Nothing in the repository integrates a non-Rust component today.

**Conclusion for Open-FMEA:** none of the "AVAILABLE NOW" Runtime capabilities are consumable by Open-FMEA today, because no integration mechanism between a Python/Django application and the Rust Runtime exists yet, and because Security/Query Engine — the two components almost any real integration would need first — are the least mature. Open-FMEA's Phase A/B work (this report and the Django PoC) must be self-contained and must not silently assume Runtime access it does not have.

## 3. Missing / Future Runtime Dependencies

Restated as a direct dependency list for Open-FMEA's own roadmap, using the same three-bucket classification required by the governing brief:

| Dependency Open-FMEA will eventually want | Status |
| --- | --- |
| Shared identity/version primitives (`ObjectId`, `Version`) | Available now, but only inside the Rust workspace — not reachable from Python/Django |
| Generic Object storage (Object Runtime) | Available now (Rust-only); no cross-language access path |
| Immutable event log (Event Engine) | Available now (Rust-only); no cross-language access path |
| Audit-grade transaction log (Transaction Engine, Levels 1-3) | Available now (Rust-only); no cross-language access path |
| Structured query over shared data (Query Engine) | Contract only; no execution |
| Authorization decisions (Security) | Contract shape only (ADR-0004); no engine |
| Reproducible snapshot marker (`ConsistencyBoundary`) | Contract shape only (ADR-0005); no engine |
| Multi-site/offline delta sync (Synchronization Engine) | Draft spec exists outside the repo; unratified |
| Declarative workflow/state execution (Process Engine) | Draft spec exists outside the repo; unratified |
| Persistent SQLite/PostgreSQL storage | Trait abstraction only; no concrete provider |
| Content Package packaging/signing | Described in Baseline; nothing built |

Open-FMEA must not build against any row above as if it already existed. This report's PoC (Section 14) is scoped to use none of them.

## 4. Proposed Open-FMEA Domain Model

The object list below is deliberately the same list already validated in `PRS-000` Section 21 ("OPEN-FMEA") and Section 3 ("OBJECT-CENTRIC SYSTEM," which explicitly names failure mode, effect, cause, control, problem, action, and evidence as first-class Open-EQMS object types). This is not a coincidence to be papered over — it means the domain model proposed here is already aligned with the ratified north star, which meaningfully de-risks the eventual Phase D integration.

Structural: `Product`, `Process`, `ProcessStep`/`Operation`, `Function`, `Requirement`, `Characteristic` (with a `SpecialCharacteristic` flag/sub-type).

Risk: `FailureMode`, `FailureEffect`, `FailureCause`, `FailureMechanism`.

Control: `PreventionControl`, `DetectionControl`, `MeasurementMethod`.

Action: `RecommendedAction`, `Action`, `ResponsibleRole` (a reference, not owned identity), `ActionStatus`, `Evidence`, `EffectivenessVerification`.

Container/governance: `FMEA` (the analysis header — type, scope, team), `FMEAProject` (optional grouping above one or more FMEAs), `FMEARevision` (Section 11).

Evaluation: no fixed `Severity`/`Occurrence`/`Detection`/`RPN` fields hard-coded onto `FailureMode`. Instead, ratings and results are values produced against a configurable `EvaluationDefinition` (Section 10) — this is a direct requirement, not a stylistic choice: Baseline itself treats "Risk = S × O × D" as one possible business rule, never a Runtime concept, and the governing brief is explicit that not all industries use identical methodology.

Every one of these is modeled as a portable domain concept first (Section 8) — a plain data shape independent of Django — before any ORM model is written.

## 5. Relationship Model

Two chains, both already present almost verbatim in `PRS-000`:

Forward (design-time): `Product → Function → Requirement → Failure Mode → Failure Effect`, and separately `Failure Mode → Failure Cause → Prevention Control → Detection Control → Measurement`. This matches the governing brief's Section 6 exactly and matches `PRS-000` Section 4's Digital Thread (`CAD → BOM → Requirement → Characteristic → Process → PFMEA → Control Plan → Measurement → Production → Complaint → 8D → Root Cause → CAPA → Lesson Learned → FMEA update`).

Living-FMEA loop (future, not required in the PoC): `Real Problem → Analysis → Failure Mode → Confirmed Root Cause → Corrective Action → Effectiveness Verification → FMEA Review → Control Plan Review → Instruction/Maintenance Review → Recurrence Monitoring`, and in reverse, `New Problem → existing FMEA → possible failure modes → known effects/causes → controls → historical occurrences → initial investigation evidence` — this is `PRS-000` Section 21's own wording, word-for-word the same shape as the governing brief's Section 7. The domain model must not prevent these relationships even though the PoC does not implement the full loop.

Relationships are modeled as typed, directional links carrying their own identity (not foreign-key-only), so that a relationship can later carry provenance, confidence, or approval status independently of either endpoint — mirroring Object Runtime's own `Relation`/`RelationDefinition` shape (a relation type plus cardinality, not a bare FK).

## 6. Portable Identity Strategy

Every domain entity carries a `stable_id`: an opaque, immutable string identifier, generated independently of any database auto-increment sequence (ULID or UUIDv7 recommended — both are sortable and time-ordered without leaking a row count). Django's internal integer primary key remains for ORM joins and query performance only; it is never exposed in any export, API response, or cross-system reference. This directly mirrors `runtime-contracts::ObjectId` — "opaque, no business meaning" — so that a future mapping from Open-FMEA's `stable_id` to an Open-EQMS `ObjectId` is a lookup, not a redesign.

Every entity also carries a `revision`: a monotonic, per-entity integer starting at 1, incremented on every controlled change. This mirrors `runtime-contracts::Version` (`initial()` = 1, `next()`) in shape, so the same optimistic-concurrency pattern Object Runtime already uses is available to Open-FMEA without translation later.

Both choices are proposed now, before any Django model exists, specifically so identity is never retrofitted.

## 7. Neutral Interchange Strategy

JSON as the primary interchange format, with an explicit, versioned Open-FMEA Exchange Format (OFEF): every exported object carries `stable_id`, `type`, `schema_version`, `revision`, and a `provenance` block (`source`, `imported_from`, `approval_status`) — matching Baseline Section 21's own requirement that "every transaction type carries a schema version from day one."

Property values are exported as a typed, discriminated bag (string / number / boolean / date / enum / reference), not a loose untyped dict — mirroring `PropertyValue`'s own discriminated-kind approach — so an independent parser in any language can reconstruct types unambiguously without depending on Python's own type coercion.

JSON Schema is used to validate OFEF documents. OpenAPI is used for the Django REST Framework surface, justified by the brief's own requirement that the domain be reachable from Rust, native apps, browsers, and mobile later — but DRF and OpenAPI are second-priority; they are not required for the PoC's vertical slice to work end-to-end locally. Protobuf is explicitly not adopted for v1: nothing in the PoC's scope needs binary wire efficiency or cross-service RPC yet, and the brief itself warns against unjustified protocol complexity.

## 8. Django Architecture

Proposed top-level Python packages inside the Django project:

- `fmea_domain/` — plain Python (dataclasses/protocols), zero Django imports. The portable domain model from Section 4, plus business rules (Section 9). This package is the one that must still make sense if Django disappeared tomorrow.
- `fmea_app/` — the Django app: `models.py` as a thin persistence mapping to/from `fmea_domain` objects, `admin.py`, Django views/templates or DRF views for the PoC's minimal UI.
- `fmea_evaluation/` — pluggable evaluation calculators keyed by an `EvaluationDefinition.method` identifier (Section 10).
- `fmea_importexport/` — Excel/CSV/OFEF-JSON import and export, including the mapping/validation/preview pipeline required by Section 12/17 below.
- `fmea_api/` (optional for the PoC, recommended once the vertical slice works) — DRF serializers/viewsets exposing OFEF JSON over REST, documented with OpenAPI.

## 9. Separation Between Domain and Django Implementation

`fmea_domain` never imports `django`. `models.py` provides explicit `to_domain()` / `from_domain()` functions on every model; no business logic lives inside `save()`, a view, a template, an admin action, or frontend JavaScript. Business rules named in the governing brief — rating validation, required relationships, approval-state transitions, action completion rules, revision rules, risk recalculation — are pure functions in `fmea_domain/rules.py`, unit-testable without a Django test database, and are exactly the unit that would later be reimplemented as a Content Package rule set or validated against a future Open-EQMS Rule Engine, without the surrounding Django/ORM code being relevant to that migration at all.

## 10. Evaluation / Scoring Architecture

An `EvaluationDefinition` object declares: a `method` id (e.g. `classic-rpn`, `aiag-vda-ap`, or an organization-defined custom matrix), the rating scales it uses (each scale carries its own min/max and localizable labels — never hard-coded English text), and is referenced, not duplicated, by every risk result it produces. A risk result is stored as its own record — inputs used, `EvaluationDefinition` reference, computed output, timestamp, and the actor/trigger that caused recalculation — never as a bare number overwritten in place. This preserves the before/after comparison an FMEA needs when a control changes, and satisfies `PRS-000` Section 33's "a result without provenance should not silently become organizational truth" even though no Runtime Transaction Engine is available yet to enforce it structurally.

Recommended PoC scope: implement exactly two methods — classic RPN (S × O × D) and one AIAG-VDA Action Priority variant — to prove the calculator is genuinely pluggable without over-building before real demand is known.

## 11. Revision / Change-Control Model

FMEA-level lifecycle: `draft → in_review → approved → superseded → obsolete`. Every transition is itself a recorded change carrying actor, timestamp, from-state, to-state, and reason — the same field set Baseline Section 9 requires of a Transaction/Audit record (actor, device/source, time, old/new value, base version, reason), even though the PoC's own audit trail is ordinary Django-side history (e.g. a `django-simple-history`-style table), not a cryptographically chained Transaction Engine record. This is a deliberate shape match: the PoC's audit rows are designed so they could later be re-expressed as Transaction Engine Level 1/2 records without changing what data is captured, only where it is stored. No Level 3 e-signature behavior is implemented or claimed in the PoC — Level 3 is explicitly a "regulated extension" in the Baseline's own MVP boundary table, and Open-FMEA has no cryptographic signing capability to build on yet.

## 12. Import / Export Architecture

Priority order: Excel/XLSX and CSV first, OFEF JSON second, existing organizational FMEA templates third. Round-trip capability (export then re-import without loss) is a goal for OFEF JSON specifically, verified by the acceptance test in Section 17.

There is existing prior art worth preserving, not discarding: the current Tkinter prototype already ships per-library CSV files (`contents/CAUSES.csv`, `CONTROLS.csv`, `DETECTIONS.csv`, `EFFECTS.csv`, `FAILURES.csv`, `RPN.csv`, `SFC.csv`, `SOD.csv`) and per-industry FMEA templates (`fmea_design.csv`, `fmea_operations.csv`, `fmea_process.csv`, `fmea_product.csv`, `fmea_software.csv`, `fmea_system.csv`, `fmea_type.csv`). These are candidate seed content for the new controlled libraries (Section 9 of the governing brief), but must go through the same mapping → validation → preview → import pipeline as any external legacy data, tagged with `provenance.imported_from = "legacy-tkinter-prototype"`, never imported silently as if it were already-approved content.

## 13. Open-EQMS Future Integration Map

| Open-FMEA need | Eventual Open-EQMS capability | Current status |
| --- | --- | --- |
| Shared Product/Process/Function objects across applications | Object Runtime | Implemented (Rust-only, no cross-language path) |
| FMEA lifecycle facts as immutable events | Event Engine | Implemented (Rust-only, no cross-language path) |
| Auditable approvals/revisions | Transaction Engine (Levels 1-3) | Implemented (Rust-only, no cross-language path) |
| Cross-FMEA search, "similar failure mode" queries | Query Engine | Contract only, no execution, blocked on Security + ConsistencyBoundary |
| Real authorization on who can see/edit what | Security | Contract shape only, no engine |
| Multi-site/offline FMEA collaboration | Synchronization Engine | Unratified draft outside the repo |
| Structured 8D/CAPA workflow linkage | Process Engine | Unratified draft outside the repo |
| Content-Package-based FMEA delivery | Package Loader + Content Package format | Not built |

Per Baseline Section 27 and the governing brief's own Phase D gating, none of these integrations may be built until the corresponding Runtime contract exists and is approved. This report proposes no Phase D work.

## 14. Proposed Minimal Working PoC

Scoped to run entirely on Django + SQLite (PostgreSQL-compatible) + a local browser, using nothing from the row list in Section 3:

Create FMEA → define Product/Process → define Function → define Requirement → add Failure Mode → add Effect → add Cause → add Prevention Control → add Detection Control → perform configurable risk evaluation (classic RPN and one AIAG-VDA variant) → create Action → record completion/evidence → re-evaluate → create Revision → export (OFEF JSON and XLSX).

This is one completed vertical slice, matching the governing brief's own instruction to prefer one finished slice over many partial modules.

## 15. Proposed Repository Structure

```text
open-fmea/
  architecture/
    adr/
    spec/
    product/
  domain/            # fmea_domain — framework-free
  django_app/         # fmea_app, fmea_evaluation, fmea_importexport, fmea_api
  legacy/
    tkinter-prototype/   # current fmea_app.py and everything beside it, moved as-is
  docs/
    exchange-format/    # OFEF JSON Schema, versioned
README.md
AGENTS.md
```

This deliberately mirrors `open-eqms`'s own top-level structure (`architecture/`, an implementation area, `legacy/`) so the two repositories stay legible to the same contributors using the same mental model.

## 16. Test Strategy

`fmea_domain`: pure unit tests, no database, no Django test runner needed. `fmea_evaluation`: table-driven tests per methodology (known input ratings → known output). `django_app`: model/serializer/API tests using Django's test framework. `fmea_importexport`: round-trip tests (export then re-import, assert equality on domain objects, not on raw bytes). The portability acceptance test (Section 17) runs as its own separate, mandatory CI job, distinct from ordinary unit tests, because its purpose is specifically to catch domain logic that has quietly become Django-dependent.

## 17. Portability Acceptance Test

Per the governing brief's own required acceptance criterion: build a populated FMEA (multiple failure modes/causes/controls/actions, at least one evaluation recalculation, at least one revision). Export it to OFEF JSON from the Django application. In a fresh environment with no Django installed (a plain Python virtual environment, or ideally a second language entirely — even a minimal Node or Rust JSON-Schema-validating script), parse the export independently and reconstruct the semantic FMEA: every `stable_id`, every relationship, every revision number, and every evaluation result and its inputs must survive intact. This test must exist and pass before the PoC is declared portable — it is a required gate, not an optional nicety.

## 18. Identified Architectural Risks

- **Identity leakage.** The single biggest risk to portability is a Django auto-increment PK quietly leaking into an export, a URL, or a foreign-system reference. This needs an explicit code-review checklist item and, ideally, a lint/test that fails if any serializer emits a raw integer `id` field.
- **Open-EQMS Runtime is not consumable yet, on any realistic near-term timeline.** Open-FMEA must not block its own delivery waiting for Query Engine execution, Security, or a Rust↔Python bridge that does not exist and is not scheduled. This report's PoC intentionally depends on none of it.
- **The legacy prototype has real data, not just old code.** Unlike a clean-slate rewrite, `tables/*.csv`, `open_fmea.sql`, and `open_fmea_type.sqbpro` under the current repository represent actual working content (default tables, per-industry templates, prior FMEA data shapes). Treat this as a real, non-trivial legacy-import problem (Section 12), not as disposable prototype code to delete.
- **PoC authorization must be clearly labeled non-authoritative.** Whatever Django-side auth is built for the PoC (Section 22 of the governing brief) must never be silently treated later as "the" Open-FMEA security model — that decision belongs to a future Security Engine integration, once one exists.
- **Evaluation-method scope creep.** Supporting every conceivable industry methodology in the PoC risks shipping nothing. Recommend exactly two methods for the PoC (Section 10) with the calculator contract designed for more.
- **Two parallel "real" implementations.** If the Tkinter prototype keeps receiving substantive feature work while the Django rebuild is underway, the project accumulates two systems of record. This is the direct reason Section 19's freeze recommendation matters.

## 19. Decisions Requiring Project Manager Approval

1. Adopt Django + (optionally) Django REST Framework + SQLite/PostgreSQL as the confirmed Open-FMEA PoC stack, formally, as this report's proposal — the governing brief already leans this way, but nothing has ratified it for this repository yet, the way ADR-0000 ratified the Rust Runtime direction for Open-EQMS.
2. Freeze the current Tkinter/SQLite prototype (`beta-v01`) as `legacy/` before new domain work begins, mirroring `open-eqms` ADR-0000 exactly. This session already began that transition in practice: PR #4 (a real crash fix — `Image.ANTIALIAS`, removed in Pillow 10+, still referenced on `beta-v01`) was reviewed earlier this session and is recommended for merge specifically because `beta-v01` is about to become the frozen legacy reference and should not freeze with a known crash bug in it.
3. Initial evaluation-method scope for the PoC: classic RPN and one AIAG-VDA Action Priority variant, per Section 10 and Section 18.
4. Whether the legacy CSV/SQLite library content under `contents/`/`tables/` is imported as seed library content now, or deferred to a later, dedicated import milestone.
5. Repository decision: continue in the existing `dromation/open-fmea` repository, restructured per Section 15 with history and the legacy prototype preserved, rather than starting a fresh repository — recommended, mirroring how `open-eqms` itself preserved its own history rather than discarding it.

## 20. Recommendation

**READY WITH CONDITIONS.**

The grounding is solid: `PRS-000` Section 21 already ratifies this exact object list and closed-loop relationship model as product north star, so the domain model proposed here is not a competing design, it is an implementation of an already-approved vision fragment. None of the proposed Phase B (Django PoC) work depends on any Open-EQMS Runtime capability that is not yet implemented — Section 2's findings show clearly that no such dependency is safe to take today regardless, since no cross-language integration path from Python to the Rust Runtime exists yet.

Conditions before Phase B implementation begins: the five decisions in Section 19 need explicit Project Manager approval, in particular the legacy-freeze decision (2) and the PR #4 merge (already recommended, separately, in this session) — both should happen before or alongside starting the new domain work, not after, so the project never has two independently evolving "real" implementations at once.

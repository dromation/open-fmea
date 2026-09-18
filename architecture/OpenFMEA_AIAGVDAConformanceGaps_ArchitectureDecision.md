# Open-FMEA Architecture Decision — Closing the Three AIAG & VDA Conformance Gaps

Status: **Decision, 2026-09-12** — proposing three independent, firm, narrow defaults for the user to approve, correct, or decline separately. Written directly in response to `OpenFMEA_AIAGVDAConformance_ArchitectureReview.md`'s three highest-priority findings. **Nothing currently built is removed, renamed in place, or reinterpreted by any option proposed here** — every option below is additive on top of the 25 already-shipped slices, per the user's explicit instruction to keep everything that already exists. Each of Part A, B, and C is its own decision the user can accept independently; accepting one does not commit to the others.

Grounded directly in the real, current code before writing this — `django_app/fmea_app/models.py` (`EvaluationDefinition`, `RiskEvaluation`, `ProductCharacteristic`, `ProcessCharacteristic`, `ClassificationScheme`/`ClassificationTerm`, `FMEA.FMEA_TYPE_CHOICES`), `django_app/fmea_evaluation/calculators.py`, `django_app/fmea_app/risk_matrix.py`, `django_app/fmea_app/management/commands/seed_demo.py` — plus the AIAG & VDA FMEA Handbook (1st Ed. 2019) sections read directly for the prior review (Appendix C tables, Section 2.5/3.5 Risk Analysis, Section 4 FMEA-MSR, Appendix D1 Special Characteristics).

---

## Part A — Real Severity/Occurrence/Detection criteria + a real Action Priority table

### A.1 What already exists, verified live

`EvaluationDefinition.rating_scales` is a `JSONField` — currently seeded (`seed_demo.py`) as only `{"minimum": 1, "maximum": 10}` per factor, no criteria text. `RiskEvaluation.severity`/`.occurrence`/`.detection` are bare `PositiveSmallIntegerField`s (1-10), unconstrained beyond range. Two `EvaluationDefinition` rows already exist: `classic-rpn` (`calculate_classic_rpn`: `severity × occurrence × detection`, banded at ≥200/≥80/else) and `aiag-vda-ap-poc` (`calculate_action_priority`, using `_action_priority_band()` — a small hand-written set of threshold rules, explicitly labeled in the code's own docstring as *"a PoC variant"*). `risk_matrix.normalize_method()` falls back to `classic-rpn` for any missing/unrecognized value — RPN-threshold classification is today's effective default display method, which is the specific practice the handbook says is not recommended.

### A.2 Decision 1 — add real criteria text to `rating_scales`, don't touch the schema

`rating_scales` is already a `JSONField`, so populating it with the handbook's real per-band criteria text for Severity (Table D1), Occurrence (Table D2), and Detection (Table D3) is a **data-only change — no migration, no model change**. Proposed shape (additive to what's already there):

```json
{
  "severity": {
    "minimum": 1, "maximum": 10,
    "bands": {"10": "Affects safe operation...", "9": "Noncompliance with regulations.", "...": "..."}
  },
  "occurrence": {"minimum": 1, "maximum": 10, "bands": {"10": "...", "...": "..."}},
  "detection": {"minimum": 1, "maximum": 10, "bands": {"10": "...", "...": "..."}}
}
```

The GUI's Severity/Occurrence/Detection input fields (wherever a `RiskEvaluation` is entered — need to locate the exact form once this is instructed) would show the matching band's real text next to each 1-10 choice, the same way `RELATIONSHIP_TYPE_CHOICES` already renders human labels next to machine values elsewhere in this app — no new interaction pattern, just real content behind an existing pattern.

**Open sub-question needing the user's call**: the handbook gives DFMEA's Severity table (Table D1) one set of wording and PFMEA's own severity table a differently-worded one (PFMEA severity is framed across three perspectives — "Your Plant" / "Ship to Plant" / "End User" — not DFMEA's single vehicle-level framing), while Occurrence and Detection each also have separate DFMEA vs. PFMEA versions with different criteria bases (DFMEA: product-experience/prevention-control maturity; PFMEA: process-experience/prevention-control maturity, worded around manufacturing rather than design). **Proposed default: store DFMEA's and PFMEA's versions as two separate `rating_scales` entries** (e.g. on two `EvaluationDefinition` rows, `aiag-vda-dfmea` and `aiag-vda-pfmea`, both new — see Decision 2), rather than force one shared wording onto both FMEA types. This is the literally-correct reading of the handbook, but is more content to transcribe than a single shared table — confirm this is worth the extra scope, or say if one shared table (using DFMEA's wording everywhere) is an acceptable simplification for now.

### A.3 Decision 2 — add new method(s), do not overwrite `aiag-vda-ap-poc` in place

Since `RiskEvaluation.definition` is a `ForeignKey(EvaluationDefinition, on_delete=PROTECT)` and existing seeded/demo data already carries `method="aiag-vda-ap-poc"` results, silently changing what that method *means* would retroactively reinterpret historical evaluations. **Proposed: add a new method, `aiag-vda-ap` (real table), as a new `EvaluationDefinition` row, leaving `classic-rpn` and `aiag-vda-ap-poc` exactly as they are** — both remain selectable, per "keep everything." `fmea_evaluation/calculators.py` gains a new `calculate_action_priority_real(rating)` (or similar name) implementing the actual Table AP lookup (Severity-band → Occurrence-band → Detection-band → High/Medium/Low), transcribed in full from Appendix C — **not yet done**: the prior review's extraction captured the table's shape and several example rows, not its complete cell-by-cell enumeration. Before an implementation instruction can be written responsibly, someone needs to read Appendix C's AP table pages in full and transcribe every band combination — flagging this now so it isn't silently approximated later the way the current PoC was.

### A.4 Decision 3 — `normalize_method()`'s default fallback

Once a real `aiag-vda-ap` method exists, should `risk_matrix.normalize_method()` keep falling back to `classic-rpn` (today's behavior, kept for backward compatibility with existing demo data and any FMEA that intentionally still wants RPN), or should the fallback change to the new real AP method (aligning the *default* view with what the standard actually recommends)? **Proposed default: change the fallback to `aiag-vda-ap` once it exists**, since the handbook is explicit that RPN-threshold is not a recommended default, while leaving `classic-rpn` fully available as an explicit, non-default choice for anyone who wants it. Confirm or say if `classic-rpn` should stay the default.

### A.5 Explicitly out of scope for Part A

No change to `RiskEvaluation`'s schema (still three plain integers — the real criteria text lives in `rating_scales`, not as new columns). No removal of `classic-rpn` or `aiag-vda-ap-poc`. No change to the Risk Matrix's grid axes (`classify_severity_occurrence`, a *different*, already-separate severity×occurrence banding used only for grid coloring, stays as-is — this was already noted as independent of AP in the code's own comment).

---

## Part B — FMEA-MSR (Supplemental FMEA for Monitoring and System Response)

### B.1 What already exists, verified live

`FMEA.FMEA_TYPE_CHOICES` = `design`, `process`, `product`, `software`, `system` — no `msr`/monitoring-related value. Nothing named "MSR", "Monitoring", "Frequency rating", or "Failure Scenario" exists anywhere in the codebase (confirmed by the prior review's grep pass). This is a **wholly new capability** — unlike Parts A and C, there is no partial version of this to extend.

### B.2 Decision 1 — reuse the existing `RiskEvaluation`/`EvaluationDefinition` plumbing, don't invent a parallel model

The handbook's FMEA-MSR keeps the same three-factor shape as DFMEA/PFMEA (Severity stays identical; Occurrence is renamed/reinterpreted as **Frequency (F)**; Detection is renamed/reinterpreted as **Monitoring (M)**), each still 1-10, each still combining into its own Action Priority table. **Proposed: no new risk-evaluation model.** A new `EvaluationDefinition` (`method="aiag-vda-msr"`) reuses the existing `RiskEvaluation.severity`/`.occurrence`/`.detection` integer fields verbatim — `occurrence` holds the Frequency (F) rating, `detection` holds the Monitoring (M) rating, under this one method. This is the same "one generic 3-factor row, meaning depends on `method`" pattern the app already uses for `classic-rpn` vs. `aiag-vda-ap-poc` — no schema change for the rating fields themselves.

### B.3 Decision 2 — the Failure Scenario concept (Non-Hazardous / Hazardous / Mitigated) needs one new field — the one real model change in this whole proposal

FMEA-MSR's distinguishing concept — whether a fault leads to a Non-Hazardous outcome, a Hazardous one, or a Mitigated one (system/driver detects and responds before the hazard) — has no existing field to reuse; it is genuinely new. **Proposed: one new nullable `failure_scenario` choice field on `RiskEvaluation`** (`non_hazardous` / `hazardous` / `mitigated`, blank/null for every non-MSR evaluation — meaningless outside `method="aiag-vda-msr"`), populated only when the FMEA-MSR method is used. This is the **one migration this entire three-part proposal needs** — flagged explicitly since every other change across Parts A/B/C is additive/data-only. Confirm this is acceptable, or propose an alternative (e.g. storing it inside the existing `result` JSONField instead of a new column — also viable, and avoids a migration entirely at the cost of it being less queryable/filterable; this is a real trade-off worth the user's call, not assumed).

### B.4 Decision 3 — does FMEA-MSR need its own `fmea_type`, or does it attach to an existing DFMEA?

The handbook frames FMEA-MSR as a **supplement to an existing DFMEA**, not a freestanding analysis — same Structure/Function Analysis artifacts as its parent DFMEA are reused, only Failure/Risk Analysis differ. **Proposed: do not add a new `FMEA_TYPE_CHOICES` value.** Instead, FMEA-MSR results live as `RiskEvaluation` rows (`method="aiag-vda-msr"`) against the **same `FailureMode` rows an existing `design`-type FMEA already has** — an MSR risk view is a second lens on the same failure modes, not a separate project. This keeps the "PM-FMEA" (`fmea_type` value never added, separate held-off maintenance concept) and FMEA-MSR (a `method` value on existing evaluations) clearly distinct in the data model, which directly addresses the naming confusion the prior review flagged. Confirm this framing, since it's the most consequential design call in Part B — a "no, FMEA-MSR should be its own FMEA-like top-level thing" answer would restructure this considerably.

### B.5 Decision 4 — GUI scope for a first increment

**Proposed, narrow first increment**: extend the existing Risk tab/detail panel (already built in Slice O's `failure_mode_list`) with an `aiag-vda-msr` option in whatever method selector exists, rendering Frequency/Monitoring instead of Occurrence/Detection labels when that method is active, plus the new `failure_scenario` field. **Not proposed for a first increment**: a dedicated FMEA-MSR-specific page, a Fault Handling Time Interval field, or the handbook's more detailed sub-rules (e.g. lowering F based on % of operating-time exposure, or the M=1-forces-mitigated-severity rule for the parent DFMEA's own AP). These are real parts of the handbook worth eventually capturing but are individually smaller decisions that don't block a usable first version.

### B.6 Explicitly out of scope for Part B

The Fault Handling Time Interval as its own tracked field. Any change to `PM-FMEA`'s existing standing hold — this proposal does not lift, touch, or reference that hold; it is a fully separate track, kept exactly as-is. A standalone FMEA-MSR page/route — Decision 5 confines this to the existing Failure Mode risk views for a first increment.

---

## Part C — Special Characteristics: DFMEA "Filter Code" vs. PFMEA "Classification"

### C.1 What already exists, verified live

`ClassificationScheme`/`ClassificationTerm` (one scheme, four seeded terms: Legal, Safety, Functional, Decorative) attaches to `ProductCharacteristic` only, via `ProductCharacteristic.primary_classification` (single nullable FK) — already built and exercised across Slices M, N, O, P, Q. **`ProcessCharacteristic` (the Operation-scoped control record built in Slices H/N) has no classification field of any kind today** — confirmed by direct read of its model body (`control_type`, `method`, `status`, `effectiveness`, `owner`, `reaction_plan`, but nothing classification-related). The handbook's structure — DFMEA carries an *optional, advisory* "Filter Code"; PFMEA carries the *authoritative* "Classification", determined by whether a characteristic is sensitive to manufacturing/assembly variation — has no counterpart to either half today: `ProductCharacteristic.primary_classification` is unconditionally shown wherever it appears (Slice P's register, Slice Q's Characteristics Flow), not marked "advisory," and nothing on the PFMEA/process side carries an equivalent field at all.

### C.2 Decision 1 — keep `ProductCharacteristic.primary_classification` exactly as-is; it already behaves like an advisory DFMEA-side signal

**Proposed: no change to `ProductCharacteristic` or its existing four terms.** Its current unconditional display across Slices M/N/O/P/Q is a reasonable stand-in for the handbook's optional DFMEA "Filter Code" — nothing here requires the four terms to be renamed or restricted; the handbook itself says the actual term set is organization-specific, so "Legal/Safety/Functional/Decorative" is a legitimate (if untypical) choice, not a defect.

### C.3 Decision 2 — add the missing PFMEA-side "Classification," scoped to `ProcessCharacteristic`

**Proposed: reuse the existing `ClassificationScheme`/`ClassificationTerm` models (no new taxonomy model) and add one new nullable FK, `ProcessCharacteristic.special_classification` (or similarly named), pointing at the same `ClassificationTerm` table `ProductCharacteristic` already uses.** This is one migration (one new FK column on an existing model), reusing 100% of the existing classification infrastructure rather than inventing a second one. Whether the *same four terms* (Legal/Safety/Functional/Decorative) are appropriate on the process side, or whether the process-side scheme should use different, more manufacturing-sensitivity-flavored terms (e.g. adding "Special" / "Standard" specifically, closer to the handbook's own binary framing) is a real open question — **proposed default: reuse the same scheme/terms for both**, since introducing a second scheme is more taxonomy than this increment needs, but flag this for the user's explicit confirmation since it's a genuine judgment call, not a certainty.

### C.4 Decision 3 — is `primary_classification` "advisory" vs. "authoritative" a display-only distinction, or does it need an enforced field?

The handbook's real distinction between DFMEA's Filter Code and PFMEA's Classification is partly about *governance* (Filter Code doesn't have to be shown; Classification does, and flows into Control Plans), not just a difference in column name. **Proposed for this increment: display-only.** No "required" validation is added to `ProcessCharacteristic.special_classification`, and no Control Plan concept is introduced (Control Plans don't exist anywhere in this app, and adding them is a materially larger, separate feature outside this proposal's scope). This increment only makes the *field* exist on the correct side of DFMEA/PFMEA — it does not attempt the handbook's downstream Control-Plan governance flow.

### C.5 Explicitly out of scope for Part C

No Control Plan model or page. No renaming or restriction of the existing four `ClassificationTerm` rows. No change to any of Slices M/N/O/P/Q's existing `ProductCharacteristic`-side behavior — every existing page, filter, and test involving `primary_classification` is untouched. No automatic "cascade" logic propagating a DFMEA characteristic's classification onto a related `ProcessCharacteristic` — the handbook describes a team decision (sensitivity to manufacturing/assembly variation), not a mechanical copy, so this increment leaves `special_classification` as an independently-set field, not a computed/inherited one.

---

## Summary — what each Part actually costs

| Part | New migration? | New model? | Existing data/behavior touched? |
|---|---|---|---|
| A (real S/O/D + AP) | No (JSONField, data-only) | No (new `EvaluationDefinition` rows only) | No — `classic-rpn`/`aiag-vda-ap-poc` untouched; only the `normalize_method()` default fallback changes (Decision 3, itself optional) |
| B (FMEA-MSR) | Yes — one nullable field (`RiskEvaluation.failure_scenario`) | No | No — additive `method` value, existing `FailureMode`/`FMEA` rows unaffected |
| C (Special Characteristics) | Yes — one nullable FK (`ProcessCharacteristic.special_classification`) | No | No — `ProductCharacteristic` side fully unchanged |

## Recommendation

All three are **ready for the user's per-part decision**, not yet ready for an implementation instruction — each still has at least one open sub-question (A: DFMEA-vs-PFMEA rating-table split and the fallback-method default; B: where `failure_scenario` lives and the reuse-vs-new-`fmea_type` framing; C: shared vs. separate classification scheme for the process side) that a real Codex-style implementation instruction should not silently resolve on its own. Recommended order if approving more than one: **A first** (highest conformance value, smallest footprint, no migration), **C second** (small, one migration, directly reuses existing infrastructure), **B last** (the only genuinely new capability, and the one still needing the fullest treatment — the Appendix C AP-table transcription for FMEA-MSR's own separate table hasn't been done at all yet, on top of Part A's DFMEA/PFMEA table needing the same treatment first).

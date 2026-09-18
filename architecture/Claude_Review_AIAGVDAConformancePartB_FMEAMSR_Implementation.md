# Review — AIAG & VDA Conformance, Part B (FMEA-MSR) Implementation

**Scope**: implements Part B (FMEA-MSR — Supplemental FMEA for Monitoring and System Response) from `OpenFMEA_AIAGVDAConformanceGaps_ArchitectureDecision.md`, completing the three-part "kodiraj" instruction alongside the already-delivered Parts A and C (see `Claude_Review_AIAGVDAConformancePartsAC_Implementation.md`).

This is the part the decision doc itself flagged as needing the fullest treatment, and the one previous review noted its own tables had not survived a context compaction. A fresh, dedicated research pass re-transcribed FMEA-MSR's Frequency (F), Monitoring (M), and Action Priority tables verbatim from the handbook (AIAG & VDA FMEA Handbook, 1st Ed. 2019, Chapter 4, pp. 125-153) before any code was written, per this project's standing "never approximate a table, always transcribe the real one" discipline.

---

## 1. What was built

- `fmea_evaluation/calculators.py`: a new method constant `AIAG_VDA_MSR_METHOD = "aiag-vda-msr"` and `calculate_action_priority_msr(rating)`, implementing the handbook's own separate FMEA-MSR Table AP (pp. 146-148) — structurally different from the DFMEA/PFMEA Table AP: uneven Frequency-band × Monitoring-band rectangles per Severity value, not a clean 4-band grid. Encoded as an explicit list of `(f_range, m_range) -> priority` rules per Severity value, with `RiskRating.occurrence` read as Frequency (F) and `RiskRating.detection` read as Monitoring (M) — the same "one generic 3-factor row, meaning depends on `method`" pattern the app already uses for `classic-rpn` vs. `aiag-vda-ap-poc` vs. `aiag-vda-ap`. Verified by brute-force test that all 1,000 (S, F, M) combinations resolve to a priority with no gaps, and by 33 hand-checked cases against the transcribed table spanning every Severity band.
- `models.RiskEvaluation.failure_scenario`: one new nullable/blank `CharField` with choices `non_hazardous` / `hazardous` / `mitigated` (the handbook's own labels: "Non-Hazardous", "Hazardous", "Mitigated (Effect)") — the one migration this whole three-part proposal needed (migration `0015_riskevaluation_failure_scenario.py`), exactly as flagged in the decision doc. Blank for every non-MSR evaluation.
- `fmea_app/services.evaluate_failure_mode()`: gained one new optional `failure_scenario: str = ""` keyword argument, threaded straight into the created/updated `RiskEvaluation` row. No existing caller needed to change.
- `fmea_app/forms.RiskEvaluationForm`: gained an optional `failure_scenario` choice field (default "N/A").
- `fmea_app/views.evaluate_failure()`: passes the form's `failure_scenario` through to the service.
- `fmea_app/risk_matrix.py`: `AIAG_VDA_MSR_METHOD` added to `KNOWN_METHODS`/`METHOD_LABELS`. As with Part A's new method, no other risk_matrix.py logic needed to change — the existing generic (non-`classic-rpn`) branches already handle any `"priority"`-shaped result.
- `seed_demo.py`: a fourth `EvaluationDefinition` row (`method="aiag-vda-msr"`), with `rating_scales` carrying the verbatim Frequency/Monitoring criteria text and the three Failure Scenario category descriptions, transcribed from Tables MSR2/MSR3 and section 4.4.2. One new demo `RiskEvaluation` exercises the method on the existing demo failure mode with `failure_scenario="hazardous"`.
- `fmea_detail.html` / `views.py`: the Risk Evaluation form's S/O/D labels are now "S" / "O / F" / "D / M" (a static relabel, since there is no page-reload-free way to dynamically relabel by selected method without violating the project's no-AJAX convention), plus a new optional "Failure Scenario (FMEA-MSR only)" dropdown. A second collapsible reference block, independent of the DFMEA/PFMEA one from Part A, shows the three Failure Scenario descriptions and the full Frequency/Monitoring criteria text (including the Monitoring table's own "use the least effective of the two" combination rule) whenever an `aiag-vda-msr` `EvaluationDefinition` exists — shown regardless of the FMEA's `fmea_type`, matching Decision 3 below (FMEA-MSR is not its own FMEA type; it's a lens on any existing FailureMode).

## 2. Decisions made (all as proposed in the decision doc — no deviations this time)

**Decision 1 (reuse `RiskEvaluation`/`EvaluationDefinition` plumbing) — adopted exactly.** No new model. `occurrence`/`detection` are reinterpreted as Frequency/Monitoring under `method="aiag-vda-msr"`, exactly as the decision doc proposed.

**Decision 2 (`failure_scenario` as one new nullable field) — adopted exactly**, including the decision doc's explicit acknowledgment that this is "the one migration this entire three-part proposal needs." Stored as a real column (not folded into the `result` JSONField), matching the doc's preferred alternative for queryability.

**Decision 3 (no new `fmea_type`; MSR results live against the same `FailureMode` rows) — adopted exactly.** `FMEA.FMEA_TYPE_CHOICES` is untouched. An `aiag-vda-msr` `RiskEvaluation` can be created against any existing `FailureMode`, on any FMEA, the same way `aiag-vda-ap` or `classic-rpn` evaluations can. This is the decision that keeps "PM-FMEA" (the project's own held-off maintenance/asset track, `fmea_type` never added) and "FMEA-MSR" (a `method` value on existing evaluations) unambiguously distinct in the data model — directly resolving the naming confusion flagged in the original conformance review.

**Decision 4 (narrow GUI first increment) — adopted exactly, including its explicit non-goals.** Not built, matching the decision doc's own "Not proposed for a first increment" list: no dedicated FMEA-MSR page or route, no Fault Handling Time Interval field, no Frequency exposure-time-percentage reduction UI (the rule is documented in the reference block's text but not wired into an interactive control), and — most importantly — no implementation of Handbook NOTE 1/NOTE 2 (the rule that when Monitoring=1, the *mitigated* Failure Effect's severity replaces the original Failure Effect's severity for this AP lookup, and for the parent DFMEA's own AP lookup too). This is called out explicitly in a code comment directly above `calculate_action_priority_msr()`: `RiskRating` carries one severity value with no "original vs. mitigated" distinction, so the substitution cannot be applied without scope beyond this increment's one new field. Until that is built, the calculator uses whatever severity the caller passes — this is a known, documented limitation, not a silent gap.

## 3. A transcription correction, flagged transparently

The research pass found that Table MSR3's row M=8 in the handbook's main body (p. 143) prints "the reaction ... may **riot** always occur" — a genuine typesetting/OCR artifact in the published PDF, independently confirmed against two extraction methods and against the Appendix C duplicate of the same table, which correctly prints "may **not** always occur." The corrected wording ("not") was used in `_aiag_vda_msr_rating_scales()`'s stored text rather than reproducing the source typo verbatim, since propagating a known print error into reference text shown to users would be actively misleading. This is the one place this session's data deviates character-for-character from the literal PDF text, and it is deliberate.

## 4. Explicitly out of scope (unchanged from the decision doc)

The Fault Handling Time Interval as its own tracked field. Any change to PM-FMEA's standing hold — untouched, fully separate. A standalone FMEA-MSR page or route. The Frequency exposure-time reduction rule and the Monitoring=1 severity-substitution rule (NOTE 1/NOTE 2) as active calculation logic — both are documented in reference text and code comments for a future increment, not silently dropped.

## 5. Tests

`tests/test_domain_evaluation.py`: 3 new tests — output shape/method identity confirming `occurrence`/`detection` are read as Frequency/Monitoring, a full 1,000-combination coverage sweep (no gaps in the encoded rules), and a 33-case table-accuracy test spanning every Severity band, independently derived from the transcribed table.

`tests/test_risk_matrix.py`: 4 new tests — method registration alongside the other three methods, and a dedicated query-logic test class (mirroring the existing `AiagVdaApRiskMatrixQueryLogicTests` pattern) proving method-scoped latest-evaluation lookup, band-order sorting, and page rendering all work unmodified for the new method, plus confirming `failure_scenario` round-trips through the ORM.

`tests/test_app_workflow.py`: 6 new tests — the new method and Failure Scenario field appear on the `fmea_detail` form; the MSR reference block renders (and is absent when no `aiag-vda-msr` definition exists); `evaluate_failure` saves `failure_scenario` only when submitted and leaves it blank for every other method/evaluation.

272 → 284 tests, all passing. `makemigrations --check --dry-run` confirms the one expected migration (`0015`) is already applied and nothing further is pending. `seed_demo` and its reproducibility test (`test_seed_demo_reproducibility.py`) both continue to pass unmodified against the new fourth `EvaluationDefinition` row.

## 6. Combined three-part result

All three parts of the AIAG & VDA conformance decision doc are now implemented: Part A (real S/O/D criteria + real Table AP), Part B (FMEA-MSR), and Part C (PFMEA-side Special Characteristics). 284 tests passing across this session's Parts A/B/C work (was 253 before any of it started). Every pre-existing method, field, page, and test remains byte-identical except where a new option, column, or field was inserted alongside what was already there — no `classic-rpn`, `aiag-vda-ap-poc`, `ProductCharacteristic.primary_classification`, or existing page behavior was removed, renamed, or had its semantics changed, per the user's governing "keep everything that already exists, only add" instruction throughout.

# Review — AIAG & VDA Conformance, Parts A & C Implementation

**Scope**: implements Part A (real Severity/Occurrence/Detection criteria text + a real Action Priority table) and Part C (Special Characteristics: PFMEA-side Classification on `ProcessCharacteristic`) from `OpenFMEA_AIAGVDAConformanceGaps_ArchitectureDecision.md`, following the user's "kodiraj" instruction. Part B (FMEA-MSR) is deliberately not included in this review — see the closing note.

Both parts follow the standing "keep everything that already exists, only add" constraint: nothing pre-existing was removed, renamed, or had its behavior changed in place, except one documented, narrow exception in Part A (Decision 3 below).

---

## Part A — Real AIAG & VDA Table AP

### 1. What was built

- `fmea_evaluation/calculators.py`: a new method constant `AIAG_VDA_AP_METHOD = "aiag-vda-ap"` and a new function `calculate_action_priority_aiag_vda(rating)`, implementing the verbatim 69-row Table AP lookup (Severity-band → Occurrence-band → Detection-band → High/Medium/Low) transcribed from Appendix C of the AIAG & VDA FMEA Handbook, 1st Ed. 2019. This is genuinely the handbook's table, not an approximation: every band boundary and every one of the table's cells was hand-verified against the transcribed source before being encoded, and a dedicated test (`test_aiag_vda_ap_table_matches_the_handbook_table_ap_exactly`) checks 33 cells spanning all four Severity bands and all Detection bands, independently re-derived from the table rather than copied from the implementation.
- `_action_priority_band()` / `calculate_action_priority()` (the existing PoC) and `CLASSIC_RPN_METHOD` / `calculate_classic_rpn()` are **completely untouched** — confirmed by re-running their existing tests unchanged and by diffing that no existing line was edited, only appended to.
- `calculate()`'s dispatch gained one new `if method == AIAG_VDA_AP_METHOD` branch; the other two branches are unmodified.
- `fmea_app/risk_matrix.py`: `AIAG_VDA_AP_METHOD` added to `KNOWN_METHODS` and `METHOD_LABELS` ("AIAG & VDA Action Priority (Table AP)"). No other logic needed to change — `top_evaluations()`'s existing generic "else" branch (band-order sort via `result.get("priority")`) already works correctly for the new method's output shape, the same way it already worked for the PoC method.
- `seed_demo.py`: a third `EvaluationDefinition` row (`method="aiag-vda-ap"`) alongside the existing `classic-rpn` and `aiag-vda-ap-poc` rows — all three now selectable side by side. Its `rating_scales` carries the verbatim Severity/Occurrence/Detection criteria text for **both** DFMEA and PFMEA, transcribed from Tables D1-D3 and P1-P3 (including PFMEA's three-perspective severity: Your Plant / Ship-to Plant / End User), plus the DFMEA alternate Occurrence scales are *not* included (out of scope, noted below). One new demo `RiskEvaluation` row exercises the new method on the existing demo failure mode.
- `fmea_detail.html` / `views.py`: the Risk Evaluation form gained a collapsible (`<details>`, no JS) "AIAG & VDA rating criteria" reference block, showing the real Severity/Occurrence/Detection band text. It automatically switches between DFMEA wording and PFMEA wording based on the FMEA's own `fmea_type` (`"process"` → PFMEA text, everything else → DFMEA text) — this is real, existing data driving the choice, not a guess.
- No migration: `rating_scales`/`configuration` are pre-existing `JSONField`s, so this entire part is data + code, matching the decision doc's own framing.

### 2. Decisions made (and deviations from the decision doc, flagged transparently)

**Decision 1 (criteria text) — adopted with a simplification.** The decision doc's open sub-question proposed storing DFMEA and PFMEA wording as **two separate `EvaluationDefinition` rows** (`aiag-vda-dfmea` / `aiag-vda-pfmea`). This was **not** what got built. Instead, a single `EvaluationDefinition` (method `aiag-vda-ap`) stores both wordings as two sub-keys (`rating_scales.dfmea` / `rating_scales.pfmea`) of one row.

*Why this is a deliberate deviation, not an oversight*: the subagent transcription task explicitly confirmed the Table AP lookup itself is **cell-for-cell identical** between DFMEA and PFMEA — only the reference wording differs, not the calculation. Two methods would have meant either two near-duplicate calculator functions (violating single-source-of-truth) or one function serving two methods (which defeats the point of having two method rows). One method with two text variants keeps the calculation single-sourced and lets the GUI pick the right wording from data already on hand (`fmea.fmea_type`), with no method-selection ambiguity for a method-agnostic view like the Risk Matrix.

**Decision 2 (new method, not overwriting the PoC) — adopted as proposed.** `aiag-vda-ap-poc` and `classic-rpn` are unchanged; `aiag-vda-ap` is additive.

**Decision 3 (`normalize_method()` default fallback) — deviated from the decision doc's proposed default.** The decision doc proposed switching the fallback from `classic-rpn` to the new real method. **This was not done** — `normalize_method()` still falls back to `classic-rpn` for `None`/unrecognized values, exactly as before Part A.

*Why*: switching the default changes what every method-agnostic view (Risk Matrix, "Top High Risk Items", dashboards) shows by default for every existing FMEA, with no user action — that is a behavior change to existing data's *presentation*, not a pure addition, and sits uneasily with "keep everything that already exists." The new method is fully available and clearly labeled, one click away, but nothing currently pointed at `classic-rpn` silently starts showing something else. This is called out explicitly in code (`risk_matrix.py`'s `normalize_method()` docstring already documented the fallback; a test - `test_normalize_method_default_fallback_is_still_classic_rpn` - locks this decision in place so a future change here is deliberate, not an accidental import-order side effect. If the user's judgment differs from mine on this specific call, flipping the fallback is a one-line change with no migration.

### 3. Explicitly out of scope (unchanged from the decision doc)

No change to `RiskEvaluation`'s schema. No removal of `classic-rpn` or `aiag-vda-ap-poc`. No change to the Risk Matrix's grid axes or `classify_severity_occurrence`. The DFMEA alternate Occurrence scales (Incidents per Thousand / Time Based) transcribed by the research subagent were **not** wired into `rating_scales` — only the primary qualitative Occurrence scale is stored, since the decision doc never proposed the alternates and adding them would be new scope, not implementation of an existing decision.

### 4. Tests

`tests/test_domain_evaluation.py`: 4 new tests on the calculator directly (framework-free, matching the file's existing style) — output shape/method identity, S=1 and O=1 special-cased to always "low", and a 33-case table-accuracy test spanning every Severity band.

`tests/test_risk_matrix.py`: 2 new test classes — method registration (`KNOWN_METHODS`/`METHOD_LABELS`/`normalize_method` behavior, including the fallback-stays-classic-rpn decision) and generic query-logic reuse (latest-evaluation scoping, band-order sorting, the Risk Matrix page rendering the new method without error).

`tests/test_app_workflow.py`: 3 new tests on `fmea_detail` — the new method appears as a selectable option, and the rating-reference block renders the correct wording (PFMEA vs. DFMEA) for the correct FMEA type.

253 → 266 tests, all passing; `makemigrations --check --dry-run` confirms no migration needed for Part A.

---

## Part C — PFMEA-side Special Characteristics Classification

### 1. What was built

- `models.ProcessCharacteristic.special_classification`: a new nullable FK to the **existing** `ClassificationTerm` table (the same one `ProductCharacteristic.primary_classification` already uses), `on_delete=SET_NULL`. One migration (`0014_processcharacteristic_special_classification.py`), additive only.
- `domain/fmea_domain/entities.py`: `ProcessCharacteristic.special_classification_id` added to the framework-free domain dataclass, threaded through `models.ProcessCharacteristic.to_domain()` — mirrors `ProductCharacteristic.primary_classification_id`'s existing pattern exactly. This also means OFEF export (`fmea_importexport/ofef.py`) picks it up automatically, since export serializes the domain dataclass generically.
- `admin.py`: `special_classification` added to `ProcessCharacteristicAdmin`'s `list_display`/`list_filter`.
- `forms.ProcessCharacteristicForm`: `special_classification` added as an optional field (mirrors `owner`'s optional-FK pattern), with its queryset ordered by name.
- GUI: the "New Process Characteristic" form, the Process Characteristics list/detail-panel page (Slice N), and the standalone Process Characteristic detail page all now show "Special Classification" — reusing the same `<span class="status">` badge convention Slice Q already established for `ProductCharacteristic.primary_classification`, so **zero new CSS** was needed for this. All three relevant querysets gained `select_related("special_classification")` to keep this a single additional join, not per-row queries.

### 2. Decisions made

**Decision 1 (`ProductCharacteristic.primary_classification` unchanged) — adopted exactly.** No change to any Slice M/N/O/P/Q behavior involving it.

**Decision 2 (reuse `ClassificationScheme`/`ClassificationTerm`, scoped to `ProcessCharacteristic`) — adopted exactly**, including the proposed default of reusing the same scheme/terms rather than introducing a manufacturing-sensitivity-flavored second scheme. Nothing stops an org from adding "Special"/"Standard" terms to the existing scheme later; this increment doesn't force that choice.

**Decision 3 (display-only, no governance) — adopted exactly.** No required-field validation, no Control Plan concept introduced.

### 3. Explicitly out of scope (unchanged from the decision doc)

No Control Plan model or page. No renaming/restriction of the four existing `ClassificationTerm` rows. No cascade/inheritance logic from a `ProductCharacteristic`'s classification onto a related `ProcessCharacteristic` — confirmed by a dedicated test (`test_deleting_the_classification_term_sets_the_field_to_null_not_cascade`) that also proves the FK is `SET_NULL`, not `CASCADE` — deleting a classification term does not delete the characteristic that referenced it.

### 4. Tests

`tests/test_process_characteristic_control_fields.py`: one new test class (`ProcessCharacteristicSpecialClassificationTests`, 7 tests) plus one assertion added to the existing pre-migration-defaults test. Covers: default-None on existing rows, set/read via the shared `ClassificationTerm` table, `SET_NULL` behavior, `to_domain()` propagation, form accept/optional behavior, and GUI rendering on both the list+panel page and the standalone detail page.

266 → 272 tests, all passing; `makemigrations --check --dry-run` confirms the one expected migration is already applied and nothing further is pending.

---

## Combined result

272 tests passing (was 253 before this session's Part A/C work; 253 → 266 → 272). No existing test was modified to make it pass — only new tests were added and one new assertion appended to a pre-existing test. Every file changed is additive in the sense the user asked for: existing methods, existing fields, existing pages, and existing tests are all byte-identical to before except where a new `<th>`/`<td>`/form field/admin column/select_related was inserted alongside what was already there.

## Note on Part B (FMEA-MSR)

Part B is **not** included in this delivery. Its own S/F/M criteria text and its separate 39-row Action Priority table were transcribed by an earlier research pass in this session, but that transcription lived only in conversation context and did not survive a context-window compaction that occurred before this implementation pass began — unlike Part A's DFMEA/PFMEA tables, which were re-transcribed fresh from the source PDF specifically for this implementation and are fully verified. Rather than encode Part B's tables from memory (which would violate this project's standing "never approximate a table, always transcribe the real one" discipline - the exact failure mode this whole conformance effort exists to fix), Part B needs one more research pass against the handbook PDF before it can be implemented responsibly. Parts A and C are complete, tested, and delivered now; Part B is next, pending that re-transcription.

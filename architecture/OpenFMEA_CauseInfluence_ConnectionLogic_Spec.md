# Open-FMEA — CauseInfluence Connection/Linking Logic Specification

Status: design specification for `fmea_domain/rules.py` transition-validation functions consumed by `Codex_Instruction_CauseInfluence_CauseCategoryScheme_IshikawaBackend_Slice.md`. Not a standalone implementation instruction — it is that instruction's authority for Commit 1's rule functions and Commit 4's transition endpoint. Implement this document precisely.

Author: Claude, acting as Open-FMEA Technical Architect.

## Why this exists

`CauseInfluence.status` is the whole point of the entity — it is what turns a raw "this might be related" observation into a governed investigation trail (Section 5, 8, 21 of `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md`). Without an explicit set of rules for which transitions are legal, from where, to where, and what each requires, "status" degenerates into a free-text label anyone can set to anything — which would silently reopen the same problem the review flagged for AI output: an unearned claim of certainty. This document is the rule set that keeps status meaningful.

## The status vocabulary (unchanged, restated for reference)

`SUSPECTED → POSSIBLE → CORRELATED → EXPERIMENTALLY_SUPPORTED → CONFIRMED_ROOT_CAUSE`, with `REJECTED` reachable from any non-terminal state. `CONFIRMED_ROOT_CAUSE` and `REJECTED` are terminal — no further transition out of either in this slice (reopening a rejected or confirmed investigation is a future decision, not built here; if a user needs to reopen one, the correct action in this slice is to create a new `CauseInfluence`, not to un-terminate the old one).

## Transition rules

1. **Forward progression is one step at a time by default, but skipping ahead is allowed with justification.** A transition from `SUSPECTED` directly to `CONFIRMED_ROOT_CAUSE` is not rejected outright — real investigations sometimes have decisive evidence immediately — but any transition that skips over `CORRELATED` and `EXPERIMENTALLY_SUPPORTED` (i.e., a jump of more than one step forward) requires a non-empty `review_note` explaining why the intermediate evidence gathering was skipped. A single-step forward transition (e.g. `SUSPECTED → POSSIBLE`) never requires a note, though one is always allowed.
2. **No backward transition among the five non-terminal, non-rejected states.** `CORRELATED → POSSIBLE` is illegal — evidence-strength status does not go backward; if new evidence contradicts an edge, the correct action is `REJECTED`, not demotion. (This deliberately does not model "this looked more certain than it was" as a demotion — it models it as rejection-and-recreate, keeping the audit trail honest: a demoted-then-reconfirmed edge would otherwise hide the fact that the earlier confidence was wrong.)
3. **`REJECTED` is reachable from `SUSPECTED`, `POSSIBLE`, `CORRELATED`, or `EXPERIMENTALLY_SUPPORTED`**, always requires a non-empty `review_note` (why it was rejected), and is terminal.
4. **Reaching `CONFIRMED_ROOT_CAUSE` requires the edge's `target_type` to be `FailureCause`, not `FailureMode`.** This is the promotion rule from Section 5 of the architecture review: a candidate cause targets a `FailureMode` while still unconfirmed; confirming it requires it to already point at (or be retargeted to, via the API's `failure_cause_stable_id` parameter — Section 6 of the Codex instruction) a real `FailureCause` record. The transition endpoint must perform this retarget-then-confirm as one atomic operation: if `target_type` is currently `FailureMode`, the request must supply `failure_cause_stable_id`, and the service both updates `target_id`/`target_type` to that `FailureCause` and sets `status=CONFIRMED_ROOT_CAUSE` in the same transaction. A request to confirm without supplying this when the current target is a `FailureMode` is rejected with a specific error naming the missing field — never silently left at the previous status, never silently confirmed against the wrong target.
5. **`CONFIRMED_ROOT_CAUSE` requires `review_note` non-empty.** A root-cause confirmation with no stated reasoning is rejected — this mirrors the "always advisory, never a bare assertion" principle already established for AI output, applied here to human review actions carrying equivalent weight.
6. **`EXPERIMENTALLY_SUPPORTED` requires at least one `evidence_ids` entry OR a non-empty `review_note`.** Reaching this status is a claim that something concrete backs the correlation — the rule accepts either a linked `Evidence` reference or, until the `Evidence`-linking UI is built (Decision 5, deferred), a written note describing the experiment/test, so the rule is enforceable today without blocking on unbuilt UI.
7. **No transition changes `source_id`/`source_type`.** Only `target_id`/`target_type` may change, and only in the specific `FailureMode → FailureCause` retarget described in rule 4 — a `CauseInfluence`'s source is fixed at creation; if the true source turns out to be wrong, the correct action is to reject this edge and create a new one, not to mutate the source of an existing investigation trail.
8. **`cause_category_id` may be set or changed on any transition, including no-op transitions (re-saving the current status).** Recategorizing which 5M+E bone an edge belongs to is not itself an evidentiary claim and carries no status implication.
9. **Every transition is attributed.** `reviewed_by`/`reviewed_at` are set on every transition, matching the pattern already established for `ImportCandidateRecord`/`FmeaRowGroup` review actions — no transition happens without an identified actor (or anonymous, if the deployment allows unauthenticated review, matching the existing `_user_or_none` pattern already used elsewhere in this codebase).

## Function shape (for `fmea_domain/rules.py`)

Mirror the existing style already established in that file (pure functions, no Django import, raising a domain-specific exception rather than returning a bare boolean, so the specific violated rule is always visible to the caller — do not restructure any existing function in that file to accommodate this). Proposed shape:

```python
class CauseInfluenceTransitionError(Exception):
    """Raised when a requested CauseInfluence status transition violates a rule."""


def validate_cause_influence_transition(
    *,
    current_status: CauseInfluenceStatus,
    new_status: CauseInfluenceStatus,
    current_target_type: str,
    review_note: str,
    evidence_ids: tuple[str, ...],
    retarget_failure_cause_stable_id: str | None,
) -> None:
    """Raises CauseInfluenceTransitionError with a specific reason if the
    transition is not allowed. Returns None (does not mutate anything —
    the caller applies the transition only after this raises nothing)."""
```

This function is the single source of truth both `test_cause_influence_rules.py` and the transition endpoint (Section 6 of the Codex instruction) must call — the endpoint must not duplicate any of these checks inline.

## Worked examples

- `SUSPECTED → POSSIBLE`, no note: **legal.**
- `SUSPECTED → CORRELATED`, no note: **illegal** — two-step jump without justification (rule 1).
- `SUSPECTED → CORRELATED`, `review_note="Confirmed by cross-referencing three prior complaint records with matching lot numbers."`: **legal.**
- `CORRELATED → POSSIBLE`: **illegal always** — backward transition (rule 2), no note can make this legal.
- `POSSIBLE → REJECTED`, no note: **illegal** — rejection requires a note (rule 3).
- `EXPERIMENTALLY_SUPPORTED → CONFIRMED_ROOT_CAUSE`, current target is a `FailureMode`, no `retarget_failure_cause_stable_id` supplied: **illegal**, error names the missing field (rule 4).
- Same transition, `retarget_failure_cause_stable_id` supplied, `review_note` empty: **illegal** — confirmation requires a note regardless of retarget (rule 5).
- Same transition, both supplied: **legal**, and the service performs the retarget and the status change together.
- `CORRELATED → EXPERIMENTALLY_SUPPORTED`, no `evidence_ids`, `review_note="Ran a controlled reproduction on the affected lot, 4/4 units failed identically."`: **legal** (rule 6, note substitutes for evidence link).
- `POSSIBLE → CONFIRMED_ROOT_CAUSE` (two-step jump), target already a `FailureCause`, `review_note` present: **legal** — this is an allowed skip-ahead (rule 1) combined with the confirmation requirements (rules 4/5), both satisfied.

## Verification

Not independently testable without the entity/model code from the Codex instruction existing first — this document's own worked-example table above is the acceptance basis for `test_cause_influence_rules.py`: every example listed must appear as a test case, legal cases asserting no exception, illegal cases asserting `CauseInfluenceTransitionError` with a message that names the specific violated rule.

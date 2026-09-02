from __future__ import annotations

import unittest

from fmea_domain import (
    CauseInfluenceStatus,
    CauseInfluenceTransitionError,
    validate_cause_influence_transition,
)


class CauseInfluenceRulesTests(unittest.TestCase):
    def test_suspected_to_possible_without_note_is_legal(self):
        self.assert_transition_ok(
            CauseInfluenceStatus.SUSPECTED,
            CauseInfluenceStatus.POSSIBLE,
        )

    def test_skip_to_correlated_requires_note(self):
        self.assert_transition_error(
            CauseInfluenceStatus.SUSPECTED,
            CauseInfluenceStatus.CORRELATED,
            "skipping",
        )

    def test_skip_to_correlated_with_note_is_legal(self):
        self.assert_transition_ok(
            CauseInfluenceStatus.SUSPECTED,
            CauseInfluenceStatus.CORRELATED,
            review_note="Confirmed by cross-referencing three prior complaint records.",
        )

    def test_backward_transition_is_illegal(self):
        self.assert_transition_error(
            CauseInfluenceStatus.CORRELATED,
            CauseInfluenceStatus.POSSIBLE,
            "Backward",
        )

    def test_rejected_requires_note(self):
        self.assert_transition_error(
            CauseInfluenceStatus.POSSIBLE,
            CauseInfluenceStatus.REJECTED,
            "review_note",
        )

    def test_rejected_with_note_is_legal(self):
        self.assert_transition_ok(
            CauseInfluenceStatus.POSSIBLE,
            CauseInfluenceStatus.REJECTED,
            review_note="Cause disproved by teardown.",
        )

    def test_terminal_status_has_no_outgoing_transition(self):
        self.assert_transition_error(
            CauseInfluenceStatus.REJECTED,
            CauseInfluenceStatus.POSSIBLE,
            "terminal",
        )
        self.assert_transition_error(
            CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE,
            CauseInfluenceStatus.REJECTED,
            "terminal",
            current_target_type="FailureCause",
        )

    def test_confirming_failure_mode_target_requires_retarget_failure_cause_id(self):
        self.assert_transition_error(
            CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED,
            CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE,
            "failure_cause_stable_id",
            review_note="Controlled reproduction confirmed the cause.",
        )

    def test_confirming_requires_note_even_with_retarget(self):
        self.assert_transition_error(
            CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED,
            CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE,
            "review_note",
            retarget_failure_cause_stable_id="failure-cause:seal-nicked",
        )

    def test_confirming_with_retarget_and_note_is_legal(self):
        self.assert_transition_ok(
            CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED,
            CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE,
            review_note="Controlled reproduction confirmed the cause.",
            retarget_failure_cause_stable_id="failure-cause:seal-nicked",
        )

    def test_experimentally_supported_requires_evidence_or_note(self):
        self.assert_transition_error(
            CauseInfluenceStatus.CORRELATED,
            CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED,
            "evidence_ids",
        )

    def test_experimentally_supported_with_note_is_legal(self):
        self.assert_transition_ok(
            CauseInfluenceStatus.CORRELATED,
            CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED,
            review_note="Ran a controlled reproduction on the affected lot.",
        )

    def test_possible_to_confirmed_targeting_failure_cause_with_note_is_legal(self):
        self.assert_transition_ok(
            CauseInfluenceStatus.POSSIBLE,
            CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE,
            current_target_type="FailureCause",
            review_note="Decisive inspection evidence was already available.",
        )

    def test_noop_transition_is_legal_for_recategorization(self):
        self.assert_transition_ok(
            CauseInfluenceStatus.POSSIBLE,
            CauseInfluenceStatus.POSSIBLE,
        )

    def assert_transition_ok(
        self,
        current_status: CauseInfluenceStatus,
        new_status: CauseInfluenceStatus,
        *,
        current_target_type: str = "FailureMode",
        review_note: str = "",
        evidence_ids: tuple[str, ...] = (),
        retarget_failure_cause_stable_id: str | None = None,
    ) -> None:
        validate_cause_influence_transition(
            current_status=current_status,
            new_status=new_status,
            current_target_type=current_target_type,
            review_note=review_note,
            evidence_ids=evidence_ids,
            retarget_failure_cause_stable_id=retarget_failure_cause_stable_id,
        )

    def assert_transition_error(
        self,
        current_status: CauseInfluenceStatus,
        new_status: CauseInfluenceStatus,
        pattern: str,
        *,
        current_target_type: str = "FailureMode",
        review_note: str = "",
        evidence_ids: tuple[str, ...] = (),
        retarget_failure_cause_stable_id: str | None = None,
    ) -> None:
        with self.assertRaisesRegex(CauseInfluenceTransitionError, pattern):
            self.assert_transition_ok(
                current_status,
                new_status,
                current_target_type=current_target_type,
                review_note=review_note,
                evidence_ids=evidence_ids,
                retarget_failure_cause_stable_id=retarget_failure_cause_stable_id,
            )


if __name__ == "__main__":
    unittest.main()

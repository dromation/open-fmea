from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domain"))
sys.path.insert(0, str(ROOT / "django_app"))

from fmea_domain import (  # noqa: E402
    DomainValidationError,
    FMEALifecycle,
    RiskRating,
    assert_valid_lifecycle_transition,
    validate_rating,
)
from fmea_evaluation import (  # noqa: E402
    ACTION_PRIORITY_POC_METHOD,
    CLASSIC_RPN_METHOD,
    calculate,
)


class DomainEvaluationTests(unittest.TestCase):
    def test_classic_rpn_calculates_score_and_classification(self):
        result = calculate(
            CLASSIC_RPN_METHOD,
            RiskRating(severity=9, occurrence=4, detection=5),
        )

        self.assertEqual(result.output["score"], 180)
        self.assertEqual(result.output["classification"], "medium")

    def test_action_priority_variant_is_pluggable(self):
        result = calculate(
            ACTION_PRIORITY_POC_METHOD,
            RiskRating(severity=9, occurrence=4, detection=5),
        )

        self.assertEqual(result.output["priority"], "high")
        self.assertEqual(result.output["variant"], "configurable-poc-matrix")

    def test_rating_validation_rejects_out_of_range_values(self):
        with self.assertRaises(DomainValidationError):
            validate_rating(RiskRating(severity=11, occurrence=4, detection=5))

    def test_lifecycle_transition_rules_are_explicit(self):
        assert_valid_lifecycle_transition(
            FMEALifecycle.DRAFT,
            FMEALifecycle.IN_REVIEW,
        )
        with self.assertRaises(DomainValidationError):
            assert_valid_lifecycle_transition(
                FMEALifecycle.APPROVED,
                FMEALifecycle.DRAFT,
            )


if __name__ == "__main__":
    unittest.main()

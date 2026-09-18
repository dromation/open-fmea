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
    AIAG_VDA_AP_METHOD,
    AIAG_VDA_MSR_METHOD,
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

    def test_aiag_vda_ap_is_a_distinct_real_method_not_a_replacement_for_the_poc(self):
        # The PoC method and its threshold-based band function are untouched
        # by adding the real handbook table under a different method name.
        result = calculate(
            AIAG_VDA_AP_METHOD,
            RiskRating(severity=9, occurrence=4, detection=5),
        )
        self.assertEqual(result.method, AIAG_VDA_AP_METHOD)
        self.assertEqual(result.output["variant"], "aiag-vda-handbook-table-ap")
        self.assertIn("priority", result.output)

        poc_result = calculate(
            ACTION_PRIORITY_POC_METHOD,
            RiskRating(severity=9, occurrence=4, detection=5),
        )
        self.assertEqual(poc_result.output["variant"], "configurable-poc-matrix")

    def test_aiag_vda_ap_severity_one_is_always_low_regardless_of_occurrence_or_detection(self):
        for occurrence in (1, 2, 5, 10):
            for detection in (1, 4, 6, 10):
                result = calculate(
                    AIAG_VDA_AP_METHOD,
                    RiskRating(severity=1, occurrence=occurrence, detection=detection),
                )
                self.assertEqual(result.output["priority"], "low")

    def test_aiag_vda_ap_occurrence_one_is_always_low_regardless_of_severity_or_detection(self):
        for severity in (1, 3, 6, 8, 10):
            for detection in (1, 4, 6, 10):
                result = calculate(
                    AIAG_VDA_AP_METHOD,
                    RiskRating(severity=severity, occurrence=1, detection=detection),
                )
                self.assertEqual(result.output["priority"], "low")

    def test_aiag_vda_ap_table_matches_the_handbook_table_ap_exactly(self):
        # Every case below is a direct transcription check against Table AP
        # (AIAG & VDA FMEA Handbook, 1st Ed. 2019, Appendix C), not a
        # re-derivation of the implementation's own banding logic - each
        # (severity, occurrence, detection) exercises a specific handbook
        # row/column/cell, including every S-band/O-band boundary value.
        cases = [
            # S = 9-10 row
            ((10, 10, 10), "high"), ((9, 8, 1), "high"),
            ((10, 10, 1), "high"), ((10, 6, 10), "high"),
            ((9, 6, 1), "high"), ((10, 4, 10), "high"),
            ((9, 4, 1), "medium"), ((10, 2, 10), "high"),
            ((10, 2, 6), "medium"), ((9, 3, 4), "low"),
            ((10, 2, 1), "low"),
            # S = 7-8 row
            ((8, 10, 10), "high"), ((7, 8, 1), "high"),
            ((8, 6, 10), "high"), ((7, 6, 1), "medium"),
            ((8, 4, 10), "high"), ((7, 4, 6), "medium"),
            ((8, 4, 1), "medium"), ((7, 2, 10), "medium"),
            ((8, 2, 6), "medium"), ((7, 2, 4), "low"),
            ((8, 2, 1), "low"),
            # S = 4-6 row
            ((6, 10, 10), "high"), ((4, 8, 1), "medium"),
            ((5, 6, 10), "medium"), ((6, 6, 1), "low"),
            ((4, 4, 10), "medium"), ((6, 4, 6), "low"),
            ((5, 4, 1), "low"), ((4, 2, 10), "low"),
            ((6, 2, 1), "low"),
            # S = 2-3 row
            ((3, 10, 10), "medium"), ((2, 8, 1), "low"),
            ((3, 6, 10), "low"), ((2, 4, 10), "low"),
            ((3, 2, 10), "low"), ((2, 2, 1), "low"),
        ]
        for (severity, occurrence, detection), expected in cases:
            with self.subTest(severity=severity, occurrence=occurrence, detection=detection):
                result = calculate(
                    AIAG_VDA_AP_METHOD,
                    RiskRating(severity=severity, occurrence=occurrence, detection=detection),
                )
                self.assertEqual(result.output["priority"], expected)

    def test_aiag_vda_msr_reuses_occurrence_and_detection_as_frequency_and_monitoring(self):
        # rating.occurrence is read as Frequency (F); rating.detection is
        # read as Monitoring (M) - a distinct method from aiag-vda-ap, whose
        # occurrence/detection instead mean Occurrence/Detection.
        result = calculate(
            AIAG_VDA_MSR_METHOD,
            RiskRating(severity=9, occurrence=4, detection=5),
        )
        self.assertEqual(result.method, AIAG_VDA_MSR_METHOD)
        self.assertEqual(result.output["variant"], "aiag-vda-msr-handbook-table-ap")
        self.assertEqual(result.output["priority"], "high")

    def test_aiag_vda_msr_table_covers_every_severity_frequency_monitoring_combination(self):
        # The handbook's own table is built from uneven Frequency/Monitoring
        # band rectangles per Severity value - this proves the encoded rules
        # fully partition all 1000 (S, F, M) combinations with no gaps.
        for severity in range(1, 11):
            for frequency in range(1, 11):
                for monitoring in range(1, 11):
                    result = calculate(
                        AIAG_VDA_MSR_METHOD,
                        RiskRating(severity=severity, occurrence=frequency, detection=monitoring),
                    )
                    self.assertIn(result.output["priority"], ("high", "medium", "low"))

    def test_aiag_vda_msr_table_matches_the_handbook_table_ap_exactly(self):
        # Each case is a direct transcription check against the FMEA-MSR
        # Table AP (Handbook Ch. 4, pp. 146-148), covering every Severity
        # band and every Frequency/Monitoring band boundary within it.
        cases = [
            # S = 10
            ((10, 10, 10), "high"), ((10, 5, 1), "high"),
            ((10, 4, 10), "high"), ((10, 4, 2), "high"), ((10, 4, 1), "medium"),
            ((10, 3, 4), "high"), ((10, 3, 2), "medium"), ((10, 3, 1), "low"),
            ((10, 2, 4), "medium"), ((10, 2, 3), "low"), ((10, 1, 10), "low"),
            # S = 9
            ((9, 10, 1), "high"), ((9, 4, 1), "high"),
            ((9, 3, 2), "high"), ((9, 3, 1), "low"), ((9, 1, 10), "low"),
            # S = 7-8
            ((8, 10, 1), "high"), ((7, 5, 5), "high"), ((8, 5, 4), "medium"),
            ((7, 4, 7), "high"), ((8, 4, 6), "medium"), ((7, 4, 3), "low"),
            ((8, 3, 9), "high"), ((7, 3, 8), "medium"), ((8, 3, 6), "low"),
            ((7, 2, 7), "medium"), ((8, 2, 6), "low"), ((7, 1, 10), "low"),
            # S = 4-6
            ((6, 10, 1), "high"), ((5, 6, 10), "high"), ((4, 6, 5), "medium"),
            ((6, 4, 10), "medium"), ((5, 4, 8), "medium"), ((4, 4, 6), "low"),
            ((6, 2, 9), "medium"), ((5, 2, 6), "low"), ((4, 1, 10), "low"),
            # S = 2-3
            ((3, 10, 1), "high"), ((2, 6, 10), "medium"), ((3, 6, 6), "low"),
            ((2, 4, 1), "low"), ((3, 1, 10), "low"),
            # S = 1
            ((1, 10, 10), "low"), ((1, 1, 1), "low"),
        ]
        for (severity, frequency, monitoring), expected in cases:
            with self.subTest(severity=severity, frequency=frequency, monitoring=monitoring):
                result = calculate(
                    AIAG_VDA_MSR_METHOD,
                    RiskRating(severity=severity, occurrence=frequency, detection=monitoring),
                )
                self.assertEqual(result.output["priority"], expected)

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

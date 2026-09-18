from __future__ import annotations

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from fmea_app import models
from fmea_app import risk_matrix
from fmea_app.services import evaluate_failure_mode
from fmea_evaluation import (
    ACTION_PRIORITY_POC_METHOD,
    AIAG_VDA_AP_METHOD,
    AIAG_VDA_MSR_METHOD,
    CLASSIC_RPN_METHOD,
    classify_severity_occurrence,
)


class ClassifySeverityOccurrenceTests(TestCase):
    def test_bands_match_the_reviewed_thresholds_exactly(self):
        # <=8 low, 9-24 medium, 25-48 high, >48 very_high
        self.assertEqual(classify_severity_occurrence(2, 4), "low")  # 8
        self.assertEqual(classify_severity_occurrence(3, 3), "medium")  # 9
        self.assertEqual(classify_severity_occurrence(4, 6), "medium")  # 24
        self.assertEqual(classify_severity_occurrence(5, 5), "high")  # 25
        self.assertEqual(classify_severity_occurrence(6, 8), "high")  # 48
        self.assertEqual(classify_severity_occurrence(7, 7), "very_high")  # 49
        self.assertEqual(classify_severity_occurrence(10, 10), "very_high")  # 100

    def test_function_signature_has_no_detection_input(self):
        # Cell placement is severity x occurrence only - detection is not
        # even a parameter, let alone used to place a cell.
        self.assertEqual(classify_severity_occurrence.__code__.co_varnames[:2], ("severity", "occurrence"))
        self.assertEqual(classify_severity_occurrence.__code__.co_argcount, 2)


class _RiskMatrixFixture:
    """Shared seed data: setUp() belongs to each TestCase subclass so this
    mixin is not itself a TestCase and its test-shaped names never run
    twice."""

    def _seed_risk_matrix_fixture(self) -> None:
        self.classic_definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:risk-matrix-classic-rpn",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        self.ap_definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:risk-matrix-aiag-vda-ap-poc",
            method=ACTION_PRIORITY_POC_METHOD,
            name="AIAG-VDA Action Priority (PoC)",
        )
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:risk-matrix",
            name="Risk Matrix FMEA",
        )

        # Failure mode with evaluations under BOTH methods, at different
        # evaluated_at times - proves method-filtering uses "most recent
        # under that specific method", not "most recent overall".
        self.fm_both = models.FailureMode.objects.create(
            stable_id="fm:risk-matrix-both-methods",
            fmea=self.fmea,
            name="Both-method failure mode",
        )
        now = timezone.now()
        evaluate_failure_mode(
            failure_mode=self.fm_both,
            definition=self.classic_definition,
            severity=9,
            occurrence=4,
            detection=5,
            stable_id="riskeval:both-classic-older",
            evaluated_at=now - timedelta(days=2),
        )
        evaluate_failure_mode(
            failure_mode=self.fm_both,
            definition=self.ap_definition,
            severity=9,
            occurrence=8,
            detection=7,
            stable_id="riskeval:both-ap-newer",
            evaluated_at=now,
        )

        # Failure mode with only a classic-rpn evaluation.
        self.fm_classic_only = models.FailureMode.objects.create(
            stable_id="fm:risk-matrix-classic-only",
            fmea=self.fmea,
            name="Classic-only failure mode",
        )
        evaluate_failure_mode(
            failure_mode=self.fm_classic_only,
            definition=self.classic_definition,
            severity=2,
            occurrence=2,
            detection=2,
            stable_id="riskeval:classic-only",
            evaluated_at=now,
        )


class RiskMatrixQueryLogicTests(_RiskMatrixFixture, TestCase):
    def setUp(self) -> None:
        self._seed_risk_matrix_fixture()

    def test_latest_evaluations_by_method_returns_distinct_sets(self):
        classic = risk_matrix.latest_evaluations_by_method(CLASSIC_RPN_METHOD)
        ap = risk_matrix.latest_evaluations_by_method(ACTION_PRIORITY_POC_METHOD)

        self.assertEqual(set(classic.keys()), {self.fm_both.stable_id, self.fm_classic_only.stable_id})
        self.assertEqual(set(ap.keys()), {self.fm_both.stable_id})

        # fm_both's classic-rpn placement uses its classic-rpn evaluation
        # (severity 9, occurrence 4), not its more recent AP evaluation
        # (severity 9, occurrence 8) - method-specific "most recent", not
        # "most recent overall".
        classic_eval = classic[self.fm_both.stable_id]
        ap_eval = ap[self.fm_both.stable_id]
        self.assertEqual((classic_eval.severity, classic_eval.occurrence), (9, 4))
        self.assertEqual((ap_eval.severity, ap_eval.occurrence), (9, 8))

    def test_unevaluated_count_excludes_failure_modes_with_no_evaluation_under_method(self):
        self.assertEqual(risk_matrix.unevaluated_failure_mode_count(CLASSIC_RPN_METHOD), 0)
        # fm_classic_only has no aiag-vda-ap-poc evaluation at all.
        self.assertEqual(risk_matrix.unevaluated_failure_mode_count(ACTION_PRIORITY_POC_METHOD), 1)

    def test_failure_mode_never_appears_twice_on_the_same_grid(self):
        # Give fm_both a second, older classic-rpn evaluation too.
        evaluate_failure_mode(
            failure_mode=self.fm_both,
            definition=self.classic_definition,
            severity=1,
            occurrence=1,
            detection=1,
            stable_id="riskeval:both-classic-oldest",
            evaluated_at=timezone.now() - timedelta(days=10),
        )

        grid = risk_matrix.grid_rows(CLASSIC_RPN_METHOD)
        total_plotted = sum(cell["count"] for row in grid for cell in row)
        self.assertEqual(total_plotted, 2)  # fm_both once, fm_classic_only once

    def test_grid_cell_placement_ignores_detection(self):
        other_fmea = models.FMEA.objects.create(stable_id="fmea:risk-matrix-detection", name="Detection FMEA")
        fm_low_detection = models.FailureMode.objects.create(
            stable_id="fm:risk-matrix-low-detection", fmea=other_fmea, name="Low detection failure mode"
        )
        fm_high_detection = models.FailureMode.objects.create(
            stable_id="fm:risk-matrix-high-detection", fmea=other_fmea, name="High detection failure mode"
        )
        evaluate_failure_mode(
            failure_mode=fm_low_detection,
            definition=self.classic_definition,
            severity=6,
            occurrence=6,
            detection=1,
            stable_id="riskeval:low-detection",
        )
        evaluate_failure_mode(
            failure_mode=fm_high_detection,
            definition=self.classic_definition,
            severity=6,
            occurrence=6,
            detection=10,
            stable_id="riskeval:high-detection",
        )

        cell = risk_matrix.cell_evaluations(CLASSIC_RPN_METHOD, 6, 6)
        self.assertEqual(
            {item.failure_mode.stable_id for item in cell},
            {fm_low_detection.stable_id, fm_high_detection.stable_id},
        )


class RiskMatrixViewTests(_RiskMatrixFixture, TestCase):
    def setUp(self) -> None:
        self._seed_risk_matrix_fixture()

    def test_matrix_page_reports_unevaluated_count_per_method(self):
        classic_response = self.client.get("/risk-matrix/", {"method": CLASSIC_RPN_METHOD})
        self.assertContains(classic_response, "Every failure mode has an evaluation")

        ap_response = self.client.get("/risk-matrix/", {"method": ACTION_PRIORITY_POC_METHOD})
        self.assertContains(ap_response, "1 failure mode")
        self.assertContains(ap_response, "no aiag-vda-ap-poc evaluation yet")

    def test_unrecognized_method_falls_back_to_classic_rpn_without_error(self):
        response = self.client.get("/risk-matrix/", {"method": "not-a-real-method"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Every failure mode has an evaluation")

    def test_cell_drill_down_shows_correct_failure_modes_per_method(self):
        classic_cell = self.client.get(
            "/risk-matrix/cell/",
            {"method": CLASSIC_RPN_METHOD, "severity": 9, "occurrence": 4},
        )
        self.assertContains(classic_cell, "Both-method failure mode")

        ap_cell_at_classic_coords = self.client.get(
            "/risk-matrix/cell/",
            {"method": ACTION_PRIORITY_POC_METHOD, "severity": 9, "occurrence": 4},
        )
        self.assertNotContains(ap_cell_at_classic_coords, "Both-method failure mode")

        ap_cell_at_ap_coords = self.client.get(
            "/risk-matrix/cell/",
            {"method": ACTION_PRIORITY_POC_METHOD, "severity": 9, "occurrence": 8},
        )
        self.assertContains(ap_cell_at_ap_coords, "Both-method failure mode")

    def test_drill_down_shows_stored_result_verbatim_never_recomputed(self):
        stale_evaluation = models.RiskEvaluation.objects.create(
            stable_id="riskeval:deliberately-stale",
            failure_mode=self.fm_classic_only,
            definition=self.classic_definition,
            method=CLASSIC_RPN_METHOD,
            severity=7,
            occurrence=7,
            detection=1,
            result={"score": 999999, "classification": "high"},
        )
        self.assertNotEqual(
            stale_evaluation.result["score"],
            stale_evaluation.severity * stale_evaluation.occurrence * stale_evaluation.detection,
        )

        response = self.client.get(
            "/risk-matrix/cell/",
            {"method": CLASSIC_RPN_METHOD, "severity": 7, "occurrence": 7},
        )
        self.assertContains(response, "999999")

    def test_top_high_risk_items_sorted_by_stored_score_descending(self):
        # fm_classic_only's evaluation (2,2,2) -> RPN 8.
        # fm_both's classic-rpn evaluation (9,4,5) -> RPN 180. 180 > 8, so
        # fm_both must be ranked ahead of fm_classic_only.
        response = self.client.get("/risk-matrix/top/", {"method": CLASSIC_RPN_METHOD})
        content = response.content.decode()
        self.assertLess(
            content.index("Both-method failure mode"),
            content.index("Classic-only failure mode"),
        )

    def test_nav_and_dashboard_expose_risk_matrix(self):
        dashboard = self.client.get("/")
        self.assertContains(dashboard, "Risk Matrix")
        self.assertContains(dashboard, "High Risk Items")


class AiagVdaApMethodRegistrationTests(TestCase):
    """The real AIAG & VDA Table AP method is a new, separately selectable
    method alongside classic-rpn and aiag-vda-ap-poc - it does not replace
    either, and normalize_method()'s default fallback deliberately stays
    classic-rpn (a documented deviation from switching the default, kept to
    avoid changing what every existing view shows by default)."""

    def test_aiag_vda_ap_is_a_known_method_with_a_label(self):
        self.assertIn(AIAG_VDA_AP_METHOD, risk_matrix.KNOWN_METHODS)
        self.assertIn(CLASSIC_RPN_METHOD, risk_matrix.KNOWN_METHODS)
        self.assertIn(ACTION_PRIORITY_POC_METHOD, risk_matrix.KNOWN_METHODS)
        self.assertIn(AIAG_VDA_AP_METHOD, risk_matrix.METHOD_LABELS)

    def test_normalize_method_recognizes_the_new_method_without_falling_back(self):
        self.assertEqual(risk_matrix.normalize_method(AIAG_VDA_AP_METHOD), AIAG_VDA_AP_METHOD)

    def test_normalize_method_default_fallback_is_still_classic_rpn(self):
        # Deliberate: the decision doc's proposed alternative (switch the
        # default fallback to the new real method) was not adopted, since
        # that would change what every method-agnostic view shows by
        # default - a behavior change, not an addition.
        self.assertEqual(risk_matrix.normalize_method(None), CLASSIC_RPN_METHOD)
        self.assertEqual(risk_matrix.normalize_method("not-a-real-method"), CLASSIC_RPN_METHOD)

    def test_aiag_vda_msr_is_also_a_known_method_alongside_the_others(self):
        # Part B: FMEA-MSR is additive too - all four methods coexist.
        self.assertIn(AIAG_VDA_MSR_METHOD, risk_matrix.KNOWN_METHODS)
        self.assertIn(AIAG_VDA_MSR_METHOD, risk_matrix.METHOD_LABELS)
        self.assertEqual(risk_matrix.normalize_method(AIAG_VDA_MSR_METHOD), AIAG_VDA_MSR_METHOD)


class AiagVdaApRiskMatrixQueryLogicTests(_RiskMatrixFixture, TestCase):
    """The generic (non-classic-rpn) branches of risk_matrix.py - the
    "priority"-keyed band sorting, method-scoped latest-evaluation lookup -
    already work for any AP-shaped method; this proves it for the new real
    method the same way test_risk_matrix.py proves it for the PoC method."""

    def setUp(self) -> None:
        self._seed_risk_matrix_fixture()
        self.real_ap_definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:risk-matrix-aiag-vda-ap",
            method=AIAG_VDA_AP_METHOD,
            name="AIAG & VDA Action Priority (Table AP)",
        )
        evaluate_failure_mode(
            failure_mode=self.fm_classic_only,
            definition=self.real_ap_definition,
            severity=10,
            occurrence=10,
            detection=10,
            stable_id="riskeval:real-ap-high",
        )
        evaluate_failure_mode(
            failure_mode=self.fm_both,
            definition=self.real_ap_definition,
            severity=1,
            occurrence=10,
            detection=10,
            stable_id="riskeval:real-ap-low",
        )

    def test_latest_evaluations_scoped_to_the_new_method_only(self):
        latest = risk_matrix.latest_evaluations_by_method(AIAG_VDA_AP_METHOD)
        self.assertEqual(set(latest.keys()), {self.fm_classic_only.stable_id, self.fm_both.stable_id})

    def test_top_evaluations_sorts_by_priority_band_not_score(self):
        top = risk_matrix.top_evaluations(AIAG_VDA_AP_METHOD)
        self.assertEqual(top[0].failure_mode.stable_id, self.fm_classic_only.stable_id)
        self.assertEqual(top[0].result["priority"], "high")
        self.assertEqual(top[1].result["priority"], "low")

    def test_matrix_page_accepts_the_new_method_without_error(self):
        response = self.client.get("/risk-matrix/", {"method": AIAG_VDA_AP_METHOD})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AIAG &amp; VDA Action Priority (Table AP)")


class AiagVdaMsrRiskMatrixQueryLogicTests(_RiskMatrixFixture, TestCase):
    """Part B: FMEA-MSR's method also flows through the same generic
    query-logic branches, using occurrence/detection as Frequency/Monitoring
    rather than Occurrence/Detection."""

    def setUp(self) -> None:
        self._seed_risk_matrix_fixture()
        self.msr_definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:risk-matrix-aiag-vda-msr",
            method=AIAG_VDA_MSR_METHOD,
            name="AIAG & VDA FMEA-MSR Action Priority (Frequency / Monitoring)",
        )
        evaluate_failure_mode(
            failure_mode=self.fm_classic_only,
            definition=self.msr_definition,
            severity=10,
            occurrence=10,  # Frequency
            detection=10,  # Monitoring
            stable_id="riskeval:msr-high",
            failure_scenario="hazardous",
        )
        evaluate_failure_mode(
            failure_mode=self.fm_both,
            definition=self.msr_definition,
            severity=1,
            occurrence=10,
            detection=10,
            stable_id="riskeval:msr-low",
            failure_scenario="non_hazardous",
        )

    def test_latest_evaluations_scoped_to_the_msr_method_only(self):
        latest = risk_matrix.latest_evaluations_by_method(AIAG_VDA_MSR_METHOD)
        self.assertEqual(set(latest.keys()), {self.fm_classic_only.stable_id, self.fm_both.stable_id})
        self.assertEqual(latest[self.fm_classic_only.stable_id].failure_scenario, "hazardous")

    def test_top_evaluations_sorts_msr_by_priority_band(self):
        top = risk_matrix.top_evaluations(AIAG_VDA_MSR_METHOD)
        self.assertEqual(top[0].failure_mode.stable_id, self.fm_classic_only.stable_id)
        self.assertEqual(top[0].result["priority"], "high")
        self.assertEqual(top[1].result["priority"], "low")

    def test_matrix_page_accepts_the_msr_method_without_error(self):
        response = self.client.get("/risk-matrix/", {"method": AIAG_VDA_MSR_METHOD})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AIAG &amp; VDA FMEA-MSR Action Priority (Frequency / Monitoring)")

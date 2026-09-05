from __future__ import annotations

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from fmea_app import models
from fmea_app.services import evaluate_failure_mode
from fmea_evaluation import ACTION_PRIORITY_POC_METHOD, CLASSIC_RPN_METHOD


class RiskTrajectoryModelTests(TestCase):
    def setUp(self) -> None:
        self.definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:risk-trajectory-classic-rpn",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        self.fmea = models.FMEA.objects.create(stable_id="fmea:risk-trajectory", name="Trajectory FMEA")
        self.failure_mode = models.FailureMode.objects.create(
            stable_id="fm:risk-trajectory-model", fmea=self.fmea, name="Model test failure mode"
        )

    def test_lifecycle_gate_defaults_to_current_when_omitted(self):
        evaluation = evaluate_failure_mode(
            failure_mode=self.failure_mode,
            definition=self.definition,
            severity=3,
            occurrence=3,
            detection=3,
            stable_id="riskeval:trajectory-default-gate",
        )
        self.assertEqual(evaluation.lifecycle_gate, "current")
        self.assertEqual(evaluation.get_lifecycle_gate_display(), "Current")

    def test_lifecycle_gate_persists_and_round_trips_when_explicit(self):
        evaluation = evaluate_failure_mode(
            failure_mode=self.failure_mode,
            definition=self.definition,
            severity=4,
            occurrence=4,
            detection=4,
            stable_id="riskeval:trajectory-explicit-gate",
            lifecycle_gate="design_verification",
        )
        evaluation.refresh_from_db()
        self.assertEqual(evaluation.lifecycle_gate, "design_verification")
        self.assertEqual(evaluation.get_lifecycle_gate_display(), "Design Verification")


class _TrajectoryFixture:
    def _seed_trajectory_fixture(self) -> None:
        self.classic_definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:risk-trajectory-classic",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        self.ap_definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:risk-trajectory-ap",
            method=ACTION_PRIORITY_POC_METHOD,
            name="AIAG-VDA Action Priority (PoC)",
        )
        self.fmea = models.FMEA.objects.create(stable_id="fmea:risk-trajectory-view", name="Trajectory View FMEA")
        self.failure_mode = models.FailureMode.objects.create(
            stable_id="fm:risk-trajectory-view", fmea=self.fmea, name="Trajectory view failure mode"
        )
        self.unevaluated_failure_mode = models.FailureMode.objects.create(
            stable_id="fm:risk-trajectory-unevaluated", fmea=self.fmea, name="Never evaluated failure mode"
        )

        now = timezone.now()
        evaluate_failure_mode(
            failure_mode=self.failure_mode,
            definition=self.classic_definition,
            severity=3,
            occurrence=3,
            detection=3,
            stable_id="riskeval:trajectory-oldest",
            evaluated_at=now - timedelta(days=20),
            lifecycle_gate="concept_design",
        )
        evaluate_failure_mode(
            failure_mode=self.failure_mode,
            definition=self.ap_definition,
            severity=6,
            occurrence=6,
            detection=6,
            stable_id="riskeval:trajectory-middle",
            evaluated_at=now - timedelta(days=10),
            lifecycle_gate="process_validation",
        )
        self.newest_evaluation = models.RiskEvaluation.objects.create(
            stable_id="riskeval:trajectory-newest-stale",
            failure_mode=self.failure_mode,
            definition=self.classic_definition,
            method=CLASSIC_RPN_METHOD,
            severity=9,
            occurrence=9,
            detection=9,
            result={"score": 424242, "classification": "very_high"},
            evaluated_at=now,
            lifecycle_gate="serial_production",
        )


class RiskTrajectoryDetailViewTests(_TrajectoryFixture, TestCase):
    def setUp(self) -> None:
        self._seed_trajectory_fixture()

    def test_detail_shows_all_rows_in_ascending_chronological_order_with_verbatim_data(self):
        response = self.client.get(reverse("fmea:risk_trajectory", args=[self.failure_mode.stable_id]))
        content = response.content.decode()

        self.assertContains(response, "Concept/Design")
        self.assertContains(response, "Process Validation")
        self.assertContains(response, "Serial Production (SOP)")

        oldest_index = content.index("Concept/Design")
        middle_index = content.index("Process Validation")
        newest_index = content.index("Serial Production (SOP)")
        self.assertLess(oldest_index, middle_index)
        self.assertLess(middle_index, newest_index)

        # Stale, deliberately-wrong stored result must appear verbatim.
        self.assertContains(response, "424242")
        self.assertNotEqual(
            self.newest_evaluation.result["score"],
            self.newest_evaluation.severity * self.newest_evaluation.occurrence * self.newest_evaluation.detection,
        )

        self.assertContains(response, str(CLASSIC_RPN_METHOD))
        self.assertContains(response, str(ACTION_PRIORITY_POC_METHOD))


class RiskTrajectoryIndexViewTests(_TrajectoryFixture, TestCase):
    def setUp(self) -> None:
        self._seed_trajectory_fixture()

    def test_index_lists_evaluated_failure_modes_with_count_and_link_only(self):
        response = self.client.get(reverse("fmea:risk_trajectory_index"))

        self.assertContains(response, "Trajectory view failure mode")
        self.assertContains(response, "Trajectory View FMEA")
        self.assertContains(response, "3")
        self.assertContains(
            response, f'href="{reverse("fmea:risk_trajectory", args=[self.failure_mode.stable_id])}"'
        )
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea.stable_id])}"'
        )

        self.assertNotContains(response, "Never evaluated failure mode")


class RiskMatrixTrajectoryLinkTests(_TrajectoryFixture, TestCase):
    def setUp(self) -> None:
        self._seed_trajectory_fixture()

    def test_cell_drill_down_includes_view_trajectory_link(self):
        response = self.client.get(
            reverse("fmea:risk_matrix_cell"),
            {"method": CLASSIC_RPN_METHOD, "severity": 9, "occurrence": 9},
        )
        self.assertContains(response, "View Trajectory")
        self.assertContains(
            response, f'href="{reverse("fmea:risk_trajectory", args=[self.failure_mode.stable_id])}"'
        )


class EvaluateFailureLifecycleGateTests(TestCase):
    def setUp(self) -> None:
        self.definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:evaluate-failure-gate",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        self.fmea = models.FMEA.objects.create(stable_id="fmea:evaluate-failure-gate", name="Evaluate Gate FMEA")
        self.failure_mode = models.FailureMode.objects.create(
            stable_id="fm:evaluate-failure-gate", fmea=self.fmea, name="Evaluate gate failure mode"
        )

    def test_evaluate_failure_with_explicit_lifecycle_gate_persists_it(self):
        self.client.post(
            reverse("fmea:evaluate_failure", args=[self.failure_mode.stable_id]),
            data={
                "definition": self.definition.pk,
                "severity": 5,
                "occurrence": 5,
                "detection": 5,
                "lifecycle_gate": "pre_production",
            },
        )
        evaluation = models.RiskEvaluation.objects.get(failure_mode=self.failure_mode)
        self.assertEqual(evaluation.lifecycle_gate, "pre_production")

    def test_evaluate_failure_without_lifecycle_gate_defaults_to_current(self):
        self.client.post(
            reverse("fmea:evaluate_failure", args=[self.failure_mode.stable_id]),
            data={
                "definition": self.definition.pk,
                "severity": 5,
                "occurrence": 5,
                "detection": 5,
            },
        )
        evaluation = models.RiskEvaluation.objects.get(failure_mode=self.failure_mode)
        self.assertEqual(evaluation.lifecycle_gate, "current")


class RiskTrajectoryScopeTests(_TrajectoryFixture, TestCase):
    def setUp(self) -> None:
        self._seed_trajectory_fixture()

    def test_pages_have_no_canvas_and_no_propagation_chain_content(self):
        for response in (
            self.client.get(reverse("fmea:risk_trajectory_index")),
            self.client.get(reverse("fmea:risk_trajectory", args=[self.failure_mode.stable_id])),
        ):
            for excluded in (
                "<canvas",
                "Local Effect",
                "Next-Level Effect",
                "System Effect",
                "End Effect",
                "PM-FMEA",
            ):
                self.assertNotContains(response, excluded)

    def test_sidebar_has_exactly_one_new_risk_trajectory_link_and_other_unbuilt_labels_stay_absent(self):
        response = self.client.get("/")

        self.assertContains(response, "Risk Trajectory & Propagation")
        self.assertContains(response, f'href="{reverse("fmea:risk_trajectory_index")}"')
        self.assertEqual(response.content.decode().count("Risk Trajectory & Propagation"), 1)

        for unbuilt_label in (
            "Validation Trajectory",
            "CAPA",
            "Control Plans",
            "AI Assistant",
            "AP/Detection",
            "XDA Investigations",
            "SPC/ITRA-DT",
            "Documents & Links",
            "Lessons Learned",
            "Knowledge & References",
            "Operations",
            "Project Health",
            "FMEA Team",
        ):
            self.assertNotContains(response, unbuilt_label)

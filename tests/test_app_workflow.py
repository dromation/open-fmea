from __future__ import annotations

from django.test import TestCase

from fmea_app import models
from fmea_evaluation import CLASSIC_RPN_METHOD


class AppWorkflowTests(TestCase):
    def test_create_fmea_and_build_failure_chain_through_views(self):
        definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:classic-rpn-test",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )

        self.client.post(
            "/projects/create/",
            {"name": "Launch Project", "description": "New customer launch"},
        )
        project = models.FMEAProject.objects.get()

        response = self.client.post(
            "/fmeas/create/",
            {
                "project": project.pk,
                "name": "Assembly PFMEA",
                "fmea_type": "process",
                "scope": "Station 20",
            },
        )
        self.assertEqual(response.status_code, 302)
        fmea = models.FMEA.objects.get(name="Assembly PFMEA")

        self.client.post(
            f"/fmea/{fmea.stable_id}/failure-modes/add/",
            {"name": "Seal leaks", "description": "Pressure loss after assembly"},
        )
        failure_mode = models.FailureMode.objects.get()

        self.client.post(
            f"/failure-mode/{failure_mode.stable_id}/effects/add/",
            {"name": "Reduced braking performance", "description": ""},
        )
        self.client.post(
            f"/failure-mode/{failure_mode.stable_id}/causes/add/",
            {"name": "Seal nicked", "description": ""},
        )
        cause = models.FailureCause.objects.get()

        self.client.post(
            f"/cause/{cause.stable_id}/prevention-controls/add/",
            {"name": "Chamfer check", "description": ""},
        )
        self.client.post(
            f"/cause/{cause.stable_id}/detection-controls/add/",
            {"name": "Leak test", "description": ""},
        )
        self.client.post(
            f"/failure-mode/{failure_mode.stable_id}/evaluate/",
            {
                "definition": definition.pk,
                "severity": 9,
                "occurrence": 4,
                "detection": 5,
            },
        )

        self.assertEqual(models.FailureEffect.objects.count(), 1)
        self.assertEqual(models.PreventionControl.objects.count(), 1)
        self.assertEqual(models.DetectionControl.objects.count(), 1)
        evaluation = models.RiskEvaluation.objects.get()
        self.assertEqual(evaluation.result["score"], 180)

    def test_dashboard_renders_application_shell(self):
        response = self.client.get("/")

        self.assertContains(response, "FMEA Workspace")
        self.assertContains(response, "Create FMEA")
        self.assertContains(response, "Import Workbooks")

    def test_fmea_detail_renders_worksheet_table(self):
        definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:worksheet-classic-rpn",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        fmea = models.FMEA.objects.create(
            stable_id="fmea:worksheet",
            name="Worksheet PFMEA",
        )
        failure_mode = models.FailureMode.objects.create(
            stable_id="fm:worksheet-seal-leak",
            fmea=fmea,
            name="Seal leaks",
        )
        models.FailureEffect.objects.create(
            failure_mode=failure_mode,
            name="Fluid loss",
        )
        cause = models.FailureCause.objects.create(
            failure_mode=failure_mode,
            name="Seal nicked",
        )
        models.PreventionControl.objects.create(
            failure_cause=cause,
            name="Chamfer check",
        )
        models.DetectionControl.objects.create(
            failure_cause=cause,
            name="Leak test",
        )
        self.client.post(
            f"/failure-mode/{failure_mode.stable_id}/evaluate/",
            {
                "definition": definition.pk,
                "severity": 9,
                "occurrence": 4,
                "detection": 5,
            },
        )

        response = self.client.get(f"/fmea/{fmea.stable_id}/")

        self.assertContains(response, "FMEA Worksheet")
        self.assertContains(response, "Failure Mode")
        self.assertContains(response, "Prevention Controls")
        self.assertContains(response, "Detection Controls")
        self.assertContains(response, "Seal leaks")
        self.assertContains(response, "Seal nicked")
        self.assertContains(response, "RPN 180")

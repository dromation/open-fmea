from __future__ import annotations

from django.test import TestCase

from fmea_app import models
from fmea_app.management.commands.seed_demo import _aiag_vda_msr_rating_scales, _aiag_vda_rating_scales
from fmea_evaluation import AIAG_VDA_AP_METHOD, AIAG_VDA_MSR_METHOD, CLASSIC_RPN_METHOD


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

    def test_fmea_detail_offers_the_real_aiag_vda_ap_method_alongside_existing_methods(self):
        models.EvaluationDefinition.objects.create(
            stable_id="eval:aiag-vda-ap-form-option",
            method=AIAG_VDA_AP_METHOD,
            name="AIAG & VDA Action Priority (Table AP)",
        )
        fmea = models.FMEA.objects.create(stable_id="fmea:ap-form-option", name="Form Option PFMEA")
        models.FailureMode.objects.create(stable_id="fm:ap-form-option", fmea=fmea, name="Seal leaks")

        response = self.client.get(f"/fmea/{fmea.stable_id}/")

        # The pre-existing classic-rpn/aiag-vda-ap-poc options are untouched;
        # the new real method is just another selectable <option>, not a
        # replacement.
        self.assertContains(response, "AIAG &amp; VDA Action Priority (Table AP)")

    def test_fmea_detail_shows_pfmea_rating_reference_for_a_process_type_fmea(self):
        models.EvaluationDefinition.objects.create(
            stable_id="eval:aiag-vda-ap-reference-pfmea",
            method=AIAG_VDA_AP_METHOD,
            name="AIAG & VDA Action Priority (Table AP)",
            rating_scales=_aiag_vda_rating_scales(),
        )
        fmea = models.FMEA.objects.create(
            stable_id="fmea:ap-reference-pfmea", name="Reference PFMEA", fmea_type="process"
        )
        models.FailureMode.objects.create(stable_id="fm:ap-reference-pfmea", fmea=fmea, name="Seal leaks")

        response = self.client.get(f"/fmea/{fmea.stable_id}/")

        self.assertContains(response, "AIAG &amp; VDA rating criteria (PFMEA)")
        self.assertContains(response, "Your Plant:")
        self.assertContains(response, "Ship-to Plant:")
        self.assertContains(response, "End User:")

    def test_fmea_detail_shows_dfmea_rating_reference_for_a_design_type_fmea(self):
        models.EvaluationDefinition.objects.create(
            stable_id="eval:aiag-vda-ap-reference-dfmea",
            method=AIAG_VDA_AP_METHOD,
            name="AIAG & VDA Action Priority (Table AP)",
            rating_scales=_aiag_vda_rating_scales(),
        )
        fmea = models.FMEA.objects.create(
            stable_id="fmea:ap-reference-dfmea", name="Reference DFMEA", fmea_type="design"
        )
        models.FailureMode.objects.create(stable_id="fm:ap-reference-dfmea", fmea=fmea, name="Seal leaks")

        response = self.client.get(f"/fmea/{fmea.stable_id}/")

        self.assertContains(response, "AIAG &amp; VDA rating criteria (DFMEA)")
        self.assertNotContains(response, "Your Plant:")
        self.assertContains(response, "Affects safe operation of the vehicle")

    def test_fmea_detail_offers_the_aiag_vda_msr_method_and_failure_scenario_field(self):
        models.EvaluationDefinition.objects.create(
            stable_id="eval:aiag-vda-msr-form-option",
            method=AIAG_VDA_MSR_METHOD,
            name="AIAG & VDA FMEA-MSR Action Priority (Frequency / Monitoring)",
        )
        fmea = models.FMEA.objects.create(stable_id="fmea:msr-form-option", name="MSR Form Option DFMEA")
        models.FailureMode.objects.create(stable_id="fm:msr-form-option", fmea=fmea, name="Seal leaks")

        response = self.client.get(f"/fmea/{fmea.stable_id}/")

        self.assertContains(response, "AIAG &amp; VDA FMEA-MSR Action Priority (Frequency / Monitoring)")
        self.assertContains(response, "Failure Scenario")
        self.assertContains(response, "Non-Hazardous")
        self.assertContains(response, "Mitigated (Effect)")

    def test_fmea_detail_shows_msr_criteria_reference_when_msr_definition_exists(self):
        models.EvaluationDefinition.objects.create(
            stable_id="eval:aiag-vda-msr-reference",
            method=AIAG_VDA_MSR_METHOD,
            name="AIAG & VDA FMEA-MSR Action Priority (Frequency / Monitoring)",
            rating_scales=_aiag_vda_msr_rating_scales(),
        )
        fmea = models.FMEA.objects.create(stable_id="fmea:msr-reference", name="MSR Reference DFMEA")
        models.FailureMode.objects.create(stable_id="fm:msr-reference", fmea=fmea, name="Seal leaks")

        response = self.client.get(f"/fmea/{fmea.stable_id}/")

        self.assertContains(response, "AIAG &amp; VDA FMEA-MSR criteria (Frequency / Monitoring)")
        self.assertContains(response, "Use the rating number that corresponds with the least effective")
        self.assertContains(response, "Fault Handling Time Interval")

    def test_fmea_detail_omits_msr_reference_when_no_msr_definition_exists(self):
        fmea = models.FMEA.objects.create(stable_id="fmea:no-msr-reference", name="No MSR Reference DFMEA")
        models.FailureMode.objects.create(stable_id="fm:no-msr-reference", fmea=fmea, name="Seal leaks")

        response = self.client.get(f"/fmea/{fmea.stable_id}/")

        self.assertNotContains(response, "AIAG &amp; VDA FMEA-MSR criteria")

    def test_evaluate_failure_saves_failure_scenario_only_for_msr_evaluations(self):
        msr_definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:aiag-vda-msr-save",
            method=AIAG_VDA_MSR_METHOD,
            name="AIAG & VDA FMEA-MSR Action Priority (Frequency / Monitoring)",
        )
        fmea = models.FMEA.objects.create(stable_id="fmea:msr-save", name="MSR Save DFMEA")
        failure_mode = models.FailureMode.objects.create(stable_id="fm:msr-save", fmea=fmea, name="Seal leaks")

        self.client.post(
            f"/failure-mode/{failure_mode.stable_id}/evaluate/",
            {
                "definition": msr_definition.pk,
                "severity": 9,
                "occurrence": 4,  # Frequency
                "detection": 5,  # Monitoring
                "failure_scenario": "hazardous",
            },
        )

        evaluation = models.RiskEvaluation.objects.get()
        self.assertEqual(evaluation.failure_scenario, "hazardous")
        self.assertEqual(evaluation.result["priority"], "high")

    def test_evaluate_failure_leaves_failure_scenario_blank_when_not_submitted(self):
        classic_definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:classic-rpn-no-scenario",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        fmea = models.FMEA.objects.create(stable_id="fmea:no-scenario", name="No Scenario PFMEA")
        failure_mode = models.FailureMode.objects.create(stable_id="fm:no-scenario", fmea=fmea, name="Seal leaks")

        self.client.post(
            f"/failure-mode/{failure_mode.stable_id}/evaluate/",
            {
                "definition": classic_definition.pk,
                "severity": 9,
                "occurrence": 4,
                "detection": 5,
            },
        )

        evaluation = models.RiskEvaluation.objects.get()
        self.assertEqual(evaluation.failure_scenario, "")

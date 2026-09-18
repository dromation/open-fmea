from __future__ import annotations

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from fmea_app import models
from fmea_evaluation import CLASSIC_RPN_METHOD


class CrossSliceWorkflowTests(TestCase):
    def test_full_gui_workflow_across_slices(self):
        # 1. Dashboard renders, theme-toggle control present (ties the
        #    presentational slice into the same session as everything else).
        dashboard_response = self.client.get(reverse("fmea:dashboard"))
        self.assertContains(dashboard_response, "data-theme-toggle")

        # 2. Prerequisites with no GUI creation path yet: created via ORM,
        #    exactly as test_app_workflow.py already does for
        #    EvaluationDefinition.
        models.EvaluationDefinition.objects.create(
            stable_id="eval:cross-slice-workflow",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        call_command("seed_cause_category_scheme")
        method_category = models.CauseCategory.objects.get(name="Method")

        # 3. Real FMEA created through the GUI.
        self.client.post(
            reverse("fmea:create_project"),
            {"name": "Cross-Slice Launch Project", "description": "End-to-end workflow fixture"},
        )
        project = models.FMEAProject.objects.get(name="Cross-Slice Launch Project")

        fmea_response = self.client.post(
            reverse("fmea:create_fmea"),
            {
                "project": project.pk,
                "name": "Cross-Slice PFMEA",
                "fmea_type": "process",
                "scope": "Cross-slice workflow station",
            },
        )
        self.assertEqual(fmea_response.status_code, 302)
        fmea = models.FMEA.objects.get(name="Cross-Slice PFMEA")

        product = models.Product.objects.create(
            stable_id="product:cross-slice-workflow",
            fmea=fmea,
            name="Cross-Slice Product",
        )
        process = models.Process.objects.create(
            stable_id="process:cross-slice-workflow",
            fmea=fmea,
            name="Cross-Slice Process",
        )
        operation = models.Operation.objects.create(
            stable_id="operation:cross-slice-workflow",
            process=process,
            name="Install seal",
            sequence="10",
        )

        # 4. Functions slice: a Function tied to the Product created above.
        function_response = self.client.post(
            reverse("fmea:add_function", args=[fmea.stable_id]),
            {"name": "Maintain hydraulic pressure", "description": "", "product": product.pk},
        )
        self.assertEqual(function_response.status_code, 302)
        function = models.Function.objects.get(name="Maintain hydraulic pressure")
        self.assertEqual(function.product_id, product.pk)

        # 5. Failure mode and cause, real failure chain.
        failure_mode_response = self.client.post(
            reverse("fmea:add_failure_mode", args=[fmea.stable_id]),
            {"name": "Seal leaks after assembly", "description": "", "function": function.pk},
        )
        self.assertEqual(failure_mode_response.status_code, 302)
        failure_mode = models.FailureMode.objects.get(name="Seal leaks after assembly")
        self.assertEqual(failure_mode.function_id, function.pk)

        cause_response = self.client.post(
            reverse("fmea:add_failure_cause", args=[failure_mode.stable_id]),
            {"name": "Seal nicked during installation", "description": ""},
        )
        self.assertEqual(cause_response.status_code, 302)
        cause = models.FailureCause.objects.get(name="Seal nicked during installation")
        self.assertEqual(cause.failure_mode_id, failure_mode.pk)

        # 6. Actions slice, on the same FailureCause from step 5.
        action_response = self.client.post(
            reverse("fmea:add_action_to_cause", args=[cause.stable_id]),
            {"name": "Inspect seal seating surface", "description": "", "status": "open"},
        )
        self.assertEqual(action_response.status_code, 302)
        action = models.RecommendedAction.objects.get(name="Inspect seal seating surface")
        self.assertEqual(action.failure_cause_id, cause.pk)
        self.assertIsNone(action.failure_mode_id)

        # 7. Process Characteristic slice, on the Operation created above.
        characteristic_response = self.client.post(
            reverse("fmea:new_process_characteristic"),
            {
                "operation": operation.pk,
                "name": "Seal installation force",
                "description": "Force applied while seating the seal.",
                "cause_category_id": "",
                "attributes": '{"nominal": "controlled insertion"}',
            },
        )
        self.assertEqual(characteristic_response.status_code, 302)
        process_characteristic = models.ProcessCharacteristic.objects.get(name="Seal installation force")

        # 8. Cause Influence (Ishikawa backend), linking the real Process
        #    Characteristic from step 7 to the real FailureCause from step 5.
        influence_response = self.client.post(
            reverse("fmea:create_cause_influence"),
            {
                "source_type": "ProcessCharacteristic",
                "source_id": process_characteristic.stable_id,
                "target_type": "FailureCause",
                "target_id": cause.stable_id,
                "influence_type": "affects",
                "cause_category_id": method_category.stable_id,
            },
        )
        self.assertEqual(influence_response.status_code, 302)
        influence = models.CauseInfluence.objects.get(
            source_id=process_characteristic.stable_id,
            target_id=cause.stable_id,
        )
        self.assertEqual(influence.influence_type, "affects")

        # 9. Ishikawa board for the failure mode from step 5: the cause and
        #    the influence link from step 8 both appear.
        ishikawa_response = self.client.get(
            reverse("fmea:ishikawa_board", args=[failure_mode.stable_id])
        )
        self.assertContains(ishikawa_response, cause.name)
        self.assertContains(ishikawa_response, process_characteristic.name)

        # 10. Risk Matrix: system-wide, no per-FMEA scoping assertion.
        risk_matrix_response = self.client.get(reverse("fmea:risk_matrix"))
        self.assertEqual(risk_matrix_response.status_code, 200)
        self.assertContains(risk_matrix_response, "Risk Matrix")

        # 11. Back to the worksheet: function, failure mode, cause, and
        #     action names all present together, plus the theme toggle.
        worksheet_response = self.client.get(reverse("fmea:fmea_detail", args=[fmea.stable_id]))
        self.assertContains(worksheet_response, function.name)
        self.assertContains(worksheet_response, failure_mode.name)
        self.assertContains(worksheet_response, cause.name)
        self.assertContains(worksheet_response, action.name)
        self.assertContains(worksheet_response, "data-theme-toggle")

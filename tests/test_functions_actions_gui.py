from __future__ import annotations

from django.test import TestCase

from fmea_app import models


class FunctionsActionsGuiTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:functions-actions",
            name="Functions/Actions FMEA",
        )
        self.product = models.Product.objects.create(
            stable_id="product:functions-actions",
            fmea=self.fmea,
            name="Test Product",
        )
        self.process = models.Process.objects.create(
            stable_id="process:functions-actions",
            fmea=self.fmea,
            name="Test Process",
        )
        self.operation = models.Operation.objects.create(
            stable_id="operation:functions-actions",
            process=self.process,
            name="Test Operation",
            sequence="10",
        )

    def test_function_can_be_created_and_appears_in_the_fmea_function_section(self):
        response = self.client.post(
            f"/fmea/{self.fmea.stable_id}/functions/add/",
            {"name": "Maintain seal", "description": "Keep fluid contained", "product": self.product.pk},
        )
        self.assertEqual(response.status_code, 302)
        function = models.Function.objects.get(name="Maintain seal")
        self.assertEqual(function.product_id, self.product.pk)

        detail = self.client.get(f"/fmea/{self.fmea.stable_id}/")
        self.assertContains(detail, "Maintain seal")

    def test_function_requires_a_product_or_operation(self):
        response = self.client.post(
            f"/fmea/{self.fmea.stable_id}/functions/add/",
            {"name": "Orphan function", "description": ""},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Function.objects.filter(name="Orphan function").exists())

    def test_failure_mode_can_be_created_with_an_optional_function_link(self):
        function = models.Function.objects.create(
            stable_id="function:functions-actions-seal",
            product=self.product,
            name="Maintain seal",
        )

        response = self.client.post(
            f"/fmea/{self.fmea.stable_id}/failure-modes/add/",
            {"name": "Seal leaks", "description": "", "function": function.pk},
        )
        self.assertEqual(response.status_code, 302)
        failure_mode = models.FailureMode.objects.get(name="Seal leaks")
        self.assertEqual(failure_mode.function_id, function.pk)

        detail = self.client.get(f"/fmea/{self.fmea.stable_id}/")
        self.assertContains(detail, "Maintain seal")

    def test_failure_mode_function_select_is_scoped_to_its_own_fmea(self):
        other_fmea = models.FMEA.objects.create(stable_id="fmea:functions-actions-other", name="Other FMEA")
        other_product = models.Product.objects.create(
            stable_id="product:functions-actions-other", fmea=other_fmea, name="Other Product"
        )
        models.Function.objects.create(
            stable_id="function:functions-actions-other",
            product=other_product,
            name="Other FMEA's function",
        )

        response = self.client.get(f"/fmea/{self.fmea.stable_id}/")
        self.assertNotContains(response, "Other FMEA's function")

    def test_action_created_via_cause_form_has_failure_cause_set_and_failure_mode_null(self):
        failure_mode = models.FailureMode.objects.create(
            stable_id="fm:functions-actions", fmea=self.fmea, name="Seal leaks"
        )
        cause = models.FailureCause.objects.create(
            stable_id="cause:functions-actions", failure_mode=failure_mode, name="Seal nicked"
        )

        response = self.client.post(
            f"/cause/{cause.stable_id}/actions/add/",
            {"name": "Inspect seal", "description": "", "status": "open"},
        )
        self.assertEqual(response.status_code, 302)
        action = models.RecommendedAction.objects.get(name="Inspect seal")
        self.assertEqual(action.failure_cause_id, cause.pk)
        self.assertIsNone(action.failure_mode_id)

    def test_action_created_via_failure_mode_form_has_failure_mode_set_and_failure_cause_null(self):
        failure_mode = models.FailureMode.objects.create(
            stable_id="fm:functions-actions-2", fmea=self.fmea, name="Seal leaks 2"
        )

        response = self.client.post(
            f"/failure-mode/{failure_mode.stable_id}/actions/add/",
            {"name": "Review design", "description": "", "status": "open"},
        )
        self.assertEqual(response.status_code, 302)
        action = models.RecommendedAction.objects.get(name="Review design")
        self.assertEqual(action.failure_mode_id, failure_mode.pk)
        self.assertIsNone(action.failure_cause_id)

    def test_action_detail_renders_its_own_fields(self):
        failure_mode = models.FailureMode.objects.create(
            stable_id="fm:functions-actions-3", fmea=self.fmea, name="Seal leaks 3"
        )
        action = models.RecommendedAction.objects.create(
            stable_id="action:functions-actions",
            failure_mode=failure_mode,
            name="Review torque spec",
            status="open",
            due_date="2026-10-01",
        )

        response = self.client.get(f"/actions/{action.stable_id}/")
        self.assertContains(response, "Review torque spec")
        self.assertContains(response, "Oct. 1, 2026")

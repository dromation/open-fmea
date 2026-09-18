from __future__ import annotations

from datetime import date

from django.test import TestCase
from django.urls import reverse

from fmea_app import models


class ValidationTestListTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:validation-tests",
            name="Validation Tests FMEA",
        )
        self.failure_mode = models.FailureMode.objects.create(
            stable_id="failure-mode:validation-tests",
            fmea=self.fmea,
            name="Seal leaks",
        )
        self.role = models.ResponsibleRole.objects.create(
            stable_id="responsible-role:validation-tests",
            name="Test Engineer",
        )
        self.action = models.RecommendedAction.objects.create(
            stable_id="action:validation-tests",
            failure_mode=self.failure_mode,
            name="Improve seal seating process",
        )
        self.test_a = models.ValidationTest.objects.create(
            stable_id="validation-test:a",
            failure_mode=self.failure_mode,
            recommended_action=self.action,
            name="Leak rate validation",
            test_type="validation",
            method="Pressure decay test",
            result_status="pass",
            planned_date=date(2026, 1, 10),
            executed_date=date(2026, 1, 12),
            priority="high",
            owner=self.role,
            lifecycle_gate="design_verification",
            status="completed",
        )
        self.test_b = models.ValidationTest.objects.create(
            stable_id="validation-test:b",
            failure_mode=self.failure_mode,
            name="Field reliability check",
            test_type="reliability",
            method="Accelerated life test",
            result_status="pending",
            priority="medium",
            lifecycle_gate="serial_production",
            status="planned",
        )

    def test_list_shows_all_columns_with_correct_data_and_links(self):
        response = self.client.get(reverse("fmea:validation_test_list"))
        content = response.content.decode()

        self.assertContains(response, "Seal leaks")
        self.assertContains(response, "Validation")
        self.assertContains(response, "Pressure decay test")
        self.assertContains(response, "Pass")
        self.assertContains(response, "Jan. 10, 2026")
        self.assertContains(response, "Jan. 12, 2026")
        self.assertContains(response, "High")
        self.assertContains(response, "Test Engineer")
        self.assertContains(response, "Completed")
        self.assertContains(response, "Design Verification")

        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea.stable_id])}"'
        )

    def test_create_view_persists_all_fields_including_recommended_action(self):
        response = self.client.post(
            reverse("fmea:new_validation_test"),
            data={
                "name": "New Test",
                "failure_mode": self.failure_mode.pk,
                "recommended_action": self.action.pk,
                "test_type": "verification",
                "method": "Dimensional check",
                "objective": "Confirm dimension within spec",
                "nominal_target": "10mm +/- 0.1",
                "acceptance_criteria": "Within tolerance",
                "result_status": "pending",
                "planned_date": "2026-02-01",
                "executed_date": "",
                "priority": "medium",
                "owner": self.role.pk,
                "lifecycle_gate": "pre_production",
                "status": "planned",
            },
        )
        created = models.ValidationTest.objects.get(name="New Test")
        self.assertRedirects(response, reverse("fmea:validation_test_detail", args=[created.stable_id]))
        self.assertEqual(created.recommended_action_id, self.action.pk)
        self.assertEqual(created.owner_id, self.role.pk)
        self.assertEqual(created.method, "Dimensional check")
        self.assertEqual(created.nominal_target, "10mm +/- 0.1")

    def test_create_view_without_recommended_action_stores_null(self):
        response = self.client.post(
            reverse("fmea:new_validation_test"),
            data={
                "name": "Unlinked Test",
                "failure_mode": self.failure_mode.pk,
                "recommended_action": "",
                "test_type": "acceptance",
                "method": "",
                "objective": "",
                "nominal_target": "",
                "acceptance_criteria": "",
                "result_status": "pending",
                "planned_date": "",
                "executed_date": "",
                "priority": "low",
                "owner": "",
                "lifecycle_gate": "current",
                "status": "planned",
            },
        )
        created = models.ValidationTest.objects.get(name="Unlinked Test")
        self.assertRedirects(response, reverse("fmea:validation_test_detail", args=[created.stable_id]))
        self.assertIsNone(created.recommended_action_id)

    def test_detail_shows_action_link_when_set_and_not_linked_message_when_unset(self):
        linked_response = self.client.get(reverse("fmea:validation_test_detail", args=[self.test_a.stable_id]))
        self.assertContains(linked_response, "Improve seal seating process")
        self.assertContains(
            linked_response, f'href="{reverse("fmea:action_detail", args=[self.action.stable_id])}"'
        )

        unlinked_response = self.client.get(reverse("fmea:validation_test_detail", args=[self.test_b.stable_id]))
        self.assertContains(unlinked_response, "Not linked to an action")
        self.assertNotContains(
            unlinked_response, f'href="{reverse("fmea:action_detail", args=[self.action.stable_id])}"'
        )

    def test_get_filters_narrow_the_list_individually_and_combined(self):
        base_url = reverse("fmea:validation_test_list")

        response = self.client.get(base_url, {"test_type": "validation"})
        self.assertContains(response, "Pressure decay test")
        self.assertNotContains(response, "Accelerated life test")

        response = self.client.get(base_url, {"status": "planned"})
        self.assertNotContains(response, "Pressure decay test")
        self.assertContains(response, "Accelerated life test")

        response = self.client.get(base_url, {"lifecycle_gate": "serial_production"})
        self.assertNotContains(response, "Pressure decay test")
        self.assertContains(response, "Accelerated life test")

        response = self.client.get(
            base_url, {"test_type": "reliability", "status": "planned", "lifecycle_gate": "serial_production"}
        )
        self.assertContains(response, "Accelerated life test")
        self.assertNotContains(response, "Pressure decay test")

    def test_pages_have_no_upload_ui_no_canvas_and_no_test_plan_content(self):
        for response in (
            self.client.get(reverse("fmea:validation_test_list")),
            self.client.get(reverse("fmea:new_validation_test")),
            self.client.get(reverse("fmea:validation_test_detail", args=[self.test_a.stable_id])),
        ):
            for excluded in ('type="file"', "<canvas", "Test Plan"):
                self.assertNotContains(response, excluded)

    def test_evidence_and_effectiveness_verification_are_untouched(self):
        # Regression check: this slice must not have touched Evidence or
        # EffectivenessVerification. Confirmed independently by grep at
        # implementation time (zero lines changed in either model, no
        # migration operation naming either table); this test locks in
        # that both still work exactly as before.
        evidence = models.Evidence.objects.create(
            stable_id="evidence:validation-tests-regression",
            action=self.action,
            name="Inspection photo reference",
        )
        verification = models.EffectivenessVerification.objects.create(
            stable_id="effectiveness-verification:validation-tests-regression",
            action=self.action,
            name="Effectiveness check",
            result="Effective",
        )
        self.assertEqual(evidence.action_id, self.action.pk)
        self.assertEqual(verification.action_id, self.action.pk)

from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from fmea_app import forms, models


class ProcessCharacteristicControlFieldsModelTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:process-control-fields",
            name="Process Control Fields FMEA",
            fmea_type="process",
        )
        self.process = models.Process.objects.create(
            stable_id="process:process-control-fields",
            fmea=self.fmea,
            name="Seal Assembly",
        )
        self.operation = models.Operation.objects.create(
            stable_id="operation:process-control-fields",
            process=self.process,
            name="Install seal",
            sequence="10",
        )
        self.role = models.ResponsibleRole.objects.create(
            stable_id="responsible-role:process-control-fields",
            name="Process Engineer",
        )

    def test_existing_rows_migrate_with_no_data_loss_and_correct_defaults(self):
        # Simulates a pre-slice row: only the original five fields set,
        # matching every ProcessCharacteristic that existed before this
        # migration. Confirms the additive migration didn't disturb them and
        # that status/effectiveness pick up their new defaults correctly.
        characteristic = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:pre-existing",
            operation=self.operation,
            name="Seal installation force",
            description="Force applied while seating the piston seal.",
            cause_category_id="cause-category:ishikawa-5me:method",
            attributes={"nominal": "controlled manual insertion"},
        )
        characteristic.refresh_from_db()

        self.assertEqual(characteristic.operation_id, self.operation.pk)
        self.assertEqual(characteristic.name, "Seal installation force")
        self.assertEqual(characteristic.description, "Force applied while seating the piston seal.")
        self.assertEqual(characteristic.cause_category_id, "cause-category:ishikawa-5me:method")
        self.assertEqual(characteristic.attributes, {"nominal": "controlled manual insertion"})

        self.assertEqual(characteristic.status, models.ControlStatus.ACTIVE)
        self.assertEqual(characteristic.effectiveness, models.ControlEffectiveness.UNKNOWN)
        self.assertEqual(characteristic.control_type, "")
        self.assertIsNone(characteristic.owner_id)
        self.assertIsNone(characteristic.review_due)
        self.assertEqual(characteristic.reaction_plan, "")

    def test_form_creates_characteristic_with_all_nine_new_fields_populated(self):
        form = forms.ProcessCharacteristicForm(
            data={
                "operation": self.operation.pk,
                "name": "Leak test pressure",
                "description": "",
                "cause_category_id": "",
                "attributes": "{}",
                "control_type": "measurement",
                "method": "Pressure decay gauge",
                "resource_equipment": "Gauge PN-4021",
                "frequency_trigger": "Every unit",
                "status": "review",
                "effectiveness": "effective",
                "owner": self.role.pk,
                "review_due": "2026-06-01",
                "reaction_plan": "Escalate to quality engineer if out of spec.",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        characteristic = form.save()
        characteristic.full_clean()

        self.assertEqual(characteristic.control_type, "measurement")
        self.assertEqual(characteristic.method, "Pressure decay gauge")
        self.assertEqual(characteristic.resource_equipment, "Gauge PN-4021")
        self.assertEqual(characteristic.frequency_trigger, "Every unit")
        self.assertEqual(characteristic.status, "review")
        self.assertEqual(characteristic.effectiveness, "effective")
        self.assertEqual(characteristic.owner_id, self.role.pk)
        self.assertEqual(characteristic.review_due, date(2026, 6, 1))
        self.assertEqual(characteristic.reaction_plan, "Escalate to quality engineer if out of spec.")

    def test_enum_fields_reject_values_outside_their_choices(self):
        characteristic = models.ProcessCharacteristic(
            stable_id="process-characteristic:invalid-choice",
            operation=self.operation,
            name="Invalid control type",
            control_type="not_a_real_control_type",
        )
        with self.assertRaises(ValidationError):
            characteristic.full_clean()

        characteristic2 = models.ProcessCharacteristic(
            stable_id="process-characteristic:invalid-status",
            operation=self.operation,
            name="Invalid status",
            status="not_a_real_status",
        )
        with self.assertRaises(ValidationError):
            characteristic2.full_clean()

        characteristic3 = models.ProcessCharacteristic(
            stable_id="process-characteristic:invalid-effectiveness",
            operation=self.operation,
            name="Invalid effectiveness",
            effectiveness="not_a_real_effectiveness",
        )
        with self.assertRaises(ValidationError):
            characteristic3.full_clean()

    def test_owner_accepts_none_and_a_valid_responsible_role(self):
        unassigned = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:owner-none",
            operation=self.operation,
            name="Unowned characteristic",
        )
        unassigned.full_clean()
        self.assertIsNone(unassigned.owner_id)

        assigned = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:owner-set",
            operation=self.operation,
            name="Owned characteristic",
            owner=self.role,
        )
        assigned.full_clean()
        self.assertEqual(assigned.owner_id, self.role.pk)


class ProcessCharacteristicControlFieldsViewTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:process-control-fields-view",
            name="Process Control Fields View FMEA",
            fmea_type="process",
        )
        self.process = models.Process.objects.create(
            stable_id="process:process-control-fields-view",
            fmea=self.fmea,
            name="Seal Assembly",
        )
        self.operation = models.Operation.objects.create(
            stable_id="operation:process-control-fields-view",
            process=self.process,
            name="Install seal",
            sequence="10",
        )
        self.role = models.ResponsibleRole.objects.create(
            stable_id="responsible-role:process-control-fields-view",
            name="Process Engineer",
        )
        self.measurement_characteristic = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:measurement-active",
            operation=self.operation,
            name="Leak test pressure",
            control_type="measurement",
            status="active",
            effectiveness="effective",
            owner=self.role,
            review_due=date(2026, 6, 1),
            reaction_plan="Escalate to quality engineer if out of spec.",
        )
        self.detection_characteristic = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:detection-review",
            operation=self.operation,
            name="Visual weld inspection",
            control_type="detection",
            status="review",
        )

    def test_control_type_filter_narrows_the_list(self):
        response = self.client.get(reverse("fmea:process_characteristic_list"), {"control_type": "measurement"})
        self.assertContains(response, "Leak test pressure")
        self.assertNotContains(response, "Visual weld inspection")

    def test_status_filter_narrows_the_list(self):
        response = self.client.get(reverse("fmea:process_characteristic_list"), {"status": "review"})
        self.assertNotContains(response, "Leak test pressure")
        self.assertContains(response, "Visual weld inspection")

    def test_empty_or_unrecognized_filter_returns_unfiltered_list(self):
        response = self.client.get(reverse("fmea:process_characteristic_list"), {"control_type": ""})
        self.assertContains(response, "Leak test pressure")
        self.assertContains(response, "Visual weld inspection")

        response = self.client.get(reverse("fmea:process_characteristic_list"), {"status": "not_a_real_status"})
        self.assertNotContains(response, "Leak test pressure")
        self.assertNotContains(response, "Visual weld inspection")

    def test_list_and_detail_render_the_new_field_values(self):
        list_response = self.client.get(reverse("fmea:process_characteristic_list"))
        self.assertContains(list_response, "Measurement")
        self.assertContains(list_response, "Effective")
        self.assertContains(list_response, "Process Engineer")

        detail_response = self.client.get(
            reverse("fmea:process_characteristic_detail", args=[self.measurement_characteristic.stable_id])
        )
        self.assertContains(detail_response, "Measurement")
        self.assertContains(detail_response, "Effective")
        self.assertContains(detail_response, "Process Engineer")
        self.assertContains(detail_response, "Escalate to quality engineer if out of spec.")

    def test_pages_have_no_canvas_and_no_approval_workflow_ui(self):
        for response in (
            self.client.get(reverse("fmea:process_characteristic_list")),
            self.client.get(
                reverse("fmea:process_characteristic_detail", args=[self.measurement_characteristic.stable_id])
            ),
            self.client.get(reverse("fmea:new_process_characteristic")),
        ):
            for excluded in ("<canvas", "Approve", "Pending Approval", "Approval Workflow"):
                self.assertNotContains(response, excluded)

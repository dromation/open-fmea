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
        # Part C addition: special_classification is additive - a
        # pre-existing row has none, same as ProductCharacteristic's
        # primary_classification defaults to None for old rows.
        self.assertIsNone(characteristic.special_classification_id)

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


class ProcessCharacteristicSpecialClassificationTests(TestCase):
    """Part C: the PFMEA-side 'Classification' field (AIAG & VDA Handbook),
    scoped to ProcessCharacteristic and reusing the same ClassificationTerm
    table ProductCharacteristic.primary_classification already uses -
    independently set, not inherited/cascaded from any related
    ProductCharacteristic."""

    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:process-special-classification",
            name="Special Classification FMEA",
            fmea_type="process",
        )
        self.process = models.Process.objects.create(
            stable_id="process:special-classification",
            fmea=self.fmea,
            name="Seal Assembly",
        )
        self.operation = models.Operation.objects.create(
            stable_id="operation:special-classification",
            process=self.process,
            name="Install seal",
            sequence="10",
        )
        self.scheme = models.ClassificationScheme.objects.create(
            stable_id="classification-scheme:process-special", name="Process Special Scheme"
        )
        self.safety = models.ClassificationTerm.objects.create(
            stable_id="classification-term:process-special-safety",
            scheme=self.scheme,
            name="Safety",
            order=1,
        )

    def test_defaults_to_none_and_can_be_set_via_the_shared_classification_term_table(self):
        unclassified = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:special-unclassified",
            operation=self.operation,
            name="Unclassified characteristic",
        )
        self.assertIsNone(unclassified.special_classification_id)

        classified = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:special-classified",
            operation=self.operation,
            name="Classified characteristic",
            special_classification=self.safety,
        )
        classified.refresh_from_db()
        self.assertEqual(classified.special_classification_id, self.safety.pk)
        self.assertEqual(classified.special_classification.name, "Safety")

    def test_deleting_the_classification_term_sets_the_field_to_null_not_cascade(self):
        classified = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:special-set-null",
            operation=self.operation,
            name="Classified characteristic",
            special_classification=self.safety,
        )
        self.safety.delete()
        classified.refresh_from_db()
        self.assertIsNone(classified.special_classification_id)

    def test_to_domain_carries_special_classification_id(self):
        classified = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:special-domain",
            operation=self.operation,
            name="Classified characteristic",
            special_classification=self.safety,
        )
        domain_obj = classified.to_domain()
        self.assertEqual(domain_obj.special_classification_id, self.safety.stable_id)

        unclassified = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:special-domain-none",
            operation=self.operation,
            name="Unclassified characteristic",
        )
        self.assertIsNone(unclassified.to_domain().special_classification_id)

    def test_form_accepts_special_classification(self):
        form = forms.ProcessCharacteristicForm(
            data={
                "operation": self.operation.pk,
                "name": "Leak test pressure",
                "description": "",
                "cause_category_id": "",
                "attributes": "{}",
                "special_classification": self.safety.pk,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        characteristic = form.save()
        self.assertEqual(characteristic.special_classification_id, self.safety.pk)

    def test_form_leaves_special_classification_optional(self):
        form = forms.ProcessCharacteristicForm(
            data={
                "operation": self.operation.pk,
                "name": "Leak test pressure",
                "description": "",
                "cause_category_id": "",
                "attributes": "{}",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        characteristic = form.save()
        self.assertIsNone(characteristic.special_classification_id)

    def test_list_and_detail_pages_render_special_classification(self):
        classified = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:special-render",
            operation=self.operation,
            name="Classified characteristic",
            special_classification=self.safety,
        )
        unclassified = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:special-render-none",
            operation=self.operation,
            name="Unclassified characteristic",
        )

        list_response = self.client.get(reverse("fmea:process_characteristic_list"))
        self.assertContains(list_response, "Special Classification")
        self.assertContains(list_response, "Safety")
        self.assertContains(list_response, "Unclassified")

        panel_response = self.client.get(
            reverse("fmea:process_characteristic_list"), {"selected": classified.stable_id}
        )
        self.assertContains(panel_response, "Safety")

        detail_response = self.client.get(
            reverse("fmea:process_characteristic_detail", args=[classified.stable_id])
        )
        self.assertContains(detail_response, "Special Classification")
        self.assertContains(detail_response, "Safety")

        unclassified_detail = self.client.get(
            reverse("fmea:process_characteristic_detail", args=[unclassified.stable_id])
        )
        self.assertContains(unclassified_detail, "Unclassified")


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

    def test_pages_have_no_approval_workflow_ui(self):
        for response in (
            self.client.get(reverse("fmea:process_characteristic_list")),
            self.client.get(
                reverse("fmea:process_characteristic_detail", args=[self.measurement_characteristic.stable_id])
            ),
            self.client.get(reverse("fmea:new_process_characteristic")),
        ):
            for excluded in ("Approve", "Pending Approval", "Approval Workflow", "Control Plan"):
                self.assertNotContains(response, excluded)

    def test_detail_and_form_pages_still_have_no_canvas(self):
        # Slice N (2026-09-06) added two Chart.js donuts to the list page only
        # (see ProcessCharacteristicRicherPageTests below); the detail and
        # create/edit pages were explicitly excluded from that slice's scope
        # and must remain canvas-free, exactly as this test originally
        # asserted for all three pages before Slice N existed.
        for response in (
            self.client.get(
                reverse("fmea:process_characteristic_detail", args=[self.measurement_characteristic.stable_id])
            ),
            self.client.get(reverse("fmea:new_process_characteristic")),
        ):
            self.assertNotContains(response, "<canvas")

    def test_list_page_has_exactly_two_canvases_for_the_two_required_donuts(self):
        # Decision 6 of the Slice N architecture decision calls for exactly
        # two Chart.js donuts (Control Type Distribution, Effectiveness
        # Overview) on this page and no more.
        response = self.client.get(reverse("fmea:process_characteristic_list"))
        self.assertEqual(response.content.decode().count("<canvas"), 2)


class ProcessCharacteristicRicherPageTests(TestCase):
    """Slice N (2026-09-06): KPI row, coarse PFMEA-link fact, right-docked
    detail panel with GET-param tabs, and filter/KPI consistency."""

    def setUp(self) -> None:
        self.process_fmea = models.FMEA.objects.create(
            stable_id="fmea:richer-page-process",
            name="Richer Page Process FMEA",
            fmea_type="process",
        )
        self.design_fmea = models.FMEA.objects.create(
            stable_id="fmea:richer-page-design",
            name="Richer Page Design FMEA",
            fmea_type="design",
        )
        self.process = models.Process.objects.create(
            stable_id="process:richer-page",
            fmea=self.process_fmea,
            name="Seal Assembly",
        )
        self.design_process = models.Process.objects.create(
            stable_id="process:richer-page-design",
            fmea=self.design_fmea,
            name="Design Process Shell",
        )
        self.operation = models.Operation.objects.create(
            stable_id="operation:richer-page",
            process=self.process,
            name="Install seal",
            sequence="10",
        )
        self.design_operation = models.Operation.objects.create(
            stable_id="operation:richer-page-design",
            process=self.design_process,
            name="Design-only operation",
            sequence="10",
        )

        self.c1 = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:richer-c1",
            operation=self.operation,
            name="Leak test pressure",
            control_type="measurement",
            status="active",
            effectiveness="effective",
            reaction_plan="Escalate to quality engineer.",
        )
        self.c2 = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:richer-c2",
            operation=self.operation,
            name="Visual weld inspection",
            control_type="detection",
            status="active",
            effectiveness="not_effective",
            reaction_plan="",
        )
        self.c3 = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:richer-c3",
            operation=self.operation,
            name="Torque check",
            control_type="test",
            status="review",
            effectiveness="not_effective",
            reaction_plan="Retorque and re-check.",
        )
        self.c4 = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:richer-c4",
            operation=self.design_operation,
            name="Design-only characteristic",
            control_type="",
            status="inactive",
            effectiveness="unknown",
            reaction_plan="",
        )
        self.c5 = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:richer-c5",
            operation=self.operation,
            name="Fixture alignment",
            control_type="monitoring",
            status="active",
            effectiveness="partially_effective",
            reaction_plan="Realign fixture.",
        )

    def test_kpi_tiles_match_expected_counts(self):
        response = self.client.get(reverse("fmea:process_characteristic_list"))
        self.assertEqual(response.context["kpi_total"], 5)
        self.assertEqual(response.context["kpi_active"], 3)
        self.assertEqual(response.context["kpi_not_effective"], 2)
        self.assertEqual(response.context["kpi_needs_review"], 1)
        self.assertEqual(response.context["kpi_no_reaction_plan"], 2)
        self.assertEqual(response.context["kpi_linked"], 4)

    def test_linked_to_pfmea_fact_is_correct_in_kpi_and_top_links_table(self):
        response = self.client.get(reverse("fmea:process_characteristic_list"))
        self.assertEqual(response.context["kpi_linked"], 4)
        top_links = response.context["top_pfmea_links"]
        self.assertEqual(len(top_links), 1)
        self.assertEqual(top_links[0]["fmea"].stable_id, self.process_fmea.stable_id)
        self.assertEqual(top_links[0]["count"], 4)
        self.assertContains(response, "Richer Page Process FMEA")
        self.assertNotContains(response, "Richer Page Design FMEA")

    def test_detail_panel_renders_real_field_values_per_tab(self):
        base_url = reverse("fmea:process_characteristic_list")

        general = self.client.get(base_url, {"selected": self.c1.stable_id})
        self.assertContains(general, "Leak test pressure")
        self.assertContains(general, "Install seal")

        method = self.client.get(base_url, {"selected": self.c1.stable_id, "tab": "method"})
        self.assertContains(method, "Measurement")

        reaction = self.client.get(base_url, {"selected": self.c1.stable_id, "tab": "reaction"})
        self.assertContains(reaction, "Escalate to quality engineer.")

        history = self.client.get(base_url, {"selected": self.c1.stable_id, "tab": "history"})
        self.assertEqual(history.status_code, 200)
        self.assertContains(history, str(self.c1.created_at.year))
        self.assertNotContains(history, "Created by")
        self.assertNotContains(history, "Last Updated by")

    def test_unrecognized_tab_defaults_to_general_without_500(self):
        response = self.client.get(
            reverse("fmea:process_characteristic_list"),
            {"selected": self.c1.stable_id, "tab": "not-a-real-tab"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "general")

    def test_missing_tab_defaults_to_general(self):
        response = self.client.get(
            reverse("fmea:process_characteristic_list"), {"selected": self.c1.stable_id}
        )
        self.assertEqual(response.context["active_tab"], "general")

    def test_invalid_selected_id_returns_404_not_500(self):
        response = self.client.get(
            reverse("fmea:process_characteristic_list"), {"selected": "process-characteristic:does-not-exist"}
        )
        self.assertEqual(response.status_code, 404)

    def test_existing_filters_still_work_and_kpi_donuts_move_with_them(self):
        response = self.client.get(reverse("fmea:process_characteristic_list"), {"status": "active"})
        self.assertEqual(response.context["kpi_total"], 3)
        self.assertEqual(response.context["kpi_active"], 3)
        self.assertEqual(response.context["kpi_needs_review"], 0)
        self.assertContains(response, "Leak test pressure")
        self.assertNotContains(response, "Torque check")

        control_type_labels = response.context["control_type_chart_data"]["labels"]
        self.assertNotIn("Test", control_type_labels)

from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from fmea_app import models


class ProductCharacteristicRegisterPageTests(TestCase):
    def setUp(self) -> None:
        self.scheme = models.ClassificationScheme.objects.create(
            stable_id="classification-scheme:pc-register", name="PC Register Test Scheme"
        )
        self.safety = models.ClassificationTerm.objects.create(
            stable_id="classification-term:pc-register-safety",
            scheme=self.scheme,
            name="Safety",
            order=1,
        )
        self.legal = models.ClassificationTerm.objects.create(
            stable_id="classification-term:pc-register-legal",
            scheme=self.scheme,
            name="Legal",
            order=2,
        )

        self.fmea = models.FMEA.objects.create(stable_id="fmea:pc-register", name="Register FMEA")

        self.system_optical = models.System.objects.create(
            stable_id="system:pc-register-optical", name="Optical System"
        )
        self.system_weld = models.System.objects.create(stable_id="system:pc-register-weld", name="Weld System")

        # Fully-resolving chain via the Product path: requirement -> function -> product -> system.
        self.product = models.Product.objects.create(
            stable_id="product:pc-register",
            fmea=self.fmea,
            name="Headlamp Housing",
            system=self.system_optical,
        )
        self.function_product = models.Function.objects.create(
            stable_id="function:pc-register-product", product=self.product, name="Contain Lens"
        )
        self.requirement_product = models.Requirement.objects.create(
            stable_id="requirement:pc-register-product", function=self.function_product, name="No Leaks"
        )

        # Fully-resolving chain via the Process path: requirement -> function -> operation -> process -> system.
        self.process = models.Process.objects.create(
            stable_id="process:pc-register", fmea=self.fmea, name="Weld Station", system=self.system_weld
        )
        self.operation = models.Operation.objects.create(
            stable_id="operation:pc-register", process=self.process, name="Weld Seam"
        )
        self.function_process = models.Function.objects.create(
            stable_id="function:pc-register-process", operation=self.operation, name="Join Panels"
        )
        self.requirement_process = models.Requirement.objects.create(
            stable_id="requirement:pc-register-process", function=self.function_process, name="Full Penetration"
        )

        # Dead-end chain: function has neither product nor operation set.
        self.function_dead_end = models.Function.objects.create(
            stable_id="function:pc-register-dead-end", name="Unassigned Function"
        )
        self.requirement_dead_end = models.Requirement.objects.create(
            stable_id="requirement:pc-register-dead-end", function=self.function_dead_end, name="Dead End Requirement"
        )

        self.characteristic_product = models.ProductCharacteristic.objects.create(
            stable_id="pc:register-product",
            requirement=self.requirement_product,
            name="Seal Flatness",
            is_special=True,
            primary_classification=self.safety,
        )
        self.characteristic_process = models.ProductCharacteristic.objects.create(
            stable_id="pc:register-process",
            requirement=self.requirement_process,
            name="Weld Penetration Depth",
            primary_classification=self.legal,
        )
        self.characteristic_dead_end = models.ProductCharacteristic.objects.create(
            stable_id="pc:register-dead-end",
            requirement=self.requirement_dead_end,
            name="Orphan Characteristic",
        )
        self.characteristic_no_requirement = models.ProductCharacteristic.objects.create(
            stable_id="pc:register-no-requirement", name="No Requirement Characteristic"
        )

        self.link = models.CharacteristicLink.objects.create(
            stable_id="characteristic-link:pc-register",
            from_characteristic=self.characteristic_product,
            to_characteristic=self.characteristic_process,
            relationship_type="drives",
            strength="high",
        )

    def test_table_renders_category_links_and_status_values(self):
        response = self.client.get(reverse("fmea:product_characteristic_list"))

        self.assertContains(response, "Seal Flatness")
        self.assertContains(response, "Weld Penetration Depth")
        self.assertContains(response, "Orphan Characteristic")
        self.assertContains(response, "Safety")
        self.assertContains(response, "Legal")
        self.assertContains(response, "Unclassified")
        self.assertContains(response, "Special")
        self.assertContains(response, "Standard")

    def test_system_product_column_renders_resolved_name_or_dead_end_placeholder(self):
        response = self.client.get(reverse("fmea:product_characteristic_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Optical System")
        self.assertContains(response, "Weld System")
        # Two dead-end rows (no requirement, and a requirement whose function
        # resolves neither product nor operation) must render the explicit
        # placeholder, not a blank cell.
        content = response.content.decode()
        self.assertGreaterEqual(content.count("&mdash;") + content.count("—"), 2)

    def test_kpi_tiles_match_expected_counts(self):
        response = self.client.get(reverse("fmea:product_characteristic_list"))

        self.assertEqual(response.context["kpi_total"], 4)
        self.assertEqual(response.context["kpi_special"], 1)
        self.assertEqual(response.context["kpi_unclassified"], 2)
        self.assertEqual(response.context["kpi_linked"], 2)

    def test_coverage_summary_matches_kpi_derived_facts(self):
        response = self.client.get(reverse("fmea:product_characteristic_list"))

        self.assertEqual(response.context["coverage_unclassified"], 2)
        self.assertEqual(response.context["coverage_unlinked"], 2)
        self.assertEqual(response.context["coverage_no_chain"], 2)

    def test_classification_filter_narrows_rows(self):
        response = self.client.get(
            reverse("fmea:product_characteristic_list"), {"classification": self.safety.stable_id}
        )

        self.assertContains(response, "Seal Flatness")
        self.assertNotContains(response, "Weld Penetration Depth")
        self.assertNotContains(response, "Orphan Characteristic")

    def test_is_special_filter_narrows_rows(self):
        response = self.client.get(reverse("fmea:product_characteristic_list"), {"is_special": "yes"})

        self.assertContains(response, "Seal Flatness")
        self.assertNotContains(response, "Weld Penetration Depth")
        self.assertNotContains(response, "Orphan Characteristic")

    def test_system_filter_matches_via_product_chain(self):
        response = self.client.get(
            reverse("fmea:product_characteristic_list"), {"system": self.system_optical.stable_id}
        )

        self.assertContains(response, "Seal Flatness")
        self.assertNotContains(response, "Weld Penetration Depth")

    def test_system_filter_matches_via_process_chain(self):
        response = self.client.get(
            reverse("fmea:product_characteristic_list"), {"system": self.system_weld.stable_id}
        )

        self.assertContains(response, "Weld Penetration Depth")
        self.assertNotContains(response, "Seal Flatness")

    def test_links_tab_links_out_to_characteristics_flow_without_duplicating_controls(self):
        response = self.client.get(
            reverse("fmea:product_characteristic_list"),
            {"selected": self.characteristic_product.stable_id, "tab": "links"},
        )

        self.assertContains(response, "Weld Penetration Depth")
        expected_href = (
            f'href="{reverse("fmea:characteristic_link_list")}?characteristic={self.characteristic_product.pk}"'
        )
        self.assertContains(response, expected_href)
        self.assertNotContains(response, "New Link")

    def test_unrecognized_tab_defaults_to_general_without_500(self):
        response = self.client.get(
            reverse("fmea:product_characteristic_list"),
            {"selected": self.characteristic_product.stable_id, "tab": "not-a-real-tab"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "general")

    def test_invalid_selected_id_returns_404_not_500(self):
        response = self.client.get(reverse("fmea:product_characteristic_list"), {"selected": "does-not-exist"})

        self.assertEqual(response.status_code, 404)

    def test_post_to_list_and_selected_are_rejected_not_silently_accepted(self):
        list_response = self.client.post(reverse("fmea:product_characteristic_list"))
        self.assertEqual(list_response.status_code, 405)

        selected_response = self.client.post(
            reverse("fmea:product_characteristic_list"), {"selected": self.characteristic_product.stable_id}
        )
        self.assertEqual(selected_response.status_code, 405)

    def test_page_has_no_create_edit_delete_controls(self):
        response = self.client.get(reverse("fmea:product_characteristic_list"))

        for excluded in (
            "<form method=\"post\"",
            "New Characteristic",
            "Add Characteristic",
            "Edit Characteristic",
            "Delete Characteristic",
            ">Edit<",
            ">Delete<",
            ">New<",
            ">Add<",
        ):
            self.assertNotContains(response, excluded)

    def test_no_speculative_chart_or_ajax_content(self):
        response = self.client.get(reverse("fmea:product_characteristic_list"))

        for excluded in ("<canvas", "fetch(", "XMLHttpRequest", "Monitoring Status"):
            self.assertNotContains(response, excluded)

    def test_sidebar_has_a_real_working_product_characteristics_link(self):
        response = self.client.get("/")

        self.assertContains(response, "Product Characteristics")
        self.assertContains(response, f'href="{reverse("fmea:product_characteristic_list")}"')

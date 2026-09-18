from __future__ import annotations

from urllib.parse import quote

from django.test import TestCase
from django.urls import reverse

from fmea_app import models
from fmea_app.models import (
    CharacteristicLink,
    ClassificationScheme,
    ClassificationTerm,
    FMEA,
    Function,
    Operation,
    Process,
    Product,
    ProductCharacteristic,
    Requirement,
    System,
)


class CharacteristicLinkTests(TestCase):
    def setUp(self) -> None:
        self.characteristic_a = models.ProductCharacteristic.objects.create(
            stable_id="pc:characteristic-link-a", name="Bracket Flatness"
        )
        self.characteristic_b = models.ProductCharacteristic.objects.create(
            stable_id="pc:characteristic-link-b", name="Weld Strength"
        )
        self.characteristic_c = models.ProductCharacteristic.objects.create(
            stable_id="pc:characteristic-link-c", name="Fastener Torque"
        )
        self.link_ab = models.CharacteristicLink.objects.create(
            stable_id="characteristic-link:a-to-b",
            from_characteristic=self.characteristic_a,
            to_characteristic=self.characteristic_b,
            relationship_type="drives",
            strength="high",
            created_by="Alex Reviewer",
        )
        self.link_bc = models.CharacteristicLink.objects.create(
            stable_id="characteristic-link:b-to-c",
            from_characteristic=self.characteristic_b,
            to_characteristic=self.characteristic_c,
            relationship_type="constrained_by",
            strength="medium",
            created_by="Jamie Reviewer",
        )

    def test_list_renders_both_characteristic_names_and_relationship_fields(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"))

        self.assertContains(response, "Bracket Flatness")
        self.assertContains(response, "Weld Strength")
        self.assertContains(response, "Drives")
        self.assertContains(response, "High")
        self.assertContains(response, "Alex Reviewer")

    def test_relationship_type_filter_narrows_to_matching_rows(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"), {"relationship_type": "drives"})

        self.assertContains(response, "Alex Reviewer")
        self.assertNotContains(response, "Jamie Reviewer")

    def test_characteristic_filter_matches_either_from_or_to(self):
        base_url = reverse("fmea:characteristic_link_list")

        # characteristic_b is the "to" side of link_ab and the "from" side
        # of link_bc - both must appear when filtered on it.
        response = self.client.get(base_url, {"characteristic": self.characteristic_b.pk})
        self.assertContains(response, "Alex Reviewer")
        self.assertContains(response, "Jamie Reviewer")

        # characteristic_a only appears in link_ab.
        response = self.client.get(base_url, {"characteristic": self.characteristic_a.pk})
        self.assertContains(response, "Alex Reviewer")
        self.assertNotContains(response, "Jamie Reviewer")

    def test_create_view_persists_exactly_the_submitted_fields_and_redirects_to_list(self):
        response = self.client.post(
            reverse("fmea:characteristic_link_create"),
            data={
                "from_characteristic": self.characteristic_a.pk,
                "to_characteristic": self.characteristic_c.pk,
                "relationship_type": "supports",
                "strength": "critical",
                "created_by": "Morgan Reviewer",
            },
        )
        self.assertRedirects(response, reverse("fmea:characteristic_link_list"))

        created = models.CharacteristicLink.objects.get(
            from_characteristic=self.characteristic_a, to_characteristic=self.characteristic_c
        )
        self.assertEqual(created.relationship_type, "supports")
        self.assertEqual(created.strength, "critical")
        self.assertEqual(created.created_by, "Morgan Reviewer")

    def test_delete_removes_exactly_the_targeted_link_and_redirects_to_list(self):
        response = self.client.post(
            reverse("fmea:characteristic_link_delete", args=[self.link_ab.stable_id])
        )
        self.assertRedirects(response, reverse("fmea:characteristic_link_list"))

        self.assertFalse(models.CharacteristicLink.objects.filter(pk=self.link_ab.pk).exists())
        self.assertTrue(models.CharacteristicLink.objects.filter(pk=self.link_bc.pk).exists())

    def test_pages_have_no_ai_graph_or_extra_tab_content(self):
        for response in (
            self.client.get(reverse("fmea:characteristic_link_list")),
            self.client.get(reverse("fmea:characteristic_link_create")),
        ):
            for excluded in (
                "<canvas",
                "Link Matrix",
                "Link Rules",
                "Impact Paths",
                "confidence",
                "Auto Link",
            ):
                self.assertNotContains(response, excluded)

    def test_sidebar_has_a_real_working_characteristics_flow_link(self):
        response = self.client.get("/")

        self.assertContains(response, "Characteristics Flow")
        self.assertContains(response, f'href="{reverse("fmea:characteristic_link_list")}"')


class CharacteristicLinkListEnrichmentTests(TestCase):
    """Slice Q: category/system/view filters, Incoming/Outgoing detail panel,
    Coverage Summary, and the Unlinked Characteristics panel."""

    def setUp(self) -> None:
        self.scheme = ClassificationScheme.objects.create(
            stable_id="classification-scheme:link-enrich", name="Link Enrichment Scheme"
        )
        self.safety = ClassificationTerm.objects.create(
            stable_id="classification-term:link-enrich-safety", scheme=self.scheme, name="Safety", order=1
        )
        self.legal = ClassificationTerm.objects.create(
            stable_id="classification-term:link-enrich-legal", scheme=self.scheme, name="Legal", order=2
        )

        self.fmea = FMEA.objects.create(stable_id="fmea:link-enrich", name="Link Enrichment FMEA")
        self.system_a = System.objects.create(stable_id="system:link-enrich-a", name="Enrichment System A")
        self.system_b = System.objects.create(stable_id="system:link-enrich-b", name="Enrichment System B")

        # p and q both resolve to system_a via the Product chain, both Safety.
        self.product_a = Product.objects.create(
            stable_id="product:link-enrich-a", fmea=self.fmea, name="Product A", system=self.system_a
        )
        self.function_p = Function.objects.create(
            stable_id="function:link-enrich-p", product=self.product_a, name="Function P"
        )
        self.requirement_p = Requirement.objects.create(
            stable_id="requirement:link-enrich-p", function=self.function_p, name="Requirement P"
        )
        self.characteristic_p = ProductCharacteristic.objects.create(
            stable_id="pc:link-enrich-p",
            requirement=self.requirement_p,
            name="Characteristic P",
            primary_classification=self.safety,
        )
        self.function_q = Function.objects.create(
            stable_id="function:link-enrich-q", product=self.product_a, name="Function Q"
        )
        self.requirement_q = Requirement.objects.create(
            stable_id="requirement:link-enrich-q", function=self.function_q, name="Requirement Q"
        )
        self.characteristic_q = ProductCharacteristic.objects.create(
            stable_id="pc:link-enrich-q",
            requirement=self.requirement_q,
            name="Characteristic Q",
            primary_classification=self.safety,
        )

        # r and s both resolve to system_b via the Process chain, both Legal.
        self.process_b = Process.objects.create(
            stable_id="process:link-enrich-b", fmea=self.fmea, name="Process B", system=self.system_b
        )
        self.operation_b = Operation.objects.create(
            stable_id="operation:link-enrich-b", process=self.process_b, name="Operation B"
        )
        self.function_r = Function.objects.create(
            stable_id="function:link-enrich-r", operation=self.operation_b, name="Function R"
        )
        self.requirement_r = Requirement.objects.create(
            stable_id="requirement:link-enrich-r", function=self.function_r, name="Requirement R"
        )
        self.characteristic_r = ProductCharacteristic.objects.create(
            stable_id="pc:link-enrich-r",
            requirement=self.requirement_r,
            name="Characteristic R",
            primary_classification=self.legal,
        )
        self.function_s = Function.objects.create(
            stable_id="function:link-enrich-s", operation=self.operation_b, name="Function S"
        )
        self.requirement_s = Requirement.objects.create(
            stable_id="requirement:link-enrich-s", function=self.function_s, name="Requirement S"
        )
        self.characteristic_s = ProductCharacteristic.objects.create(
            stable_id="pc:link-enrich-s",
            requirement=self.requirement_s,
            name="Characteristic S",
            primary_classification=self.legal,
        )

        # t: unclassified and unlinked. u, v: classified and unlinked.
        self.characteristic_t = ProductCharacteristic.objects.create(
            stable_id="pc:link-enrich-t", name="Characteristic T"
        )
        self.characteristic_u = ProductCharacteristic.objects.create(
            stable_id="pc:link-enrich-u", name="Characteristic U", primary_classification=self.safety
        )
        self.characteristic_v = ProductCharacteristic.objects.create(
            stable_id="pc:link-enrich-v", name="Characteristic V", primary_classification=self.legal
        )

        # w: standalone Safety, is_special, gives p a second (incoming) link so
        # the detail panel's Incoming vs Outgoing lists can be checked for mixing.
        self.characteristic_w = ProductCharacteristic.objects.create(
            stable_id="pc:link-enrich-w", name="Characteristic W", primary_classification=self.safety, is_special=True
        )

        self.link_p_to_q = CharacteristicLink.objects.create(
            stable_id="characteristic-link:link-enrich-p-q",
            from_characteristic=self.characteristic_p,
            to_characteristic=self.characteristic_q,
            relationship_type="drives",
            strength="high",
        )
        self.link_r_to_s = CharacteristicLink.objects.create(
            stable_id="characteristic-link:link-enrich-r-s",
            from_characteristic=self.characteristic_r,
            to_characteristic=self.characteristic_s,
            relationship_type="influences",
            strength="medium",
        )
        self.link_w_to_p = CharacteristicLink.objects.create(
            stable_id="characteristic-link:link-enrich-w-p",
            from_characteristic=self.characteristic_w,
            to_characteristic=self.characteristic_p,
            relationship_type="supports",
            strength="low",
        )

        # Fixture summary: 8 characteristics total (p, q, r, s, t, u, v, w);
        # linked = p, q, r, s, w (5); unlinked = t, u, v (3); 3 links total.

    def test_category_filter_narrows_links_and_unlinked_panel(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"), {"category": self.safety.stable_id})

        link_pks = {link.pk for link in response.context["links"]}
        self.assertIn(self.link_p_to_q.pk, link_pks)
        self.assertIn(self.link_w_to_p.pk, link_pks)
        self.assertNotIn(self.link_r_to_s.pk, link_pks)

        unlinked_names = {c.name for c in response.context["unlinked_characteristics"]}
        self.assertEqual(unlinked_names, {"Characteristic U"})

    def test_system_filter_matches_via_product_chain(self):
        response = self.client.get(
            reverse("fmea:characteristic_link_list"), {"system": self.system_a.stable_id}
        )

        link_pks = {link.pk for link in response.context["links"]}
        self.assertIn(self.link_p_to_q.pk, link_pks)
        self.assertNotIn(self.link_r_to_s.pk, link_pks)

    def test_system_filter_matches_via_process_chain(self):
        response = self.client.get(
            reverse("fmea:characteristic_link_list"), {"system": self.system_b.stable_id}
        )

        link_pks = {link.pk for link in response.context["links"]}
        self.assertIn(self.link_r_to_s.pk, link_pks)
        self.assertNotIn(self.link_p_to_q.pk, link_pks)

    def test_view_filter_unlinked_only_narrows_coverage_and_panel(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"), {"view": "unlinked-only"})

        self.assertEqual(response.context["coverage_total_in_view"], 3)
        self.assertEqual(response.context["coverage_linked_in_view"], 0)
        self.assertEqual(response.context["coverage_unlinked_in_view"], 3)
        names = {c.name for c in response.context["unlinked_characteristics"]}
        self.assertEqual(names, {"Characteristic T", "Characteristic U", "Characteristic V"})

    def test_view_filter_linked_only_narrows_coverage_and_panel(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"), {"view": "linked-only"})

        self.assertEqual(response.context["coverage_total_in_view"], 5)
        self.assertEqual(response.context["coverage_linked_in_view"], 5)
        self.assertEqual(response.context["coverage_unlinked_in_view"], 0)
        self.assertEqual(list(response.context["unlinked_characteristics"]), [])

    def test_coverage_summary_and_unlinked_panel_match_known_fixture(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"))

        self.assertEqual(response.context["coverage_total_in_view"], 8)
        self.assertEqual(response.context["coverage_linked_in_view"], 5)
        self.assertEqual(response.context["coverage_unlinked_in_view"], 3)
        self.assertEqual(response.context["coverage_total_link_count"], 3)

        names = {c.name for c in response.context["unlinked_characteristics"]}
        self.assertEqual(names, {"Characteristic T", "Characteristic U", "Characteristic V"})
        for characteristic in response.context["unlinked_characteristics"]:
            expected_href = (
                f'href="{reverse("fmea:product_characteristic_list")}?selected='
                f'{quote(characteristic.stable_id)}"'
            )
            self.assertContains(response, expected_href)

    def test_detail_panel_incoming_and_outgoing_do_not_mix(self):
        response = self.client.get(
            reverse("fmea:characteristic_link_list"), {"selected": self.characteristic_p.stable_id}
        )

        incoming_names = {link.from_characteristic.name for link in response.context["selected_incoming_links"]}
        outgoing_names = {link.to_characteristic.name for link in response.context["selected_outgoing_links"]}
        self.assertEqual(incoming_names, {"Characteristic W"})
        self.assertEqual(outgoing_names, {"Characteristic Q"})

    def test_detail_panel_invalid_selected_returns_404_not_500(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"), {"selected": "does-not-exist"})

        self.assertEqual(response.status_code, 404)

    def test_category_and_special_badges_render_real_facts(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"))

        self.assertContains(response, "Unclassified")
        self.assertContains(response, "Special")
        self.assertContains(response, "Safety")
        self.assertContains(response, "Legal")

    def test_no_status_field_on_characteristic_link(self):
        field_names = {field.name for field in CharacteristicLink._meta.get_fields()}
        self.assertNotIn("status", field_names)

    def test_no_ai_suggestion_or_diagram_content_added(self):
        response = self.client.get(reverse("fmea:characteristic_link_list"))

        for excluded in (
            "<canvas",
            "confirmed",
            "suggested",
            "Suggested",
            "Confirmed",
            "Possible Link",
            "Auto Link",
            "confidence",
        ):
            self.assertNotContains(response, excluded)

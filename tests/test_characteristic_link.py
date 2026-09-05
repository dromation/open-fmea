from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from fmea_app import models


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

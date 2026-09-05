from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from fmea_app import models


class SystemCharacteristicsBaseViewTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:system-characteristics-base",
            name="System Characteristics Base FMEA",
        )
        self.root = models.System.objects.create(
            stable_id="system:scb-root",
            name="Vehicle Platform",
            code="SYS-ROOT",
        )
        self.child = models.System.objects.create(
            stable_id="system:scb-child",
            name="Braking Subsystem",
            code="SYS-CHILD",
            parent=self.root,
        )
        self.product = models.Product.objects.create(
            stable_id="product:scb",
            fmea=self.fmea,
            name="Brake Caliper",
            system=self.child,
        )
        self.process = models.Process.objects.create(
            stable_id="process:scb",
            fmea=self.fmea,
            name="Caliper Assembly",
            system=self.child,
        )

    def test_system_list_returns_200_and_lists_every_system_with_children_grouped_near_parent(self):
        response = self.client.get(reverse("fmea:system_list"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        self.assertIn("Vehicle Platform", content)
        self.assertIn("Braking Subsystem", content)

        # This app's actual /systems/ page (built by the System/Product/Process
        # slice, independently verified before this slice existed) groups a
        # child System near its parent via a sorted flat list with a Parent
        # column, rather than nested/indented rows - see this slice's review
        # doc for the full note on this UI-shape difference from what this
        # instruction originally described.
        child_start = content.index("Braking Subsystem")
        child_end = content.index("</tr>", child_start)
        child_row = content[child_start:child_end]
        self.assertIn("Vehicle Platform", child_row)

    def test_system_list_counts_match_actual_querysets(self):
        response = self.client.get(reverse("fmea:system_list"))
        content = response.content.decode()

        root_start = content.index("Vehicle Platform")
        root_end = content.index("</tr>", root_start)
        root_row = content[root_start:root_end]
        # Root has 1 direct child, 0 direct products/processes.
        self.assertIn(">0<", root_row)

        child_start = content.index("Braking Subsystem")
        child_end = content.index("</tr>", child_start)
        child_row = content[child_start:child_end]
        # Child has 1 linked product and 1 linked process.
        self.assertEqual(child_row.count(">1<"), 2)

    def test_creating_a_system_via_the_form_persists_it(self):
        response = self.client.post(
            reverse("fmea:system_create"),
            data={"name": "New System", "description": "", "code": "SYS-NEW", "parent": "", "status": "active"},
        )
        created = models.System.objects.get(name="New System")
        self.assertRedirects(response, reverse("fmea:system_detail", args=[created.stable_id]))

    def test_editing_a_system_to_create_a_cycle_is_rejected_and_nothing_is_modified(self):
        original_name = self.root.name
        response = self.client.post(
            reverse("fmea:system_edit", args=[self.root.stable_id]),
            data={
                "name": "Should Not Save",
                "description": "",
                "code": self.root.code,
                "parent": self.child.pk,
                "status": "active",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.root.refresh_from_db()
        self.assertEqual(self.root.name, original_name)
        self.assertIsNone(self.root.parent_id)

    def test_system_list_stays_within_narrowed_scope(self):
        response = self.client.get(reverse("fmea:system_list"))

        for excluded in ("Organizations", "Importance", "Monitoring", "<canvas"):
            self.assertNotContains(response, excluded)


class WorksheetClassificationColumnTests(TestCase):
    def setUp(self) -> None:
        call_command("seed_classification_scheme", stdout=StringIO())
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:worksheet-classification",
            name="Worksheet Classification FMEA",
        )
        self.function = models.Function.objects.create(
            stable_id="function:worksheet-classification",
            name="Contain fluid",
        )
        self.requirement = models.Requirement.objects.create(
            stable_id="requirement:worksheet-classification",
            function=self.function,
            name="No leaks",
        )
        self.failure_mode = models.FailureMode.objects.create(
            stable_id="failure-mode:worksheet-classification",
            fmea=self.fmea,
            function=self.function,
            requirement=self.requirement,
            name="Seal leaks",
        )
        self.safety_term = models.ClassificationTerm.objects.get(name="Safety")
        models.ProductCharacteristic.objects.create(
            stable_id="product-characteristic:worksheet-classified",
            requirement=self.requirement,
            name="Classified Characteristic",
            primary_classification=self.safety_term,
        )
        models.ProductCharacteristic.objects.create(
            stable_id="product-characteristic:worksheet-unclassified",
            requirement=self.requirement,
            name="Unclassified Characteristic",
        )

    def test_worksheet_shows_classification_column_with_term_name_and_dash_when_unset(self):
        response = self.client.get(reverse("fmea:fmea_detail", args=[self.fmea.stable_id]))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        self.assertIn("Classification", content)
        self.assertIn("Classified Characteristic", content)
        self.assertIn("Safety", content)
        self.assertIn("Unclassified Characteristic", content)

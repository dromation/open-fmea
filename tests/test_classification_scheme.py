from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from fmea_app import models


class ClassificationSchemeSeedTests(TestCase):
    def test_seed_classification_scheme_is_idempotent(self):
        stdout = StringIO()
        call_command("seed_classification_scheme", stdout=stdout)
        call_command("seed_classification_scheme", stdout=stdout)

        self.assertEqual(models.ClassificationScheme.objects.count(), 1)
        scheme = models.ClassificationScheme.objects.get()
        self.assertEqual(scheme.name, "Product Characteristic Classification (default)")
        self.assertEqual(models.ClassificationTerm.objects.count(), 4)
        self.assertEqual(
            list(models.ClassificationTerm.objects.order_by("order").values_list("name", flat=True)),
            ["Legal", "Safety", "Functional", "Decorative"],
        )
        self.assertIn("Seeded classification scheme", stdout.getvalue())


class ProductCharacteristicClassificationTests(TestCase):
    def setUp(self) -> None:
        call_command("seed_classification_scheme", stdout=StringIO())
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:classification-scheme",
            name="Classification Scheme FMEA",
        )
        self.function = models.Function.objects.create(
            stable_id="function:classification-scheme",
            name="Contain fluid",
        )
        self.requirement = models.Requirement.objects.create(
            stable_id="requirement:classification-scheme",
            function=self.function,
            name="No leaks",
        )
        self.safety_term = models.ClassificationTerm.objects.get(name="Safety")

    def test_product_characteristic_with_classification_round_trips_correctly(self):
        characteristic = models.ProductCharacteristic.objects.create(
            stable_id="product-characteristic:classification-scheme-classified",
            requirement=self.requirement,
            name="Seal seat surface condition",
            primary_classification=self.safety_term,
        )
        characteristic.refresh_from_db()
        self.assertEqual(characteristic.primary_classification_id, self.safety_term.pk)
        self.assertEqual(characteristic.primary_classification.name, "Safety")

        domain = characteristic.to_domain()
        self.assertEqual(domain.primary_classification_id, self.safety_term.stable_id)

    def test_product_characteristic_without_classification_displays_as_unclassified_not_error(self):
        characteristic = models.ProductCharacteristic.objects.create(
            stable_id="product-characteristic:classification-scheme-unclassified",
            requirement=self.requirement,
            name="Unclassified characteristic",
        )
        characteristic.refresh_from_db()
        self.assertIsNone(characteristic.primary_classification)

        domain = characteristic.to_domain()
        self.assertIsNone(domain.primary_classification_id)

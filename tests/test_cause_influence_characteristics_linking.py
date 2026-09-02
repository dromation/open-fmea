from __future__ import annotations

from django.core.management import call_command
from django.test import TestCase

from fmea_app import models
from fmea_app.services import DomainConstructionError, create_cause_influence
from fmea_domain import CauseInfluenceStatus


class CauseInfluenceCharacteristicsLinkingTests(TestCase):
    def setUp(self) -> None:
        call_command("seed_cause_category_scheme")
        self.method_category = models.CauseCategory.objects.get(name="Method")
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:characteristics-linking",
            name="Characteristics Linking FMEA",
        )
        self.process = models.Process.objects.create(
            stable_id="process:characteristics-linking",
            fmea=self.fmea,
            name="Assembly",
        )
        self.operation = models.Operation.objects.create(
            stable_id="operation:characteristics-linking-install-seal",
            process=self.process,
            name="Install seal",
            sequence="20",
        )
        self.function = models.Function.objects.create(
            stable_id="function:characteristics-linking",
            operation=self.operation,
            name="Maintain hydraulic pressure",
        )
        self.requirement = models.Requirement.objects.create(
            stable_id="requirement:characteristics-linking",
            function=self.function,
            name="No external leakage",
        )
        self.product_characteristic = models.ProductCharacteristic.objects.create(
            stable_id="product-characteristic:seal-seat-surface",
            requirement=self.requirement,
            name="Seal seat surface condition",
        )
        self.process_characteristic = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:seal-installation-force",
            operation=self.operation,
            name="Seal installation force",
            cause_category_id=self.method_category.stable_id,
            attributes={"nominal": "controlled insertion"},
        )
        self.failure_mode = models.FailureMode.objects.create(
            stable_id="failure-mode:characteristics-linking-seal-leak",
            fmea=self.fmea,
            function=self.function,
            requirement=self.requirement,
            name="Seal leaks after assembly",
        )

    def test_process_characteristic_to_product_characteristic_influence_is_legal(self):
        influence = create_cause_influence(
            source_type="ProcessCharacteristic",
            source_id=self.process_characteristic.stable_id,
            target_type="ProductCharacteristic",
            target_id=self.product_characteristic.stable_id,
            influence_type="affects",
            cause_category_id=self.method_category.stable_id,
        )

        self.assertEqual(influence.status, CauseInfluenceStatus.SUSPECTED.value)
        detail = self.client.get(
            f"/process-characteristics/{self.process_characteristic.stable_id}/"
        )
        self.assertContains(detail, "Seal seat surface condition")
        self.assertContains(detail, "affects")

    def test_product_characteristic_target_cannot_be_confirmed_root_cause(self):
        with self.assertRaisesRegex(DomainConstructionError, "confirmed_root_cause"):
            create_cause_influence(
                source_type="ProcessCharacteristic",
                source_id=self.process_characteristic.stable_id,
                target_type="ProductCharacteristic",
                target_id=self.product_characteristic.stable_id,
                influence_type="affects",
                status=CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE.value,
                cause_category_id=self.method_category.stable_id,
            )

    def test_characteristic_chain_is_constructible_without_widening_product_source(self):
        influence = create_cause_influence(
            source_type="ProcessCharacteristic",
            source_id=self.process_characteristic.stable_id,
            target_type="ProductCharacteristic",
            target_id=self.product_characteristic.stable_id,
            influence_type="affects",
            cause_category_id=self.method_category.stable_id,
        )

        self.assertEqual(influence.target_id, self.product_characteristic.stable_id)
        self.assertEqual(self.product_characteristic.requirement, self.requirement)
        self.assertEqual(self.failure_mode.requirement, self.requirement)
        self.assertEqual(self.failure_mode.effects.count(), 0)


if __name__ == "__main__":
    unittest.main()

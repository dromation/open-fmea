from __future__ import annotations

from django.core.management import call_command
from django.test import TestCase

from fmea_app import models
from fmea_app.services import create_cause_influence


class ProcessFlowViewTests(TestCase):
    def setUp(self) -> None:
        call_command("seed_cause_category_scheme")
        self.method_category = models.CauseCategory.objects.get(name="Method")

        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:process-flow",
            name="Process Flow FMEA",
        )
        self.process = models.Process.objects.create(
            stable_id="process:process-flow-assembly",
            fmea=self.fmea,
            name="Assembly",
        )
        self.operation_a = models.Operation.objects.create(
            stable_id="operation:process-flow-station-10",
            process=self.process,
            name="Install bracket",
            sequence="10",
        )
        self.operation_b = models.Operation.objects.create(
            stable_id="operation:process-flow-station-20",
            process=self.process,
            name="Install seal",
            sequence="20",
        )

        self.characteristic_a = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:process-flow-bracket-torque",
            operation=self.operation_a,
            name="Bracket torque",
            attributes={"nominal": "12 Nm"},
        )
        self.characteristic_b = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:process-flow-installation-force",
            operation=self.operation_b,
            name="Seal installation force",
            cause_category_id=self.method_category.stable_id,
            attributes={"nominal": "controlled manual insertion"},
        )

        self.product_characteristic = models.ProductCharacteristic.objects.create(
            stable_id="characteristic:process-flow-seal-seat-condition",
            name="Seal seat surface condition",
        )

    def test_selecting_operation_shows_only_its_own_process_characteristics(self):
        response = self.client.get(
            f"/processes/{self.process.stable_id}/flow/",
            {"operation_id": self.operation_b.stable_id},
        )

        self.assertContains(response, "Seal installation force")
        self.assertNotContains(response, "Bracket torque")

    def test_linked_product_characteristics_only_shows_reachable_ones(self):
        create_cause_influence(
            source_type="ProcessCharacteristic",
            source_id=self.characteristic_b.stable_id,
            target_type="ProductCharacteristic",
            target_id=self.product_characteristic.stable_id,
            influence_type="affects",
            cause_category_id=self.method_category.stable_id,
        )

        response_b = self.client.get(
            f"/processes/{self.process.stable_id}/flow/",
            {"operation_id": self.operation_b.stable_id},
        )
        self.assertContains(response_b, "Seal seat surface condition")

        response_a = self.client.get(
            f"/processes/{self.process.stable_id}/flow/",
            {"operation_id": self.operation_a.stable_id},
        )
        self.assertNotContains(response_a, "Seal seat surface condition")

    def test_response_has_no_type_or_criticality_column(self):
        create_cause_influence(
            source_type="ProcessCharacteristic",
            source_id=self.characteristic_b.stable_id,
            target_type="ProductCharacteristic",
            target_id=self.product_characteristic.stable_id,
            influence_type="affects",
            cause_category_id=self.method_category.stable_id,
        )

        response = self.client.get(
            f"/processes/{self.process.stable_id}/flow/",
            {"operation_id": self.operation_b.stable_id},
        )

        self.assertNotContains(response, "Criticality")
        self.assertNotContains(response, "<th>Type</th>")

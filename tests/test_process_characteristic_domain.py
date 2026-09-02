from __future__ import annotations

import unittest

from django.test import TestCase

from fmea_app import models
from fmea_domain import ProcessCharacteristic


class ProcessCharacteristicDomainTests(unittest.TestCase):
    def test_process_characteristic_constructs_with_attributes(self):
        characteristic = ProcessCharacteristic(
            stable_id="process-characteristic:installation-force",
            operation_id="operation:install-seal",
            name="Seal installation force",
            cause_category_id="cause-category:ishikawa-5me:method",
            attributes={
                "nominal": "controlled manual insertion",
                "observed": "operator-dependent variation",
            },
        )

        self.assertEqual(characteristic.operation_id, "operation:install-seal")
        self.assertEqual(characteristic.attributes["nominal"], "controlled manual insertion")

    def test_process_characteristic_requires_operation_id(self):
        with self.assertRaisesRegex(ValueError, "stable_id"):
            ProcessCharacteristic(
                stable_id="process-characteristic:missing-operation",
                operation_id="",
                name="Seal installation force",
            )

    def test_process_characteristic_requires_attributes_dict(self):
        with self.assertRaisesRegex(ValueError, "attributes"):
            ProcessCharacteristic(
                stable_id="process-characteristic:bad-attributes",
                operation_id="operation:install-seal",
                name="Seal installation force",
                attributes=["not", "a", "dict"],  # type: ignore[arg-type]
            )


class ProcessCharacteristicDjangoTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:process-characteristic",
            name="Process Characteristic FMEA",
        )
        self.process = models.Process.objects.create(
            stable_id="process:assembly",
            fmea=self.fmea,
            name="Assembly",
        )
        self.operation = models.Operation.objects.create(
            stable_id="operation:install-seal",
            process=self.process,
            name="Install seal",
            sequence="20",
        )

    def test_model_persists_instance_level_process_characteristic(self):
        characteristic = models.ProcessCharacteristic.objects.create(
            stable_id="process-characteristic:installation-force-model",
            operation=self.operation,
            name="Seal installation force",
            attributes={"nominal": "controlled insertion"},
        )

        domain = characteristic.to_domain()
        self.assertEqual(domain.operation_id, self.operation.stable_id)
        self.assertEqual(domain.attributes, {"nominal": "controlled insertion"})

    def test_minimal_crud_views_render_and_create(self):
        response = self.client.get("/process-characteristics/")
        self.assertContains(response, "Process Characteristics")

        response = self.client.post(
            "/process-characteristics/new/",
            {
                "operation": self.operation.pk,
                "name": "Seal installation force",
                "description": "Force applied while seating the seal.",
                "cause_category_id": "",
                "attributes": '{"nominal": "controlled insertion"}',
            },
        )

        self.assertEqual(response.status_code, 302)
        characteristic = models.ProcessCharacteristic.objects.get()
        detail = self.client.get(f"/process-characteristics/{characteristic.stable_id}/")
        self.assertContains(detail, "Seal installation force")
        self.assertContains(detail, "controlled insertion")


if __name__ == "__main__":
    unittest.main()

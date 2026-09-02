from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

from django.test import TestCase

from fmea_app import models as fmea_models
from fmea_ingestion.parsers import parse_xlsx_workbook
from fmea_review import models as review_models


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domain"))
sys.path.insert(0, str(ROOT / "django_app"))


class ProductCharacteristicRenameTests(TestCase):
    def test_product_characteristic_replaces_existing_model_behavior(self):
        function = fmea_models.Function.objects.create(
            stable_id="function:product-characteristic-rename",
            name="Maintain pressure",
        )
        requirement = fmea_models.Requirement.objects.create(
            stable_id="requirement:product-characteristic-rename",
            function=function,
            name="No external leakage",
        )

        characteristic = fmea_models.ProductCharacteristic.objects.create(
            stable_id="product-characteristic:seal-seat-condition",
            requirement=requirement,
            name="Seal seat surface condition",
            is_special=True,
        )

        domain = characteristic.to_domain()
        self.assertEqual(domain.name, "Seal seat surface condition")
        self.assertEqual(domain.requirement_id, requirement.stable_id)
        self.assertTrue(domain.is_special)
        self.assertIsNone(domain.primary_classification_id)
        self.assertEqual(
            list(requirement.product_characteristics.values_list("stable_id", flat=True)),
            [characteristic.stable_id],
        )

    def test_import_candidate_type_backfill_migration_updates_old_values(self):
        session = review_models.ImportSession.objects.create(
            stable_id="session:product-characteristic-backfill",
            source_filename="legacy.xlsx",
            document_version="a" * 64,
            status="reviewing",
        )
        row_group = review_models.FmeaRowGroup.objects.create(
            stable_id="row-group:product-characteristic-backfill",
            session=session,
            sheet_name="PFMEA",
            row_start=7,
            row_end=7,
            source_range="PFMEA!7:7",
            parser_version="ooxml-v1",
            detected_fields={
                "Characteristic": ["Seal seat surface condition"],
                "FailureMode": ["Seal leaks"],
            },
        )
        review_models.ImportCandidateRecord.objects.create(
            stable_id="candidate:product-characteristic-backfill",
            session=session,
            row_group=row_group,
            extracted_value="Seal seat surface condition",
            suggested_domain_type="Characteristic",
            source_document_id="xlsx:aaaaaaaaaaaaaaaa",
            document_version="a" * 64,
            workbook_name="legacy.xlsx",
            sheet_name="PFMEA",
            row_number=7,
            column_name="Product Characteristics ID/Description",
            extraction_method="deterministic",
            parser_version="ooxml-v1",
        )

        migration = importlib.import_module(
            "fmea_review.migrations.0003_backfill_product_characteristic_candidate_type"
        )
        migration.forwards(_MigrationApps(), None)

        record = review_models.ImportCandidateRecord.objects.get()
        row_group.refresh_from_db()
        self.assertEqual(record.suggested_domain_type, "ProductCharacteristic")
        self.assertNotIn("Characteristic", row_group.detected_fields)
        self.assertEqual(
            row_group.detected_fields["ProductCharacteristic"],
            ["Seal seat surface condition"],
        )


class RealWorkbookProductCharacteristicTests(unittest.TestCase):
    def test_real_workbook_counts_are_unchanged_after_rename(self):
        fixtures = (
            (ROOT / "samples" / "open_fmea" / "FMEA_templates.xlsx", 1904),
            (ROOT / "samples" / "open_fmea" / "examples" / "FMEA_442710252570.00.xlsx", 316),
            (ROOT / "samples" / "open_fmea" / "examples" / "PPAP_Prirobnica.XX2.xlsx", 198),
        )

        for path, expected_count in fixtures:
            with self.subTest(path=path.name):
                candidates = parse_xlsx_workbook(path)
                self.assertEqual(len(candidates), expected_count)
                self.assertNotIn(
                    "Characteristic",
                    {candidate.suggested_domain_type for candidate in candidates},
                )


class _MigrationApps:
    def get_model(self, app_label: str, model_name: str):
        if app_label != "fmea_review":
            raise LookupError(app_label)
        return getattr(review_models, model_name)


if __name__ == "__main__":
    unittest.main()

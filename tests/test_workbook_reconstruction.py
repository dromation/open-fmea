from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domain"))
sys.path.insert(0, str(ROOT / "django_app"))

from fmea_ingestion import reconstruct_fmea_row_groups  # noqa: E402
from fmea_ingestion.parsers import parse_xlsx_workbook  # noqa: E402


class WorkbookReconstructionTests(unittest.TestCase):
    def test_cell_candidates_are_grouped_into_logical_fmea_rows(self):
        fixture = ROOT / "tests" / "fixtures" / "sample_fmea_minimal.xlsx"

        candidates = parse_xlsx_workbook(fixture)
        row_groups = reconstruct_fmea_row_groups(candidates)

        self.assertEqual(len(row_groups), 3)
        first = row_groups[0]
        self.assertEqual(first.source_range, "Process FMEA!2:2")
        self.assertEqual(first.mapped_candidate_count, 7)
        self.assertEqual(first.unmapped_candidate_count, 1)
        self.assertEqual(first.detected_fields["Function"], ["Seal hydraulic pressure"])
        self.assertEqual(first.detected_fields["Requirement"], ["No external leakage"])
        self.assertEqual(first.detected_fields["FailureMode"], ["Seal leaks"])
        self.assertEqual(first.detected_fields["FailureEffect"], ["Brake fluid loss"])
        self.assertEqual(first.detected_fields["FailureCause"], ["Seal nicked during assembly"])
        self.assertEqual(first.detected_fields["PreventionControl"], ["Lubricate seal before install"])
        self.assertEqual(first.detected_fields["DetectionControl"], ["Visual leak test"])
        self.assertTrue(first.stable_id.startswith("row-group:"))

    def test_row_group_ids_are_deterministic(self):
        fixture = ROOT / "tests" / "fixtures" / "sample_fmea_minimal.xlsx"

        first = reconstruct_fmea_row_groups(parse_xlsx_workbook(fixture))
        second = reconstruct_fmea_row_groups(parse_xlsx_workbook(fixture))

        self.assertEqual(
            [row_group.stable_id for row_group in first],
            [row_group.stable_id for row_group in second],
        )


if __name__ == "__main__":
    unittest.main()

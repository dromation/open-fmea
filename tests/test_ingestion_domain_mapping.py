from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domain"))
sys.path.insert(0, str(ROOT / "django_app"))

from fmea_ai.providers.disabled_provider import DisabledProvider  # noqa: E402
from fmea_ingestion import ImportCandidate, ReviewStatus, SourceProvenance  # noqa: E402
from fmea_ingestion.mapping import build_candidate, enrich_candidate_with_ai, map_header  # noqa: E402


class IngestionDomainMappingTests(unittest.TestCase):
    def test_ingestion_and_ai_import_without_django(self):
        code = (
            "import sys; "
            f"sys.path.insert(0, {str(ROOT / 'domain')!r}); "
            f"sys.path.insert(0, {str(ROOT / 'django_app')!r}); "
            "import fmea_ingestion, fmea_ai; "
            "print(any(name == 'django' or name.startswith('django.') for name in sys.modules))"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), "False")

    def test_candidate_contract_validates_review_status_and_domain_type(self):
        candidate = ImportCandidate(
            stable_id="candidate:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            extracted_value="Seal leaks",
            suggested_domain_type="FailureMode",
            provenance=_provenance("Potential Failure Mode"),
            parsing_confidence=1.0,
        )

        self.assertEqual(candidate.review_status, ReviewStatus.UNREVIEWED)
        self.assertEqual(
            candidate.with_review_status(ReviewStatus.REJECTED).review_status,
            ReviewStatus.REJECTED,
        )

    def test_known_header_variants_map_to_existing_domain_types(self):
        self.assertEqual(map_header("Potential Failure Mode").suggested_domain_type, "FailureMode")
        self.assertEqual(map_header("current-prevention/control").suggested_domain_type, "PreventionControl")
        self.assertEqual(map_header("Requirements").suggested_domain_type, "Requirement")
        self.assertEqual(
            map_header("Product Characteristics ID/Description").suggested_domain_type,
            "ProductCharacteristic",
        )
        self.assertEqual(
            map_header("Process Function/ Requirment").suggested_domain_type,
            "Function",
        )
        self.assertEqual(
            map_header(
                "Undesirable customer effects\n"
                "Effects of failure on syst. / part / operation"
            ).suggested_domain_type,
            "FailureEffect",
        )
        self.assertEqual(map_header("Causes of failure").suggested_domain_type, "FailureCause")
        self.assertEqual(map_header("Testing - Simulation").suggested_domain_type, "DetectionControl")

    def test_unmapped_column_becomes_candidate_with_validation_issue(self):
        candidate = build_candidate(
            stable_id="candidate:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            extracted_value="Line note A",
            column_header="Unexpected Column",
            provenance=_provenance("Unexpected Column"),
        )

        self.assertEqual(candidate.suggested_domain_type, "unmapped")
        self.assertEqual(candidate.parsing_confidence, 0.0)
        self.assertIn("Unmapped column header", candidate.validation_issues[0])

    def test_ai_disabled_fallback_keeps_deterministic_candidate(self):
        candidate = build_candidate(
            stable_id="candidate:cccccccccccccccccccccccccccccccc",
            extracted_value="Seal leaks",
            column_header="Failure Mode",
            provenance=_provenance("Failure Mode"),
        )

        enriched = enrich_candidate_with_ai(candidate, DisabledProvider(), enabled=False)

        self.assertEqual(enriched, candidate)
        self.assertIsNone(enriched.ai_confidence)


def _provenance(column_name: str) -> SourceProvenance:
    return SourceProvenance(
        source_document_id="xlsx:aaaaaaaaaaaaaaaa",
        document_version="a" * 64,
        workbook_name="sample.xlsx",
        sheet_name="Process FMEA",
        row_number=2,
        column_name=column_name,
        extraction_method="deterministic",
        parser_version="ooxml-v1",
    )


if __name__ == "__main__":
    unittest.main()

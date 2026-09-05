from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from fmea_ingestion import ReviewStatus
from fmea_review.models import ImportCandidateRecord, ImportSession


class AiCorpusExportTests(TestCase):
    def test_export_ai_corpus_writes_reviewed_jsonl_examples(self):
        session = ImportSession.objects.create(
            stable_id="session:ai-corpus",
            source_filename="source.xlsx",
            document_version="a" * 64,
            status="reviewing",
        )
        ImportCandidateRecord.objects.create(
            stable_id="candidate:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            session=session,
            extracted_value="Seal leaks",
            suggested_domain_type="FailureMode",
            source_document_id="xlsx:aaaaaaaaaaaaaaaa",
            document_version="a" * 64,
            workbook_name="source.xlsx",
            sheet_name="PFMEA",
            row_number=9,
            column_name="Potential Failure Mode",
            extraction_method="deterministic",
            parser_version="ooxml-v1",
            review_status=ReviewStatus.ACCEPTED.value,
            accepted_object_stable_id="failure-mode:accepted",
            reviewed_at=timezone.now(),
        )
        ImportCandidateRecord.objects.create(
            stable_id="candidate:ffffffffffffffffffffffffffffffff",
            session=session,
            extracted_value="Line note",
            suggested_domain_type="unmapped",
            source_document_id="xlsx:aaaaaaaaaaaaaaaa",
            document_version="a" * 64,
            workbook_name="source.xlsx",
            sheet_name="PFMEA",
            row_number=10,
            column_name="Unexpected Column",
            extraction_method="deterministic",
            parser_version="ooxml-v1",
            validation_issues=["Unmapped column header: Unexpected Column"],
            review_status=ReviewStatus.UNREVIEWED.value,
        )

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "ai-corpus.jsonl"
            stdout = StringIO()
            call_command("export_ai_corpus", str(output_path), stdout=stdout)

            lines = output_path.read_text(encoding="utf-8").splitlines()

        self.assertIn("Exported 1 AI corpus examples", stdout.getvalue())
        self.assertEqual(len(lines), 1)
        example = json.loads(lines[0])
        self.assertEqual(example["schema_version"], "open-fmea-ai-corpus-v1")
        self.assertEqual(example["input"]["cell_text"], "Seal leaks")
        self.assertEqual(example["input"]["suggested_domain_type"], "FailureMode")
        self.assertEqual(example["label"]["review_status"], ReviewStatus.ACCEPTED.value)
        self.assertEqual(example["label"]["accepted_object_stable_id"], "failure-mode:accepted")
        self.assertEqual(example["provenance"]["workbook_name"], "source.xlsx")

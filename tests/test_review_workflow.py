from __future__ import annotations

from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from fmea_app import models as fmea_models
from fmea_ingestion import ReviewStatus
from fmea_review.models import FmeaRowGroup, ImportCandidateRecord, ImportSession


ROOT = Path(__file__).resolve().parents[1]


class ReviewWorkflowTests(TestCase):
    def setUp(self) -> None:
        self.project = fmea_models.FMEAProject.objects.create(
            stable_id="project:review-workflow",
            name="Review Workflow",
        )
        self.fmea = fmea_models.FMEA.objects.create(
            stable_id="fmea:review-workflow",
            project=self.project,
            name="Review Workflow FMEA",
        )

    def test_upload_creates_session_and_unreviewed_candidates_only(self):
        response = self._upload("sample_fmea_minimal.xlsx")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ImportSession.objects.count(), 1)
        self.assertEqual(FmeaRowGroup.objects.count(), 3)
        self.assertEqual(ImportCandidateRecord.objects.count(), 24)
        self.assertEqual(
            ImportCandidateRecord.objects.filter(row_group__isnull=False).count(),
            24,
        )
        self.assertEqual(
            set(ImportCandidateRecord.objects.values_list("review_status", flat=True)),
            {ReviewStatus.UNREVIEWED.value},
        )
        self.assertEqual(fmea_models.FailureMode.objects.count(), 0)

    def test_accept_promotes_exactly_one_object_through_service_path(self):
        self._upload("sample_fmea_minimal.xlsx")
        record = ImportCandidateRecord.objects.get(extracted_value="Seal leaks")

        response = self.client.post(
            f"/review/candidate/{record.stable_id}/accept/",
            {"fmea_stable_id": self.fmea.stable_id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(fmea_models.FailureMode.objects.count(), 1)
        created = fmea_models.FailureMode.objects.get()
        record.refresh_from_db()
        self.assertEqual(record.review_status, ReviewStatus.ACCEPTED.value)
        self.assertEqual(record.accepted_object_stable_id, created.stable_id)
        self.assertEqual(created.name, "Seal leaks")

    def test_reject_never_creates_domain_object(self):
        self._upload("sample_fmea_minimal.xlsx")
        record = ImportCandidateRecord.objects.get(extracted_value="Piston sticks")

        response = self.client.post(
            f"/review/candidate/{record.stable_id}/reject/",
            {"reason": "Duplicate in source workbook"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(fmea_models.FailureMode.objects.count(), 0)
        record.refresh_from_db()
        self.assertEqual(record.review_status, ReviewStatus.REJECTED.value)
        self.assertIn("Duplicate", record.review_note)

    def test_accept_row_group_promotes_one_logical_fmea_chain(self):
        self._upload("sample_fmea_minimal.xlsx")
        row_group = FmeaRowGroup.objects.get(row_start=2)

        response = self.client.post(
            f"/review/row/{row_group.stable_id}/accept/",
            {"fmea_stable_id": self.fmea.stable_id},
        )

        self.assertEqual(response.status_code, 302)
        row_group.refresh_from_db()
        self.assertEqual(row_group.review_status, ReviewStatus.ACCEPTED.value)
        self.assertEqual(fmea_models.Function.objects.count(), 1)
        self.assertEqual(fmea_models.Requirement.objects.count(), 1)
        self.assertEqual(fmea_models.FailureMode.objects.count(), 1)
        self.assertEqual(fmea_models.FailureEffect.objects.count(), 1)
        self.assertEqual(fmea_models.FailureCause.objects.count(), 1)
        self.assertEqual(fmea_models.PreventionControl.objects.count(), 1)
        self.assertEqual(fmea_models.DetectionControl.objects.count(), 1)
        failure_mode = fmea_models.FailureMode.objects.get()
        self.assertEqual(failure_mode.name, "Seal leaks")
        self.assertEqual(failure_mode.function.name, "Seal hydraulic pressure")
        self.assertEqual(failure_mode.requirement.name, "No external leakage")
        self.assertEqual(
            row_group.candidates.filter(review_status=ReviewStatus.ACCEPTED.value).count(),
            7,
        )
        self.assertEqual(
            row_group.candidates.filter(review_status=ReviewStatus.NEEDS_CLARIFICATION.value).count(),
            1,
        )

    def test_reject_row_group_marks_all_grouped_candidates_rejected(self):
        self._upload("sample_fmea_minimal.xlsx")
        row_group = FmeaRowGroup.objects.get(row_start=2)

        response = self.client.post(
            f"/review/row/{row_group.stable_id}/reject/",
            {"reason": "Wrong source row"},
        )

        self.assertEqual(response.status_code, 302)
        row_group.refresh_from_db()
        self.assertEqual(row_group.review_status, ReviewStatus.REJECTED.value)
        self.assertEqual(
            set(row_group.candidates.values_list("review_status", flat=True)),
            {ReviewStatus.REJECTED.value},
        )
        self.assertEqual(fmea_models.FailureMode.objects.count(), 0)

    def test_accept_characteristic_candidate_uses_existing_domain_model(self):
        session = ImportSession.objects.create(
            stable_id="session:characteristic-review",
            source_filename="manual.xlsx",
            document_version="a" * 64,
            status="reviewing",
        )
        record = ImportCandidateRecord.objects.create(
            stable_id="candidate:dddddddddddddddddddddddddddddddd",
            session=session,
            extracted_value="Material structure",
            suggested_domain_type="ProductCharacteristic",
            source_document_id="xlsx:aaaaaaaaaaaaaaaa",
            document_version="a" * 64,
            workbook_name="manual.xlsx",
            sheet_name="PFMEA",
            row_number=9,
            column_name="Product Characteristics ID/Description",
            extraction_method="deterministic",
            parser_version="ooxml-v1",
        )

        response = self.client.post(f"/review/candidate/{record.stable_id}/accept/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(fmea_models.ProductCharacteristic.objects.count(), 1)
        characteristic = fmea_models.ProductCharacteristic.objects.get()
        record.refresh_from_db()
        self.assertEqual(record.review_status, ReviewStatus.ACCEPTED.value)
        self.assertEqual(record.accepted_object_stable_id, characteristic.stable_id)
        self.assertEqual(characteristic.name, "Material structure")

    def _upload(self, fixture_name: str):
        fixture = ROOT / "tests" / "fixtures" / fixture_name
        upload = SimpleUploadedFile(
            fixture_name,
            fixture.read_bytes(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        return self.client.post("/review/upload/", {"workbook": upload})

from __future__ import annotations

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from fmea_app import models as fmea_models
from fmea_domain import CauseInfluenceStatus
from fmea_ingestion import ReviewStatus
from fmea_review import models as review_models


class DashboardViewTests(TestCase):
    def test_dashboard_uses_real_counts_and_recent_review_activity(self):
        fmea_models.FMEA.objects.create(stable_id="fmea:dashboard-one", name="Dashboard One")
        fmea_models.FMEA.objects.create(stable_id="fmea:dashboard-two", name="Dashboard Two")
        session = review_models.ImportSession.objects.create(
            stable_id="import-session:dashboard",
            source_filename="dashboard.xlsx",
            document_version="doc-version",
        )
        row_group = review_models.FmeaRowGroup.objects.create(
            stable_id="row-group:dashboard-pending",
            session=session,
            sheet_name="PFMEA",
            row_start=4,
            row_end=4,
            source_range="PFMEA!4:4",
            parser_version="test",
            detected_fields={"FailureMode": ["Seal leaks"]},
            review_status=ReviewStatus.UNREVIEWED.value,
        )
        review_models.FmeaRowGroup.objects.create(
            stable_id="row-group:dashboard-rejected",
            session=session,
            sheet_name="PFMEA",
            row_start=5,
            row_end=5,
            source_range="PFMEA!5:5",
            parser_version="test",
            detected_fields={"FailureMode": ["Noise"]},
            review_status=ReviewStatus.REJECTED.value,
            reviewed_at=timezone.now() - timedelta(minutes=5),
        )
        review_models.ImportCandidateRecord.objects.create(
            stable_id="candidate:dashboard-pending-one",
            session=session,
            row_group=row_group,
            extracted_value="Seal leaks after assembly",
            suggested_domain_type="FailureMode",
            source_document_id="doc",
            document_version="doc-version",
            workbook_name="dashboard.xlsx",
            sheet_name="PFMEA",
            row_number=4,
            column_name="Failure Mode",
            extraction_method="deterministic",
            parser_version="test",
            review_status=ReviewStatus.UNREVIEWED.value,
        )
        review_models.ImportCandidateRecord.objects.create(
            stable_id="candidate:dashboard-pending-two",
            session=session,
            extracted_value="Seal nicked",
            suggested_domain_type="FailureCause",
            source_document_id="doc",
            document_version="doc-version",
            workbook_name="dashboard.xlsx",
            sheet_name="PFMEA",
            row_number=4,
            column_name="Failure Cause",
            extraction_method="deterministic",
            parser_version="test",
            review_status=ReviewStatus.UNREVIEWED.value,
        )
        review_models.ImportCandidateRecord.objects.create(
            stable_id="candidate:dashboard-accepted",
            session=session,
            extracted_value="Leak test",
            suggested_domain_type="DetectionControl",
            source_document_id="doc",
            document_version="doc-version",
            workbook_name="dashboard.xlsx",
            sheet_name="PFMEA",
            row_number=4,
            column_name="Detection",
            extraction_method="deterministic",
            parser_version="test",
            review_status=ReviewStatus.ACCEPTED.value,
            reviewed_at=timezone.now(),
        )
        fmea_models.CauseInfluence.objects.create(
            stable_id="cause-influence:dashboard-suspected",
            source_type="FailureCause",
            source_id="failure-cause:dashboard",
            target_type="FailureMode",
            target_id="failure-mode:dashboard",
            influence_type="produces",
            status=CauseInfluenceStatus.SUSPECTED.value,
        )
        fmea_models.CauseInfluence.objects.create(
            stable_id="cause-influence:dashboard-possible",
            source_type="FailureCause",
            source_id="failure-cause:dashboard-two",
            target_type="FailureMode",
            target_id="failure-mode:dashboard",
            influence_type="contributes_to",
            status=CauseInfluenceStatus.POSSIBLE.value,
            reviewed_at=timezone.now() - timedelta(minutes=1),
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["fmea_count"], 2)
        self.assertEqual(response.context["pending_candidate_count"], 2)
        self.assertEqual(response.context["pending_row_group_count"], 1)
        self.assertContains(response, "FMEA Projects")
        self.assertContains(response, "2 candidates, 1 row")
        self.assertContains(response, "Suspected")
        self.assertContains(response, "Possible")
        self.assertContains(response, "Candidate - Accepted")
        self.assertContains(response, "Cause Influence - Transitioned to Possible")

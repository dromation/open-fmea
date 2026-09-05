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


import json

from fmea_app.services import evaluate_failure_mode
from fmea_app.views import _risk_evaluation_trend
from fmea_evaluation import CLASSIC_RPN_METHOD


class DashboardStatTileTests(TestCase):
    def test_stat_tiles_match_direct_count_queries(self):
        project = fmea_models.FMEAProject.objects.create(
            stable_id="project:dashboard-tiles", name="Dashboard Tiles Project"
        )
        fmea = fmea_models.FMEA.objects.create(
            stable_id="fmea:dashboard-tiles", name="Dashboard Tiles FMEA", project=project
        )
        failure_mode_one = fmea_models.FailureMode.objects.create(
            stable_id="fm:dashboard-tiles-one", fmea=fmea, name="Tile Failure Mode One"
        )
        fmea_models.FailureMode.objects.create(
            stable_id="fm:dashboard-tiles-two", fmea=fmea, name="Tile Failure Mode Two"
        )
        fmea_models.RecommendedAction.objects.create(
            stable_id="action:dashboard-tiles-one", failure_mode=failure_mode_one, name="Tile Action One"
        )

        response = self.client.get("/")

        self.assertEqual(response.context["project_count"], fmea_models.FMEAProject.objects.count())
        self.assertEqual(response.context["failure_mode_count"], fmea_models.FailureMode.objects.count())
        self.assertEqual(response.context["action_count"], fmea_models.RecommendedAction.objects.count())
        self.assertContains(response, "Projects")
        self.assertContains(response, "Failure Modes")
        self.assertContains(response, "Actions Summary")


class DashboardActionsSummaryTests(TestCase):
    def setUp(self) -> None:
        self.fmea = fmea_models.FMEA.objects.create(stable_id="fmea:dashboard-actions", name="Actions FMEA")
        self.failure_mode = fmea_models.FailureMode.objects.create(
            stable_id="fm:dashboard-actions", fmea=self.fmea, name="Actions Failure Mode"
        )
        self.today = timezone.now().date()

        fmea_models.RecommendedAction.objects.create(
            stable_id="action:dashboard-past-due-open",
            failure_mode=self.failure_mode,
            name="Past due, open",
            status="open",
            due_date=self.today - timedelta(days=5),
        )
        fmea_models.RecommendedAction.objects.create(
            stable_id="action:dashboard-due-in-3-open",
            failure_mode=self.failure_mode,
            name="Due in 3 days, open",
            status="open",
            due_date=self.today + timedelta(days=3),
        )
        fmea_models.RecommendedAction.objects.create(
            stable_id="action:dashboard-due-in-30-open",
            failure_mode=self.failure_mode,
            name="Due in 30 days, open",
            status="open",
            due_date=self.today + timedelta(days=30),
        )
        fmea_models.RecommendedAction.objects.create(
            stable_id="action:dashboard-past-due-completed",
            failure_mode=self.failure_mode,
            name="Past due, completed",
            status="completed",
            due_date=self.today - timedelta(days=10),
        )

    def test_overdue_and_due_soon_counts_exclude_terminal_statuses(self):
        response = self.client.get("/")

        self.assertEqual(response.context["actions_total"], 4)
        # Only the open, past-due action counts as overdue - the
        # completed-but-overdue action must not count.
        self.assertEqual(response.context["actions_overdue"], 1)
        # Only the open, due-in-3-days action counts as due soon.
        self.assertEqual(response.context["actions_due_soon"], 1)


class RiskEvaluationTrendHelperTests(TestCase):
    def setUp(self) -> None:
        self.definition = fmea_models.EvaluationDefinition.objects.create(
            stable_id="eval:dashboard-trend",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        self.fmea = fmea_models.FMEA.objects.create(stable_id="fmea:dashboard-trend", name="Trend FMEA")
        self.failure_mode = fmea_models.FailureMode.objects.create(
            stable_id="fm:dashboard-trend", fmea=self.fmea, name="Trend Failure Mode"
        )

    def test_trend_includes_only_in_window_dates_bucketed_with_zero_fill(self):
        now = timezone.now()
        today = now.date()

        # Two evaluations on the same in-window day.
        evaluate_failure_mode(
            failure_mode=self.failure_mode,
            definition=self.definition,
            severity=3,
            occurrence=3,
            detection=3,
            stable_id="riskeval:trend-in-window-a",
            evaluated_at=now - timedelta(days=5),
        )
        evaluate_failure_mode(
            failure_mode=self.failure_mode,
            definition=self.definition,
            severity=4,
            occurrence=4,
            detection=4,
            stable_id="riskeval:trend-in-window-b",
            evaluated_at=now - timedelta(days=5),
        )
        # One evaluation outside the 30-day window - must not appear.
        evaluate_failure_mode(
            failure_mode=self.failure_mode,
            definition=self.definition,
            severity=5,
            occurrence=5,
            detection=5,
            stable_id="riskeval:trend-out-of-window",
            evaluated_at=now - timedelta(days=45),
        )

        labels, counts = _risk_evaluation_trend(days=30)

        self.assertEqual(len(labels), 31)
        self.assertEqual(len(counts), 31)
        self.assertEqual(labels[0], (today - timedelta(days=30)).isoformat())
        self.assertEqual(labels[-1], today.isoformat())

        in_window_day = (today - timedelta(days=5)).isoformat()
        self.assertEqual(counts[labels.index(in_window_day)], 2)

        # Every other day, including days with zero evaluations, is
        # present and zero-filled.
        for label, count in zip(labels, counts):
            if label != in_window_day:
                self.assertEqual(count, 0)


class DashboardRiskTrendChartRenderTests(TestCase):
    def setUp(self) -> None:
        self.definition = fmea_models.EvaluationDefinition.objects.create(
            stable_id="eval:dashboard-chart-render",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )
        self.fmea = fmea_models.FMEA.objects.create(stable_id="fmea:dashboard-chart-render", name="Chart FMEA")
        self.failure_mode = fmea_models.FailureMode.objects.create(
            stable_id="fm:dashboard-chart-render", fmea=self.fmea, name="Chart Failure Mode"
        )
        evaluate_failure_mode(
            failure_mode=self.failure_mode,
            definition=self.definition,
            severity=2,
            occurrence=2,
            detection=2,
            stable_id="riskeval:dashboard-chart-render",
        )

    def test_response_has_exactly_one_canvas_and_matching_json_script_data(self):
        response = self.client.get("/")
        content = response.content.decode()

        self.assertEqual(content.count('<canvas id="risk-trend-chart"'), 1)

        script_start = content.index('<script id="risk-trend-data"')
        script_end = content.index("</script>", script_start)
        script_block = content[script_start:script_end]
        json_start = script_block.index(">") + 1
        payload = json.loads(script_block[json_start:])

        expected_labels, expected_counts = _risk_evaluation_trend(days=30)
        self.assertEqual(payload["labels"], expected_labels)
        self.assertEqual(payload["counts"], expected_counts)

    def test_response_excludes_out_of_scope_sections(self):
        response = self.client.get("/")

        for excluded in ("Operations", "Overall Health", "Coverage", "Broken Links", "PM-FMEA"):
            self.assertNotContains(response, excluded)

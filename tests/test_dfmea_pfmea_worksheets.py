from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from fmea_app import models
from fmea_evaluation import CLASSIC_RPN_METHOD


class DfmeaPfmeaWorksheetTests(TestCase):
    def setUp(self) -> None:
        self.definition = models.EvaluationDefinition.objects.create(
            stable_id="eval:dfmea-pfmea-worksheets",
            method=CLASSIC_RPN_METHOD,
            name="Classic RPN",
        )

        # Design-side fixture (fmea_type != "process") -> should appear on /dfmea/ only.
        self.design_fmea = models.FMEA.objects.create(
            stable_id="fmea:dfmea-worksheets-design",
            name="Bracket DFMEA",
            fmea_type="design",
        )
        self.design_failure_mode = models.FailureMode.objects.create(
            stable_id="fm:dfmea-worksheets-design",
            fmea=self.design_fmea,
            name="Bracket cracks under load",
        )
        design_cause = models.FailureCause.objects.create(
            stable_id="cause:dfmea-worksheets-design",
            failure_mode=self.design_failure_mode,
            name="Undersized fillet radius",
        )
        models.PreventionControl.objects.create(
            stable_id="prevention:dfmea-worksheets-design",
            failure_cause=design_cause,
            name="Design review checklist",
        )
        models.DetectionControl.objects.create(
            stable_id="detection:dfmea-worksheets-design",
            failure_cause=design_cause,
            name="FEA stress analysis",
        )
        models.RiskEvaluation.objects.create(
            failure_mode=self.design_failure_mode,
            definition=self.definition,
            severity=8,
            occurrence=3,
            detection=4,
            result={"score": 96, "classification": "medium"},
        )
        # One overdue, one open-not-overdue action on this cause.
        models.RecommendedAction.objects.create(
            stable_id="action:dfmea-worksheets-overdue",
            failure_cause=design_cause,
            name="Redesign fillet",
            status="open",
            due_date=date.today() - timedelta(days=5),
        )
        models.RecommendedAction.objects.create(
            stable_id="action:dfmea-worksheets-open",
            failure_cause=design_cause,
            name="Schedule FEA re-run",
            status="open",
            due_date=date.today() + timedelta(days=10),
        )

        # Process-side fixture (fmea_type == "process") -> should appear on /pfmea/ only.
        self.process_fmea = models.FMEA.objects.create(
            stable_id="fmea:dfmea-worksheets-process",
            name="Seal Assembly PFMEA",
            fmea_type="process",
        )
        self.process_failure_mode = models.FailureMode.objects.create(
            stable_id="fm:dfmea-worksheets-process",
            fmea=self.process_fmea,
            name="Seal leaks after assembly",
        )
        process_cause = models.FailureCause.objects.create(
            stable_id="cause:dfmea-worksheets-process",
            failure_mode=self.process_failure_mode,
            name="Seal nicked during installation",
        )
        models.PreventionControl.objects.create(
            stable_id="prevention:dfmea-worksheets-process",
            failure_cause=process_cause,
            name="Chamfer check",
        )
        models.DetectionControl.objects.create(
            stable_id="detection:dfmea-worksheets-process",
            failure_cause=process_cause,
            name="Leak test",
        )
        models.RiskEvaluation.objects.create(
            failure_mode=self.process_failure_mode,
            definition=self.definition,
            severity=9,
            occurrence=4,
            detection=5,
            result={"score": 180, "classification": "high"},
        )

    def test_design_type_fmea_appears_only_on_dfmea_page(self):
        dfmea_response = self.client.get(reverse("fmea:dfmea_worksheet"))
        pfmea_response = self.client.get(reverse("fmea:pfmea_worksheet"))

        self.assertContains(dfmea_response, "Bracket cracks under load")
        self.assertNotContains(pfmea_response, "Bracket cracks under load")

    def test_process_type_fmea_appears_only_on_pfmea_page(self):
        dfmea_response = self.client.get(reverse("fmea:dfmea_worksheet"))
        pfmea_response = self.client.get(reverse("fmea:pfmea_worksheet"))

        self.assertContains(pfmea_response, "Seal leaks after assembly")
        self.assertNotContains(dfmea_response, "Seal leaks after assembly")

    def test_row_content_matches_fixture_data_on_dfmea_page(self):
        response = self.client.get(reverse("fmea:dfmea_worksheet"))

        self.assertContains(response, "Bracket cracks under load")
        self.assertContains(response, "Undersized fillet radius")
        self.assertContains(response, "Design review checklist")
        self.assertContains(response, "FEA stress analysis")
        self.assertContains(response, "RPN 96")

        content = response.content.decode()
        row_start = content.index("Bracket cracks under load")
        row_end = content.index("</tr>", row_start)
        row_html = content[row_start:row_end]
        self.assertIn(">8<", row_html)
        self.assertIn(">3<", row_html)
        self.assertIn(">4<", row_html)

    def test_row_content_matches_fixture_data_on_pfmea_page(self):
        response = self.client.get(reverse("fmea:pfmea_worksheet"))

        self.assertContains(response, "Seal leaks after assembly")
        self.assertContains(response, "Seal nicked during installation")
        self.assertContains(response, "Chamfer check")
        self.assertContains(response, "Leak test")
        self.assertContains(response, "RPN 180")

        content = response.content.decode()
        row_start = content.index("Seal leaks after assembly")
        row_end = content.index("</tr>", row_start)
        row_html = content[row_start:row_end]
        self.assertIn(">9<", row_html)
        self.assertIn(">4<", row_html)
        self.assertIn(">5<", row_html)

    def test_actions_column_shows_correct_open_and_overdue_counts(self):
        response = self.client.get(reverse("fmea:dfmea_worksheet"))

        self.assertContains(response, "2 open / 1 overdue")

    def test_pages_stay_within_narrowed_scope(self):
        for url_name in ("fmea:dfmea_worksheet", "fmea:pfmea_worksheet"):
            response = self.client.get(reverse(url_name))
            for excluded in (
                "<canvas",
                "Structure Tree",
                "Interface Matrix",
                "Parameter Diagram",
                "Control Plan",
            ):
                self.assertNotContains(response, excluded)

    def test_rows_link_to_the_correct_fmea_detail_page(self):
        dfmea_response = self.client.get(reverse("fmea:dfmea_worksheet"))
        pfmea_response = self.client.get(reverse("fmea:pfmea_worksheet"))

        self.assertContains(
            dfmea_response,
            f'href="{reverse("fmea:fmea_detail", args=[self.design_fmea.stable_id])}"',
        )
        self.assertContains(
            pfmea_response,
            f'href="{reverse("fmea:fmea_detail", args=[self.process_fmea.stable_id])}"',
        )

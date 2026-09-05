from __future__ import annotations

from datetime import date

from django.test import TestCase
from django.urls import reverse

from fmea_app import models


class FMEAElementsStandalonePagesTests(TestCase):
    def setUp(self) -> None:
        self.fmea_a = models.FMEA.objects.create(
            stable_id="fmea:elements-a",
            name="Elements FMEA A",
        )
        self.fmea_b = models.FMEA.objects.create(
            stable_id="fmea:elements-b",
            name="Elements FMEA B",
        )

        self.function_a = models.Function.objects.create(
            stable_id="function:elements-a",
            name="Contain fluid",
        )
        self.failure_mode_a = models.FailureMode.objects.create(
            stable_id="failure-mode:elements-a",
            fmea=self.fmea_a,
            function=self.function_a,
            name="Seal leaks",
            description="Seal fails to contain fluid.",
        )
        self.failure_mode_b = models.FailureMode.objects.create(
            stable_id="failure-mode:elements-b",
            fmea=self.fmea_b,
            name="Bracket cracks",
            description="Bracket fails under load.",
        )

        self.effect_a = models.FailureEffect.objects.create(
            stable_id="effect:elements-a",
            failure_mode=self.failure_mode_a,
            name="Fluid loss",
        )
        self.effect_b = models.FailureEffect.objects.create(
            stable_id="effect:elements-b",
            failure_mode=self.failure_mode_b,
            name="Structural failure",
        )

        self.cause_a = models.FailureCause.objects.create(
            stable_id="cause:elements-a",
            failure_mode=self.failure_mode_a,
            name="Seal nicked",
        )
        self.cause_b = models.FailureCause.objects.create(
            stable_id="cause:elements-b",
            failure_mode=self.failure_mode_b,
            name="Undersized fillet radius",
        )

        self.prevention_a = models.PreventionControl.objects.create(
            stable_id="prevention:elements-a",
            failure_cause=self.cause_a,
            name="Installation checklist",
        )
        self.prevention_b = models.PreventionControl.objects.create(
            stable_id="prevention:elements-b",
            failure_cause=self.cause_b,
            name="Design review",
        )
        self.detection_a = models.DetectionControl.objects.create(
            stable_id="detection:elements-a",
            failure_cause=self.cause_a,
            name="Leak test",
        )

        self.role = models.ResponsibleRole.objects.create(
            stable_id="responsible-role:elements",
            name="Quality Engineer",
        )
        self.action_direct_on_mode = models.RecommendedAction.objects.create(
            stable_id="action:elements-direct-mode",
            failure_mode=self.failure_mode_a,
            name="Add inline leak check",
            status="open",
            responsible_role=self.role,
            due_date=date(2026, 3, 1),
        )
        self.action_on_cause = models.RecommendedAction.objects.create(
            stable_id="action:elements-on-cause",
            failure_cause=self.cause_b,
            name="Redesign fillet",
            status="on_hold",
            due_date=date(2026, 4, 1),
        )

        self.evaluation_definition = models.EvaluationDefinition.objects.create(
            stable_id="evaluation-definition:elements",
            name="Classic RPN",
            method="classic_rpn",
        )
        models.RiskEvaluation.objects.create(
            stable_id="risk-evaluation:elements-a",
            failure_mode=self.failure_mode_a,
            definition=self.evaluation_definition,
            severity=8,
            occurrence=3,
            detection=4,
            result={"score": 96, "classification": "medium"},
        )

    def test_failure_mode_list_spans_multiple_fmeas_with_correct_counts_and_links(self):
        response = self.client.get(reverse("fmea:failure_mode_list"))

        self.assertContains(response, "Seal leaks")
        self.assertContains(response, "Bracket cracks")
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea_a.stable_id])}"'
        )
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea_b.stable_id])}"'
        )
        self.assertContains(response, "RPN 96")

        content = response.content.decode()
        row_a_start = content.index("Seal leaks")
        row_a_end = content.index("</tr>", row_a_start)
        row_a = content[row_a_start:row_a_end]
        self.assertIn(">1<", row_a)  # 1 effect, 1 cause, 1 direct action - all "1"

    def test_failure_cause_list_spans_multiple_fmeas_with_correct_counts(self):
        response = self.client.get(reverse("fmea:failure_cause_list"))

        self.assertContains(response, "Seal nicked")
        self.assertContains(response, "Undersized fillet radius")

        content = response.content.decode()
        row_a_start = content.index("Seal nicked")
        row_a_end = content.index("</tr>", row_a_start)
        row_a = content[row_a_start:row_a_end]
        # cause_a: 1 prevention control, 1 detection control, 0 actions
        self.assertIn(">1<", row_a)
        self.assertIn(">0<", row_a)

        row_b_start = content.index("Undersized fillet radius")
        row_b_end = content.index("</tr>", row_b_start)
        row_b = content[row_b_start:row_b_end]
        # cause_b: 1 prevention control, 0 detection controls, 1 action
        self.assertIn(">1<", row_b)
        self.assertIn(">0<", row_b)

    def test_failure_effect_list_spans_multiple_fmeas(self):
        response = self.client.get(reverse("fmea:failure_effect_list"))
        self.assertContains(response, "Fluid loss")
        self.assertContains(response, "Structural failure")
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea_a.stable_id])}"'
        )
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea_b.stable_id])}"'
        )

    def test_prevention_control_list_spans_multiple_fmeas(self):
        response = self.client.get(reverse("fmea:prevention_control_list"))
        self.assertContains(response, "Installation checklist")
        self.assertContains(response, "Design review")
        self.assertContains(response, "Seal nicked")
        self.assertContains(response, "Undersized fillet radius")

    def test_detection_control_list_spans_multiple_fmeas(self):
        response = self.client.get(reverse("fmea:detection_control_list"))
        self.assertContains(response, "Leak test")
        self.assertContains(response, "Seal nicked")

    def test_action_list_shows_actions_from_both_fmeas_with_correct_links_and_labels(self):
        response = self.client.get(reverse("fmea:action_list"))

        self.assertContains(response, "Add inline leak check")
        self.assertContains(response, "Redesign fillet")
        self.assertContains(response, "Failure Mode: Seal leaks")
        self.assertContains(response, "Cause: Undersized fillet radius")
        self.assertContains(
            response, f'href="{reverse("fmea:action_detail", args=[self.action_direct_on_mode.stable_id])}"'
        )
        self.assertContains(
            response, f'href="{reverse("fmea:action_detail", args=[self.action_on_cause.stable_id])}"'
        )
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea_a.stable_id])}"'
        )
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea_b.stable_id])}"'
        )

    def test_action_status_filter_includes_on_hold_and_new_status_persists_and_filters(self):
        response = self.client.get(reverse("fmea:action_list"))
        self.assertContains(response, 'value="on_hold"')
        self.assertContains(response, "On Hold")

        self.action_on_cause.refresh_from_db()
        self.assertEqual(self.action_on_cause.status, "on_hold")

        filtered = self.client.get(reverse("fmea:action_list"), {"status": "on_hold"})
        self.assertContains(filtered, "Redesign fillet")
        self.assertNotContains(filtered, "Add inline leak check")

    def test_failure_cause_model_is_unchanged_single_failure_mode_relationship(self):
        field_names = {f.name for f in models.FailureCause._meta.get_fields()}
        self.assertIn("failure_mode", field_names)
        fk_field = models.FailureCause._meta.get_field("failure_mode")
        self.assertFalse(fk_field.many_to_many)
        self.assertEqual(self.cause_a.failure_mode_id, self.failure_mode_a.pk)

    def test_none_of_the_six_pages_contain_post_form_markup(self):
        pages = (
            reverse("fmea:failure_mode_list"),
            reverse("fmea:failure_cause_list"),
            reverse("fmea:failure_effect_list"),
            reverse("fmea:prevention_control_list"),
            reverse("fmea:detection_control_list"),
            reverse("fmea:action_list"),
        )
        for url in pages:
            response = self.client.get(url)
            self.assertNotContains(response, 'method="post"')

    def test_sidebar_shows_fmea_elements_group_with_six_links(self):
        response = self.client.get(reverse("fmea:dashboard"))

        self.assertContains(response, "FMEA ELEMENTS")
        for label, url_name in (
            ("Failure Modes", "failure_mode_list"),
            ("Causes", "failure_cause_list"),
            ("Effects", "failure_effect_list"),
            ("Preventive Controls", "prevention_control_list"),
            ("Detection Controls", "detection_control_list"),
            ("Actions", "action_list"),
        ):
            self.assertContains(response, label)
            self.assertContains(response, f'href="{reverse(f"fmea:{url_name}")}"')

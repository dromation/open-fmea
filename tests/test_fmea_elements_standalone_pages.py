from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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


class FailureModeRicherPageTests(TestCase):
    """Slice O (2026-09-06): KPI row, filter toolbar, right-docked detail
    panel with GET-param tabs (direct + via-cause Actions), FMEA Chain View
    diagram, Coverage Summary, and the Risk Summary donut."""

    def setUp(self) -> None:
        self.fmea_1 = models.FMEA.objects.create(
            stable_id="fmea:richer-o-1",
            name="Richer O FMEA One",
        )
        self.fmea_2 = models.FMEA.objects.create(
            stable_id="fmea:richer-o-2",
            name="Richer O FMEA Two",
        )
        self.evaluation_definition = models.EvaluationDefinition.objects.create(
            stable_id="evaluation-definition:richer-o",
            name="Classic RPN",
            method="classic_rpn_richer_o",
        )

        # FM_full: high risk, one cause, one effect, one direct action.
        self.fm_full = models.FailureMode.objects.create(
            stable_id="failure-mode:richer-o-full",
            fmea=self.fmea_1,
            name="Full coverage failure mode",
        )
        self.effect_full = models.FailureEffect.objects.create(
            stable_id="effect:richer-o-full",
            failure_mode=self.fm_full,
            name="Full effect",
        )
        self.cause_full = models.FailureCause.objects.create(
            stable_id="cause:richer-o-full",
            failure_mode=self.fm_full,
            name="Full cause",
        )
        self.action_direct_full = models.RecommendedAction.objects.create(
            stable_id="action:richer-o-full-direct",
            failure_mode=self.fm_full,
            name="Direct action on full FM",
        )
        now = timezone.now()
        self.risk_full_newest = models.RiskEvaluation.objects.create(
            stable_id="risk-evaluation:richer-o-full-newest",
            failure_mode=self.fm_full,
            definition=self.evaluation_definition,
            severity=9,
            occurrence=8,
            detection=5,
            result={"score": 360, "classification": "high"},
            evaluated_at=now,
        )
        self.risk_full_older = models.RiskEvaluation.objects.create(
            stable_id="risk-evaluation:richer-o-full-older",
            failure_mode=self.fm_full,
            definition=self.evaluation_definition,
            severity=6,
            occurrence=5,
            detection=5,
            result={"score": 150, "classification": "medium"},
            evaluated_at=now - timedelta(days=5),
        )

        # FM_via_cause_only: low risk, one cause (which itself carries an
        # action), no direct action, no effects.
        self.fm_via_cause_only = models.FailureMode.objects.create(
            stable_id="failure-mode:richer-o-via-cause",
            fmea=self.fmea_2,
            name="Via cause only failure mode",
        )
        self.cause_via = models.FailureCause.objects.create(
            stable_id="cause:richer-o-via",
            failure_mode=self.fm_via_cause_only,
            name="Cause with its own action",
        )
        self.action_via_cause = models.RecommendedAction.objects.create(
            stable_id="action:richer-o-via-cause",
            failure_cause=self.cause_via,
            name="Action reachable only via cause",
        )
        models.RiskEvaluation.objects.create(
            stable_id="risk-evaluation:richer-o-via",
            failure_mode=self.fm_via_cause_only,
            definition=self.evaluation_definition,
            severity=3,
            occurrence=2,
            detection=3,
            result={"score": 18, "classification": "low"},
        )

        # FM_medium: medium risk, one cause (no action anywhere), one effect,
        # no direct or via-cause action.
        self.fm_medium = models.FailureMode.objects.create(
            stable_id="failure-mode:richer-o-medium",
            fmea=self.fmea_1,
            name="Medium risk failure mode",
        )
        models.FailureEffect.objects.create(
            stable_id="effect:richer-o-medium",
            failure_mode=self.fm_medium,
            name="Medium effect",
        )
        models.FailureCause.objects.create(
            stable_id="cause:richer-o-medium",
            failure_mode=self.fm_medium,
            name="Medium cause, no action",
        )
        models.RiskEvaluation.objects.create(
            stable_id="risk-evaluation:richer-o-medium",
            failure_mode=self.fm_medium,
            definition=self.evaluation_definition,
            severity=5,
            occurrence=4,
            detection=5,
            result={"score": 100, "classification": "medium"},
        )

        # FM_no_coverage: nothing recorded at all - zero causes, zero
        # effects, zero actions, zero risk evaluations.
        self.fm_no_coverage = models.FailureMode.objects.create(
            stable_id="failure-mode:richer-o-empty",
            fmea=self.fmea_2,
            name="No coverage failure mode",
        )

    def test_kpi_tiles_match_expected_counts(self):
        response = self.client.get(reverse("fmea:failure_mode_list"))
        self.assertEqual(response.context["kpi_total"], 4)
        self.assertEqual(response.context["kpi_not_evaluated"], 1)
        self.assertEqual(response.context["kpi_high_critical"], 1)
        self.assertEqual(response.context["kpi_no_cause"], 1)
        self.assertEqual(response.context["kpi_no_action"], 2)

    def test_coverage_summary_matches_kpi_derived_facts(self):
        response = self.client.get(reverse("fmea:failure_mode_list"))
        self.assertEqual(response.context["coverage_zero_causes"], 1)
        self.assertEqual(response.context["coverage_zero_effects"], 2)
        self.assertEqual(response.context["coverage_zero_actions"], 2)
        self.assertEqual(response.context["coverage_zero_risk_evaluations"], 1)

    def test_fmea_filter_narrows_rows_and_kpi_together(self):
        response = self.client.get(reverse("fmea:failure_mode_list"), {"fmea": self.fmea_1.stable_id})
        self.assertContains(response, "Full coverage failure mode")
        self.assertContains(response, "Medium risk failure mode")
        self.assertNotContains(response, "Via cause only failure mode")
        self.assertNotContains(response, "No coverage failure mode")
        self.assertEqual(response.context["kpi_total"], 2)
        self.assertEqual(response.context["kpi_no_action"], 1)

    def test_risk_level_filter_narrows_rows_and_kpi_together(self):
        response = self.client.get(reverse("fmea:failure_mode_list"), {"risk_level": "high"})
        self.assertContains(response, "Full coverage failure mode")
        self.assertNotContains(response, "Medium risk failure mode")
        self.assertNotContains(response, "Via cause only failure mode")
        self.assertNotContains(response, "No coverage failure mode")
        self.assertEqual(response.context["kpi_total"], 1)

    def test_has_action_filter_narrows_rows_and_kpi_together(self):
        yes_response = self.client.get(reverse("fmea:failure_mode_list"), {"has_action": "yes"})
        self.assertContains(yes_response, "Full coverage failure mode")
        self.assertContains(yes_response, "Via cause only failure mode")
        self.assertNotContains(yes_response, "Medium risk failure mode")
        self.assertNotContains(yes_response, "No coverage failure mode")
        self.assertEqual(yes_response.context["kpi_total"], 2)

        no_response = self.client.get(reverse("fmea:failure_mode_list"), {"has_action": "no"})
        self.assertContains(no_response, "Medium risk failure mode")
        self.assertContains(no_response, "No coverage failure mode")
        self.assertNotContains(no_response, "Full coverage failure mode")
        self.assertNotContains(no_response, "Via cause only failure mode")
        self.assertEqual(no_response.context["kpi_total"], 2)

    def test_actions_direct_column_is_unchanged_while_actions_tab_includes_via_cause(self):
        response = self.client.get(reverse("fmea:failure_mode_list"))
        content = response.content.decode()
        row_start = content.index("Via cause only failure mode")
        row_end = content.index("</tr>", row_start)
        row = content[row_start:row_end]
        # actions_count (direct) must still read 0 for this row - the action
        # exists only via its cause, never FK'd straight to the FailureMode.
        self.assertIn(">0<", row)

        panel = self.client.get(
            reverse("fmea:failure_mode_list"),
            {"selected": self.fm_via_cause_only.stable_id, "tab": "actions"},
        )
        self.assertContains(panel, "Action reachable only via cause")
        self.assertContains(panel, "Actions (direct + via causes)")

    def test_risk_tab_renders_history_newest_first(self):
        response = self.client.get(
            reverse("fmea:failure_mode_list"), {"selected": self.fm_full.stable_id, "tab": "risk"}
        )
        content = response.content.decode()
        newest_index = content.index("RPN 360")
        older_index = content.index("RPN 150")
        self.assertLess(newest_index, older_index)

    def test_chain_diagram_renders_none_recorded_for_empty_branches(self):
        response = self.client.get(
            reverse("fmea:failure_mode_list"), {"selected": self.fm_no_coverage.stable_id}
        )
        self.assertContains(response, "No coverage failure mode")
        # Function/Requirement, Effects, Causes, and Actions are all empty
        # for this failure mode - each must render an explicit box, not a
        # silently omitted arrow.
        self.assertGreaterEqual(response.content.decode().count("None recorded"), 4)

    def test_unrecognized_tab_defaults_to_general_without_500(self):
        response = self.client.get(
            reverse("fmea:failure_mode_list"),
            {"selected": self.fm_full.stable_id, "tab": "not-a-real-tab"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "general")

    def test_invalid_selected_id_returns_404_not_500(self):
        response = self.client.get(
            reverse("fmea:failure_mode_list"), {"selected": "failure-mode:does-not-exist"}
        )
        self.assertEqual(response.status_code, 404)

    def test_pages_have_no_open_eqms_scope_creep(self):
        # Decision 7's permanent boundary: none of this new-to-this-slice
        # content ever appears. "Ishikawa" is deliberately not checked here -
        # the shared sidebar already carries a legitimate, pre-existing
        # "Ishikawa / Cause Analysis" nav group from an earlier slice,
        # unrelated to this page or this boundary.
        response = self.client.get(reverse("fmea:failure_mode_list"))
        for excluded in (
            "Complaint",
            "NCR",
            "8D",
            "XDA",
            "5-Why",
            "5 Why",
            "Error Catalog",
            "Defect Catalog",
            "Open-EQMS",
            "Open EQMS",
        ):
            self.assertNotContains(response, excluded)

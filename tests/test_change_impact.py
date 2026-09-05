from __future__ import annotations

from datetime import date

from django.test import TestCase
from django.urls import reverse

from fmea_app import models


class ChangeImpactTests(TestCase):
    def setUp(self) -> None:
        self.design_fmea = models.FMEA.objects.create(
            stable_id="fmea:change-impact-design",
            name="Bracket Design FMEA",
            fmea_type="design",
        )
        self.process_fmea = models.FMEA.objects.create(
            stable_id="fmea:change-impact-process",
            name="Bracket Process FMEA",
            fmea_type="process",
        )
        self.failure_mode_design = models.FailureMode.objects.create(
            stable_id="failure-mode:change-impact-design",
            fmea=self.design_fmea,
            name="Bracket cracks under load",
        )
        self.failure_mode_process = models.FailureMode.objects.create(
            stable_id="failure-mode:change-impact-process",
            fmea=self.process_fmea,
            name="Weld porosity",
        )
        self.other_failure_mode = models.FailureMode.objects.create(
            stable_id="failure-mode:change-impact-other",
            fmea=self.process_fmea,
            name="Torque out of spec",
        )
        self.role = models.ResponsibleRole.objects.create(
            stable_id="responsible-role:change-impact",
            name="Change Coordinator",
        )
        self.change_a = models.Change.objects.create(
            stable_id="change:a",
            title="Switch to aluminum bracket",
            change_type="design",
            source="Customer request",
            reason="Weight reduction",
            description="Replace steel bracket with aluminum equivalent.",
            impact_level="high",
            status="in_progress",
            owner=self.role,
            target_date=date(2026, 3, 1),
        )
        self.change_a.affected_failure_modes.set(
            [self.failure_mode_design, self.failure_mode_process]
        )
        self.change_b = models.Change.objects.create(
            stable_id="change:b",
            title="New weld supplier qualification",
            change_type="supplier",
            source="Sourcing",
            reason="Cost reduction",
            impact_level="critical",
            status="closed",
        )

    def test_create_view_persists_all_fields_including_m2m(self):
        response = self.client.post(
            reverse("fmea:new_change"),
            data={
                "title": "Update fastener torque spec",
                "change_type": "process",
                "source": "Internal audit",
                "reason": "Field failures",
                "description": "Increase torque tolerance band.",
                "impact_level": "medium",
                "status": "under_analysis",
                "owner": self.role.pk,
                "target_date": "2026-05-01",
                "affected_failure_modes": [self.other_failure_mode.pk],
            },
        )
        created = models.Change.objects.get(title="Update fastener torque spec")
        self.assertRedirects(response, reverse("fmea:change_detail", args=[created.stable_id]))
        self.assertEqual(created.change_type, "process")
        self.assertEqual(created.impact_level, "medium")
        self.assertEqual(created.status, "under_analysis")
        self.assertEqual(created.owner_id, self.role.pk)
        self.assertEqual(
            set(created.affected_failure_modes.values_list("pk", flat=True)),
            {self.other_failure_mode.pk},
        )

    def test_list_shows_all_rows_with_correct_columns(self):
        response = self.client.get(reverse("fmea:change_list"))

        self.assertContains(response, "Switch to aluminum bracket")
        self.assertContains(response, "Design")
        self.assertContains(response, "High")
        self.assertContains(response, "In Progress")
        self.assertContains(response, "Change Coordinator")
        self.assertContains(response, "March 1, 2026")

        self.assertContains(response, "New weld supplier qualification")
        self.assertContains(response, "Supplier")
        self.assertContains(response, "Critical")
        self.assertContains(response, "Closed")

    def test_get_filters_narrow_the_list_individually_and_combined(self):
        base_url = reverse("fmea:change_list")

        response = self.client.get(base_url, {"change_type": "supplier"})
        self.assertContains(response, "New weld supplier qualification")
        self.assertNotContains(response, "Switch to aluminum bracket")

        response = self.client.get(base_url, {"impact_level": "critical"})
        self.assertContains(response, "New weld supplier qualification")
        self.assertNotContains(response, "Switch to aluminum bracket")

        response = self.client.get(base_url, {"status": "closed"})
        self.assertContains(response, "New weld supplier qualification")
        self.assertNotContains(response, "Switch to aluminum bracket")

        response = self.client.get(
            base_url, {"change_type": "supplier", "impact_level": "critical", "status": "closed"}
        )
        self.assertContains(response, "New weld supplier qualification")
        self.assertNotContains(response, "Switch to aluminum bracket")

    def test_detail_shows_linked_failure_modes_with_correct_dfmea_pfmea_labels(self):
        response = self.client.get(reverse("fmea:change_detail", args=[self.change_a.stable_id]))

        self.assertContains(response, "Bracket cracks under load")
        self.assertContains(response, "Weld porosity")
        self.assertContains(response, "DFMEA")
        self.assertContains(response, "PFMEA")
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.design_fmea.stable_id])}"'
        )
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.process_fmea.stable_id])}"'
        )
        self.assertContains(response, "Affected Failure Modes (2)")

    def test_edit_view_updates_affected_failure_modes_to_exactly_the_new_set(self):
        response = self.client.post(
            reverse("fmea:edit_change", args=[self.change_a.stable_id]),
            data={
                "title": self.change_a.title,
                "change_type": self.change_a.change_type,
                "source": self.change_a.source,
                "reason": self.change_a.reason,
                "description": self.change_a.description,
                "impact_level": self.change_a.impact_level,
                "status": self.change_a.status,
                "owner": self.role.pk,
                "target_date": "2026-03-01",
                "affected_failure_modes": [self.failure_mode_design.pk, self.other_failure_mode.pk],
            },
        )
        self.assertRedirects(response, reverse("fmea:change_detail", args=[self.change_a.stable_id]))

        detail_response = self.client.get(reverse("fmea:change_detail", args=[self.change_a.stable_id]))
        self.assertContains(detail_response, "Bracket cracks under load")
        self.assertContains(detail_response, "Torque out of spec")
        self.assertNotContains(detail_response, "Weld porosity")
        self.assertContains(detail_response, "Affected Failure Modes (2)")

    def test_pages_have_no_canvas_and_no_excluded_tab_content(self):
        for response in (
            self.client.get(reverse("fmea:change_list")),
            self.client.get(reverse("fmea:new_change")),
            self.client.get(reverse("fmea:edit_change", args=[self.change_a.stable_id])),
            self.client.get(reverse("fmea:change_detail", args=[self.change_a.stable_id])),
        ):
            for excluded in ("<canvas", "Impact Matrix", "Action Plan", "Change History"):
                self.assertNotContains(response, excluded)

    def test_sidebar_has_exactly_one_new_change_impact_link_and_other_unbuilt_labels_stay_absent(self):
        response = self.client.get("/")

        self.assertContains(response, "Change Impact")
        self.assertContains(response, f'href="{reverse("fmea:change_list")}"')
        self.assertEqual(response.content.decode().count("Change Impact"), 1)

        for unbuilt_label in (
            "Validation Trajectory",
            "CAPA",
            "Control Plans",
            "AI Assistant",
            "AP/Detection",
            "XDA Investigations",
            "SPC/ITRA-DT",
            "Documents & Links",
            "Lessons Learned",
            "Knowledge & References",
            "Operations",
            "Project Health",
            "FMEA Team",
        ):
            self.assertNotContains(response, unbuilt_label)

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from fmea_app import models


class ProjectsListAndTeamRosterTests(TestCase):
    def setUp(self) -> None:
        self.project = models.FMEAProject.objects.create(
            stable_id="project:customer-launch",
            name="Customer Launch",
            project_code="CL-2026",
            status="active",
            description="Launch readiness FMEA set",
        )
        self.process_fmea = models.FMEA.objects.create(
            stable_id="fmea:launch-pfmea",
            project=self.project,
            name="Assembly PFMEA",
            fmea_type="process",
            scope="Station 20",
        )
        self.design_fmea = models.FMEA.objects.create(
            stable_id="fmea:launch-dfmea",
            project=self.project,
            name="Housing DFMEA",
            fmea_type="design",
        )
        models.Product.objects.create(
            stable_id="product:launch-housing",
            fmea=self.design_fmea,
            name="Housing",
            part_number="442710",
        )
        models.Process.objects.create(
            stable_id="process:launch-assembly",
            fmea=self.process_fmea,
            name="Assembly",
            process_code="ASM",
        )

    def test_projects_list_renders_stat_cards_and_project_row(self):
        response = self.client.get("/fmea/projects/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Projects")
        self.assertContains(response, "Active")
        self.assertContains(response, "Customer Launch")
        self.assertContains(response, "CL-2026")
        self.assertContains(response, "Process: 1")
        self.assertContains(response, "Design: 1")

    def test_create_project_form_persists_project_code_and_status(self):
        response = self.client.post(
            "/projects/create/",
            {
                "name": "Service Launch",
                "project_code": "SL-2026",
                "status": "on_hold",
                "description": "Field service rollout",
            },
        )

        self.assertEqual(response.status_code, 302)
        project = models.FMEAProject.objects.get(name="Service Launch")
        self.assertEqual(project.project_code, "SL-2026")
        self.assertEqual(project.status, "on_hold")

    def test_existing_project_create_posts_default_to_active_status(self):
        response = self.client.post(
            "/projects/create/",
            {"name": "Legacy Flow", "description": "Older tests omit status"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.FMEAProject.objects.get(name="Legacy Flow").status, "active")

    def test_project_detail_lists_fmeas_products_and_processes(self):
        response = self.client.get(f"/fmea/projects/{self.project.stable_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Project Metadata")
        self.assertContains(response, "Assembly PFMEA")
        self.assertContains(response, "Housing DFMEA")
        self.assertContains(response, "Housing")
        self.assertContains(response, "Assembly")

    def test_team_route_adds_and_renders_project_membership(self):
        response = self.client.post(
            f"/fmea/projects/{self.project.stable_id}/team/",
            {
                "action": "add",
                "first_name": "Janez",
                "last_name": "Novak",
                "email": "janez.novak@example.com",
                "role": "fmea_leader",
            },
        )

        self.assertEqual(response.status_code, 302)
        membership = models.ProjectMembership.objects.get(project=self.project)
        self.assertEqual(membership.role, "fmea_leader")
        self.assertEqual(membership.user.email, "janez.novak@example.com")

        detail = self.client.get(f"/fmea/projects/{self.project.stable_id}/team/")
        self.assertContains(detail, "Janez Novak")
        self.assertContains(detail, "janez.novak@example.com")
        self.assertContains(detail, "FMEA Leader")

    def test_team_route_reuses_existing_user_by_email(self):
        user_model = get_user_model()
        user = user_model.objects.create(
            username="existing-user",
            email="member@example.com",
            first_name="Existing",
            last_name="Member",
        )

        self.client.post(
            f"/fmea/projects/{self.project.stable_id}/team/",
            {
                "action": "add",
                "first_name": "",
                "last_name": "",
                "email": "member@example.com",
                "role": "viewer",
            },
        )

        membership = models.ProjectMembership.objects.get(project=self.project)
        self.assertEqual(membership.user_id, user.pk)
        self.assertEqual(membership.role, "viewer")

    def test_team_route_removes_member(self):
        user_model = get_user_model()
        user = user_model.objects.create(
            username="remove-user",
            email="remove@example.com",
        )
        membership = models.ProjectMembership.objects.create(
            stable_id="project-membership:remove",
            project=self.project,
            user=user,
            role="contributor",
        )

        response = self.client.post(
            f"/fmea/projects/{self.project.stable_id}/team/",
            {"action": "remove", "membership_id": membership.stable_id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.ProjectMembership.objects.filter(pk=membership.pk).exists())

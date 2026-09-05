from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.test import TestCase


class GuiNavigationScopeTests(TestCase):
    def test_shell_contains_only_built_navigation_surfaces(self):
        response = self.client.get("/")

        self.assertContains(response, "Home")
        self.assertContains(response, "FMEA Projects")
        self.assertContains(response, "Import Sessions")
        self.assertContains(response, "Cause Influences")
        self.assertContains(response, "Process Characteristics")
        self.assertContains(response, "Risk Matrix")

        self.assertContains(response, "HOME")
        self.assertContains(response, "WORKSPACE")
        self.assertContains(response, "CONTEXT")
        self.assertContains(response, "Characteristics Flow")
        self.assertContains(response, "RISK")
        self.assertContains(response, "FMEA ANALYSIS")
        self.assertContains(response, "DFMEA")
        self.assertContains(response, "PFMEA")
        self.assertContains(response, "VALIDATION & CHANGE")
        self.assertContains(response, "Evidence & Tests")
        self.assertContains(response, "Change Impact")
        self.assertContains(response, "FMEA ELEMENTS")
        self.assertContains(response, "Failure Modes")
        self.assertContains(response, "Causes")
        self.assertContains(response, "Effects")
        self.assertContains(response, "Preventive Controls")
        self.assertContains(response, "Detection Controls")
        self.assertContains(response, "Actions")
        self.assertContains(response, "Import & Review")
        self.assertContains(response, "Ishikawa / Cause Analysis")

        self.assertContains(response, "Process Characteristics")
        self.assertNotContains(response, "Process Control Characteristics")

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

    def test_shell_runtime_assets_are_offline_safe(self):
        template_roots = [
            Path(settings.BASE_DIR) / "django_app" / "fmea_app" / "templates",
            Path(settings.BASE_DIR) / "django_app" / "fmea_review" / "templates",
            Path(settings.BASE_DIR) / "django_app" / "fmea_app" / "static",
        ]
        forbidden = ("http://", "https://", "cdn.", "fonts.googleapis", "unpkg", "jsdelivr")
        checked_files = []

        for root in template_roots:
            for path in root.rglob("*"):
                if path.suffix.lower() not in {".html", ".css", ".js"}:
                    continue
                checked_files.append(path)
                content = path.read_text(encoding="utf-8")
                for token in forbidden:
                    self.assertNotIn(token, content, f"{path} references {token}")

        self.assertTrue(checked_files)

    def test_local_static_theme_is_discoverable(self):
        theme_path = find("fmea_app/css/theme.css")

        self.assertIsNotNone(theme_path)
        content = Path(theme_path).read_text(encoding="utf-8")
        self.assertIn("--bg-app", content)

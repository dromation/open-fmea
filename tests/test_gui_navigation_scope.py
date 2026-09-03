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

        for unbuilt_label in (
            "Validation Trajectory",
            "CAPA",
            "Control Plans",
            "AI Assistant",
            "AP/Detection",
            "Evidence & Tests",
            "Change Impact",
            "XDA Investigations",
            "SPC/ITRA-DT",
            "Documents & Links",
            "Lessons Learned",
            "Knowledge & References",
            "Operations",
            "Project Health",
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

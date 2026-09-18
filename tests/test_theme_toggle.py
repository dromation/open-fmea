from __future__ import annotations

from pathlib import Path

from django.contrib.staticfiles.finders import find
from django.test import TestCase
from django.urls import reverse

from fmea_app import models as fmea_models

from _contrast import CHECKED_PAIRS, contrast_ratio, extract_theme_tokens


class ThemeToggleTests(TestCase):
    def test_toggle_control_present_on_dashboard(self):
        response = self.client.get(reverse("fmea:dashboard"))

        self.assertContains(response, "data-theme-toggle")
        self.assertContains(response, "theme-toggle-icon-light")
        self.assertContains(response, "theme-toggle-icon-dark")

    def test_toggle_control_present_on_a_detail_page(self):
        fmea = fmea_models.FMEA.objects.create(
            stable_id="fmea:theme-toggle-detail",
            name="Theme Toggle Detail Fixture",
        )

        response = self.client.get(reverse("fmea:fmea_detail", args=[fmea.stable_id]))

        self.assertContains(response, "data-theme-toggle")

    def test_toggle_is_in_the_shared_header_not_duplicated_per_page(self):
        dashboard_response = self.client.get(reverse("fmea:dashboard"))
        fmea = fmea_models.FMEA.objects.create(
            stable_id="fmea:theme-toggle-shared",
            name="Theme Toggle Shared Header Fixture",
        )
        detail_response = self.client.get(reverse("fmea:fmea_detail", args=[fmea.stable_id]))

        for response in (dashboard_response, detail_response):
            self.assertEqual(response.content.decode().count("data-theme-toggle"), 1)

    def test_theme_css_defines_dark_default_and_light_override_tokens(self):
        theme_path = find("fmea_app/css/theme.css")
        self.assertIsNotNone(theme_path)
        content = Path(theme_path).read_text(encoding="utf-8")

        self.assertIn(":root {", content)
        self.assertIn("color-scheme: dark;", content)
        self.assertIn("--bg-app: #0e121b;", content)

        self.assertIn('[data-theme="light"]', content)
        self.assertIn("prefers-color-scheme: light", content)
        self.assertIn("--bg-app: #f5f7fb;", content)
        self.assertIn("--text-primary: #0f172a;", content)

    def test_app_js_reads_and_writes_the_theme_preference_defensively(self):
        js_path = find("fmea_app/js/app.js")
        self.assertIsNotNone(js_path)
        content = Path(js_path).read_text(encoding="utf-8")

        self.assertIn("open-fmea-theme", content)
        self.assertIn("data-theme-toggle", content)
        self.assertIn("try {", content)
        self.assertIn("catch", content)

    def test_existing_navigation_scope_is_unaffected(self):
        response = self.client.get(reverse("fmea:dashboard"))

        self.assertContains(response, "Home")
        self.assertContains(response, "Risk Matrix")
        for unbuilt_label in ("Validation Trajectory", "CAPA", "Control Plans"):
            self.assertNotContains(response, unbuilt_label)

    def test_wcag_aa_contrast_for_text_background_pairs(self):
        theme_path = find("fmea_app/css/theme.css")
        self.assertIsNotNone(theme_path)
        content = Path(theme_path).read_text(encoding="utf-8")

        dark_tokens = extract_theme_tokens(content, ":root {")
        light_tokens = extract_theme_tokens(content, ':root[data-theme="light"] {')

        for foreground, background in CHECKED_PAIRS:
            for theme_name, tokens in (("dark", dark_tokens), ("light", light_tokens)):
                self.assertIn(
                    foreground, tokens,
                    f"{foreground} missing from the {theme_name} token block",
                )
                self.assertIn(
                    background, tokens,
                    f"{background} missing from the {theme_name} token block",
                )
                ratio = contrast_ratio(tokens[foreground], tokens[background])
                self.assertGreaterEqual(
                    ratio, 4.5,
                    f"{theme_name} {foreground} ({tokens[foreground]}) on "
                    f"{background} ({tokens[background]}) is only {ratio:.2f}:1, "
                    "below the 4.5:1 AA floor for normal text",
                )

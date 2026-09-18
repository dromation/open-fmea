from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from fmea_app import models


class EngineeringContextTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:engineering-context",
            name="Engineering Context FMEA",
        )
        self.product = models.Product.objects.create(
            stable_id="product:engineering-context",
            fmea=self.fmea,
            name="Hydraulic Pump Assembly",
            part_number="HP-4021",
        )
        models.Function.objects.create(
            stable_id="function:engineering-context-1",
            product=self.product,
            name="Maintain hydraulic pressure",
        )
        models.Function.objects.create(
            stable_id="function:engineering-context-2",
            product=self.product,
            name="Contain fluid",
        )

        self.process = models.Process.objects.create(
            stable_id="process:engineering-context",
            fmea=self.fmea,
            name="Seal Assembly",
            process_code="OP-2000",
        )
        models.Operation.objects.create(
            stable_id="operation:engineering-context-1",
            process=self.process,
            name="Install seal",
            sequence="10",
        )
        models.Operation.objects.create(
            stable_id="operation:engineering-context-2",
            process=self.process,
            name="Torque fasteners",
            sequence="20",
        )
        models.Operation.objects.create(
            stable_id="operation:engineering-context-3",
            process=self.process,
            name="Leak test",
            sequence="30",
        )

    def test_page_renders_panel_headings_and_real_rows(self):
        response = self.client.get(reverse("fmea:engineering_context"))

        self.assertContains(response, "Products")
        self.assertContains(response, "Processes")

        self.assertContains(response, "Hydraulic Pump Assembly")
        self.assertContains(response, "HP-4021")
        self.assertContains(response, "Seal Assembly")
        self.assertContains(response, "OP-2000")

        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea.stable_id])}"'
        )
        self.assertContains(
            response, f'href="{reverse("fmea:process_flow", args=[self.process.stable_id])}"'
        )

    def test_function_and_operation_counts_are_correct(self):
        response = self.client.get(reverse("fmea:engineering_context"))
        content = response.content.decode()

        product_row_start = content.index("Hydraulic Pump Assembly")
        product_row_end = content.index("</tr>", product_row_start)
        self.assertIn(">2<", content[product_row_start:product_row_end])

        process_row_start = content.index("Seal Assembly")
        process_row_end = content.index("</tr>", process_row_start)
        self.assertIn(">3<", content[process_row_start:process_row_end])

    def test_page_stays_within_narrowed_scope(self):
        response = self.client.get(reverse("fmea:engineering_context"))
        content = response.content.decode()

        # Scoped to the page's own <main> content, not the full response: the
        # shared sidebar (rendered on every page via base.html) legitimately
        # gained a real "System / Product / Process" nav link once Slice E
        # was built, so a blanket page-wide "System" exclusion would now
        # trip on that unrelated, correctly-built link - the same category
        # of false failure as the shared header's theme-toggle <svg> icons
        # caught before this test was first written.
        main_start = content.index('<main class="content-shell">')
        main_content = content[main_start:]

        for excluded in ("System", "Classification", "Control Plan", "<canvas"):
            self.assertNotIn(excluded, main_content)

    def test_sidebar_links_to_engineering_context_under_context_group(self):
        response = self.client.get(reverse("fmea:dashboard"))

        self.assertContains(response, "Engineering Context")
        self.assertContains(
            response, f'href="{reverse("fmea:engineering_context")}"'
        )

from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from fmea_app import forms, models


class SystemListTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:system-slice",
            name="System Slice FMEA",
        )
        self.root_a = models.System.objects.create(
            stable_id="system:root-a",
            name="Vehicle Platform",
            code="SYS-A",
            status="active",
        )
        self.root_b = models.System.objects.create(
            stable_id="system:root-b",
            name="Powertrain",
            code="SYS-B",
            status="inactive",
        )
        self.child = models.System.objects.create(
            stable_id="system:child-a1",
            name="Braking Subsystem",
            code="SYS-A1",
            status="active",
            parent=self.root_a,
        )
        self.product_with_system = models.Product.objects.create(
            stable_id="product:with-system",
            fmea=self.fmea,
            name="Brake Caliper",
            part_number="BC-100",
            system=self.child,
        )
        self.product_without_system = models.Product.objects.create(
            stable_id="product:without-system",
            fmea=self.fmea,
            name="Unassigned Bracket",
            part_number="UB-200",
        )
        self.process_with_system = models.Process.objects.create(
            stable_id="process:with-system",
            fmea=self.fmea,
            name="Caliper Assembly",
            process_code="OP-100",
            system=self.child,
        )
        self.process_without_system = models.Process.objects.create(
            stable_id="process:without-system",
            fmea=self.fmea,
            name="Unassigned Process",
            process_code="OP-200",
        )

    def test_system_list_shows_correct_rows_and_counts(self):
        response = self.client.get(reverse("fmea:system_list"))
        content = response.content.decode()

        self.assertContains(response, "Vehicle Platform")
        self.assertContains(response, "Powertrain")
        self.assertContains(response, "Braking Subsystem")
        self.assertContains(response, "SYS-A1")

        # Root System with no parent shows the em-dash placeholder.
        root_a_start = content.index("Vehicle Platform")
        root_a_end = content.index("</tr>", root_a_start)
        self.assertIn("&mdash;", content[root_a_start:root_a_end])

        # Child System's Parent column links to the parent's own detail page.
        child_start = content.index("Braking Subsystem")
        child_end = content.index("</tr>", child_start)
        child_row = content[child_start:child_end]
        self.assertIn("Vehicle Platform", child_row)
        self.assertIn(
            f'href="{reverse("fmea:system_detail", args=[self.root_a.stable_id])}"',
            child_row,
        )
        # Product/Process counts computed correctly (one of each on the child System).
        self.assertIn(">1<", child_row)

    def test_system_detail_shows_linked_products_processes_and_children(self):
        response = self.client.get(reverse("fmea:system_detail", args=[self.child.stable_id]))

        self.assertContains(response, "Braking Subsystem")
        self.assertContains(response, "Brake Caliper")
        self.assertContains(response, "BC-100")
        self.assertContains(response, "Caliper Assembly")
        self.assertContains(response, "OP-100")
        self.assertContains(
            response, f'href="{reverse("fmea:fmea_detail", args=[self.fmea.stable_id])}"'
        )

        response_root = self.client.get(reverse("fmea:system_detail", args=[self.root_a.stable_id]))
        self.assertContains(response_root, "Braking Subsystem")
        self.assertContains(
            response_root,
            f'href="{reverse("fmea:system_detail", args=[self.child.stable_id])}"',
        )

    def test_system_form_rejects_setting_itself_as_its_own_parent(self):
        form = forms.SystemForm(
            data={
                "name": self.child.name,
                "description": "",
                "code": self.child.code,
                "parent": self.child.pk,
                "status": "active",
            },
            instance=self.child,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("parent", form.errors)

    def test_system_form_parent_queryset_excludes_self_but_offers_others_on_create(self):
        create_form = forms.SystemForm()
        self.assertIn(self.root_a, create_form.fields["parent"].queryset)
        self.assertIn(self.child, create_form.fields["parent"].queryset)

        edit_form = forms.SystemForm(instance=self.child)
        self.assertNotIn(self.child, edit_form.fields["parent"].queryset)
        self.assertIn(self.root_a, edit_form.fields["parent"].queryset)

    def test_system_create_and_edit_views_persist_correctly(self):
        create_response = self.client.post(
            reverse("fmea:system_create"),
            data={"name": "New System", "description": "", "code": "SYS-NEW", "parent": "", "status": "active"},
        )
        created = models.System.objects.get(name="New System")
        self.assertRedirects(create_response, reverse("fmea:system_detail", args=[created.stable_id]))

        edit_response = self.client.post(
            reverse("fmea:system_edit", args=[created.stable_id]),
            data={
                "name": "New System",
                "description": "Updated",
                "code": "SYS-NEW",
                "parent": self.root_b.pk,
                "status": "inactive",
            },
        )
        created.refresh_from_db()
        self.assertRedirects(edit_response, reverse("fmea:system_detail", args=[created.stable_id]))
        self.assertEqual(created.description, "Updated")
        self.assertEqual(created.status, "inactive")
        self.assertEqual(created.parent_id, self.root_b.pk)

    def test_product_and_process_system_fk_persists(self):
        # No ProductForm/ProcessForm (or any create/edit GUI for Product/Process)
        # exists anywhere in this app today - confirmed by grep before writing
        # this slice (zero matches for "ProductForm"/"ProcessForm", zero
        # Product/Process routes in urls.py, zero product/process view
        # functions). Decision 10 / Exact Scope item 6 of the instruction
        # assumed such a form already existed and only needed one field added;
        # that assumption does not hold, so no new Product/Process CRUD GUI is
        # built here (out of this slice's allowed-file list). This test
        # instead verifies the actual, in-scope requirement - the model-level
        # `system` FK on Product/Process (Decision 1 / Exact Scope item 2) -
        # persists and reloads correctly.
        product = models.Product.objects.create(
            stable_id="product:fk-check",
            fmea=self.fmea,
            name="FK Check Product",
            system=self.root_a,
        )
        process = models.Process.objects.create(
            stable_id="process:fk-check",
            fmea=self.fmea,
            name="FK Check Process",
            system=self.root_b,
        )
        product.refresh_from_db()
        process.refresh_from_db()
        self.assertEqual(product.system_id, self.root_a.pk)
        self.assertEqual(process.system_id, self.root_b.pk)

    def test_products_and_processes_without_a_system_render_correctly_everywhere(self):
        # Regression check, not new functionality: existing rows with no
        # System assigned must keep rendering with no error everywhere they
        # already appear.
        context_response = self.client.get(reverse("fmea:engineering_context"))
        self.assertEqual(context_response.status_code, 200)
        self.assertContains(context_response, "Unassigned Bracket")
        self.assertContains(context_response, "Unassigned Process")

        fmea_response = self.client.get(reverse("fmea:fmea_detail", args=[self.fmea.stable_id]))
        self.assertEqual(fmea_response.status_code, 200)

        system_list_response = self.client.get(reverse("fmea:system_list"))
        self.assertEqual(system_list_response.status_code, 200)

    def test_sidebar_links_to_system_list_under_context_group(self):
        response = self.client.get(reverse("fmea:dashboard"))

        self.assertContains(response, "System / Product / Process")
        self.assertContains(response, f'href="{reverse("fmea:system_list")}"')

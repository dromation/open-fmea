from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from fmea_app import models


class SystemModelTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:system-model",
            name="System Model FMEA",
        )
        self.root = models.System.objects.create(
            stable_id="system:model-root",
            name="Vehicle Platform",
            code="SYS-ROOT",
        )
        self.child = models.System.objects.create(
            stable_id="system:model-child",
            name="Braking Subsystem",
            code="SYS-CHILD",
            parent=self.root,
        )
        self.grandchild = models.System.objects.create(
            stable_id="system:model-grandchild",
            name="Caliper Group",
            code="SYS-GRANDCHILD",
            parent=self.child,
        )

    def test_creating_a_system_with_a_parent_is_reflected_in_parents_children(self):
        self.assertIn(self.child, self.root.children.all())
        self.assertIn(self.grandchild, self.child.children.all())

    def test_setting_a_systems_parent_to_itself_is_rejected(self):
        self.root.parent = self.root
        with self.assertRaises(ValidationError) as ctx:
            self.root.full_clean()
        self.assertIn("parent", ctx.exception.message_dict)

    def test_setting_a_systems_parent_to_its_own_grandchild_descendant_is_rejected(self):
        # root -> child -> grandchild. Making root's parent = grandchild would
        # create a cycle two levels deep.
        self.root.parent = self.grandchild
        with self.assertRaises(ValidationError) as ctx:
            self.root.full_clean()
        self.assertIn("parent", ctx.exception.message_dict)

    def test_product_and_process_with_no_system_still_save_and_display_correctly(self):
        product = models.Product.objects.create(
            stable_id="product:system-model-unassigned",
            fmea=self.fmea,
            name="Unassigned Product",
        )
        process = models.Process.objects.create(
            stable_id="process:system-model-unassigned",
            fmea=self.fmea,
            name="Unassigned Process",
        )
        product.full_clean()
        process.full_clean()
        self.assertIsNone(product.system_id)
        self.assertIsNone(process.system_id)

from __future__ import annotations

from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from fmea_app import models
from fmea_app.services import (
    DomainConstructionError,
    create_cause_influence,
    transition_cause_influence,
)
from fmea_domain import CauseInfluenceStatus


class CauseInfluenceDjangoTests(TestCase):
    def setUp(self) -> None:
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:cause-influence-django",
            name="Cause Influence FMEA",
        )
        self.failure_mode = models.FailureMode.objects.create(
            stable_id="failure-mode:cause-influence-django",
            fmea=self.fmea,
            name="Seal leaks",
        )
        self.failure_cause = models.FailureCause.objects.create(
            stable_id="failure-cause:seal-nicked-django",
            failure_mode=self.failure_mode,
            name="Seal nicked",
        )
        self.mechanism = models.FailureMechanism.objects.create(
            stable_id="failure-mechanism:sharp-edge-django",
            failure_cause=self.failure_cause,
            name="Sharp edge contacts seal lip",
        )

    def test_seed_cause_category_scheme_is_idempotent(self):
        stdout = StringIO()
        call_command("seed_cause_category_scheme", stdout=stdout)
        call_command("seed_cause_category_scheme", stdout=stdout)

        self.assertEqual(models.CauseCategoryScheme.objects.count(), 1)
        scheme = models.CauseCategoryScheme.objects.get()
        self.assertEqual(scheme.name, "Ishikawa 5M+E (default)")
        self.assertEqual(models.CauseCategory.objects.count(), 6)
        self.assertEqual(
            list(models.CauseCategory.objects.order_by("sort_order").values_list("name", flat=True)),
            ["Man", "Machine", "Material", "Method", "Measurement", "Environment"],
        )
        self.assertIn("Seeded cause-category scheme", stdout.getvalue())

    def test_model_validation_rejects_confirmed_root_cause_targeting_failure_mode(self):
        influence = models.CauseInfluence(
            stable_id="cause-influence:invalid-confirmed-django",
            source_type="FailureCause",
            source_id=self.failure_cause.stable_id,
            target_type="FailureMode",
            target_id=self.failure_mode.stable_id,
            influence_type="produces",
            status=CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE.value,
        )

        with self.assertRaisesRegex(ValidationError, "confirmed_root_cause"):
            influence.full_clean()

    def test_create_service_rejects_wrong_typed_reference(self):
        with self.assertRaisesRegex(DomainConstructionError, "No FailureMechanism"):
            create_cause_influence(
                source_type="FailureMechanism",
                source_id=self.failure_cause.stable_id,
                target_type="FailureMode",
                target_id=self.failure_mode.stable_id,
                influence_type="produces",
            )

    def test_create_service_persists_valid_cause_influence(self):
        call_command("seed_cause_category_scheme")
        category = models.CauseCategory.objects.get(name="Method")

        influence = create_cause_influence(
            source_type="FailureCause",
            source_id=self.failure_cause.stable_id,
            target_type="FailureMode",
            target_id=self.failure_mode.stable_id,
            influence_type="produces",
            cause_category_id=category.stable_id,
            strength="medium",
        )

        self.assertEqual(influence.status, CauseInfluenceStatus.SUSPECTED.value)
        self.assertEqual(influence.cause_category_id, category.stable_id)
        self.assertEqual(models.CauseInfluence.objects.count(), 1)

    def test_transition_to_confirmed_retargets_to_failure_cause_atomically(self):
        influence = create_cause_influence(
            source_type="FailureMechanism",
            source_id=self.mechanism.stable_id,
            target_type="FailureMode",
            target_id=self.failure_mode.stable_id,
            influence_type="produces",
            status=CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED.value,
            review_note="Initial test evidence.",
        )

        transition_cause_influence(
            influence,
            new_status=CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE.value,
            failure_cause_stable_id=self.failure_cause.stable_id,
            review_note="Controlled reproduction confirmed the root cause.",
        )

        influence.refresh_from_db()
        self.assertEqual(influence.status, CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE.value)
        self.assertEqual(influence.target_type, "FailureCause")
        self.assertEqual(influence.target_id, self.failure_cause.stable_id)

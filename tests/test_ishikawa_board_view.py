from __future__ import annotations

from django.core.management import call_command
from django.test import TestCase

from fmea_app import models
from fmea_app.services import create_cause_influence
from fmea_domain import CauseInfluenceStatus


class IshikawaBoardViewTests(TestCase):
    def setUp(self) -> None:
        call_command("seed_cause_category_scheme")
        self.method_category = models.CauseCategory.objects.get(name="Method")
        self.fmea = models.FMEA.objects.create(
            stable_id="fmea:ishikawa-view",
            name="Ishikawa View FMEA",
        )
        self.failure_mode = models.FailureMode.objects.create(
            stable_id="failure-mode:ishikawa-seal-leak",
            fmea=self.fmea,
            name="Seal leaks",
        )
        self.failure_cause = models.FailureCause.objects.create(
            stable_id="failure-cause:ishikawa-seal-nicked",
            failure_mode=self.failure_mode,
            name="Seal nicked",
        )
        self.mechanism = models.FailureMechanism.objects.create(
            stable_id="failure-mechanism:ishikawa-sharp-edge",
            failure_cause=self.failure_cause,
            name="Sharp edge contacts seal lip",
        )

    def test_ishikawa_board_groups_influences_by_category(self):
        create_cause_influence(
            source_type="FailureCause",
            source_id=self.failure_cause.stable_id,
            target_type="FailureMode",
            target_id=self.failure_mode.stable_id,
            influence_type="produces",
            cause_category_id=self.method_category.stable_id,
        )
        create_cause_influence(
            source_type="FailureMechanism",
            source_id=self.mechanism.stable_id,
            target_type="FailureMode",
            target_id=self.failure_mode.stable_id,
            influence_type="contributes_to",
        )

        response = self.client.get(
            f"/failure-modes/{self.failure_mode.stable_id}/ishikawa-board/"
        )

        self.assertContains(response, "Method")
        self.assertContains(response, "Uncategorized")
        self.assertContains(response, "Seal nicked")
        self.assertContains(response, "Sharp edge contacts seal lip")

    def test_create_view_starts_influence_as_suspected(self):
        response = self.client.post(
            "/cause-influences/create/",
            {
                "source_type": "FailureCause",
                "source_id": self.failure_cause.stable_id,
                "target_type": "FailureMode",
                "target_id": self.failure_mode.stable_id,
                "influence_type": "produces",
                "status": CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE.value,
                "cause_category_id": self.method_category.stable_id,
                "source_context": "FMEA",
            },
        )

        self.assertEqual(response.status_code, 302)
        influence = models.CauseInfluence.objects.get()
        self.assertEqual(influence.status, CauseInfluenceStatus.SUSPECTED.value)
        self.assertEqual(influence.cause_category_id, self.method_category.stable_id)

    def test_backward_transition_is_rejected_without_mutating_status(self):
        influence = create_cause_influence(
            source_type="FailureCause",
            source_id=self.failure_cause.stable_id,
            target_type="FailureMode",
            target_id=self.failure_mode.stable_id,
            influence_type="produces",
            status=CauseInfluenceStatus.CORRELATED.value,
        )

        response = self.client.post(
            f"/cause-influences/{influence.stable_id}/transition/",
            {"new_status": CauseInfluenceStatus.POSSIBLE.value},
            follow=True,
        )

        self.assertContains(response, "Backward CauseInfluence transition is not allowed")
        influence.refresh_from_db()
        self.assertEqual(influence.status, CauseInfluenceStatus.CORRELATED.value)

    def test_confirming_failure_mode_target_requires_failure_cause_retarget(self):
        influence = create_cause_influence(
            source_type="FailureMechanism",
            source_id=self.mechanism.stable_id,
            target_type="FailureMode",
            target_id=self.failure_mode.stable_id,
            influence_type="produces",
            status=CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED.value,
            cause_category_id=self.method_category.stable_id,
        )

        response = self.client.post(
            f"/cause-influences/{influence.stable_id}/transition/",
            {
                "new_status": CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE.value,
                "review_note": "Controlled trial reproduced the issue.",
                "cause_category_id": self.method_category.stable_id,
            },
            follow=True,
        )

        self.assertContains(
            response,
            "failure_cause_stable_id is required when confirming a FailureMode-targeted influence",
        )
        influence.refresh_from_db()
        self.assertEqual(influence.status, CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED.value)
        self.assertEqual(influence.target_type, "FailureMode")

    def test_confirming_root_cause_retargets_to_failure_cause(self):
        influence = create_cause_influence(
            source_type="FailureMechanism",
            source_id=self.mechanism.stable_id,
            target_type="FailureMode",
            target_id=self.failure_mode.stable_id,
            influence_type="produces",
            status=CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED.value,
            cause_category_id=self.method_category.stable_id,
        )

        response = self.client.post(
            f"/cause-influences/{influence.stable_id}/transition/",
            {
                "new_status": CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE.value,
                "failure_cause_stable_id": self.failure_cause.stable_id,
                "review_note": "Controlled trial reproduced the issue.",
                "cause_category_id": self.method_category.stable_id,
            },
            follow=True,
        )

        self.assertContains(response, "Cause influence status updated.")
        influence.refresh_from_db()
        self.assertEqual(influence.status, CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE.value)
        self.assertEqual(influence.target_type, "FailureCause")
        self.assertEqual(influence.target_id, self.failure_cause.stable_id)
        self.assertEqual(influence.cause_category_id, self.method_category.stable_id)

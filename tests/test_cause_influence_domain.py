from __future__ import annotations

import unittest

from fmea_domain import (
    CauseCategory,
    CauseCategoryScheme,
    CauseInfluence,
    CauseInfluenceStatus,
)


class CauseInfluenceDomainTests(unittest.TestCase):
    def test_cause_category_scheme_and_category_construct(self):
        scheme = CauseCategoryScheme(
            stable_id="cause-category-scheme:test",
            name="Ishikawa 5M+E",
            description="Default cause categories",
        )
        category = CauseCategory(
            stable_id="cause-category:test:method",
            scheme_id=scheme.stable_id,
            name="Method",
            sort_order=4,
        )

        self.assertEqual(category.scheme_id, scheme.stable_id)
        self.assertEqual(category.name, "Method")

    def test_cause_influence_constructs_with_allowed_types(self):
        influence = CauseInfluence(
            stable_id="cause-influence:test:001",
            source_id="failure-cause:seal-nicked",
            source_type="FailureCause",
            target_id="failure-mode:seal-leak",
            target_type="FailureMode",
            influence_type="produces",
            status=CauseInfluenceStatus.SUSPECTED,
            cause_category_id="cause-category:test:method",
            confidence=0.7,
            strength="medium",
            evidence_ids=("evidence:trial-001",),
            source_context="FMEA",
        )

        self.assertEqual(influence.status, CauseInfluenceStatus.SUSPECTED)
        self.assertEqual(influence.target_type, "FailureMode")

    def test_cause_influence_accepts_process_characteristic_source(self):
        influence = CauseInfluence(
            stable_id="cause-influence:test:002",
            source_id="process-characteristic:installation-force",
            source_type="ProcessCharacteristic",
            target_id="failure-mode:seal-leak",
            target_type="FailureMode",
            influence_type="contributes_to",
        )

        self.assertEqual(influence.source_type, "ProcessCharacteristic")

    def test_cause_influence_rejects_unsupported_source_type(self):
        with self.assertRaisesRegex(ValueError, "source_type"):
            CauseInfluence(
                stable_id="cause-influence:test:003",
                source_id="product:invalid",
                source_type="Product",  # type: ignore[arg-type]
                target_id="failure-mode:seal-leak",
                target_type="FailureMode",
                influence_type="produces",
            )

    def test_confirmed_root_cause_requires_failure_cause_target(self):
        with self.assertRaisesRegex(ValueError, "confirmed_root_cause"):
            CauseInfluence(
                stable_id="cause-influence:test:004",
                source_id="failure-cause:seal-nicked",
                source_type="FailureCause",
                target_id="failure-mode:seal-leak",
                target_type="FailureMode",
                influence_type="produces",
                status=CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE,
            )

    def test_confidence_must_be_between_zero_and_one(self):
        with self.assertRaisesRegex(ValueError, "confidence"):
            CauseInfluence(
                stable_id="cause-influence:test:005",
                source_id="failure-cause:seal-nicked",
                source_type="FailureCause",
                target_id="failure-mode:seal-leak",
                target_type="FailureMode",
                influence_type="produces",
                confidence=1.5,
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domain"))
sys.path.insert(0, str(ROOT / "django_app"))

from fmea_domain import (  # noqa: E402
    CauseCategory,
    CauseCategoryScheme,
    CauseInfluence,
    CauseInfluenceStatus,
    EvaluationDefinition,
    FMEA,
    FMEADocument,
    FMEARevision,
    FMEALifecycle,
    FailureMode,
    Operation,
    ProcessCharacteristic,
    Product,
    ProductCharacteristic,
    Relationship,
    RiskEvaluation,
    RiskRating,
)
from fmea_importexport import export_document, import_document, to_json  # noqa: E402


class OfefExportTests(unittest.TestCase):
    def test_ofef_round_trip_preserves_portable_identity(self):
        definition = EvaluationDefinition(
            stable_id="eval:classic-rpn",
            method="classic-rpn",
            name="Classic RPN",
        )
        category_scheme = CauseCategoryScheme(
            stable_id="cause-category-scheme:ishikawa-5me-test",
            name="Ishikawa 5M+E",
        )
        category = CauseCategory(
            stable_id="cause-category:ishikawa-5me:method-test",
            scheme_id=category_scheme.stable_id,
            name="Method",
            sort_order=4,
        )
        failure_mode = FailureMode(
            stable_id="fm:seal-leak-001",
            fmea_id="fmea:process-001",
            name="Seal leaks",
        )
        product_characteristic = ProductCharacteristic(
            stable_id="product-characteristic:seal-seat-001",
            requirement_id="requirement:seal-seat-001",
            name="Seal seat surface condition",
            is_special=True,
        )
        process_characteristic = ProcessCharacteristic(
            stable_id="process-characteristic:installation-force-001",
            operation_id="operation:install-seal-001",
            name="Seal installation force",
            cause_category_id=category.stable_id,
            attributes={"nominal": "controlled insertion"},
        )
        influence = CauseInfluence(
            stable_id="cause-influence:seal-nick-method",
            source_id="failure-cause:seal-nicked-001",
            source_type="FailureCause",
            target_id=failure_mode.stable_id,
            target_type="FailureMode",
            influence_type="produces",
            status=CauseInfluenceStatus.CORRELATED,
            cause_category_id=category.stable_id,
            evidence_ids=("evidence:fixture-trial-001",),
            source_context="FMEA",
            review_note="Observed on three matching lots.",
        )
        document = FMEADocument(
            stable_id="doc:process-001",
            fmea=FMEA(
                stable_id="fmea:process-001",
                name="Process FMEA",
                lifecycle=FMEALifecycle.IN_REVIEW,
            ),
            entities=(
                Product(stable_id="product:caliper-001", name="Caliper"),
                Operation(
                    stable_id="operation:install-seal-001",
                    process_id="process:assembly-001",
                    name="Install seal",
                ),
                definition,
                category_scheme,
                category,
                product_characteristic,
                process_characteristic,
                failure_mode,
                influence,
            ),
            relationships=(
                Relationship(
                    stable_id="rel:product-function-001",
                    source_id="product:caliper-001",
                    target_id="fm:seal-leak-001",
                    relationship_type="product_has_failure_mode",
                ),
            ),
            evaluations=(
                RiskEvaluation(
                    stable_id="risk:seal-leak-001",
                    failure_mode_id=failure_mode.stable_id,
                    evaluation_definition_id=definition.stable_id,
                    method="classic-rpn",
                    inputs=RiskRating(severity=9, occurrence=4, detection=5),
                    result={"score": 180, "classification": "medium"},
                    evaluated_at=datetime(2026, 8, 30, tzinfo=timezone.utc),
                ),
            ),
            revisions=(
                FMEARevision(
                    stable_id="rev:process-001-001",
                    fmea_id="fmea:process-001",
                    revision_number=1,
                    lifecycle_from=FMEALifecycle.DRAFT,
                    lifecycle_to=FMEALifecycle.IN_REVIEW,
                    reason="Initial review",
                    actor="test",
                    created_at=datetime(2026, 8, 30, tzinfo=timezone.utc),
                ),
            ),
        )

        payload = export_document(document)
        restored = import_document(json.loads(to_json(document)))

        self.assertEqual(payload["format"], "open-fmea-exchange")
        self.assertEqual(document.all_stable_ids(), restored.all_stable_ids())
        restored_influence = next(
            entity for entity in restored.entities if entity.stable_id == influence.stable_id
        )
        self.assertEqual(restored_influence.status, CauseInfluenceStatus.CORRELATED)
        self.assertEqual(restored_influence.evidence_ids, ("evidence:fixture-trial-001",))
        restored_process_characteristic = next(
            entity
            for entity in restored.entities
            if entity.stable_id == process_characteristic.stable_id
        )
        self.assertEqual(
            restored_process_characteristic.attributes,
            {"nominal": "controlled insertion"},
        )
        self.assert_no_integer_pk_keys(payload)

    def assert_no_integer_pk_keys(self, value):
        if isinstance(value, dict):
            self.assertNotIn("id", value)
            for child in value.values():
                self.assert_no_integer_pk_keys(child)
        elif isinstance(value, list):
            for child in value:
                self.assert_no_integer_pk_keys(child)


if __name__ == "__main__":
    unittest.main()

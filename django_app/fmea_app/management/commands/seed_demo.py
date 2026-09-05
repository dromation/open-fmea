from __future__ import annotations

from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from django.db import transaction

from fmea_domain import ActionStatus, CauseInfluenceStatus, FMEALifecycle
from fmea_evaluation import ACTION_PRIORITY_POC_METHOD, CLASSIC_RPN_METHOD

from fmea_app import models
from fmea_app.management.commands.seed_cause_category_scheme import (
    DEFAULT_CATEGORIES,
    DEFAULT_SCHEME_STABLE_ID,
)
from fmea_app.services import evaluate_failure_mode


DEMO_TIMESTAMP = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)


class Command(BaseCommand):
    help = "Seed a small Open-FMEA demo vertical slice."

    @transaction.atomic
    def handle(self, *args, **options):
        classic, _ = models.EvaluationDefinition.objects.update_or_create(
            method=CLASSIC_RPN_METHOD,
            defaults={
                "stable_id": "demo:evaluation-definition:classic-rpn",
                "name": "Classic RPN",
                "rating_scales": _default_rating_scales(),
                "configuration": {"formula": "severity * occurrence * detection"},
            },
        )
        ap, _ = models.EvaluationDefinition.objects.update_or_create(
            method=ACTION_PRIORITY_POC_METHOD,
            defaults={
                "stable_id": "demo:evaluation-definition:action-priority-poc",
                "name": "Action Priority PoC Matrix",
                "rating_scales": _default_rating_scales(),
                "configuration": {"variant": "configurable-poc-matrix"},
            },
        )

        project, _ = models.FMEAProject.objects.update_or_create(
            stable_id="demo:project:brake-assembly",
            defaults={
                "name": "Brake Assembly Launch",
                "description": "Demo project for the first Open-FMEA vertical slice.",
            },
        )
        fmea, _ = models.FMEA.objects.update_or_create(
            stable_id="demo:fmea:brake-assembly-process",
            defaults={
                "project": project,
                "name": "Brake Assembly Process FMEA",
                "description": "Initial process FMEA for assembly risk review.",
                "fmea_type": "process",
                "scope": "Station 20 brake caliper assembly and verification.",
                "lifecycle": FMEALifecycle.IN_REVIEW.value,
                "team": ["Quality Engineer", "Manufacturing Engineer", "Production Lead"],
            },
        )
        product, _ = models.Product.objects.update_or_create(
            stable_id="demo:product:brake-caliper",
            defaults={
                "fmea": fmea,
                "name": "Brake Caliper Assembly",
                "part_number": "BC-DEMO-001",
            },
        )
        process, _ = models.Process.objects.update_or_create(
            stable_id="demo:process:assembly",
            defaults={
                "fmea": fmea,
                "name": "Assembly Process",
                "process_code": "ASM-20",
            },
        )
        operation, _ = models.Operation.objects.update_or_create(
            stable_id="demo:operation:station-20",
            defaults={
                "process": process,
                "name": "Install piston seal",
                "sequence": "20",
            },
        )
        function, _ = models.Function.objects.update_or_create(
            stable_id="demo:function:seal-fluid-pressure",
            defaults={
                "product": product,
                "operation": operation,
                "name": "Maintain hydraulic pressure",
                "description": "Seal must prevent fluid leakage under operating load.",
            },
        )
        requirement, _ = models.Requirement.objects.update_or_create(
            stable_id="demo:requirement:leak-rate",
            defaults={
                "function": function,
                "name": "Leak rate below customer limit",
                "source_reference": "REQ-DEMO-042",
            },
        )
        models.ProductCharacteristic.objects.update_or_create(
            stable_id="demo:characteristic:seal-seat-condition",
            defaults={
                "requirement": requirement,
                "name": "Seal seat surface condition",
                "is_special": True,
                "primary_classification_id": None,
            },
        )
        categories = _seed_default_cause_categories()
        models.ProcessCharacteristic.objects.update_or_create(
            stable_id="demo:process-characteristic:installation-force",
            defaults={
                "operation": operation,
                "name": "Seal installation force",
                "description": "Force applied while seating the piston seal.",
                "cause_category_id": categories["Method"].stable_id,
                "attributes": {
                    "nominal": "controlled manual insertion",
                    "observed": "operator-dependent variation",
                },
            },
        )
        failure_mode, _ = models.FailureMode.objects.update_or_create(
            stable_id="demo:failure-mode:seal-leak",
            defaults={
                "fmea": fmea,
                "function": function,
                "requirement": requirement,
                "name": "Seal leaks after assembly",
                "description": "Piston seal does not hold pressure after final assembly.",
            },
        )
        models.FailureEffect.objects.update_or_create(
            stable_id="demo:effect:loss-of-braking",
            defaults={
                "failure_mode": failure_mode,
                "name": "Reduced braking performance",
            },
        )
        cause, _ = models.FailureCause.objects.update_or_create(
            stable_id="demo:cause:seal-nicked",
            defaults={
                "failure_mode": failure_mode,
                "name": "Seal nicked during installation",
            },
        )
        mechanism, _ = models.FailureMechanism.objects.update_or_create(
            stable_id="demo:mechanism:sharp-edge-contact",
            defaults={
                "failure_cause": cause,
                "name": "Sharp edge contacts seal lip",
            },
        )
        models.PreventionControl.objects.update_or_create(
            stable_id="demo:prevention:chamfer-check",
            defaults={
                "failure_cause": cause,
                "name": "Chamfer verification before assembly",
            },
        )
        detection, _ = models.DetectionControl.objects.update_or_create(
            stable_id="demo:detection:pressure-decay",
            defaults={
                "failure_cause": cause,
                "name": "Pressure decay leak test",
            },
        )
        models.MeasurementMethod.objects.update_or_create(
            stable_id="demo:measurement:leak-tester",
            defaults={
                "detection_control": detection,
                "name": "Automated leak tester",
                "unit": "mbar/min",
            },
        )
        role, _ = models.ResponsibleRole.objects.update_or_create(
            stable_id="demo:role:manufacturing-engineer",
            defaults={"name": "Manufacturing Engineer"},
        )
        action, _ = models.RecommendedAction.objects.update_or_create(
            stable_id="demo:action:add-installation-guide",
            defaults={
                "failure_mode": failure_mode,
                "failure_cause": cause,
                "responsible_role": role,
                "name": "Add seal installation guide fixture",
                "status": ActionStatus.IN_PROGRESS.value,
            },
        )
        models.Evidence.objects.update_or_create(
            stable_id="demo:evidence:fixture-trial",
            defaults={
                "action": action,
                "name": "Fixture trial record",
                "reference_uri": "demo://fixture-trial-001",
            },
        )

        _upsert_cause_influence(
            stable_id="demo:cause-influence:seal-nicked-method",
            source_type="FailureCause",
            source_id=cause.stable_id,
            target_type="FailureMode",
            target_id=failure_mode.stable_id,
            influence_type="produces",
            status=CauseInfluenceStatus.POSSIBLE.value,
            cause_category_id=categories["Method"].stable_id,
            strength="medium",
            source_context="seed_demo",
            review_note="Demo: installation method can damage the seal.",
        )
        _upsert_cause_influence(
            stable_id="demo:cause-influence:sharp-edge-machine",
            source_type="FailureMechanism",
            source_id=mechanism.stable_id,
            target_type="FailureMode",
            target_id=failure_mode.stable_id,
            influence_type="contributes_to",
            status=CauseInfluenceStatus.CORRELATED.value,
            cause_category_id=categories["Machine"].stable_id,
            strength="high",
            evidence_ids=["demo:evidence:fixture-trial"],
            source_context="seed_demo",
            review_note="Demo: fixture trial linked the sharp edge to seal damage.",
        )

        _upsert_cause_influence(
            stable_id="demo:cause-influence:installation-force-seal-seat",
            source_type="ProcessCharacteristic",
            source_id="demo:process-characteristic:installation-force",
            target_type="ProductCharacteristic",
            target_id="demo:characteristic:seal-seat-condition",
            influence_type="affects",
            status=CauseInfluenceStatus.POSSIBLE.value,
            cause_category_id=categories["Method"].stable_id,
            strength="medium",
            source_context="seed_demo",
            review_note="Demo: installation force variation affects the seal seat surface condition.",
        )

        models.RiskEvaluation.objects.filter(failure_mode=failure_mode, actor="seed_demo").delete()
        evaluate_failure_mode(
            failure_mode=failure_mode,
            definition=classic,
            severity=9,
            occurrence=4,
            detection=5,
            actor="seed_demo",
            trigger="initial-demo-risk",
            stable_id="demo:risk-evaluation:seal-leak:classic-rpn",
            evaluated_at=DEMO_TIMESTAMP,
        )
        evaluate_failure_mode(
            failure_mode=failure_mode,
            definition=ap,
            severity=9,
            occurrence=4,
            detection=5,
            actor="seed_demo",
            trigger="initial-demo-risk",
            stable_id="demo:risk-evaluation:seal-leak:action-priority",
            evaluated_at=DEMO_TIMESTAMP,
        )

        models.FMEARevision.objects.update_or_create(
            fmea=fmea,
            revision_number=1,
            defaults={
                "stable_id": "demo:revision:brake-assembly-process:001",
                "lifecycle_from": FMEALifecycle.DRAFT.value,
                "lifecycle_to": FMEALifecycle.IN_REVIEW.value,
                "reason": "Initial demo FMEA created for Phase B vertical slice.",
                "actor": "seed_demo",
                "created_at": DEMO_TIMESTAMP,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"Seeded demo FMEA: {fmea.stable_id}"))


def _default_rating_scales() -> dict:
    return {
        "severity": {"minimum": 1, "maximum": 10},
        "occurrence": {"minimum": 1, "maximum": 10},
        "detection": {"minimum": 1, "maximum": 10},
    }


def _seed_default_cause_categories() -> dict[str, models.CauseCategory]:
    scheme, _ = models.CauseCategoryScheme.objects.update_or_create(
        stable_id=DEFAULT_SCHEME_STABLE_ID,
        defaults={
            "name": "Ishikawa 5M+E (default)",
            "description": "Default configurable cause-category scheme for Ishikawa review.",
        },
    )
    categories: dict[str, models.CauseCategory] = {}
    for stable_id, name, description, sort_order in DEFAULT_CATEGORIES:
        category, _ = models.CauseCategory.objects.update_or_create(
            stable_id=stable_id,
            defaults={
                "scheme_id": scheme.stable_id,
                "name": name,
                "description": description,
                "sort_order": sort_order,
            },
        )
        categories[name] = category
    return categories


def _upsert_cause_influence(
    *,
    stable_id: str,
    source_type: str,
    source_id: str,
    target_type: str,
    target_id: str,
    influence_type: str,
    status: str,
    cause_category_id: str,
    strength: str,
    source_context: str,
    review_note: str,
    evidence_ids: list[str] | None = None,
) -> models.CauseInfluence:
    influence, _ = models.CauseInfluence.objects.update_or_create(
        stable_id=stable_id,
        defaults={
            "source_type": source_type,
            "source_id": source_id,
            "target_type": target_type,
            "target_id": target_id,
            "influence_type": influence_type,
            "status": status,
            "cause_category_id": cause_category_id,
            "strength": strength,
            "source_context": source_context,
            "review_note": review_note,
            "evidence_ids": evidence_ids or [],
        },
    )
    influence.full_clean()
    return influence

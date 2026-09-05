from __future__ import annotations

import uuid
from datetime import datetime
from typing import Mapping

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from fmea_domain import (
    CauseInfluenceStatus,
    CauseInfluenceTransitionError,
    FMEADocument,
    Relationship,
    RiskRating,
    validate_cause_influence_transition,
)
from fmea_evaluation import calculate

from . import models


class DomainConstructionError(ValueError):
    pass


_CAUSE_INFLUENCE_MODEL_BY_TYPE = {
    "FailureCause": models.FailureCause,
    "FailureMechanism": models.FailureMechanism,
    "FailureMode": models.FailureMode,
    "ProcessCharacteristic": models.ProcessCharacteristic,
    "ProductCharacteristic": models.ProductCharacteristic,
}


@transaction.atomic
def evaluate_failure_mode(
    *,
    failure_mode: models.FailureMode,
    definition: models.EvaluationDefinition,
    severity: int,
    occurrence: int,
    detection: int,
    actor: str = "system",
    trigger: str = "manual",
    stable_id: str | None = None,
    evaluated_at: datetime | None = None,
    lifecycle_gate: str = "current",
) -> models.RiskEvaluation:
    rating = RiskRating(
        severity=severity,
        occurrence=occurrence,
        detection=detection,
    )
    result = calculate(definition.method, rating)
    values = {
        "failure_mode": failure_mode,
        "definition": definition,
        "method": result.method,
        "severity": severity,
        "occurrence": occurrence,
        "detection": detection,
        "result": result.output,
        "actor": actor,
        "trigger": trigger,
        "lifecycle_gate": lifecycle_gate,
    }
    if evaluated_at is not None:
        values["evaluated_at"] = evaluated_at
    if stable_id is not None:
        evaluation, _ = models.RiskEvaluation.objects.update_or_create(
            stable_id=stable_id,
            defaults=values,
        )
        return evaluation
    return models.RiskEvaluation.objects.create(**values)


@transaction.atomic
def promote_import_candidate_to_domain_object(
    *,
    suggested_domain_type: str,
    extracted_value: str,
    context: Mapping[str, str] | None = None,
) -> models.StableModel:
    """Central construction path for reviewed import candidates."""
    value = extracted_value.strip()
    if not value:
        raise DomainConstructionError("extracted_value is required")
    context = context or {}

    if suggested_domain_type == "Function":
        return models.Function.objects.create(name=value)

    if suggested_domain_type == "Requirement":
        function = _required_context_model(context, "function_stable_id", models.Function)
        return models.Requirement.objects.create(function=function, name=value)

    if suggested_domain_type == "ProductCharacteristic":
        requirement = _optional_context_model(
            context,
            "requirement_stable_id",
            models.Requirement,
        )
        return models.ProductCharacteristic.objects.create(requirement=requirement, name=value)

    if suggested_domain_type == "ProcessCharacteristic":
        operation = _required_context_model(
            context,
            "operation_stable_id",
            models.Operation,
        )
        cause_category_id = context.get("cause_category_stable_id", "").strip() or None
        if cause_category_id:
            _validated_cause_category_id(cause_category_id)
        return models.ProcessCharacteristic.objects.create(
            operation=operation,
            name=value,
            cause_category_id=cause_category_id,
        )

    if suggested_domain_type == "FailureMode":
        fmea = _required_context_model(context, "fmea_stable_id", models.FMEA)
        function = _optional_context_model(context, "function_stable_id", models.Function)
        requirement = _optional_context_model(context, "requirement_stable_id", models.Requirement)
        return models.FailureMode.objects.create(
            fmea=fmea,
            function=function,
            requirement=requirement,
            name=value,
        )

    if suggested_domain_type == "FailureEffect":
        failure_mode = _required_context_model(
            context,
            "failure_mode_stable_id",
            models.FailureMode,
        )
        return models.FailureEffect.objects.create(failure_mode=failure_mode, name=value)

    if suggested_domain_type == "FailureCause":
        failure_mode = _required_context_model(
            context,
            "failure_mode_stable_id",
            models.FailureMode,
        )
        return models.FailureCause.objects.create(failure_mode=failure_mode, name=value)

    if suggested_domain_type == "PreventionControl":
        failure_cause = _required_context_model(
            context,
            "failure_cause_stable_id",
            models.FailureCause,
        )
        return models.PreventionControl.objects.create(failure_cause=failure_cause, name=value)

    if suggested_domain_type == "DetectionControl":
        failure_cause = _required_context_model(
            context,
            "failure_cause_stable_id",
            models.FailureCause,
        )
        return models.DetectionControl.objects.create(failure_cause=failure_cause, name=value)

    raise DomainConstructionError(f"Unsupported import candidate type: {suggested_domain_type}")


@transaction.atomic
def create_cause_influence(
    *,
    source_type: str,
    source_id: str,
    target_type: str,
    target_id: str,
    influence_type: str,
    status: str = CauseInfluenceStatus.SUSPECTED.value,
    cause_category_id: str | None = None,
    confidence: float | None = None,
    strength: str | None = None,
    evidence_ids: tuple[str, ...] = (),
    source_context: str = "FMEA",
    review_note: str = "",
) -> models.CauseInfluence:
    _require_typed_reference(source_type, source_id)
    _require_typed_reference(target_type, target_id)
    category_id = _validated_cause_category_id(cause_category_id)
    influence = models.CauseInfluence(
        source_type=source_type,
        source_id=source_id,
        target_type=target_type,
        target_id=target_id,
        influence_type=influence_type.strip(),
        status=CauseInfluenceStatus(status).value,
        cause_category_id=category_id,
        confidence=confidence,
        strength=(strength or "").strip() or None,
        evidence_ids=list(evidence_ids),
        source_context=(source_context or "FMEA").strip(),
        review_note=review_note.strip(),
    )
    _full_clean_or_domain_error(influence)
    influence.save()
    return influence


@transaction.atomic
def transition_cause_influence(
    influence: models.CauseInfluence,
    *,
    new_status: str,
    review_note: str = "",
    failure_cause_stable_id: str | None = None,
    cause_category_id: str | None = None,
    reviewed_by=None,
) -> models.CauseInfluence:
    target_failure_cause = None
    retarget = (failure_cause_stable_id or "").strip()
    if retarget:
        target_failure_cause = _require_failure_cause_retarget(influence, retarget)

    try:
        validate_cause_influence_transition(
            current_status=CauseInfluenceStatus(influence.status),
            new_status=CauseInfluenceStatus(new_status),
            current_target_type=influence.target_type,
            review_note=review_note,
            evidence_ids=tuple(influence.evidence_ids or ()),
            retarget_failure_cause_stable_id=retarget or None,
        )
    except (CauseInfluenceTransitionError, ValueError) as exc:
        raise DomainConstructionError(str(exc)) from exc

    category_id = (
        influence.cause_category_id
        if cause_category_id is None
        else _validated_cause_category_id(cause_category_id)
    )
    if target_failure_cause is not None:
        influence.target_type = "FailureCause"
        influence.target_id = target_failure_cause.stable_id
    influence.status = CauseInfluenceStatus(new_status).value
    influence.cause_category_id = category_id
    influence.review_note = review_note.strip()
    influence.reviewed_by = _user_or_none(reviewed_by)
    influence.reviewed_at = timezone.now()
    _full_clean_or_domain_error(influence)
    influence.save(
        update_fields=[
            "target_type",
            "target_id",
            "status",
            "cause_category_id",
            "review_note",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )
    return influence


def legal_cause_influence_transition_statuses(
    influence: models.CauseInfluence,
) -> list[CauseInfluenceStatus]:
    legal: list[CauseInfluenceStatus] = []
    for status in CauseInfluenceStatus:
        if status.value == influence.status:
            continue
        try:
            validate_cause_influence_transition(
                current_status=CauseInfluenceStatus(influence.status),
                new_status=status,
                current_target_type=influence.target_type,
                review_note="preview",
                evidence_ids=tuple(influence.evidence_ids or ()),
                retarget_failure_cause_stable_id=(
                    "failure-cause:preview" if influence.target_type == "FailureMode" else None
                ),
            )
        except CauseInfluenceTransitionError:
            continue
        legal.append(status)
    return legal


def build_ofef_document(fmea: models.FMEA) -> FMEADocument:
    entities_by_stable_id = {}
    relationships: list[Relationship] = []

    def add(entity_model: models.StableModel | None):
        if entity_model is not None:
            entities_by_stable_id[entity_model.stable_id] = entity_model.to_domain()

    def relate(source: models.StableModel, target: models.StableModel, relation_type: str):
        relationships.append(
            Relationship(
                stable_id=_relationship_stable_id(
                    source.stable_id,
                    target.stable_id,
                    relation_type,
                ),
                source_id=source.stable_id,
                target_id=target.stable_id,
                relationship_type=relation_type,
                provenance={"source": "django-adapter"},
            )
        )

    add(fmea.project)
    if fmea.project:
        relate(fmea.project, fmea, "project_contains_fmea")

    for product in fmea.products.all():
        add(product)
        relate(fmea, product, "fmea_contains_product")
        for function in product.functions.all():
            add(function)
            relate(product, function, "product_has_function")

    for process in fmea.processes.all():
        add(process)
        relate(fmea, process, "fmea_contains_process")
        for operation in process.operations.all():
            add(operation)
            relate(process, operation, "process_has_operation")
            for function in operation.functions.all():
                add(function)
                relate(operation, function, "operation_has_function")
            for process_characteristic in operation.process_characteristics.all():
                add(process_characteristic)
                relate(
                    operation,
                    process_characteristic,
                    "operation_has_process_characteristic",
                )

    for function in list(entities_by_stable_id.values()):
        if function.__class__.__name__ != "Function":
            continue
        function_model = models.Function.objects.get(stable_id=function.stable_id)
        for requirement in function_model.requirements.all():
            add(requirement)
            relate(function_model, requirement, "function_has_requirement")
            for product_characteristic in requirement.product_characteristics.all():
                add(product_characteristic)
                relate(
                    requirement,
                    product_characteristic,
                    "requirement_has_product_characteristic",
                )

    failure_modes = fmea.failure_modes.select_related("function", "requirement").all()
    for failure_mode in failure_modes:
        add(failure_mode)
        relate(fmea, failure_mode, "fmea_contains_failure_mode")
        if failure_mode.function:
            relate(failure_mode.function, failure_mode, "function_has_failure_mode")
        if failure_mode.requirement:
            relate(failure_mode.requirement, failure_mode, "requirement_has_failure_mode")

        for effect in failure_mode.effects.all():
            add(effect)
            relate(failure_mode, effect, "failure_mode_has_effect")

        for cause in failure_mode.causes.all():
            add(cause)
            relate(failure_mode, cause, "failure_mode_has_cause")
            for mechanism in cause.mechanisms.all():
                add(mechanism)
                relate(cause, mechanism, "failure_cause_has_mechanism")
            for prevention in cause.prevention_controls.all():
                add(prevention)
                relate(cause, prevention, "failure_cause_has_prevention_control")
            for detection in cause.detection_controls.all():
                add(detection)
                relate(cause, detection, "failure_cause_has_detection_control")
                for measurement in detection.measurement_methods.all():
                    add(measurement)
                    relate(detection, measurement, "detection_control_has_measurement")
            for action in cause.recommended_actions.all():
                add(action)
                relate(cause, action, "failure_cause_has_recommended_action")

        for action in failure_mode.recommended_actions.all():
            add(action)
            relate(failure_mode, action, "failure_mode_has_recommended_action")
            if action.responsible_role:
                add(action.responsible_role)
                relate(action, action.responsible_role, "action_has_responsible_role")
            for evidence in action.evidence.all():
                add(evidence)
                relate(action, evidence, "action_has_evidence")
            for verification in action.effectiveness_verifications.all():
                add(verification)
                relate(action, verification, "action_has_effectiveness_verification")

    evaluation_models = list(fmea.risk_evaluations())
    for evaluation in evaluation_models:
        add(evaluation.definition)
    evaluations = tuple(evaluation.to_domain() for evaluation in evaluation_models)
    revisions = tuple(revision.to_domain() for revision in fmea.revisions.all())

    known_ids = {fmea.stable_id, *entities_by_stable_id.keys()}
    cause_influences = models.CauseInfluence.objects.filter(
        Q(source_id__in=known_ids) | Q(target_id__in=known_ids)
    ).order_by("stable_id")
    for influence in cause_influences:
        add(influence)
        if influence.cause_category_id:
            try:
                category = models.CauseCategory.objects.get(stable_id=influence.cause_category_id)
            except models.CauseCategory.DoesNotExist:
                category = None
            add(category)
            if category is not None:
                try:
                    scheme = models.CauseCategoryScheme.objects.get(stable_id=category.scheme_id)
                except models.CauseCategoryScheme.DoesNotExist:
                    scheme = None
                add(scheme)

    known_ids = {fmea.stable_id, *entities_by_stable_id.keys()}
    for relationship in models.DomainRelationship.objects.filter(
        source_stable_id__in=known_ids,
        target_stable_id__in=known_ids,
    ):
        relationships.append(relationship.to_domain())

    return FMEADocument(
        stable_id=f"ofef:{fmea.stable_id}",
        fmea=fmea.to_domain(),
        entities=tuple(entities_by_stable_id.values()),
        relationships=tuple(relationships),
        evaluations=evaluations,
        revisions=revisions,
    )


def get_fmea_by_stable_id(stable_id: str) -> models.FMEA:
    return get_object_or_404(models.FMEA, stable_id=stable_id)


def _relationship_stable_id(source_id: str, target_id: str, relation_type: str) -> str:
    relationship_key = f"open-fmea:{source_id}:{relation_type}:{target_id}"
    return f"rel:{uuid.uuid5(uuid.NAMESPACE_URL, relationship_key).hex}"


def _required_context_model(
    context: Mapping[str, str],
    key: str,
    model_class: type[models.StableModel],
) -> models.StableModel:
    stable_id = context.get(key, "").strip()
    if not stable_id:
        raise DomainConstructionError(f"{key} is required for this candidate type")
    try:
        return model_class.objects.get(stable_id=stable_id)
    except model_class.DoesNotExist as exc:
        raise DomainConstructionError(f"No {model_class.__name__} found for {key}") from exc


def _optional_context_model(
    context: Mapping[str, str],
    key: str,
    model_class: type[models.StableModel],
) -> models.StableModel | None:
    stable_id = context.get(key, "").strip()
    if not stable_id:
        return None
    try:
        return model_class.objects.get(stable_id=stable_id)
    except model_class.DoesNotExist as exc:
        raise DomainConstructionError(f"No {model_class.__name__} found for {key}") from exc


def _require_typed_reference(reference_type: str, stable_id: str) -> models.StableModel:
    model_class = _CAUSE_INFLUENCE_MODEL_BY_TYPE.get(reference_type)
    if model_class is None:
        raise DomainConstructionError(f"Unsupported reference type: {reference_type}")
    stable_id = stable_id.strip()
    if not stable_id:
        raise DomainConstructionError(f"{reference_type} stable_id is required")
    try:
        return model_class.objects.get(stable_id=stable_id)
    except model_class.DoesNotExist as exc:
        raise DomainConstructionError(f"No {reference_type} found for stable_id {stable_id}") from exc


def _validated_cause_category_id(cause_category_id: str | None) -> str | None:
    stable_id = (cause_category_id or "").strip()
    if not stable_id:
        return None
    if not models.CauseCategory.objects.filter(stable_id=stable_id).exists():
        raise DomainConstructionError(f"No CauseCategory found for stable_id {stable_id}")
    return stable_id


def _full_clean_or_domain_error(model_instance: models.StableModel) -> None:
    try:
        model_instance.full_clean()
    except ValidationError as exc:
        messages = []
        if hasattr(exc, "message_dict"):
            for field, field_messages in exc.message_dict.items():
                messages.extend(f"{field}: {message}" for message in field_messages)
        else:
            messages.extend(exc.messages)
        raise DomainConstructionError("; ".join(messages)) from exc


def _require_failure_cause_retarget(
    influence: models.CauseInfluence,
    failure_cause_stable_id: str,
) -> models.FailureCause:
    if influence.target_type != "FailureMode":
        raise DomainConstructionError(
            "failure_cause_stable_id can only retarget an influence currently targeting a FailureMode"
        )
    try:
        failure_cause = models.FailureCause.objects.select_related("failure_mode").get(
            stable_id=failure_cause_stable_id
        )
    except models.FailureCause.DoesNotExist as exc:
        raise DomainConstructionError(
            f"No FailureCause found for stable_id {failure_cause_stable_id}"
        ) from exc
    if failure_cause.failure_mode.stable_id != influence.target_id:
        raise DomainConstructionError(
            "failure_cause_stable_id must belong to the influence's current FailureMode target"
        )
    return failure_cause


def _user_or_none(user):
    if user is None or getattr(user, "is_anonymous", False):
        return None
    return user

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from fmea_domain import (
    ActionStatus,
    CauseCategory as DomainCauseCategory,
    CauseCategoryScheme as DomainCauseCategoryScheme,
    CauseInfluence as DomainCauseInfluence,
    CauseInfluenceStatus,
    DetectionControl as DomainDetectionControl,
    EffectivenessVerification as DomainEffectivenessVerification,
    EvaluationDefinition as DomainEvaluationDefinition,
    Evidence as DomainEvidence,
    FMEA as DomainFMEA,
    FMEALifecycle,
    FMEAProject as DomainFMEAProject,
    FMEARevision as DomainFMEARevision,
    FailureCause as DomainFailureCause,
    FailureEffect as DomainFailureEffect,
    FailureMechanism as DomainFailureMechanism,
    FailureMode as DomainFailureMode,
    Function as DomainFunction,
    MeasurementMethod as DomainMeasurementMethod,
    Operation as DomainOperation,
    PreventionControl as DomainPreventionControl,
    Process as DomainProcess,
    ProcessCharacteristic as DomainProcessCharacteristic,
    Product as DomainProduct,
    ProductCharacteristic as DomainProductCharacteristic,
    RecommendedAction as DomainRecommendedAction,
    Relationship as DomainRelationshipEntity,
    Requirement as DomainRequirement,
    ResponsibleRole as DomainResponsibleRole,
    RiskEvaluation as DomainRiskEvaluation,
    RiskRating,
    new_stable_id,
)


class StableModel(models.Model):
    stable_id = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        editable=False,
        default=new_stable_id,
    )
    schema_version = models.CharField(max_length=16, default="1.0")
    revision = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FMEAProject(StableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainFMEAProject:
        return DomainFMEAProject(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
        )


class FMEA(StableModel):
    FMEA_TYPE_CHOICES = [
        ("design", "Design"),
        ("process", "Process"),
        ("product", "Product"),
        ("software", "Software"),
        ("system", "System"),
    ]

    LIFECYCLE_CHOICES = [(state.value, state.name.replace("_", " ").title()) for state in FMEALifecycle]

    project = models.ForeignKey(
        FMEAProject,
        null=True,
        blank=True,
        related_name="fmeas",
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    fmea_type = models.CharField(max_length=32, choices=FMEA_TYPE_CHOICES, default="process")
    scope = models.TextField(blank=True)
    lifecycle = models.CharField(
        max_length=32,
        choices=LIFECYCLE_CHOICES,
        default=FMEALifecycle.DRAFT.value,
    )
    team = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainFMEA:
        return DomainFMEA(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            fmea_type=self.fmea_type,
            scope=self.scope,
            lifecycle=FMEALifecycle(self.lifecycle),
            project_id=self.project.stable_id if self.project else None,
            team=tuple(self.team or ()),
        )

    def risk_evaluations(self):
        return RiskEvaluation.objects.filter(failure_mode__fmea=self).select_related("definition", "failure_mode")


class Product(StableModel):
    fmea = models.ForeignKey(FMEA, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    part_number = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainProduct:
        return DomainProduct(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            part_number=self.part_number,
        )


class Process(StableModel):
    fmea = models.ForeignKey(FMEA, related_name="processes", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    process_code = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainProcess:
        return DomainProcess(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            process_code=self.process_code,
        )


class Operation(StableModel):
    process = models.ForeignKey(Process, related_name="operations", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["sequence", "name"]

    def __str__(self) -> str:
        return f"{self.sequence} {self.name}".strip()

    def to_domain(self) -> DomainOperation:
        return DomainOperation(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            process_id=self.process.stable_id,
            sequence=self.sequence,
        )


class Function(StableModel):
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        related_name="functions",
        on_delete=models.CASCADE,
    )
    operation = models.ForeignKey(
        Operation,
        null=True,
        blank=True,
        related_name="functions",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainFunction:
        return DomainFunction(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            product_id=self.product.stable_id if self.product else None,
            operation_id=self.operation.stable_id if self.operation else None,
        )


class Requirement(StableModel):
    function = models.ForeignKey(Function, related_name="requirements", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source_reference = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainRequirement:
        return DomainRequirement(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            function_id=self.function.stable_id,
            source_reference=self.source_reference,
        )


class ProductCharacteristic(StableModel):
    requirement = models.ForeignKey(
        Requirement,
        null=True,
        blank=True,
        related_name="product_characteristics",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_special = models.BooleanField(default=False)
    primary_classification_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainProductCharacteristic:
        return DomainProductCharacteristic(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            requirement_id=self.requirement.stable_id if self.requirement else None,
            is_special=self.is_special,
            primary_classification_id=self.primary_classification_id,
        )


class ProcessCharacteristic(StableModel):
    operation = models.ForeignKey(
        Operation,
        related_name="process_characteristics",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cause_category_id = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    attributes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["operation", "name"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        try:
            self.to_domain()
        except (ValueError, TypeError) as exc:
            raise ValidationError(str(exc)) from exc

    def to_domain(self) -> DomainProcessCharacteristic:
        return DomainProcessCharacteristic(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            operation_id=self.operation.stable_id,
            cause_category_id=self.cause_category_id or None,
            attributes=self.attributes or {},
        )


class FailureMode(StableModel):
    fmea = models.ForeignKey(FMEA, related_name="failure_modes", on_delete=models.CASCADE)
    function = models.ForeignKey(
        Function,
        null=True,
        blank=True,
        related_name="failure_modes",
        on_delete=models.SET_NULL,
    )
    requirement = models.ForeignKey(
        Requirement,
        null=True,
        blank=True,
        related_name="failure_modes",
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainFailureMode:
        return DomainFailureMode(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            fmea_id=self.fmea.stable_id,
            function_id=self.function.stable_id if self.function else None,
            requirement_id=self.requirement.stable_id if self.requirement else None,
        )


class FailureEffect(StableModel):
    failure_mode = models.ForeignKey(FailureMode, related_name="effects", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainFailureEffect:
        return DomainFailureEffect(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            failure_mode_id=self.failure_mode.stable_id,
        )


class FailureCause(StableModel):
    failure_mode = models.ForeignKey(FailureMode, related_name="causes", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainFailureCause:
        return DomainFailureCause(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            failure_mode_id=self.failure_mode.stable_id,
        )


class FailureMechanism(StableModel):
    failure_cause = models.ForeignKey(FailureCause, related_name="mechanisms", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainFailureMechanism:
        return DomainFailureMechanism(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            failure_cause_id=self.failure_cause.stable_id,
        )


class PreventionControl(StableModel):
    failure_cause = models.ForeignKey(FailureCause, related_name="prevention_controls", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainPreventionControl:
        return DomainPreventionControl(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            failure_cause_id=self.failure_cause.stable_id,
        )


class DetectionControl(StableModel):
    failure_cause = models.ForeignKey(FailureCause, related_name="detection_controls", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainDetectionControl:
        return DomainDetectionControl(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            failure_cause_id=self.failure_cause.stable_id,
        )


class MeasurementMethod(StableModel):
    detection_control = models.ForeignKey(
        DetectionControl,
        related_name="measurement_methods",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=64, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainMeasurementMethod:
        return DomainMeasurementMethod(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            detection_control_id=self.detection_control.stable_id,
            unit=self.unit,
        )


class ResponsibleRole(StableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainResponsibleRole:
        return DomainResponsibleRole(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
        )


class RecommendedAction(StableModel):
    STATUS_CHOICES = [(status.value, status.name.replace("_", " ").title()) for status in ActionStatus]

    failure_mode = models.ForeignKey(
        FailureMode,
        null=True,
        blank=True,
        related_name="recommended_actions",
        on_delete=models.CASCADE,
    )
    failure_cause = models.ForeignKey(
        FailureCause,
        null=True,
        blank=True,
        related_name="recommended_actions",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    responsible_role = models.ForeignKey(
        ResponsibleRole,
        null=True,
        blank=True,
        related_name="recommended_actions",
        on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=ActionStatus.OPEN.value)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainRecommendedAction:
        return DomainRecommendedAction(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            failure_mode_id=self.failure_mode.stable_id if self.failure_mode else None,
            failure_cause_id=self.failure_cause.stable_id if self.failure_cause else None,
            status=ActionStatus(self.status),
            responsible_role_id=self.responsible_role.stable_id if self.responsible_role else None,
            due_date=self.due_date,
        )


class Evidence(StableModel):
    action = models.ForeignKey(RecommendedAction, related_name="evidence", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    reference_uri = models.CharField(max_length=500, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainEvidence:
        return DomainEvidence(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            action_id=self.action.stable_id,
            reference_uri=self.reference_uri,
        )


class EffectivenessVerification(StableModel):
    action = models.ForeignKey(
        RecommendedAction,
        related_name="effectiveness_verifications",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    result = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainEffectivenessVerification:
        return DomainEffectivenessVerification(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
            action_id=self.action.stable_id,
            result=self.result,
            verified_at=self.verified_at,
        )


class EvaluationDefinition(StableModel):
    method = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rating_scales = models.JSONField(default=dict, blank=True)
    configuration = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.name

    def to_domain(self) -> DomainEvaluationDefinition:
        return DomainEvaluationDefinition(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            method=self.method,
            name=self.name,
            rating_scales=self.rating_scales,
            configuration=self.configuration,
        )


class CauseCategoryScheme(StableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        try:
            self.to_domain()
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    def to_domain(self) -> DomainCauseCategoryScheme:
        return DomainCauseCategoryScheme(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            name=self.name,
            description=self.description,
        )


class CauseCategory(StableModel):
    scheme_id = models.CharField(max_length=128, db_index=True)
    # Permanent constraint: this category model stores process/cause taxonomy only,
    # never subjective personal, health, demographic, or blame-oriented data.
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["scheme_id", "sort_order", "name"]
        unique_together = [("scheme_id", "name")]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        try:
            self.to_domain()
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    def to_domain(self) -> DomainCauseCategory:
        return DomainCauseCategory(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            scheme_id=self.scheme_id,
            name=self.name,
            description=self.description,
            sort_order=self.sort_order,
        )


class CauseInfluence(StableModel):
    SOURCE_TYPE_CHOICES = [
        ("FailureCause", "Failure Cause"),
        ("FailureMechanism", "Failure Mechanism"),
        ("ProcessCharacteristic", "Process Characteristic"),
    ]
    TARGET_TYPE_CHOICES = [
        ("FailureMode", "Failure Mode"),
        ("FailureCause", "Failure Cause"),
        ("ProductCharacteristic", "Product Characteristic"),
    ]
    STATUS_CHOICES = [
        (status.value, status.name.replace("_", " ").title())
        for status in CauseInfluenceStatus
    ]

    source_id = models.CharField(max_length=128, db_index=True)
    source_type = models.CharField(max_length=64, choices=SOURCE_TYPE_CHOICES)
    target_id = models.CharField(max_length=128, db_index=True)
    target_type = models.CharField(max_length=64, choices=TARGET_TYPE_CHOICES)
    influence_type = models.CharField(max_length=128)
    status = models.CharField(
        max_length=64,
        choices=STATUS_CHOICES,
        default=CauseInfluenceStatus.SUSPECTED.value,
        db_index=True,
    )
    cause_category_id = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    confidence = models.FloatField(null=True, blank=True)
    strength = models.CharField(max_length=128, blank=True, null=True)
    evidence_ids = models.JSONField(default=list, blank=True)
    source_context = models.CharField(max_length=128, default="FMEA")
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="cause_influence_reviews",
        on_delete=models.SET_NULL,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["target_type", "target_id", "status", "source_type", "source_id"]
        indexes = [
            models.Index(fields=["target_type", "target_id"], name="cause_infl_target_idx"),
            models.Index(fields=["source_type", "source_id"], name="cause_infl_source_idx"),
            models.Index(fields=["status", "cause_category_id"], name="cause_infl_status_cat_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.source_type}:{self.source_id} -> {self.target_type}:{self.target_id}"

    def clean(self) -> None:
        super().clean()
        try:
            self.to_domain()
        except (ValueError, TypeError) as exc:
            raise ValidationError(str(exc)) from exc

    def to_domain(self) -> DomainCauseInfluence:
        return DomainCauseInfluence(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            source_id=self.source_id,
            source_type=self.source_type,  # type: ignore[arg-type]
            target_id=self.target_id,
            target_type=self.target_type,  # type: ignore[arg-type]
            influence_type=self.influence_type,
            status=CauseInfluenceStatus(self.status),
            cause_category_id=self.cause_category_id or None,
            confidence=self.confidence,
            strength=self.strength,
            evidence_ids=tuple(self.evidence_ids or ()),
            source_context=self.source_context,
            review_note=self.review_note,
        )


class RiskEvaluation(StableModel):
    failure_mode = models.ForeignKey(FailureMode, related_name="risk_evaluations", on_delete=models.CASCADE)
    definition = models.ForeignKey(EvaluationDefinition, related_name="risk_evaluations", on_delete=models.PROTECT)
    method = models.CharField(max_length=64)
    severity = models.PositiveSmallIntegerField()
    occurrence = models.PositiveSmallIntegerField()
    detection = models.PositiveSmallIntegerField()
    result = models.JSONField(default=dict)
    evaluated_at = models.DateTimeField(default=timezone.now)
    actor = models.CharField(max_length=255, default="system")
    trigger = models.CharField(max_length=64, default="manual")

    class Meta:
        ordering = ["-evaluated_at", "-id"]

    def __str__(self) -> str:
        return f"{self.failure_mode} - {self.method}"

    def to_domain(self) -> DomainRiskEvaluation:
        return DomainRiskEvaluation(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            failure_mode_id=self.failure_mode.stable_id,
            evaluation_definition_id=self.definition.stable_id,
            method=self.method,
            inputs=RiskRating(
                severity=self.severity,
                occurrence=self.occurrence,
                detection=self.detection,
            ),
            result=self.result,
            evaluated_at=self.evaluated_at,
            actor=self.actor,
            trigger=self.trigger,
        )


class FMEARevision(StableModel):
    fmea = models.ForeignKey(FMEA, related_name="revisions", on_delete=models.CASCADE)
    revision_number = models.PositiveIntegerField()
    lifecycle_from = models.CharField(max_length=32, choices=FMEA.LIFECYCLE_CHOICES)
    lifecycle_to = models.CharField(max_length=32, choices=FMEA.LIFECYCLE_CHOICES)
    reason = models.TextField()
    actor = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("fmea", "revision_number")]
        ordering = ["revision_number"]

    def __str__(self) -> str:
        return f"{self.fmea} revision {self.revision_number}"

    def to_domain(self) -> DomainFMEARevision:
        return DomainFMEARevision(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            fmea_id=self.fmea.stable_id,
            revision_number=self.revision_number,
            lifecycle_from=FMEALifecycle(self.lifecycle_from),
            lifecycle_to=FMEALifecycle(self.lifecycle_to),
            reason=self.reason,
            actor=self.actor,
            created_at=self.created_at,
        )


class DomainRelationship(StableModel):
    source_stable_id = models.CharField(max_length=128, db_index=True)
    target_stable_id = models.CharField(max_length=128, db_index=True)
    relationship_type = models.CharField(max_length=128)
    provenance = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["source_stable_id", "relationship_type"]),
            models.Index(fields=["target_stable_id", "relationship_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.source_stable_id} -> {self.target_stable_id}"

    def to_domain(self) -> DomainRelationshipEntity:
        return DomainRelationshipEntity(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            source_id=self.source_stable_id,
            target_id=self.target_stable_id,
            relationship_type=self.relationship_type,
            provenance=self.provenance,
        )

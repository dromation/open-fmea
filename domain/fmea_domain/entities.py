"""Portable Open-FMEA domain entities.

This module intentionally has no Django imports. These objects are the semantic
model used by Django, import/export, tests, and future integration adapters.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Literal

from .identifiers import new_stable_id, require_stable_id


class FMEALifecycle(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    OBSOLETE = "obsolete"


class ActionStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class CauseInfluenceStatus(str, Enum):
    SUSPECTED = "suspected"
    POSSIBLE = "possible"
    CORRELATED = "correlated"
    EXPERIMENTALLY_SUPPORTED = "experimentally_supported"
    CONFIRMED_ROOT_CAUSE = "confirmed_root_cause"
    REJECTED = "rejected"


class TestType(str, Enum):
    VALIDATION = "validation"
    VERIFICATION = "verification"
    RELIABILITY = "reliability"
    ACCEPTANCE = "acceptance"


class ValidationResultStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LifecycleGate(str, Enum):
    CONCEPT_DESIGN = "concept_design"
    DESIGN_VERIFICATION = "design_verification"
    PROCESS_VALIDATION = "process_validation"
    PRE_PRODUCTION = "pre_production"
    SERIAL_PRODUCTION = "serial_production"
    CURRENT = "current"


class ValidationTestStatus(str, Enum):
    PLANNED = "planned"
    IN_EXECUTION = "in_execution"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


@dataclass(frozen=True, kw_only=True)
class DomainEntity:
    stable_id: str = field(default_factory=new_stable_id)
    schema_version: str = "1.0"
    revision: int = 1

    def __post_init__(self) -> None:
        require_stable_id(self.stable_id)
        if self.revision < 1:
            raise ValueError("revision must be >= 1")

    def next_revision(self) -> "DomainEntity":
        return replace(self, revision=self.revision + 1)


@dataclass(frozen=True, kw_only=True)
class NamedEntity(DomainEntity):
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name.strip():
            raise ValueError("name is required")


@dataclass(frozen=True, kw_only=True)
class FMEAProject(NamedEntity):
    pass


@dataclass(frozen=True, kw_only=True)
class FMEA(NamedEntity):
    fmea_type: str = "process"
    scope: str = ""
    lifecycle: FMEALifecycle = FMEALifecycle.DRAFT
    project_id: str | None = None
    team: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class Product(NamedEntity):
    part_number: str = ""


@dataclass(frozen=True, kw_only=True)
class Process(NamedEntity):
    process_code: str = ""


@dataclass(frozen=True, kw_only=True)
class Operation(NamedEntity):
    process_id: str
    sequence: str = ""


@dataclass(frozen=True, kw_only=True)
class Function(NamedEntity):
    product_id: str | None = None
    operation_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class Requirement(NamedEntity):
    function_id: str
    source_reference: str = ""


@dataclass(frozen=True, kw_only=True)
class ProductCharacteristic(NamedEntity):
    requirement_id: str | None = None
    is_special: bool = False
    primary_classification_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class ProcessCharacteristic(NamedEntity):
    operation_id: str
    cause_category_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        require_stable_id(self.operation_id)
        if self.cause_category_id is not None:
            require_stable_id(self.cause_category_id)
        if not isinstance(self.attributes, dict):
            raise ValueError("attributes must be a dict")


@dataclass(frozen=True, kw_only=True)
class FailureMode(NamedEntity):
    fmea_id: str
    function_id: str | None = None
    requirement_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class FailureEffect(NamedEntity):
    failure_mode_id: str


@dataclass(frozen=True, kw_only=True)
class FailureCause(NamedEntity):
    failure_mode_id: str


@dataclass(frozen=True, kw_only=True)
class FailureMechanism(NamedEntity):
    failure_cause_id: str


@dataclass(frozen=True, kw_only=True)
class PreventionControl(NamedEntity):
    failure_cause_id: str
    control_type: str = "prevention"


@dataclass(frozen=True, kw_only=True)
class DetectionControl(NamedEntity):
    failure_cause_id: str
    control_type: str = "detection"


@dataclass(frozen=True, kw_only=True)
class MeasurementMethod(NamedEntity):
    detection_control_id: str
    unit: str = ""


@dataclass(frozen=True, kw_only=True)
class ResponsibleRole(NamedEntity):
    pass


@dataclass(frozen=True, kw_only=True)
class RecommendedAction(NamedEntity):
    failure_mode_id: str | None = None
    failure_cause_id: str | None = None
    responsible_role_id: str | None = None
    status: ActionStatus = ActionStatus.OPEN
    due_date: date | None = None


@dataclass(frozen=True, kw_only=True)
class ValidationTest(NamedEntity):
    failure_mode_id: str
    test_type: TestType
    lifecycle_gate: LifecycleGate
    recommended_action_id: str | None = None
    method: str = ""
    objective: str = ""
    nominal_target: str = ""
    acceptance_criteria: str = ""
    result_status: ValidationResultStatus = ValidationResultStatus.PENDING
    planned_date: date | None = None
    executed_date: date | None = None
    priority: Priority = Priority.MEDIUM
    owner_id: str | None = None
    status: ValidationTestStatus = ValidationTestStatus.PLANNED


@dataclass(frozen=True, kw_only=True)
class Evidence(NamedEntity):
    action_id: str
    reference_uri: str = ""


@dataclass(frozen=True, kw_only=True)
class EffectivenessVerification(NamedEntity):
    action_id: str
    result: str = ""
    verified_at: datetime | None = None


@dataclass(frozen=True, kw_only=True)
class Relationship(DomainEntity):
    source_id: str
    target_id: str
    relationship_type: str
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        require_stable_id(self.source_id)
        require_stable_id(self.target_id)
        if not self.relationship_type.strip():
            raise ValueError("relationship_type is required")


@dataclass(frozen=True, kw_only=True)
class RiskRating:
    severity: int
    occurrence: int
    detection: int


@dataclass(frozen=True, kw_only=True)
class EvaluationDefinition(DomainEntity):
    method: str
    name: str
    rating_scales: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.method.strip():
            raise ValueError("method is required")
        if not self.name.strip():
            raise ValueError("name is required")


@dataclass(frozen=True, kw_only=True)
class CauseCategoryScheme(DomainEntity):
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name.strip():
            raise ValueError("name is required")


@dataclass(frozen=True, kw_only=True)
class CauseCategory(DomainEntity):
    scheme_id: str
    name: str
    description: str = ""
    sort_order: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        require_stable_id(self.scheme_id)
        if not self.name.strip():
            raise ValueError("name is required")
        if self.sort_order < 0:
            raise ValueError("sort_order must be >= 0")


@dataclass(frozen=True, kw_only=True)
class CauseInfluence(DomainEntity):
    source_id: str
    source_type: Literal["FailureCause", "FailureMechanism", "ProcessCharacteristic"]
    target_id: str
    target_type: Literal["FailureMode", "FailureCause", "ProductCharacteristic"]
    influence_type: str
    status: CauseInfluenceStatus = CauseInfluenceStatus.SUSPECTED
    cause_category_id: str | None = None
    confidence: float | None = None
    strength: str | None = None
    evidence_ids: tuple[str, ...] = ()
    source_context: str = "FMEA"
    review_note: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        require_stable_id(self.source_id)
        require_stable_id(self.target_id)
        if self.source_type not in {
            "FailureCause",
            "FailureMechanism",
            "ProcessCharacteristic",
        }:
            raise ValueError(
                "source_type must be FailureCause, FailureMechanism, or ProcessCharacteristic"
            )
        if self.target_type not in {"FailureMode", "FailureCause", "ProductCharacteristic"}:
            raise ValueError(
                "target_type must be FailureMode, FailureCause, or ProductCharacteristic"
            )
        if not self.influence_type.strip():
            raise ValueError("influence_type is required")
        if not isinstance(self.status, CauseInfluenceStatus):
            object.__setattr__(self, "status", CauseInfluenceStatus(self.status))
        if (
            self.status == CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE
            and self.target_type != "FailureCause"
        ):
            raise ValueError("confirmed_root_cause status requires target_type FailureCause")
        if self.cause_category_id is not None:
            require_stable_id(self.cause_category_id)
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        for evidence_id in self.evidence_ids:
            require_stable_id(evidence_id)
        if not self.source_context.strip():
            raise ValueError("source_context is required")


@dataclass(frozen=True, kw_only=True)
class RiskEvaluation(DomainEntity):
    failure_mode_id: str
    evaluation_definition_id: str
    method: str
    inputs: RiskRating
    result: dict[str, Any]
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str = "system"
    trigger: str = "manual"

    def __post_init__(self) -> None:
        super().__post_init__()
        require_stable_id(self.failure_mode_id)
        require_stable_id(self.evaluation_definition_id)
        if not self.method.strip():
            raise ValueError("method is required")


@dataclass(frozen=True, kw_only=True)
class FMEARevision(DomainEntity):
    fmea_id: str
    revision_number: int
    lifecycle_from: FMEALifecycle
    lifecycle_to: FMEALifecycle
    reason: str
    actor: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        super().__post_init__()
        require_stable_id(self.fmea_id)
        if self.revision_number < 1:
            raise ValueError("revision_number must be >= 1")
        if not self.reason.strip():
            raise ValueError("reason is required")
        if not self.actor.strip():
            raise ValueError("actor is required")


@dataclass(frozen=True, kw_only=True)
class FMEADocument(DomainEntity):
    fmea: FMEA
    entities: tuple[DomainEntity, ...] = ()
    relationships: tuple[Relationship, ...] = ()
    evaluations: tuple[RiskEvaluation, ...] = ()
    revisions: tuple[FMEARevision, ...] = ()

    def all_stable_ids(self) -> set[str]:
        ids = {self.stable_id, self.fmea.stable_id}
        ids.update(entity.stable_id for entity in self.entities)
        ids.update(relationship.stable_id for relationship in self.relationships)
        ids.update(evaluation.stable_id for evaluation in self.evaluations)
        ids.update(revision.stable_id for revision in self.revisions)
        return ids

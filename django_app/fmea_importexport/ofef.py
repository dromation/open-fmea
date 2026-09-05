"""Open-FMEA Exchange Format (OFEF) JSON support."""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

from fmea_domain import (
    ActionStatus,
    CauseCategory,
    CauseCategoryScheme,
    CauseInfluence,
    CauseInfluenceStatus,
    DetectionControl,
    DomainEntity,
    EffectivenessVerification,
    EvaluationDefinition,
    Evidence,
    FMEA,
    FMEADocument,
    FMEALifecycle,
    FMEAProject,
    FMEARevision,
    FailureCause,
    FailureEffect,
    FailureMechanism,
    FailureMode,
    Function,
    MeasurementMethod,
    Operation,
    PreventionControl,
    Process,
    ProcessCharacteristic,
    Product,
    ProductCharacteristic,
    RecommendedAction,
    Relationship,
    Requirement,
    ResponsibleRole,
    RiskEvaluation,
    RiskRating,
)


OFEF_FORMAT = "open-fmea-exchange"
OFEF_SCHEMA_VERSION = "1.0"


_ENTITY_TYPES: dict[str, type[DomainEntity]] = {
    cls.__name__: cls
    for cls in (
        CauseCategory,
        CauseCategoryScheme,
        CauseInfluence,
        DetectionControl,
        EffectivenessVerification,
        EvaluationDefinition,
        Evidence,
        FMEAProject,
        FailureCause,
        FailureEffect,
        FailureMechanism,
        FailureMode,
        Function,
        MeasurementMethod,
        Operation,
        PreventionControl,
        Process,
        ProcessCharacteristic,
        Product,
        ProductCharacteristic,
        RecommendedAction,
        Requirement,
        ResponsibleRole,
    )
}


def export_document(document: FMEADocument) -> dict[str, Any]:
    return {
        "format": OFEF_FORMAT,
        "schema_version": OFEF_SCHEMA_VERSION,
        "document": {
            "type": document.__class__.__name__,
            "stable_id": document.stable_id,
            "schema_version": document.schema_version,
            "revision": document.revision,
        },
        "fmea": _serialize_entity(document.fmea),
        "entities": [_serialize_entity(entity) for entity in document.entities],
        "relationships": [
            _serialize_entity(relationship) for relationship in document.relationships
        ],
        "evaluations": [
            _serialize_entity(evaluation) for evaluation in document.evaluations
        ],
        "revisions": [_serialize_entity(revision) for revision in document.revisions],
    }


def to_json(document: FMEADocument) -> str:
    return json.dumps(export_document(document), indent=2, sort_keys=True)


def import_document(payload: dict[str, Any]) -> FMEADocument:
    if payload.get("format") != OFEF_FORMAT:
        raise ValueError("Not an Open-FMEA Exchange Format document")
    if payload.get("schema_version") != OFEF_SCHEMA_VERSION:
        raise ValueError(f"Unsupported OFEF schema version: {payload.get('schema_version')}")

    document_data = _entity_payload(payload["document"])
    return FMEADocument(
        stable_id=document_data["stable_id"],
        schema_version=document_data.get("schema_version", OFEF_SCHEMA_VERSION),
        revision=document_data.get("revision", 1),
        fmea=_deserialize_fmea(payload["fmea"]),
        entities=tuple(_deserialize_entity(item) for item in payload.get("entities", [])),
        relationships=tuple(
            _deserialize_relationship(item) for item in payload.get("relationships", [])
        ),
        evaluations=tuple(
            _deserialize_evaluation(item) for item in payload.get("evaluations", [])
        ),
        revisions=tuple(
            _deserialize_revision(item) for item in payload.get("revisions", [])
        ),
    )


def _serialize_entity(entity: Any) -> dict[str, Any]:
    if not is_dataclass(entity):
        raise TypeError(f"Cannot serialize non-dataclass entity: {type(entity)!r}")
    data = _serialize_value(asdict(entity))
    data["type"] = entity.__class__.__name__
    return data


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_serialize_value(item) for item in value]
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    return value


def _entity_payload(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    data.pop("type", None)
    return data


def _deserialize_fmea(payload: dict[str, Any]) -> FMEA:
    data = _entity_payload(payload)
    data["lifecycle"] = FMEALifecycle(data["lifecycle"])
    data["team"] = tuple(data.get("team", ()))
    return FMEA(**data)


def _deserialize_entity(payload: dict[str, Any]) -> DomainEntity:
    entity_type = payload.get("type")
    cls = _ENTITY_TYPES.get(entity_type)
    if cls is None:
        raise ValueError(f"Unsupported OFEF entity type: {entity_type}")
    data = _entity_payload(payload)
    if cls is RecommendedAction and data.get("status"):
        data["status"] = ActionStatus(data["status"])
    if cls is CauseInfluence:
        data["status"] = CauseInfluenceStatus(data["status"])
        data["evidence_ids"] = tuple(data.get("evidence_ids", ()))
    if cls is EffectivenessVerification and data.get("verified_at"):
        data["verified_at"] = datetime.fromisoformat(data["verified_at"])
    return cls(**data)


def _deserialize_relationship(payload: dict[str, Any]) -> Relationship:
    return Relationship(**_entity_payload(payload))


def _deserialize_evaluation(payload: dict[str, Any]) -> RiskEvaluation:
    data = _entity_payload(payload)
    data["inputs"] = RiskRating(**data["inputs"])
    data["evaluated_at"] = datetime.fromisoformat(data["evaluated_at"])
    return RiskEvaluation(**data)


def _deserialize_revision(payload: dict[str, Any]) -> FMEARevision:
    data = _entity_payload(payload)
    data["lifecycle_from"] = FMEALifecycle(data["lifecycle_from"])
    data["lifecycle_to"] = FMEALifecycle(data["lifecycle_to"])
    data["created_at"] = datetime.fromisoformat(data["created_at"])
    return FMEARevision(**data)

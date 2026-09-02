"""Map parsed cells into Open-FMEA import candidates without touching Django."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from fmea_ai.contracts import AiProvider, AiTaskRequest
from fmea_ai.validation import validate_structured_output

from ..candidates import ImportCandidate, SourceProvenance, UNMAPPED_DOMAIN_TYPE
from .column_mapping import map_header


STRUCTURED_EXTRACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "extracted_value": {"type": "string", "minLength": 1},
        "suggested_domain_type": {
            "type": "string",
            "enum": [
                "Function",
                "Requirement",
                "ProductCharacteristic",
                "ProcessCharacteristic",
                "FailureMode",
                "FailureEffect",
                "FailureCause",
                "PreventionControl",
                "DetectionControl",
                "unmapped",
            ],
        },
        "parsing_confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "ai_confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "relationship_suggestions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["extracted_value", "suggested_domain_type"],
    "additionalProperties": False,
}


def build_candidate(
    *,
    stable_id: str,
    extracted_value: str,
    column_header: str,
    provenance: SourceProvenance,
) -> ImportCandidate:
    mapping = map_header(column_header)
    validation_issues: tuple[str, ...] = ()
    suggested_domain_type = UNMAPPED_DOMAIN_TYPE
    parsing_confidence = 1.0
    if mapping is None:
        validation_issues = (f"Unmapped column header: {column_header}",)
        parsing_confidence = 0.0
    else:
        suggested_domain_type = mapping.suggested_domain_type

    return ImportCandidate(
        stable_id=stable_id,
        extracted_value=extracted_value,
        suggested_domain_type=suggested_domain_type,
        provenance=provenance,
        parsing_confidence=parsing_confidence,
        validation_issues=validation_issues,
    )


def enrich_candidate_with_ai(
    candidate: ImportCandidate,
    provider: AiProvider | None,
    *,
    enabled: bool,
) -> ImportCandidate:
    if not enabled or provider is None:
        return candidate

    request = AiTaskRequest(
        task="extract_structured_data",
        input_text=candidate.extracted_value,
        context={
            "column_name": candidate.provenance.column_name,
            "deterministic_type": candidate.suggested_domain_type,
        },
        output_schema=STRUCTURED_EXTRACTION_SCHEMA,
    )
    response = provider.extract_structured_data(request)
    if response.status != "ok" or response.structured_output is None:
        return candidate

    valid, _issues = validate_structured_output(response.structured_output, STRUCTURED_EXTRACTION_SCHEMA)
    if not valid:
        return candidate

    output = response.structured_output
    extracted_value = str(output.get("extracted_value") or candidate.extracted_value).strip()
    suggested_domain_type = str(output.get("suggested_domain_type") or candidate.suggested_domain_type)
    if not extracted_value:
        return candidate
    if suggested_domain_type == "unmapped" and not candidate.validation_issues:
        return candidate

    try:
        return replace(
            candidate,
            extracted_value=extracted_value,
            suggested_domain_type=suggested_domain_type,
            ai_confidence=output.get("ai_confidence", response.model_confidence),
            relationship_suggestions=tuple(output.get("relationship_suggestions") or ()),
        )
    except ValueError:
        return candidate

"""Configurable XLSX header mapping for the first Open-FMEA ingestion slice."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class HeaderMapping:
    field_name: str
    suggested_domain_type: str


DEFAULT_HEADER_MAPPINGS: dict[str, HeaderMapping] = {
    "function": HeaderMapping("function", "Function"),
    "product function": HeaderMapping("function", "Function"),
    "process function": HeaderMapping("function", "Function"),
    "item function": HeaderMapping("function", "Function"),
    "process product function requirment": HeaderMapping("function", "Function"),
    "process product function requirement": HeaderMapping("function", "Function"),
    "design part product requirment": HeaderMapping("function", "Function"),
    "design part product requirement": HeaderMapping("function", "Function"),
    "process function task tool requirment": HeaderMapping("function", "Function"),
    "process function task tool requirement": HeaderMapping("function", "Function"),
    "process function requirment": HeaderMapping("function", "Function"),
    "process function requirement": HeaderMapping("function", "Function"),
    "system architecture execution function requirment": HeaderMapping("function", "Function"),
    "system architecture execution function requirement": HeaderMapping("function", "Function"),
    "software architecture algorithm code function requirment": HeaderMapping("function", "Function"),
    "software architecture algorithm code function requirement": HeaderMapping("function", "Function"),
    "operation function requirment": HeaderMapping("function", "Function"),
    "operation function requirement": HeaderMapping("function", "Function"),
    "function part operation": HeaderMapping("function", "Function"),
    "requirement": HeaderMapping("requirement", "Requirement"),
    "requirements": HeaderMapping("requirement", "Requirement"),
    "specification": HeaderMapping("requirement", "Requirement"),
    "requirement specification": HeaderMapping("requirement", "Requirement"),
    "product characteristics id description": HeaderMapping(
        "product_characteristic",
        "ProductCharacteristic",
    ),
    "characteristics": HeaderMapping("product_characteristic", "ProductCharacteristic"),
    "potential failure mode": HeaderMapping("failure_mode", "FailureMode"),
    "failure mode": HeaderMapping("failure_mode", "FailureMode"),
    "failure": HeaderMapping("failure_mode", "FailureMode"),
    "potential effect": HeaderMapping("failure_effect", "FailureEffect"),
    "potential effects": HeaderMapping("failure_effect", "FailureEffect"),
    "potential effect of failure": HeaderMapping("failure_effect", "FailureEffect"),
    "potential effects of failure": HeaderMapping("failure_effect", "FailureEffect"),
    "effect": HeaderMapping("failure_effect", "FailureEffect"),
    "failure effect": HeaderMapping("failure_effect", "FailureEffect"),
    "effects of failure": HeaderMapping("failure_effect", "FailureEffect"),
    "effects of failure on syst part operation": HeaderMapping("failure_effect", "FailureEffect"),
    "undesirable customer effects": HeaderMapping("failure_effect", "FailureEffect"),
    "undesirable customer effects effects of failure on syst part operation": HeaderMapping("failure_effect", "FailureEffect"),
    "potential cause": HeaderMapping("failure_cause", "FailureCause"),
    "potential causes": HeaderMapping("failure_cause", "FailureCause"),
    "potential cause of failure": HeaderMapping("failure_cause", "FailureCause"),
    "potential causes of failure": HeaderMapping("failure_cause", "FailureCause"),
    "cause": HeaderMapping("failure_cause", "FailureCause"),
    "causes of failure": HeaderMapping("failure_cause", "FailureCause"),
    "failure cause": HeaderMapping("failure_cause", "FailureCause"),
    "prevention control": HeaderMapping("prevention_control", "PreventionControl"),
    "prevention controls": HeaderMapping("prevention_control", "PreventionControl"),
    "current prevention control": HeaderMapping("prevention_control", "PreventionControl"),
    "current prevention controls": HeaderMapping("prevention_control", "PreventionControl"),
    "controls prevention": HeaderMapping("prevention_control", "PreventionControl"),
    "current process controls prevention": HeaderMapping("prevention_control", "PreventionControl"),
    "current design controls prevention": HeaderMapping("prevention_control", "PreventionControl"),
    "detection control": HeaderMapping("detection_control", "DetectionControl"),
    "detection controls": HeaderMapping("detection_control", "DetectionControl"),
    "current detection control": HeaderMapping("detection_control", "DetectionControl"),
    "current detection controls": HeaderMapping("detection_control", "DetectionControl"),
    "controls detection": HeaderMapping("detection_control", "DetectionControl"),
    "current process controls detection": HeaderMapping("detection_control", "DetectionControl"),
    "current design controls detection": HeaderMapping("detection_control", "DetectionControl"),
    "testing simulation": HeaderMapping("detection_control", "DetectionControl"),
}


def normalize_header(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[\r\n\t_/\\-]+", " ", text)
    text = re.sub(r"[^a-z0-9+ ]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def map_header(
    header: object,
    custom_mappings: Mapping[str, HeaderMapping | tuple[str, str]] | None = None,
) -> HeaderMapping | None:
    mappings = dict(DEFAULT_HEADER_MAPPINGS)
    if custom_mappings:
        for key, value in custom_mappings.items():
            mappings[normalize_header(key)] = (
                value
                if isinstance(value, HeaderMapping)
                else HeaderMapping(field_name=value[0], suggested_domain_type=value[1])
            )
    return mappings.get(normalize_header(header))

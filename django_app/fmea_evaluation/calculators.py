"""Pluggable risk evaluation calculators.

The Action Priority implementation is a PoC variant. The rule table is explicit
and replaceable so a licensed organization-specific matrix can be substituted
without changing persistence or export shape.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fmea_domain import RiskRating, validate_rating


CLASSIC_RPN_METHOD = "classic-rpn"
ACTION_PRIORITY_POC_METHOD = "aiag-vda-ap-poc"


@dataclass(frozen=True)
class EvaluationResult:
    method: str
    inputs: RiskRating
    output: dict[str, Any]


def calculate_classic_rpn(rating: RiskRating) -> EvaluationResult:
    validate_rating(rating)
    rpn = rating.severity * rating.occurrence * rating.detection
    return EvaluationResult(
        method=CLASSIC_RPN_METHOD,
        inputs=rating,
        output={
            "score": rpn,
            "classification": classify_rpn(rpn),
        },
    )


def classify_rpn(rpn: int) -> str:
    if rpn >= 200:
        return "high"
    if rpn >= 80:
        return "medium"
    return "low"


def classify_severity_occurrence(severity: int, occurrence: int) -> str:
    """Bands a (severity, occurrence) pair on the same 1-10 scale RiskRating
    already validates to. Independent of any RiskEvaluation method - this is
    a grid-coloring band, not a replacement for classify_rpn or the AP bands."""
    product = severity * occurrence
    if product <= 8:
        return "low"
    if product <= 24:
        return "medium"
    if product <= 48:
        return "high"
    return "very_high"


def calculate_action_priority(rating: RiskRating) -> EvaluationResult:
    validate_rating(rating)
    priority = _action_priority_band(rating)
    return EvaluationResult(
        method=ACTION_PRIORITY_POC_METHOD,
        inputs=rating,
        output={
            "priority": priority,
            "variant": "configurable-poc-matrix",
        },
    )


def calculate(method: str, rating: RiskRating) -> EvaluationResult:
    if method == CLASSIC_RPN_METHOD:
        return calculate_classic_rpn(rating)
    if method == ACTION_PRIORITY_POC_METHOD:
        return calculate_action_priority(rating)
    raise ValueError(f"Unknown evaluation method: {method}")


def _action_priority_band(rating: RiskRating) -> str:
    s = rating.severity
    o = rating.occurrence
    d = rating.detection

    if s >= 9 and (o >= 4 or d >= 7):
        return "high"
    if s >= 7 and o >= 6 and d >= 4:
        return "high"
    if s >= 5 and o >= 8 and d >= 7:
        return "high"

    if s >= 9:
        return "medium"
    if s >= 7 and (o >= 4 or d >= 6):
        return "medium"
    if s >= 5 and (o >= 6 or d >= 8):
        return "medium"
    if s >= 4 and o >= 8:
        return "medium"

    return "low"

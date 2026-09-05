"""Risk matrix query logic.

Cell placement is always severity x occurrence (1-10 each); detection is
never a grid axis. For a selected evaluation `method`, only FailureModes with
at least one RiskEvaluation under that specific method are considered, using
each FailureMode's most recent evaluation under that method.

Scores and bands returned here are read from the stored RiskEvaluation.result
instead of being recomputed during display.
"""
from __future__ import annotations

from fmea_evaluation import (
    ACTION_PRIORITY_POC_METHOD,
    CLASSIC_RPN_METHOD,
    classify_severity_occurrence,
)

from . import models

KNOWN_METHODS = (CLASSIC_RPN_METHOD, ACTION_PRIORITY_POC_METHOD)

METHOD_LABELS = {
    CLASSIC_RPN_METHOD: "Classic RPN",
    ACTION_PRIORITY_POC_METHOD: "AIAG-VDA Action Priority (PoC)",
}

# aiag-vda-ap-poc's calculator output (fmea_evaluation.calculators.
# calculate_action_priority) has no numeric score, only a "priority" band -
# unlike classic-rpn's result["score"]. Sorting "Top High Risk Items" for
# that method falls back to band severity order instead of a score. This is
# a real asymmetry between the two methods' output shape, not an oversight.
_AP_BAND_ORDER = {"high": 2, "medium": 1, "low": 0}


def normalize_method(method: str | None) -> str:
    """Falls back to classic-rpn for a missing/unrecognized value - this is a
    display filter, not a form submission with a contract to enforce
    strictly."""
    if method in KNOWN_METHODS:
        return method
    return CLASSIC_RPN_METHOD


def latest_evaluations_by_method(method: str) -> dict[str, models.RiskEvaluation]:
    """Each FailureMode's most recent RiskEvaluation under `method`, keyed by
    FailureMode stable_id. A FailureMode with no evaluation under this
    method is simply absent from the returned mapping.

    A single query ordered by (failure_mode_id, -evaluated_at, -id) groups
    each FailureMode's evaluations together with the most recent one first
    within its group, so keeping only the first row seen per failure_mode_id
    yields the "most recent per FailureMode" set without a window function.
    """
    latest: dict[str, models.RiskEvaluation] = {}
    evaluations = (
        models.RiskEvaluation.objects.filter(method=method)
        .select_related("failure_mode", "failure_mode__fmea")
        .order_by("failure_mode_id", "-evaluated_at", "-id")
    )
    for evaluation in evaluations:
        key = evaluation.failure_mode.stable_id
        if key not in latest:
            latest[key] = evaluation
    return latest


def grid_rows(method: str) -> list[list[dict]]:
    """A 10x10 grid as rows of cell dicts. Rows run occurrence 10 down to 1
    (top row = highest occurrence), columns run severity 1 to 10 - an axis
    order convention chosen to match the common AIAG severity/occurrence
    matrix orientation."""
    counts: dict[tuple[int, int], int] = {}
    for evaluation in latest_evaluations_by_method(method).values():
        key = (evaluation.severity, evaluation.occurrence)
        counts[key] = counts.get(key, 0) + 1

    rows: list[list[dict]] = []
    for occurrence in range(10, 0, -1):
        row = []
        for severity in range(1, 11):
            row.append(
                {
                    "severity": severity,
                    "occurrence": occurrence,
                    "count": counts.get((severity, occurrence), 0),
                    "band": classify_severity_occurrence(severity, occurrence),
                }
            )
        rows.append(row)
    return rows


def unevaluated_failure_mode_count(method: str) -> int:
    """FailureModes with no RiskEvaluation under `method` at all."""
    evaluated_ids = set(latest_evaluations_by_method(method).keys())
    return models.FailureMode.objects.exclude(stable_id__in=evaluated_ids).count()


def high_risk_failure_mode_count(method: str = CLASSIC_RPN_METHOD) -> int:
    """FailureModes whose most recent evaluation under `method` falls in the
    high or very_high severity x occurrence band, computed the same way as
    grid_rows."""
    return sum(
        1
        for evaluation in latest_evaluations_by_method(method).values()
        if classify_severity_occurrence(evaluation.severity, evaluation.occurrence)
        in ("high", "very_high")
    )


def cell_evaluations(method: str, severity: int, occurrence: int) -> list[models.RiskEvaluation]:
    """FailureModes' most-recent-under-`method` evaluations placed in this
    exact (severity, occurrence) cell, for the drill-down view."""
    matches = [
        evaluation
        for evaluation in latest_evaluations_by_method(method).values()
        if evaluation.severity == severity and evaluation.occurrence == occurrence
    ]
    matches.sort(key=lambda evaluation: evaluation.failure_mode.name)
    return matches


def top_evaluations(method: str, limit: int = 25) -> list[models.RiskEvaluation]:
    """Every FailureMode with an evaluation under `method`, sorted by
    computed score descending (classic-rpn: result["score"]; aiag-vda-ap-poc:
    band severity order, see _AP_BAND_ORDER)."""
    evaluations = list(latest_evaluations_by_method(method).values())
    if method == CLASSIC_RPN_METHOD:
        evaluations.sort(key=lambda evaluation: evaluation.result.get("score", 0), reverse=True)
    else:
        evaluations.sort(
            key=lambda evaluation: _AP_BAND_ORDER.get(evaluation.result.get("priority"), -1),
            reverse=True,
        )
    return evaluations[:limit] if limit else evaluations

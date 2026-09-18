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
AIAG_VDA_AP_METHOD = "aiag-vda-ap"
AIAG_VDA_MSR_METHOD = "aiag-vda-msr"


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
    if method == AIAG_VDA_AP_METHOD:
        return calculate_action_priority_aiag_vda(rating)
    if method == AIAG_VDA_MSR_METHOD:
        return calculate_action_priority_msr(rating)
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


# ---------------------------------------------------------------------------
# Real AIAG & VDA Table AP (Action Priority) - Handbook, 1st Ed. 2019.
#
# This is the actual 69-row Severity-band x Occurrence-band x Detection-band
# lookup table transcribed from Appendix C of the handbook, not an invented
# threshold approximation like `_action_priority_band` above. The table is
# confirmed cell-for-cell identical between DFMEA and PFMEA (only the S/O/D
# *criteria wording* differs between the two - see EvaluationDefinition
# "aiag-vda-ap"'s rating_scales, which stores both wordings), so this single
# calculator serves both FMEA types; no separate DFMEA/PFMEA method or table
# is needed.
# ---------------------------------------------------------------------------

# Row/column order: [S-band][O-band] -> (AP for D-band 7-10, 5-6, 2-4, 1)
# S-bands (rows):      9-10, 7-8, 4-6, 2-3   (S=1 is handled separately: always "low")
# O-bands (columns):   8-10, 6-7, 4-5, 2-3   (O=1 is handled separately: always "low")
# D-bands (tuple):     7-10 (low-very low ability to detect), 5-6 (moderate), 2-4 (high), 1 (very high)
_AIAG_VDA_AP_TABLE: tuple[tuple[tuple[str, str, str, str], ...], ...] = (
    (  # S = 9-10
        ("high", "high", "high", "high"),      # O = 8-10
        ("high", "high", "high", "high"),      # O = 6-7
        ("high", "high", "high", "medium"),    # O = 4-5
        ("high", "medium", "low", "low"),      # O = 2-3
    ),
    (  # S = 7-8
        ("high", "high", "high", "high"),      # O = 8-10
        ("high", "high", "high", "medium"),    # O = 6-7
        ("high", "medium", "medium", "medium"),  # O = 4-5
        ("medium", "medium", "low", "low"),    # O = 2-3
    ),
    (  # S = 4-6
        ("high", "high", "medium", "medium"),  # O = 8-10
        ("medium", "medium", "medium", "low"),  # O = 6-7
        ("medium", "low", "low", "low"),       # O = 4-5
        ("low", "low", "low", "low"),          # O = 2-3
    ),
    (  # S = 2-3
        ("medium", "medium", "low", "low"),    # O = 8-10
        ("low", "low", "low", "low"),          # O = 6-7
        ("low", "low", "low", "low"),          # O = 4-5
        ("low", "low", "low", "low"),          # O = 2-3
    ),
)


def _aiag_vda_severity_band(severity: int) -> int | None:
    """Index into _AIAG_VDA_AP_TABLE's rows, or None for S=1 (handled as a
    standalone always-"low" case, not part of the 4x4 grid)."""
    if severity >= 9:
        return 0
    if severity >= 7:
        return 1
    if severity >= 4:
        return 2
    if severity >= 2:
        return 3
    return None  # severity == 1


def _aiag_vda_occurrence_band(occurrence: int) -> int | None:
    """Index into a table row, or None for O=1 (always "low" regardless of
    S/D, per the handbook table)."""
    if occurrence >= 8:
        return 0
    if occurrence >= 6:
        return 1
    if occurrence >= 4:
        return 2
    if occurrence >= 2:
        return 3
    return None  # occurrence == 1


def _aiag_vda_detection_band(detection: int) -> int:
    """Index into a table row's 4-tuple (D=7-10, D=5-6, D=2-4, D=1)."""
    if detection >= 7:
        return 0
    if detection >= 5:
        return 1
    if detection >= 2:
        return 2
    return 3  # detection == 1


def _action_priority_band_aiag_vda(rating: RiskRating) -> str:
    """The real Table AP lookup: Severity-band -> Occurrence-band ->
    Detection-band -> High/Medium/Low. See _AIAG_VDA_AP_TABLE above."""
    s_band = _aiag_vda_severity_band(rating.severity)
    if s_band is None:
        return "low"  # S = 1: any O, any D -> Low
    o_band = _aiag_vda_occurrence_band(rating.occurrence)
    if o_band is None:
        return "low"  # O = 1: any D -> Low
    d_band = _aiag_vda_detection_band(rating.detection)
    return _AIAG_VDA_AP_TABLE[s_band][o_band][d_band]


def calculate_action_priority_aiag_vda(rating: RiskRating) -> EvaluationResult:
    """The real AIAG & VDA Table AP - not a PoC approximation. See
    calculate_action_priority() above for the pre-existing PoC variant, which
    this leaves untouched."""
    validate_rating(rating)
    priority = _action_priority_band_aiag_vda(rating)
    return EvaluationResult(
        method=AIAG_VDA_AP_METHOD,
        inputs=rating,
        output={
            "priority": priority,
            "variant": "aiag-vda-handbook-table-ap",
        },
    )


# ---------------------------------------------------------------------------
# Real AIAG & VDA FMEA-MSR (Supplemental FMEA for Monitoring and System
# Response) Table AP - Handbook, 1st Ed. 2019, Chapter 4, pp. 146-148.
#
# FMEA-MSR reuses RiskRating's three integer slots with different meanings:
#   - severity  -> Severity (S), same scale/meaning as DFMEA.
#   - occurrence -> Frequency (F), NOT Occurrence. Replaces Occurrence in
#     FMEA-MSR - a measure of how often the Failure Cause occurs in relevant
#     operating situations, not "product experience/prevention controls".
#   - detection -> Monitoring (M), NOT Detection. Replaces Detection in
#     FMEA-MSR - the combined ability of diagnostic monitoring and system
#     response/human reaction to reach a safe state before a hazard occurs.
#
# This table's own shape (per the handbook) is organized as uneven
# Frequency-band x Monitoring-band rectangles within each Severity band,
# not a clean 4x4 grid like the DFMEA/PFMEA Table AP - so it is encoded as
# an explicit list of (f_range, m_range) -> priority rules per Severity
# band, each band's rules verified to exactly partition the full 10x10
# Frequency x Monitoring space with no gaps or overlaps.
#
# NOT implemented in this first increment (explicitly out of scope per the
# architecture decision): Handbook NOTE 1/NOTE 2 (when Monitoring=1, the
# *mitigated* Failure Effect's severity replaces the original Failure
# Effect's severity for this AP lookup, and for the parent DFMEA's own AP
# lookup too). RiskRating carries a single severity value with no
# "original vs. mitigated" distinction, so this substitution rule cannot be
# applied without a model change beyond this increment's one new field
# (RiskEvaluation.failure_scenario). Until that is built, callers are
# responsible for passing whichever severity they intend this lookup to use.
# ---------------------------------------------------------------------------

_AIAG_VDA_MSR_AP_RULES: dict[int, tuple[tuple[tuple[int, int], tuple[int, int], str], ...]] = {
    10: (
        ((5, 10), (1, 10), "high"),
        ((4, 4), (4, 10), "high"),
        ((4, 4), (2, 3), "high"),
        ((4, 4), (1, 1), "medium"),
        ((3, 3), (4, 10), "high"),
        ((3, 3), (2, 3), "medium"),
        ((3, 3), (1, 1), "low"),
        ((2, 2), (4, 10), "medium"),
        ((2, 2), (1, 3), "low"),
        ((1, 1), (1, 10), "low"),
    ),
    9: (
        ((4, 10), (1, 10), "high"),
        ((2, 3), (2, 10), "high"),
        ((2, 3), (1, 1), "low"),
        ((1, 1), (1, 10), "low"),
    ),
    8: (
        ((6, 10), (1, 10), "high"),
        ((5, 5), (5, 10), "high"),
        ((5, 5), (1, 4), "medium"),
        ((4, 4), (7, 10), "high"),
        ((4, 4), (4, 6), "medium"),
        ((4, 4), (1, 3), "low"),
        ((3, 3), (9, 10), "high"),
        ((3, 3), (7, 8), "medium"),
        ((3, 3), (1, 6), "low"),
        ((2, 2), (7, 10), "medium"),
        ((2, 2), (1, 6), "low"),
        ((1, 1), (1, 10), "low"),
    ),
    6: (
        ((7, 10), (1, 10), "high"),
        ((5, 6), (6, 10), "high"),
        ((5, 6), (1, 5), "medium"),
        ((2, 4), (9, 10), "medium"),
        ((2, 4), (7, 8), "medium"),
        ((2, 4), (1, 6), "low"),
        ((1, 1), (1, 10), "low"),
    ),
    3: (
        ((7, 10), (1, 10), "high"),
        ((5, 6), (7, 10), "medium"),
        ((5, 6), (1, 6), "low"),
        ((2, 4), (1, 10), "low"),
        ((1, 1), (1, 10), "low"),
    ),
    1: (
        ((1, 10), (1, 10), "low"),
    ),
}
# S=7-8 share the same rule set (verbatim identical bands in the handbook);
# S=4-6 share one rule set; S=2-3 share one rule set. Keyed above by 8, 6,
# and 3 respectively; the other members of each band alias to that key.
_AIAG_VDA_MSR_AP_RULES[7] = _AIAG_VDA_MSR_AP_RULES[8]
_AIAG_VDA_MSR_AP_RULES[4] = _AIAG_VDA_MSR_AP_RULES[6]
_AIAG_VDA_MSR_AP_RULES[5] = _AIAG_VDA_MSR_AP_RULES[6]
_AIAG_VDA_MSR_AP_RULES[2] = _AIAG_VDA_MSR_AP_RULES[3]


def _action_priority_band_msr(rating: RiskRating) -> str:
    """Table AP for FMEA-MSR: Severity -> (Frequency, Monitoring) -> H/M/L.
    `rating.occurrence` is read as Frequency (F); `rating.detection` is read
    as Monitoring (M) - see the module comment above."""
    rules = _AIAG_VDA_MSR_AP_RULES[rating.severity]
    frequency = rating.occurrence
    monitoring = rating.detection
    for (f_min, f_max), (m_min, m_max), priority in rules:
        if f_min <= frequency <= f_max and m_min <= monitoring <= m_max:
            return priority
    raise ValueError(  # pragma: no cover - rules are verified to fully cover 1-10 x 1-10
        f"No FMEA-MSR Table AP rule matched severity={rating.severity} "
        f"frequency={frequency} monitoring={monitoring}"
    )


def calculate_action_priority_msr(rating: RiskRating) -> EvaluationResult:
    """The real AIAG & VDA FMEA-MSR Table AP (Handbook Ch. 4, pp. 146-148).
    `rating.occurrence` holds Frequency (F); `rating.detection` holds
    Monitoring (M) - not Occurrence/Detection. See the module comment above
    for what this increment does not yet implement (the M=1 mitigated-
    severity substitution rule)."""
    validate_rating(rating)
    priority = _action_priority_band_msr(rating)
    return EvaluationResult(
        method=AIAG_VDA_MSR_METHOD,
        inputs=rating,
        output={
            "priority": priority,
            "variant": "aiag-vda-msr-handbook-table-ap",
        },
    )

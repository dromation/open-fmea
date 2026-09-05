"""Framework-free domain rules."""
from __future__ import annotations

from .entities import CauseInfluenceStatus, FMEALifecycle, RiskRating


class DomainValidationError(ValueError):
    """Raised when a domain command would violate Open-FMEA rules."""


class CauseInfluenceTransitionError(Exception):
    """Raised when a CauseInfluence status transition violates a domain rule."""


_ALLOWED_LIFECYCLE_TRANSITIONS: dict[FMEALifecycle, set[FMEALifecycle]] = {
    FMEALifecycle.DRAFT: {FMEALifecycle.IN_REVIEW, FMEALifecycle.OBSOLETE},
    FMEALifecycle.IN_REVIEW: {FMEALifecycle.DRAFT, FMEALifecycle.APPROVED},
    FMEALifecycle.APPROVED: {FMEALifecycle.SUPERSEDED, FMEALifecycle.OBSOLETE},
    FMEALifecycle.SUPERSEDED: {FMEALifecycle.OBSOLETE},
    FMEALifecycle.OBSOLETE: set(),
}

_CAUSE_INFLUENCE_PROGRESS = (
    CauseInfluenceStatus.SUSPECTED,
    CauseInfluenceStatus.POSSIBLE,
    CauseInfluenceStatus.CORRELATED,
    CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED,
    CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE,
)
_CAUSE_INFLUENCE_RANK = {
    status: index for index, status in enumerate(_CAUSE_INFLUENCE_PROGRESS)
}
_CAUSE_INFLUENCE_TERMINAL = {
    CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE,
    CauseInfluenceStatus.REJECTED,
}


def validate_rating(rating: RiskRating) -> RiskRating:
    for name, value in (
        ("severity", rating.severity),
        ("occurrence", rating.occurrence),
        ("detection", rating.detection),
    ):
        if not isinstance(value, int) or not 1 <= value <= 10:
            raise DomainValidationError(f"{name} must be an integer from 1 to 10")
    return rating


def next_revision_number(current_revision: int) -> int:
    if not isinstance(current_revision, int) or current_revision < 1:
        raise DomainValidationError("current_revision must be an integer >= 1")
    return current_revision + 1


def assert_valid_lifecycle_transition(
    current: FMEALifecycle,
    target: FMEALifecycle,
) -> None:
    if target not in _ALLOWED_LIFECYCLE_TRANSITIONS[current]:
        raise DomainValidationError(
            f"Invalid FMEA lifecycle transition: {current.value} -> {target.value}"
        )


def validate_cause_influence_transition(
    *,
    current_status: CauseInfluenceStatus,
    new_status: CauseInfluenceStatus,
    current_target_type: str,
    review_note: str,
    evidence_ids: tuple[str, ...],
    retarget_failure_cause_stable_id: str | None,
) -> None:
    current_status = CauseInfluenceStatus(current_status)
    new_status = CauseInfluenceStatus(new_status)
    note = review_note.strip()
    retarget = (retarget_failure_cause_stable_id or "").strip()

    if current_status == new_status:
        return

    if current_status in _CAUSE_INFLUENCE_TERMINAL:
        raise CauseInfluenceTransitionError(
            f"{current_status.value} is terminal and cannot transition to {new_status.value}"
        )

    if retarget and current_target_type != "FailureMode":
        raise CauseInfluenceTransitionError(
            "failure_cause_stable_id can only retarget an influence currently targeting a FailureMode"
        )

    if new_status == CauseInfluenceStatus.REJECTED:
        if not note:
            raise CauseInfluenceTransitionError("review_note is required when rejecting a cause influence")
        return

    if new_status not in _CAUSE_INFLUENCE_RANK:
        raise CauseInfluenceTransitionError(f"Unsupported CauseInfluence status: {new_status.value}")

    current_rank = _CAUSE_INFLUENCE_RANK[current_status]
    new_rank = _CAUSE_INFLUENCE_RANK[new_status]
    if new_rank < current_rank:
        raise CauseInfluenceTransitionError(
            f"Backward CauseInfluence transition is not allowed: {current_status.value} -> {new_status.value}"
        )

    if new_rank - current_rank > 1 and not note:
        raise CauseInfluenceTransitionError(
            "review_note is required when skipping intermediate CauseInfluence statuses"
        )

    if new_status == CauseInfluenceStatus.CONFIRMED_ROOT_CAUSE:
        if current_target_type == "FailureMode" and not retarget:
            raise CauseInfluenceTransitionError(
                "failure_cause_stable_id is required when confirming a FailureMode-targeted influence"
            )
        if current_target_type not in {"FailureMode", "FailureCause"}:
            raise CauseInfluenceTransitionError(
                "confirmed_root_cause requires target_type FailureCause"
            )
        if not note:
            raise CauseInfluenceTransitionError(
                "review_note is required when confirming a root cause"
            )

    if (
        new_status == CauseInfluenceStatus.EXPERIMENTALLY_SUPPORTED
        and not evidence_ids
        and not note
    ):
        raise CauseInfluenceTransitionError(
            "experimentally_supported requires evidence_ids or a review_note"
        )

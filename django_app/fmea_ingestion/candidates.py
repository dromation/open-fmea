"""Framework-free ingestion contracts for imported Open-FMEA candidates."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Literal

from fmea_domain.identifiers import new_stable_id, require_stable_id


VALID_DOMAIN_TYPES = frozenset(
    {
        "Function",
        "Requirement",
        "ProductCharacteristic",
        "ProcessCharacteristic",
        "FailureMode",
        "FailureEffect",
        "FailureCause",
        "PreventionControl",
        "DetectionControl",
    }
)
UNMAPPED_DOMAIN_TYPE = "unmapped"
VALID_SUGGESTED_TYPES = VALID_DOMAIN_TYPES | {UNMAPPED_DOMAIN_TYPE}


class ReviewStatus(str, Enum):
    UNREVIEWED = "unreviewed"
    ACCEPTED = "accepted"
    MODIFIED = "modified"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
    NEEDS_CLARIFICATION = "needs_clarification"


@dataclass(frozen=True, kw_only=True)
class SourceProvenance:
    source_document_id: str
    document_version: str
    workbook_name: str
    sheet_name: str
    row_number: int
    column_name: str
    extraction_method: Literal["deterministic", "ai"]
    parser_version: str

    def __post_init__(self) -> None:
        if len(self.document_version) != 64 or not all(
            char in "0123456789abcdef" for char in self.document_version.lower()
        ):
            raise ValueError("document_version must be a SHA-256 hex digest")
        if self.row_number < 1:
            raise ValueError("row_number must be >= 1")
        for field_name in (
            "source_document_id",
            "workbook_name",
            "sheet_name",
            "column_name",
            "parser_version",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} is required")


@dataclass(frozen=True, kw_only=True)
class ImportCandidate:
    stable_id: str = field(default_factory=lambda: new_stable_id("candidate"))
    schema_version: str = "1.0"
    revision: int = 1
    extracted_value: str
    suggested_domain_type: str
    provenance: SourceProvenance
    parsing_confidence: float | None = None
    ai_confidence: float | None = None
    validation_issues: tuple[str, ...] = ()
    relationship_suggestions: tuple[str, ...] = ()
    review_status: ReviewStatus = ReviewStatus.UNREVIEWED

    def __post_init__(self) -> None:
        require_stable_id(self.stable_id)
        if self.revision < 1:
            raise ValueError("revision must be >= 1")
        if not self.extracted_value.strip():
            raise ValueError("extracted_value is required")
        if self.suggested_domain_type not in VALID_SUGGESTED_TYPES:
            raise ValueError(f"Unsupported suggested_domain_type: {self.suggested_domain_type}")
        if (
            self.suggested_domain_type == UNMAPPED_DOMAIN_TYPE
            and not self.validation_issues
        ):
            raise ValueError("unmapped candidates must carry a validation issue")
        _validate_confidence("parsing_confidence", self.parsing_confidence)
        _validate_confidence("ai_confidence", self.ai_confidence)
        if not isinstance(self.review_status, ReviewStatus):
            object.__setattr__(self, "review_status", ReviewStatus(self.review_status))

    def with_review_status(self, status: ReviewStatus) -> "ImportCandidate":
        return replace(self, review_status=status)


def _validate_confidence(name: str, value: float | None) -> None:
    if value is None:
        return
    if value < 0 or value > 1:
        raise ValueError(f"{name} must be between 0 and 1")

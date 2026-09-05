"""Transient workbook reconstruction helpers for logical FMEA rows."""
from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass

from .candidates import ImportCandidate, UNMAPPED_DOMAIN_TYPE, VALID_DOMAIN_TYPES


SUPPORTED_ROW_TYPES = (
    "Function",
    "Requirement",
    "ProductCharacteristic",
    "ProcessCharacteristic",
    "FailureMode",
    "FailureEffect",
    "FailureCause",
    "PreventionControl",
    "DetectionControl",
)


@dataclass(frozen=True, kw_only=True)
class FmeaRowCandidate:
    stable_id: str
    workbook_name: str
    document_version: str
    sheet_name: str
    row_start: int
    row_end: int
    source_range: str
    parser_version: str
    detected_fields: dict[str, list[str]]
    candidates: tuple[ImportCandidate, ...]

    @property
    def mapped_candidate_count(self) -> int:
        return sum(
            1
            for candidate in self.candidates
            if candidate.suggested_domain_type in VALID_DOMAIN_TYPES
        )

    @property
    def unmapped_candidate_count(self) -> int:
        return sum(
            1
            for candidate in self.candidates
            if candidate.suggested_domain_type == UNMAPPED_DOMAIN_TYPE
        )


def reconstruct_fmea_row_groups(
    candidates: list[ImportCandidate],
) -> list[FmeaRowCandidate]:
    grouped: dict[tuple[str, str, int], list[ImportCandidate]] = defaultdict(list)
    for candidate in candidates:
        provenance = candidate.provenance
        grouped[
            (
                provenance.workbook_name,
                provenance.sheet_name,
                provenance.row_number,
            )
        ].append(candidate)

    rows: list[FmeaRowCandidate] = []
    for (_workbook_name, _sheet_name, row_number), row_candidates in grouped.items():
        if not _is_reconstructable_fmea_row(row_candidates):
            continue
        ordered_candidates = tuple(
            sorted(
                row_candidates,
                key=lambda candidate: (
                    candidate.provenance.row_number,
                    candidate.provenance.column_name,
                    candidate.stable_id,
                ),
            )
        )
        first = ordered_candidates[0]
        provenance = first.provenance
        rows.append(
            FmeaRowCandidate(
                stable_id=_row_group_stable_id(
                    provenance.document_version,
                    provenance.workbook_name,
                    provenance.sheet_name,
                    row_number,
                    row_number,
                ),
                workbook_name=provenance.workbook_name,
                document_version=provenance.document_version,
                sheet_name=provenance.sheet_name,
                row_start=row_number,
                row_end=row_number,
                source_range=f"{provenance.sheet_name}!{row_number}:{row_number}",
                parser_version=provenance.parser_version,
                detected_fields=_detected_fields(ordered_candidates),
                candidates=ordered_candidates,
            )
        )

    return sorted(
        rows,
        key=lambda row: (row.sheet_name, row.row_start, row.row_end, row.stable_id),
    )


def _is_reconstructable_fmea_row(candidates: list[ImportCandidate]) -> bool:
    mapped_types = {
        candidate.suggested_domain_type
        for candidate in candidates
        if candidate.suggested_domain_type in VALID_DOMAIN_TYPES
    }
    if "FailureMode" not in mapped_types:
        return False
    return len(mapped_types) >= 2


def _detected_fields(candidates: tuple[ImportCandidate, ...]) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {domain_type: [] for domain_type in SUPPORTED_ROW_TYPES}
    for candidate in candidates:
        if candidate.suggested_domain_type not in fields:
            continue
        fields[candidate.suggested_domain_type].append(candidate.extracted_value)
    return {domain_type: values for domain_type, values in fields.items() if values}


def _row_group_stable_id(
    document_version: str,
    workbook_name: str,
    sheet_name: str,
    row_start: int,
    row_end: int,
) -> str:
    key = (
        "open-fmea:row-group:"
        f"{document_version}:{workbook_name}:{sheet_name}:{row_start}:{row_end}"
    )
    return f"row-group:{uuid.uuid5(uuid.NAMESPACE_URL, key).hex}"

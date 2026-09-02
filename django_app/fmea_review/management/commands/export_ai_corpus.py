from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand

from fmea_ingestion import ReviewStatus
from fmea_review.models import ImportCandidateRecord


DEFAULT_EXPORT_STATUSES = {
    ReviewStatus.ACCEPTED.value,
    ReviewStatus.MODIFIED.value,
}


class Command(BaseCommand):
    help = "Export reviewed import candidates as JSONL examples for AI prompt context."

    def add_arguments(self, parser) -> None:
        parser.add_argument("output_path", help="Destination JSONL file.")
        parser.add_argument(
            "--include-rejected",
            action="store_true",
            help="Include rejected examples with their review notes.",
        )
        parser.add_argument(
            "--include-duplicates",
            action="store_true",
            help="Include duplicate/merged examples.",
        )
        parser.add_argument(
            "--include-unreviewed",
            action="store_true",
            help="Include unreviewed examples for diagnostics only.",
        )

    def handle(self, *args, **options) -> None:
        output_path = Path(options["output_path"])
        statuses = set(DEFAULT_EXPORT_STATUSES)
        if options["include_rejected"]:
            statuses.add(ReviewStatus.REJECTED.value)
        if options["include_duplicates"]:
            statuses.add(ReviewStatus.DUPLICATE.value)
        if options["include_unreviewed"]:
            statuses.add(ReviewStatus.UNREVIEWED.value)
            statuses.add(ReviewStatus.NEEDS_CLARIFICATION.value)

        records = (
            ImportCandidateRecord.objects.select_related("session", "row_group", "reviewed_by")
            .filter(review_status__in=statuses)
            .order_by("session__uploaded_at", "row_number", "column_name", "stable_id")
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        exported_count = 0
        with output_path.open("w", encoding="utf-8", newline="\n") as handle:
            for record in records.iterator():
                handle.write(
                    json.dumps(_record_to_example(record), ensure_ascii=False, sort_keys=True)
                    + "\n"
                )
                exported_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Exported {exported_count} AI corpus examples to {output_path}")
        )


def _record_to_example(record: ImportCandidateRecord) -> dict[str, Any]:
    return {
        "schema_version": "open-fmea-ai-corpus-v1",
        "record_stable_id": record.stable_id,
        "input": {
            "cell_text": record.extracted_value,
            "column_name": record.column_name,
            "suggested_domain_type": record.suggested_domain_type,
            "validation_issues": record.validation_issues or [],
            "relationship_suggestions": record.relationship_suggestions or [],
        },
        "label": {
            "review_status": record.review_status,
            "accepted_object_stable_id": record.accepted_object_stable_id or "",
            "review_note": record.review_note,
            "was_modified_before_acceptance": record.review_note == "Modified before acceptance.",
        },
        "provenance": {
            "source_document_id": record.source_document_id,
            "document_version": record.document_version,
            "workbook_name": record.workbook_name,
            "sheet_name": record.sheet_name,
            "row_number": record.row_number,
            "row_group_stable_id": record.row_group.stable_id if record.row_group else "",
            "source_range": record.row_group.source_range if record.row_group else "",
            "parser_version": record.parser_version,
            "extraction_method": record.extraction_method,
        },
        "review": {
            "reviewed_at": record.reviewed_at.isoformat() if record.reviewed_at else "",
            "reviewed_by": record.reviewed_by.get_username() if record.reviewed_by else "",
        },
    }

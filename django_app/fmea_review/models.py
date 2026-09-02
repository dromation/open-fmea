from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from fmea_domain.identifiers import new_stable_id
from fmea_ingestion import ImportCandidate, ReviewStatus, SourceProvenance


class ImportSession(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewing", "Reviewing"),
        ("completed", "Completed"),
    ]

    stable_id = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        editable=False,
        default=new_stable_id,
    )
    source_filename = models.CharField(max_length=255)
    document_version = models.CharField(max_length=64, db_index=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="fmea_import_sessions",
        on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="pending")

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.source_filename} ({self.status})"


class FmeaRowGroup(models.Model):
    REVIEW_STATUS_CHOICES = [
        (status.value, status.name.replace("_", " ").title()) for status in ReviewStatus
    ]

    stable_id = models.CharField(max_length=128, unique=True, db_index=True, editable=False)
    session = models.ForeignKey(
        ImportSession,
        related_name="row_groups",
        on_delete=models.CASCADE,
    )
    sheet_name = models.CharField(max_length=255)
    row_start = models.PositiveIntegerField()
    row_end = models.PositiveIntegerField()
    source_range = models.CharField(max_length=255)
    parser_version = models.CharField(max_length=32)
    detected_fields = models.JSONField(default=dict, blank=True)
    review_status = models.CharField(
        max_length=32,
        choices=REVIEW_STATUS_CHOICES,
        default=ReviewStatus.UNREVIEWED.value,
    )
    accepted_object_stable_ids = models.JSONField(default=list, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="fmea_row_group_reviews",
        on_delete=models.SET_NULL,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        ordering = ["session", "sheet_name", "row_start", "row_end"]
        indexes = [
            models.Index(fields=["session", "review_status"], name="fmea_row_group_session_idx"),
            models.Index(fields=["sheet_name", "row_start"], name="fmea_row_group_source_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.sheet_name} rows {self.row_start}-{self.row_end}"


class ImportCandidateRecord(models.Model):
    REVIEW_STATUS_CHOICES = [
        (status.value, status.name.replace("_", " ").title()) for status in ReviewStatus
    ]

    stable_id = models.CharField(max_length=128, unique=True, db_index=True, editable=False)
    schema_version = models.CharField(max_length=16, default="1.0")
    revision = models.PositiveIntegerField(default=1)
    session = models.ForeignKey(
        ImportSession,
        related_name="candidates",
        on_delete=models.CASCADE,
    )
    row_group = models.ForeignKey(
        FmeaRowGroup,
        null=True,
        blank=True,
        related_name="candidates",
        on_delete=models.SET_NULL,
    )
    extracted_value = models.TextField()
    suggested_domain_type = models.CharField(max_length=64)
    source_document_id = models.CharField(max_length=128)
    document_version = models.CharField(max_length=64)
    workbook_name = models.CharField(max_length=255)
    sheet_name = models.CharField(max_length=255)
    row_number = models.PositiveIntegerField()
    column_name = models.CharField(max_length=255)
    extraction_method = models.CharField(
        max_length=32,
        choices=[("deterministic", "Deterministic"), ("ai", "AI")],
    )
    parser_version = models.CharField(max_length=32)
    parsing_confidence = models.FloatField(null=True, blank=True)
    ai_confidence = models.FloatField(null=True, blank=True)
    validation_issues = models.JSONField(default=list, blank=True)
    relationship_suggestions = models.JSONField(default=list, blank=True)
    review_status = models.CharField(
        max_length=32,
        choices=REVIEW_STATUS_CHOICES,
        default=ReviewStatus.UNREVIEWED.value,
    )
    accepted_object_stable_id = models.CharField(max_length=128, null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="fmea_import_candidate_reviews",
        on_delete=models.SET_NULL,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        ordering = ["session", "row_number", "column_name"]
        indexes = [
            models.Index(fields=["session", "review_status"], name="fmea_review_session_bcb716_idx"),
            models.Index(fields=["suggested_domain_type"], name="fmea_review_suggest_e2b2ec_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.suggested_domain_type}: {self.extracted_value[:60]}"

    @classmethod
    def from_candidate(
        cls,
        *,
        session: ImportSession,
        candidate: ImportCandidate,
        row_group: FmeaRowGroup | None = None,
    ) -> "ImportCandidateRecord":
        return cls(
            stable_id=candidate.stable_id,
            schema_version=candidate.schema_version,
            revision=candidate.revision,
            session=session,
            row_group=row_group,
            extracted_value=candidate.extracted_value,
            suggested_domain_type=candidate.suggested_domain_type,
            source_document_id=candidate.provenance.source_document_id,
            document_version=candidate.provenance.document_version,
            workbook_name=candidate.provenance.workbook_name,
            sheet_name=candidate.provenance.sheet_name,
            row_number=candidate.provenance.row_number,
            column_name=candidate.provenance.column_name,
            extraction_method=candidate.provenance.extraction_method,
            parser_version=candidate.provenance.parser_version,
            parsing_confidence=candidate.parsing_confidence,
            ai_confidence=candidate.ai_confidence,
            validation_issues=list(candidate.validation_issues),
            relationship_suggestions=list(candidate.relationship_suggestions),
            review_status=candidate.review_status.value,
        )

    def to_candidate(self) -> ImportCandidate:
        return ImportCandidate(
            stable_id=self.stable_id,
            schema_version=self.schema_version,
            revision=self.revision,
            extracted_value=self.extracted_value,
            suggested_domain_type=self.suggested_domain_type,
            provenance=SourceProvenance(
                source_document_id=self.source_document_id,
                document_version=self.document_version,
                workbook_name=self.workbook_name,
                sheet_name=self.sheet_name,
                row_number=self.row_number,
                column_name=self.column_name,
                extraction_method=self.extraction_method,  # type: ignore[arg-type]
                parser_version=self.parser_version,
            ),
            parsing_confidence=self.parsing_confidence,
            ai_confidence=self.ai_confidence,
            validation_issues=tuple(self.validation_issues or ()),
            relationship_suggestions=tuple(self.relationship_suggestions or ()),
            review_status=ReviewStatus(self.review_status),
        )

from __future__ import annotations

from typing import Mapping

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db import transaction
from django.utils import timezone

from fmea_ai.contracts import AiProvider
from fmea_ai.providers.disabled_provider import DisabledProvider
from fmea_ai.providers.ollama_provider import OllamaProvider
from fmea_app import models as fmea_models
from fmea_app.services import (
    DomainConstructionError,
    promote_import_candidate_to_domain_object,
)
from fmea_ingestion import ReviewStatus, reconstruct_fmea_row_groups
from fmea_ingestion.parsers import parse_xlsx_bytes

from . import models


ReviewUser = AbstractBaseUser | AnonymousUser | None


@transaction.atomic
def create_import_session_from_xlsx(
    *,
    file_bytes: bytes,
    source_filename: str,
    uploaded_by: ReviewUser = None,
    provider: AiProvider | None = None,
    ai_enabled: bool | None = None,
) -> models.ImportSession:
    effective_ai_enabled = (
        bool(getattr(settings, "OPEN_FMEA_AI_ENABLED", False))
        if ai_enabled is None
        else ai_enabled
    )
    provider = provider or _provider_from_settings(enabled=effective_ai_enabled)
    candidates = parse_xlsx_bytes(
        file_bytes,
        workbook_name=source_filename,
        provider=provider,
        ai_enabled=effective_ai_enabled,
    )
    session = models.ImportSession.objects.create(
        source_filename=source_filename,
        document_version=candidates[0].provenance.document_version,
        uploaded_by=_user_or_none(uploaded_by),
        status="reviewing",
    )
    row_candidates = reconstruct_fmea_row_groups(candidates)
    grouped_candidate_ids: set[str] = set()
    records = []
    for row_candidate in row_candidates:
        row_group = models.FmeaRowGroup.objects.create(
            stable_id=row_candidate.stable_id,
            session=session,
            sheet_name=row_candidate.sheet_name,
            row_start=row_candidate.row_start,
            row_end=row_candidate.row_end,
            source_range=row_candidate.source_range,
            parser_version=row_candidate.parser_version,
            detected_fields=row_candidate.detected_fields,
        )
        for candidate in row_candidate.candidates:
            grouped_candidate_ids.add(candidate.stable_id)
            records.append(
                models.ImportCandidateRecord.from_candidate(
                    session=session,
                    candidate=candidate,
                    row_group=row_group,
                )
            )
    for candidate in candidates:
        if candidate.stable_id in grouped_candidate_ids:
            continue
        records.append(models.ImportCandidateRecord.from_candidate(session=session, candidate=candidate))
    models.ImportCandidateRecord.objects.bulk_create(records)
    return session


@transaction.atomic
def accept_candidate(
    record: models.ImportCandidateRecord,
    *,
    reviewed_by: ReviewUser = None,
    context: Mapping[str, str] | None = None,
) -> models.ImportCandidateRecord:
    if record.review_status == ReviewStatus.REJECTED.value:
        raise DomainConstructionError("Rejected candidates cannot be accepted")
    if record.suggested_domain_type == "unmapped":
        raise DomainConstructionError("Unmapped candidates must be edited before acceptance")

    created = promote_import_candidate_to_domain_object(
        suggested_domain_type=record.suggested_domain_type,
        extracted_value=record.extracted_value,
        context=context,
    )
    record.accepted_object_stable_id = created.stable_id
    record.review_status = ReviewStatus.ACCEPTED.value
    record.reviewed_by = _user_or_none(reviewed_by)
    record.reviewed_at = timezone.now()
    record.save(
        update_fields=[
            "accepted_object_stable_id",
            "review_status",
            "reviewed_by",
            "reviewed_at",
        ]
    )
    _refresh_session_status(record.session)
    return record


@transaction.atomic
def reject_candidate(
    record: models.ImportCandidateRecord,
    *,
    reviewed_by: ReviewUser = None,
    reason: str = "",
) -> models.ImportCandidateRecord:
    record.review_status = ReviewStatus.REJECTED.value
    record.reviewed_by = _user_or_none(reviewed_by)
    record.reviewed_at = timezone.now()
    record.review_note = reason.strip()
    record.save(update_fields=["review_status", "reviewed_by", "reviewed_at", "review_note"])
    _refresh_session_status(record.session)
    return record


@transaction.atomic
def modify_and_accept_candidate(
    record: models.ImportCandidateRecord,
    *,
    reviewed_by: ReviewUser = None,
    extracted_value: str,
    suggested_domain_type: str,
    context: Mapping[str, str] | None = None,
) -> models.ImportCandidateRecord:
    record.extracted_value = extracted_value.strip()
    record.suggested_domain_type = suggested_domain_type.strip()
    record.review_status = ReviewStatus.MODIFIED.value
    record.reviewed_by = _user_or_none(reviewed_by)
    record.reviewed_at = timezone.now()
    record.review_note = "Modified before acceptance."
    record.save(
        update_fields=[
            "extracted_value",
            "suggested_domain_type",
            "review_status",
            "reviewed_by",
            "reviewed_at",
            "review_note",
        ]
    )
    return accept_candidate(record, reviewed_by=reviewed_by, context=context)


@transaction.atomic
def link_existing_candidate(
    record: models.ImportCandidateRecord,
    *,
    existing_stable_id: str,
    reviewed_by: ReviewUser = None,
) -> models.ImportCandidateRecord:
    if not _domain_object_exists(existing_stable_id):
        raise DomainConstructionError("No existing FMEA object found for that stable_id")
    record.accepted_object_stable_id = existing_stable_id
    record.review_status = ReviewStatus.ACCEPTED.value
    record.reviewed_by = _user_or_none(reviewed_by)
    record.reviewed_at = timezone.now()
    record.review_note = "Linked to an existing object."
    record.save(
        update_fields=[
            "accepted_object_stable_id",
            "review_status",
            "reviewed_by",
            "reviewed_at",
            "review_note",
        ]
    )
    _refresh_session_status(record.session)
    return record


@transaction.atomic
def merge_candidate(
    record: models.ImportCandidateRecord,
    *,
    target_record: models.ImportCandidateRecord,
    reviewed_by: ReviewUser = None,
) -> models.ImportCandidateRecord:
    if record.session_id != target_record.session_id:
        raise DomainConstructionError("Candidates can only be merged within one import session")
    record.accepted_object_stable_id = target_record.accepted_object_stable_id
    record.review_status = ReviewStatus.DUPLICATE.value
    record.reviewed_by = _user_or_none(reviewed_by)
    record.reviewed_at = timezone.now()
    record.review_note = f"Merged with candidate {target_record.stable_id}."
    record.save(
        update_fields=[
            "accepted_object_stable_id",
            "review_status",
            "reviewed_by",
            "reviewed_at",
            "review_note",
        ]
    )
    _refresh_session_status(record.session)
    return record


@transaction.atomic
def accept_row_group(
    row_group: models.FmeaRowGroup,
    *,
    reviewed_by: ReviewUser = None,
    context: Mapping[str, str] | None = None,
) -> models.FmeaRowGroup:
    if row_group.review_status == ReviewStatus.REJECTED.value:
        raise DomainConstructionError("Rejected row groups cannot be accepted")

    created_ids: list[str] = []
    working_context = dict(context or {})
    records = list(
        row_group.candidates.exclude(suggested_domain_type="unmapped").order_by(
            "row_number",
            "column_name",
            "stable_id",
        )
    )
    if not records:
        raise DomainConstructionError("Row group does not contain importable FMEA fields")

    for domain_type in (
        "Function",
        "Requirement",
        "ProductCharacteristic",
        "ProcessCharacteristic",
        "FailureMode",
        "FailureEffect",
        "FailureCause",
        "PreventionControl",
        "DetectionControl",
    ):
        for record in [item for item in records if item.suggested_domain_type == domain_type]:
            record_context = _context_for_row_record(record, working_context)
            created = promote_import_candidate_to_domain_object(
                suggested_domain_type=record.suggested_domain_type,
                extracted_value=record.extracted_value,
                context=record_context,
            )
            created_ids.append(created.stable_id)
            _store_created_context(record.suggested_domain_type, created, working_context)
            _mark_candidate_reviewed(
                record,
                status=ReviewStatus.ACCEPTED,
                accepted_object_stable_id=created.stable_id,
                reviewed_by=reviewed_by,
            )

    for record in row_group.candidates.filter(suggested_domain_type="unmapped"):
        _mark_candidate_reviewed(
            record,
            status=ReviewStatus.NEEDS_CLARIFICATION,
            accepted_object_stable_id="",
            reviewed_by=reviewed_by,
            review_note="Row accepted; this cell is not importable in the current slice.",
        )

    row_group.accepted_object_stable_ids = created_ids
    row_group.review_status = ReviewStatus.ACCEPTED.value
    row_group.reviewed_by = _user_or_none(reviewed_by)
    row_group.reviewed_at = timezone.now()
    row_group.review_note = "Accepted as a logical FMEA row."
    row_group.save(
        update_fields=[
            "accepted_object_stable_ids",
            "review_status",
            "reviewed_by",
            "reviewed_at",
            "review_note",
        ]
    )
    _refresh_session_status(row_group.session)
    return row_group


@transaction.atomic
def reject_row_group(
    row_group: models.FmeaRowGroup,
    *,
    reviewed_by: ReviewUser = None,
    reason: str = "",
) -> models.FmeaRowGroup:
    note = reason.strip()
    now = timezone.now()
    row_group.review_status = ReviewStatus.REJECTED.value
    row_group.reviewed_by = _user_or_none(reviewed_by)
    row_group.reviewed_at = now
    row_group.review_note = note
    row_group.save(update_fields=["review_status", "reviewed_by", "reviewed_at", "review_note"])
    row_group.candidates.update(
        review_status=ReviewStatus.REJECTED.value,
        reviewed_by=_user_or_none(reviewed_by),
        reviewed_at=now,
        review_note=note,
    )
    _refresh_session_status(row_group.session)
    return row_group


def _provider_from_settings(*, enabled: bool) -> AiProvider:
    if not enabled:
        return DisabledProvider()
    return OllamaProvider(
        endpoint=getattr(settings, "OPEN_FMEA_OLLAMA_ENDPOINT", "http://127.0.0.1:11434"),
        model=getattr(settings, "OPEN_FMEA_OLLAMA_MODEL", None),
        timeout=float(getattr(settings, "OPEN_FMEA_OLLAMA_TIMEOUT_SECONDS", 30)),
        enabled=enabled,
    )


def _refresh_session_status(session: models.ImportSession) -> None:
    if session.row_groups.exists():
        open_count = session.row_groups.filter(review_status=ReviewStatus.UNREVIEWED.value).count()
        open_count += session.candidates.filter(
            row_group__isnull=True,
            review_status=ReviewStatus.UNREVIEWED.value,
        ).count()
    else:
        open_count = session.candidates.filter(review_status=ReviewStatus.UNREVIEWED.value).count()
    session.status = "completed" if open_count == 0 else "reviewing"
    session.save(update_fields=["status"])


def _user_or_none(user: ReviewUser) -> AbstractBaseUser | None:
    if user is None or getattr(user, "is_anonymous", False):
        return None
    return user  # type: ignore[return-value]


def _domain_object_exists(stable_id: str) -> bool:
    model_classes = (
        fmea_models.Function,
        fmea_models.Requirement,
        fmea_models.ProductCharacteristic,
        fmea_models.ProcessCharacteristic,
        fmea_models.FailureMode,
        fmea_models.FailureEffect,
        fmea_models.FailureCause,
        fmea_models.PreventionControl,
        fmea_models.DetectionControl,
    )
    return any(model_class.objects.filter(stable_id=stable_id).exists() for model_class in model_classes)


def _context_for_row_record(
    record: models.ImportCandidateRecord,
    working_context: dict[str, str],
) -> dict[str, str]:
    context = dict(working_context)
    if record.suggested_domain_type in {"FailureEffect", "FailureCause"}:
        _require_working_context(context, "failure_mode_stable_id", record.suggested_domain_type)
    if record.suggested_domain_type in {"PreventionControl", "DetectionControl"}:
        _require_working_context(context, "failure_cause_stable_id", record.suggested_domain_type)
    if record.suggested_domain_type == "FailureMode":
        _require_working_context(context, "fmea_stable_id", record.suggested_domain_type)
    if record.suggested_domain_type == "ProcessCharacteristic":
        _require_working_context(context, "operation_stable_id", record.suggested_domain_type)
    return context


def _require_working_context(context: dict[str, str], key: str, domain_type: str) -> None:
    if not context.get(key, "").strip():
        raise DomainConstructionError(f"{key} is required for row-level {domain_type} creation")


def _store_created_context(
    domain_type: str,
    created: fmea_models.StableModel,
    working_context: dict[str, str],
) -> None:
    if domain_type == "Function":
        working_context.setdefault("function_stable_id", created.stable_id)
    elif domain_type == "Requirement":
        working_context.setdefault("requirement_stable_id", created.stable_id)
    elif domain_type == "ProductCharacteristic":
        working_context.setdefault("product_characteristic_stable_id", created.stable_id)
    elif domain_type == "ProcessCharacteristic":
        working_context.setdefault("process_characteristic_stable_id", created.stable_id)
    elif domain_type == "FailureMode":
        working_context.setdefault("failure_mode_stable_id", created.stable_id)
    elif domain_type == "FailureCause":
        working_context.setdefault("failure_cause_stable_id", created.stable_id)


def _mark_candidate_reviewed(
    record: models.ImportCandidateRecord,
    *,
    status: ReviewStatus,
    accepted_object_stable_id: str,
    reviewed_by: ReviewUser,
    review_note: str = "",
) -> None:
    record.review_status = status.value
    record.accepted_object_stable_id = accepted_object_stable_id or None
    record.reviewed_by = _user_or_none(reviewed_by)
    record.reviewed_at = timezone.now()
    if review_note:
        record.review_note = review_note
    record.save(
        update_fields=[
            "review_status",
            "accepted_object_stable_id",
            "reviewed_by",
            "reviewed_at",
            "review_note",
        ]
    )

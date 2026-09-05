from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from fmea_app import models as fmea_models
from fmea_app.services import DomainConstructionError
from fmea_ingestion import VALID_DOMAIN_TYPES
from fmea_ingestion.parsers import WorkbookParseError

from . import models, services


def session_list(request):
    sessions = models.ImportSession.objects.prefetch_related("candidates").all()
    return render(request, "fmea_review/session_list.html", {"sessions": sessions})


@require_POST
def upload_xlsx(request):
    upload = request.FILES.get("workbook")
    if upload is None:
        messages.error(request, "Select an .xlsx or .xlsm workbook before uploading.")
        return redirect("fmea_review:session_list")
    if not upload.name.lower().endswith((".xlsx", ".xlsm")):
        messages.error(request, "Only .xlsx and .xlsm workbooks are supported in this slice.")
        return redirect("fmea_review:session_list")
    max_bytes = int(getattr(settings, "OPEN_FMEA_IMPORT_MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
    if upload.size > max_bytes:
        messages.error(request, f"Workbook is larger than the configured {max_bytes} byte limit.")
        return redirect("fmea_review:session_list")

    try:
        session = services.create_import_session_from_xlsx(
            file_bytes=upload.read(),
            source_filename=upload.name,
            uploaded_by=request.user,
        )
    except WorkbookParseError as exc:
        messages.error(request, str(exc))
        return redirect("fmea_review:session_list")

    messages.success(request, f"Imported {session.candidates.count()} candidates for review.")
    return redirect("fmea_review:session_detail", stable_id=session.stable_id)


def session_detail(request, stable_id: str):
    session = get_object_or_404(
        models.ImportSession.objects.prefetch_related("row_groups", "candidates"),
        stable_id=stable_id,
    )
    return render(request, "fmea_review/session_detail.html", {"session": session})


def row_group_detail(request, stable_id: str):
    row_group = get_object_or_404(
        models.FmeaRowGroup.objects.select_related("session").prefetch_related("candidates"),
        stable_id=stable_id,
    )
    return render(
        request,
        "fmea_review/row_group_detail.html",
        {
            "row_group": row_group,
            "fmeas": fmea_models.FMEA.objects.order_by("name"),
        },
    )


def candidate_detail(request, stable_id: str):
    record = get_object_or_404(models.ImportCandidateRecord, stable_id=stable_id)
    return render(
        request,
        "fmea_review/candidate_detail.html",
        {
            "record": record,
            "domain_types": sorted(VALID_DOMAIN_TYPES),
            "fmeas": fmea_models.FMEA.objects.order_by("name"),
            "failure_modes": fmea_models.FailureMode.objects.order_by("name"),
            "failure_causes": fmea_models.FailureCause.objects.order_by("name"),
            "functions": fmea_models.Function.objects.order_by("name"),
            "requirements": fmea_models.Requirement.objects.order_by("name"),
        },
    )


@require_POST
def accept_candidate(request, stable_id: str):
    record = get_object_or_404(models.ImportCandidateRecord, stable_id=stable_id)
    try:
        services.accept_candidate(
            record,
            reviewed_by=request.user,
            context=_context_from_post(request.POST),
        )
    except DomainConstructionError as exc:
        messages.error(request, str(exc))
        return redirect("fmea_review:candidate_detail", stable_id=record.stable_id)
    messages.success(request, "Candidate accepted.")
    return redirect("fmea_review:session_detail", stable_id=record.session.stable_id)


@require_POST
def reject_candidate(request, stable_id: str):
    record = get_object_or_404(models.ImportCandidateRecord, stable_id=stable_id)
    services.reject_candidate(
        record,
        reviewed_by=request.user,
        reason=request.POST.get("reason", ""),
    )
    messages.success(request, "Candidate rejected.")
    return redirect("fmea_review:session_detail", stable_id=record.session.stable_id)


@require_POST
def modify_candidate(request, stable_id: str):
    record = get_object_or_404(models.ImportCandidateRecord, stable_id=stable_id)
    try:
        services.modify_and_accept_candidate(
            record,
            reviewed_by=request.user,
            extracted_value=request.POST.get("extracted_value", ""),
            suggested_domain_type=request.POST.get("suggested_domain_type", ""),
            context=_context_from_post(request.POST),
        )
    except DomainConstructionError as exc:
        messages.error(request, str(exc))
        return redirect("fmea_review:candidate_detail", stable_id=record.stable_id)
    messages.success(request, "Candidate modified and accepted.")
    return redirect("fmea_review:session_detail", stable_id=record.session.stable_id)


@require_POST
def link_existing(request, stable_id: str):
    record = get_object_or_404(models.ImportCandidateRecord, stable_id=stable_id)
    try:
        services.link_existing_candidate(
            record,
            existing_stable_id=request.POST.get("existing_stable_id", ""),
            reviewed_by=request.user,
        )
    except DomainConstructionError as exc:
        messages.error(request, str(exc))
        return redirect("fmea_review:candidate_detail", stable_id=record.stable_id)
    messages.success(request, "Candidate linked to an existing object.")
    return redirect("fmea_review:session_detail", stable_id=record.session.stable_id)


@require_POST
def merge_candidate(request, stable_id: str):
    record = get_object_or_404(models.ImportCandidateRecord, stable_id=stable_id)
    target = get_object_or_404(
        models.ImportCandidateRecord,
        stable_id=request.POST.get("target_candidate_stable_id", ""),
    )
    try:
        services.merge_candidate(record, target_record=target, reviewed_by=request.user)
    except DomainConstructionError as exc:
        messages.error(request, str(exc))
        return redirect("fmea_review:candidate_detail", stable_id=record.stable_id)
    messages.success(request, "Candidate merged.")
    return redirect("fmea_review:session_detail", stable_id=record.session.stable_id)


@require_POST
def accept_row_group(request, stable_id: str):
    row_group = get_object_or_404(models.FmeaRowGroup, stable_id=stable_id)
    try:
        services.accept_row_group(
            row_group,
            reviewed_by=request.user,
            context=_context_from_post(request.POST),
        )
    except DomainConstructionError as exc:
        messages.error(request, str(exc))
        return redirect("fmea_review:row_group_detail", stable_id=row_group.stable_id)
    messages.success(request, "FMEA row accepted.")
    return redirect("fmea_review:session_detail", stable_id=row_group.session.stable_id)


@require_POST
def reject_row_group(request, stable_id: str):
    row_group = get_object_or_404(models.FmeaRowGroup, stable_id=stable_id)
    services.reject_row_group(
        row_group,
        reviewed_by=request.user,
        reason=request.POST.get("reason", ""),
    )
    messages.success(request, "FMEA row rejected.")
    return redirect("fmea_review:session_detail", stable_id=row_group.session.stable_id)


def _context_from_post(post_data) -> dict[str, str]:
    return {
        key: str(post_data.get(key, "")).strip()
        for key in (
            "fmea_stable_id",
            "function_stable_id",
            "requirement_stable_id",
            "operation_stable_id",
            "cause_category_stable_id",
            "product_characteristic_stable_id",
            "process_characteristic_stable_id",
            "failure_mode_stable_id",
            "failure_cause_stable_id",
        )
        if str(post_data.get(key, "")).strip()
    }

from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from fmea_domain import CauseInfluenceStatus
from fmea_ingestion import ReviewStatus
from fmea_review import models as review_models

from . import forms
from . import models
from .models import FailureCause, FailureMode, FMEA, FMEAProject
from .services import (
    DomainConstructionError,
    create_cause_influence,
    evaluate_failure_mode,
    get_fmea_by_stable_id,
    legal_cause_influence_transition_statuses,
    transition_cause_influence,
)


def dashboard(request):
    fmeas = FMEA.objects.select_related("project").order_by("name")
    pending_candidate_count = review_models.ImportCandidateRecord.objects.filter(
        review_status=ReviewStatus.UNREVIEWED.value
    ).count()
    pending_row_group_count = review_models.FmeaRowGroup.objects.filter(
        review_status=ReviewStatus.UNREVIEWED.value
    ).count()
    return render(
        request,
        "fmea_app/dashboard.html",
        {
            "fmeas": fmeas,
            "projects": FMEAProject.objects.order_by("name"),
            "fmea_count": FMEA.objects.count(),
            "project_form": forms.FMEAProjectForm(),
            "fmea_form": forms.FMEAForm(),
            "pending_candidate_count": pending_candidate_count,
            "pending_row_group_count": pending_row_group_count,
            "pending_review_detail": (
                f"{pending_candidate_count} {_plural('candidate', pending_candidate_count)}, "
                f"{pending_row_group_count} {_plural('row', pending_row_group_count)}"
            ),
            "cause_status_breakdown": _cause_status_breakdown(),
            "recent_activity": _recent_activity(),
        },
    )


@require_POST
def create_project(request):
    form = forms.FMEAProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        messages.success(request, f"Created project {project.name}.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:dashboard")


@require_POST
def create_fmea(request):
    form = forms.FMEAForm(request.POST)
    if form.is_valid():
        fmea = form.save()
        messages.success(request, f"Created FMEA {fmea.name}.")
        return redirect("fmea:fmea_detail", stable_id=fmea.stable_id)
    messages.error(request, _form_errors(form))
    return redirect("fmea:dashboard")


def fmea_detail(request, stable_id: str):
    fmea = get_fmea_by_stable_id(stable_id)
    failure_modes = (
        fmea.failure_modes.select_related("function", "requirement")
        .prefetch_related(
            "requirement__product_characteristics",
            "effects",
            "causes__prevention_controls",
            "causes__detection_controls",
            "risk_evaluations__definition",
        )
        .order_by("name")
    )
    worksheet_rows = _build_worksheet_rows(failure_modes)
    return render(
        request,
        "fmea_app/fmea_detail.html",
        {
            "fmea": fmea,
            "failure_modes": failure_modes,
            "worksheet_rows": worksheet_rows,
            "failure_mode_form": forms.FailureModeForm(),
            "effect_form": forms.FailureEffectForm(),
            "cause_form": forms.FailureCauseForm(),
            "prevention_form": forms.PreventionControlForm(),
            "detection_form": forms.DetectionControlForm(),
            "risk_form": forms.RiskEvaluationForm(),
        },
    )


@require_POST
def add_failure_mode(request, stable_id: str):
    fmea = get_fmea_by_stable_id(stable_id)
    form = forms.FailureModeForm(request.POST)
    if form.is_valid():
        failure_mode = form.save(commit=False)
        failure_mode.fmea = fmea
        failure_mode.save()
        messages.success(request, "Failure mode added.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=fmea.stable_id)


@require_POST
def add_failure_effect(request, stable_id: str):
    failure_mode = get_object_or_404(FailureMode, stable_id=stable_id)
    form = forms.FailureEffectForm(request.POST)
    if form.is_valid():
        effect = form.save(commit=False)
        effect.failure_mode = failure_mode
        effect.save()
        messages.success(request, "Effect added.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=failure_mode.fmea.stable_id)


@require_POST
def add_failure_cause(request, stable_id: str):
    failure_mode = get_object_or_404(FailureMode, stable_id=stable_id)
    form = forms.FailureCauseForm(request.POST)
    if form.is_valid():
        cause = form.save(commit=False)
        cause.failure_mode = failure_mode
        cause.save()
        messages.success(request, "Cause added.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=failure_mode.fmea.stable_id)


@require_POST
def add_prevention_control(request, stable_id: str):
    cause = get_object_or_404(FailureCause, stable_id=stable_id)
    form = forms.PreventionControlForm(request.POST)
    if form.is_valid():
        prevention = form.save(commit=False)
        prevention.failure_cause = cause
        prevention.save()
        messages.success(request, "Prevention control added.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=cause.failure_mode.fmea.stable_id)


@require_POST
def add_detection_control(request, stable_id: str):
    cause = get_object_or_404(FailureCause, stable_id=stable_id)
    form = forms.DetectionControlForm(request.POST)
    if form.is_valid():
        detection = form.save(commit=False)
        detection.failure_cause = cause
        detection.save()
        messages.success(request, "Detection control added.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=cause.failure_mode.fmea.stable_id)


@require_POST
def evaluate_failure(request, stable_id: str):
    failure_mode = get_object_or_404(FailureMode, stable_id=stable_id)
    form = forms.RiskEvaluationForm(request.POST)
    if form.is_valid():
        evaluate_failure_mode(
            failure_mode=failure_mode,
            definition=form.cleaned_data["definition"],
            severity=form.cleaned_data["severity"],
            occurrence=form.cleaned_data["occurrence"],
            detection=form.cleaned_data["detection"],
            actor=request.user.username if request.user.is_authenticated else "local-user",
        )
        messages.success(request, "Risk evaluation saved.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=failure_mode.fmea.stable_id)


def cause_influence_list(request):
    status_filter = request.GET.get("status", "").strip()
    category_filter = request.GET.get("cause_category_id", "").strip()
    influences = models.CauseInfluence.objects.order_by(
        "target_type",
        "target_id",
        "status",
        "source_type",
        "source_id",
    )
    if status_filter:
        influences = influences.filter(status=status_filter)
    if category_filter:
        influences = influences.filter(cause_category_id=category_filter)
    category_by_id = _category_by_id()
    return render(
        request,
        "fmea_app/cause_influence_list.html",
        {
            "influences": [_influence_view_model(item, category_by_id) for item in influences],
            "categories": models.CauseCategory.objects.order_by("sort_order", "name"),
            "statuses": CauseInfluenceStatus,
            "status_filter": status_filter,
            "category_filter": category_filter,
        },
    )


def process_characteristic_list(request):
    process_characteristics = models.ProcessCharacteristic.objects.select_related(
        "operation",
        "operation__process",
    ).order_by("operation__process__name", "operation__sequence", "operation__name", "name")
    category_by_id = _category_by_id()
    return render(
        request,
        "fmea_app/process_characteristic_list.html",
        {
            "process_characteristics": [
                {
                    "item": item,
                    "category_name": (
                        category_by_id[item.cause_category_id].name
                        if item.cause_category_id in category_by_id
                        else "Uncategorized"
                    ),
                }
                for item in process_characteristics
            ],
        },
    )


def new_process_characteristic(request):
    if request.method == "POST":
        form = forms.ProcessCharacteristicForm(request.POST)
        if form.is_valid():
            process_characteristic = form.save()
            messages.success(request, "Process characteristic created.")
            return redirect(
                "fmea:process_characteristic_detail",
                stable_id=process_characteristic.stable_id,
            )
        messages.error(request, _form_errors(form))
    else:
        initial = {}
        operation_id = request.GET.get("operation_id", "").strip()
        if operation_id:
            try:
                initial["operation"] = models.Operation.objects.get(stable_id=operation_id)
            except models.Operation.DoesNotExist:
                messages.error(request, f"No Operation found for stable_id {operation_id}")
        form = forms.ProcessCharacteristicForm(initial=initial)
    return render(
        request,
        "fmea_app/process_characteristic_form.html",
        {"form": form},
    )


def process_characteristic_detail(request, stable_id: str):
    process_characteristic = get_object_or_404(
        models.ProcessCharacteristic.objects.select_related("operation", "operation__process"),
        stable_id=stable_id,
    )
    category_by_id = _category_by_id()
    outgoing = [
        _influence_view_model(influence, category_by_id)
        for influence in models.CauseInfluence.objects.filter(
            source_type="ProcessCharacteristic",
            source_id=process_characteristic.stable_id,
        ).order_by("target_type", "target_id", "status")
    ]
    incoming = [
        _influence_view_model(influence, category_by_id)
        for influence in models.CauseInfluence.objects.filter(
            target_type="ProcessCharacteristic",
            target_id=process_characteristic.stable_id,
        ).order_by("source_type", "source_id", "status")
    ]
    category = category_by_id.get(process_characteristic.cause_category_id or "")
    return render(
        request,
        "fmea_app/process_characteristic_detail.html",
        {
            "process_characteristic": process_characteristic,
            "category": category,
            "outgoing_influences": outgoing,
            "incoming_influences": incoming,
        },
    )


def new_cause_influence(request):
    source_type = request.GET.get("source_type", "").strip()
    source_id = request.GET.get("source_id", "").strip()
    target_type = request.GET.get("target_type", "").strip()
    target_id = request.GET.get("target_id", "").strip()
    source_label = _label_for_reference(source_type, source_id) if source_type and source_id else ""
    target_label = _label_for_reference(target_type, target_id) if target_type and target_id else ""
    return render(
        request,
        "fmea_app/cause_influence_form.html",
        {
            "categories": models.CauseCategory.objects.order_by("sort_order", "name"),
            "statuses": CauseInfluenceStatus,
            "source_types": models.CauseInfluence.SOURCE_TYPE_CHOICES,
            "target_types": models.CauseInfluence.TARGET_TYPE_CHOICES,
            "source_type": source_type,
            "source_id": source_id,
            "source_label": source_label,
            "target_type": target_type,
            "target_id": target_id,
            "target_label": target_label,
            "failure_causes": models.FailureCause.objects.order_by("name"),
            "failure_mechanisms": models.FailureMechanism.objects.order_by("name"),
            "product_characteristics": models.ProductCharacteristic.objects.order_by("name"),
            "process_characteristics": models.ProcessCharacteristic.objects.order_by("name"),
        },
    )


@require_POST
def create_cause_influence_view(request):
    try:
        confidence = _optional_float(request.POST.get("confidence", ""))
        influence = create_cause_influence(
            source_type=request.POST.get("source_type", ""),
            source_id=request.POST.get("source_id", ""),
            target_type=request.POST.get("target_type", ""),
            target_id=request.POST.get("target_id", ""),
            influence_type=request.POST.get("influence_type", ""),
            status=CauseInfluenceStatus.SUSPECTED.value,
            cause_category_id=request.POST.get("cause_category_id", ""),
            confidence=confidence,
            strength=request.POST.get("strength", ""),
            source_context=request.POST.get("source_context", "FMEA"),
            review_note=request.POST.get("review_note", ""),
        )
    except (DomainConstructionError, ValueError) as exc:
        messages.error(request, str(exc))
        query = urlencode(
            {
                "target_type": request.POST.get("target_type", ""),
                "target_id": request.POST.get("target_id", ""),
            }
        )
        return redirect(f"{reverse('fmea:new_cause_influence')}?{query}")
    messages.success(request, "Cause influence created.")
    return redirect("fmea:cause_influence_detail", stable_id=influence.stable_id)


def cause_influence_detail(request, stable_id: str):
    influence = get_object_or_404(models.CauseInfluence, stable_id=stable_id)
    category_by_id = _category_by_id()
    target_failure_causes = []
    if influence.target_type == "FailureMode":
        target_failure_causes = models.FailureCause.objects.filter(
            failure_mode__stable_id=influence.target_id
        ).order_by("name")
    return render(
        request,
        "fmea_app/cause_influence_detail.html",
        {
            "item": _influence_view_model(influence, category_by_id),
            "influence": influence,
            "categories": models.CauseCategory.objects.order_by("sort_order", "name"),
            "legal_statuses": legal_cause_influence_transition_statuses(influence),
            "target_failure_causes": target_failure_causes,
        },
    )


@require_POST
def transition_cause_influence_view(request, stable_id: str):
    influence = get_object_or_404(models.CauseInfluence, stable_id=stable_id)
    try:
        transition_cause_influence(
            influence,
            new_status=request.POST.get("new_status", ""),
            review_note=request.POST.get("review_note", ""),
            failure_cause_stable_id=request.POST.get("failure_cause_stable_id", ""),
            cause_category_id=request.POST.get("cause_category_id", ""),
            reviewed_by=request.user,
        )
    except DomainConstructionError as exc:
        messages.error(request, str(exc))
        return redirect("fmea:cause_influence_detail", stable_id=influence.stable_id)
    messages.success(request, "Cause influence status updated.")
    return redirect("fmea:cause_influence_detail", stable_id=influence.stable_id)


def ishikawa_board(request, stable_id: str):
    failure_mode = get_object_or_404(
        FailureMode.objects.select_related("fmea").prefetch_related("causes"),
        stable_id=stable_id,
    )
    failure_cause_ids = list(failure_mode.causes.values_list("stable_id", flat=True))
    influences = models.CauseInfluence.objects.filter(
        Q(target_type="FailureMode", target_id=failure_mode.stable_id)
        | Q(target_type="FailureCause", target_id__in=failure_cause_ids)
    ).order_by("cause_category_id", "status", "source_type", "source_id")
    category_by_id = _category_by_id()
    groups = _ishikawa_groups(influences, category_by_id)
    return render(
        request,
        "fmea_app/ishikawa_board.html",
        {
            "failure_mode": failure_mode,
            "groups": groups,
        },
    )


def _form_errors(form) -> str:
    return " ".join(
        f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()
    )


def _cause_status_breakdown() -> list[dict]:
    counts = {
        row["status"]: row["count"]
        for row in models.CauseInfluence.objects.values("status").annotate(count=Count("id"))
    }
    max_count = max(counts.values(), default=0) or 1
    breakdown = []
    for status in CauseInfluenceStatus:
        count = counts.get(status.value, 0)
        breakdown.append(
            {
                "status": status.value,
                "label": status.name.replace("_", " ").title(),
                "count": count,
                "percent": int((count / max_count) * 100) if count else 0,
            }
        )
    return breakdown


def _recent_activity() -> list[dict]:
    activities = []
    candidate_actions = review_models.ImportCandidateRecord.objects.exclude(
        reviewed_at__isnull=True
    ).order_by("-reviewed_at")[:10]
    for record in candidate_actions:
        activities.append(
            {
                "when": record.reviewed_at,
                "kind": "Candidate",
                "title": record.get_review_status_display(),
                "description": f"{record.suggested_domain_type}: {record.extracted_value[:80]}",
                "stable_id": record.stable_id,
            }
        )

    row_actions = review_models.FmeaRowGroup.objects.exclude(
        reviewed_at__isnull=True
    ).order_by("-reviewed_at")[:10]
    for row_group in row_actions:
        activities.append(
            {
                "when": row_group.reviewed_at,
                "kind": "Row Group",
                "title": row_group.get_review_status_display(),
                "description": row_group.source_range,
                "stable_id": row_group.stable_id,
            }
        )

    influence_actions = models.CauseInfluence.objects.exclude(reviewed_at__isnull=True).order_by(
        "-reviewed_at"
    )[:10]
    for influence in influence_actions:
        activities.append(
            {
                "when": influence.reviewed_at,
                "kind": "Cause Influence",
                "title": f"Transitioned to {influence.get_status_display()}",
                "description": f"{influence.source_type} -> {influence.target_type}",
                "stable_id": influence.stable_id,
            }
        )

    return sorted(activities, key=lambda item: item["when"], reverse=True)[:10]


def _plural(label: str, count: int) -> str:
    return label if count == 1 else f"{label}s"


def _build_worksheet_rows(failure_modes):
    rows = []
    for failure_mode in failure_modes:
        effects = list(failure_mode.effects.all())
        causes = list(failure_mode.causes.all())
        evaluations = list(failure_mode.risk_evaluations.all())
        latest = evaluations[0] if evaluations else None
        if not causes:
            rows.append(_worksheet_row(failure_mode, effects, None, latest))
            continue
        for cause in causes:
            rows.append(_worksheet_row(failure_mode, effects, cause, latest))
    return rows


def _worksheet_row(failure_mode, effects, cause, latest):
    result = ""
    result_class = ""
    if latest:
        if "score" in latest.result:
            result = f"RPN {latest.result['score']}"
            result_class = latest.result.get("classification", "")
        elif "priority" in latest.result:
            result = str(latest.result["priority"]).upper()
            result_class = latest.result.get("priority", "")
    return {
        "function": failure_mode.function.name if failure_mode.function else "",
        "requirement": failure_mode.requirement.name if failure_mode.requirement else "",
        "product_characteristics": (
            list(failure_mode.requirement.product_characteristics.all())
            if failure_mode.requirement
            else []
        ),
        "failure_mode": failure_mode,
        "effects": effects,
        "cause": cause,
        "prevention_controls": list(cause.prevention_controls.all()) if cause else [],
        "detection_controls": list(cause.detection_controls.all()) if cause else [],
        "severity": latest.severity if latest else "",
        "occurrence": latest.occurrence if latest else "",
        "detection": latest.detection if latest else "",
        "result": result,
        "result_class": result_class,
    }


def _category_by_id() -> dict[str, models.CauseCategory]:
    return {category.stable_id: category for category in models.CauseCategory.objects.all()}


def _influence_view_model(influence: models.CauseInfluence, category_by_id):
    category = category_by_id.get(influence.cause_category_id or "")
    return {
        "influence": influence,
        "category": category,
        "category_name": category.name if category else "Uncategorized",
        "source_label": _label_for_reference(influence.source_type, influence.source_id),
        "target_label": _label_for_reference(influence.target_type, influence.target_id),
    }


def _ishikawa_groups(influences, category_by_id):
    grouped: dict[str, dict] = {}
    for category in sorted(category_by_id.values(), key=lambda item: (item.sort_order, item.name)):
        grouped[category.stable_id] = {"name": category.name, "items": []}
    grouped[""] = {"name": "Uncategorized", "items": []}

    for influence in influences:
        key = influence.cause_category_id or ""
        if key not in grouped:
            grouped[key] = {"name": "Uncategorized", "items": []}
        grouped[key]["items"].append(_influence_view_model(influence, category_by_id))

    return [group for group in grouped.values() if group["items"]]


def _label_for_reference(reference_type: str, stable_id: str) -> str:
    model_class = {
        "FailureMode": models.FailureMode,
        "FailureCause": models.FailureCause,
        "FailureMechanism": models.FailureMechanism,
        "ProductCharacteristic": models.ProductCharacteristic,
        "ProcessCharacteristic": models.ProcessCharacteristic,
    }.get(reference_type)
    if model_class is None or not stable_id:
        return stable_id
    try:
        return str(model_class.objects.get(stable_id=stable_id))
    except model_class.DoesNotExist:
        return stable_id


def _optional_float(value: str) -> float | None:
    stripped = value.strip()
    if not stripped:
        return None
    return float(stripped)

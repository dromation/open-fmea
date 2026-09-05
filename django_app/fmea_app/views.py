from collections import Counter
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone

from fmea_domain import ActionStatus, CauseInfluenceStatus
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
from .risk_matrix import (
    METHOD_LABELS,
    cell_evaluations,
    grid_rows,
    high_risk_failure_mode_count,
    normalize_method,
    top_evaluations,
    unevaluated_failure_mode_count,
)

RISK_MATRIX_METHOD_CHOICES = list(METHOD_LABELS.items())


def dashboard(request):
    fmeas = FMEA.objects.select_related("project").order_by("name")
    pending_candidate_count = review_models.ImportCandidateRecord.objects.filter(
        review_status=ReviewStatus.UNREVIEWED.value
    ).count()
    pending_row_group_count = review_models.FmeaRowGroup.objects.filter(
        review_status=ReviewStatus.UNREVIEWED.value
    ).count()

    today = timezone.now().date()
    non_terminal_statuses = [
        ActionStatus.OPEN.value,
        ActionStatus.IN_PROGRESS.value,
    ]
    actions_total = models.RecommendedAction.objects.count()
    actions_overdue = models.RecommendedAction.objects.filter(
        due_date__lt=today, status__in=non_terminal_statuses
    ).count()
    actions_due_soon = models.RecommendedAction.objects.filter(
        due_date__gte=today, due_date__lte=today + timedelta(days=7), status__in=non_terminal_statuses
    ).count()

    project_count = FMEAProject.objects.count()
    failure_mode_count = models.FailureMode.objects.count()
    action_count = actions_total

    risk_trend_labels, risk_trend_counts = _risk_evaluation_trend(days=30)

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
            "high_risk_failure_mode_count": high_risk_failure_mode_count(),
            "project_count": project_count,
            "failure_mode_count": failure_mode_count,
            "action_count": action_count,
            "actions_total": actions_total,
            "actions_overdue": actions_overdue,
            "actions_due_soon": actions_due_soon,
            "risk_trend_data": {"labels": risk_trend_labels, "counts": risk_trend_counts},
        },
    )


def _risk_evaluation_trend(days: int) -> tuple[list[str], list[int]]:
    """Daily count of RiskEvaluation rows over the trailing `days` window,
    zero-filled so the chart has a continuous, evenly-spaced x-axis."""
    today = timezone.now().date()
    start = today - timedelta(days=days)

    rows = (
        models.RiskEvaluation.objects.filter(evaluated_at__date__gte=start)
        .annotate(day=TruncDate("evaluated_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    counts_by_day = {row["day"]: row["count"] for row in rows}

    labels: list[str] = []
    counts: list[int] = []
    for offset in range(days + 1):
        day = start + timedelta(days=offset)
        labels.append(day.isoformat())
        counts.append(counts_by_day.get(day, 0))
    return labels, counts


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


def project_list(request):
    projects = FMEAProject.objects.prefetch_related("fmeas").order_by("name")
    status_counts = {
        row["status"]: row["count"]
        for row in FMEAProject.objects.values("status").annotate(count=Count("id"))
    }
    return render(
        request,
        "fmea_app/project_list.html",
        {
            "project_rows": _project_rows(projects),
            "project_form": forms.FMEAProjectForm(),
            "project_count": FMEAProject.objects.count(),
            "active_project_count": status_counts.get("active", 0),
            "on_hold_project_count": status_counts.get("on_hold", 0),
            "completed_project_count": status_counts.get("completed", 0),
        },
    )


def project_detail(request, stable_id: str):
    project = get_object_or_404(FMEAProject, stable_id=stable_id)
    return render(
        request,
        "fmea_app/project_detail.html",
        _project_context(project),
    )


def project_team(request, stable_id: str):
    project = get_object_or_404(FMEAProject, stable_id=stable_id)
    if request.method == "POST":
        action = request.POST.get("action", "").strip()
        if action == "remove":
            membership = get_object_or_404(
                models.ProjectMembership,
                project=project,
                stable_id=request.POST.get("membership_id", ""),
            )
            display_name = _display_user_name(membership.user)
            membership.delete()
            messages.success(request, f"Removed {display_name} from the project team.")
            return redirect("fmea:project_team", stable_id=project.stable_id)

        form = forms.ProjectMembershipForm(request.POST)
        if form.is_valid():
            membership, created = form.save(project=project)
            action_label = "Added" if created else "Updated"
            messages.success(
                request,
                f"{action_label} {_display_user_name(membership.user)} as {membership.get_role_display()}.",
            )
            return redirect("fmea:project_team", stable_id=project.stable_id)

        messages.error(request, _form_errors(form))
        return render(
            request,
            "fmea_app/project_detail.html",
            _project_context(project, membership_form=form, active_section="team"),
        )

    return render(
        request,
        "fmea_app/project_detail.html",
        _project_context(project, active_section="team"),
    )


def engineering_context(request):
    products = (
        models.Product.objects.select_related("fmea")
        .annotate(function_count=Count("functions", distinct=True))
        .order_by("fmea__name", "name")
    )
    processes = (
        models.Process.objects.select_related("fmea")
        .annotate(operation_count=Count("operations", distinct=True))
        .order_by("fmea__name", "name")
    )
    return render(
        request,
        "fmea_app/engineering_context.html",
        {
            "products": products,
            "processes": processes,
        },
    )


def system_list(request):
    systems = (
        models.System.objects.select_related("parent")
        .annotate(
            product_count=Count("products", distinct=True),
            process_count=Count("processes", distinct=True),
        )
        .order_by("parent__name", "name")
    )
    return render(request, "fmea_app/system_list.html", {"systems": systems})


def system_detail(request, stable_id: str):
    system = get_object_or_404(models.System.objects.select_related("parent"), stable_id=stable_id)
    products = models.Product.objects.filter(system=system).select_related("fmea").order_by("name")
    processes = models.Process.objects.filter(system=system).select_related("fmea").order_by("name")
    children = system.children.order_by("name")
    return render(
        request,
        "fmea_app/system_detail.html",
        {
            "system": system,
            "products": products,
            "processes": processes,
            "children": children,
        },
    )


def system_create(request):
    if request.method == "POST":
        form = forms.SystemForm(request.POST)
        if form.is_valid():
            system = form.save()
            messages.success(request, "System created.")
            return redirect("fmea:system_detail", stable_id=system.stable_id)
        messages.error(request, _form_errors(form))
    else:
        form = forms.SystemForm()
    return render(
        request,
        "fmea_app/system_form.html",
        {"form": form, "system": None},
    )


def system_edit(request, stable_id: str):
    system = get_object_or_404(models.System, stable_id=stable_id)
    if request.method == "POST":
        form = forms.SystemForm(request.POST, instance=system)
        if form.is_valid():
            system = form.save()
            messages.success(request, "System updated.")
            return redirect("fmea:system_detail", stable_id=system.stable_id)
        messages.error(request, _form_errors(form))
    else:
        form = forms.SystemForm(instance=system)
    return render(
        request,
        "fmea_app/system_form.html",
        {"form": form, "system": system},
    )


def validation_test_list(request):
    test_type = request.GET.get("test_type", "").strip()
    status = request.GET.get("status", "").strip()
    lifecycle_gate = request.GET.get("lifecycle_gate", "").strip()

    tests = models.ValidationTest.objects.select_related(
        "failure_mode", "failure_mode__fmea", "recommended_action", "owner"
    ).order_by("name")
    if test_type:
        tests = tests.filter(test_type=test_type)
    if status:
        tests = tests.filter(status=status)
    if lifecycle_gate:
        tests = tests.filter(lifecycle_gate=lifecycle_gate)

    return render(
        request,
        "fmea_app/validation_test_list.html",
        {
            "validation_tests": tests,
            "test_type": test_type,
            "status": status,
            "lifecycle_gate": lifecycle_gate,
            "test_type_choices": models.ValidationTest.TEST_TYPE_CHOICES,
            "status_choices": models.ValidationTest.STATUS_CHOICES,
            "lifecycle_gate_choices": models.ValidationTest.LIFECYCLE_GATE_CHOICES,
        },
    )


def new_validation_test(request):
    if request.method == "POST":
        form = forms.ValidationTestForm(request.POST)
        if form.is_valid():
            validation_test = form.save()
            messages.success(request, "Validation test created.")
            return redirect("fmea:validation_test_detail", stable_id=validation_test.stable_id)
        messages.error(request, _form_errors(form))
    else:
        form = forms.ValidationTestForm()
    return render(
        request,
        "fmea_app/validation_test_form.html",
        {"form": form},
    )


def validation_test_detail(request, stable_id: str):
    validation_test = get_object_or_404(
        models.ValidationTest.objects.select_related(
            "failure_mode", "failure_mode__fmea", "recommended_action", "owner"
        ),
        stable_id=stable_id,
    )
    return render(
        request,
        "fmea_app/validation_test_detail.html",
        {"validation_test": validation_test},
    )


def _latest_risk_result(failure_mode):
    # Reuses the same "latest RiskEvaluation" read _worksheet_row already
    # performs, without modifying or forking _build_worksheet_rows/
    # _worksheet_row themselves (Decision 6, Slice G).
    evaluations = list(failure_mode.risk_evaluations.all())
    if not evaluations:
        return {"severity": "", "occurrence": "", "detection": "", "result": "", "result_class": ""}
    latest = evaluations[0]
    result = ""
    result_class = ""
    if "score" in latest.result:
        result = f"RPN {latest.result['score']}"
        result_class = latest.result.get("classification", "")
    elif "priority" in latest.result:
        result = str(latest.result["priority"]).upper()
        result_class = latest.result.get("priority", "")
    return {
        "severity": latest.severity,
        "occurrence": latest.occurrence,
        "detection": latest.detection,
        "result": result,
        "result_class": result_class,
    }


def failure_mode_list(request):
    failure_modes = models.FailureMode.objects.select_related(
        "fmea", "function", "requirement"
    ).order_by("fmea__name", "name")
    rows = [
        {
            "failure_mode": fm,
            "function_or_requirement": fm.function.name if fm.function else (fm.requirement.name if fm.requirement else ""),
            "risk": _latest_risk_result(fm),
            "effects_count": fm.effects.count(),
            "causes_count": fm.causes.count(),
            "actions_count": fm.recommended_actions.count(),
        }
        for fm in failure_modes
    ]
    return render(request, "fmea_app/failure_mode_list.html", {"rows": rows})


def failure_cause_list(request):
    causes = models.FailureCause.objects.select_related(
        "failure_mode", "failure_mode__fmea"
    ).order_by("failure_mode__fmea__name", "failure_mode__name", "name")
    rows = [
        {
            "cause": cause,
            "prevention_controls_count": cause.prevention_controls.count(),
            "detection_controls_count": cause.detection_controls.count(),
            "actions_count": cause.recommended_actions.count(),
        }
        for cause in causes
    ]
    return render(request, "fmea_app/failure_cause_list.html", {"rows": rows})


def failure_effect_list(request):
    effects = models.FailureEffect.objects.select_related(
        "failure_mode", "failure_mode__fmea"
    ).order_by("failure_mode__fmea__name", "failure_mode__name", "name")
    return render(request, "fmea_app/failure_effect_list.html", {"effects": effects})


def prevention_control_list(request):
    controls = models.PreventionControl.objects.select_related(
        "failure_cause", "failure_cause__failure_mode", "failure_cause__failure_mode__fmea"
    ).order_by(
        "failure_cause__failure_mode__fmea__name",
        "failure_cause__failure_mode__name",
        "failure_cause__name",
        "name",
    )
    return render(request, "fmea_app/prevention_control_list.html", {"controls": controls})


def detection_control_list(request):
    controls = models.DetectionControl.objects.select_related(
        "failure_cause", "failure_cause__failure_mode", "failure_cause__failure_mode__fmea"
    ).order_by(
        "failure_cause__failure_mode__fmea__name",
        "failure_cause__failure_mode__name",
        "failure_cause__name",
        "name",
    )
    return render(request, "fmea_app/detection_control_list.html", {"controls": controls})


def action_list(request):
    status_filter = request.GET.get("status", "").strip()
    actions = models.RecommendedAction.objects.select_related(
        "failure_mode__fmea", "failure_cause__failure_mode__fmea", "responsible_role"
    ).order_by("-due_date", "name")
    if status_filter:
        actions = actions.filter(status=status_filter)

    rows = []
    for action in actions:
        if action.failure_mode:
            fmea = action.failure_mode.fmea
            linked_label = f"Failure Mode: {action.failure_mode.name}"
        elif action.failure_cause:
            fmea = action.failure_cause.failure_mode.fmea
            linked_label = f"Cause: {action.failure_cause.name}"
        else:
            fmea = None
            linked_label = ""
        rows.append({"action": action, "fmea": fmea, "linked_label": linked_label})

    return render(
        request,
        "fmea_app/action_list.html",
        {
            "rows": rows,
            "status_choices": models.RecommendedAction.STATUS_CHOICES,
            "status_filter": status_filter,
        },
    )


_CLOSED_ACTION_STATUSES = ("completed", "verified", "cancelled")


def _worksheet_row_action_counts(row: dict) -> tuple[int, int]:
    if row["cause"] is not None:
        actions = list(row["cause"].recommended_actions.all())
    else:
        actions = list(row["failure_mode"].recommended_actions.all())
    today = timezone.now().date()
    open_count = len(actions)
    overdue_count = sum(
        1
        for action in actions
        if action.due_date
        and action.due_date < today
        and action.status not in _CLOSED_ACTION_STATUSES
    )
    return open_count, overdue_count


def _cross_fmea_worksheet_rows(fmeas):
    rows = []
    for fmea in fmeas:
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
        for row in _build_worksheet_rows(failure_modes):
            row["fmea"] = fmea
            row["actions_open"], row["actions_overdue"] = _worksheet_row_action_counts(row)
            rows.append(row)
    return rows


def dfmea_worksheet(request):
    fmeas = FMEA.objects.exclude(fmea_type="process").order_by("name")
    return render(
        request,
        "fmea_app/dfmea_worksheet.html",
        {"rows": _cross_fmea_worksheet_rows(fmeas)},
    )


def pfmea_worksheet(request):
    fmeas = FMEA.objects.filter(fmea_type="process").order_by("name")
    return render(
        request,
        "fmea_app/pfmea_worksheet.html",
        {"rows": _cross_fmea_worksheet_rows(fmeas)},
    )


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
    processes = fmea.processes.prefetch_related("operations").order_by("name")
    functions = models.Function.objects.filter(
        Q(product__fmea=fmea) | Q(operation__process__fmea=fmea)
    ).select_related("product", "operation").order_by("name")
    return render(
        request,
        "fmea_app/fmea_detail.html",
        {
            "fmea": fmea,
            "failure_modes": failure_modes,
            "worksheet_rows": worksheet_rows,
            "processes": processes,
            "functions": functions,
            "function_form": forms.FunctionForm(fmea=fmea),
            "failure_mode_form": forms.FailureModeForm(fmea=fmea),
            "effect_form": forms.FailureEffectForm(),
            "cause_form": forms.FailureCauseForm(),
            "prevention_form": forms.PreventionControlForm(),
            "detection_form": forms.DetectionControlForm(),
            "risk_form": forms.RiskEvaluationForm(),
            "action_form": forms.RecommendedActionForm(),
        },
    )


@require_POST
def add_failure_mode(request, stable_id: str):
    fmea = get_fmea_by_stable_id(stable_id)
    form = forms.FailureModeForm(request.POST, fmea=fmea)
    if form.is_valid():
        failure_mode = form.save(commit=False)
        failure_mode.fmea = fmea
        failure_mode.save()
        messages.success(request, "Failure mode added.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=fmea.stable_id)


@require_POST
def add_function(request, stable_id: str):
    fmea = get_fmea_by_stable_id(stable_id)
    form = forms.FunctionForm(request.POST, fmea=fmea)
    if form.is_valid():
        form.save()
        messages.success(request, "Function added.")
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
def add_action_to_cause(request, stable_id: str):
    cause = get_object_or_404(FailureCause, stable_id=stable_id)
    form = forms.RecommendedActionForm(request.POST)
    if form.is_valid():
        action = form.save(commit=False)
        action.failure_cause = cause
        action.failure_mode = None
        action.save()
        messages.success(request, "Action added.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=cause.failure_mode.fmea.stable_id)


@require_POST
def add_action_to_failure_mode(request, stable_id: str):
    failure_mode = get_object_or_404(FailureMode, stable_id=stable_id)
    form = forms.RecommendedActionForm(request.POST)
    if form.is_valid():
        action = form.save(commit=False)
        action.failure_mode = failure_mode
        action.failure_cause = None
        action.save()
        messages.success(request, "Action added.")
    else:
        messages.error(request, _form_errors(form))
    return redirect("fmea:fmea_detail", stable_id=failure_mode.fmea.stable_id)


def action_detail(request, stable_id: str):
    action = get_object_or_404(
        models.RecommendedAction.objects.select_related(
            "failure_mode__fmea",
            "failure_cause__failure_mode__fmea",
            "responsible_role",
        ),
        stable_id=stable_id,
    )
    return render(
        request,
        "fmea_app/action_detail.html",
        {"action": action},
    )


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
            lifecycle_gate=form.cleaned_data.get("lifecycle_gate") or "current",
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
    control_type_filter = request.GET.get("control_type", "").strip()
    status_filter = request.GET.get("status", "").strip()

    process_characteristics = models.ProcessCharacteristic.objects.select_related(
        "operation",
        "operation__process",
        "owner",
    ).order_by("operation__process__name", "operation__sequence", "operation__name", "name")
    if control_type_filter:
        process_characteristics = process_characteristics.filter(control_type=control_type_filter)
    if status_filter:
        process_characteristics = process_characteristics.filter(status=status_filter)

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
            "control_type_choices": models.ControlType.choices,
            "status_choices": models.ControlStatus.choices,
            "control_type_filter": control_type_filter,
            "status_filter": status_filter,
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


def process_flow(request, stable_id: str):
    process = get_object_or_404(models.Process.objects.select_related("fmea"), stable_id=stable_id)
    operations = list(process.operations.order_by("sequence", "name"))

    selected_operation_id = request.GET.get("operation_id", "").strip()
    selected_operation = None
    if selected_operation_id:
        selected_operation = next(
            (operation for operation in operations if operation.stable_id == selected_operation_id),
            None,
        )
    if selected_operation is None and operations:
        selected_operation = operations[0]

    process_characteristics = []
    linked_product_characteristics = []
    if selected_operation is not None:
        category_by_id = _category_by_id()
        characteristics = list(
            models.ProcessCharacteristic.objects.filter(operation=selected_operation).order_by("name")
        )
        process_characteristics = [
            {
                "item": characteristic,
                "category_name": (
                    category_by_id[characteristic.cause_category_id].name
                    if characteristic.cause_category_id in category_by_id
                    else "Uncategorized"
                ),
                "attribute_items": sorted((characteristic.attributes or {}).items()),
            }
            for characteristic in characteristics
        ]

        source_ids = [characteristic.stable_id for characteristic in characteristics]
        influences = list(
            models.CauseInfluence.objects.filter(
                source_type="ProcessCharacteristic",
                source_id__in=source_ids,
                target_type="ProductCharacteristic",
            ).order_by("target_id", "status")
        )
        product_characteristic_by_id = {
            item.stable_id: item
            for item in models.ProductCharacteristic.objects.filter(
                stable_id__in=[influence.target_id for influence in influences]
            )
        }
        linked_product_characteristics = [
            {
                "influence": influence,
                "product_characteristic": product_characteristic_by_id.get(influence.target_id),
                "source_label": _label_for_reference(influence.source_type, influence.source_id),
            }
            for influence in influences
        ]

    return render(
        request,
        "fmea_app/process_flow.html",
        {
            "process": process,
            "operations": operations,
            "selected_operation": selected_operation,
            "process_characteristics": process_characteristics,
            "linked_product_characteristics": linked_product_characteristics,
        },
    )


def risk_matrix(request):
    method = normalize_method(request.GET.get("method"))
    return render(
        request,
        "fmea_app/risk_matrix.html",
        {
            "method": method,
            "methods": RISK_MATRIX_METHOD_CHOICES,
            "grid_rows": grid_rows(method),
            "unevaluated_count": unevaluated_failure_mode_count(method),
        },
    )


def risk_matrix_cell(request):
    method = normalize_method(request.GET.get("method"))
    severity = _optional_int(request.GET.get("severity"))
    occurrence = _optional_int(request.GET.get("occurrence"))
    evaluations = (
        cell_evaluations(method, severity, occurrence)
        if severity is not None and occurrence is not None
        else []
    )
    return render(
        request,
        "fmea_app/risk_matrix_cell.html",
        {
            "method": method,
            "method_label": METHOD_LABELS.get(method, method),
            "methods": RISK_MATRIX_METHOD_CHOICES,
            "severity": severity,
            "occurrence": occurrence,
            "evaluations": evaluations,
        },
    )


def risk_matrix_top(request):
    method = normalize_method(request.GET.get("method"))
    return render(
        request,
        "fmea_app/risk_matrix_top.html",
        {
            "method": method,
            "method_label": METHOD_LABELS.get(method, method),
            "methods": RISK_MATRIX_METHOD_CHOICES,
            "evaluations": top_evaluations(method),
        },
    )


def risk_trajectory_index(request):
    failure_modes = (
        FailureMode.objects.filter(risk_evaluations__isnull=False)
        .select_related("fmea")
        .annotate(evaluation_count=Count("risk_evaluations", distinct=True))
        .distinct()
        .order_by("fmea__name", "name")
    )
    return render(
        request,
        "fmea_app/risk_trajectory_index.html",
        {"failure_modes": failure_modes},
    )


def risk_trajectory(request, stable_id: str):
    failure_mode = get_object_or_404(FailureMode.objects.select_related("fmea"), stable_id=stable_id)
    evaluations = failure_mode.risk_evaluations.order_by("evaluated_at", "id")
    return render(
        request,
        "fmea_app/risk_trajectory.html",
        {"failure_mode": failure_mode, "evaluations": evaluations},
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


def _project_context(
    project: FMEAProject,
    *,
    membership_form: forms.ProjectMembershipForm | None = None,
    active_section: str = "overview",
) -> dict:
    fmeas = list(
        project.fmeas.prefetch_related("products", "processes").order_by("name")
    )
    return {
        "project": project,
        "project_row": _project_row(project),
        "fmea_rows": _fmea_rows(fmeas),
        "related_products": models.Product.objects.filter(fmea__project=project)
        .order_by("name")
        .distinct(),
        "related_processes": models.Process.objects.filter(fmea__project=project)
        .order_by("name")
        .distinct(),
        "memberships": project.memberships.select_related("user").order_by(
            "role",
            "user__last_name",
            "user__first_name",
            "user__email",
        ),
        "membership_form": membership_form or forms.ProjectMembershipForm(),
        "active_section": active_section,
    }


def _project_rows(projects) -> list[dict]:
    return [_project_row(project) for project in projects]


def _project_row(project: FMEAProject) -> dict:
    fmeas = list(project.fmeas.all())
    last_updated = project.updated_at
    if fmeas:
        last_updated = max([last_updated, *(fmea.updated_at for fmea in fmeas)])
    return {
        "project": project,
        "fmea_count": len(fmeas),
        "type_breakdown": _fmea_type_breakdown(fmeas),
        "last_updated": last_updated,
    }


def _fmea_rows(fmeas) -> list[dict]:
    return [
        {
            "fmea": fmea,
            "products": list(fmea.products.all()),
            "processes": list(fmea.processes.all()),
        }
        for fmea in fmeas
    ]


def _fmea_type_breakdown(fmeas) -> str:
    counts = Counter(fmea.fmea_type for fmea in fmeas)
    type_labels = dict(FMEA.FMEA_TYPE_CHOICES)
    return ", ".join(
        f"{type_labels.get(fmea_type, fmea_type)}: {count}"
        for fmea_type, count in sorted(counts.items())
    )


def _display_user_name(user) -> str:
    full_name = user.get_full_name().strip()
    return full_name or user.email or user.username


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


def _optional_int(value: str | None) -> int | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return int(stripped)
    except ValueError:
        return None



def change_list(request):
    change_type = request.GET.get("change_type", "").strip()
    impact_level = request.GET.get("impact_level", "").strip()
    status = request.GET.get("status", "").strip()

    changes = models.Change.objects.select_related("owner").order_by("title")
    if change_type:
        changes = changes.filter(change_type=change_type)
    if impact_level:
        changes = changes.filter(impact_level=impact_level)
    if status:
        changes = changes.filter(status=status)

    return render(
        request,
        "fmea_app/change_list.html",
        {
            "changes": changes,
            "change_type": change_type,
            "impact_level": impact_level,
            "status": status,
            "change_type_choices": models.Change.CHANGE_TYPE_CHOICES,
            "impact_level_choices": models.Change.IMPACT_LEVEL_CHOICES,
            "status_choices": models.Change.STATUS_CHOICES,
        },
    )


def new_change(request):
    if request.method == "POST":
        form = forms.ChangeForm(request.POST)
        if form.is_valid():
            change = form.save()
            messages.success(request, "Change created.")
            return redirect("fmea:change_detail", stable_id=change.stable_id)
        messages.error(request, _form_errors(form))
    else:
        form = forms.ChangeForm()
    return render(
        request,
        "fmea_app/change_form.html",
        {"form": form, "change": None},
    )


def edit_change(request, stable_id: str):
    change = get_object_or_404(models.Change, stable_id=stable_id)
    if request.method == "POST":
        form = forms.ChangeForm(request.POST, instance=change)
        if form.is_valid():
            change = form.save()
            messages.success(request, "Change updated.")
            return redirect("fmea:change_detail", stable_id=change.stable_id)
        messages.error(request, _form_errors(form))
    else:
        form = forms.ChangeForm(instance=change)
    return render(
        request,
        "fmea_app/change_form.html",
        {"form": form, "change": change},
    )


def _fmea_type_label(fmea) -> str:
    if fmea.fmea_type == "design":
        return "DFMEA"
    if fmea.fmea_type == "process":
        return "PFMEA"
    return fmea.get_fmea_type_display()


def change_detail(request, stable_id: str):
    change = get_object_or_404(
        models.Change.objects.select_related("owner"),
        stable_id=stable_id,
    )
    failure_modes = change.affected_failure_modes.select_related("fmea").order_by("fmea__name", "name")
    affected_rows = [
        {"failure_mode": failure_mode, "fmea_type_label": _fmea_type_label(failure_mode.fmea)}
        for failure_mode in failure_modes
    ]
    return render(
        request,
        "fmea_app/change_detail.html",
        {
            "change": change,
            "affected_rows": affected_rows,
            "affected_count": len(affected_rows),
        },
    )


def characteristic_link_list(request):
    relationship_type = request.GET.get("relationship_type", "").strip()
    characteristic_id = request.GET.get("characteristic", "").strip()

    links = models.CharacteristicLink.objects.select_related(
        "from_characteristic", "to_characteristic"
    ).order_by("from_characteristic__name", "to_characteristic__name")
    if relationship_type:
        links = links.filter(relationship_type=relationship_type)
    if characteristic_id:
        links = links.filter(
            Q(from_characteristic__pk=characteristic_id) | Q(to_characteristic__pk=characteristic_id)
        )

    return render(
        request,
        "fmea_app/characteristic_link_list.html",
        {
            "links": links,
            "relationship_type": relationship_type,
            "characteristic_id": characteristic_id,
            "relationship_type_choices": models.CharacteristicLink.RELATIONSHIP_TYPE_CHOICES,
            "characteristics": models.ProductCharacteristic.objects.order_by("name"),
        },
    )


def characteristic_link_create(request):
    if request.method == "POST":
        form = forms.CharacteristicLinkForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Characteristic link created.")
            return redirect("fmea:characteristic_link_list")
        messages.error(request, _form_errors(form))
    else:
        form = forms.CharacteristicLinkForm()
    return render(
        request,
        "fmea_app/characteristic_link_form.html",
        {"form": form},
    )


@require_POST
def characteristic_link_delete(request, stable_id: str):
    link = get_object_or_404(models.CharacteristicLink, stable_id=stable_id)
    link.delete()
    messages.success(request, "Characteristic link deleted.")
    return redirect("fmea:characteristic_link_list")

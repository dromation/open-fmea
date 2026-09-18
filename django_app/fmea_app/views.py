from collections import Counter
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
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
    AIAG_VDA_AP_METHOD,
    AIAG_VDA_MSR_METHOD,
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


def asset_list(request):
    assets = models.Asset.objects.annotate(
        failure_mode_count=Count("failure_modes", distinct=True),
    ).order_by("name")
    return render(request, "fmea_app/asset_list.html", {"assets": assets})


def asset_detail(request, stable_id: str):
    asset = get_object_or_404(models.Asset, stable_id=stable_id)
    failure_modes = models.FailureMode.objects.filter(asset=asset).select_related("fmea").order_by("name")
    return render(
        request,
        "fmea_app/asset_detail.html",
        {"asset": asset, "failure_modes": failure_modes},
    )


def asset_create(request):
    if request.method == "POST":
        form = forms.AssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            messages.success(request, "Asset created.")
            return redirect("fmea:asset_detail", stable_id=asset.stable_id)
        messages.error(request, _form_errors(form))
    else:
        form = forms.AssetForm()
    return render(request, "fmea_app/asset_form.html", {"form": form, "asset": None})


def asset_edit(request, stable_id: str):
    asset = get_object_or_404(models.Asset, stable_id=stable_id)
    if request.method == "POST":
        form = forms.AssetForm(request.POST, instance=asset)
        if form.is_valid():
            asset = form.save()
            messages.success(request, "Asset updated.")
            return redirect("fmea:asset_detail", stable_id=asset.stable_id)
        messages.error(request, _form_errors(form))
    else:
        form = forms.AssetForm(instance=asset)
    return render(request, "fmea_app/asset_form.html", {"form": form, "asset": asset})


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


FAILURE_MODE_DETAIL_TABS = ("general", "effects", "causes", "actions", "risk")

RISK_LEVEL_CHOICES = [
    ("not_evaluated", "Not Evaluated"),
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High/Critical"),
]

HAS_ACTION_CHOICES = [("yes", "Yes"), ("no", "No")]


def _failure_mode_actions(fm):
    """Direct actions (unchanged query, matches the flat table's own
    'Actions (direct)' column) and actions reachable via any of this
    failure mode's causes - the two paths Decision 3/Section 3 of the
    Slice O instruction requires to agree by construction wherever either
    is used (KPI tile, filter, Actions tab)."""
    direct = list(fm.recommended_actions.all())
    via_cause = list(models.RecommendedAction.objects.filter(failure_cause__in=fm.causes.all()))
    return direct, via_cause


def _risk_result_for_evaluation(evaluation) -> dict:
    # Same trivial "read the already-stored classification/priority key"
    # extraction _latest_risk_result performs for its one latest row - no
    # RPN/priority threshold is recomputed here, only the stored
    # RiskEvaluation.result JSON is formatted, exactly like _latest_risk_result
    # already does (Decision 3, Slice O: "not a new scoring path").
    result = ""
    result_class = ""
    if "score" in evaluation.result:
        result = f"RPN {evaluation.result['score']}"
        result_class = evaluation.result.get("classification", "")
    elif "priority" in evaluation.result:
        result = str(evaluation.result["priority"]).upper()
        result_class = evaluation.result.get("priority", "")
    return {
        "evaluation": evaluation,
        "severity": evaluation.severity,
        "occurrence": evaluation.occurrence,
        "detection": evaluation.detection,
        "result": result,
        "result_class": result_class,
    }


def failure_mode_list(request):
    fmea_filter = request.GET.get("fmea", "").strip()
    risk_level_filter = request.GET.get("risk_level", "").strip()
    has_action_filter = request.GET.get("has_action", "").strip()

    failure_modes_qs = models.FailureMode.objects.select_related(
        "fmea", "function", "requirement"
    ).order_by("fmea__name", "name")
    if fmea_filter:
        failure_modes_qs = failure_modes_qs.filter(fmea__stable_id=fmea_filter)

    rows = []
    for fm in failure_modes_qs:
        risk = _latest_risk_result(fm)
        risk_bucket = risk["result_class"] if risk["result"] else "not_evaluated"
        direct_actions, via_cause_actions = _failure_mode_actions(fm)
        has_action = bool(direct_actions or via_cause_actions)
        rows.append(
            {
                "failure_mode": fm,
                "function_or_requirement": fm.function.name if fm.function else (fm.requirement.name if fm.requirement else ""),
                "risk": risk,
                "risk_bucket": risk_bucket,
                "effects_count": fm.effects.count(),
                "causes_count": fm.causes.count(),
                "actions_count": fm.recommended_actions.count(),
                "has_action": has_action,
            }
        )

    if risk_level_filter:
        rows = [row for row in rows if row["risk_bucket"] == risk_level_filter]
    if has_action_filter:
        wanted = has_action_filter == "yes"
        rows = [row for row in rows if row["has_action"] == wanted]

    total_count = len(rows)
    not_evaluated_count = sum(1 for row in rows if row["risk_bucket"] == "not_evaluated")
    high_critical_count = sum(1 for row in rows if row["risk_bucket"] == "high")
    no_cause_count = sum(1 for row in rows if row["causes_count"] == 0)
    no_action_count = sum(1 for row in rows if not row["has_action"])
    zero_effects_count = sum(1 for row in rows if row["effects_count"] == 0)

    risk_bucket_labels = dict(RISK_LEVEL_CHOICES)
    risk_bucket_counts = Counter(row["risk_bucket"] for row in rows)

    fmea_choices = [(fmea.stable_id, fmea.name) for fmea in models.FMEA.objects.order_by("name")]

    filter_params = {"fmea": fmea_filter, "risk_level": risk_level_filter, "has_action": has_action_filter}
    filter_querystring = urlencode({key: value for key, value in filter_params.items() if value})
    query_prefix = f"?{filter_querystring}&" if filter_querystring else "?"

    selected_id = request.GET.get("selected", "").strip()
    selected_failure_mode = None
    if selected_id:
        selected_failure_mode = get_object_or_404(
            models.FailureMode.objects.select_related("fmea", "function", "requirement"),
            stable_id=selected_id,
        )

    active_tab = request.GET.get("tab", "general").strip().lower()
    if active_tab not in FAILURE_MODE_DETAIL_TABS:
        active_tab = "general"

    selected_effects = []
    selected_causes = []
    selected_direct_actions = []
    selected_via_cause_actions = []
    selected_total_actions_count = 0
    selected_risk_history = []
    if selected_failure_mode is not None:
        selected_effects = list(selected_failure_mode.effects.all())
        selected_causes = list(selected_failure_mode.causes.all())
        selected_direct_actions, selected_via_cause_actions = _failure_mode_actions(selected_failure_mode)
        selected_total_actions_count = len(selected_direct_actions) + len(selected_via_cause_actions)
        selected_risk_history = [
            _risk_result_for_evaluation(evaluation)
            for evaluation in selected_failure_mode.risk_evaluations.all()
        ]

    return render(
        request,
        "fmea_app/failure_mode_list.html",
        {
            "rows": rows,
            "kpi_total": total_count,
            "kpi_not_evaluated": not_evaluated_count,
            "kpi_high_critical": high_critical_count,
            "kpi_no_cause": no_cause_count,
            "kpi_no_action": no_action_count,
            "risk_chart_data": {
                "labels": [risk_bucket_labels.get(key, key) for key in risk_bucket_counts.keys()],
                "counts": list(risk_bucket_counts.values()),
            },
            "coverage_zero_causes": no_cause_count,
            "coverage_zero_effects": zero_effects_count,
            "coverage_zero_actions": no_action_count,
            "coverage_zero_risk_evaluations": not_evaluated_count,
            "fmea_choices": fmea_choices,
            "risk_level_choices": RISK_LEVEL_CHOICES,
            "has_action_choices": HAS_ACTION_CHOICES,
            "fmea_filter": fmea_filter,
            "risk_level_filter": risk_level_filter,
            "has_action_filter": has_action_filter,
            "query_prefix": query_prefix,
            "selected_failure_mode": selected_failure_mode,
            "selected_effects": selected_effects,
            "selected_causes": selected_causes,
            "selected_direct_actions": selected_direct_actions,
            "selected_via_cause_actions": selected_via_cause_actions,
            "selected_total_actions_count": selected_total_actions_count,
            "selected_risk_history": selected_risk_history,
            "active_tab": active_tab,
            "detail_tabs": FAILURE_MODE_DETAIL_TABS,
        },
    )


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
            fmea.failure_modes.select_related("function", "requirement", "asset")
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
    fmeas = FMEA.objects.exclude(fmea_type__in=["process", "preventive"]).order_by("name")
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


def pmfmea_worksheet(request):
    fmeas = FMEA.objects.filter(fmea_type="preventive").order_by("name")
    return render(
        request,
        "fmea_app/pmfmea_worksheet.html",
        {"rows": _cross_fmea_worksheet_rows(fmeas)},
    )


def fmea_detail(request, stable_id: str):
    fmea = get_fmea_by_stable_id(stable_id)
    failure_modes = (
        fmea.failure_modes.select_related("function", "requirement", "asset")
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
    aiag_vda_perspective = "pfmea" if fmea.fmea_type == "process" else "dfmea"
    aiag_vda_definition = models.EvaluationDefinition.objects.filter(method=AIAG_VDA_AP_METHOD).first()
    aiag_vda_rating_scales = (
        (aiag_vda_definition.rating_scales or {}).get(aiag_vda_perspective) if aiag_vda_definition else None
    )
    aiag_vda_msr_definition = models.EvaluationDefinition.objects.filter(method=AIAG_VDA_MSR_METHOD).first()
    aiag_vda_msr_rating_scales = aiag_vda_msr_definition.rating_scales if aiag_vda_msr_definition else None
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
            "aiag_vda_perspective": aiag_vda_perspective,
            "aiag_vda_rating_scales": aiag_vda_rating_scales,
            "aiag_vda_msr_rating_scales": aiag_vda_msr_rating_scales,
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
            failure_scenario=form.cleaned_data.get("failure_scenario") or "",
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


PROCESS_CHARACTERISTIC_DETAIL_TABS = ("general", "method", "reaction", "links", "history")

CONTROL_TYPE_RESULT_TEXT = {
    "administrative": "Confirms the administrative procedure was followed as documented.",
    "measurement": "Confirms the measured value falls within the specified tolerance.",
    "detection": "Confirms the defect or condition being screened for was not detected.",
    "monitoring": "Confirms the monitored parameter stayed within its expected range.",
    "poka_yoke": "Confirms the error-proofing device prevented the incorrect condition.",
    "test": "Confirms the test outcome met the defined acceptance criteria.",
}


def process_characteristic_list(request):
    control_type_filter = request.GET.get("control_type", "").strip()
    status_filter = request.GET.get("status", "").strip()

    process_characteristics_qs = models.ProcessCharacteristic.objects.select_related(
        "operation",
        "operation__process",
        "operation__process__fmea",
        "owner",
        "special_classification",
    ).order_by("operation__process__name", "operation__sequence", "operation__name", "name")
    if control_type_filter:
        process_characteristics_qs = process_characteristics_qs.filter(control_type=control_type_filter)
    if status_filter:
        process_characteristics_qs = process_characteristics_qs.filter(status=status_filter)

    process_characteristics = list(process_characteristics_qs)
    category_by_id = _category_by_id()

    not_effective = models.ControlEffectiveness.NOT_EFFECTIVE
    active_status = models.ControlStatus.ACTIVE
    review_status = models.ControlStatus.REVIEW

    total_count = len(process_characteristics)
    active_count = sum(1 for item in process_characteristics if item.status == active_status)
    not_effective_count = sum(1 for item in process_characteristics if item.effectiveness == not_effective)
    needs_review_count = sum(1 for item in process_characteristics if item.status == review_status)
    no_reaction_plan_count = sum(1 for item in process_characteristics if not (item.reaction_plan or "").strip())
    linked_items = [item for item in process_characteristics if _is_linked_to_pfmea(item)]
    linked_count = len(linked_items)

    control_type_counts = Counter(
        item.get_control_type_display() if item.control_type else "Unspecified"
        for item in process_characteristics
    )
    effectiveness_counts = Counter(item.get_effectiveness_display() for item in process_characteristics)

    top_pfmea_links = _top_pfmea_links(linked_items)

    filter_params = {"control_type": control_type_filter, "status": status_filter}
    filter_querystring = urlencode({key: value for key, value in filter_params.items() if value})
    query_prefix = f"?{filter_querystring}&" if filter_querystring else "?"

    selected_id = request.GET.get("selected", "").strip()
    selected_characteristic = None
    if selected_id:
        selected_characteristic = get_object_or_404(
            models.ProcessCharacteristic.objects.select_related(
                "operation", "operation__process", "operation__process__fmea", "owner", "special_classification"
            ),
            stable_id=selected_id,
        )

    active_tab = request.GET.get("tab", "general").strip().lower()
    if active_tab not in PROCESS_CHARACTERISTIC_DETAIL_TABS:
        active_tab = "general"

    selected_category_name = None
    selected_linked_fmea = None
    flow_result_text = None
    if selected_characteristic is not None:
        selected_category_name = (
            category_by_id[selected_characteristic.cause_category_id].name
            if selected_characteristic.cause_category_id in category_by_id
            else "Uncategorized"
        )
        if _is_linked_to_pfmea(selected_characteristic):
            selected_linked_fmea = selected_characteristic.operation.process.fmea
        flow_result_text = _process_control_flow_result_text(selected_characteristic)

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
                    "linked_to_pfmea": _is_linked_to_pfmea(item),
                }
                for item in process_characteristics
            ],
            "control_type_choices": models.ControlType.choices,
            "status_choices": models.ControlStatus.choices,
            "control_type_filter": control_type_filter,
            "status_filter": status_filter,
            "query_prefix": query_prefix,
            "kpi_total": total_count,
            "kpi_active": active_count,
            "kpi_not_effective": not_effective_count,
            "kpi_needs_review": needs_review_count,
            "kpi_no_reaction_plan": no_reaction_plan_count,
            "kpi_linked": linked_count,
            "control_type_chart_data": {
                "labels": list(control_type_counts.keys()),
                "counts": list(control_type_counts.values()),
            },
            "effectiveness_chart_data": {
                "labels": list(effectiveness_counts.keys()),
                "counts": list(effectiveness_counts.values()),
            },
            "top_pfmea_links": top_pfmea_links,
            "selected_characteristic": selected_characteristic,
            "selected_category_name": selected_category_name,
            "selected_linked_fmea": selected_linked_fmea,
            "flow_result_text": flow_result_text,
            "active_tab": active_tab,
            "detail_tabs": PROCESS_CHARACTERISTIC_DETAIL_TABS,
        },
    )


def _is_linked_to_pfmea(characteristic) -> bool:
    return characteristic.operation.process.fmea.fmea_type == "process"


def _top_pfmea_links(linked_items) -> list[dict]:
    entries: dict[str, dict] = {}
    for item in linked_items:
        fmea = item.operation.process.fmea
        entry = entries.setdefault(fmea.stable_id, {"fmea": fmea, "count": 0})
        entry["count"] += 1
    return sorted(entries.values(), key=lambda entry: (-entry["count"], entry["fmea"].name))


def _process_control_flow_result_text(characteristic) -> str:
    base_text = CONTROL_TYPE_RESULT_TEXT.get(
        characteristic.control_type,
        "Confirms the control's defined check was satisfied.",
    )
    if characteristic.method:
        return f"{base_text} (Method: {characteristic.method})"
    return base_text


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
        models.ProcessCharacteristic.objects.select_related(
            "operation", "operation__process", "special_classification"
        ),
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
    category_filter = request.GET.get("category", "").strip()
    system_filter = request.GET.get("system", "").strip()
    view_filter = request.GET.get("view", "").strip()

    characteristics_qs = models.ProductCharacteristic.objects.select_related(
        "primary_classification",
        "requirement",
        "requirement__function",
        "requirement__function__product",
        "requirement__function__product__system",
        "requirement__function__operation",
        "requirement__function__operation__process",
        "requirement__function__operation__process__system",
    ).annotate(
        outgoing_link_count=Count("outgoing_links", distinct=True),
        incoming_link_count=Count("incoming_links", distinct=True),
    )
    if category_filter:
        characteristics_qs = characteristics_qs.filter(primary_classification__stable_id=category_filter)
    if system_filter:
        characteristics_qs = characteristics_qs.filter(
            Q(requirement__function__product__system__stable_id=system_filter)
            | Q(requirement__function__operation__process__system__stable_id=system_filter)
        )

    # One shared definition of "links_count" (and therefore of Linked/Unlinked)
    # reused by the view filter, the Coverage Summary counts, and the Unlinked
    # Characteristics panel below - never recomputed independently.
    category_system_scoped = list(characteristics_qs)
    for characteristic in category_system_scoped:
        characteristic.links_count = characteristic.outgoing_link_count + characteristic.incoming_link_count
    category_system_scoped_ids = [characteristic.pk for characteristic in category_system_scoped]

    view_scoped = category_system_scoped
    if view_filter == "linked-only":
        view_scoped = [c for c in category_system_scoped if c.links_count > 0]
    elif view_filter == "unlinked-only":
        view_scoped = [c for c in category_system_scoped if c.links_count == 0]
    view_scoped_ids = [characteristic.pk for characteristic in view_scoped]

    links = models.CharacteristicLink.objects.select_related(
        "from_characteristic",
        "from_characteristic__primary_classification",
        "to_characteristic",
        "to_characteristic__primary_classification",
    ).order_by("from_characteristic__name", "to_characteristic__name")
    if relationship_type:
        links = links.filter(relationship_type=relationship_type)
    if characteristic_id:
        links = links.filter(
            Q(from_characteristic__pk=characteristic_id) | Q(to_characteristic__pk=characteristic_id)
        )
    if category_filter or system_filter:
        links = links.filter(
            Q(from_characteristic__pk__in=category_system_scoped_ids)
            | Q(to_characteristic__pk__in=category_system_scoped_ids)
        )

    total_in_view = len(view_scoped)
    linked_in_view = sum(1 for c in view_scoped if c.links_count > 0)
    unlinked_in_view = sum(1 for c in view_scoped if c.links_count == 0)
    total_link_count = (
        models.CharacteristicLink.objects.filter(
            Q(from_characteristic__pk__in=view_scoped_ids) | Q(to_characteristic__pk__in=view_scoped_ids)
        )
        .distinct()
        .count()
    )
    unlinked_characteristics = [c for c in view_scoped if c.links_count == 0]
    unlinked_characteristics.sort(key=lambda c: c.name)

    selected_id = request.GET.get("selected", "").strip()
    selected_characteristic = None
    selected_incoming_links = []
    selected_outgoing_links = []
    if selected_id:
        selected_characteristic = get_object_or_404(
            models.ProductCharacteristic.objects.select_related("primary_classification"),
            stable_id=selected_id,
        )
        selected_incoming_links = list(
            models.CharacteristicLink.objects.select_related("from_characteristic").filter(
                to_characteristic=selected_characteristic
            )
        )
        selected_outgoing_links = list(
            models.CharacteristicLink.objects.select_related("to_characteristic").filter(
                from_characteristic=selected_characteristic
            )
        )

    filter_params = {
        "relationship_type": relationship_type,
        "characteristic": characteristic_id,
        "category": category_filter,
        "system": system_filter,
        "view": view_filter,
    }
    filter_querystring = urlencode({key: value for key, value in filter_params.items() if value})
    query_prefix = f"?{filter_querystring}&" if filter_querystring else "?"

    return render(
        request,
        "fmea_app/characteristic_link_list.html",
        {
            "links": links,
            "relationship_type": relationship_type,
            "characteristic_id": characteristic_id,
            "category_filter": category_filter,
            "system_filter": system_filter,
            "view_filter": view_filter,
            "relationship_type_choices": models.CharacteristicLink.RELATIONSHIP_TYPE_CHOICES,
            "characteristics": models.ProductCharacteristic.objects.order_by("name"),
            "classification_choices": models.ClassificationTerm.objects.order_by("scheme_id", "order", "name"),
            "system_choices": models.System.objects.order_by("name"),
            "coverage_total_in_view": total_in_view,
            "coverage_linked_in_view": linked_in_view,
            "coverage_unlinked_in_view": unlinked_in_view,
            "coverage_total_link_count": total_link_count,
            "unlinked_characteristics": unlinked_characteristics,
            "query_prefix": query_prefix,
            "selected_characteristic": selected_characteristic,
            "selected_incoming_links": selected_incoming_links,
            "selected_outgoing_links": selected_outgoing_links,
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


PRODUCT_CHARACTERISTIC_DETAIL_TABS = ("general", "classification", "links")


def _system_product_label(characteristic) -> str:
    requirement = characteristic.requirement
    if requirement is None:
        return "—"
    function = requirement.function
    if function is None:
        return "—"
    product = function.product
    if product is not None:
        if product.system is not None:
            return product.system.name
        return product.name
    operation = function.operation
    if operation is not None:
        process = operation.process
        if process is not None:
            if process.system is not None:
                return process.system.name
            return process.name
    return "—"


@require_GET
def product_characteristic_list(request):
    classification_filter = request.GET.get("classification", "").strip()
    is_special_filter = request.GET.get("is_special", "").strip()
    system_filter = request.GET.get("system", "").strip()

    characteristics = (
        models.ProductCharacteristic.objects.select_related(
            "primary_classification",
            "requirement",
            "requirement__function",
            "requirement__function__product",
            "requirement__function__product__system",
            "requirement__function__operation",
            "requirement__function__operation__process",
            "requirement__function__operation__process__system",
        )
        .annotate(
            outgoing_link_count=Count("outgoing_links", distinct=True),
            incoming_link_count=Count("incoming_links", distinct=True),
        )
        .order_by("name")
    )
    if classification_filter:
        characteristics = characteristics.filter(primary_classification__stable_id=classification_filter)
    if is_special_filter:
        characteristics = characteristics.filter(is_special=(is_special_filter == "yes"))
    if system_filter:
        characteristics = characteristics.filter(
            Q(requirement__function__product__system__stable_id=system_filter)
            | Q(requirement__function__operation__process__system__stable_id=system_filter)
        )

    rows = []
    for characteristic in characteristics:
        links_count = characteristic.outgoing_link_count + characteristic.incoming_link_count
        rows.append(
            {
                "characteristic": characteristic,
                "category_label": (
                    characteristic.primary_classification.name
                    if characteristic.primary_classification
                    else "Unclassified"
                ),
                "system_product_label": _system_product_label(characteristic),
                "links_count": links_count,
                "status_label": "Special" if characteristic.is_special else "Standard",
            }
        )

    total_count = len(rows)
    special_count = sum(1 for row in rows if row["characteristic"].is_special)
    unclassified_count = sum(1 for row in rows if row["characteristic"].primary_classification_id is None)
    linked_count = sum(1 for row in rows if row["links_count"] > 0)
    coverage_unclassified = unclassified_count
    coverage_unlinked = sum(1 for row in rows if row["links_count"] == 0)
    coverage_no_chain = sum(1 for row in rows if row["system_product_label"] == "—")

    classification_choices = models.ClassificationTerm.objects.order_by("scheme_id", "order", "name")
    system_choices = models.System.objects.order_by("name")
    is_special_choices = [("yes", "Yes"), ("no", "No")]

    filter_params = {
        "classification": classification_filter,
        "is_special": is_special_filter,
        "system": system_filter,
    }
    filter_querystring = urlencode({key: value for key, value in filter_params.items() if value})
    query_prefix = f"?{filter_querystring}&" if filter_querystring else "?"

    selected_id = request.GET.get("selected", "").strip()
    selected_characteristic = None
    if selected_id:
        selected_characteristic = get_object_or_404(
            models.ProductCharacteristic.objects.select_related(
                "primary_classification",
                "primary_classification__scheme",
                "requirement",
                "requirement__function",
                "requirement__function__product",
                "requirement__function__product__system",
                "requirement__function__operation",
                "requirement__function__operation__process",
                "requirement__function__operation__process__system",
            ),
            stable_id=selected_id,
        )

    active_tab = request.GET.get("tab", "general").strip().lower()
    if active_tab not in PRODUCT_CHARACTERISTIC_DETAIL_TABS:
        active_tab = "general"

    selected_system_product_label = "—"
    selected_links = []
    if selected_characteristic is not None:
        selected_system_product_label = _system_product_label(selected_characteristic)
        selected_links = list(
            models.CharacteristicLink.objects.select_related("from_characteristic", "to_characteristic")
            .filter(
                Q(from_characteristic__pk=selected_characteristic.pk)
                | Q(to_characteristic__pk=selected_characteristic.pk)
            )
            .order_by("from_characteristic__name", "to_characteristic__name")
        )

    return render(
        request,
        "fmea_app/product_characteristic_list.html",
        {
            "rows": rows,
            "kpi_total": total_count,
            "kpi_special": special_count,
            "kpi_unclassified": unclassified_count,
            "kpi_linked": linked_count,
            "coverage_unclassified": coverage_unclassified,
            "coverage_unlinked": coverage_unlinked,
            "coverage_no_chain": coverage_no_chain,
            "classification_choices": classification_choices,
            "system_choices": system_choices,
            "is_special_choices": is_special_choices,
            "classification_filter": classification_filter,
            "is_special_filter": is_special_filter,
            "system_filter": system_filter,
            "query_prefix": query_prefix,
            "selected_characteristic": selected_characteristic,
            "selected_system_product_label": selected_system_product_label,
            "selected_links": selected_links,
            "active_tab": active_tab,
            "detail_tabs": PRODUCT_CHARACTERISTIC_DETAIL_TABS,
        },
    )

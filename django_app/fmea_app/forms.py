from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from . import models


class FMEAProjectForm(forms.ModelForm):
    class Meta:
        model = models.FMEAProject
        fields = ["name", "project_code", "status", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].required = False

    def clean_status(self):
        return self.cleaned_data["status"] or "active"


class ProjectMembershipForm(forms.Form):
    first_name = forms.CharField(required=False, max_length=150)
    last_name = forms.CharField(required=False, max_length=150)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=models.ProjectMembership.ROLE_CHOICES)

    def save(self, *, project: models.FMEAProject) -> tuple[models.ProjectMembership, bool]:
        email = self.cleaned_data["email"].strip().lower()
        first_name = self.cleaned_data["first_name"].strip()
        last_name = self.cleaned_data["last_name"].strip()
        role = self.cleaned_data["role"]

        user_model = get_user_model()
        user = user_model.objects.filter(email__iexact=email).first()
        if user is None:
            user = user_model.objects.create(
                username=_available_username(user_model, email),
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
        else:
            update_fields = []
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                update_fields.append("first_name")
            if last_name and user.last_name != last_name:
                user.last_name = last_name
                update_fields.append("last_name")
            if update_fields:
                user.save(update_fields=update_fields)

        return models.ProjectMembership.objects.update_or_create(
            project=project,
            user=user,
            defaults={"role": role},
        )


def _available_username(user_model, email: str) -> str:
    base = email[:150] or "project-member"
    username = base
    suffix = 2
    while user_model.objects.filter(username=username).exists():
        suffix_text = f"-{suffix}"
        username = f"{base[: 150 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    return username


class FMEAForm(forms.ModelForm):
    class Meta:
        model = models.FMEA
        fields = ["project", "name", "fmea_type", "scope"]
        widgets = {
            "scope": forms.Textarea(attrs={"rows": 2}),
        }


class FunctionForm(forms.ModelForm):
    class Meta:
        model = models.Function
        fields = ["name", "description", "product", "operation"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, fmea=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].required = False
        self.fields["operation"].required = False
        if fmea is not None:
            self.fields["product"].queryset = fmea.products.order_by("name")
            self.fields["operation"].queryset = models.Operation.objects.filter(
                process__fmea=fmea
            ).order_by("process__name", "sequence", "name")
        else:
            self.fields["product"].queryset = models.Product.objects.none()
            self.fields["operation"].queryset = models.Operation.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        # Function has no direct FMEA FK in the model - it is only reachable
        # from an FMEA through Product or Operation (both nullable). Without
        # at least one of them set, a Function created from this form would
        # be an orphan invisible from every FMEA's page, not "created under"
        # the FMEA the form appeared on. Enforced here (a GUI form guard, not
        # a fmea_domain/rules.py domain rule) rather than left to silently
        # produce unreachable data.
        if not cleaned_data.get("product") and not cleaned_data.get("operation"):
            raise forms.ValidationError(
                "Select a Product or an Operation so this Function is linked to this FMEA."
            )
        return cleaned_data


class FailureModeForm(forms.ModelForm):
    class Meta:
        model = models.FailureMode
        fields = ["name", "description", "function"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, fmea=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["function"].required = False
        if fmea is not None:
            self.fields["function"].queryset = models.Function.objects.filter(
                Q(product__fmea=fmea) | Q(operation__process__fmea=fmea)
            ).order_by("name")
        else:
            self.fields["function"].queryset = models.Function.objects.none()


class FailureEffectForm(forms.ModelForm):
    class Meta:
        model = models.FailureEffect
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class FailureCauseForm(forms.ModelForm):
    class Meta:
        model = models.FailureCause
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class PreventionControlForm(forms.ModelForm):
    class Meta:
        model = models.PreventionControl
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class DetectionControlForm(forms.ModelForm):
    class Meta:
        model = models.DetectionControl
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class RecommendedActionForm(forms.ModelForm):
    class Meta:
        model = models.RecommendedAction
        fields = ["name", "description", "responsible_role", "status", "due_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible_role"].queryset = models.ResponsibleRole.objects.order_by("name")
        self.fields["responsible_role"].required = False


class ProcessCharacteristicForm(forms.ModelForm):
    cause_category_id = forms.ChoiceField(required=False, choices=())
    attributes = forms.JSONField(required=False, widget=forms.Textarea(attrs={"rows": 4}))

    class Meta:
        model = models.ProcessCharacteristic
        fields = [
            "operation",
            "name",
            "description",
            "cause_category_id",
            "attributes",
            "control_type",
            "method",
            "resource_equipment",
            "frequency_trigger",
            "status",
            "effectiveness",
            "owner",
            "review_due",
            "reaction_plan",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "reaction_plan": forms.Textarea(attrs={"rows": 2}),
            "review_due": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["operation"].queryset = models.Operation.objects.order_by(
            "process__name",
            "sequence",
            "name",
        )
        self.fields["cause_category_id"].choices = [
            ("", "Uncategorized"),
            *[
                (category.stable_id, category.name)
                for category in models.CauseCategory.objects.order_by("sort_order", "name")
            ],
        ]
        self.fields["control_type"].required = False
        self.fields["status"].required = False
        self.fields["effectiveness"].required = False
        self.fields["owner"].required = False
        self.fields["owner"].queryset = models.ResponsibleRole.objects.order_by("name")

    def clean_attributes(self):
        return self.cleaned_data["attributes"] or {}


class ValidationTestForm(forms.ModelForm):
    class Meta:
        model = models.ValidationTest
        fields = [
            "name",
            "failure_mode",
            "recommended_action",
            "test_type",
            "method",
            "objective",
            "nominal_target",
            "acceptance_criteria",
            "result_status",
            "planned_date",
            "executed_date",
            "priority",
            "owner",
            "lifecycle_gate",
            "status",
        ]
        widgets = {
            "objective": forms.Textarea(attrs={"rows": 2}),
            "acceptance_criteria": forms.Textarea(attrs={"rows": 2}),
            "planned_date": forms.DateInput(attrs={"type": "date"}),
            "executed_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recommended_action"].required = False
        self.fields["recommended_action"].queryset = models.RecommendedAction.objects.order_by("name")
        self.fields["owner"].required = False
        self.fields["owner"].queryset = models.ResponsibleRole.objects.order_by("name")


class SystemForm(forms.ModelForm):
    class Meta:
        model = models.System
        fields = ["name", "description", "code", "parent", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = models.System.objects.order_by("name")
        if self.instance is not None and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        self.fields["parent"].queryset = queryset
        self.fields["parent"].required = False
        self.fields["status"].required = False

    def clean_status(self):
        return self.cleaned_data["status"] or "active"


class RiskEvaluationForm(forms.Form):
    definition = forms.ModelChoiceField(
        queryset=models.EvaluationDefinition.objects.order_by("name"),
        empty_label=None,
    )
    severity = forms.IntegerField(min_value=1, max_value=10)
    occurrence = forms.IntegerField(min_value=1, max_value=10)
    detection = forms.IntegerField(min_value=1, max_value=10)
    lifecycle_gate = forms.ChoiceField(
        choices=models.RiskEvaluation.LIFECYCLE_GATE_CHOICES,
        required=False,
    )


class ChangeForm(forms.ModelForm):
    class Meta:
        model = models.Change
        fields = [
            "title",
            "change_type",
            "source",
            "reason",
            "description",
            "impact_level",
            "status",
            "owner",
            "target_date",
            "affected_failure_modes",
        ]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 2}),
            "description": forms.Textarea(attrs={"rows": 2}),
            "target_date": forms.DateInput(attrs={"type": "date"}),
            "affected_failure_modes": forms.SelectMultiple(attrs={"size": 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].required = False
        self.fields["owner"].queryset = models.ResponsibleRole.objects.order_by("name")
        self.fields["affected_failure_modes"].required = False
        self.fields["affected_failure_modes"].queryset = models.FailureMode.objects.select_related(
            "fmea"
        ).order_by("fmea__name", "name")


class CharacteristicLinkForm(forms.ModelForm):
    class Meta:
        model = models.CharacteristicLink
        fields = [
            "from_characteristic",
            "to_characteristic",
            "relationship_type",
            "strength",
            "created_by",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        characteristics = models.ProductCharacteristic.objects.order_by("name")
        self.fields["from_characteristic"].queryset = characteristics
        self.fields["to_characteristic"].queryset = characteristics

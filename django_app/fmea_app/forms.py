from __future__ import annotations

from django import forms
from django.db.models import Q

from . import models


class FMEAProjectForm(forms.ModelForm):
    class Meta:
        model = models.FMEAProject
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


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
        fields = ["operation", "name", "description", "cause_category_id", "attributes"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
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

    def clean_attributes(self):
        return self.cleaned_data["attributes"] or {}


class RiskEvaluationForm(forms.Form):
    definition = forms.ModelChoiceField(
        queryset=models.EvaluationDefinition.objects.order_by("name"),
        empty_label=None,
    )
    severity = forms.IntegerField(min_value=1, max_value=10)
    occurrence = forms.IntegerField(min_value=1, max_value=10)
    detection = forms.IntegerField(min_value=1, max_value=10)

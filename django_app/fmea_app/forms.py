from __future__ import annotations

from django import forms

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


class FailureModeForm(forms.ModelForm):
    class Meta:
        model = models.FailureMode
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


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

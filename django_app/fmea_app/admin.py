from django.contrib import admin

from . import models


@admin.register(models.FMEAProject)
class FMEAProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "stable_id", "revision")
    search_fields = ("name", "stable_id")


@admin.register(models.FMEA)
class FMEAAdmin(admin.ModelAdmin):
    list_display = ("name", "fmea_type", "lifecycle", "stable_id", "revision")
    list_filter = ("fmea_type", "lifecycle")
    search_fields = ("name", "stable_id", "scope")


@admin.register(models.FailureMode)
class FailureModeAdmin(admin.ModelAdmin):
    list_display = ("name", "fmea", "stable_id", "revision")
    search_fields = ("name", "stable_id", "description")


@admin.register(models.RiskEvaluation)
class RiskEvaluationAdmin(admin.ModelAdmin):
    list_display = ("failure_mode", "method", "severity", "occurrence", "detection", "evaluated_at")
    list_filter = ("method",)
    readonly_fields = ("result", "evaluated_at")


@admin.register(models.CauseCategoryScheme)
class CauseCategorySchemeAdmin(admin.ModelAdmin):
    list_display = ("name", "stable_id", "revision")
    search_fields = ("name", "stable_id", "description")


@admin.register(models.CauseCategory)
class CauseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "scheme_id", "sort_order", "stable_id")
    list_filter = ("scheme_id",)
    search_fields = ("name", "stable_id", "description", "scheme_id")


@admin.register(models.CauseInfluence)
class CauseInfluenceAdmin(admin.ModelAdmin):
    list_display = (
        "source_type",
        "source_id",
        "target_type",
        "target_id",
        "status",
        "cause_category_id",
        "stable_id",
    )
    list_filter = ("source_type", "target_type", "status", "cause_category_id")
    search_fields = ("stable_id", "source_id", "target_id", "influence_type", "review_note")


@admin.register(models.ProductCharacteristic)
class ProductCharacteristicAdmin(admin.ModelAdmin):
    list_display = ("name", "requirement", "is_special", "primary_classification", "stable_id")
    list_filter = ("is_special", "primary_classification")
    search_fields = ("name", "stable_id", "description", "primary_classification__name")


@admin.register(models.System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "status", "parent", "stable_id")
    list_filter = ("status",)
    search_fields = ("name", "stable_id", "code", "description")


@admin.register(models.ClassificationScheme)
class ClassificationSchemeAdmin(admin.ModelAdmin):
    list_display = ("name", "stable_id", "revision")
    search_fields = ("name", "stable_id", "description")


@admin.register(models.ClassificationTerm)
class ClassificationTermAdmin(admin.ModelAdmin):
    list_display = ("name", "scheme", "order", "stable_id")
    list_filter = ("scheme",)
    search_fields = ("name", "stable_id", "description")


@admin.register(models.ProcessCharacteristic)
class ProcessCharacteristicAdmin(admin.ModelAdmin):
    list_display = ("name", "operation", "cause_category_id", "stable_id")
    list_filter = ("cause_category_id",)
    search_fields = ("name", "stable_id", "description", "cause_category_id")


for model in (
    models.Product,
    models.Process,
    models.Operation,
    models.Function,
    models.Requirement,
    models.FailureEffect,
    models.FailureCause,
    models.FailureMechanism,
    models.PreventionControl,
    models.DetectionControl,
    models.MeasurementMethod,
    models.ResponsibleRole,
    models.RecommendedAction,
    models.Evidence,
    models.EffectivenessVerification,
    models.EvaluationDefinition,
    models.FMEARevision,
    models.DomainRelationship,
):
    admin.site.register(model)

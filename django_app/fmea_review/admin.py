from django.contrib import admin

from . import models


@admin.register(models.ImportSession)
class ImportSessionAdmin(admin.ModelAdmin):
    list_display = ("source_filename", "status", "uploaded_at", "stable_id")
    list_filter = ("status",)
    search_fields = ("source_filename", "stable_id", "document_version")


@admin.register(models.FmeaRowGroup)
class FmeaRowGroupAdmin(admin.ModelAdmin):
    list_display = ("sheet_name", "row_start", "row_end", "review_status", "stable_id")
    list_filter = ("review_status", "sheet_name")
    search_fields = ("stable_id", "sheet_name", "source_range")
    readonly_fields = ("stable_id",)


@admin.register(models.ImportCandidateRecord)
class ImportCandidateRecordAdmin(admin.ModelAdmin):
    list_display = (
        "suggested_domain_type",
        "extracted_value",
        "review_status",
        "row_group",
        "row_number",
        "column_name",
    )
    list_filter = ("review_status", "suggested_domain_type", "extraction_method", "row_group")
    search_fields = ("extracted_value", "stable_id", "accepted_object_stable_id")
    readonly_fields = ("stable_id", "document_version", "source_document_id")

# Generated for Open-FMEA Characteristics-Linking-1 on 2026-09-01

from django.db import migrations


OLD_TYPE = "Characteristic"
NEW_TYPE = "ProductCharacteristic"


def forwards(apps, schema_editor):
    ImportCandidateRecord = apps.get_model("fmea_review", "ImportCandidateRecord")
    FmeaRowGroup = apps.get_model("fmea_review", "FmeaRowGroup")

    ImportCandidateRecord.objects.filter(suggested_domain_type=OLD_TYPE).update(
        suggested_domain_type=NEW_TYPE
    )
    _rename_detected_field_keys(FmeaRowGroup, OLD_TYPE, NEW_TYPE)


def backwards(apps, schema_editor):
    ImportCandidateRecord = apps.get_model("fmea_review", "ImportCandidateRecord")
    FmeaRowGroup = apps.get_model("fmea_review", "FmeaRowGroup")

    ImportCandidateRecord.objects.filter(suggested_domain_type=NEW_TYPE).update(
        suggested_domain_type=OLD_TYPE
    )
    _rename_detected_field_keys(FmeaRowGroup, NEW_TYPE, OLD_TYPE)


def _rename_detected_field_keys(model_class, old_key: str, new_key: str) -> None:
    for row_group in model_class.objects.all().iterator():
        detected_fields = dict(row_group.detected_fields or {})
        if old_key not in detected_fields:
            continue
        values = detected_fields.pop(old_key)
        if new_key in detected_fields:
            detected_fields[new_key] = [*detected_fields[new_key], *values]
        else:
            detected_fields[new_key] = values
        row_group.detected_fields = detected_fields
        row_group.save(update_fields=["detected_fields"])


class Migration(migrations.Migration):

    dependencies = [
        ("fmea_review", "0002_fmearowgroup_importcandidaterecord_row_group_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

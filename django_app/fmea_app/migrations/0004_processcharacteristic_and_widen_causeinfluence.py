# Generated for Open-FMEA Characteristics-Linking-1 on 2026-09-01

import django.db.models.deletion
import fmea_domain.identifiers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fmea_app", "0003_rename_characteristic_to_productcharacteristic"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProcessCharacteristic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "stable_id",
                    models.CharField(
                        db_index=True,
                        default=fmea_domain.identifiers.new_stable_id,
                        editable=False,
                        max_length=128,
                        unique=True,
                    ),
                ),
                ("schema_version", models.CharField(default="1.0", max_length=16)),
                ("revision", models.PositiveIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "cause_category_id",
                    models.CharField(blank=True, db_index=True, max_length=128, null=True),
                ),
                ("attributes", models.JSONField(blank=True, default=dict)),
                (
                    "operation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="process_characteristics",
                        to="fmea_app.operation",
                    ),
                ),
            ],
            options={
                "ordering": ["operation", "name"],
            },
        ),
        migrations.AlterField(
            model_name="causeinfluence",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("FailureCause", "Failure Cause"),
                    ("FailureMechanism", "Failure Mechanism"),
                    ("ProcessCharacteristic", "Process Characteristic"),
                ],
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="causeinfluence",
            name="target_type",
            field=models.CharField(
                choices=[
                    ("FailureMode", "Failure Mode"),
                    ("FailureCause", "Failure Cause"),
                    ("ProductCharacteristic", "Product Characteristic"),
                ],
                max_length=64,
            ),
        ),
    ]

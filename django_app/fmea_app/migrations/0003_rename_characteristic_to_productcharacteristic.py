# Generated for Open-FMEA Characteristics-Linking-1 on 2026-09-01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fmea_app", "0002_causecategoryscheme_causecategory_causeinfluence"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Characteristic",
            new_name="ProductCharacteristic",
        ),
        migrations.AddField(
            model_name="productcharacteristic",
            name="primary_classification_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="productcharacteristic",
            name="requirement",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_characteristics",
                to="fmea_app.requirement",
            ),
        ),
    ]

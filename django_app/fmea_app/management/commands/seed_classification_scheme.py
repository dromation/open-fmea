from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from fmea_app import models


DEFAULT_SCHEME_STABLE_ID = "classification-scheme:product-characteristic-default"
DEFAULT_TERMS = (
    ("classification-term:product-characteristic-default:legal", "Legal", "", 1),
    ("classification-term:product-characteristic-default:safety", "Safety", "", 2),
    ("classification-term:product-characteristic-default:functional", "Functional", "", 3),
    ("classification-term:product-characteristic-default:decorative", "Decorative", "", 4),
)


class Command(BaseCommand):
    help = "Seed the default Product Characteristic classification scheme (Legal/Safety/Functional/Decorative)."

    @transaction.atomic
    def handle(self, *args, **options):
        scheme, _ = models.ClassificationScheme.objects.update_or_create(
            stable_id=DEFAULT_SCHEME_STABLE_ID,
            defaults={
                "name": "Product Characteristic Classification (default)",
                "description": "Default classification scheme for Product Characteristic Type/Category.",
            },
        )
        for stable_id, name, description, order in DEFAULT_TERMS:
            models.ClassificationTerm.objects.update_or_create(
                stable_id=stable_id,
                defaults={
                    "scheme": scheme,
                    "name": name,
                    "description": description,
                    "order": order,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(f"Seeded classification scheme: {scheme.stable_id}")
        )

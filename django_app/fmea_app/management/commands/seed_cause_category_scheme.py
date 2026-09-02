from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from fmea_app import models


DEFAULT_SCHEME_STABLE_ID = "cause-category-scheme:ishikawa-5me-default"
DEFAULT_CATEGORIES = (
    ("cause-category:ishikawa-5me:man", "Man", "Human work-system factors; never personal blame data.", 1),
    ("cause-category:ishikawa-5me:machine", "Machine", "Equipment, tooling, fixtures, and machine condition.", 2),
    ("cause-category:ishikawa-5me:material", "Material", "Input material, component, lot, and supplier variation.", 3),
    ("cause-category:ishikawa-5me:method", "Method", "Work method, setup, sequence, and process instruction factors.", 4),
    ("cause-category:ishikawa-5me:measurement", "Measurement", "Inspection, measurement system, gauge, and test-method factors.", 5),
    ("cause-category:ishikawa-5me:environment", "Environment", "Ambient, storage, handling, and workplace environmental factors.", 6),
)


class Command(BaseCommand):
    help = "Seed the default configurable Ishikawa 5M+E cause-category scheme."

    @transaction.atomic
    def handle(self, *args, **options):
        scheme, _ = models.CauseCategoryScheme.objects.update_or_create(
            stable_id=DEFAULT_SCHEME_STABLE_ID,
            defaults={
                "name": "Ishikawa 5M+E (default)",
                "description": "Default configurable cause-category scheme for Ishikawa review.",
            },
        )
        for stable_id, name, description, sort_order in DEFAULT_CATEGORIES:
            models.CauseCategory.objects.update_or_create(
                stable_id=stable_id,
                defaults={
                    "scheme_id": scheme.stable_id,
                    "name": name,
                    "description": description,
                    "sort_order": sort_order,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(f"Seeded cause-category scheme: {scheme.stable_id}")
        )

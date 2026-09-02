from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from fmea_app.models import FMEA
from fmea_app.services import build_ofef_document
from fmea_importexport import to_json


class Command(BaseCommand):
    help = "Export an FMEA as Open-FMEA Exchange Format JSON."

    def add_arguments(self, parser):
        parser.add_argument("stable_id", help="FMEA stable_id to export")
        parser.add_argument("--output", "-o", help="Output JSON file")

    def handle(self, *args, **options):
        stable_id = options["stable_id"]
        try:
            fmea = FMEA.objects.get(stable_id=stable_id)
        except FMEA.DoesNotExist as exc:
            raise CommandError(f"FMEA not found: {stable_id}") from exc

        content = to_json(build_ofef_document(fmea))
        output = options.get("output")
        if output:
            Path(output).write_bytes(content.encode("utf-8"))
            self.stdout.write(self.style.SUCCESS(f"Exported OFEF JSON to {output}"))
        else:
            self.stdout.write(content)

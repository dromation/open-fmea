#!/usr/bin/env python
"""Django command entry point for Open FMEA."""
from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
for package_root in (ROOT / "domain", ROOT / "django_app"):
    package_root_str = str(package_root)
    if package_root_str not in sys.path:
        sys.path.insert(0, package_root_str)


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "open_fmea_project.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

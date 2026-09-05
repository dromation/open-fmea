from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NoDjangoImportTests(unittest.TestCase):
    def test_domain_and_evaluation_import_without_django(self):
        code = (
            "import sys; "
            f"sys.path.insert(0, {str(ROOT / 'domain')!r}); "
            f"sys.path.insert(0, {str(ROOT / 'django_app')!r}); "
            "import fmea_domain, fmea_evaluation; "
            "print(any(name == 'django' or name.startswith('django.') for name in sys.modules))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), "False")


if __name__ == "__main__":
    unittest.main()

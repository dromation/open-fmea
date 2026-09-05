from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SeedDemoReproducibilityTests(unittest.TestCase):
    def test_seed_demo_export_is_reproducible_on_fresh_databases(self):
        first = self._export_from_fresh_database("first")
        second = self._export_from_fresh_database("second")

        self.assertEqual(first, second)

    def _export_from_fresh_database(self, label: str) -> str:
        with tempfile.TemporaryDirectory(prefix=f"open-fmea-{label}-") as directory:
            temp_dir = Path(directory)
            db_path = temp_dir / "db.sqlite3"
            output_path = temp_dir / "demo.ofef.json"
            env = os.environ.copy()
            env["OPEN_FMEA_DB_PATH"] = str(db_path)

            self._run(["manage.py", "migrate", "--noinput"], env)
            self._run(["manage.py", "seed_demo"], env)
            self._run(
                [
                    "manage.py",
                    "export_ofef",
                    "demo:fmea:brake-assembly-process",
                    "--output",
                    str(output_path),
                ],
                env,
            )

            self.assertNotIn(b"\r\n", output_path.read_bytes())
            return output_path.read_text(encoding="utf-8")

    def _run(self, args: list[str], env: dict[str, str]) -> None:
        subprocess.run(
            [sys.executable, "-B", *args],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()

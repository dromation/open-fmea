from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "django_app"))

from fmea_ai.validation import validate_structured_output  # noqa: E402


class AiValidationSchemaTests(unittest.TestCase):
    def test_malformed_structured_output_is_rejected(self):
        valid, issues = validate_structured_output(
            {"name": 42},
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
                "additionalProperties": False,
            },
        )

        self.assertFalse(valid)
        self.assertTrue(issues)

    def test_non_object_structured_output_is_rejected(self):
        valid, issues = validate_structured_output(
            None,
            {"type": "object"},
        )

        self.assertFalse(valid)
        self.assertEqual(issues, ("structured_output must be an object",))


if __name__ == "__main__":
    unittest.main()

"""JSON-Schema validation helpers for structured AI output."""
from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


def validate_structured_output(
    structured_output: dict[str, Any] | None,
    output_schema: dict[str, Any],
) -> tuple[bool, tuple[str, ...]]:
    if not isinstance(structured_output, dict):
        return False, ("structured_output must be an object",)
    try:
        validator = Draft202012Validator(output_schema)
        Draft202012Validator.check_schema(output_schema)
    except SchemaError as exc:
        return False, (f"invalid output schema: {exc.message}",)

    issues = tuple(error.message for error in sorted(validator.iter_errors(structured_output), key=str))
    return (not issues, issues)

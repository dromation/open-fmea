"""Portable identifiers for Open-FMEA domain objects."""
from __future__ import annotations

import re
import uuid


_STABLE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{7,127}$")


def new_stable_id(prefix: str | None = None) -> str:
    """Return an opaque, immutable identifier independent of database PKs."""
    value = uuid.uuid4().hex
    if not prefix:
        return value
    cleaned = prefix.strip().lower().replace(" ", "-")
    return f"{cleaned}:{value}"


def require_stable_id(value: str) -> str:
    if not isinstance(value, str) or not _STABLE_ID_PATTERN.match(value):
        raise ValueError(f"Invalid stable_id: {value!r}")
    return value

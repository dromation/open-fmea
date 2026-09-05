"""Pure-Python WCAG 2.1 contrast helpers for testing theme.css tokens.

No Django/domain imports — this is a plain-Python utility module, not a
test module itself (pytest will not collect it, since it doesn't match
the tests/test_*.py pattern and doesn't start with "test_").
"""
from __future__ import annotations

import re

_HEX_RE = re.compile(r"^#([0-9a-fA-F]{6})$")


def relative_luminance(hex_color: str) -> float:
    """WCAG 2.1 relative luminance for a "#rrggbb" color string."""
    match = _HEX_RE.match(hex_color.strip())
    if not match:
        raise ValueError(f"Not a bare #rrggbb hex color: {hex_color!r}")
    raw = match.group(1)
    r, g, b = int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)

    def channel(component: int) -> float:
        c = component / 255
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    r_lin, g_lin, b_lin = channel(r), channel(g), channel(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """WCAG 2.1 contrast ratio between two "#rrggbb" colors."""
    l_fg = relative_luminance(fg_hex)
    l_bg = relative_luminance(bg_hex)
    lighter = max(l_fg, l_bg)
    darker = min(l_fg, l_bg)
    return (lighter + 0.05) / (darker + 0.05)


_DECLARATION_RE = re.compile(r"--([a-zA-Z0-9-]+)\s*:\s*([^;]+);")


def extract_theme_tokens(css_text: str, block_selector: str) -> dict[str, str]:
    """Extract ``{token_name: "#hexvalue"}`` from one top-level CSS block.

    ``block_selector`` is matched literally (e.g. ``":root {"`` or
    ``':root[data-theme="light"] {'``). Scanning starts right after the
    selector's own opening brace and tracks brace depth so any nested
    ``@media { ... }`` block appearing before the top-level selector's
    closing ``}`` does not prematurely end the scan. Declarations whose
    value is not a bare ``#rrggbb`` hex literal (``rgba(...)``,
    ``var(...)``, etc.) are skipped rather than raising.
    """
    start = css_text.find(block_selector)
    if start == -1:
        raise ValueError(f"Block selector not found: {block_selector!r}")

    brace_start = css_text.index("{", start)
    depth = 1
    pos = brace_start + 1
    end = len(css_text)
    while pos < len(css_text):
        char = css_text[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = pos
                break
        pos += 1

    block_text = css_text[brace_start + 1 : end]

    tokens: dict[str, str] = {}
    for name, value in _DECLARATION_RE.findall(block_text):
        value = value.strip()
        if _HEX_RE.match(value):
            tokens[f"--{name}"] = value
    return tokens


CHECKED_PAIRS: list[tuple[str, str]] = [
    ("--text-primary", "--bg-app"),
    ("--text-primary", "--bg-card"),
    ("--text-secondary", "--bg-app"),
    ("--text-secondary", "--bg-card"),
    ("--text-muted", "--bg-app"),
    ("--text-muted", "--bg-card"),
    ("--status-good-text", "--bg-card"),
    ("--status-warning-text", "--bg-card"),
    ("--status-critical-text", "--bg-card"),
    ("--link-color", "--bg-card"),
    ("--code-color", "--bg-card"),
    ("--brand-mark-fg", "--brand-mark-bg"),
]

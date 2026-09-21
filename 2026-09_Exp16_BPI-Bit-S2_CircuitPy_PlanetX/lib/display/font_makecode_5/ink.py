"""Look up trimmed ink columns from the generated spaced-glyph table.

Pure module: no hardware imports. The table itself is generated; this
accessor is the hand-written contract on top of it.

Tofu is the glyph representing a missing character:
this module uses □ precomputed and stored as ``_TOFU_INK``
(icons.py ``# 38: SMALL_SQUARE`` with blank columns stripped).
"""

from __future__ import annotations

from .spaced_glyphs import (
    _ASCII_END,
    _ASCII_START,
    _RECORD_STRIDE,
    _SPACED_GLYPHS,
)

# tofu ink: SMALL_SQUARE with blank columns stripped.
# Enforced by tests/test_font_spacing.py::test_tofu_matches_stripped_small_square.
_TOFU_INK = bytes((0x0E, 0x0A, 0x0E))


def glyph_ink(ch: str) -> bytes:
    """Return the authored occupied columns for one character, ready to draw.

    Typical case: printable ASCII (32..126) is sliced from ``_SPACED_GLYPHS``.
    Ink-bearing glyphs are already trimmed of blank lead/trail columns; space
    is three blank columns (a following inter-glyph spacer, if any, supplies
    the fourth).

    Unknown, empty, or out-of-range input is tofu (``_TOFU_INK``), not a hole.
    """
    if not ch:
        return _TOFU_INK
    code = ord(ch[0])
    if code < _ASCII_START or code > _ASCII_END:
        return _TOFU_INK
    i = (code - _ASCII_START) * _RECORD_STRIDE
    n = _SPACED_GLYPHS[i]
    i += 1  # byte with index zero states how many non-empty columns the glyph has
    return _SPACED_GLYPHS[i : i + n]

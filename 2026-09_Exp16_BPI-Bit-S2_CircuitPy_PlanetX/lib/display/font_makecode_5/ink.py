"""Look up trimmed ink columns from the generated spaced-glyph table.

Pure module: no hardware imports. The table itself is generated; this
accessor is the hand-written contract on top of it.
"""

from __future__ import annotations

from .._constants import WIDTH
from .spaced_glyphs import _ASCII_END, _ASCII_START, _RECORD_STRIDE, _SPACED_GLYPHS


def glyph_ink(ch: str) -> tuple[bytes, bool]:
    """Return ``(ink_columns, needs_spacer)`` for one character.

    ``ink_columns`` is the glyph's authored occupied span, ready to draw:
    ink-bearing glyphs are already trimmed of blank lead/trail columns;
    space is four blank columns; unknown or empty input is ``WIDTH`` blank
    columns. ``needs_spacer`` is True when this glyph has any ink, meaning a
    one-column blank should be prepended before the next glyph (never after
    the last one).
    """
    if not ch:
        return bytes(WIDTH), False
    code = ord(ch[0])
    if code < _ASCII_START or code > _ASCII_END:
        return bytes(WIDTH), False
    i = (code - _ASCII_START) * _RECORD_STRIDE
    rec = _SPACED_GLYPHS[i : i + _RECORD_STRIDE]
    length = rec[0]
    ink = rec[1 : 1 + length]
    return bytes(ink), any(ink)

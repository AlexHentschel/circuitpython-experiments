"""Look up trimmed glyph columns from the pre-generated glyph table.
The the underlying glyph table is generated; this accessor is the hand-written contract on top of it.

Tofu is the glyph representing a missing character:
this module uses □ precomputed and stored as ``_TOFU_INK``
(icons.py ``# 38: SMALL_SQUARE`` with blank columns stripped).

``Font`` defines abstractly what we need to draw characters in a font: ``glyph`` for drawing, ``width`` for measuring
how much of the display is occupied by the character. Both methods of ``Font`` raise ``NotImplementedError``.
A concrete font must properly implements both of those methods.
``Makecode5Font.width`` reads the record's length byte and does not copy the glyph.
"""

from __future__ import annotations

# Pure module: no hardware imports.
from .spaced_glyphs import (
    _ASCII_END,
    _ASCII_START,
    _RECORD_STRIDE,
    _SPACED_GLYPHS,
)

# tofu glyph: SMALL_SQUARE □  with blank columns stripped.
# Enforced by tests/test_font_spacing.py::test_tofu_matches_stripped_small_square.
_TOFU_INK = bytes((0x0E, 0x0A, 0x0E))


def _length_index(ch: str) -> int:
    """Index of the length byte in ``_SPACED_GLYPHS``, or -1 when ``ch`` is tofu."""
    if not ch:
        return -1
    code = ord(ch[0])
    if code < _ASCII_START or code > _ASCII_END:
        return -1
    return (code - _ASCII_START) * _RECORD_STRIDE


class Font:
    """Abstract definition of the characters of a font. Each character has a representation as column bytes and a width.
    ``width(ch)`` is the number of columns in ``glyph(ch)``. Spacing between characters is the feeder's job.

    A concrete font implements both ``glyph`` and ``width``.
    """

    def glyph(self, ch: str) -> bytes:
        """The drawing of one character, as column bytes.

        Python has no separate type for a single character, so ``ch`` must be a string of length 1, such as ``"A"`` or ``"7"``.
        """
        raise NotImplementedError

    def width(self, ch: str) -> int:
        """How many columns ``glyph(ch)`` contains.
        Python has no separate type for a single character, so ``ch`` must be a string of length 1, such as ``"A"`` or ``"7"``.
        """
        raise NotImplementedError


class Makecode5Font(Font):
    """The shipped 5x5 font. Missing, empty, and out-of-range characters are tofu."""

    def glyph(self, ch: str) -> bytes:
        """Return the glyph for the input character ``ch``, which can be drawn with the display library.
        Python has no separate type for a single character, so ``ch`` must be string of length 1, such as ``"A"`` or ``"7"``.

        Typical case: printable ASCII (32..126) is sliced from ``_SPACED_GLYPHS``.
        Glyphs with painted columns are already trimmed of blank lead/trail columns; space
        is three blank columns (a following inter-character spacer, if any, supplies
        the fourth).

        Unknown, empty, or out-of-range input is tofu (``_TOFU_INK``), not a hole.
        """
        i = _length_index(ch)
        if i < 0:
            return _TOFU_INK
        n = _SPACED_GLYPHS[i]
        i += 1  # byte with index zero states how many columns the glyph has
        return _SPACED_GLYPHS[i : i + n]

    def width(self, ch: str) -> int:
        """How many columns the character ``ch`` occupies."""
        # Reads the record's length byte. Do not copy the glyph just to count its number of columns.
        i = _length_index(ch)
        if i < 0:
            return len(_TOFU_INK)
        return _SPACED_GLYPHS[i]


FONT = Makecode5Font()

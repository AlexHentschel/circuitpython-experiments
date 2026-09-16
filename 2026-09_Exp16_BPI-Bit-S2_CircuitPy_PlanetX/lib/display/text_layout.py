"""Column-at-a-time text layout with build-time-trimmed inter-glyph spacing.

Pure module: no ``board`` / ``neopixel`` import, so host pytest can exercise
the feeder. ``Display.show_string`` is the on-device caller (after cutover).

A spacer column (0) is prepended before glyph N when glyph N-1 had ink.
There is never a trailing spacer after the last glyph — the same rule for
the scrolling path and the fit-on-screen path.
"""

from __future__ import annotations

from .font_makecode_5.ink import glyph_ink


class SpacedGlyphColumnFeeder:
    """Yield one column byte at a time across a text string.

    Materialises one glyph at a time via ``glyph_ink`` (or an injected
    ``lookup`` of the same ``(ink_bytes, needs_spacer)`` shape). Bounded
    memory: only the current glyph's columns plus a cursor, regardless of
    text length.

    ``next_column`` returns ``None`` once the text is exhausted. Callers
    that need a scroll-out tail substitute blank columns (``0``) themselves.
    """

    __slots__ = ("_text", "_lookup", "_char_idx", "_cols", "_col_idx", "_pending_spacer")

    def __init__(self, text: str, lookup=glyph_ink) -> None:
        self._text = text
        self._lookup = lookup
        self._char_idx = 0
        self._cols = b""
        self._col_idx = 0
        # True when the just-finished glyph had ink, so the *next* glyph
        # (if any) gets a spacer prepended. Starts False: the first glyph
        # has no predecessor.
        self._pending_spacer = False

    def next_column(self) -> int | None:
        # ``while`` (not ``if``) so a zero-width glyph is skipped in the same
        # call rather than stalling. Spacer emission is a ``return 0`` on the
        # pending-spacer path, not a stored extra column, so exhaustion cannot
        # emit a trailing blank: there is no "next glyph" to prepend before.
        while True:
            if self._col_idx < len(self._cols):
                b = self._cols[self._col_idx]
                self._col_idx += 1
                return b
            if self._char_idx >= len(self._text):
                return None
            ink, needs_spacer = self._lookup(self._text[self._char_idx])
            self._char_idx += 1
            if self._pending_spacer:
                self._cols = ink
                self._col_idx = 0
                self._pending_spacer = needs_spacer
                return 0
            self._cols = ink
            self._col_idx = 0
            self._pending_spacer = needs_spacer

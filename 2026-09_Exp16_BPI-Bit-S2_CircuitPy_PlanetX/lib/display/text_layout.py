"""Column-at-a-time text layout with build-time-trimmed inter-glyph spacing.

Pure module: no ``board`` / ``neopixel`` import, so host pytest can exercise
the feeder. ``Display.show_string`` is the on-device caller.

A spacer column (byte value 0) is prepended before every glyph except the first.
There is never a trailing spacer after the last glyph; the same rule for
the scrolling path and the fit-on-screen path.
"""

from __future__ import annotations

from .font_makecode_5.ink import glyph_ink


class SpacedGlyphColumnFeeder:
    """Yield one column byte at a time across a text string.

    Materialises one glyph at a time via ``glyph_ink`` (or an injected
    ``lookup`` that returns ink ``bytes``). Bounded memory: only the current
    glyph's columns plus a cursor, regardless of text length.

    ``next_column`` returns ``None`` once the text is exhausted. Callers
    that need a scroll-out tail substitute blank columns (``0``) themselves.
    """

    __slots__ = ("_text", "_lookup", "_next_char_idx", "_cols", "_col_idx", "_pending_spacer")

    def __init__(self, text: str, lookup=glyph_ink) -> None:
        self._text = text
        self._lookup = lookup
        self._next_char_idx = 0
        self._cols = b""
        self._col_idx = 0
        # True after the first glyph has been loaded, so every later glyph
        # gets a spacer prepended. Starts False: the first glyph has no predecessor.
        self._pending_spacer = False

    def next_column(self) -> int | None:
        # An empty spacer column, i.e. `return 0`, is only added once right before the next char is started.
        # End of text therefore returns `None` without emitting a pending spacer, because there is no next char
        # to prepend before, so the last glyph has no trailing blank.
        while True:  # empty ink: load the next char in this call; empty is not the end of the string
            if self._col_idx < len(self._cols):
                b = self._cols[self._col_idx]
                self._col_idx += 1
                return b
            if self._next_char_idx >= len(self._text):
                return None
            ink = self._lookup(self._text[self._next_char_idx])
            self._next_char_idx += 1
            self._cols = ink
            self._col_idx = 0
            if self._pending_spacer:
                return 0  # empty column (spacer)
            self._pending_spacer = True

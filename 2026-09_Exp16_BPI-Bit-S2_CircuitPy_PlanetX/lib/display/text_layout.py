"""Column-at-a-time text layout with build-time-trimmed inter-glyph spacing.

Pure module: no ``board`` / ``neopixel`` import, so host pytest can exercise
the feeder. ``Display.show_string`` and ``Display.render_string`` are the
on-device callers.

A spacer column (byte value 0) is prepended before every character except the first.
There is never a trailing spacer after the last character; the same rule for
the scrolling path, the fit-on-screen path, and ``render_string``.
"""

from __future__ import annotations

from .font_makecode_5.ink import FONT, Font


class SpacedGlyphColumnFeeder:
    """Turn a string into columns you can draw, one column at a time.

    A character such as a letter or a number is an abstract unit of information, while a glyph is
    the actual physical drawing of that character on the screen. This class takes the
    characters of a string and gives you each glyph one column at a time.

    A blank column sits in between every two, so neighboring glyphs do not touch.
    The first character has no blank column before it and the last character none after it.

    ``next_column`` returns the next column, and returns ``None`` when the string is finished.
    To scroll the text all the way off the screen, add your own blank columns after that.

    ``column_count`` is how many columns the whole string uses, including those blank columns.
    ``column_count_wider_than`` says whether that total is more than a number you choose.
    ``column_count_wider_than`` is often faster than ``column_count`` for long strings, because
    it can stop early when exceeding the ``limit`` you provided instead of counting the whole string.
    Asking either question leaves you at the same column ``next_column`` would return next.
    """

    __slots__ = ("_text", "_font", "_next_char_idx", "_cols", "_col_idx", "_pending_spacer")

    def __init__(self, text: str, font: Font = FONT) -> None:
        # For a character `ch`: font supplies glyph(ch) and width(ch). The default is the shipped MakeCode font.
        self._text = text
        self._font = font
        self._next_char_idx = 0
        self._cols = b""
        self._col_idx = 0
        # True after the first character has been loaded, so every later character
        # gets a spacer prepended. Starts False: the first character has no predecessor.
        self._pending_spacer = False

    def next_column(self) -> int | None:
        # An empty spacer column, i.e. `return 0`, is only added once right before the next character is started.
        # End of text therefore returns `None` without emitting a pending spacer, because there is no next character
        # to prepend before. Hence, the last character has no trailing blank.
        while True:  # empty glyph: load the next character in this call; empty is not the end of the string
            if self._col_idx < len(self._cols):
                b = self._cols[self._col_idx]
                self._col_idx += 1
                return b
            if self._next_char_idx >= len(self._text):
                return None
            self._cols = self._font.glyph(self._text[self._next_char_idx])
            self._col_idx = 0
            self._next_char_idx += 1
            if self._pending_spacer:
                return 0  # empty spacer column
            self._pending_spacer = True

    def reset(self) -> None:
        """Put the next column back at the start of the text.

        The text and the font stay as they were. ``column_count`` is unchanged, because it does not use the cursor.
        """
        self._next_char_idx = 0
        self._cols = b""
        self._col_idx = 0
        self._pending_spacer = False

    # Both count methods bind width once per call. Makecode5Font.width reads the length byte and does not copy the glyph.
    def column_count(self) -> int:
        """Returns how many columns the text overall encompasses; i.e. how many columns
        ``next_column`` would yield from the start of the text before producing ``None``.
        An empty string has zero width.

        This count only depends on the string and ignores how many columns have already been
        consumed from the feeder. Each character adds the columns of its glyph, plus one spacer column
        before every character after the first. (There are only spacer columns in between glyphs.)

        Does not move the cursor, i.e. does not change what ``next_column`` would return.
        """
        text = self._text
        n = len(text)
        if n == 0:
            return 0
        width = self._font.width
        count = width(text[0])
        for i in range(1, n):
            count += 1 + width(text[i])
        return count

    def column_count_wider_than(self, limit: int) -> bool:
        """True when this feeder's text occupies more than ``limit`` columns.
        Raises ``ValueError`` if ``limit`` is negative. An empty string has zero width.

        Stops at the first character that makes that true. Same spacer rule as ``column_count``.
        ``column_count_wider_than`` is often faster than ``column_count`` for long strings, because
        it can stop early when exceeding the ``limit`` you provided instead of counting the whole string.

        Does not move the cursor, i.e. does not change what ``next_column`` would return.
        """
        if limit < 0:
            raise ValueError(f"limit must be >= 0, got {limit}")
        text = self._text
        n = len(text)
        if n == 0:
            return False
        width = self._font.width
        count = width(text[0])
        if count > limit:
            return True
        for i in range(1, n):
            count += 1 + width(text[i])  # the "+1" term is the spacer _in between_ glyphs
            if count > limit:
                return True
        return False

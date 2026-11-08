"""Column-at-a-time text layout with build-time-trimmed inter-glyph spacing.

Pure module: no ``board`` / ``neopixel`` import, so host pytest can exercise
the readers. ``Display`` text methods are the on-device callers.

A spacer column (byte value 0) sits between characters. The first character
has no spacer before it, and the last character has none after it. The same
rule is used by every text method.

``ScreenText`` holds the text and its width. Each display call builds a fresh
reader, so a student's ``ScreenText`` has no cursor a scroll could move.
"""

from __future__ import annotations

from ._constants import WIDTH
from .font_makecode_5.ink import FONT, Font


def _column_count(text: str, font: Font) -> int:
    """Columns ``next_column`` would yield from the start, including spacers."""
    n = len(text)
    if n == 0:
        return 0
    width = font.width
    count = width(text[0])
    for i in range(1, n):
        count += 1 + width(text[i])  # `+1` term here is spacer column between characters
    return count


def _column_count_wider_than(text: str, font: Font, limit: int) -> bool:
    """True when ``text`` occupies more than ``limit`` columns. Stops early."""
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")
    n = len(text)
    if n == 0:
        return False
    width = font.width
    count = width(text[0])
    if count > limit:
        return True
    for i in range(1, n):
        count += 1 + width(text[i])  # `+1` term here is spacer column between characters
        if count > limit:
            return True
    return False


class _ColumnReader:
    """Cursor over a string's glyph columns.

    ``next_column`` returns the next column byte, then ``None`` at the end.
    Further calls keep returning ``None``. ``reset`` puts the cursor back at
    the first column. ``skip(n)`` drops ``n`` columns; ``n <= 0`` does nothing.
    """

    __slots__ = ("_text", "_font", "_next_char_idx", "_cols", "_col_idx", "_pending_spacer")

    def __init__(self, text: str, font: Font = FONT) -> None:
        self._text = text
        self._font = font
        self._next_char_idx = 0
        self._cols = b""
        self._col_idx = 0
        # True after the first character has been loaded, so every later character
        # gets a spacer prepended. Starts False: the first character has no predecessor.
        self._pending_spacer = False

    def next_column(self) -> int | None:
        # An empty spacer column is emitted once, immediately before the next character's ink.
        # End of text returns None without a trailing spacer.
        while True:
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
                return 0
            self._pending_spacer = True

    def reset(self) -> None:
        """Put the next column back at the start of the text."""
        self._next_char_idx = 0
        self._cols = b""
        self._col_idx = 0
        self._pending_spacer = False

    def skip(self, n: int) -> None:
        """Drop ``n`` columns. Whole glyphs are skipped by width, without copying ink.

        A group is ``width(ch)`` columns for the first character and ``1 + width(ch)``
        after that (the spacer plus the glyph). An already-loaded glyph tail is
        consumed first. When the next group is larger than the columns still to skip,
        the rest is taken with ``next_column``, so a skip that lands on a spacer
        still loads that glyph and the following ``next_column`` stays in step.
        ``n <= 0`` does nothing.
        """
        if n <= 0:
            return
        available = len(self._cols) - self._col_idx
        if available > 0:
            take = available if available < n else n  # implies: `take` ≤ `n`
            self._col_idx += take
            n -= take
            if n == 0:
                return
            self._cols = b""
            self._col_idx = 0
        width = self._font.width
        text = self._text
        nchars = len(text)
        while n > 0 and self._next_char_idx < nchars:
            group = width(text[self._next_char_idx])
            if self._pending_spacer:
                group += 1
            if group > n:
                for _ in range(n):
                    self.next_column()
                return
            n -= group
            self._next_char_idx += 1
            self._pending_spacer = True
            self._cols = b""
            self._col_idx = 0


class _FixedColumnReader:
    """Cursor over a byte sequence of ``columns``, with the same operations as ``_ColumnReader``.

    ``next_column`` returns the next byte, then ``None`` after the last one, and keeps returning ``None``.
    ``skip(n)`` moves the cursor ``n`` bytes forward and stops at the end; ``n <= 0`` does nothing.
    ``reset`` moves the cursor back to the first byte.

    The reader keeps a reference to ``columns`` and does not copy it. Do not mutate ``columns``
    after the constructor has returned: this would change what the reader returns and could
    produce subtle errors.
    """

    __slots__ = ("_cols", "_idx")

    def __init__(self, columns: bytes) -> None:
        self._cols = columns
        self._idx = 0

    def next_column(self) -> int | None:
        if self._idx >= len(self._cols):
            return None
        b = self._cols[self._idx]
        self._idx += 1
        return b

    def reset(self) -> None:
        self._idx = 0

    def skip(self, n: int) -> None:
        if n <= 0:
            return
        idx = self._idx + n
        limit = len(self._cols)
        self._idx = limit if idx > limit else idx


class ScreenText:
    """``ScreenText`` takes a plain ``text`` (Python string) and prepares it for the LED matrix.
    Passing a ``ScreenText`` to display methods avoids repeating the preprocessing needed to display
    plain strings. Showing a ``ScreenText`` does not change it, so you can create it once and show
    it again and again. This is more efficient if you want to display the same ``text`` many times.

    A ``ScreenText`` can also tell you how the text would be displayed, without drawing anything:
    - ``width``: the number of LED columns the text needs, including the blank column between
      letters. It is counted the first time you ask and remembered after that.
    - ``column_count_wider_than(limit)``: ``True`` if the text needs more than ``limit`` columns.
      For a long text this can answer sooner than ``width``, because it stops counting early.
    Use these to decide whether the text fits on the display or has to scroll.

    ``centered(text)`` returns a ``ScreenText`` too.
    An empty text is allowed: its ``width`` is 0 and it shows as a blank display.
    """

    __slots__ = ("_text", "_font", "_columns", "_width")

    def __init__(self, text: str, font: Font = FONT) -> None:
        self._text = text if isinstance(text, str) else str(text)
        self._font = font
        self._columns = None
        self._width = None

    @classmethod
    def _from_columns(cls, columns: bytes) -> ScreenText:
        """A picture that is already column bytes. ``width`` is ``len(columns)``."""
        obj = object.__new__(cls)
        obj._text = ""
        obj._font = FONT
        obj._columns = columns
        obj._width = len(columns)
        return obj

    @property
    def width(self) -> int:
        """Columns this text occupies, including spacers. Computed once (and remembered after that)."""
        cached = self._width
        if cached is None:
            cached = _column_count(self._text, self._font)
            self._width = cached
        return cached

    def column_count_wider_than(self, limit: int) -> bool:
        """``True`` if this text needs more than ``limit`` columns, otherwise ``False``.

        Stops counting as soon as the count exceeds ``limit``, so it can be faster than ``width``
        for a long text. If ``width`` has already been computed, it just compares that value.
        Unlike ``width``, it does not remember its own result.

        Raises ``ValueError`` if ``limit`` is negative.  An empty string has width 0.
        """
        if limit < 0:
            raise ValueError(f"limit must be >= 0, got {limit}")
        cached = self._width
        if cached is not None:
            return cached > limit
        return _column_count_wider_than(self._text, self._font, limit)

    def _reader(self) -> _ColumnReader | _FixedColumnReader:
        columns = self._columns
        if columns is not None:
            return _FixedColumnReader(columns)
        return _ColumnReader(self._text, self._font)


def _reader_for(content: str | int | float | ScreenText) -> _ColumnReader | _FixedColumnReader:
    """A fresh reader. A ``str`` does not allocate a ``ScreenText``."""
    if isinstance(content, ScreenText):
        return content._reader()
    return _ColumnReader(str(content), FONT)


def centered(content: str | int | float | ScreenText) -> ScreenText:
    """Return a ``ScreenText`` exactly ``WIDTH`` columns wide, with ``content`` centered.

    ``content`` may be a ``str``, an ``int``, a ``float`` (shown as ``str(content)``), or
    a ``ScreenText``. Text that fits is padded with blanks about equally on both sides; if
    an odd number of blank column then the extra blank goes on the right. Text that is wider
    keeps ``WIDTH`` columns and drops the extra on the right when the overflow is odd. The
    result's ``width`` is ``WIDTH``.
    Calling ``centered`` on that result returns the same picture.

    This measures the text once and builds a 5-column picture. Do it once and reuse the result.
    """
    if not isinstance(content, ScreenText):
        content = ScreenText(str(content))
    w = content.width
    out = bytearray(WIDTH)
    reader = content._reader()
    # ``width`` equals the number of columns the reader yields (a font's ``width(ch)`` is
    # ``len(glyph(ch))``), so ``next_column`` never returns ``None`` below. A font that breaks
    # this fails here with a ``TypeError`` instead of drawing a quietly shortened picture.
    if w <= WIDTH:
        pad = (WIDTH - w) // 2
        for i in range(w):
            out[pad + i] = reader.next_column()
    else:
        reader.skip((w - WIDTH) // 2)
        for i in range(WIDTH):
            out[i] = reader.next_column()
    return ScreenText._from_columns(bytes(out))

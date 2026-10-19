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
        count += 1 + width(text[i])
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
        count += 1 + width(text[i])
        if count > limit:
            return True
    return False


class _ColumnReader:
    """Cursor over a string's glyph columns. One reader per display call.

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
        remaining = n
        available = len(self._cols) - self._col_idx
        if available > 0:
            take = available if available < remaining else remaining
            self._col_idx += take
            remaining -= take
            if remaining == 0:
                return
            self._cols = b""
            self._col_idx = 0
        width = self._font.width
        text = self._text
        nchars = len(text)
        while remaining > 0 and self._next_char_idx < nchars:
            group = width(text[self._next_char_idx])
            if self._pending_spacer:
                group += 1
            if group > remaining:
                for _ in range(remaining):
                    self.next_column()
                return
            remaining -= group
            self._next_char_idx += 1
            self._pending_spacer = True
            self._cols = b""
            self._col_idx = 0


class _FixedColumnReader:
    """Cursor over a prepared column-byte string. Used by ``centered``."""

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
    """Prepared text: the string, the font, and the column count.

    ``width`` is the number of columns, including the spacer between characters.
    It is computed the first time you ask and then remembered. Building a
    ``ScreenText`` does not draw anything, and a display call does not change it.

    ``column_count_wider_than(limit)`` answers whether the text needs more than
    ``limit`` columns. It can stop before the end of a long string. Use it
    (or compare ``width`` with the display width) to choose ``show_*`` for text
    that fits and ``scroll_*`` for text that does not.
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
        """Columns this text occupies, including spacers. Computed once."""
        cached = self._width
        if cached is None:
            cached = _column_count(self._text, self._font)
            self._width = cached
        return cached

    def column_count_wider_than(self, limit: int) -> bool:
        """True when this text occupies more than ``limit`` columns.

        Raises ``ValueError`` if ``limit`` is negative. An empty string has width 0.
        Stops at the first character that makes the answer true.
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


def _reader_for(content: object) -> _ColumnReader | _FixedColumnReader:
    """A fresh reader. A ``str`` does not allocate a ``ScreenText``."""
    if isinstance(content, ScreenText):
        return content._reader()
    return _ColumnReader(str(content), FONT)


def _wider_than(content: object, limit: int) -> bool:
    if isinstance(content, ScreenText):
        return content.column_count_wider_than(limit)
    return _column_count_wider_than(str(content), FONT, limit)


def centered(content: object) -> ScreenText:
    """Return a ``ScreenText`` exactly ``WIDTH`` columns wide, with ``content`` centered.

    ``content`` may be a ``str``, a number, or a ``ScreenText``. Anything else is
    drawn as ``str(content)``. Text that fits is padded with blanks; a spare blank
    goes on the right. Text that is wider keeps ``WIDTH`` columns and drops the
    extra on the right when the overflow is odd. The result's ``width`` is ``WIDTH``.
    Calling ``centered`` on that result returns the same picture.

    This measures the text once and builds a 5-column picture. Do it once and
    reuse the result.
    """
    if isinstance(content, ScreenText):
        src = content
    else:
        src = ScreenText(str(content))
    w = src.width
    out = bytearray(WIDTH)
    reader = src._reader()
    if w <= WIDTH:
        pad = (WIDTH - w) // 2
        for i in range(w):
            col = reader.next_column()
            if col is None:
                break
            out[pad + i] = col
    else:
        reader.skip((w - WIDTH) // 2)
        for i in range(WIDTH):
            col = reader.next_column()
            if col is None:
                break
            out[i] = col
    return ScreenText._from_columns(bytes(out))

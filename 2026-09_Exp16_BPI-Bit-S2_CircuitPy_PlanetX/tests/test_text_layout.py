"""
ScreenText and column readers (host, no board / no core.py).
"""

import pytest

from display._constants import WIDTH
from display.font_makecode_5.ink import FONT
from display.font_makecode_5.ink import Font
from display.text_layout import ScreenText, _ColumnReader, _FixedColumnReader, centered


class _TableFont(Font):
    """Stand-in font whose glyph is a character-to-bytes map. ``width`` is the length of that glyph."""

    def __init__(self, table: dict[str, bytes]) -> None:
        self._table = table

    def glyph(self, ch: str) -> bytes:
        return self._table[ch]

    def width(self, ch: str) -> int:
        return len(self._table[ch])


class _SameGlyph(Font):
    """Stand-in font that returns the same glyph for every character."""

    def __init__(self, glyph: bytes) -> None:
        self._glyph = glyph

    def glyph(self, ch: str) -> bytes:
        return self._glyph

    def width(self, ch: str) -> int:
        return len(self._glyph)


def _drain(text: str, font: Font | None = None) -> list[int]:
    """Feed until ``None``; does not invent a scroll-out tail."""
    kwargs = {} if font is None else {"font": font}
    reader = _ColumnReader(text, **kwargs)
    cols: list[int] = []
    while True:
        col = reader.next_column()
        if col is None:
            break
        cols.append(col)
    return cols


def test_font_requires_glyph_and_width():
    """``Font`` implements neither ``glyph`` nor ``width``.

    - Covers: a base ``width`` that builds the glyph in order to measure it.
    - How: call both methods on a bare ``Font``.
    """
    font = Font()
    with pytest.raises(NotImplementedError):
        font.glyph("A")
    with pytest.raises(NotImplementedError):
        font.width("A")


def test_bootstrap_first_glyph_has_no_spacer():
    """The first glyph is emitted as-is; no leading or trailing blank.

    - Covers: a leftover pending-spacer on construction, or a trailing pad
      after a single ink-bearing glyph.
    - How: a stand-in font returns one two-byte glyph; drain equals those two bytes.
    """
    cols = _drain("X", font=_SameGlyph(b"\x01\x02"))
    assert cols == [1, 2]


def test_one_spacer_exactly_once_between_two_glyphs():
    """Adjacent glyphs get exactly one 0 between them.

    - Covers: missing spacer (collision), doubled spacer, or a trailing 0
      after the second glyph.
    - How: injected ``A``/``B`` each one ink byte.
    """
    table = {"A": b"\x0a", "B": b"\x0b"}
    cols = _drain("AB", font=_TableFont(table))
    assert cols == [0x0A, 0, 0x0B]


def test_space_is_three_blanks_with_spacers_around_it():
    """Space is three zeros; the uniform spacer still sits on both sides.

    Interior ``"A B"`` is then five blank columns — same as the former
    4-column space with a spacer only after ink.

    - Covers: dropping the prepend before a blank, omitting the spacer after
      it, or keeping space at 4 authored columns (would yield six blanks).
    - How: ``A`` + 3-zero space + ``B``.
    """
    table = {
        "A": b"\x0a",
        " ": b"\x00\x00\x00",
        "B": b"\x0b",
    }
    cols = _drain("A B", font=_TableFont(table))
    assert cols == [0x0A, 0, 0, 0, 0, 0, 0x0B]


def test_trailing_space_has_no_extra_spacer():
    """A last-character space is three blanks after the preceding spacer, not four.

    - Covers: emitting a pending spacer after the last glyph (would restore
      the old trailing-space width of 4).
    - How: ``A`` then space.
    """
    table = {"A": b"\x0a", " ": b"\x00\x00\x00"}
    cols = _drain("A ", font=_TableFont(table))
    assert cols == [0x0A, 0, 0, 0, 0]


def test_no_trailing_spacer_after_last_glyph():
    """Exhaustion returns ``None`` without a synthetic pad after the last glyph.

    - Covers: append-after semantics leaking a trailing 0 that would shift
      fit-on-screen centering.
    - How: one glyph; drain length equals the ink length, last byte is the ink byte.
    """
    cols = _drain("Z", font=_SameGlyph(b"\xff"))
    assert cols == [0xFF]
    extra = _ColumnReader("Z", font=_SameGlyph(b"\xff"))
    for _ in cols:
        extra.next_column()
    assert extra.next_column() is None


def test_twenty_seven_point_three_column_sequence():
    """``"27.3"`` is digit, spacer, digit, spacer, period, spacer, digit.

    - Covers: composition of the real accessor with prepend-spacer sequencing
      on the motivating decimal string; a trailing spacer after ``3``.
    - How: drain the live feeder; compare to the Phase-2-pinned slices with
      a 0 between each pair. Last byte is ``3``'s last ink column.
    """
    two = FONT.glyph("2")
    seven = FONT.glyph("7")
    period = FONT.glyph(".")
    three = FONT.glyph("3")
    expected = (
        list(two) + [0] + list(seven) + [0] + list(period) + [0] + list(three)
    )
    cols = _drain("27.3")
    assert cols == expected
    assert cols[-1] == three[-1]


def test_narrow_pair_fits_wide_pair_scrolls():
    """Trimmed ``"!!"`` totals ≤ WIDTH; ``"ST"`` totals > WIDTH.

    - Covers: a trim-logic change silently moving strings across the
      fit-on-screen vs scroll boundary (§ 3b).
    - How: drain each pair; compare the column count to ``WIDTH``.
    """
    bang_bang = _drain("!!")
    st = _drain("ST")
    assert bang_bang == [0x17, 0, 0x17]
    assert len(bang_bang) <= WIDTH
    assert len(st) > WIDTH


def test_stand_in_font_count_matches_its_drain():
    """A stand-in font's ``column_count`` equals a full drain of that same font.

    - Covers: the count using a different character source than ``next_column``.
    - How: ``"AB"`` with 2-column then 1-column ink. The count matches the drain, and the cursor stays at the first column.
    """
    font = _TableFont({"A": b"\x0a\x0b", "B": b"\x0c"})
    prepared = ScreenText("AB", font=font)
    reader = prepared._reader()
    drained = _drain("AB", font=font)
    assert drained == [0x0A, 0x0B, 0, 0x0C]
    assert prepared.width == len(drained)
    assert prepared.column_count_wider_than(len(drained)) is False
    assert prepared.column_count_wider_than(len(drained) - 1) is True
    assert reader.next_column() == drained[0]
    assert _drain("") == []


def test_reset_replays_from_the_first_column():
    """``reset`` makes ``next_column`` yield the same columns again.

    - Covers: a second pass keeping the spacer from the previous glyph, or resuming mid-glyph.
    - How: drain ``"AB"`` on a stand-in font, reset, drain again. After one column, reset, that column repeats.
    """
    font = _TableFont({"A": b"\x0a\x0b", "B": b"\x0c"})
    feeder = _ColumnReader("AB", font=font)
    first = []
    while True:
        col = feeder.next_column()
        if col is None:
            break
        first.append(col)
    assert first == [0x0A, 0x0B, 0, 0x0C]
    feeder.reset()
    second = []
    while True:
        col = feeder.next_column()
        if col is None:
            break
        second.append(col)
    assert second == first
    feeder.reset()
    assert feeder.next_column() == 0x0A
    feeder.reset()
    assert feeder.next_column() == 0x0A


def test_column_count_matches_a_full_drain():
    """``column_count`` equals a full ``next_column`` drain of the built-in font.

    - Covers: the length-byte path disagreeing with the ink path.
    - How: ``""``, ``"!"``, ``"7"``, ``"Hallo"``, and a character outside ASCII.
    """
    for text in ("", "A", "AB", "A B", "HELLO", "!", "7", "Hallo", "☃"):
        assert ScreenText(text).width == len(_drain(text))
    assert ScreenText(" ").width == 3


def test_column_count_wider_than_matches_a_drain():
    """``column_count_wider_than`` is true exactly when a full drain is longer than the limit.

    - Covers: the length-byte walk disagreeing with the ink path at the fit boundary.
    - How: empty, one column, exact ``WIDTH``, one over ``WIDTH``, and a long string.
      Each is compared to its own drain length and to ``WIDTH``. The feeder's first column is still unread.
    """
    for text in ("", "!", "7", "0!", "Hallo"):
        prepared = ScreenText(text)
        reader = prepared._reader()
        width = len(_drain(text))
        assert prepared.column_count_wider_than(width) is False
        if width:
            assert prepared.column_count_wider_than(width - 1) is True
        assert prepared.column_count_wider_than(WIDTH) is (width > WIDTH)
        assert reader.next_column() == (_drain(text)[0] if width else None)


def test_column_count_wider_than_rejects_a_negative_limit():
    """A negative ``limit`` raises ``ValueError``.

    - Covers: treating an empty string as wider than a negative column count, or accepting the limit.
    - How: empty text and ``"A"``, each with ``limit=-1``. ``limit=0`` on empty text is false.
    """
    empty = ScreenText("")
    with pytest.raises(ValueError, match="limit must be >= 0"):
        empty.column_count_wider_than(-1)
    assert empty.column_count_wider_than(0) is False
    with pytest.raises(ValueError, match="limit must be >= 0"):
        ScreenText("A").column_count_wider_than(-1)


class _CountingFont(Font):
    """Counts ``glyph`` and ``width`` calls. Forwards to an inner font."""

    def __init__(self, inner: Font) -> None:
        self._inner = inner
        self.glyph_calls = 0
        self.width_calls = 0

    def glyph(self, ch: str) -> bytes:
        self.glyph_calls += 1
        return self._inner.glyph(ch)

    def width(self, ch: str) -> int:
        self.width_calls += 1
        return self._inner.width(ch)


def test_width_is_cached():
    """``.width`` measures the string once.

    - Covers: a second ``.width`` walking the font again.
    - How: a counting font; two ``.width`` reads; the second adds no ``width`` calls.
    """
    font = _CountingFont(_TableFont({"A": b"\x01\x02", "B": b"\x03"}))
    prepared = ScreenText("AB", font=font)
    assert prepared.width == 4
    calls = font.width_calls
    assert prepared.width == 4
    assert font.width_calls == calls


def test_next_column_stays_none_after_the_end():
    """``next_column`` keeps returning ``None`` after the text is finished.

    - Covers: a later call raising, or restarting the string.
    - How: drain ``"A"`` on a one-byte font, then two more calls.
    """
    reader = _ColumnReader("A", font=_SameGlyph(b"\x11"))
    assert reader.next_column() == 0x11
    assert reader.next_column() is None
    assert reader.next_column() is None


def test_skip_whole_first_glyph_does_not_call_glyph():
    """Skipping a whole first glyph uses ``width`` only.

    - Covers: ``glyph`` being called for a character the skip does not cut.
    - How: ``"AB"``, skip 2 (all of ``A``). ``glyph`` calls stay 0. The drain is the tail.
    """
    font = _CountingFont(_TableFont({"A": b"\x0a\x0b", "B": b"\x0c"}))
    reader = _ColumnReader("AB", font=font)
    reader.skip(2)
    assert font.glyph_calls == 0
    assert _drain_from(reader) == [0, 0x0C]


def test_skip_into_the_next_glyph_stays_in_sync():
    """A skip that ends inside the next glyph, or on its spacer, calls ``glyph`` once.

    - Covers: a width-only stop on the spacer leaving the next ``next_column`` one column ahead.
    - How: skip 3 of ``"AB"`` (``A`` plus the spacer) and skip 4 (through ``B``'s first column is the whole string's 4).
      Also skip 0 and a negative count, which leave the reader at the start.
    """
    font = _CountingFont(_TableFont({"A": b"\x0a\x0b", "B": b"\x0c"}))
    reader = _ColumnReader("AB", font=font)
    reader.skip(3)
    assert font.glyph_calls == 1
    assert _drain_from(reader) == [0x0C]

    font2 = _CountingFont(_TableFont({"A": b"\x0a\x0b", "B": b"\x0c"}))
    on_spacer = _ColumnReader("AB", font=font2)
    on_spacer.skip(2)
    assert font2.glyph_calls == 0
    assert on_spacer.next_column() == 0
    assert font2.glyph_calls == 1
    assert on_spacer.next_column() == 0x0C

    untouched = _ColumnReader("AB", font=_TableFont({"A": b"\x0a\x0b", "B": b"\x0c"}))
    untouched.skip(0)
    untouched.skip(-3)
    assert _drain_from(untouched) == [0x0A, 0x0B, 0, 0x0C]


def test_fixed_column_reader_skip():
    """``_FixedColumnReader.skip`` advances an index into the prepared bytes.

    - Covers: a skip past the end raising, or ``n <= 0`` moving the index.
    - How: bytes ``1, 2, 3``. Skip 1, then the rest. A fresh reader skips 0 and a negative count.
    """
    reader = _FixedColumnReader(b"\x01\x02\x03")
    reader.skip(1)
    assert _drain_from(reader) == [2, 3]
    reader.reset()
    reader.skip(0)
    reader.skip(-1)
    assert reader.next_column() == 1
    reader.skip(10)
    assert reader.next_column() is None


def test_centered_width_and_inputs():
    """``centered`` is ``WIDTH`` columns wide for a string, an int, and a ``ScreenText``, and repeating it is a no-op.

    - Covers: a result whose width is the source width, or a second ``centered`` shifting the picture.
    - How: ``"!"``, ``7``, and ``ScreenText("A")``. Compare column bytes of one call and two.
    """
    for content in ("!", 7, ScreenText("A")):
        once = centered(content)
        twice = centered(once)
        assert once.width == WIDTH
        assert _drain_from(twice._reader()) == _drain_from(once._reader())


def _drain_from(reader) -> list[int]:
    cols = []
    while True:
        col = reader.next_column()
        if col is None:
            return cols
        cols.append(col)

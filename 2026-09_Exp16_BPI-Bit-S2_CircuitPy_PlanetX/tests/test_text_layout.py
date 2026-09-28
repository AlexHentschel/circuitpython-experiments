"""
Spaced glyph-column feeder (host, no board / no core.py).
"""

from display._constants import WIDTH
from display.font_makecode_5 import glyph_ink
from display.text_layout import SpacedGlyphColumnFeeder


def _drain(text: str, lookup=None) -> list[int]:
    """Feed until ``None``; does not invent a scroll-out tail."""
    kwargs = {} if lookup is None else {"lookup": lookup}
    feeder = SpacedGlyphColumnFeeder(text, **kwargs)
    cols: list[int] = []
    while True:
        col = feeder.next_column()
        if col is None:
            break
        cols.append(col)
    return cols


def test_bootstrap_first_glyph_has_no_spacer():
    """The first glyph is emitted as-is; no leading or trailing blank.

    - Covers: a leftover pending-spacer on construction, or a trailing pad
      after a single ink-bearing glyph.
    - How: injected lookup returns one two-byte glyph; drain equals those two bytes.
    """
    cols = _drain("X", lookup=lambda ch: b"\x01\x02")
    assert cols == [1, 2]


def test_one_spacer_exactly_once_between_two_glyphs():
    """Adjacent glyphs get exactly one 0 between them.

    - Covers: missing spacer (collision), doubled spacer, or a trailing 0
      after the second glyph.
    - How: injected ``A``/``B`` each one ink byte.
    """
    table = {"A": b"\x0a", "B": b"\x0b"}
    cols = _drain("AB", lookup=lambda ch: table[ch])
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
    cols = _drain("A B", lookup=lambda ch: table[ch])
    assert cols == [0x0A, 0, 0, 0, 0, 0, 0x0B]


def test_trailing_space_has_no_extra_spacer():
    """A last-character space is three blanks after the preceding spacer, not four.

    - Covers: emitting a pending spacer after the last glyph (would restore
      the old trailing-space width of 4).
    - How: ``A`` then space.
    """
    table = {"A": b"\x0a", " ": b"\x00\x00\x00"}
    cols = _drain("A ", lookup=lambda ch: table[ch])
    assert cols == [0x0A, 0, 0, 0, 0]


def test_no_trailing_spacer_after_last_glyph():
    """Exhaustion returns ``None`` without a synthetic pad after the last glyph.

    - Covers: append-after semantics leaking a trailing 0 that would shift
      fit-on-screen centering.
    - How: one glyph; drain length equals the ink length, last byte is the ink byte.
    """
    cols = _drain("Z", lookup=lambda ch: b"\xff")
    assert cols == [0xFF]
    extra = SpacedGlyphColumnFeeder("Z", lookup=lambda ch: b"\xff")
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
    two = glyph_ink("2")
    seven = glyph_ink("7")
    period = glyph_ink(".")
    three = glyph_ink("3")
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

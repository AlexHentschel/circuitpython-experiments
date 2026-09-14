"""
Single-glyph ``glyph_ink`` accessor (host, no board / no core.py).

Sequence-level spacing belongs in ``test_text_layout.py``.
"""

from display._constants import WIDTH
from display.font_makecode_5 import glyph_ink


def _cols_from_rows(rows: list[str]) -> bytes:
    """Encode a 5-row ``#``/``.`` picture as column-major bytes (bit 0 = top)."""
    cols = [0] * WIDTH
    for row_i, row in enumerate(rows):
        for col_i, cell in enumerate(row):
            if cell == "#":
                cols[col_i] |= 1 << row_i
    return bytes(cols)


def _trim_ink(cols: bytes) -> bytes:
    """Drop leading and trailing all-zero columns from a native-width glyph."""
    start = next(i for i, b in enumerate(cols) if b)
    end = len(cols) - next(i for i, b in enumerate(reversed(cols)) if b)
    return cols[start:end]


def test_margined_glyph_is_trimmed_and_owes_a_spacer():
    """A letter with a blank trailing column returns the trimmed slice + True.

    - Covers: accessor returning a full ``WIDTH`` record, or ``needs_spacer=False``,
      for an ink-bearing glyph that has a native self-margin.
    - How: hand-drawn ``A`` (DAL shape, independent of the generated table);
      encode → trim locally; compare to ``glyph_ink("A")``.
    """
    native = _cols_from_rows(
        [
            ".##..",
            "#..#.",
            "####.",
            "#..#.",
            "#..#.",
        ]
    )
    ink, needs_spacer = glyph_ink("A")
    assert ink == _trim_ink(native)
    assert len(ink) < WIDTH
    assert needs_spacer is True


def test_full_width_glyph_keeps_width_and_owes_a_spacer():
    """``7`` fills every column, so the accessor returns ``WIDTH`` bytes + True.

    - Covers: trimming a glyph that has no blank margin, or dropping ``needs_spacer``.
    - How: hand-drawn ``7``; encode; compare length and bytes.
    """
    native = _cols_from_rows(
        [
            "#####",
            "...#.",
            "..#..",
            ".#...",
            "#....",
        ]
    )
    ink, needs_spacer = glyph_ink("7")
    assert ink == native
    assert len(ink) == WIDTH
    assert needs_spacer is True


def test_space_is_four_blank_columns_without_a_spacer():
    """Space is a 4-column blank and does not owe a following spacer.

    - Covers: treating space as a full-``WIDTH`` pass-through, trimming it to
      empty, or setting ``needs_spacer=True`` on a blank glyph.
    - How: ``glyph_ink(" ") == (bytes(4), False)``.
    """
    ink, needs_spacer = glyph_ink(" ")
    assert ink == bytes(4)
    assert needs_spacer is False


def test_unknown_is_full_width_blank_without_a_spacer():
    """Out-of-table characters (NUL, empty string) are ``WIDTH`` zeros + False.

    - Covers: ``ord``/slice exception, substituting ``?``, or ``needs_spacer=True``.
    - How: ``glyph_ink("\\x00")`` and ``glyph_ink("")`` equal ``(bytes(WIDTH), False)``.
    """
    assert glyph_ink("\x00") == (bytes(WIDTH), False)
    assert glyph_ink("") == (bytes(WIDTH), False)


def test_period_and_three_match_hand_drawn_slices():
    """The ``.`` and ``3`` glyphs from the ``"27.3"`` example trim correctly.

    - Covers: wrong occupied span on a deeply-inset punctuation mark (``.``)
      or on a trailing-margined digit (``3``); sets up sequence tests in
      ``test_text_layout.py`` without performing them.
    - How: hand-drawn grids → local trim; compare to ``glyph_ink``.
    """
    period_native = _cols_from_rows(
        [
            ".....",
            ".....",
            ".....",
            ".#...",
            ".....",
        ]
    )
    three_native = _cols_from_rows(
        [
            "####.",
            "...#.",
            "..#..",
            "#..#.",
            ".##..",
        ]
    )
    period_ink, period_needs = glyph_ink(".")
    three_ink, three_needs = glyph_ink("3")
    assert period_ink == _trim_ink(period_native)
    assert len(period_ink) == 1
    assert period_needs is True
    assert three_ink == _trim_ink(three_native)
    assert three_needs is True

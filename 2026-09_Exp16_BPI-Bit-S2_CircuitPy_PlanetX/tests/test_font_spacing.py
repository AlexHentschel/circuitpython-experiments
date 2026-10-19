"""
Single-glyph ``FONT.glyph`` accessor (host, no board / no core.py).

Sequence-level spacing belongs in ``test_text_layout.py``.
"""

from display._constants import WIDTH
from display.font_makecode_5.ink import _TOFU_INK, FONT
from display.font_makecode_5.spaced_glyphs import (
    _ASCII_END,
    _ASCII_START,
    _RECORD_STRIDE,
    _SPACED_GLYPHS,
)
from display.icons import EMOJIS, EMOJI_NAMES


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


def test_margined_glyph_is_trimmed():
    """A letter with a blank trailing column returns the trimmed slice.

    - Covers: accessor returning a full ``WIDTH`` record for an ink-bearing
      glyph that has a native self-margin.
    - How: hand-drawn ``A`` (DAL shape, independent of the generated table);
      encode → trim locally; compare to ``FONT.glyph("A")``.
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
    ink = FONT.glyph("A")
    assert ink == _trim_ink(native)
    assert len(ink) < WIDTH


def test_full_width_glyph_keeps_width():
    """``7`` fills every column, so the accessor returns ``WIDTH`` bytes.

    - Covers: trimming a glyph that has no blank margin.
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
    ink = FONT.glyph("7")
    assert ink == native
    assert len(ink) == WIDTH


def test_space_is_three_blank_columns():
    """Space is a 3-column blank (the uniform inter-glyph spacer is not stored).

    - Covers: treating space as a full-``WIDTH`` pass-through, trimming it to
      empty, or keeping the former 4-column authored width.
    - How: ``FONT.glyph(" ") == bytes(3)``.
    """
    assert FONT.glyph(" ") == bytes(3)


def test_unknown_is_tofu():
    """Out-of-table characters are tofu, not a hole or ``?``.

    - Covers: ``ord``/slice exception, substituting ``?``, a full-``WIDTH`` blank,
      or omitting the glyph.
    - How: NUL, empty string, and ``☐`` (U+25A1) equal ``_TOFU_INK``.
    """
    assert FONT.glyph("\x00") == _TOFU_INK
    assert FONT.glyph("") == _TOFU_INK
    assert FONT.glyph("☐") == _TOFU_INK


def test_period_and_three_match_hand_drawn_slices():
    """The ``.`` and ``3`` glyphs from the ``"27.3"`` example trim correctly.

    - Covers: wrong occupied span on a deeply-inset punctuation mark (``.``)
      or on a trailing-margined digit (``3``); sets up sequence tests in
      ``test_text_layout.py`` without performing them.
    - How: hand-drawn grids → local trim; compare to ``FONT.glyph``.
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
    period_ink = FONT.glyph(".")
    three_ink = FONT.glyph("3")
    assert period_ink == _trim_ink(period_native)
    assert len(period_ink) == 1
    assert three_ink == _trim_ink(three_native)


def test_spaced_glyphs_table_covers_ascii_printable_range():
    """``_SPACED_GLYPHS`` is one ``WIDTH + 1``-byte record per ASCII 32..126.

    - Covers: truncated or padded table, stride drift vs ``WIDTH + 1``.
    - How: ``len(_SPACED_GLYPHS) == (_ASCII_END - _ASCII_START + 1) * _RECORD_STRIDE``.
    """
    assert len(_SPACED_GLYPHS) == (_ASCII_END - _ASCII_START + 1) * _RECORD_STRIDE


def test_tofu_matches_stripped_small_square():
    """Stripping ``icons.py`` ``SMALL_SQUARE`` produces the same ink as tofu.

    - Covers: ``_TOFU_INK`` drifting from the named icon, or keeping the icon's
      lead/trail zeros.
    - How: slice ``EMOJIS`` at ``EMOJI_NAMES.index("SMALL_SQUARE")``; drop leading
      and trailing zero columns; compare to ``_TOFU_INK``.
    """
    slot = EMOJI_NAMES.index("SMALL_SQUARE")
    native = EMOJIS[slot * WIDTH : (slot + 1) * WIDTH]
    assert _trim_ink(native) == _TOFU_INK


def test_font_width_is_the_length_byte_and_matches_the_glyph():
    """``FONT.width`` is the record's length byte, and it matches ``len(FONT.glyph)``.

    - Covers: the width copying the glyph, or disagreeing with the glyph for tofu and ASCII.
    - How: compare ``"A"`` to the table byte; compare several characters, including tofu, to ``len(FONT.glyph)``.
    """
    record = (ord("A") - _ASCII_START) * _RECORD_STRIDE
    assert FONT.width("A") == _SPACED_GLYPHS[record]
    assert type(FONT.width("A")) is int
    for ch in ("A", "!", " ", "7", "~", "", "\n", "☃"):
        assert FONT.width(ch) == len(FONT.glyph(ch))
    assert FONT.width("☃") == len(_TOFU_INK)

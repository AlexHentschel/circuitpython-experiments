"""
DAL pendolino3 → column-major glyph table (host, no PCF / no core.py).
"""

from display._constants import WIDTH
from display.font_makecode_5 import glyph_columns


def test_min_set_a_to_d_and_digits_are_nonzero():
    """Glyphs A–D and 0–9 are WIDTH bytes and not blank.

    - Covers: missing table entries / all-zero conversion for the Watch/letter minimum set.
    - How: ``glyph_columns(ch)`` for each; ``len == WIDTH`` and ``any(cols)``.
    """
    for ch in "ABCD0123456789":
        cols = glyph_columns(ch)
        assert len(cols) == WIDTH
        assert any(cols), f"glyph {ch!r} is blank"


def test_space_is_blank():
    """Space renders as WIDTH zero bytes (advance without pixels).

    - Covers: space looking like an unknown-char box, or missing from the table.
    - How: ``glyph_columns(" ") == bytes(WIDTH)``.
    """
    assert glyph_columns(" ") == bytes(WIDTH)


def test_unknown_is_blank():
    """Out-of-table characters (NUL, empty string) are blank, not a crash or box.

    - Covers: ``ord``/slice exception, or substituting ``?``.
    - How: ``glyph_columns("\\x00")`` and ``glyph_columns("")`` equal ``bytes(WIDTH)``.
    """
    assert glyph_columns("\x00") == bytes(WIDTH)
    assert glyph_columns("") == bytes(WIDTH)


def test_a_matches_converted_dal_shape():
    """``A`` matches the DAL-converted 5×5 (not FreeMono, not a blank).

    - Covers: row/column swap or bit-order slip in the vendor conversion.
    - How: decode column bytes to 5 row strings; equal the DAL ``A`` ASCII.
    """
    # DAL 'A' converted: .##.. / #..#. / ####. / #..#. / #..#.
    cols = glyph_columns("A")
    rows = [
        "".join("#" if (cols[c] >> r) & 1 else "." for c in range(WIDTH))
        for r in range(5)
    ]
    assert rows == [
        ".##..",
        "#..#.",
        "####.",
        "#..#.",
        "#..#.",
    ]


def test_zero_is_closed_loop():
    """Digit ``0`` has ink on both the top and bottom rows (a closed loop, not a ``C``).

    - Covers: conversion dropping the base or cap of ``0``.
    - How: decode to rows; ``rows[0]`` and ``rows[4]`` each have ≥2 ``#``.
    """
    cols = glyph_columns("0")
    rows = [
        "".join("#" if (cols[c] >> r) & 1 else "." for c in range(WIDTH))
        for r in range(5)
    ]
    assert rows[0].count("#") >= 2
    assert rows[4].count("#") >= 2

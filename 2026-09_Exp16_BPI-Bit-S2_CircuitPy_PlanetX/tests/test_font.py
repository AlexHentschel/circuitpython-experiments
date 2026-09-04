"""
DAL pendolino3 → column-major glyph table (host, no PCF / no core.py).
"""

from display._constants import WIDTH
from display.font_makecode_5 import glyph_columns


def test_min_set_a_to_d_and_digits_are_nonzero():
    for ch in "ABCD0123456789":
        cols = glyph_columns(ch)
        assert len(cols) == WIDTH
        assert any(cols), f"glyph {ch!r} is blank"


def test_space_is_blank():
    assert glyph_columns(" ") == bytes(WIDTH)


def test_unknown_is_blank():
    assert glyph_columns("\x00") == bytes(WIDTH)
    assert glyph_columns("") == bytes(WIDTH)


def test_a_matches_converted_dal_shape():
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
    cols = glyph_columns("0")
    rows = [
        "".join("#" if (cols[c] >> r) & 1 else "." for c in range(WIDTH))
        for r in range(5)
    ]
    assert rows[0].count("#") >= 2
    assert rows[4].count("#") >= 2

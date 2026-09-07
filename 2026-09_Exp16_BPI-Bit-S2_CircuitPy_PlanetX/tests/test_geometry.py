"""
LUT correctness tests for the BPI-Bit-S2 5×5 wiring.

Visual fixture (rotation=0) is the BananaPi / Exp09 sequential grid, authored
by hand from the published LED list -- not from ``row + 20 - column * 5``.
Rotations compose that fixture with standard 2D clockwise mapping, so a bug
in ``build_lut``'s stage-2 algebra cannot bless itself (shared-derivation hazard).
"""

import pytest

from display._constants import WIDTH, HEIGHT, NUM_PIXELS
from display.bitmap_codec import pattern_to_colmajor
from display.geometry import build_lut, xy_to_index


# Hand-authored physical strip indices at rotation=0.
# Top of board is row 0; edge connector is below row 4.
# Source: BananaPi Bit-S2 “5*5 LED Sequential List” / Exp09 ASCII map.
_VISUAL_ROT0 = (
    (20, 15, 10, 5, 0),
    (21, 16, 11, 6, 1),
    (22, 17, 12, 7, 2),
    (23, 18, 13, 8, 3),
    (24, 19, 14, 9, 4),
)


def _visual_index(rotation, x, y):
    """Look up strip index from the visual grid after a standard CW rotation.

    Stage 1 only: (x, y) -> (px, py). Stage 2 is the hand grid, not the formula.
    """
    if rotation == 0:
        px, py = x, y
    elif rotation == 90:
        px, py = WIDTH - 1 - y, x
    elif rotation == 180:
        px, py = WIDTH - 1 - x, HEIGHT - 1 - y
    else:  # 270
        px, py = y, HEIGHT - 1 - x
    return _VISUAL_ROT0[py][px]


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_shape(rotation):
    """Look-Up Table [LUT] is a ``bytearray`` of NUM_PIXELS entries.

    - Covers: wrong type (tuple/list) or length after a 5×5 swap.
    - How: ``build_lut(rotation)``; check type and ``len == NUM_PIXELS``.
    """
    lut = build_lut(rotation)
    assert isinstance(lut, bytearray)
    assert len(lut) == NUM_PIXELS


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_is_permutation(rotation):
    """LUT values are 0..NUM_PIXELS-1 each used once (a permutation of strip indices).

    - Covers: duplicate indices (two logical pixels → one LED) or holes.
    - How: ``sorted(lut) == list(range(NUM_PIXELS))``.
    """
    lut = build_lut(rotation)
    assert sorted(lut) == list(range(NUM_PIXELS))


# Corners + one interior cell, from the visual grid (not the wiring formula).
_CORNER_EXPECTATIONS = {
    0:   [((0, 0), 20), ((4, 0), 0), ((0, 4), 24), ((4, 4), 4), ((2, 2), 12)],
    90:  [((0, 0),  0), ((4, 0), 4), ((0, 4), 20), ((4, 4), 24), ((2, 2), 12)],
    180: [((0, 0),  4), ((4, 0), 24), ((0, 4), 0), ((4, 4), 20), ((2, 2), 12)],
    270: [((0, 0), 24), ((4, 0), 20), ((0, 4), 4), ((4, 4), 0), ((2, 2), 12)],
}


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_corner_and_interior_visual_fixture(rotation):
    """Corners + center match the hand sequential list after rotation.

    - Covers: origin/axis swap that still permutes 0..24 (would pass shape tests).
    - How: ``xy_to_index`` vs ``_CORNER_EXPECTATIONS`` (from the visual grid, not the formula).
    """
    lut = build_lut(rotation)
    for (x, y), expected in _CORNER_EXPECTATIONS[rotation]:
        got = xy_to_index(x, y, lut)
        assert got == expected, (
            f"rotation={rotation} xy=({x},{y}) expected {expected}, got {got}"
        )


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_matches_visual_fixture_every_cell(rotation):
    """Every (x, y) matches the visual fixture (independent of ``build_lut`` algebra).

    - Covers: interior cells wrong while corners stay correct.
    - How: full WIDTH×HEIGHT walk; ``xy_to_index`` vs ``_visual_index`` (hand grid + CW map).
    """
    lut = build_lut(rotation)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            assert xy_to_index(x, y, lut) == _visual_index(rotation, x, y), (
                f"rotation={rotation} (x, y)=({x}, {y})"
            )


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_xy_to_index_matches_direct_lut_indexing(rotation):
    """``xy_to_index(x, y, lut)`` is ``lut[x * HEIGHT + y]``.

    - Covers: helper using a different stride than the LUT layout.
    - How: every cell; helper vs raw indexing.
    """
    lut = build_lut(rotation)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            assert xy_to_index(x, y, lut) == lut[x * HEIGHT + y]


def test_build_lut_default_rotation_is_zero():
    """``build_lut()`` with no args equals ``build_lut(0)``.

    - Covers: default silently becoming 90/None.
    - How: equality of the two return values.
    """
    assert build_lut() == build_lut(0)


def test_build_lut_returns_fresh_instance():
    """Two calls without ``dest`` do not share a buffer.

    - Covers: returning a cached/module-global LUT that callers then mutate.
    - How: build twice; mutate ``a[0]``; ``b[0]`` must stay original.
    """
    a = build_lut(0)
    b = build_lut(0)
    assert a == b
    a[0] = 42
    assert b[0] != 42


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_build_lut_dest_writes_in_place_and_returns_same_object(rotation):
    """``dest=`` fills that buffer and returns it (identity, not a copy).

    - Covers: allocating a new array despite ``dest``; leaving ``dest`` empty.
    - How: pass a zeroed ``bytearray``; ``result is dest`` and equals a fresh ``build_lut``.
    """
    dest = bytearray(NUM_PIXELS)
    result = build_lut(rotation, dest=dest)
    assert result is dest
    assert result == build_lut(rotation)


def test_build_lut_dest_reuse_overwrites_previous_rotation():
    """Reusing ``dest`` replaces the previous rotation (no leftover indices).

    - Covers: only writing cells that changed, leaving rotation-0 crumbs.
    - How: ``build_lut(0, dest)`` then ``build_lut(90, dest)``; equal to a fresh 90° LUT.
    """
    dest = bytearray(NUM_PIXELS)
    build_lut(0, dest=dest)
    build_lut(90, dest=dest)
    assert dest == build_lut(90)


@pytest.mark.parametrize("bad_len", [0, NUM_PIXELS - 1, NUM_PIXELS + 1])
def test_build_lut_rejects_wrong_length_dest(bad_len):
    """``dest`` whose length is not NUM_PIXELS raises ``ValueError``.

    - Covers: silent truncate/pad of a mis-sized buffer.
    - How: ``bad_len`` in {0, 24, 26}; expect ``ValueError``.
    """
    with pytest.raises(ValueError):
        build_lut(0, dest=bytearray(bad_len))


def test_build_lut_invalid_rotation_leaves_dest_unmodified():
    """Rejected rotation must not half-write ``dest``.

    - Covers: filling dest then raising; caller seeing a torn LUT.
    - How: snapshot a valid LUT; ``build_lut(45, dest=...)`` raises; dest bytes unchanged.
    """
    dest = build_lut(0)
    snapshot = bytes(dest)
    with pytest.raises(ValueError):
        build_lut(45, dest=dest)
    assert bytes(dest) == snapshot


@pytest.mark.parametrize("negative, positive", [(-90, 270), (-180, 180), (-270, 90)])
def test_build_lut_negative_rotations_match_positive_equivalents(negative, positive):
    """``-90/-180/-270`` aliases equal the matching positive angles.

    - Covers: alias mapping inverted (e.g. -90 → 90 instead of 270).
    - How: pairwise equality of the two LUTs.
    """
    assert build_lut(negative) == build_lut(positive)


@pytest.mark.parametrize("bad", [1, 45, 89, 91, 135, 359, -1, -45, 360, -360, 450, 720])
def test_build_lut_rejects_non_canonical_rotations(bad):
    """Angles outside the accepted set raise ``ValueError`` (no silent wrap).

    - Covers: modulo wrap-around (45 → 0) or treating 360 as 0 without error.
    - How: parametrize near-miss and wrap candidates; expect ``ValueError``.
    """
    with pytest.raises(ValueError):
        build_lut(bad)


# 5×5 F — visually authored, then rotated by eye for the 90° fixture.
_F_PATTERN = """
# # # # .
# . . . .
# # # . .
# . . . .
# . . . .
"""

_F_PATTERN_ROT_90 = """
# # # # #
. . # . #
. . # . #
. . . . #
. . . . .
"""

_F_PATTERN_ROT_180 = """
. . . . #
. . . . #
. . # # #
. . . . #
. # # # #
"""

_F_PATTERN_ROT_270 = """
. . . . .
# . . . .
# . # . .
# . # . .
# # # # #
"""


def _pattern_to_cells(pattern):
    cols = pattern_to_colmajor(pattern)
    return {
        (x, y)
        for x in range(WIDTH)
        for y in range(HEIGHT)
        if (cols[x] >> y) & 1
    }


def _render_cells_at(cells, rotation):
    lut = build_lut(rotation)
    frame = bytearray(NUM_PIXELS)
    for x, y in cells:
        frame[lut[x * HEIGHT + y]] = 1
    return frame


def _rotate_cells_cw_90(cells, steps=1):
    for _ in range(steps % 4):
        cells = {(HEIGHT - 1 - y, x) for x, y in cells}
    return cells


_F_CELLS = _pattern_to_cells(_F_PATTERN)


@pytest.mark.parametrize("rotation, pre_rotated_pattern", [
    (0,   _F_PATTERN),
    (90,  _F_PATTERN_ROT_90),
    (180, _F_PATTERN_ROT_180),
    (270, _F_PATTERN_ROT_270),
])
def test_rotation_matches_hand_constructed_fixture(rotation, pre_rotated_pattern):
    """An F drawn at rotation=0, then LUT-rotated, matches an F pre-rotated by eye.

    - Covers: permutation-vs-rotation (right set of LEDs, wrong arrangement).
    - How: render F cells through ``build_lut(rotation)``; equal to rendering the
      hand-rotated ASCII at rotation=0. Fixtures authored visually, not from LUT algebra.
    """
    pre_rotated_cells = _pattern_to_cells(pre_rotated_pattern)
    assert _render_cells_at(_F_CELLS, rotation) == _render_cells_at(pre_rotated_cells, 0)


@pytest.mark.parametrize("steps, equivalent_rotation", [
    (0, 0),
    (1, 90),
    (2, 180),
    (3, 270),
    (4, 0),
])
def test_repeated_90cw_rotations_compose(steps, equivalent_rotation):
    """N× 90° CW on the pattern equals one ``build_lut`` call at N×90.

    - Covers: composition (90+90 ≠ 180 LUT, or 4×90 ≠ identity).
    - How: rotate F cells in software ``steps`` times; render at 0 vs render original at ``equivalent_rotation``.
    """
    rotated_cells = _rotate_cells_cw_90(_F_CELLS, steps=steps)
    assert _render_cells_at(rotated_cells, 0) == _render_cells_at(_F_CELLS, equivalent_rotation)

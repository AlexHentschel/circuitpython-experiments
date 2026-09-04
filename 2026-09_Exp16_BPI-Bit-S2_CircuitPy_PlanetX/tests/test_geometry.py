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
    lut = build_lut(rotation)
    assert isinstance(lut, bytearray)
    assert len(lut) == NUM_PIXELS


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_is_permutation(rotation):
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
    """Corners + center must match the hand-authored sequential list after rotation."""
    lut = build_lut(rotation)
    for (x, y), expected in _CORNER_EXPECTATIONS[rotation]:
        got = xy_to_index(x, y, lut)
        assert got == expected, (
            f"rotation={rotation} xy=({x},{y}) expected {expected}, got {got}"
        )


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_matches_visual_fixture_every_cell(rotation):
    """Full-grid check against the visual fixture (independent of build_lut algebra)."""
    lut = build_lut(rotation)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            assert xy_to_index(x, y, lut) == _visual_index(rotation, x, y), (
                f"rotation={rotation} (x, y)=({x}, {y})"
            )


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_xy_to_index_matches_direct_lut_indexing(rotation):
    lut = build_lut(rotation)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            assert xy_to_index(x, y, lut) == lut[x * HEIGHT + y]


def test_build_lut_default_rotation_is_zero():
    assert build_lut() == build_lut(0)


def test_build_lut_returns_fresh_instance():
    a = build_lut(0)
    b = build_lut(0)
    assert a == b
    a[0] = 42
    assert b[0] != 42


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_build_lut_dest_writes_in_place_and_returns_same_object(rotation):
    dest = bytearray(NUM_PIXELS)
    result = build_lut(rotation, dest=dest)
    assert result is dest
    assert result == build_lut(rotation)


def test_build_lut_dest_reuse_overwrites_previous_rotation():
    dest = bytearray(NUM_PIXELS)
    build_lut(0, dest=dest)
    build_lut(90, dest=dest)
    assert dest == build_lut(90)


@pytest.mark.parametrize("bad_len", [0, NUM_PIXELS - 1, NUM_PIXELS + 1])
def test_build_lut_rejects_wrong_length_dest(bad_len):
    with pytest.raises(ValueError):
        build_lut(0, dest=bytearray(bad_len))


def test_build_lut_invalid_rotation_leaves_dest_unmodified():
    dest = build_lut(0)
    snapshot = bytes(dest)
    with pytest.raises(ValueError):
        build_lut(45, dest=dest)
    assert bytes(dest) == snapshot


@pytest.mark.parametrize("negative, positive", [(-90, 270), (-180, 180), (-270, 90)])
def test_build_lut_negative_rotations_match_positive_equivalents(negative, positive):
    assert build_lut(negative) == build_lut(positive)


@pytest.mark.parametrize("bad", [1, 45, 89, 91, 135, 359, -1, -45, 360, -360, 450, 720])
def test_build_lut_rejects_non_canonical_rotations(bad):
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
    rotated_cells = _rotate_cells_cw_90(_F_CELLS, steps=steps)
    assert _render_cells_at(rotated_cells, 0) == _render_cells_at(_F_CELLS, equivalent_rotation)

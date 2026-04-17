"""
LUT correctness tests for ``display.geometry``.

The LUT bakes two transforms into a single ``bytearray`` lookup:
  (1) rotation: logical (x, y) -> physical (px, py)
  (2) progressive bottom-up wiring: idx = (H-1-py)*W + px

Each rotation is pinned by its four corner mappings; the corner set is
the minimal fixture that discriminates rotation from reflection and
identifies any off-by-one in either stage.
"""

import pytest

from display._constants import WIDTH, HEIGHT, NUM_PIXELS
from display.geometry import build_lut, xy_to_index


# ---------------------------------------------------------------------------
# Shape and element-range invariants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_shape(rotation):
    lut = build_lut(rotation)
    assert isinstance(lut, bytearray)
    assert len(lut) == NUM_PIXELS


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_is_permutation(rotation):
    """Every strip index appears exactly once -- LUT is a bijection."""
    lut = build_lut(rotation)
    assert sorted(lut) == list(range(NUM_PIXELS))


# ---------------------------------------------------------------------------
# Per-rotation corner mappings.
#
# Reference table for rotation=0 (from geometry.build_lut docstring):
#   (0, 0) -> 56  (top-left logical  -> top-left of strip's top row)
#   (7, 0) -> 63  (top-right logical)
#   (0, 7) ->  0  (bottom-left logical -> strip start)
#   (7, 7) ->  7  (bottom-right logical)
#
# Other rotations derived by composing Stage 1 (rotation) with Stage 2
# (wiring: idx = (H-1-py)*W + px).
# ---------------------------------------------------------------------------

_CORNER_EXPECTATIONS = {
    0:   [((0, 0), 56), ((7, 0), 63), ((0, 7),  0), ((7, 7),  7)],
    90:  [((0, 0), 63), ((0, 7), 56), ((7, 0),  7), ((7, 7),  0)],
    180: [((0, 0),  7), ((7, 0),  0), ((0, 7), 63), ((7, 7), 56)],
    270: [((0, 0),  0), ((0, 7),  7), ((7, 0), 56), ((7, 7), 63)],
}


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_corner_mappings(rotation):
    lut = build_lut(rotation)
    for (x, y), expected in _CORNER_EXPECTATIONS[rotation]:
        assert xy_to_index(x, y, lut) == expected, (
            "rotation={} xy=({}, {}) expected idx {}, got {}".format(
                rotation, x, y, expected, xy_to_index(x, y, lut)
            )
        )


def test_xy_to_index_matches_direct_lut_indexing():
    """xy_to_index is a thin wrapper; its output must match LUT[x*H + y]."""
    lut = build_lut(0)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            assert xy_to_index(x, y, lut) == lut[x * HEIGHT + y]


def test_build_lut_default_rotation_is_zero():
    assert build_lut() == build_lut(0)


def test_build_lut_returns_fresh_instance():
    """Successive calls must return independent buffers; caller-owned."""
    a = build_lut(0)
    b = build_lut(0)
    assert a == b
    a[0] = 42
    assert b[0] != 42

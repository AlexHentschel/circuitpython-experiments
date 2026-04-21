"""
LUT correctness tests for ``display.geometry``.

The LUT bakes two transforms into a single ``bytearray`` lookup:
  (1) rotation: logical (x, y) -> physical (px, py)
  (2) progressive bottom-up wiring: idx = (HEIGHT-1-py)*WIDTH + px

Each rotation is pinned by its four corner mappings; the corner set is
the minimal fixture that discriminates rotation from reflection and
identifies any off-by-one in either stage. The per-pixel reference-formula
test backs the corner set up with full-interior coverage, and the F-letter
fixtures + rotation-composition tests cross-check build_lut's rotation
against a visually hand-constructed reference.
"""

import pytest

from display._constants import WIDTH, HEIGHT, NUM_PIXELS
from display.bitmap_codec import pattern_to_colmajor
from display.geometry import build_lut, xy_to_index


# ---------------------------------------------------------------------------
# Shape and element-range invariants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_shape(rotation):
    """LUT is a ``bytearray`` of exactly ``NUM_PIXELS`` bytes, independent of rotation."""
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
# (wiring: idx = (HEIGHT-1-py)*WIDTH + px).
# ---------------------------------------------------------------------------

_CORNER_EXPECTATIONS = {
    0:   [((0, 0), 56), ((7, 0), 63), ((0, 7),  0), ((7, 7),  7)],
    90:  [((0, 0), 63), ((0, 7), 56), ((7, 0),  7), ((7, 7),  0)],
    180: [((0, 0),  7), ((7, 0),  0), ((0, 7), 63), ((7, 7), 56)],
    270: [((0, 0),  0), ((0, 7),  7), ((7, 0), 56), ((7, 7), 63)],
}


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_corner_mappings(rotation):
    """Each rotation's four logical corners map to the expected physical strip indices.

    Four-corner fixtures are the minimal set that discriminates rotation from reflection
    and catches off-by-one in either the rotation or the bottom-up wiring stage."""
    lut = build_lut(rotation)
    for (x, y), expected in _CORNER_EXPECTATIONS[rotation]:
        assert xy_to_index(x, y, lut) == expected, (
            "rotation={} xy=({}, {}) expected idx {}, got {}".format(
                rotation, x, y, expected, xy_to_index(x, y, lut)
            )
        )


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_xy_to_index_matches_direct_lut_indexing(rotation):
    """xy_to_index is a thin wrapper; its output must match LUT[x*H + y] for every rotation."""
    lut = build_lut(rotation)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            assert xy_to_index(x, y, lut) == lut[x * HEIGHT + y]


def test_build_lut_default_rotation_is_zero():
    """Calling ``build_lut()`` with no argument is equivalent to ``build_lut(0)``."""
    assert build_lut() == build_lut(0)


def test_build_lut_returns_fresh_instance():
    """Successive calls must return independent buffers; caller-owned."""
    a = build_lut(0)
    b = build_lut(0)
    assert a == b
    a[0] = 42
    assert b[0] != 42


# ---------------------------------------------------------------------------
# Input-domain contract: accept {0, 90, 180, 270} and their counter-clockwise
# equivalents {-270, -180, -90}; reject everything else (including out-of-range
# multiples of 90 like 360 or -360). Callers normalise at their own site.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("negative, positive", [(-90, 270), (-180, 180), (-270, 90)])
def test_build_lut_negative_rotations_match_positive_equivalents(negative, positive):
    """``-90``, ``-180``, ``-270`` are accepted as counter-clockwise sugar for ``270``, ``180``, ``90``."""
    assert build_lut(negative) == build_lut(positive)


@pytest.mark.parametrize("bad", [1, 45, 89, 91, 135, 359, -1, -45, 360, -360, 450, 720])
def test_build_lut_rejects_non_canonical_rotations(bad):
    """Non-canonical rotations (non-multiples of 90 and out-of-range multiples) raise ``ValueError``.

    Includes near-canonical near-misses (1, 89, 91, 359) and wrap-around attempts
    (360, -360, 450, 720) -- ``build_lut`` is strict and does not normalise."""
    with pytest.raises(ValueError):
        build_lut(bad)


# ---------------------------------------------------------------------------
# Interior correctness -- full-matrix check against an independent reference.
# Re-derives the expected strip index from the documented two-stage pipeline
# (Stage 1: rotation mapping (x,y)->(px,py); Stage 2: bottom-up wiring) rather
# than from the same hoisted expressions inside ``build_lut``. This catches
# any systematic interior off-by-one that corner + permutation tests miss.
# ---------------------------------------------------------------------------

def _reference_index(rotation, x, y):
    """Independent per-pixel reference: composes Stage 1 + Stage 2 verbatim."""
    if rotation == 0:
        px, py = x, y
    elif rotation == 90:
        px, py = WIDTH - 1 - y, x
    elif rotation == 180:
        px, py = WIDTH - 1 - x, HEIGHT - 1 - y
    else:  # 270
        px, py = y, HEIGHT - 1 - x
    return (HEIGHT - 1 - py) * WIDTH + px


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_lut_matches_reference_formula(rotation):
    """Every (x, y) maps to the strip index dictated by the two-stage spec."""
    lut = build_lut(rotation)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            assert xy_to_index(x, y, lut) == _reference_index(rotation, x, y), (
                f"rotation={rotation} (x, y)=({x}, {y})"
            )


# ---------------------------------------------------------------------------
# Rotation composition invariants.
#
# Strategy: (1) take the F-letter reference from README.md, (2) hand-construct
# its rotated variants by eye, (3) round-trip each ASCII pattern through the
# production ``pattern_to_colmajor`` encoder to extract its lit-cell set, then
# cross-check build_lut against these fixtures -- rendering F at rotation R
# must produce the same physical frame as rendering the visually-pre-rotated
# F at rotation 0.
#
# Composition tests go further: applying a pure-Python 90deg-CW rotation to
# the input pattern N times and rendering at rotation 0 must equal rendering
# the original at the equivalent single rotation (N*90 mod 360). This pins
# down the invariants the user cares about ("three 90s == one 270", "four
# 90s == identity", "-180 then -90 == -270", etc.).
# ---------------------------------------------------------------------------

# Reference F from lib/display/README.md (column-major bytes section).
_F_PATTERN = """
. # # # # # # .
. # . . . . . .
. # . . . . . .
. # # # # . . .
. # . . . . . .
. # . . . . . .
. # . . . . . .
. . . . . . . .
"""

# Visually hand-rotated 90 deg CW: top row becomes rightmost column, stem rotates to top edge.
_F_PATTERN_ROT_90 = """
. . . . . . . .
. # # # # # # #
. . . . # . . #
. . . . # . . #
. . . . # . . #
. . . . . . . #
. . . . . . . #
. . . . . . . .
"""

# Visually hand-rotated 180 deg: upside-down mirror of the original.
_F_PATTERN_ROT_180 = """
. . . . . . . .
. . . . . . # .
. . . . . . # .
. . . . . . # .
. . . # # # # .
. . . . . . # .
. . . . . . # .
. # # # # # # .
"""

# Visually hand-rotated 270 deg CW (equivalently, 90 deg CCW).
_F_PATTERN_ROT_270 = """
. . . . . . . .
# . . . . . . .
# . . . . . . .
# . . # . . . .
# . . # . . . .
# . . # . . . .
# # # # # # # .
. . . . . . . .
"""


def _pattern_to_cells(pattern):
    """Round-trip an ASCII pattern through ``pattern_to_colmajor`` and extract
    the set of lit ``(x, y)`` cells. Using the production encoder here means
    the fixtures exercise the same parse path as real icon data."""
    cols = pattern_to_colmajor(pattern)
    return {
        (x, y)
        for x in range(WIDTH)
        for y in range(HEIGHT)
        if (cols[x] >> y) & 1
    }


def _render_cells_at(cells, rotation):
    """Render a set of lit (x, y) cells through build_lut(rotation) into a 64-byte physical-strip frame."""
    lut = build_lut(rotation)
    frame = bytearray(NUM_PIXELS)
    for x, y in cells:
        frame[lut[x * HEIGHT + y]] = 1
    return frame


def _rotate_cells_cw_90(cells, steps=1):
    """Pure-geometric 90deg-CW rotation of a cell set: (x, y) -> (HEIGHT-1-y, x), applied ``steps`` times (mod 4)."""
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
    """Rendering F at rotation R equals rendering the hand-rotated F fixture at rotation 0.

    Each fixture was constructed visually from the README's F letter and verified
    by deriving the CW-90 cell map ``(x, y) -> (HEIGHT-1-y, x)`` on paper."""
    pre_rotated_cells = _pattern_to_cells(pre_rotated_pattern)
    assert _render_cells_at(_F_CELLS, rotation) == _render_cells_at(pre_rotated_cells, 0)


@pytest.mark.parametrize("steps, equivalent_rotation", [
    (0, 0),     # identity
    (1, 90),    # one  90 CW == rotation=90
    (2, 180),   # two  90 CW == rotation=180
    (3, 270),   # three 90 CW == rotation=270   (user's example)
    (4, 0),    # four 90 CW == identity        (user's example)
    (5, 90),    # five 90 CW == 450 deg == rotation=90
    (7, 270),   # seven 90 CW == 630 deg == rotation=270
])
def test_repeated_90cw_rotations_compose(steps, equivalent_rotation):
    """Applying 90deg CW to the input pattern N times and rendering at rotation=0
    equals rendering the original pattern at the single equivalent rotation."""
    rotated_cells = _rotate_cells_cw_90(_F_CELLS, steps=steps)
    assert _render_cells_at(rotated_cells, 0) == _render_cells_at(_F_CELLS, equivalent_rotation)


@pytest.mark.parametrize("sequence, equivalent_rotation", [
    # Positive-angle sequences
    ((90, 90),           180),
    ((90, 90, 90),       270),
    ((90, 90, 90, 90),   0),
    ((180, 90),          270),
    ((270, 180),         90),  # 450 deg == 90 deg
    # Negative-angle sequences -- user's explicit example: -180 then -90 == -270.
    ((-180, -90),        -270),
    ((-90, -90, -90),    -270),
    ((-90, -180, 90),    -180),  # mixed CW / CCW: -90 + -180 + 90 == -180
])
def test_rotation_sequence_composes_to_single_angle(sequence, equivalent_rotation):
    """A sequence of rotations applied stepwise to the input pattern renders identically to
    invoking build_lut once with the net equivalent angle (mod 360)."""
    cells = _F_CELLS
    for angle in sequence:
        # Convert each angle to a count of 90deg-CW steps (handles negative angles via Python's
        # floor-division semantics: -90 // 90 == -1, (-1) % 4 == 3 == "three 90deg-CW steps").
        steps = (angle // 90) % 4
        cells = _rotate_cells_cw_90(cells, steps=steps)
    assert _render_cells_at(cells, 0) == _render_cells_at(_F_CELLS, equivalent_rotation)

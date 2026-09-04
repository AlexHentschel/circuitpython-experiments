"""
Icon and arrow bitmap data plus ordered name lists for the 5x5 display.

Nomenclature and Convention:
 • column-major bytes -- one byte per column, where bit N of each byte indicates
   row N is lit (bit 0 = top row).  This convention requires that the display is
   physically at most 8 bits high (see also comment below).
 • Each icon/arrow is ``WIDTH`` bytes (one per column of the ``WIDTH`` x ``HEIGHT`` grid).
  Designed as row-major ASCII art (# = on, . = off), then transposed to
  column-major at design time; see ``bitmap_codec`` for details and examples.

Encoding-vs-geometry: the single-byte-per-column format caps height at
8 bits per byte. This is independent of display geometry -- a taller
display would need a different storage format, not just a parameter
change. See ``_MAX_HEIGHT_PER_COLUMN_BYTE`` in ``_constants``.

Lookup: the slice ``ICONS[i * WIDTH : (i + 1) * WIDTH]`` represents the icon at position ``i``.
Specifically, the icon is ``WIDTH`` bytes, each byte representing one column of the icon.
Identical convention applies for ``ARROWS``.

Name lists ``ICON_NAMES`` and ``ARROW_NAMES`` are ordered tuples of
strings that describe which icon/arrow lives at each slot. ``core.py``
consumes these lists at import time to populate the user-facing
``Icons`` / ``Arrows`` classes whose attributes are ``Image`` instances
backed by the matching slice. Any name-vs-byte drift therefore surfaces
as a single-place mismatch in this file, not as silent slot corruption
across the API.

Bitmaps are converted from Exp09 ``microbit.Image.*`` 25-byte row-major
(brightness 0–9, any non-zero = on) to this column-major 1-bit form.
"""

from ._constants import WIDTH  # noqa: F401 -- documents the lookup math


# ---------------------------------------------------------------------------
# Ordered name lists -- index = slot in ICONS / ARROWS.
# ---------------------------------------------------------------------------
ICON_NAMES = (
    "HEART",
    "SMALL_HEART",
    "YES",
    "NO",
    "HAPPY",
    "SAD",
    "CONFUSED",
    "ANGRY",
    "ASLEEP",
    "SURPRISED",
    "SILLY",
    "FABULOUS",
    "MEH",
    "TSHIRT",
    "ROLLERSKATE",
    "DUCK",
    "HOUSE",
    "TORTOISE",
    "BUTTERFLY",
    "STICK_FIGURE",
    "GHOST",
    "SWORD",
    "GIRAFFE",
    "SKULL",
    "UMBRELLA",
    "SNAKE",
    "RABBIT",
    "COW",
    "QUARTER_NOTE",
    "EIGHTH_NOTE",
    "PITCHFORK",
    "TARGET",
    "TRIANGLE",
    "LEFT_TRIANGLE",
    "CHESSBOARD",
    "DIAMOND",
    "SMALL_DIAMOND",
    "SQUARE",
    "SMALL_SQUARE",
    "SCISSORS",
)

ARROW_NAMES = (
    "NORTH",
    "NORTH_EAST",
    "EAST",
    "SOUTH_EAST",
    "SOUTH",
    "SOUTH_WEST",
    "WEST",
    "NORTH_WEST",
)


# fmt: off

# ---------------------------------------------------------------------------
# 40 Icons -- 5 bytes each, column-major. Ordering matches ICON_NAMES.
# ---------------------------------------------------------------------------

ICONS = bytes([
    # 0: HEART
    #    . # . # .
    #    # # # # #
    #    # # # # #
    #    . # # # .
    #    . . # . .
    0x06, 0x0F, 0x1E, 0x0F, 0x06,

    # 1: SMALL_HEART
    #    . . . . .
    #    . # . # .
    #    . # # # .
    #    . . # . .
    #    . . . . .
    0x00, 0x06, 0x0C, 0x06, 0x00,

    # 2: YES
    #    . . . . .
    #    . . . . #
    #    . . . # .
    #    # . # . .
    #    . # . . .
    0x08, 0x10, 0x08, 0x04, 0x02,

    # 3: NO
    #    # . . . #
    #    . # . # .
    #    . . # . .
    #    . # . # .
    #    # . . . #
    0x11, 0x0A, 0x04, 0x0A, 0x11,

    # 4: HAPPY
    #    . . . . .
    #    . # . # .
    #    . . . . .
    #    # . . . #
    #    . # # # .
    0x08, 0x12, 0x10, 0x12, 0x08,

    # 5: SAD
    #    . . . . .
    #    . # . # .
    #    . . . . .
    #    . # # # .
    #    # . . . #
    0x10, 0x0A, 0x08, 0x0A, 0x10,

    # 6: CONFUSED
    #    . . . . .
    #    . # . # .
    #    . . . . .
    #    . # . # .
    #    # . # . #
    0x10, 0x0A, 0x10, 0x0A, 0x10,

    # 7: ANGRY
    #    # . . . #
    #    . # . # .
    #    . . . . .
    #    # # # # #
    #    # . # . #
    0x19, 0x0A, 0x18, 0x0A, 0x19,

    # 8: ASLEEP
    #    . . . . .
    #    # # . # #
    #    . . . . .
    #    . # # # .
    #    . . . . .
    0x02, 0x0A, 0x08, 0x0A, 0x02,

    # 9: SURPRISED
    #    . # . # .
    #    . . . . .
    #    . . # . .
    #    . # . # .
    #    . . # . .
    0x00, 0x09, 0x14, 0x09, 0x00,

    # 10: SILLY
    #    # . . . #
    #    . . . . .
    #    # # # # #
    #    . . # . #
    #    . . # # #
    0x05, 0x04, 0x1C, 0x14, 0x1D,

    # 11: FABULOUS
    #    # # # # #
    #    # # . # #
    #    . . . . .
    #    . # . # .
    #    . # # # .
    0x03, 0x1B, 0x11, 0x1B, 0x03,

    # 12: MEH
    #    . # . # .
    #    . . . . .
    #    . . . # .
    #    . . # . .
    #    . # . . .
    0x00, 0x11, 0x08, 0x05, 0x00,

    # 13: TSHIRT
    #    # # . # #
    #    # # # # #
    #    . # # # .
    #    . # # # .
    #    . # # # .
    0x03, 0x1F, 0x1E, 0x1F, 0x03,

    # 14: ROLLERSKATE
    #    . . . # #
    #    . . . # #
    #    # # # # #
    #    # # # # #
    #    . # . # .
    0x0C, 0x1C, 0x0C, 0x1F, 0x0F,

    # 15: DUCK
    #    . # # . .
    #    # # # . .
    #    . # # # #
    #    . # # # .
    #    . . . . .
    0x02, 0x0F, 0x0F, 0x0C, 0x04,

    # 16: HOUSE
    #    . . # . .
    #    . # # # .
    #    # # # # #
    #    . # # # .
    #    . # . # .
    0x04, 0x1E, 0x0F, 0x1E, 0x04,

    # 17: TORTOISE
    #    . . . . .
    #    . # # # .
    #    # # # # #
    #    . # . # .
    #    . . . . .
    0x04, 0x0E, 0x06, 0x0E, 0x04,

    # 18: BUTTERFLY
    #    # # . # #
    #    # # # # #
    #    . . # . .
    #    # # # # #
    #    # # . # #
    0x1B, 0x1B, 0x0E, 0x1B, 0x1B,

    # 19: STICK_FIGURE
    #    . . # . .
    #    # # # # #
    #    . . # . .
    #    . # . # .
    #    # . . . #
    0x12, 0x0A, 0x07, 0x0A, 0x12,

    # 20: GHOST
    #    # # # # #
    #    # . # . #
    #    # # # # #
    #    # # # # #
    #    # . # . #
    0x1F, 0x0D, 0x1F, 0x0D, 0x1F,

    # 21: SWORD
    #    . . # . .
    #    . . # . .
    #    . . # . .
    #    . # # # .
    #    . . # . .
    0x00, 0x08, 0x1F, 0x08, 0x00,

    # 22: GIRAFFE
    #    # # . . .
    #    . # . . .
    #    . # . . .
    #    . # # # .
    #    . # . # .
    0x01, 0x1F, 0x08, 0x18, 0x00,

    # 23: SKULL
    #    . # # # .
    #    # . # . #
    #    # # # # #
    #    . # # # .
    #    . # # # .
    0x06, 0x1D, 0x1F, 0x1D, 0x06,

    # 24: UMBRELLA
    #    . # # # .
    #    # # # # #
    #    . . # . .
    #    # . # . .
    #    . # # . .
    0x0A, 0x13, 0x1F, 0x03, 0x02,

    # 25: SNAKE
    #    # # . . .
    #    # # . # #
    #    . # . # .
    #    . # # # .
    #    . . . . .
    0x03, 0x0F, 0x08, 0x0E, 0x02,

    # 26: RABBIT
    #    # . # . .
    #    # . # . .
    #    # # # # .
    #    # # . # .
    #    # # # # .
    0x1F, 0x1C, 0x17, 0x1C, 0x00,

    # 27: COW
    #    # . . . #
    #    # . . . #
    #    # # # # #
    #    . # # # .
    #    . . # . .
    0x07, 0x0C, 0x1C, 0x0C, 0x07,

    # 28: QUARTER_NOTE
    #    . . # . .
    #    . . # . .
    #    . . # . .
    #    # # # . .
    #    # # # . .
    0x18, 0x18, 0x1F, 0x00, 0x00,

    # 29: EIGHTH_NOTE
    #    . . # . .
    #    . . # # .
    #    . . # . #
    #    # # # . .
    #    # # # . .
    0x18, 0x18, 0x1F, 0x02, 0x04,

    # 30: PITCHFORK
    #    # . # . #
    #    # . # . #
    #    # # # # #
    #    . . # . .
    #    . . # . .
    0x07, 0x04, 0x1F, 0x04, 0x07,

    # 31: TARGET
    #    . . # . .
    #    . # # # .
    #    # # . # #
    #    . # # # .
    #    . . # . .
    0x04, 0x0E, 0x1B, 0x0E, 0x04,

    # 32: TRIANGLE
    #    . . . . .
    #    . . # . .
    #    . # . # .
    #    # # # # #
    #    . . . . .
    0x08, 0x0C, 0x0A, 0x0C, 0x08,

    # 33: LEFT_TRIANGLE
    #    # . . . .
    #    # # . . .
    #    # . # . .
    #    . . . # .
    #    . . . . .
    0x07, 0x02, 0x04, 0x08, 0x00,

    # 34: CHESSBOARD
    #    . # . # .
    #    # . # . #
    #    . # . # .
    #    # . # . #
    #    . # . # .
    0x0A, 0x15, 0x0A, 0x15, 0x0A,

    # 35: DIAMOND
    #    . . # . .
    #    . # . # .
    #    # . . . #
    #    . # . # .
    #    . . # . .
    0x04, 0x0A, 0x11, 0x0A, 0x04,

    # 36: SMALL_DIAMOND
    #    . . . . .
    #    . . # . .
    #    . # . # .
    #    . . # . .
    #    . . . . .
    0x00, 0x04, 0x0A, 0x04, 0x00,

    # 37: SQUARE
    #    # # # # #
    #    # . . . #
    #    # . . . #
    #    # . . . #
    #    # # # # #
    0x1F, 0x11, 0x11, 0x11, 0x1F,

    # 38: SMALL_SQUARE
    #    . . . . .
    #    . # # # .
    #    . # . # .
    #    . # # # .
    #    . . . . .
    0x00, 0x0E, 0x0A, 0x0E, 0x00,

    # 39: SCISSORS
    #    # # . . #
    #    # # . # .
    #    . . # . .
    #    # # . # .
    #    # # . . #
    0x1B, 0x1B, 0x04, 0x0A, 0x11,
])


# ---------------------------------------------------------------------------
# 8 Arrows -- 5 bytes each, column-major. Ordering matches ARROW_NAMES.
# ---------------------------------------------------------------------------

ARROWS = bytes([
    # 0: NORTH
    #    . . # . .
    #    . # # # .
    #    # . # . #
    #    . . # . .
    #    . . # . .
    0x04, 0x02, 0x1F, 0x02, 0x04,

    # 1: NORTH_EAST
    #    . . # # #
    #    . . . # #
    #    . . # . #
    #    . # . . .
    #    # . . . .
    0x10, 0x08, 0x05, 0x03, 0x07,

    # 2: EAST
    #    . . # . .
    #    . . . # .
    #    # # # # #
    #    . . . # .
    #    . . # . .
    0x04, 0x04, 0x15, 0x0E, 0x04,

    # 3: SOUTH_EAST
    #    # . . . .
    #    . # . . .
    #    . . # . #
    #    . . . # #
    #    . . # # #
    0x01, 0x02, 0x14, 0x18, 0x1C,

    # 4: SOUTH
    #    . . # . .
    #    . . # . .
    #    # . # . #
    #    . # # # .
    #    . . # . .
    0x04, 0x08, 0x1F, 0x08, 0x04,

    # 5: SOUTH_WEST
    #    . . . . #
    #    . . . # .
    #    # . # . .
    #    # # . . .
    #    # # # . .
    0x1C, 0x18, 0x14, 0x02, 0x01,

    # 6: WEST
    #    . . # . .
    #    . # . . .
    #    # # # # #
    #    . # . . .
    #    . . # . .
    0x04, 0x0E, 0x15, 0x04, 0x04,

    # 7: NORTH_WEST
    #    # # # . .
    #    # # . . .
    #    # . # . .
    #    . . . # .
    #    . . . . #
    0x07, 0x03, 0x05, 0x08, 0x10,
])

# fmt: on

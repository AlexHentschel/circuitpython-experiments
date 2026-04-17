"""
Pure coordinate mapping for the LED matrix.

Separates the (x, y) -> strip-index transform from the hardware layer so
it can be exercised on CPython without a device. ``Display.set_rotation``
in ``core.py`` delegates here and mutates the module-level LUT in place.
"""

from ._constants import WIDTH, HEIGHT


def build_lut(rotation=0):
    """Return a fresh ``bytearray`` of ``WIDTH * HEIGHT`` bytes.

    ``result[x * HEIGHT + y]`` is the NeoPixel strip index for logical
    pixel ``(x, y)`` at the given rotation.

    Two-stage coordinate transform:
      1. Rotation: logical (x, y) -> physical (px, py).
         Clockwise rotation in degrees; unknown values fall through to 0.
      2. Bottom-up progressive wiring: physical (px, py) -> strip index.
         All rows run left-to-right. Bottom row (py=H-1) = strip indices 0-7.
         idx = (H-1-py)*W + px.

    Logical coordinates (x = column, y = row):

             x=0   x=1   x=2   x=3   x=4   x=5   x=6   x=7
    y=0    (0,0) (1,0) (2,0) (3,0) (4,0) (5,0) (6,0) (7,0)
    y=1    (0,1) (1,1) (2,1) (3,1) (4,1) (5,1) (6,1) (7,1)
    ...
    y=7    (0,7) (1,7) (2,7) (3,7) (4,7) (5,7) (6,7) (7,7)

    Physical strip indices (progressive bottom-up L-to-R, rotation=0):

             x=0   x=1   x=2   x=3   x=4   x=5   x=6   x=7
    y=0    (56)  (57)  (58)  (59)  (60)  (61)  (62)  (63)  -> top row
    y=1    (48)  (49)  (50)  (51)  (52)  (53)  (54)  (55)
    y=2    (40)  (41)  (42)  (43)  (44)  (45)  (46)  (47)
    y=3    (32)  (33)  (34)  (35)  (36)  (37)  (38)  (39)
    y=4    (24)  (25)  (26)  (27)  (28)  (29)  (30)  (31)
    y=5    (16)  (17)  (18)  (19)  (20)  (21)  (22)  (23)
    y=6    ( 8)  ( 9)  (10)  (11)  (12)  (13)  (14)  (15)
    y=7    ( 0)  ( 1)  ( 2)  ( 3)  ( 4)  ( 5)  ( 6)  ( 7)  -> bottom row (strip start)
    """
    lut = bytearray(WIDTH * HEIGHT)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            # Stage 1: rotate logical -> physical
            if rotation == 90:
                px, py = (WIDTH - 1) - y, x
            elif rotation == 180:
                px, py = (WIDTH - 1) - x, (HEIGHT - 1) - y
            elif rotation == 270:
                px, py = y, (HEIGHT - 1) - x
            else:
                px, py = x, y
            # Stage 2: bottom-up progressive wiring -> strip index
            # All rows L-to-R, bottom row = indices 0..W-1
            lut[x * HEIGHT + y] = ((HEIGHT - 1) - py) * WIDTH + px
    return lut


def xy_to_index(x, y, lut):
    """Map logical (x, y) to NeoPixel strip index via the given LUT."""
    return lut[x * HEIGHT + y]

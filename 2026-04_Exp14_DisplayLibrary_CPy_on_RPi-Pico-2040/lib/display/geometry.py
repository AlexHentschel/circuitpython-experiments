"""
Pure coordinate mapping for the LED matrix.

Separates the (x, y) -> strip-index transform from the hardware layer so
it can be exercised on CPython without a device. ``Display.set_rotation``
in ``core.py`` delegates here and mutates the module-level LUT in place.

Indexing convention: the LUT is a flat ``bytearray`` of ``WIDTH * HEIGHT``
entries indexed as ``lut[x * HEIGHT + y]`` -- x is the outer stride, y the
inner. This is x-major, not the row-major ``[row][col]`` convention common
in NumPy / OpenCV; it matches the column-major bitmap layout used elsewhere
in the package (one byte per column; see ``bitmap_codec``). The 1D layout
is deliberate on this MCU target: one heap allocation, native single
``bytearray`` subscript in the render hot path, and isomorphic to the
downstream 1D NeoPixel strip -- see the architecture notes in ``README.md``
for the full rationale.
"""

from ._constants import WIDTH, HEIGHT


def build_lut(rotation=0):
    """Return a fresh ``bytearray`` of ``WIDTH * HEIGHT`` bytes.

    ``result[x * HEIGHT + y]`` is the NeoPixel strip index for logical
    pixel ``(x, y)`` at the given rotation.

    Two-stage coordinate transform:
      1. Rotation: logical (x, y) -> physical (px, py).
         Clockwise rotation in degrees. Accepted values: ``0``, ``90``, ``180``,
         ``270``, and their counter-clockwise equivalents ``-270``, ``-180``,
         ``-90``. Any other value raises ``ValueError``. Out-of-range inputs
         (e.g. ``360``, ``-360``) are rejected rather than wrapped -- callers
         who want wrap-around should normalise at their own call site (e.g.
         ``build_lut(degrees % 360)``); modulo is left out of this primitive
         so the cost isn't paid by callers that don't need it.
      2. Bottom-up progressive wiring: physical (px, py) -> strip index.
         All rows run left-to-right. Bottom row (py=HEIGHT-1) is represented by
         strip indices 0-7. The formula for the strip index is:
         ``idx = (HEIGHT-1-py)*WIDTH + px``.

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
    if rotation == 0:
        # px, py = x, y
        #   =>  idx  =  (HEIGHT - 1 - y) * WIDTH + x  =  (HEIGHT - 1) * WIDTH + x - y * WIDTH
        #            =  _x_offset - y * WIDTH     where _x_offset = (HEIGHT - 1) * WIDTH + x
        _c = (HEIGHT - 1) * WIDTH
        for x in range(WIDTH):
            x_base = x * HEIGHT
            _x_offset = _c + x
            for y in range(HEIGHT):
                lut[x_base + y] = _x_offset - y * WIDTH
    elif rotation == 90 or rotation == -270:
        # px, py = (WIDTH-1)-y, x
        #   =>  idx  =  (HEIGHT - 1 - x) * WIDTH + (WIDTH - 1 - y)  =  (HEIGHT - x) * WIDTH - 1 - y
        #            =  HEIGHT * WIDTH - 1 - x * WIDTH - y
        #            =  _x_offset - y              where _x_offset = (HEIGHT * WIDTH - 1) - x * WIDTH
        _c = HEIGHT * WIDTH - 1
        for x in range(WIDTH):
            x_base = x * HEIGHT
            _x_offset = _c - x * WIDTH
            for y in range(HEIGHT):
                lut[x_base + y] = _x_offset - y
    elif rotation == 180 or rotation == -180:
        # px, py = (WIDTH-1)-x, (HEIGHT-1)-y
        #   =>  idx  =  (HEIGHT - 1 - (HEIGHT-1-y)) * WIDTH + (WIDTH - 1 - x)
        #            =  y * WIDTH + (WIDTH - 1 - x)  =  _x_offset + y * WIDTH
        #   where _x_offset = WIDTH - 1 - x
        _c = WIDTH - 1
        for x in range(WIDTH):
            x_base = x * HEIGHT
            _x_offset = _c - x
            for y in range(HEIGHT):
                lut[x_base + y] = _x_offset + y * WIDTH
    elif rotation == 270 or rotation == -90:
        # px, py = y, (HEIGHT-1)-x
        #   =>  idx  =  (HEIGHT - 1 - (HEIGHT-1-x)) * WIDTH + y
        #            =  x * WIDTH + y  =  _x_offset + y       where _x_offset = x * WIDTH
        for x in range(WIDTH):
            x_base = x * HEIGHT
            _x_offset = x * WIDTH
            for y in range(HEIGHT):
                lut[x_base + y] = _x_offset + y
    else:
        raise ValueError(f"rotation must be one of 0, 90, 180, 270, -90, -180, -270; got {rotation!r}")
    return lut


def xy_to_index(x, y, lut):
    """Map logical (x, y) to NeoPixel strip index via the given LUT."""
    return lut[x * HEIGHT + y]

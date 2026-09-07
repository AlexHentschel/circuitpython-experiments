"""
Pure coordinate mapping for the LED matrix.

Separates the (x, y) -> strip-index transform from the hardware layer so
it can be exercised on CPython without a device. ``Display.set_rotation``
in ``core.py`` delegates here and mutates the module-level Look-Up Table
[LUT] in place.

Indexing convention: the LUT is a flat ``bytearray`` of ``WIDTH * HEIGHT``
entries indexed as ``lut[x * HEIGHT + y]`` -- x is the outer stride, y the
inner. This is x-major, not the row-major ``[row][col]`` convention common
in NumPy / OpenCV; it matches the column-major bitmap layout used by the
Microbit (one byte per column; see ``bitmap_codec``). The 1D layout
is deliberate on this MCU target: one heap allocation, native single
``bytearray`` subscript in the render hot path, and isomorphic to the
downstream 1D NeoPixel strip -- see the architecture notes in ``README.md``
for the full rationale.
"""

from ._constants import WIDTH, HEIGHT


def build_lut(rotation: int = 0, dest: bytearray | None = None) -> bytearray:
    """Build the coordinate LUT, returning a ``WIDTH * HEIGHT``-byte ``bytearray``.

    ``result[x * HEIGHT + y]`` is the NeoPixel strip index for logical
    pixel ``(x, y)`` at the given rotation.

    ``dest``: optional pre-allocated target buffer. When ``None`` (default) a
    fresh ``bytearray`` is allocated and returned. When supplied it must be
    exactly ``WIDTH * HEIGHT`` bytes; the table is written into it in place and
    the same object is returned -- this lets ``Display.set_rotation`` rebuild the
    live LUT without a fresh allocation (avoids per-rotation heap churn). On an
    invalid ``rotation`` the function raises before writing, so ``dest`` is left
    unmodified; an invalid ``dest`` length raises before any writes as well.

    Two-stage coordinate transform:
      1. Rotation: logical (x, y) -> physical (px, py).
         Clockwise rotation in degrees. Accepted values: ``0``, ``90``, ``180``,
         ``270``, and their counter-clockwise equivalents ``-270``, ``-180``,
         ``-90``. Any other value raises ``ValueError``. Out-of-range inputs
         (e.g. ``360``, ``-360``) are rejected rather than wrapped -- callers
         who want wrap-around should normalise at their own call site (e.g.
         ``build_lut(degrees % 360)``); modulo is left out of this primitive
         so the cost isn't paid by callers that don't need it.
      2. BPI-Bit-S2 column-major wiring: physical (px, py) -> strip index.
         Columns run top-to-bottom (py increases with strip index). Columns are
         ordered right-to-left on the board: logical column 4 is strip start.
         For this 5×5 matrix the formula is ``idx = py + 20 - px * 5``
         (Exp09 / BananaPi sequential list). Equivalently, with the current
         ``WIDTH``/``HEIGHT`` (both 5): ``idx = py + HEIGHT * (WIDTH - 1 - px)``.

    Logical coordinates (x = column, y = row):

            x=0   x=1   x=2   x=3   x=4
    y=0    (0,0) (1,0) (2,0) (3,0) (4,0)
    y=1    (0,1) (1,1) (2,1) (3,1) (4,1)
    y=2    (0,2) (1,2) (2,2) (3,2) (4,2)
    y=3    (0,3) (1,3) (2,3) (3,3) (4,3)
    y=4    (0,4) (1,4) (2,4) (3,4) (4,4)

    Physical strip indices (column-major, right-to-left, rotation=0):

            x=0   x=1   x=2   x=3   x=4
    y=0     20    15    10     5     0     -> top row
    y=1     21    16    11     6     1
    y=2     22    17    12     7     2
    y=3     23    18    13     8     3
    y=4     24    19    14     9     4     -> bottom row (edge connector)
    """
    if dest is None:
        lut = bytearray(WIDTH * HEIGHT)
    else:
        if len(dest) != WIDTH * HEIGHT:
            raise ValueError(f"dest must be exactly {WIDTH * HEIGHT} bytes; got {len(dest)}")
        lut = dest
    if rotation == 0:
        # px, py = x, y
        #   =>  idx  =  py + HEIGHT * (WIDTH - 1 - px)
        #            =  y + HEIGHT * (WIDTH - 1 - x)
        #            =  _x_offset + y     where _x_offset = HEIGHT * (WIDTH - 1 - x)
        # 5×5 numeric form: idx = y + 20 - x * 5
        for x in range(WIDTH):
            x_base = x * HEIGHT
            _x_offset = HEIGHT * (WIDTH - 1 - x)
            for y in range(HEIGHT):
                lut[x_base + y] = _x_offset + y
    elif rotation == 90 or rotation == -270:
        # px, py = (WIDTH-1)-y, x
        #   =>  idx  =  x + HEIGHT * (WIDTH - 1 - ((WIDTH - 1) - y))
        #            =  x + y * HEIGHT
        # Start at idx = x (y=0) and accumulate +HEIGHT per row.
        # invariant: _x_offset == x + y * HEIGHT
        for x in range(WIDTH):
            x_base = x * HEIGHT
            _x_offset = x
            for y in range(HEIGHT):
                lut[x_base + y] = _x_offset
                _x_offset += HEIGHT
    elif rotation == 180 or rotation == -180:
        # px, py = (WIDTH-1)-x, (HEIGHT-1)-y
        #   =>  idx  =  (HEIGHT - 1 - y) + HEIGHT * x
        #            =  _x_offset - y     where _x_offset = x * HEIGHT + (HEIGHT - 1)
        for x in range(WIDTH):
            x_base = x * HEIGHT
            _x_offset = x * HEIGHT + (HEIGHT - 1)
            for y in range(HEIGHT):
                lut[x_base + y] = _x_offset - y
    elif rotation == 270 or rotation == -90:
        # px, py = y, (HEIGHT-1)-x
        #   =>  idx  =  (HEIGHT - 1 - x) + HEIGHT * (WIDTH - 1 - y)
        #            =  WIDTH * HEIGHT - 1 - x - y * HEIGHT
        # Start at idx = WIDTH*HEIGHT-1-x (y=0) and accumulate -HEIGHT per row.
        # invariant: _x_offset == (WIDTH * HEIGHT - 1 - x) - y * HEIGHT
        _c = WIDTH * HEIGHT - 1
        for x in range(WIDTH):
            x_base = x * HEIGHT
            _x_offset = _c - x
            for y in range(HEIGHT):
                lut[x_base + y] = _x_offset
                _x_offset -= HEIGHT
    else:
        raise ValueError(f"rotation must be one of 0, 90, 180, 270, -90, -180, -270; got {rotation!r}")
    return lut


def xy_to_index(x: int, y: int, lut: bytearray) -> int:
    """Map logical (x, y) to NeoPixel strip index via the given LUT."""
    return lut[x * HEIGHT + y]

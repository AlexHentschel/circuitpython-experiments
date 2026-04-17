"""
Dimensions, encoding limits, and color constants shared across the
``display`` package.

Pure module: no hardware imports (``board``, ``neopixel``, ``rainbowio``).
Hardware-coupled values (``PIXEL_PIN``, ``BRIGHTNESS``) live in ``core.py``
so host-side tests can import the rest of the package without a device.

Distinctions preserved here:
  * ``WIDTH`` / ``HEIGHT`` -- current display geometry (parametric).
  * ``_MAX_HEIGHT_PER_COLUMN_BYTE`` -- hard encoding limit (8 bits per byte)
    of the column-major bitmap format. Independent of display geometry;
    exceeding it is a storage-format redesign, not a resize.
"""

# ---------------------------------------------------------------------------
# Display geometry
# ---------------------------------------------------------------------------
WIDTH = 8
HEIGHT = 8
NUM_PIXELS = WIDTH * HEIGHT

# Encoding-imposed hard limit: each column is stored as a single byte, so at
# most 8 rows can be encoded. This is a property of the column-major byte
# format, NOT of the display geometry. Error messages must distinguish the
# two: exceeding this is a storage-format redesign, not a simple resize.
_MAX_HEIGHT_PER_COLUMN_BYTE = 8


# ---------------------------------------------------------------------------
# Color constants -- Adafruit LED Animation standard + LED-tuned extras
# ---------------------------------------------------------------------------
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 40, 0)
GREEN = (0, 255, 0)
TEAL = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 20)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 222, 30)
PINK = (242, 90, 255)
AQUA = (50, 255, 255)
JADE = (0, 255, 40)
AMBER = (255, 100, 0)
OLD_LACE = (253, 245, 230)
RAINBOW = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)

GRAY = (160, 160, 160)
DARKSLATEBLUE = (80, 0, 180)
YELLOWGREEN = (120, 230, 0)
DEEPPINK = (255, 0, 160)

OFF = BLACK

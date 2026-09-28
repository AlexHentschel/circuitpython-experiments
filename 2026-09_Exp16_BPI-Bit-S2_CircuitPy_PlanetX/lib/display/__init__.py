"""
MakeCode-style display library for a 5x5 WS2812 NeoPixel matrix.

Covers hardware wiring, the two-tier sync+async API, cooperative
multitasking via a cancellation ``Token`` returned by every Tier 2
method, the column-major bitmap format, and how ``Display``/``Image``
share state (each ``Display`` owns its own NeoPixel buffer and LUT; an
``Image`` renders to whichever ``Display`` instance calls it).

See ``README.md`` in this package for architecture and design rationale.
"""

from ._constants import (
    WIDTH,
    HEIGHT,
    NUM_PIXELS,
    RED,
    YELLOW,
    ORANGE,
    GREEN,
    TEAL,
    CYAN,
    BLUE,
    PURPLE,
    MAGENTA,
    WHITE,
    BLACK,
    GOLD,
    PINK,
    AQUA,
    JADE,
    AMBER,
    OLD_LACE,
    RAINBOW,
    GRAY,
    DARKSLATEBLUE,
    YELLOWGREEN,
    DEEPPINK,
    OFF,
)
from .icons import EMOJIS, ARROWS, EMOJI_NAMES, ARROW_NAMES

# core.py requires board/neopixel/rainbowio/adafruit_bitmap_font. On
# CPython (e.g. pytest hosts) those are absent; skip the re-export so
# pure sub-modules remain importable for host-side tests. On device the
# import always succeeds.
# ``Emojis`` / ``Arrows`` are constructed inside core.py (they are Icon
# instances), so they ship with the hardware import group too.
try:
    import board  # noqa: F401 -- presence check for CircuitPython runtime

    _HAS_HARDWARE = True
except ImportError:
    _HAS_HARDWARE = False

if _HAS_HARDWARE:
    from .core import (  # noqa: F401
        Display,
        Image,
        Icon,
        Token,
        Emojis,
        Arrows,
        display,
        color,
        colorwheel,
    )

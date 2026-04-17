"""
MakeCode-style display library for an 8x8 WS2812b NeoPixel matrix.

Covers hardware wiring, the two-tier sync+async API, cooperative
multitasking via a cancellation-token counter, the column-major bitmap
format, and the Display/Image coupling to module-level state.

See ``README.md`` in this package for architecture and design rationale.
"""

from ._constants import (
    WIDTH, HEIGHT, NUM_PIXELS,
    RED, YELLOW, ORANGE, GREEN, TEAL, CYAN, BLUE, PURPLE, MAGENTA,
    WHITE, BLACK, GOLD, PINK, AQUA, JADE, AMBER, OLD_LACE, RAINBOW,
    GRAY, DARKSLATEBLUE, YELLOWGREEN, DEEPPINK, OFF,
)
from .icons import ICONS, ARROWS, IconNames, ArrowNames

# core.py requires board/neopixel/rainbowio/adafruit_bitmap_font. On
# CPython (e.g. pytest hosts) those are absent; skip the re-export so
# pure sub-modules remain importable for host-side tests. On device the
# import always succeeds.
try:
    import board  # noqa: F401 -- presence check for CircuitPython runtime
    _HAS_HARDWARE = True
except ImportError:
    _HAS_HARDWARE = False

if _HAS_HARDWARE:
    from .core import (  # noqa: F401
        Display, Image, display, color, colorwheel,
        create_image, create_big_image,
    )

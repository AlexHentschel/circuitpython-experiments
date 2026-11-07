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
from .text_layout import ScreenText, centered

import sys

# core.py requires board/neopixel/rainbowio/adafruit_bitmap_font. They exist only
# on CircuitPython. In the test environment (CPython) they are absent; we skip the
# re-export so the pure sub-modules remain importable. Detected by the interpreter
# name, not by importing ``board``: a working Blinka ``board`` would otherwise make
# the test environment look like hardware.
# ``Emojis`` / ``Arrows`` are constructed inside core.py (they are Icon
# instances), so they ship with the hardware import group too.
_HAS_HARDWARE = sys.implementation.name == "circuitpython"

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

"""Default `code.py` -- idle demo: HEART icon, cycling through colors indefinitely.

Not a test script -- see the sibling `code_stageN.py` files for the round-1
on-device test suite; `CONCLUSIONS.md`/`SESSION_LOG.md` (persona memory)
track their findings. This is what deploys when `.vscode/cpfiles.txt`'s
`# default` entry (plain ``code.py``, no ``->`` remap) is the active line --
a simple, low-risk Tier 1 (sync) sketch that just shows the board is alive,
for whenever no test stage's manifest line is active instead.

Holds each color for 3 seconds before advancing to the next, forever.

Color list deliberately **skips** YELLOW and ORANGE: `CONCLUSIONS.md` flags
both as perceptually off on this board's WS2812/diffuser (YELLOW reads with
a visible orange tinge; ORANGE is visually indistinguishable from plain red)
-- not fixed there yet, so this default avoids relying on either looking
distinct from its neighbors.
"""

import time

import display
from display import Icons

d = display.display

d.set_rotation(0)
d.set_brightness(0.10)  # matches Alex's live brightness preference for this file

# Named constants from lib/display/_constants.py, chosen to be visually
# distinct from each other (and from the flagged YELLOW/ORANGE pair above).
_COLORS = (
    ("RED", display.RED),
    ("GREEN", display.GREEN),
    ("BLUE", display.BLUE),
    ("CYAN", display.CYAN),
    ("MAGENTA", display.MAGENTA),
    ("PURPLE", display.PURPLE),
    ("GOLD", display.GOLD),
    ("WHITE", display.WHITE),
)
_HOLD_S = 3

print("Default: HEART icon, color cycle, 3s hold per color, indefinitely")

d.clear_screen()
_i = 0
while True:
    _name, _color = _COLORS[_i % len(_COLORS)]
    d.render_icon(Icons.HEART, _color)
    print(f"HEART in {_name}")
    time.sleep(_HOLD_S)
    _i += 1

"""Round-1 LED-matrix on-device test -- Stage 0 (Tier 1 sync only).

Deliberately does NOT import ``asyncio`` and does NOT touch ``lib/buttons.py``.
Purpose: isolate the display library's synchronous rendering path before
K1 (bundle asyncio) enters the picture at Stage 2. See the LED-matrix test
plan (persona memory, projects/circuitpython-exp16-planetx/SESSION_LOG.md,
Session 17) for stages 1-3.

What this proves, if it prints all five lines and the matrix behaves as
described:
  - ``import display`` succeeds on-device (board/neopixel/rainbowio present,
    library's own hardware-import branch fires, LUT builds, NeoPixel
    buffer allocates).
  - ``fill`` / ``clear_screen`` / ``set_pixel`` / ``render_icon`` /
    ``set_brightness`` / ``set_rotation`` (Tier 1) write real pixels.
  - Logical origin (0, 0) is visually top-left, per the documented wiring
    LUT (``row + 20 - column * 5``) -- not yet independently confirmed
    on-device.
"""

import time

import display
from display import Icons

d = display.display

print("Stage 0: import display OK")

# 1) fill -- confirms NeoPixel init + fill() writes all 25 pixels the same color.
d.fill(display.RED)
print("1/5: fill(RED) -- whole 5x5 should be solid red")
time.sleep(2)

# 2) set_pixel -- confirms logical origin is top-left, as documented.
d.clear_screen()
d.set_pixel(0, 0, display.WHITE)
print("2/5: set_pixel(0, 0, WHITE) -- exactly one LED lit, top-left corner")
time.sleep(2)

# 3) render_icon -- confirms icon-table lookup + column-major bitmap decode.
d.clear_screen()
d.render_icon(Icons.HEART, display.RED)
print("3/5: render_icon(Icons.HEART) -- recognizable heart shape")
time.sleep(2)

# 4) set_brightness + set_rotation -- confirms both non-cancelling sync setters;
#    same heart re-rendered after rotating 90 deg so the shape should visibly turn.
d.set_brightness(0.05)
d.set_rotation(90)
d.render_icon(Icons.HEART, display.RED)
print("4/5: set_brightness(0.05) + set_rotation(90) -- dimmer, heart rotated 90deg")
time.sleep(2)

# 5) done -- leave the matrix off; nothing left running (no asyncio task, no button pump).
d.clear_screen()
print("5/5: clear_screen -- matrix off. Stage 0 complete (Tier 1 sync only, no asyncio).")

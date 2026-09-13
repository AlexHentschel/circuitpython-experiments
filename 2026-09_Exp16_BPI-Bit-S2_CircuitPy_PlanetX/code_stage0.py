"""Round-1 LED-matrix on-device test -- Stage 0 (Tier 1 sync only).

Deliberately does NOT import ``asyncio`` and does NOT touch ``lib/buttons.py``.
Purpose: isolate the display library's synchronous rendering path before
K1 (bundle asyncio) enters the picture at Stage 2. See the LED-matrix test
plan (persona memory, projects/circuitpython-exp16-planetx/SESSION_LOG.md,
Session 17) for stages 1-3.

Looped (``while True``), not one-shot: a CircuitPython script that reaches
its end falls back to the REPL and stops producing output. Since the human
message that triggers an autonomous serial-log capture can't be reliably
timed against a single ~10s run, the whole sequence repeats indefinitely
instead -- any capture window of a bit more than one cycle is guaranteed
to observe a full cycle, regardless of when it starts. This is diagnostic-
harness shape, not the project's eventual production shape (that will be
an async main loop once Stage 2+ brings asyncio in).

What this proves, if it prints all six lines each cycle and the matrix
behaves as described:
  - ``import display`` succeeds on-device (board/neopixel/rainbowio present,
    library's own hardware-import branch fires, LUT builds, NeoPixel
    buffer allocates).
  - ``fill`` / ``clear_screen`` / ``set_pixel`` / ``render_icon`` /
    ``set_brightness`` / ``set_rotation`` (Tier 1) write real pixels.
  - Logical origin (0, 0) is visually top-left, per the documented wiring
    LUT (``row + 20 - column * 5``) -- confirmed on-device 2026-09-11.
  - Step 6 (edge case): ``set_brightness()``'s practical floor. **Confirmed
    on-device 2026-09-11** (Alex's authoritative observation): 0.01 and
    below is visually indistinguishable from off; 0.02 was the lowest
    level still visibly lit in this test.
"""

import time

import display
from display import Icons

d = display.display

print("Stage 0: import display OK")

cycle = 0
while True:
    cycle += 1
    # Reset to a known state at the top of every cycle -- set_rotation() rebuilds the LUT
    # for an *absolute* target angle (see lib/display/core.py docstring), so
    # this doesn't drift across cycles, but it does carry the prior cycle's 90-degree
    # rotation forward if not reset explicitly. Brightness resets to 0.20 -- the library's
    # actual default (lib/display/core.py BRIGHTNESS, not re-exported publicly, hardcoded
    # here to match) -- not to step 4's 0.05 target, so step 4's dimming is visible fresh
    # every cycle instead of only once (a same-value no-op bug caught by Alex, 2026-09-11).
    d.set_rotation(0)
    d.set_brightness(0.20)
    print(f"=== cycle {cycle} ===")

    # 1) fill -- confirms NeoPixel init + fill() writes all 25 pixels the same color.
    d.fill(display.RED)
    print("1/6: fill(RED) -- whole 5x5 should be solid red")
    time.sleep(2)

    # 2) set_pixel -- confirms logical origin is top-left, as documented.
    d.clear_screen()
    d.set_pixel(0, 0, display.WHITE)
    print("2/6: set_pixel(0, 0, WHITE) -- exactly one LED lit, top-left corner")
    time.sleep(2)

    # 3) render_icon -- confirms icon-table lookup + column-major bitmap decode.
    d.clear_screen()
    d.render_icon(Icons.HEART, display.RED)
    print("3/6: render_icon(Icons.HEART) -- recognizable heart shape")
    time.sleep(2)

    # 4) set_brightness + set_rotation -- confirms both non-cancelling sync setters;
    #    same heart re-rendered after rotating 90 deg so the shape should visibly turn.
    d.set_brightness(0.05)
    d.set_rotation(90)
    d.render_icon(Icons.HEART, display.RED)
    print("4/6: set_brightness(0.05) + set_rotation(90) -- dimmer, heart rotated 90deg")
    time.sleep(2)

    # 5) done with the main sequence -- reset rotation before the brightness-floor edge
    #    case below so a rotated heart doesn't confuse a test that's only about brightness.
    d.clear_screen()
    d.set_rotation(0)
    print("5/6: clear_screen -- main sequence done. Cycle continues into the brightness-floor check.")
    time.sleep(1)

    # 6) EDGE CASE -- brightness floor. Brightness 0.01 and below is visually indistinguishable
    #    from off; 0.02 is the lowest level still visibly lit (confirmed on-device 2026-09-11).
    #    Likely mechanism (not independently verified): WS2812 duty-cycle/rounding at very low
    #    brightness*color products. Fill once; set_brightness() re-shows the existing buffer at
    #    each new level on its own (verified against lib/display/core.py: the setter calls
    #    _pixels.show() itself), so no need to re-fill per level -- isolates brightness as the
    #    only changing variable.
    d.fill(display.BLUE)
    for _level in (0.05, 0.04, 0.03, 0.02, 0.01, 0.005, 0.0):
        d.set_brightness(_level)
        print(f"6/6: set_brightness({_level}) -- solid blue fill, watch for the visual floor")
        time.sleep(2)
    d.clear_screen()
    print("6/6: brightness-floor check done. Cycle complete (Tier 1 sync only, no asyncio).")

    time.sleep(1)

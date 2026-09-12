"""Round-1 LED-matrix on-device test -- Stage 0+1 (Tier 1 sync only).

Deliberately does NOT import ``asyncio`` and does NOT touch ``lib/buttons.py``.
Purpose: isolate the display library's synchronous rendering path before
K1 (bundle asyncio) enters the picture at Stage 2. See the LED-matrix test
plan (persona memory, projects/circuitpython-exp16-planetx/SESSION_LOG.md,
Session 17) for the original stage breakdown; Stage 0 (minimal Tier 1) and
Stage 1 (broader Tier 1) are combined here in one script since both are
still Tier-1-only -- no reason to fragment across files for that alone.

Looped (``while True``), not one-shot: a CircuitPython script that reaches
its end falls back to the REPL and stops producing output. Since the human
message that triggers an autonomous serial-log capture can't be reliably
timed against a single ~10s run, the whole sequence repeats indefinitely
instead -- any capture window of a bit more than one cycle is guaranteed
to observe a full cycle, regardless of when it starts. This is diagnostic-
harness shape, not the project's eventual production shape (that will be
an async main loop once Stage 2+ brings asyncio in).

What this proves, if it prints all twelve lines each cycle and the matrix
behaves as described:
  - ``import display`` succeeds on-device (board/neopixel/rainbowio present,
    library's own hardware-import branch fires, LUT builds, NeoPixel
    buffer allocates).
  - Steps 1-6 (Stage 0, confirmed on-device 2026-09-11): ``fill`` /
    ``clear_screen`` / ``set_pixel`` / ``render_icon`` / ``set_brightness`` /
    ``set_rotation`` write real pixels; logical origin (0, 0) is top-left,
    matching the documented wiring LUT (``row + 20 - column * 5``);
    ``set_brightness()`` below 0.02 is visually off, 0.02 is the lowest
    level still visibly lit.
  - Steps 7-12 (Stage 1, broader Tier 1 -- not yet run): ``render_pattern``
    (direct grid-string render), ``render_arrow``, ``get_pixel`` read-back
    (self-checking via a printed match/mismatch, no visual judgment needed),
    ``set_rotation`` at 180/270 (closes the rotation matrix Stage 0 left
    partial), a second icon (generalizes the icon-decode path beyond
    ``HEART``), ``create_image`` (the ``Image.from_pattern`` decode path,
    distinct from ``render_pattern``'s direct-write path), and the
    ``colorwheel`` re-export from ``rainbowio``.
"""

import time

import display
from display import Icons, Arrows

d = display.display

print("Stage 0+1: import display OK")

# Constants for steps 7 and 11 -- built once, not per-cycle, matching the
# module-level Icons/Arrows singletons' own allocate-once pattern.
_DIAMOND = ". . # . .\n. # # # .\n# # # # #\n. # # # .\n. . # . .\n"
_RING_PATTERN = "# # # # #\n# . . . #\n# . # . #\n# . . . #\n# # # # #\n"
_ring_image = display.create_image(_RING_PATTERN, display.ORANGE)

cycle = 0
while True:
    cycle += 1
    # Reset to a known state at the top of every cycle -- set_rotation() rebuilds the LUT
    # for an *absolute* target angle (see lib/display/core.py docstring), so this doesn't
    # drift across cycles, but it does carry the prior cycle's rotation forward if not
    # reset explicitly. Brightness resets to 0.20 -- the library's actual default
    # (lib/display/core.py BRIGHTNESS, not re-exported publicly, hardcoded here to match)
    # -- not to step 4's 0.05 target, so step 4's dimming is visible fresh every cycle
    # instead of only once (a same-value no-op bug caught by Alex, 2026-09-11).
    d.set_rotation(0)
    d.set_brightness(0.20)
    print(f"\n=== cycle {cycle} ===")

    # 1) fill -- confirms NeoPixel init + fill() writes all 25 pixels the same color.
    d.fill(display.RED)
    print("1/12: fill(RED) -- whole 5x5 should be solid red")
    time.sleep(2)

    # 2) set_pixel -- confirms logical origin is top-left, as documented.
    d.clear_screen()
    d.set_pixel(0, 0, display.WHITE)
    print("2/12: set_pixel(0, 0, WHITE) -- exactly one LED lit, top-left corner")
    time.sleep(2)

    # 3) render_icon -- confirms icon-table lookup + column-major bitmap decode.
    d.clear_screen()
    d.render_icon(Icons.HEART, display.RED)
    print("3/12: render_icon(Icons.HEART) -- recognizable heart shape")
    time.sleep(2)

    # 4) set_brightness + set_rotation -- confirms both non-cancelling sync setters;
    #    same heart re-rendered after rotating 90 deg so the shape should visibly turn.
    d.set_brightness(0.05)
    d.set_rotation(90)
    d.render_icon(Icons.HEART, display.RED)
    print("4/12: set_brightness(0.05) + set_rotation(90) -- dimmer, heart rotated 90deg")
    time.sleep(2)

    # 5) done with the Stage-0 core sequence -- reset rotation before the brightness-floor
    #    edge case below so a rotated heart doesn't confuse a test that's only about
    #    brightness.
    d.clear_screen()
    d.set_rotation(0)
    print("5/12: clear_screen -- Stage-0 core sequence done, continuing into brightness-floor check.")
    time.sleep(1)

    # 6) EDGE CASE -- brightness floor. Alex's hypothesis (2026-09-11): below the project's
    #    working 0.05 level, set_brightness() may make the matrix visually indistinguishable
    #    from off (WS2812 duty-cycle/rounding at very low brightness*color products). Fill
    #    once; set_brightness() re-shows the existing buffer at each new level on its own
    #    (verified against lib/display/core.py: the setter calls _pixels.show() itself), so
    #    no need to re-fill per level -- isolates brightness as the only changing variable.
    #    CONFIRMED on-device 2026-09-11: 0.01 and below is visually off; 0.02 is the lowest
    #    level still visibly lit.
    d.fill(display.BLUE)
    for _level in (0.05, 0.04, 0.03, 0.02, 0.01, 0.005, 0.0):
        d.set_brightness(_level)
        print(f"6/12: set_brightness({_level}) -- solid blue fill, watch for the visual floor")
        time.sleep(2)
    d.clear_screen()
    print("6/12: brightness-floor check done. Restoring 0.20 default before Stage-1 steps.")
    d.set_brightness(0.20)
    time.sleep(1)

    # --- Stage 1 (broader Tier 1) starts here -- not yet run on-device. ---

    # 7) render_pattern -- direct grid-string render (no intermediate Image), distinct
    #    code path from render_icon/render_arrow's column-major buffer lookup.
    d.clear_screen()
    d.render_pattern(_DIAMOND, display.GREEN)
    print("7/12: render_pattern(diamond) -- direct grid string, green diamond")
    time.sleep(2)

    # 8) render_arrow -- confirms the arrow table (separate from the icon table, same
    #    column-major decode machinery).
    d.clear_screen()
    d.render_arrow(Arrows.NORTH, display.CYAN)
    print("8/12: render_arrow(Arrows.NORTH) -- arrow pointing up")
    time.sleep(2)

    # 9) get_pixel read-back -- SERIAL SELF-CHECK, no visual judgment needed: prints
    #    whether the read-back value matches what was just written.
    d.clear_screen()
    d.set_pixel(2, 2, display.MAGENTA)
    _readback = d.get_pixel(2, 2)
    _match = "OK" if _readback == display.MAGENTA else "MISMATCH"
    print(f"9/12: set_pixel(2,2,MAGENTA) -> get_pixel(2,2) = {_readback} [{_match}] -- center LED")
    time.sleep(2)

    # 10) second icon at all four rotations -- generalizes icon-decode beyond HEART
    #     (step 3) and closes the rotation matrix Stage 0 only partially covered
    #     (0/90 only; 180/270 untested until now).
    d.clear_screen()
    for _deg in (0, 90, 180, 270):
        d.set_rotation(_deg)
        d.render_icon(Icons.HAPPY, display.YELLOW)
        print(f"10/12: render_icon(Icons.HAPPY) at rotation {_deg}deg")
        time.sleep(1.5)
    d.set_rotation(0)

    # 11) create_image -- exercises Image.from_pattern's decode-at-parse-time path
    #     (distinct from step 7's render_pattern direct-write path); image built once
    #     above the loop, only rendered here.
    d.clear_screen()
    d.render_icon(_ring_image, display.ORANGE)
    print("11/12: create_image(ring pattern) + render_icon -- Image.from_pattern decode path")
    time.sleep(2)

    # 12) colorwheel -- confirms the rainbowio re-export returns a usable RGB tuple.
    d.clear_screen()
    for _hue in (0, 85, 170):
        _c = display.colorwheel(_hue)
        d.fill(_c)
        print(f"12/12: fill(colorwheel({_hue})) -> {_c}")
        time.sleep(1.5)
    d.clear_screen()
    print("12/12: colorwheel sweep done. Cycle complete (Tier 1 sync only, no asyncio).")
    time.sleep(1)

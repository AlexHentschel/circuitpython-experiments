"""Round-1 LED-matrix on-device test -- Stage 1 (Tier 1 sync only, broader).

Additive, not repetitive: Stage 0 (minimal Tier 1 -- ``fill``/``clear_screen``/
``set_pixel``/``render_icon``/``set_brightness``/``set_rotation(90)``/the
brightness-floor edge case) is already confirmed on-device and frozen in the
sibling `code_stage0.py` -- see `CONCLUSIONS.md` for its findings. This script
only exercises what Stage 0 did **not** cover, so a human re-running this
doesn't have to re-watch already-confirmed behaviour. See the LED-matrix test
plan (persona memory, projects/circuitpython-exp16-planetx/SESSION_LOG.md,
Session 17) for the original stage breakdown.

Deliberately does NOT import ``asyncio`` and does NOT touch ``lib/buttons.py``
-- still Tier 1 only, isolating the sync rendering path before K1 (bundle
asyncio) enters the picture at Stage 2.

Looped (``while True``), not one-shot: a CircuitPython script that reaches
its end falls back to the REPL and stops producing output. Since the human
message that triggers an autonomous serial-log capture can't be reliably
timed against a single ~10s run, the whole sequence repeats indefinitely
instead -- any capture window of a bit more than one cycle is guaranteed
to observe a full cycle, regardless of when it starts. This is diagnostic-
harness shape, not the project's eventual production shape (that will be
an async main loop once Stage 2+ brings asyncio in).

What this proves, if it prints all six lines each cycle and the matrix
behaves as described: ``render_pattern`` (direct grid-string render),
``render_arrow``, ``get_pixel`` read-back (self-checking via a printed
match/mismatch, no visual judgment needed), ``set_rotation`` at 180/270
(closes the rotation matrix Stage 0 left partial -- it only exercised
0/90), a second icon (generalizes the icon-decode path beyond Stage 0's
``HEART``), ``create_image`` (the ``Image.from_pattern`` decode path,
distinct from ``render_pattern``'s direct-write path), and the
``colorwheel`` re-export from ``rainbowio``.

At the end of the larger test architecture (once Stage 2/3 are also
confirmed), consider whether a single unified end-to-end script combining
all stages is worth building for a future maintainer to re-run everything
in one go -- ask Alex when that point is reached rather than assuming.
"""

import time

import display
from display import Icons, Arrows

d = display.display

print("Stage 1: import display OK")

# Constants for steps 1 and 5 -- built once, not per-cycle, matching the
# module-level Icons/Arrows singletons' own allocate-once pattern. Multiline
# triple-quoted form, one row per line, columns aligned -- matches
# bitmap_codec.py's own docstring convention; render_pattern/from_pattern
# ignore all whitespace, so this is purely for human readability.
_DIAMOND = """
. . # . .
. # # # .
# # # # #
. # # # .
. . # . .
"""
_RING_PATTERN = """
# # # # #
# . . . #
# . # . #
# . . . #
# # # # #
"""
_ring_image = display.create_image(_RING_PATTERN, display.ORANGE)

cycle = 0
while True:
    cycle += 1
    # Defensive baseline at the top of every cycle: set_rotation() rebuilds the LUT for an
    # *absolute* target angle (see lib/display/core.py docstring), and step 4 below leaves
    # rotation at 0 on its own, but resetting explicitly here keeps every cycle's starting
    # state independent of what a future added step might leave behind. Brightness resets to
    # 0.20 -- the library's actual default (lib/display/core.py BRIGHTNESS, not re-exported
    # publicly, hardcoded here to match); nothing in this script currently changes it, but the
    # explicit reset costs nothing and avoids relying on that staying true.
    d.set_rotation(0)
    d.set_brightness(0.20)
    print(f"\n=== cycle {cycle} ===")

    # 1) render_pattern -- direct grid-string render (no intermediate Image), distinct
    #    code path from render_icon/render_arrow's column-major buffer lookup.
    d.clear_screen()
    d.render_pattern(_DIAMOND, display.GREEN)
    print("1/6: render_pattern(diamond) -- direct grid string, green diamond")
    time.sleep(2)

    # 2) render_arrow -- confirms the arrow table (separate from the icon table, same
    #    column-major decode machinery).
    d.clear_screen()
    d.render_arrow(Arrows.NORTH, display.CYAN)
    print("2/6: render_arrow(Arrows.NORTH) -- arrow pointing up")
    time.sleep(2)

    # 3) get_pixel read-back -- SERIAL SELF-CHECK, no visual judgment needed: prints
    #    whether the read-back value matches what was just written.
    d.clear_screen()
    d.set_pixel(2, 2, display.MAGENTA)
    _readback = d.get_pixel(2, 2)
    _match = "OK" if _readback == display.MAGENTA else "MISMATCH"
    print(f"3/6: set_pixel(2,2,MAGENTA) -> get_pixel(2,2) = {_readback} [{_match}] -- center LED")
    time.sleep(2)

    # 4) second icon at all four rotations -- generalizes icon-decode beyond Stage 0's
    #    HEART and closes the rotation matrix Stage 0 only partially covered (0/90 only;
    #    180/270 untested until now).
    d.clear_screen()
    for _deg in (0, 90, 180, 270):
        d.set_rotation(_deg)
        d.render_icon(Icons.HAPPY, display.YELLOW)
        print(f"4/6: render_icon(Icons.HAPPY) at rotation {_deg}deg")
        time.sleep(1.5)
    d.set_rotation(0)

    # 5) create_image -- exercises Image.from_pattern's decode-at-parse-time path
    #    (distinct from step 1's render_pattern direct-write path); image built once
    #    above the loop, only rendered here.
    d.clear_screen()
    d.render_icon(_ring_image, display.ORANGE)
    print("5/6: create_image(ring pattern) + render_icon -- Image.from_pattern decode path")
    time.sleep(2)

    # 6) colorwheel -- confirms the rainbowio re-export returns a usable RGB tuple.
    d.clear_screen()
    for _hue in (0, 85, 170):
        _c = display.colorwheel(_hue)
        d.fill(_c)
        print(f"6/6: fill(colorwheel({_hue})) -> {_c}")
        time.sleep(1.5)
    d.clear_screen()
    print("6/6: colorwheel sweep done. Cycle complete (Tier 1 sync only, no asyncio).")
    time.sleep(1)

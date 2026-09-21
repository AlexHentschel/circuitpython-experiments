"""Round-1 LED-matrix on-device test, Stage 1 (Tier 1 sync, broader).

Sync rendering only. This script does not import ``asyncio`` and does not
use the button modules.

Stage 0 walked ``fill``, ``clear_screen``, ``set_pixel``, ``render_icon``
(``Icons.HEART``), ``set_brightness``, ``set_rotation(90)``, and the
brightness-floor edge case. We assume that works, and use those calls here
as setup. This script adds the calls Stage 0 did not walk.

What runs:

  1. ``render_pattern`` — a green diamond from a grid string, written
     directly (no ``Image``).
  2. ``render_arrow(Arrows.NORTH)``.
  3. ``set_pixel`` then ``get_pixel`` at (2, 2). Serial prints ``[OK]``
     when the read-back matches ``MAGENTA``.
  4. ``render_icon(Icons.HAPPY)`` at rotations 0, 90, 180, and 270.
  5. ``create_image`` of a ring, then ``render_icon`` of that image.
     ``Image.from_pattern`` decoded it; step 1 writes the grid directly.
  6. ``fill(colorwheel(hue))`` at hues 0, 85, and 170.

Each cycle starts at rotation 0 and brightness 0.20 (the library default).
The sequence repeats so the script does not fall through to the REPL.
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
    # Each cycle starts at rotation 0 and brightness 0.20 (the library
    # default), independent of what the previous cycle left set.
    d.set_rotation(0)
    d.set_brightness(0.20)
    print(f"\n=== cycle {cycle} ===")

    # 1) render_pattern writes the grid string directly. No Image object.
    d.clear_screen()
    d.render_pattern(_DIAMOND, display.GREEN)
    print("1/6: render_pattern(diamond) -- direct grid string, green diamond")
    time.sleep(2)

    # 2) render_arrow(Arrows.NORTH). The arrow table is separate from icons.
    d.clear_screen()
    d.render_arrow(Arrows.NORTH, display.CYAN)
    print("2/6: render_arrow(Arrows.NORTH) -- arrow pointing up")
    time.sleep(2)

    # 3) set_pixel then get_pixel. [OK] means the read-back equals MAGENTA.
    d.clear_screen()
    d.set_pixel(2, 2, display.MAGENTA)
    _readback = d.get_pixel(2, 2)
    _match = "OK" if _readback == display.MAGENTA else "MISMATCH"
    print(f"3/6: set_pixel(2,2,MAGENTA) -> get_pixel(2,2) = {_readback} [{_match}] -- center LED")
    time.sleep(2)

    # 4) Icons.HAPPY at 0, 90, 180, and 270, then back to 0.
    #    Stage 0 used HEART at 0 and 90; we assume that path works.
    d.clear_screen()
    for _deg in (0, 90, 180, 270):
        d.set_rotation(_deg)
        d.render_icon(Icons.HAPPY, display.YELLOW)
        print(f"4/6: render_icon(Icons.HAPPY) at rotation {_deg}deg")
        time.sleep(1.5)
    d.set_rotation(0)

    # 5) The ring Image was built once above. render_icon draws it.
    #    from_pattern decoded it; step 1's render_pattern does not.
    d.clear_screen()
    d.render_icon(_ring_image, display.ORANGE)
    print("5/6: create_image(ring pattern) + render_icon -- Image.from_pattern decode path")
    time.sleep(2)

    # 6) colorwheel(hue) returns an RGB tuple; fill paints the matrix with it.
    d.clear_screen()
    for _hue in (0, 85, 170):
        _c = display.colorwheel(_hue)
        d.fill(_c)
        print(f"6/6: fill(colorwheel({_hue})) -> {_c}")
        time.sleep(1.5)
    d.clear_screen()
    print("6/6: colorwheel sweep done. Cycle complete (Tier 1 sync only, no asyncio).")
    time.sleep(1)

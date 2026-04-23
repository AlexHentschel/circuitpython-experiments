"""
Snapshot of `code.py` at the moment the font-distortion root cause was identified
(2026-04-21). This is the *probe-instrumented* version — it is not the project's
live demo. Companion writeup: ``working-docs/font-distortion-findings.md``.

What this file does on-device:

1. Sleeps 8 s to give the serial terminal time to reconnect after a soft-reboot
   (the CircuitPythonSync "Copy Files to Board" task triggers one).
2. Runs three probes *before* the animation loop, dumping their data once:
     - Probe 2: for each of ``'H'``, ``'a'``, ``'4'`` — the bitmap-font metrics
       (``width / height / dx / dy / shift_x``), the column bytes returned by
       ``_glyph_columns`` (bit 0 = top display row), and a per-row ``#``/``.``
       rendering of those column bytes.
     - Probe 3: the same glyphs' raw pixels read back from the underlying
       ``displayio.Bitmap`` via 1D flat-index (``bm[cx + cy*w]``) *and* 2D tuple
       (``bm[cx, cy]``) access side by side, with an automatic ``MISMATCH``
       marker when the two disagree.
3. Enters the normal animation loop with one modification — stage 3
   ("text scrolling") is replaced by a static hold of a single ``'H'`` glyph
   via ``show_string("H", ...)`` for direct visual comparison against the
   Probe 2 column-byte dump (this is the "Probe 1" test).

How the observed output pins the bug location:

- Probe 3's ``1d == 2d`` for every row => the ``displayio.Bitmap`` pixel storage
  is consistent; no loader-side or indexing-side corruption.
- Probe 2's column bytes exactly match the bit pattern the display renders
  under Probe 1's static hold => ``_render_colmajor`` is faithful.
- The column bytes themselves, however, describe a garbled glyph shape —
  e.g. ``H`` comes back as asymmetric columns with missing top-left and
  bottom-left pixels. Cross-checked with an independent ``struct``-based
  PCF parser on the host, the same bytes are present *in the font file*.

Conclusion: the software pipeline is correct end-to-end; the source of the
distortion is the font file itself (``font_free_mono_8/font.pcf``), which is a
FreeType auto-rasterization of ``FreeMono.ttf`` at ``PIXEL_SIZE: 8`` — a size
at which a TrueType outline font cannot preserve stroke structure. Glyphs are
stored as 3-5 pixel wide bitmaps that do not represent the intended letters.

See the companion findings writeup for the generalization and the fix direction
(swap to a hand-designed bitmap font sized for the 8x8 matrix).

Hardware: YD-RP2040, WS2812b 8x8 matrix on GP0 via level shifter.
"""

import asyncio
import time
from display import (
    display,
    IconNames,
    create_image,
    create_big_image,
    color,
    RED,
    GREEN,
    BLUE,
    CYAN,
    YELLOW,
    PURPLE,
    WHITE,
    GOLD,
    PINK,
    AMBER,
    OFF,
)

# ---------------------------------------------------------------------------
# Multi-color palette example (French flag)
# ---------------------------------------------------------------------------
FLAG_PALETTE = {
    "B": color(0, 0, 255),
    "W": color(255, 255, 255),
    "R": color(255, 0, 0),
    ".": OFF,
}

FLAG_PATTERN = """
B B B W W R R R
B B B W W R R R
B B B W W R R R
B B B W W R R R
B B B W W R R R
B B B W W R R R
B B B W W R R R
B B B W W R R R
"""

# ---------------------------------------------------------------------------
# Image examples
# ---------------------------------------------------------------------------
ARROW_IMAGE = create_image(
    """
. . . # . . . .
. . # # . . . .
. # # # # # # .
# # # # # # # #
. . # # . . . .
. . # # . . . .
. . # # . . . .
. . # # . . . .
""",
    color=CYAN,
)

WIDE_IMAGE = create_big_image(
    """
# . . . . . . . . . . . . . . #
. # . . . . . . . . . . . . # .
. . # . . . . . . . . . . # . .
. . . # . . . . . . . . # . . .
. . . . # . . . . . . # . . . .
. . . . . # . . . . # . . . . .
. . . . . . # . . # . . . . . .
. . . . . . . # # . . . . . . .
""",
    color=GOLD,
)


async def main():
    from display.core import _glyph_columns, _font  # type: ignore[attr-defined]

    # PROBE 2 (diagnostic, temporary): dump column bytes for the characters that visibly distort.
    # Each printed line shows one column byte as 8 bits (bit 0 = top display row, leftmost in the
    # `row 0..7` string). Compare against expected glyph shape to localise the bug in `_glyph_columns`.
    # 8-second delay gives time to reconnect the serial terminal after `CP Copy Files to Board`
    # triggers a soft-reboot; adjust down once the diagnostic is no longer needed.
    time.sleep(8)
    print("Exp14 Phase 2: async display demo")

    print("PROBE 2: glyph column bytes for 'H', 'a', '4'")
    print(f"  font.ascent={_font.ascent}, font.descent={_font.descent}")
    for _ch in "Ha4":
        _g = _font.get_glyph(ord(_ch))
        if _g is None:
            print(f"  {_ch!r}: GLYPH MISSING")
            continue
        print(f"  {_ch!r}: width={_g.width} height={_g.height} dx={_g.dx} dy={_g.dy} shift_x={_g.shift_x}")
        _cols = _glyph_columns(_ch)
        print(f"     len(cols)={len(_cols)}")
        for _i, _b in enumerate(_cols):
            _bits = "".join("#" if (_b >> _y) & 1 else "." for _y in range(8))
            print(f"     col {_i}: 0x{_b:02x}  rows={_bits}")
        # PROBE 3: compare 1D flat-index vs 2D tuple access on the underlying displayio.Bitmap.
        # If the two disagree, `_glyph_columns` is reading via a broken access path and we switch
        # to tuple indexing. Columns show the actual pixel reads side by side, per row.
        _bm = _g.bitmap
        print(f"     bitmap pixel reads (1d = bm[cx+cy*w], 2d = bm[cx, cy]):")
        for _cy in range(_g.height):
            _r1d = "".join("#" if _bm[_cx + _cy * _g.width] else "." for _cx in range(_g.width))
            _r2d = "".join("#" if _bm[_cx, _cy] else "." for _cx in range(_g.width))
            _mark = "  <-- MISMATCH" if _r1d != _r2d else ""
            print(f"     row {_cy}: 1d={_r1d}  2d={_r2d}{_mark}")

    while True:
        # 1. Icon showcase
        print("Icons: HEART, HAPPY, SKULL, BUTTERFLY")
        await display.show_icon(IconNames.HEART, color=RED, interval_ms=800)
        await display.show_icon(IconNames.HAPPY, color=GREEN, interval_ms=800)
        await display.show_icon(IconNames.SKULL, color=WHITE, interval_ms=800)
        await display.show_icon(IconNames.BUTTERFLY, color=PURPLE, interval_ms=800)

        # 2. Arrow cycle
        print("Arrow directions")
        for d in range(8):
            await display.show_arrow(d, color=CYAN, interval_ms=400)

        # 3. Text scrolling
        # PROBE 1 (diagnostic, temporary): static single-char render. If this renders a clean "H",
        # the distortion lives in the scroll path (glyph stitching / buffer layout), not in
        # `_glyph_columns`. If "H" also looks distorted, the bug is in glyph-to-column conversion.
        print("PROBE 1: static 'H' for ~3s")
        await display.show_string("H", color=YELLOW, interval_ms=500)
        await display.pause(300)

        # 4. Number display
        print("Numbers: 42")
        await display.show_number(42, color=AMBER, interval_ms=120)
        await display.pause(300)

        # 5. Single digit (centered)
        print("Single digit: 7")
        await display.show_number(7, color=PINK, interval_ms=200)
        await display.pause(500)

        # 6. Multi-color palette
        print("Multi-color: French flag")
        await display.show_leds(FLAG_PATTERN, color=FLAG_PALETTE, interval_ms=1500)

        # 7. Image display and scroll
        print("Image: arrow")
        await ARROW_IMAGE.show_image(offset=0, interval_ms=1000)

        print("Image: wide scroll")
        await WIDE_IMAGE.scroll_image(offset=1, interval_ms=150)
        await display.pause(300)

        # 8. Recolor demo
        print("Recolor arrow image to RED")
        ARROW_IMAGE.recolor(RED)
        await ARROW_IMAGE.show_image(offset=0, interval_ms=1000)
        ARROW_IMAGE.recolor(CYAN)
        await ARROW_IMAGE.show_image(offset=0, interval_ms=1000)

        # 9. Tier 1 sync demo (works without await)
        print("Tier 1 sync: render_icon + clear")
        display.render_icon(IconNames.GHOST, color=BLUE)
        await display.pause(1000)
        display.clear_screen()
        await display.pause(500)

        print("--- Loop restart ---")


asyncio.run(main())

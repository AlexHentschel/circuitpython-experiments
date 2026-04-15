"""
Exp14 -- Phase 2 Display Library Demo (asyncio)

Showcases the MakeCode-style async API: icons, arrows, text scrolling,
number display, Image class with scrolling, and multi-color palettes.

Hardware: YD-RP2040, WS2812b 8x8 matrix on GP0 via level shifter.
"""

import asyncio
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
    color_palette=CYAN,
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
    color_palette=GOLD,
)


async def main():
    print("Exp14 Phase 2: async display demo")

    while True:
        # 1. Icon showcase
        print("Icons: HEART, HAPPY, SKULL, BUTTERFLY")
        await display.show_icon(IconNames.HEART, color=RED, interval=800)
        await display.show_icon(IconNames.HAPPY, color=GREEN, interval=800)
        await display.show_icon(IconNames.SKULL, color=WHITE, interval=800)
        await display.show_icon(IconNames.BUTTERFLY, color=PURPLE, interval=800)

        # 2. Arrow cycle
        print("Arrow directions")
        for d in range(8):
            await display.show_arrow(d, color=CYAN, interval=400)

        # 3. Text scrolling
        print("Scrolling text: Hello!")
        await display.show_string("Hello!", color=YELLOW, interval=120)
        await display.pause(300)

        # 4. Number display
        print("Numbers: 42")
        await display.show_number(42, color=AMBER, interval=120)
        await display.pause(300)

        # 5. Single digit (centered)
        print("Single digit: 7")
        await display.show_number(7, color=PINK, interval=200)
        await display.pause(500)

        # 6. Multi-color palette
        print("Multi-color: French flag")
        await display.show_leds(FLAG_PATTERN, color_palette=FLAG_PALETTE, interval=1500)

        # 7. Image display and scroll
        print("Image: arrow")
        await ARROW_IMAGE.show_image(offset=0, interval=1000)

        print("Image: wide scroll")
        await WIDE_IMAGE.scroll_image(offset=1, interval=150)
        await display.pause(300)

        # 8. Recolor demo
        print("Recolor arrow image to RED")
        ARROW_IMAGE.recolor(RED)
        await ARROW_IMAGE.show_image(offset=0, interval=1000)
        ARROW_IMAGE.recolor(CYAN)

        # 9. Tier 1 sync demo (works without await)
        print("Tier 1 sync: render_icon + clear")
        display.render_icon(IconNames.GHOST, color=BLUE)
        await display.pause(1000)
        display.clear_screen()
        await display.pause(500)

        print("--- Loop restart ---")


asyncio.run(main())

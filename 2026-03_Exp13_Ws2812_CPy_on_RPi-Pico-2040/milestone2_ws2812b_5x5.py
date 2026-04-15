"""
MILESTONE 2: WS2812b 5x5 Matrix Test
=====================================
Drives a generic 5x5 WS2812b (NeoPixel) matrix via GP0 on the
YD-RP2040 board, through a TTL signal level-shifter module.

BOARD: YD-RP2040 by VCC-GND Studio (RP2040, USB-C, 16 MB flash)

PIN CHOICE: GP0 (physical pin 1 on the left header).

WIRING:
  YD-RP2040 GP0 ──────► Level-Shifter DIN  (signal in, 3.3V)
  Level-Shifter DOUT ──► WS2812b DIN       (signal out, 5V)
  5V PSU (+)  ─────────► WS2812b VCC + Level-Shifter high-voltage VCC (output side)
  GND (common) ────────► YD-RP2040 GND + Level-Shifter GND + WS2812b GND + PSU GND

  ** Do NOT connect Level-Shifter low-voltage VCC (input side) to 3.3V --
     it self-biases to 5V from the output side. Connecting might overload
     the MCU's power rail! **
  ** Common GND across all components is essential. **

PIXEL LAYOUT:
  Generic 5x5 matrices are usually wired in one of two patterns.
  This script lights pixels 0-4 (first five in the chain) so you can
  visually confirm which row/direction they follow.
  Adjust SERPENTINE below once you know your matrix wiring.

REQUIRES:
  circup install neopixel   (installs neopixel.mpy into lib/)
"""

import board
import neopixel
import time

# ---- Configuration ----
PIXEL_PIN = board.GP0  # physical pin 1, left header
NUM_PIXELS = 25  # 5 x 5
BRIGHTNESS = 0.05  # start very dim -- safe for eyes and power
SERPENTINE = True  # set False if your matrix is row-sequential

WIDTH = 5
HEIGHT = 5


# ---- Helper: (col, row) -> pixel index ----
def xy_to_index(x, y):
    """Map (x=col, y=row) to NeoPixel index, accounting for wiring."""
    if SERPENTINE:
        if y & 1 == 0:
            return y * WIDTH + x  # left-to-right
        else:
            return y * WIDTH + (WIDTH - 1 - x)  # right-to-left
    else:
        return y * WIDTH + x


# ---- Colours ----
OFF = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 120, 0)
COLORS = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE, WHITE]

# ---- NeoPixel init ----
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=neopixel.GRB,
)


def clear():
    pixels.fill(OFF)
    pixels.show()


def show_pattern(pattern_str, color=WHITE):
    """Display a 5x5 '#'/'. ' pattern string."""
    lines = [l.strip() for l in pattern_str.strip().splitlines() if l.strip()]
    for y, line in enumerate(lines[:HEIGHT]):
        chars = line.replace(" ", "")
        for x, ch in enumerate(chars[:WIDTH]):
            pixels[xy_to_index(x, y)] = color if ch == "#" else OFF
    pixels.show()


# ---- Test patterns ----
HEART = """
. # . # .
# # # # #
# # # # #
. # # # .
. . # . .
"""

CROSS = """
# . . . #
. # . # .
. . # . .
. # . # .
# . . . #
"""

FRAME = """
# # # # #
# . . . #
# . . . #
# . . . #
# # # # #
"""

CHECKER = """
# . # . #
. # . # .
# . # . #
. # . # .
# . # . #
"""

# ---- Demo routines ----


def test_first_five():
    """Light pixels 0-4 sequentially to help identify wiring direction."""
    print("Lighting pixels 0 -> 4 (first five in chain) one at a time.")
    print("Watch which physical LEDs light up to confirm wiring order.")
    for i in range(5):
        clear()
        pixels[i] = GREEN
        pixels.show()
        print(f"  pixel[{i}] = GREEN")
        time.sleep(1)
    clear()


def test_xy_grid():
    """Light each (col, row) position so you can verify the xy_to_index mapping."""
    print("Lighting (col, row) one by one  -- row-major order.")
    for y in range(HEIGHT):
        for x in range(WIDTH):
            clear()
            idx = xy_to_index(x, y)
            pixels[idx] = CYAN
            pixels.show()
            print(f"  ({x},{y}) -> index {idx}")
            time.sleep(0.4)
    clear()


def test_fill_colors():
    """Fill the entire matrix with each colour."""
    print("Full-matrix colour sweep.")
    for c in COLORS:
        pixels.fill(c)
        pixels.show()
        time.sleep(0.6)
    clear()


def test_patterns():
    """Show several 5x5 patterns."""
    patterns = [
        ("Heart  RED", HEART, RED),
        ("Heart  BLUE", HEART, BLUE),
        ("Cross  YELLOW", CROSS, YELLOW),
        ("Frame  GREEN", FRAME, GREEN),
        ("Checker CYAN", CHECKER, CYAN),
    ]
    for name, pat, col in patterns:
        print(f"  {name}")
        show_pattern(pat, col)
        time.sleep(1.2)
    clear()


def test_brightness_ramp():
    """Ramp brightness from 0 -> 0.3 -> 0 on a heart pattern."""
    print("Brightness ramp (heart pattern, 0 -> 0.3 -> 0).")
    steps = 30
    for i in range(steps):
        pixels.brightness = i / (steps / 0.3)
        show_pattern(HEART, MAGENTA)
        time.sleep(0.05)
    for i in range(steps, -1, -1):
        pixels.brightness = i / (steps / 0.3)
        show_pattern(HEART, MAGENTA)
        time.sleep(0.05)
    pixels.brightness = BRIGHTNESS
    clear()


# ---- Main ----
print()
print("=" * 60)
print("  MILESTONE 2  --  WS2812b 5x5 Matrix Test")
print("=" * 60)
print(f"  Board: YD-RP2040   Pin: GP0   Pixels: {NUM_PIXELS}")
print(f"  Brightness: {BRIGHTNESS}   Serpentine: {SERPENTINE}")
print()

cycle = 0
while True:
    cycle += 1
    print(f"--- cycle {cycle} ---")

    test_first_five()
    time.sleep(0.5)

    test_xy_grid()
    time.sleep(0.5)

    test_fill_colors()
    time.sleep(0.5)

    test_patterns()
    time.sleep(0.5)

    test_brightness_ramp()

    print(f"Cycle {cycle} done. Restarting in 3s...\n")
    time.sleep(3)

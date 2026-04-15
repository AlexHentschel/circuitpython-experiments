"""
MILESTONE 3: Adafruit DotStar FeatherWing 6x12 Test
====================================================
Drives the Adafruit DotStar FeatherWing (6 rows × 12 cols = 72 APA102 LEDs)
from the RP2350 bit board using hardware SPI1:
  Clock : GP10  (SPI1_SCK,  micro:bit edge pad 13)
  Data  : GP11  (SPI1_MOSI, micro:bit edge pad 15)

PIN CHOICE: GP10/GP11 are the dedicated SPI1 hardware pins -- fastest and
  most reliable. GP0/GP1 are NOT used -- they are tied to Button A / Button B.

WIRING  -- Option A  (direct 3.3V -- try this first):
  RP2350 GP11 ────► DotStar DI   (data,  SPI1_MOSI)
  RP2350 GP10 ────► DotStar CI   (clock, SPI1_SCK)
  5V PSU (+)  ────► DotStar VCC
  GND (common) ──► RP2350 GND + DotStar GND + PSU GND

WIRING  -- Option B  (level-shifted 5V via amplifier module in 4-pin mode):
  RP2350 GP11  ──► Amplifier DAT-IN   → DAT-OUT ──► DotStar DI
  RP2350 GP10  ──► Amplifier CLK-IN   → CLK-OUT ──► DotStar CI
  5V PSU       ──► Amplifier high-voltage VCC (output side) + DotStar VCC
  GND          ──► all GNDs
  ** Do NOT connect Amplifier low-voltage VCC (input side) to 3.3V --
     self-biases to 5V from the output side. Connecting might overload the MCU's power rail! **

  APA102 spec says logic-high threshold is 0.7×VCC = 3.5V at 5V supply,
  so 3.3V is marginal.  Option A often works; if you see flicker or
  wrong colours, switch to Option B.

REQUIRES:
  circup install adafruit_dotstar   (installs adafruit_dotstar.mpy into lib/)

FEATHERWING PIXEL LAYOUT (serpentine, active area viewed from front):
  Row 0 (top):    pixel  0 →  11   (left to right)
  Row 1:          pixel 23 ← 12    (right to left)
  Row 2:          pixel 24 →  35   (left to right)
  Row 3:          pixel 47 ← 36    (right to left)
  Row 4:          pixel 48 →  59   (left to right)
  Row 5 (bottom): pixel 71 ← 60    (right to left)
"""

import board
import busio
import adafruit_dotstar
import time

# ---- Configuration ----
# Hardware SPI1: GP10 = SCK (edge pad 13), GP11 = MOSI (edge pad 15)
# GP0 = Button A, GP1 = Button B -- do NOT use for SPI.
CLOCK_PIN = board.GP10  # SPI1_SCK,  micro:bit edge pad 13
DATA_PIN = board.GP11  # SPI1_MOSI, micro:bit edge pad 15
NUM_PIXELS = 72  # 6 × 12
BRIGHTNESS = 0.05  # very dim to start
WIDTH = 12
HEIGHT = 6

# ---- DotStar init (hardware SPI1) ----
_spi = busio.SPI(clock=CLOCK_PIN, MOSI=DATA_PIN)
dots = adafruit_dotstar.DotStar(
    _spi,
    None,
    NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
)

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


# ---- Coordinate mapping (serpentine) ----
def xy_to_index(x, y):
    """Map (x=col 0..11, y=row 0..5) to pixel index for serpentine wiring."""
    if y % 2 == 0:
        return y * WIDTH + x
    else:
        return y * WIDTH + (WIDTH - 1 - x)


def clear():
    dots.fill(OFF)
    dots.show()


def set_pixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        dots[xy_to_index(x, y)] = color


def show_pattern_6x12(pattern_str, color=WHITE):
    """Parse a 6-row × 12-col '#'/'.' pattern and display it."""
    lines = [l.strip() for l in pattern_str.strip().splitlines() if l.strip()]
    for y, line in enumerate(lines[:HEIGHT]):
        chars = line.replace(" ", "")
        for x, ch in enumerate(chars[:WIDTH]):
            dots[xy_to_index(x, y)] = color if ch == "#" else OFF
    dots.show()


# ---- Test patterns (6×12) ----

SMILEY_6x12 = """
. . . # # # # # # . . .
. . # . . . . . . # . .
. # . . # . . # . . # .
. # . . . . . . . . # .
. . # . # . . # . # . .
. . . # . # # . # . . .
"""

FRAME_6x12 = """
# # # # # # # # # # # #
# . . . . . . . . . . #
# . . . . . . . . . . #
# . . . . . . . . . . #
# . . . . . . . . . . #
# # # # # # # # # # # #
"""

STRIPES_H = """
# # # # # # # # # # # #
. . . . . . . . . . . .
# # # # # # # # # # # #
. . . . . . . . . . . .
# # # # # # # # # # # #
. . . . . . . . . . . .
"""

CHECKER_6x12 = """
# . # . # . # . # . # .
. # . # . # . # . # . #
# . # . # . # . # . # .
. # . # . # . # . # . #
# . # . # . # . # . # .
. # . # . # . # . # . #
"""

# ---- Demo routines ----


def test_sequential():
    """Light pixels 0-71 one at a time to verify wiring order."""
    print("Sequential pixel walk (0 → 71)...")
    for i in range(NUM_PIXELS):
        clear()
        dots[i] = GREEN
        dots.show()
        time.sleep(0.04)
    clear()


def test_xy_scan():
    """Scan (col, row) to verify coordinate mapping."""
    print("XY scan (col-major, top-left to bottom-right)...")
    for y in range(HEIGHT):
        for x in range(WIDTH):
            clear()
            dots[xy_to_index(x, y)] = CYAN
            dots.show()
            time.sleep(0.03)
    clear()


def test_row_colors():
    """Each row in a different colour."""
    print("Row colours...")
    for y in range(HEIGHT):
        c = COLORS[y % len(COLORS)]
        for x in range(WIDTH):
            set_pixel(x, y, c)
    dots.show()
    time.sleep(2)
    clear()


def test_column_colors():
    """Each column in a different colour."""
    print("Column colours...")
    for x in range(WIDTH):
        c = COLORS[x % len(COLORS)]
        for y in range(HEIGHT):
            set_pixel(x, y, c)
    dots.show()
    time.sleep(2)
    clear()


def test_fill_colors():
    """Full-matrix colour sweep."""
    print("Colour sweep...")
    for c in COLORS:
        dots.fill(c)
        dots.show()
        time.sleep(0.5)
    clear()


def test_patterns():
    """Show 6×12 patterns."""
    patterns = [
        ("Smiley  GREEN", SMILEY_6x12, GREEN),
        ("Smiley  BLUE", SMILEY_6x12, BLUE),
        ("Frame   RED", FRAME_6x12, RED),
        ("Stripes YELLOW", STRIPES_H, YELLOW),
        ("Checker CYAN", CHECKER_6x12, CYAN),
    ]
    for name, pat, col in patterns:
        print(f"  {name}")
        show_pattern_6x12(pat, col)
        time.sleep(1.5)
    clear()


def test_scrolling_bar():
    """Vertical bar scrolls left to right."""
    print("Scrolling vertical bar...")
    for x_bar in range(WIDTH):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                set_pixel(x, y, MAGENTA if x == x_bar else OFF)
        dots.show()
        time.sleep(0.08)
    clear()


def test_brightness_ramp():
    """Ramp brightness on the smiley pattern."""
    print("Brightness ramp (smiley, 0 → 0.3 → 0)...")
    steps = 30
    for i in range(steps + 1):
        dots.brightness = i * 0.3 / steps
        show_pattern_6x12(SMILEY_6x12, MAGENTA)
        time.sleep(0.04)
    for i in range(steps, -1, -1):
        dots.brightness = i * 0.3 / steps
        show_pattern_6x12(SMILEY_6x12, MAGENTA)
        time.sleep(0.04)
    dots.brightness = BRIGHTNESS
    clear()


# ---- Main ----
print()
print("=" * 56)
print("  MILESTONE 3  --  DotStar FeatherWing 6×12 Test")
print("=" * 56)
print(f"  Data : GP0   Clock: GP1   Pixels: {NUM_PIXELS}")
print(f"  Brightness: {BRIGHTNESS}")
print()

cycle = 0
while True:
    cycle += 1
    print(f"--- cycle {cycle} ---")

    test_sequential()
    time.sleep(0.3)

    test_xy_scan()
    time.sleep(0.3)

    test_row_colors()
    test_column_colors()

    test_fill_colors()
    time.sleep(0.3)

    test_patterns()
    time.sleep(0.3)

    test_scrolling_bar()

    test_brightness_ramp()

    print(f"Cycle {cycle} done. Restarting in 3s...\n")
    time.sleep(3)

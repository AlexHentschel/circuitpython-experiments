"""
MILESTONE 1: GPIO Wire Test for RP2350 Bit Board
=================================================
The original 5x5 Charlieplexed LED matrix has been de-soldered.
Wires were soldered to the LED pads on the RP2350 bit board.
This script tests each of the 10 GPIO pins that drove the matrix.

GPIO PINS (from schematics):
  Column drivers (1K series resistor): GP2, GP3, GP4, GP5, GP25
  Row drivers:                         GP7, GP8, GP9, GP21, GP22

HOW TO TEST:
  1. Connect multimeter (DC voltage) between a wire and GND
  2. Script toggles each GPIO HIGH for 3 sec, then LOW
  3. Console prints which GPIO is currently active
  4. Note which wire shows ~3.3V for each GPIO

ALSO TESTS:
  GP0, GP1 (edge connector large pads) -- these will be used
  for WS2812b and DotStar in later milestones.
"""

import board
import digitalio
import time

# All 10 LED-matrix GPIOs plus the 3 edge-connector pads for LEDs/SPI.
# NOTE: GP0 = Button A, GP1 = Button B on this board -- NOT free GPIOs!
#   Edge pad 3 → GP6   (WS2812b data in Milestone 2)
#   Edge pad 13 → GP10  (DotStar SPI1_SCK in Milestone 3)
#   Edge pad 15 → GP11  (DotStar SPI1_MOSI in Milestone 3)
PINS_TO_TEST = [
    ("GP6  (edge pad 3 - WS2812b data)", board.GP6),
    ("GP10 (edge pad 13 - DotStar SPI1_SCK)", board.GP10),
    ("GP11 (edge pad 15 - DotStar SPI1_MOSI)", board.GP11),
    ("GP2  (LED col driver, 1K resistor)", board.GP2),
    ("GP3  (LED col driver, 1K resistor)", board.GP3),
    ("GP4  (LED col driver, 1K resistor)", board.GP4),
    ("GP5  (LED col driver, 1K resistor)", board.GP5),
    ("GP25 (LED col driver, 1K resistor)", board.GP25),
    ("GP7  (LED row driver)", board.GP7),
    ("GP8  (LED row driver)", board.GP8),
    ("GP9  (LED row driver)", board.GP9),
    ("GP21 (LED row driver)", board.GP21),
    ("GP22 (LED row driver)", board.GP22),
]

pins = []
for label, pin_ref in PINS_TO_TEST:
    dio = digitalio.DigitalInOut(pin_ref)
    dio.direction = digitalio.Direction.OUTPUT
    dio.value = False
    pins.append((label, dio))

HOLD_SECONDS = 3
GAP_SECONDS = 0.5


def all_off():
    for _, dio in pins:
        dio.value = False


def banner():
    print()
    print("=" * 56)
    print("  MILESTONE 1  --  GPIO Wire Test")
    print("=" * 56)
    print()
    print("Pins under test:")
    for label, _ in pins:
        print(f"  - {label}")
    print()
    print(f"Each pin goes HIGH for {HOLD_SECONDS}s, then LOW.")
    print()


def phase_one_by_one():
    """Toggle each pin individually."""
    print("--- Phase 1: One pin at a time ---")
    for label, dio in pins:
        dio.value = True
        print(f"  >>> HIGH : {label}")
        time.sleep(HOLD_SECONDS)
        dio.value = False
        print(f"      LOW  : {label}")
        time.sleep(GAP_SECONDS)


def phase_all_on():
    """All pins HIGH simultaneously -- quick continuity check."""
    print("--- Phase 2: ALL pins HIGH for 5 seconds ---")
    for _, dio in pins:
        dio.value = True
    time.sleep(5)
    all_off()
    print("      ALL pins LOW")


banner()
cycle = 0
while True:
    cycle += 1
    print(f"\n{'='*56}")
    print(f"  Test Cycle {cycle}")
    print(f"{'='*56}\n")
    phase_one_by_one()
    print()
    phase_all_on()
    print()
    print(f"Cycle {cycle} complete. Restarting in 3 seconds...\n")
    time.sleep(3)

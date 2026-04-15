"""
MILESTONE 1: GPIO & Board Test for YD-RP2040
=============================================
Verify that the YD-RP2040 board is running CircuitPython correctly and that
the GPIO pins chosen for LED driving are functional.

BOARD: YD-RP2040 by VCC-GND Studio
  - RP2040, USB-C, 16 MB flash (W25Q128)
  - On-board green LED: board.LED (GP25)
  - On-board WS2812 RGB LED: board.NEOPIXEL / board.RGB (GP23, REQUIRES solder jumper)
  - USR button: board.BUTTON (GP24)

FIRMWARE PIN NAMES (from dir(board)):
  The vcc_gnd_yd_rp2040 CircuitPython build does NOT expose GP23, GP24, GP25
  as named pins. Use the aliases instead:
    board.LED      -> on-board green LED (GP25)
    board.NEOPIXEL -> on-board WS2812 RGB LED (GP23)
    board.RGB      -> same as NEOPIXEL
    board.BUTTON   -> USR button (GP24)

PINS UNDER TEST:
  GP0   -- WS2812b external matrix data pin (Milestone 2)
  GP10  -- SPI1_SCK (general GPIO verification)
  GP11  -- SPI1_MOSI (general GPIO verification)
  GP2-GP5 -- general GPIO verification (optional, no external wiring needed)
  board.LED      -- on-board green LED (blink test, works out of the box)
  board.NEOPIXEL -- on-board WS2812 RGB LED (needs solder jumper closed to be visible)
  board.BUTTON   -- USR button (input test, active low)

HOW TO TEST:
  1. Flash CircuitPython 10.1.4 for vcc_gnd_yd_rp2040 onto the board.
  2. Copy this file's content into code.py (or use cpfiles.txt manifest).
  3. Open a serial monitor (115200 baud).
  4. The script cycles through each test phase.
  5. Use a multimeter (DC voltage between pin and GND) or a breadboard LED
     + 330 Ohm resistor to verify external GPIO signals.

REQUIRES: Only built-in modules (digitalio, neopixel_write, board, time).
"""

import board
import digitalio
import time
import neopixel_write

# ---- On-board green LED (board.LED = GP25) ----
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# ---- USR button (board.BUTTON = GP24, active low) ----
button = digitalio.DigitalInOut(board.BUTTON)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# ---- On-board WS2812 RGB LED (board.NEOPIXEL = GP23) ----
rgb_pin = digitalio.DigitalInOut(board.NEOPIXEL)
rgb_pin.direction = digitalio.Direction.OUTPUT

# ---- External GPIO pins to test ----
PINS_TO_TEST = [
    ("GP0  (WS2812b data -- Milestone 2)", board.GP0),
    ("GP10 (SPI1_SCK -- general GPIO)", board.GP10),
    ("GP11 (SPI1_MOSI -- general GPIO)", board.GP11),
    ("GP2  (general GPIO)", board.GP2),
    ("GP3  (general GPIO)", board.GP3),
    ("GP4  (general GPIO)", board.GP4),
    ("GP5  (general GPIO)", board.GP5),
]

pins = []
for label, gp in PINS_TO_TEST:
    dio = digitalio.DigitalInOut(gp)
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
    print("=" * 60)
    print("  MILESTONE 1  --  YD-RP2040 GPIO & Board Test")
    print("=" * 60)
    print()
    print("Board: YD-RP2040 (VCC-GND Studio), RP2040, 16 MB flash")
    print()
    print("Pins under test:")
    for label, _ in pins:
        print(f"  - {label}")
    print("  - board.LED (on-board green LED, GP25)")
    print("  - board.NEOPIXEL (on-board WS2812 RGB, GP23 -- solder jumper required)")
    print("  - board.BUTTON (USR button, GP24, input)")
    print()
    print(f"Each pin goes HIGH for {HOLD_SECONDS}s, then LOW.")
    print()


def phase_blink_led():
    """Blink the on-board green LED (board.LED) -- immediate visual feedback."""
    print("--- Phase 1: Blink on-board green LED (board.LED / GP25) ---")
    for i in range(6):
        led.value = not led.value
        state = "ON" if led.value else "OFF"
        print(f"  LED: {state}")
        time.sleep(0.5)
    led.value = False


def phase_rgb_led():
    """Drive the on-board WS2812 RGB LED (GP23) via neopixel_write.

    This test is harmless even if the solder jumper is open -- the signal
    is sent but no LED will light up without the jumper.
    """
    print("--- Phase 2: On-board WS2812 RGB LED (board.NEOPIXEL / GP23) ---")
    print("  NOTE: Requires solder jumper to be closed. If the RGB LED")
    print("        does not light up, the jumper is likely open.")

    pixel_buf = bytearray(3)  # GRB order for WS2812

    colors = [
        ("RED", (0, 255, 0)),  # GRB
        ("GREEN", (255, 0, 0)),  # GRB
        ("BLUE", (0, 0, 255)),  # GRB
        ("WHITE", (255, 255, 255)),
        ("OFF", (0, 0, 0)),
    ]
    for name, (g, r, b) in colors:
        pixel_buf[0] = g
        pixel_buf[1] = r
        pixel_buf[2] = b
        neopixel_write.neopixel_write(rgb_pin, pixel_buf)
        print(f"  NEOPIXEL RGB: {name}")
        time.sleep(0.8)


def phase_button():
    """Read the USR button (GP24) for a few seconds."""
    print("--- Phase 3: USR button (board.BUTTON / GP24) -- press to test ---")
    print("  Reading button state for 5 seconds...")
    start = time.monotonic()
    pressed_seen = False
    while time.monotonic() - start < 5:
        if not button.value:  # active low
            if not pressed_seen:
                print("  >>> BUTTON PRESSED")
                pressed_seen = True
        else:
            if pressed_seen:
                print("      Button released")
                pressed_seen = False
        time.sleep(0.05)
    if not pressed_seen:
        print("  (no button press detected)")


def phase_one_by_one():
    """Toggle each external GPIO pin individually."""
    print("--- Phase 4: External GPIO pins one at a time ---")
    for label, dio in pins:
        dio.value = True
        print(f"  >>> HIGH : {label}")
        time.sleep(HOLD_SECONDS)
        dio.value = False
        print(f"      LOW  : {label}")
        time.sleep(GAP_SECONDS)


def phase_all_on():
    """All external GPIO pins HIGH simultaneously."""
    print("--- Phase 5: ALL external GPIO pins HIGH for 5 seconds ---")
    for _, dio in pins:
        dio.value = True
    time.sleep(5)
    all_off()
    print("      ALL pins LOW")


# ---- Main ----
banner()
cycle = 0
while True:
    cycle += 1
    print(f"\n{'=' * 60}")
    print(f"  Test Cycle {cycle}")
    print(f"{'=' * 60}\n")

    phase_blink_led()
    print()

    phase_rgb_led()
    print()

    phase_button()
    print()

    phase_one_by_one()
    print()

    phase_all_on()
    print()

    print(f"Cycle {cycle} complete. Restarting in 3 seconds...\n")
    time.sleep(3)

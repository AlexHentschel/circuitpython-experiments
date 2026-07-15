"""
SANITY CHECK: Blink an external LED on LED_Col1 (GP2)
=====================================================
First bring-up test for Exp15 (micro:bit alternative on the RP2350 bit board).
Toggles a single GPIO so we can confirm the toolchain, board, and a soldered
LED-matrix-pad wire all work end-to-end before building anything larger.

HARDWARE (RP2350 bit board, original 5x5 LED matrix de-soldered):
  LED_Col1 == GP2, driven through the on-board 1K series resistor (R1_LED).
  See docs/removed-LED-matrix-wiring.png for the full former-matrix net map.

WIRING (active-high):
  GP2 (LED_Col1 pad) --[on-board 1K]--> LED anode (+)
  LED cathode (-) ---------------------> GND

  The on-board 1K resistor already limits current (~1.5 mA at 3.3 V), so no
  external resistor is required for this test. GP2 HIGH -> LED on.

EXPECTED:
  LED blinks ~1 Hz (0.5 s on, 0.5 s off). Serial console (115200 baud) prints
  the pin state each toggle.
"""

import board
import digitalio
import time

# LED_Col1 column driver -- GP2, on-board 1K series resistor (R1_LED).
LED_PIN = board.GP2
BLINK_PERIOD_S = 2

led = digitalio.DigitalInOut(LED_PIN)
led.direction = digitalio.Direction.OUTPUT
led.value = False

print()
print("=" * 56)
print("  Exp15 SANITY CHECK -- Blink LED on LED_Col1 (GP2)")
print("=" * 56)
print(f"  Pin: GP2   Period: {BLINK_PERIOD_S * 2:.1f}s   (active-high via 1K)")
print()

while True:
    led.value = True
    print("  GP2 HIGH  (LED on)")
    time.sleep(BLINK_PERIOD_S)
    led.value = False
    print("  GP2 LOW   (LED off)")
    time.sleep(BLINK_PERIOD_S)

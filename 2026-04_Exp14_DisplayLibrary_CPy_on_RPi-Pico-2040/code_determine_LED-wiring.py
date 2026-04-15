"""
Exp14 -- Wiring discovery: light each NeoPixel by strip index, one at a time.

Watch the matrix and note which physical LED lights up for each index.
This reveals the actual wiring order (row direction and starting corner).

Press Ctrl+C in REPL to stop.
"""

import board
import neopixel
import time

NUM_PIXELS = 64
PIXEL_PIN = board.GP0
BRIGHTNESS = 0.05

pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False
)

WHITE = (255, 255, 255)
OFF = (0, 0, 0)

print("Wiring discovery: lighting pixels 0-63 one at a time")
print("Watch which physical LED lights for each index.")
print()

while True:
    for i in range(NUM_PIXELS):
        pixels.fill(OFF)
        pixels[i] = WHITE
        pixels.show()
        print(f"Strip index: {i:2d}")
        time.sleep(0.5)
    pixels.fill(OFF)
    pixels.show()
    print("--- cycle complete, restarting ---")
    time.sleep(1)

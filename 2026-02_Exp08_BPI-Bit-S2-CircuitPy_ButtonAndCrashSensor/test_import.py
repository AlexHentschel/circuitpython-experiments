# Quick test - no library imports
import time
import board
import neopixel

print("=== Quick Test ===")
print("If you see this, basic imports work!")

# NeoPixel test
pixels = neopixel.NeoPixel(board.NEOPIXEL, 25, brightness=0.05, auto_write=False)
pixels.fill((255, 0, 0))
pixels.show()
print("LEDs should be RED now")

time.sleep(1)

# Now test the library import
print("\nTesting elecfreaks_planetx import...")
try:
    from elecfreaks_planetx import Button, Crash
    print("SUCCESS: Library imported!")
except ImportError as e:
    print(f"FAILED: {e}")
    print("\nMake sure lib/elecfreaks_planetx/ folder is on CIRCUITPY drive!")

pixels.fill((0, 255, 0))
pixels.show()
print("LEDs should be GREEN now - test complete")

while True:
    time.sleep(1)

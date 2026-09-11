import time
import board
import neopixel
import keypad


print("Hello World :-)")

# --- Config ---
NUM_PIXELS = 25
BRIGHTNESS = 0.05

# Try the usual onboard NeoPixel pin:
PIXEL_PIN = board.NEOPIXEL   # identical to GPIO18 i.e. `board.IO18`, to which the WS2812 LED Matrix is connected

# NeoPixel object
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
)

# --- Round-1 PlanetX button smoke test (added on top of the pre-existing demo below) ---
# Goal: prove a PlanetX C/D button press fires, by logging it to the serial console.
# Wiring: PlanetX C/D via the Nezha Pro/v2 breakout -> BPI-Bit-S2 J3 -> goldfinger P13/P14
# -> firmware board.IO13/IO14 (source: Notes/bpi_bit_v2_goldfinger.jpg + CP 10.3.0 pins.c,
# both agree: P13->GPIO36, P14->GPIO37). Pull-up, active-low: LOW = pressed.
planetx_keys = keypad.Keys(
    (board.IO13, board.IO14),
    value_when_pressed=False,
    pull=True,
)
_PLANETX_KEY_NAMES = ("C", "D")


def poll_planetx_buttons():
    """Drain any pending PlanetX C/D key events and log presses to the serial console.

    Synchronous poll (not the eventual asyncio dispatcher) -- this is only the round-1
    smoke test proving the wiring + firmware pin identity, called periodically from the
    existing demo loop below.
    """
    event = planetx_keys.events.get()
    while event is not None:
        if event.pressed:
            name = _PLANETX_KEY_NAMES[event.key_number]
            print(f"PlanetX button {name} pressed (key_number={event.key_number})")
        event = planetx_keys.events.get()


# --- Helper for 5x5 Matrix LED, mapping the standard microbit ---
# --- Helper for 5x5 Matrix LED, mapping the standard microbit  ---

def column_row_2_index(column,row):
    """
    Maps standard microbit (column,row) addresses for the 5x5 Matrix LED
    to NeoPixel index. For the physical layout of the BPI-Bit-S2 board,
    the LEDs are addessed the same as on a microbit

           Top of board
    (0,0) (1,0) (2,0) (3,0) (4,0)

    (0,1) (1,1) (2,1) (3,1) (4,1)

    (0,2) (1,2) (2,2) (3,2) (4,2)

    (0,3) (1,3) (2,3) (3,3) (4,3)

    (0,4) (1,4) (2,4) (3,4) (4,4)
          Bottom of board
        with edge connector
    """
    # Internally, the BPI-Bit-S2 board addresses the LEDs as follows
    #         Top of board
    #     (20) (15) (10) (5) (0)
    # 
    #     (21) (16) (11) (6) (1)
    # 
    #     (22) (17) (12) (7) (2)
    # 
    #     (23) (18) (13) (8) (3)
    # 
    #     (24) (19) (14) (9) (4)
    #         Bottom of board
    #      with edge connector
    return row + 20 - column*5 


def set_pixel(column,row, color):
    pixels[column_row_2_index(column,row)] = color

def clear():
    pixels.fill((0, 0, 0))

# --- Demo pattern ---
clear()

# Light a few test pixels
print("light up corner and center pixels")
set_pixel(0, 0, (255, 0, 0))   # top-left red
set_pixel(4, 0, (0, 255, 0))   # top-right green
set_pixel(0, 4, (0, 0, 255))   # bottom-left blue
set_pixel(4, 4, (255, 255, 255)) # bottom-right white
set_pixel(2, 2, (255, 255, 0)) # center yellow

# offset = 20
# pixels[0+offset] = (255, 0, 0)   # top-left red
# pixels[1+offset] = (0, 255, 0)   # top-right green
# pixels[2+offset] = (0, 0, 255)   # bottom-left blue
# pixels[3+offset] = (255, 255, 255) # bottom-right white
# pixels[4+offset] = (255, 255, 0) # center yellow


pixels.show()
time.sleep(2)

# Draw a simple "X" pattern
print("light up X pattern")

clear()
for i in range(5):
    set_pixel(i, i, (255, 0, 255))       # diagonal
    set_pixel(4 - i, i, (0, 255, 255))   # other diagonal
pixels.show()
time.sleep(2)

# Blink the full matrix
print("Blink the full matrix")
for _ in range(3):
    pixels.fill((50, 50, 50))
    pixels.show()
    time.sleep(0.3)
    clear()
    pixels.show()
    time.sleep(0.3)

# Idle loop so it doesn't restart constantly
while True:
    poll_planetx_buttons()
    print("Color snake ..", end="")
    for offset in range(20):
        poll_planetx_buttons()
        clear()        
        pixels[0+offset] = (255, 0, 0)   # top-left red
        pixels[1+offset] = (0, 255, 0)   # top-right green
        pixels[2+offset] = (0, 0, 255)   # bottom-left blue
        pixels[3+offset] = (255, 255, 255) # bottom-right white
        pixels[4+offset] = (255, 255, 0) # center yellow
        pixels.show()
        time.sleep(0.3)
        # print(".", end="")
    print("\n", end="")






# EOF

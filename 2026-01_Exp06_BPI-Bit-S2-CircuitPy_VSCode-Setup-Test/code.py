import time
import board
import neopixel


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
    print("Color snake ..", end="")
    for offset in range(20):
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

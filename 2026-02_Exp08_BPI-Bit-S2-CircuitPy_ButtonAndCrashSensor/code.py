import time
import board
import neopixel
from elecfreaks_planetx import Button, Crash


print("Experiment 08: Button & Crash Sensor Demo")
print("==========================================")

# --- Sensor Pin Configuration ---
# TODO: Configure these pins based on your wiring to the BPI-Bit-S2
# Button sensor uses two pins (C and D buttons)
# Crash sensor uses one pin
#
# Example pin mappings on Nezha V2 expansion board:
#   J1: pin_c=pin1, pin_d=pin8   | crash=pin8
#   J2: pin_c=pin2, pin_d=pin12  | crash=pin12
#   J3: pin_c=pin13, pin_d=pin14 | crash=pin14
#   J4: pin_c=pin15, pin_d=pin16 | crash=pin16

# Placeholder pins - CHANGE THESE to match your wiring!
BUTTON_PIN_C = board.IO15  # Button C pin (J4 equivalent)
BUTTON_PIN_D = board.IO16  # Button D pin (J4 equivalent)
CRASH_PIN = board.IO14     # Crash sensor pin (J3 equivalent)

# --- NeoPixel Config ---
NUM_PIXELS = 25
BRIGHTNESS = 0.05

# Try the usual onboard NeoPixel pin:
PIXEL_PIN = board.NEOPIXEL   # identical to GPIO18 i.e. `board.IO18`, to which the WS2812 LED Matrix is connected

# NeoPixel object
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False
)

# --- Initialize Sensors ---
button = Button(BUTTON_PIN_C, BUTTON_PIN_D)
crash = Crash(CRASH_PIN)

print(f"Button initialized on pins: C={BUTTON_PIN_C}, D={BUTTON_PIN_D}")
print(f"Crash sensor initialized on pin: {CRASH_PIN}")


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

# --- State Variables ---
motor_running = False


# --- Motor Control Stubs ---
# TODO: Replace with actual motor control when Nezha V2 driver is implemented

def rotate_motors(speed_pcts):
    """Rotate motors at specified speed (placeholder)."""
    global motor_running
    motor_running = True
    print(f"[MOTOR] Rotating at {speed_pcts}% speed, 340 degrees CW")

def stop_motors():
    """Stop all motors (placeholder)."""
    global motor_running
    motor_running = False
    print("[MOTOR] Stopped")

def motors_back_to_zero():
    """Reset motors to zero position (placeholder)."""
    global motor_running
    motor_running = False
    print("[MOTOR] Reset to zero position")


# --- Display Helpers ---

def show_letter_c():
    """Display letter C on the LED matrix."""
    clear()
    # Simple C pattern
    set_pixel(1, 0, (0, 255, 0))
    set_pixel(2, 0, (0, 255, 0))
    set_pixel(3, 0, (0, 255, 0))
    set_pixel(0, 1, (0, 255, 0))
    set_pixel(0, 2, (0, 255, 0))
    set_pixel(0, 3, (0, 255, 0))
    set_pixel(1, 4, (0, 255, 0))
    set_pixel(2, 4, (0, 255, 0))
    set_pixel(3, 4, (0, 255, 0))
    pixels.show()

def show_letter_d():
    """Display letter D on the LED matrix."""
    clear()
    # Simple D pattern
    set_pixel(0, 0, (0, 0, 255))
    set_pixel(1, 0, (0, 0, 255))
    set_pixel(2, 0, (0, 0, 255))
    set_pixel(0, 1, (0, 0, 255))
    set_pixel(3, 1, (0, 0, 255))
    set_pixel(0, 2, (0, 0, 255))
    set_pixel(3, 2, (0, 0, 255))
    set_pixel(0, 3, (0, 0, 255))
    set_pixel(3, 3, (0, 0, 255))
    set_pixel(0, 4, (0, 0, 255))
    set_pixel(1, 4, (0, 0, 255))
    set_pixel(2, 4, (0, 0, 255))
    pixels.show()

def show_heart():
    """Display heart icon on the LED matrix."""
    clear()
    # Heart pattern
    set_pixel(1, 0, (255, 0, 0))
    set_pixel(3, 0, (255, 0, 0))
    set_pixel(0, 1, (255, 0, 0))
    set_pixel(1, 1, (255, 0, 0))
    set_pixel(2, 1, (255, 0, 0))
    set_pixel(3, 1, (255, 0, 0))
    set_pixel(4, 1, (255, 0, 0))
    set_pixel(0, 2, (255, 0, 0))
    set_pixel(1, 2, (255, 0, 0))
    set_pixel(2, 2, (255, 0, 0))
    set_pixel(3, 2, (255, 0, 0))
    set_pixel(4, 2, (255, 0, 0))
    set_pixel(1, 3, (255, 0, 0))
    set_pixel(2, 3, (255, 0, 0))
    set_pixel(3, 3, (255, 0, 0))
    set_pixel(2, 4, (255, 0, 0))
    pixels.show()

def show_stop():
    """Display stop indicator (X) on the LED matrix."""
    clear()
    for i in range(5):
        set_pixel(i, i, (255, 0, 0))       # diagonal
        set_pixel(4 - i, i, (255, 0, 0))   # other diagonal
    pixels.show()


# --- Initialization ---
print("\nStarting sensor monitoring...")
show_heart()
time.sleep(1)
clear()
pixels.show()


# --- Main Loop ---
# Implements the logic from the MakeCode example:
# - Button D pressed: show "D", rotate motors, then clear
# - Button C pressed: show "C", reset motors to zero, then clear  
# - Crash sensor triggered: stop motors immediately

print("\nReady! Monitoring sensors...")
print("  - Press button C: Reset motors to zero")
print("  - Press button D: Rotate motors")
print("  - Trigger crash sensor: Emergency stop")
print("")

while True:
    # Check for button D press (start motors)
    if button.D_is_pressed:
        print("Button D pressed!")
        show_letter_d()
        rotate_motors(10)
        time.sleep(0.5)  # Brief display
        clear()
        pixels.show()
    
    # Check for button C press (reset motors)
    elif button.C_is_pressed:
        print("Button C pressed!")
        show_letter_c()
        motors_back_to_zero()
        time.sleep(0.5)  # Brief display
        clear()
        pixels.show()
    
    # Check for both buttons pressed
    elif button.CD_is_pressed:
        print("Both buttons C+D pressed!")
        pixels.fill((255, 255, 0))  # Yellow
        pixels.show()
        time.sleep(0.3)
        clear()
        pixels.show()
    
    # Check crash sensor (emergency stop)
    if crash.Is_pressed:
        print("CRASH SENSOR TRIGGERED")
        if motor_running:
            print("Emergency stop!")
            show_stop()
            stop_motors()
            time.sleep(0.3)
            clear()
            pixels.show()
    
    # Small delay to prevent CPU overload
    time.sleep(0.05)


# EOF

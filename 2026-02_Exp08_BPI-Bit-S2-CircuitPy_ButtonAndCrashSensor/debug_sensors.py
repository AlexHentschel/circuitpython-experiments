# Debug script for Button and Crash sensor
# This prints raw GPIO values to help diagnose connection issues

import time
import board
import digitalio

# --- Pin Configuration ---
BUTTON_PIN_C = board.IO15
BUTTON_PIN_D = board.IO16
CRASH_PIN = board.IO14

print("Button & Crash Sensor Debug")
print("============================")
print(f"Button C pin: {BUTTON_PIN_C}")
print(f"Button D pin: {BUTTON_PIN_D}")
print(f"Crash pin: {CRASH_PIN}")
print("")

# --- Setup pins with pull-up ---
pin_c = digitalio.DigitalInOut(BUTTON_PIN_C)
pin_c.direction = digitalio.Direction.INPUT
pin_c.pull = digitalio.Pull.UP

pin_d = digitalio.DigitalInOut(BUTTON_PIN_D)
pin_d.direction = digitalio.Direction.INPUT
pin_d.pull = digitalio.Pull.UP

crash_pin = digitalio.DigitalInOut(CRASH_PIN)
crash_pin.direction = digitalio.Direction.INPUT
crash_pin.pull = digitalio.Pull.UP

print("Pins configured with PULL_UP")
print("Expected: HIGH (True) when not pressed, LOW (False) when pressed")
print("")
print("Monitoring... Press buttons/sensor to see changes:")
print("Format: [C_raw, D_raw, Crash_raw] -> interpretation")
print("-" * 50)

# Track previous state to only print on changes
prev_state = None

while True:
    c_val = pin_c.value
    d_val = pin_d.value
    crash_val = crash_pin.value
    
    current_state = (c_val, d_val, crash_val)
    
    # Only print when state changes
    if current_state != prev_state:
        # Interpret the values
        status = []
        if not c_val:
            status.append("C_PRESSED")
        if not d_val:
            status.append("D_PRESSED")
        if not crash_val:
            status.append("CRASH_PRESSED")
        
        status_str = ", ".join(status) if status else "all released"
        
        print(f"[C={c_val}, D={d_val}, Crash={crash_val}] -> {status_str}")
        prev_state = current_state
    
    time.sleep(0.05)

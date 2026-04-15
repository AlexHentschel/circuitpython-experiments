import time
import board
import neopixel
import asyncio
import keypad

print("Experiment 08: Asyncio + Keypad Demo")
print("====================================")

# --- Configuration ---
BUTTON_PIN_C = board.IO15
BUTTON_PIN_D = board.IO16
CRASH_PIN = board.IO14
PIXEL_PIN = board.NEOPIXEL
NUM_PIXELS = 25

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.05, auto_write=False)

# Initialize Keypad
# pins=(C, D, Crash)
# value_when_pressed=False (Ground when pressed)
# pull=True (Enable internal pull-ups)
keys = keypad.Keys(
    (BUTTON_PIN_C, BUTTON_PIN_D, CRASH_PIN), 
    value_when_pressed=False, 
    pull=True
)

KEY_C = 0
KEY_D = 1
KEY_CRASH = 2

# Global State
motor_running = False

# --- Helper Functions ---
def clear():
    pixels.fill((0, 0, 0))
    pixels.show()

def set_pixel_map(col, row, color):
    # Map 5x5 matrix (micropython style) to linear index
    idx = row + 20 - col * 5
    if 0 <= idx < 25:
        pixels[idx] = color

def show_icon(char):
    clear()
    if char == 'C':
        for i in range(5): set_pixel_map(0, i, (0, 255, 0))
        for i in range(1, 4): set_pixel_map(i, 0, (0, 255, 0)); set_pixel_map(i, 4, (0, 255, 0))
    elif char == 'D':
        for i in range(5): set_pixel_map(0, i, (0, 0, 255))
        set_pixel_map(1, 0, (0, 0, 255)); set_pixel_map(2, 0, (0, 0, 255))
        set_pixel_map(1, 4, (0, 0, 255)); set_pixel_map(2, 4, (0, 0, 255))
        set_pixel_map(3, 1, (0, 0, 255)); set_pixel_map(3, 2, (0, 0, 255)); set_pixel_map(3, 3, (0, 0, 255))
    elif char == 'STOP':
        pixels.fill((255, 0, 0))
        
    pixels.show()

# --- Async Tasks ---

async def input_monitor_task():
    global motor_running
    print("Task: Keypad monitor started")
    
    # Event loop
    while True:
        event = keys.events.get()
        if event:
            if event.pressed:
                key_num = event.key_number
                
                if key_num == KEY_C:
                    print("EVENT: Button C -> Reset")
                    show_icon('C')
                    motor_running = False
                    # No display hold here to keep responsive, separate display task if needed
                    # but simple is fine for demo
                    
                elif key_num == KEY_D:
                    print("EVENT: Button D -> Start Motor")
                    show_icon('D')
                    motor_running = True
                    
                elif key_num == KEY_CRASH:
                    print(f"DEBUG: Crash Sensor Pressed (Motor state: {motor_running})")
                    if motor_running:
                        print(">>> EMERGENCY STOP <<<")
                        motor_running = False
                        show_icon('STOP')
            
            elif event.released:
                # Optional: handle release
                pass

        # Use sleep(0) to yield to other tasks but check as fast as possible
        await asyncio.sleep(0)

async def motor_task():
    print("Task: Motor runner started")
    while True:
        if motor_running:
            print(f"[MOTOR] Running... {time.monotonic():.1f}")
            # Simulate motor work
        await asyncio.sleep(0.5) # Control loop speed

async def heartbeat_task():
    print("Task: Heartbeat started")
    while True:
        print(f"Heartbeat: {time.monotonic():.1f}")
        await asyncio.sleep(2.0)

async def main():
    await asyncio.gather(
        input_monitor_task(),
        motor_task(),
        heartbeat_task()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

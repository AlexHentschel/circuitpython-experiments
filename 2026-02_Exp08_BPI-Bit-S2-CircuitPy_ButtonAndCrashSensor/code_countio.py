import time
import board
import neopixel
import asyncio
import countio

print("Experiment 08: Asyncio + CountIO (Interrupts)")
print("=============================================")

# --- Configuration ---
BUTTON_PIN_C = board.IO15
BUTTON_PIN_D = board.IO16
CRASH_PIN = board.IO14
PIXEL_PIN = board.NEOPIXEL
NUM_PIXELS = 25

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.05, auto_write=False)

# Global State
motor_running = False

# --- Helper Functions ---
def clear():
    pixels.fill((0, 0, 0))
    pixels.show()

def set_pixel_map(col, row, color):
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

async def monitor_pin_edges(pin, name):
    """
    Monitor falling edges (high -> low) for buttons/sensors pulled high.
    This effectively acts as an interrupt handler.
    """
    global motor_running
    
    # countio monitors hardware interrupts/edges
    # Buttons are active LOW, so we watch for falling edges (press)
    with countio.Counter(pin, edge=countio.Edge.FALL_INT) as counter:
        print(f"Task: Monitoring {name} on {pin}")
        
        while True:
            # Check if any edges were counted
            if counter.count > 0:
                print(f"INTERRUPT: {name} triggered! ({counter.count} times)")
                
                # Reset count for next batch
                counter.reset()
                
                # Handle Logic
                if name == "Button C":
                    print("ACTION: Reset Motors")
                    show_icon('C')
                    motor_running = False
                    await asyncio.sleep(0.5) # Debounce/hold time
                    clear()
                    
                elif name == "Button D":
                    print("ACTION: Start Motors")
                    show_icon('D')
                    motor_running = True
                    await asyncio.sleep(0.5) # Debounce/hold time
                    clear()
                    
                elif name == "Crash Sensor":
                    print(f"ACTION: Crash Detected (Motor={motor_running})")
                    if motor_running:
                        print(">>> EMERGENCY STOP <<<")
                        motor_running = False
                        show_icon('STOP')
                        await asyncio.sleep(1.0) # Hold stop sign
                        clear()

            # Yield to let other tasks run
            # With countio, we can sleep longer or just 0
            await asyncio.sleep(0)

async def motor_task():
    print("Task: Motor runner started")
    while True:
        if motor_running:
            print(f"[MOTOR] Running... {time.monotonic():.1f}")
        await asyncio.sleep(0.5)

async def heartbeat_task():
    print("Task: Heartbeat started")
    while True:
        if not motor_running:
            print(f"Heartbeat: {time.monotonic():.1f}")
        await asyncio.sleep(2.0)

async def main():
    # Use gather to run everything concurrently
    # Note: countio requires creating the Counter object inside the task 
    # or passing it in, but 'with' context managers are tricky across tasks.
    # The structure in monitor_pin_edges handles it cleanly per pin.
    
    await asyncio.gather(
        monitor_pin_edges(BUTTON_PIN_C, "Button C"),
        monitor_pin_edges(BUTTON_PIN_D, "Button D"),
        monitor_pin_edges(CRASH_PIN, "Crash Sensor"),
        motor_task(),
        heartbeat_task()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

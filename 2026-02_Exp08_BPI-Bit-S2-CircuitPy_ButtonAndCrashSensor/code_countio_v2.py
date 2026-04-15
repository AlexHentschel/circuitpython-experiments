import digitalio
import board
import countio
import asyncio
import neopixel

print("Experiment 08: CountIO (Interrupts) - v2")
print("===============================================")


# --- Configuration ---
BUTTON_PIN_C = board.IO15
BUTTON_PIN_D = board.IO16
CRASH_PIN = board.IO14
PIXEL_PIN = board.NEOPIXEL
NUM_PIXELS = 25

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.05, auto_write=False)
motor_running = False

def clear():
    pixels.fill((0, 0, 0))
    pixels.show()

def show_icon(char):
    clear()
    if char == 'C':
        pixels[12] = (0, 255, 0)
    elif char == 'D':
        pixels[12] = (0, 0, 255)
    elif char == 'STOP':
        pixels.fill((255, 0, 0))
    pixels.show()

async def monitor_pin(pin_num, name):
    global motor_running
    # Use CountIO to detect falling edges (active LOW press)
    with countio.Counter(pin_num, edge=countio.Edge.FALL, pull=None) as counter:
        # Note: Internal pull-ups need to be set externally first if countio doesn't support them directly
        # or use external resistors.
        # However, countio usually wraps a digitalio pin. CircuitPython countio takes 'pin_id'
        # The docs state: class countio.Counter(pin_a: microcontroller.Pin, *, edge: Edge = Edge.RISE, pull: digitalio.Pull = digitalio.Pull.UP)
        
        while True:
            if counter.count > 0:
                print(f"INTERRUPT: {name} ({counter.count})")
                counter.reset()
                
                if name == "Button C":
                    motor_running = False
                    show_icon('C')
                elif name == "Button D":
                    motor_running = True
                    show_icon('D')
                elif name == "Crash":
                    if motor_running:
                        print("!!! EMERGENCY STOP !!!")
                        motor_running = False
                        show_icon('STOP')

            await asyncio.sleep(0)

async def main():
    # Setup Pull-Ups first if countio doesn't handle them automatically in your version
    # Check if Counter supports 'pull' argument (recent CircuitPython versions do)
    
    # We will instantiate tasks with explicit pull configuration inside the tasks
    # Re-writing the monitor to be safe
    pass

# Standard async main logic
async def monitor_c():
    global motor_running
    with countio.Counter(BUTTON_PIN_C, edge=countio.Edge.FALL, pull=digitalio.Pull.UP) as c:
         while True:
            if c.count > 0:
                c.reset()
                print("Button C Pressed -> Stop")
                motor_running = False
                show_icon('C')
                await asyncio.sleep(0.2)
            await asyncio.sleep(0)

async def monitor_d():
    global motor_running
    with countio.Counter(BUTTON_PIN_D, edge=countio.Edge.FALL, pull=digitalio.Pull.UP) as c:
         while True:
            if c.count > 0:
                c.reset()
                print("Button D Pressed -> Start")
                motor_running = True
                show_icon('D')
                await asyncio.sleep(0.2)
            await asyncio.sleep(0)

async def monitor_crash():
    global motor_running
    with countio.Counter(CRASH_PIN, edge=countio.Edge.FALL, pull=digitalio.Pull.UP) as c:
         while True:
            if c.count > 0:
                c.reset()
                print("Crash Sensor Triggered")
                if motor_running:
                    print(">>> EMERGENCY STOP <<<")
                    motor_running = False
                    show_icon('STOP')
                    await asyncio.sleep(0.5)
            await asyncio.sleep(0)

async def heartbeat():
    while True:
        if not motor_running:
            print(".")
        await asyncio.sleep(2.0)

async def run_all():
    await asyncio.gather(monitor_c(), monitor_d(), monitor_crash(), heartbeat())

if __name__ == "__main__":
    asyncio.run(run_all())

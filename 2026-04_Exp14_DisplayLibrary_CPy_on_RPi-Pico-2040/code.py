"""
Exp14 -- Icon review: cycle through all icons, pause/resume with USR button.

Press the USR button (GP24) to pause on the current icon.
Press again to resume cycling.
Serial output shows the icon index and name for each displayed icon.
"""

import time
import board
import digitalio
from display import display, IconNames, WHITE

# --- Icon name table (index -> name) for serial output ---
ICON_NAMES = [attr for attr in dir(IconNames) if not attr.startswith("_")]
ICON_NAMES.sort(key=lambda name: getattr(IconNames, name))
NUM_ICONS = len(ICON_NAMES)

# --- USR button (active low, internal pull-up) ---
btn = digitalio.DigitalInOut(board.BUTTON)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP


def wait_release():
    """Block until button is released (debounced)."""
    while not btn.value:
        time.sleep(0.02)
    time.sleep(0.05)


def button_pressed():
    """Return True on a falling edge (press), with debounce."""
    if not btn.value:
        wait_release()
        return True
    return False


print(f"Icon review: cycling {NUM_ICONS} icons")
print("Press USR button to pause/resume.\n")

i = 0
while True:
    name = ICON_NAMES[i]
    idx = getattr(IconNames, name)
    display.render_icon(idx, color=WHITE)
    print(f"[{idx:2d}] {name}")

    # Hold each icon for 4s, checking for button press throughout
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        if button_pressed():
            print("  ** PAUSED -- press button to resume **")
            while not button_pressed():
                time.sleep(0.05)
            print("  ** RESUMED **")
            break
        time.sleep(0.05)

    i = (i + 1) % NUM_ICONS

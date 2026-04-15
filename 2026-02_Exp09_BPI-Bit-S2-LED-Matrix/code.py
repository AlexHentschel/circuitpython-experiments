import time
import display

print("Display MakeCode-Style Demo starting...")

# Define patterns using MakeCode-style syntax
HEART_PATTERN = """
. # . # .
# # # # #
# # # # #
. # # # .
. . # . .
"""

HAPPY_PATTERN = """
. . . . .
. # . # .
. . . . .
# . . . #
. # # # .
"""

WINK_PATTERN = """
. . . . .
. # . # .
. . . . .
# . . . #
. # # # .
"""

EYES_CLOSED_PATTERN = """
. . . . .
. . . . .
. . . . .
# # # # #
. . . . .
"""

while True:
    # 1. Pulse HEART in BLUE (custom color tuple)
    print("Heart (BLUE)")
    display.display.show_leds(HEART_PATTERN, color=(0, 0, 255))
    display.display.clear()
    time.sleep(0.3)    
    display.display.show_leds(HEART_PATTERN, color=(0, 0, 255))
    display.display.clear()
    time.sleep(0.3)    
    display.display.show_leds(HEART_PATTERN, color=(0, 0, 255))
    display.display.clear()
    time.sleep(0.3)    

    # 2. Same HEART in RED with pre-defined color constants
    print("Heart (RED)")
    for c in [display.RED, display.DARKRED, display.CORAL,
              display.DEEPPINK,  display.FUCHSIA, 
              display.GREEN, display.DARKOLIVEGREEN, display.LIME, display.SPRINGGREEN,
              display.BLUE,  display.DARKBLUE, display.DARKSLATEBLUE,  display.AQUA, 
              display.ORANGE, display.YELLOW, display.YELLOWGREEN, 
              display.WHITE, display.PLUM, display.GRAY]:
    # for c in [display.RED, display.GRAY, display.DARKOLIVEGREEN, display.MAROON, display.DARKSLATEBLUE, display.GREEN, display.YELLOWGREEN, display.DARKBLUE, display.ORANGE, display.YELLOW, display.LIME, display.SPRINGGREEN, display.BLUE, display.AQUA, display.CORAL, display.FUCHSIA, display.DEEPPINK, display.PLUM, display.KHAKI]:
        display.display.show_leds(HEART_PATTERN, color=c)
        time.sleep(1)
        display.display.clear()
        time.sleep(0.3)    



    # 3. Show HAPPY Face in GREEN
    print("Happy (GREEN)")
    display.display.show_leds(HAPPY_PATTERN, color=display.GREEN)
    time.sleep(1)

    # 4. Simple animation: Blink an eye
    print("Animation: Wink")
    
    # Wink (one eye closed) - Actually let's redefine proper wink
    WINK_ACTUAL = """
    . . . . .
    . # . . .
    . . . . .
    # . . . #
    . # # # .
    """
    display.display.show_leds(WINK_ACTUAL, color=(255, 255, 0)) # Yellow
    time.sleep(0.5)
    
    # Open both eyes
    display.display.show_leds(HAPPY_PATTERN, color=(255, 255, 0))
    time.sleep(0.5)

    display.display.clear()
    time.sleep(0.5)

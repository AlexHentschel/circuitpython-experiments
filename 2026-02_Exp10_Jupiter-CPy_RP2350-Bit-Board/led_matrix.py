import board
import digitalio
import time

class LEDMatrix5x5:
    # GPIO mapping from README
    COL_PINS = [board.GP2, board.GP3, board.GP4, board.GP5, board.GP25]
    ROW_PINS = [board.GP7, board.GP8, board.GP9, board.GP21, board.GP22]

    def __init__(self):
        self.cols = [digitalio.DigitalInOut(pin) for pin in self.COL_PINS]
        self.rows = [digitalio.DigitalInOut(pin) for pin in self.ROW_PINS]
        for col in self.cols:
            col.direction = digitalio.Direction.OUTPUT
            col.value = False  # Columns are active high (default off)
        for row in self.rows:
            row.direction = digitalio.Direction.OUTPUT
            row.value = True  # Rows are active low (default off)

    def light_pixel(self, x, y, duration=0.1):
        # Turn off all columns (set low)
        for col in self.cols:
            col.value = False
        # Set all rows high (inactive)
        for row in self.rows:
            row.value = True
        # Activate selected column (set high)
        self.cols[x].value = True
        # Activate selected row (set low)
        self.rows[y].value = False
        time.sleep(duration)
        # Reset: all columns low, all rows high
        for col in self.cols:
            col.value = False
        for row in self.rows:
            row.value = True

# Example usage:
# matrix = LEDMatrix5x5()
# matrix.light_pixel(2, 3)  # Light up pixel at (2,3) for 0.1s

# Micro:bit compatibility module for BPI-Bit-S2
# Emulates the 'microbit' module API for the 5x5 LED Matrix

"""
Micro:bit Compatibility Module for BPI-Bit-S2
=============================================

This module emulates the core ``microbit`` Python API for the BPI-Bit-S2 board's
5x5 WS2812B (NeoPixel) LED Matrix.

TODO: update

Key Features:
- **Image Class**: Supports standard 5x5 icons (HEART, HAPPY, ARROWS, CLOCKS, etc.) and string-based image definition.
- **Display Object**: Implements ``microbit.display`` methods:
  - ``show(image)``: Render an image or animation.
  - ``clear()``: Turn off all pixels.
  - ``set_pixel(x, y, brightness)``: Set individual pixels (0-9 brightness).
- **Physical Mapping**: Maps logical Micro:bit coordinates (0,0 is top-left) to the BPI-Bit-S2's specific NeoPixel wiring order.
- **Color Mapping**: Maps 0-9 brightness levels to Red color intensity to mimic the original Micro:bit display.
"""

import board
import neopixel
import time

# --- Hardware Configuration for BPI-Bit-S2 ---
_NUM_PIXELS = 25
_PIXEL_PIN = board.NEOPIXEL
_BRIGHTNESS = 0.1 # Default brightness

# Internal NeoPixel object
_pixels = neopixel.NeoPixel(
    _PIXEL_PIN,
    _NUM_PIXELS,
    brightness=_BRIGHTNESS,
    auto_write=False,
)

def _column_row_2_index(column, row):
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

    WARNING: Does NOT perform bounds checking for performance. 
    Caller must ensure column/row are within 0-4.
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
    return row + 20 - column * 5

class Image:
    """
    Represents a Micro:bit 5x5 LED image.

    This class handles standard Micro:bit image strings (e.g., '09090:99999...') 
    where '0' is off and '9' is maximum brightness.

    Attributes:
        _buffer (bytearray): Flattened 5x5 brightness data (0-9).
    """

    def __init__(self, data=None):
        self._width = 5
        self._height = 5
        
        if data is None: # empty image, i.e. LED matrix is off. 
            self._buffer = bytearray(25)
        elif isinstance(data, (bytes, bytearray)):
            if len(data) == 25:
                # Direct load - optimized path, avoid copy
                self._buffer = bytearray(data)
            else:
                 # allocate buffer of correct size and copy as much as fits, since we have a fixed 5x5 LED grid
                 self._buffer = bytearray(25)
                 l = min(len(data), 25)
                 self._buffer[:l] = data[:l]
        elif isinstance(data, str):
            self._buffer = bytearray(25)
            self._parse_string(data)
        else:
            raise TypeError("Image data must be bytes, bytearray, or string")
    
    def _parse_string(self, s):
        # Handle string input like "09090:99999:..." or single char
        # Clean up whitespace and colons
        rows = s.replace(':', '').split('\n')
        # If it was a single string with colons but no newlines, rows might be just one element
        if len(rows) == 1 and ':' in s:
             rows = s.split(':')
        
        # Filter empty strings if any
        rows = [r.strip() for r in rows if r.strip()]
        
        # if input is just one long string of digits without separators
        if len(rows) == 1 and len(rows[0]) == 25:
             # Just strict 25 chars
             vals = rows[0]
             for i in range(25):
                 self._buffer[i] = int(vals[i])
             return

        # otherwise parsing row by row
        for r_idx, row_str in enumerate(rows):
            if r_idx >= 5: break
            for c_idx, char in enumerate(row_str):
                if c_idx >= 5: break
                val = 0
                if '0' <= char <= '9':
                    val = int(char)
                self.set_pixel(c_idx, r_idx, val)

    def width(self):
        return self._width

    def height(self):
        return self._height

    def set_pixel(self, x, y, value):
        if 0 <= x < 5 and 0 <= y < 5 and 0 <= value <= 9:
             self._buffer[y * 5 + x] = value

    def get_pixel(self, x, y):
        # Optimized: removed bounds width/height check since fixed at 5x5
        if 0 <= x < 5 and 0 <= y < 5:
            return self._buffer[y * 5 + x]
        return 0
    
    def crop(self, x, y, w, h):
        """
        Return a new Image by cropping this image.

        Args:
            x (int): The x-coordinate to start the crop.
            y (int): The y-coordinate to start the crop.
            w (int): The width of the cropped area.
            h (int): The height of the cropped area.

        Returns:
            Image: A new Image object containing the cropped area. 
                   (Note: In this 5x5 emulation, the result is still a 5x5 Image 
                   object but with the cropped content drawn into it starting at 0,0).
        """
        res = Image() 
        for dy in range(h):
            for dx in range(w):
                val = self.get_pixel(x + dx, y + dy)
                res.set_pixel(dx, dy, val)
        return res

    def copy(self):
        new_img = Image()
        new_img._buffer = bytearray(self._buffer)
        return new_img

    def invert(self):
        new_img = Image()
        for i in range(25):
            new_img._buffer[i] = 9 - self._buffer[i]
        return new_img
        
    def shift_left(self, n):
        # Returns a new image
        new_img = Image()
        for y in range(5):
            for x in range(5):
                src_x = x + n
                if 0 <= src_x < 5:
                    new_img.set_pixel(x, y, self.get_pixel(src_x, y))
        return new_img

    def shift_right(self, n):
        return self.shift_left(-n)

    def shift_up(self, n):
        new_img = Image()
        for y in range(5):
            for x in range(5):
                src_y = y + n
                if 0 <= src_y < 5:
                    new_img.set_pixel(x, y, self.get_pixel(x, src_y))
        return new_img
    
    def shift_down(self, n):
        return self.shift_up(-n)

    def __repr__(self):
        return "Image(...)"

    def __add__(self, other):
        # Superposition - Microbit docs say: 
        # "Images can be added together... The values of each pixel are added..."
        new_img = Image()
        for i in range(25):
            val = self._buffer[i] + other._buffer[i]
            new_img._buffer[i] = min(9, val)
        return new_img
    
    def __sub__(self, other):
        new_img = Image()
        for i in range(25):
            val = self._buffer[i] - other._buffer[i]
            new_img._buffer[i] = max(0, val)
        return new_img
    
    def __mul__(self, other):
         # Scalar mult
         if isinstance(other, (int, float)):
            new_img = Image()
            for i in range(25):
                val = int(self._buffer[i] * other) // 81 # normalize by 9*9 to keep in 0-9 range
                new_img._buffer[i] = min(9, max(0, val))
            return new_img
         return NotImplemented


# --- Standard Images ---
# Defined to use 'bytes' for memory efficiency
# Bbyte string b'\t' is an immutable sequence containing a single byte with the value 9 (decimal), which is the ASCII value for the horizontal tab character.
Image.HEART = Image(b'\x00\t\x00\t\x00\t\t\t\t\t\t\t\t\t\t\x00\t\t\t\x00\x00\x00\t\x00\x00')
Image.HEART_SMALL = Image(b'\x00\x00\x00\x00\x00\x00\t\x00\t\x00\x00\t\t\t\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00')
Image.HAPPY = Image(b'\x00\x00\x00\x00\x00\x00\t\x00\t\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\t\t\t\x00')
Image.SMILE = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\t\t\t\x00')
Image.SAD = Image(b'\x00\x00\x00\x00\x00\x00\t\x00\t\x00\x00\x00\x00\x00\x00\x00\t\t\t\x00\t\x00\x00\x00\t')
Image.CONFUSED = Image(b'\x00\x00\x00\x00\x00\x00\t\x00\t\x00\x00\x00\x00\x00\x00\x00\t\x00\t\x00\t\x00\t\x00\t')
Image.ANGRY = Image(b'\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\x00\x00\x00\t\t\t\t\t\t\x00\t\x00\t')
Image.ASLEEP = Image(b'\x00\x00\x00\x00\x00\t\t\x00\t\t\x00\x00\x00\x00\x00\x00\t\t\t\x00\x00\x00\x00\x00\x00')
Image.SURPRISED = Image(b'\x00\t\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\x00\x00\t\x00\x00')
Image.SILLY = Image(b'\t\x00\x00\x00\t\x00\x00\x00\x00\x00\t\t\t\t\t\x00\x00\t\x00\t\x00\x00\t\t\t')
Image.FABULOUS = Image(b'\t\t\t\t\t\t\t\x00\t\t\x00\x00\x00\x00\x00\x00\t\x00\t\x00\x00\t\t\t\x00')
Image.MEH = Image(b'\x00\t\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00')
Image.YES = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t\x00\x00\x00')
Image.NO = Image(b'\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t')
Image.CLOCK12 = Image(b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Image.CLOCK11 = Image(b'\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Image.CLOCK10 = Image(b'\x00\x00\x00\x00\x00\t\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Image.CLOCK9 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\t\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Image.CLOCK8 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\t\t\x00\x00\x00\x00\x00\x00\x00\x00')
Image.CLOCK7 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00')
Image.CLOCK6 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00')
Image.CLOCK5 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00')
Image.CLOCK4 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\t\x00\x00\x00\x00\x00')
Image.CLOCK3 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\t\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Image.CLOCK2 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00').shift_right(1)
Image.CLOCK1 = Image(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
Image.ARROW_N = Image(b'\x00\x00\t\x00\x00\x00\t\t\t\x00\t\x00\t\x00\t\x00\x00\t\x00\x00\x00\x00\t\x00\x00')
Image.ARROW_NE = Image(b'\x00\x00\t\t\t\x00\x00\x00\t\t\x00\x00\t\x00\t\x00\t\x00\x00\x00\t\x00\x00\x00\x00')
Image.ARROW_E = Image(b'\x00\x00\t\x00\x00\x00\x00\x00\t\x00\t\t\t\t\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00')
Image.ARROW_SE = Image(b'\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00\t\x00\x00\x00\t\t\x00\x00\t\t\t')
Image.ARROW_S = Image(b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\t\x00\t\x00\t\x00\t\t\t\x00\x00\x00\t\x00\x00')
Image.ARROW_SW = Image(b'\x00\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\t\t\x00\x00\x00\t\t\t\x00\x00')
Image.ARROW_W = Image(b'\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\t\t\t\t\x00\t\x00\x00\x00\x00\x00\t\x00\x00')
Image.ARROW_NW = Image(b'\t\t\t\x00\x00\t\t\x00\x00\x00\t\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t')
Image.TRIANGLE = Image(b'\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\t\t\t\t\t\x00\x00\x00\x00\x00')
Image.TRIANGLE_LEFT = Image(b'\t\x00\x00\x00\x00\t\t\x00\x00\x00\t\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00')
Image.CHESSBOARD = Image(b'\x00\t\x00\t\x00\t\x00\t\x00\t\x00\t\x00\t\x00\t\x00\t\x00\t\x00\t\x00\t\x00')
Image.DIAMOND = Image(b'\x00\x00\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t\x00\x00')
Image.DIAMOND_SMALL = Image(b'\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00')
Image.SQUARE = Image(b'\t\t\t\t\t\t\x00\x00\x00\t\t\x00\x00\x00\t\t\x00\x00\x00\t\t\t\t\t\t')
Image.SQUARE_SMALL = Image(b'\x00\x00\x00\x00\x00\x00\t\t\t\x00\x00\t\x00\t\x00\x00\t\t\t\x00\x00\x00\x00\x00\x00')
Image.RABBIT = Image(b'\t\x00\t\x00\x00\t\x00\t\x00\x00\t\t\t\t\x00\t\t\x00\t\x00\t\t\t\t\x00')
Image.COW = Image(b'\t\x00\x00\x00\t\t\x00\x00\x00\t\t\t\t\t\t\x00\t\t\t\x00\x00\x00\t\x00\x00')
Image.MUSIC_CROTCHET = Image(b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\t\t\t\x00\x00\t\t\t\x00\x00')
Image.MUSIC_QUAVER = Image(b'\x00\x00\t\x00\x00\x00\x00\t\t\x00\x00\x00\t\x00\t\t\t\t\x00\x00\t\t\t\x00\x00')
Image.MUSIC_QUAVERS = Image(b'\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\x00\x00\t\t\t\x00\t\t\t\t\x00\t\t')
Image.PITCHFORK = Image(b'\t\x00\t\x00\t\t\x00\t\x00\t\t\t\t\t\t\x00\x00\t\x00\x00\x00\x00\t\x00\x00')
Image.XMAS = Image(b'\x00\x00\t\x00\x00\x00\t\t\t\x00\x00\x00\t\x00\x00\x00\t\t\t\x00\t\t\t\t\t')
Image.PACMAN = Image(b'\x00\t\t\t\t\t\t\x00\t\x00\t\t\t\x00\x00\t\t\t\t\x00\x00\t\t\t\t')
Image.TARGET = Image(b'\x00\x00\t\x00\x00\x00\t\t\t\x00\t\t\x00\t\t\x00\t\t\t\x00\x00\x00\t\x00\x00')
Image.TSHIRT = Image(b'\t\t\x00\t\t\t\t\t\t\t\x00\t\t\t\x00\x00\t\t\t\x00\x00\t\t\t\x00')
Image.ROLLERSKATE = Image(b'\x00\x00\x00\t\t\x00\x00\x00\t\t\t\t\t\t\t\t\t\t\t\t\x00\t\x00\t\x00')
Image.DUCK = Image(b'\x00\t\t\x00\x00\t\t\t\x00\x00\x00\t\t\t\t\x00\t\t\t\x00\x00\x00\x00\x00\x00')
Image.HOUSE = Image(b'\x00\x00\t\x00\x00\x00\t\t\t\x00\t\t\t\t\t\x00\t\t\t\x00\x00\t\x00\t\x00')
Image.TORTOISE = Image(b'\x00\x00\x00\x00\x00\x00\t\t\t\x00\t\t\t\t\t\x00\t\x00\t\x00\x00\x00\x00\x00\x00')
Image.BUTTERFLY = Image(b'\t\t\x00\t\t\t\t\t\t\t\x00\x00\t\x00\x00\t\t\t\t\t\t\t\x00\t\t')
Image.STICKFIGURE = Image(b'\x00\x00\t\x00\x00\t\t\t\t\t\x00\x00\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t')
Image.GHOST = Image(b'\t\t\t\t\t\t\x00\t\x00\t\t\t\t\t\t\t\t\t\t\t\t\x00\t\x00\t')
Image.SWORD = Image(b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\t\t\t\x00\x00\x00\t\x00\x00')
Image.GIRAFFE = Image(b'\t\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\t\t\x00\x00\t\x00\t\x00')
Image.SKULL = Image(b'\x00\t\t\t\x00\t\x00\t\x00\t\t\t\t\t\t\x00\t\t\t\x00\x00\t\t\t\x00')
Image.UMBRELLA = Image(b'\x00\t\t\t\x00\t\t\t\t\t\x00\x00\t\x00\x00\t\x00\t\x00\x00\x00\t\t\x00\x00')
Image.SNAKE = Image(b'\t\t\x00\x00\x00\t\t\x00\t\t\x00\t\x00\t\x00\x00\t\t\t\x00\x00\x00\x00\x00\x00')
Image.SCISSORS = Image(b'\t\t\x00\x00\t\t\t\x00\t\x00\x00\x00\t\x00\x00\t\t\x00\t\x00\t\t\x00\x00\t')

# Font data derived from: https://github.com/stef/pitchfork-5x5/blob/master/pitchfork5x5.h
# License: GPLv3
_FONT = {
    ' ': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', #  
    '!': b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00', # !
    '"': b'\x00\t\x00\t\x00\x00\t\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', # "
    '#': b'\x00\t\x00\t\x00\t\t\t\t\t\x00\t\x00\t\x00\t\t\t\t\t\x00\t\x00\t\x00', # #
    '$': b'\x00\t\t\t\x00\t\x00\t\x00\x00\x00\t\t\t\x00\x00\x00\t\x00\t\t\t\t\t\x00', # $
    '%': b'\t\t\x00\x00\t\t\t\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\t\t\t\x00\x00\t\t', # %
    '&': b'\t\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\t\t\x00\x00\t\x00\x00\t\t\x00\t', # &
    "'": b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', # '
    '(': b'\x00\x00\t\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00\x00', # (
    ')': b'\x00\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\t\x00\x00', # )
    '*': b'\x00\t\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', # *
    '+': b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\t\t\t\t\t\x00\x00\t\x00\x00\x00\x00\t\x00\x00', # +
    ',': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00', # ,
    '-': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\t\t\t\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', # -
    '.': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\t\x00\x00\x00\t\t\x00\x00', # .
    '/': b'\x00\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\x00', # /
    '0': b'\x00\t\t\t\x00\t\x00\x00\x00\t\t\x00\t\x00\t\t\x00\x00\x00\t\x00\t\t\t\x00', # 0
    '1': b'\x00\x00\t\x00\x00\x00\t\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\t\t\t\x00', # 1
    '2': b'\x00\t\t\t\t\x00\x00\x00\x00\t\x00\t\t\t\t\x00\t\x00\x00\x00\x00\t\t\t\t', # 2
    '3': b'\x00\t\t\t\x00\x00\x00\x00\x00\t\x00\x00\t\t\t\x00\x00\x00\x00\t\x00\t\t\t\x00', # 3
    '4': b'\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\t\t\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t', # 4
    '5': b'\x00\t\t\t\t\x00\t\x00\x00\x00\x00\t\t\t\x00\x00\x00\x00\x00\t\x00\t\t\t\x00', # 5
    '6': b'\x00\t\t\t\t\x00\t\x00\x00\x00\x00\t\t\t\t\x00\t\x00\x00\t\x00\t\t\t\t', # 6
    '7': b'\x00\t\t\t\t\x00\t\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00', # 7
    '8': b'\x00\x00\t\t\x00\x00\t\x00\x00\t\x00\x00\t\t\x00\x00\t\x00\x00\t\x00\x00\t\t\x00', # 8
    '9': b'\x00\x00\t\t\x00\x00\t\x00\x00\t\x00\x00\t\t\t\x00\x00\x00\x00\t\x00\x00\t\t\x00', # 9
    ':': b'\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00', # :
    ';': b'\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\t\t\x00\x00\x00\x00\t\x00\x00', # ;
    '<': b'\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00', # <
    '=': b'\x00\x00\x00\x00\x00\x00\t\t\t\t\x00\x00\x00\x00\x00\x00\t\t\t\t\x00\x00\x00\x00\x00', # =
    '>': b'\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00', # >
    '?': b'\x00\t\t\t\x00\x00\x00\x00\x00\t\x00\x00\t\t\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00', # ?
    '@': b'\x00\t\t\t\x00\t\x00\x00\x00\t\t\x00\t\t\t\t\x00\x00\x00\x00\x00\t\t\x00\x00', # @
    'A': b'\x00\t\t\t\t\x00\t\x00\x00\t\x00\t\t\t\t\x00\t\x00\x00\t\x00\t\x00\x00\t', # A
    'B': b'\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\t\t\t\x00\t\x00\x00\t\x00\t\t\t\x00', # B
    'C': b'\x00\x00\t\t\x00\x00\t\x00\x00\t\x00\t\x00\x00\x00\x00\t\x00\x00\t\x00\x00\t\t\x00', # C
    'D': b'\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\t\t\x00', # D
    'E': b'\x00\t\t\t\t\x00\t\x00\x00\x00\x00\t\t\t\x00\x00\t\x00\x00\x00\x00\t\t\t\t', # E
    'F': b'\x00\t\t\t\t\x00\t\x00\x00\x00\x00\t\t\t\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00', # F
    'G': b'\x00\x00\t\t\t\x00\t\x00\x00\x00\x00\t\x00\t\t\x00\t\x00\x00\t\x00\x00\t\t\t', # G
    'H': b'\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\t\t\t\x00\t\x00\x00\t\x00\t\x00\x00\t', # H
    'I': b'\x00\t\t\t\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\t\t\t\x00', # I
    'J': b'\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\t\x00\x00\t\x00\t\t\t\t', # J
    'K': b'\x00\t\x00\x00\t\x00\t\x00\t\x00\x00\t\t\x00\x00\x00\t\x00\t\x00\x00\t\x00\x00\t', # K
    'L': b'\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\t\t\t', # L
    'M': b'\t\x00\x00\x00\t\t\t\x00\t\t\t\x00\t\x00\t\t\x00\t\x00\t\t\x00\x00\x00\t', # M
    'N': b'\x00\t\x00\x00\t\x00\t\t\x00\t\x00\t\t\t\t\x00\t\x00\t\t\x00\t\x00\x00\t', # N
    'O': b'\x00\x00\t\t\x00\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\x00\t\t\x00', # O
    'P': b'\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\t\t\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00', # P
    'Q': b'\x00\x00\t\t\x00\x00\t\x00\x00\t\x00\t\t\x00\t\x00\t\x00\t\t\x00\x00\t\t\t', # Q
    'R': b'\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\t\t\x00\x00\t\x00\t\x00\x00\t\x00\x00\t', # R
    'S': b'\x00\x00\t\t\t\x00\t\x00\x00\x00\x00\x00\t\t\x00\x00\x00\x00\x00\t\x00\t\t\t\x00', # S
    'T': b'\t\t\t\t\t\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00', # T
    'U': b'\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\x00\t\t\x00', # U
    'V': b'\t\x00\x00\x00\t\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\t\x00\t\x00\x00\x00\t\x00\x00', # V
    'W': b'\t\x00\x00\x00\t\t\x00\x00\x00\t\t\x00\t\x00\t\t\x00\t\x00\t\x00\t\x00\t\x00\t', # W
    'X': b'\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t', # X
    'Y': b'\t\x00\x00\x00\t\x00\t\x00\t\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00', # Y
    'Z': b'\x00\t\t\t\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\x00\t\t\t\t', # Z
    '[': b'\x00\t\t\t\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\t\t\x00', # [
    '\\': b'\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t', # \
    ']': b'\x00\t\t\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\t\t\t\x00', # ]
    '^': b'\x00\x00\t\x00\x00\x00\t\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', # ^
    '_': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\t\t\t\t', # _
    '`': b'\x00\t\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', # `
    'a': b'\x00\x00\x00\x00\x00\x00\x00\t\t\x00\x00\x00\x00\x00\t\x00\t\t\t\t\x00\x00\t\t\t', # a
    'b': b'\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\t\t\x00', # b
    'c': b'\x00\x00\x00\x00\x00\x00\x00\t\t\t\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\t\t\t', # c
    'd': b'\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\t\t\t\x00\t\x00\x00\t\x00\x00\t\t\t', # d
    'e': b'\x00\x00\x00\x00\x00\x00\x00\t\t\x00\x00\t\t\t\t\x00\t\x00\x00\x00\x00\x00\t\t\t', # e
    'f': b'\x00\x00\x00\t\t\x00\x00\t\x00\x00\x00\t\t\t\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00', # f
    'g': b'\x00\x00\x00\x00\x00\x00\x00\t\t\x00\x00\t\x00\x00\x00\x00\t\x00\t\t\x00\x00\t\t\x00', # g
    'h': b'\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\x00\x00\t', # h
    'i': b'\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\t\t\t\x00\x00\x00\x00\t\x00\x00\t\t\t\t', # i
    'j': b'\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\t\x00\x00\t\x00\t\t\t\t', # j
    'k': b'\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\t\x00\x00\t\t\t\x00\x00\t\x00\x00\t', # k
    'l': b'\x00\t\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\t\t\t\x00', # l
    'm': b'\x00\x00\x00\x00\x00\t\t\t\t\x00\t\x00\t\x00\t\t\x00\t\x00\t\t\x00\t\x00\t', # m
    'n': b'\x00\x00\x00\x00\x00\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\x00\x00\t', # n
    'o': b'\x00\x00\x00\x00\x00\x00\x00\t\t\x00\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\x00\t\t\x00', # o
    'p': b'\x00\x00\x00\x00\x00\x00\t\t\t\x00\x00\t\x00\x00\t\x00\t\t\t\x00\x00\t\x00\x00\x00', # p
    'q': b'\x00\x00\x00\x00\x00\x00\x00\t\t\t\x00\t\x00\x00\t\x00\x00\t\t\t\x00\x00\x00\x00\t', # q
    'r': b'\x00\x00\x00\x00\x00\x00\x00\t\t\t\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00', # r
    's': b'\x00\x00\x00\x00\x00\x00\x00\t\t\t\x00\t\t\x00\x00\x00\x00\t\t\t\x00\t\t\t\x00', # s
    't': b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\t\t\t\x00\x00\x00\t\x00\x00\x00\x00\x00\t\t', # t
    'u': b'\x00\x00\x00\x00\x00\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\x00\t\t\t', # u
    'v': b'\x00\x00\x00\x00\x00\x00\t\x00\x00\t\x00\t\x00\x00\t\x00\x00\t\t\x00\x00\x00\t\t\x00', # v
    'w': b'\x00\x00\x00\x00\x00\t\x00\t\x00\t\t\x00\t\x00\t\t\x00\t\x00\t\x00\t\x00\t\x00', # w
    'x': b'\x00\x00\x00\x00\x00\x00\t\x00\x00\t\x00\x00\t\t\x00\x00\x00\t\t\x00\x00\t\x00\x00\t', # x
    'y': b'\x00\x00\x00\x00\x00\x00\t\x00\x00\t\x00\x00\t\t\x00\x00\x00\x00\t\x00\x00\x00\t\t\x00', # y
    'z': b'\x00\x00\x00\x00\x00\x00\t\t\t\t\x00\x00\x00\t\x00\x00\x00\t\x00\x00\x00\t\t\t\t', # z
    '{': b'\x00\x00\t\t\t\x00\x00\t\x00\x00\x00\t\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\t\t', # {
    '|': b'\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\x00\x00', # |
    '}': b'\x00\t\t\t\x00\x00\x00\x00\t\x00\x00\x00\x00\t\t\x00\x00\x00\t\x00\x00\t\t\t\x00', # }
    '~': b'\x00\t\t\x00\x00\x00\x00\t\t\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', # ~
}



# --- Display Class ---

class Display:
    """
    Controls the physical 5x5 LED Matrix on the BPI-Bit-S2.

    Implements core methods from the Micro:bit display API:
    - ``show()``: Render an Image or sequence of Images.
    - ``scroll()``: Display scrolling text (currently logs to console).
    - ``clear()``: Turn off all LEDs.
    - ``set_pixel()``/``get_pixel()``: Manipulate individual pixels (0-9).

    Brightness values (0-9) are mapped to Red color intensity (0-255).
    """

    def __init__(self):
        pass

    def show(self, image, delay=0, wait=True, loop=False, clear=False):
        # image can be Image, string, or valid iterable of Images
        if isinstance(image, str):
             # If string, show each character one by one (not scroll)
             # Map chars to Images
             images = []
             for char in image:
                 if char in _FONT:
                     images.append(Image(_FONT[char]))
                 else:
                     images.append(Image(_FONT['?'])) # default
             
             # Treat as animation
             # Use default delay if 0 provided? Microbit default is 400ms for show(str)
             if delay == 0: 
                 delay = 400
                 
             self._play_animation(images, delay, wait, loop, clear)
             return

        if isinstance(image, Image):
            self._render(image)
            if delay > 0:
                time.sleep(delay / 1000.0)
            if clear:
                self.clear()
        elif hasattr(image, '__iter__'):
             # Animation (list of Images)
             self._play_animation(image, delay, wait, loop, clear)

    def _play_animation(self, images, delay, wait, loop, clear):
        while True:
            for img in images:
                if isinstance(img, Image):
                    self._render(img)
                elif isinstance(img, str) and img in _FONT:
                    # mixed list?
                    self._render(Image(_FONT[img]))
                
                if delay > 0:
                        time.sleep(delay / 1000.0)
            if not loop:
                break
        if clear:
            self.clear()

    def scroll(self, text, delay=150, wait=True, loop=False, monospace=False):
        """
        Scrolls text across the display.
        """
        if not text:
            return

        # Convert text to a list of frames (5x5 Images) shifted appropriately?
        # No, better to generate a long strip of columns and slide a view over it.
        # But we can't easily hold a generic infinite strip.
        # We process character by character.
        
        # Standard microbit behavior:
        # Start: screen blank.
        # First char scrolls in from rigt.
        # Spacing of 1 blank column between chars.
        # Finishes when last char scrolls off to the left.
        
        # We need a buffer that holds the current visible 5x5
        # and shifts in new columns.
        
        # Column buffer: list of 5 (pixel values 0-9)
        # We can implement a generator that yields the next column to append.
        
        def column_generator(text_str):
            for char in text_str:
                # Get char image data (25 bytes)
                img_bytes = _FONT.get(char, _FONT['?'])
                
                # Yield 5 columns of this char
                for col in range(5):
                    # Extract column 'col' from the 5x5 row-major bytes
                    # indices: col, col+5, col+10, col+15, col+20
                    yield [img_bytes[col + r*5] for r in range(5)]
                
                # Yield 1 blank spacing column
                yield [0, 0, 0, 0, 0]
            
            # Pad with 5 blank columns to scroll the last char off screen
            for _ in range(5):
                yield [0, 0, 0, 0, 0]

        # Initial state: blank screen
        
        def run_scroll():
            # We represent the screen as 5 columns. Each column is a list of 5 pixels.
            # Reset screen_cols for each run to ensure clean state
            screen_cols = [[0]*5 for _ in range(5)]
            
            # Simple generator consumption
            col_gen = column_generator(text)

            # Pre-fill? No, start blank and scroll in.
            
            for next_col in col_gen:
                # Shift screen cols left
                screen_cols.pop(0)
                screen_cols.append(next_col)
                
                # Render screen_cols to Image buffer format (row-major)
                # screen_cols[x][y] is pixel at column x, row y
                # buffer index = y * 5 + x
                flat_buf = bytearray(25)
                for x in range(5):
                   col_data = screen_cols[x]
                   for y in range(5):
                        flat_buf[y*5 + x] = col_data[y]
                
                img = Image(flat_buf)
                self.show(img) 
                time.sleep(delay / 1000.0)
            
            # After scrolling, clear
            self.clear()

        # TODO: Implement wait=False using asyncio or background task?
        # For now, simplistic blocking implementation.
        run_scroll()
        while loop:
            run_scroll()

    def clear(self):
        _pixels.fill((0, 0, 0))
        _pixels.show()

    def set_pixel(self, x, y, value):
        if 0 <= x < 5 and 0 <= y < 5 and 0 <= value <= 9:
             _pixels[_column_row_2_index(x, y)] = (int((value/9.0)*255 * _BRIGHTNESS), 0, 0)
             _pixels.show()

    def get_pixel(self, x, y):
         if 0 <= x < 5 and 0 <= y < 5:
             r, g, b = _pixels[_column_row_2_index(x, y)]
             return int((r / (255.0 * _BRIGHTNESS)) * 9)
         return 0

    def on(self):
        pass # Turn on display?

    def off(self):
        self.clear()

    def is_on(self):
        return True

    def read_light_level(self):
        return 0 # Stub

    def _render(self, image):
        for y in range(5):
            for x in range(5):
                val = image.get_pixel(x, y)
                # Convert 0-9 to color
                # Using Red for microbit feel
                intensity = int((val / 9.0) * 255)
                idx = _column_row_2_index(x, y)
                if idx != -1:
                     _pixels[idx] = (intensity, 0, 0) # Red
        _pixels.show()

display = Display()


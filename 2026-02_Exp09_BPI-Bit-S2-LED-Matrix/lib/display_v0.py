import board
import neopixel
import time
import asyncio

# --- Hardware Configuration for BPI-Bit-S2 ---
_NUM_PIXELS = 25
_PIXEL_PIN = board.NEOPIXEL
_BRIGHTNESS = 0.1 # Default global brightness

# Internal NeoPixel object
_pixels = neopixel.NeoPixel(
    _PIXEL_PIN,
    _NUM_PIXELS,
    brightness=_BRIGHTNESS,
    auto_write=False,
)

# Color constants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARKOLIVEGREEN = (85, 107, 47)
DARKRED = (128, 0, 0)
DARKSLATEBLUE = (72, 61, 139)
GREEN = (0, 128, 0)
YELLOWGREEN = (154, 205, 50)
DARKBLUE = (0, 0, 139)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
LIME = (0, 255, 0)
SPRINGGREEN = (0, 255, 127)
BLUE = (0, 0, 255)
AQUA = (0, 255, 255)
CORAL = (255, 127, 80)
FUCHSIA = (255, 0, 255)
DEEPPINK = (255, 20, 147)
PLUM = (221, 160, 221)
off = (0, 0, 0)

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

class Display:
    """
    Controls the physical 5x5 LED Matrix on the BPI-Bit-S2.
    Supports MakeCode-style API with #/. syntax and color support.
    """

    def __init__(self):
        self.clear()

    def _render_pattern(self, leds_str, color=WHITE):
        """
        Core logic for parsing and displaying a 5x5 pattern string.
        '#' = ON (in specified color), '.' = OFF.
        This method only updates the NeoPixel buffer and calls show().
        No timing or async logic here.
        """
        # Parse the input string into rows
        # Filter out empty lines often caused by the first/last newline in multiline strings
        lines = leds_str.strip().split('\n')  # removes leading and trailing characters from a string, returning a new string
        processed_lines = 0
        y = 0  # row index pending to be processed
        number_lines = len(lines)
        while processed_lines < number_lines:
            row = lines[processed_lines].strip()  # removes leading and trailing characters from a string, returning a new string
            if len(row) == 0:  # Skip empty lines (e.g., from extra newlines in the input)
                processed_lines += 1
                continue
            #
            # Process this row
            row = row.replace(" ", "")  # Remove spaces to handle "# # . # #" format
            x = 0  # column index to be processed in this row
            cap = min(5, len(row))  # Only process up to 5 columns, ignore extra
            while x < cap:
                if row[x] == '#':
                    pixel_color = color
                else:
                    pixel_color = off
                _pixels[_column_row_2_index(x, y)] = pixel_color  # Directly update buffer; without showing LEDs' new state yet (efficiency)
                x += 1
            # In case this row is incomplete (e.g., only 3 columns defined), treat missing columns as off
            while x < 5:
                _pixels[_column_row_2_index(x, y)] = off
                x += 1
            y += 1
            processed_lines += 1
            if y >= 5: # We have processed 5 rows, which is the max for our display. Ignore any extra rows in the input.
                break
        #
        # In case we are still missing rows (e.g., only 3 rows defined), treat missing rows as off
        while y < 5:
            x = 0
            while x < 5:
                _pixels[_column_row_2_index(x, y)] = off
                x += 1
            y += 1
        # Single hardware update after all pixels set
        _pixels.show()

    def show_leds(self, leds_str, color=WHITE, delay=400, wait=True):
        """
        Display a 5x5 pattern defined by a multiline string.
        '#' = ON (in specified color), '.' = OFF.
        If wait=True, blocks until done. If wait=False, schedules as background task.
        Handles both synchronous and asynchronous contexts.
        Args:
            leds_str: Multiline string pattern (5x5 grid, '#' and '.')
            color: RGB tuple for ON pixels (default WHITE)
            delay: Milliseconds to show the pattern (default 400)
            wait: If True, block until done; if False, return immediately (background)
        Returns:
            In async context and wait=True, returns coroutine to be awaited.
            Otherwise, returns None.
        """
        import asyncio
        async def _show_leds_async():
            self._render_pattern(leds_str, color)
            if delay > 0:
                await asyncio.sleep(delay / 1000.0)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                if wait:
                    # In async context, must be awaited by caller
                    # Optionally, could raise or warn here
                    return _show_leds_async()
                else:
                    asyncio.create_task(_show_leds_async())
            else:
                if wait:
                    loop.run_until_complete(_show_leds_async())
                else:
                    asyncio.create_task(_show_leds_async())
        except RuntimeError:
            # No event loop, fallback to blocking
            self._render_pattern(leds_str, color)
            if delay > 0 and wait:
                import time
                time.sleep(delay / 1000.0)

    def clear(self):
        _pixels.fill(off)
        _pixels.show()

    def set_pixel(self, x, y, color):
        """
        Set a single pixel to a specific RGB color.
        """
        if 0 <= x < 5 and 0 <= y < 5:
             _pixels[_column_row_2_index(x, y)] = color
             _pixels.show()

    def get_pixel(self, x, y):
        """
        Get the current color of a single pixel as an RGB tuple. Returns (0, 0, 0) if out of bounds or pixel is off.
        Note: This reads from the internal buffer, which may not reflect the actual hardware state if show() has not been called after changes.
        """         
        # Returns color tuple (r,g,b)
        if 0 <= x < 5 and 0 <= y < 5:
            return _pixels[_column_row_2_index(x, y)]
        return off

    async def show(self, image, delay=400, *, wait=True, loop=False, clear=False, color=WHITE):
        """
        TODO: INCOMPLETE - early draft

        Show a string, number, or sequence of patterns/images on the display.
        - If image is a string/int/float: display as scrolling text (one char at a time)
        - If image is an iterable: display each pattern in sequence
        - If image is a 5x5 pattern string: display it directly
        Args:
            image: string, character, number, or iterable sequence of those (which we call frames)
            delay: milliseconds each frame is shown before next (default 400ms)
            wait: if True, block until done; else run in background
            loop: if True, repeat forever
            clear: if True, clear display after
            color: RGB tuple (default WHITE)
        """
        async def _show_sequence(seq):
            while True:
                for frame in seq:
                    if isinstance(frame, str):
                        self.show_leds(frame, color=color, delay=0, wait=False)
                    else:
                        # Assume frame is a 5x5 pattern (list of lists or similar)
                        # Not implemented: add support if needed
                        pass
                    await asyncio.sleep(delay / 1000)
                if not loop:
                    break
            if clear:
                self.clear()

        # Convert input to sequence
        if isinstance(image, (str, int, float)):
            # Convert to string, scroll one char at a time
            text = str(image)
            seq = []
            for c in text:

                    # Use a simple 5x5 font mapping or just show the char as a pattern
                # For now, treat each char as a pattern string (user must provide patterns for letters)
                seq.append(c)
            coro = _show_sequence(seq)
        elif hasattr(image, '__iter__'):
            # Sequence of patterns
            coro = _show_sequence(image)
        else:
            # Single pattern
            coro = _show_sequence([image])

        if wait:
            await coro
        else:
            asyncio.create_task(coro)

def float_to_str(f):
    '''
    converst float to string in positional format without scientific notation and with full precision
    '''
    # from https://stackoverflow.com/questions/38847690/convert-float-to-string-in-positional-format-without-scientific-notation-and-fa
    # by user 'Karin'
    float_string = repr(f)
    # if str(old).__contains__('e-'): # alternative
    if 'e' in float_string:  # detect scientific notation
        digits, exp = float_string.split('e')
        digits = digits.replace('.', '').replace('-', '')
        exp = int(exp)
        zero_padding = '0' * (abs(int(exp)) - 1)  # minus 1 for decimal point in the sci notation
        sign = '-' if f < 0 else ''
        if exp > 0:
            float_string = "{}{}{}.0".format(sign, digits, zero_padding)
        else:
            float_string = "{}0.{}{}".format(sign, zero_padding, digits)
    return float_string


# Create singleton instance
display = Display()

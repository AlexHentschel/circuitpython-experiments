"""
MakeCode-style display library for an 8x8 WS2812b NeoPixel matrix.

Hardware: YD-RP2040, WS2812b data on GP0 via 3.3V-to-5V level shifter.
Wiring:   Progressive left-to-right, bottom-up (strip index 0 = bottom-left).

Two-tier API:
  Tier 1 (sync):  render_pattern, render_icon, render_arrow, clear_screen,
                   set_pixel, fill, set_rotation, set_brightness, get_pixel.
  Tier 2 (async): show_leds, show_icon, show_arrow, show_string, show_number,
                   pause.  Require ``await`` from asyncio code.

Cooperative multitasking via asyncio + cancellation-token counter (_seq).
Display-mutating methods call _acquire() to invalidate any ongoing animation.
Async methods check _cancelled(token) after each await to detect preemption.

Monochrome bitmaps (icons, arrows, font glyphs, mono Images) use column-major
bytes internally: one byte per column, bit N = row N (bit 0 = top). This
enables efficient horizontal scrolling by iterating contiguous column bytes.

Image class owns its display color(s) and supports async show/scroll.
Image methods reference module globals (display, _LUT, _pixels) directly --
tight coupling acceptable for a single-display MCU library.
"""

import asyncio
import board
import neopixel
from rainbowio import colorwheel  # noqa: F401 -- re-export for user convenience

from adafruit_bitmap_font import bitmap_font
from display_icons import ICONS, ARROWS

# ---------------------------------------------------------------------------
# Hardware configuration
# ---------------------------------------------------------------------------
WIDTH = 8
HEIGHT = 8
NUM_PIXELS = WIDTH * HEIGHT
PIXEL_PIN = board.GP0
BRIGHTNESS = 0.05

_pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False
)

# ---------------------------------------------------------------------------
# Color constants -- Adafruit LED Animation standard + LED-tuned extras
# ---------------------------------------------------------------------------
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 40, 0)
GREEN = (0, 255, 0)
TEAL = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 20)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 222, 30)
PINK = (242, 90, 255)
AQUA = (50, 255, 255)
JADE = (0, 255, 40)
AMBER = (255, 100, 0)
OLD_LACE = (253, 245, 230)
RAINBOW = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)

GRAY = (160, 160, 160)
DARKSLATEBLUE = (80, 0, 180)
YELLOWGREEN = (120, 230, 0)
DEEPPINK = (255, 0, 160)

OFF = BLACK


def color(r, g, b):
    """Convenience constructor mirroring Adafruit NeoMatrix's matrix.Color()."""
    return (r, g, b)


# ---------------------------------------------------------------------------
# Coordinate LUT -- pre-computed (x, y) -> strip index
# ---------------------------------------------------------------------------
_LUT = bytearray(WIDTH * HEIGHT)


def _build_lut(rotation=0):
    """Pre-compute (x, y) -> strip index for configured rotation.

    Two-stage coordinate transform:
      1. Rotation: logical (x, y) -> physical (px, py).
         Clockwise rotation in degrees.
      2. Bottom-up progressive wiring: physical (px, py) -> strip index.
         All rows run left-to-right. Bottom row (py=H-1) = strip indices 0-7.
         idx = (H-1-py)*W + px.

    Logical coordinates (x = column, y = row):

             x=0   x=1   x=2   x=3   x=4   x=5   x=6   x=7
    y=0    (0,0) (1,0) (2,0) (3,0) (4,0) (5,0) (6,0) (7,0)
    y=1    (0,1) (1,1) (2,1) (3,1) (4,1) (5,1) (6,1) (7,1)
    ...
    y=7    (0,7) (1,7) (2,7) (3,7) (4,7) (5,7) (6,7) (7,7)

    Physical strip indices (progressive bottom-up L-to-R, rotation=0):

             x=0   x=1   x=2   x=3   x=4   x=5   x=6   x=7
    y=0    (56)  (57)  (58)  (59)  (60)  (61)  (62)  (63)  -> top row
    y=1    (48)  (49)  (50)  (51)  (52)  (53)  (54)  (55)
    y=2    (40)  (41)  (42)  (43)  (44)  (45)  (46)  (47)
    y=3    (32)  (33)  (34)  (35)  (36)  (37)  (38)  (39)
    y=4    (24)  (25)  (26)  (27)  (28)  (29)  (30)  (31)
    y=5    (16)  (17)  (18)  (19)  (20)  (21)  (22)  (23)
    y=6    ( 8)  ( 9)  (10)  (11)  (12)  (13)  (14)  (15)
    y=7    ( 0)  ( 1)  ( 2)  ( 3)  ( 4)  ( 5)  ( 6)  ( 7)  -> bottom row (strip start)
    """
    for x in range(WIDTH):
        for y in range(HEIGHT):
            # Stage 1: rotate logical -> physical
            if rotation == 90:
                px, py = (WIDTH - 1) - y, x
            elif rotation == 180:
                px, py = (WIDTH - 1) - x, (HEIGHT - 1) - y
            elif rotation == 270:
                px, py = y, (HEIGHT - 1) - x
            else:
                px, py = x, y
            # Stage 2: bottom-up progressive wiring -> strip index
            # All rows L-to-R, bottom row = indices 0..W-1
            _LUT[x * HEIGHT + y] = ((HEIGHT - 1) - py) * WIDTH + px


_build_lut(0)


def _xy_to_index(x, y):
    """Map logical (x, y) to NeoPixel strip index via pre-computed LUT."""
    return _LUT[x * HEIGHT + y]


# ---------------------------------------------------------------------------
# Monochrome column-major render helper
# ---------------------------------------------------------------------------
def _render_colmajor(data, offset, color_on):
    """Render WIDTH columns of column-major bitmap data to _pixels.

    data[offset+x] is one column byte; bit y = row y (0=top).
    Uses _LUT for coordinate mapping. Writes all 64 pixels then shows.
    """
    for x in range(WIDTH):
        col_byte = data[offset + x]
        for y in range(HEIGHT):
            _pixels[_LUT[x * HEIGHT + y]] = color_on if (col_byte >> y) & 1 else OFF
    _pixels.show()


# ---------------------------------------------------------------------------
# Font loading -- PCF font via adafruit_bitmap_font
# ---------------------------------------------------------------------------
_font = bitmap_font.load_font("/lib/font_free_mono_8/font.pcf")
_font.load_glyphs(range(32, 127))


def _glyph_columns(ch):
    """Convert a font glyph to column-major bytes for the 8-row LED matrix.

    Returns one byte per column spanning the glyph's advance width.
    Bit N of each byte = row N (0 = top).

    Font metric terms (from fontio.Glyph / PCF):
      ascent:  rows from baseline to top of tallest glyph (= display row 0).
      dy:      rows from baseline to bottom edge of this glyph's bitmap.
      dx:      columns from pen position to left edge of this glyph's bitmap.
      shift_x: advance width (columns the pen moves right after this glyph).
      width/height: pixel dimensions of the glyph's actual bitmap.

    Coordinate mapping from glyph bitmap (cx, cy) to display:
      display_row = ascent - height - dy + cy
        (glyph top edge at font-y = dy + height; display row 0 = ascent)
      display_col = cx + dx
        (dx = horizontal bearing from pen to bitmap left edge)
    """
    glyph = _font.get_glyph(ord(ch))
    if glyph is None:
        return bytes(WIDTH)
    bm = glyph.bitmap
    ascent = _font.ascent
    cols = bytearray(glyph.shift_x)
    # top row of glyph bitmap in display coords (loop-invariant)
    row_origin = ascent - glyph.height - glyph.dy
    for cx in range(glyph.width):
        col_byte = 0
        for cy in range(glyph.height):
            display_row = row_origin + cy
            if 0 <= display_row < HEIGHT and bm[cx + cy * glyph.width]:
                col_byte |= 1 << display_row
        # dx = horizontal bearing: pen position -> bitmap left edge
        bx = cx + glyph.dx
        if 0 <= bx < len(cols):
            cols[bx] = col_byte
    return bytes(cols)


# ---------------------------------------------------------------------------
# IconNames / ArrowNames enums
# ---------------------------------------------------------------------------
class IconNames:
    HEART = 0
    SMALL_HEART = 1
    YES = 2
    NO = 3
    HAPPY = 4
    SAD = 5
    CONFUSED = 6
    ANGRY = 7
    ASLEEP = 8
    SURPRISED = 9
    SILLY = 10
    FABULOUS = 11
    MEH = 12
    TSHIRT = 13
    ROLLERSKATE = 14
    DUCK = 15
    HOUSE = 16
    TORTOISE = 17
    BUTTERFLY = 18
    STICK_FIGURE = 19
    GHOST = 20
    SWORD = 21
    GIRAFFE = 22
    SKULL = 23
    UMBRELLA = 24
    SNAKE = 25
    RABBIT = 26
    COW = 27
    QUARTER_NOTE = 28
    EIGHTH_NOTE = 29
    PITCHFORK = 30
    TARGET = 31
    TRIANGLE = 32
    LEFT_TRIANGLE = 33
    CHESSBOARD = 34
    DIAMOND = 35
    SMALL_DIAMOND = 36
    SQUARE = 37
    SMALL_SQUARE = 38
    SCISSORS = 39


class ArrowNames:
    NORTH = 0
    NORTH_EAST = 1
    EAST = 2
    SOUTH_EAST = 3
    SOUTH = 4
    SOUTH_WEST = 5
    WEST = 6
    NORTH_WEST = 7


# ---------------------------------------------------------------------------
# Image class
# ---------------------------------------------------------------------------
class Image:
    """Bitmap image for the 8-row LED matrix.

    Monochrome images store column-major bytes + a single _color tuple.
    Multi-color images store a flat tuple of per-pixel RGB tuples.

    Image async methods reference module globals (display, _LUT, _pixels)
    directly -- coupling documented in the Phase 2 plan (section 8.3).
    """
    __slots__ = ('_data', '_width', '_multi', '_color')

    def __init__(self, data, width, multi, col):
        self._data = data
        self._width = width
        self._multi = multi
        self._color = col

    @staticmethod
    def from_pattern(pattern_str, color_palette=None):
        """Parse a pattern string into an Image.

        color_palette: RGB tuple (mono) or dict {char: RGB} (multi-color).
        Mono images use column-major bytes; multi-color uses per-pixel tuple.

        Column-major conversion happens here (not at render time) because
        Image data persists for repeated show_image / scroll_image calls.
        """
        if color_palette is None:
            color_palette = WHITE
        is_dict = isinstance(color_palette, dict)
        lines = pattern_str.strip().split('\n')
        rows = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                rows.append(stripped.replace(" ", ""))
        height = min(len(rows), HEIGHT)
        img_width = max((len(r) for r in rows), default=WIDTH)

        if is_dict:
            # Multi-color: flat tuple of RGB, index = x * HEIGHT + y
            pixels = []
            for x in range(img_width):
                for y in range(HEIGHT):
                    if y < height and x < len(rows[y]):
                        ch = rows[y][x]
                        pixels.append(color_palette.get(ch, OFF))
                    else:
                        pixels.append(OFF)
            return Image(tuple(pixels), img_width, True, None)
        else:
            # Mono: column-major bytes, one byte per column
            cols = bytearray(img_width)
            for x in range(img_width):
                col_byte = 0
                for y in range(height):
                    if x < len(rows[y]) and rows[y][x] == '#':
                        col_byte |= 1 << y
                cols[x] = col_byte
            return Image(bytes(cols), img_width, False, color_palette)

    @property
    def width(self):
        return self._width

    def recolor(self, new_color):
        """Change a mono Image's display color in place. No-op for multi-color."""
        if not self._multi:
            self._color = new_color

    async def show_image(self, offset=0, interval=0):
        """Render WIDTH columns starting at offset. Holds for interval ms."""
        display._acquire()
        if self._multi:
            # Multi-color: per-pixel lookup
            for x in range(WIDTH):
                src_x = offset + x
                for y in range(HEIGHT):
                    if 0 <= src_x < self._width:
                        _pixels[_LUT[x * HEIGHT + y]] = self._data[src_x * HEIGHT + y]
                    else:
                        _pixels[_LUT[x * HEIGHT + y]] = OFF
            _pixels.show()
        else:
            # Mono: column-major bytes
            for x in range(WIDTH):
                src_x = offset + x
                if 0 <= src_x < self._width:
                    col_byte = self._data[src_x]
                else:
                    col_byte = 0
                for y in range(HEIGHT):
                    _pixels[_LUT[x * HEIGHT + y]] = self._color if (col_byte >> y) & 1 else OFF
            _pixels.show()
        if interval > 0:
            await asyncio.sleep(interval / 1000)

    async def scroll_image(self, offset=1, interval=200):
        """Scroll through the image, advancing offset columns per frame.

        Uses display._seq for cancellation -- a newer display operation
        will cause this coroutine to return early.
        """
        token = display._acquire()
        max_start = self._width - WIDTH
        if max_start < 0:
            max_start = 0
        pos = 0
        while pos <= max_start:
            if display._cancelled(token):
                return
            if self._multi:
                for x in range(WIDTH):
                    src_x = pos + x
                    for y in range(HEIGHT):
                        if src_x < self._width:
                            _pixels[_LUT[x * HEIGHT + y]] = self._data[src_x * HEIGHT + y]
                        else:
                            _pixels[_LUT[x * HEIGHT + y]] = OFF
                _pixels.show()
            else:
                for x in range(WIDTH):
                    src_x = pos + x
                    col_byte = self._data[src_x] if src_x < self._width else 0
                    for y in range(HEIGHT):
                        _pixels[_LUT[x * HEIGHT + y]] = self._color if (col_byte >> y) & 1 else OFF
                _pixels.show()
            await asyncio.sleep(interval / 1000)
            if display._cancelled(token):
                return
            pos += offset


# Module-level factories
def create_image(pattern_str, color_palette=None):
    if color_palette is None:
        color_palette = WHITE
    return Image.from_pattern(pattern_str, color_palette)


def create_big_image(pattern_str, color_palette=None):
    if color_palette is None:
        color_palette = WHITE
    return Image.from_pattern(pattern_str, color_palette)


# ---------------------------------------------------------------------------
# Display class
# ---------------------------------------------------------------------------
class Display:
    """Controls an 8x8 WS2812b NeoPixel matrix.

    Singleton at module level (``display``). Manages the cancellation-token
    counter (_seq) for cooperative multitasking: every display-mutating method
    calls _acquire() to invalidate ongoing animations.
    """

    def __init__(self):
        self._seq = 0

    # -- Cancellation token --------------------------------------------------

    def _acquire(self):
        """Increment and return the cancellation token.

        Called by every display-mutating method. Any Tier 2 animation
        holding an older token will detect preemption via _cancelled().
        """
        self._seq += 1
        return self._seq

    def _cancelled(self, token):
        """True if a newer operation has superseded the given token."""
        return self._seq != token

    # -- Tier 1: Synchronous rendering primitives ----------------------------

    def render_pattern(self, pattern, color_palette=None):
        """Parse and render a pattern string directly to LEDs.

        Direct render via LUT -- no intermediate column-major buffer.
        Faster than create_image for one-shot display since it avoids
        building a persistent bitmap (one parse pass, immediate pixel writes).

        color_palette: RGB tuple for mono ('#'/'.' mode) or dict for palette.
        """
        if color_palette is None:
            color_palette = WHITE
        self._acquire()
        is_dict = isinstance(color_palette, dict)
        lines = pattern.strip().split('\n')
        y = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            row = stripped.replace(" ", "")
            cap = min(WIDTH, len(row))
            for x in range(cap):
                ch = row[x]
                if is_dict:
                    _pixels[_LUT[x * HEIGHT + y]] = color_palette.get(ch, OFF)
                else:
                    _pixels[_LUT[x * HEIGHT + y]] = color_palette if ch == '#' else OFF
            for x in range(cap, WIDTH):
                _pixels[_LUT[x * HEIGHT + y]] = OFF
            y += 1
            if y >= HEIGHT:
                break
        while y < HEIGHT:
            for x in range(WIDTH):
                _pixels[_LUT[x * HEIGHT + y]] = OFF
            y += 1
        _pixels.show()

    def render_icon(self, icon, color=None):
        """Render an icon bitmap (from ICONS) to the LEDs."""
        if color is None:
            color = WHITE
        self._acquire()
        _render_colmajor(ICONS, icon * WIDTH, color)

    def render_arrow(self, direction, color=None):
        """Render an arrow bitmap (from ARROWS) to the LEDs."""
        if color is None:
            color = WHITE
        self._acquire()
        _render_colmajor(ARROWS, direction * WIDTH, color)

    def clear_screen(self):
        """Turn off all pixels. Cancels any ongoing animation."""
        self._acquire()
        _pixels.fill(OFF)
        _pixels.show()

    def clear(self):
        """Alias for clear_screen()."""
        self.clear_screen()

    def set_pixel(self, x, y, color=None):
        """Set one pixel and update the display. Cancels ongoing animations."""
        if color is None:
            color = WHITE
        self._acquire()
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            _pixels[_LUT[x * HEIGHT + y]] = color
            _pixels.show()

    def fill(self, color=None):
        """Fill all pixels. Cancels ongoing animations."""
        if color is None:
            color = WHITE
        self._acquire()
        _pixels.fill(color)
        _pixels.show()

    def get_pixel(self, x, y):
        """Read the buffered pixel color at (x, y). Does not acquire."""
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            return _pixels[_LUT[x * HEIGHT + y]]
        return OFF

    @staticmethod
    def set_brightness(value):
        """Adjust global brightness (0.0-1.0). Does not cancel animations."""
        _pixels.brightness = value
        _pixels.show()

    @staticmethod
    def set_rotation(degrees):
        """Rebuild coordinate LUT for 0/90/180/270 rotation."""
        _build_lut(degrees)

    # -- Tier 2: Async MakeCode-compatible methods ---------------------------

    async def show_leds(self, pattern, color_palette=None, interval=0):
        """Render a pattern, then hold for interval ms (0 = return after render).

        color_palette: RGB tuple (mono '#'/'.' mode) or dict (palette).
        """
        if color_palette is None:
            color_palette = WHITE
        self.render_pattern(pattern, color_palette)
        if interval > 0:
            await asyncio.sleep(interval / 1000)

    async def show_icon(self, icon, color=None, interval=0):
        """Render icon, hold for interval ms."""
        if color is None:
            color = WHITE
        self.render_icon(icon, color)
        if interval > 0:
            await asyncio.sleep(interval / 1000)

    async def show_arrow(self, direction, color=None, interval=0):
        """Render arrow, hold for interval ms."""
        if color is None:
            color = WHITE
        self.render_arrow(direction, color)
        if interval > 0:
            await asyncio.sleep(interval / 1000)

    async def show_string(self, text, color=None, interval=150):
        """Scroll text across the display.

        Builds a column-major buffer from font glyphs, then slides an
        8-column window across it. interval = ms per column step.
        Single character: display directly, hold for interval * 5.
        """
        if color is None:
            color = WHITE
        token = self._acquire()
        text = str(text)
        if not text:
            return
        # Build scroll buffer from glyph columns
        buf = bytearray()
        for ch in text:
            buf.extend(_glyph_columns(ch))
        if len(buf) <= WIDTH:
            # Fits on screen: display centered, hold
            pad = (WIDTH - len(buf)) // 2
            padded = bytearray(WIDTH)
            for i in range(len(buf)):
                if pad + i < WIDTH:
                    padded[pad + i] = buf[i]
            _render_colmajor(padded, 0, color)
            if interval > 0:
                await asyncio.sleep(interval * 5 / 1000)
            return
        # Scroll: slide window across buffer
        # Pad with blank columns at start and end for scroll-in/out effect
        padding = bytearray(WIDTH)
        scroll_buf = padding + buf + padding
        max_offset = len(scroll_buf) - WIDTH
        for offset in range(max_offset + 1):
            if self._cancelled(token):
                return
            _render_colmajor(scroll_buf, offset, color)
            await asyncio.sleep(interval / 1000)
            if self._cancelled(token):
                return

    async def show_number(self, n, color=None, interval=150):
        """Display a number. Single digit: centered. Multi-digit: scroll."""
        if color is None:
            color = WHITE
        await self.show_string(str(n), color, interval)

    async def pause(self, ms):
        """Cancellable async sleep for ms milliseconds."""
        self._acquire()
        await asyncio.sleep(ms / 1000)

    @staticmethod
    def forever(callback):
        """Sync convenience: run callback in a while-True loop via asyncio.

        For simple scripts that don't need custom async setup.
        """
        async def _loop():
            while True:
                result = callback()
                if hasattr(result, '__await__') or hasattr(result, 'send'):
                    await result
                await asyncio.sleep(0)
        asyncio.run(_loop())


# Singleton -- ``from display import display``
display = Display()

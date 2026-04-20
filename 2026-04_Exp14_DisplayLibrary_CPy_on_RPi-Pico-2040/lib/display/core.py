"""
Runtime display engine for the 8x8 WS2812b NeoPixel matrix.

Owns the live NeoPixel buffer, the coordinate Look-Up Table [LUT] (populated via
``geometry.build_lut``), the PCF font (loaded from the sibling
``font_free_mono_8/`` directory via a ``__file__``-relative path), and
the ``Display`` + ``Image`` classes.

Cooperative multitasking uses a module-level sequence counter
(``Display._seq``). Every display-mutating method calls ``_acquire()``
to increment the token; Tier 2 animations holding an older token abort
via ``_is_cancelled(token)`` between awaits. ``Image`` methods reference
module globals (``display``, ``_LUT``, ``_pixels``) directly -- tight
coupling acceptable for a single-display MCU library.

Two-tier API:
  Tier 1 (sync):  render_pattern, render_icon, render_arrow, clear_screen,
                   set_pixel, fill, set_rotation, set_brightness, get_pixel.
  Tier 2 (async): show_leds, show_icon, show_arrow, show_string, show_number,
                   pause.  Require ``await`` from asyncio code.
"""

import asyncio
import board
import neopixel
from rainbowio import colorwheel  # noqa: F401 -- re-export for user convenience

from adafruit_bitmap_font import bitmap_font

from ._constants import WIDTH, HEIGHT, NUM_PIXELS, WHITE, OFF
from .geometry import build_lut
from .icons import ICONS, ARROWS


# ---------------------------------------------------------------------------
# Hardware configuration (kept out of _constants.py so that pure sub-modules
# stay importable on CPython without a device).
# ---------------------------------------------------------------------------
PIXEL_PIN = board.GP0
BRIGHTNESS = 0.05

_pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)


def color(r, g, b):
    """Convenience constructor mirroring Adafruit NeoMatrix's matrix.Color()."""
    return (r, g, b)


# ---------------------------------------------------------------------------
# Coordinate LUT -- mutated in-place on rotation so references stay valid.
# ---------------------------------------------------------------------------
_LUT = build_lut(0)


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
# Font loading -- PCF font via adafruit_bitmap_font.
# Path is resolved relative to this file so the font ships with the package
# on both host and device; os.path coverage on CircuitPython is partial so
# rsplit is preferred over os.path.dirname.
# ---------------------------------------------------------------------------
_FONT_PATH = __file__.rsplit("/", 1)[0] + "/font_free_mono_8/font.pcf"
_font = bitmap_font.load_font(_FONT_PATH)
_font.load_glyphs(range(32, 127))  # preload printable ASCII at import time


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
# Image class
# ---------------------------------------------------------------------------
class Image:
    """Bitmap image for the 8-row LED matrix.

    Monochrome images store column-major bytes + a single color RGB-triple.
    Multi-color images store a flat tuple of per-pixel RGB tuples.

    Image async methods reference module globals (display, _LUT, _pixels)
    directly - for details on the coupling see the package's README.
    """

    __slots__ = ("_data", "_width", "_multi", "_color")

    def __init__(self, data, width, multi, color):
        self._data = data
        self._width = width
        self._multi = multi
        self._color = color

    @staticmethod
    def from_pattern(pattern_str, color=WHITE):
        """Parse a pattern string into an Image.

        color: RGB tuple (mono) or dict {char: RGB} (multi-color).
        Mono images use column-major bytes; multi-color uses per-pixel tuple.

        Column-major conversion happens here (not at render time) because
        Image data persists for repeated show_image / scroll_image calls.
        """
        is_dict = isinstance(color, dict)
        lines = pattern_str.strip().split("\n")
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
                        pixels.append(color.get(ch, OFF))
                    else:
                        pixels.append(OFF)
            return Image(tuple(pixels), img_width, True, None)
        else:
            # Mono: column-major bytes, one byte per column
            cols = bytearray(img_width)
            for x in range(img_width):
                col_byte = 0
                for y in range(height):
                    if x < len(rows[y]) and rows[y][x] == "#":
                        col_byte |= 1 << y
                cols[x] = col_byte
            return Image(bytes(cols), img_width, False, color)

    @property
    def width(self):
        return self._width

    def recolor(self, new_color):
        """Change a mono Image's display color in place. No-op for multi-color."""
        if not self._multi:
            self._color = new_color

    async def show_image(self, offset=0, interval_ms=0):
        """Render WIDTH columns starting at offset. Holds for interval_ms milliseconds."""
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
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def scroll_image(self, offset=1, interval_ms=200):
        """Scroll through the image, advancing `offset` columns per frame, with `interval_ms` milliseconds between frames.

        Uses display._seq for cancellation -- a newer display operation
        will cause this coroutine to return early.
        """
        token = display._acquire()
        max_start = self._width - WIDTH
        if max_start < 0:
            max_start = 0
        pos = 0
        while pos <= max_start:
            if display._is_cancelled(token):
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
            await asyncio.sleep(interval_ms / 1000)
            if display._is_cancelled(token):
                return
            pos += offset


def create_image(pattern_str, color=WHITE):
    return Image.from_pattern(pattern_str, color)


def create_big_image(pattern_str, color=WHITE):
    return Image.from_pattern(pattern_str, color)


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
        holding an older token will detect preemption via _is_cancelled().
        """
        self._seq += 1
        return self._seq

    def _is_cancelled(self, token):
        """Returns True if a newer operation has superseded the given token."""
        return self._seq != token

    # -- Tier 1: Synchronous rendering primitives ----------------------------

    def render_pattern(self, pattern, color=WHITE):
        """Parse and render a pattern string directly to LEDs.

        Direct render via LUT -- no intermediate column-major buffer.
        Faster than create_image for one-shot display since it avoids
        building a persistent bitmap (one parse pass, immediate pixel writes).

        color: RGB tuple for mono ('#'/'.' mode) or dict for palette.
        """
        self._acquire()
        is_dict = isinstance(color, dict)
        lines = pattern.strip().split("\n")
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
                    _pixels[_LUT[x * HEIGHT + y]] = color.get(ch, OFF)
                else:
                    _pixels[_LUT[x * HEIGHT + y]] = color if ch == "#" else OFF
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

    def render_icon(self, icon, color=WHITE):
        """Render an icon bitmap (from ICONS) to the LEDs."""
        self._acquire()
        _render_colmajor(ICONS, icon * WIDTH, color)

    def render_arrow(self, direction, color=WHITE):
        """Render an arrow bitmap (from ARROWS) to the LEDs."""
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

    def set_pixel(self, x, y, color=WHITE):
        """Set one pixel and update the display. Cancels ongoing animations."""
        self._acquire()
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            _pixels[_LUT[x * HEIGHT + y]] = color
            _pixels.show()

    def fill(self, color=WHITE):
        """Fill all pixels. Cancels ongoing animations."""
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
        # Mutate in place so any module reading _LUT sees the new mapping
        # without needing to re-import.
        _LUT[:] = build_lut(degrees)

    # -- Tier 2: Async MakeCode-compatible methods ---------------------------

    async def show_leds(self, pattern, color=WHITE, interval_ms=0):
        """Render a pattern, then hold for interval_ms milliseconds (0 = return after render).

        color: RGB tuple (mono '#'/'.' mode) or dict (palette).
        """
        self.render_pattern(pattern, color)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def show_icon(self, icon, color=WHITE, interval_ms=0):
        """Render icon, hold for interval_ms milliseconds."""
        self.render_icon(icon, color)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def show_arrow(self, direction, color=WHITE, interval_ms=0):
        """Render arrow, hold for interval_ms milliseconds."""
        self.render_arrow(direction, color)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def show_string(self, text, color=WHITE, interval_ms=150):
        """Scroll text across the display.

        Builds a column-major buffer from font glyphs, then slides an
        8-column window across it. interval_ms = milliseconds per column step.
        Single character: display directly, hold for interval_ms * 5.
        """
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
            if interval_ms > 0:
                await asyncio.sleep(interval_ms * 5 / 1000)
            return
        # Scroll: slide window across buffer
        # Pad with blank columns at start and end for scroll-in/out effect
        padding = bytearray(WIDTH)
        scroll_buf = padding + buf + padding
        max_offset = len(scroll_buf) - WIDTH
        for offset in range(max_offset + 1):
            if self._is_cancelled(token):
                return
            _render_colmajor(scroll_buf, offset, color)
            await asyncio.sleep(interval_ms / 1000)
            if self._is_cancelled(token):
                return

    async def show_number(self, n, color=WHITE, interval_ms=150):
        """Display a number. Single digit: centered. Multi-digit: scroll."""
        await self.show_string(str(n), color, interval_ms)

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
                if hasattr(result, "__await__") or hasattr(result, "send"):
                    await result
                await asyncio.sleep(0)

        asyncio.run(_loop())


# Singleton -- ``from display import display``
display = Display()

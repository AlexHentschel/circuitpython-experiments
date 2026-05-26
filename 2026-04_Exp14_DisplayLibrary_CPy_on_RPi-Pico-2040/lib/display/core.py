"""
Runtime display engine for the 8x8 WS2812b NeoPixel matrix.

Owns the live NeoPixel buffer, the coordinate Look-Up Table [LUT] (populated via
``geometry.build_lut``), the PCF font (loaded from the sibling
``font_free_mono_8/`` directory via a ``__file__``-relative path), and
the ``Display`` + ``Image`` classes.

Two-tier API:
  Tier 1 (sync):  render_pattern, render_icon, render_arrow, clear_screen,
                   set_pixel, fill, set_rotation, set_brightness, get_pixel.
  Tier 2 (async): show_leds, show_icon, show_arrow, show_string, show_number,
                   pause.  Require ``await`` from asyncio code.

Cancellation policy: any display-mutating method cancels an in-progress
Tier 2 animation, and starting a new Tier 2 animation cancels any earlier
one. The exceptions are ``get_pixel`` (pure read), ``set_brightness``, and
``set_rotation`` -- deliberately non-cancelling so a running animation is
not disturbed when the user dims the matrix or rotates the frame.
Mechanism: a private, monotonically-increasing sequence counter, captured
by each animation as a token and re-checked between frames; see
``_acquire`` and ``_is_cancelled``.

Bitmap encoding (used throughout this module): monochrome icons, arrows,
glyphs, and ``Image`` instances are stored as *column-major bytes* -- one
byte per column, with bit ``y`` of the byte encoding the pixel at display
row ``y`` (bit 0 = top row). A *column byte* is therefore one such byte,
covering one column of up to ``_MAX_HEIGHT_PER_COLUMN_BYTE`` (= 8)
vertically-stacked pixels. Full format specification in ``bitmap_codec.py``
and ``lib/display/README.md § Column-major bytes``.

``Image`` methods reference module globals (``display``, ``_LUT``, ``_pixels``)
directly -- tight coupling acceptable for a single-display MCU library.
"""

import asyncio
import board
import neopixel
from rainbowio import colorwheel  # noqa: F401 -- re-export for user convenience

from adafruit_bitmap_font import bitmap_font

from ._constants import WIDTH, HEIGHT, NUM_PIXELS, WHITE, OFF
from .geometry import build_lut
from .icons import ICONS, ARROWS, ICON_NAMES, ARROW_NAMES


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
# Runtime pattern-row parsers. Two specialised helpers, one per call-site
# profile:
#   - ``_iter_pattern_rows`` -- cold path. Used by ``Image.from_pattern``,
#     ``create_image``, ``create_big_image``. Lenient: collapses *all* Python
#     whitespace via ``"".join(raw.split())`` (matches the design-time idiom
#     in ``bitmap_codec.pattern_to_colmajor``). Allocations are not
#     performance-critical here.
#   - ``_iter_pattern_rows_fast`` -- hot path. Used by ``Display.render_pattern``,
#     called per Tier 2 frame. Single string allocation per row via
#     ``str.translate`` (no intermediate list, unlike ``split``+``join``).
#     Whitespace tolerance is deliberately narrower: only space, tab, CR
#     are stripped -- the only characters that realistically appear in a
#     human-typed pattern string.
# For strict design-time pattern validation, use
# ``bitmap_codec.pattern_to_colmajor`` (raises on shape and unknown-cell
# errors instead of silently dropping or padding).
# ---------------------------------------------------------------------------

# Translation table for ``_iter_pattern_rows_fast``. Maps the three
# realistically-occurring whitespace ordinals (space, tab, CR) to ``None``,
# which ``str.translate`` interprets as deletion. Built once at import time.
_HOTPATH_WS = {ord(" "): None, ord("\t"): None, ord("\r"): None}


def _iter_pattern_rows(pattern_str):
    """Yield normalized non-blank rows from a pattern -- *cold-path* parser.

    Each emitted string has all Python whitespace (spaces, tabs, CRs, FFs,
    VTs) collapsed via ``"".join(raw.split())``, mirroring the design-time
    idiom in ``bitmap_codec.pattern_to_colmajor``. Blank lines (any amount
    of whitespace) are skipped.

    Cold-path callers: ``Image.from_pattern``, ``create_image``,
    ``create_big_image``. For per-frame parsing in render code, use
    ``_iter_pattern_rows_fast``.
    """
    for raw in pattern_str.split("\n"):
        row = "".join(raw.split())
        if row:
            yield row


def _iter_pattern_rows_fast(pattern_str):
    """Yield non-blank rows from a pattern -- *hot-path* parser.

    Optimised for per-frame use in ``Display.render_pattern``: one string
    allocation per row via ``str.translate(_HOTPATH_WS)`` -- no list
    allocation as ``"".join(raw.split())`` would induce. Strips only space,
    tab, CR; other whitespace (``\\v``, ``\\f``) is left in the row and would
    render as ``OFF`` (unknown char) in mono mode. This is acceptable because
    those code points do not appear in human-typed pattern strings.

    Compared to the cold-path ``_iter_pattern_rows`` this parser is *less*
    whitespace-lenient: it strips only space/tab/CR, not every Python
    whitespace character. The render path is still lenient compared to
    ``bitmap_codec.pattern_to_colmajor`` because unknown row characters are
    not validation errors -- they simply render as ``OFF`` in mono mode or
    as the palette default in multi-color mode.

    The payoff is fewer allocations per row and lower fragmentation pressure
    on CircuitPython's non-compacting GC.
    """
    for raw in pattern_str.split("\n"):
        row = raw.translate(_HOTPATH_WS)
        if row:
            yield row


def _write_pattern_on_the_fly(pattern, color, pixels, lut, off, width, height):
    """Candidate replacement for ``_iter_pattern_rows_fast`` in ``render_pattern``.

    Intentionally unused for now. Sketches the fully-fused hot-path version:
    scan the source string once, skip only space / tab / CR, write each cell
    directly to the NeoPixel buffer, ignore columns past ``width``, ignore
    rows past ``height``, pad short / missing rows with ``off``. Avoids both
    the per-row string allocation of ``_iter_pattern_rows_fast`` and
    generator-yield overhead.

    Does NOT call ``pixels.show()`` -- caller is responsible for flushing
    the buffer to the display after invocation.

    The mono / dict shape of ``color`` is hoisted to a top-level branch so
    the per-cell write has no shape check per cell. The two branches share
    the same state-machine structure with one differing line (cell write);
    closure / callback indirection at the cell-write site would re-introduce
    per-cell call overhead and defeat the hoist.
    """
    x = 0
    y = 0
    row_has_cell = False

    if isinstance(color, dict):
        for ch in pattern:
            if ch == "\n":
                if row_has_cell:
                    while x < width:  # fill remaining positions in the row with Off
                        pixels[lut[x * height + y]] = off
                        x += 1
                    y += 1
                    if y >= height:
                        return
                    x = 0
                    row_has_cell = False
                continue
            if ch == " " or ch == "\t" or ch == "\r":
                continue

            row_has_cell = True
            if x < width:
                pixels[lut[x * height + y]] = color.get(ch, off)
                x += 1
        # reaching the following rows lines means that we have parsed less than height rows
        # up to the tailing newline (otherwise check `if y >= height` above would have returned).
        # EDGE case: row with index heigh has missing newline

        if row_has_cell and y < height:
            while x < width:
                pixels[lut[x * height + y]] = off
                x += 1
            y += 1

        while y < height:
            for xi in range(width):
                pixels[lut[xi * height + y]] = off
            y += 1
    else:
        for ch in pattern:
            if ch == "\n":
                if row_has_cell:
                    while x < width:  # fill remaining positions in the row with Off
                        pixels[lut[x * height + y]] = off
                        x += 1
                    y += 1
                    if y >= height:
                        return
                    x = 0
                    row_has_cell = False
                continue
            if ch == " " or ch == "\t" or ch == "\r":
                continue

            row_has_cell = True
            if x < width:
                pixels[lut[x * height + y]] = color if ch == "#" else off
                x += 1
        # reaching the following rows lines means that we have parsed less than height rows
        # up to the tailing newline (otherwise check `if y >= height` above would have returned).
        # EDGE case: row with index heigh has missing newline

        if row_has_cell and y < height:
            while x < width:
                pixels[lut[x * height + y]] = off
                x += 1
            y += 1

        while y < height:
            for xi in range(width):
                pixels[lut[xi * height + y]] = off
            y += 1


# ---------------------------------------------------------------------------
# Monochrome column-major render helper
# ---------------------------------------------------------------------------
def _render_colmajor(data, offset, color):
    """Render WIDTH column bytes from ``data`` starting at ``data[offset]`` to ``_pixels``.

    Each ``data[offset + x]`` is one column byte (i.e. a single byte representing
    one column of the bitmap). Bit ``y`` of the byte selects the pixel at display
    row ``y`` (with bit 0 = top row).
    On the hardware level, the LED are addressed using a single index. The Look-Up Table
    [``LUT`` ] translates from logical pixels (x, y) to the physical strip index. The ``LUT``
    is organized using x-major convention, i.e. ``_LUT[x * HEIGHT + y]`` returns the physical
    strip index for the logical pixel (x, y).
    After all pixel values have been written, then we call ``show()`` once.

    CAUTION: this function is part of the hot path and used to render many icons;
    especially for scrolling this code is performance sensitive.
    """
    # Cache module globals into function-locals: LOAD_FAST (frame-slot access) is cheaper than LOAD_GLOBAL (module-dict lookup).
    # This is explained in more detail in MicroPython docs: `docs.micropython.org/en/latest/reference/speed_python.html` § "Caching object references".
    # CircuitPython inherits this unchanged from MicroPython's VM: AI-verified sources are `py/vm.c` (MP_BC_LOAD_FAST_N, MP_BC_LOAD_GLOBAL) and `py/runtime.c`
    # (mp_load_global);
    pixels = _pixels
    lut = _LUT
    off = OFF
    for x in range(WIDTH):
        col_byte = data[offset + x]
        x_base = x * HEIGHT  # matches `geometry.build_lut` slot-name convention
        for y in range(HEIGHT):
            pixels[lut[x_base + y]] = color if (col_byte >> y) & 1 else off
    pixels.show()


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
      ascent:       rows from baseline to top of tallest glyph (= display row 0).
      dy:           rows from baseline to bottom edge of this glyph's bitmap.
      dx:           columns from current text position to left edge of this glyph's bitmap.
      glyph.height: the height of the glyph's bitmap in pixels
      shift_x:      advance width (columns the current text position moves right after this glyph).
      width/height: pixel dimensions of the glyph's actual bitmap.

    Coordinate mapping from glyph bitmap (cx, cy) to display:
      display_row = ascent - height - dy + cy
        (glyph top edge at font-y = dy + height; display row 0 = ascent)
      display_col = cx + dx
        (dx = horizontal offset from current text position to bitmap left edge)
    """
    glyph = _font.get_glyph(ord(ch))
    if glyph is None:
        return bytes(WIDTH)
    bm = glyph.bitmap
    ascent = _font.ascent  # the maximum vertical distance from the baseline to the top of the tallest glyphs
    cols = bytearray(glyph.shift_x)
    # row_origin is the top row of glyph bitmap in display coordinates (loop-invariant)
    row_origin = ascent - glyph.height - glyph.dy
    for cx in range(glyph.width):
        col_byte = 0
        for cy in range(glyph.height):
            display_row = row_origin + cy
            if 0 <= display_row < HEIGHT and bm[cx + cy * glyph.width]:
                col_byte |= 1 << display_row
        # dx = horizontal offset: current text position -> bitmap left edge
        bx = cx + glyph.dx
        if 0 <= bx < len(cols):
            cols[bx] = col_byte
    return bytes(cols)


# ---------------------------------------------------------------------------
# Scrolling-text helpers: ring-window renderer + one-column-at-a-time
# glyph feeder. Used by ``Display.show_string``; see that method's
# docstring for the ring-size derivation.
# ---------------------------------------------------------------------------
def _render_ring_window(ring, read_head, color_on):
    """Render a WIDTH-sized ring buffer as a left-to-right window starting at ``read_head``.

    The ring holds exactly ``WIDTH`` column bytes; ``read_head`` is the index
    of the leftmost visible column. Wrap is handled by a single subtract
    instead of a per-pixel modulo (cheaper on the MCU VM).
    """
    pixels = _pixels
    lut = _LUT
    off = OFF
    x_base = 0
    for x in range(WIDTH):
        idx = read_head + x
        if idx >= WIDTH:
            idx -= WIDTH
        col_byte = ring[idx]
        x_base += HEIGHT  # light weight way of calulating x_base = x * HEIGHT
        for y in range(HEIGHT):
            pixels[lut[x_base + y]] = color_on if (col_byte >> y) & 1 else off
    pixels.show()


class _GlyphColumnFeeder:
    """Yield one glyph column byte at a time across a text string.

    Materialises exactly one glyph's column buffer at a time (via
    ``_glyph_columns``), then exposes its bytes one-by-one. ``next_column``
    returns ``None`` once the text is exhausted -- callers substitute
    blank columns (``0``) to pad the scroll-out tail.

    Bounded memory: only the current glyph's cols plus a cursor live in
    the feeder, regardless of how long the text is. This is the whole
    point of the ring-buffer scroll path.
    """

    __slots__ = ("_text", "_char_idx", "_cols", "_col_idx")

    def __init__(self, text):
        self._text = text
        self._char_idx = 0
        self._cols = b""
        self._col_idx = 0

    def next_column(self):
        # Load the next glyph whenever the current glyph's columns are exhausted;
        # `while` condition initially succeeds because `_cols` is empty and `_col_idx = 0`.
        # Usage of `while` here (instead of `if`) skips any zero-width glyphs.
        while self._col_idx >= len(self._cols):
            if self._char_idx >= len(self._text):
                return None
            self._cols = _glyph_columns(self._text[self._char_idx])  # load glyph
            self._char_idx += 1
            self._col_idx = 0  # for the new glyph, we start at column with index 0
        b = self._cols[self._col_idx]
        self._col_idx += 1
        return b


# ---------------------------------------------------------------------------
# Image class
# ---------------------------------------------------------------------------
class Image:
    """Bitmap image for the 8-row LED matrix.

    Monochrome images store column-major bytes + a single color RGB-triple.
    Multi-color images store a flat sequence of per-pixel RGB tuples (one per pixel).
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
        The returned Image is reusable across multiple ``show_image`` /
        ``scroll_image`` calls.

        Rows past ``HEIGHT`` are dropped; short rows are padded with OFF.
        Image width is the widest of the kept rows. Unknown chars in mono
        mode render as OFF. Whitespace (spaces, tabs, CRs) in the pattern
        is ignored. For strict size validation, use ``create_image`` or
        ``create_big_image``.
        """
        # Internal encoding: mono images store column-major bytes (one byte
        # per column, bit y = row y counted from top); multi-color stores a flat
        # tuple of per-pixel RGB tuples. Conversion happens here so render methods
        # do not re-parse on each call.
        is_dict = isinstance(color, dict)
        rows = list[str](_iter_pattern_rows(pattern_str))
        height = min(len(rows), HEIGHT)
        img_width = max((len(r) for r in rows[:height]), default=WIDTH)

        if is_dict:
            pixels = [OFF] * (img_width * HEIGHT)
            for y in range(height):
                row = rows[y]
                for x in range(min(img_width, len(row))):
                    pixels[x * HEIGHT + y] = color.get(row[x], OFF)
            return Image(tuple(pixels), img_width, True, None)
        else:
            cols = bytearray(img_width)
            for y in range(height):
                row = rows[y]
                for x in range(min(img_width, len(row))):
                    if row[x] == "#":
                        cols[x] |= 1 << y
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
        self._render_window(offset)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def scroll_image(self, offset=1, interval_ms=200):
        """Scroll through the image, advancing `offset` columns per frame, with `interval_ms` milliseconds between frames.

        Cancellable: any newer display operation causes this coroutine to
        return early (see module docstring's cancellation policy).
        """
        token = display._acquire()
        max_start = self._width - WIDTH
        if max_start < 0:
            max_start = 0
        pos = 0
        while pos <= max_start:
            if display._is_cancelled(token):
                return
            self._render_window(pos)
            await asyncio.sleep(interval_ms / 1000)
            if display._is_cancelled(token):
                return
            pos += offset

    def _render_window(self, offset):
        """Render the WIDTH-column window starting at ``offset`` into ``_pixels`` and show().

        Splits the display into three slices ahead of the per-pixel loop --
        ``[0, x_min)`` and ``[x_max, WIDTH)`` render OFF (source is out of
        bounds), ``[x_min, x_max)`` copies from ``self._data`` with no
        per-iteration bounds check. This replaces an ``if 0 <= src_x < width``
        check inside the ``WIDTH * HEIGHT`` = 64-iteration inner loop.

        Negative ``offset`` is supported (image appears partially off the
        left edge) via ``x_min = max(0, -offset)``.
        """
        pixels = _pixels
        lut = _LUT
        off = OFF
        width = self._width
        x_min = -offset
        if x_min < 0:
            x_min = 0
        elif x_min > WIDTH:
            x_min = WIDTH
        x_max = width - offset
        if x_max < x_min:
            x_max = x_min
        elif x_max > WIDTH:
            x_max = WIDTH

        if self._multi:
            data = self._data
            for x in range(x_min):
                x_base = x * HEIGHT
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = off
            for x in range(x_min, x_max):
                x_base = x * HEIGHT
                src_base = (offset + x) * HEIGHT
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = data[src_base + y]
            for x in range(x_max, WIDTH):
                x_base = x * HEIGHT
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = off
        else:
            data = self._data
            color_on = self._color
            for x in range(x_min):
                x_base = x * HEIGHT
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = off
            for x in range(x_min, x_max):
                x_base = x * HEIGHT
                col_byte = data[offset + x]
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = color_on if (col_byte >> y) & 1 else off
            for x in range(x_max, WIDTH):
                x_base = x * HEIGHT
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = off
        pixels.show()


# ---------------------------------------------------------------------------
# Icons / Arrows -- Image instances constructed once at import from the bulk
# ``ICONS`` / ``ARROWS`` bytes; names/ordering come from ``ICON_NAMES`` /
# ``ARROW_NAMES`` in ``icons.py`` (single source of truth). ``bytes``
# slicing copies, so each Image owns its own 8-byte backing block -- the
# bulk arrays exist for deterministic ordering, not byte-sharing.
# Each Image's stored color is WHITE; ``render_icon`` / ``render_arrow``
# accept a ``color`` kwarg that overrides it at render time.
#
# Sharing hazard: ``Icons.HEART`` / ``Arrows.NORTH`` are module-global
# singletons. Calling ``.recolor(...)`` on one mutates the shared instance
# for all callers (and persists across coroutine boundaries). Primary
# callers (``render_icon`` / ``show_icon`` / ``render_arrow`` / ``show_arrow``)
# already pass ``color`` as a render-time override, so staying on those is
# the safe path. If you want a private, mutable copy of an icon bitmap,
# build one via ``create_image`` from a pattern.
# ---------------------------------------------------------------------------
def _build_image_namespace(names, data):
    """Populate a bare class with Image instances indexed by name order."""
    cls = type("_ImageNamespace", (), {})
    for i, name in enumerate(names):
        start = i * WIDTH
        setattr(cls, name, Image(data[start : start + WIDTH], WIDTH, False, WHITE))
    return cls


Icons = _build_image_namespace(ICON_NAMES, ICONS)
Arrows = _build_image_namespace(ARROW_NAMES, ARROWS)


def create_image(pattern_str, color=WHITE):
    """Create an 8x8 Image.

    Raises ``ValueError`` if the pattern is not exactly ``WIDTH`` columns
    by ``HEIGHT`` rows (whitespace and blank lines ignored, see
    ``_iter_pattern_rows``).
    """
    img = Image.from_pattern(pattern_str, color)
    row_count = sum(1 for _ in _iter_pattern_rows(pattern_str))
    if img.width != WIDTH or row_count != HEIGHT:
        raise ValueError("create_image requires {h} rows x {w} columns; got {rh} rows x {rw} columns".format(h=HEIGHT, w=WIDTH, rh=row_count, rw=img.width))
    return img


def create_big_image(pattern_str, color=WHITE):
    """Create a 16-wide Image (scrollable).

    Raises ``ValueError`` if the pattern is not exactly ``2 * WIDTH``
    columns by ``HEIGHT`` rows.
    """
    img = Image.from_pattern(pattern_str, color)
    row_count = sum(1 for _ in _iter_pattern_rows(pattern_str))
    expected_w = 2 * WIDTH
    if img.width != expected_w or row_count != HEIGHT:
        raise ValueError("create_big_image requires {h} rows x {w} columns; got {rh} rows x {rw} columns".format(h=HEIGHT, w=expected_w, rh=row_count, rw=img.width))
    return img


# ---------------------------------------------------------------------------
# Display class
# ---------------------------------------------------------------------------
class Display:
    """Controls an 8x8 WS2812b NeoPixel matrix.

    Singleton at module level (``display``). Starting any display-mutating
    operation cancels any Tier 2 animation in progress. Non-cancelling
    methods: ``get_pixel``, ``set_brightness``, ``set_rotation``. See the
    module docstring for the full cancellation policy.
    """

    def __init__(self):
        self._seq = 0

    # -- Cancellation token --------------------------------------------------

    def _acquire(self):
        """Start a new display-operation generation.

        Increments the sequence counter and returns the new value as a
        cancellation token. Any Tier 2 animation that captured an earlier
        token before this call will see ``_is_cancelled(its_token)`` become
        True on its next check, and should return early. Called internally
        by every display-mutating method.
        """
        self._seq += 1
        return self._seq

    def _is_cancelled(self, token):
        """True if a display operation newer than ``token`` has started.

        Tier 2 animations check this between frames -- on both sides of an
        ``await`` -- and return early when it becomes True.
        """
        return self._seq != token

    # -- Tier 1: Synchronous rendering primitives ----------------------------

    def render_pattern(self, pattern, color=WHITE):
        """Parse and render a pattern string directly to LEDs.

        Direct render via LUT -- no intermediate column-major buffer.
        Faster than create_image for one-shot display since it avoids
        building a persistent bitmap (one parse pass, immediate pixel writes).

        color: RGB tuple for mono ('#'/'.' mode) or dict for palette.
        Short rows are padded with OFF; rows past HEIGHT are ignored.
        """
        self._acquire()
        # Cache module globals as function-locals so the inner WIDTH * HEIGHT
        # pixel-write loop hits LOAD_FAST instead of LOAD_GLOBAL. Same idiom
        # as ``_render_colmajor``; rationale and CPy/MicroPython VM sources
        # documented there and in ``TECHNICAL.md § Name loading``.
        pixels = _pixels
        lut = _LUT
        off = OFF
        width = WIDTH
        height = HEIGHT
        is_dict = isinstance(color, dict)
        y = 0
        for row in _iter_pattern_rows_fast(pattern):
            if y >= height:
                break
            cap = min(width, len(row))
            for x in range(cap):
                ch = row[x]
                if is_dict:
                    pixels[lut[x * height + y]] = color.get(ch, off)
                else:
                    pixels[lut[x * height + y]] = color if ch == "#" else off
            for x in range(cap, width):
                pixels[lut[x * height + y]] = off
            y += 1
        while y < height:
            for x in range(width):
                pixels[lut[x * height + y]] = off
            y += 1
        pixels.show()

    def render_icon(self, icon, color=WHITE):
        """Render an icon ``Image`` (e.g. ``Icons.HEART``) to the LEDs.

        ``color`` is the mono render color and always overrides the icon's
        stored color -- the icon is effectively a reusable bitmap shape.
        """
        self._acquire()
        _render_colmajor(icon._data, 0, color)

    def render_arrow(self, arrow, color=WHITE):
        """Render an arrow ``Image`` (e.g. ``Arrows.NORTH``) to the LEDs.

        ``color`` is the mono render color and always overrides the arrow's
        stored color.
        """
        self._acquire()
        _render_colmajor(arrow._data, 0, color)

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
        """Read the buffered pixel color at (x, y). Read-only; does not cancel ongoing animations."""
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
        """Rebuild coordinate LUT for 0/90/180/270 clockwise rotation. Does not cancel animations.

        ``degrees`` must be one of ``0``, ``90``, ``180``, ``270`` or their counter-clockwise equivalents
        ``-270``, ``-180``, ``-90``. Other values raise ``ValueError``. Out-of-range inputs (``360``,
        ``-360``, ...) are rejected; normalise at the call site (e.g. ``set_rotation(d % 360)``) if wrap-around
        is needed.
        """
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
        """Render an icon ``Image`` (e.g. ``Icons.HEART``), hold for interval_ms milliseconds."""
        self.render_icon(icon, color)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def show_arrow(self, arrow, color=WHITE, interval_ms=0):
        """Render an arrow ``Image`` (e.g. ``Arrows.NORTH``), hold for interval_ms milliseconds."""
        self.render_arrow(arrow, color)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def show_string(self, text, color=WHITE, interval_ms=150, loop=False):
        """Scroll text across the display.

        Fit-on-screen text (total glyph-column width <= WIDTH) is centered
        and held: for ``interval_ms * 5`` ms when ``interval_ms > 0``,
        indefinitely when ``loop=True``, or returned immediately when
        ``interval_ms == 0`` and ``loop=False`` (i.e. render-and-return,
        the short-text counterpart to ``show_leds(pattern, interval_ms=0)``).

        Longer text scrolls one column per ``interval_ms`` step through a
        ``WIDTH``-slot ring buffer, fed one column at a time from a
        ``_GlyphColumnFeeder`` (see below) -- so scroll-loop memory is
        O(WIDTH) *beyond the input text reference that the caller
        already holds*.

        Ring sizing: the visible window is exactly ``WIDTH`` columns; each
        newly arriving column overwrites the slot that just scrolled off
        the left edge, so a single ``WIDTH``-byte ring is sufficient. The
        initial all-zero ring serves as the scroll-in padding; scroll-out
        is produced by feeding ``WIDTH + 1`` trailing blanks once the
        feeder drains so the final fully-blank frame is actually
        rendered. A non-looping scroll therefore ends exactly when the
        last meaningful column has left the screen.

        loop: if True, keep scrolling indefinitely (or, for fit-on-screen
        text, hold indefinitely) until cancelled by another display
        operation. On the short-text hold path, cancellation is polled
        every ``interval_ms`` ms (or every 50 ms when ``interval_ms == 0``).
        """
        token = self._acquire()
        text = str(text)
        if not text:
            return
        sleep_s = interval_ms / 1000

        # Materialise glyphs only as far as needed to decide "fits on screen?".
        fit_buf = bytearray()
        for ch in text:
            fit_buf.extend(_glyph_columns(ch))
            if len(fit_buf) > WIDTH:
                break

        if len(fit_buf) <= WIDTH:
            pad = (WIDTH - len(fit_buf)) // 2
            padded = bytearray(WIDTH)
            for i in range(len(fit_buf)):
                padded[pad + i] = fit_buf[i]
            _render_colmajor(padded, 0, color)
            if loop:
                poll_s = sleep_s if interval_ms > 0 else 0.05
                while True:
                    if self._is_cancelled(token):
                        return
                    await asyncio.sleep(poll_s)
            if interval_ms > 0:
                await asyncio.sleep(interval_ms * 5 / 1000)
            return

        while True:
            feeder = _GlyphColumnFeeder(text)
            ring = bytearray(WIDTH)
            read_head = 0
            trailing_blanks = 0
            while True:
                if self._is_cancelled(token):
                    return
                _render_ring_window(ring, read_head, color)
                await asyncio.sleep(sleep_s)
                if self._is_cancelled(token):
                    return
                col = feeder.next_column()
                if col is None:
                    col = 0
                    trailing_blanks += 1
                ring[read_head] = col
                read_head += 1
                if read_head == WIDTH:
                    read_head = 0
                # `> WIDTH` (not `>=`) so the final fully-blank frame is
                # actually rendered -- with `>=` the loop breaks while
                # the last meaningful column is still at x=0.
                if trailing_blanks > WIDTH:
                    break
            if not loop:
                return

    async def show_number(self, n, color=WHITE, interval_ms=150, loop=False):
        """Display a number via ``show_string(str(n))``.

        Fit-on-screen numbers (total glyph width <= WIDTH -- typically
        one digit in the bundled monospace font) are centered and held;
        longer numbers scroll. See ``show_string`` for the full behavior
        including ``loop=True``.
        """
        await self.show_string(str(n), color, interval_ms, loop)

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

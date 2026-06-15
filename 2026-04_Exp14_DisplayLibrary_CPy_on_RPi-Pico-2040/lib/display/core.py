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
  Lifecycle:      deinit -- releases the data pin / PIO; the singleton is
                   unusable afterwards (no re-init path).

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

# PEP 563: defer all annotation evaluation, so PEP 585 subscripts
# (e.g. ``dict[str, tuple[int, int, int]]``) and forward references work
# uniformly without per-annotation string-quoting and incur zero on-device
# evaluation cost. Required for this file because the typing-guarded
# ``Callable`` import below is unbound at runtime on device.
from __future__ import annotations

# Type hints only -- not loaded at runtime on device. See:
# https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/typing-information
# https://github.com/adafruit/Adafruit_CircuitPython_NTP/issues/18
try:
    from typing import Callable
except ImportError:
    pass

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


def color(r: int, g: int, b: int) -> tuple[int, int, int]:
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


def _iter_pattern_rows(pattern_str: str):
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


# Translation table for ``_iter_pattern_rows_fast``. Maps the three
# realistically-occurring whitespace ordinals (space, tab, CR) to ``None``,
# which ``str.translate`` interprets as deletion. Built once at import time.
_HOTPATH_WS = {ord(" "): None, ord("\t"): None, ord("\r"): None}


def _iter_pattern_rows_fast(pattern_str: str):
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


def _write_pattern_on_the_fly(
    pattern: str,
    color: tuple[int, int, int] | dict[str, tuple[int, int, int]],
    pixels: neopixel.NeoPixel,
    lut: bytearray,
    off: tuple[int, int, int],
    width: int,
    height: int,
) -> None:
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

        if row_has_cell and y < height:  # completing last row if partially-filled
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

        if row_has_cell and y < height:  # completing last row if partially-filled
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
def _render_colmajor(data: bytes, offset: int, color: tuple[int, int, int]) -> None:
    """Render WIDTH column bytes from ``data`` starting at ``data[offset]`` to ``_pixels``.

    Each ``data[offset + x]`` is one column byte (i.e. a single byte representing
    one column of the bitmap). Bit ``y`` of the byte selects the pixel at display
    row ``y`` (with bit 0 = top row).
    On the hardware level, the LEDs are addressed using a single index. The Look-Up Table
    [``LUT`` ] translates from logical pixels (x, y) to the physical strip index. The ``LUT``
    is organized using x-major convention, i.e. ``_LUT[x * HEIGHT + y]`` returns the physical
    strip index for the logical pixel (x, y).
    After all pixel values have been written, then we call ``show()`` once.

    CAUTION: this function is part of the hot path and used to render many icons;
    especially for scrolling this code is performance sensitive.
    """
    # Cache module globals into function-locals: LOAD_FAST (frame-slot access) is cheaper than LOAD_GLOBAL (module-dict lookup). This is explained in
    # more detail in MicroPython docs: `docs.micropython.org/en/latest/reference/speed_python.html` § "Caching object references". CircuitPython inherits
    # this unchanged from MicroPython's VM: AI-verified sources are `py/vm.c` (MP_BC_LOAD_FAST_N, MP_BC_LOAD_GLOBAL) and `py/runtime.c` (mp_load_global);
    pixels = _pixels
    lut = _LUT
    off = OFF
    x_base = 0  # invariant at top of loop: x_base == x * HEIGHT (`geometry.build_lut` slot convention)
    for x in range(WIDTH):
        col_byte = data[offset + x]
        for y in range(HEIGHT):
            pixels[lut[x_base + y]] = color if (col_byte >> y) & 1 else off
        x_base += HEIGHT  # advance to next column; addition avoids a per-column multiply
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


def _glyph_columns(ch: str) -> bytes:
    """Convert a font glyph to column-major bytes for the 8-row LED matrix.

    Returns one byte per column spanning the glyph's advance width.
    Bit N of each byte = row N (with row 0 = top).

    Font metric terms (from fontio.Glyph / PCF):
      ascent:       rows from baseline to top of tallest glyph (= display row 0).
      dy:           rows from baseline to bottom edge of this glyph's bitmap.
      dx:           columns from current text position to left edge of this glyph's bitmap.
      glyph.height: the height of the glyph's bitmap in pixels
      shift_x:      advance width (columns the current text position moves right after this glyph).
      width/height: pixel dimensions of the glyph's actual bitmap.

    Coordinate systems (formal 2D handedness with +z out of the screen towards the observer;
    x points right in both, so only the y-axis direction differs). IMPORTANT: glyph properties
    are defined in the right-handed system, while the glyph bitmap is in the left-handed system.
      right-handed -- y UP from the baseline:    ``ascent``, ``dy`` (metric offsets).
      left-handed  -- y DOWN from the top:       ``cx``/``cy``, ``display_row``/``col`` (bitmap rasters).
      magnitudes are coordinate system agnostic: ``height``, ``width`` (glyph extent).
    Only the vertical placement crosses coordinate systems: ``dy + height`` is the glyph's top edge in the
    right-handed system (bottom left pixel being the origin). The transformation ``ascent - (dy + height)``
    flips it into the left-handed display coordinate system (top left pixel being the origin).

    Coordinate mapping from glyph bitmap (cx, cy) to display (x,y). Note: the glyph bitmap rastering is already stored
    in the left-handed coordinate system, which happens to be aligned with the display; hence ``cy`` is not fliped:
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
            y = row_origin + cy
            if 0 <= y < HEIGHT and bm[cx + cy * glyph.width]:
                col_byte |= 1 << y
        # dx = horizontal offset: current text position -> bitmap left edge
        x = cx + glyph.dx
        if 0 <= x < len(cols):
            cols[x] = col_byte
    return bytes(cols)


# ---------------------------------------------------------------------------
# Scrolling-text helpers: ring-window renderer + one-column-at-a-time
# glyph feeder. Used by ``Display.show_string``; see that method's
# docstring for the ring-size derivation.
# ---------------------------------------------------------------------------
def _render_ring_window(ring: bytearray, read_head: int, color_on: tuple[int, int, int]) -> None:
    """Render a WIDTH-sized ring buffer as a left-to-right window starting at ``read_head``.

    The ring holds exactly ``WIDTH`` column bytes; ``read_head`` is the index
    of the leftmost visible column. Wrap is handled by a single subtract
    instead of a per-pixel modulo (cheaper on the MCU VM).
    """
    pixels = _pixels
    lut = _LUT
    off = OFF
    x_base = 0  # invariant at top of loop: x_base == x * HEIGHT
    for x in range(WIDTH):
        idx = read_head + x
        if idx >= WIDTH:
            idx -= WIDTH
        col_byte = ring[idx]
        for y in range(HEIGHT):
            pixels[lut[x_base + y]] = color_on if (col_byte >> y) & 1 else off
        x_base += HEIGHT  # advance to next column; addition avoids a per-column multiply
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

    def __init__(self, text: str) -> None:
        self._text = text
        self._char_idx = 0
        self._cols = b""
        self._col_idx = 0

    def next_column(self) -> int | None:
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

    The image's height is always assumed to be ``HEIGHT`` (8) rows. Width is independent of the display
    and may be smaller, equal to, or **larger** than the ``WIDTH`` (8) physical columns of the LED matrix:
      - ``create_image`` builds an exactly-``WIDTH`` (8-wide) image.
      - ``create_big_image`` builds a ``2 * WIDTH`` (16-wide) image.
      - ``from_pattern`` accepts any width (the widest kept row).
    An image wider than the display is shown a ``WIDTH``-column window at a
    time: ``show_image(offset)`` picks the window and ``scroll_image`` animates
    it across the full width -- image columns outside that window are trimmed.
    Where the display window overhangs the image (a narrower image, or an ``offset``
    past an edge), the uncovered display columns render as ``OFF``.
    """

    __slots__ = ("_data", "_width", "_multi", "_color")

    def __init__(
        self,
        data: bytes | tuple,
        width: int,
        multi: bool,
        color: tuple[int, int, int] | None,
    ) -> None:
        self._data = data
        self._width = width
        self._multi = multi
        self._color = color

    @staticmethod
    def from_pattern(
        pattern_str: str,
        color: dict[str, tuple[int, int, int]] | tuple[int, int, int] = WHITE,
    ) -> Image:
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
        rows = list(_iter_pattern_rows(pattern_str))
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
    def width(self) -> int:
        return self._width

    def recolor(self, new_color: tuple[int, int, int]) -> None:
        """Change a mono Image's display color in place. No-op for multi-color."""
        if not self._multi:
            self._color = new_color

    async def show_image(self, offset: int = 0, interval_ms: int = 0) -> None:
        """Render WIDTH columns starting at offset. Holds for interval_ms milliseconds."""
        display._acquire()
        self._render_window(offset)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def scroll_image(self, offset: int = 1, interval_ms: int = 200) -> None:
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

    def _render_window(self, offset: int) -> None:
        """Render a WIDTH-column window of this image at ``offset`` into ``_pixels`` and show().

        ``offset`` is the image column shown at display column 0. The image width is independent of the display: it may exceed ``WIDTH``
        (e.g. a 16-pixel-wide ``create_big_image``, scrolled via ``scroll_image``) or be narrower. Only the window columns
        ``[offset, offset + WIDTH)`` from ``self._data`` are transferred to the display; any display column not covered by the image
        renders ``OFF`` (e.g. if the picture is narrower than the display, or if offset leaves display columns uncovered).

        Negative ``offset`` is supported (image appears partially off the left edge) via ``x_min = max(0, -offset)``.


        -------- Goal -----------------------------------------------------------------------------------------------------------

        ``x_min`` and ``x_max`` are the two display-column boundaries that split the WIDTH-wide display into three contiguous slices:
        a left OFF margin ``[0, x_min)``; the image-covered span ``[x_min, x_max)``; and a right OFF margin ``[x_max, WIDTH)``. The goal is
        to iterate over the columns with a ``range(x_min, x_max)``, where all boundary checks are efficiently pre-computed.

            0          x_min                    x_max          WIDTH
            │           [───────── image ──────── )               │
            ☐ ☐ ☐ ☐ ☐ ☐ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ▣ ☐ ☐ ☐ ☐ ☐ ☐ ☐ ☐ │
            ╰── OFF ──╯                           ╰──── OFF ────╯

        -------- Deriving the window bounds ``x_min`` and ``x_max`` --------------------------------------------------------------

        Display column ``x ∈ [0, WIDTH)`` shows image column ``src = offset + x`` iff ``0 ≤ src < width``. Hence, exactly the display columns ``x ∈ [0, WIDTH)``
        are covered by the image that satisfy ``-offset ≤ x < width - offset``. Intersecting with the display domain ``[0, WIDTH)`` gives the interval of display
        columns covered by the image: ``x ∈ I := [max(0, -offset), min(WIDTH, width - offset))``. Note that I is the empty interval, iff the formula for the lower
        bound is greater than or equal to the formula for the upper bound.

        Cases (``[...]`` = the WIDTH-wide display; ``▣`` covered display col, ``☐`` OFF display col, ``▪`` image col off-window):

            (0) 0 ≤ offset; display fully covered     ▪[▣▣▣▣]▪    x_min=0,        x_max=WIDTH                    fully covered
            (1) 0 < offset, image runs out         ▪▪▪▪[▣▣☐☐]     x_min=0,        x_max=width-offset             right tail OFF
            (2) negative offset < 0                    [☐▣▣▣]▪▪▪  x_min=-offset,  x_max=min(width-offset,WIDTH)  left edge OFF
            (3) negative offset < 0, narrow image      [☐▣☐☐]     x_min=-offset,  x_max=width-offset             both edges OFF

        We want to define loop bounds ``x_min`` and ``x_max``, such that we cover the edge case where the interval is empty: formally ``x_max ≥ x_min`` and
        ``x_max, x_min ∈ [0, WIDTH]`` and ``[x_min, x_max) = I``. Observations:
        • If ``offset ≥ Image.width``, the image has entirely been moved off the display on the left. Hence, let's define
          ``offset_upper_cutoff := min(offset, Image.width)``. For any ``offset ≥ offset_upper_cutoff``, we can just use ``offset_upper_cutoff`` instead.
          Physical display output remains unchanged: no part of the image is visible.
        • For a negative ``offset ≤ - display.WIDTH``, the image has entirely been moved off the display on the right. For any ``offset ≤ offset_lower_cutoff``,
          we can just use ``offset_lower_cutoff := max(offset, -display.WIDTH)`` without altering the display output (no part of the image visible).

        We define ``_offset := max(- display.WIDTH, min(offset, Image.width))``. As we have argued above, offsets exceeding the cutoff bounds can be clipped
        without changing the output. (It can be proven that offsets outside the clipping bound always result in I = ∅.) Therefore, we can state I also in terms
        of the clipped offset:
           ``x ∈ I ≡ [x_min, x_max)``   with   ``x_min := max(0, - _offset)``  and  ``x_max := min(WIDTH, width - _offset)``
         By definition, we have ``0 ≤ x_min``. Furthermore, ``x_max = min(WIDTH, …)`` ensures  ``x_max ≤ WIDTH``.
        • For ``_offset = 0`` we find: ``x_min ≤ x_max`` and ``x_max, x_min ∈ [0, WIDTH]``, because ``WIDTH`` and ``width`` are non-negative integers.
        • For ``_offset > 0`` we find: ``x_max = min(WIDTH, width - _offset) ≥ 0``, because ``_offset`` is upper-bounded by ``Image.width``.
          Since ``x_min = 0`` for any positive ``_offset``, we conclude that ``x_min ≤ x_max`` and ``x_max, x_min ∈ [0, WIDTH]``
        • For ``_offset < 0`` we find: we have ``0 ≤ x_max`` because both arguments of ``min(WIDTH, width - _offset)`` are non-negative.
          As ``_offset`` is lower-bounded by ``- display.WIDTH``, we have ``x_min ≤ WIDTH``. Hence, ``x_max, x_min ∈ [0, WIDTH]``.
          For negative ``_offset``, we have ``x_min = - _offset`` which implies: ``x_min = - _offset ≤ width - _offset`` (for non-negative ``width``).
          We note that the lower ``_offset`` bound implies ``x_min = -_offset ≤ WIDTH``. Hence we have shown that ``x_min`` is smaller or equal to
          either terms in ``min(WIDTH, width - _offset) = x_max``, i.e. ``x_min ≤ x_max``.

        ┌──── Corollary ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ For any  ``_offset := max(- display.WIDTH, min(offset, Image.width))``, the interval I of display columns covered by the image is  │
        │ given exactly by:                                                                                                                  │
        │              ``x ∈ I ≡ [x_min, x_max)``       with  ``x_min := max(0, - _offset)``  and  ``x_max := min(WIDTH, width - _offset)``  │
        │ It is guaranteed that                                                                                                              │
        │  •  ``x_max, x_min ∈ [0, WIDTH]`` implies values are within the display's bound                                                    │
        │  •  ``x_min ≤ x_max`` allows iteration via Python ``range(x_min, x_max)``    (efficient)                                           │
        │  •  for x ∈ I ≡ [x_min, x_max), the image column displayed is ``offset + x``                                                       │
        │  •  display columns left of x_min are off, specifically columns x ∈ [0, x_min); and likewise columns x ∈ [x_max, WIDTH) are off.   │
        └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
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

        # x_base invariant at the top of every loop body: x_base == x * HEIGHT.
        # The three slices cover contiguous x in [0, x_min), [x_min, x_max),
        # [x_max, WIDTH), so a single accumulator stays in sync across them --
        # addition per column instead of recomputing x * HEIGHT.
        if self._multi:
            data = self._data
            x_base = 0
            for x in range(x_min):
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = off
                x_base += HEIGHT
            src_base = (offset + x_min) * HEIGHT  # one setup multiply; loop body stays additive
            for x in range(x_min, x_max):
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = data[src_base + y]
                x_base += HEIGHT
                src_base += HEIGHT
            for x in range(x_max, WIDTH):
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = off
                x_base += HEIGHT
        else:
            data = self._data
            color_on = self._color
            x_base = 0
            for x in range(x_min):
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = off
                x_base += HEIGHT
            for x in range(x_min, x_max):
                col_byte = data[offset + x]
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = color_on if (col_byte >> y) & 1 else off
                x_base += HEIGHT
            for x in range(x_max, WIDTH):
                for y in range(HEIGHT):
                    pixels[lut[x_base + y]] = off
                x_base += HEIGHT
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
def _build_image_namespace(names: tuple[str, ...], data: bytes) -> type:
    """Populate a bare class with Image instances indexed by name order."""
    cls = type("_ImageNamespace", (), {})
    for i, name in enumerate(names):
        start = i * WIDTH
        setattr(cls, name, Image(data[start : start + WIDTH], WIDTH, False, WHITE))
    return cls


Icons = _build_image_namespace(ICON_NAMES, ICONS)
Arrows = _build_image_namespace(ARROW_NAMES, ARROWS)


def create_image(
    pattern_str: str,
    color: tuple[int, int, int] | dict[str, tuple[int, int, int]] = WHITE,
) -> Image:
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


def create_big_image(
    pattern_str: str,
    color: tuple[int, int, int] | dict[str, tuple[int, int, int]] = WHITE,
) -> Image:
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

    def __init__(self) -> None:
        self._seq = 0

    # -- Cancellation token --------------------------------------------------

    def _acquire(self) -> int:
        """Start a new display-operation generation.

        Increments the sequence counter and returns the new value as a
        cancellation token. Any Tier 2 animation that captured an earlier
        token before this call will see ``_is_cancelled(its_token)`` become
        True on its next check, and should return early. Called internally
        by every display-mutating method.
        """
        self._seq += 1
        return self._seq

    def _is_cancelled(self, token: int) -> bool:
        """True if a display operation newer than ``token`` has started.

        Tier 2 animations check this between frames -- on both sides of an
        ``await`` -- and return early when it becomes True.
        """
        return self._seq != token

    # -- Tier 1: Synchronous rendering primitives ----------------------------

    def render_pattern(
        self,
        pattern: str,
        color: tuple[int, int, int] | dict[str, tuple[int, int, int]] = WHITE,
    ) -> None:
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

    def render_icon(self, icon: Image, color: tuple[int, int, int] = WHITE) -> None:
        """Render an icon ``Image`` (e.g. ``Icons.HEART``) to the LEDs.

        ``color`` is the mono render color and always overrides the icon's
        stored color -- the icon is effectively a reusable bitmap shape.
        """
        self._acquire()
        _render_colmajor(icon._data, 0, color)

    def render_arrow(self, arrow: Image, color: tuple[int, int, int] = WHITE) -> None:
        """Render an arrow ``Image`` (e.g. ``Arrows.NORTH``) to the LEDs.

        ``color`` is the mono render color and always overrides the arrow's
        stored color.
        """
        self._acquire()
        _render_colmajor(arrow._data, 0, color)

    def clear_screen(self) -> None:
        """Turn off all pixels. Cancels any ongoing animation."""
        self._acquire()
        _pixels.fill(OFF)
        _pixels.show()

    def clear(self) -> None:
        """Alias for clear_screen()."""
        self.clear_screen()

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int] = WHITE) -> None:
        """Set one pixel and update the display. Cancels ongoing animations."""
        self._acquire()
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            _pixels[_LUT[x * HEIGHT + y]] = color
            _pixels.show()

    def fill(self, color: tuple[int, int, int] = WHITE) -> None:
        """Fill all pixels. Cancels ongoing animations."""
        self._acquire()
        _pixels.fill(color)
        _pixels.show()

    def get_pixel(self, x: int, y: int) -> tuple[int, int, int]:
        """Read the buffered pixel color at (x, y). Read-only; does not cancel ongoing animations."""
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            return _pixels[_LUT[x * HEIGHT + y]]
        return OFF

    @staticmethod
    def set_brightness(value: float) -> None:
        """Adjust global brightness (0.0-1.0). Does not cancel animations."""
        _pixels.brightness = value
        _pixels.show()

    @staticmethod
    def set_rotation(degrees: int) -> None:
        """Rebuild coordinate LUT for 0/90/180/270 clockwise rotation. Does not cancel animations.

        ``degrees`` must be one of ``0``, ``90``, ``180``, ``270`` or their counter-clockwise equivalents
        ``-270``, ``-180``, ``-90``. Other values raise ``ValueError``. Out-of-range inputs (``360``,
        ``-360``, ...) are rejected; normalise at the call site (e.g. ``set_rotation(d % 360)``) if wrap-around
        is needed.
        """
        # Mutate in place so any module reading _LUT sees the new mapping
        # without needing to re-import. Passing dest=_LUT writes the new table
        # directly into the live buffer -- no fresh bytearray + slice-copy.
        build_lut(degrees, dest=_LUT)

    # -- Lifecycle -----------------------------------------------------------

    def deinit(self) -> None:
        """Release the NeoPixel hardware (PIO state machine + data pin).

        Cancels any ongoing animation, then deinitializes the underlying
        NeoPixel buffer. After this call the ``display`` singleton is unusable
        -- any further render call raises. There is no re-init path; this is a
        teardown hook for code that wants to free the data pin / PIO for other
        use (e.g. before a soft reboot, or to hand the pin to a different
        peripheral). See ``lib/display/README.md`` for why this library exposes
        a single module-level ``display`` instead of supporting multiple
        ``Display`` instances.
        """
        self._acquire()
        _pixels.deinit()

    # -- Tier 2: Async MakeCode-compatible methods ---------------------------

    async def show_leds(
        self,
        pattern: str,
        color: tuple[int, int, int] | dict[str, tuple[int, int, int]] = WHITE,
        interval_ms: int = 0,
    ) -> None:
        """Render a pattern, then hold for interval_ms milliseconds (0 = return after render).

        color: RGB tuple (mono '#'/'.' mode) or dict (palette).
        """
        self.render_pattern(pattern, color)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def show_icon(self, icon: Image, color: tuple[int, int, int] = WHITE, interval_ms: int = 0) -> None:
        """Render an icon ``Image`` (e.g. ``Icons.HEART``), hold for interval_ms milliseconds."""
        self.render_icon(icon, color)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def show_arrow(self, arrow: Image, color: tuple[int, int, int] = WHITE, interval_ms: int = 0) -> None:
        """Render an arrow ``Image`` (e.g. ``Arrows.NORTH``), hold for interval_ms milliseconds."""
        self.render_arrow(arrow, color)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)

    async def show_string(
        self,
        text: str,
        color: tuple[int, int, int] = WHITE,
        interval_ms: int = 150,
        loop: bool = False,
    ) -> None:
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

    async def show_number(
        self,
        n: int,
        color: tuple[int, int, int] = WHITE,
        interval_ms: int = 150,
        loop: bool = False,
    ) -> None:
        """Display a number via ``show_string(str(n))``.

        Fit-on-screen numbers (total glyph width <= WIDTH -- typically
        one digit in the bundled monospace font) are centered and held;
        longer numbers scroll. See ``show_string`` for the full behavior
        including ``loop=True``.
        """
        await self.show_string(str(n), color, interval_ms, loop)

    async def pause(self, ms: int) -> None:
        """Cancellable async sleep for ms milliseconds."""
        self._acquire()
        await asyncio.sleep(ms / 1000)

    @staticmethod
    def forever(callback: Callable[[], object]) -> None:
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

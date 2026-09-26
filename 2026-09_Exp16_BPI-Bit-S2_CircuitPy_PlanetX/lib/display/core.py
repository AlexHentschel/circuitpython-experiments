"""
Runtime display engine for the 5x5 WS2812 NeoPixel matrix (BPI-Bit-S2).

Owns the live NeoPixel buffer, the coordinate Look-Up Table [LUT] (populated via
``geometry.build_lut``), the MakeCode-style 5×5 font (sibling
``font_makecode_5/`` spaced table, laid out by ``text_layout``), and the
``Display``, ``Image``, and ``Icon`` classes.

Two-tier API:
  Tier 1 (sync):  render_pattern, render_icon, render_arrow, clear_screen,
                   set_pixel, fill, set_rotation, set_brightness, get_pixel.
  Tier 2 (async): show_pattern, show_icon, show_arrow, show_image, scroll_image,
                   show_string, show_number, pause.  Require ``await`` from
                   asyncio code.
  Lifecycle:      deinit — releases the data pin / RMT peripheral; the module-level
                   ``display`` instance is unusable afterwards (no re-init path).

Cancellation policy: any display-mutating method cancels an in-progress
Tier 2 animation, and starting a new Tier 2 animation cancels any earlier
one. The exceptions are ``get_pixel`` (pure read), ``set_brightness``, and
``set_rotation`` — deliberately non-cancelling so a running animation is
not disturbed when the user dims the matrix or rotates the frame. Every
Tier 2 method returns a ``Token``; check ``token.is_expired`` to see
whether a later display operation has since superseded it. Tier 1
methods (and ``deinit``) do not return a token — there is nothing to
await after them, so there is nothing meaningful to have been cancelled.
``set_rotation`` not cancelling is safe by construction (in-place LUT
mutation + every render primitive re-reading ``_LUT`` fresh each frame +
single-threaded cooperative ``asyncio`` giving atomicity) — see
``README.md`` § "Rotation during an in-flight Tier 2 animation" for the
full argument.

Bitmap encoding (used throughout this module): images are stored one column
at a time (not one row at a time). Monochrome icons/arrows (``Icon``), glyphs, and
``Image`` instances are stored as *column-major bytes* — one byte per column,
with bit ``y`` of the byte encoding the pixel at display row ``y`` (bit 0 = top row). A *column byte* is therefore one such byte,
covering one column of up to ``_MAX_HEIGHT_PER_COLUMN_BYTE`` (= 8)
vertically-stacked pixels. Full format specification in ``bitmap_codec.py``
and ``lib/display/README.md § Column-major bytes``.
"""

# PEP 563: defer all annotation evaluation, so PEP 585 subscripts
# (e.g. ``dict[str, tuple[int, int, int]]``) and forward references work
# uniformly without per-annotation string-quoting and incur zero on-device
# evaluation cost. Required for this file because the typing-guarded
# ``Callable`` import below is unbound at runtime on device.
from __future__ import annotations

# Type hints only — not loaded at runtime on device. See:
# https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/typing-information
# https://github.com/adafruit/Adafruit_CircuitPython_NTP/issues/18
try:
    from typing import Callable
except ImportError:
    pass

import asyncio
import board
import neopixel
from rainbowio import colorwheel  # noqa: F401 — re-export for user convenience

from ._constants import WIDTH, HEIGHT, NUM_PIXELS, WHITE, OFF
from .geometry import build_lut
from .text_layout import SpacedGlyphColumnFeeder
from .icons import EMOJIS, ARROWS, EMOJI_NAMES, ARROW_NAMES


# ---------------------------------------------------------------------------
# Hardware configuration (kept out of _constants.py so that pure sub-modules
# stay importable on CPython without a device).
# ---------------------------------------------------------------------------
PIXEL_PIN = board.NEOPIXEL
BRIGHTNESS = 0.20

_pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)


def color(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Convenience constructor mirroring Adafruit NeoMatrix's matrix.Color()."""
    return (r, g, b)


# ---------------------------------------------------------------------------
# Coordinate LUT — mutated in-place on rotation so references stay valid.
# ---------------------------------------------------------------------------
_LUT = build_lut(0)


# ---------------------------------------------------------------------------
# Runtime pattern parsers:
#   - ``_iter_pattern_rows`` for cold path. Used by ``Image.create``,
#     ``Icon.create``. Lenient: collapses *all* Python whitespace via
#     ``"".join(raw.split())`` (matches the design-time idiom in
#     ``bitmap_codec.pattern_to_colmajor``). Allocations are not
#     performance-critical here.
#   - ``_write_pattern_on_the_fly`` for hot path. Used by ``Display.render_pattern``.
#     One scan of the source string; skips space / tab / CR; writes cells
#     directly to the NeoPixel buffer.
# For strict design-time pattern validation, use
# ``bitmap_codec.pattern_to_colmajor`` (raises on shape and unknown-cell
# errors instead of silently dropping or padding).
# ---------------------------------------------------------------------------


def _iter_pattern_rows(pattern_str: str):
    """Yield normalized non-blank rows from a pattern — *cold-path* parser.

    Each emitted string has all Python whitespace (spaces, tabs, CRs, FFs,
    VTs) collapsed via ``"".join(raw.split())``, mirroring the design-time
    idiom in ``bitmap_codec.pattern_to_colmajor``. Blank lines (any amount
    of whitespace) are skipped.

    Cold-path callers: ``Image.create``, ``Icon.create``.
    Per-frame render uses ``_write_pattern_on_the_fly``.
    """
    for raw in pattern_str.split("\n"):
        row = "".join(raw.split())
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
    """Fused hot-path used by ``render_pattern``: one scan of the pattern string.

    Scan the source string once, skip only space / tab / CR, write each cell
    directly to the NeoPixel buffer, ignore columns past ``width``, ignore
    rows past ``height``, pad short / missing rows with ``off``. No per-row
    string allocation and no generator.

    Does NOT call ``pixels.show()`` — caller is responsible for flushing
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
        # reaching the following code lines means that we have parsed less than height
        # rows with non-whitespace characters, up to and including the tailing newline.
        # (Otherwise check `if y >= height` above would have returned).
        # EDGE case: the pattern's last row has no trailing newline

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
        # reaching the following code lines means that we have parsed less than height
        # rows with non-whitespace characters, up to and including the tailing newline.
        # (Otherwise check `if y >= height` above would have returned).
        # EDGE case: the pattern's last row has no trailing newline

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
    # Cache module-globals into function-locals: LOAD_FAST (frame-slot access) is cheaper than LOAD_GLOBAL (module-dict lookup). This is explained in
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
    # `_LUT` is read fresh on every call (not cached once per animation): this
    # is one of the three facts (alongside set_rotation's in-place mutation and
    # asyncio's cooperative scheduling) that make rotating mid-scroll safe.
    # See README.md § "Rotation during an in-flight Tier 2 animation".
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


# ---------------------------------------------------------------------------
# Image class
#
# Implementation note: ``Image`` methods reference module globals (``display``,
# ``_LUT``, ``_pixels``) directly — tight coupling accepted for a single-display
# MCU library.
# ---------------------------------------------------------------------------
class Image:
    """Bitmap image for the LED matrix.

    An image is always ``HEIGHT`` rows tall (see ``height``). Its width (see
    ``width``) is independent of the display and may be smaller, equal to,
    or **larger** than the ``WIDTH`` physical columns of the LED matrix —
    ``create`` accepts any width (the widest kept row). There is no
    dedicated strict-shape constructor; check properties ``.width``/``.height``
    yourself (e.g. ``if img.width != WIDTH: raise ...``) in the rare cases
    where you need to enforce an exact size.
    An image can be monochrome (one shared color, recolorable via ``recolor``)
    or multi-color (a fixed color per pixel).
    An image wider than the display is shown a ``WIDTH``-column window at a
    time: ``Display.show_image(offset)`` picks the window and
    ``Display.scroll_image`` scrolls it across the full width — image
    columns outside that window are trimmed.
    Where the display window overhangs the image (a narrower image, or an ``offset``
    past an edge), the uncovered display columns render as ``OFF``.

    Internally (see ``columns``): monochrome images store column-major bytes
    plus one RGB color; multi-color images store a flat per-pixel RGB sequence.
    """

    __slots__ = ("_data", "_width", "_multi", "_color")

    def __init__(
        self,
        data: bytes | tuple,
        width: int,
        multi: bool,
        color: tuple[int, int, int] | None,
    ) -> None:
        """Build an image from already-encoded pixels.

        Usage outside of this module is discouraged, because this method applies no checks!
        Please call ``Image.create(…)`` to instantiate an ``Image``.
        Input ``width`` is this image's column count (independent of the LED
        matrix). Input ``multi`` is True for an individual color per pixel, False for
        one shared mono color for all pixels (``color``).
        """
        self._data = data
        self._width = width
        self._multi = multi
        self._color = color

    @staticmethod
    def create(
        pattern_str: str,
        color: dict[str, tuple[int, int, int]] | tuple[int, int, int] = WHITE,
    ) -> Image:
        """Parse a pattern string into an Image.

        color: RGB tuple (mono) or dict {char: RGB} (multi-color).
        The returned Image is reusable across multiple ``Display.show_image``
        / ``Display.scroll_image`` calls.

        Rows past ``HEIGHT`` are dropped; short rows are padded with OFF.
        Image width is the widest of the kept rows. Unknown chars in mono
        mode render as OFF. Whitespace (spaces, tabs, CRs) in the pattern
        is ignored. For strict size validation, check the returned
        ``.width``/``.height`` yourself.
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
        """Column count of this image, not the physical display width.

        May be smaller, equal to, or larger than ``WIDTH``. Factory method ``create``
        sets the Image width to the widest row on the LED matrix (ignoring rows overflowing ``HEIGHT``). Read-only.
        """
        return self._width

    @property
    def height(self) -> int:
        """Row count of this image — always ``HEIGHT``. Read-only.

        Not stored per-instance (every ``Image`` is exactly ``HEIGHT`` rows
        tall by construction); exists alongside ``width`` so callers can
        validate an image's exact shape themselves — e.g.
        ``if img.width != WIDTH or img.height != HEIGHT: raise ValueError(...)``
        — without a dedicated strict-shape constructor.
        """
        return HEIGHT

    @property
    def columns(self) -> bytes | tuple:
        """Raw backing data: column-major ``bytes`` (mono) or a flat per-pixel RGB-tuple sequence (multi-color).

        Intended for composability (e.g. combining two same-width mono
        ``Image``s column-by-column). Read-only: mutate via ``recolor`` (mono
        color only), or get an independent copy via ``clone()``.
        """
        return self._data

    def recolor(self, new_color: tuple[int, int, int]) -> None:
        """Change a mono Image's display color in place. No-op for multi-color.

        In-place mutation: recoloring a shared ``Image`` (e.g. one built once
        at module scope and reused across calls, like a scrollable
        big image built via ``create``) changes it for every caller
        (and across coroutines). Call ``clone()`` first if you need an Image
        instance whose color can be changed independently without affecting the original.

        ``Icon`` (``Emojis.*`` / ``Arrows.*``) has no color field at all and
        no ``recolor`` — pass ``color`` to ``render_icon``/``show_icon``
        instead. This method only exists on ``Image``.
        """
        if not self._multi:
            self._color = new_color

    def clone(self) -> Image:
        """Return an independent copy of this Image.

        Safe to share the backing data as-is rather than deep-copying it:
        ``_data`` is either ``bytes`` (mono) or a ``tuple`` of RGB tuples
        (multi-color) — both immutable, and nothing in this class ever
        mutates them in place (only ``recolor`` mutates state, and it only
        touches ``_color``, a separate field). So the clone is a new
        instance with its own ``_color``, sharing the same ``_data``.

        Calling ``recolor()`` on the clone (or on the original) afterward
        affects only that instance — this is the direct way to get an
        independent color for an ``Image`` you already have (e.g. one built
        once at module scope and reused, like a scrollable big image)
        without re-parsing its original pattern string through
        ``create`` again.
        """
        return Image(self._data, self._width, self._multi, self._color)

    async def _show_image(self, offset: int = 0, interval_ms: int = 0) -> Token:
        """Internal implementation backing ``Display.show_image``.

        Show a ``WIDTH``-column window of this image, then wait before returning.
        ``offset`` is the image column placed at display column 0. It may
        be negative or past the right edge; uncovered display columns are
        ``OFF``. Waits ``interval_ms`` milliseconds before returning
        (0 = return after render). Cancels any prior Tier 2 animation.
        """
        token = display._acquire()
        self._render_window(offset)
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)
        return token

    async def _scroll_image(self, step: int = 1, interval_ms: int = 200) -> Token:
        """Internal implementation backing ``Display.scroll_image``.

        Scroll through the image, advancing `step` columns per frame, with `interval_ms` milliseconds between frames.

        `step` is a per-frame *incremental* movement of the columns.
        The scroll always starts at position 0; there is no parameter to
        change the starting position (unlike ``Display.show_image``, which
        can start anywhere, including negative or past the image's right edge).

        Cancellable: any newer display operation causes this coroutine to
        return early (see module docstring's cancellation policy).

        Raises ``ValueError`` if ``step <= 0``. Reverse scrolling (negative
        ``step``) is not yet supported.
        """
        if step <= 0:
            # TODO: allow step < 0 for bi-directional (right-to-left) scrolling.
            raise ValueError(f"step must be > 0, got {step}")
        token = display._acquire()
        max_start = self._width - WIDTH
        max_start = max(max_start, 0)
        pos = 0
        interval_seconds = interval_ms / 1000
        while pos <= max_start:
            if token.is_expired:
                return token
            self._render_window(pos)
            await asyncio.sleep(interval_seconds)
            pos += step
        # pos increased until it *overshoots* max_start. There are two cases:
        #  (i)  `max_start` *is* an integer multiple of `step`. In this case, the last loop iteration runs with `pos == max_start`.
        #       Then, the while loop exits with `pos == max_start + step`.
        #  (ii) `max_start` is *not* an integer multiple of `step`. In this case, the last full loop iteration will have `pos < max_start`.
        #       Then, the while loop exits with `pos < max_start + step`.
        if pos != max_start + step:  # The following happens if `max_start` is *not* an integer multiple of `step`
            # Note: doing this check after the loop avoids computing `max_start % step` up front
            self._render_window(pos)
        return token

    def _render_window(self, offset: int) -> None:
        """Render a WIDTH-column window of this image at ``offset`` into ``_pixels`` and show().

        ``offset`` is the image column shown at display column 0. The image width is independent of the display: it may exceed ``WIDTH``
        (e.g. a 16-pixel-wide image, scrolled via ``Display.scroll_image``) or be narrower. Only the window columns
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
          either term in ``min(WIDTH, width - _offset) = x_max``, i.e. ``x_min ≤ x_max``.

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
        # `_LUT` is read fresh on every call (not cached once per animation) -- this is
        # what lets `set_rotation` change a `Display.scroll_image` and `Display.show_image`
        # animation's orientation mid-flight without corrupting it. See
        # README.md § "Rotation during an in-flight Tier 2 animation".
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
        # [x_max, WIDTH), so a single accumulator stays in sync across them:
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
# Icon class
#
# A WIDTH x HEIGHT monochrome bitmap shape; by convention always the same dimension as LED
# matrix. Icon doesn't carry a color value; instead the color is provided as a render-time
# argument.
#
# Deliberately not an ``Image`` subclass: ``Image`` carries ``_width`` /
# ``_multi`` / ``_color`` slots and a ``recolor`` method that would all be
# either dead weight or actively misleading on a type whose entire point is
# "no color, fixed size."
# ---------------------------------------------------------------------------
class Icon:
    """A WIDTH x HEIGHT monochrome bitmap shape (e.g. ``Emojis.HEART``, ``Arrows.NORTH``).

    Carries no color of its own — always rendered with a caller-supplied
    ``color`` (see methods ``render_icon`` / ``show_icon`` / ``render_arrow`` / ``show_arrow``).
    Build one from a pattern via ``Icon.create``.
    """

    __slots__ = ("_data",)

    def __init__(self, data: bytes) -> None:
        """Build an Icon from already-encoded column-major bytes.

        Usage outside of this module is discouraged, because this method applies no checks!
        Please call ``Icon.create(…)`` to instantiate an ``Icon``.
        """
        self._data = data

    @property
    def columns(self) -> bytes:
        """Raw backing data: WIDTH column-major bytes. Read-only."""
        return self._data

    @staticmethod
    def create(pattern_str: str) -> Icon:
        """Create an ``Icon``, up to ``WIDTH`` columns by ``HEIGHT`` rows, from a ``#``/``.`` pattern string.

        Mono only, and no ``color`` parameter — an ``Icon`` carries no color;
        pass ``color`` at render time (``render_icon`` / ``show_icon``).

        Smaller patterns are accepted: missing rows/columns pad as ``OFF``
        (bottom/right, since row 0 = top and column 0 = left). Raises
        ``ValueError`` if the pattern *exceeds* ``WIDTH`` columns or
        ``HEIGHT`` rows (whitespace and blank lines ignored). For a
        multi-color bitmap, or one wider than ``WIDTH`` (e.g. a scrollable
        image), use ``Image.create`` instead.
        """
        # Dedicated mono-only parse: an Icon has no color and a fixed WIDTH,
        # so (unlike Image.create) there is no color-shape branch and
        # no variable-width bookkeeping. It is verified on the fly, that ``len(row)``
        # does not exceed ``WIDTH``. We error immediately on the first over-wide
        # row rather than pre-validating every row's length up front.
        rows = list(_iter_pattern_rows(pattern_str))
        row_count = len(rows)
        if row_count > HEIGHT:
            raise ValueError(f"Icon.create requires at most {HEIGHT} rows x {WIDTH} columns; got {row_count} rows")

        cols = bytearray(WIDTH)
        for y in range(row_count):
            row = rows[y]
            row_len = len(row)
            if row_len > WIDTH:
                raise ValueError(f"Icon.create requires at most {HEIGHT} rows x {WIDTH} columns; got {row_count} rows x {len(row)} columns")
            for x in range(row_len):
                if row[x] == "#":
                    cols[x] |= 1 << y
        return Icon(bytes(cols))


# ---------------------------------------------------------------------------
# Emojis / Arrows — Icon instances constructed once at import from the bulk
# ``EMOJIS`` / ``ARROWS`` bytes; names/ordering come from ``EMOJI_NAMES`` /
# ``ARROW_NAMES`` in ``icons.py`` (single source of truth). ``bytes``
# slicing copies, so each Icon owns its own WIDTH-byte backing block;
# the bulk arrays exist for deterministic ordering, not byte-sharing.
# ---------------------------------------------------------------------------
def _build_icon_namespace(names: tuple[str, ...], data: bytes) -> type:
    """Populate a bare class with Icon instances indexed by name order."""
    cls = type("_IconNamespace", (), {})
    for i, name in enumerate(names):
        start = i * WIDTH
        setattr(cls, name, Icon(data[start : start + WIDTH]))
    return cls


Emojis = _build_icon_namespace(EMOJI_NAMES, EMOJIS)
Arrows = _build_icon_namespace(ARROW_NAMES, ARROWS)


# ---------------------------------------------------------------------------
# Cancellation token
# ---------------------------------------------------------------------------
class Token:
    """A display-operation generation marker, returned by every mutating call.

    ``is_expired`` starts False and is set True exactly once — by a later
    ``Display._acquire()`` call — at the moment this generation is
    superseded. Self-contained: no back-reference to ``Display``, no
    sequence-number comparison to recompute; check the flag directly.
    """

    __slots__ = ("_is_expired",)

    def __init__(self) -> None:
        # Read-only from outside this module: ``is_expired`` is a property
        # backed by ``_is_expired``, so external code can check it but not set
        # it. ``Display._acquire()`` — the only code allowed to expire a token —
        # writes ``_is_expired`` directly (module-internal access, not the
        # public property).
        self._is_expired = False

    @property
    def is_expired(self) -> bool:
        """True once a later ``Display._acquire()`` call has superseded this token."""
        return self._is_expired


# ---------------------------------------------------------------------------
# Display class
# ---------------------------------------------------------------------------
class Display:
    """Controls the 5×5 WS2812 NeoPixel matrix.

    Use the module-level ``display`` instance. Starting any display-mutating
    operation cancels any Tier 2 animation in progress. Non-cancelling
    methods: ``get_pixel``, ``set_brightness``, ``set_rotation``. See the
    module docstring for the full cancellation policy.
    """

    def __init__(self) -> None:
        """Create the matrix controller.

        Use the module-level ``display`` instance; do not construct another.
        A second instance would still drive the same LEDs.
        """
        self._token = Token()

    # — Cancellation token --------------------------------------------------

    def _acquire(self) -> Token:
        """Start a new display-operation generation.

        Expires the previous token (its ``is_expired`` becomes True) and
        creates a new one which is then returned. Any Tier 2 animation
        holding the previous token will see its ``is_expired`` become True
        on its next check, and should return early. Called internally by
        every display-mutating method.
        """
        self._token._is_expired = True  # module-internal write; public side is read-only
        self._token = Token()
        return self._token

    # — Tier 1: Synchronous rendering primitives ----------------------------

    def render_pattern(
        self,
        pattern: str,
        color: tuple[int, int, int] | dict[str, tuple[int, int, int]] = WHITE,
    ) -> None:
        """Parse and render a pattern string directly to LEDs.

        Faster than building an ``Image`` (e.g. via ``Image.create``)
        for one-shot display since it avoids building a persistent bitmap
        (one parse pass, immediate pixel writes).

        color: RGB tuple for mono ('#'/'.' mode) or dict for palette.
        Short rows are padded with OFF; rows past HEIGHT are ignored.
        """
        self._acquire()
        # Direct render via LUT — no intermediate column-major buffer.
        # Fused one-pass scan. Locals here are LOAD_FAST args into the helper;
        # rationale (vs LOAD_GLOBAL) is documented on ``_render_colmajor``.
        pixels = _pixels
        lut = _LUT
        off = OFF
        _write_pattern_on_the_fly(pattern, color, pixels, lut, off, WIDTH, HEIGHT)
        pixels.show()

    def render_icon(self, icon: Icon, color: tuple[int, int, int] = WHITE) -> None:
        """Render an ``Icon`` (e.g. ``Emojis.HEART``) to the LEDs.

        ``color`` is the render color — an ``Icon`` carries no color of its
        own, so ``color`` is not an override of anything, just the color.
        """
        self._acquire()
        _render_colmajor(icon.columns, 0, color)

    def render_arrow(self, arrow: Icon, color: tuple[int, int, int] = WHITE) -> None:
        """Render an ``Icon`` from the arrow catalog (e.g. ``Arrows.NORTH``) to the LEDs.

        Alias of ``render_icon``, kept as a separate public method name.
        """
        self.render_icon(arrow, color)

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
        """Set clockwise rotation to 0/90/180/270 degrees. Does not cancel animations.

        ``degrees`` must be one of ``0``, ``90``, ``180``, ``270`` or their counter-clockwise equivalents
        ``-270``, ``-180``, ``-90``. Other values raise ``ValueError``. Out-of-range inputs (``360``,
        ``-360``, ...) are rejected; normalise at the call site (e.g. ``set_rotation(d % 360)``) if wrap-around
        is needed.
        """
        # Mutate in place so any module reading _LUT sees the new mapping
        # without needing to re-import. Passing dest=_LUT writes the new table
        # directly into the live buffer — no fresh bytearray + slice-copy.
        # This in-place mutation (plus render primitives re-reading _LUT fresh
        # each frame, plus asyncio's cooperative single-threaded scheduling) is
        # exactly what makes this method safe to call while a Tier 2 animation
        # is running, despite deliberately not cancelling it. See README.md §
        # "Rotation during an in-flight Tier 2 animation" for the full argument.
        build_lut(degrees, dest=_LUT)

    # — Lifecycle -----------------------------------------------------------

    def deinit(self) -> None:
        """Release the NeoPixel hardware (RMT peripheral + data pin).

        Cancels any ongoing animation, then deinitializes the underlying
        NeoPixel buffer. After this call the ``display`` singleton is unusable
        — any further render call raises. There is no re-init path; this is a
        teardown hook for code that wants to free the data pin / RMT peripheral for other
        use (e.g. before a soft reboot, or to hand the pin to a different
        peripheral). See ``lib/display/README.md`` for why this library exposes
        a single module-level ``display`` instead of supporting multiple
        ``Display`` instances.
        """
        self._acquire()
        _pixels.deinit()

    # — Tier 2: Async MakeCode-compatible methods ---------------------------

    async def show_pattern(
        self,
        pattern: str,
        color: tuple[int, int, int] | dict[str, tuple[int, int, int]] = WHITE,
        interval_ms: int = 0,
    ) -> Token:
        """Render a pattern, then wait ``interval_ms`` milliseconds before returning (0 = return after render).

        color: RGB tuple (mono '#'/'.' mode) or dict (palette).

        Raises ``ValueError`` if ``interval_ms < 0``.
        Returns the cancellation ``Token`` (check ``token.is_expired`` to see
        whether a later display operation preempted the wait).
        """
        if interval_ms < 0:
            raise ValueError(f"interval_ms must be >= 0, got {interval_ms}")
        self.render_pattern(pattern, color)
        token = self._token  # render_pattern's internal _acquire() just minted this
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)
        return token

    async def show_icon(self, icon: Icon, color: tuple[int, int, int] = WHITE, interval_ms: int = 0) -> Token:
        """Render an ``Icon`` (e.g. ``Emojis.HEART``), then wait ``interval_ms`` milliseconds before returning.

        Raises ``ValueError`` if ``interval_ms < 0``.
        Returns the cancellation ``Token`` (check ``token.is_expired`` to see
        whether a later display operation preempted the wait).
        """
        if interval_ms < 0:
            raise ValueError(f"interval_ms must be >= 0, got {interval_ms}")
        self.render_icon(icon, color)
        token = self._token  # render_icon's internal _acquire() just minted this
        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)
        return token

    async def show_arrow(self, arrow: Icon, color: tuple[int, int, int] = WHITE, interval_ms: int = 0) -> Token:
        """Render an ``Icon`` from the arrow catalog (e.g. ``Arrows.NORTH``), then wait ``interval_ms`` milliseconds before returning.
        Raises ``ValueError`` if ``interval_ms < 0``.
        """
        # functionally this method is alias of ``show_icon``, kept as a separate public method name.
        return await self.show_icon(arrow, color=color, interval_ms=interval_ms)

    async def show_image(self, img: Image, offset: int = 0, interval_ms: int = 0) -> Token:
        """Show a ``WIDTH``-column window of ``img``, then wait before returning.

        ``offset`` is the image column placed at display column 0. It may be negative
        or positive and may push the image partially or fully out of the display area.
        Display columns ouside the Image are ``OFF``. Waits ``interval_ms`` milliseconds
        before returning (0 = return after render). Cancels any prior Tier 2 animation.
        """
        return await img._show_image(offset, interval_ms)

    async def scroll_image(self, img: Image, step: int = 1, interval_ms: int = 200) -> Token:
        """Scroll through ``img``, advancing ``step`` columns per frame, with ``interval_ms`` milliseconds between frames.

        ``step`` is a per-frame *incremental* movement of the columns. The
        scroll always starts at position 0; there is no parameter to change
        the starting position (unlike ``show_image``, which can start
        anywhere, including negative or past the image's right edge).

        Cancellable: any newer display operation causes this coroutine to
        return early (see module docstring's cancellation policy).

        Raises ``ValueError`` if ``step <= 0``. Reverse scrolling (negative
        ``step``) is not yet supported.
        """
        return await img._scroll_image(step, interval_ms)

    async def show_string(
        self,
        text: str,
        color: tuple[int, int, int] = WHITE,
        interval_ms: int = 150,
        loop: bool = False,
    ) -> Token:
        """Scroll text across the display.

        The typical case where text is wider than ``WIDTH`` glyph-columns:
        we scroll one column every ``interval_ms`` time step. A one-column
        blank sits between characters, so adjacent glyphs do not merge.

        A non-looping scroll ends exactly when the last meaningful column
        has left the screen: the display is left fully blank (not paused
        mid-scroll with a character still partially visible).

        Fit-on-screen text (total glyph-column width <= WIDTH) has
        nothing to scroll, so it's centered and held in place instead.
        The hold duration is a fixed ``interval_ms * 5`` (five step-
        durations, using the same per-column time unit the scrolling case
        above steps by; not a value derived from ``WIDTH`` or from how
        long an equivalent scroll would take) when ``interval_ms > 0``,
        indefinite when ``loop=True``, or immediate (render-and-return)
        when ``interval_ms == 0`` and ``loop=False`` (the short-text
        counterpart to ``show_pattern(pattern, interval_ms=0)``). The ``5``
        is an arbitrary "long enough to read" choice, unchanged since
        this method's first draft; it is not a tuned or derived constant.

        loop: if True, keep scrolling indefinitely (or, for fit-on-screen
        text, hold indefinitely) until cancelled by another display
        operation. On the short-text hold path, cancellation is polled
        every ``interval_ms`` ms (or every 50 ms when ``interval_ms == 0``).

        Raises ``ValueError`` if ``interval_ms < 0``: a negative delay has
        no sensible meaning here (see the class discussion of cold-call-
        site validation in ``CODING_PRINCIPLES.md``).
        Returns the cancellation ``Token`` (check ``token.is_expired`` to see
        whether a later display operation preempted this call).
        """
        if interval_ms < 0:
            raise ValueError(f"interval_ms must be >= 0, got {interval_ms}")
        token = self._acquire()
        text = str(text)
        if not text:
            return token
        sleep_s = interval_ms / 1000

        # Probe with the same feeder the scroll path uses, so spacer / tofu /
        # space-width rules cannot drift between "fits?" and the actual render.
        probe = SpacedGlyphColumnFeeder(text)
        fit_buf = bytearray()
        while True:
            col = probe.next_column()
            if col is None:
                break
            fit_buf.append(col)
            if len(fit_buf) > WIDTH:
                break

        # Fit-on-screen path: text is no wider than WIDTH glyph-columns, so there's nothing
        # to scroll. Center text once and hold: indefinitely iff `loop == true`. For `loop ==
        # false`, we hold for a fixed `interval_ms * 5` duration when `interval_ms > 0`, or
        # return immediately when `interval_ms == 0` (i.e. skipping the sleep entirely, not
        # sleeping for 0 ms, because `asyncio.sleep(0)` yields to the event loop once, so
        # skipping the call is needed for a true immediate return).
        if len(fit_buf) <= WIDTH:
            pad = (WIDTH - len(fit_buf)) // 2
            padded = bytearray(WIDTH)
            for i in range(len(fit_buf)):
                padded[pad + i] = fit_buf[i]
            if token.is_expired:
                return token
            _render_colmajor(padded, 0, color)
            if loop:
                poll_s = sleep_s if interval_ms > 0 else 0.05
                while True:
                    if token.is_expired:
                        return token
                    await asyncio.sleep(poll_s)
            if interval_ms > 0:
                await asyncio.sleep(interval_ms * 5 / 1000)
            return token

        while True:
            # Scroll loop memory: rather than materialising the whole scrolled
            # bitmap, columns are fed one at a time from `feeder` into a
            # WIDTH-byte ring buffer. The visible window is exactly WIDTH
            # columns, so a ring that size is sufficient regardless of how
            # long `text` is: each newly arriving column overwrites the slot
            # that just scrolled off the left edge. The initial all-zero ring
            # is the scroll-in padding, so the first frame renders as a fully
            # blank display with the first column arriving from the right,
            # rather than jumping straight to a partially-filled window.
            feeder = SpacedGlyphColumnFeeder(text)
            ring = bytearray(WIDTH)
            read_head = 0
            trailing_blanks = 0
            while True:
                if token.is_expired:
                    return token
                _render_ring_window(ring, read_head, color)
                await asyncio.sleep(sleep_s)
                if token.is_expired:
                    return token
                col = feeder.next_column()
                if col is None:
                    col = 0  # empty column
                    trailing_blanks += 1
                ring[read_head] = col
                read_head += 1
                if read_head == WIDTH:
                    read_head = 0
                # Scroll-out: once the feeder drains, keep feeding blank columns
                # until WIDTH + 1 of them have gone by. `> WIDTH` (not `>=`) so the
                # final fully-blank frame is actually rendered; with `>=` the loop
                # would break while the last meaningful column is still at x=0,
                # leaving the caller's docstring-promised "ends fully blank"
                # contract unmet.
                if trailing_blanks > WIDTH:
                    break
            if not loop:
                return token

    async def show_number(
        self,
        n: int,
        color: tuple[int, int, int] = WHITE,
        interval_ms: int = 150,
        loop: bool = False,
    ) -> Token:
        """Display a number via ``show_string(str(n))``.

        Fit-on-screen numbers (total glyph width <= WIDTH — typically
        one digit in the bundled font) are centered and held;
        longer numbers scroll. See ``show_string`` for the full behavior
        including ``loop=True``.
        """
        return await self.show_string(str(n), color, interval_ms, loop)

    async def pause(self, ms: int) -> Token:
        """Cancellable async sleep for ms milliseconds.

        Raises ``ValueError`` if ``ms < 0``.
        Returns the cancellation ``Token`` (check ``token.is_expired`` to see
        whether a later display operation preempted this wait).
        """
        if ms < 0:
            raise ValueError(f"ms must be >= 0, got {ms}")
        token = self._acquire()
        await asyncio.sleep(ms / 1000)
        return token

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


# Singleton — ``from display import display``
display = Display()

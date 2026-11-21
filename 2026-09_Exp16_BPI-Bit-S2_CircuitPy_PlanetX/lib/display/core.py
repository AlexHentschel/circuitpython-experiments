"""
Runtime display engine for the 5x5 WS2812 NeoPixel matrix (BPI-Bit-S2).

Owns the MakeCode-style 5×5 font (sibling ``font_makecode_5/`` spaced
table, laid out by ``text_layout``), and the ``Display``, ``Image``, and
``Icon`` classes. Each ``Display`` instance owns its own live NeoPixel
buffer and coordinate Look-Up Table [LUT] (populated via
``geometry.build_lut``).

Two-tier API:
  Tier 1 (sync):  render_pattern, render_icon, render_arrow, render_string, render_number,
                   set_pixel, render_filled, set_rotation, set_brightness, get_pixel, clear.
  Tier 2 (async): show_pattern, show_icon, show_arrow, show_image, scroll_image,
                   show_string, show_number, hold, repeat_until_cancelled.  Require ``await`` from
                   asyncio code.
  Lifecycle:      deinit — releases the data pin / RMT peripheral; *this instance*
                   is unusable afterwards (no re-init path on it), but the pin is
                   now free for a newly-constructed ``Display()``.

Cancellation policy:
* any display-mutating method cancels an in-progress Tier 2 animation, and starting a new
  Tier 2 animation cancels any earlier one. The exceptions are ``get_pixel`` (pure read),
  ``set_brightness``, and ``set_rotation``; in other words running animation is not disturbed
  when the user dims the matrix or rotates the frame.
* Consistent with the general rule of in-progress Tier 2 animation being cancelled
  by any display-mutating method, ``set_pixel`` and ``show_string`` also cancel a
  Tier 2 operation:
  - ``set_pixel`` leaves the display on the most recent frame only with the set pixel
    being updated. If the coordinate is outside the LED matrix, the latest frame is
    left unchanged and kept on the display.
  - ``show_string`` scrolls the string across the display, one column at a time, replacing
    whatever was showing. A scroll leaves the screen blank unless it got cancelled (in
    which case the cancelling operation specifies the display's new content). A string
    short enough to fit is drawn from the left and held (no scrolling for convenience of reading),
    and very roughly held for a similar time as if the text was scrolled and thereafter
    cleared. An empty string shows that blank frame. ``loop=True`` keeps scrolling (or
    holding a short string) until another display operation cancels the call.
* Every Tier 2 method returns a ``Token``. ``Token.was_completed`` stays true once the call has run to its own end
  (a later operation taking over the display does not change it). ``Token.is_expired`` becomes true when a later
  display operation takes the display (no matter whether the Token's display operation completed or was cancelled).
  After the ``await`` for a display operation returns, when ``Token.is_expired`` is False, the display is still as
  that operation left it.
* Tier 1 methods (and ``deinit``) do not return a token: there is nothing to
  await after them, so there is nothing meaningful to have been cancelled.

Bitmap encoding (used throughout this module): images are stored one column
at a time (not one row at a time). Monochrome icons/arrows (``Icon``), glyphs, and
``Image`` instances are stored as *column-major bytes* — one byte per column,
with bit ``y`` of the byte encoding the pixel at display row ``y`` (bit 0 = top row).
A *column byte* is therefore one such byte,
covering one column of up to ``_MAX_HEIGHT_PER_COLUMN_BYTE`` (= 8)
vertically-stacked pixels. Full format specification in ``bitmap_codec.py``
and ``lib/display/README.md § Column-major bytes``.
"""

# Maintainer notes
# * On performance numbers: Comments in this file that say "benchmarked" quote the following experimental runs:
#   Hardware and software: BPI-Bit-S2 (ESP32-S2), CircuitPython 10.3.0 (2026-08-31), code compiled to ``.mpy`` with mpy-cross 10.3.0, the 25 onboard
#   WS2812 LEDs at brightness 0.02, 2026-11-16. Medians of 7 rounds on one board. Other ports and firmware may differ.
#   Costs are quoted in µs and as a fraction of one ``show()`` of 25 pixels, which takes 1954 µs. Why ``show()`` is the reference: every displayed frame
#   ends with one ``show()``, and its duration is set by the NeoPixel driver and the LED data rate, not by our code. It is the fixed baseline for
#   updating the display. Therefore, ``show()`` is a good reference frame.

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

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
    from typing import Awaitable, Callable, Iterator, NoReturn, TypeAlias
    from .text_layout import _ColumnReader, _FixedColumnReader

    # One ``(red, green, blue)`` color, each channel 0–255. ``ColorDict`` maps a pattern character to such a color.
    # Defined here, after the ``typing`` import, so that CircuitPython (no ``typing``) never evaluates ``tuple[...]``.
    RGBcolor: TypeAlias = tuple[int, int, int]
    ColorDict: TypeAlias = dict[str, RGBcolor]
except ImportError:
    pass

import asyncio

try:
    from micropython import const
except ImportError:  # host tests; CircuitPython always provides micropython.const

    def const(value):
        return value


import board
from adafruit_ticks import ticks_add, ticks_diff, ticks_ms
import neopixel
from rainbowio import colorwheel  # noqa: F401 — re-export for user convenience

from ._constants import WIDTH, HEIGHT, NUM_PIXELS, WHITE, OFF
from .geometry import build_lut
from .text_layout import ScreenText, _reader_for
from .icons import EMOJIS, ARROWS, EMOJI_NAMES, ARROW_NAMES


# ---------------------------------------------------------------------------
# Hardware configuration (kept out of _constants.py so that pure sub-modules
# stay importable on CPython without a device).
#
# ``PIXEL_PIN`` / ``BRIGHTNESS`` are pure config, so they stay module-level.
# The NeoPixel buffer and coordinate LUT are tied to a Display instance.
# This is beneficial so that the Display instance can be constructed again after
# an earlier instance's ``deinit()`` freed the pin and NeoPixel buffer.
# ---------------------------------------------------------------------------
PIXEL_PIN = board.NEOPIXEL
BRIGHTNESS = 0.20


def color(r: int, g: int, b: int) -> RGBcolor:
    """Convenience constructor mirroring Adafruit NeoMatrix's matrix.Color()."""
    return (r, g, b)


# ---------------------------------------------------------------------------
# Runtime pattern parsers:
#   - ``_iter_pattern_rows`` for cold path. Used by ``Image(pattern)``,
#     ``Icon(pattern)``. Lenient: collapses *all* Python whitespace via
#     ``"".join(raw.split())`` (matches the design-time idiom in
#     ``bitmap_codec.pattern_to_colmajor``). Allocations are not
#     performance-critical here.
#   - ``Display._write_pattern_on_the_fly`` for hot path. Used by ``Display.render_pattern``.
#     One scan of the source string; skips space / tab / CR; writes cells
#     directly to the NeoPixel buffer.
# For strict design-time pattern validation, use
# ``bitmap_codec.pattern_to_colmajor`` (raises on shape and unknown-cell
# errors instead of silently dropping or padding).
# ---------------------------------------------------------------------------


def _iter_pattern_rows(pattern_str: str) -> Iterator[str]:
    """Yield normalized non-blank rows from a pattern — *cold-path* parser.

    Each emitted string has all Python whitespace (spaces, tabs, CRs, FFs,
    VTs) collapsed via ``"".join(raw.split())``, mirroring the design-time
    idiom in ``bitmap_codec.pattern_to_colmajor``. Blank lines (any amount
    of whitespace) are skipped.

    Cold-path callers: ``Image(pattern)``, ``Icon(pattern)``.
    Per-frame render uses ``Display._write_pattern_on_the_fly``.
    """
    for raw in pattern_str.split("\n"):
        row = "".join(raw.split())
        if row:
            yield row


# ---------------------------------------------------------------------------
# Image class
#
# Implementation note: ``Image._render_window`` takes the acting ``Display``
# instance as an explicit parameter. An ``Image`` has no fixed display of
# its own; it renders to whichever ``Display`` calls it.
# ---------------------------------------------------------------------------
class Image:
    """Bitmap image for the LED matrix.

    An image is always ``HEIGHT`` rows tall (see property ``height``). Its width (see property ``width``) is independent of the
    display and may be smaller, equal to, or **larger** than the ``WIDTH`` physical columns of the LED matrix. ``Image(pattern)``
    accepts any width (the widest kept row). Short rows are padded with OFF. An image can be monochrome (one shared color,
    recolorable via ``recolor``) or multi-color (a fixed color per pixel, ``recolor`` is no-op).

    You can choose an image's horizontal position when you draw it by specifying the LED column ``start_col`` where the image's leftmost
    column goes. Image columns that land outside the matrix are not shown, and LEDs that no image column reaches are off.
    """

    # Implementation notes:
    # Internally (see ``columns``): monochrome images store column-major bytes plus one RGB color; multi-color images store a flat per-pixel RGB sequence.

    __slots__ = ("_data", "_width", "_multi", "_color")

    def __init__(
        self,
        pattern_str: str,
        color: RGBcolor | ColorDict = WHITE,
    ) -> None:
        """Parse a pattern string into an Image.

        If ``color`` is a single RGB tuple ``(red, green, blue)``: the entire image is drawn in that color, with illuminated pixels marked by ``#``.
        If a dictionary ``{character: RGB tuple}`` is given for the input ``color``, then characters such as ``G`` or ``c`` in the pattern stand
        for colors. You set each character's RGB tuple in ``color``, for example ``color["G"] = (0, 255, 0)``. Keep the Image and pass it to
        ``show_image`` or ``scroll_image`` again.

        Rows past ``HEIGHT`` are dropped; short rows or columns are padded with OFF. Image width is the widest row, in pixels (ignoring rows beyond
        ``HEIGHT``). Characters without a specified color render as OFF. Whitespace (spaces, tabs, carriage returns, form feeds, vertical tabs) is
        ignored; it only helps you format ``pattern_str`` readably, so ``# .  #`` displays the same picture as ``#.#``.
        Any other character is interpreted as a pixel.
        """
        # Notes:
        #  * Internal encoding: mono images store column-major bytes (one byte per column, bit y = row y counted from top); multi-color
        #    stores a flat tuple of per-pixel RGB tuples. Conversion happens here so render methods do not re-parse on each call.
        #  * For comparison, ``render_pattern`` skips fewer whitespace characters (only space, tab, and carriage return) than the code below. This
        #    is a deliberate trade-off: when we render pattern strings directly to the display, we prioritize performance and accept that exotic
        #    whitespace characters are not supported. For ``Image``, the use case is to parse once at object creation, so we accept a higher runtime
        #    cost and also support exotic whitespace characters. For performance details, see maintainer note in ``_write_pattern_on_the_fly``.
        rows = list(_iter_pattern_rows(pattern_str))
        height = min(len(rows), HEIGHT)
        img_width = max((len(r) for r in rows[:height]), default=WIDTH)

        if isinstance(color, dict):
            pixels = [OFF] * (img_width * HEIGHT)
            for y in range(height):
                row = rows[y]
                for x in range(min(img_width, len(row))):
                    pixels[x * HEIGHT + y] = color.get(row[x], OFF)
            self._data = tuple(pixels)
            self._multi = True
            self._color = None
        else:
            cols = bytearray(img_width)
            for y in range(height):
                row = rows[y]
                for x in range(min(img_width, len(row))):
                    if row[x] == "#":
                        cols[x] |= 1 << y
            self._data = bytes(cols)
            self._multi = False
            self._color = color
        self._width = img_width

    @classmethod
    def _from_encoded(
        cls,
        data: bytes | tuple[RGBcolor, ...],
        width: int,
        multi: bool,
        color: RGBcolor | None,
    ) -> Image:
        """Build an image from already-encoded pixels. Applies no checks.

        Internal: for ``clone`` and for tests. ``width`` is the column count. ``multi`` is True for
        an individual color per pixel (``data`` is a flat tuple of RGB tuples, ``color`` is None),
        False for one shared mono color (``data`` is column-major bytes, ``color`` is that color).
        Skips ``__init__``, like ``_from_columns`` on ``ScreenText``.
        """
        obj = object.__new__(cls)
        obj._data = data
        obj._width = width
        obj._multi = multi
        obj._color = color
        return obj

    @property
    def width(self) -> int:
        """Column count of this image, not the physical display width. Read-only.

        May be smaller, equal to, or larger than ``WIDTH``. ``Image(pattern)``
        sets ``width`` to the length of the widest row in the pattern.
        """
        return self._width

    @property
    def height(self) -> int:
        """Row count of this image: always display ``HEIGHT``. Read-only.

        If an image is created from pattern that has less rows than the display's ``HEIGHT``,
        ``Image(pattern)`` always pads with OFF to ``HEIGHT`` rows. Equivalently,
        ``Image(pattern)`` truncates an overly tall pattern to ``HEIGHT`` rows.
        """
        return HEIGHT

    def recolor(self, new_color: RGBcolor) -> None:
        """Change a mono Image's display color in place. No-op for multi-color.

        In-place mutation: recoloring a shared ``Image`` (e.g. one built once
        at module scope and reused across calls, like a scrollable
        big image built via ``Image(pattern)``) changes it for every caller
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
        ``Image(pattern)`` again.
        """
        return Image._from_encoded(self._data, self._width, self._multi, self._color)

    def _render_window(self, disp: Display, offset: int) -> None:
        """Render a WIDTH-column window of this image at ``offset`` into ``disp``'s pixel buffer and show().

        ``disp`` is the ``Display`` instance to render to.

        ``offset`` is the image column shown at display column 0. It has the opposite sign of the public ``start_col`` (the display column where the image's
        first column goes): ``render_image(image, start_col)`` calls this with ``offset = -start_col``. In the derivation below, ``x`` is a display column
        (loop variable).

        The image width is independent of the display: it may exceed ``WIDTH``
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

        pixels = disp._pixels
        # `disp._lut` is read fresh on every call (not cached once per animation) -- this is
        # what lets `set_rotation` change a `Display.scroll_image` and `Display.show_image`
        # animation's orientation mid-flight without corrupting it. See
        # README.md § "Rotation during an in-flight Tier 2 animation".
        lut = disp._lut
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
                _write_column(pixels, lut, x_base, data[offset + x], color_on, off)
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
    Build one from a pattern: ``Icon(pattern)``.
    """

    __slots__ = ("_data",)

    def __init__(self, pattern_str: str) -> None:
        """Create an ``Icon`` of ``WIDTH`` columns by ``HEIGHT`` rows, from a pattern string.
        ``#`` is a lit pixel and ``.`` is off. So the row ``#.#`` reads on, off, on.

        The Icon stores no color of its own. Pass the color when you draw it,
        with ``Display.render_icon`` or ``Display.show_icon``.

        Smaller patterns are accepted: missing rows/columns pad as ``OFF``
        (bottom/right, since row 0 = top and column 0 = left).
        Raises ``ValueError`` if the pattern *exceeds* ``WIDTH`` columns or
        ``HEIGHT`` rows (every whitespace character and blank lines ignored).
        For a multi-color bitmap, or one wider than ``WIDTH`` (e.g. a scrollable
        image), use ``Image`` instead.
        """
        # Dedicated mono-only parse: an Icon has no color and a fixed WIDTH,
        # so (unlike Image) there is no color-shape branch and
        # no variable-width bookkeeping. It is verified on the fly, that ``len(row)``
        # does not exceed ``WIDTH``. We error immediately on the first over-wide
        # row rather than pre-validating every row's length up front.
        rows = list(_iter_pattern_rows(pattern_str))
        row_count = len(rows)
        if row_count > HEIGHT:
            raise ValueError(f"Icon requires at most {HEIGHT} rows x {WIDTH} columns; got {row_count} rows")

        cols = bytearray(WIDTH)
        for y in range(row_count):
            row = rows[y]
            row_len = len(row)
            if row_len > WIDTH:
                raise ValueError(f"Icon requires at most {HEIGHT} rows x {WIDTH} columns; got {row_count} rows x {len(row)} columns")
            for x in range(row_len):
                if row[x] == "#":
                    cols[x] |= 1 << y
        self._data = bytes(cols)

    @classmethod
    def _from_columns(cls, data: bytes) -> Icon:
        """Build an Icon from already-encoded column-major bytes. Applies no checks.

        Internal: for ``Emojis`` / ``Arrows`` and for tests. Skips ``__init__``.
        """
        obj = object.__new__(cls)
        obj._data = data
        return obj

    @property
    def _columns(self) -> bytes:
        """Raw backing data: WIDTH column-major bytes. Internal: ``Display`` reads it to draw the icon."""
        return self._data


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
        setattr(cls, name, Icon._from_columns(data[start : start + WIDTH]))
    return cls


Emojis = _build_icon_namespace(EMOJI_NAMES, EMOJIS)
Arrows = _build_icon_namespace(ARROW_NAMES, ARROWS)


# ---------------------------------------------------------------------------
# Cancellation token. The two facts are bits in one small int (``_state``).
# ---------------------------------------------------------------------------
_EXPIRED_MASK = const(1)
_COMPLETED_MASK = const(2)


class Token:
    """Reports two facts about one display operation, such as a ``show_*``, ``scroll_*``, or ``hold`` call.
    ``Token.was_completed`` stays true once the call has run to its own end (a later operation taking over the display
    does not change it). ``Token.is_expired`` becomes true when a later display operation takes the display (no matter
    whether this call completed or was cancelled). After the ``await`` for a display operation returns, when
    ``Token.is_expired`` is False, the display is still as that operation left it.
    You can read ``Token.was_completed`` and ``Token.is_expired``, but not set them.

        token = await display.scroll_string("Hello", blank_edges=False)  # the scroll's last frame stays lit, with the text ending at the right display edge
        if token.was_completed and not token.is_expired:
            display.clear()

    ``clear()`` runs only when the scroll finished and that last frame is still up. Otherwise another display call has already
    overwritten the display, either during the scroll or after it finished.
    """

    # __slots__ = ("_state",)

    # Formally we use the trailing two bits of the integer ``_state`` to encode two boolean values ``COMPLETED`` and ``EXPIRED``;
    # in binary representation:  _state ≡ … 0 0 0 [COMPLETED] [EXPIRED].
    # State machine:
    #  - when a display operation successfully completes, it sets the COMPLETED bit of its own token to True, by calling ``Token._complete_unless_expired``.
    #    This should never happen if the display operation was already cancelled, i.e. the token expired. Therefore, ``_complete_unless_expired`` sets
    #    the COMPLETED bit to True, only if the EXPIRED bit is still clear. (Possible TODO: consider error in case the token is expired).
    #  - ``_acquire`` and the ``_ensure_*_and_acquire`` methods set the EXPIRED bit of the previous token always to True.
    #     (irrespective of whether the previous display operation was completed or not, thereby cancelling it if it is still ongoing).
    _state: int

    def __init__(self) -> None:
        self._state = 0  # COMPLETED = EXPIRED ≡ False

    @property
    def was_completed(self) -> bool:
        """True once the display operation associated with this token has run to its own end. For a cancelled display operation,
        this remains False. Once it is True, a later operation taking over the display does not change it."""
        return (self._state & _COMPLETED_MASK) != 0

    @property
    def is_expired(self) -> bool:
        """True when a later operation has already taken control of the display, no matter whether the token's own operation was completed or
        cancelled. After the ``await`` for a display operation returns, False means the display is still as this call left it."""
        return (self._state & _EXPIRED_MASK) != 0

    def _expire(self) -> None:
        """Set the expired bit. A completed bit that is already set stays set. Idempotent."""
        self._state |= _EXPIRED_MASK

    def _complete_unless_expired(self) -> None:
        """Set the completed bit only when this Token's display operation was not already cancelled. A cancelled call already has the
        expired bit set and must stay ``was_completed`` false. Repeated calls are harmless."""
        if not (self._state & _EXPIRED_MASK):
            self._state |= _COMPLETED_MASK


# ---------------------------------------------------------------------------
# Cancellation-aware sleep helpers. Operate only on a ``Token``, with no
# dependency on any ``Display`` instance's state -- callers pass whichever
# token they are holding.
# ---------------------------------------------------------------------------


def _ensure_non_negative_duration(method_name: str, param_name: str, duration: int) -> None:
    """Reject a time ``duration`` that is not an integer or is negative (strict type check: for example, ``float`` or ``bool`` is rejected too).

    ``method_name`` is the name of the public ``Display`` method that was called and ``param_name`` is its parameter providing
    the time ``duration``. Both only appear in the error message, for example ``show_image(): 'duration_ms' must be >= 0, got '-5'``.
    This check should be run before the display is acquired.
    """
    # ``type(duration) is int`` is exact: ``bool`` (subclass of ``int``) fails it, so no separate check is needed.
    if type(duration) is not int:
        raise TypeError(f"{method_name}(): '{param_name}' must be an integer, got '{duration}'")
    if duration < 0:
        raise ValueError(f"{method_name}(): '{param_name}' must be >= 0, got '{duration}'")


async def _sleep_pollable(token: Token, total_ms: int, poll_ms: int = 47) -> None:
    """Sleep up to ``total_ms`` milliseconds, returning early once ``token.is_expired``.

    Chunks the sleep into at most ``poll_ms``-sized pieces so a caller notices a superseding display operation approximately within ``poll_ms``
    (not only after the full ``total_ms`` has elapsed). Without cancellation the wait ends close to ``total_ms``, usually negligibly longer:
    other coroutines run until their next ``await``, so this coroutine might resume a little beyond the requested ``total_ms``.

    This function always awaits at least once, so other coroutines get a turn even when ``total_ms`` is very small, 0 or negative (a negative
    value behaves like 0).
    """
    deadline = ticks_add(ticks_ms(), total_ms)
    remaining = total_ms
    while remaining > poll_ms and not token.is_expired:
        await asyncio.sleep_ms(poll_ms)
        remaining = ticks_diff(deadline, ticks_ms())
    # Last piece, always awaited: ensures we yield at least once, even if ``total_ms`` is negative, 0 or very small. An expired token (also on entry)
    # shortens it to 0. ``remaining`` can be negative, since scheduling jitters may overshoot the deadline, and ``total_ms`` itself may be negative.
    # Note: ``asyncio.sleep_ms`` clamping negative values to 0 is an undocumented feature of asyncio ``core.py`` (10.3.0). Therefore, we do not rely
    # on it and clamp explicitly with ``max(0, remaining)``.
    await asyncio.sleep_ms(0 if token.is_expired else max(0, remaining))


def _write_column(pixels: neopixel.NeoPixel, lut: bytearray, x_base: int, col_byte: int, color: RGBcolor, off: RGBcolor) -> None:
    """Write one column byte at logical column ``x_base // HEIGHT``. Bit 0 is the top row."""
    # Not inlined into the callers. Benchmarked: calling this helper instead of writing the column's pixels inline adds 24 µs per column, so 119 µs
    # for the five columns of an icon (6.1% of one ``show()``). Inlining five copies of the body was judged not worth that.
    for y in range(HEIGHT):
        pixels[lut[x_base + y]] = color if (col_byte >> y) & 1 else off


# ---------------------------------------------------------------------------
# Display class
# ---------------------------------------------------------------------------
class Display:
    """Controls the 5×5 LED matrix.

    Use the ready-made ``display`` object from this module; you normally do not create a ``Display`` yourself. For one physical LED matrix, only
    a single ``Display`` object can exist for operating it. This is because the ``Display`` object takes control of the data pin the LED matrix is
    connected to. Creating a second ``Display`` raises an error unless you call ``deinit()`` on the first. After ``deinit()``, that first object
    is unusable. See ``lib/display/README.md`` § "Singleton design & ``deinit``" for the package's rationale for exposing one ready-made
    ``display`` instance.

    Starting any display operation cancels an animation that is still running (a Tier 2 call, i.e. one started with an ``await`` method such as
    ``show_string`` or ``scroll_image``). The exceptions are ``get_pixel``, ``set_brightness`` and ``set_rotation``. See the module docstring for the
    two tiers and further details on the cancellation policy.

    All times (``duration_ms``, ``interval_ms``, ``sleep_between_ms``) are integer milliseconds. ``float`` raises ``TypeError``.
    To convert, write ``int(1000 / 3)`` or use integer division ``1000 // 3``. Both drop the fraction (truncate).
    """

    _pixels: neopixel.NeoPixel
    """The raw NeoPixel buffer. Index a single pixel through ``_lut`` (logical ``(x, y)`` to NeoPixel index). 
    Uniform buffer operations such as ``fill`` need no index."""

    _lut: bytearray
    """Look-up table [LUT] from logical pixel (``x`` = column, ``y`` = row) to NeoPixel index in ``_pixels``:
    ``index = _lut[x * HEIGHT + y]``. At rotation 0 that is ``index = y + HEIGHT * (WIDTH - 1 - x)``.
    LUT reflects current rotation and is updated when rotation is changed by method ``set_rotation``."""

    _token: Token
    """The token of the current display operation. The public method that performs the display-mutating operation acquires a
    token first (``_acquire()`` or an ``_ensure_*_and_acquire()`` method) before it changes a pixel. 
    By convention, a Tier 2 method must call ``Token._complete_unless_expired()`` right before it returns. The call sets the
    token's ``was_completed`` to True iff the token is not already expired.

    Important: A helper the display operation calls, such as ``_hold_then_blank`` or ``_scroll_text``, does not acquire a token
    and does not call ``Token._complete_unless_expired()``. That helper could be one step inside a larger operation, so the top-level
    operation is what acquires the display and what declares that the display operation has reached its end.

    Acquiring expires the previous token, which cancels any Tier 2 animation still holding it. See
    ``lib/display/README.md`` § "Cooperative multitasking & ``Token``". ``get_pixel``, ``set_brightness`` and
    ``set_rotation`` do not acquire, so they leave a running Tier 2 animation alone. ``set_rotation`` still rewrites the pixels."""

    _frame: list[RGBcolor]
    """Scratch buffer for temporarily storing a snapshot of the current frame. For example, ``set_rotation`` uses it to avoid memory
    allocation on each call. Any method may overwrite it, so its contents are only valid until the next ``await``: write and read it
    without an ``await`` in between, and never use it to pass data between methods."""

    def __init__(self) -> None:
        """Create the matrix controller, claiming the NeoPixel data pin.

        Use the module-level ``display`` instance for normal use. Raises
        whatever ``neopixel.NeoPixel(...)`` raises if the pin is already
        claimed by another live ``Display`` — call that instance's
        ``deinit()`` first to free it.
        """
        self._pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)
        self._lut = build_lut(0)
        self._token = Token()
        # We allocate a single list here to hold a snapshot of a frame. This is useful for the ``set_rotation`` operation, which is
        # supposed to rotate the frame in place. This is beneficial, because rotation needs to first cache the current frame, then update
        # the LUT and finally write the frame back to the rotated LUT; we can reuse this list instead of allocating a new one on each rotation.
        self._frame = [OFF] * NUM_PIXELS

    # — Cancellation token --------------------------------------------------

    def _acquire(self) -> Token:
        """Start a new display-operation generation.

        Expires the previous token (specifically setting ``is_expired`` to True) and creates a new one which is then returned. Any
        Tier 2 animation holding the previous token will see its ``is_expired`` become True on its next check, and should return early.
        """
        self._token._expire()
        self._token = Token()
        return self._token

    def _ensure_integer_offset_and_acquire(self, method_name: str, start_col: int) -> Token:
        """Reject any non-integer ``start_col``, then acquire the display, and return the new ``Token``.
        The integer check is strict: for example, ``bool`` is rejected too. The check runs before the display is acquired.
        A rejected ``start_col`` leaves the display and any running animation untouched:
        ``method_name`` is the public method the caller used. It only appears in the error message, for example
        ``render_icon(): 'start_col' must be an integer, got 'True'``.

        This is a convenience method that combines the offset check with the display acquisition for performance reasons:
        both operations are very frequently used together and combining them saves an additional method call at runtime.
        """
        # ``type(start_col) is int`` is exact: ``bool`` (subclass of ``int``) fails it, so no separate check is needed.
        if type(start_col) is not int:
            raise TypeError(f"{method_name}(): 'start_col' must be an integer, got '{start_col}'")
        self._token._expire()
        self._token = Token()
        return self._token

    def _ensure_non_negative_duration_and_acquire(self, method_name: str, param_name: str, duration: int) -> Token:
        """Reject a time ``duration`` that is not an integer or is negative, then acquire the display, and return the new ``Token``.
        The integer check is strict: for example, ``bool`` is rejected too. The check runs before the display is acquired.
        A rejected ``duration`` leaves the display and any running animation untouched.
        ``method_name`` is the public method the caller used and ``param_name`` is its time parameter. Both only appear in the
        error message, for example ``scroll_string(): 'interval_ms' must be >= 0, got '-5'``.

        This is a convenience method that combines the duration check with the display acquisition for performance reasons:
        both operations are very frequently used together and combining them saves an additional method call at runtime.
        """
        # ``type(duration) is int`` is exact: ``bool`` (subclass of ``int``) fails it, so no separate check is needed.
        if type(duration) is not int:
            raise TypeError(f"{method_name}(): '{param_name}' must be an integer, got '{duration}'")
        if duration < 0:
            raise ValueError(f"{method_name}(): '{param_name}' must be >= 0, got '{duration}'")
        self._token._expire()
        self._token = Token()
        return self._token

    def _ensure_duration_and_start_col_and_acquire(self, method_name: str, duration_ms: int, start_col: int) -> Token:
        """Reject an invalid ``duration_ms`` or ``start_col``, then acquire the display, and return the new ``Token``. Enforces:
        ``duration_ms`` must be an integer ``>= 0``, and ``start_col`` must be an integer. Both integer checks are strict: for example, ``bool`` is
        rejected too. Both checks run before the display is acquired, so a rejected argument leaves the display and any running animation untouched.
        ``method_name`` is the public method the caller used. It only appears in the error message, for example
        ``show_pattern(): 'duration_ms' must be >= 0, got '-5'``.

        This is a convenience method for the ``show_*`` methods: it combines the checks of ``_ensure_non_negative_duration`` and
        ``_ensure_integer_offset_and_acquire`` with ``_acquire`` for performance reasons, because all three are used together and combining them
        saves two method calls at runtime.
        """
        # ``type(...) is int`` is exact: ``bool`` (subclass of ``int``) fails it, so no separate check is needed.
        if type(duration_ms) is not int:
            raise TypeError(f"{method_name}(): 'duration_ms' must be an integer, got '{duration_ms}'")
        if duration_ms < 0:
            raise ValueError(f"{method_name}(): 'duration_ms' must be >= 0, got '{duration_ms}'")
        if type(start_col) is not int:
            raise TypeError(f"{method_name}(): 'start_col' must be an integer, got '{start_col}'")
        self._token._expire()
        self._token = Token()
        return self._token

    # — Render primitives (hot path, called by Tier 1/2 render methods) ------

    def _write_pattern_on_the_fly(
        self,
        pattern_str: str,
        color: RGBcolor | ColorDict,
        start_col: int = 0,
    ) -> None:
        """Write ``pattern_str`` into this instance's pixel buffer in a single scan of the string, decoding and drawing each character as it is read.

        ``start_col`` is the display column where the pattern's first column goes (not validated here: the public entry points check that it is an
        integer). ``start_col=0`` means the pattern starts at the left-most LED column. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off. LEDs uncovered by the pattern are written ``OFF`` (for example, ``start_col=2`` leaves columns 0 and 1 off).

        Scan the source string once, skip only space / tab / CR, write each cell directly to this instance's NeoPixel buffer, ignore rows past
        ``HEIGHT``, pad short / missing rows with ``OFF``. No per-row string allocation and no generator.

        Does not call ``show()``. The caller flushes the buffer after invocation.
        """
        # Maintainer notes:
        # 1. Only space, tab and CR are recognized as whitespace here. In contrast, the cold-path parser ``_iter_pattern_rows(…)`` skips all whitespace
        #    via ``split()`` and ``join()`` per row. Doing the same here would need one string allocation per row, which this single scan avoids.
        #    Benchmarked: this scan renders a 5x5 pattern 1916 µs faster than parsing an ``Image`` and rendering its window (1598 vs 3514 µs;
        #    98% of one ``show()``). Using ``split()`` / ``join()`` alone would cost +422 µs for four rows (22% of one ``show()``; see ``bitmap_codec``).
        # 2. The type of ``color`` (single color or dict) is checked once, before the scan, so the per-cell write needs no check. The price is two copies
        #    of the loop that differ only in the cell write. Do not merge them via a per-cell callback: that would add a function call per cell, which is
        #    what this split avoids. Benchmarked: +122 µs per 25 cells (6.2% of one ``show()``).
        # 3. Supporting the parameter ``start_col`` costs +83 µs even at start_col=0, compared with a scanner without it (4.3% of one ``show()``).
        # Benchmark figures for 2. and 3. were done with a mock list in place of the NeoPixel pixel buffer. Comparable deltas measured on the NeoPixel
        # came out larger, so treat these two figures as lower bounds.
        pixels = self._pixels
        lut = self._lut
        off = OFF
        width = WIDTH
        height = HEIGHT

        # We parse the pattern string row by row and write its cells (non-whitespace characters) to the ``pixels`` buffer. We do not clear the buffer
        # first, so every pixel must be written here, including pixels outside the pattern: columns that no cell reaches (pattern shifted by ``start_col`` or
        # narrower than the display) are blanked at the end of each row, and rows the pattern does not reach are blanked at the end.
        x = start_col  # display column the next cell would fall onto: might be negative if shifted left, or ``≥ width`` if shifted off the right edge
        y = 0  # display row of the next cell
        row_has_cell = False  # True once the current row has a non-whitespace character, even one cut off by ``start_col``

        if isinstance(color, dict):
            for ch in pattern_str:
                if ch == "\n":
                    if row_has_cell:
                        # For the current row that we just reached the end of, the pattern covers columns [start_col, x), clipped to the display.
                        # We now need to set the pixels in the row to off that are outside of [start_col, x).
                        b = start_col if start_col < width else width  # left margin: blank [0, b); empty if start_col ≤ 0 (``range(b)`` with b ≤ 0 yields no numbers)
                        for blank_col in range(b):
                            pixels[lut[blank_col * height + y]] = off
                        b = x if x > 0 else 0  # right margin: blank [b, width); empty if x ≥ width
                        for blank_col in range(b, width):
                            pixels[lut[blank_col * height + y]] = off
                        y += 1
                        if y >= height:
                            return
                        x = start_col
                        row_has_cell = False
                    continue
                if ch == " " or ch == "\t" or ch == "\r":
                    continue

                row_has_cell = True
                if 0 <= x < width:
                    pixels[lut[x * height + y]] = color.get(ch, off)
                x += 1
            # End of the pattern string. The code that finishes the last row and blanks the remaining rows is shared by both branches and follows below.

        else:  # ``color`` is not a dictionary
            for ch in pattern_str:
                if ch == "\n":
                    if row_has_cell:
                        # For the current row that we just reached the end of, the pattern covers columns [start_col, x), clipped to the display.
                        # We now need to set the pixels in the row to off that are outside of [start_col, x).
                        b = start_col if start_col < width else width  # left margin: blank [0, b); empty if start_col ≤ 0 (``range(b)`` with b ≤ 0 yields no numbers)
                        for blank_col in range(b):
                            pixels[lut[blank_col * height + y]] = off
                        b = x if x > 0 else 0  # right margin: blank [b, width); empty if x ≥ width
                        for blank_col in range(b, width):
                            pixels[lut[blank_col * height + y]] = off
                        y += 1
                        if y >= height:
                            return
                        x = start_col
                        row_has_cell = False
                    continue
                if ch == " " or ch == "\t" or ch == "\r":
                    continue

                row_has_cell = True
                if 0 <= x < width:
                    pixels[lut[x * height + y]] = color if ch == "#" else off
                x += 1
            # End of the pattern string. The code that finishes the last row and blanks the remaining rows is shared by both branches and follows below.

        # Shared by both branches: we reach this point only after the whole pattern string was scanned. We necessarily have ``y < HEIGHT``, because every
        # ``y += 1`` in the loops above is followed by ``if y >= height: return``. So there are still rows to fill with off.
        # Caution EDGE CASE: the pattern's last row might have no trailing newline. Then its margins have not been blanked yet, so we finish that row first.
        if row_has_cell:
            # For the current row that we just reached the end of, the pattern covers columns [start_col, x), clipped to the display.
            # We now need to set the pixels in the row to off that are outside of [start_col, x).
            b = start_col if start_col < width else width  # left margin: blank [0, b); empty if start_col ≤ 0 (``range(b)`` with b ≤ 0 yields no numbers)
            for blank_col in range(b):
                pixels[lut[blank_col * height + y]] = off
            b = x if x > 0 else 0  # right margin: blank [b, width); empty if x ≥ width
            for blank_col in range(b, width):
                pixels[lut[blank_col * height + y]] = off
            y += 1
        while y < height:  # lastly, fill the remaining rows with off
            for blank_col in range(width):
                pixels[lut[blank_col * height + y]] = off
            y += 1

    def _render_colmajor(self, data: bytes, color: RGBcolor, start_col: int = 0) -> None:
        """Draw the column bytes of ``data`` into ``self._pixels``, starting at the display column ``start_col``. Then ``show()``. ``data`` is not modified.

        Each byte of ``data`` is one column of the bitmap. Bit ``y`` of the byte selects the pixel at display row ``y`` (bit 0 = top row).
        If ``HEIGHT`` is less than 8, bits ``HEIGHT`` to 7 (the high-order bits of the byte) are ignored.

        ``start_col`` is the display column where the first column of ``data`` goes (not validated here: the public entry points check that it is an
        integer). ``start_col=0`` means ``data`` starts at the left-most display column. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off. LEDs uncovered by ``data`` are off (for example, ``start_col=2`` leaves columns 0 and 1 off). ``data`` may be shorter or longer
        than ``WIDTH`` bytes.

        On the hardware level, the LEDs are addressed using a single index. The Look-Up Table (``lut``) translates from logical pixels (column, row)
        to the physical strip index. The ``lut`` is organized using column-major convention, i.e. ``lut[column * HEIGHT + row]`` returns the
        physical strip index for the logical pixel (column, row). Writes ``self._pixels`` and reads ``self._lut``.

        CAUTION: this method is part of the hot path for rendering. Especially for scrolling, this code is performance sensitive.
        """
        # Maintainer notes:
        # * supporting ``start_col`` (three loops instead of the single loop of a renderer without it)
        #   costs +41 µs at start_col=0 (2.1% of one ``show()``; benchmarked on the NeoPixel).
        # * We cache references to attributes and global values before the loops: a local (LOAD_FAST) is cheaper than ``self._pixels`` / ``self._lut``
        #   (LOAD_ATTR) or ``OFF`` (LOAD_GLOBAL), which would otherwise be looked up for every ``_write_column`` call. Benchmarked (mock list instead of
        #   NeoPixel) with per-pixel lookups instead: attributes +57 µs per 5x5 frame (2.9% of one ``show()``, about the size of that run's spread), a global
        #   ``OFF`` +3.7 µs (a tie). With one lookup per column the saving here is smaller (not benchmarked; about a fifth, roughly 0.6% of one ``show()``).
        #   Mechanism, checked against MicroPython's VM (`py/vm.c` MP_BC_LOAD_FAST_N / MP_BC_LOAD_GLOBAL, `py/runtime.c` mp_load_global).
        pixels = self._pixels
        lut = self._lut
        off = OFF
        # Display columns showing ``data`` are [first, cutoff): ``first`` is the left-most column showing data, ``cutoff`` the first display column right of
        # the data (exclusive). We ensure that ``0 ≤ first ≤ cutoff ≤ WIDTH``. The three loops below write [0, first), [first, cutoff), [cutoff, WIDTH),
        # so together they cover each display column exactly once. ``first`` and ``cutoff`` are clamped with compares, not ``min()`` / ``max()``:
        # benchmarked +91 µs per clamp for ``min()`` / ``max()`` (4.7% of one ``show()``).
        if start_col < 0:
            # Data starts left of the display: skip its first ``-start_col`` columns.
            first = 0
            src = -start_col
            cutoff = start_col + len(data)
            if cutoff < 0:  # all data lies off the left edge: nothing to draw
                cutoff = 0
            elif cutoff > WIDTH:
                cutoff = WIDTH
        else:
            first = start_col if start_col < WIDTH else WIDTH  # ``start_col ≥ WIDTH`` blanks every column in the first loop below
            src = 0
            cutoff = start_col + len(data)
            if cutoff > WIDTH:
                cutoff = WIDTH
        x_base = 0  # invariant at top of each loop: x_base == <display column> * HEIGHT (see `geometry.build_lut` convention)
        for _ in range(first):  # blank columns left of the data
            _write_column(pixels, lut, x_base, 0, color, off)
            x_base += HEIGHT  # advance to next column; addition avoids a per-column multiply
        for _ in range(first, cutoff):  # data columns, starting at ``data[src]``
            _write_column(pixels, lut, x_base, data[src], color, off)
            src += 1
            x_base += HEIGHT
        for _ in range(cutoff, WIDTH):  # blank columns right of the data
            _write_column(pixels, lut, x_base, 0, color, off)
            x_base += HEIGHT
        pixels.show()

    def _draw_text(self, reader: _ColumnReader | _FixedColumnReader, start_col: int, color: RGBcolor) -> None:
        """Draw ``reader`` starting at the display column ``start_col``. Then ``show()``.

        ``start_col`` is the display column where the first column of ``reader`` goes (not validated here: the public entry points check that it is
        an integer). ``start_col=0`` means the text starts at the left-most display column. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off. LEDs uncovered by the text are off (for example, ``start_col=2`` leaves columns 0 and 1 off).

        ``next_column`` returning ``None`` is a blank column; later calls stay ``None``.
        """
        pixels = self._pixels
        lut = self._lut
        off = OFF
        if start_col < 0:
            reader.skip(-start_col)
            start = 0
        else:
            # Deliberately not ``min(start_col, WIDTH)``: benchmarked +27 µs for ``min`` over the compare (1.4% of one ``show()``).
            start = WIDTH if start_col > WIDTH else start_col
        split = start * HEIGHT  # x_base of the first column that shows text (x_base == column * HEIGHT)
        for x_base in range(0, split, HEIGHT):  # columns before the text starts are off
            _write_column(pixels, lut, x_base, 0, color, off)
        for x_base in range(split, WIDTH * HEIGHT, HEIGHT):
            col_byte = reader.next_column()
            if col_byte is None:
                col_byte = 0
            _write_column(pixels, lut, x_base, col_byte, color, off)
        pixels.show()

    def _render_ring_window(
        self,
        ring: bytearray,
        read_head: int,
        color_on: RGBcolor,
    ) -> None:
        """Render a WIDTH-sized ring buffer as a left-to-right window starting at ``read_head``. Then ``show()``.
        IMPORTANT: ``read_head`` must be in 0..WIDTH-1!

        The ring holds exactly ``WIDTH`` column bytes; ``read_head`` is the index of the left-most visible column. Wrap is handled by splitting the draw
        into two loops (``read_head`` to the end, then the start up to ``read_head``), with no per-column modulo, subtraction or compare (cheaper on the
        MCU VM).

        Reads ``self._pixels`` / ``self._lut`` fresh on every call, not cached once per animation. This is one of the three facts (alongside
        ``set_rotation``'s in-place mutation and asyncio's cooperative scheduling) that make rotating mid-scroll safe. See README.md § "Rotation during an
        in-flight Tier 2 animation".
        """
        pixels = self._pixels
        lut = self._lut
        off = OFF
        x_base = 0  # invariant at top of loop: x_base == <display column> * HEIGHT
        # The visible columns are ring[read_head:WIDTH], then ring[0:read_head]. We break the loop into two
        # parts to avoid tests inside the loops on whether we have wrapped around the ring. This requires
        # that ``read_head`` is in 0..WIDTH-1; when ``read_head == 0`` the second loop is empty.
        for idx in range(read_head, WIDTH):
            _write_column(pixels, lut, x_base, ring[idx], color_on, off)
            x_base += HEIGHT  # advance to next column; addition avoids a per-column multiply
        for idx in range(read_head):
            _write_column(pixels, lut, x_base, ring[idx], color_on, off)
            x_base += HEIGHT
        pixels.show()

    # — Tier 1: Synchronous rendering primitives ----------------------------

    def render_pattern(
        self,
        pattern: str,
        color: RGBcolor | ColorDict = WHITE,
        *,
        start_col: int = 0,
    ) -> None:
        """Draw a pattern string straight onto the LEDs. Leave it lit until some other call overwrites the display.
        Best for a picture you show once, because this method needs to go over the input string and decode every character into a pixel (this is
        called "parsing" the pattern). For pictures you want to show repeatedly, it is best to only parse the pattern once, which is done by
        constructing an ``Image(pattern)`` or an ``Icon(pattern)``. Each is a parsed Image / Icon, whose reference you can keep and show repeatedly.

        Each line of the pattern is one row of the picture, starting at the top left corner of the LED matrix by default. A row covering fewer than WIDTH
        pixels is filled with off pixels on the right. Extra pixels on the right, and rows past the bottom of the screen, are cut off. Missing rows at
        the bottom are off.

        ``start_col`` is the display column where the pattern's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the pattern starts at the left-most LED column. A positive value moves the pattern to the right, so
        ``start_col=2`` leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of column 0, or
        at ``WIDTH`` and further right, are cut off, and LEDs the pattern does not cover are also off. A float or a bool raises ``TypeError`` before the display
        changes.

        If ``color`` is an RGB tuple ``(red, green, blue)``, every ``#`` is an LED lit in that color and every other character is off, so ``#.#``
        shows "on, off, on". The default color is white. If ``color`` is a dict ``{character: RGB tuple}``, you can specify different letters to
        represent different colors, such as ``color["G"] = (0, 255, 0)`` for green and ``color["R"] = (255, 0, 0)`` for red (and so on). Then,
        writing ``G.RG`` shows "green, off, red, green". Any character that is not in the dict represents off.

        Spaces, tabs and carriage returns are skipped, so ``#.#`` and ``# .  #`` are the same picture. Any other character represents one pixel.
        """
        self._ensure_integer_offset_and_acquire("render_pattern", start_col)
        # Direct render via LUT: no intermediate column-major buffer and no ``Image``, for every ``start_col``.
        self._write_pattern_on_the_fly(pattern, color, start_col)
        self._pixels.show()

    def render_icon(self, icon: Icon, color: RGBcolor = WHITE, *, start_col: int = 0) -> None:
        """Render an ``Icon`` (e.g. ``Emojis.HEART``) to the LEDs. Leave it lit until some other call overwrites the display.
        The icon is shown in the provided ``color`` (white by default), which must be explicitly stated because an ``Icon`` carries no color of its own.

        ``start_col`` is the display column where the icon's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the icon starts at the left-most LED column. A positive value moves the icon to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of column 0, or at ``WIDTH`` and
        further right, are cut off, and LEDs the icon does not cover are off. A float or a bool raises ``TypeError`` before the display changes.
        """
        columns = icon._columns
        self._ensure_integer_offset_and_acquire("render_icon", start_col)
        self._render_colmajor(columns, color, start_col)

    def render_arrow(self, arrow: Icon, color: RGBcolor = WHITE, *, start_col: int = 0) -> None:
        """Render an ``Icon`` from the arrow catalog (e.g. ``Arrows.NORTH``) to the LEDs. Leave it lit until some other call overwrites the display.
        The icon is shown in the provided ``color`` (white by default), which must be explicitly stated because an ``Icon`` carries no color of its own.

        ``start_col`` is the display column where the arrow's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the arrow starts at the left-most LED column. A positive value moves the arrow to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the arrow does not cover are off. A float or a bool raises ``TypeError`` before the display changes.
        """
        # Body of ``render_icon`` repeated on purpose: saves one method lookup and call. Keep the two in sync.
        columns = arrow._columns
        self._ensure_integer_offset_and_acquire("render_arrow", start_col)
        self._render_colmajor(columns, color, start_col)

    def render_string(self, text: str | ScreenText, color: RGBcolor = WHITE, *, start_col: int = 0) -> None:
        """Draw ``text`` left-aligned and leave it lit until some other call overwrites the display.
        Text hanging over the display on the right is cut off. To scroll longer text, call ``scroll_string``.

        ``start_col`` is the display column where the text's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the text starts at the left-most display column. A positive value moves the text to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the text does not cover are off. A float or a bool raises ``TypeError`` before the display changes.

        ``text`` may be a Python ``str`` or a ``ScreenText``. An empty string draws a blank screen.

        A plain ``str`` is the easy choice for text you draw once. A ``ScreenText`` is pre-prepared text: it counts how many columns the text needs (its
        ``width``) the first time you ask, and remembers the answer. Use ``ScreenText`` when you draw the same text again and again, or when you want to check
        ``width`` against the display before you choose how to show the text.

        Pass ``centered(text)`` when the text should sit in the middle. ``centered(text)`` returns a ``ScreenText`` too, so create it once and reuse it if you
        want to show the centered text repeatedly.
        """
        reader = _reader_for(text)
        self._ensure_integer_offset_and_acquire("render_string", start_col)
        self._draw_text(reader, start_col, color)

    def render_image(self, image: Image, *, start_col: int = 0) -> None:
        """Draw a ``WIDTH``-column window of ``image`` and leave it lit until some other call overwrites it.
        By default, the window starts at the image's first column, and an image wider than ``WIDTH`` is cut off on the right.
        To scroll a wider image, call ``scroll_image``.

        ``start_col`` is the display column where the image's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the image starts at the left-most LED column. A positive value moves the image to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the image does not cover are off. A float or a bool raises ``TypeError`` before the display changes.
        """
        self._ensure_integer_offset_and_acquire("render_image", start_col)
        image._render_window(self, -start_col)

    def render_number(self, n: int | float, color: RGBcolor = WHITE, *, start_col: int = 0) -> None:
        """Draws number ``n`` as text (internally converted using python's ``str(n)``) and leaves it lit until some other call overwrites the display.
        By default, the number starts at the left-most LED column, and a longer number is cut off on the right. To scroll longer numbers, call ``scroll_number``.

        ``start_col`` is the display column where the number's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the number starts at the left-most LED column. A positive value moves the number to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the number does not cover are off. A float or a bool raises ``TypeError`` before the display changes.
        """
        reader = _reader_for(str(n))
        self._ensure_integer_offset_and_acquire("render_number", start_col)
        self._draw_text(reader, start_col, color)

    def render_filled(self, color: RGBcolor = WHITE) -> None:
        """Fill all pixels with ``color``."""
        self._acquire()
        self._pixels.fill(color)
        self._pixels.show()

    def clear(self) -> None:
        """Turn off all pixels."""
        self._acquire()
        self._pixels.fill(OFF)
        self._pixels.show()

    def set_pixel(self, x: int, y: int, color: RGBcolor = WHITE) -> None:
        """Set one pixel.

        The display stays on the most recent frame. When ``(x, y)`` is on the matrix, that pixel is changed and
        flushed. When it is outside, nothing is written and the frame is left as it was. Writing to coordinates
        ``(x, y)`` outside the matrix draws nothing visible, but it still cancels any Tier 2 call that is running
        (such as a ``show_string`` scroll), as every other display-changing call does.
        """
        self._acquire()
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self._pixels[self._lut[x * HEIGHT + y]] = color
            self._pixels.show()

    def get_pixel(self, x: int, y: int) -> RGBcolor:
        """Read the buffered pixel color at (x, y). Read-only; does not cancel ongoing animations."""
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            return self._pixels[self._lut[x * HEIGHT + y]]
        return OFF

    def set_brightness(self, value: float) -> None:
        """Adjust global brightness (0.0-1.0). Does not cancel animations."""
        self._pixels.brightness = value
        self._pixels.show()

    def set_rotation(self, degrees: int) -> None:
        """Set clockwise rotation to 0/90/180/270 degrees. Does not cancel animations.

        The picture currently on the LEDs is drawn again in the new orientation.
        A scroll that is already running keeps going, just rotated in the new orientation.

        ``degrees`` is how far to turn the picture clockwise. Allowed values are ``0``, ``90``, ``180`` and ``270``. A negative value turns it
        counter-clockwise, so ``-90`` is the same as ``270``, ``-180`` the same as ``180`` and ``-270`` the same as ``90``. Any other value,
        including a full turn such as ``360`` or ``-360``, raises ``ValueError`` and leaves the display as it was. To accept any angle, bring
        it into range [-270°, 270°] yourself, for example ``set_rotation(angle % 360)``. The result must still be 0, 90, 180 or 270.
        """
        # Snapshot the current frame using the current LUT (prior to rotation), then rebuild the LUT in place to represent the new rotation, then write
        # the frame back. `build_lut` raises before it writes when degrees is rejected, so a bad value leaves the LEDs and the LUT as they were. No await
        # in this method, and no _acquire, so an in-flight Tier 2 animation is not cancelled and cannot interleave with the rewrite. The list we use as
        # cache for the current frame, `self._frame`, is allocated once in `__init__`. See README.md § "Rotation during an in-flight Tier 2 animation".
        snap = self._frame
        pixels = self._pixels
        lut = self._lut
        i = 0
        for x in range(WIDTH):
            x_base = x * HEIGHT
            for y in range(HEIGHT):
                snap[i] = pixels[lut[x_base + y]]
                i += 1
        build_lut(degrees, dest=lut)
        i = 0
        for x in range(WIDTH):
            x_base = x * HEIGHT
            for y in range(HEIGHT):
                pixels[lut[x_base + y]] = snap[i]
                i += 1
        pixels.show()

    # — Lifecycle -----------------------------------------------------------

    def deinit(self) -> None:
        """Shut the display down and free the pin it uses for the LEDs.

        Call this only when you are completely done with the LED display, for example when you want to use the same pin for something else.
        It stops any animation that is running. After that, this ``Display`` object can no longer be used: any drawing call on it
        raises an error. To the same physical LED display again, create a new ``Display()`` object for controlling it.

        See ``lib/display/README.md`` § "Singleton design & ``deinit``" for why a ready-made ``display`` object exists.
        """
        # Maintainer: releases the NeoPixel RMT peripheral and data pin. There is no re-init path on this instance. A fresh ``Display()`` claims the pin
        # again and starts with a clean buffer, LUT and token; it does not resurrect this one.
        self._acquire()
        self._pixels.deinit()

    # — Tier 2: Async MakeCode-compatible methods ---------------------------

    async def _hold_then_blank(self, token: Token, duration_ms: int) -> Token:
        """Wait ``duration_ms``, then turn every LED off, but only if this call's token has not expired.

        The caller has already taken over the display and drawn its picture. This helper does not mutate the state of the token:
        a caller may compose this wait into a larger operation. See ``lib/display/README.md`` § "Cooperative multitasking & ``Token``".
        The token is read only to see whether another display call has expired it. If so, the wait ends early and the display is not
        touched (the wipe that would follow a finished wait is skipped). The display is left to that other call.
        """
        await _sleep_pollable(token, duration_ms)
        if token.is_expired:
            return token
        self._pixels.fill(OFF)
        self._pixels.show()
        return token

    async def show_pattern(
        self,
        pattern: str,
        color: RGBcolor | ColorDict = WHITE,
        *,
        start_col: int = 0,
        duration_ms: int,
    ) -> Token:
        """Draw a pattern, hold it for ``duration_ms`` milliseconds, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call raises ``TypeError``. The picture stays up for
        the hold duration. If another display call takes over during the hold, ``show_pattern`` returns at that point (leaving the display to the other caller)
        and its returned token is expired. With ``duration_ms=0``, ``show_pattern`` draws the pattern, lets other ready tasks run once, and then wipes the
        display (if no other call has taken over). This is probably just a short flicker.

        ``start_col`` is the display column where the pattern's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the pattern starts at the left-most LED column. A positive value moves the pattern to the right, so
        ``start_col=2`` leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at
        ``WIDTH`` and further right, are cut off, and LEDs the pattern does not cover are also off. A float or a bool raises ``TypeError`` before the display
        changes.

        If ``color`` is an RGB tuple, every ``#`` is an LED lit in that color and every other character is off.
        If ``color`` is a dict ``{character: RGB tuple}``, each listed character lights its LED in the given color
        and any character not in the dict is off. Spaces, tabs and carriage returns are skipped; any other character
        represents one pixel. See ``render_pattern`` for more detailed examples.

        Raises ``TypeError`` if ``duration_ms`` or ``start_col`` is not an integer, and ``ValueError`` if ``duration_ms < 0``,
        before the display changes.
        """
        token = self._ensure_duration_and_start_col_and_acquire("show_pattern", duration_ms, start_col)
        self._write_pattern_on_the_fly(pattern, color, start_col)
        self._pixels.show()
        await self._hold_then_blank(token, duration_ms)
        token._complete_unless_expired()
        return token

    async def show_icon(self, icon: Icon, color: RGBcolor = WHITE, *, start_col: int = 0, duration_ms: int) -> Token:
        """Draw an ``Icon`` (e.g. ``Emojis.HEART``), hold it for ``duration_ms`` milliseconds, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call raises ``TypeError``. The picture stays up for
        the hold duration. If another display call takes over during the hold, ``show_icon`` returns at that point (leaving the display to the other caller) and
        its returned token is expired. With ``duration_ms=0``, ``show_icon`` draws the icon, lets other ready tasks run once, and then wipes the display (if no
        other call has taken over). This is probably just a short flicker.

        ``start_col`` is the display column where the icon's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the icon starts at the left-most LED column. A positive value moves the icon to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the icon does not cover are off. A float or a bool raises ``TypeError`` before the display changes.

        Raises ``TypeError`` if ``duration_ms`` or ``start_col`` is not an integer, and ``ValueError`` if ``duration_ms < 0``,
        before the display changes.
        """
        columns = icon._columns
        token = self._ensure_duration_and_start_col_and_acquire("show_icon", duration_ms, start_col)
        self._render_colmajor(columns, color, start_col)
        await self._hold_then_blank(token, duration_ms)
        token._complete_unless_expired()
        return token

    async def show_arrow(self, arrow: Icon, color: RGBcolor = WHITE, *, start_col: int = 0, duration_ms: int) -> Token:
        """Draw an arrow ``Icon`` (e.g. ``Arrows.NORTH``), hold it, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call raises ``TypeError``. The picture stays up for
        the hold duration. If another display call takes over during the hold, ``show_arrow`` returns at that point (leaving the display to the other caller)
        and its returned token is expired. With ``duration_ms=0``, ``show_arrow`` draws the arrow, lets other ready tasks run once, and then wipes the display
        (if no other call has taken over). This is probably just a short flicker.

        ``start_col`` is the display column where the arrow's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the arrow starts at the left-most LED column. A positive value moves the arrow to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the arrow does not cover are off. A float or a bool raises ``TypeError`` before the display changes.

        Raises ``TypeError`` if ``duration_ms`` or ``start_col`` is not an integer, and ``ValueError`` if ``duration_ms < 0``,
        before the display changes.
        """
        columns = arrow._columns
        token = self._ensure_duration_and_start_col_and_acquire("show_arrow", duration_ms, start_col)
        self._render_colmajor(columns, color, start_col)
        await self._hold_then_blank(token, duration_ms)
        token._complete_unless_expired()
        return token

    async def show_filled(self, color: RGBcolor = WHITE, *, duration_ms: int) -> Token:
        """Fill the display with ``color``, hold it for ``duration_ms`` milliseconds, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call raises ``TypeError``. The picture stays up for
        the hold duration. If another display call takes over during the hold, ``show_filled`` returns at that point (leaving the display to the other caller)
        and its returned token is expired. With ``duration_ms=0``, ``show_filled`` fills the display, lets other ready tasks run once, and then wipes the
        display (if no other call has taken over). This is probably just a short flicker.

        Raises ``TypeError`` if ``duration_ms`` is not an integer, and ``ValueError`` if ``duration_ms < 0``, before the display changes.
        """
        _ensure_non_negative_duration("show_filled", "duration_ms", duration_ms)
        self.render_filled(color)
        token = self._token
        await self._hold_then_blank(token, duration_ms)
        token._complete_unless_expired()
        return token

    async def show_image(self, image: Image, *, start_col: int = 0, duration_ms: int) -> Token:
        """Show a ``WIDTH``-column window of ``image``, hold it for ``duration_ms`` milliseconds, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call raises ``TypeError``. The picture stays up for
        the hold duration. If another display call takes over during the hold, ``show_image`` returns at that point (leaving the display to the other caller)
        and its returned token is expired. With ``duration_ms=0``, ``show_image`` shows the window, lets other ready tasks run once, and then wipes the display
        (if no other call has taken over). This is probably just a short flicker.

        By default, the window starts at the image's first column, and an image wider than ``WIDTH`` is cut off on the right.
        To scroll a wider image, call ``scroll_image``.

        ``start_col`` is the display column where the image's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the image starts at the left-most LED column. A positive value moves the image to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the image does not cover are off. A float or a bool raises ``TypeError`` before the display changes.

        Raises ``TypeError`` if ``duration_ms`` or ``start_col`` is not an integer, and ``ValueError`` if ``duration_ms < 0``, before the display changes.
        """
        token = self._ensure_duration_and_start_col_and_acquire("show_image", duration_ms, start_col)
        image._render_window(self, -start_col)
        await self._hold_then_blank(token, duration_ms)
        token._complete_unless_expired()
        return token

    async def show_string(
        self,
        text: str | ScreenText,
        color: RGBcolor = WHITE,
        *,
        start_col: int = 0,
        duration_ms: int,
    ) -> Token:
        """Draw ``text`` left-aligned, hold it for ``duration_ms`` milliseconds, then turn the LEDs off.
        Text hanging over the display on the right is cut off. To scroll longer text, call ``scroll_string``.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call raises ``TypeError``. The picture stays up for
        the hold duration. If another display call takes over during the hold, ``show_string`` returns at that point (leaving the display to the other caller)
        and its returned token is expired. With ``duration_ms=0``, ``show_string`` draws the text, lets other ready tasks run once, and then wipes the display
        (if no other call has taken over). This is probably just a short flicker.

        ``start_col`` is the display column where the text's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the text starts at the left-most display column. A positive value moves the text to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the text does not cover are off. A float or a bool raises ``TypeError`` before the display changes.

        ``text`` may be a Python ``str`` or a ``ScreenText``. An empty string draws a blank screen.
        A plain ``str`` is the easy choice for text you draw once. A ``ScreenText`` remembers how many columns
        the text needs. Pass ``centered(text)`` when the text should sit in the middle.

        Raises ``TypeError`` if ``duration_ms`` or ``start_col`` is not an integer, and ``ValueError`` if ``duration_ms < 0``,
        before the display changes.
        """
        reader = _reader_for(text)
        token = self._ensure_duration_and_start_col_and_acquire("show_string", duration_ms, start_col)
        self._draw_text(reader, start_col, color)
        await self._hold_then_blank(token, duration_ms)
        token._complete_unless_expired()
        return token

    async def show_number(
        self,
        n: int | float,
        color: RGBcolor = WHITE,
        *,
        start_col: int = 0,
        duration_ms: int,
    ) -> Token:
        """Draw ``n`` left-aligned, as ``str(n)``, hold it for ``duration_ms`` milliseconds, then turn the LEDs off.
        A number hanging over the display on the right is cut off. To scroll a longer number, call ``scroll_number``.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call raises ``TypeError``. The picture stays up for
        the hold duration. If another display call takes over during the hold, ``show_number`` returns at that point (leaving the display to the other caller)
        and its returned token is expired. With ``duration_ms=0``, ``show_number`` draws the number, lets other ready tasks run once, and then wipes the display
        (if no other call has taken over). This is probably just a short flicker.

        ``start_col`` is the display column where the number's first column goes. It must be an integer and defaults to 0. Always pass it by name, for example
        ``start_col=2``. ``start_col=0`` means the number starts at the left-most LED column. A positive value moves the number to the right, so ``start_col=2``
        leaves columns 0 and 1 off. A negative value moves it to the left, partly off the screen. Columns that would land left of 0, or at ``WIDTH`` and further
        right, are cut off, and LEDs the number does not cover are off. A float or a bool raises ``TypeError`` before the display changes.

        Raises ``TypeError`` if ``duration_ms`` or ``start_col`` is not an integer, and ``ValueError`` if ``duration_ms < 0``,
        before the display changes.
        """
        reader = _reader_for(str(n))
        token = self._ensure_duration_and_start_col_and_acquire("show_number", duration_ms, start_col)
        self._draw_text(reader, start_col, color)
        await self._hold_then_blank(token, duration_ms)
        token._complete_unless_expired()
        return token

    async def scroll_image(
        self,
        image: Image,
        *,
        interval_ms: int = 150,
        loop: bool = False,
        blank_edges: bool = True,
    ) -> Token:
        """Scroll ``image`` across the display, one column every ``interval_ms`` milliseconds.

        Always pass the interval by name, for example ``interval_ms=150``. Without the name the call raises ``TypeError``. ``interval_ms=0`` still lets other
        ready tasks run once between frames.

        With the default ``blank_edges=True``, the display starts empty. The image comes in at the right-most LED, moves left, leaves at the left-most LED, and
        the display ends empty. With ``blank_edges=False``, the first frame already shows the image's first column on the left-most LED. The image moves left
        and stops when its last column reaches the right-most LED. When the scroll runs through to its end, it stops on its last frame, which stays on the
        display until another call replaces it: a blank display with ``blank_edges=True``, and the image's final window with ``blank_edges=False``.

        An image of ``WIDTH`` columns or fewer does not move with ``blank_edges=False``: its first frame is also its last. With ``blank_edges=True`` it still
        scrolls in and out like any other. With ``loop=True`` and ``blank_edges=False``, such an image is simply drawn again and again until another
        display call takes over.

        With ``loop=True``, the scroll repeats until another display call takes over and only at that point, ``scroll_image`` returns (leaving the display to
        the other caller). So the first line below never finishes, and the code after it never runs. To keep your program going, run the scroll as a background
        task and stop it later with any other display call, such as ``clear()``:

            await display.scroll_image(my_image, loop=True)  # never returns

            task = asyncio.create_task(display.scroll_image(my_image, loop=True))  # runs alongside the rest of your program
            ...
            display.clear()  # takes over the display: the scroll stops and its task ends

        The display is not cleared after the scroll ends. To clear it after a scroll that ends on a lit frame (``blank_edges=False``), check the token this call
        returns first. If the token is expired, another display call has taken over the display, and ``clear()`` would erase its picture. Example:

            token = await display.scroll_image(my_image, blank_edges=False)
            if not token.is_expired:
                display.clear()

        To show an image without scrolling it (images wider than the display are cut off), use ``render_image`` (it stays until the next display call) or
        ``show_image`` (it stays for a set time).

        Raises ``TypeError`` if ``interval_ms`` is not an integer, and ``ValueError`` if ``interval_ms < 0``, before the display changes.
        """
        n = image._width
        token = self._ensure_non_negative_duration_and_acquire("scroll_image", "interval_ms", interval_ms)
        # One sleep per frame. ``offset`` is the image column shown at the left-most LED, so the window moves one column per frame.
        if blank_edges:
            first_offset = -WIDTH  # the window starts WIDTH columns before the image's first column, so the image is off-screen at first and enters from the right
            last_offset = n  # the window starts at column n: the image has scrolled completely off to the left
        else:
            first_offset = 0
            last_offset = n - WIDTH  # columns to scroll, if the image is wider than WIDTH: the last image column then reaches the right-most LED
            if last_offset < 0:  # the image is narrower than WIDTH and fits on the display
                last_offset = 0  # so there is nothing to scroll: one still frame
        # Note that it always holds: first_offset ≤ last_offset. When scrolling the image, we want to iterate over the interval
        # [first_offset, last_offset] inclusive of both endpoints.
        offsets = range(first_offset, last_offset + 1)  # reusable: every ``for`` makes a new iterator, no list is built
        sleep_ms = asyncio.sleep_ms
        while True:
            for offset in offsets:
                image._render_window(self, offset)
                await sleep_ms(interval_ms)
                if token.is_expired:
                    # Already expired, so ``_complete_unless_expired()`` would leave ``was_completed`` false.
                    return token
            if not loop:
                token._complete_unless_expired()
                return token

    async def _scroll_text(
        self,
        token: Token,
        reader: _ColumnReader | _FixedColumnReader,
        color: RGBcolor,
        interval_ms: int,
        loop: bool,
        blank_edges: bool,
    ) -> Token:
        """Scroll content from ``reader`` one column per ``interval_ms``.

        The caller has already acquired ``token``. This helper does not mutate the state of the token:
        a caller may compose this scroll into a larger operation. See ``lib/display/README.md`` § "Cooperative multitasking & ``Token``".
        The token is read only to see whether another display call has expired it. If so, the scroll returns at that check and the display
        is not touched (no further frame is drawn). The display is left to that other call. If ``token`` is already expired on entry,
        the helper yields once and returns without drawing.

        With ``blank_edges=True`` the display starts empty, the content comes in from the right, leaves at the left, and, when the scroll runs
        through to its end, the display ends empty. With ``blank_edges=False`` the first column is already on the left-most LED, and the scroll
        stops when the last column reaches the right-most LED (content of ``WIDTH`` columns or fewer is a single still frame). If the scroll
        runs through to its end, that last frame stays lit and nothing is cleared. On a return where the scroll ran through to its end, the
        token is not expired. ``loop`` repeats the pass; the call then returns only when another display call expires the token.
        """
        sleep_ms = asyncio.sleep_ms
        if token.is_expired:
            await sleep_ms(0)
            return token
        ring = bytearray(WIDTH)
        # The ring starts all zero. If the user did NOT want to start and end with blank edges, we need to pre-fill the ring with text columns.
        if not blank_edges:
            for i in range(WIDTH):
                col = reader.next_column()
                if col is None:
                    break
                ring[i] = col
        # Now the ring elements [0, …, WIDTH-1] contain the columns we want to show on the first frame. After the first frame has been shown, we
        # scroll in the next column from the right; i.e. [1, …, WIDTH-1] contains the left-most columns and element ring[0] needs to be updated
        # with the new column from the reader, becoming the right-most column on the subsequent frame. We repeat until the reader is exhausted.
        while True:
            read_head = 0
            self._render_ring_window(ring, read_head, color)  # initial frame
            await sleep_ms(interval_ms)
            if token.is_expired:
                return token
            col = reader.next_column()
            while col is not None:
                ring[read_head] = col
                read_head += 1
                if read_head == WIDTH:
                    read_head = 0
                self._render_ring_window(ring, read_head, color)
                await sleep_ms(interval_ms)
                if token.is_expired:
                    return token
                col = reader.next_column()
            # The reader is exhausted. If the shift loop ran, the frame just shown has the last content column on the right-most LED. If it did not run, the initial frame is still showing.
            if blank_edges:
                for _ in range(WIDTH):
                    ring[read_head] = 0
                    read_head += 1
                    if read_head == WIDTH:
                        read_head = 0
                    self._render_ring_window(ring, read_head, color)
                    await sleep_ms(interval_ms)
                    if token.is_expired:
                        return token
            if not loop:
                return token
            reader.reset()
            # When looping, we need to re-initialize the buffer. Note: if ``blank_edges`` is True, then the buffer starts and ends in a state
            # where all elements are zero. In other words, only if ``blank_edges`` is False, the buffer needs re-initialization.
            if not blank_edges:
                # In most cases, we just read WIDTH columns from the reader and write them to the buffer. However, if the reader has k < WIDTH columns, then
                # it is guaranteed that the remaining columns [k, …, WIDTH-1] in the ring are already zero. Reasoning: in this case the pre-initialization
                # logic at the top only filled elements [0, …, k-1] in the ring, while the remaining elements remained zero. Further, we know that the reader
                # has no more columns to read, so the loop ``while col is not None`` that writes to ``ring`` does not run, leaving ``ring`` unmodified.
                for i in range(WIDTH):
                    col = reader.next_column()
                    if col is None:
                        break
                    ring[i] = col

    async def scroll_string(
        self,
        text: str | ScreenText,
        color: RGBcolor = WHITE,
        *,
        interval_ms: int = 150,
        loop: bool = False,
        blank_edges: bool = True,
    ) -> Token:
        """Scroll ``text`` across the display, one column every ``interval_ms`` milliseconds.

        Always pass the interval by name, for example ``interval_ms=150``. Without the name the call raises
        ``TypeError``. ``interval_ms=0`` still lets other ready tasks run once between frames.

        With the default ``blank_edges=True``, the display starts empty. The text comes in at the right-most LED, moves left, leaves at the left-most LED, and
        the display ends empty. With ``blank_edges=False``, the first frame already shows the text's first column on the left-most LED. The text moves left and
        stops when its last column reaches the right-most LED. When the scroll runs through to its end, it stops on its last frame, which stays on the display
        until another call replaces it: a blank display with ``blank_edges=True``, and the text's final window with ``blank_edges=False``.

        Text of ``WIDTH`` columns or fewer does not move with ``blank_edges=False``: its first frame is also its last. With ``blank_edges=True`` it still
        scrolls in and out like any other. With ``loop=True`` and ``blank_edges=False``, such text is simply drawn again and again until another
        display call takes over.

        With ``loop=True``, the scroll repeats until another display call takes over and only at that point, ``scroll_string`` returns (leaving the display to
        the other caller). So the first line below never finishes, and the code after it never runs. To keep your program going, run the scroll as a background
        task and stop it later with any other display call, such as ``clear()``:

            await display.scroll_string("Hello", loop=True)  # never returns

            task = asyncio.create_task(display.scroll_string("Hello", loop=True))  # runs alongside the rest of your program
            ...
            display.clear()  # takes over the display: the scroll stops and its task ends

        ``text`` may be a Python ``str`` or a ``ScreenText``. A plain ``str`` is the easy choice for text you scroll once.
        A ``ScreenText`` remembers how many columns the text needs. Pass ``centered(text)`` when each frame should
        show the centered picture instead.

        The display is not cleared after the scroll ends. To clear it after a scroll that ends on a lit frame (``blank_edges=False``), check the token this call
        returns first. If the token is expired, another display call has taken over the display, and ``clear()`` would erase its picture. Example:

            token = await display.scroll_string("Hello", blank_edges=False)
            if not token.is_expired:
                display.clear()

        To show text without scrolling it (text wider than the display is cut off), use ``render_string`` (it stays until the next display call) or
        ``show_string`` (it stays for a set time).

        Raises ``TypeError`` if ``interval_ms`` is not an integer, and ``ValueError`` if ``interval_ms < 0``, before the display changes.
        """
        reader = _reader_for(text)
        token = self._ensure_non_negative_duration_and_acquire("scroll_string", "interval_ms", interval_ms)
        await self._scroll_text(token, reader, color, interval_ms, loop, blank_edges)
        token._complete_unless_expired()
        return token

    async def scroll_number(
        self,
        n: int | float,
        color: RGBcolor = WHITE,
        *,
        interval_ms: int = 150,
        loop: bool = False,
        blank_edges: bool = True,
    ) -> Token:
        """Scroll ``n`` across the display, as ``str(n)``, one column every ``interval_ms`` milliseconds.

        Always pass the interval by name, for example ``interval_ms=150``. Without the name the call raises
        ``TypeError``. ``interval_ms=0`` still lets other ready tasks run once between frames.

        With the default ``blank_edges=True``, the display starts empty. The number comes in at the right-most LED, moves left, leaves at the left-most LED, and
        the display ends empty. With ``blank_edges=False``, the first frame already shows the number's first column on the left-most LED. The number moves left
        and stops when its last column reaches the right-most LED. When the scroll runs through to its end, it stops on its last frame, which stays on the
        display until another call replaces it: a blank display with ``blank_edges=True``, and the number's final window with ``blank_edges=False``.

        A number of ``WIDTH`` columns or fewer does not move with ``blank_edges=False``: its first frame is also its last. With ``blank_edges=True`` it still
        scrolls in and out like any other. With ``loop=True`` and ``blank_edges=False``, such a number is simply drawn again and again until another
        display call takes over.

        With ``loop=True``, the scroll repeats until another display call takes over and only at that point, ``scroll_number`` returns (leaving the display to
        the other caller). So the first line below never finishes, and the code after it never runs. To keep your program going, run the scroll as a background
        task and stop it later with any other display call, such as ``clear()``:

            await display.scroll_number(12345, loop=True)  # never returns

            task = asyncio.create_task(display.scroll_number(12345, loop=True))  # runs alongside the rest of your program
            ...
            display.clear()  # takes over the display: the scroll stops and its task ends

        The display is not cleared after the scroll ends. To clear it after a scroll that ends on a lit frame (``blank_edges=False``), check the token this call
        returns first. If the token is expired, another display call has taken over the display, and ``clear()`` would erase its picture. Example:

            token = await display.scroll_number(12345, blank_edges=False)
            if not token.is_expired:
                display.clear()

        To show a number without scrolling it (numbers wider than the display are cut off), use ``render_number`` (it stays until the next display call) or
        ``show_number`` (it stays for a set time).

        Raises ``TypeError`` if ``interval_ms`` is not an integer, and ``ValueError`` if ``interval_ms < 0``, before the display changes.
        """
        reader = _reader_for(str(n))
        token = self._ensure_non_negative_duration_and_acquire("scroll_number", "interval_ms", interval_ms)
        await self._scroll_text(token, reader, color, interval_ms, loop, blank_edges)
        token._complete_unless_expired()
        return token

    async def hold(self, duration_ms: int) -> Token:
        """Keep the picture that is on the display for ``duration_ms`` milliseconds, then return.

        ``hold`` does not draw anything, and it does not wipe the display afterwards. Use it after a ``render_*`` call to keep that
        picture up for a set time:

            display.render_number(7)
            await display.hold(2000)  # the 7 stays up for 2 seconds and is not wiped afterwards

        Calling ``hold`` takes over the display. A scroll or ``show_*`` that is still running stops, and the picture it had drawn stays up.
        If another display call takes over during the wait, ``hold`` returns at that point (leaving the display to the other caller).

        The returned token tells you which of the two happened: ``token.was_completed`` is True if the whole wait passed, and False if
        another display call cut it short. It stays True even if another display call takes over later (``token.is_expired`` is then True).

        Raises ``TypeError`` if ``duration_ms`` is not an integer, and ``ValueError`` if ``duration_ms < 0``, before the display changes.
        """
        token = self._ensure_non_negative_duration_and_acquire("hold", "duration_ms", duration_ms)
        await _sleep_pollable(token, duration_ms)
        token._complete_unless_expired()
        return token

    @staticmethod
    async def repeat_until_cancelled(callback: Callable[[], Awaitable[None] | None], sleep_between_ms: int = 10) -> NoReturn:
        """Call ``callback`` again and again, until the task executing ``repeat_until_cancelled`` is cancelled.

        Another display operation (for example from a button handler) does not stop it: the next
        round simply draws over whatever was shown in between. If you want a repeat that stops
        when something else takes over the display, use ``loop=True`` on the ``scroll_*`` methods.

        Use this when you want to repeat a task, for example showing a message over and over. You give
        ``repeat_until_cancelled`` a function that takes no arguments. It calls that function, waits for it
        to finish, rests for ``sleep_between_ms`` milliseconds, and then calls it again.

        The ``callback`` can be a normal ``def`` function or an ``async def`` (a function that
        uses ``await``). If it is an ``async def`` function, ``repeat_until_cancelled`` waits until it is done.

        Say you want to repeat this function:

            async def say_hello():
                await display.show_string("Hello", duration_ms=500)

        Pass the function itself, ``repeat_until_cancelled(say_hello)``, without parentheses: it is
        ``repeat_until_cancelled`` that calls ``say_hello``, once per round. Just for comparison, with
        ``say_hello()`` Python would call it on the spot and pass on what that returns. Essentially
        ``say_hello()`` produces a coroutine that can run only once. In comparison, ``say_hello`` is the
        recipe for producing such a coroutine, and can be used arbitrarily many times.

        ``repeat_until_cancelled`` is itself ``async`` and it never returns on its own. So the code you write after it, in the
        same place, never runs, unless you start ``repeat_until_cancelled`` as a task (way 3 below). There are three ways:

            # 1. In the main part of your program, outside any async function, as its last line.
            #    No code after this line will ever run, so use it only when repeating is the whole program:
            asyncio.run(display.repeat_until_cancelled(say_hello))

            # 2. Inside an async function. The rest of this function will never run, but your
            #    other tasks (for example button handlers) keep running:
            await display.repeat_until_cancelled(say_hello)

            # 3. Inside an async function, as a task. The function carries on while
            #    ``repeat_until_cancelled`` repeats, and you can stop it later:
            task = asyncio.create_task(display.repeat_until_cancelled(say_hello))
            await asyncio.sleep(10)  # ...do other things, for example wait for a button press
            task.cancel()            # stops ``repeat_until_cancelled`` at its next ``await``

        Cancelling stops ``repeat_until_cancelled`` and the ``callback`` that is running at that moment, and
        leaves whatever is on the LEDs lit. Call ``display.clear()`` afterwards if you want the display cleared.

        After each round, ``repeat_until_cancelled`` rests for ``sleep_between_ms`` milliseconds
        (a whole number of milliseconds). The time from one start to the
        next is the time ``callback`` takes plus this rest. The rest lets your other tasks (for example
        button handlers) run, even when ``callback`` finishes quickly. If your callback already waits
        (for example ``show_string`` or ``hold``), the rest is not needed, but by default it is so
        short (10 ms) that you will probably not notice. Set ``sleep_between_ms=0`` only if the repeat
        must be as fast or as regular as your own callback makes it, for example a repeat every
        1000 ms. Even with ``0``, other ready tasks still get one turn per round.

        Only one task runs at a time, and it keeps going until it reaches an ``await``. Tasks
        that are ready to run will get their turn, but they have to wait until your ``callback``
        reaches its next ``await``. So keep your callback short and let it ``await`` often, or
        other tasks (such as button handlers) will react late.

        Raises ``TypeError`` if ``sleep_between_ms`` is not an integer, and ``ValueError`` if it is negative. Because ``repeat_until_cancelled``
        never returns, the only ways out are an exception in ``callback`` or cancelling
        the task executing ``repeat_until_cancelled``.
        """
        # Maintainer note, why times must be integers: `asyncio.sleep_ms` adds its argument to a tick count and hands the sum to the scheduler
        # as the wake-up time. The C task queue (`_asyncio`) reads that time as a small int and only asserts it, so float wake-up times could
        # silently mis-order tasks (inferred from the 10.3.0 source, not tried on the board). Check once, before the loop.
        _ensure_non_negative_duration("repeat_until_cancelled", "sleep_between_ms", sleep_between_ms)
        while True:
            result = callback()
            if hasattr(result, "__await__"):
                await result
            await asyncio.sleep_ms(sleep_between_ms)


# Singleton — ``from display import display``
display = Display()

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
                   show_string, show_number, pause, repeat_until_cancelled.  Require ``await`` from
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
* Every Tier 2 method returns a ``Token``; check ``token.is_expired`` to see
  whether a later display operation has since superseded it. Tier 1
  methods (and ``deinit``) do not return a token — there is nothing to
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

import board
from adafruit_ticks import ticks_add, ticks_diff, ticks_ms
import neopixel
from rainbowio import colorwheel  # noqa: F401 — re-export for user convenience

from ._constants import WIDTH, HEIGHT, NUM_PIXELS, WHITE, OFF
from .geometry import build_lut
from .text_layout import ScreenText, _reader_for, _wider_than
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
# Implementation note: ``Image``'s internals (``_scroll_image`` /
# ``_render_window``) take the acting ``Display``
# instance as an explicit parameter. An ``Image`` has no fixed display of
# its own; it renders to whichever ``Display`` calls it.
# ---------------------------------------------------------------------------
class Image:
    """Bitmap image for the LED matrix.

    An image is always ``HEIGHT`` rows tall (see property ``height``). Its width (see
    property ``width``) is independent of the display and may be smaller, equal to,
    or **larger** than the ``WIDTH`` physical columns of the LED matrix.
    ``Image(pattern)`` accepts any width (the widest kept row).
    Short rows are padded with OFF.
    An image can be monochrome (one shared color, recolorable via ``recolor``)
    or multi-color (a fixed color per pixel, ``recolor`` is no-op).
    An image wider than the display is shown a ``WIDTH``-column window at a
    time: ``Display.show_image(offset)`` picks the window; image
    columns outside that window are trimmed.
    ``Display.scroll_image`` scrolls the Image across the display. Where the
    display window overhangs the image (a narrower image, or an ``offset``
    past an edge), the uncovered display columns render as ``OFF``.
    """

    # Implementation notes:
    # Internally (see ``columns``): monochrome images store column-major bytes
    # plus one RGB color; multi-color images store a flat per-pixel RGB sequence.

    __slots__ = ("_data", "_width", "_multi", "_color")

    def __init__(
        self,
        pattern_str: str,
        color: RGBcolor | ColorDict = WHITE,
    ) -> None:
        """Parse a pattern string into an Image.

        If ``color`` is a single RGB tuple ``(red, green, blue)``:
        the entire image is drawn in that color, with illuminated pixels marked by ``#``.
        If a dictionary ``{character: RGB tuple}`` is given for the input ``color``,
        then characters such as ``G`` or ``c`` in the pattern stand for colors.
        You set each character's RGB tuple in ``color``, for example ``color["G"] = (0, 255, 0)``.
        Keep the Image and pass it to ``show_image`` or ``scroll_image`` again.

        Rows past ``HEIGHT`` are dropped; short rows or columns are padded with OFF.
        Image width is the widest of the rows (ignoring rows beyond``HEIGHT``).
        Unknown chars in mono mode render as OFF. Spaces and other invisible characters are
        skipped, so ``#`` marks close up around them. ``render_pattern`` skips only space,
        tab, and carriage return; anything else stays a pixel, off when it is not ``#``.
        """
        # Internal encoding: mono images store column-major bytes (one byte
        # per column, bit y = row y counted from top); multi-color stores a flat
        # tuple of per-pixel RGB tuples. Conversion happens here so render methods
        # do not re-parse on each call.
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

    async def _scroll_image(self, disp: Display, step: int = 1, interval_ms: int | float = 200) -> Token:
        """Internal implementation backing ``Display.scroll_image``.

        Scroll through the image, advancing ``step`` columns per frame, with ``interval_ms`` milliseconds between frames.
        ``step`` is how many image columns scroll in from the right each frame. The scroll always starts at position 0.
        Every ``interval_ms``, ``step`` image columns scroll in, until the last column of the image has appeared.
        If ``step`` is greater than 1, that last step might need to pad with empty columns after the last image column.
        Negative ``step`` is not yet supported.

        If a subsequent operation acquires the display before the scroll completes, this method returns after the
        current frame's ``interval_ms`` sleep; check the returned ``Token``'s ``is_expired`` to tell whether
        the wait was cut short by another task.

        ``disp`` is the ``Display`` instance to render to.

        Raises ``ValueError`` if ``step <= 0``. Reverse scrolling (negative ``step``) is not yet supported.
        A negative ``interval_ms`` waits 0 ms between frames, the same as ``interval_ms=0``.
        That wait still lets other tasks that are ready run once before the next frame.
        """
        if step <= 0:
            # TODO: allow step < 0 for bi-directional (right-to-left) scrolling.
            raise ValueError(f"step must be > 0, got {step}")
        token = disp._acquire()
        # Each frame, ``step`` image columns scroll in from the right. ``image_columns_to_scroll_in``
        # is how many image columns start off the right edge of the screen.
        # Scrolling continues in full steps of ``step`` until that column has come in.
        # A last step might need to pad with empty columns after that column.
        image_columns_to_scroll_in = max(0, self._width - WIDTH)
        columns_scrolled = 0
        # Once before the loop we do a potential type conversion, e.g. if a float is passed
        # then ``int`` truncates decimal places (for example, 0.9 becomes 0).
        interval_ms = int(interval_ms)
        sleep_ms = asyncio.sleep_ms
        while True:
            if token.is_expired:
                return token
            self._render_window(disp, columns_scrolled)
            await sleep_ms(interval_ms)
            if columns_scrolled >= image_columns_to_scroll_in:
                return token
            columns_scrolled += step

    def _render_window(self, disp: Display, offset: int) -> None:
        """Render a WIDTH-column window of this image at ``offset`` into ``disp``'s pixel buffer and show().

        ``disp`` is the ``Display`` instance to render to.

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
# Cancellation-aware sleep helpers. Operate only on a ``Token``, with no
# dependency on any ``Display`` instance's state -- callers pass whichever
# token they are holding.
# ---------------------------------------------------------------------------


def _check_ms(method: str, param: str, value: int | float) -> int:
    """Reject a negative duration, then truncate to whole milliseconds.

    ``method`` is the name of the public ``Display`` method that was called and ``param`` is its
    parameter holding ``value``. Both only appear in the error message, for example
    ``show_image(): duration_ms must be >= 0, got -5``.
    Runs before the display is taken over. A float is truncated (``1.9`` becomes ``1``).
    """
    if value < 0:
        raise ValueError(f"{method}(): {param} must be >= 0, got {value}")
    return int(value)


async def _sleep_pollable(token: Token, total_ms: int | float, poll_ms: int = 47) -> None:
    """Sleep up to ``total_ms`` milliseconds, returning early once ``token.is_expired``.

    Chunks the sleep into at most ``poll_ms``-sized pieces so a caller notices
    a superseding display operation within ``poll_ms``, not only after the full
    ``total_ms`` has elapsed. When not cancelled, the total elapsed time still converges
    to ``total_ms`` (the final chunk is the time still left, never overshooting).

    A ``total_ms ≤ 0`` allows once for other coroutines to run (we call ``asyncio.sleep_ms(0)``)
    before this function returns. If no pause is desired, please use a synchronous Tier 1 method, which
    returns in the same call, so those other coroutines must wait until the caller itself pauses.
    """
    # Once before the loop we do a potential type conversion, e.g. if a float is passed
    # then ``int`` truncates decimal places (for example, 0.9 becomes 0).
    total_ms = int(total_ms)
    if total_ms <= 0:
        await asyncio.sleep_ms(0)  # passing a negative value is safe and behaves exactly like 0 and still yields once.
        return
    deadline = ticks_add(ticks_ms(), total_ms)
    while True:
        if token.is_expired:
            return
        remaining = ticks_diff(deadline, ticks_ms())
        if remaining <= 0:
            return
        if remaining <= poll_ms:
            await asyncio.sleep_ms(remaining)
            return
        await asyncio.sleep_ms(poll_ms)


async def _sleep_until_cancelled(token: Token, poll_ms: int = 51) -> None:
    """Sleep in ``poll_ms``-sized chunks until ``token.is_expired``.

    A negative ``poll_ms`` waits 0 ms per chunk but still yields once.
    Each chunk still lets other tasks that are ready run once.
    """
    poll_ms = int(poll_ms)
    while not token.is_expired:
        await asyncio.sleep_ms(poll_ms)


def _write_column(pixels: neopixel.NeoPixel, lut: bytearray, x_base: int, col_byte: int, color: RGBcolor, off: RGBcolor) -> None:
    """Write one column byte at logical column ``x_base // HEIGHT``. Bit 0 is the top row."""
    for y in range(HEIGHT):
        pixels[lut[x_base + y]] = color if (col_byte >> y) & 1 else off


# ---------------------------------------------------------------------------
# Display class
# ---------------------------------------------------------------------------
class Display:
    """Controls the 5×5 WS2812 NeoPixel matrix.

    Use the module-level ``display`` instance for normal use. Starting any
    display-mutating operation cancels any Tier 2 animation in progress.
    Non-cancelling methods: ``get_pixel``, ``set_brightness``,
    ``set_rotation``. See the module docstring for the full cancellation
    policy.

    Each ``Display`` owns its own NeoPixel buffer, coordinate LUT, and
    cancellation token (``self._pixels`` / ``self._lut`` / ``self._token``).
    Constructing a ``Display`` instance claims the data pin's RMT peripheral.
    Constructing a *second* instance while an existing one is still live raises
    (the pin is already claimed); call ``deinit()`` on the existing instance first
    to free it, then construct a new ``Display()``. See ``lib/display/README.md``
    § "Singleton design & ``deinit``" for the package's rationale for
    exposing one ready-made ``display`` instance.
    """

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

        Expires the previous token (its ``is_expired`` becomes True) and
        creates a new one which is then returned. Any Tier 2 animation
        holding the previous token will see its ``is_expired`` become True
        on its next check, and should return early. Called internally by
        every display-mutating method.
        """
        self._token._is_expired = True  # module-internal write; public side is read-only
        self._token = Token()
        return self._token

    # — Render primitives (hot path, called by Tier 1/2 render methods) ------

    def _write_pattern_on_the_fly(
        self,
        pattern: str,
        color: RGBcolor | ColorDict,
    ) -> None:
        """Write ``pattern`` into this instance's pixel buffer: parsing and drawing fused in one scan of the string.

        Scan the source string once, skip only space / tab / CR, write each cell
        directly to this instance's NeoPixel buffer, ignore columns past ``WIDTH``,
        ignore rows past ``HEIGHT``, pad short / missing rows with ``OFF``. No
        per-row string allocation and no generator.

        Does not call ``show()``. The caller flushes the buffer after invocation.

        The mono / dict shape of ``color`` is hoisted to a top-level branch so
        the per-cell write has no shape check per cell. The two branches share
        the same state-machine structure with one differing line (cell write);
        closure / callback indirection at the cell-write site would re-introduce
        per-cell call overhead and defeat the hoist.
        """
        pixels = self._pixels
        lut = self._lut
        off = OFF
        width = WIDTH
        height = HEIGHT
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
            # rows with non-whitespace characters, up to and including the trailing newline.
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

    def _render_colmajor(
        self,
        data: bytes,
        offset: int,
        color: RGBcolor,
    ) -> None:
        """Render WIDTH column bytes from ``data`` starting at ``data[offset]`` to this instance's ``self._pixels``.

        Each byte ``data[offset + x]`` for x=0, 1,…, WIDTH-1 is drawn as one column (i.e. a single
        byte representing one column of the bitmap). Bit ``y`` of the byte selects the pixel at display
        row ``y`` (with bit 0 = top row).
        On the hardware level, the LEDs are addressed using a single index. The Look-Up Table
        [``lut``] translates from logical pixels (x, y) to the physical strip index. The ``lut``
        is organized using x-major convention, i.e. ``lut[x * HEIGHT + y]`` returns the physical
        strip index for the logical pixel (x, y).
        After all pixel values have been written, then we call ``show()`` once.

        Reads this instance's own buffer and LUT (``self._pixels`` / ``self._lut``).

        CAUTION: this method is part of the hot path and used to render many icons;
        especially for scrolling this code is performance sensitive.
        """
        # Cache attribute reads into locals before the loop: LOAD_FAST (frame-slot access) is cheaper than a
        # repeated LOAD_ATTR (self._pixels/self._lut) or LOAD_GLOBAL (OFF) lookup per pixel. LOAD_FAST-vs-LOAD_GLOBAL
        # is AI-verified in MicroPython's VM (`py/vm.c` MP_BC_LOAD_FAST_N / MP_BC_LOAD_GLOBAL, `py/runtime.c`
        # mp_load_global); the LOAD_ATTR case is assumed analogous (also a dict-style lookup) but not separately
        # re-verified.
        pixels = self._pixels
        lut = self._lut
        off = OFF
        x_base = 0  # invariant at top of loop: x_base == x * HEIGHT (`geometry.build_lut` slot convention)
        for x in range(WIDTH):
            _write_column(pixels, lut, x_base, data[offset + x], color, off)
            x_base += HEIGHT  # advance to next column; addition avoids a per-column multiply
        pixels.show()

    def _draw_text(self, reader: _ColumnReader | _FixedColumnReader, x: int, color: RGBcolor) -> None:
        """Draw ``reader`` with its first column at display column ``x``. One ``show()``.

        ``x < 0`` skips ``-x`` content columns and starts at display column 0.
        Columns before the start, and columns after the reader ends, are off.
        ``next_column`` returning ``None`` is a blank column; later calls stay ``None``.
        """
        pixels = self._pixels
        lut = self._lut
        off = OFF
        if x < 0:
            reader.skip(-x)
            start = 0
        else:
            start = WIDTH if x > WIDTH else x  # deliberately not ``min(x, WIDTH)``: the builtin call costs more than a compare on the MCU VM.
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
        """Render a WIDTH-sized ring buffer as a left-to-right window starting at ``read_head``.
        IMPORTANT: ``read_head`` must be in 0..WIDTH-1!

        The ring holds exactly ``WIDTH`` column bytes; ``read_head`` is the index
        of the leftmost visible column. Wrap is handled by splitting the draw
        into two loops (``read_head`` to the end, then the start up to ``read_head``),
        with no per-column modulo, subtraction or compare (cheaper on the MCU VM).

        Reads ``self._pixels`` / ``self._lut`` fresh on every call, not cached
        once per animation. This is one of the three facts (alongside
        set_rotation's in-place mutation and asyncio's cooperative scheduling)
        that make rotating mid-scroll safe. See README.md § "Rotation during an
        in-flight Tier 2 animation".
        """
        pixels = self._pixels
        lut = self._lut
        off = OFF
        x_base = 0  # invariant at top of loop: x_base == x * HEIGHT
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
    ) -> None:
        """Draw a pattern string straight onto the LEDs.
        Best for a picture you show once, because this method needs to go over the input string
        and decode every character into a pixel (this is called "parsing" the pattern).
        For pictures you want to show repeatedly, it is best to only parse the pattern once,
        which is done by constructing an ``Image(pattern)`` or an ``Icon(pattern)``. Each is
        a parsed Image / Icon, whose reference you can keep and show repeatedly.

        Each line of the pattern is one row of the picture, starting at the top left corner of the
        LED matrix. A row with fewer than 5 characters is filled with off pixels on the right.
        Extra characters on the right, and rows past the bottom of the screen, are cut off.
        Missing rows at the bottom are off.

        If ``color`` is an RGB tuple ``(red, green, blue)``, every ``#`` is an LED lit in that color
        and every other character is off, so ``#.#`` shows "on, off, on". The default color is white.
        If ``color`` is a dict ``{character: RGB tuple}``, you can specify different letters to represent
        different colors, such as ``color["G"] = (0, 255, 0)`` for green and ``color["R"] = (255, 0, 0)``
        for red (and so on). Then, writing ``G.RG`` shows "green, off, red, green". Any character that
        is not in the dict represents off.

        Spaces, tabs and carriage returns are skipped, so ``#.#`` and ``# .  #`` are the same picture.
        Any other character takes one column.
        """
        self._acquire()
        # Direct render via LUT — no intermediate column-major buffer. Fused one-pass scan.
        self._write_pattern_on_the_fly(pattern, color)
        self._pixels.show()

    def render_icon(self, icon: Icon, color: RGBcolor = WHITE) -> None:
        """Render an ``Icon`` (e.g. ``Emojis.HEART``) to the LEDs.
        The icon is shown in the provided ``color`` (white by default), which must be
        explicitly stated because an ``Icon`` carries no color of its own.
        """
        self._acquire()
        self._render_colmajor(icon._columns, 0, color)

    def render_arrow(self, arrow: Icon, color: RGBcolor = WHITE) -> None:
        """Render an ``Icon`` from the arrow catalog (e.g. ``Arrows.NORTH``) to the LEDs.

        The icon is shown in the provided ``color`` (white by default), which must be
        explicitly stated because an ``Icon`` carries no color of its own.
        """
        # Body of ``render_icon`` repeated on purpose: saves one method lookup and call. Keep the two in sync.
        self._acquire()
        self._render_colmajor(arrow._columns, 0, color)

    def render_string(self, text: str | ScreenText, color: RGBcolor = WHITE) -> None:
        """Draw ``text`` left-aligned and leave it lit until some other call overwrites the display.
        Text wider than the display is cropped on the right. To scroll longer text, call ``show_string``.

        ``text`` may be a Python ``str`` or a ``ScreenText``. An empty string draws a blank screen.

        A plain ``str`` is the easy choice for text you draw once. A ``ScreenText`` is pre-prepared text:
        it counts how many columns the text needs (its ``width``) the first time you ask, and remembers
        the answer. Use ``ScreenText`` when you draw the same text again and again, or when you want to
        check ``width`` against the display before you choose how to show the text.

        Pass ``centered(text)`` when the text should sit in the middle. ``centered(text)`` returns a
        ``ScreenText`` too, so create it once and reuse it if you want to show the centered text repeatedly.
        """
        self._acquire()
        self._draw_text(_reader_for(text), 0, color)

    def render_number(self, n: int | float, color: RGBcolor = WHITE) -> None:
        """Converts number ``n`` into a string (via python's ``str(n)``) and displays it
        starting at the left-most LED, and leaves it lit until some other call overwrites the display.

        A number wider than the screen shows its first columns and crops the rest.
        To scroll longer numbers, call ``show_string``.
        """
        self.render_string(str(n), color)

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

    def render_filled(self, color: RGBcolor = WHITE) -> None:
        """Fill all pixels with ``color``."""
        self._acquire()
        self._pixels.fill(color)
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

        ``degrees`` must be one of ``0``, ``90``, ``180``, ``270`` or their counter-clockwise equivalents
        ``-270``, ``-180``, ``-90``. Other values raise ``ValueError``. Out-of-range inputs (``360``,
        ``-360``, ...) are rejected; normalise at the call site (e.g. ``set_rotation(d % 360)``) if wrap-around
        is needed.
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
        """Release the NeoPixel hardware (RMT peripheral + data pin).

        Cancels any ongoing animation, then deinitializes the underlying NeoPixel buffer. After this call *this instance*
        is unusable and it must be discarded (any further render call on it raises an error). There is no re-init path
        *on this instance* — but the pin is now free, so a fresh ``Display()`` may be constructed afterward (it will claim
        the pin again and start with a clean buffer/LUT/token; it is unrelated to and does not resurrect this deinitialized
        instance). This is a teardown hook for code that wants to free the data pin / RMT peripheral for other use (e.g.
        before a soft reboot, to hand the pin to a different peripheral, or to restart the display with new hardware
        config). See ``lib/display/README.md`` § "Singleton design & ``deinit``" for the module-level ``display``
        singleton's rationale.
        """
        self._acquire()
        self._pixels.deinit()

    # — Tier 2: Async MakeCode-compatible methods ---------------------------

    async def _hold_then_blank(self, token: Token, duration_ms: int) -> Token:
        """Wait ``duration_ms``, then turn every LED off IF AND ONLY IF this call still owns the display.

        This function does not take over the display (i.e. it does not cancel any ongoing Tier 2 operation).
        A call that superseded this one leaves its own picture up.
        """
        await _sleep_pollable(token, duration_ms)
        if not token.is_expired:
            self._pixels.fill(OFF)
            self._pixels.show()
        return token

    async def show_pattern(
        self,
        pattern: str,
        color: RGBcolor | ColorDict = WHITE,
        *,
        duration_ms: int | float,
    ) -> Token:
        """Draw a pattern, hold it for ``duration_ms`` milliseconds, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call
        raises ``TypeError``. This call's picture stays up for the hold duration. A later display call during the hold
        replaces it, and this call's token expires. ``duration_ms=0`` draws the pattern, lets other ready tasks run
        once, then blanks, which is probably just a short flicker.

        If ``color`` is an RGB tuple, every ``#`` is an LED lit in that color and every other character is off.
        If ``color`` is a dict ``{character: RGB tuple}``, each listed character lights its LED in the given color
        and any character not in the dict is off. Spaces, tabs and carriage returns are skipped; any other character
        takes one column. See ``render_pattern`` for more detailed examples.

        Raises ``ValueError`` if ``duration_ms < 0``, before the display changes.
        """
        duration_ms = _check_ms("show_pattern", "duration_ms", duration_ms)
        self.render_pattern(pattern, color)
        return await self._hold_then_blank(self._token, duration_ms)

    async def show_icon(self, icon: Icon, color: RGBcolor = WHITE, *, duration_ms: int | float) -> Token:
        """Draw an ``Icon`` (e.g. ``Emojis.HEART``), hold it for ``duration_ms`` milliseconds, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call
        raises ``TypeError``. This call's picture stays up for the hold duration. A later display call during the hold
        replaces it, and this call's token expires. ``duration_ms=0`` draws the icon, lets other ready tasks run once,
        then blanks, which is probably just a short flicker.

        Raises ``ValueError`` if ``duration_ms < 0``, before the display changes.
        """
        duration_ms = _check_ms("show_icon", "duration_ms", duration_ms)
        self.render_icon(icon, color)
        return await self._hold_then_blank(self._token, duration_ms)

    async def show_arrow(self, arrow: Icon, color: RGBcolor = WHITE, *, duration_ms: int | float) -> Token:
        """Draw an arrow ``Icon`` (e.g. ``Arrows.NORTH``), hold it, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call
        raises ``TypeError``. This call's picture stays up for the hold duration. A later display call during the hold
        replaces it, and this call's token expires. ``duration_ms=0`` draws the arrow, lets other ready tasks run
        once, then blanks, which is probably just a short flicker.

        Raises ``ValueError`` if ``duration_ms < 0``, before the display changes.
        """
        duration_ms = _check_ms("show_arrow", "duration_ms", duration_ms)
        self.render_arrow(arrow, color)
        return await self._hold_then_blank(self._token, duration_ms)

    async def show_filled(self, color: RGBcolor = WHITE, *, duration_ms: int | float) -> Token:
        """Fill the display with ``color``, hold it for ``duration_ms`` milliseconds, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call
        raises ``TypeError``. This call's picture stays up for the hold duration. A later display call during the hold
        replaces it, and this call's token expires. ``duration_ms=0`` fills the display, lets other ready tasks run
        once, then blanks, which is probably just a short flicker.

        Raises ``ValueError`` if ``duration_ms < 0``, before the display changes.
        """
        duration_ms = _check_ms("show_filled", "duration_ms", duration_ms)
        self.render_filled(color)
        return await self._hold_then_blank(self._token, duration_ms)

    async def show_image(self, image: Image, offset: int = 0, *, duration_ms: int | float) -> Token:
        """Show a ``WIDTH``-column window of ``image``, hold it for ``duration_ms`` milliseconds, then turn the LEDs off.

        Always pass the hold time parameter by name, for example ``duration_ms=1000``. Without the name the call
        raises ``TypeError``. ``offset`` is the image column placed at display column 0. It may be negative or past
        the right edge; uncovered columns are off. This call's picture stays up for the hold duration. A later display
        call during the hold replaces it, and this call's token expires. ``duration_ms=0`` shows the window, lets
        other ready tasks run once, then blanks, which is probably just a short flicker.

        Raises ``ValueError`` if ``duration_ms < 0``, before the display changes.
        """
        duration_ms = _check_ms("show_image", "duration_ms", duration_ms)
        token = self._acquire()
        image._render_window(self, offset)
        return await self._hold_then_blank(token, duration_ms)

    async def scroll_image(self, image: Image, step: int = 1, interval_ms: int | float = 200) -> Token:
        """Scroll through ``image``, advancing ``step`` columns per frame, with ``interval_ms`` milliseconds between frames.

        ``step`` is how many image columns scroll in from the right each frame. The scroll always starts at position 0.
        Every ``interval_ms``, ``step`` image columns scroll in, until the last column of the image has appeared.
        If ``step`` is greater than 1, that last step might need to pad with empty columns after the last image column.
        Negative ``step`` is not yet supported.

        If a subsequent operation acquires the display before the scroll completes, this method returns after the
        current frame's ``interval_ms`` sleep; check the returned ``Token``'s ``is_expired`` to tell whether
        tell whether the wait was cut short by another task.

        Raises ``ValueError`` if ``step <= 0``. Reverse scrolling (negative ``step``) is not yet supported.
        A negative ``interval_ms`` waits 0 ms between frames, the same as ``interval_ms=0``.
        That wait still lets other tasks that are ready run once before the next frame.
        """
        return await image._scroll_image(self, step, interval_ms)

    async def show_string(
        self,
        text: str | ScreenText,
        color: RGBcolor = WHITE,
        interval_ms: int | float = 150,
        loop: bool = False,
    ) -> Token:
        """Scroll text across the display.

        The typical case where text is wider than ``WIDTH`` glyph-columns: we scroll
        one column every ``interval_ms`` (time duration measured in milliseconds). If
        ``loop`` is ``True``, keep scrolling indefinitely until cancelled by another
        display operation. A non-looping scroll ends exactly when the last non-empty
        column of the string has left the screen: the display is left fully blank.

        For text that fits on the display without scrolling (total width <= WIDTH),
        the text is drawn from the left-most LED and held for ``interval_ms * WIDTH`` milliseconds and the
        screen is then cleared. So a held text and a scrolled text of comparable width
        provide comparable time to read.
        ``interval_ms=0`` puts the text on the display and then immediately lets other
        tasks that are ready run once, and then clears the screen. How long the text stays
        up is however long those tasks take to run. That is often only a short flash.
        ``loop=True`` holds that picture until another display operation
        cancels the call, not interfeering with whatever that operation drew. The hold
        is the same for every ``interval_ms``.

        An empty string follows the same convention as text fitting on screen without
        scrolling: we just show a blank screen and hold it according to the definition of above

        If you want to display a letter or a number that stays on the screen indefinitely
        until overwritten call ``render_string`` or ``render_number``. In comparision,
        ``show_string`` is primarily focused on scrolling text across the display, with
        short text ommitting the scrolling just as a readability improvement.

        Raises ``ValueError`` if ``interval_ms < 0``: a negative delay has
        no sensible meaning here (see the class discussion of cold-call-
        site validation in ``CODING_PRINCIPLES.md``).
        Returns the cancellation ``Token`` (check ``token.is_expired`` to see
        whether a later display operation preempted this call).
        """
        interval_ms = _check_ms("show_string", "interval_ms", interval_ms)
        token = self._acquire()
        if isinstance(text, ScreenText):
            source: str | ScreenText = text
        else:
            source = str(text)

        # Text fits screen: width <= WIDTH (covers also empty string of zero columns). Draw from the left, the same helper as render_string.
        # Hold for interval_ms * WIDTH milliseconds, which is roughly similar to the hypothetical scroll time of the text; then clear the screen.
        # That all-off frame does not call _acquire, so this call's token stays the one minted above and is_expired stays false when nobody cancelled
        # the holding time. For interval_ms=0, the implementation behaves the same: _sleep_pollable awaits sleep_ms(0) once, other ready tasks each get
        # one turn to run (fifo scheduling), and when those other tasks are done running (i.e. `_sleep_pollable` returns) then the screen is cleared
        # immediately.
        # If loop=True, we hold for a constant short time, check for expiry and wait again if not expired, which is all done by
        # _sleep_until_cancelled(token).  This is deliberate, so interval_ms=0 with loop=True does not create a busy expirely polling loop.
        # Length bytes only, same spacer rule as the scroll. Stop once the text is wider than the screen.
        if not _wider_than(source, WIDTH):
            if token.is_expired:
                return token
            self._draw_text(_reader_for(source), 0, color)
            if loop:
                await _sleep_until_cancelled(token)
                return token
            await _sleep_pollable(token, interval_ms * WIDTH)
            if not token.is_expired:  # Every LED off
                self._pixels.fill(OFF)
                self._pixels.show()
            return token

        # Bound once. ``sleep_ms`` takes whole milliseconds, so the loop does no float math.
        sleep_ms = asyncio.sleep_ms  # passing a negative value is safe and behaves exactly like 0 and still yields once.
        reader = _reader_for(source)
        while True:
            reader.reset()  # loop=True scrolls this same reader again from the first column
            # Scroll loop memory: rather than materialising the whole scrolled bitmap, columns are fed one at a time from `reader` into a WIDTH-byte ring buffer.
            # The visible window is exactly WIDTH columns, so a ring that size is sufficient regardless of how long `text` is:
            # each newly arriving column overwrites the slot that just scrolled off the left edge. The initial all-zero ring is the scroll-in padding,
            # so the first frame renders as a fully blank display with the first column arriving from the right, rather than jumping straight to a partially-filled window.

            ring = bytearray(WIDTH)
            read_head = 0
            trailing_blanks = 0
            while True:
                if token.is_expired:
                    return token
                self._render_ring_window(ring, read_head, color)
                await sleep_ms(interval_ms)
                if token.is_expired:
                    return token
                col = reader.next_column()
                if col is None:
                    col = 0  # empty column
                    trailing_blanks += 1
                ring[read_head] = col
                read_head += 1
                if read_head == WIDTH:
                    read_head = 0
                # Scroll-out: once the reader drains, keep feeding blank columns
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
        n: int | float,
        color: RGBcolor = WHITE,
        interval_ms: int | float = 150,
        loop: bool = False,
    ) -> Token:
        """Show ``str(n)`` the same way as ``show_string``: the call blocks, takes time, and ends on a blank screen.

        A number that fits is held for ``interval_ms * WIDTH`` milliseconds, then the screen is cleared.
        A wider number scrolls. ``loop=True`` runs until another display operation cancels the call.
        For a number that stays lit, call ``render_number``.
        """
        # Implementation note: ``n`` is specified as a number. A str or a bool is unspecified. This body
        # passes ``str(n)`` through unchanged. Booleans will therefore render as "True" or "False" for example.
        return await self.show_string(str(n), color, interval_ms, loop)

    async def pause(self, duration_ms: int | float) -> Token:
        """Wait up to ``duration_ms`` milliseconds before returning. If a subsequent operation acquires the display
        before the wait elapses, this method returns immediately instead; check the returned ``Token``'s
        ``is_expired`` to tell whether the wait was cut short by another task.

        Raises ``ValueError`` if ``duration_ms < 0``.
        """
        # Not ``_check_ms``: it would truncate to ``int`` here, and ``_sleep_pollable`` truncates again right below.
        # So only the negative check is written out. Keep this message in the format of ``_check_ms``.
        if duration_ms < 0:
            raise ValueError(f"pause(): duration_ms must be >= 0, got {duration_ms}")
        token = self._acquire()
        await _sleep_pollable(token, duration_ms)
        return token

    @staticmethod
    async def repeat_until_cancelled(callback: Callable[[], Awaitable[None] | None], sleep_between_ms: int | float = 10) -> NoReturn:
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
                await display.show_string("Hello")

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
        (whole milliseconds: a fraction is dropped, so 25.9 means 25). The time from one start to the
        next is the time ``callback`` takes plus this rest. The rest lets your other tasks (for example
        button handlers) run, even when ``callback`` finishes quickly. If your callback already waits
        (for example ``show_string`` or ``pause``), the rest is not needed, but by default it is so
        short (10 ms) that you will probably not notice. Set ``sleep_between_ms=0`` only if the repeat
        must be as fast or as regular as your own callback makes it, for example a repeat every
        1000 ms. Even with ``0``, other ready tasks still get one turn per round.

        Only one task runs at a time, and it keeps going until it reaches an ``await``. Tasks
        that are ready to run will get their turn, but they have to wait until your ``callback``
        reaches its next ``await``. So keep your callback short and let it ``await`` often, or
        other tasks (such as button handlers) will react late.

        Raises ``ValueError`` if ``sleep_between_ms`` is negative. Because ``repeat_until_cancelled``
        never returns, the only ways out are an exception in ``callback`` or cancelling
        the task executing ``repeat_until_cancelled``.
        """
        # `sleep_between_ms` may be an `int` or a `float` (for example `1000 / 3` or `10.0`). `asyncio.sleep_ms` adds
        # its argument to a tick count and hands the sum to the scheduler as the wake-up time. The C task queue (`_asyncio`) reads that time as
        # a small int and only asserts it, so a float wake-up time could silently mis-order tasks (inferred from the 10.3.0 source, not tried on
        # the board). `_check_ms` rejects a negative value, then `int()` makes sure we always pass whole milliseconds. It truncates, it does not
        # round (25.9 becomes 25). Run it once as preprocessing of the loop.
        rest_ms = _check_ms("repeat_until_cancelled", "sleep_between_ms", sleep_between_ms)
        while True:
            result = callback()
            if hasattr(result, "__await__"):
                await result
            await asyncio.sleep_ms(rest_ms)


# Singleton — ``from display import display``
display = Display()

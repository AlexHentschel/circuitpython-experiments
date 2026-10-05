"""
Runtime display engine for the 5x5 WS2812 NeoPixel matrix (BPI-Bit-S2).

Owns the MakeCode-style 5×5 font (sibling ``font_makecode_5/`` spaced
table, laid out by ``text_layout``), and the ``Display``, ``Image``, and
``Icon`` classes. Each ``Display`` instance owns its own live NeoPixel
buffer and coordinate Look-Up Table [LUT] (populated via
``geometry.build_lut``).

Two-tier API:
  Tier 1 (sync):  render_pattern, render_icon, render_arrow, clear_screen,
                   set_pixel, fill, set_rotation, set_brightness, get_pixel.
  Tier 2 (async): show_pattern, show_icon, show_arrow, show_image, scroll_image,
                   show_string, show_number, pause.  Require ``await`` from
                   asyncio code.
  Lifecycle:      deinit — releases the data pin / RMT peripheral; *this instance*
                   is unusable afterwards (no re-init path on it), but the pin is
                   now free for a newly-constructed ``Display()``.

Cancellation policy:
* any display-mutating method cancels an in-progress
  Tier 2 animation, and starting a new Tier 2 animation cancels any earlier
  one. The exceptions are ``get_pixel`` (pure read), ``set_brightness``, and
  ``set_rotation``; in other words running animation is not disturbed when the
  user dims the matrix or rotates the frame.
* Consistent with the general rule of in-progress Tier 2 animation being cancelled
  by any display-mutating method, ``set_pixel`` and ``show_string`` also cancels a
  Tier 2 operation:
  - ``set_pixel`` leaves the display on the most recent frame only with the set pixel
    being updated. If the coordinate is outside the LED matrix, the latest frame is
    left unchanged and kept on the display.
  - ``show_string`` always replaces the matrix with the given string; an empty string
    present the blank frame on the display, the same fit-on-screen path
    as any other short string.
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
    from typing import Callable, NoReturn
except ImportError:
    pass

import asyncio

import board
from adafruit_ticks import ticks_add, ticks_diff, ticks_ms
import neopixel
from rainbowio import colorwheel  # noqa: F401 — re-export for user convenience

from ._constants import WIDTH, HEIGHT, NUM_PIXELS, WHITE, OFF
from .geometry import build_lut
from .text_layout import SpacedGlyphColumnFeeder
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


def color(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Convenience constructor mirroring Adafruit NeoMatrix's matrix.Color()."""
    return (r, g, b)


# ---------------------------------------------------------------------------
# Runtime pattern parsers:
#   - ``_iter_pattern_rows`` for cold path. Used by ``Image.create``,
#     ``Icon.create``. Lenient: collapses *all* Python whitespace via
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


def _iter_pattern_rows(pattern_str: str):
    """Yield normalized non-blank rows from a pattern — *cold-path* parser.

    Each emitted string has all Python whitespace (spaces, tabs, CRs, FFs,
    VTs) collapsed via ``"".join(raw.split())``, mirroring the design-time
    idiom in ``bitmap_codec.pattern_to_colmajor``. Blank lines (any amount
    of whitespace) are skipped.

    Cold-path callers: ``Image.create``, ``Icon.create``.
    Per-frame render uses ``Display._write_pattern_on_the_fly``.
    """
    for raw in pattern_str.split("\n"):
        row = "".join(raw.split())
        if row:
            yield row


# ---------------------------------------------------------------------------
# Image class
#
# Implementation note: ``Image``'s Tier 2 internals (``_show_image`` /
# ``_scroll_image`` / ``_render_window``) take the acting ``Display``
# instance as an explicit parameter. An ``Image`` has no fixed display of
# its own; it renders to whichever ``Display`` calls it.
# ---------------------------------------------------------------------------
class Image:
    """Bitmap image for the LED matrix.

    An image is always ``HEIGHT`` rows tall (see property ``height``). Its width (see
    property ``width``) is independent of the display and may be smaller, equal to,
    or **larger** than the ``WIDTH`` physical columns of the LED matrix.
    The factory method ``Image.create`` accepts any width (the widest kept row).
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
        """Factory Method: Parse a pattern string into an Image.

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
        """Column count of this image, not the physical display width. Read-only.

        May be smaller, equal to, or larger than ``WIDTH``. Factory method
        ``Image.create`` sets ``width`` to the length of the widest row in the pattern.
        """
        return self._width

    @property
    def height(self) -> int:
        """Row count of this image: always display ``HEIGHT``. Read-only.

        If an image is created from pattern that has less rows than the display's ``HEIGHT``,
        the factory method ``Image.create(…)`` always pads with OFF to ``HEIGHT`` rows. Equivalently,
        ``Image.create(…)`` truncates an overly tall pattern to ``HEIGHT`` rows.
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

    async def _show_image(self, disp: Display, offset: int = 0, interval_ms: int = 0) -> Token:
        """Internal implementation backing ``Display.show_image``.

        Show a ``WIDTH``-column window of this image, then wait up to ``interval_ms`` milliseconds before
        returning. If a subsequent operation acquires the display before the wait
        elapses, this method returns immediately instead; check the returned ``Token``'s ``is_expired`` to
        tell whether that happened.

        ``disp`` is the ``Display`` instance to render to.
        ``offset`` is the image column placed at display column 0. It may
        be negative or past the right edge; uncovered display columns are
        ``OFF``. Cancels any prior Tier 2 animation.
        A negative ``interval_ms`` waits 0 ms, the same as ``interval_ms=0``.
        That 0 ms wait still lets other tasks that are ready run once, then this call returns.
        """
        token = disp._acquire()
        self._render_window(disp, offset)
        await _sleep_pollable(token, interval_ms)
        return token

    async def _scroll_image(self, disp: Display, step: int = 1, interval_ms: int = 200) -> Token:
        """Internal implementation backing ``Display.scroll_image``.

        Scroll through the image, advancing ``step`` columns per frame, with ``interval_ms`` milliseconds between frames.
        ``step`` is how many image columns scroll in from the right each frame. The scroll always starts at position 0.
        Every ``interval_ms``, ``step`` image columns scroll in, until the last column of the image has appeared.
        If ``step`` is greater than 1, that last step might need to pad with empty columns after the last image column.
        Negative ``step`` is not yet supported.

        If a subsequent operation acquires the display before the scroll completes, this method returns after the
        current frame's ``interval_ms`` sleep; check the returned ``Token``'s ``is_expired`` to tell whether that happened.

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
        # Once. ``int`` truncates a float; ``sleep_ms`` clamps a negative to 0.
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
        """Factory Method: Create an ``Icon`` of ``WIDTH`` columns by ``HEIGHT`` rows, from a pattern string.
        ``#`` is a lit pixel and ``.`` is off. So the row ``#.#`` reads on, off, on.

        The Icon stores no color of its own. Pass the color when you draw it,
        with ``Display.render_icon`` or ``Display.show_icon``.

        Smaller patterns are accepted: missing rows/columns pad as ``OFF``
        (bottom/right, since row 0 = top and column 0 = left).
        Raises ``ValueError`` if the pattern *exceeds* ``WIDTH`` columns or
        ``HEIGHT`` rows (every whitespace character and blank lines ignored).
        For a multi-color bitmap, or one wider than ``WIDTH`` (e.g. a scrollable
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
# Cancellation-aware sleep helpers. Operate only on a ``Token``, with no
# dependency on any ``Display`` instance's state -- callers pass whichever
# token they are holding.
# ---------------------------------------------------------------------------


async def _sleep_pollable(token: Token, total_ms: int, poll_ms: int = 47) -> None:
    """Sleep up to ``total_ms`` milliseconds, returning early once ``token.is_expired``.

    Chunks the sleep into at most ``poll_ms``-sized pieces so a caller notices
    a superseding display operation within ``poll_ms``, not only after the full
    ``total_ms`` has elapsed. When not cancelled, the total elapsed time still converges
    to ``total_ms`` (the final chunk is the time still left, never overshooting).

    A ``total_ms ≤ 0`` allows once for other coroutines to run (we call ``asyncio.sleep_ms(0)``)
    before this function returns. If no pause is desired, please use a synchronous Tier 1 method, which
    returns in the same call, so those other coroutines must wait until the caller itself pauses.
    """
    # Once. ``int`` truncates a float (0.9 becomes 0). ``<= 0`` still yields once.
    total_ms = int(total_ms)
    if total_ms <= 0:
        await asyncio.sleep_ms(0)
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

    A negative ``poll_ms`` waits 0 ms per chunk. Each chunk still lets other
    tasks that are ready run once.
    """
    poll_ms = int(poll_ms)
    while not token.is_expired:
        await asyncio.sleep_ms(poll_ms)


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
        color: tuple[int, int, int] | dict[str, tuple[int, int, int]],
    ) -> None:
        """Fused hot-path used by ``render_pattern``: one scan of the pattern string.

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
        color: tuple[int, int, int],
    ) -> None:
        """Render WIDTH column bytes from ``data`` starting at ``data[offset]`` to this instance's buffer.

        Each ``data[offset + x]`` is one column byte (i.e. a single byte representing
        one column of the bitmap). Bit ``y`` of the byte selects the pixel at display
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
            col_byte = data[offset + x]
            for y in range(HEIGHT):
                pixels[lut[x_base + y]] = color if (col_byte >> y) & 1 else off
            x_base += HEIGHT  # advance to next column; addition avoids a per-column multiply
        pixels.show()

    def _render_ring_window(
        self,
        ring: bytearray,
        read_head: int,
        color_on: tuple[int, int, int],
    ) -> None:
        """Render a WIDTH-sized ring buffer as a left-to-right window starting at ``read_head``.

        The ring holds exactly ``WIDTH`` column bytes; ``read_head`` is the index
        of the leftmost visible column. Wrap is handled by a single subtract
        instead of a per-pixel modulo (cheaper on the MCU VM).

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
        for x in range(WIDTH):
            idx = read_head + x
            if idx >= WIDTH:
                idx -= WIDTH
            col_byte = ring[idx]
            for y in range(HEIGHT):
                pixels[lut[x_base + y]] = color_on if (col_byte >> y) & 1 else off
            x_base += HEIGHT  # advance to next column; addition avoids a per-column multiply
        pixels.show()

    # — Tier 1: Synchronous rendering primitives ----------------------------

    def render_pattern(
        self,
        pattern: str,
        color: tuple[int, int, int] | dict[str, tuple[int, int, int]] = WHITE,
    ) -> None:
        """Draw a pattern string straight onto the LEDs.
        Best for a picture you show once, because this method needs to go over the input string
        and decode every character into a pixel (this is called "parsing" the pattern).
        For pictures you want to show repeatedly, it is best to only parse the pattern once,
        which is done by the factory methods ``Image.create`` or ``Icon.create``. They return
        a parsed Image / Icon, whose reference you can keep and show repeatedly.

        An RGB tuple ``(red, green, blue)`` lights every ``#``, and ``.`` is off,
        so ``#.#`` is on, off, on. A short row is filled with off pixels on the
        right. Rows past the bottom of the screen are left out.
        A dict ``{character: RGB tuple}`` gives each character its own color,
        as in ``color["G"] = (0, 255, 0)``.
        Space, tab, and carriage return are skipped. Any other character is a
        pixel. With one RGB tuple, a character other than ``#`` is off and still
        takes a column.
        """
        self._acquire()
        # Direct render via LUT — no intermediate column-major buffer. Fused one-pass scan.
        self._write_pattern_on_the_fly(pattern, color)
        self._pixels.show()

    def render_icon(self, icon: Icon, color: tuple[int, int, int] = WHITE) -> None:
        """Render an ``Icon`` (e.g. ``Emojis.HEART``) to the LEDs.

        ``color`` is the render color — an ``Icon`` carries no color of its
        own, so ``color`` is not an override of anything, just the color.
        """
        self._acquire()
        self._render_colmajor(icon.columns, 0, color)

    def render_arrow(self, arrow: Icon, color: tuple[int, int, int] = WHITE) -> None:
        """Render an ``Icon`` from the arrow catalog (e.g. ``Arrows.NORTH``) to the LEDs.

        Alias of ``render_icon``, kept as a separate public method name.
        """
        self.render_icon(arrow, color)

    def clear_screen(self) -> None:
        """Turn off all pixels. Cancels any ongoing animation."""
        self._acquire()
        self._pixels.fill(OFF)
        self._pixels.show()

    def clear(self) -> None:
        """Alias for clear_screen()."""
        self.clear_screen()

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int] = WHITE) -> None:
        """Set one pixel. Cancels any in-progress Tier 2 operation.

        The display stays on the most recent frame. When ``(x, y)`` is on
        the matrix, that pixel is changed and flushed. When it is outside,
        nothing is written and the frame is left as it was.
        """
        self._acquire()
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self._pixels[self._lut[x * HEIGHT + y]] = color
            self._pixels.show()

    def fill(self, color: tuple[int, int, int] = WHITE) -> None:
        """Fill all pixels. Cancels ongoing animations."""
        self._acquire()
        self._pixels.fill(color)
        self._pixels.show()

    def get_pixel(self, x: int, y: int) -> tuple[int, int, int]:
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

        Cancels any ongoing animation, then deinitializes the underlying
        NeoPixel buffer. After this call *this instance* is unusable and it must
        be discarded (any further render call on it raises an error). There is
        no re-init path *on this instance* — but the pin is now free, so a
        fresh ``Display()`` may be constructed afterward (it will claim the
        pin again and start with a clean buffer/LUT/token; it is unrelated to
        and does not resurrect this deinitialized instance). This is a
        teardown hook for code that wants to free the data pin / RMT peripheral
        for other use (e.g. before a soft reboot, to hand the pin to a
        different peripheral, or to restart the display with new hardware
        config). See ``lib/display/README.md`` § "Singleton design &
        ``deinit``" for the module-level ``display`` singleton's rationale.
        """
        self._acquire()
        self._pixels.deinit()

    # — Tier 2: Async MakeCode-compatible methods ---------------------------

    async def show_pattern(
        self,
        pattern: str,
        color: tuple[int, int, int] | dict[str, tuple[int, int, int]] = WHITE,
        interval_ms: int = 0,
    ) -> Token:
        """Render a pattern, then wait up to ``interval_ms`` milliseconds before returning. A wait of 0 ms
        still lets other tasks that are ready run once, then this call returns. If a subsequent operation
        acquires the display before the wait elapses, this method returns
        immediately instead; check the returned ``Token``'s ``is_expired`` to tell whether that happened.

        color: RGB tuple (mono '#'/'.' mode) or dict (palette).
        Same pattern rules as ``render_pattern``.

        Raises ``ValueError`` if ``interval_ms < 0``.
        """
        if interval_ms < 0:
            raise ValueError(f"interval_ms must be >= 0, got {interval_ms}")
        self.render_pattern(pattern, color)
        token = self._token  # render_pattern's internal _acquire() just minted this
        await _sleep_pollable(token, interval_ms)
        return token

    async def show_icon(self, icon: Icon, color: tuple[int, int, int] = WHITE, interval_ms: int = 0) -> Token:
        """Render an ``Icon`` (e.g. ``Emojis.HEART``), then wait up to ``interval_ms`` milliseconds before
        returning. If a subsequent operation acquires the display before the wait elapses, this method
        returns immediately instead; check the returned ``Token``'s ``is_expired`` to tell whether that
        happened.

        Raises ``ValueError`` if ``interval_ms < 0``.
        """
        if interval_ms < 0:
            raise ValueError(f"interval_ms must be >= 0, got {interval_ms}")
        self.render_icon(icon, color)
        token = self._token  # render_icon's internal _acquire() just minted this
        await _sleep_pollable(token, interval_ms)
        return token

    async def show_arrow(self, arrow: Icon, color: tuple[int, int, int] = WHITE, interval_ms: int = 0) -> Token:
        """Render an ``Icon`` from the arrow catalog (e.g. ``Arrows.NORTH``), then wait up to ``interval_ms``
        milliseconds before returning. If a subsequent operation acquires the display before the wait
        elapses, this method returns immediately instead; check the returned ``Token``'s ``is_expired`` to
        tell whether that happened.

        Raises ``ValueError`` if ``interval_ms < 0``.
        """
        # Functionally this method is an alias of ``show_icon``, kept as a separate public method name.
        return await self.show_icon(arrow, color=color, interval_ms=interval_ms)

    async def show_image(self, image: Image, offset: int = 0, interval_ms: int = 0) -> Token:
        """Show a ``WIDTH``-column window of ``img``, then wait up to ``interval_ms`` milliseconds before
        returning. If a subsequent operation acquires the display before the wait
        elapses, this method returns immediately instead; check the returned ``Token``'s ``is_expired`` to
        tell whether that happened.

        ``offset`` is the image column placed at display column 0. It may be negative
        or positive and may push the image partially or fully out of the display area.
        Display columns outside the Image are ``OFF``. Cancels any prior Tier 2 animation.
        A negative ``interval_ms`` waits 0 ms, the same as ``interval_ms=0``.
        That 0 ms wait still lets other tasks that are ready run once, then this call returns.
        """
        return await image._show_image(self, offset, interval_ms)

    async def scroll_image(self, image: Image, step: int = 1, interval_ms: int = 200) -> Token:
        """Scroll through ``image``, advancing ``step`` columns per frame, with ``interval_ms`` milliseconds between frames.

        ``step`` is how many image columns scroll in from the right each frame. The scroll always starts at position 0.
        Every ``interval_ms``, ``step`` image columns scroll in, until the last column of the image has appeared.
        If ``step`` is greater than 1, that last step might need to pad with empty columns after the last image column.
        Negative ``step`` is not yet supported.

        If a subsequent operation acquires the display before the scroll completes, this method returns after the
        current frame's ``interval_ms`` sleep; check the returned ``Token``'s ``is_expired`` to tell whether that happened.

        Raises ``ValueError`` if ``step <= 0``. Reverse scrolling (negative ``step``) is not yet supported.
        A negative ``interval_ms`` waits 0 ms between frames, the same as ``interval_ms=0``.
        That wait still lets other tasks that are ready run once before the next frame.
        """
        return await image._scroll_image(self, step, interval_ms)

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
        If ``loop`` is ``True``, keep scrolling indefinitely (or, for fit-on-screen
        text, hold indefinitely) until cancelled by another display
        operation.
        A non-looping scroll ends exactly when the last non-empty column of
        the string has left the screen: the display is left fully blank.

        For text that fits on the display without scrolling (total width <= WIDTH),
        we do not scroll. The text is centered and held in place.
        The hold duration is up to ``interval_ms * WIDTH`` when ``interval_ms > 0``,
        so a held text and a scrolled text of comparable width provide comparable time
        to read. If ``loop=True``, the string is held indefinitely until cancelled by
        another display operation. When ``interval_ms`` is 0 and ``loop`` is
        false, we show the text, let other tasks that are ready run once, and
        return (the short-text counterpart to ``show_pattern(pattern, interval_ms=0)``).

        The call replaces the matrix with ``text``. An empty string follows the same
        convention as text fitting on screen without scrolling: we just show a blank
        screen and hold it according to the definition of above

        Raises ``ValueError`` if ``interval_ms < 0``: a negative delay has
        no sensible meaning here (see the class discussion of cold-call-
        site validation in ``CODING_PRINCIPLES.md``).
        Returns the cancellation ``Token`` (check ``token.is_expired`` to see
        whether a later display operation preempted this call).
        """
        if interval_ms < 0:
            raise ValueError(f"interval_ms must be >= 0, got {interval_ms}")
        interval_ms = int(interval_ms)
        token = self._acquire()
        text = str(text)

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

        # Fit-on-screen path: text is no wider than WIDTH glyph-columns, so there's nothing to scroll. Center text
        # once and hold: indefinitely iff `loop == true`. For `loop == false`, we hold for an `interval_ms * WIDTH`
        # duration. When that duration is 0, `_sleep_pollable` pauses once (`asyncio.sleep_ms(0)`) so other
        # coroutines can run, then returns.
        # Note: An empty string has zero columns and takes this same path: the frame is all OFF (the empty string drawn).
        if len(fit_buf) <= WIDTH:
            pad = (WIDTH - len(fit_buf)) // 2
            padded = bytearray(WIDTH)
            for i in range(len(fit_buf)):
                padded[pad + i] = fit_buf[i]
            if token.is_expired:
                return token
            self._render_colmajor(padded, 0, color)
            if loop:
                await _sleep_until_cancelled(token)
                return token
            await _sleep_pollable(token, interval_ms * WIDTH)
            return token

        # Bound once. ``sleep_ms`` takes whole milliseconds, so the loop does no float math.
        sleep_ms = asyncio.sleep_ms
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
                self._render_ring_window(ring, read_head, color)
                await sleep_ms(interval_ms)
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
        # Implementation note: ``n`` is specified as a number. A str or a bool is unspecified. This body
        # passes ``str(n)`` through unchanged. Booleans will therefore render as "True" or "False" for example.
        return await self.show_string(str(n), color, interval_ms, loop)

    async def pause(self, ms: int) -> Token:
        """Wait up to ``ms`` milliseconds before returning. If a subsequent operation acquires the display
        before the wait elapses, this method returns immediately instead; check the returned ``Token``'s
        ``is_expired`` to tell whether that happened.

        Raises ``ValueError`` if ``ms < 0``.
        """
        if ms < 0:
            raise ValueError(f"ms must be >= 0, got {ms}")
        token = self._acquire()
        await _sleep_pollable(token, ms)
        return token

    @staticmethod
    async def forever(callback: Callable[[], object], sleep_between_ms: int = 10) -> NoReturn:
        """Run ``callback`` again and again, without ever stopping.

        Use this when you want to do a certain task forever, for example scrolling
        a message over and over. You give ``forever`` a function that takes no
        arguments. It calls that function, waits for it to finish, rests for
        ``sleep_between_ms`` milliseconds, and then calls it again.

        The ``callback`` can be a normal ``def`` function or an ``async def`` (a function that
        uses ``await``). If it is an ``async def`` function, ``forever`` waits until it is done.

        Here is a function to repeat. Give ``forever`` its name without parentheses
        (``say_hello``, not ``say_hello()``), because ``forever`` calls it for you:

            async def say_hello():
                await display.show_string("Hello")

        ``forever`` is itself ``async`` and it never ends. So the code you write after it, in the same
        place, never runs, unless you start ``forever`` as a task (way 3 below). There are three ways:

            # 1. In the main part of your program, outside any async function, as its last line. No
            #    code after this line will ever run, so use it only when repeating is the whole program:
            asyncio.run(display.forever(say_hello))

            # 2. Inside an async function. The rest of this function will never run, but your
            #    other tasks (for example button handlers) keep running:
            await display.forever(say_hello)

            # 3. Inside an async function, as a task. The function carries on while ``forever``
            #    repeats, and you can stop it later:
            task = asyncio.create_task(display.forever(say_hello))
            await asyncio.sleep(10)  # ...do other things, for example wait for a button press
            task.cancel()            # stops ``forever`` at its next ``await``

        A cancelled ``forever`` leaves the last picture on the LEDs. Call ``display.clear_screen()``
        afterwards if you want them dark.

        After each round, ``forever`` rests for ``sleep_between_ms`` milliseconds. This rest keeps the
        board calm and lets your other tasks (for example button handlers) run, even when ``callback``
        finishes instantly (``show_icon`` does by default, unless you configure it to sleep by setting
        ``interval_ms``). If your callback already waits (for example ``show_string`` or ``pause``),
        the rest is not needed, but by default the rest is so short (10 ms) that you will probably not
        notice. Set ``sleep_between_ms=0`` only if you need the timing of your own callback to be exact,
        for example a repeat every 1000 ms, or a very fast repeat.

        Only one task runs at a time, and it keeps going until it reaches an ``await``. Tasks
        that are ready to run will get their turn, but they have to wait until your ``callback``
        reaches its next ``await``. So keep your callback short and let it ``await`` often, or
        other tasks (such as button handlers) will react late.

        Raises ``ValueError`` if ``sleep_between_ms`` is negative. Because ``forever``
        never returns, the only ways out are an exception in ``callback`` or cancelling
        the task that is running it.
        """
        if sleep_between_ms < 0:
            raise ValueError(f"sleep_between_ms must be >= 0, got {sleep_between_ms}")
        # Once. ``sleep_ms`` leaves a positive float as a float deadline; the C task queue asserts a small int.
        # ``int`` truncates (25.9 becomes 25). A negative already raised above.
        rest_ms = int(sleep_between_ms)
        while True:
            result = callback()
            if hasattr(result, "__await__"):
                await result
            await asyncio.sleep_ms(rest_ms)


# Singleton — ``from display import display``
display = Display()

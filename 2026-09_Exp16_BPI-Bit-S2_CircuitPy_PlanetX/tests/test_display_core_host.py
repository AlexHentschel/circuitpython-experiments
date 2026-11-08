"""Host execution of ``display.core`` behind stubs. No board, no NeoPixel hardware.

``test_no_board_core.py`` still requires that a normal import of ``display``
does not load ``core``. This module installs ``board`` / ``neopixel`` /
``adafruit_ticks`` / ``rainbowio`` only inside a fixture and removes them
before the test returns.

Out of scope here (needs the board or a design change): the real pin lock on
a second ``Display()`` and keypad scan timing.
"""

import asyncio
import contextlib
import sys
import types

import pytest

from display._constants import HEIGHT, OFF, RED, WHITE, WIDTH
from display.text_layout import ScreenText, _ColumnReader, centered

_STUB_NAMES = ("board", "neopixel", "adafruit_ticks", "rainbowio")
_TICKS_PERIOD = 1 << 29
_TICKS_MAX = _TICKS_PERIOD - 1
_TICKS_HALF = _TICKS_PERIOD // 2


class FakePixels:
    """Enough of ``neopixel.NeoPixel`` for ``Display`` to render into RAM."""

    def __init__(self, pin, n, brightness=1.0, auto_write=True):
        self.n = n
        self.brightness = brightness
        self.auto_write = auto_write
        self.buf = [OFF] * n
        self.latched = [OFF] * n
        self.shows = 0
        self.alive = True

    def __setitem__(self, index, color):
        if not self.alive:
            raise RuntimeError("used after deinit")
        self.buf[index] = color

    def __getitem__(self, index):
        if not self.alive:
            raise RuntimeError("used after deinit")
        return self.buf[index]

    def fill(self, color):
        if not self.alive:
            raise RuntimeError("used after deinit")
        self.buf = [color] * self.n

    def show(self):
        if not self.alive:
            raise RuntimeError("used after deinit")
        self.shows += 1
        self.latched = list(self.buf)

    def deinit(self):
        self.alive = False


def _ticks_diff(end, start):
    diff = (end - start) & _TICKS_MAX
    return ((diff + _TICKS_HALF) & _TICKS_MAX) - _TICKS_HALF


def _feeder_columns(text):
    reader = _ColumnReader(str(text))
    count = 0
    while reader.next_column() is not None:
        count += 1
    return count


def _drain_reader(reader):
    columns = []
    while True:
        col = reader.next_column()
        if col is None:
            return columns
        columns.append(col)


def _feeder_column_bytes(text):
    return _drain_reader(_ColumnReader(str(text)))


def _feeder_column_bytes_of(text):
    """Drain a ``ScreenText`` through a fresh reader."""
    return _drain_reader(text._reader())


def _left_window(text):
    """Left-aligned ``WIDTH`` window. Columns past the right edge are dropped."""
    columns = _feeder_column_bytes(text)
    window = [0] * WIDTH
    for i, col in enumerate(columns[:WIDTH]):
        window[i] = col
    return window


def _centered_window(text, origin):
    """``WIDTH`` window with source column 0 at display column ``origin``."""
    columns = _feeder_column_bytes(text)
    window = [0] * WIDTH
    for src, col in enumerate(columns):
        dest = origin + src
        if 0 <= dest < WIDTH:
            window[dest] = col
    return window


def _frame_of(columns, color=WHITE):
    """Logical pixels for exactly ``WIDTH`` column bytes. Bit ``y`` is row ``y``."""
    return tuple(
        tuple(color if (columns[x] >> y) & 1 else OFF for x in range(WIDTH))
        for y in range(HEIGHT)
    )


def _fit_window(text):
    """Centered ``WIDTH`` window for text that fits. Pad rule: ``(WIDTH - w) // 2``."""
    columns = _feeder_column_bytes(text)
    pad = (WIDTH - len(columns)) // 2
    window = [0] * WIDTH
    for i, col in enumerate(columns):
        window[pad + i] = col
    return window


_BLANK = tuple(tuple(OFF for _ in range(WIDTH)) for _ in range(HEIGHT))


@contextlib.contextmanager
def _recorded_shows(host):
    """Latch each ``show()`` as a logical frame. Restores the pixel ``show``."""
    frames = []
    pixels = host.disp._pixels
    orig = pixels.show

    def capture():
        orig()
        frames.append(host.logical())

    pixels.show = capture
    try:
        yield frames
    finally:
        pixels.show = orig


class _Host:
    def __init__(self, core, sleeps, hook, clock):
        self.core = core
        self.disp = core.display
        self.sleeps = sleeps
        self.hook = hook
        self.clock = clock

    def logical(self):
        disp = self.disp
        return tuple(
            tuple(disp.get_pixel(x, y) for x in range(WIDTH)) for y in range(HEIGHT)
        )

    def paint_logical(self):
        """One distinct color per logical cell, written through the current LUT."""
        pixels = self.disp._pixels
        lut = self.disp._lut
        for x in range(WIDTH):
            base = x * HEIGHT
            for y in range(HEIGHT):
                pixels[lut[base + y]] = (x, y, 7)
        pixels.show()


@pytest.fixture
def host():
    """Import ``display.core`` against stubs. Restore ``sys.modules`` afterwards."""
    saved = {name: sys.modules.get(name) for name in _STUB_NAMES}
    had_core = "display.core" in sys.modules
    orig_sleep = asyncio.sleep
    had_sleep_ms = hasattr(asyncio, "sleep_ms")
    orig_sleep_ms = getattr(asyncio, "sleep_ms", None)

    board = types.ModuleType("board")
    board.NEOPIXEL = object()
    sys.modules["board"] = board

    neo = types.ModuleType("neopixel")
    neo.NeoPixel = FakePixels
    sys.modules["neopixel"] = neo

    clock = {"now": 0}
    ticks = types.ModuleType("adafruit_ticks")
    ticks.ticks_ms = lambda: clock["now"] & _TICKS_MAX
    ticks.ticks_add = lambda base, delta: (base + delta) & _TICKS_MAX
    ticks.ticks_diff = _ticks_diff
    sys.modules["adafruit_ticks"] = ticks

    rainbow = types.ModuleType("rainbowio")
    rainbow.colorwheel = lambda pos: (pos, 0, 0)
    sys.modules["rainbowio"] = rainbow

    sys.modules.pop("display.core", None)
    import display.core as core

    sleeps = []
    hook = {"fn": None}

    async def sleep_ms(ms):
        sleeps.append(("ms", ms))
        if hook["fn"] is not None:
            hook["fn"]()
        clock["now"] += int(ms)
        await orig_sleep(0)

    async def fake_sleep(seconds):
        sleeps.append(("s", seconds))
        if hook["fn"] is not None:
            hook["fn"]()
        await orig_sleep(0)

    asyncio.sleep = fake_sleep
    asyncio.sleep_ms = sleep_ms
    try:
        yield _Host(core, sleeps, hook, clock)
    finally:
        asyncio.sleep = orig_sleep
        if had_sleep_ms:
            asyncio.sleep_ms = orig_sleep_ms
        else:
            del asyncio.sleep_ms
        if not had_core:
            sys.modules.pop("display.core", None)
        for name, old in saved.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old


def test_rotation_keeps_logical_colors_and_shows_once(host):
    """Each accepted rotation redraws the same logical picture and latches once.

    - Covers: ``set_rotation`` changing the LUT without ``show``, or scrambling logical colors.
    - How: paint ``(x, y, 7)`` at rotation 0; rotate through 90/180/270/-90/0; ``get_pixel`` matches; ``show`` count grows by 1 each call.
    """
    disp = host.disp
    host.paint_logical()
    shows = disp._pixels.shows
    token = disp._token
    origin = disp._lut[0]
    for degrees in (90, 180, 270, -90, 0):
        disp.set_rotation(degrees)
        shows += 1
        assert disp._pixels.shows == shows
        assert disp._token is token and token.is_expired is False
        for x in range(WIDTH):
            for y in range(HEIGHT):
                assert disp.get_pixel(x, y) == (x, y, 7)
        if degrees % 360 != 0:
            assert disp._lut[0] != origin


def test_rejected_rotation_does_not_draw(host):
    """``set_rotation(45)`` raises and leaves the LUT and the latch alone.

    - Covers: applying a partial LUT, or latching, before the angle check fails.
    - How: paint, call 45, catch ``ValueError``; LUT bytes and ``show`` count unchanged.
    """
    disp = host.disp
    host.paint_logical()
    lut = bytes(disp._lut)
    shows = disp._pixels.shows
    with pytest.raises(ValueError):
        disp.set_rotation(45)
    assert bytes(disp._lut) == lut
    assert disp._pixels.shows == shows


def test_recolor_does_not_redraw(host):
    """``Image.recolor`` changes the next draw, not the frame already latched.

    - Covers: ``recolor`` calling ``show`` or painting the new color immediately.
    - How: draw the image, ``recolor(RED)``; ``show`` count unchanged and pixel still white; a second draw is red.
    """
    disp = host.disp
    image = host.core.Image._from_encoded(bytes([0x1F]), 1, False, WHITE)

    image._render_window(disp, 0)
    shows = disp._pixels.shows
    image.recolor(RED)
    assert disp._pixels.shows == shows
    assert disp.get_pixel(0, 0) == WHITE
    image._render_window(disp, 0)
    assert disp.get_pixel(0, 0) == RED


def test_zero_hold_yields_once(host):
    """``pause(0)`` lets a sibling task run. ``pause(100)`` sleeps 47+47+6.

    - Covers: a 0 ms hold returning with no ``await``, or the chunk sum drifting.
    - How: create a task that sets a flag; ``await pause(0)``; flag is set. Then sum the millisecond sleeps for 100.
    """
    disp = host.disp

    async def run():
        flag = {"ran": False}

        async def other():
            flag["ran"] = True

        asyncio.create_task(other())
        host.sleeps.clear()
        await disp.pause(0)
        assert flag["ran"] is True
        assert ("ms", 0) in host.sleeps
        host.sleeps.clear()
        await disp.pause(100)
        assert sum(ms for kind, ms in host.sleeps if kind == "ms") == 100

    asyncio.run(run())


def test_negative_pause_does_not_cancel(host):
    """``pause(-1)`` raises before acquiring, so the current token stays.

    - Covers: a negative pause expiring an in-flight animation.
    - How: remember ``_token``; ``pause(-1)`` raises ``ValueError``; same token, not expired.
    """
    disp = host.disp
    token = disp._token

    async def run():
        with pytest.raises(ValueError):
            await disp.pause(-1)

    asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False


def test_set_pixel_outside_cancels_without_a_latch(host):
    """An out-of-range ``set_pixel`` expires the token and does not ``show``.

    - Covers: writing a wrapped coordinate, or leaving the previous animation running.
    - How: fill red, ``set_pixel(-1, 0)``; token expired, ``show`` count unchanged, corner still red.
    """
    disp = host.disp
    disp.render_filled(RED)
    token = disp._token
    shows = disp._pixels.shows
    disp.set_pixel(-1, 0, WHITE)
    assert token.is_expired is True
    assert disp._pixels.shows == shows
    assert disp.get_pixel(0, 0) == RED
    assert disp.get_pixel(-1, 0) == OFF


def test_brightness_shows_without_cancelling(host):
    """``set_brightness`` latches the current buffer and keeps the token.

    - Covers: brightness acquiring a new token, or skipping ``show``.
    - How: fill, remember token and ``show`` count, set 0.1; token unchanged, one new ``show``.
    """
    disp = host.disp
    disp.render_filled(WHITE)
    token = disp._token
    shows = disp._pixels.shows
    disp.set_brightness(0.1)
    assert disp._token is token
    assert token.is_expired is False
    assert disp._pixels.shows == shows + 1
    assert disp._pixels.brightness == 0.1


def test_show_string_empty_holds_blank_for_interval_times_width(host):
    """``show_string('')`` draws off pixels and waits ``interval_ms * WIDTH``.

    - Covers: empty text leaving the previous frame, or holding a different duration.
    - How: ``interval_ms=100``; millisecond sleeps sum to 500; every logical pixel is off.
    """
    disp = host.disp
    disp.render_filled(RED)

    async def run():
        host.sleeps.clear()
        await disp.show_string("", interval_ms=100)
        assert sum(ms for kind, ms in host.sleeps if kind == "ms") == 100 * WIDTH
        assert host.logical() == tuple(tuple(OFF for _ in range(WIDTH)) for _ in range(HEIGHT))

    asyncio.run(run())


def test_show_string_scroll_frame_count(host):
    """Text wider than the display sleeps once per ``1 + columns + WIDTH`` frame.

    - Covers: the scroll-out blank frame being skipped, or the fit-path hold being used.
    - How: ``"HI"``; count ``show`` calls; first and last frames are blank; a middle frame is not.
    """
    disp = host.disp
    frames = []
    pixels = disp._pixels
    orig = pixels.show

    def capture():
        orig()
        frames.append(host.logical())

    pixels.show = capture
    columns = _feeder_columns("HI")
    assert columns > WIDTH

    async def run():
        await disp.show_string("HI", interval_ms=150)

    asyncio.run(run())
    assert len(frames) == 1 + columns + WIDTH
    blank = tuple(tuple(OFF for _ in range(WIDTH)) for _ in range(HEIGHT))
    assert frames[0] == blank
    assert frames[-1] == blank
    assert any(frame != blank for frame in frames)


def test_scroll_step_skips_a_middle_column(host):
    """``scroll_image`` stays on the step lattice. Width 10, step 6 visits 0 then 6.

    - Covers: snapping the last frame onto column 5.
    - How: record ``_render_window`` offsets.
    """
    disp = host.disp
    image = host.core.Image._from_encoded(bytes([1] * 10), 10, False, WHITE)
    offsets = []
    orig = host.core.Image._render_window

    def capture(self, disp_, offset):
        offsets.append(offset)
        return orig(self, disp_, offset)

    host.core.Image._render_window = capture
    try:
        async def run():
            await disp.scroll_image(image, step=6, interval_ms=10)

        asyncio.run(run())
    finally:
        host.core.Image._render_window = orig
    assert offsets == [0, 6]


def test_scroll_cancel_does_not_draw_another_frame(host):
    """A cancel during the frame sleep returns before the next ``_render_window``.

    - Covers: one more frame after the token expires.
    - How: ``render_filled`` inside the first ``asyncio.sleep_ms``; recorded offsets are ``[0]``; token expired.
    """
    disp = host.disp
    image = host.core.Image._from_encoded(bytes([1] * 10), 10, False, WHITE)
    offsets = []
    orig = host.core.Image._render_window

    def capture(self, disp_, offset):
        offsets.append(offset)
        return orig(self, disp_, offset)

    def cancel():
        disp.render_filled(OFF)

    host.core.Image._render_window = capture
    host.hook["fn"] = cancel
    try:
        async def run():
            return await disp.scroll_image(image, step=1, interval_ms=100)

        token = asyncio.run(run())
    finally:
        host.core.Image._render_window = orig
        host.hook["fn"] = None
    assert offsets == [0]
    assert token.is_expired is True


def test_show_image_negative_duration_does_not_take_over(host):
    """A negative ``show_image`` duration raises before the display changes.

    - Covers: clamping a negative duration, or drawing and then raising.
    - How: paint red; ``duration_ms=-5`` raises ``ValueError``; same token; frame still red; no sleep.
    """
    disp = host.disp
    image = host.core.Image._from_encoded(bytes([0x1F, 0x00]), 2, False, WHITE)
    disp.render_filled(RED)
    before = host.logical()
    token = disp._token
    host.sleeps.clear()

    async def run():
        await disp.show_image(image, offset=-2, duration_ms=-5)

    with pytest.raises(ValueError, match="duration_ms must be >= 0"):
        asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False
    assert host.logical() == before
    assert host.sleeps == []


def test_show_string_negative_interval_does_not_cancel(host):
    """``show_string`` rejects a negative interval before ``_acquire``.

    - Covers: clamping, or expiring the current token on the way to the error.
    - How: ``interval_ms=-1`` raises ``ValueError``; same token, not expired.
    """
    disp = host.disp
    token = disp._token

    async def run():
        with pytest.raises(ValueError):
            await disp.show_string("I", interval_ms=-1)

    asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False


def test_render_string_fitting_text_stays_lit(host):
    """``render_string`` draws a fitting string once, from the left, and returns without sleeping.

    - Covers: an async renderer, a second ``show``, or the previous token staying current.
    - How: ``"A"`` (4 columns, one leftover blank on the right); one ``show``; sleeps empty; old token expired.
    """
    disp = host.disp
    columns = _feeder_column_bytes("A")
    assert len(columns) == 4
    window = _left_window("A")
    assert window == columns + [0]
    previous = disp._token
    shows = disp._pixels.shows
    host.sleeps.clear()
    assert disp.render_string("A") is None
    assert disp._pixels.shows == shows + 1
    assert host.sleeps == []
    assert previous.is_expired is True
    assert disp._token is not previous
    assert host.logical() == _frame_of(window)


def test_render_string_exactly_width_has_no_pad(host):
    """Text that is exactly ``WIDTH`` columns is drawn in order, with nothing added or dropped.

    - Covers: a pad column, or a crop, when the feeder width is already ``WIDTH``.
    - How: ``"7"`` is 5 columns; the frame is those feeder bytes.
    """
    disp = host.disp
    columns = _feeder_column_bytes("7")
    assert len(columns) == WIDTH
    disp.render_string("7")
    assert host.logical() == _frame_of(columns)


def test_centered_and_left_aligned_cover_empty_through_long(host):
    """``centered`` reproduces the pinned windows; ``render_string`` is left-aligned.

    - Covers: a spare blank on the left of the default path, keeping the tail of a wide string, or a window whose length is not ``WIDTH``.
    - How: feeder bytes placed at a pinned origin for ``centered``; origin 0 for ``render_string``.
    """
    # (text, width, centered origin). origin is the display column where source column 0 lands.
    # The origins are literals. ``"0!"`` and ``"HELLO"`` are odd overflows: the other
    # floor would move those windows one column to the left.
    cases = (
        ("", 0, 0),
        ("!", 1, 2),
        ("A", 4, 0),
        ("7", 5, 0),
        ("0!", 6, 0),
        ("Hallo", 23, -9),
        ("HELLO", 24, -9),
    )
    for text, width, origin in cases:
        columns = _feeder_column_bytes(text)
        assert len(columns) == width, text
        centered_window = _centered_window(text, origin)
        prepared = centered(text)
        assert prepared.width == WIDTH
        assert _feeder_column_bytes_of(prepared) == centered_window, text
        host.disp.render_string(prepared)
        assert host.logical() == _frame_of(centered_window), text
        host.disp.render_string(text)
        assert host.logical() == _frame_of(_left_window(text)), text

    bang = _feeder_column_bytes("!")
    assert _feeder_column_bytes_of(centered("!")) == [0, 0, bang[0], 0, 0]
    assert _feeder_column_bytes_of(centered("A")) == _feeder_column_bytes("A") + [0]
    wide = _feeder_column_bytes("0!")
    assert _feeder_column_bytes_of(centered("0!")) == wide[:WIDTH]
    assert wide[WIDTH] == 0x17


def test_render_string_wider_than_width_keeps_the_start(host):
    """Wider text shows the first ``WIDTH`` columns. ``centered`` drops an odd leftover on the right.

    - Covers: the default path keeping a middle slice, or ``centered`` keeping the right-most columns.
    - How: feeder bytes. Default frame is columns ``0:WIDTH``. ``centered`` uses the pinned first-kept index.
    """
    disp = host.disp
    # (text, feeder width, index of the first column ``centered`` keeps). Slices are pinned, not computed.
    cases = (("0!", 6, 0), ("11", 7, 1), ("01", 8, 1))
    for text, width, first in cases:
        columns = _feeder_column_bytes(text)
        assert len(columns) == width
        disp.render_string(text)
        assert host.logical() == _frame_of(columns[:WIDTH]), text
        centered_window = columns[first : first + WIDTH]
        assert len(centered_window) == WIDTH
        disp.render_string(centered(text))
        assert host.logical() == _frame_of(centered_window), text


def test_render_string_empty_is_blank(host):
    """``render_string('')`` draws an all-off frame and does not sleep.

    - Covers: raising on an empty string, or leaving the previous picture up.
    - How: fill red, then render ``""``; every pixel off; sleeps empty.
    """
    disp = host.disp
    disp.render_filled(RED)
    host.sleeps.clear()
    disp.render_string("")
    assert host.sleeps == []
    assert host.logical() == _BLANK


def test_render_string_cancels_a_running_scroll(host):
    """``render_string`` during a scroll expires that scroll and leaves its letter up.

    - Covers: another scroll frame after the sync call, or the letter being cleared.
    - How: on the first scroll sleep, ``render_string("K")``; token expired; last frame is ``K``; no later ``show``.
    """
    disp = host.disp
    expected = _frame_of(_fit_window("K"))
    after = {}

    def preempt():
        host.hook["fn"] = None
        disp.render_string("K")
        after["shows"] = disp._pixels.shows
        after["frame"] = host.logical()

    host.hook["fn"] = preempt
    try:
        async def run():
            return await disp.show_string("STAGE2", interval_ms=80)

        token = asyncio.run(run())
    finally:
        host.hook["fn"] = None
    assert token.is_expired is True
    assert after["frame"] == expected
    assert host.logical() == expected
    assert disp._pixels.shows == after["shows"]


def test_render_number_matches_render_string(host):
    """``render_number(n)`` draws the same frame as ``render_string(str(n))``.

    - Covers: extra formatting, or a different crop, for a fitting digit and a wide number.
    - How: ``7`` and ``42``; draw with ``render_string``, then with ``render_number``; frames match.
    """
    disp = host.disp
    for n in (7, 42):
        disp.render_string(str(n))
        as_text = host.logical()
        disp.render_number(n)
        assert host.logical() == as_text


def test_show_string_fit_path_ends_blank(host):
    """A fitting ``show_string`` holds for ``interval_ms * WIDTH``, then the last frame is blank.

    - Covers: the letter staying lit, a different hold, or the call expiring its own token.
    - How: ``"A"``, ``interval_ms=100``; sleeps sum to 500; frames are the letter then all off; token still current.
    """
    disp = host.disp
    expected = _frame_of(_fit_window("A"))

    async def run():
        host.sleeps.clear()
        with _recorded_shows(host) as frames:
            token = await disp.show_string("A", interval_ms=100)
        return token, list(frames)

    token, frames = asyncio.run(run())
    assert sum(ms for kind, ms in host.sleeps if kind == "ms") == 100 * WIDTH
    assert frames[0] == expected
    assert frames[-1] == _BLANK
    assert token.is_expired is False
    assert disp._token is token


def test_show_string_fit_preempted_during_hold_keeps_the_other_frame(host):
    """A Tier 1 write during a fitting hold wins. The hold does not blank that frame.

    - Covers: a blank drawn after ``render_filled``, or the token staying current.
    - How: hook ``render_filled(RED)`` on the first sleep of ``show_string("A")``; frame stays red; token expired.
    """
    disp = host.disp

    def preempt():
        host.hook["fn"] = None
        disp.render_filled(RED)

    host.hook["fn"] = preempt
    try:
        async def run():
            return await disp.show_string("A", interval_ms=100)

        token = asyncio.run(run())
    finally:
        host.hook["fn"] = None
    assert token.is_expired is True
    assert host.logical() == tuple(tuple(RED for _ in range(WIDTH)) for _ in range(HEIGHT))


def test_show_string_fit_loop_cancelled_does_not_blank(host):
    """``loop=True`` on fitting text leaves the canceller's frame up.

    - Covers: a blank written after cancellation.
    - How: hook ``render_filled(RED)`` on the first sleep; frame stays red.
    """
    disp = host.disp

    def preempt():
        host.hook["fn"] = None
        disp.render_filled(RED)

    host.hook["fn"] = preempt
    try:
        async def run():
            return await disp.show_string("A", interval_ms=100, loop=True)

        token = asyncio.run(run())
    finally:
        host.hook["fn"] = None
    assert token.is_expired is True
    assert host.logical() == tuple(tuple(RED for _ in range(WIDTH)) for _ in range(HEIGHT))


def test_show_string_fit_interval_zero_flashes_then_blanks(host):
    """``interval_ms=0`` on fitting text yields once, then the screen is blank.

    - Covers: skipping the yield, leaving the text up, or expiring the token.
    - How: ``"A"``; sleeps are ``[("ms", 0)]``; frames are the letter then all off; token not expired.
    """
    disp = host.disp
    expected = _frame_of(_fit_window("A"))

    async def run():
        host.sleeps.clear()
        with _recorded_shows(host) as frames:
            token = await disp.show_string("A", interval_ms=0)
        return token, list(frames)

    token, frames = asyncio.run(run())
    assert host.sleeps == [("ms", 0)]
    assert frames == [expected, _BLANK]
    assert token.is_expired is False


def test_show_number_fit_ends_blank_render_number_stays(host):
    """``show_number(7)`` ends blank. ``render_number(7)`` leaves the ``render_string("7")`` picture up.

    - Covers: a one-digit show staying lit, or ``render_number`` clearing itself.
    - How: await ``show_number(7)``; frame all off; token not expired. Then both renders of ``7``; frames match; no sleep.
    """
    disp = host.disp

    async def run():
        host.sleeps.clear()
        return await disp.show_number(7, interval_ms=40)

    token = asyncio.run(run())
    assert token.is_expired is False
    assert host.logical() == _BLANK
    assert sum(ms for kind, ms in host.sleeps if kind == "ms") == 40 * WIDTH
    disp.render_string("7")
    held = host.logical()
    assert held != _BLANK
    host.sleeps.clear()
    assert disp.render_number(7) is None
    assert host.sleeps == []
    assert host.logical() == held


def test_short_icon_does_not_latch_a_partial_write(host):
    """A short ``Icon`` raises inside the column loop, before ``show``.

    - Covers: latching a half-written buffer, or ignoring the length mismatch.
    - How: ``Icon`` of one byte; ``IndexError``; ``show`` count unchanged; RAM buffer differs from the latch.
    """
    disp = host.disp
    disp.render_filled(OFF)
    pixels = disp._pixels
    shows = pixels.shows
    with pytest.raises(IndexError):
        disp.render_icon(host.core.Icon._from_columns(b"\xff"), WHITE)
    assert pixels.shows == shows
    assert pixels.buf != pixels.latched


def test_render_pattern_clips_a_wide_row_image_keeps_it(host):
    """``render_pattern`` drops columns past ``WIDTH``. ``Image(pattern)`` keeps them as width.

    - Covers: both entry points silently using the same width rule.
    - How: six hashes; the rendered row is five on-pixels; the image reports width 6.
    """
    disp = host.disp
    disp.render_pattern("######\n#")
    assert host.logical()[0] == tuple(WHITE for _ in range(WIDTH))
    assert host.logical()[1][0] == WHITE
    assert host.logical()[1][1] == OFF
    image = host.core.Image("######\n#")
    assert image.width == 6


def test_image_and_icon_are_built_from_a_pattern_only(host):
    """``Image(pattern)`` and ``Icon(pattern)`` are the public constructors. No ``create`` remains.

    - Covers: a second public construction path coming back, or the raw seam leaking into the signature.
    - How: no ``create`` attribute; the constructors parse; ``Icon`` rejects an over-wide row; the
      private seams skip ``__init__`` and keep the given data.
    """
    core = host.core
    assert not hasattr(core.Image, "create")
    assert not hasattr(core.Icon, "create")
    assert core.Icon("#.#")._columns == bytes([1, 0, 1, 0, 0])
    with pytest.raises(ValueError):
        core.Icon("######")
    mono = core.Image("##", RED)
    assert (mono._data, mono.width) == (bytes([1, 1]), 2)
    multi = core.Image("R", {"R": RED})
    assert multi.width == 1 and multi._data[0] == RED
    raw = core.Image._from_encoded(bytes([3]), 1, False, RED)
    assert raw.clone()._data == bytes([3])
    assert core.Icon._from_columns(b"\x01")._columns == b"\x01"


@pytest.mark.parametrize(
    "method, call",
    [
        ("show_pattern", lambda d, c: d.show_pattern("#", duration_ms=-1)),
        ("show_icon", lambda d, c: d.show_icon(c.Icon("#"), duration_ms=-1)),
        ("show_arrow", lambda d, c: d.show_arrow(c.Icon("#"), duration_ms=-1)),
        ("show_filled", lambda d, c: d.show_filled(duration_ms=-1)),
        ("show_image", lambda d, c: d.show_image(c.Image("#"), duration_ms=-1)),
        ("show_string", lambda d, c: d.show_string("A", interval_ms=-1)),
        ("pause", lambda d, c: d.pause(-1)),
        ("repeat_until_cancelled", lambda d, c: c.Display.repeat_until_cancelled(lambda: None, -1)),
    ],
)
def test_negative_time_error_names_method_and_parameter(host, method, call):
    """A negative time raises ``ValueError("<method>(): <param> must be >= 0, got <v>")``.

    - Covers: one of the checks drifting to another message format, or naming the wrong method.
    - How: each public entry point is called with -1; the method name is matched in the message.
    """
    disp = host.disp

    async def run():
        await call(disp, host.core)

    with pytest.raises(ValueError, match=rf"^{method}\(\): \w+ must be >= 0, got -1$"):
        asyncio.run(run())


def test_deinit_then_render_filled_raises(host):
    """``render_filled`` after ``deinit`` raises. The call also expires that instance's token.

    - Covers: a deinited display still accepting draws.
    - How: a second ``Display()`` (the stub does not lock the pin); ``deinit``; ``render_filled`` raises ``RuntimeError``.
    """
    fresh = host.core.Display()
    token = fresh._token
    fresh.deinit()
    assert token.is_expired is True
    with pytest.raises(RuntimeError):
        fresh.render_filled(RED)


def test_repeat_until_cancelled_runs_inside_a_running_coroutine(host):
    """``await Display.repeat_until_cancelled(...)`` works from a coroutine, and cancelling ends it.

    - Covers: ``repeat_until_cancelled`` calling ``asyncio.run`` (``RuntimeError`` inside a running loop), or ignoring cancel.
    - How: run it as a task inside ``asyncio.run``; wait for three calls; cancel; the task ends cancelled.
    """
    calls = []

    async def run():
        task = asyncio.create_task(host.core.Display.repeat_until_cancelled(lambda: calls.append(1)))
        while len(calls) < 3:
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert len(calls) >= 3


def test_repeat_until_cancelled_awaits_async_callbacks_and_rests_between_rounds(host):
    """An ``async def`` callback is awaited, and each round ends with a ``sleep_ms(rest)``.

    - Covers: a coroutine callback never being awaited, or the rest not using whole milliseconds.
    - How: callback is ``async``; after two rounds the recorded ``("ms", 25)`` sleeps are counted; ``sleep_between_ms=25.9`` becomes 25.
    """
    done = []

    async def callback():
        done.append(1)

    async def run():
        task = asyncio.create_task(host.core.Display.repeat_until_cancelled(callback, sleep_between_ms=25.9))
        while len(done) < 2:
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert len(done) >= 2
    assert ("ms", 25) in host.sleeps
    assert all(ms == 25 for kind, ms in host.sleeps if kind == "ms")


def test_repeat_until_cancelled_default_rest_is_10_ms_and_zero_still_yields(host):
    """Default rest is 10 ms. With ``0`` a sibling task still gets a turn each round.

    - Covers: a wrong default, or ``sleep_between_ms=0`` skipping the yield.
    - How: default run records ``("ms", 10)``; a ``0`` run lets a sibling task set a flag.
    """
    ticks = []

    async def run_default():
        task = asyncio.create_task(host.core.Display.repeat_until_cancelled(lambda: ticks.append(1)))
        while not ticks:
            await asyncio.sleep(0)
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run_default())
    assert ("ms", 10) in host.sleeps

    flag = {"ran": False}

    async def sibling():
        flag["ran"] = True

    async def run_zero():
        task = asyncio.create_task(host.core.Display.repeat_until_cancelled(lambda: None, sleep_between_ms=0))
        asyncio.create_task(sibling())
        for _ in range(5):
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run_zero())
    assert flag["ran"] is True


def test_repeat_until_cancelled_negative_rest_and_callback_error(host):
    """A negative rest raises ``ValueError``. An exception in the callback ends ``repeat_until_cancelled``.

    - Covers: a negative rest being accepted, or a callback error being swallowed.
    - How: await ``repeat_until_cancelled(cb, -1)``; then a callback that raises ``KeyError`` propagates.
    """

    async def run():
        with pytest.raises(ValueError):
            await host.core.Display.repeat_until_cancelled(lambda: None, sleep_between_ms=-1)

        def boom():
            raise KeyError("x")

        with pytest.raises(KeyError):
            await host.core.Display.repeat_until_cancelled(boom)

    asyncio.run(run())


def _start_show(disp, core, noun, duration_ms):
    """Start one ``show_*`` call. ``duration_ms`` is passed by name."""
    icon = core.Icon._from_columns(b"\x1f\x00\x00\x00\x00")
    if noun == "pattern":
        return disp.show_pattern("#", RED, duration_ms=duration_ms)
    if noun == "icon":
        return disp.show_icon(icon, RED, duration_ms=duration_ms)
    if noun == "arrow":
        return disp.show_arrow(icon, RED, duration_ms=duration_ms)
    if noun == "image":
        image = core.Image._from_encoded(bytes([0x1F]), 1, False, RED)
        return disp.show_image(image, duration_ms=duration_ms)
    if noun == "filled":
        return disp.show_filled(RED, duration_ms=duration_ms)
    raise AssertionError(noun)


_SHOW_NOUNS = ("pattern", "icon", "arrow", "image", "filled")


@pytest.mark.parametrize("noun", _SHOW_NOUNS)
def test_show_returns_current_token_and_ends_blank(host, noun):
    """A ``show_*`` call holds for ``duration_ms``, then the last frame is off.

    - Covers: the picture staying lit, the call expiring its own token, or the sleep sum drifting.
    - How: ``duration_ms=100``; token still current; millisecond sleeps sum to 100; last frame blank.
    """
    disp = host.disp

    async def run():
        host.sleeps.clear()
        with _recorded_shows(host) as frames:
            token = await _start_show(disp, host.core, noun, 100)
        return token, frames

    token, frames = asyncio.run(run())
    assert token.is_expired is False
    assert token is disp._token
    assert sum(ms for kind, ms in host.sleeps if kind == "ms") == 100
    assert frames[-1] == _BLANK
    assert host.logical() == _BLANK


@pytest.mark.parametrize("noun", _SHOW_NOUNS)
def test_show_takeover_during_hold_keeps_the_other_frame(host, noun):
    """A ``render_filled`` during the hold expires the token and stays on the display.

    - Covers: the hold blanking after it was superseded, or the token staying current.
    - How: hook ``render_filled(RED)`` on the first sleep; token expired; last frame is red.
    """
    disp = host.disp

    def preempt():
        host.hook["fn"] = None
        disp.render_filled(RED)

    host.hook["fn"] = preempt

    async def run():
        return await _start_show(disp, host.core, noun, 200)

    token = asyncio.run(run())
    host.hook["fn"] = None
    assert token.is_expired is True
    assert host.logical() == tuple(tuple(RED for _ in range(WIDTH)) for _ in range(HEIGHT))


@pytest.mark.parametrize("noun", _SHOW_NOUNS)
def test_show_negative_duration_does_not_draw(host, noun):
    """A negative ``duration_ms`` raises before the display changes.

    - Covers: drawing first, or expiring the current token on the way to the error.
    - How: paint white; ``duration_ms=-1`` raises; same token; frame still white; no sleep.
    """
    disp = host.disp
    disp.render_filled(WHITE)
    before = host.logical()
    token = disp._token
    host.sleeps.clear()

    async def run():
        await _start_show(disp, host.core, noun, -1)

    with pytest.raises(ValueError, match="duration_ms must be >= 0"):
        asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False
    assert host.logical() == before
    assert host.sleeps == []


@pytest.mark.parametrize("noun", _SHOW_NOUNS)
def test_show_zero_duration_yields_once_then_blanks(host, noun):
    """``duration_ms=0`` draws one frame, yields once, then blanks.

    - Covers: returning without a yield, or leaving the picture up.
    - How: sleeps are one ``("ms", 0)``; recorded frames are the picture then all off.
    """
    disp = host.disp

    async def run():
        host.sleeps.clear()
        with _recorded_shows(host) as frames:
            token = await _start_show(disp, host.core, noun, 0)
        return token, frames

    token, frames = asyncio.run(run())
    assert token.is_expired is False
    assert host.sleeps == [("ms", 0)]
    assert len(frames) == 2
    assert frames[1] == _BLANK
    assert frames[0] != _BLANK


@pytest.mark.parametrize("noun", _SHOW_NOUNS)
def test_show_requires_duration_by_name(host, noun):
    """``duration_ms`` must be passed by name; omitting it or passing it positionally raises ``TypeError``.

    - Covers: a default of 0, or a positional time being accepted.
    - How: omit ``duration_ms``; pass the time as a positional argument. Both raise ``TypeError`` and do not draw.
    """
    disp = host.disp
    disp.render_filled(WHITE)
    before = host.logical()
    token = disp._token
    icon = host.core.Icon._from_columns(b"\x1f\x00\x00\x00\x00")
    image = host.core.Image._from_encoded(bytes([0x1F]), 1, False, RED)

    async def missing():
        if noun == "pattern":
            await disp.show_pattern("#")
        elif noun == "icon":
            await disp.show_icon(icon)
        elif noun == "arrow":
            await disp.show_arrow(icon)
        elif noun == "image":
            await disp.show_image(image)
        else:
            await disp.show_filled()

    async def positional():
        if noun == "pattern":
            await disp.show_pattern("#", RED, 1000)
        elif noun == "icon":
            await disp.show_icon(icon, RED, 1000)
        elif noun == "arrow":
            await disp.show_arrow(icon, RED, 1000)
        elif noun == "image":
            await disp.show_image(image, 0, 1000)
        else:
            await disp.show_filled(RED, 1000)

    with pytest.raises(TypeError):
        asyncio.run(missing())
    with pytest.raises(TypeError):
        asyncio.run(positional())
    assert disp._token is token
    assert host.logical() == before


def test_render_string_left_aligns_narrow_glyphs(host):
    """``render_string`` of a narrow glyph starts at display column 0.

    - Covers: the old centered start column for width 1 or 3.
    - How: ``"1"``, ``"I"``, ``"!"``; frame equals the left-aligned window; column 0 is ink.
    """
    disp = host.disp
    for text in ("1", "I", "!"):
        window = _left_window(text)
        assert window[0] != 0, text
        disp.render_string(text)
        assert host.logical() == _frame_of(window), text


def test_render_string_of_screen_text_matches_the_string(host):
    """``render_string(ScreenText(s))`` draws the same frame as ``render_string(s)``.

    - Covers: a second measurement shifting the picture, or the object changing after the call.
    - How: draw ``ScreenText("HELLO")``, then the string. Width and a fresh drain match before and after a scroll.
    """
    disp = host.disp
    prepared = ScreenText("HELLO")
    width = prepared.width
    drain = _feeder_column_bytes_of(prepared)
    disp.render_string(prepared)
    as_object = host.logical()
    disp.render_string("HELLO")
    assert host.logical() == as_object
    assert host.logical() == _frame_of(_left_window("HELLO"))

    async def scroll():
        await disp.show_string(prepared, interval_ms=0)

    asyncio.run(scroll())
    disp.render_string("K")
    assert prepared.width == width
    assert _feeder_column_bytes_of(prepared) == drain


def test_centered_accepts_number_and_screen_text_and_is_idempotent(host):
    """``centered`` accepts an int and a ``ScreenText``, and a second call keeps the picture.

    - Covers: ``centered(7)`` differing from ``centered("7")``, or the second call shifting columns.
    - How: compare column drains and the rendered frame.
    """
    once = centered(7)
    twice = centered(once)
    from_text = centered(ScreenText("7"))
    assert once.width == WIDTH
    assert _feeder_column_bytes_of(twice) == _feeder_column_bytes_of(once)
    assert _feeder_column_bytes_of(from_text) == _feeder_column_bytes_of(once)
    host.disp.render_string(once)
    frame = host.logical()
    host.disp.render_string(centered("7"))
    assert host.logical() == frame

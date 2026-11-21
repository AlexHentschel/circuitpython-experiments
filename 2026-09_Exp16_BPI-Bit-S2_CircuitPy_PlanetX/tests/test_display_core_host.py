"""Host execution of ``display.core`` behind stubs. No board, no NeoPixel hardware.

``test_no_board_core.py`` still requires that a normal import of ``display``
does not load ``core``. This module installs ``board`` / ``neopixel`` /
``adafruit_ticks`` / ``rainbowio`` only inside a fixture and removes them
before the test returns.

Out of scope here (needs the board or a design change): the real pin lock on
a second ``Display()`` and keypad scan timing.

Terminology used in test names and docstrings (not in production code): a *marquee* is the scroll with ``blank_edges=True``, where the display
starts empty, the content comes in from the right, leaves at the left, and the display ends empty (``start_col`` runs from ``WIDTH`` to ``-n``,
with ``n`` the content width in columns). A *pan* is the scroll with ``blank_edges=False``, where the first frame already shows the content's first
column at the left-most LED and the scroll stops when its last column reaches the right-most LED (``start_col`` runs from 0 to
``-max(0, n - WIDTH)``).
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


def _placed_window(columns, start_col):
    """Content column 0 lands at display column ``start_col``. Columns off the matrix are 0."""
    window = [0] * WIDTH
    n = len(columns)
    for c in range(WIDTH):
        src = c - start_col
        if 0 <= src < n:
            window[c] = columns[src]
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
    return tuple(tuple(color if (columns[x] >> y) & 1 else OFF for x in range(WIDTH)) for y in range(HEIGHT))


def _fit_window(text):
    """Centered ``WIDTH`` window for text that fits. Pad rule: ``(WIDTH - w) // 2``."""
    columns = _feeder_column_bytes(text)
    pad = (WIDTH - len(columns)) // 2
    window = [0] * WIDTH
    for i, col in enumerate(columns):
        window[pad + i] = col
    return window


_BLANK = tuple(tuple(OFF for _ in range(WIDTH)) for _ in range(HEIGHT))

_DIRTY = (9, 9, 9)  # not OFF and not any color a test draws with: a pixel nobody wrote stays visibly wrong
_GREEN = (0, 255, 0)
_BLUE = (0, 0, 255)


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
        return tuple(tuple(disp.get_pixel(x, y) for x in range(WIDTH)) for y in range(HEIGHT))

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


def _run_sleep_pollable(host, token, total_ms, poll_ms=None, on_sleep=None):
    """Run ``_sleep_pollable`` once. Return ``(sleeps_in_ms, elapsed_ms)`` as the fake clock saw them.

    ``on_sleep(call_number)`` runs at the start of the ``call_number``-th ``sleep_ms`` (1-based), before the clock advances,
    so a test can expire the token or advance the clock extra (a late wake-up) during that sleep.
    """
    calls = {"n": 0}

    def hook():
        calls["n"] += 1
        if on_sleep is not None:
            on_sleep(calls["n"])

    host.hook["fn"] = hook
    host.sleeps.clear()
    start = host.clock["now"]
    try:
        if poll_ms is None:
            asyncio.run(host.core._sleep_pollable(token, total_ms))
        else:
            asyncio.run(host.core._sleep_pollable(token, total_ms, poll_ms))
    finally:
        host.hook["fn"] = None
    return [ms for kind, ms in host.sleeps if kind == "ms"], host.clock["now"] - start


@pytest.mark.parametrize("poll_ms", (47, 10, 1))
def test_sleep_pollable_fresh_token_splits_every_total_into_consistent_chunks(host, poll_ms):
    """For every ``total_ms`` from 0 to 300 and a fresh token, the sleeps follow one arithmetic rule.

    Scenario: nothing cancels the hold and the clock has no jitter. Expected for each ``total_ms`` (``poll_ms`` = P):

    - The number of sleeps is ``max(1, ceil(total_ms / P))``: at least one ``await`` even for 0, then one per started chunk.
    - Every sleep is between 0 and P. For ``total_ms > 0`` every sleep is above 0 (no empty chunk, also not at exact multiples of P).
    - The sleeps sum to ``total_ms`` and the clock advances by exactly ``total_ms``: the wait neither ends early nor overshoots.

    This covers all boundaries (``total_ms`` of P - 1, P, P + 1, 2P, 2P + 1, ...) for three chunk sizes, including P = 1.

    - Covers: an off-by-one at a chunk boundary, a skipped ``await`` for a tiny hold, an empty last chunk, drift of the total.
    - How: run ``_sleep_pollable`` directly for each ``total_ms`` and check the three properties above.
    """
    for total_ms in range(301):
        sleeps, elapsed = _run_sleep_pollable(host, host.core.Token(), total_ms, poll_ms)
        assert len(sleeps) == max(1, -(-total_ms // poll_ms)), (total_ms, sleeps)
        assert all(0 <= ms <= poll_ms for ms in sleeps), (total_ms, sleeps)
        if total_ms > 0:
            assert all(ms > 0 for ms in sleeps), (total_ms, sleeps)
        assert sum(sleeps) == total_ms, (total_ms, sleeps)
        assert elapsed == total_ms, (total_ms, elapsed)


@pytest.mark.parametrize(
    "total_ms, expected_sleeps",
    [
        (0, [0]),
        (1, [1]),
        (17, [17]),
        (46, [46]),
        (47, [47]),
        (48, [47, 1]),
        (94, [47, 47]),
        (95, [47, 47, 1]),
        (100, [47, 47, 6]),
    ],
)
def test_sleep_pollable_default_chunk_examples(host, total_ms, expected_sleeps):
    """Concrete chunk lists for the default 47 ms chunk size, as a readable table of the rule above.

    Scenario: fresh token, no jitter. Expected: 0 gives one ``sleep_ms(0)`` (other coroutines still get a turn); a hold of up to 47 ms is
    one sleep of exactly that length; longer holds are 47 ms chunks followed by the time left (48 gives 47 then 1; 94 gives 47 then 47,
    with no empty third chunk; 95 gives 47, 47, 1; 100 gives 47, 47, 6).

    - Covers: wrong chunking at the first two chunk boundaries.
    - How: run ``_sleep_pollable`` directly and compare the recorded sleeps with the list.
    """
    sleeps, _ = _run_sleep_pollable(host, host.core.Token(), total_ms)
    assert sleeps == expected_sleeps


@pytest.mark.parametrize("total_ms", (-1, -47, -1000))
def test_sleep_pollable_negative_total_is_one_immediate_yield(host, total_ms):
    """A negative ``total_ms`` behaves like 0: one sleep, no chunk loop, no wait.

    Scenario: fresh token, ``total_ms`` of -1, -47 or -1000 (the public methods reject negatives, so this is the private contract).
    Expected: exactly one ``sleep_ms`` call, made with 0 (the function clamps the negative value itself, because
    ``asyncio.sleep_ms`` does not document negative values): one immediate yield.

    - Covers: a negative value entering the chunk loop, reaching ``sleep_ms`` unclamped, sleeping several times, or no ``await``.
    - How: call ``_sleep_pollable`` directly; the recorded sleeps must be ``[0]``.
    """
    sleeps, _ = _run_sleep_pollable(host, host.core.Token(), total_ms)
    assert sleeps == [0]


@pytest.mark.parametrize("poll_ms", (47, 10, 1))
def test_sleep_pollable_expired_at_entry_never_waits(host, poll_ms):
    """A token that is already expired makes every hold from 0 to 300 ms one immediate yield.

    Scenario: another display call took over before the hold started (``total_ms`` 0 to 300, chunk size 47, 10 or 1).
    Expected: exactly one ``sleep_ms(0)``. The function does not wait the requested time, not even a first chunk, but it
    still awaits once so that other coroutines get a turn. The clock does not advance.

    - Covers: an expired token still sleeping its full time or a first chunk, or returning without any ``await``.
    - How: expire the token before the call; check the sleeps are ``[0]`` and the elapsed time is 0.
    """
    for total_ms in range(301):
        token = host.core.Token()
        token._is_expired = True
        sleeps, elapsed = _run_sleep_pollable(host, token, total_ms, poll_ms)
        assert sleeps == [0], (total_ms, sleeps)
        assert elapsed == 0


@pytest.mark.parametrize(
    "total_ms, expire_during_call, expected_sleeps",
    [
        (200, 1, [47, 0]),
        (200, 2, [47, 47, 0]),
        (200, 4, [47, 47, 47, 47, 0]),
        (200, 5, [47, 47, 47, 47, 12]),
        (100, 2, [47, 47, 0]),
        (100, 3, [47, 47, 6]),
        (47, 1, [47]),
    ],
)
def test_sleep_pollable_token_expiring_during_the_hold(host, total_ms, expire_during_call, expected_sleeps):
    """The token expires while the ``expire_during_call``-th sleep is running (another display call takes over mid-hold).

    Expected: that sleep still finishes, because ``sleep_ms`` cannot be interrupted. Then the function stops waiting. If more than one
    chunk was still planned, the last sleep becomes ``sleep_ms(0)`` (one immediate yield) instead of the remaining time. So a superseded
    hold reacts within one chunk, never after the full hold. Cases:

    - 200 ms, expiry during sleep 1, 2 or 4 (a loop chunk): the sleeps so far, then ``0``. The planned 153, 106 or 12 ms are not waited.
    - 200 ms, expiry during sleep 5 (the last chunk, the 12 ms left): nothing left to cut, the sleeps are unchanged.
    - 100 ms, expiry during sleep 2 (the second 47 ms chunk): the 6 ms left becomes ``0``. During sleep 3 (the 6 ms chunk): unchanged.
    - 47 ms, expiry during its only sleep: unchanged.

    - Covers: continuing the full hold after another display call took over, or cutting a chunk that has already started.
    - How: the sleep hook expires the token at the given call number; compare the recorded sleeps with the list.
    """
    token = host.core.Token()

    def expire(call_number):
        if call_number == expire_during_call:
            token._is_expired = True

    sleeps, _ = _run_sleep_pollable(host, token, total_ms, on_sleep=expire)
    assert sleeps == expected_sleeps


@pytest.mark.parametrize(
    "extra_late_ms, late_during_call, expected_sleeps",
    [
        (30, 1, [47, 23]),
        (80, 1, [47, 0]),
        (30, 3, [47, 47, 6]),
        (3, 1, [47, 47, 3]),
    ],
)
def test_sleep_pollable_late_wake_ups_never_end_the_hold_early(host, extra_late_ms, late_during_call, expected_sleeps):
    """Another coroutine delays the wake-up. The hold re-reads the clock, so lateness is absorbed and never ends the hold early.

    Scenario: a 100 ms hold, fresh token, and the ``late_during_call``-th sleep takes ``extra_late_ms`` longer than requested (the clock
    jumps ahead, as when another task runs a long time without ``await``). Expected:

    - 30 ms late in the first chunk: the time left shrinks from 53 to 23, so the sleeps are 47 then 23. The total elapsed is 100.
    - 80 ms late in the first chunk: the deadline has already passed, the time left is -27. The function clamps it to 0 itself
      (``asyncio.sleep_ms`` does not document negative values), so the last sleep is 0: one immediate yield. The total elapsed is 127.
    - 30 ms late in the last chunk (the third): nothing can make up for it. The sleeps are 47, 47, 6 and the total elapsed is 130.
    - 3 ms late in the first chunk: the time left is 50, still above 47, so the loop runs another full chunk. The sleeps are 47, 47, 3
      and the total elapsed is 100.

    In all cases the elapsed time is at least ``total_ms``: a hold is never shorter than requested.

    - Covers: summing requested chunks instead of reading the clock (drift), a negative final sleep breaking the loop, ending early.
    - How: the sleep hook advances the fake clock extra during the given call; compare sleeps; check ``elapsed >= total_ms``.
    """
    total_ms = 100

    def late(call_number):
        if call_number == late_during_call:
            host.clock["now"] += extra_late_ms

    sleeps, elapsed = _run_sleep_pollable(host, host.core.Token(), total_ms, on_sleep=late)
    assert sleeps == expected_sleeps
    assert elapsed >= total_ms


def test_sleep_pollable_survives_tick_counter_wraparound(host):
    """The hold is correct when the tick counter wraps around during it.

    Scenario: the millisecond tick counter is 50 ms before its maximum, and a 100 ms hold runs across the wrap.
    Expected: the same sleeps as without wraparound, 47, 47, 6, and exactly 100 ms elapsed (``ticks_diff`` handles the wrap).

    - Covers: comparing raw tick values instead of using ``ticks_diff``.
    - How: set the fake clock near ``_TICKS_MAX``; run the hold; compare sleeps.
    """
    host.clock["now"] = _TICKS_MAX - 50
    sleeps, elapsed = _run_sleep_pollable(host, host.core.Token(), 100)
    assert sleeps == [47, 47, 6]
    assert elapsed == 100


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


def test_show_string_empty_holds_blank_for_the_duration(host):
    """``show_string('')`` draws off pixels and waits ``duration_ms``.

    - Covers: empty text leaving the previous frame, or holding ``duration_ms * WIDTH``.
    - How: ``duration_ms=100``; millisecond sleeps sum to 100; every logical pixel is off.
    """
    disp = host.disp
    disp.render_filled(RED)

    async def run():
        host.sleeps.clear()
        await disp.show_string("", duration_ms=100, start_col=0)
        assert sum(ms for kind, ms in host.sleeps if kind == "ms") == 100
        assert host.logical() == tuple(tuple(OFF for _ in range(WIDTH)) for _ in range(HEIGHT))

    asyncio.run(run())


def test_scroll_string_marquee_frame_count(host):
    """A marquee sleeps once per ``1 + columns + WIDTH`` frame.

    - Covers: the scroll-out blank frame being skipped, or a hold being used for wide text.
    - How: ``scroll_string("HI")``; count ``show`` calls; first and last frames are blank; a middle frame is not.
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
        await disp.scroll_string("HI", interval_ms=150)

    asyncio.run(run())
    assert len(frames) == 1 + columns + WIDTH
    blank = tuple(tuple(OFF for _ in range(WIDTH)) for _ in range(HEIGHT))
    assert frames[0] == blank
    assert frames[-1] == blank
    assert any(frame != blank for frame in frames)


def test_scroll_image_pan_visits_each_window(host):
    """A pan of a 10-wide image visits offsets 0 through 5, one column at a time.

    - Covers: skipping a middle window, or stopping one column early.
    - How: record ``_render_window`` offsets for ``blank_edges=False``.
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
            await disp.scroll_image(image, interval_ms=10, blank_edges=False)

        asyncio.run(run())
    finally:
        host.core.Image._render_window = orig
    assert offsets == [0, 1, 2, 3, 4, 5]


def test_scroll_cancel_does_not_draw_another_frame(host):
    """A cancel during the frame sleep returns before the next ``_render_window``.

    - Covers: one more frame after the token expires.
    - How: ``render_filled`` inside the first ``asyncio.sleep_ms``; the only offset is the marquee's first window; token expired.
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
            return await disp.scroll_image(image, interval_ms=100)

        token = asyncio.run(run())
    finally:
        host.core.Image._render_window = orig
        host.hook["fn"] = None
    assert offsets == [-WIDTH]
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
        await disp.show_image(image, start_col=-2, duration_ms=-5)

    with pytest.raises(ValueError, match="'duration_ms' must be >= 0"):
        asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False
    assert host.logical() == before
    assert host.sleeps == []


def test_show_string_negative_duration_does_not_cancel(host):
    """``show_string`` rejects a negative duration before ``_acquire``.

    - Covers: clamping, or expiring the current token on the way to the error.
    - How: ``duration_ms=-1`` raises ``ValueError``; same token, not expired.
    """
    disp = host.disp
    token = disp._token

    async def run():
        with pytest.raises(ValueError):
            await disp.show_string("I", duration_ms=-1, start_col=0)

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
    assert disp.render_string("A", start_col=0) is None
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
    disp.render_string("7", start_col=0)
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
        host.disp.render_string(prepared, start_col=0)
        assert host.logical() == _frame_of(centered_window), text
        host.disp.render_string(text, start_col=0)
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
        disp.render_string(text, start_col=0)
        assert host.logical() == _frame_of(columns[:WIDTH]), text
        centered_window = columns[first : first + WIDTH]
        assert len(centered_window) == WIDTH
        disp.render_string(centered(text), start_col=0)
        assert host.logical() == _frame_of(centered_window), text


def test_render_string_empty_is_blank(host):
    """``render_string('')`` draws an all-off frame and does not sleep.

    - Covers: raising on an empty string, or leaving the previous picture up.
    - How: fill red, then render ``""``; every pixel off; sleeps empty.
    """
    disp = host.disp
    disp.render_filled(RED)
    host.sleeps.clear()
    disp.render_string("", start_col=0)
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
        disp.render_string("K", start_col=0)
        after["shows"] = disp._pixels.shows
        after["frame"] = host.logical()

    host.hook["fn"] = preempt
    try:

        async def run():
            return await disp.scroll_string("STAGE2", interval_ms=80)

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
        disp.render_string(str(n), start_col=0)
        as_text = host.logical()
        disp.render_number(n, start_col=0)
        assert host.logical() == as_text


def test_show_string_fit_path_ends_blank(host):
    """A fitting ``show_string`` holds for ``duration_ms``, then the last frame is blank.

    - Covers: the letter staying lit, a hold of ``duration_ms * WIDTH``, or the call expiring its own token.
    - How: ``"A"``, ``duration_ms=100``; sleeps sum to 100; frames are the letter then all off; token still current.
    """
    disp = host.disp
    expected = _frame_of(_left_window("A"))

    async def run():
        host.sleeps.clear()
        with _recorded_shows(host) as frames:
            token = await disp.show_string("A", duration_ms=100, start_col=0)
        return token, list(frames)

    token, frames = asyncio.run(run())
    assert sum(ms for kind, ms in host.sleeps if kind == "ms") == 100
    assert frames[0] == expected
    assert frames[-1] == _BLANK
    assert token.is_expired is False
    assert disp._token is token


def test_show_string_fit_preempted_during_hold_keeps_the_other_frame(host):
    """A Tier 1 write during a fitting hold wins. The hold does not blank that frame.

    - Covers: a blank drawn after ``render_filled``, or the token staying current.
    - How: hook ``render_filled(RED)`` on the first sleep of ``show_string("A", duration_ms=100)``; frame stays red.
    """
    disp = host.disp

    def preempt():
        host.hook["fn"] = None
        disp.render_filled(RED)

    host.hook["fn"] = preempt
    try:

        async def run():
            return await disp.show_string("A", duration_ms=100, start_col=0)

        token = asyncio.run(run())
    finally:
        host.hook["fn"] = None
    assert token.is_expired is True
    assert host.logical() == tuple(tuple(RED for _ in range(WIDTH)) for _ in range(HEIGHT))


def test_scroll_string_loop_cancelled_leaves_the_other_frame(host):
    """``loop=True`` stops when another display call takes over, and that picture stays up.

    - Covers: the scroll blanking after it was superseded, or ignoring the takeover.
    - How: hook ``render_filled(RED)`` on the first sleep of ``scroll_string(..., loop=True)``; frame stays red; token expired.
    """
    disp = host.disp

    def preempt():
        host.hook["fn"] = None
        disp.render_filled(RED)

    host.hook["fn"] = preempt
    try:

        async def run():
            return await disp.scroll_string("A", interval_ms=100, loop=True)

        token = asyncio.run(run())
    finally:
        host.hook["fn"] = None
    assert token.is_expired is True
    assert host.logical() == tuple(tuple(RED for _ in range(WIDTH)) for _ in range(HEIGHT))


def test_show_string_fit_interval_zero_flashes_then_blanks(host):
    """``duration_ms=0`` yields once, then the screen is blank.

    - Covers: skipping the yield, leaving the text up, or expiring the token.
    - How: ``"A"``; sleeps are ``[("ms", 0)]``; frames are the letter then all off; token not expired.
    """
    disp = host.disp
    expected = _frame_of(_left_window("A"))

    async def run():
        host.sleeps.clear()
        with _recorded_shows(host) as frames:
            token = await disp.show_string("A", duration_ms=0, start_col=0)
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
        return await disp.show_number(7, duration_ms=40, start_col=0)

    token = asyncio.run(run())
    assert token.is_expired is False
    assert host.logical() == _BLANK
    assert sum(ms for kind, ms in host.sleeps if kind == "ms") == 40
    disp.render_string("7", start_col=0)
    held = host.logical()
    assert held != _BLANK
    host.sleeps.clear()
    assert disp.render_number(7, start_col=0) is None
    assert host.sleeps == []
    assert host.logical() == held


@pytest.mark.parametrize("columns", (b"", b"\xff", b"\x01\x02\x04"))
def test_short_icon_is_padded_with_off_columns(host, columns):
    """An ``Icon`` with fewer than ``WIDTH`` column bytes draws its columns and leaves the rest off, in one ``show``.

    - Scenario: an icon of 0, 1 or 3 bytes (only reachable through the private ``_from_columns`` seam; the public constructors always give
      ``WIDTH`` bytes), drawn over a lit display at ``start_col`` = 0, 2 and -1.
    - Expected: the given columns sit at display column ``start_col`` (columns cut off at either edge), every other pixel is off, and exactly one
      ``show`` happens per call. The call never raises ``IndexError`` and never leaves a half-written, unlatched buffer.
    - Covers: reading ``data`` past its end, a stale pixel surviving next to a short icon, or latching a half-written buffer.
    - How: dirty the display, render, compare the frame with ``_placed_window``; compare ``pixels.shows`` and the latch.
    """
    disp = host.disp
    pixels = disp._pixels
    icon = host.core.Icon._from_columns(columns)
    for start_col in (0, 2, -1):
        disp.render_filled(_DIRTY)
        shows = pixels.shows
        disp.render_icon(icon, WHITE, start_col=start_col)
        assert pixels.shows == shows + 1, start_col
        assert pixels.buf == pixels.latched, start_col
        assert host.logical() == _frame_of(_placed_window(list(columns), start_col)), (columns, start_col)


def test_render_pattern_clips_a_wide_row_image_keeps_it(host):
    """``render_pattern`` drops columns past ``WIDTH``. ``Image(pattern)`` keeps them as width.

    - Covers: both entry points silently using the same width rule.
    - How: six hashes; the rendered row is five on-pixels; the image reports width 6.
    """
    disp = host.disp
    disp.render_pattern("######\n#", start_col=0)
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
        ("show_pattern", lambda d, c: d.show_pattern("#", duration_ms=-1, start_col=0)),
        ("show_icon", lambda d, c: d.show_icon(c.Icon("#"), duration_ms=-1, start_col=0)),
        ("show_arrow", lambda d, c: d.show_arrow(c.Icon("#"), duration_ms=-1, start_col=0)),
        ("show_filled", lambda d, c: d.show_filled(duration_ms=-1)),
        ("show_image", lambda d, c: d.show_image(c.Image("#"), duration_ms=-1, start_col=0)),
        ("show_string", lambda d, c: d.show_string("A", duration_ms=-1, start_col=0)),
        ("show_number", lambda d, c: d.show_number(7, duration_ms=-1, start_col=0)),
        ("scroll_string", lambda d, c: d.scroll_string("A", interval_ms=-1)),
        ("scroll_number", lambda d, c: d.scroll_number(7, interval_ms=-1)),
        ("scroll_image", lambda d, c: d.scroll_image(c.Image("#"), interval_ms=-1)),
        ("pause", lambda d, c: d.pause(-1)),
        ("repeat_until_cancelled", lambda d, c: c.Display.repeat_until_cancelled(lambda: None, -1)),
    ],
)
def test_negative_time_error_names_method_and_parameter(host, method, call):
    """A negative time raises ``ValueError("<method>(): '<param>' must be >= 0, got '<v>'")``.

    - Covers: one of the checks drifting to another message format, or naming the wrong method.
    - How: each public entry point is called with -1; the method name is matched in the message.
    """
    disp = host.disp

    async def run():
        await call(disp, host.core)

    with pytest.raises(ValueError, match=rf"^{method}\(\): '\w+' must be >= 0, got '-1'$"):
        asyncio.run(run())


@pytest.mark.parametrize("bad", (True, 1.5, "5"))
@pytest.mark.parametrize(
    "method, call",
    [
        ("show_filled", lambda d, c, bad: d.show_filled(duration_ms=bad)),
        ("show_string", lambda d, c, bad: d.show_string("A", duration_ms=bad, start_col=0)),
        ("scroll_string", lambda d, c, bad: d.scroll_string("A", interval_ms=bad)),
        ("scroll_number", lambda d, c, bad: d.scroll_number(7, interval_ms=bad)),
        ("scroll_image", lambda d, c, bad: d.scroll_image(c.Image("#"), interval_ms=bad)),
        ("pause", lambda d, c, bad: d.pause(bad)),
        ("repeat_until_cancelled", lambda d, c, bad: c.Display.repeat_until_cancelled(lambda: None, bad)),
    ],
)
def test_time_must_be_an_integer(host, method, call, bad):
    """``float``, ``bool`` or ``str`` time raises ``TypeError("<method>(): '<param>' must be an integer, got '<v>'")``.

    - Covers: accepting ``True`` because ``bool`` is an ``int``, silently truncating ``float``, or different message format.
      Includes ``scroll_number``, which shares the interval check with the other scrolls.
    - How: each listed entry point is called with ``True``, ``1.5`` and ``"5"``. The token stays, the frame stays, and nothing sleeps.
    """
    disp = host.disp
    disp.render_filled(RED)
    before = host.logical()
    token = disp._token
    host.sleeps.clear()

    async def run():
        await call(disp, host.core, bad)

    with pytest.raises(TypeError, match=rf"^{method}\(\): '\w+' must be an integer, got '{bad}'$"):
        asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False
    assert host.logical() == before
    assert host.sleeps == []


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
    - How: callback is ``async``; after two rounds the recorded ``("ms", 25)`` sleeps are counted; ``sleep_between_ms=25``.
    """
    done = []

    async def callback():
        done.append(1)

    async def run():
        task = asyncio.create_task(host.core.Display.repeat_until_cancelled(callback, sleep_between_ms=25))
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
        return disp.show_pattern("#", RED, duration_ms=duration_ms, start_col=0)
    if noun == "icon":
        return disp.show_icon(icon, RED, duration_ms=duration_ms, start_col=0)
    if noun == "arrow":
        return disp.show_arrow(icon, RED, duration_ms=duration_ms, start_col=0)
    if noun == "image":
        image = core.Image._from_encoded(bytes([0x1F]), 1, False, RED)
        return disp.show_image(image, duration_ms=duration_ms, start_col=0)
    if noun == "filled":
        return disp.show_filled(RED, duration_ms=duration_ms)
    if noun == "string":
        return disp.show_string("A", RED, duration_ms=duration_ms, start_col=0)
    if noun == "number":
        return disp.show_number(7, RED, duration_ms=duration_ms, start_col=0)
    raise AssertionError(noun)


_SHOW_NOUNS = ("pattern", "icon", "arrow", "image", "filled", "string", "number")


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

    with pytest.raises(ValueError, match="'duration_ms' must be >= 0"):
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
            await disp.show_pattern("#", start_col=0)
        elif noun == "icon":
            await disp.show_icon(icon, start_col=0)
        elif noun == "arrow":
            await disp.show_arrow(icon, start_col=0)
        elif noun == "image":
            await disp.show_image(image, start_col=0)
        elif noun == "string":
            await disp.show_string("A", start_col=0)
        elif noun == "number":
            await disp.show_number(7, start_col=0)
        else:
            await disp.show_filled()

    async def positional():
        if noun == "pattern":
            await disp.show_pattern("#", RED, 1000, start_col=0)
        elif noun == "icon":
            await disp.show_icon(icon, RED, 1000, start_col=0)
        elif noun == "arrow":
            await disp.show_arrow(icon, RED, 1000, start_col=0)
        elif noun == "image":
            await disp.show_image(image, 1000, start_col=0)
        elif noun == "string":
            await disp.show_string("A", RED, 1000, start_col=0)
        elif noun == "number":
            await disp.show_number(7, RED, 1000, start_col=0)
        else:
            await disp.show_filled(RED, 1000)

    with pytest.raises(TypeError):
        asyncio.run(missing())
    with pytest.raises(TypeError):
        asyncio.run(positional())
    assert disp._token is token
    assert host.logical() == before


_START_COL_NOUNS = ("pattern", "icon", "arrow", "image", "string", "number")


@pytest.mark.parametrize("verb", ("render", "show"))
@pytest.mark.parametrize("noun", _START_COL_NOUNS)
def test_start_col_is_keyword_only_and_defaults_to_zero(host, verb, noun):
    """``start_col`` must be passed by name, for every ``render_*`` and ``show_*`` method that takes it, and defaults to 0.

    - Covers: ``start_col`` being accepted as a positional argument, or the default not being column 0.
    - How: pass it positionally: ``TypeError``, no takeover, picture unchanged. Omitting it draws the same frame as ``start_col=0``.
    """
    disp = host.disp
    disp.render_filled(WHITE)
    before = host.logical()
    token = disp._token
    icon = host.core.Icon._from_columns(b"\x1f\x00\x00\x00\x00")
    image = host.core.Image._from_encoded(bytes([0x1F]), 1, False, RED)
    content = {"pattern": "#", "icon": icon, "arrow": icon, "image": image, "string": "A", "number": 7}[noun]
    method = getattr(disp, f"{verb}_{noun}")
    has_color = noun != "image"
    extra = {"duration_ms": 0} if verb == "show" else {}

    def call(*args, **kwargs):
        result = method(content, *args, **kwargs, **extra)
        if verb == "show":
            asyncio.run(result)

    with pytest.raises(TypeError):
        call(RED, 0) if has_color else call(0)
    assert disp._token is token
    assert host.logical() == before
    call(start_col=0)
    explicit = host.logical()
    disp.render_filled(WHITE)
    call()
    assert host.logical() == explicit


def test_render_string_left_aligns_narrow_glyphs(host):
    """``render_string`` of a narrow glyph starts at display column 0.

    - Covers: the old centered start column for width 1 or 3.
    - How: ``"1"``, ``"I"``, ``"!"``; frame equals the left-aligned window; column 0 is ink.
    """
    disp = host.disp
    for text in ("1", "I", "!"):
        window = _left_window(text)
        assert window[0] != 0, text
        disp.render_string(text, start_col=0)
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
    disp.render_string(prepared, start_col=0)
    as_object = host.logical()
    disp.render_string("HELLO", start_col=0)
    assert host.logical() == as_object
    assert host.logical() == _frame_of(_left_window("HELLO"))

    async def scroll():
        await disp.scroll_string(prepared, interval_ms=0)

    asyncio.run(scroll())
    disp.render_string("K", start_col=0)
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
    host.disp.render_string(once, start_col=0)
    frame = host.logical()
    host.disp.render_string(centered("7"), start_col=0)
    assert host.logical() == frame


def _red_frame():
    return tuple(tuple(RED for _ in range(WIDTH)) for _ in range(HEIGHT))


@pytest.mark.parametrize("text", ("", "1", "A", "HELLO"))
@pytest.mark.parametrize("as_screen_text", (False, True))
def test_render_string_x_matches_the_shifted_columns(host, text, as_screen_text):
    """``render_string(..., start_col=k)`` places a full column drain at display column ``k``.

    - Covers: a clamp off by one, a skip one column short, or a non-blank frame when ``start_col`` is past the right edge.
    - How: ``start_col`` from ``-(WIDTH + 1)`` to ``WIDTH + 2``. Oracle is the drain. One ``show``. Both a ``str`` and a ``ScreenText``.
    """
    disp = host.disp
    columns = _feeder_column_bytes(text)
    content = ScreenText(text) if as_screen_text else text
    for start_col in range(-(WIDTH + 1), WIDTH + 3):
        shows = disp._pixels.shows
        disp.render_string(content, start_col=start_col)
        assert disp._pixels.shows == shows + 1, (text, start_col, as_screen_text)
        assert host.logical() == _frame_of(_placed_window(columns, start_col)), (text, start_col, as_screen_text)


def test_render_string_past_the_right_edge_does_not_read_columns(host):
    """``start_col >= WIDTH`` draws a blank frame and does not pull a column from the reader.

    - Covers: the clamp treating ``start_col == WIDTH`` as a real column, or still calling ``next_column``.
    - How: count ``_ColumnReader.next_column`` for ``""``, ``"A"``, ``"HELLO"`` at ``WIDTH``, ``WIDTH + 1``, ``WIDTH + 2``.
    """
    reads = {"n": 0}
    orig = _ColumnReader.next_column

    def counting(self):
        reads["n"] += 1
        return orig(self)

    _ColumnReader.next_column = counting
    try:
        for text in ("", "A", "HELLO"):
            for start_col in (WIDTH, WIDTH + 1, WIDTH + 2):
                reads["n"] = 0
                host.disp.render_string(text, start_col=start_col)
                assert reads["n"] == 0, (text, start_col)
                assert host.logical() == _BLANK, (text, start_col)
    finally:
        _ColumnReader.next_column = orig


def test_render_icon_arrow_and_image_x_matches_shifted_columns(host):
    """Icons, arrows and images place column 0 at display column ``start_col``.

    - Covers: the ``start_col == 0`` path and the window path disagreeing, or a shift in the wrong direction.
    - How: distinct column bytes; ``start_col`` walks past both edges; default ``start_col`` matches explicit ``0``. A 5-wide and a 10-wide image.
    """
    disp = host.disp
    columns = [0x01, 0x02, 0x04, 0x08, 0x10]
    icon = host.core.Icon._from_columns(bytes(columns))
    for start_col in range(-(WIDTH + 1), WIDTH + 3):
        disp.render_icon(icon, WHITE, start_col=start_col)
        assert host.logical() == _frame_of(_placed_window(columns, start_col)), start_col
        disp.render_arrow(icon, RED, start_col=start_col)
        assert host.logical() == _frame_of(_placed_window(columns, start_col), RED), start_col
    wide = [1, 2, 4, 8, 16, 1, 2, 4, 8, 16]
    images = (
        (host.core.Image._from_encoded(bytes(columns), 5, False, WHITE), columns),
        (host.core.Image._from_encoded(bytes(wide), 10, False, WHITE), wide),
    )
    for image, cols in images:
        for start_col in range(-(len(cols) + 1), WIDTH + 2):
            disp.render_image(image, start_col=start_col)
            assert host.logical() == _frame_of(_placed_window(cols, start_col)), (len(cols), start_col)
    disp.render_icon(icon, start_col=0)
    at_default = host.logical()
    disp.render_icon(icon, start_col=0)
    assert host.logical() == at_default
    disp.render_image(images[1][0], start_col=0)
    at_default = host.logical()
    disp.render_image(images[1][0], start_col=0)
    assert host.logical() == at_default


def test_render_pattern_x_pans_the_parsed_columns(host):
    """``render_pattern`` at ``start_col`` shows the parsed pattern shifted, including the ``start_col == 0`` scan.

    - Covers: a wide row staying clipped when ``start_col`` is negative, or the fused scan disagreeing with the parsed columns.
    - How: six hashes; oracle is ``Image``'s column bytes placed at ``start_col``, for ``start_col`` from -6 to ``WIDTH + 1``.
    """
    disp = host.disp
    columns = list(host.core.Image("######")._data)
    assert len(columns) == 6
    for start_col in range(-6, WIDTH + 2):
        disp.render_pattern("######", start_col=start_col)
        assert host.logical() == _frame_of(_placed_window(columns, start_col)), start_col
    disp.render_pattern("######", start_col=0)
    assert host.logical() == _frame_of(_placed_window(columns, 0))


# Display offsets: every start_col that changes the picture for content up to ~15 columns wide, plus values far outside any picture.
_START_COL_SWEEP = tuple(range(-(3 * WIDTH), 3 * WIDTH + 1)) + (-50, 50, -1000, 1000)

# (id, pattern). Letters need a color dict, ``#`` is the lit cell for a single color. Whitespace is limited to the characters
# ``render_pattern`` skips (space, tab, CR), so the cold-path ``Image`` parser is a valid oracle for each of them.
_PATTERNS = (
    ("empty", ""),
    ("only-newlines", "\n\n\n"),
    ("single-cell", "#"),
    ("short-rows-no-trailing-newline", "#.#\n.#.\n#.#"),
    ("short-rows-trailing-newline", "#.#\n.#.\n#.#\n"),
    ("wide-and-narrow-rows", "RRRRRRRR\nG\n#G#G#G#G#G#G"),
    ("full-screen", "#####\n#####\n#####\n#####\n#####"),
    ("exactly-height-rows-trailing-newline", "#\n#\n#\n#\n#\n"),
    ("more-rows-than-height", "#\nR\nG\n#\nR\nG\n#"),
    ("whitespace-and-blank-lines", "  # .\t\n\n \t \n\r\nR\t G\r\n"),
    ("unknown-characters", "?!#ab"),
)


@pytest.mark.parametrize("degrees", (0, 90, 180, 270))
@pytest.mark.parametrize("use_dict", (False, True), ids=("single-color", "color-dict"))
@pytest.mark.parametrize("pattern", [p for _, p in _PATTERNS], ids=[name for name, _ in _PATTERNS])
def test_render_pattern_x_equals_the_parsed_image_at_x_for_every_x(host, pattern, use_dict, degrees):
    """``render_pattern(p, color, start_col)`` draws the same frame as ``render_image(Image(p, color), start_col)``, for every ``start_col``.

    - Scenario: each pattern shape (empty, short rows, wide rows, too many rows, whitespace, unknown characters, with and without a
      trailing newline) as a single color and as a color dict, under each rotation, for ``start_col`` from ``-3 * WIDTH`` to ``3 * WIDTH`` and
      for ``start_col`` = +-50 and +-1000. The display is lit with a dirty color before every call.
    - Expected: the two frames are equal pixel by pixel. In particular a column the pattern does not reach (left of ``start_col``, right of the
      row end, below the last row, or left of 0 for ``start_col < 0``) is off, never the dirty color. Exactly one ``show`` per call.
    - Covers: a stale pixel left behind in the left or right margin, an off-by-one at either edge, ``start_col`` past ``WIDTH``, a wide row not
      cut off, the early return at ``HEIGHT`` rows, the unterminated last row, a LUT index error visible only under rotation.
    - How: the cold-path ``Image`` and its window renderer are the independent oracle (a different parser and a different writer).
    """
    disp = host.disp
    disp.set_rotation(degrees)
    color = {"#": _BLUE, "R": RED, "G": _GREEN} if use_dict else RED
    image = host.core.Image(pattern, color)
    pixels = disp._pixels
    for start_col in _START_COL_SWEEP:
        disp.render_filled(_DIRTY)
        shows = pixels.shows
        disp.render_pattern(pattern, color, start_col=start_col)
        assert pixels.shows == shows + 1, start_col
        got = host.logical()
        disp.render_filled(_DIRTY)
        disp.render_image(image, start_col=start_col)
        assert got == host.logical(), (pattern, start_col)


def test_render_pattern_x_pinned_frames(host):
    """Hand-computed frames for ``render_pattern`` at a few offsets, independent of any other renderer.

    - Scenario: pattern ``"#.#"`` (three columns: on, off, on) in red, at ``start_col`` = 0, 2, 4, 5, -1, -2, -3.
    - Expected: row 0 holds the cells that land on display columns 0..4 (``start_col`` = 2 gives columns 2 and 4; ``start_col`` = 4 only column 4; ``start_col`` = 5
      nothing; ``start_col`` = -1 gives column 1 only; ``start_col`` = -2 gives column 0 only; ``start_col`` = -3 nothing). Rows 1..4 are off.
    - Covers: the equivalence test and the code under test sharing a bug (both shifted the wrong way, say).
    - How: expected on-columns are written out by hand.
    """
    disp = host.disp
    expected_on_columns = {0: (0, 2), 2: (2, 4), 4: (4,), 5: (), -1: (1,), -2: (0,), -3: ()}
    for start_col, on in expected_on_columns.items():
        disp.render_filled(_DIRTY)
        disp.render_pattern("#.#", RED, start_col=start_col)
        frame = host.logical()
        assert frame[0] == tuple(RED if c in on else OFF for c in range(WIDTH)), start_col
        assert all(pixel == OFF for row in frame[1:] for pixel in row), start_col


def test_render_pattern_skips_only_space_tab_and_cr_unlike_image(host):
    """``render_pattern`` treats a form feed as a cell (off), ``Image`` skips it. The documented whitespace difference.

    - Scenario: pattern ``"#\\f#"`` (hash, form feed, hash).
    - Expected: ``render_pattern`` lights columns 0 and 2 (the form feed takes column 1). ``Image`` lights columns 0 and 1.
    - Covers: the two parsers silently converging or diverging from what the ``Image`` and ``render_pattern`` docstrings promise.
    - How: render both, read the top row.
    """
    disp = host.disp
    disp.render_pattern("#\f#", RED, start_col=0)
    assert host.logical()[0] == (RED, OFF, RED, OFF, OFF)
    disp.render_image(host.core.Image("#\f#", RED), start_col=0)
    assert host.logical()[0] == (RED, RED, OFF, OFF, OFF)


@pytest.mark.parametrize("degrees", (0, 90, 180, 270))
@pytest.mark.parametrize("columns", ([0x01, 0x02, 0x04, 0x08, 0x10], [0x1F] * 5, [0x00] * 5, [0x10, 0x00, 0x01, 0x00, 0x1F]))
def test_render_icon_and_arrow_x_for_every_x_on_a_dirty_display(host, columns, degrees):
    """``render_icon`` and ``render_arrow`` place the icon's column 0 at display column ``start_col``, and nothing else is lit.

    - Scenario: four column layouts (diagonal, all lit, all off, mixed), each rotation, ``start_col`` from ``-3 * WIDTH`` to ``3 * WIDTH`` and
      +-50, +-1000, drawn over a display lit with a dirty color. One ``show`` per call.
    - Expected: ``_placed_window(columns, start_col)`` in the given color, every other pixel off (not the dirty color), including ``start_col >= WIDTH``
      and ``start_col <= -WIDTH`` where the whole display is blank.
    - Covers: a margin column left unwritten, an off-by-one when the icon is partly cut off, ``src`` indexing at either edge, far
      offsets, a LUT error visible only under rotation.
    - How: ``_placed_window`` is the oracle, computed from the column bytes alone.
    """
    disp = host.disp
    disp.set_rotation(degrees)
    icon = host.core.Icon._from_columns(bytes(columns))
    pixels = disp._pixels
    for start_col in _START_COL_SWEEP:
        for render, color in ((disp.render_icon, WHITE), (disp.render_arrow, RED)):
            disp.render_filled(_DIRTY)
            shows = pixels.shows
            render(icon, color, start_col=start_col)
            assert pixels.shows == shows + 1, start_col
            assert host.logical() == _frame_of(_placed_window(columns, start_col), color), (columns, start_col)


def test_render_string_of_centered_text_shifts_with_x(host):
    """``render_string(centered("1"), start_col=1)`` is the centered picture moved one column right.

    - Covers: ``start_col`` being ignored for a ``ScreenText``, or the shift going left.
    - How: drain ``centered("1")`` and place those columns at ``start_col = 1``.
    """
    columns = _feeder_column_bytes_of(centered("1"))
    host.disp.render_string(centered("1"), start_col=1)
    assert host.logical() == _frame_of(_placed_window(columns, 1))


def test_render_image_multi_color_respects_x(host):
    """A multi-color image puts each pixel's own color at the shifted column.

    - Covers: a multi-color window using the mono color, or ignoring ``start_col``.
    - How: ``"RG"`` with red and green; ``start_col=1`` lights column 1 red and column 2 green.
    """
    green = (0, 255, 0)
    image = host.core.Image("RG", {"R": RED, "G": green})
    host.disp.render_image(image, start_col=1)
    row = host.logical()[0]
    assert row[0] == OFF
    assert row[1] == RED
    assert row[2] == green
    assert row[3] == OFF


@pytest.mark.parametrize(
    "method",
    (
        "render_pattern",
        "render_icon",
        "render_arrow",
        "render_string",
        "render_number",
        "render_image",
        "show_pattern",
        "show_icon",
        "show_arrow",
        "show_string",
        "show_number",
        "show_image",
    ),
)
@pytest.mark.parametrize("bad", (True, 1.5))
def test_x_must_be_an_int_and_does_not_take_over(host, method, bad):
    """A float or a bool ``start_col`` raises ``TypeError`` and leaves the display alone.

    - Covers: accepting ``True`` because ``bool`` is an ``int``, or taking over before the check.
    - How: paint red; call each method with ``start_col=True`` and ``start_col=1.5``; same token; frame still red; no sleep.
    """
    disp = host.disp
    disp.render_filled(RED)
    before = host.logical()
    token = disp._token
    host.sleeps.clear()
    core = host.core
    icon = core.Icon("#")
    image = core.Image("#")

    def call():
        if method == "render_pattern":
            return disp.render_pattern("#", start_col=bad)
        if method == "render_icon":
            return disp.render_icon(icon, start_col=bad)
        if method == "render_arrow":
            return disp.render_arrow(icon, start_col=bad)
        if method == "render_string":
            return disp.render_string("A", start_col=bad)
        if method == "render_number":
            return disp.render_number(7, start_col=bad)
        if method == "render_image":
            return disp.render_image(image, start_col=bad)
        if method == "show_pattern":
            return disp.show_pattern("#", start_col=bad, duration_ms=10)
        if method == "show_icon":
            return disp.show_icon(icon, start_col=bad, duration_ms=10)
        if method == "show_arrow":
            return disp.show_arrow(icon, start_col=bad, duration_ms=10)
        if method == "show_string":
            return disp.show_string("A", start_col=bad, duration_ms=10)
        if method == "show_number":
            return disp.show_number(7, start_col=bad, duration_ms=10)
        if method == "show_image":
            return disp.show_image(image, start_col=bad, duration_ms=10)
        raise AssertionError(method)

    async def run():
        result = call()
        if result is not None:
            await result

    with pytest.raises(TypeError, match=rf"^{method}\(\): 'start_col' must be an integer, got '{bad}'$"):
        asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False
    assert host.logical() == before
    assert host.sleeps == []


@pytest.mark.parametrize("start_col", (-WIDTH - 3, -2, -1, 0, 1, WIDTH - 1, WIDTH, WIDTH + 3))
@pytest.mark.parametrize("noun", ("pattern", "icon", "arrow", "image", "string", "number"))
def test_show_frame_matches_render_at_the_same_x(host, noun, start_col):
    """The first frame of ``show_*`` at a ``start_col`` is the matching ``render_*`` frame, also for negative and cut-off values.

    - Covers: ``show_*`` ignoring ``start_col``, or drawing a different window than ``render_*`` (``show_pattern`` draws without ``render_pattern``).
    - How: render at ``start_col``, remember the frame, then ``show_*`` at the same ``start_col`` with ``duration_ms=0``; first recorded frame matches.
    """
    disp = host.disp
    core = host.core
    icon = core.Icon._from_columns(b"\x01\x02\x04\x08\x10")
    image = core.Image._from_encoded(bytes([0x01, 0x02, 0x04]), 3, False, RED)
    if noun == "pattern":
        disp.render_pattern("#.#", RED, start_col=start_col)
    elif noun == "icon":
        disp.render_icon(icon, RED, start_col=start_col)
    elif noun == "arrow":
        disp.render_arrow(icon, RED, start_col=start_col)
    elif noun == "image":
        disp.render_image(image, start_col=start_col)
    elif noun == "string":
        disp.render_string("A", RED, start_col=start_col)
    else:
        disp.render_number(7, RED, start_col=start_col)
    expected = host.logical()

    async def run():
        with _recorded_shows(host) as frames:
            if noun == "pattern":
                await disp.show_pattern("#.#", RED, start_col=start_col, duration_ms=0)
            elif noun == "icon":
                await disp.show_icon(icon, RED, start_col=start_col, duration_ms=0)
            elif noun == "arrow":
                await disp.show_arrow(icon, RED, start_col=start_col, duration_ms=0)
            elif noun == "image":
                await disp.show_image(image, start_col=start_col, duration_ms=0)
            elif noun == "string":
                await disp.show_string("A", RED, start_col=start_col, duration_ms=0)
            else:
                await disp.show_number(7, RED, start_col=start_col, duration_ms=0)
        return list(frames)

    frames = asyncio.run(run())
    assert frames[0] == expected


_SHOW_WITH_START_COL = ("pattern", "icon", "arrow", "image", "string", "number")


def _start_show_with(disp, core, noun, duration_ms, start_col):
    """Start one ``show_*`` call that takes ``start_col``. Both ``duration_ms`` and ``start_col`` are passed by name."""
    icon = core.Icon("#")
    image = core.Image("#")
    if noun == "pattern":
        return disp.show_pattern("#", start_col=start_col, duration_ms=duration_ms)
    if noun == "icon":
        return disp.show_icon(icon, start_col=start_col, duration_ms=duration_ms)
    if noun == "arrow":
        return disp.show_arrow(icon, start_col=start_col, duration_ms=duration_ms)
    if noun == "image":
        return disp.show_image(image, start_col=start_col, duration_ms=duration_ms)
    if noun == "string":
        return disp.show_string("A", start_col=start_col, duration_ms=duration_ms)
    if noun == "number":
        return disp.show_number(7, start_col=start_col, duration_ms=duration_ms)
    raise AssertionError(noun)


@pytest.mark.parametrize("bad", (True, 1.5, "5"))
@pytest.mark.parametrize("noun", _SHOW_NOUNS)
def test_show_duration_must_be_an_int_and_does_not_take_over(host, noun, bad):
    """A float, bool or str ``duration_ms`` raises ``TypeError`` for every ``show_*`` and leaves the display alone.

    - Covers: accepting ``True`` because ``bool`` is an ``int``, truncating a ``float``, or taking over before the check.
    - How: paint white; call with a bad ``duration_ms``; exact message names the method; same token, not expired; frame still white; no sleep.
    """
    disp = host.disp
    disp.render_filled(WHITE)
    before = host.logical()
    token = disp._token
    host.sleeps.clear()

    async def run():
        await _start_show(disp, host.core, noun, bad)

    with pytest.raises(TypeError, match=rf"^show_{noun}\(\): 'duration_ms' must be an integer, got '{bad}'$"):
        asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False
    assert host.logical() == before
    assert host.sleeps == []


@pytest.mark.parametrize("bad_duration, error", ((-1, ValueError), (True, TypeError), (1.5, TypeError)))
@pytest.mark.parametrize("bad_start_col", (True, 1.5, "1"))
@pytest.mark.parametrize("noun", _SHOW_WITH_START_COL)
def test_show_checks_duration_before_start_col(host, noun, bad_start_col, bad_duration, error):
    """When ``duration_ms`` and ``start_col`` are both invalid, the ``duration_ms`` error is reported, and nothing changes.

    - Covers: the check order changing, an error for the wrong argument, or a draw or takeover before both checks passed.
    - How: paint white; both arguments bad; the error is the ``duration_ms`` one; same token, not expired; frame still white; no sleep.
    """
    disp = host.disp
    disp.render_filled(WHITE)
    before = host.logical()
    token = disp._token
    host.sleeps.clear()

    async def run():
        await _start_show_with(disp, host.core, noun, bad_duration, bad_start_col)

    with pytest.raises(error, match=r"'duration_ms' must be"):
        asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False
    assert host.logical() == before
    assert host.sleeps == []


@pytest.mark.parametrize("noun", _SHOW_NOUNS)
def test_show_expires_the_previous_token(host, noun):
    """Every ``show_*`` takes over the display: the previous token expires and the returned token is a new, current one.

    - Covers: ``show_*`` (``show_pattern`` acquires without ``render_pattern``) leaving the previous animation running.
    - How: remember the token, run ``show_*``; the old token is expired; the returned token is a different, not-expired object and is ``disp._token``.
    """
    disp = host.disp
    old = disp._token

    async def run():
        return await _start_show(disp, host.core, noun, 0)

    new = asyncio.run(run())
    assert old.is_expired is True
    assert new is not old
    assert new is disp._token
    assert new.is_expired is False


def test_duration_start_col_check_and_acquire_returns_a_fresh_token(host):
    """``_ensure_duration_and_start_col_and_acquire`` acquires exactly once, and only when both arguments are valid.

    - Covers: acquiring before a check, acquiring twice, returning a stale token, or accepting ``bool`` for either argument.
    - How: valid call returns ``disp._token`` (new object) and expires the old one; every invalid combination raises and leaves the token alone.
    """
    disp = host.disp
    check = disp._ensure_duration_and_start_col_and_acquire
    old = disp._token
    new = check("m", 0, -3)
    assert new is disp._token and new is not old
    assert old.is_expired is True and new.is_expired is False

    cases = (
        ((-1, 0), ValueError, r"^m\(\): 'duration_ms' must be >= 0, got '-1'$"),
        ((True, 0), TypeError, r"^m\(\): 'duration_ms' must be an integer, got 'True'$"),
        ((1.5, 0), TypeError, r"^m\(\): 'duration_ms' must be an integer, got '1.5'$"),
        ((5, True), TypeError, r"^m\(\): 'start_col' must be an integer, got 'True'$"),
        ((5, 1.5), TypeError, r"^m\(\): 'start_col' must be an integer, got '1.5'$"),
        ((-1, 1.5), ValueError, r"'duration_ms' must be >= 0"),
    )
    for (duration_ms, start_col), error, message in cases:
        with pytest.raises(error, match=message):
            check("m", duration_ms, start_col)
        assert disp._token is new
        assert new.is_expired is False


def test_duration_check_and_acquire_returns_a_fresh_token(host):
    """``_ensure_non_negative_duration_and_acquire`` acquires exactly once, and only when the time is valid.

    - Covers: acquiring before the check, acquiring twice, returning a stale token, or accepting ``bool`` or ``float``.
    - How: a valid call returns ``disp._token`` (new object) and expires the old one; each invalid time raises and leaves that token alone.
    """
    disp = host.disp
    check = disp._ensure_non_negative_duration_and_acquire
    old = disp._token
    new = check("m", "interval_ms", 0)
    assert new is disp._token and new is not old
    assert old.is_expired is True and new.is_expired is False

    cases = (
        (-1, ValueError, r"^m\(\): 'interval_ms' must be >= 0, got '-1'$"),
        (True, TypeError, r"^m\(\): 'interval_ms' must be an integer, got 'True'$"),
        (1.5, TypeError, r"^m\(\): 'interval_ms' must be an integer, got '1.5'$"),
    )
    for duration, error, message in cases:
        with pytest.raises(error, match=message):
            check("m", "interval_ms", duration)
        assert disp._token is new
        assert new.is_expired is False


def test_scroll_text_expired_token_yields_once_and_does_not_draw(host):
    """``_scroll_text`` with an already-expired token yields once and leaves the display alone.

    - Covers: drawing a frame, or returning without a yield, when the caller hands in an expired token.
    - How: paint red; expire that token with another acquire; call ``_scroll_text`` with it. One ``sleep_ms(0)``; no further ``show``;
      frame still red; the same token comes back.
    """
    disp = host.disp
    disp.render_filled(RED)
    before = host.logical()
    shows = disp._pixels.shows
    token = disp._token
    disp._acquire()
    assert token.is_expired is True
    host.sleeps.clear()

    async def run():
        return await disp._scroll_text(token, ScreenText("A")._reader(), RED, 10, False, True)

    returned = asyncio.run(run())
    assert returned is token
    assert host.sleeps == [("ms", 0)]
    assert disp._pixels.shows == shows
    assert host.logical() == before


def _windows(disp, host, draw, xs):
    frames = []
    for start_col in xs:
        draw(start_col)
        frames.append(host.logical())
    return frames


# Widths where the ring index finishes on a different slot: every length through one past the
# display, then one column short of two laps, an exact two laps, one past that, and 27 (27 % WIDTH == 2).
_RING_EDGE_WIDTHS = (*range(WIDTH + 2), 2 * WIDTH - 1, 2 * WIDTH, 2 * WIDTH + 1, 27)


def _screen_text_of_width(n):
    """``n`` distinct nonzero columns, so a window shifted by one column cannot look like its neighbor."""
    text = ScreenText._from_columns(bytes(range(1, n + 1)))
    assert _feeder_column_bytes_of(text) == list(range(1, n + 1))
    return text


def _scroll_start_cols(n, blank_edges):
    """Marquee runs ``WIDTH`` down to ``-n``. Pan runs ``0`` down to ``-max(0, n - WIDTH)``. Both ends included."""
    if blank_edges:
        return range(WIDTH, -n - 1, -1)
    last = 0 if n <= WIDTH else n - WIDTH
    return range(0, -last - 1, -1)


def _scroll_pass_length(n, blank_edges):
    if blank_edges:
        return n + WIDTH + 1
    if n <= WIDTH:
        return 1
    return n - WIDTH + 1


def test_scroll_frames_match_render_windows(host):
    """Marquee and pan frames are the ``render_*`` frames at the ``start_col`` values from the frame law.

    - Covers: an off-by-one last window, a pan that starts blank, or a marquee that starts on the content.
    - How: string, number, and a 10-wide image; one sleep of ``interval_ms`` per frame; empty string too.
    """
    disp = host.disp
    interval = 7

    def check(draw, scroll, n, narrow):
        marquee = list(range(WIDTH, -n - 1, -1))
        span = 0 if narrow else n - WIDTH
        pan = list(range(0, -span - 1, -1))
        expected_m = _windows(disp, host, draw, marquee)
        expected_p = _windows(disp, host, draw, pan)

        async def run_marquee():
            host.sleeps.clear()
            with _recorded_shows(host) as frames:
                await scroll(True)
            return list(frames)

        async def run_pan():
            host.sleeps.clear()
            with _recorded_shows(host) as frames:
                await scroll(False)
            return list(frames)

        frames_m = asyncio.run(run_marquee())
        assert frames_m == expected_m
        assert frames_m[0] == _BLANK
        assert frames_m[-1] == _BLANK
        assert [ms for kind, ms in host.sleeps if kind == "ms"] == [interval] * len(frames_m)
        frames_p = asyncio.run(run_pan())
        assert frames_p == expected_p
        assert frames_p[0] != _BLANK or n == 0
        assert [ms for kind, ms in host.sleeps if kind == "ms"] == [interval] * len(frames_p)
        if narrow:
            assert len(frames_p) == 1

    text = "HI"
    n = _feeder_columns(text)
    assert n > WIDTH
    check(
        lambda start_col: disp.render_string(text, start_col=start_col),
        lambda edges: disp.scroll_string(text, interval_ms=interval, blank_edges=edges),
        n,
        False,
    )
    check(
        lambda start_col: disp.render_number(42, start_col=start_col),
        lambda edges: disp.scroll_number(42, interval_ms=interval, blank_edges=edges),
        _feeder_columns("42"),
        _feeder_columns("42") <= WIDTH,
    )
    wide = bytes([1, 2, 4, 8, 16, 1, 2, 4, 8, 16])
    image = host.core.Image._from_encoded(wide, 10, False, WHITE)
    check(
        lambda start_col: disp.render_image(image, start_col=start_col),
        lambda edges: disp.scroll_image(image, interval_ms=interval, blank_edges=edges),
        10,
        False,
    )
    short = host.core.Image._from_encoded(bytes([1, 2, 4]), 3, False, WHITE)
    check(
        lambda start_col: disp.render_image(short, start_col=start_col),
        lambda edges: disp.scroll_image(short, interval_ms=interval, blank_edges=edges),
        3,
        True,
    )
    check(
        lambda start_col: disp.render_string("", start_col=start_col),
        lambda edges: disp.scroll_string("", interval_ms=interval, blank_edges=edges),
        0,
        True,
    )


@pytest.mark.parametrize("blank_edges", (True, False), ids=("pan", "marquee"))
@pytest.mark.parametrize("n", _RING_EDGE_WIDTHS)
def test_scroll_string_frames_at_ring_edges(host, n, blank_edges):
    """Each frame of ``scroll_string`` is the ``render_string`` window at that step's ``start_col``.

    - Covers: text of 0, 1, …, ``WIDTH + 1`` columns, then ``2*WIDTH - 1``, ``2*WIDTH``, ``2*WIDTH + 1``, and 27 columns.
      Both ``blank_edges`` values. A ring that wraps one slot early, drops the last column, or leaves a stale column fails here.
    - How: a ``ScreenText`` of exactly ``n`` distinct nonzero columns. Marquee ``start_col`` runs from ``WIDTH`` down to ``-n``.
      Pan ``start_col`` runs from 0 down to ``-max(0, n - WIDTH)``. One sleep per frame. The token is still current, and the last frame stays.
    """
    disp = host.disp
    text = _screen_text_of_width(n)
    interval = 1
    expected = _windows(
        disp,
        host,
        lambda start_col: disp.render_string(text, start_col=start_col),
        _scroll_start_cols(n, blank_edges),
    )
    assert len(expected) == _scroll_pass_length(n, blank_edges)

    async def run():
        host.sleeps.clear()
        with _recorded_shows(host) as frames:
            token = await disp.scroll_string(text, interval_ms=interval, blank_edges=blank_edges)
        return token, list(frames)

    token, frames = asyncio.run(run())
    assert frames == expected
    assert host.logical() == frames[-1]
    assert token is disp._token
    assert token.is_expired is False
    assert [ms for kind, ms in host.sleeps if kind == "ms"] == [interval] * len(frames)


@pytest.mark.parametrize("blank_edges", (True, False), ids=("pan", "marquee"))
@pytest.mark.parametrize("n", _RING_EDGE_WIDTHS)
def test_scroll_string_loop_repeats_the_ring_edge_frames(host, n, blank_edges):
    """``loop=True`` plays those frames a second time, then a takeover leaves its own frame up.

    - Covers: a second pass that keeps scrolling, inserts a blank, or repeats the last window.
      The widths that make the refill load-bearing are a pan of exactly ``2*WIDTH`` columns (``read_head`` is 0 again, but the
      ring holds the second lap, not the first) and a marquee whose blank-out starts mid-ring (``n % WIDTH != 0``, including 27).
      A short pan (``n <= WIDTH``) never writes the ring during the shift, so this test checks that the one frame is drawn again,
      with nothing between the two passes.
    - How: stop on the sleep after two full passes, via ``render_filled(RED)``. Pass 2 equals pass 1. No frame sits between them.
      The returned token is expired and the red frame is the last one.
    """
    disp = host.disp
    text = _screen_text_of_width(n)
    expected = _windows(
        disp,
        host,
        lambda start_col: disp.render_string(text, start_col=start_col),
        _scroll_start_cols(n, blank_edges),
    )
    per_pass = len(expected)
    assert per_pass == _scroll_pass_length(n, blank_edges)

    async def run():
        with _recorded_shows(host) as frames:
            def stop():
                if len(frames) >= 2 * per_pass:
                    disp.render_filled(RED)

            host.hook["fn"] = stop
            token = await disp.scroll_string(text, interval_ms=5, loop=True, blank_edges=blank_edges)
        return token, list(frames)

    token, frames = asyncio.run(run())
    host.hook["fn"] = None
    assert frames[:per_pass] == expected
    assert frames[per_pass : 2 * per_pass] == expected
    assert len(frames) == 2 * per_pass + 1
    assert frames[-1] == _red_frame()
    assert token.is_expired is True
    assert host.logical() == _red_frame()


@pytest.mark.parametrize("blank_edges", (True, False))
@pytest.mark.parametrize("kind", ("string", "number", "image"))
@pytest.mark.parametrize("size", (1, 2, 3, WIDTH, WIDTH + 1, 2 * WIDTH + 3))
def test_scroll_ends_on_its_last_frame_which_stays_lit(host, kind, size, blank_edges):
    """After a finished ``scroll_*`` the display shows its last frame, and the returned token is still current.

    - Covers: a scroll that blanks, clears or redraws at the end for some content widths or methods only, or that expires its own token.
    - How: ``size`` is the number of columns of an ``Image``, or the number of characters of a string or number (so the text widths vary around ``WIDTH``);
      ``blank_edges=True`` ends blank; ``blank_edges=False`` ends on the ``render_*`` window at ``start_col = -max(0, n - WIDTH)``, with ``n`` the
      content width in columns; the display is read after the call returned.
    """
    disp = host.disp
    core = host.core
    if kind == "image":
        content = core.Image._from_encoded(bytes([(i % 31) + 1 for i in range(size)]), size, False, WHITE)
        n = size
        draw = lambda start_col: disp.render_image(content, start_col=start_col)
        scroll = lambda: disp.scroll_image(content, interval_ms=1, blank_edges=blank_edges)
    elif kind == "string":
        content = "I" * size
        n = _feeder_columns(content)
        draw = lambda start_col: disp.render_string(content, start_col=start_col)
        scroll = lambda: disp.scroll_string(content, interval_ms=1, blank_edges=blank_edges)
    else:
        content = int("1" * size)
        n = _feeder_columns(str(content))
        draw = lambda start_col: disp.render_number(content, start_col=start_col)
        scroll = lambda: disp.scroll_number(content, interval_ms=1, blank_edges=blank_edges)

    async def run():
        return await scroll()

    token = asyncio.run(run())
    final = host.logical()
    assert token is disp._token
    assert token.is_expired is False
    if blank_edges:
        expected = _BLANK
    else:
        draw(-max(0, n - WIDTH))
        expected = host.logical()
    assert final == expected


def test_scroll_string_loop_repeats_then_stops_on_takeover(host):
    """``loop=True`` plays the marquee twice, then a takeover leaves its own frame up.

    - Covers: the second pass starting mid-text, or a blank written after the takeover.
    - How: ``"A"``; stop on the sleep after two full passes via ``render_filled(RED)``.
    """
    disp = host.disp
    n = _feeder_columns("A")
    per_pass = 1 + n + WIDTH
    expected = _windows(disp, host, lambda start_col: disp.render_string("A", start_col=start_col), range(WIDTH, -n - 1, -1))

    async def run():
        with _recorded_shows(host) as frames:
            def stop():
                if len(frames) >= 2 * per_pass:
                    disp.render_filled(RED)

            host.hook["fn"] = stop
            token = await disp.scroll_string("A", interval_ms=5, loop=True)
        return token, list(frames)

    token, frames = asyncio.run(run())
    host.hook["fn"] = None
    assert frames[:per_pass] == expected
    assert frames[per_pass : 2 * per_pass] == expected
    assert frames[-1] == _red_frame()
    assert token.is_expired is True


def test_scroll_pan_loop_jumps_back_to_the_first_window(host):
    """A looping pan returns to ``start_col = 0`` after the last window.

    - Covers: the second pass continuing past the last column, or inserting a blank between passes.
    - How: ``"HI"`` with ``blank_edges=False``; two passes, then ``render_filled``.
    """
    disp = host.disp
    text = "HI"
    n = _feeder_columns(text)
    assert n > WIDTH
    per_pass = 1 + n - WIDTH
    expected = _windows(disp, host, lambda start_col: disp.render_string(text, start_col=start_col), range(0, -(n - WIDTH) - 1, -1))

    async def run():
        with _recorded_shows(host) as frames:
            def stop():
                if len(frames) >= 2 * per_pass:
                    disp.render_filled(RED)

            host.hook["fn"] = stop
            token = await disp.scroll_string(text, interval_ms=5, loop=True, blank_edges=False)
        return token, list(frames)

    token, frames = asyncio.run(run())
    host.hook["fn"] = None
    assert frames[:per_pass] == expected
    assert frames[per_pass : 2 * per_pass] == expected
    assert token.is_expired is True


def test_set_rotation_does_not_shorten_a_scroll(host):
    """``set_rotation`` during a scroll keeps the marquee's frame count.

    - Covers: rotation taking over the display and cutting the scroll short.
    - How: rotate 180 on the first sleep of ``scroll_string`` and of ``scroll_image``; sleep count stays ``1 + n + WIDTH``.
    """
    disp = host.disp
    text = "HI"
    n = _feeder_columns(text)
    expected = 1 + n + WIDTH
    image = host.core.Image._from_encoded(bytes([1] * n), n, False, WHITE)

    async def once(call):
        turned = {"done": False}

        def hook():
            if not turned["done"]:
                disp.set_rotation(180)
                turned["done"] = True

        host.hook["fn"] = hook
        host.sleeps.clear()
        await call()
        host.hook["fn"] = None
        return sum(1 for kind, _ms in host.sleeps if kind == "ms")

    async def run():
        text_sleeps = await once(lambda: disp.scroll_string(text, interval_ms=10))
        image_sleeps = await once(lambda: disp.scroll_image(image, interval_ms=10))
        return text_sleeps, image_sleeps

    assert asyncio.run(run()) == (expected, expected)


def test_loop_stops_on_takeover_but_repeat_draws_again(host):
    """``loop=True`` returns when an arrow is drawn. ``repeat_until_cancelled`` draws over that arrow.

    - Covers: a looping scroll ignoring takeover, or a repeat stopping because the display changed.
    - How: after two shows, ``render_arrow``. The loop task returns expired. The repeat task then changes the frame and stops on ``cancel``.
    """
    disp = host.disp
    icon = host.core.Icon._from_columns(b"\x1f\x00\x00\x00\x00")

    async def loop_case():
        task = asyncio.create_task(disp.scroll_string("HELLO", interval_ms=10, loop=True))
        while disp._pixels.shows < 2:
            await asyncio.sleep(0)
        disp.render_arrow(icon, RED, start_col=0)
        return await task

    token = asyncio.run(loop_case())
    assert token.is_expired is True
    assert host.logical() == _frame_of(_placed_window([0x1F, 0, 0, 0, 0], 0), RED)

    async def repeat_case():
        async def body():
            await disp.scroll_string("HI", interval_ms=10)

        task = asyncio.create_task(disp.repeat_until_cancelled(body, sleep_between_ms=0))
        while disp._pixels.shows < 2:
            await asyncio.sleep(0)
        disp.render_arrow(icon, RED, start_col=0)
        held = host.logical()
        overwritten = False
        for _ in range(200):
            await asyncio.sleep(0)
            if host.logical() != held:
                overwritten = True
                break
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        return overwritten

    assert asyncio.run(repeat_case()) is True


def test_pause_after_an_expired_token_mints_a_fresh_one(host):
    """A quiet ``pause`` expires the previous token and returns a new one.

    - Covers: ``pause`` handing back the token it found, including one a render already replaced.
    - How: two ``pause(0)`` calls. The first is expired; the second is a different current token.
      Then ``render_filled`` and one more ``pause`` inside ``while token.is_expired``.
    """
    disp = host.disp

    async def run():
        first = await disp.pause(0)
        second = await disp.pause(0)
        assert first.is_expired is True
        assert second is not first
        assert second is disp._token
        disp.render_filled(RED)
        assert second.is_expired is True
        while second.is_expired:
            second = await disp.pause(0)
            break
        return second

    token = asyncio.run(run())
    assert token.is_expired is False
    assert token is disp._token


def test_scroll_negative_interval_does_not_take_over(host):
    """A negative ``interval_ms`` on each ``scroll_*`` raises before the display changes.

    - Covers: clamping a negative interval and scrolling anyway.
    - How: paint red; ``interval_ms=-1`` on string, number and image; same token; frame still red.
    """
    disp = host.disp
    disp.render_filled(RED)
    before = host.logical()
    token = disp._token
    image = host.core.Image("#")

    async def run():
        with pytest.raises(ValueError, match=r"^scroll_string\(\): 'interval_ms' must be >= 0, got '-1'$"):
            await disp.scroll_string("A", interval_ms=-1)
        with pytest.raises(ValueError, match=r"^scroll_number\(\): 'interval_ms' must be >= 0, got '-1'$"):
            await disp.scroll_number(7, interval_ms=-1)
        with pytest.raises(ValueError, match=r"^scroll_image\(\): 'interval_ms' must be >= 0, got '-1'$"):
            await disp.scroll_image(image, interval_ms=-1)

    asyncio.run(run())
    assert disp._token is token
    assert host.logical() == before


def test_scroll_time_and_flags_are_passed_by_name(host):
    """A positional interval or flag on ``scroll_*`` raises ``TypeError`` and does not draw.

    - Covers: ``interval_ms`` or ``blank_edges`` being accepted by position.
    - How: a third positional on the text scrolls, and a second positional on ``scroll_image``.
    """
    disp = host.disp
    disp.render_filled(WHITE)
    before = host.logical()
    token = disp._token
    image = host.core.Image("#")

    async def run():
        with pytest.raises(TypeError):
            await disp.scroll_string("A", WHITE, 150)
        with pytest.raises(TypeError):
            await disp.scroll_number(7, WHITE, False)
        with pytest.raises(TypeError):
            await disp.scroll_image(image, 10)

    asyncio.run(run())
    assert disp._token is token
    assert host.logical() == before


def test_explicit_x_takes_over_a_running_scroll(host):
    """``render_string(..., start_col=1)`` during a scroll expires it and leaves the shifted letter up.

    - Covers: an explicit ``start_col`` failing to take over, or drawing at ``start_col = 0``.
    - How: cancel ``scroll_image(..., loop=True)`` with ``render_string("A", start_col=1)`` after the first show.
    """
    disp = host.disp
    image = host.core.Image("#####")

    async def run():
        task = asyncio.create_task(disp.scroll_image(image, interval_ms=30, loop=True))
        while disp._pixels.shows < 1:
            await asyncio.sleep(0)
        disp.render_string("A", start_col=1)
        return await task

    token = asyncio.run(run())
    assert token.is_expired is True
    assert host.logical() == _frame_of(_placed_window(_feeder_column_bytes("A"), 1))


def test_render_ring_window_at_each_read_head(host):
    """``_render_ring_window`` shows ``ring[read_head:]`` then ``ring[:read_head]``.

    - Covers: a wrap that drops a column or draws the two halves in the wrong order.
    - How: distinct column bytes; ``read_head`` of 0, 1 and ``WIDTH - 1``.
    """
    ring = bytearray([0x01, 0x02, 0x04, 0x08, 0x10])
    assert len(ring) == WIDTH
    for head in (0, 1, WIDTH - 1):
        visible = list(ring[head:]) + list(ring[:head])
        host.disp._render_ring_window(ring, head, WHITE)
        assert host.logical() == _frame_of(visible), head


def test_color_helper_returns_the_rgb_tuple(host):
    """``color(r, g, b)`` returns the plain ``(r, g, b)`` tuple that every draw method accepts.

    - Covers: the helper returning a list, reordering channels, or clamping values.
    - How: three distinct channel values; the result is a tuple equal to the arguments.
    """
    result = host.core.color(1, 2, 3)
    assert type(result) is tuple
    assert result == (1, 2, 3)


def test_image_height_is_the_display_height(host):
    """``Image.height`` is ``HEIGHT`` for any pattern, because patterns are padded or cut to ``HEIGHT`` rows.

    - Covers: a height that follows the number of pattern rows.
    - How: an empty, a one-row and a ``HEIGHT + 2``-row pattern, mono and multi-color.
    """
    core = host.core
    assert core.Image("").height == HEIGHT
    assert core.Image("#").height == HEIGHT
    assert core.Image("#\n" * (HEIGHT + 2)).height == HEIGHT
    assert core.Image("R", {"R": RED}).height == HEIGHT


def test_recolor_does_not_change_a_multicolor_image(host):
    """``recolor`` on a multi-color ``Image`` does nothing.

    - Covers: ``recolor`` overwriting the per-pixel colors of a multi-color image.
    - How: ``Image("R", {"R": RED}).recolor(BLUE)``; the lit pixel is still red after drawing.
    """
    disp = host.disp
    image = host.core.Image("R", {"R": RED})
    image.recolor(_BLUE)
    disp.render_image(image, start_col=0)
    assert disp.get_pixel(0, 0) == RED


def test_icon_with_too_many_rows_raises(host):
    """An ``Icon`` pattern with more than ``HEIGHT`` rows raises ``ValueError``; ``HEIGHT`` rows are accepted.

    - Covers: silently dropping extra rows (that is what ``Image`` does, an ``Icon`` is strict), or an off-by-one at ``HEIGHT``.
    - How: ``HEIGHT`` rows build; ``HEIGHT + 1`` rows raise with the row count in the message.
    """
    core = host.core
    core.Icon("#\n" * HEIGHT)
    with pytest.raises(ValueError, match=rf"Icon requires at most {HEIGHT} rows x {WIDTH} columns; got {HEIGHT + 1} rows$"):
        core.Icon("#\n" * (HEIGHT + 1))


@pytest.mark.parametrize("start_col", (-6, -3, -1, 0, 1, 3, WIDTH, WIDTH + 2))
def test_render_icon_with_more_than_width_columns_is_cut_off(host, start_col):
    """Column data longer than ``WIDTH`` is cut off on the right, and a negative ``start_col`` cuts off its first columns.

    - Covers: the cut-off column arithmetic for data wider than the display (private ``_render_colmajor`` called with such data).
    - How: ``Icon._from_columns`` with ``2 * WIDTH`` distinct columns; the frame equals ``_placed_window`` at each ``start_col``.
    """
    columns = bytes((i % 31) + 1 for i in range(2 * WIDTH))
    icon = host.core.Icon._from_columns(columns)
    host.disp.render_icon(icon, WHITE, start_col=start_col)
    assert host.logical() == _frame_of(_placed_window(columns, start_col))


def test_clear_turns_every_pixel_off_and_takes_over(host):
    """``clear`` blanks the display, shows once, and expires the previous token.

    - Covers: a ``clear`` that keeps the old token (so a running animation redraws over it) or that skips the ``show``.
    - How: fill red, remember token and ``show`` count; ``clear``; all off, new current token, one more ``show``.
    """
    disp = host.disp
    disp.render_filled(RED)
    token = disp._token
    shows = disp._pixels.shows
    disp.clear()
    assert host.logical() == _BLANK
    assert token.is_expired is True
    assert disp._token is not token
    assert disp._token.is_expired is False
    assert disp._pixels.shows == shows + 1


def test_set_pixel_lights_exactly_that_pixel_at_every_position(host):
    """``set_pixel`` on the matrix lights exactly the addressed pixel, shows once, and expires the previous token.

    - Covers: a wrong pixel through the lookup table at some position, a missing ``show``, or the token surviving.
    - How: for every ``(x, y)``: clear, ``set_pixel(x, y, RED)``; only that pixel is red; one new ``show``; previous token expired.
    """
    disp = host.disp
    for y in range(HEIGHT):
        for x in range(WIDTH):
            disp.clear()
            token = disp._token
            shows = disp._pixels.shows
            disp.set_pixel(x, y, RED)
            expected = tuple(tuple(RED if (cx, cy) == (x, y) else OFF for cx in range(WIDTH)) for cy in range(HEIGHT))
            assert host.logical() == expected, (x, y)
            assert disp._pixels.shows == shows + 1
            assert token.is_expired is True


@pytest.mark.parametrize("kind", ("image", "string", "number"))
def test_scroll_loop_as_a_background_task_runs_until_clear(host, kind):
    """The docstring example works: a looping scroll started with ``create_task`` keeps running until ``clear()`` takes over.

    - Covers: the ``loop=True`` caution in the ``scroll_*`` docstrings being wrong, or ``clear()`` not stopping a looping scroll.
    - How: start the looping scroll as a task; let it run a few frames; the task is still running; ``clear()`` ends it with an expired token and a
      blank display.
    """
    disp = host.disp
    image = host.core.Image._from_encoded(bytes([1, 2, 4, 8, 16, 1, 2, 4, 8, 16]), 10, False, WHITE)
    start = {
        "image": lambda: disp.scroll_image(image, interval_ms=5, loop=True),
        "string": lambda: disp.scroll_string("Hello", interval_ms=5, loop=True),
        "number": lambda: disp.scroll_number(12345, interval_ms=5, loop=True),
    }[kind]

    async def run():
        task = asyncio.create_task(start())
        for _ in range(40):
            await asyncio.sleep(0)
        still_running = not task.done()
        disp.clear()
        token = await task
        return still_running, token

    still_running, token = asyncio.run(run())
    assert still_running
    assert token.is_expired is True
    assert host.logical() == _BLANK


@pytest.mark.parametrize("blank_edges", (True, False))
def test_scroll_image_loop_repeats_then_stops_on_takeover(host, blank_edges):
    """``scroll_image(loop=True)`` plays its pass twice with no frame in between, then a takeover leaves its own frame up.

    - Covers: ``loop`` being ignored by ``scroll_image``, a blank or repeated frame between passes, or the call not returning on takeover.
    - How: 10-wide image; two passes are recorded, then ``render_filled(RED)`` from the hook; both ``blank_edges`` values.
    """
    disp = host.disp
    n = 10
    image = host.core.Image._from_encoded(bytes([1, 2, 4, 8, 16, 1, 2, 4, 8, 16]), n, False, WHITE)
    starts = range(WIDTH, -n - 1, -1) if blank_edges else range(0, -(n - WIDTH) - 1, -1)
    per_pass = len(starts)
    expected = _windows(disp, host, lambda start_col: disp.render_image(image, start_col=start_col), starts)

    async def run():
        with _recorded_shows(host) as frames:

            def stop():
                if len(frames) >= 2 * per_pass:
                    disp.render_filled(RED)

            host.hook["fn"] = stop
            token = await disp.scroll_image(image, interval_ms=5, loop=True, blank_edges=blank_edges)
        return token, list(frames)

    token, frames = asyncio.run(run())
    host.hook["fn"] = None
    assert frames[:per_pass] == expected
    assert frames[per_pass : 2 * per_pass] == expected
    assert frames[-1] == _red_frame()
    assert token.is_expired is True


class _BadText:
    """``str()`` raises ``RuntimeError``. A text or number argument then fails while it is being read."""

    def __str__(self):
        raise RuntimeError("bad text")


def _assert_rejected_before_takeover(host, call, error, message):
    """``call`` raises ``error`` and leaves the token, the frame, and the sleep log alone."""
    disp = host.disp
    disp.render_filled(RED)
    before = host.logical()
    token = disp._token
    host.sleeps.clear()

    async def run():
        result = call(disp)
        if result is not None:
            await result

    with pytest.raises(error, match=message):
        asyncio.run(run())
    assert disp._token is token
    assert token.is_expired is False
    assert host.logical() == before
    assert host.sleeps == []


@pytest.mark.parametrize(
    "call, error, message",
    [
        pytest.param(lambda d: d.render_icon(object(), start_col=0), AttributeError, "_columns", id="render_icon"),
        pytest.param(lambda d: d.render_arrow(object(), start_col=0), AttributeError, "_columns", id="render_arrow"),
        pytest.param(
            lambda d: d.show_icon(object(), start_col=0, duration_ms=10), AttributeError, "_columns", id="show_icon"
        ),
        pytest.param(
            lambda d: d.show_arrow(object(), start_col=0, duration_ms=10), AttributeError, "_columns", id="show_arrow"
        ),
        pytest.param(lambda d: d.render_string(_BadText(), start_col=0), RuntimeError, "bad text", id="render_string"),
        pytest.param(
            lambda d: d.show_string(_BadText(), start_col=0, duration_ms=10), RuntimeError, "bad text", id="show_string"
        ),
        pytest.param(lambda d: d.scroll_string(_BadText(), interval_ms=10), RuntimeError, "bad text", id="scroll_string"),
        pytest.param(lambda d: d.render_number(_BadText(), start_col=0), RuntimeError, "bad text", id="render_number"),
        pytest.param(
            lambda d: d.show_number(_BadText(), start_col=0, duration_ms=10), RuntimeError, "bad text", id="show_number"
        ),
        pytest.param(lambda d: d.scroll_number(_BadText(), interval_ms=10), RuntimeError, "bad text", id="scroll_number"),
        pytest.param(lambda d: d.scroll_image(object(), interval_ms=10), AttributeError, "_width", id="scroll_image"),
    ],
)
def test_wrong_object_does_not_take_over(host, call, error, message):
    """A bad object argument raises before the display is taken over.

    - Covers: reading the object after ``_acquire`` (the previous animation would already be cancelled) for icon, arrow,
      string, number, and ``scroll_image``.
    - How: paint red; pass ``object()`` where the code reads ``_columns`` or ``_width``, or an object whose ``__str__`` raises.
      Valid ``start_col``, ``duration_ms`` and ``interval_ms``. Same token, not expired; frame still red; no sleep.
    """
    _assert_rejected_before_takeover(host, call, error, message)


@pytest.mark.parametrize(
    "call, error, message",
    [
        pytest.param(lambda d: d.render_icon(object(), start_col=1.5), AttributeError, "_columns", id="render_icon"),
        pytest.param(lambda d: d.render_arrow(object(), start_col=1.5), AttributeError, "_columns", id="render_arrow"),
        pytest.param(
            lambda d: d.show_icon(object(), start_col=0, duration_ms=-1), AttributeError, "_columns", id="show_icon_duration"
        ),
        pytest.param(
            lambda d: d.show_arrow(object(), start_col=0, duration_ms=-1),
            AttributeError,
            "_columns",
            id="show_arrow_duration",
        ),
        pytest.param(
            lambda d: d.show_icon(object(), start_col=1.5, duration_ms=10),
            AttributeError,
            "_columns",
            id="show_icon_start_col",
        ),
        pytest.param(
            lambda d: d.show_arrow(object(), start_col=1.5, duration_ms=10),
            AttributeError,
            "_columns",
            id="show_arrow_start_col",
        ),
        pytest.param(lambda d: d.render_string(_BadText(), start_col=1.5), RuntimeError, "bad text", id="render_string"),
        pytest.param(
            lambda d: d.show_string(_BadText(), start_col=0, duration_ms=1.5),
            RuntimeError,
            "bad text",
            id="show_string_duration",
        ),
        pytest.param(
            lambda d: d.show_string(_BadText(), start_col=True, duration_ms=10),
            RuntimeError,
            "bad text",
            id="show_string_start_col",
        ),
        pytest.param(lambda d: d.scroll_string(_BadText(), interval_ms=-1), RuntimeError, "bad text", id="scroll_string"),
        pytest.param(lambda d: d.scroll_number(_BadText(), interval_ms=-1), RuntimeError, "bad text", id="scroll_number"),
        pytest.param(lambda d: d.render_number(_BadText(), start_col=1.5), RuntimeError, "bad text", id="render_number"),
        pytest.param(
            lambda d: d.show_number(_BadText(), start_col=0, duration_ms=-1),
            RuntimeError,
            "bad text",
            id="show_number_duration",
        ),
        pytest.param(
            lambda d: d.show_number(_BadText(), start_col=True, duration_ms=10),
            RuntimeError,
            "bad text",
            id="show_number_start_col",
        ),
    ],
)
def test_wrong_object_is_reported_before_a_bad_number(host, call, error, message):
    """When the object and a number are both invalid, the object error is the one that is raised.

    - Covers: checking ``duration_ms``, ``start_col`` or ``interval_ms`` before the object is read.
    - How: the same bad objects as ``test_wrong_object_does_not_take_over``, plus one bad number. The numeric error is not raised.
      The token stays, the frame stays red, and nothing sleeps.
    """
    _assert_rejected_before_takeover(host, call, error, message)


def test_show_string_of_screen_text_matches_the_string(host):
    """``show_string(ScreenText)`` holds the same picture as ``show_string`` of that plain string.

    - Covers: the hold path turning a ``ScreenText`` into its default ``str`` (which is not the text).
    - How: ``ScreenText("A")`` and ``"A"``, ``duration_ms=0``. Both first frames equal ``render_string("A")``.
      Draining the ``ScreenText`` afterwards yields the same columns.
    """
    disp = host.disp
    prepared = ScreenText("A")
    columns = _feeder_column_bytes_of(prepared)
    disp.render_string("A", start_col=0)
    expected = host.logical()

    async def run(text):
        with _recorded_shows(host) as frames:
            await disp.show_string(text, duration_ms=0, start_col=0)
        return list(frames)

    assert asyncio.run(run("A"))[0] == expected
    assert asyncio.run(run(prepared))[0] == expected
    assert _feeder_column_bytes_of(prepared) == columns


@pytest.mark.parametrize("blank_edges", (True, False))
def test_scroll_string_keeps_an_interior_zero_column(host, blank_edges):
    """A 0 column inside the text is blank ink. It is not the end of the reader.

    - Covers: stopping the scroll when a column byte is 0, as if ``next_column`` had returned ``None``.
    - How: a ``ScreenText`` whose columns are ``1, 0, 2``. Frames equal ``render_string`` at the frame-law ``start_col`` values.
      Both ``blank_edges``.
    """
    disp = host.disp
    text = ScreenText._from_columns(bytes([1, 0, 2]))
    n = 3
    expected = _windows(
        disp,
        host,
        lambda start_col: disp.render_string(text, start_col=start_col),
        _scroll_start_cols(n, blank_edges),
    )
    assert len(expected) == _scroll_pass_length(n, blank_edges)

    async def run():
        with _recorded_shows(host) as frames:
            await disp.scroll_string(text, interval_ms=1, blank_edges=blank_edges)
        return list(frames)

    assert asyncio.run(run()) == expected


def test_number_methods_draw_str_of_negative_and_float(host):
    """``render_number``, ``show_number`` and ``scroll_number`` draw ``str(n)`` for a negative and a float.

    - Covers: a format other than ``str(n)``, or dropping the sign or the decimal point.
    - How: ``-3`` and ``1.5``. ``render_number`` matches ``render_string(str(n))``. The first ``show_number`` frame matches that.
      ``scroll_number`` frames match the ``render_number`` windows, for both ``blank_edges``.
    """
    disp = host.disp
    for n in (-3, 1.5):
        disp.render_string(str(n), start_col=0)
        as_text = host.logical()
        disp.render_number(n, start_col=0)
        assert host.logical() == as_text, n

        async def show(number=n):
            with _recorded_shows(host) as frames:
                await disp.show_number(number, duration_ms=0, start_col=0)
            return list(frames)

        assert asyncio.run(show())[0] == as_text, n

        n_cols = _feeder_columns(str(n))
        for blank_edges in (True, False):

            def draw(start_col, number=n):
                disp.render_number(number, start_col=start_col)

            expected = _windows(disp, host, draw, _scroll_start_cols(n_cols, blank_edges))

            async def scroll(number=n, edges=blank_edges):
                with _recorded_shows(host) as frames:
                    await disp.scroll_number(number, interval_ms=1, blank_edges=edges)
                return list(frames)

            assert asyncio.run(scroll()) == expected, (n, blank_edges)

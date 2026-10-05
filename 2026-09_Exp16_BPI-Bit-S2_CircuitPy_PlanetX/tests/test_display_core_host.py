"""Host execution of ``display.core`` behind stubs. No board, no NeoPixel hardware.

``test_no_board_core.py`` still requires that a normal import of ``display``
does not load ``core``. This module installs ``board`` / ``neopixel`` /
``adafruit_ticks`` / ``rainbowio`` only inside a fixture and removes them
before the test returns.

Out of scope here (needs the board or a design change): the real pin lock on
a second ``Display()`` and keypad scan timing.
"""

import asyncio
import sys
import types

import pytest

from display._constants import HEIGHT, OFF, RED, WHITE, WIDTH
from display.text_layout import SpacedGlyphColumnFeeder

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
    feeder = SpacedGlyphColumnFeeder(str(text))
    count = 0
    while feeder.next_column() is not None:
        count += 1
    return count


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
    - How: ``show_image`` in white, ``recolor(RED)``; ``show`` count unchanged and pixel still white; a second show is red.
    """
    disp = host.disp
    image = host.core.Image(bytes([0x1F]), 1, False, WHITE)

    async def run():
        await disp.show_image(image, interval_ms=0)
        shows = disp._pixels.shows
        image.recolor(RED)
        assert disp._pixels.shows == shows
        assert disp.get_pixel(0, 0) == WHITE
        await disp.show_image(image, interval_ms=0)
        assert disp.get_pixel(0, 0) == RED

    asyncio.run(run())


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
    disp.fill(RED)
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
    disp.fill(WHITE)
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
    disp.fill(RED)

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
    image = host.core.Image(bytes([1] * 10), 10, False, WHITE)
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
    - How: ``fill`` inside the first ``asyncio.sleep_ms``; recorded offsets are ``[0]``; token expired.
    """
    disp = host.disp
    image = host.core.Image(bytes([1] * 10), 10, False, WHITE)
    offsets = []
    orig = host.core.Image._render_window

    def capture(self, disp_, offset):
        offsets.append(offset)
        return orig(self, disp_, offset)

    def cancel():
        disp.fill(OFF)

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


def test_show_image_negative_interval_cancels_and_does_not_wait(host):
    """A negative ``show_image`` interval is clamped to 0 and still acquires.

    - Covers: raising like ``pause``, or sleeping the negative duration.
    - How: remember the token; ``interval_ms=-5``; old token expired; no positive sleep recorded.
    """
    disp = host.disp
    image = host.core.Image(bytes([0x1F, 0x00]), 2, False, WHITE)
    token = disp._token

    async def run():
        host.sleeps.clear()
        await disp.show_image(image, offset=-2, interval_ms=-5)

    asyncio.run(run())
    assert token.is_expired is True
    assert disp.get_pixel(2, 0) == WHITE
    assert disp.get_pixel(0, 0) == OFF
    assert not any(kind == "s" and seconds > 0 for kind, seconds in host.sleeps)
    assert ("ms", 0) in host.sleeps


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


def test_short_icon_does_not_latch_a_partial_write(host):
    """A short ``Icon`` raises inside the column loop, before ``show``.

    - Covers: latching a half-written buffer, or ignoring the length mismatch.
    - How: ``Icon`` of one byte; ``IndexError``; ``show`` count unchanged; RAM buffer differs from the latch.
    """
    disp = host.disp
    disp.fill(OFF)
    pixels = disp._pixels
    shows = pixels.shows
    with pytest.raises(IndexError):
        disp.render_icon(host.core.Icon(b"\xff"), WHITE)
    assert pixels.shows == shows
    assert pixels.buf != pixels.latched


def test_render_pattern_clips_a_wide_row_image_create_keeps_it(host):
    """``render_pattern`` drops columns past ``WIDTH``. ``Image.create`` keeps them as width.

    - Covers: both entry points silently using the same width rule.
    - How: six hashes; the rendered row is five on-pixels; the image reports width 6.
    """
    disp = host.disp
    disp.render_pattern("######\n#")
    assert host.logical()[0] == tuple(WHITE for _ in range(WIDTH))
    assert host.logical()[1][0] == WHITE
    assert host.logical()[1][1] == OFF
    image = host.core.Image.create("######\n#")
    assert image.width == 6


def test_deinit_then_fill_raises(host):
    """``fill`` after ``deinit`` raises. The call also expires that instance's token.

    - Covers: a deinited display still accepting draws.
    - How: a second ``Display()`` (the stub does not lock the pin); ``deinit``; ``fill`` raises ``RuntimeError``.
    """
    fresh = host.core.Display()
    token = fresh._token
    fresh.deinit()
    assert token.is_expired is True
    with pytest.raises(RuntimeError):
        fresh.fill(RED)


def test_forever_runs_inside_a_running_coroutine(host):
    """``await Display.forever(...)`` works from a coroutine, and cancelling ends it.

    - Covers: ``forever`` calling ``asyncio.run`` (``RuntimeError`` inside a running loop), or ignoring cancel.
    - How: run it as a task inside ``asyncio.run``; wait for three calls; cancel; the task ends cancelled.
    """
    calls = []

    async def run():
        task = asyncio.create_task(host.core.Display.forever(lambda: calls.append(1)))
        while len(calls) < 3:
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert len(calls) >= 3


def test_forever_awaits_async_callbacks_and_rests_between_rounds(host):
    """An ``async def`` callback is awaited, and each round ends with a ``sleep_ms(rest)``.

    - Covers: a coroutine callback never being awaited, or the rest not using whole milliseconds.
    - How: callback is ``async``; after two rounds the recorded ``("ms", 25)`` sleeps are counted; ``sleep_between_ms=25.9`` becomes 25.
    """
    done = []

    async def callback():
        done.append(1)

    async def run():
        task = asyncio.create_task(host.core.Display.forever(callback, sleep_between_ms=25.9))
        while len(done) < 2:
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert len(done) >= 2
    assert ("ms", 25) in host.sleeps
    assert all(ms == 25 for kind, ms in host.sleeps if kind == "ms")


def test_forever_default_rest_is_10_ms_and_zero_still_yields(host):
    """Default rest is 10 ms. With ``0`` a sibling task still gets a turn each round.

    - Covers: a wrong default, or ``sleep_between_ms=0`` skipping the yield.
    - How: default run records ``("ms", 10)``; a ``0`` run lets a sibling task set a flag.
    """
    ticks = []

    async def run_default():
        task = asyncio.create_task(host.core.Display.forever(lambda: ticks.append(1)))
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
        task = asyncio.create_task(host.core.Display.forever(lambda: None, sleep_between_ms=0))
        asyncio.create_task(sibling())
        for _ in range(5):
            await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run_zero())
    assert flag["ran"] is True


def test_forever_negative_rest_and_callback_error(host):
    """A negative rest raises ``ValueError``. An exception in the callback ends ``forever``.

    - Covers: a negative rest being accepted, or a callback error being swallowed.
    - How: await ``forever(cb, -1)``; then a callback that raises ``KeyError`` propagates.
    """

    async def run():
        with pytest.raises(ValueError):
            await host.core.Display.forever(lambda: None, sleep_between_ms=-1)

        def boom():
            raise KeyError("x")

        with pytest.raises(KeyError):
            await host.core.Display.forever(boom)

    asyncio.run(run())

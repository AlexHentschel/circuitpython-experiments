"""Round-1 LED-matrix on-device test, Stage 2 (Tier 2 async, display only).

``asyncio`` drives the Tier-2 display calls. This script does not use the
button modules. Stage 3 runs the button-coroutines beside a display animation.

Stage 0 and Stage 1 tested the sycnrhonous calls. This stage assumes those work.

Maintainer checklist of 26 checks. Most are display checks. Each check prints ``n/26``.
``[OK|MISMATCH]`` is printed where the timing, the token, or the exception can be checked
on the board. Visual-only checks say what to watch. Edit ``_PARTS`` to re-run one part (``"A"``, ``"B"``, ``"C"``,
or ``"ABC"``).

Part A, show/scroll contract (1-17):

  1. ``asyncio.sleep(0.5)``. ``[OK]`` within +/-10 ms.
  2. ``show_pattern(..., duration_ms=1500)``. Picture, then blank.
     Elapsed close to 1.5 s. Last frame blank (verified using ``get_pixel`` scan).
  3. ``show_icon(Emojis.DUCK, duration_ms=1500)``. Same checks.
  4. ``show_arrow(Arrows.SOUTH, duration_ms=1500)``. Same checks.
  5. ``show_string("K", duration_ms=1500)``. Left-aligned, then blank.
  6. ``scroll_string("STAGE2")``. Marquee: in from the right, out the left.
     Elapsed is ``(1 + columns + WIDTH) * interval_ms`` plus 2–3 ms per frame for drawing, ±10 ms tolerance for time jitters.
     ``columns`` is ``ScreenText("STAGE2").width``.
  7. ``scroll_number(42)``. Same marquee check.
  8. ``show_number(7, duration_ms=1500)``. Hold, then blank.
  9. ``show_image(img, start_col=k, duration_ms=900)`` for ``k`` in
     ``0, -3, -5, 2, -8``. A window, then blank, each time.
  10. ``scroll_image(img)`` marquee. Blank, in, out, blank.
      Elapsed is ``(1 + width + WIDTH) * interval_ms`` plus 2–3 ms per frame for drawing, ±10 ms tolerance for time jitters.
  11. ``scroll_image(img, blank_edges=False)``. Starts on content, ends on
      the last window, and that window stays lit.
      Elapsed is ``(1 + max(0, img.width - WIDTH)) * interval_ms`` plus 2–3 ms per frame for drawing, ±10 ms tolerance for time jitters.
  12. Slow ``scroll_image`` gathered with ``render_filled`` at 1 s.
      The scroll notices the fill only when the current frame wait ends, so
      elapsed is from 1.0 s until 1.0 s + 400 ms, ±10 ms. The fill stays,
      token ``is_expired``.
  13. ``scroll_string("ROTATE")`` gathered with ``set_rotation(270)``.
      The axis turns vertical. Pass when elapsed is the frame waits
      ``(1 + w + WIDTH) * 200`` ms plus 2–3 ms per frame for drawing, ±10 ms tolerance for time jitters.
      ``w`` is ``ScreenText("ROTATE").width``.
  14. ``scroll_image`` gathered with ``set_rotation(180)``. Mirrored in
      place. Pass when elapsed is the frame waits
      ``(1 + img.width + WIDTH) * 200`` ms plus 2–3 ms per frame for drawing, ±10 ms tolerance for time jitters.
  15. ``show_string("K", duration_ms=2000)`` cut by ``render_filled`` at
      0.5 s. The hold notices the fill on its next 47 ms poll, so elapsed
      is from 0.5 s until 0.5 s + 47 ms, ±10 ms. The fill stays. Token
      ``is_expired``.
  16. ``scroll_string("HI", loop=True)`` cut by ``render_filled`` at 2.5 s.
      The scroll notices the fill only when the current frame wait ends, so
      elapsed is from 2.5 s until 2.5 s + 200 ms, ±10 ms. ``loop=True`` does
      not change that. The fill stays. Token ``is_expired``.
  17. ``repeat_until_cancelled`` blinks a heart (``show_icon`` for 250 ms,
      then ``clear``). Cancel leaves the last picture up.

Part B, placement (18-22) and a timing check (23):

  18. Hand-built marquee: ``render_image`` at ``start_col`` from ``WIDTH``
      down through ``-width``, ``hold(150)`` between frames.
      Frame count ``== 1 + width + WIDTH``.
  19. Hand-built pan that jumps two columns:
      ``start_col`` in ``range(0, -(width - WIDTH) - 1, -2)``,
      ``hold(200)`` between frames. Watch the jump.
  20. ``render_icon(HEART, start_col=k)`` for ``k`` from ``WIDTH`` down to
      ``0``, ``hold(100)`` between frames. Watch the heart slide in.
  21. ``render_string("HELLO", start_col=k)`` across the display, then
      ``render_string(centered("1"))`` beside ``render_string("1")``.
      ``hold`` keeps each still picture visible.
  22. ``show_filled(RED, duration_ms=500)``. Red, then blank.
  23. 100 ``render_string("HELLO")`` and 100 ``render_string`` of a
      prepared ``ScreenText``. Prints elapsed ms and how many bytes the heap grew.
      A reading of ``-1`` prints ``unknown`` for that pair, because the amount is not known.

Part C, takeover and argument errors (24-26):

  24. ``scroll_string("IDLE", loop=True)`` gathered with ``render_arrow``
      after 2.5 s. The scroll stops, the arrow stays, token ``is_expired``.
  25. ``repeat_until_cancelled(lambda: scroll_string("IDLE"))`` with the
      same arrow after 2.5 s. The arrow is overwritten and the scroll
      resumes. The task is still running, then ``task.cancel()`` stops it.
  26. Argument errors while ``scroll_string("BLUE", BLUE, loop=True)`` keeps moving.
      The scroll is a word, not a heart. Each call raises before it takes the display:
      ``show_icon(HEART)`` (missing ``duration_ms``);
      ``show_icon(HEART, duration_ms=-1)``;
      ``show_icon(HEART, RED, 0, 1000)`` (positional time);
      ``scroll_string("A", interval_ms=-1)``;
      ``render_icon(HEART, start_col=1.5)``.
      ``[OK]`` when the exception type matches and the blue scroll is still running.
      After the five calls, the scroll is held another 1 s. ``task.cancel()`` is the only thing that stops it.
      The message text is printed so the board's wording can be copied down.

``show_*`` takes ``duration_ms``. ``scroll_*`` takes ``interval_ms``.
Placement is ``start_col``. ``hold`` keeps the current frame.
There is no ``step`` argument.

Each cycle starts at rotation 0 and brightness 0.10. The sequence repeats
so the script does not fall through to the REPL.
"""

import asyncio
import gc
import time

import display
from display import Arrows, Emojis, ScreenText, centered

d = display.display

# Edit to "A", "B", or "C" to re-run one part.
_PARTS = "ABC"
# _PARTS = "A"

# Timing test: Pass when elapsed = expected + ε, with -10 ms ≤ ε ≤ +10 ms.
# For a display operation that holds a single frame, the expected duration is the holding period.
# A scroll's expected time is the sum of its frame waits, plus 2–3 ms of drawing per frame.
# Nothing else is scheduled to run on the board while the tests, so we expect tight timing in practice.
_TOLERANCE = 0.010  # allowed timing deviation in seconds
_HOLD_TOLERANCE_S = _TOLERANCE
_SLEEP_TOLERANCE_S = _TOLERANCE
# show() of this 5×5 is about 2 ms. One stage-2 run on this board was about 2.2–2.5 ms per frame on BPI-Bit-S2.
_FRAME_DRAW_MIN_S = 0.002
_FRAME_DRAW_MAX_S = 0.003

print("Stage 2: import asyncio OK")

# 10 columns x 5 rows. Left half is a diamond, right half is a solid block,
# so the show_image windows and the scroll are visually distinct.
_BIG_PATTERN = """
. . # . . # # # # #
. # # # . # # # # #
# # # # # # # # # #
. # # # . # # # # #
. . # . . # # # # #
"""
_big_image = display.Image(_BIG_PATTERN, display.CYAN)


def _scroll_frames(columns: int, blank_edges: bool) -> int:
    """Frames required for one scroll pass.
    Marquee (``blank_edges=True``): ``start_col`` runs from ``WIDTH`` through
    ``-columns``. ``WIDTH`` is the opening blank, the first column sitting just
    past the right edge. ``-columns`` is the closing blank, the last column
    just past the left edge. That is ``1 + columns + WIDTH`` frames.
    Pan (``blank_edges=False``): ``start_col`` runs from ``0`` through
    ``-(columns - WIDTH)`` when the content is wider than the display.
    ``0`` already puts the first column on the left LED. The last value puts
    the last column on the right LED, and that frame stays lit. A content of
    ``WIDTH`` columns or fewer does not move: the range is ``{0}``, i.e. one frame.
    So in summary, the result is ``1 + max(0, columns - WIDTH)`` frames.
    """
    if blank_edges:
        return 1 + columns + display.WIDTH
    extra = columns - display.WIDTH
    if extra < 0:
        extra = 0
    return 1 + extra


def _expected_scroll_duration(columns: int, interval_ms: int, blank_edges: bool) -> tuple[float, float]:
    """Estimated earliest and latest duration [in seconds] for one full scroll pass.
    This function estimates the expected duration lower and upper bounds by accounting for the awaited sleeps after each frame
    and in addition by an empirical duration for drawing the frames.
    ``columns`` is the width of the content we are scrolling (e.g. ``ScreenText(text).width`` or ``image.width``).

    Specifics: The sum of the pure sleeps is ``frames * interval_ms / 1000`` [seconds]. In addition, each frame
    also requires time for drawing: between ``_FRAME_DRAW_MIN_S`` and ``_FRAME_DRAW_MAX_S`` [seconds].
    ``_TOLERANCE`` is an additional jitter that we allow, subtracted on the early side and added on the late side.
    """
    frames = _scroll_frames(columns, blank_edges)
    sleeps_s = frames * interval_ms / 1000  # each frame stays up for `interval_ms` milliseconds
    low = sleeps_s + frames * _FRAME_DRAW_MIN_S - _TOLERANCE
    high = sleeps_s + frames * _FRAME_DRAW_MAX_S + _TOLERANCE
    return low, high


def _is_blank() -> bool:
    """True when every LED in the buffer is off."""
    off = display.OFF
    for x in range(display.WIDTH):
        for y in range(display.HEIGHT):
            if d.get_pixel(x, y) != off:
                return False
    return True


def _frame() -> tuple:
    """One color per LED, row by row, for a before/after compare."""
    cells = []
    for y in range(display.HEIGHT):
        for x in range(display.WIDTH):
            cells.append(d.get_pixel(x, y))
    return tuple(cells)


def _close(elapsed_s: float, expected_s: float, tolerance_s: float) -> str:
    """``OK`` when ``elapsed_s`` is ``expected_s + ε`` with ``|ε| ≤ tolerance_s``. Otherwise ``MISMATCH``."""
    if abs(elapsed_s - expected_s) <= tolerance_s:
        return "OK"
    return "MISMATCH"


async def _trigger_filled_after(delay_s: float, color) -> None:
    """Wait for ``delay_s`` [seconds], then ``render_filled``. That expires the running token."""
    await asyncio.sleep(delay_s)
    d.render_filled(color)


async def _trigger_rotation_after(delay_s: float, degrees: int) -> None:
    """Wait for ``delay_s`` [seconds], then rotate. ``set_rotation`` does not expire the running token."""
    await asyncio.sleep(delay_s)
    d.set_rotation(degrees)


async def _trigger_arrow_after(delay_s: float) -> None:
    """Wait for ``delay_s`` [seconds], then draw an arrow. ``render_arrow`` expires the running token."""
    await asyncio.sleep(delay_s)
    d.render_arrow(Arrows.NORTH, display.ORANGE)


async def _blink_heart() -> None:
    """One blink. ``show_icon`` holds the heart for 250 ms, then wipes, unless the hold was taken over."""
    await d.show_icon(Emojis.HEART, display.RED, duration_ms=250)


async def _show_then_blank(label: str, call, expected_s: float) -> None:
    """Await one ``show_*``, then check the elapsed time and that the display is left blank."""
    _t0 = time.monotonic()
    await call
    _elapsed = time.monotonic() - _t0
    _time = _close(_elapsed, expected_s, _HOLD_TOLERANCE_S)
    _blank = "OK" if _is_blank() else "MISMATCH"
    print(f"{label} elapsed={_elapsed:.2f}s expected={expected_s:.2f}s [{_time}] last frame blank [{_blank}]")


async def _scroll_elapsed(label: str, call, columns: int, interval_ms: int, blank_edges: bool) -> None:
    """Await one scroll pass and compare elapsed time with ``_expected_scroll_duration`` (the frame waits, plus an empirical approximation per frame, plus some tolerance for jitters)."""
    _low, _high = _expected_scroll_duration(columns, interval_ms, blank_edges)
    _t0 = time.monotonic()
    await call
    _elapsed = time.monotonic() - _t0
    _time = "OK" if _low <= _elapsed <= _high else "MISMATCH"
    print(f"{label} elapsed={_elapsed:.2f}s window=[{_low:.2f}, {_high:.2f}]s (columns={columns}, interval_ms={interval_ms}, blank_edges={blank_edges}) [{_time}]")


async def _check_error(label: str, exc_type: type, invoke, scroll_task) -> None:
    """Call ``invoke`` while ``scroll_task`` is scrolling. ``[OK]`` when the exception type matches and the scroll is still running.

    The calls under test raise before they take the display, so the scroll keeps moving. A short pause after the call makes that visible.
    """
    try:
        _result = invoke()
        if hasattr(_result, "__await__"):
            await _result
    except exc_type as exc:
        _alive = "OK" if not scroll_task.done() else "MISMATCH"
        print(f"26/26: {label} -> {type(exc).__name__}: {exc} [{_alive}] (scroll still running)")
        await asyncio.sleep(0.4)
        return
    except Exception as exc:
        print(f"26/26: {label} -> {type(exc).__name__}: {exc} [MISMATCH] (expected {exc_type.__name__})")
        return
    print(f"26/26: {label} -> no exception [MISMATCH]")


def _heap_grew(before: int, after: int) -> str:
    """How much the heap grew, as ``"<n> bytes"``. ``"unknown"`` when either ``gc.mem_free()`` reading is ``-1``."""
    if before == -1 or after == -1:
        return "unknown"
    return f"{before - after} bytes"


# -------------------------------------------- Part A of tests -------------------------------------------- #


async def _part_a() -> None:
    print("\n--- A: show/scroll contract (1-17) ---")

    # One sleep, and no other task. This is a sanity check of the scheduler's own accuracy, before we do any display operations.
    _sleep_target_s = 0.5
    _t0 = time.monotonic()
    await asyncio.sleep(_sleep_target_s)
    _elapsed = time.monotonic() - _t0
    _deviation = abs(_elapsed - _sleep_target_s)
    _status = "OK" if _deviation <= _SLEEP_TOLERANCE_S else "MISMATCH"
    print(f"1/26: asyncio.sleep({_sleep_target_s}) returned after {_elapsed:.4f}s (deviation={_deviation * 1000:.1f}ms) [{_status}]")

    _checker = """
            . # . # .
            # . # . #
            . # . # .
            # . # . #
            . # . # .
            """
    await _show_then_blank(
        "2/26: show_pattern checkerboard, then blank",
        d.show_pattern(_checker, display.GREEN, duration_ms=1500),
        1.5,
    )
    await _show_then_blank(
        "3/26: show_icon(DUCK), then blank",
        d.show_icon(Emojis.DUCK, display.YELLOW, duration_ms=1500),
        1.5,
    )
    await _show_then_blank(
        "4/26: show_arrow(SOUTH), then blank",
        d.show_arrow(Arrows.SOUTH, display.CYAN, duration_ms=1500),
        1.5,
    )
    await _show_then_blank(
        "5/26: show_string('K') left-aligned, then blank",
        d.show_string("K", display.MAGENTA, duration_ms=1500),
        1.5,
    )

    _stage2_columns = ScreenText("STAGE2").width
    await _scroll_elapsed(
        "6/26: scroll_string('STAGE2') marquee, then blank",
        d.scroll_string("STAGE2", display.WHITE, interval_ms=150),
        _stage2_columns,
        150,
        True,
    )
    _forty_two_columns = ScreenText("42").width
    await _scroll_elapsed(
        "7/26: scroll_number(42) marquee, then blank",
        d.scroll_number(42, display.GOLD, interval_ms=150),
        _forty_two_columns,
        150,
        True,
    )
    await _show_then_blank(
        "8/26: show_number(7), then blank",
        d.show_number(7, display.GOLD, duration_ms=1500),
        1.5,
    )

    _big_image.recolor(display.CYAN)
    for _start_col in (0, -3, -5, 2, -8):
        await _show_then_blank(
            f"9/26: show_image(start_col={_start_col}), then blank",
            d.show_image(_big_image, start_col=_start_col, duration_ms=900),
            0.9,
        )

    _big_image.recolor(display.PURPLE)
    await _scroll_elapsed(
        "10/26: scroll_image marquee (blank, in, out, blank)",
        d.scroll_image(_big_image, interval_ms=250),
        _big_image.width,
        250,
        True,
    )

    _big_image.recolor(display.CYAN)
    _t0 = time.monotonic()
    await d.scroll_image(_big_image, interval_ms=150, blank_edges=False)
    _elapsed = time.monotonic() - _t0
    _low, _high = _expected_scroll_duration(_big_image.width, 150, False)
    _time = "OK" if _low <= _elapsed <= _high else "MISMATCH"
    _lit = "MISMATCH" if _is_blank() else "OK"
    print(f"11/26: scroll_image pan, last window stays lit [{_lit}] elapsed={_elapsed:.2f}s window=[{_low:.2f}, {_high:.2f}]s [{_time}]")

    _big_image.recolor(display.WHITE)
    # We have a second display operation (fill) cancelling the first (scroll) after waiting `_duration_until_display_takeover`. The scroll notices only when its
    # current frame wait ends, so it returns between the moment of cancellation and one `_frame_interval_ms` later. We additionally allow for _TOLERANCE time jitters.
    _duration_until_display_takeover = 1.0  # seconds
    _frame_interval_ms = 400  # milliseconds
    _t0 = time.monotonic()
    try:
        _held = await asyncio.gather(
            d.scroll_image(_big_image, interval_ms=_frame_interval_ms),
            _trigger_filled_after(_duration_until_display_takeover, display.RED),
        )
        _elapsed = time.monotonic() - _t0
        _token = _held[0]
        _earliest = _duration_until_display_takeover - _TOLERANCE
        _latest = _duration_until_display_takeover + _frame_interval_ms / 1000 + _TOLERANCE
        _on_time = _earliest <= _elapsed <= _latest
        _fill = d.get_pixel(0, 0) == display.RED
        _status = "OK" if _on_time and _token.is_expired and _fill else "MISMATCH"
        print(
            f"12/26: scroll_image cut by render_filled, elapsed={_elapsed:.2f}s window=[{_earliest:.2f}, {_latest:.2f}]s is_expired={_token.is_expired} fill_stays={_fill} [{_status}]"
        )
    except AttributeError as exc:
        print(f"12/26: SKIPPED, {exc!r} (bundled asyncio API gap)")

    _rotate_columns = ScreenText("ROTATE").width
    _low, _high = _expected_scroll_duration(_rotate_columns, 200, True)
    d.set_rotation(0)
    _t0 = time.monotonic()
    try:
        await asyncio.gather(
            d.scroll_string("ROTATE", display.GREEN, interval_ms=200),
            _trigger_rotation_after(2.5, 270),
        )
        _elapsed = time.monotonic() - _t0
        _status = "OK" if _low <= _elapsed <= _high else "MISMATCH"
        print(f"13/26: scroll_string('ROTATE') with set_rotation(270), elapsed={_elapsed:.2f}s window=[{_low:.2f}, {_high:.2f}]s [{_status}] -- watch the axis turn vertical")
    except AttributeError as exc:
        print(f"13/26: SKIPPED, {exc!r} (bundled asyncio API gap)")
    d.set_rotation(0)

    _big_image.recolor(display.BLUE)
    _low, _high = _expected_scroll_duration(_big_image.width, 200, True)
    d.set_rotation(0)
    _t0 = time.monotonic()
    try:
        await asyncio.gather(
            d.scroll_image(_big_image, interval_ms=200),
            _trigger_rotation_after(1.0, 180),
        )
        _elapsed = time.monotonic() - _t0
        _status = "OK" if _low <= _elapsed <= _high else "MISMATCH"
        print(f"14/26: scroll_image with set_rotation(180), elapsed={_elapsed:.2f}s window=[{_low:.2f}, {_high:.2f}]s [{_status}] -- watch the motion mirrored in place")
    except AttributeError as exc:
        print(f"14/26: SKIPPED, {exc!r} (bundled asyncio API gap)")
    d.set_rotation(0)

    # The hold sleeps in 47 ms polls and returns on the next check after the fill. One more poll is possible
    # when the hold resumes in the same turn as the fill and starts another chunk before it sees the expiry.
    _duration_until_display_takeover = 0.5  # seconds
    _poll_ms = 47  # milliseconds, the default chunk in _sleep_pollable
    _t0 = time.monotonic()
    _held = await asyncio.gather(
        d.show_string("K", display.MAGENTA, duration_ms=2000),
        _trigger_filled_after(_duration_until_display_takeover, display.ORANGE),
    )
    _elapsed = time.monotonic() - _t0
    _token = _held[0]
    _earliest = _duration_until_display_takeover - _TOLERANCE
    _latest = _duration_until_display_takeover + _poll_ms / 1000 + _TOLERANCE
    _on_time = _earliest <= _elapsed <= _latest
    _fill = d.get_pixel(0, 0) == display.ORANGE
    _status = "OK" if _on_time and _token.is_expired and _fill else "MISMATCH"
    print(
        f"15/26: show_string('K') cut by render_filled, elapsed={_elapsed:.2f}s window=[{_earliest:.2f}, {_latest:.2f}]s is_expired={_token.is_expired} fill_stays={_fill} [{_status}]"
    )
    await asyncio.sleep(0.8)

    # Same cut as step 12. loop=True still returns only when the frame wait in progress at the fill ends.
    _duration_until_display_takeover = 2.5  # seconds
    _frame_interval_ms = 200  # milliseconds
    _t0 = time.monotonic()
    _held = await asyncio.gather(
        d.scroll_string("HI", display.GREEN, interval_ms=_frame_interval_ms, loop=True),
        _trigger_filled_after(_duration_until_display_takeover, display.BLUE),
    )
    _elapsed = time.monotonic() - _t0
    _token = _held[0]
    _earliest = _duration_until_display_takeover - _TOLERANCE
    _latest = _duration_until_display_takeover + _frame_interval_ms / 1000 + _TOLERANCE
    _on_time = _earliest <= _elapsed <= _latest
    _fill = d.get_pixel(0, 0) == display.BLUE
    _status = "OK" if _on_time and _token.is_expired and _fill else "MISMATCH"
    print(
        f"16/26: scroll_string('HI', loop=True) cut by render_filled, elapsed={_elapsed:.2f}s window=[{_earliest:.2f}, {_latest:.2f}]s is_expired={_token.is_expired} fill_stays={_fill} [{_status}]"
    )
    await asyncio.sleep(0.8)

    _repeat = asyncio.create_task(d.repeat_until_cancelled(_blink_heart))
    await asyncio.sleep(2.0)
    _repeat.cancel()
    try:
        await _repeat
    except asyncio.CancelledError:
        print("17/26: repeat_until_cancelled blinked a heart; cancel leaves the last picture up")
    else:
        print("17/26: repeat_until_cancelled returned without CancelledError [MISMATCH]")
    await asyncio.sleep(0.8)


# -------------------------------------------- Part B of tests -------------------------------------------- #


async def _part_b() -> None:
    print("\n--- B: placement and student-built animations (18-22), timing check (23) ---")
    _width = _big_image.width
    _big_image.recolor(display.PURPLE)
    _frames = 0
    for _start_col in range(display.WIDTH, -_width - 1, -1):
        d.render_image(_big_image, start_col=_start_col)
        await d.hold(150)
        _frames += 1
    _expected = 1 + _width + display.WIDTH
    _status = "OK" if _frames == _expected else "MISMATCH"
    print(f"18/26: hand-built marquee frames={_frames} expected={_expected} [{_status}] -- watch: looks like scroll_image")

    _shown = []
    for _start_col in range(0, -(_width - display.WIDTH) - 1, -2):
        d.render_image(_big_image, start_col=_start_col)
        await d.hold(1000)
        _shown.append(_start_col)
    print(f"19/26: hand-built two-column pan, start_col={_shown} -- watch the jump (no scroll parameter; the range strides by 2)")

    for _start_col in range(display.WIDTH, -1, -1):
        d.render_icon(Emojis.HEART, display.RED, start_col=_start_col)
        await d.hold(100)
    print("20/26: render_icon(HEART) slide-in, start_col from WIDTH down to 0 -- watch the smoothness")
    await asyncio.sleep_ms(1000)

    _hello = ScreenText("HELLO")
    for _start_col in range(display.WIDTH, -_hello.width - 1, -1):
        d.render_string(_hello, display.WHITE, start_col=_start_col)
        await d.hold(80)
    d.render_string(centered("1"), display.YELLOW)
    await d.hold(1000)
    d.render_string("1", display.YELLOW)
    await d.hold(1000)
    print("21/26: HELLO sweeps, then a centered '1', then a left-aligned '1' -- watch the crop and the centering")

    await _show_then_blank(
        "22/26: show_filled(RED), then blank",
        d.show_filled(display.RED, duration_ms=500),
        0.5,
    )

    gc.collect()
    _free_0 = gc.mem_free()  # Return the number of bytes of heap RAM that is available for Python code to allocate, or -1 if this amount is not known.
    _t0 = time.monotonic()
    for _ in range(100):
        d.render_string("HELLO")
    _ms_plain = (time.monotonic() - _t0) * 1000
    _grew_plain = _heap_grew(_free_0, gc.mem_free())
    _prepared = ScreenText("HELLO")
    gc.collect()
    _free_1 = gc.mem_free()
    _t0 = time.monotonic()
    for _ in range(100):
        d.render_string(_prepared)
    _ms_prepared = (time.monotonic() - _t0) * 1000
    _grew_prepared = _heap_grew(_free_1, gc.mem_free())
    print(f"23/26: 100 render_string('HELLO') {_ms_plain:.0f} ms, heap grew by {_grew_plain}; 100 render_string(ScreenText) {_ms_prepared:.0f} ms, heap grew by {_grew_prepared}")


# -------------------------------------------- Part C of tests -------------------------------------------- #


async def _part_c() -> None:
    print("\n--- C: takeover and argument errors (24-26) ---")
    _held = await asyncio.gather(
        d.scroll_string("IDLE", display.WHITE, loop=True),
        _trigger_arrow_after(2.5),
    )
    _token = _held[0]
    _status = "OK" if _token.is_expired else "MISMATCH"
    print(f"24/26: scroll_string('IDLE', loop=True) cut by render_arrow, is_expired={_token.is_expired} [{_status}] -- the arrow stays")
    await asyncio.sleep(0.8)

    # Unlike step 24, the arrow stops only the scroll of "IDLE" currently running. ``repeat_until_cancelled`` then commences the next scroll,
    # and the next scroll_string draws over the arrow that cancelled the first scroll. That's why we only see the arrow flashing very briefly, and then the scroll resumes.
    _repeat = asyncio.create_task(d.repeat_until_cancelled(lambda: d.scroll_string("IDLE", display.GREEN)))
    await _trigger_arrow_after(1.8)  # cancels *single* ongoing scroll of "IDLE"
    await asyncio.sleep(1.5)  # ``repeat_until_cancelled`` then commences the next scroll of "IDLE", expiring the arrow that cancelled the first scroll.
    _still = "OK" if not _repeat.done() else "MISMATCH"
    _repeat.cancel()
    try:
        await _repeat
        _stopped = "MISMATCH"
    except asyncio.CancelledError:
        _stopped = "OK"
    print(
        f"25/26: repeat_until_cancelled(scroll_string('IDLE')) still running after the arrow [{_still}], "
        f"stopped on cancel [{_stopped}] -- the arrow flashes, then the scroll resumes"
    )

    # A blue scroll of a word, not a heart. These calls raise before they take the display, so the scroll should keep moving.
    _scroll = asyncio.create_task(d.scroll_string("BLUE.", display.BLUE, blank_edges=False, loop=True))
    await asyncio.sleep(0.5)
    await _check_error(
        "show_icon(HEART) missing duration_ms",
        TypeError,
        lambda: d.show_icon(Emojis.HEART),
        _scroll,
    )
    await _check_error(
        "show_icon duration_ms=-1",
        ValueError,
        lambda: d.show_icon(Emojis.HEART, duration_ms=-1),
        _scroll,
    )
    await _check_error(
        "show_icon positional time",
        TypeError,
        lambda: d.show_icon(Emojis.HEART, display.RED, 0, 1000),
        _scroll,
    )
    await _check_error(
        "scroll_string interval_ms=-1",
        ValueError,
        lambda: d.scroll_string("A", interval_ms=-1),
        _scroll,
    )
    await _check_error(
        "render_icon start_col=1.5",
        TypeError,
        lambda: d.render_icon(Emojis.HEART, start_col=1.5),
        _scroll,
    )
    _alive = "OK" if not _scroll.done() else "MISMATCH"
    print(f"26/26: misconfigured display calls did not stop the scroll [{_alive}] -- holding it for another 1s, then cancel")
    await asyncio.sleep(2.0)
    _scroll.cancel()
    try:
        await _scroll
    except asyncio.CancelledError:
        pass


# -------------------------------------------- main  -------------------------------------------- #


async def main() -> None:
    cycle = 0
    while True:
        cycle += 1
        d.set_rotation(0)
        d.set_brightness(0.10)
        print(f"\n=== cycle {cycle} parts={_PARTS!r} ===")
        if "A" in _PARTS:
            await _part_a()
        if "B" in _PARTS:
            await _part_b()
        if "C" in _PARTS:
            await _part_c()
        d.clear()
        print("Cycle complete (Tier 2 async, display only).")
        await asyncio.sleep(1)


asyncio.run(main())

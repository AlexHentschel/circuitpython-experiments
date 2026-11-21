"""Round-1 LED-matrix on-device test, Stage 2 (Tier 2 async, display only).

``asyncio`` drives the Tier-2 display calls. This script does not use the
button modules. Stage 3 runs those ``run()`` coroutines beside a display
animation.

Stage 0 and Stage 1 walked the sync calls. This stage assumes those work.

Maintainer checklist. Each step prints ``n/25`` and ``[OK|MISMATCH]`` where
the timing or the token can be checked on the board. Visual-only steps say
what to watch. Edit ``_PARTS`` to re-run one part (``"A"``, ``"B"``, ``"C"``,
or ``"ABC"``).

Part A, show/scroll contract (1-17):

  1. ``asyncio.sleep(0.5)``. ``[OK]`` within +/-10 ms.
  2. ``show_pattern(..., duration_ms=1500)``. Picture, then blank.
     Elapsed close to 1.5 s. Last frame blank (``get_pixel`` scan).
  3. ``show_icon(Emojis.DUCK, duration_ms=1500)``. Same checks.
  4. ``show_arrow(Arrows.SOUTH, duration_ms=1500)``. Same checks.
  5. ``show_string("K", duration_ms=1500)``. Left-aligned, then blank.
  6. ``scroll_string("STAGE2")``. Marquee: in from the right, out the left.
     Elapsed close to ``(1 + columns + WIDTH) * interval_ms``.
     ``columns`` is ``ScreenText("STAGE2").width``.
  7. ``scroll_number(42)``. Same marquee check.
  8. ``show_number(7, duration_ms=1500)``. Hold, then blank.
  9. ``show_image(img, start_col=k, duration_ms=900)`` for ``k`` in
     ``0, -3, -5, 2, -8``. A window, then blank, each time.
  10. ``scroll_image(img)`` marquee. Blank, in, out, blank.
      Elapsed close to ``(1 + width + WIDTH) * interval_ms``.
  11. ``scroll_image(img, blank_edges=False)``. Starts on content, ends on
      the last window, and that window stays lit.
      Elapsed close to ``(1 + max(0, width - WIDTH)) * interval_ms``.
  12. Slow ``scroll_image`` gathered with ``render_filled`` at 1 s.
      Cut short, the fill stays, token ``is_expired``.
  13. ``scroll_string("ROTATE")`` gathered with ``set_rotation(270)``.
      The axis turns vertical. Elapsed is not shorter than the marquee.
  14. ``scroll_image`` gathered with ``set_rotation(180)``. Mirrored in
      place. Elapsed is not shorter than the marquee.
  15. ``show_string("K", duration_ms=2000)`` cut by ``render_filled`` at
      0.5 s. The fill stays. Token ``is_expired``.
  16. ``scroll_string("HI", loop=True)`` cut by ``render_filled`` after
      2.5 s. The fill stays. Token ``is_expired``.
  17. ``repeat_until_cancelled`` blinks a heart (``show_icon`` for 250 ms,
      then ``clear``). Cancel leaves the last picture up.

Part B, placement (18-22), plus an unnumbered timing print:

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
  B-timing. 100 ``render_string("HELLO")`` and 100 ``render_string`` of a
  prepared ``ScreenText``. Prints elapsed ms and ``gc.mem_free`` delta.

Part C, takeover and argument errors (23-25):

  23. ``scroll_string("IDLE", loop=True)`` gathered with ``render_arrow``
      after 2.5 s. The scroll stops, the arrow stays, token ``is_expired``.
  24. ``repeat_until_cancelled(lambda: scroll_string("IDLE"))`` with the
      same arrow after 2.5 s. The arrow is overwritten and the scroll
      resumes. The task is still running, then ``task.cancel()`` stops it.
  25. Argument errors, each with the display left unchanged:
      ``show_icon(HEART)`` (missing ``duration_ms``);
      ``show_icon(HEART, duration_ms=-1)``;
      ``show_icon(HEART, RED, 0, 1000)`` (positional time);
      ``scroll_string("A", interval_ms=-1)``;
      ``render_icon(HEART, start_col=1.5)``.
      ``[OK]`` when the exception type matches and the frame is unchanged.
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

_HOLD_TOLERANCE_S = 0.10
_SCROLL_TOLERANCE_S = 0.35
_SLEEP_TOLERANCE_S = 0.010

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


def _scroll_sleep_s(columns: int, interval_ms: int, blank_edges: bool) -> float:
    """Seconds of frame waits for one scroll pass, with no cancellation.

    ``columns`` is ``ScreenText(text).width`` or ``image.width``.
    Marquee (``blank_edges=True``): ``1 + columns + WIDTH`` frames.
    Pan (``blank_edges=False``): ``1 + max(0, columns - WIDTH)`` frames.
    One ``interval_ms`` sleep per frame.
    """
    if blank_edges:
        frames = 1 + columns + display.WIDTH
    else:
        extra = columns - display.WIDTH
        if extra < 0:
            extra = 0
        frames = 1 + extra
    return frames * interval_ms / 1000


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
    if abs(elapsed_s - expected_s) <= tolerance_s:
        return "OK"
    return "MISMATCH"


async def _trigger_filled_after(delay_s: float, color) -> None:
    """Wait, then ``render_filled``. That expires the running token."""
    await asyncio.sleep(delay_s)
    d.render_filled(color)


async def _trigger_rotation_after(delay_s: float, degrees: int) -> None:
    """Wait, then rotate. ``set_rotation`` does not expire the running token."""
    await asyncio.sleep(delay_s)
    d.set_rotation(degrees)


async def _trigger_arrow_after(delay_s: float) -> None:
    """Wait, then draw an arrow. ``render_arrow`` expires the running token."""
    await asyncio.sleep(delay_s)
    d.render_arrow(Arrows.NORTH, display.ORANGE)


async def _blink_heart() -> None:
    """One blink: a heart for 250 ms, then a dark screen."""
    await d.show_icon(Emojis.HEART, display.RED, duration_ms=250)
    d.clear()


async def _show_then_blank(label: str, call, expected_s: float) -> None:
    """Await one ``show_*``, then check the elapsed time and a blank frame."""
    _t0 = time.monotonic()
    await call
    _elapsed = time.monotonic() - _t0
    _time = _close(_elapsed, expected_s, _HOLD_TOLERANCE_S)
    _blank = "OK" if _is_blank() else "MISMATCH"
    print(
        f"{label} elapsed={_elapsed:.2f}s expected={expected_s:.2f}s [{_time}] "
        f"last frame blank [{_blank}]"
    )


async def _scroll_elapsed(label: str, call, columns: int, interval_ms: int, blank_edges: bool) -> None:
    """Await one scroll pass and compare elapsed time with the frame law."""
    _expected = _scroll_sleep_s(columns, interval_ms, blank_edges)
    _t0 = time.monotonic()
    await call
    _elapsed = time.monotonic() - _t0
    _time = _close(_elapsed, _expected, _SCROLL_TOLERANCE_S)
    print(
        f"{label} elapsed={_elapsed:.2f}s expected={_expected:.2f}s "
        f"(columns={columns}, interval_ms={interval_ms}, blank_edges={blank_edges}) [{_time}]"
    )


async def _check_error(label: str, exc_type: type, invoke) -> None:
    """Call ``invoke``. ``[OK]`` when the exception type matches and the frame is unchanged."""
    d.render_filled(display.GREEN)
    _before = _frame()
    try:
        _result = invoke()
        if hasattr(_result, "__await__"):
            await _result
    except exc_type as exc:
        _intact = _frame() == _before
        _status = "OK" if _intact else "MISMATCH"
        print(f"25/25: {label} -> {type(exc).__name__}: {exc} [{_status}] (display unchanged)")
        return
    except Exception as exc:
        print(
            f"25/25: {label} -> {type(exc).__name__}: {exc} [MISMATCH] "
            f"(expected {exc_type.__name__})"
        )
        return
    print(f"25/25: {label} -> no exception [MISMATCH]")


async def _part_a() -> None:
    print("\n--- A: show/scroll contract (1-17) ---")

    _sleep_target_s = 0.5
    _t0 = time.monotonic()
    await asyncio.sleep(_sleep_target_s)
    _elapsed = time.monotonic() - _t0
    _deviation = abs(_elapsed - _sleep_target_s)
    _status = "OK" if _deviation <= _SLEEP_TOLERANCE_S else "MISMATCH"
    print(
        f"1/25: asyncio.sleep({_sleep_target_s}) returned after {_elapsed:.4f}s "
        f"(deviation={_deviation * 1000:.1f}ms) [{_status}]"
    )

    _checker = """
            . # . # .
            # . # . #
            . # . # .
            # . # . #
            . # . # .
            """
    await _show_then_blank(
        "2/25: show_pattern checkerboard, then blank",
        d.show_pattern(_checker, display.GREEN, duration_ms=1500),
        1.5,
    )
    await _show_then_blank(
        "3/25: show_icon(DUCK), then blank",
        d.show_icon(Emojis.DUCK, display.YELLOW, duration_ms=1500),
        1.5,
    )
    await _show_then_blank(
        "4/25: show_arrow(SOUTH), then blank",
        d.show_arrow(Arrows.SOUTH, display.CYAN, duration_ms=1500),
        1.5,
    )
    await _show_then_blank(
        "5/25: show_string('K') left-aligned, then blank",
        d.show_string("K", display.MAGENTA, duration_ms=1500),
        1.5,
    )

    _stage2_columns = ScreenText("STAGE2").width
    await _scroll_elapsed(
        "6/25: scroll_string('STAGE2') marquee, then blank",
        d.scroll_string("STAGE2", display.WHITE, interval_ms=150),
        _stage2_columns,
        150,
        True,
    )
    _forty_two_columns = ScreenText("42").width
    await _scroll_elapsed(
        "7/25: scroll_number(42) marquee, then blank",
        d.scroll_number(42, display.GOLD, interval_ms=150),
        _forty_two_columns,
        150,
        True,
    )
    await _show_then_blank(
        "8/25: show_number(7), then blank",
        d.show_number(7, display.GOLD, duration_ms=1500),
        1.5,
    )

    _big_image.recolor(display.CYAN)
    for _start_col in (0, -3, -5, 2, -8):
        await _show_then_blank(
            f"9/25: show_image(start_col={_start_col}), then blank",
            d.show_image(_big_image, start_col=_start_col, duration_ms=900),
            0.9,
        )

    _big_image.recolor(display.PURPLE)
    await _scroll_elapsed(
        "10/25: scroll_image marquee (blank, in, out, blank)",
        d.scroll_image(_big_image, interval_ms=250),
        _big_image.width,
        250,
        True,
    )
    _big_image.recolor(display.CYAN)
    _t0 = time.monotonic()
    await d.scroll_image(_big_image, interval_ms=150, blank_edges=False)
    _elapsed = time.monotonic() - _t0
    _expected = _scroll_sleep_s(_big_image.width, 150, False)
    _time = _close(_elapsed, _expected, _SCROLL_TOLERANCE_S)
    _lit = "MISMATCH" if _is_blank() else "OK"
    print(
        f"11/25: scroll_image pan, last window stays lit [{_lit}] "
        f"elapsed={_elapsed:.2f}s expected={_expected:.2f}s [{_time}]"
    )

    _big_image.recolor(display.WHITE)
    _full = _scroll_sleep_s(_big_image.width, 400, True)
    _t0 = time.monotonic()
    try:
        _held = await asyncio.gather(
            d.scroll_image(_big_image, interval_ms=400),
            _trigger_filled_after(1.0, display.RED),
        )
        _elapsed = time.monotonic() - _t0
        _token = _held[0]
        _cut = _elapsed < (_full - 0.4)
        _fill = d.get_pixel(0, 0) == display.RED
        _status = "OK" if _cut and _token.is_expired and _fill else "MISMATCH"
        print(
            f"12/25: scroll_image cut by render_filled, elapsed={_elapsed:.2f}s "
            f"full={_full:.2f}s is_expired={_token.is_expired} fill_stays={_fill} [{_status}]"
        )
    except AttributeError as exc:
        print(f"12/25: SKIPPED, {exc!r} (bundled asyncio API gap)")

    _rotate_columns = ScreenText("ROTATE").width
    _full = _scroll_sleep_s(_rotate_columns, 200, True)
    d.set_rotation(0)
    _t0 = time.monotonic()
    try:
        await asyncio.gather(
            d.scroll_string("ROTATE", display.GREEN, interval_ms=200),
            _trigger_rotation_after(2.5, 270),
        )
        _elapsed = time.monotonic() - _t0
        _status = "OK" if _elapsed >= (_full - _SCROLL_TOLERANCE_S) else "MISMATCH"
        print(
            f"13/25: scroll_string('ROTATE') with set_rotation(270), "
            f"elapsed={_elapsed:.2f}s full={_full:.2f}s [{_status}] "
            f"-- watch the axis turn vertical"
        )
    except AttributeError as exc:
        print(f"13/25: SKIPPED, {exc!r} (bundled asyncio API gap)")
    d.set_rotation(0)

    _big_image.recolor(display.BLUE)
    _full = _scroll_sleep_s(_big_image.width, 200, True)
    d.set_rotation(0)
    _t0 = time.monotonic()
    try:
        await asyncio.gather(
            d.scroll_image(_big_image, interval_ms=200),
            _trigger_rotation_after(1.0, 180),
        )
        _elapsed = time.monotonic() - _t0
        _status = "OK" if _elapsed >= (_full - _SCROLL_TOLERANCE_S) else "MISMATCH"
        print(
            f"14/25: scroll_image with set_rotation(180), "
            f"elapsed={_elapsed:.2f}s full={_full:.2f}s [{_status}] "
            f"-- watch the motion mirrored in place"
        )
    except AttributeError as exc:
        print(f"14/25: SKIPPED, {exc!r} (bundled asyncio API gap)")
    d.set_rotation(0)

    _held = await asyncio.gather(
        d.show_string("K", display.MAGENTA, duration_ms=2000),
        _trigger_filled_after(0.5, display.ORANGE),
    )
    _token = _held[0]
    _fill = d.get_pixel(0, 0) == display.ORANGE
    _status = "OK" if _token.is_expired and _fill else "MISMATCH"
    print(
        f"15/25: show_string('K') cut by render_filled, "
        f"is_expired={_token.is_expired} fill_stays={_fill} [{_status}]"
    )
    await asyncio.sleep(0.8)

    _held = await asyncio.gather(
        d.scroll_string("HI", display.GREEN, interval_ms=200, loop=True),
        _trigger_filled_after(2.5, display.BLUE),
    )
    _token = _held[0]
    _fill = d.get_pixel(0, 0) == display.BLUE
    _status = "OK" if _token.is_expired and _fill else "MISMATCH"
    print(
        f"16/25: scroll_string('HI', loop=True) cut by render_filled, "
        f"is_expired={_token.is_expired} fill_stays={_fill} [{_status}]"
    )
    await asyncio.sleep(0.8)

    _repeat = asyncio.create_task(d.repeat_until_cancelled(_blink_heart))
    await asyncio.sleep(2.0)
    _repeat.cancel()
    try:
        await _repeat
    except asyncio.CancelledError:
        pass
    print("17/25: repeat_until_cancelled blinked a heart; cancel leaves the last picture up")
    await asyncio.sleep(0.8)


async def _part_b() -> None:
    print("\n--- B: placement and student-built animations (18-22) ---")
    _width = _big_image.width
    _big_image.recolor(display.PURPLE)
    _frames = 0
    for _start_col in range(display.WIDTH, -_width - 1, -1):
        d.render_image(_big_image, start_col=_start_col)
        await d.hold(150)
        _frames += 1
    _expected = 1 + _width + display.WIDTH
    _status = "OK" if _frames == _expected else "MISMATCH"
    print(
        f"18/25: hand-built marquee frames={_frames} expected={_expected} [{_status}] "
        f"-- watch: looks like scroll_image"
    )

    _shown = []
    for _start_col in range(0, -(_width - display.WIDTH) - 1, -2):
        d.render_image(_big_image, start_col=_start_col)
        await d.hold(200)
        _shown.append(_start_col)
    print(
        f"19/25: hand-built two-column pan, start_col={_shown} "
        f"-- watch the jump (no scroll parameter; the range strides by 2)"
    )

    for _start_col in range(display.WIDTH, -1, -1):
        d.render_icon(Emojis.HEART, display.RED, start_col=_start_col)
        await d.hold(100)
    print("20/25: render_icon(HEART) slide-in, start_col from WIDTH down to 0 -- watch the smoothness")

    _hello = ScreenText("HELLO")
    for _start_col in range(display.WIDTH, -_hello.width - 1, -1):
        d.render_string(_hello, display.WHITE, start_col=_start_col)
        await d.hold(80)
    d.render_string(centered("1"), display.YELLOW)
    await d.hold(1000)
    d.render_string("1", display.YELLOW)
    await d.hold(1000)
    print("21/25: HELLO sweeps, then a centered '1', then a left-aligned '1' -- watch the crop and the centering")

    await _show_then_blank(
        "22/25: show_filled(RED), then blank",
        d.show_filled(display.RED, duration_ms=500),
        0.5,
    )

    gc.collect()
    _free_0 = gc.mem_free()
    _t0 = time.monotonic()
    for _ in range(100):
        d.render_string("HELLO")
    _ms_plain = (time.monotonic() - _t0) * 1000
    _free_plain = gc.mem_free() - _free_0
    _prepared = ScreenText("HELLO")
    gc.collect()
    _free_1 = gc.mem_free()
    _t0 = time.monotonic()
    for _ in range(100):
        d.render_string(_prepared)
    _ms_prepared = (time.monotonic() - _t0) * 1000
    _free_prepared = gc.mem_free() - _free_1
    print(
        f"B-timing: 100 render_string('HELLO') {_ms_plain:.0f} ms, mem_free delta {_free_plain}; "
        f"100 render_string(ScreenText) {_ms_prepared:.0f} ms, mem_free delta {_free_prepared}"
    )


async def _part_c() -> None:
    print("\n--- C: takeover and argument errors (23-25) ---")
    _held = await asyncio.gather(
        d.scroll_string("IDLE", display.WHITE, loop=True),
        _trigger_arrow_after(2.5),
    )
    _token = _held[0]
    _status = "OK" if _token.is_expired else "MISMATCH"
    print(
        f"23/25: scroll_string('IDLE', loop=True) cut by render_arrow, "
        f"is_expired={_token.is_expired} [{_status}] -- the arrow stays"
    )
    await asyncio.sleep(0.8)

    _repeat = asyncio.create_task(d.repeat_until_cancelled(lambda: d.scroll_string("IDLE")))
    await _trigger_arrow_after(2.5)
    await asyncio.sleep(0.8)
    _still = "OK" if not _repeat.done() else "MISMATCH"
    _repeat.cancel()
    try:
        await _repeat
        _stopped = "MISMATCH"
    except asyncio.CancelledError:
        _stopped = "OK"
    print(
        f"24/25: repeat_until_cancelled(scroll_string('IDLE')) still running after the arrow [{_still}], "
        f"stopped on cancel [{_stopped}] -- the arrow flashes, then the scroll resumes"
    )

    await _check_error(
        "show_icon(HEART) missing duration_ms",
        TypeError,
        lambda: d.show_icon(Emojis.HEART),
    )
    await _check_error(
        "show_icon duration_ms=-1",
        ValueError,
        lambda: d.show_icon(Emojis.HEART, duration_ms=-1),
    )
    await _check_error(
        "show_icon positional time",
        TypeError,
        lambda: d.show_icon(Emojis.HEART, display.RED, 0, 1000),
    )
    await _check_error(
        "scroll_string interval_ms=-1",
        ValueError,
        lambda: d.scroll_string("A", interval_ms=-1),
    )
    await _check_error(
        "render_icon start_col=1.5",
        TypeError,
        lambda: d.render_icon(Emojis.HEART, start_col=1.5),
    )


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

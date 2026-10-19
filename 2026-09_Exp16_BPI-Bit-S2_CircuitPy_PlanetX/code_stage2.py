"""Round-1 LED-matrix on-device test, Stage 2 (Tier 2 async, display only).

``asyncio`` drives the Tier-2 display calls. This script does not use the
button modules. Stage 3 runs those ``run()`` coroutines beside a display
animation.

Stage 0 and Stage 1 walked the sync calls (``fill`` / ``clear_screen`` /
``set_pixel`` / ``render_icon`` / ``render_pattern`` / ``render_arrow`` /
``render_string`` / ``render_number`` / ``get_pixel`` / ``set_rotation`` /
``Icon.create`` / ``colorwheel``).
We assume that works, and use those calls here as setup around the async
steps.

What runs:

  1. ``asyncio.sleep(0.5)``. Serial prints ``[OK]`` when the elapsed time
     stays within 10 ms.
  2. ``show_pattern`` — a green checkerboard, held by ``interval_ms``.
     The picture stays up after the wait.
  3. ``show_icon(Emojis.DUCK)``. The picture stays up after the wait.
  4. ``show_arrow(Arrows.SOUTH)``. The picture stays up after the wait.
  5. ``show_string("K")`` — fits. Centered for ``interval_ms * WIDTH``,
     then the screen goes blank.
  6. ``show_string("STAGE2")`` — wider than the display, so the scrolling
     path (``SpacedGlyphColumnFeeder`` into a ring buffer). Ends blank.
  7. ``show_number(42)`` — ``show_string(str(42))``, also the scroll path.
     Ends blank.
  8. ``show_number(7)`` — one digit, so the fit path. Holds, then blank.
  9. ``Display.show_image`` on a 10-column image at offsets 0, 3, 5, -2,
     and 8 (left half, straddling both halves, right half, off the left
     edge, off the right edge). The picture stays up after each wait.
  10. ``Display.scroll_image`` of that same image.
  11. A slow ``scroll_image`` gathered with a Tier-1 ``fill`` after 1 s.
      ``fill`` cancels the animation (``Display._acquire``), so elapsed
      time should fall short of the uninterrupted length. Serial prints
      ``[OK]`` when it does.
  12. ``show_string("ROTATE")`` gathered with ``set_rotation(270)`` after
      2.5s. Rotation does not cancel, so the scroll should run out, and
      the motion should turn from horizontal to vertical. The ``[OK]``
      check compares elapsed time with ``_scroll_sleep_s``: one empty
      frame, then one frame per text column, then ``WIDTH`` empty columns,
      each held for ``interval_ms``.
  13. ``Display.scroll_image`` gathered with ``set_rotation(180)`` after 1 s.
      Same non-cancel check, through ``Image._render_window`` rather than
      step 12's ring buffer. 180 mirrors in place. The estimate is
      ``(width - WIDTH) // step + 1`` frames.
  14. ``show_string("K")`` gathered with a ``fill`` during the hold.
      The fill stays lit. A blank screen means the hold cleared itself
      after being cut short. Serial prints ``[OK]`` when the token expired.
      This is the fit-path hold, not step 11's scroll.
  15. ``show_string("A", loop=True)`` gathered with a ``fill``. The letter
      would stay up until cancelled. The fill stays. Serial prints ``[OK]``
      when the token expired.
  16. ``Display.forever`` blinks a heart until the task is cancelled.
      The last picture stays up.

A rotate-then-start-a-new-scroll case is not here. It would only compose
``set_rotation`` (Stages 0 and 1) with a scroll that starts at a fixed
rotation (steps 6, 7, and 10).

Each cycle starts at rotation 0 and brightness 0.10. The sequence repeats
so the script does not fall through to the REPL.
"""

import asyncio
import time

import display
from display import Emojis, Arrows
from display.text_layout import SpacedGlyphColumnFeeder

d = display.display

print("Stage 2: import asyncio OK")

# Constants for steps 8-10, built once (not per-cycle), matching Stage 1's
# own allocate-once pattern. 10 columns x 5 rows (2 * WIDTH x HEIGHT):
# left half is a diamond (distinct shape), right half is a solid block, so
# `Display.show_image` at offset 0 vs. offset 5 renders two visually
# distinct windows and `Display.scroll_image` shows a clear transition
# between them.
_BIG_PATTERN = """
. . # . . # # # # #
. # # # . # # # # #
# # # # # # # # # #
. # # # . # # # # #
. . # . . # # # # #
"""
_big_image = display.Image.create(_BIG_PATTERN, display.CYAN)


def _scroll_sleep_s(text: str, interval_ms: int) -> float:
    """Seconds that ``Display.show_string(text)`` spends waiting, with no cancellation.

    ``c`` is how many columns ``SpacedGlyphColumnFeeder(text).column_count()`` reports.
    Each frame is held for ``interval_ms`` milliseconds. An uninterrupted
    scroll of text wider than the display waits three groups of frames:

    * 1 frame shows the empty screen before the first column comes in.
    * ``c`` frames bring the text in, one column at a time.
    * ``WIDTH`` frames bring in empty columns, one column at a time, until
      the last text column has left the screen.

    The wait is therefore ``(1 + c + WIDTH) × interval_ms`` milliseconds.
    Text that fits (``c <= WIDTH``, including an empty string) is centered
    and held for ``interval_ms × WIDTH`` instead, then the screen is cleared.
    That clear is not part of this wait. Both formulas are for ``loop=False``.
    With ``loop=True``, the call runs until cancelled: text that fits stays
    up, and wider text keeps scrolling.
    """
    columns = SpacedGlyphColumnFeeder(str(text)).column_count()
    if columns <= display.WIDTH:
        return interval_ms * display.WIDTH / 1000
    return (1 + columns + display.WIDTH) * interval_ms / 1000


async def _trigger_cancellation_after(delay_s: float, color=display.RED) -> None:
    """Wait ``delay_s`` seconds, then ``fill`` with ``color``.

    ``fill`` calls ``Display._acquire``, which expires the display's current
    cancellation ``Token``. A Tier-2 call still holding that token returns
    on its next check (see ``core.py``, "Cancellation policy").

    Used by the scroll-cancel step and by the fit-hold preempt step.
    """
    await asyncio.sleep(delay_s)
    d.fill(color)


async def _trigger_rotation_after(delay_s: float, degrees: int) -> None:
    """Wait ``delay_s`` seconds, then rotate -- the non-cancelling counterpart
    to ``_trigger_cancellation_after`` above.

    ``set_rotation`` does not call ``Display._acquire`` (see ``core.py``'s
    module docstring, "Cancellation policy"). The in-flight Tier-2 animation
    keeps its token; only the next frame's coordinate mapping changes.

    Runs concurrently with a slow Tier-2 scroll (via ``asyncio.gather``) in
    the two rotate-while-scrolling steps, changing the display's orientation
    mid-animation instead of interrupting it. See ``lib/display/README.md``'s
    "Rotation during an in-flight Tier 2 animation" section for why this is safe:
    in-place ``_LUT`` mutation + every render primitive re-reading ``_LUT``
    fresh each frame + ``asyncio``'s cooperative, single-threaded scheduling.
    """
    await asyncio.sleep(delay_s)
    d.set_rotation(degrees)


async def _pulse_heart() -> None:
    """One blink for ``Display.forever``: a heart, then a dark screen."""
    d.render_icon(Emojis.HEART, color=display.RED)
    await asyncio.sleep(0.25)
    d.clear_screen()
    await asyncio.sleep(0.25)


async def main() -> None:
    cycle = 0
    while True:
        cycle += 1
        # Each cycle starts at rotation 0 and brightness 0.10, independent
        # of what the previous cycle left set. 0.10 is dimmer than the
        # library default 0.20.
        d.set_rotation(0)
        d.set_brightness(0.10)
        print(f"\n=== cycle {cycle} ===")

        # 1) asyncio.sleep(0.5). [OK] means elapsed time stayed within 10 ms,
        #    so the scheduler honored the delay.
        _sleep_target_s = 0.5
        _tolerance_s = 0.010
        _t0 = time.monotonic()
        await asyncio.sleep(_sleep_target_s)
        _elapsed = time.monotonic() - _t0
        _timing_deviation = abs(_elapsed - _sleep_target_s)
        _status = "OK" if _timing_deviation <= _tolerance_s else "MISMATCH"
        print(
            f"1/16: asyncio.sleep({_sleep_target_s}) returned after {_elapsed:.4f}s "
            f"(deviation={_timing_deviation * 1000:.1f}ms, tolerance=+/-{_tolerance_s * 1000:.0f}ms) [{_status}] "
            f"(asyncio.sleep honored the delay)"
        )

        # 2) show_pattern holds the checkerboard for interval_ms. Stage 1's
        #    render_pattern returned immediately and the script slept itself.
        d.clear_screen()
        await d.show_pattern(
            """
            . # . # .
            # . # . #
            . # . # .
            # . # . #
            . # . # .
            """,
            display.GREEN,
            interval_ms=1500,
        )
        print("2/16: show_pattern(checkerboard) -- picture stays up after the wait")

        # 3) show_icon(Emojis.DUCK). Stage 0 used HEART and Stage 1 used HAPPY;
        #    we assume those icon paths work.
        d.clear_screen()
        await d.show_icon(Emojis.DUCK, color=display.YELLOW, interval_ms=1500)
        print("3/16: show_icon(Emojis.DUCK) -- picture stays up after the wait")

        # 4) show_arrow(Arrows.SOUTH). Stage 1 used NORTH; we assume that
        #    arrow path works.
        d.clear_screen()
        await d.show_arrow(Arrows.SOUTH, display.CYAN, interval_ms=1500)
        print("4/16: show_arrow(Arrows.SOUTH) -- picture stays up after the wait")

        # 5) "K" fits. Centered for interval_ms * WIDTH (300 * 5 = 1500 ms),
        #    then the screen is blank.
        d.clear_screen()
        await d.show_string("K", display.MAGENTA, interval_ms=300)
        print("5/16: show_string('K') -- holds about 1.5s, then the screen is blank")
        await asyncio.sleep(0.8)

        # 6) "STAGE2" is wider than the display, so show_string scrolls.
        #    Columns come from SpacedGlyphColumnFeeder.
        d.clear_screen()
        await d.show_string("STAGE2", display.WHITE, interval_ms=150)
        print("6/16: show_string('STAGE2') -- scrolls, then the screen is blank")

        # 7) show_number(42) is show_string("42"). Two digits, so the scroll path.
        d.clear_screen()
        await d.show_number(42, display.GOLD, interval_ms=150)
        print("7/16: show_number(42), scrolls, then the screen is blank")

        # 8) show_number(7) is one digit, so it fits. Centered for
        #    interval_ms * WIDTH, then the screen goes blank. Step 7 scrolled.
        d.clear_screen()
        await d.show_number(7, display.GOLD, interval_ms=300)
        print("8/16: show_number(7) -- holds about 1.5s, then the screen is blank")
        await asyncio.sleep(0.8)

        # 9) show_image on the 10-column image:
        #      0   left half (diamond), fully on screen
        #      3   window straddling both halves
        #      5   right half (solid block)
        #     -2   two columns off the left edge, drawn OFF
        #      8   past the right edge, trailing columns drawn OFF
        #    _render_window writes OFF for uncovered columns, so there is no
        #    clear_screen between offsets. Recolor to CYAN first: step 10
        #    leaves this shared image PURPLE.
        _big_image.recolor(display.CYAN)
        for _offset in (0, 3, 5, -2, 8):
            await d.show_image(_big_image, offset=_offset, interval_ms=900)
            print(f"9/16: Display.show_image(offset={_offset}) rendered")
        print("9/16: Display.show_image(offset), aligned/in-between/negative/overhang windows of a 10-wide image")

        # 10) scroll_image walks the same image one column per frame.
        #    PURPLE so it is distinct from step 9's CYAN. Step 9 recolors
        #    back to CYAN at the start of the next cycle.
        d.clear_screen()
        _big_image.recolor(display.PURPLE)
        await d.scroll_image(_big_image, step=1, interval_ms=250)
        print("10/16: Display.scroll_image, full-width scroll animation (PURPLE, vs. step 9's CYAN)")

        # 11) Slow white scroll gathered with a Tier-1 fill after 1 s.
        #     fill calls _acquire, so the scroll should return early.
        #     [OK] means elapsed time is at least 0.5 s under the
        #     uninterrupted length (6 frames x 400 ms). WHITE so this
        #     scroll is distinct from step 10, and the fill turns it RED.
        d.clear_screen()
        _big_image.recolor(display.WHITE)
        _full_length_s = 6 * 0.4  # 6 renders (offsets 0..5) x 400 ms/frame, uninterrupted
        _interrupt_at_s = 1.0
        _t0 = time.monotonic()
        try:
            await asyncio.gather(
                d.scroll_image(_big_image, step=1, interval_ms=400),
                _trigger_cancellation_after(_interrupt_at_s),
            )
            _elapsed = time.monotonic() - _t0
            _cancelled_early = _elapsed < (_full_length_s - 0.5)
            _status = "OK" if _cancelled_early else "MISMATCH"
            print(f"11/16: cancellation check, elapsed={_elapsed:.2f}s vs interrupt-at={_interrupt_at_s:.2f}s vs uninterrupted-full-length={_full_length_s:.2f}s [{_status}]")
        except AttributeError as exc:
            # A missing gather (or similar) is printed and the cycle continues.
            print(f"11/16: cancellation check SKIPPED, {exc!r} (bundled asyncio API gap)")

        # 12) show_string("ROTATE") gathered with set_rotation(270) after 2.5 s.
        #     set_rotation does not call _acquire, so the scroll should run
        #     out, and 270 swaps axes so the motion turns vertical.
        #     _scroll_sleep_s counts one empty frame, then one frame per
        #     text column, then WIDTH empty columns.
        d.clear_screen()
        d.set_rotation(0)
        _text_11 = "ROTATE"
        _interval_ms_11 = 200
        _full_length_s_11 = _scroll_sleep_s(_text_11, _interval_ms_11)
        _rotate_at_s_11 = 2.5
        _t0 = time.monotonic()
        try:
            await asyncio.gather(
                d.show_string(_text_11, display.GREEN, interval_ms=_interval_ms_11),
                _trigger_rotation_after(_rotate_at_s_11, 270),
            )
            _elapsed_11 = time.monotonic() - _t0
            _not_cancelled_11 = _elapsed_11 >= (_full_length_s_11 - 0.5)
            _status_11 = "OK" if _not_cancelled_11 else "MISMATCH"
            print(
                f"12/16: rotate-while-scrolling (show_string), elapsed={_elapsed_11:.2f}s "
                f"vs rotate-at={_rotate_at_s_11:.2f}s vs uninterrupted-full-length={_full_length_s_11:.2f}s "
                f"[{_status_11}] (set_rotation must NOT shorten the scroll, contrast step 11) "
                f"-- watch for the scroll axis turning horizontal->vertical partway through"
            )
        except AttributeError as exc:
            # Same as step 11: print a missing gather and keep the cycle going.
            print(f"12/16: rotate-while-scrolling SKIPPED, {exc!r} (bundled asyncio API gap)")
        d.set_rotation(0)

        # 13) scroll_image gathered with set_rotation(180) after 1 s.
        #     Same non-cancel as step 12, through Image._render_window.
        #     180 mirrors in place (step 12's 270 turns the axis).
        #     The estimate is (width - WIDTH) // step + 1 frames, taken
        #     from this image's width. [OK] means elapsed time reaches it.
        d.clear_screen()
        d.set_rotation(0)
        _big_image.recolor(display.BLUE)
        _step_12 = 1
        _interval_ms_12 = 400
        _max_start_12 = _big_image.width - display.WIDTH
        _full_length_s_12 = ((_max_start_12 // _step_12) + 1) * _interval_ms_12 / 1000
        _rotate_at_s_12 = 1.0
        _t0 = time.monotonic()
        try:
            await asyncio.gather(
                d.scroll_image(_big_image, step=_step_12, interval_ms=_interval_ms_12),
                _trigger_rotation_after(_rotate_at_s_12, 180),
            )
            _elapsed_12 = time.monotonic() - _t0
            _not_cancelled_12 = _elapsed_12 >= (_full_length_s_12 - 0.5)
            _status_12 = "OK" if _not_cancelled_12 else "MISMATCH"
            print(
                f"13/16: rotate-while-scrolling (Display.scroll_image), elapsed={_elapsed_12:.2f}s "
                f"vs rotate-at={_rotate_at_s_12:.2f}s vs uninterrupted-full-length={_full_length_s_12:.2f}s "
                f"[{_status_12}] (set_rotation must NOT shorten the scroll, contrast step 11) "
                f"-- watch for the same motion mirrored in place (not turned 90 degrees, unlike step 12)"
            )
        except AttributeError as exc:
            print(f"13/16: rotate-while-scrolling SKIPPED, {exc!r} (bundled asyncio API gap)")
        d.set_rotation(0)

        # 14) Fitting show_string, loop=False. The full hold would be
        #     interval_ms * WIDTH (400 * 5 = 2000 ms), then a blank screen.
        #     A fill at 0.5 s cuts that short. The orange stays. This is not
        #     step 11: that step cuts a scroll between frames.
        d.clear_screen()
        _held = await asyncio.gather(
            d.show_string("K", display.MAGENTA, interval_ms=400),
            _trigger_cancellation_after(0.5, display.ORANGE),
        )
        _token = _held[0]
        _status = "OK" if _token.is_expired else "MISMATCH"
        print(
            f"14/16: show_string('K') hold cut short by an orange fill [{_status}] "
            "-- the orange stays; a blank screen means the hold cleared itself"
        )
        await asyncio.sleep(1.2)

        # 15) loop=True on a fitting letter holds until cancelled. The blue
        #     fill stays. The call does not clear the screen after the cancel.
        d.clear_screen()
        _looped = await asyncio.gather(
            d.show_string("A", display.GREEN, interval_ms=200, loop=True),
            _trigger_cancellation_after(0.8, display.BLUE),
        )
        _token = _looped[0]
        _status = "OK" if _token.is_expired else "MISMATCH"
        print(
            f"15/16: show_string('A', loop=True) cut short by a blue fill [{_status}] "
            "-- the blue stays; a blank screen means the hold cleared itself"
        )
        await asyncio.sleep(1.2)

        # 16) forever repeats _pulse_heart until the task is cancelled.
        #     The last picture stays on the LEDs.
        _forever = asyncio.create_task(d.forever(_pulse_heart, sleep_between_ms=50))
        await asyncio.sleep(2.0)
        _forever.cancel()
        try:
            await _forever
        except asyncio.CancelledError:
            pass
        print("16/16: Display.forever blinked a heart, then cancel left the last picture up")
        await asyncio.sleep(1.0)

        d.clear_screen()
        print("Cycle complete (Tier 2 async, display only).")
        await asyncio.sleep(1)


asyncio.run(main())

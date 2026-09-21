"""Round-1 LED-matrix on-device test, Stage 2 (Tier 2 async, display only).

``asyncio`` drives the Tier-2 display calls. This script does not use the
button modules. Stage 3 runs those ``run()`` coroutines beside a display
animation.

Stage 0 and Stage 1 walked the sync calls (``fill`` / ``clear_screen`` /
``set_pixel`` / ``render_icon`` / ``render_pattern`` / ``render_arrow`` /
``get_pixel`` / ``set_rotation`` / ``create_image`` / ``colorwheel``).
We assume that works, and use those calls here as setup around the async
steps.

What runs:

  1. ``asyncio.sleep(0.5)``. Serial prints ``[OK]`` when the elapsed time
     stays within 10 ms.
  2. ``show_leds`` — a green checkerboard, held by ``interval_ms``.
  3. ``show_icon(Icons.DUCK)``.
  4. ``show_arrow(Arrows.SOUTH)``.
  5. ``show_string("K")`` — narrower than the display, so the centered-hold
     path.
  6. ``show_string("STAGE2")`` — wider than the display, so the scrolling
     path (``SpacedGlyphColumnFeeder`` into a ring buffer).
  7. ``show_number(42)`` — ``show_string(str(42))``, also the scroll path.
  8. ``Image.show_image`` on a 10-column image at offsets 0, 3, 5, -2,
     and 8 (left half, straddling both halves, right half, off the left
     edge, off the right edge).
  9. ``Image.scroll_image`` of that same image.
  10. A slow ``scroll_image`` gathered with a Tier-1 ``fill`` after 1 s.
      ``fill`` cancels the animation (``Display._acquire``), so elapsed
      time should fall short of the uninterrupted length. Serial prints
      ``[OK]`` when it does.
  11. ``show_string("ROTATE")`` gathered with ``set_rotation(270)`` after
      2.5 s. Rotation does not cancel, so the scroll should run out, and
      the motion should turn from horizontal to vertical. The ``[OK]``
      check compares elapsed time with this script's full-length estimate
      (``WIDTH`` columns per character, plus a ``WIDTH + 1`` blank tail).
      That estimate leaves out the spacer column
      ``SpacedGlyphColumnFeeder`` inserts between characters.
  12. ``Image.scroll_image`` gathered with ``set_rotation(180)`` after 1 s.
      Same non-cancel check, through ``Image._render_window`` rather than
      step 11's ring buffer. 180 mirrors in place. The estimate is
      ``(width - WIDTH) // step + 1`` frames.

A rotate-then-start-a-new-scroll case is not here. It would only compose
``set_rotation`` (Stages 0 and 1) with a scroll that starts at a fixed
rotation (steps 6, 7, and 9).

Each cycle starts at rotation 0 and brightness 0.10. The sequence repeats
so the script does not fall through to the REPL.
"""

import asyncio
import time

import display
from display import Icons, Arrows

d = display.display

print("Stage 2: import asyncio OK")

# Constants for steps 8-10, built once (not per-cycle), matching Stage 1's
# own allocate-once pattern. 10 columns x 5 rows (2 * WIDTH x HEIGHT, the
# `create_big_image` contract): left half is a diamond (distinct shape),
# right half is a solid block, so `show_image` at offset 0 vs. offset 5
# renders two visually distinct windows and `scroll_image` shows a clear
# transition between them.
_BIG_PATTERN = """
. . # . . # # # # #
. # # # . # # # # #
# # # # # # # # # #
. # # # . # # # # #
. . # . . # # # # #
"""
_big_image = display.create_big_image(_BIG_PATTERN, display.CYAN)


async def _trigger_cancellation_after(delay_s: float) -> None:
    """Wait ``delay_s`` seconds, then perform an ordinary Tier-1 write.

    Every Tier-1 mutating method (here: ``fill``) calls ``Display._acquire``
    internally, which bumps the display's cancellation-token generation.
    Any Tier-2 animation still running with an older token sees this on its
    next ``_is_cancelled`` check and returns early (see ``core.py``'s
    module docstring, "Cancellation policy").

    Runs concurrently with a slow Tier-2 scroll (via ``asyncio.gather``) in
    step 10 below, acting as the interrupting event.
    """
    await asyncio.sleep(delay_s)
    d.fill(display.RED)


async def _trigger_rotation_after(delay_s: float, degrees: int) -> None:
    """Wait ``delay_s`` seconds, then rotate -- the non-cancelling counterpart
    to ``_trigger_cancellation_after`` above.

    ``set_rotation`` does not call ``Display._acquire`` (see ``core.py``'s
    module docstring, "Cancellation policy"). The in-flight Tier-2 animation
    keeps its token; only the next frame's coordinate mapping changes.

    Runs concurrently with a slow Tier-2 scroll (via ``asyncio.gather``) in
    steps 11-12 below, changing the display's orientation mid-animation
    instead of interrupting it. See ``lib/display/README.md``'s "Rotation
    during an in-flight Tier 2 animation" section for why this is safe:
    in-place ``_LUT`` mutation + every render primitive re-reading ``_LUT``
    fresh each frame + ``asyncio``'s cooperative, single-threaded scheduling.
    """
    await asyncio.sleep(delay_s)
    d.set_rotation(degrees)


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
            f"1/12: asyncio.sleep({_sleep_target_s}) returned after {_elapsed:.4f}s "
            f"(deviation={_timing_deviation * 1000:.1f}ms, tolerance=+/-{_tolerance_s * 1000:.0f}ms) [{_status}] "
            f"(asyncio.sleep honored the delay)"
        )

        # 2) show_leds holds the checkerboard for interval_ms. Stage 1's
        #    render_pattern returned immediately and the script slept itself.
        d.clear_screen()
        await d.show_leds(
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
        print("2/12: show_leds(checkerboard), async pattern render + interval_ms hold")

        # 3) show_icon(Icons.DUCK). Stage 0 used HEART and Stage 1 used HAPPY;
        #    we assume those icon paths work.
        d.clear_screen()
        await d.show_icon(Icons.DUCK, display.YELLOW, interval_ms=1500)
        print("3/12: show_icon(Icons.DUCK), async icon render + interval_ms hold")

        # 4) show_arrow(Arrows.SOUTH). Stage 1 used NORTH; we assume that
        #    arrow path works.
        d.clear_screen()
        await d.show_arrow(Arrows.SOUTH, display.CYAN, interval_ms=1500)
        print("4/12: show_arrow(Arrows.SOUTH), async arrow render + interval_ms hold")

        # 5) "K" is narrower than the display, so show_string centers and holds.
        d.clear_screen()
        await d.show_string("K", display.MAGENTA, interval_ms=300)
        print("5/12: show_string('K'), fits-on-screen centered-hold path")

        # 6) "STAGE2" is wider than the display, so show_string scrolls.
        #    Columns come from SpacedGlyphColumnFeeder.
        d.clear_screen()
        await d.show_string("STAGE2", display.WHITE, interval_ms=150)
        print("6/12: show_string('STAGE2'), scrolling ring-buffer path")

        # 7) show_number(42) is show_string("42"). Two digits, so the scroll path.
        d.clear_screen()
        await d.show_number(42, display.GOLD, interval_ms=150)
        print("7/12: show_number(42), wrapper routes into show_string's scroll path")

        # 8) show_image on the 10-column image:
        #      0   left half (diamond), fully on screen
        #      3   window straddling both halves
        #      5   right half (solid block)
        #     -2   two columns off the left edge, drawn OFF
        #      8   past the right edge, trailing columns drawn OFF
        #    _render_window writes OFF for uncovered columns, so there is no
        #    clear_screen between offsets. Recolor to CYAN first: step 9
        #    leaves this shared image PURPLE.
        _big_image.recolor(display.CYAN)
        for _offset in (0, 3, 5, -2, 8):
            await _big_image.show_image(offset=_offset, interval_ms=900)
            print(f"8/12: Image.show_image(offset={_offset}) rendered")
        print("8/12: Image.show_image(offset), aligned/in-between/negative/overhang windows of a 10-wide image")

        # 9) scroll_image walks the same image one column per frame.
        #    PURPLE so it is distinct from step 8's CYAN. Step 8 recolors
        #    back to CYAN at the start of the next cycle.
        d.clear_screen()
        _big_image.recolor(display.PURPLE)
        await _big_image.scroll_image(step=1, interval_ms=250)
        print("9/12: Image.scroll_image, full-width scroll animation (PURPLE, vs. step 8's CYAN)")

        # 10) Slow white scroll gathered with a Tier-1 fill after 1 s.
        #     fill calls _acquire, so the scroll should return early.
        #     [OK] means elapsed time is at least 0.5 s under the
        #     uninterrupted length (6 frames x 400 ms). WHITE so this
        #     scroll is distinct from step 9, and the fill turns it RED.
        d.clear_screen()
        _big_image.recolor(display.WHITE)
        _full_length_s = 6 * 0.4  # 6 renders (offsets 0..5) x 400 ms/frame, uninterrupted
        _interrupt_at_s = 1.0
        _t0 = time.monotonic()
        try:
            await asyncio.gather(
                _big_image.scroll_image(step=1, interval_ms=400),
                _trigger_cancellation_after(_interrupt_at_s),
            )
            _elapsed = time.monotonic() - _t0
            _cancelled_early = _elapsed < (_full_length_s - 0.5)
            _status = "OK" if _cancelled_early else "MISMATCH"
            print(f"10/12: cancellation check, elapsed={_elapsed:.2f}s vs interrupt-at={_interrupt_at_s:.2f}s vs uninterrupted-full-length={_full_length_s:.2f}s [{_status}]")
        except AttributeError as exc:
            # A missing gather (or similar) is printed and the cycle continues.
            print(f"10/12: cancellation check SKIPPED, {exc!r} (bundled asyncio API gap)")

        # 11) show_string("ROTATE") gathered with set_rotation(270) after 2.5 s.
        #     set_rotation does not call _acquire, so the scroll should run
        #     out, and 270 swaps axes so the motion turns vertical.
        #     The [OK] estimate counts WIDTH columns per character plus a
        #     WIDTH+1 blank tail. SpacedGlyphColumnFeeder also inserts one
        #     spacer column between characters, which this estimate leaves out.
        d.clear_screen()
        d.set_rotation(0)
        _text_11 = "ROTATE"
        _interval_ms_11 = 200
        _full_length_s_11 = (display.WIDTH * len(_text_11) + display.WIDTH + 1) * _interval_ms_11 / 1000
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
                f"11/12: rotate-while-scrolling (show_string), elapsed={_elapsed_11:.2f}s "
                f"vs rotate-at={_rotate_at_s_11:.2f}s vs uninterrupted-full-length={_full_length_s_11:.2f}s "
                f"[{_status_11}] (set_rotation must NOT shorten the scroll, contrast step 10) "
                f"-- watch for the scroll axis turning horizontal->vertical partway through"
            )
        except AttributeError as exc:
            # Same as step 10: print a missing gather and keep the cycle going.
            print(f"11/12: rotate-while-scrolling SKIPPED, {exc!r} (bundled asyncio API gap)")
        d.set_rotation(0)

        # 12) scroll_image gathered with set_rotation(180) after 1 s.
        #     Same non-cancel as step 11, through Image._render_window.
        #     180 mirrors in place (step 11's 270 turns the axis).
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
                _big_image.scroll_image(step=_step_12, interval_ms=_interval_ms_12),
                _trigger_rotation_after(_rotate_at_s_12, 180),
            )
            _elapsed_12 = time.monotonic() - _t0
            _not_cancelled_12 = _elapsed_12 >= (_full_length_s_12 - 0.5)
            _status_12 = "OK" if _not_cancelled_12 else "MISMATCH"
            print(
                f"12/12: rotate-while-scrolling (Image.scroll_image), elapsed={_elapsed_12:.2f}s "
                f"vs rotate-at={_rotate_at_s_12:.2f}s vs uninterrupted-full-length={_full_length_s_12:.2f}s "
                f"[{_status_12}] (set_rotation must NOT shorten the scroll, contrast step 10) "
                f"-- watch for the same motion mirrored in place (not turned 90 degrees, unlike step 11)"
            )
        except AttributeError as exc:
            print(f"12/12: rotate-while-scrolling SKIPPED, {exc!r} (bundled asyncio API gap)")
        d.set_rotation(0)

        d.clear_screen()
        print("Cycle complete (Tier 2 async, display only).")
        await asyncio.sleep(1)


asyncio.run(main())

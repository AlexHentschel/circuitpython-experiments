"""Round-1 LED-matrix on-device test, Stage 2 (Tier 2 async, display only).

Additive, not repetitive: Stage 0 (minimal Tier 1) and Stage 1 (broader
Tier 1) are already confirmed on-device and frozen in the sibling
`code_stage0.py` / `code_stage1.py`; see `CONCLUSIONS.md` for their
findings. This script exercises only what Stages 0/1 did **not** cover:
the async ``show_*``/``Image`` API in `lib/display/core.py`'s "Tier 2"
section (~lines 829-990), so a human re-running this doesn't have to
re-watch already-confirmed sync-rendering behaviour.

**Display only: deliberately does NOT touch `lib/buttons.py`.** The
original 4-stage breakdown (persona memory, Session 17) put buttons
combined with Tier 2 at a later stage, not this one. Confirmed with Alex
(fresh-chat handoff, 2026-09-11): combining two still-unverified things
(K1's Tier-2 async display API *and* the also-unverified async
``Buttons.run()`` wrapper) in one stage would confound failures; a
problem couldn't be cleanly attributed to one or the other. Buttons wait
for a later combined stage, where the interesting new claim becomes two
concurrent async tasks (display animation + button poll), not just K1
in isolation.

What this proves, if all ten steps print cleanly each cycle and the
matrix behaves as described: **step 1 is the actual first real test of K1**:
the bundled `asyncio` (staged onto CIRCUITPY's `lib/`, confirmed
present but never yet imported by a running script) works at all on
this board. Steps 2-4 confirm the thin async wrappers
(``show_leds``/``show_icon``/``show_arrow``) render the same way their
Tier-1 sync counterparts already did, just via ``await``. Steps 5-7
confirm ``show_string``/``show_number``: the short-text centered-hold
path (5) is a different code path from the long-text scrolling
ring-buffer path fed by ``_GlyphColumnFeeder`` (6), and ``show_number``
(7) is a thin wrapper proven to actually route through ``show_string``'s
scroll path for a 2-digit number. Steps 8-9 confirm the ``Image``
class's own async methods on an image *wider than the display*
(``create_big_image``, 10 columns vs. 5): ``show_image(offset)`` picks a
fixed window, ``scroll_image`` animates across the full width. Step 10
is the most important K1 claim of all: the cancellation-token contract
every Tier 2 animation relies on (`core.py`'s ``_acquire``/
``_is_cancelled``). It starts a slow scroll, then interrupts it
mid-flight with an ordinary Tier-1 write, confirming the animation
actually stops early instead of running to completion. This is a serial
self-check (elapsed time vs. the animation's own full-length timing),
not a visual judgment call.

Looped (``while True``), not one-shot, for the same reason as Stage
0/1: a CircuitPython script that reaches its end falls back to the
REPL and stops producing output, and the autonomous serial-capture
window can't be reliably timed against a single run.
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


async def main() -> None:
    cycle = 0
    while True:
        cycle += 1
        # Defensive baseline at the top of every cycle, matching Stage 1's own
        # rationale: keeps every cycle's starting state independent of what a
        # future added step might leave behind.
        d.set_rotation(0)
        d.set_brightness(0.10)
        print(f"\n=== cycle {cycle} ===")

        # 1) K1 smoke test: the actual first real exercise of the bundled
        #    asyncio on this board. Everything below depends on this working.
        #    Approximate timing self-check (+/- 10ms tolerance): confirms the
        #    scheduler is actually honoring the requested delay, not just that
        #    the call doesn't raise; a coroutine that returns instantly (or
        #    hangs) would otherwise print the same "returned" line either way.
        _sleep_target_s = 0.5
        _tolerance_s = 0.010
        _t0 = time.monotonic()
        await asyncio.sleep(_sleep_target_s)
        _elapsed = time.monotonic() - _t0
        _timing_deviation = abs(_elapsed - _sleep_target_s)
        _status = "OK" if _timing_deviation <= _tolerance_s else "MISMATCH"
        print(
            f"1/10: asyncio.sleep({_sleep_target_s}) returned after {_elapsed:.4f}s "
            f"(deviation={_timing_deviation * 1000:.1f}ms, tolerance=+/-{_tolerance_s * 1000:.0f}ms) [{_status}] "
            f"(bundle asyncio runs on-device, K1 smoke test)"
        )

        # 2) show_leds: async wrapper over render_pattern, holds via interval_ms
        #    instead of a separate time.sleep() the way Tier 1 test scripts needed.
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
        print("2/10: show_leds(checkerboard), async pattern render + interval_ms hold")

        # 3) show_icon: async wrapper over render_icon. DUCK (not HEART/HAPPY,
        #    both already exercised by Stage 0/1) generalizes the icon-decode
        #    path to a third icon under the async entry point specifically.
        d.clear_screen()
        await d.show_icon(Icons.DUCK, display.YELLOW, interval_ms=1500)
        print("3/10: show_icon(Icons.DUCK), async icon render + interval_ms hold")

        # 4) show_arrow: async wrapper over render_arrow. SOUTH (Stage 1 used
        #    NORTH) generalizes beyond the one direction already confirmed.
        d.clear_screen()
        await d.show_arrow(Arrows.SOUTH, display.CYAN, interval_ms=1500)
        print("4/10: show_arrow(Arrows.SOUTH), async arrow render + interval_ms hold")

        # 5) show_string, short text: fits on screen (single glyph <= WIDTH
        #    columns), so this exercises the centered-and-held path, distinct
        #    from step 6's scrolling path.
        d.clear_screen()
        await d.show_string("K", display.MAGENTA, interval_ms=300)
        print("5/10: show_string('K'), fits-on-screen centered-hold path")

        # 6) show_string, long text: forces the scrolling ring-buffer path
        #    fed by _GlyphColumnFeeder (new code Stage 0/1 never touched at
        #    all, since it's Tier 2 only).
        d.clear_screen()
        await d.show_string("STAGE2", display.WHITE, interval_ms=150)
        print("6/10: show_string('STAGE2'), scrolling ring-buffer path")

        # 7) show_number: thin wrapper over show_string(str(n)). 42 is two
        #    digits, so this also confirms the wrapper actually reaches the
        #    scroll path (not just the short-text path already proven in step 5).
        d.clear_screen()
        await d.show_number(42, display.GOLD, interval_ms=150)
        print("7/10: show_number(42), wrapper routes into show_string's scroll path")

        # 8) Image.show_image: windowed render of an image wider than the
        #    display, sweeping every case `_render_window`'s own docstring
        #    distinguishes (see its "Cases" table, core.py ~line 522):
        #      offset=0   : fully covered, left half (diamond)
        #      offset=3   : fully covered, in-between window straddling both
        #                    halves (still no OFF margin: 0 <= offset <= 5
        #                    keeps x_max pinned at WIDTH for this 10-wide image)
        #      offset=5   : fully covered, right half (solid block)
        #      offset=-2  : NEGATIVE offset: image partially off the *left*
        #                    edge, display columns [0, 2) render OFF
        #      offset=8   : OVERHANG past max_start (width - WIDTH = 5): image
        #                    partially off the *right* edge, display columns
        #                    [2, 5) render OFF; display can't be fully filled
        #    No `clear_screen()` between offsets needed: `_render_window`
        #    writes OFF explicitly for every uncovered column on each call.
        #    Set color to CYAN first (defensive baseline matching this cycle's
        #    own top-of-cycle rationale): step 9 below recolors the same shared
        #    Image to a different color, so this undoes that from the
        #    *previous* cycle before step 8 renders anything.
        _big_image.recolor(display.CYAN)
        for _offset in (0, 3, 5, -2, 8):
            await _big_image.show_image(offset=_offset, interval_ms=900)
            print(f"8/10: Image.show_image(offset={_offset}) rendered")
        print("8/10: Image.show_image(offset), aligned/in-between/negative/overhang windows of a 10-wide image")

        # 9) Image.scroll_image: animates the same image across its full
        #    width, one column per frame. Distinct code path from step 8
        #    (which jumps directly to a fixed offset with no animation).
        #    Recolored to PURPLE (was CYAN in step 8, via Image.recolor,
        #    which mutates the mono Image's stored color in place) purely so the two
        #    steps are visually distinguishable back-to-back; recolored back to
        #    CYAN at the top of step 8 next cycle, not here, matching the
        #    "reset at top of cycle" convention used elsewhere in this script.
        d.clear_screen()
        _big_image.recolor(display.PURPLE)
        await _big_image.scroll_image(step=1, interval_ms=250)
        print("9/10: Image.scroll_image, full-width scroll animation (PURPLE, vs. step 8's CYAN)")

        # 10) SERIAL SELF-CHECK, no visual judgment needed: it tests the
        #     cancellation-token contract every Tier-2 animation relies on
        #     (core.py's `_acquire`/`_is_cancelled`; see its module docstring).
        #     Runs a slow scroll (interval_ms=400, deliberately slower than
        #     step 9 so timing has a wide margin) concurrently with
        #     `_trigger_cancellation_after`, which waits 1s and then performs
        #     an ordinary Tier-1 write (`d.fill()`). If cancellation works, the
        #     scroll returns early: total elapsed time is well short of the
        #     scroll's own uninterrupted full-length duration. If it doesn't,
        #     elapsed time matches (or exceeds) that full length instead.
        #     Recolored to WHITE (was PURPLE in step 9), a third distinct color
        #     so this step is visually distinguishable from step 9's scroll at
        #     a glance, not just by waiting for the mid-scroll cut to RED below.
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
            print(f"10/10: cancellation check, elapsed={_elapsed:.2f}s vs interrupt-at={_interrupt_at_s:.2f}s vs uninterrupted-full-length={_full_length_s:.2f}s [{_status}]")
        except AttributeError as exc:
            # asyncio.gather (or another API this step depends on) may not exist
            # in the bundled asyncio version: surface that as data, not a crash,
            # so the rest of the cycle (and the rest of this diagnostic run) still
            # completes.
            print(f"10/10: cancellation check SKIPPED, {exc!r} (bundled asyncio API gap)")

        d.clear_screen()
        print("Cycle complete (Tier 2 async, display only; buttons deferred to a later stage).")
        await asyncio.sleep(1)


asyncio.run(main())

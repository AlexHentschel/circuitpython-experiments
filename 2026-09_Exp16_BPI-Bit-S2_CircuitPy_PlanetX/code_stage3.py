"""Round-1 LED-matrix + buttons on-device test, Stage 3 (Tier 2 + two button modules).

Additive, not repetitive: Stage 0 (minimal Tier 1), Stage 1 (broader Tier 1),
and Stage 2 (Tier 2 async, display only) are already confirmed on-device and
frozen in the sibling `code_stage0.py` / `code_stage1.py` / `code_stage2.py`.
See `CONCLUSIONS.md` (K1: bundle ``asyncio`` via this project's own Tier-2 API;
K2: PlanetX C/D wiring fires real button events). This is the **final stage
in the original 4-stage breakdown**: Tier 2 display animations running
concurrently with ``OnboardButtons.run()`` and ``planetx.PlanetXButtonSensor.run()``.

Deliberately does **not** re-individually-prove the five async ``show_*``
wrappers, ``Image.show_image``/``scroll_image``, or the timer-triggered
cancellation check. Stage 2 already did that (steps 2-10). This script
reuses ``show_string``/``scroll_image`` only as *background* animation, not
as a re-test of those code paths.

**Claim this stage discharges (K3): do `OnboardButtons` and
`PlanetXButtonSensor` — via each object's own `run()` pump, not a bypassing
PoC — dispatch real hardware events *while* a Tier-2 display animation is
concurrently in flight, and does a button-triggered Tier-1 write correctly
cancel that animation?** Two sub-parts:

  (a) K2's on-device confirmation (2026-09-11) used raw ``keypad.Keys`` +
      ``neopixel`` directly, bypassing this library, and only exercised the
      PlanetX C/D pair. This script is the first on-device use of this
      library's registration API and ``run()`` pumps, and the first
      exercise of the onboard A/B pair on this board.
  (b) Cooperative multitasking: ``ab.run()``, ``px.run()``, and the display
      animation loop are *sibling* coroutines under one ``asyncio.gather``.
      A button press fires its handler from inside that module's ``run()``,
      which then makes an ordinary Tier-1 write (``Display.render_arrow``)
      against the same module-level ``display`` singleton the animation
      coroutine is concurrently animating. This is safe without a lock
      because CircuitPython's ``asyncio`` is single-threaded and
      cooperative: coroutines only interleave at ``await`` points, so the
      shared cancellation-token counter (``Display._acquire`` /
      ``_is_cancelled``, see ``core.py``'s module docstring) cannot be
      corrupted by a data race.

Steps (numbered per cycle; steps 1-4 are autonomous-serial-capture-friendly,
no physical input needed; step 5 needs Alex present to press buttons):

  1. ``OnboardButtons()`` (defaults ``board.BUTTON_A`` / ``BUTTON_B``) and
     ``PlanetXButtonSensor(c_pin=IO13, d_pin=IO14)`` constructed as two
     objects: one Python object per physical module.
  2. Concurrency/liveness self-check, serial-only: Stage 2 step 1's
     ``asyncio.sleep(0.5)`` +/-10ms timing check, now concurrent with
     *two* 10 ms ``run()`` pumps as sibling tasks. A clean [OK] is evidence
     the pumps are not starving this coroutine.
  3. A continuous background ``Image.scroll_image`` animation, restarted
     every cycle: the long-running Tier-2 animation that step 5's button
     presses interrupt.
  4. ``show_string`` status line with live per-letter press counts (e.g.
     ``A0B0C0D0``): confirms Tier 2 keeps rendering fresh frames every
     cycle regardless of whether any button has been pressed yet.
  5. Physical button presses (A/B/C/D): each fires this library's own
     registered handler, prints a confirmation line with letter + running
     count, and renders a letter-specific arrow via an ordinary Tier-1
     write, which cancels whatever Tier-2 animation is in flight. On
     release, nothing happens: ``on_*_released`` is not exercised this
     stage (K2's on-device scope was press-only).

Looped (``asyncio.gather`` of three never-returning coroutines), for the
same reason as Stage 0-2 (a script that reaches its end falls back to the
REPL) and because both ``run()`` pumps need to keep listening indefinitely.
"""

import asyncio
import time

import board
import display
from display import Arrows

from buttons import OnboardButtons
from planetx import PlanetXButtonSensor

d = display.display

print("Stage 3: import display + buttons + planetx OK")

# Built once, not per-cycle, matching Stage 1/2's allocate-once pattern.
# One object per physical module: onboard A/B (pin defaults) and PlanetX C/D
# on the already-confirmed J3 wiring (IO13/IO14).
ab = OnboardButtons()
px = PlanetXButtonSensor(c_pin=board.IO13, d_pin=board.IO14)
print("Stage 3: OnboardButtons() + PlanetXButtonSensor(c_pin=IO13, d_pin=IO14) constructed OK")

# Background animation, built once. 10 columns x 5 rows (2 * WIDTH x HEIGHT,
# the create_big_image contract), same shape family as Stage 2's so a human
# comparing the two stages visually recognizes it as "the same kind of
# thing," just now interruptible by a real button instead of a synthetic
# timer.
_BIG_PATTERN = """
# . . . . # . . . #
. # # # . # # . . #
. # . # . # . # . #
. # # # . # . . # #
. . . . # # . . . #
"""
_big_image = display.create_big_image(_BIG_PATTERN, display.CYAN)

# Per-letter feedback: a distinct color + arrow direction so a human
# watching can tell at a glance which button just fired, purely by what
# appears on the matrix. A/B point outward (west/east) to loosely mirror
# their left/right position on the board; C/D (PlanetX, no natural
# direction) get north/south for visual distinctness from A/B and each other.
_LETTER_ARROW = {
    "a": Arrows.WEST,
    "b": Arrows.EAST,
    "c": Arrows.NORTH,
    "d": Arrows.SOUTH,
}
_LETTER_COLOR = {
    "a": display.CYAN,
    "b": display.MAGENTA,
    "c": display.GREEN,
    "d": display.GOLD,
}

class _PressCounter:
    """Stateful, per-letter press handler.

    Each instance owns its own ``letter`` and running ``count`` as plain
    instance attributes. A callable instance satisfies the
    ``Callable[[], None]`` handler contract exactly like a function would:
    ``__call__`` takes no arguments beyond ``self``. Sync only: no ``await``
    inside ``__call__``, matching every other handler in this file.

    Safe without a lock even though four instances all end up calling
    ``d.render_arrow(...)``: CircuitPython asyncio is single-threaded and
    cooperative (see module docstring, part (b)). A handler only ever runs
    to completion between two ``await`` points, never concurrently with the
    display loop's own writes. Each instance's ``count`` is private to that
    instance; the only thing shared between letters is ``d`` itself.
    """

    def __init__(self, letter: str) -> None:
        self.letter = letter
        self.count = 0

    def __call__(self) -> None:
        self.count += 1
        print(
            f"BUTTON {self.letter.upper()} pressed (count={self.count}) — "
            f"library handler dispatch confirmed, not the bypassing keypad PoC K2 used"
        )
        # Ordinary Tier-1 write, fired from inside that module's ``run()``
        # coroutine: the interrupting event for whatever Tier-2 animation
        # the display loop below is currently mid-flight on (see module
        # docstring part (b); the real-event counterpart to Stage 2 step 10's
        # synthetic-timer cancellation check).
        d.render_arrow(_LETTER_ARROW[self.letter], _LETTER_COLOR[self.letter])


# One counter object per letter, registered explicitly by name: a typo here
# is a NameError/AttributeError at read time, not a silent no-op at runtime.
# Matches the MakeCode screenshot's idiom of one distinctly-named handler
# wired individually per event, now on the module that owns that letter.
press_a = _PressCounter("a")
press_b = _PressCounter("b")
press_c = _PressCounter("c")
press_d = _PressCounter("d")
ab.on_a_pressed(press_a)
ab.on_b_pressed(press_b)
px.on_c_pressed(press_c)
px.on_d_pressed(press_d)
print("Stage 3: on_a/b_pressed + on_c/d_pressed handlers registered")


async def _display_loop() -> None:
    cycle = 0
    while True:
        cycle += 1
        # Defensive baseline at the top of every cycle, matching Stage 0-2:
        # keeps every cycle's starting state independent of what a future
        # added step might leave behind.
        d.set_rotation(0)
        d.set_brightness(0.10)  # matches Alex's live override on Stage 2's code.py
        print(f"\n=== cycle {cycle} ===")

        # 1) Construction + handler registration already happened above.

        # 2) Concurrency/liveness self-check (K3): identical tolerance check
        #    to Stage 2 step 1, concurrent with both module pumps rather than
        #    sequentially beforehand. A clean [OK] here is evidence that the
        #    10 ms polling loops are not starving this coroutine.
        _sleep_target_s = 0.5
        _tolerance_s = 0.010
        _t0 = time.monotonic()
        await asyncio.sleep(_sleep_target_s)
        _elapsed = time.monotonic() - _t0
        _timing_deviation = abs(_elapsed - _sleep_target_s)
        _status = "OK" if _timing_deviation <= _tolerance_s else "MISMATCH"
        print(
            f"2/4: asyncio.sleep({_sleep_target_s}) returned after {_elapsed:.4f}s "
            f"(deviation={_timing_deviation * 1000:.1f}ms, tolerance=+/-{_tolerance_s * 1000:.0f}ms) [{_status}] "
            f"(concurrent with OnboardButtons.run() + PlanetXButtonSensor.run(), K3 liveness check)"
        )

        # 3) Continuous background animation: the long-running Tier-2 op that
        #    step 5 (a physical button press, whenever it happens) interrupts.
        #    Restarted fresh every cycle, matching the "reset at top of cycle"
        #    convention used throughout this test series.
        d.clear_screen()
        _big_image.recolor(display.CYAN)
        await _big_image.scroll_image(step=1, interval_ms=300)
        print("3/4: Image.scroll_image, background animation (press any button to interrupt it)")

        # 4) Status line: live per-letter press counts, confirming Tier 2
        #    keeps rendering fresh frames every cycle regardless of whether
        #    any button has fired yet. Compact, no spaces, to keep the scroll
        #    short (show_string's scroll path was already proven by Stage 2;
        #    this is not re-testing it, just using it).
        _status_line = f"A{press_a.count}B{press_b.count}C{press_c.count}D{press_d.count}"
        await d.show_string(_status_line, display.WHITE, interval_ms=150)
        print(f"4/4: show_string('{_status_line}'), live press-count status")

        print("Cycle complete. Press A, B, C, or D any time; watch the arrow flash and the animation cut short.")
        await asyncio.sleep(1)


async def main() -> None:
    # Three sibling coroutines, none of which ever return: each module's
    # ``run()`` drains that module's hardware queue forever; ``_display_loop()``
    # animates forever. ``asyncio.gather`` on never-ending coroutines is the
    # "run concurrently, forever" shape this stage's claim needs. ``gather``
    # itself was already confirmed on this device's bundled asyncio by Stage 2
    # step 10.
    await asyncio.gather(ab.run(), px.run(), _display_loop())


asyncio.run(main())

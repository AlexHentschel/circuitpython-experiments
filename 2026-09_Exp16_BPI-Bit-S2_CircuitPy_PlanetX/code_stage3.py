"""Round-1 LED-matrix + buttons on-device test, Stage 3 (Tier 2 + two button modules).

``OnboardButtons.run()`` and ``PlanetXButtonSensor.run()`` deliver press
events while a display loop scrolls an image, then a short status string.
A press handler calls ``Display.render_arrow``, which cancels whichever
Tier-2 animation is in flight.

Stage 2 walked the five async ``show_*`` wrappers, ``Image.show_image`` /
``scroll_image``, and the timer-triggered cancellation check (steps 2-10).
We assume that works, and use ``show_string`` / ``scroll_image`` here as the
background animation.

  (a) Each module owns its scanner. ``run()`` is the coroutine that keeps
      reading that scanner and calling the handler for the button that was
      pressed.
      ``OnboardButtons()`` exposes ``button_a`` / ``button_b`` (defaults
      ``board.BUTTON_A`` / ``board.BUTTON_B``). ``PlanetXButtonSensor(port=J3)``
      exposes ``button_c`` / ``button_d`` (J3 is edge-connector P13/P14,
      ``board.IO13`` / ``board.IO14``). Handlers register with ``.on_pressed``.
      Release handlers are not registered.

  (b) ``ab.run()`` (onboard buttons A/B), ``px.run()`` (PlanetX buttons
      C/D on J3), and the display loop are sibling coroutines under one
      ``asyncio.gather``. A press handler runs inside that module's
      ``run()`` and writes the same ``display`` object the animation coroutine
      uses. CircuitPython asyncio is single-threaded and cooperative:
      coroutines interleave only at ``await``, so ``Display._acquire`` /
      ``_is_cancelled`` (see ``core.py``) is not updated from two places at once.

What runs:

  1. Construct both modules and register one press handler per letter.
  2. Each cycle, ``asyncio.sleep(0.5)`` while both ``run()`` coroutines
     are running. Serial prints elapsed time and ``[OK]`` when it is
     within +/-10 ms.
  3. ``Image.scroll_image`` — the long animation a press can cut short.
     Restarted every cycle, after rotation 0 and brightness 0.10.
  4. ``show_string`` of the press counts (``A0B0C0D0``). No spaces, so the
     scroll stays short.
  5. A press increments that letter's count, prints it, and renders that
     letter's arrow. Presses are delivered whenever those coroutines are
     running, including during steps 2-4.

The three tasks do not return, so both ``run()`` coroutines keep
listening and the script does not fall through to the REPL.
"""

import asyncio
import time

import display
from display import Arrows

from buttons import OnboardButtons
from planetx import PlanetXButtonSensor, J3

d = display.display

print("Stage 3: import display + buttons + planetx OK")

# Built once, not per cycle. Onboard A/B use pin defaults; PlanetX C/D use J3.
ab = OnboardButtons()
px = PlanetXButtonSensor(port=J3)
print("Stage 3: OnboardButtons() + PlanetXButtonSensor(port=J3) constructed OK")

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
            f"BUTTON {self.letter.upper()} pressed (count={self.count})"
        )
        # Tier-1 write from inside that module's ``run()``. Cancels whatever
        # Tier-2 animation the display loop is in the middle of.
        d.render_arrow(_LETTER_ARROW[self.letter], _LETTER_COLOR[self.letter])


# One counter object per letter, registered explicitly by name: a typo here
# is a NameError/AttributeError at read time, not a silent no-op at runtime.
# Matches the MakeCode screenshot's idiom of one distinctly-named handler
# wired individually per event, now on the module that owns that letter.
press_a = _PressCounter("a")
press_b = _PressCounter("b")
press_c = _PressCounter("c")
press_d = _PressCounter("d")
ab.button_a.on_pressed(press_a)
ab.button_b.on_pressed(press_b)
px.button_c.on_pressed(press_c)
px.button_d.on_pressed(press_d)
print("Stage 3: button_a/b and button_c/d press handlers registered")


async def _display_loop() -> None:
    cycle = 0
    while True:
        cycle += 1
        # Each cycle starts from the same rotation and brightness, independent
        # of what the previous cycle's animation or a press left on screen (matching Stage 0-2).
        d.set_rotation(0)
        d.set_brightness(0.10)  # dimmer than the library default 0.20
        print(f"\n=== cycle {cycle} ===")

        # 1) Construction + handler registration already happened above.

        # 2) Sleep 0.5 s while both run() coroutines are already running.
        #    [OK] means the elapsed time stayed within 10 ms, so those
        #    coroutines did not starve this one.
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
            f"(concurrent with OnboardButtons.run() + PlanetXButtonSensor.run())"
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

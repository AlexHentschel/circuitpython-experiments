"""Round-1 LED-matrix + buttons on-device test, Stage 3 (Tier 2 + two button modules).

``OnboardButtons.run()`` and ``PlanetXButtonSensor.run()`` deliver button events while a display loop scrolls an image, then a short status string.
A handler calls ``Display.render_arrow``, which takes over the display and expires the running token. A and B do this on press. C and D do it on release.

Stage 2 walked the async display calls, including a timer-triggered takeover. This stage assumes that works.

  (a) Each button owns its scanner. That button's ``run()`` keeps reading the scanner and calling the one handler registered for the press or the release.
      ``OnboardButtons.run()`` runs A and B together. ``PlanetXButtonSensor.run()`` runs C and D together.
      ``OnboardButtons()`` exposes ``button_a`` / ``button_b`` (defaults ``board.BUTTON_A`` / ``board.BUTTON_B``).
      ``PlanetXButtonSensor(port=J3)`` exposes ``button_c`` / ``button_d`` (J3 is edge-connector P13/P14, ``board.IO13`` / ``board.IO14``).
      A and B register with ``.on_pressed``. C and D register with ``.on_released`` but otherwise run that same count-and-arrow action.
      A later ``on_pressed`` on the same button replaces that button's press handler (analogously for ``on_released``).

  (b) ``ab.run()`` (onboard buttons A/B), ``px.run()`` (PlanetX buttons C/D on J3), and the display loop are sibling coroutines under one ``asyncio.gather``.
      The handler runs inside that button's ``run()`` and writes the same ``display`` object the animation coroutine uses. CircuitPython asyncio
      is single-threaded and cooperative: coroutines interleave only at ``await``, so the display token is not updated from two places at once.

Maintainer checklist:

  1. Construct both button modules. Register a press handler for A and B, and a release handler for C and D. Happens once, before the cycle loop.
  2. Each cycle, ``asyncio.sleep(0.5)`` while both ``run()`` coroutines are running. ``[OK]`` when elapsed time is within +/-10 ms.
  3. Idle scroll. With ``_IDLE = "loop"`` (the default): ``token = await scroll_image(..., interval_ms=300, loop=True)``.
     A press of A or B, or a release of C or D, ends it. Then ``while token.is_expired: token = await hold(800)``.
     The arrow stays up. A later one of those events starts that 800 ms wait over.
     With ``_IDLE = "repeat"``: ``repeat_until_cancelled`` of one ``scroll_image`` pass. Those events do not end it (the next pass draws over the arrow).
     Step 4 does not run in this mode.
  4. ``scroll_string`` of the counts (``A0B0C0D0``). The marquee ends on a blank screen. A press of A or B, or a release of C or D, can cut it short.
     The arrow then stays until the next cycle clears the display.
  5. A press of A or B, or a release of C or D, increments that letter's count, prints it, and renders that letter's arrow.
     Those events are delivered whenever those coroutines are running, including during steps 2-4.

There is no ``step`` argument. ``hold`` keeps the current frame and does not wipe. ``scroll_image`` / ``scroll_string`` take ``interval_ms``.

The three tasks do not return, so both ``run()`` coroutines keep listening and the script does not fall through to the REPL.
"""

import asyncio
import time

import display
from display import Arrows

from buttons import OnboardButtons
from planetx import PlanetXButtonSensor, J3

time.sleep(5)

d = display.display

# "loop": a press of A or B, or a release of C or D, ends the idle scroll, then step 4 runs.
# "repeat": those events do not end the scroll. Step 4 does not run.
_IDLE = "loop"
# _IDLE = "repeat"

print("Stage 3: import display + buttons + planetx OK")

ab = OnboardButtons()
px = PlanetXButtonSensor(port=J3)
print("Stage 3: OnboardButtons() + PlanetXButtonSensor(port=J3) constructed OK")

_BIG_PATTERN = """
# . . . . # . . . #
. # # # . # # . . #
. # . # . # . # . #
. # # # . # . . # #
. . . . # # . . . #
"""
_big_image = display.Image(_BIG_PATTERN, display.CYAN)

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

# How long the arrow stays up after a press of A or B, or a release of C or D, ends the idle scroll.
# A later one of those events starts this wait over.
_ARROW_HOLD_MS = 800


class ButtonCounter:
    """Stateful, per-letter handler for one button event.

    ``__call__`` takes no arguments beyond ``self``. Sync only: no ``await``
    inside ``__call__``. ``event`` is the word printed for that event.
    """

    def __init__(self, letter: str, event: str = "pressed") -> None:
        self.letter = letter
        self.event = event
        self.count = 0

    def __call__(self) -> None:
        self.count += 1
        print(f"BUTTON {self.letter.upper()} {self.event} (count={self.count})")
        d.render_arrow(_LETTER_ARROW[self.letter], _LETTER_COLOR[self.letter], start_col=0)


press_a = ButtonCounter("a")
press_b = ButtonCounter("b")
press_c = ButtonCounter("c", "released")
press_d = ButtonCounter("d", "released")
ab.button_a.on_pressed(press_a)
ab.button_b.on_pressed(press_b)
px.button_c.on_released(press_c)
px.button_d.on_released(press_d)
print("Stage 3: A/B press handlers and C/D release handlers registered")


async def _one_image_pass() -> None:
    """One ``scroll_image`` pass, for the ``repeat_until_cancelled`` contrast."""
    await d.scroll_image(_big_image, interval_ms=300)


async def _display_loop() -> None:
    cycle = 0
    while True:
        cycle += 1
        d.clear()
        d.set_rotation(0)
        d.set_brightness(0.10)
        print(f"\n=== cycle {cycle} idle={_IDLE!r} ===")

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

        d.clear()
        _big_image.recolor(display.CYAN)
        if _IDLE == "repeat":
            print("3/4: repeat_until_cancelled(scroll_image). A press does not end this. Step 4 does not run.")
            await d.repeat_until_cancelled(_one_image_pass)
        else:
            token = await d.scroll_image(_big_image, interval_ms=300, loop=True)
            while token.is_expired:
                token = await d.hold(_ARROW_HOLD_MS)
            print("3/4: scroll_image(loop=True). A press keeps its arrow up for 800 ms, restarted by a later press.")

            _status_line = f"A{press_a.count}B{press_b.count}C{press_c.count}D{press_d.count}"
            await d.scroll_string(_status_line, display.WHITE, interval_ms=150)
            print(f"4/4: scroll_string('{_status_line}'), live press-count status")

            print("Cycle complete. Press A, B, C, or D any time; watch the arrow and the scroll cut short.")
            await asyncio.sleep(1)


async def main() -> None:
    await asyncio.gather(ab.run(), px.run(), _display_loop())


asyncio.run(main())

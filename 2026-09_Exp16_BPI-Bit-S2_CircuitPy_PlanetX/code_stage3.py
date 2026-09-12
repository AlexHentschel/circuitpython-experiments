"""Round-1 LED-matrix + buttons on-device test, Stage 3 (Tier 2 + buttons combined).

Additive, not repetitive: Stage 0 (minimal Tier 1), Stage 1 (broader Tier 1),
and Stage 2 (Tier 2 async, display only) are already confirmed on-device and
frozen in the sibling `code_stage0.py` / `code_stage1.py` / `code_stage2.py`
-- see `CONCLUSIONS.md` for their findings (K1: bundle ``asyncio`` works via
this project's own Tier-2 API; K2: PlanetX C/D wiring fires real button
events). This is the **final stage in the original 4-stage breakdown**: Tier
2 display animations and ``lib/buttons.py``'s async button dispatcher,
running together as two concurrent tasks under one event loop.

Deliberately does **not** re-individually-prove the five async ``show_*``
wrappers, ``Image.show_image``/``scroll_image``, or the timer-triggered
cancellation check -- Stage 2 already did that (steps 2-10). This script
reuses ``show_string``/``scroll_image`` only as *background* animation, not
as a re-test of those code paths.

**New claim this stage discharges (call it K3): does `lib/buttons.py`'s
`Buttons` class -- via its own `run()` pump, not a bypassing PoC -- actually
dispatch real hardware button events *while* a Tier-2 display animation is
concurrently in flight, and does a button-triggered Tier-1 write correctly
cancel that animation?** Two sub-parts:

  (a) K2's on-device confirmation (2026-09-11) used raw ``keypad.Keys`` +
      ``neopixel`` directly, bypassing this library entirely, and only
      exercised the PlanetX C/D pair. Nothing has yet run *this library's*
      ``Buttons`` class, its ``on_*_pressed`` registration API, or its
      ``run()`` pump on real hardware -- and the onboard A/B buttons have
      never been touched on this board at all. This script is the first
      test of both.
  (b) The interesting new mechanism, beyond "buttons work" and "Tier 2
      animations work" each in isolation (both already proven separately):
      ``Buttons.run()`` and the display animation loop below are two
      *sibling* coroutines under one ``asyncio.gather``, not a sequential
      await chain. A button press fires its handler *from inside*
      ``Buttons.run()``'s own coroutine, which then makes an ordinary
      Tier-1 write (``Display.render_arrow``) against the same
      module-level ``display`` singleton the animation coroutine is
      concurrently animating. This only works safely without a lock
      because CircuitPython's ``asyncio`` is single-threaded and
      cooperative: the two coroutines only ever interleave at ``await``
      points, never truly in parallel, so the shared cancellation-token
      counter (``Display._acquire``/``_is_cancelled``, see ``core.py``'s
      module docstring) can't be corrupted by a data race. If this works,
      it demonstrates the actual claim the whole project is testing:
      genuine cooperative multitasking between an input source and an
      animation, not just "asyncio runs" (K1) or "buttons fire" (K2) each
      alone.

Steps (numbered per cycle; steps 1-4 are autonomous-serial-capture-friendly
-- no physical input needed to observe them printing cleanly; step 5 needs
Alex physically present to press buttons, matching every prior stage's
"needs a human live" bar, just for physical interaction instead of visual
judgment this time):

  1. ``Buttons(...)`` construction with all four real pins (onboard
     ``board.BUTTON_A``/``BUTTON_B`` + PlanetX ``board.IO13``/``IO14`` for
     C/D) -- ``Buttons.__init__`` requires all four when ``event_queue`` is
     omitted, so this is also the first on-device use of the onboard pair.
  2. Concurrency/liveness self-check, serial-only: repeats Stage 2 step 1's
     exact ``asyncio.sleep(0.5)`` +/-10ms timing check, but this time with
     ``Buttons.run()`` concurrently active as a sibling task (not run
     sequentially beforehand). If ``Buttons.run()``'s tight
     ``await asyncio.sleep(0)`` polling loop were starving the event loop,
     this timing check would drift outside tolerance -- passing is direct
     evidence the two tasks genuinely share the loop cooperatively.
  3. A continuous background ``Image.scroll_image`` animation, restarted
     every cycle -- the long-running Tier-2 animation that step 5's button
     presses interrupt.
  4. ``show_string`` status line with live per-letter press counts (e.g.
     ``A0B0C0D0``) -- confirms Tier 2 keeps rendering fresh frames every
     cycle regardless of whether any button has been pressed yet.
  5. Physical button presses (A/B/C/D): each fires this library's own
     registered handler (proving the dispatch path end-to-end, not just
     that the GPIO electrically works per K2), prints a confirmation line
     with letter + running count, and renders a letter-specific arrow via
     an ordinary Tier-1 write -- which cancels whatever Tier-2 animation
     (step 3's scroll or step 4's status line) is currently in flight. On
     release, nothing happens: ``on_*_released`` is intentionally not
     exercised this stage (K2's own on-device scope was press-only; adding
     release handling here would be new, unverified surface, not this
     stage's claim).

Looped (``asyncio.gather`` of two never-returning coroutines), for the same
reason as Stage 0-2 -- a script that reaches its end falls back to the REPL
and stops producing output -- but this time the looping is also load-bearing
for a second reason: ``Buttons.run()`` needs to keep listening indefinitely
for this stage to mean anything at all.
"""

import asyncio
import time

import board
import display
from display import Arrows

from buttons import Buttons

d = display.display

print("Stage 3: import display + buttons OK")

# Built once, not per-cycle, matching Stage 1/2's own allocate-once pattern.
# All four pins required together (Buttons.__init__ raises ValueError if any
# of a_pin/b_pin/c_pin/d_pin is None when event_queue is omitted) -- this is
# the first on-device use of the onboard A/B pair in this test series; C/D
# repeats K2's already-confirmed PlanetX wiring, now through this library's
# own Buttons class instead of the bypassing keypad+neopixel PoC.
buttons = Buttons(
    a_pin=board.BUTTON_A,
    b_pin=board.BUTTON_B,
    c_pin=board.IO13,
    d_pin=board.IO14,
)
print("Stage 3: Buttons(a_pin=BUTTON_A, b_pin=BUTTON_B, c_pin=IO13, d_pin=IO14) constructed OK")

# Background animation, built once. 10 columns x 5 rows (2 * WIDTH x HEIGHT,
# the create_big_image contract), same shape family as Stage 2's so a human
# comparing the two stages visually recognizes it as "the same kind of
# thing," just now interruptible by a real button instead of a synthetic
# timer.
_BIG_PATTERN = """
. . # . . # # # # #
. # # # . # # # # #
# # # # # # # # # #
. # # # . # # # # #
. . # . . # # # # #
"""
_big_image = display.create_big_image(_BIG_PATTERN, display.CYAN)

# Per-letter feedback: a distinct color + arrow direction so a human
# watching can tell at a glance which button just fired, purely by what
# appears on the matrix -- no need to read the serial log to know which
# button was pressed. A/B point outward (west/east) to loosely mirror their
# left/right position on the board; C/D (PlanetX, no natural direction) get
# north/south arbitrarily, just for visual distinctness from A/B and from
# each other.
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

# Shared, mutable, module-level state read by the display loop and written
# by the button handlers below. Safe without a lock: CircuitPython asyncio
# is single-threaded and cooperative (see module docstring, part (b)) -- the
# handlers only ever run between awaits, never while the display loop is
# mid-write. A dict (mutated, not rebound) sidesteps needing `global` inside
# the handler closures.
_state = {"counts": {"a": 0, "b": 0, "c": 0, "d": 0}, "last": None}


def _make_on_pressed(letter: str):
    """Build the pressed-handler for one letter, closing over it by value.

    A plain sync callable, matching ``Buttons``'s ``Callable[[], None]``
    contract -- handlers are not coroutines, so only Tier-1 (sync) display
    calls belong here, never ``await``.
    """

    def _handler() -> None:
        _state["counts"][letter] += 1
        _state["last"] = letter
        print(
            f"BUTTON {letter.upper()} pressed (count={_state['counts'][letter]}) -- "
            f"Buttons.run() dispatch confirmed via this library's own handler "
            f"registration, not the bypassing keypad PoC K2 used"
        )
        # Ordinary Tier-1 write, fired from inside Buttons.run()'s coroutine:
        # this is the interrupting event for whatever Tier-2 animation the
        # display loop below is currently mid-flight on (see module docstring
        # part (b); the real-event counterpart to Stage 2 step 10's
        # synthetic-timer cancellation check).
        d.render_arrow(_LETTER_ARROW[letter], _LETTER_COLOR[letter])

    return _handler


for _letter in ("a", "b", "c", "d"):
    getattr(buttons, f"on_{_letter}_pressed")(_make_on_pressed(_letter))
print("Stage 3: on_a/b/c/d_pressed handlers registered")


async def _display_loop() -> None:
    cycle = 0
    while True:
        cycle += 1
        # Defensive baseline at the top of every cycle, matching Stage 0-2's
        # own rationale: keeps every cycle's starting state independent of
        # what a future added step might leave behind.
        d.set_rotation(0)
        d.set_brightness(0.10)  # matches Alex's live override on Stage 2's code.py
        print(f"\n=== cycle {cycle} ===")

        # 1) Buttons() construction + handler registration already happened
        #    above, once, before this loop started -- printed OK already.

        # 2) Concurrency/liveness self-check (K3): identical tolerance check to
        #    Stage 2 step 1, but now running concurrently with Buttons.run()
        #    as a sibling task rather than sequentially beforehand. A clean
        #    [OK] here is direct evidence that the tight polling loop inside
        #    Buttons.run() (`await asyncio.sleep(0)`) is not starving this
        #    coroutine's own scheduling.
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
            f"(concurrent with Buttons.run(), K3 liveness check)"
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
        _counts = _state["counts"]
        _status_line = f"A{_counts['a']}B{_counts['b']}C{_counts['c']}D{_counts['d']}"
        await d.show_string(_status_line, display.WHITE, interval_ms=150)
        print(f"4/4: show_string('{_status_line}'), live press-count status")

        print(
            "Cycle complete. Press A, B, C, or D any time -- watch the arrow flash "
            "and the animation cut short."
        )
        await asyncio.sleep(1)


async def main() -> None:
    # Two sibling coroutines, neither of which ever returns: Buttons.run()
    # drains the real hardware event queue forever; _display_loop() animates
    # forever. asyncio.gather on two never-ending coroutines is exactly the
    # "run both concurrently, forever" shape this stage's claim needs --
    # gather itself was already confirmed working on this device's bundled
    # asyncio by Stage 2 step 10.
    await asyncio.gather(buttons.run(), _display_loop())


asyncio.run(main())

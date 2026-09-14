"""
Async A/B/C/D button dispatcher for PlanetX + onboard buttons.

Student-facing operations are press handlers by letter. GPIO identities
belong on the constructor (portability seam), not inside handlers.

Device backend: CircuitPython ``keypad.Keys`` (active-low, pull-up) → native
EventQueue → this dispatcher → an asyncio pump (``run``). Host tests inject
a fake queue with the CircuitPython Event shape (``.key_number``, ``.pressed``).

There is no student ``update()`` loop. Do not wrap Exp09 ``elecfreaks_planetx.Button``.
"""

from __future__ import annotations

try:
    from typing import Callable
except ImportError:
    pass


_LETTERS = ("a", "b", "c", "d")

# `run()`'s poll interval -- see its own docstring for why this is not `0`.
# Half of keypad.Keys' own default scan `interval` (0.02s / 20ms), so no
# event can be missed for longer than one hardware scan cycle would already
# impose.
_POLL_INTERVAL_S = 0.01


class Buttons:
    """Register press/release handlers for buttons A, B, C, and D.

    ``a_pin`` / ``b_pin`` / ``c_pin`` / ``d_pin`` are constructor config.
    Overnight host tests pass ``event_queue=`` and skip ``keypad``.
    """

    def __init__(
        self,
        a_pin=None,
        b_pin=None,
        c_pin=None,
        d_pin=None,
        *,
        event_queue=None,
    ) -> None:
        self._handlers = {
            letter: {"pressed": [], "released": []} for letter in _LETTERS
        }
        if event_queue is not None:
            self._queue = event_queue
            return
        # Device path -- keypad is a CircuitPython firmware module (P8 confirm).
        # TODO(P8): on-device help("modules") + PlanetX cable on IO13/IO14.
        import keypad  # CircuitPython-only; not Blinka-on-CPython

        pins = (a_pin, b_pin, c_pin, d_pin)
        if any(p is None for p in pins):
            raise ValueError("a_pin, b_pin, c_pin, d_pin are required when event_queue is omitted")
        self._keys = keypad.Keys(pins, value_when_pressed=False, pull=True)  # unread on purpose: owns the scanner; EventQueue does not keep Keys alive
        self._queue = self._keys.events

    def on_a_pressed(self, handler: Callable[[], None]) -> None:
        self._handlers["a"]["pressed"].append(handler)

    def on_b_pressed(self, handler: Callable[[], None]) -> None:
        self._handlers["b"]["pressed"].append(handler)

    def on_c_pressed(self, handler: Callable[[], None]) -> None:
        self._handlers["c"]["pressed"].append(handler)

    def on_d_pressed(self, handler: Callable[[], None]) -> None:
        self._handlers["d"]["pressed"].append(handler)

    def on_a_released(self, handler: Callable[[], None]) -> None:
        self._handlers["a"]["released"].append(handler)

    def on_b_released(self, handler: Callable[[], None]) -> None:
        self._handlers["b"]["released"].append(handler)

    def on_c_released(self, handler: Callable[[], None]) -> None:
        self._handlers["c"]["released"].append(handler)

    def on_d_released(self, handler: Callable[[], None]) -> None:
        self._handlers["d"]["released"].append(handler)

    def clear_a(self) -> None:
        self._handlers["a"] = {"pressed": [], "released": []}

    def clear_b(self) -> None:
        self._handlers["b"] = {"pressed": [], "released": []}

    def clear_c(self) -> None:
        self._handlers["c"] = {"pressed": [], "released": []}

    def clear_d(self) -> None:
        self._handlers["d"] = {"pressed": [], "released": []}

    def clear(self) -> None:
        """Drop all registered handlers for A/B/C/D."""
        for letter in _LETTERS:
            self._handlers[letter] = {"pressed": [], "released": []}

    def _dispatch(self, event) -> None:
        # `_LETTERS[event.key_number]` directly, not a separate index->letter
        # dict -- `event.key_number` is a tuple position, and `_LETTERS` is
        # already ordered to match the pins tuple built in `__init__`. Bounds
        # -checked explicitly (not a bare try/except IndexError) because a
        # negative key_number would otherwise silently wrap to a *valid*
        # tuple element instead of being rejected.
        index = event.key_number
        letter = _LETTERS[index] if 0 <= index < len(_LETTERS) else None
        if letter is None:
            return
        kind = "pressed" if event.pressed else "released"
        for handler in self._handlers[letter][kind]:
            handler()

    async def run(self) -> None:
        """Asyncio pump: drain the EventQueue and fire registered handlers.

        Student sketches ``await buttons.run()`` (typically as a background
        task alongside display animations). Host CPython ``asyncio`` here is
        the test stand-in; the CIRCUITPY bundle ``asyncio`` is a different
        library (K1 / P8).

        Poll interval is ``_POLL_INTERVAL_S`` (10 ms), not ``0``. ``0`` is not
        just "less aggressive" -- on the bundle ``asyncio`` this loop runs on
        device, ``asyncio.sleep(0)`` re-queues this task with a ready time of
        *now*, so whenever it is the only ready task (i.e. whenever the
        display task is itself mid-sleep between frames) the scheduler's
        `run_until_complete` loop never takes its blocking-poll fallback
        (``dt == 0`` skips ``_io_queue.wait_io_event(dt)``) -- a genuine
        100%-CPU busy-spin, not merely "polls a bit more than needed". A
        positive interval lets the scheduler actually block until it elapses.
        10 ms costs nothing in responsiveness: ``keypad.Keys``' own hardware
        scan/debounce runs in the background at its own ``interval``
        (default 20 ms, independent of when Python calls ``.get()``) -- new
        events cannot physically appear faster than that regardless of how
        often this loop polls, so polling faster than ~20 ms only spins the
        CPU checking an EventQueue that cannot have changed yet.
        """
        import asyncio

        while True:
            event = self._queue.get()
            if event is not None:
                self._dispatch(event)
            await asyncio.sleep(_POLL_INTERVAL_S)

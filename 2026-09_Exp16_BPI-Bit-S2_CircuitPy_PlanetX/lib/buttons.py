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
        self._index_to_letter = {i: letter for i, letter in enumerate(_LETTERS)}
        self._keys = None
        if event_queue is not None:
            self._queue = event_queue
            return
        # Device path -- keypad is a CircuitPython firmware module (P8 confirm).
        # TODO(P8): on-device help("modules") + PlanetX cable on IO13/IO14.
        import keypad  # CircuitPython-only; not Blinka-on-CPython

        pins = (a_pin, b_pin, c_pin, d_pin)
        if any(p is None for p in pins):
            raise ValueError("a_pin, b_pin, c_pin, d_pin are required when event_queue is omitted")
        self._keys = keypad.Keys(pins, value_when_pressed=False, pull=True)
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
        letter = self._index_to_letter.get(event.key_number)
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
        """
        import asyncio

        while True:
            event = self._queue.get()
            if event is not None:
                self._dispatch(event)
            await asyncio.sleep(0)

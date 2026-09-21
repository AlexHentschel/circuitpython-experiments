"""Asynchronous library for physical buttons. One Python object per physical
button module, each registering press/release handlers directly (no polling).

Register handlers, then run the object's ``run()`` forever as a background task:

    import asyncio
    from buttons import OnboardButtons

    async def main():
        buttons = OnboardButtons()
        buttons.button_a.on_pressed(lambda: print("A pressed"))
        await buttons.run()

    asyncio.run(main())

To run other work (e.g. a display animation) at the same time, gather the
tasks instead of awaiting ``run()`` alone:
``await asyncio.gather(buttons.run(), display_loop())``.

GPIO pins are constructor arguments only, never referenced inside a handler —
so swapping which physical pin a button uses is a one-line change at
construction, not a hunt through handler code. There is no ``update()``
method to call in a loop; all event delivery happens through ``run()``.

``Button`` is one GPIO pin. ``OnboardButtons`` (A/B) is this board's native
button pair. PlanetX sensor modules (C/D, etc.) live in the ``planetx``
package.
"""

from __future__ import annotations

try:
    from typing import Callable
except ImportError:
    pass


# `run()`'s poll interval: see `_pump` for why this is not `0`.
# Half of keypad.Keys' own default scan `interval` (0.02s / 20ms), so no
# event can be missed for longer than one hardware scan cycle would already
# impose.
_POLL_INTERVAL_S = 0.01


def _bind_scanner(owner, pins) -> None:
    """Attach a ``keypad.Keys`` scanner for ``pins`` onto ``owner``.

    Device path: ``keypad.Keys`` (active-low, pull-up) → native EventQueue on
    ``owner``. ``import keypad`` lives here so a host ``import buttons`` does
    not load it (tests pass ``event_queue=`` and never call this). Each
    device-path construct runs the statement; after the first it is a
    ``sys.modules`` lookup. Bind is once per physical module at construct time,
    not per event.
    """
    import keypad  # CircuitPython-only; not Blinka-on-CPython

    owner._keys = keypad.Keys(pins, value_when_pressed=False, pull=True)  # unread on purpose: owns the scanner; EventQueue does not keep Keys alive
    owner._queue = owner._keys.events


async def _pump(queue, dispatch) -> None:
    """Drain ``queue`` and call ``dispatch(event)`` until cancelled.

    Host CPython ``asyncio`` here is the test stand-in; the CIRCUITPY bundle
    ``asyncio`` is a different library.

    Poll interval is ``_POLL_INTERVAL_S`` (10 ms), not ``0``. On the bundle
    ``asyncio`` this loop runs on device, ``asyncio.sleep(0)`` re-queues this
    task with a ready time of *now*, so whenever it is the only ready task
    (whenever the display task is itself mid-sleep between frames) the
    scheduler's `run_until_complete` loop never takes its blocking-poll
    fallback (``dt == 0`` skips ``_io_queue.wait_io_event(dt)``): a genuine
    100%-CPU busy-spin, not merely "polls a bit more than needed". A positive
    interval lets the scheduler actually block until it elapses.

    10 ms costs nothing in responsiveness: ``keypad.Keys``' own hardware
    scan/debounce runs in the background at its own ``interval`` (default
    20 ms, independent of when Python calls ``.get()``). New events cannot
    physically appear faster than that regardless of how often this loop
    polls, so polling faster than ~20 ms only spins the CPU checking an
    EventQueue that cannot have changed yet.
    """
    import asyncio

    while True:
        event = queue.get()
        # Deliberately no await between dispatches: this drains the whole buffered
        # burst before yielding once below. keypad.Keys' own scan caps new events at
        # ~1 per 20 ms, so a same-tick burst worth yielding *inside* is not something
        # real hardware produces; adding a yield here would spread a burst's events
        # across multiple ticks instead (considered and rejected 2026-09-20).
        while event is not None:
            dispatch(event)
            event = queue.get()
        await asyncio.sleep(_POLL_INTERVAL_S)


class PushButtonBase:
    """Press and release handlers for one switch.

    Register with ``on_pressed`` / ``on_released``; ``clear`` (or the finer
    ``clear_pressed`` / ``clear_released``) removes them again. This object
    has no ``run()`` of its own — call ``run()`` on the owning button object
    instead (e.g. ``Button``, ``OnboardButtons``).
    """

    def __init__(self) -> None:
        """Start with no handlers registered."""
        self._pressed = []
        self._released = []

    def on_pressed(self, handler: Callable[[], None]) -> None:
        """Call ``handler()`` (no arguments) every time this switch is pressed."""
        self._pressed.append(handler)

    def on_released(self, handler: Callable[[], None]) -> None:
        """Call ``handler()`` (no arguments) every time this switch is released."""
        self._released.append(handler)

    def clear_pressed(self) -> None:
        """Drop all press handlers; leave release handlers."""
        self._pressed = []

    def clear_released(self) -> None:
        """Drop all release handlers; leave press handlers."""
        self._released = []

    def clear(self) -> None:
        """Drop all registered handlers for this switch (press and release)."""
        self._pressed = []
        self._released = []

    def _handle(self, pressed: bool) -> None:
        # Owning button object's pump calls this; students do not.
        handlers = self._pressed if pressed else self._released
        for handler in handlers:
            handler()


class Button(PushButtonBase):
    """One GPIO pin: press/release handlers (inherited from ``PushButtonBase``) plus ``run()``.

    ``run()`` must be running (e.g. via ``asyncio.gather``) for handlers
    registered with ``on_pressed`` / ``on_released`` to ever fire.
    """

    def __init__(self, pin=None, *, event_queue=None) -> None:
        """Bind to ``pin``, or skip GPIO entirely for a hardware-free test.

        ``pin`` is a board pin object, e.g. ``board.IO13``. Pass ``event_queue=``
        instead of ``pin`` to feed pre-built events without touching GPIO — used
        by tests that run without hardware. Passing neither raises ``ValueError``.
        """
        super().__init__()
        self._keys = None
        self._queue = None
        if event_queue is not None:
            self._queue = event_queue
            return
        if pin is None:
            raise ValueError("pin is required when event_queue is omitted")
        _bind_scanner(self, (pin,))

    def _dispatch(self, event) -> None:
        # Standalone scanner is a 1-tuple; ignore key_number.
        self._handle(event.pressed)

    async def run(self) -> None:
        """Never-ending task that delivers this pin's press and release events.

        Typically ``await asyncio.gather(button.run(), display_loop())``.
        """
        await _pump(self._queue, self._dispatch)


class OnboardButtons:
    """This board's native buttons: ``button_a`` and ``button_b``.

    ``button_a`` / ``button_b`` are the two switches — register handlers with
    ``.on_pressed(handler)`` / ``.on_released(handler)``; ``.clear()`` removes
    them again.
    """

    def __init__(self, a_pin=None, b_pin=None, *, event_queue=None) -> None:
        """Bind to this board's A and B buttons. Typically requires no arguments:

            buttons = OnboardButtons()

        ``a_pin`` / ``b_pin`` default to ``board.BUTTON_A`` / ``board.BUTTON_B``;
        pass them only if you want to wire A/B to different pins instead.
        """
        # event_queue is a developer/test-only hook: it replaces a_pin/b_pin
        # entirely, feeding pre-built events instead of a real keypad.Keys scanner,
        # so tests can run without hardware (same pattern as Button/PlanetXButtonSensor).
        # Not part of the student-facing construction API documented above.
        self._a = PushButtonBase()
        self._b = PushButtonBase()
        self._keys = None
        self._queue = None
        if event_queue is not None:
            self._queue = event_queue
            return
        if a_pin is None or b_pin is None:
            import board  # CircuitPython-only; not imported on the host test path

            if a_pin is None:
                a_pin = board.BUTTON_A
            if b_pin is None:
                b_pin = board.BUTTON_B
        _bind_scanner(self, (a_pin, b_pin))

    @property
    def button_a(self) -> PushButtonBase:
        """Button A — ``on_pressed`` / ``on_released`` / ``clear``."""
        return self._a

    @property
    def button_b(self) -> PushButtonBase:
        """Button B — ``on_pressed`` / ``on_released`` / ``clear``."""
        return self._b

    def clear(self) -> None:
        """Drop all registered handlers for both buttons."""
        self._a.clear()
        self._b.clear()

    def _dispatch(self, event) -> None:
        # ``event.key_number`` is a tuple position matching ``(a_pin, b_pin)``:
        # scanner slot 0 is A, slot 1 is B. Bounds-checked explicitly (not a bare
        # try/except IndexError) because a negative key_number would otherwise
        # silently wrap onto a *valid* button instead of being rejected.
        index = event.key_number
        if index == 0:
            self._a._handle(event.pressed)
        elif index == 1:
            self._b._handle(event.pressed)

    async def run(self) -> None:
        """Never-ending task that delivers both buttons' press and release events.

        Typically ``await asyncio.gather(buttons.run(), display_loop())``.
        """
        await _pump(self._queue, self._dispatch)

"""
Async button dispatcher: one Python object per physical module.

Student-facing operations are press/release handlers. GPIO identities belong
on the constructor (portability seam), not inside handlers.

``PushButtonBase`` is one switch: press/release handlers, no scanner. ``Button``
is a ``PushButtonBase`` plus a 1-pin scanner and ``run()``. ``ButtonPair`` is two
pins sharing one scanner, exposing ``left`` / ``right`` as ``PushButtonBase`` instances.
``OnboardButtons`` is this board's native A/B pair. PlanetX modules live in the
``planetx`` package (push-button sensor first).

Device backend: CircuitPython ``keypad.Keys`` (active-low, pull-up) → native
EventQueue → this dispatcher → an asyncio pump (``run``). Host tests inject
a fake queue with the CircuitPython Event shape (``.key_number``, ``.pressed``).

There is no student ``update()`` loop.
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

    ``import keypad`` lives here so a host ``import buttons`` does not load it
    (tests pass ``event_queue=`` and never call this). Each device-path
    construct runs the statement; after the first it is a ``sys.modules``
    lookup. Bind is once per physical module at construct time, not per event.
    """
    import keypad  # CircuitPython-only; not Blinka-on-CPython

    owner._keys = keypad.Keys(pins, value_when_pressed=False, pull=True)  # unread on purpose: owns the scanner; EventQueue does not keep Keys alive
    owner._queue = owner._keys.events


async def _pump(queue, dispatch) -> None:
    """Drain ``queue`` and call ``dispatch(event)`` until cancelled.

    Student sketches ``await buttons.run()`` (typically as a background task
    alongside display animations). Host CPython ``asyncio`` here is the test
    stand-in; the CIRCUITPY bundle ``asyncio`` is a different library.

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
        while event is not None:
            dispatch(event)
            event = queue.get()
        await asyncio.sleep(_POLL_INTERVAL_S)


class PushButtonBase:
    """One switch: press/release handlers. No scanner and no ``run()``.

    A ``Button`` (1-pin) or ``ButtonPair`` (2-pin) owns the queue and calls
    ``_handle``. Pair children (``left`` / ``right``, and lettered aliases)
    are ``PushButtonBase`` instances.
    """

    def __init__(self) -> None:
        self._pressed = []
        self._released = []

    def on_pressed(self, handler: Callable[[], None]) -> None:
        self._pressed.append(handler)

    def on_released(self, handler: Callable[[], None]) -> None:
        self._released.append(handler)

    def clear_pressed(self) -> None:
        """Drop all press handlers; leave release handlers."""
        self._pressed = []

    def clear_released(self) -> None:
        """Drop all release handlers; leave press handlers."""
        self._released = []

    def clear(self) -> None:
        """Drop all registered handlers for this switch."""
        self._pressed = []
        self._released = []

    def _handle(self, pressed: bool) -> None:
        handlers = self._pressed if pressed else self._released
        for handler in handlers:
            handler()


class Button(PushButtonBase):
    """One pin: a ``PushButtonBase`` plus its own scanner and ``run()`` pump.

    ``pin`` is constructor config. Overnight host tests pass ``event_queue=``
    and skip ``keypad``. ``Button()`` with neither pin nor queue raises.
    """

    def __init__(self, pin=None, *, event_queue=None) -> None:
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
        self._handle(event.pressed)

    async def run(self) -> None:
        """Asyncio pump for this button's own EventQueue."""
        await _pump(self._queue, self._dispatch)


class ButtonPair:
    """Two ``PushButtonBase`` instances sharing one 2-pin scanner: ``left`` (index 0) and ``right`` (index 1).

    ``left_pin`` / ``right_pin`` are constructor config. Overnight host tests
    pass ``event_queue=`` and skip ``keypad``. Generic names only: lettered
    A/B live on ``OnboardButtons``; C/D live on ``planetx.PlanetXButtonSensor``.
    """

    def __init__(self, left_pin=None, right_pin=None, *, event_queue=None) -> None:
        self.left = PushButtonBase()
        self.right = PushButtonBase()
        self._keys = None
        self._queue = None
        if event_queue is not None:
            self._queue = event_queue
            return
        if left_pin is None or right_pin is None:
            raise ValueError("left_pin and right_pin are required when event_queue is omitted")
        _bind_scanner(self, (left_pin, right_pin))

    def clear(self) -> None:
        """Drop all registered handlers on both buttons."""
        self.left.clear()
        self.right.clear()

    def _dispatch(self, event) -> None:
        # ``event.key_number`` is a tuple position matching ``(left_pin, right_pin)``.
        # Bounds-checked explicitly (not a bare try/except IndexError) because a
        # negative key_number would otherwise silently wrap to a *valid* tuple
        # element instead of being rejected.
        index = event.key_number
        if index == 0:
            self.left._handle(event.pressed)
        elif index == 1:
            self.right._handle(event.pressed)

    async def run(self) -> None:
        """Asyncio pump: drain this pair's EventQueue into ``left`` / ``right``.

        Contained ``PushButtonBase`` instances have no scanner; this method owns the queue.
        """
        await _pump(self._queue, self._dispatch)


class OnboardButtons(ButtonPair):
    """BPI-Bit-S2 native A (left) and B (right).

    Device path defaults ``a_pin`` / ``b_pin`` to ``board.BUTTON_A`` /
    ``board.BUTTON_B``. Overnight host tests pass ``event_queue=`` and skip
    ``board`` / ``keypad``.
    """

    def __init__(self, a_pin=None, b_pin=None, *, event_queue=None) -> None:
        if event_queue is None and (a_pin is None or b_pin is None):
            import board  # CircuitPython-only; not imported on the host test path

            if a_pin is None:
                a_pin = board.BUTTON_A
            if b_pin is None:
                b_pin = board.BUTTON_B
        super().__init__(a_pin, b_pin, event_queue=event_queue)

    @property
    def a(self) -> PushButtonBase:
        return self.left

    @property
    def b(self) -> PushButtonBase:
        return self.right

    def on_a_pressed(self, handler: Callable[[], None]) -> None:
        self.left.on_pressed(handler)

    def on_b_pressed(self, handler: Callable[[], None]) -> None:
        self.right.on_pressed(handler)

    def on_a_released(self, handler: Callable[[], None]) -> None:
        self.left.on_released(handler)

    def on_b_released(self, handler: Callable[[], None]) -> None:
        self.right.on_released(handler)

    def clear_a(self) -> None:
        self.left.clear()

    def clear_b(self) -> None:
        self.right.clear()

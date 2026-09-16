"""
One Python object per physical button module.

Student operations are press/release handlers. GPIO identities belong on the
constructor (portability seam), not inside handlers. There is no ``update()``
loop; ``await run()`` is a background task (typically gathered with display work).

``Button`` is one pin. ``ButtonPair`` is two pins as ``left`` / ``right``.
``OnboardButtons`` is this board's native A/B pair. PlanetX modules live in
the ``planetx`` package.
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
        while event is not None:
            dispatch(event)
            event = queue.get()
        await asyncio.sleep(_POLL_INTERVAL_S)


class PushButtonBase:
    """Press and release handlers for one switch.

    Register with ``on_pressed`` / ``on_released``. ``clear``, ``clear_pressed``,
    and ``clear_released`` drop handlers. This object has no ``run()``; call
    ``run`` on the owning ``Button`` or ``ButtonPair``.
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
        # Owning Button / ButtonPair pump calls this; students do not.
        handlers = self._pressed if pressed else self._released
        for handler in handlers:
            handler()


class Button(PushButtonBase):
    """One GPIO pin: press/release handlers and ``run()``.

    ``pin`` is constructor config. Pass ``event_queue=`` instead to skip GPIO
    (host tests). ``Button()`` with neither raises ``ValueError``.
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
        # Standalone scanner is a 1-tuple; ignore key_number.
        self._handle(event.pressed)

    async def run(self) -> None:
        """Never-ending task that delivers this pin's press and release events.

        Typically ``await asyncio.gather(button.run(), display_loop())``.
        """
        await _pump(self._queue, self._dispatch)


class ButtonPair:
    """Two buttons on one module: ``left`` and ``right``.

    ``left_pin`` / ``right_pin`` are constructor config. Pass ``event_queue=``
    instead to skip GPIO (host tests). Lettered names live on ``OnboardButtons``
    (A/B) and ``planetx.PlanetXButtonSensor`` (C/D).
    """

    def __init__(self, left_pin=None, right_pin=None, *, event_queue=None) -> None:
        # Generic pair children (no scanner). Lettered aliases live on subclasses.
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
        """Never-ending task that delivers this pair's press and release events.

        Typically ``await asyncio.gather(pair.run(), display_loop())``.
        Call ``run`` on the pair, not on ``left`` or ``right``.
        """
        # Pair owns the queue; contained PushButtonBase instances do not.
        await _pump(self._queue, self._dispatch)


class OnboardButtons(ButtonPair):
    """This board's native buttons A and B.

    Student operations are ``on_a_pressed`` / ``on_b_pressed`` and the matching
    release and clear names. Pins default to ``board.BUTTON_A`` / ``board.BUTTON_B``.
    Pass ``event_queue=`` to skip ``board`` / GPIO (host tests).
    """

    def __init__(self, a_pin=None, b_pin=None, *, event_queue=None) -> None:
        if event_queue is None and (a_pin is None or b_pin is None):
            import board  # CircuitPython-only; not imported on the host test path

            if a_pin is None:
                a_pin = board.BUTTON_A
            if b_pin is None:
                b_pin = board.BUTTON_B
        super().__init__(a_pin, b_pin, event_queue=event_queue)

    # Pair slots: A is left (key_number 0), B is right (key_number 1).
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

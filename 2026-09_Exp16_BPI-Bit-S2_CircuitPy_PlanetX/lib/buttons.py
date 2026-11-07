"""Buttons for this board and for PlanetX.

A handler is called when the event happens: either a button is pressed or released.
You provide the handler function and when the button is pressed, your handler is called.
Presses and releases (events) of that same button are processed one at a time, in the order
they happened. If the button events happen faster than your handler can process them, the
events are queued up and processed in order.

In the following example, ``log_button_press`` is a normal function. It runs to the
end before anything else runs. So keep your handlers short; never call ``time.sleep``
in a handler. If you want actions to be delayed or timed, then schedule them from within
the handler with ``asyncio.create_task(...)`` and return quickly from the handler itself.

    import asyncio
    import display
    from buttons import OnboardButtons

    def log_button_press():
        print("A pressed")

    async def main():
        buttons = OnboardButtons()
        buttons.button_a.on_pressed(log_button_press)
        await buttons.run()

    asyncio.run(main())

The following ``announce_and_wait`` is an ``async def``. The button library waits until
it is done. While it is paused at ``await``, the display and the other button keep running.
The next press or release of this button has to wait until the prior call of
``announce_and_wait`` returns:

    import asyncio
    import display
    from buttons import OnboardButtons

    async def announce_and_wait():
        await display.display.show_string("A")

    async def main():
        buttons = OnboardButtons()
        buttons.button_a.on_pressed(announce_and_wait)
        await buttons.run()

    asyncio.run(main())

Function ``scroll_hello`` below starts a scroll and returns, so the next press can be processed
immediately without waiting for the scroll to finish. ``create_task`` only schedules that work.
The scroll starts after your function has returned. Registering a different handler later does
not stop a scroll you already started. An error inside that scroll just ends the task, but
is not visible to the ``scroll_hello`` handler.

    import asyncio
    import display
    from buttons import OnboardButtons

    def scroll_hello():
        asyncio.create_task(display.display.show_string("HELLO", loop=True))

    async def main():
        buttons = OnboardButtons()
        buttons.button_a.on_pressed(scroll_hello)
        await buttons.run()

    asyncio.run(main())

For a handler, implement a normal function or an ``async def``. A normal function ``f`` is run as ``f()``.
A function ``a`` defined as ``async def`` is run as ``await a()``. Inside an ``async def``, ``await``
the work you want to finish. Do not return a coroutine from either kind of handler.

To make your own kind of button, write a class that extends ``Button``. For example,
``PlanetXCrashSensor``.

To watch this board's A/B buttons and a PlanetX module at the same time, make one object
for each and run both. ``buttons_ab`` is an ``OnboardButtons`` object for reacting
to the A and B buttons on this board. ``buttons_cd`` is a ``PlanetXButtonSensor``
(buttons C and D on the external module).

1. ``gather`` waits on each ``run()``. Those calls run forever, so any lines
   after ``gather`` are never reached.

        import asyncio
        from buttons import OnboardButtons
        from planetx import J3, PlanetXButtonSensor

        async def main():
            buttons_ab = OnboardButtons()
            buttons_cd = PlanetXButtonSensor(port=J3)
            await asyncio.gather(buttons_ab.run(), buttons_cd.run())

        asyncio.run(main())

2. ``create_task`` starts ``run()`` in the background and returns right away, so your
   function can continue. You can register a handler after ``run()`` has started.
   ``log_button_press`` below runs on the next press of A after it was registered as
   handler. When ``main`` returns, ``asyncio.run`` finishes and those background
   tasks (``buttons_ab.run`` and ``buttons_cd.run``) stop.

        import asyncio
        from buttons import OnboardButtons
        from planetx import J3, PlanetXButtonSensor

        def log_button_press():
            print("A pressed")

        async def main():
            buttons_ab = OnboardButtons()
            buttons_cd = PlanetXButtonSensor(port=J3)
            asyncio.create_task(buttons_ab.run())
            asyncio.create_task(buttons_cd.run())
            buttons_ab.button_a.on_pressed(log_button_press) # you can register the handler on ``buttons_ab`` before or after ``run()`` has been called
            await asyncio.sleep(60)

        asyncio.run(main())

``Button`` is one physical switch you construct yourself, specifying which GPIO pin it is
connected to. ``OnboardButtons`` is this board's A and B. ``OnboardButtons.deinit()`` releases
both pins. PlanetX modules (C/D, and the crash sensor) are in the ``planetx`` package. The
crash sensor is a ``Button``. You choose their port with ``port=`` in the constructor.

If you don't need a button anymore, you can deinitialize it by calling ``button.deinit()``.
Deinitialization releases the GPIO pin(s) the button was connected to right away, so you can
reuse the GPIO pin(s) for something right after ``button.deinit()`` returns. A ``run()`` task
that is going stops by itself: the handler already running finishes, then ``run()`` raises
``RuntimeError``.
"""

import asyncio
import sys

# ``board`` and ``keypad`` exist only on CircuitPython. In the test environment (CPython) both names
# are ``None``, and tests replace them with fakes, for example ``monkeypatch.setattr(buttons, "keypad", fake)``.
# This is the only place the code knows about tests.
if sys.implementation.name == "circuitpython":
    import board
    import keypad
else:
    board = None
    keypad = None

try:  # CircuitPython / MicroPython have ``sys.print_exception``; CPython does not.
    from sys import print_exception as _print_exception
except ImportError:
    from traceback import print_exception as _print_exception

try:  # CircuitPython provides ``micropython.const``.
    from micropython import const
except ImportError:

    def const(x):
        return x


try:
    from typing import Callable
except ImportError:
    pass


# Milliseconds ``Button.run`` waits between scans when the queue is empty.
# 10 ms is half of keypad.Keys' default scan interval (20 ms). After an event
# is already queued, the average extra wait is ``_POLL_MS / 2`` (5 ms).
# So on average, this library increases the latency by 5 ms.
_POLL_MS = 10

_OVERFLOW_WARNING = "button event queue overflowed; events were dropped"

# Button._state. 2 is final: deinit() and the end of run() both release the pin and enter 2.
_STATE_READY = const(0)  # constructed; run() has not started
_STATE_RUNNING = const(1)  # run() is inside its loop
_STATE_DEINIT = const(2)  # the pin is released; run() must raise and must not start


def _bind_scanner(owner, pins) -> None:
    """Attach a ``keypad.Keys`` scanner for ``pins`` onto ``owner``.

    Device path: ``keypad.Keys`` (active-low, pull-up) → native EventQueue on
    ``owner``. On the physical board, ``keypad`` is the real module. In the test environment it
    is ``None`` unless a test replaces it, so this function raises ``AssertionError`` if
    ``keypad`` is missing (a test bug). The check costs almost nothing, because each button
    is bound only once, at construction time.
    """
    assert keypad is not None, "keypad is CircuitPython-only; tests must replace buttons.keypad"

    # ``_keys`` is the scanner that watches the pin. ``_queue`` is that scanner's event list.
    # We retain a reference to ``_keys`` so we can ``deinit`` the button-to-pin-pairing later.
    owner._keys = keypad.Keys(pins, value_when_pressed=False, pull=True)
    owner._queue = owner._keys.events


def _report_handler_error(e) -> None:
    """Print exception ``e`` on the serial console and return. The button keeps running."""
    _print_exception(e)


def _make_buttons(pin_1, pin_2):
    """Build two ``_Switch`` objects. If the second pin fails, deinit the first."""
    first = _Switch(pin_1)
    try:
        second = _Switch(pin_2)
    except Exception:
        first._deinit()
        raise
    return first, second


class _Switch:
    """One physical button switch, wired to one GPIO pin. This is a private base class that provides
    service methods for deinitialization and event handling. ``Button`` adds public ``deinit`` and ``run``."""

    def __init__(self, pin) -> None:
        """Bind the button functionality to a GPIO ``pin``.
        ``pin`` is a board pin object, e.g. ``board.IO13``.
        """
        self._init_state()
        _bind_scanner(self, (pin,))

    @classmethod
    def _from_queue(cls, event_queue):
        """For TESTING: a button fed from ``event_queue`` instead of a GPIO pin.

        Tests push events into ``event_queue`` without pressing a physical switch. The button
        has no ``keypad.Keys`` scanner (object that would watch a pin and queue its events) and
        no pin; ``__init__`` (also a subclass's) is not called.
        """
        obj = cls.__new__(cls)
        obj._init_state()
        obj._queue = event_queue
        return obj

    def _init_state(self) -> None:
        """Set the fields every button starts with: no handlers, no scanner, not running."""
        self._pressed = None
        self._released = None
        self._keys = None
        self._queue = None
        self._state = _STATE_READY

    def on_pressed(self, handler: Callable[[], object] | None) -> None:
        """Set the ``handler`` function called when this button is pressed.

        A normal function and an ``async def`` are both accepted as ``handler``.
        A normal function ``f`` is run as ``f()``. An ``async`` function ``a`` is run
        as ``await a()``. Providing ``None`` as a handler means the event is a no-op.

        ``f()`` runs to the end before anything else runs. While ``await a()``
        is paused, the other button keeps running. This button's next event (press or
        release event) waits until the handler returns.
        """
        self._pressed = handler

    def on_released(self, handler: Callable[[], object] | None) -> None:
        """Set the ``handler`` function called when this button is released.

        A normal function and an ``async def`` are both accepted as ``handler``.
        A normal function ``f`` is run as ``f()``. An ``async`` function ``a`` is run
        as ``await a()``. Providing ``None`` as a handler means the event is a no-op.

        ``f()`` runs to the end before anything else runs. While ``await a()``
        is paused, the other button keeps running. This button's next event (press or
        release event) waits until the handler returns.
        """
        self._released = handler

    async def _on_event(self, pressed: bool) -> None:
        """Call the handler for this press (``True``) or release (``False``)."""

        handler = self._pressed if pressed else self._released
        if handler is None:
            return
        # A normal function runs here. An ``async def`` call returns a coroutine;
        # awaiting it runs the body. A coroutine that body returns is not awaited.
        try:
            result = handler()
            if hasattr(result, "__await__"):
                await result
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            _report_handler_error(exc)
        # After a handler executed we yield to other ready tasks, before this button's next
        # queued event is potentially processed. ``sleep_ms(0)`` is a single yield. An unset
        # handler returns above and does not yield, for efficiency.
        await asyncio.sleep_ms(0)

    def _deinit(self) -> None:
        """Release this switch's GPIO pin. Private service method for deinitialization, so
        individual buttons of multi-button sensors cannot be deinitialized individually,
        which would leave the multi-button sensor in an inconsistent state.
        Idempotent: calling ``_deinit()`` on an already deinitialized button is a no-op.
        """
        if self._state == _STATE_DEINIT:
            return
        self._state = _STATE_DEINIT
        keys = self._keys
        if keys is None:  # A button built with ``_from_queue`` has no scanner and no pin to release.
            return
        keys.deinit()
        self._keys = None

    async def _run(self) -> None:
        """Deliver this switch's press and release events until it is deinitialized or the task is cancelled.

        Private service method, for the same reason as ``_deinit``: its ``finally`` deinitializes this switch,
        so running one switch of a multi-button sensor on its own could leave the sensor half deinitialized.
        ``Button.run`` and the multi-button sensors' ``run`` call it to make it publicly available.
        """
        if self._state == _STATE_DEINIT:
            raise RuntimeError("button is deinitialized")
        if self._state == _STATE_RUNNING:
            raise RuntimeError("run() is already running")
        self._state = _STATE_RUNNING
        # ``_queue.overflowed`` stays true until ``_queue.clear()``, and ``clear()`` also drops queued events. So the
        # warning is printed as soon as the overflow is seen, but the flag is reset only after the queue is drained.
        # ``warned`` keeps the warning to once per overflow while the flag stays set.
        warned = False
        sleep_ms = asyncio.sleep_ms
        try:
            while True:
                if self._state == _STATE_DEINIT:
                    raise RuntimeError("button is deinitialized")
                event = self._queue.get()
                while event is not None:
                    # A full queue shows up here, right after the handler or task that kept this loop from draining.
                    # The get() just before freed a slot, so the queue can take one new event while we print.
                    if self._queue.overflowed and not warned:
                        warned = True
                        print(_OVERFLOW_WARNING)
                    await self._on_event(event.pressed)  # does asyncio.sleep_ms(0) after executing not-None handler
                    if self._state == _STATE_DEINIT:
                        raise RuntimeError("button is deinitialized")
                    event = self._queue.get()
                if self._queue.overflowed:
                    # The queue was just drained. A press that lands between the last get() and clear() is dropped. We can't do
                    # anything about it, because the board scans the pin on a timer, outside the Python VM (on ESP32-S2: using the
                    # ESP-IDF timer service). A scan can queue an event between any two statements here, even though this code does
                    # not await. print() comes after clear(): it can wait on the serial port, and presses during that wait stay queued.
                    self._queue.clear()
                    if not warned:
                        print(_OVERFLOW_WARNING)
                    warned = False
                await sleep_ms(_POLL_MS)
        finally:
            # However run() ends, for example by a cancelled task, the button is deinitialized: the pin is released and run() cannot start again.
            self._deinit()


class Button(_Switch):
    """One physical button switch you construct yourself, specifying which GPIO pin it is
    connected to.

    ``on_pressed`` sets the press handler. ``on_released`` sets the release handler.
    Calling those methods again with a new handler replaces the previous handler.
    Setting the handler to ``None`` means the event is a no-op. ``run()`` must be running
    (for example via ``asyncio.gather``) for a handler to fire. ``deinit()`` turns the
    scanner off and releases the GPIO pin.
    """

    def deinit(self) -> None:
        """Turn this button's scanner off and release its GPIO pin.

        The pin is released right away, so you can reuse it for something right after
        ``button.deinit()`` returns. A ``run()`` task that is going stops by itself: the handler
        already running finishes, then ``run()`` raises ``RuntimeError``.
        """
        self._deinit()

    async def run(self) -> None:
        """Never-ending task: deliver this button's presses and releases.

        Call it once. A second ``run()`` on the same button raises ``RuntimeError``.
        When ``run()`` ends, for example because its task was cancelled, the button is done:
        its GPIO pin is released. To use the pin again, construct a new button.
        Typically use ``await asyncio.gather(button.run(), ...)`` (blocking).
        If a handler raises an error, the error is printed and the button keeps running.

        Internally, the logic checks if new events (button presses or releases) have
        arrived and executes the respective handler. If no events have arrived, it
        waits for 10 ms before checking again. If events have been queued up, it
        processes them one at a time in the order they happened.

        After an event has happened and been queued, it takes on average 5 ms
        and 10 ms at worst for the event to be processed.
        """
        await self._run()


class OnboardButtons:
    """This board's native buttons A and B, which the code calls ``button_a`` and ``button_b``.

    Each of ``button_a`` and ``button_b`` has ``on_pressed`` and ``on_released`` to specify their
    respective button event handlers. Specifying ``None`` as a handler means the respective event
    is a no-op.
    ``run()`` processes the events from both buttons. IMPORTANT: There is no order between A and B.
    ``deinit()`` releases the GPIO pins for A and B.
    """

    def __init__(self, a_pin=None, b_pin=None) -> None:
        """Bind to this board's A and B buttons. Typically requires no arguments:

            buttons = OnboardButtons()

        ``a_pin`` / ``b_pin`` default to ``board.BUTTON_A`` / ``board.BUTTON_B``;
        pass them only if you want to act on buttons connected to different pins instead.
        """
        if a_pin is None or b_pin is None:
            # ``board`` is ``None`` in the test environment unless a test replaces it (see the top of this file).
            assert board is not None, "board is CircuitPython-only; tests must replace buttons.board"
            if a_pin is None:
                a_pin = board.BUTTON_A
            if b_pin is None:
                b_pin = board.BUTTON_B
        self._a, self._b = _make_buttons(a_pin, b_pin)

    @classmethod
    def _from_buttons(cls, button_a: _Switch, button_b: _Switch) -> "OnboardButtons":
        """For TESTING: Pair two buttons that already exist.

        ``__init__`` is not called, so nothing uses the ``board`` module (``None`` in the test
        environment) or creates ``keypad.Keys`` scanners on physical GPIO pins. Tests typically
        pass two buttons built with ``Button._from_queue(event_queue)`` and push events into
        those queues instead of pressing a physical switch.
        """
        obj = cls.__new__(cls)
        obj._a = button_a
        obj._b = button_b
        return obj

    def deinit(self) -> None:
        """Turn the scanners off and release the GPIO pins for buttons A and B.

        Both pins are released right away, so you can reuse them for something right after
        ``buttons.deinit()`` returns. A ``run()`` task that is going stops by itself: the handler
        already running finishes, then ``run()`` raises ``RuntimeError``.
        """
        self._a._deinit()
        self._b._deinit()

    @property
    def button_a(self) -> _Switch:
        """Button A."""
        return self._a

    @property
    def button_b(self) -> _Switch:
        """Button B."""
        return self._b

    async def run(self) -> None:
        """Never-ending task that delivers the press and release events of buttons A and B.

        Typically ``await buttons.run()``, or ``await asyncio.gather(buttons.run(), ...)`` to run it
        together with other tasks. Handlers are only called while this task runs. Call it once; a
        second ``run()`` raises ``RuntimeError``. A and B each have their own scanner, so a slow
        handler on one button does not hold up the other. If a handler raises an error, the error
        is printed and the buttons keep running. When this task ends, for example because it was
        cancelled, both GPIO pins are released, and this object cannot run again.
        """
        await asyncio.gather(self._a._run(), self._b._run())

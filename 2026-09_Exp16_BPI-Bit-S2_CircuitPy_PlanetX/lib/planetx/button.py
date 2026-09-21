"""ElecFreaks PlanetX push-button module: buttons C and D.

Plug the module into a Nezha2 port, then pass that port to the constructor:

    from planetx import J3, PlanetXButtonSensor

    buttons = PlanetXButtonSensor(port=J3)
    buttons.button_c.on_pressed(lambda: print("C pressed"))

Wiring ``c_pin`` / ``d_pin`` directly into the PlanetXButtonSensor constructor is
also possible. Two modules on two ports are two separate instances; in that case
the C/D names are local to each instance, not shared across modules.
"""

from __future__ import annotations

from buttons import PushButtonBase, _bind_scanner, _pump
from .ports import Port


class PlanetXButtonSensor:
    """One PlanetX push-button module: two switches, ``C`` and ``D``.

    ``button_c`` / ``button_d`` are the two switches — register handlers with
    ``.on_pressed(handler)`` / ``.on_released(handler)``; ``.clear()`` removes
    them again. Construct a ``PlanetXButtonSensor`` one of two ways (do not mix):

    1. ``port=`` a ``planetx.Port`` such as ``J3``, or
    2. a wired pin pair, ``c_pin`` and ``d_pin`` — board pin objects, e.g. ``board.IO13``
       (not the ``P-number`` itself; see ``planetx.ports`` for that translation).
    """

    def __init__(self, c_pin=None, d_pin=None, *, port: Port | None = None, event_queue=None) -> None:
        # event_queue is a developer/test-only hook: it replaces port=/c_pin+d_pin
        # entirely, feeding pre-built events instead of a real keypad.Keys scanner,
        # so tests can run without hardware (same pattern as buttons.Button/OnboardButtons).
        # Not part of the student-facing construction API documented above.
        self._c = PushButtonBase()
        self._d = PushButtonBase()
        self._keys = None
        self._queue = None
        if event_queue is not None:
            self._queue = event_queue
            return
        if port is not None:
            if c_pin is not None or d_pin is not None:
                raise ValueError("provide either parameter `port` or the pair `(c_pin and d_pin)`, not both")
            c_pin, d_pin = port.pins
        elif c_pin is None or d_pin is None:
            raise ValueError("port= or c_pin and d_pin are required when event_queue is omitted")
        _bind_scanner(self, (c_pin, d_pin))

    @property
    def button_c(self) -> PushButtonBase:
        """Switch C — ``on_pressed`` / ``on_released`` / ``clear``."""
        return self._c

    @property
    def button_d(self) -> PushButtonBase:
        """Switch D — ``on_pressed`` / ``on_released`` / ``clear``."""
        return self._d

    def clear(self) -> None:
        """Drop all registered handlers for both switches."""
        self._c.clear()
        self._d.clear()

    def _dispatch(self, event) -> None:
        # ``event.key_number`` is a tuple position matching ``(c_pin, d_pin)``:
        # scanner slot 0 is C, slot 1 is D. Bounds-checked explicitly (not a bare
        # try/except IndexError) because a negative key_number would otherwise
        # silently wrap onto a *valid* switch instead of being rejected.
        index = event.key_number
        if index == 0:
            self._c._handle(event.pressed)
        elif index == 1:
            self._d._handle(event.pressed)

    async def run(self) -> None:
        """Never-ending task that delivers both switches' press and release events.

        Typically ``await asyncio.gather(buttons.run(), display_loop())``.
        """
        await _pump(self._queue, self._dispatch)

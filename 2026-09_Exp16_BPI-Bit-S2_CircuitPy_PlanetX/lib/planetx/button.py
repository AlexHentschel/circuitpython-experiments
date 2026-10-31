"""ElecFreaks PlanetX push-button module: buttons C and D.

Plug the module into one of the Nezha2's GPIO interface ports (J1 to J4) and pass that port to the constructor
with ``port=``. Then set a handler for each button event you care about, and run the buttons:

    import asyncio
    from planetx import J3, PlanetXButtonSensor

    def log_c_press():
        print("C pressed")

    def log_d_release():
        print("D released")

    async def main():
        buttons = PlanetXButtonSensor(port=J3)
        buttons.button_c.on_pressed(log_c_press)
        buttons.button_d.on_released(log_d_release)
        await buttons.run()

    asyncio.run(main())

As long as the buttons are supposed to be active, the ``run()`` method needs to be running in the
background. Handlers are only called while ``buttons.run()`` is running, and it runs forever. Handlers
work the same way as for the board's A and B buttons; the ``buttons`` module has more examples:

- A handler is a normal function or an ``async def``. Presses and releases of one button are
  handled one at a time, in the order they happened. If they come faster than your handler
  finishes, they wait in a queue.
- A normal function runs to the end before anything else runs. So keep it short and never call
  ``time.sleep`` in it. For something that takes time, start it with ``asyncio.create_task(...)``
  and return right away.
- While an ``async def`` handler is paused at ``await``, the other button and the rest of your
  program keep running. The next event of the same button waits until the handler returns.

To watch the board's A and B buttons as well, make one object for each and run both:

    import asyncio
    from buttons import OnboardButtons
    from planetx import J3, PlanetXButtonSensor

    async def main():
        buttons_ab = OnboardButtons()
        buttons_cd = PlanetXButtonSensor(port=J3)
        # set the handlers here, as in the example above
        await asyncio.gather(buttons_ab.run(), buttons_cd.run())

    asyncio.run(main())

Each module you plug in is its own ``PlanetXButtonSensor``. With two modules on J3 and J4, you
construct two objects, and each one has its own ``button_c`` and ``button_d``.
"""

from __future__ import annotations

from buttons import _Switch, _make_buttons
from .ports import Port


class PlanetXButtonSensor:
    """One PlanetX push-button module with two buttons labelled ``C`` and ``D`` on the module,
    which the code calls ``button_c`` and ``button_d``.

    Each of ``button_c`` and ``button_d`` has ``on_pressed`` and ``on_released`` to set its handlers.
    Setting a handler to ``None`` means that event does nothing. ``run()`` processes the events of
    both buttons, and ``deinit()`` releases the GPIO interface port. ``button_c`` and ``button_d`` have no
    ``run`` or ``deinit`` of their own; use the ones on this object.
    """

    def __init__(self, c_pin=None, d_pin=None, *, port: Port | None = None) -> None:
        """Construct the logic for a PlanetXButtonSensor plugged into the GPIO interface ``port`` (J1 to J4). Example:

            buttons = PlanetXButtonSensor(port=J3)

        If the module is wired to other pins, pass ``c_pin`` and ``d_pin`` instead of ``port``.
        These are board pin objects such as ``board.IO13``, not the P-numbers printed on the
        board; see the project README's "Port mapping" section for the J1-J4/IIC table, or
        ``planetx.ports`` for the same mapping in code. Passing both ``port`` and pins, or
        neither, raises ``ValueError``.
        """
        if port is not None:
            if c_pin is not None or d_pin is not None:
                raise ValueError("provide either parameter `port` or the pair `(c_pin and d_pin)`, not both")
            c_pin, d_pin = port.pins
        elif c_pin is None or d_pin is None:
            raise ValueError("port= or c_pin and d_pin are required")
        self._c, self._d = _make_buttons(c_pin, d_pin)

    @classmethod
    def _from_buttons(cls, button_c: _Switch, button_d: _Switch) -> PlanetXButtonSensor:
        """For TESTING: Pair two buttons that already exist."""
        obj = cls.__new__(cls)
        obj._c = button_c
        obj._d = button_d
        return obj

    def deinit(self) -> None:
        """Turn the scanners off and release the GPIO pins for buttons C and D.

        Both pins are released right away, so you can reuse them for something right after
        ``buttons.deinit()`` returns. A ``run()`` task that is going stops by itself: the handler
        already running finishes, then ``run()`` raises ``RuntimeError``.
        """
        self._c._deinit()
        self._d._deinit()

    @property
    def button_c(self) -> _Switch:
        """Button C. Set its handlers with ``on_pressed`` and ``on_released``."""
        return self._c

    @property
    def button_d(self) -> _Switch:
        """Button D. Set its handlers with ``on_pressed`` and ``on_released``."""
        return self._d

    async def run(self) -> None:
        """Never-ending task that delivers the press and release events of buttons C and D.

        Typically ``await buttons.run()``, or ``await asyncio.gather(buttons.run(), ...)`` to run it
        together with other tasks. Handlers are only called while this task runs. Call it once; a
        second ``run()`` raises ``RuntimeError``. C and D each have their own scanner, so a slow
        handler on one button does not hold up the other. If a handler raises an error, the error
        is printed and the buttons keep running. When this task ends, for example because it was
        cancelled, both GPIO pins are released, and this object cannot run again.
        """
        import asyncio

        await asyncio.gather(self._c._run(), self._d._run())

"""PlanetX crash sensor: one switch on a Nezha2 jack.

The switch is the jack's second wire (J1 → P8, J2 → P12, J3 → P14, J4 → P16).
Pressed means the contacts are closed.

    import asyncio
    from planetx import J3, PlanetXCrashSensor

    async def main():
        crash = PlanetXCrashSensor(port=J3)
        crash.on_pressed(lambda: print("hit"))
        await crash.run()

    asyncio.run(main())
"""

from __future__ import annotations

from buttons import Button

from .ports import Port


class PlanetXCrashSensor:
    """One PlanetX crash sensor.

    Register ``on_pressed`` / ``on_released``, then ``await crash.run()``
    (usually inside ``asyncio.gather`` with the rest of the program).
    """

    def __init__(self, *, port: Port | None = None, event_queue=None) -> None:
        # ``event_queue`` is a test hook, same as ``buttons.Button``. Not part
        # of the student-facing construction API.
        if event_queue is not None:
            self._button = Button(event_queue=event_queue)
            return
        if port is None:
            raise ValueError("port= is required")
        # Second RJ11 wire. Same pin a button uses for one switch.
        self._button = Button(port.pins[1])

    def on_pressed(self, handler) -> None:
        """Call ``handler()`` every time the sensor is pressed."""
        self._button.on_pressed(handler)

    def on_released(self, handler) -> None:
        """Call ``handler()`` every time the sensor is released."""
        self._button.on_released(handler)

    def clear(self) -> None:
        """Drop all registered handlers."""
        self._button.clear()

    async def run(self) -> None:
        """Never-ending task that delivers press and release events.

        Typically ``await asyncio.gather(crash.run(), other_work())``.
        """
        await self._button.run()

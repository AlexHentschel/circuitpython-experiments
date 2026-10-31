"""PlanetX crash sensor: one switch on a Nezha2 GPIO interface port.

The switch is the port's second wire (J1 → P8, J2 → P12, J3 → P14, J4 → P16).
Pressed means the contacts are closed.

    import asyncio
    from planetx import J3, PlanetXCrashSensor

    def on_hit():
        print("hit")

    async def main():
        crash = PlanetXCrashSensor(port=J3)
        crash.on_pressed(on_hit)
        await crash.run()

    asyncio.run(main())
"""

from __future__ import annotations

from buttons import Button

from .ports import Port


class PlanetXCrashSensor(Button):
    """One PlanetX crash sensor.

    This is a ``Button``. Register ``on_pressed`` / ``on_released``, then
    ``await crash.run()`` (usually inside ``asyncio.gather`` with the rest
    of the program). ``port=`` selects the GPIO interface port; the sensor uses that port's
    second wire.
    """

    def __init__(self, *, port: Port) -> None:
        # Tests build a sensor with ``PlanetXCrashSensor._from_queue(queue)``, inherited from ``buttons``.
        # Second RJ11 wire. Same pin a button uses for one switch.
        super().__init__(port.pins[1])

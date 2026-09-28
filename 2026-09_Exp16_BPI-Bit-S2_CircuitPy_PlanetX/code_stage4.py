"""On-device smoke for the light sensor, rainbow ring, and smart motor.

Not selected by ``.vscode/cpfiles.txt``. To run it, point that manifest at
this file as ``/code.py`` for one deploy, then point it back.

Wire the light sensor to J1, the rainbow ring to J2, and a smart motor to M4.
The script prints how long 100 ``lux()`` calls take, lights the ring yellow
for a moment, then turns the motor 10° and back at a low speed.
"""

import asyncio

import supervisor

from planetx import (
    CLOCKWISE,
    COUNTERCLOCKWISE,
    J1,
    J2,
    M4,
    PlanetXLightSensor,
    PlanetXRainbowRing,
    PlanetXSmartMotor,
)


async def main() -> None:
    light = PlanetXLightSensor(port=J1)
    started = supervisor.ticks_ms()
    last = 0
    for _ in range(100):
        last = light.lux()
    elapsed = supervisor.ticks_ms() - started
    print("lux", last, "100 calls ms", elapsed)

    ring = PlanetXRainbowRing(port=J2)
    ring.fill((255, 150, 0))
    await asyncio.sleep(1)
    ring.off()

    motor = PlanetXSmartMotor(port=M4)
    await motor.turn(10, CLOCKWISE, speed=20)
    await motor.turn(10, COUNTERCLOCKWISE, speed=20)
    motor.stop()
    print("motor angle", motor.angle())


asyncio.run(main())

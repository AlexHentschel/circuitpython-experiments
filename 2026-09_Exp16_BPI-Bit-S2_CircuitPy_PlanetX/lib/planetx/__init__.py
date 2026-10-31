"""
ElecFreaks PlanetX sensors and the Nezha2 smart motor.

Each PlanetX module has its own class. When you create the object, you tell it with ``port=`` where the
module is plugged in: a GPIO interface port (``J1`` to ``J4``) or a motor port (``M1`` to ``M4``). After
that, you only call the object's methods; you do not name the port again:

    from planetx import J2, PlanetXRainbowRing

    ring = PlanetXRainbowRing(port=J2)
    ring.fill((255, 150, 0))   # yellow
    ring.off()

The other modules work the same way:

    from planetx import J1, J3, J4, M4
    from planetx import PlanetXButtonSensor, PlanetXCrashSensor, PlanetXLightSensor, PlanetXSmartMotor

    light = PlanetXLightSensor(port=J1)      # analog sensor: J1 or J2 only
    buttons = PlanetXButtonSensor(port=J3)
    crash = PlanetXCrashSensor(port=J4)
    motor = PlanetXSmartMotor(port=M4)

Shared Nezha2 map: ``J1``–``J4``, ``M1``–``M4``, and the shared ``I2C`` bus
in ``ports``. Do not wrap Exp09 ``elecfreaks_planetx``.
"""

# Protocol sources (MicroPython / MakeCode — not drop-in CircuitPython):
# https://github.com/elecfreaks/PlanetX_MicroPython
# https://github.com/elecfreaks/EF_Produce_MicroPython
# https://github.com/elecfreaks/pxt-PlanetX
# https://github.com/elecfreaks/pxt-nezha2
# See the experiment README § Further reading.

from .button import PlanetXButtonSensor
from .crash import PlanetXCrashSensor
from .light import PlanetXLightSensor
from .motor import (
    CLOCKWISE,
    COUNTERCLOCKWISE,
    DEGREES,
    SECONDS,
    SHORTEST,
    TURNS,
    PlanetXSmartMotor,
    Token,
)
from .neopixel import PlanetXNeoPixel, PlanetXRainbowRing, hsl
from .ports import I2C, I2CBus, J1, J2, J3, J4, M1, M2, M3, M4, MotorPort, Port

__all__ = [
    "PlanetXButtonSensor",
    "PlanetXLightSensor",
    "PlanetXNeoPixel",
    "PlanetXRainbowRing",
    "PlanetXSmartMotor",
    "PlanetXCrashSensor",
    "Token",
    "hsl",
    "CLOCKWISE",
    "COUNTERCLOCKWISE",
    "SHORTEST",
    "DEGREES",
    "TURNS",
    "SECONDS",
    "J1",
    "J2",
    "J3",
    "J4",
    "M1",
    "M2",
    "M3",
    "M4",
    "Port",
    "MotorPort",
    "I2C",
    "I2CBus",
]

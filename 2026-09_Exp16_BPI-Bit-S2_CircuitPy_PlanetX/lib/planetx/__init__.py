"""
ElecFreaks PlanetX sensors and the Nezha2 smart motor.

Student-facing operations stay on each module class. The jack or motor
port is constructor config.

    from planetx import J1, J2, J3, M4
    from planetx import PlanetXLightSensor, PlanetXRainbowRing
    from planetx import PlanetXSmartMotor, PlanetXCrashSensor, CLOCKWISE

Shared Nezha2 map: ``J1``–``J4``, ``M1``–``M4``, and the shared ``I2C`` bus
in ``ports``. Do not wrap Exp09 ``elecfreaks_planetx``.

Protocol sources (MicroPython / MakeCode — not drop-in CircuitPython):
https://github.com/elecfreaks/PlanetX_MicroPython
https://github.com/elecfreaks/EF_Produce_MicroPython
https://github.com/elecfreaks/pxt-PlanetX
https://github.com/elecfreaks/pxt-nezha2
See the experiment README § Further reading.
"""

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

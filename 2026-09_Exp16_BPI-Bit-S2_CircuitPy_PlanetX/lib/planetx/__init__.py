"""
ElecFreaks PlanetX sensors.

Student-facing operations stay on each module class (press handlers, later
sensor reads). GPIO / RJ11 port is constructor config.

This package is the home for PlanetX modules. Shared Nezha2 jack map:
``J1``–``J4`` and the shared ``I2C`` bus in ``ports``. The first module is
the two-button push-button sensor (C/D). Further sensors join as sibling
modules; do not wrap Exp09 ``elecfreaks_planetx``.

Protocol sources (MicroPython / MakeCode — not drop-in CircuitPython):
https://github.com/elecfreaks/PlanetX_MicroPython
https://github.com/elecfreaks/EF_Produce_MicroPython
https://github.com/elecfreaks/pxt-PlanetX
https://github.com/elecfreaks/pxt-nezha2
See the experiment README § Further reading.
"""

from .button import PlanetXButtonSensor
from .ports import I2C, I2CBus, J1, J2, J3, J4, Port

__all__ = ["PlanetXButtonSensor", "J1", "J2", "J3", "J4", "Port", "I2C", "I2CBus"]

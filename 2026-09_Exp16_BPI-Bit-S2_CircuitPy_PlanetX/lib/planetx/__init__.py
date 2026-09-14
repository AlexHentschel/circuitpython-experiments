"""
ElecFreaks PlanetX sensors.

Student-facing operations stay on each module class (press handlers, later
sensor reads). GPIO / RJ11 port is constructor config.

This package is the home for PlanetX modules. The first module is the
two-button push-button sensor (C/D). Further sensors join as sibling
modules; do not wrap Exp09 ``elecfreaks_planetx``.

Protocol sources (MicroPython / MakeCode — not drop-in CircuitPython):
https://github.com/elecfreaks/PlanetX_MicroPython
https://github.com/elecfreaks/EF_Produce_MicroPython
https://github.com/elecfreaks/pxt-PlanetX
https://github.com/elecfreaks/pxt-nezha2
See the experiment README § Further reading.
"""

from .button import PlanetXButtonSensor

__all__ = ["PlanetXButtonSensor"]

"""
2026 CircuitPython Community; author: AlexHentschel https://github.com/AlexHentschel

Elecfreaks PlanetX Sensors - CircuitPython Drivers

CircuitPython drivers for Elecfreaks PlanetX sensor modules.
Based on the MicroPython implementations from Elecfreaks.

Supported sensors:
- Button (AB Button with C and D buttons)
- Crash (Crash/collision sensor)
"""

from .button import Button
from .crash import Crash

__version__ = "0.0.0"
__all__ = ["Button", "Crash"]

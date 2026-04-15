"""
2026 CircuitPython Community; author: AlexHentschel https://github.com/AlexHentschel

Elecfreaks PlanetX Crash Sensor - CircuitPython Driver

A collision/crash sensor from the Elecfreaks PlanetX series.
Based on the MicroPython implementation from Elecfreaks:
https://github.com/elecfreaks/PlanetX_MicroPython

Example usage:
    import board
    from elecfreaks_planetx import Crash

    # Create crash sensor with a single GPIO pin
    crash = Crash(board.IO14)

    while True:
        if crash.is_pressed:
            print("Crash sensor triggered!")
"""

import digitalio
try:
    from typing import Optional
    from microcontroller import Pin
except ImportError:
    pass


class Crash:
    """
    Driver for Elecfreaks PlanetX Crash/Collision sensor.

    The crash sensor is a simple switch that connects to a single GPIO pin.
    It uses an internal pull-up resistor and reads LOW (0) when pressed/triggered.

    Args:
        pin: GPIO pin connected to the crash sensor

    Note:
        On Nezha V2 expansion board RJ ports (uses the second pin of each port):
        - J1: pin8
        - J2: pin12
        - J3: pin14
        - J4: pin16
    """

    def __init__(self, pin: "Pin") -> None:
        """Initialize the Crash sensor with the specified GPIO pin."""
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.INPUT
        self._pin.pull = digitalio.Pull.UP

    def deinit(self) -> None:
        """Release the GPIO pin."""
        self._pin.deinit()

    def __enter__(self) -> "Crash":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.deinit()

    @property
    def Is_pressed(self) -> bool:
        """
        Check if the crash sensor is pressed/triggered.

        Returns:
            True if the sensor is pressed, False otherwise.
        """
        return not self._pin.value

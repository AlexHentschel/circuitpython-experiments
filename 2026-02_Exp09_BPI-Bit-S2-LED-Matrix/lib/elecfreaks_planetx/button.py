# SPDX-FileCopyrightText: 2026 CircuitPython Community
# SPDX-License-Identifier: MIT

"""
Elecfreaks PlanetX Button Sensor - CircuitPython Driver

A dual-button sensor (C and D buttons) from the Elecfreaks PlanetX series.
Based on the MicroPython implementation from Elecfreaks:
https://github.com/elecfreaks/PlanetX_MicroPython

It uses an internal pull-up resistor and reads LOW (0) when pressed/triggered.


Example usage:
    import board
    from elecfreaks_planetx import Button

    # Create button with two GPIO pins (C button pin, D button pin)
    button = Button(board.IO13, board.IO14)

    while True:
        if button.c_pressed:
            print("C button pressed")
        elif button.d_pressed:
            print("D button pressed")
        elif button.cd_pressed:
            print("Both C and D buttons pressed")
"""

import digitalio

try:
    from typing import Optional
    from microcontroller import Pin
except ImportError:
    pass


class Button:
    """
    Driver for Elecfreaks PlanetX AB Button sensor.

    The button module has two buttons labeled C and D, each connected to a
    separate GPIO pin. The buttons use internal pull-up resistors and read
    LOW (0) when pressed.

    Args:
        pin_c: GPIO pin connected to the C button
        pin_d: GPIO pin connected to the D button

    Note:
        On Nezha V2 expansion board RJ ports:
        - J1: pin_c=pin1, pin_d=pin8
        - J2: pin_c=pin2, pin_d=pin12
        - J3: pin_c=pin13, pin_d=pin14
        - J4: pin_c=pin15, pin_d=pin16
    """

    def __init__(self, pin_c: "Pin", pin_d: "Pin") -> None:
        """Initialize the Button sensor with the specified GPIO pins."""
        self._pin_c = digitalio.DigitalInOut(pin_c)
        self._pin_c.direction = digitalio.Direction.INPUT
        self._pin_c.pull = digitalio.Pull.UP
        #
        self._pin_d = digitalio.DigitalInOut(pin_d)
        self._pin_d.direction = digitalio.Direction.INPUT
        self._pin_d.pull = digitalio.Pull.UP

    def deinit(self) -> None:
        """Release the GPIO pins."""
        self._pin_c.deinit()
        self._pin_d.deinit()

    def __enter__(self) -> "Button":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.deinit()

    @property
    def C_is_pressed(self) -> bool:
        """
        Check if button C is pressed (and D is not pressed).

        Returns:
            True if C is pressed and D is not pressed, False otherwise.
        """
        return not self._pin_c.value and self._pin_d.value

    @property
    def D_is_pressed(self) -> bool:
        """
        Check if button D is pressed (and C is not pressed).

        Returns:
            True if D is pressed and C is not pressed, False otherwise.
        """
        return not self._pin_d.value and self._pin_c.value

    @property
    def CD_is_pressed(self) -> bool:
        """
        Check if both buttons C and D are pressed simultaneously.

        Returns:
            True if both C and D are pressed, False otherwise.
        """
        return not self._pin_c.value and not self._pin_d.value

    @property
    def C_value(self) -> bool:
        """
        Value of button C only (True when pressed).
        Returns:
            True if C is pressed, False otherwise.
        """
        return not self._pin_c.value

    @property
    def D_value(self) -> bool:
        """
        Value of button D only (True when pressed).
        Returns:
            True if D is pressed, False otherwise.
        """
        return not self._pin_d.value

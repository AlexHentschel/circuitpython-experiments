"""
ElecFreaks PlanetX push-button module: buttons C and D.

Pass ``port=J3`` (or another ``planetx.Port``) or ``c_pin`` / ``d_pin``.
Required when ``event_queue`` is omitted: the RJ11 jack is wiring, not a board
default. Two modules on two jacks are two instances; C/D names are local to each.
"""

from __future__ import annotations

try:
    from typing import Callable
except ImportError:
    pass

from buttons import ButtonPair, PushButtonBase


class PlanetXButtonSensor(ButtonPair):
    """ElecFreaks PlanetX push-button module: C and D.

    Pass ``port=J3`` or ``c_pin`` / ``d_pin``. J3 silk P13/P14 is C then D.
    """

    def __init__(self, c_pin=None, d_pin=None, *, port=None, event_queue=None) -> None:
        if event_queue is None:
            if port is not None:
                if c_pin is not None or d_pin is not None:
                    raise ValueError("pass paramter `port` or paramter pair `(c_pin and d_pin)`, not both")
                c_pin, d_pin = port.pins
            elif c_pin is None or d_pin is None:
                raise ValueError("port= or c_pin and d_pin are required when event_queue is omitted")
        super().__init__(c_pin, d_pin, event_queue=event_queue)

    # Pair slots: C is left (key_number 0), D is right (key_number 1).
    @property
    def c(self) -> PushButtonBase:
        return self.left

    @property
    def d(self) -> PushButtonBase:
        return self.right

    def on_c_pressed(self, handler: Callable[[], None]) -> None:
        self.left.on_pressed(handler)

    def on_d_pressed(self, handler: Callable[[], None]) -> None:
        self.right.on_pressed(handler)

    def on_c_released(self, handler: Callable[[], None]) -> None:
        self.left.on_released(handler)

    def on_d_released(self, handler: Callable[[], None]) -> None:
        self.right.on_released(handler)

    def clear_c(self) -> None:
        self.left.clear()

    def clear_d(self) -> None:
        self.right.clear()

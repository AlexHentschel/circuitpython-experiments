"""
ElecFreaks PlanetX push-button module: C (left) and D (right).

``c_pin`` / ``d_pin`` are required when ``event_queue`` is omitted: the
RJ11 port is wiring, not a board default. Two modules on two ports are
two instances; C/D names are local to each.

Subclass of ``buttons.ButtonPair`` (one 2-pin scanner). Host tests inject
``event_queue=`` and skip ``keypad``.
"""

from __future__ import annotations

try:
    from typing import Callable
except ImportError:
    pass

from buttons import ButtonPair, PushButtonBase


class PlanetXButtonSensor(ButtonPair):
    """ElecFreaks PlanetX push-button module: C (left) and D (right).

    ``c_pin`` / ``d_pin`` are required when ``event_queue`` is omitted: the
    RJ11 port is wiring, not a board default. Two modules on two ports are
    two instances; C/D names are local to each.
    """

    def __init__(self, c_pin=None, d_pin=None, *, event_queue=None) -> None:
        if event_queue is None and (c_pin is None or d_pin is None):
            raise ValueError("c_pin and d_pin are required when event_queue is omitted")
        super().__init__(c_pin, d_pin, event_queue=event_queue)

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

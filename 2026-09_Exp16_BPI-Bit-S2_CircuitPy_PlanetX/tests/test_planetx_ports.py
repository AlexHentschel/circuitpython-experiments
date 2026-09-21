"""Nezha2 jack map (J1–J4 + shared I2C): host-checkable without ``board`` / ``keypad``."""

from planetx.ports import I2C, I2CBus, J1, J2, J3, J4, Port
from planetx.button import PlanetXButtonSensor

import pytest


def test_j_port_p_numbers_match_nezha_then_goldfinger():
    """Jack P-numbers are ElecFreaks order, analog on J1/J2 only.

    - Covers: swapped P13/P14, analog assigned to J3, or GPIO numbers stored as P-numbers.
    - How: ``J1.p_numbers == (1, 8)`` … ``J3.p_numbers == (13, 14)``; analog_p_number only on J1/J2.
    """
    assert J1.name == "J1" and J1.p_numbers == (1, 8) and J1.analog_p_number == 1
    assert J2.name == "J2" and J2.p_numbers == (2, 12) and J2.analog_p_number == 2
    assert J3.name == "J3" and J3.p_numbers == (13, 14) and J3.analog_p_number is None
    assert J4.name == "J4" and J4.p_numbers == (15, 16) and J4.analog_p_number is None


def test_i2c_bus_is_shared_p19_scl_p20_sda():
    """All Nezha2 IIC jacks are one bus: P19 = SCL, P20 = SDA.

    - Covers: treating IIC as four independent buses, or swapping SCL/SDA P-numbers.
    - How: ``I2C.p_number_scl == 19`` and ``I2C.p_number_sda == 20``; instance of ``I2CBus``.
    """
    assert isinstance(I2C, I2CBus)
    assert I2C.name == "I2C"
    assert I2C.p_number_scl == 19
    assert I2C.p_number_sda == 20


def test_port_instances_are_port():
    """J1–J4 are ``Port`` objects, not raw tuples.

    - Covers: exporting bare pin tuples that drivers cannot share.
    - How: ``isinstance(J3, Port)``.
    """
    for jack in (J1, J2, J3, J4):
        assert isinstance(jack, Port)


def test_button_rejects_port_and_pins_together():
    """``port=`` and ``c_pin``/``d_pin`` together raise.

    - Covers: silently ignoring one of the two wiring sources.
    - How: ``event_queue`` omitted so the check runs; dummy pins; ``ValueError``.
    """
    with pytest.raises(ValueError, match="not both"):
        PlanetXButtonSensor(c_pin=object(), d_pin=object(), port=J3)

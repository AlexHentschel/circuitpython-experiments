"""Nezha2 RJ11 jacks as BPI-Bit-S2 CircuitPython pins.

Two-step map, hard-coded for this board:

1. Nezha2 jack → micro:bit edge P-numbers (ElecFreaks Nezha 202 jack figures).
2. Goldfinger Pn → ESP32-S2 GPIO (`Notes/bpi_bit_v2_goldfinger.jpg`). CircuitPython
   ``board.IOn`` is goldfinger Pn, not ESP32 GPIO n (``IO13`` is GPIO36).

GPIO jacks J1–J4 each have their own pair. All IIC jacks are one shared bus
(P19 = SCL, P20 = SDA), not four independent I2C buses.

Signal order on J3–J4 is ElecFreaks driver order (J3: P13 then P14 = PlanetX
C then D), not the top-to-bottom stack on the jack drawing.

J1/J2 carry one analog-capable wire (micro:bit P1 / P2). J3/J4 are digital.

``Port`` and ``I2CBus`` bind ``board.IOn`` from silk P-numbers in ``__init__``.
Host ``import board`` raises ``ImportError`` (Blinka); constructors catch that so
``J1``–``J4`` and ``I2C`` can exist at import for silk checks.
"""

from __future__ import annotations


class Port:
    """One Nezha2 RJ11 jack: two signal wires, identified by silk P-numbers.

    ``silk`` is ``(p_a, p_b)`` in ElecFreaks order. ``analog_silk`` is the
    analog-capable P-number on J1/J2, or None on J3/J4. ``__init__`` looks up
    ``board.IO{n}`` for those numbers.
    """

    def __init__(self, name: str, silk: tuple, analog_silk: int | None = None) -> None:
        """Bind ``board.IOn`` for ``silk`` as ``self.pins`` (and ``analog_pin`` on J1/J2)."""
        self.name = name
        self.silk = silk
        self.analog_silk = analog_silk
        try:
            import board
        except ImportError:
            # Host pytest: Blinka ``board`` raises ImportError (pkg_resources). CircuitPython firmware
            # always provides ``board``, so this return is never taken on the device. Construction still
            # succeeds so the module-level ``J1``–``J4`` objects can exist; silk attrs remain;
            # pin objects stay unbound.
            return
        self.pins = (getattr(board, f"IO{silk[0]}"), getattr(board, f"IO{silk[1]}"))
        if analog_silk is None:
            self.analog_pin = None
        else:
            self.analog_pin = getattr(board, f"IO{analog_silk}")


# Silk P-numbers from the Nezha 202 jack figure; analog = micro:bit ADC pin.
J1 = Port("J1", (1, 8), analog_silk=1)
J2 = Port("J2", (2, 12), analog_silk=2)
J3 = Port("J3", (13, 14))
J4 = Port("J4", (15, 16))


class I2CBus:
    """Shared Nezha2 IIC bus: every I2C jack is wired to the same SCL/SDA pair.

    Silk P19 = SCL, P20 = SDA (Nezha 202 IIC figure). ``__init__`` looks up
    ``board.IO{n}`` from ``silk_scl`` / ``silk_sda``. On this firmware
    ``IO19`` / ``IO20`` are ``board.SCL`` / ``board.SDA``.
    """

    name = "I2C"
    silk_scl = 19  # goldfinger P19 → board.IO19 (SCL)
    silk_sda = 20  # goldfinger P20 → board.IO20 (SDA)

    def __init__(self) -> None:
        """Bind ``board.IOn`` for ``silk_scl`` / ``silk_sda`` as ``self.scl`` / ``self.sda``."""
        try:
            import board
        except ImportError:
            # Host pytest: Blinka ``board`` raises ImportError (pkg_resources). CircuitPython firmware
            # always provides ``board``, so this return is never taken on the device. Construction still
            # succeeds so the module-level ``I2C = I2CBus()`` can exist; silk class attrs remain;
            # ``scl`` / ``sda`` stay unbound.
            return
        self.scl = getattr(board, f"IO{self.silk_scl}")
        self.sda = getattr(board, f"IO{self.silk_sda}")

    @property
    def pins(self):
        """``(scl, sda)`` in CircuitPython ``busio.I2C`` argument order."""
        return (self.scl, self.sda)


I2C = I2CBus()

# Goldfinger ESP32-S2 GPIO (documentation only; drivers use board.IOn / SCL / SDA):
# P1=GPIO1  P2=GPIO2  P8=GPIO8   P12=GPIO21
# P13=GPIO36 P14=GPIO37 P15=GPIO35 P16=GPIO34
# P19=GPIO16 (SCL)  P20=GPIO15 (SDA)

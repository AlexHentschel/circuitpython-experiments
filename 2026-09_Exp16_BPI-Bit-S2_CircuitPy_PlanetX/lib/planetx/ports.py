"""PlanetX sensors, connected through the Nezha2 expansion board.

Sensors plug into Nezha2, a small white box that the BPI-Bit-S2 plugs into
via its edge connector — BananaPi calls this connector the "goldfinger". The
individual pins on that connector are named after the BBC micro:bit standard
this board is shaped like: P0, P1, P2, ... P20 ("P" for "pin"). Nezha2 box
houses the RJ11 sockets that sensors and motors actually plug into:

- Four **IO ports**, J1-J4, on the right side.
- Four **IIC ports** (blue marking) on the left side — wired together
  internally as one shared bus, so a sensor works the same in any of the four.
- Four **motor connectors**, M1-M4 (red marking) at the bottom of the Nezha2;
  NOT handled by this file.

    PlanetX sensor  ━━RJ11-cable━━▶  Nezha2 port  ━━edge connector━━▶  BPI-Bit-S2

Plug a sensor into a port, then refer to that same port by name in code:

    from planetx import J3, PlanetXButtonSensor

    buttons = PlanetXButtonSensor(port=J3)

J1 and J2 accept analog sensors (yellow marking — e.g. light, sound) as well
as digital ones; J3 and J4 are digital-only (red marking).
"""

from __future__ import annotations

"""
--- Maintainer notes (not needed to use this module) --- 

Two-step translation, hard-coded for the BPI-Bit-S2 + Nezha2 pairing:
1. Nezha2 port -> P-number (the BBC micro:bit edge-connector standard;
   ELECFREAKS' Nezha2 jack-figure diagrams document Nezha2's own jack wiring
   in that same micro:bit namespace).
2. Same P-number -> BPI-Bit-S2 goldfinger pad -> `board.IOn`
   (`Notes/bpi_bit_v2_goldfinger.jpg` — "goldfinger" is this board's own
   implementation of that same edge-connector standard). `board.IOn` is
   goldfinger Pn, **not** ESP32 GPIO n (`IO13` is GPIO36) — do not conflate
   those two when extending this file.

All Nezha2 IIC ports are **one** shared I2C bus (P19=SCL, P20=SDA). To
control all four IIC interfaces on the Nezha2, you only need a single
`I2CBus` object. Constructors tolerate `import board` failing (host tests
without hardware) so `J1`-`J4`/`I2C` still exist for tests that only check
port wiring, not live pins.
"""


class Port:
    """One Nezha2 RJ11 jack: two signal wires, voltage and ground. We only care about the
    signal wires, identified by their P-numbers on the micro:bit edge connector (wiring per
    ElecFreaks' Nezha v2 documentation; see module docstring).

    The wiring from an RJ11 jack to the edge connector is provided by ElecFreaks in their
    Nezha v2 documentation. ``J1``-``J4`` below are ready-made instances. But you can also
    create your own instances by configuring the pair signal wires: the paramter
    ```p_numbers`` has the format ``(p_a, p_b)`` where p_a, p_b are integers corresponding
    to the P-numbers in the ElecFreaks documentation. The parameter `analog_p_number`` is
    the analog-capable P-number on J1/J2, or None on J3/J4.
    """

    def __init__(self, name: str, p_numbers: tuple, analog_p_number: int | None = None) -> None:
        # p_numbers = (p_a, p_b): P-numbers per ElecFreaks' Nezha v2 wiring (sources
        # at the J1-J4 definitions below). analog_p_number: the analog-capable
        # P-number on J1/J2, None on J3/J4. Binds board.IO{n} for those numbers
        # as self.pins / self.analog_pin.
        self.name = name
        self.p_numbers = p_numbers
        self.analog_p_number = analog_p_number
        try:
            import board
        except ImportError:
            # Host pytest: Blinka ``board`` raises ImportError (pkg_resources). CircuitPython firmware
            # always provides ``board``, so this return is never taken on the device. Construction still
            # succeeds so the module-level ``J1``–``J4`` objects can exist; ``p_numbers``/``analog_p_number``
            # attrs remain; pin objects stay unbound.
            return
        self.pins = (getattr(board, f"IO{p_numbers[0]}"), getattr(board, f"IO{p_numbers[1]}"))
        if analog_p_number is None:
            self.analog_pin = None
        else:
            self.analog_pin = getattr(board, f"IO{analog_p_number}")


# Mapping from the Nezha2 GPIO ports to their P-numbers on the micro:bit edge
# connector (this board's "goldfinger" — see the module docstring). Sources
# • Nezha V2 wiki page, section "Introduction to interface pins":
#   https://wiki.elecfreaks.com/en/microbit/expansion-board/nezha-v2/#introduction-to-interface-pins
# • ElecFreaks' own PlanetX_MicroPython driver hard-codes mapping
#   J1=pin1/pin8, J2=pin2/pin12, J3=pin13/pin14, J4=pin15/pin16 in
#   button.py's BUTTON.__init__ (commit 268740c):
J1 = Port("J1", (1, 8), analog_p_number=1)
J2 = Port("J2", (2, 12), analog_p_number=2)
J3 = Port("J3", (13, 14))
J4 = Port("J4", (15, 16))


class I2CBus:
    """Shared Nezha2 IIC bus: every I2C port is wired to the same SCL/SDA pair.

    ``I2C`` below is a ready-made instance for the Nezha v2 board. Pass its ``pins``
    to build an I2C sensor's bus. Works the same regardless of which of the four IIC
    ports a sensor is plugged into.
    """

    name = "I2C"
    # P19 = SCL, P20 = SDA on the micro:bit edge connector (Nezha 202 IIC figure).
    p_number_scl = 19  # goldfinger P19 -> board.IO19 (SCL)
    p_number_sda = 20  # goldfinger P20 -> board.IO20 (SDA)

    def __init__(self) -> None:
        # Binds board.IO{n} for p_number_scl / p_number_sda as self.scl / self.sda.
        # On this firmware IO19 / IO20 are board.SCL / board.SDA.
        try:
            import board
        except ImportError:
            # Host pytest: Blinka ``board`` raises ImportError (pkg_resources). CircuitPython firmware
            # always provides ``board``, so this return is never taken on the device. Construction still
            # succeeds so the module-level ``I2C = I2CBus()`` can exist; ``p_number_scl``/``p_number_sda``
            # class attrs remain; ``scl`` / ``sda`` stay unbound.
            return
        self.scl = getattr(board, f"IO{self.p_number_scl}")
        self.sda = getattr(board, f"IO{self.p_number_sda}")

    @property
    def pins(self):
        """``(scl, sda)`` in CircuitPython ``busio.I2C`` argument order."""
        return (self.scl, self.sda)


I2C = I2CBus()

# Goldfinger ESP32-S2 GPIO (documentation only; drivers use board.IOn / SCL / SDA):
# P1=GPIO1  P2=GPIO2  P8=GPIO8   P12=GPIO21
# P13=GPIO36 P14=GPIO37 P15=GPIO35 P16=GPIO34
# P19=GPIO16 (SCL)  P20=GPIO15 (SDA)

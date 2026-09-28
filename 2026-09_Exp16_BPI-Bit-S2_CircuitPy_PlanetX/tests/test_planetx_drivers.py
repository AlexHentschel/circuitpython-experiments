"""Host checks for the light sensor, rainbow ring, smart motor, and crash sensor.

Does not import ``board``, ``neopixel``, ``analogio``, or ``display.core``.
"""

import ast
import asyncio
import pathlib

import pytest

from planetx import (
    CLOCKWISE,
    COUNTERCLOCKWISE,
    DEGREES,
    J1,
    J2,
    J3,
    M1,
    M4,
    SHORTEST,
    PlanetXCrashSensor,
    PlanetXLightSensor,
    PlanetXRainbowRing,
    PlanetXSmartMotor,
)
from planetx.light import _counts_to_lux, _u16_to_counts
from planetx.motor import _fill, _path_byte, firmware_degrees_from, laps_per_sec
from planetx.neopixel import RING_PIXELS, hsl
from planetx.ports import M2, M3, MotorPort


class FakeEvent:
    def __init__(self, key_number, pressed):
        self.key_number = key_number
        self.pressed = pressed


class FakeEventQueue:
    def __init__(self):
        self._pending = []

    def send(self, event):
        self._pending.append(event)

    def get(self):
        if not self._pending:
            return None
        return self._pending.pop(0)


class FakeBus:
    """Records 8-byte frames. ``reads`` are consumed by encoder reads."""

    def __init__(self, reads=None):
        self.writes = []
        self.reads = list(reads or [])

    def write(self, buf):
        self.writes.append(bytes(buf))

    def readinto(self, buf):
        payload = self.reads.pop(0) if self.reads else b"\x00\x00\x00\x00"
        for i in range(len(buf)):
            buf[i] = payload[i] if i < len(payload) else 0


class FakePixels:
    def __init__(self):
        self.brightness = 0.2
        self.colors = {}
        self.shows = 0
        self.filled = None

    def fill(self, color):
        self.filled = color

    def show(self):
        self.shows += 1

    def __setitem__(self, index, color):
        self.colors[index] = color


class StubPort:
    def __init__(self):
        self.pins = ("analog", "digital")
        self.p_numbers = (2, 12)


def _tenths(degrees):
    return (degrees * 10).to_bytes(4, "little", signed=True)


def test_lux_curve_matches_makecode_points():
    """Integer lux curve at the MakeCode anchors.

    - Covers: a 100-sample average, a float curve, or the MicroPython dark floor of 45.
    - How: ``_counts_to_lux`` at 0, 100, 200, and 1023.
    """
    assert _counts_to_lux(0) == 0
    assert _counts_to_lux(100) == 800
    assert _counts_to_lux(200) == 1600
    assert _counts_to_lux(1023) == 14000


def test_u16_full_scale_is_1023_counts():
    """65535 maps to 1023 counts, and that is 14000 lux.

    - Covers: treating AnalogIn.value as already 0..1023.
    - How: ``_u16_to_counts(65535)`` and ``lux()`` with a reader of 65535.
    """
    assert _u16_to_counts(65535) == 1023
    assert _u16_to_counts(0) == 0
    light = PlanetXLightSensor(port=J1, reader=lambda: 65535)
    assert light.lux() == 14000


def test_light_sensor_rejects_digital_jack():
    """J3 has no analog wire.

    - Covers: constructing a light sensor on J3/J4.
    - How: ``PlanetXLightSensor(port=J3)`` raises ``ValueError``.
    """
    with pytest.raises(ValueError, match="J1 or J2"):
        PlanetXLightSensor(port=J3)


def test_ring_uses_second_wire_and_eight_pixels():
    """The ring's data pin is ``port.pins[1]`` and the length is 8.

    - Covers: using the analog wire, or a strip length other than 8.
    - How: stub port; ``_pin`` is the second entry; ``count == RING_PIXELS == 8``.
    J2's second P-number is 12.
    """
    pixels = FakePixels()
    ring = PlanetXRainbowRing(port=StubPort(), pixels=pixels)
    assert ring._pin == "digital"
    assert ring.count == 8
    assert RING_PIXELS == 8
    assert J2.p_numbers[1] == 12
    assert J1.p_numbers[1] == 8
    ring.fill((255, 150, 0))
    assert pixels.filled == (255, 150, 0)
    assert pixels.shows == 1
    ring.off()
    assert pixels.filled == (0, 0, 0)


def test_hsl_primary_colors():
    """``hsl`` builds one RGB tuple. Red at hue 0, green at hue 120.

    - Covers: a strip-wide hue mode, or channels left in 0..100.
    - How: full saturation, luminosity 50.
    """
    assert hsl(0, 100, 50) == (255, 0, 0)
    assert hsl(120, 100, 50) == (0, 255, 0)


def test_motor_ports_are_indexes():
    """M1–M4 carry motor numbers 1–4 and are not jacks.

    - Covers: storing a GPIO pin on a motor port.
    - How: ``index`` and ``isinstance(..., MotorPort)``.
    """
    assert (M1.index, M2.index, M3.index, M4.index) == (1, 2, 3, 4)
    assert isinstance(M4, MotorPort)
    assert not hasattr(M4, "pins")


def test_absolute_path_cw_is_not_relative_cw():
    """Clockwise on an absolute move is path byte 2, not 1.

    - Covers: copying the MicroPython absolute-move enum (CW=1).
    - How: ``_path_byte(CLOCKWISE) == 2`` and ``_path_byte(SHORTEST) == 1``.
    """
    assert _path_byte(SHORTEST) == 1
    assert _path_byte(CLOCKWISE) == 2
    assert _path_byte(COUNTERCLOCKWISE) == 3
    buf = bytearray(8)
    _fill(buf, 4, 0, 0x5D, 0, _path_byte(CLOCKWISE), 90)
    assert bytes(buf) == bytes([0xFF, 0xF9, 4, 0, 0x5D, 0, 2, 90])


def test_relative_move_frame_is_cw_then_degrees():
    """A 10° clockwise move is opcode 0x70, direction 1, mode degrees.

    - Covers: swapped direction, or mode numbering from the absolute command.
    - How: ``_fill`` of motor 4, dir 1, opcode 0x70, mode ``DEGREES``, value 10.
    """
    buf = bytearray(8)
    _fill(buf, 4, CLOCKWISE, 0x70, 0, DEGREES, 10)
    assert bytes(buf) == bytes([0xFF, 0xF9, 4, 1, 0x70, 0, DEGREES, 10])


def test_no_relative_angle_method():
    """Students read the bookmarked coordinate with ``angle`` only.

    - Covers: a second ``relative_angle`` that repeats ``angle``.
    - How: the name is absent on the class.
    """
    assert not hasattr(PlanetXSmartMotor, "relative_angle")


def test_set_zero_shifts_bookmark_without_encoder_opcode():
    """``set_zero(45)`` stops the motor and does not send opcode 0x1D.

    - Covers: sending the firmware zero command from ``set_zero``.
    - How: the only write is opcode ``0x5F``.
    """
    bus = FakeBus(reads=[_tenths(55)])
    motor = PlanetXSmartMotor(port=M4, bus=bus, settle_s=0, poll_s=0)
    motor.set_zero(45)
    assert bus.writes[-1][4] == 0x5F
    assert all(frame[4] != 0x1D for frame in bus.writes)


@pytest.mark.asyncio
async def test_go_to_adds_bookmark_to_firmware_angle():
    """``go_to(10)`` after ``set_zero(45)`` commands firmware angle 55.

    - Covers: sending the student angle straight to 0x5D.
    - How: the 0x5D frame's split 16-bit value is 55; the wait read reports 55°.
    """
    bus = FakeBus(reads=[_tenths(55)])
    motor = PlanetXSmartMotor(port=M4, bus=bus, settle_s=0, poll_s=0)
    motor.set_zero(45)
    token = await motor.go_to(10)
    frame = next(item for item in reversed(bus.writes) if item[4] == 0x5D)
    assert frame[4] == 0x5D
    assert frame[6] == _path_byte(SHORTEST)
    assert ((frame[5] << 8) | frame[7]) == 55
    assert token.is_expired is False


def test_stop_expires_start_token_with_one_stop_frame():
    """``stop`` expires the token from ``start`` and writes opcode 0x5F once.

    - Covers: ``stop`` returning a token, or a waiter sending a second stop.
    - How: one 0x60 frame, then one 0x5F frame; the start token is expired.
    """
    bus = FakeBus()
    motor = PlanetXSmartMotor(port=M1, bus=bus, settle_s=0)
    token = motor.start(10, CLOCKWISE)
    assert token.is_expired is False
    assert bus.writes[-1][4] == 0x60
    assert bus.writes[-1][3] == CLOCKWISE
    assert bus.writes[-1][5] == 10
    motor.stop()
    assert token.is_expired is True
    assert bus.writes[-1][4] == 0x5F
    assert [frame[4] for frame in bus.writes] == [0x60, 0x5F]
    assert motor.stop() is None


def test_firmware_tenths_round_and_speed_formula():
    """Encoder tenths round to degrees. Speed uses the MakeCode laps/sec formula.

    - Covers: truncating tenths, or the MicroPython ``raw * 0.0926`` speed.
    - How: 555 tenths → 56°; raw 360 → 1.0 laps/s.
    """
    assert firmware_degrees_from((555).to_bytes(4, "little", signed=True)) == 56
    assert laps_per_sec(360) == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_crash_press_fires():
    """A press on the crash sensor runs the handler.

    - Covers: the sensor not forwarding to ``Button.run``.
    - How: fake event queue; one press; handler appends ``"hit"``.
    """
    queue = FakeEventQueue()
    crash = PlanetXCrashSensor(event_queue=queue)
    fired = []
    crash.on_pressed(lambda: fired.append("hit"))
    queue.send(FakeEvent(0, pressed=True))
    task = asyncio.create_task(crash.run())
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert fired == ["hit"]


def test_crash_sensor_source_uses_second_wire():
    """The crash sensor passes ``port.pins[1]`` to ``Button``.

    - Covers: binding the analog wire, or a ``digitalio`` poller.
    - How: AST of ``crash.py``; a ``Button`` call whose argument is ``port.pins`` subscript 1.
      J3's second P-number is 14.
    """
    path = pathlib.Path(__file__).resolve().parent.parent / "lib" / "planetx" / "crash.py"
    tree = ast.parse(path.read_text())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Button":
            if node.args and isinstance(node.args[0], ast.Subscript):
                sl = node.args[0].slice
                value = sl.value if isinstance(sl, ast.Constant) else None
                if value == 1:
                    found = True
    assert found
    assert J3.p_numbers[1] == 14

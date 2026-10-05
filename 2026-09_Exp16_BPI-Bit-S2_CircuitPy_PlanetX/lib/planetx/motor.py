"""PlanetX smart motor on a Nezha2 motor connector (M1–M4).

The motor turns on its own after you send a command. ``turn`` and ``go_to``
wait until that motion finishes, and other tasks keep running during the wait.
``stop`` holds the shaft where it is.

    from planetx import M4, CLOCKWISE, PlanetXSmartMotor

    motor = PlanetXSmartMotor(port=M4)
    motor.start(10, CLOCKWISE)
    motor.stop()

    token = await motor.turn(340, CLOCKWISE)
    if token.is_expired:
        # stop(), start(), turn(), or go_to() took the motor
"""

from __future__ import annotations

import time

from .ports import MotorPort

# Student names. On a relative move the wire uses 1 and 2. On an absolute
# move the wire uses a different numbering; ``_path_byte`` translates.
CLOCKWISE = 1
COUNTERCLOCKWISE = 2
SHORTEST = 0

DEGREES = 2
TURNS = 1
SECONDS = 3

_ADDR = 0x10
_ARRIVED = 3  # degrees; the motor's stated accuracy is about 3°


class Token:
    """Marks one motor command.

    ``is_expired`` becomes true when a later ``stop``, ``start``, ``turn``,
    ``go_to``, ``go_zero``, or ``set_zero`` takes the motor. Check it
    immediately after ``await``. A later command can still set it after a
    move has already finished.
    """

    def __init__(self) -> None:
        self._is_expired = False

    @property
    def is_expired(self) -> bool:
        """True once a later command has taken the motor."""
        return self._is_expired


def _fill(buf, motor, arg_a, opcode, high, mode, low) -> None:
    buf[0] = 0xFF
    buf[1] = 0xF9
    buf[2] = motor & 0xFF
    buf[3] = arg_a & 0xFF
    buf[4] = opcode & 0xFF
    buf[5] = high & 0xFF
    buf[6] = mode & 0xFF
    buf[7] = low & 0xFF


def _path_byte(direction: int) -> int:
    # MakeCode absolute-move path: shortest=1, clockwise=2, counterclockwise=3.
    # MicroPython swaps those numbers. Relative moves use CLOCKWISE=1 directly.
    if direction == SHORTEST:
        return 1
    if direction == CLOCKWISE:
        return 2
    if direction == COUNTERCLOCKWISE:
        return 3
    raise ValueError("direction must be SHORTEST, CLOCKWISE, or COUNTERCLOCKWISE")


def _move_dir(direction: int) -> int:
    if direction == CLOCKWISE:
        return 1
    if direction == COUNTERCLOCKWISE:
        return 2
    raise ValueError("direction must be CLOCKWISE or COUNTERCLOCKWISE")


def _check_speed(speed: int) -> int:
    if speed < 0 or speed > 100:
        raise ValueError("speed must be 0..100")
    return speed


def firmware_degrees_from(buf) -> int:
    """Whole degrees 0..359 from a 4-byte little-endian encoder reading.

    The motor reports tenths of a degree. Negative readings wrap into 0..359.9
    before rounding to the nearest degree.
    """
    raw = int.from_bytes(buf[:4], "little", signed=True)
    tenths = raw % 3600
    if tenths < 0:
        tenths += 3600
    degrees = (tenths + 5) // 10
    if degrees >= 360:
        return 0
    return degrees


def laps_per_sec(raw: int) -> float:
    """MakeCode speed block: ``floor(raw / 3.6) * 0.01`` laps per second."""
    if raw < 0:
        raw = 0
    return (raw * 10 // 36) * 0.01


class PlanetXSmartMotor:
    """One PlanetX smart motor on M1, M2, M3, or M4.

    ``angle()`` is degrees from a zero you can move with ``set_zero``.
    Until you call ``set_zero``, zero is the pose at power-on.
    ``go_to`` uses that same zero. ``turn`` is a step from wherever the
    shaft is now.

        motor = PlanetXSmartMotor(port=M4)
        motor.start(10, CLOCKWISE)
        motor.stop()

        token = await motor.turn(340, CLOCKWISE)
        if token.is_expired:
            # stop(), start(), turn(), or go_to() took the motor

    ``is_expired`` means another command took over. If it is still false,
    the wait ended: the shaft arrived, or the motor did not finish in time.
    Read ``angle()`` when you need to tell those apart.
    """

    def __init__(self, *, port: MotorPort, bus=None, settle_s: float = 0.004, poll_s: float = 0.02) -> None:
        # ``bus``, ``settle_s``, and ``poll_s`` are test hooks. Students pass
        # ``port=`` only. ``settle_s`` is the no-yield pause after a read opcode.
        self._index = port.index
        self._bookmark = 0
        self._token = Token()
        self._buf = bytearray(8)
        self._read4 = bytearray(4)
        self._bus = bus
        self._settle_s = settle_s
        # Test hook, stored once as whole milliseconds. ``sleep_ms`` clamps a negative to 0.
        self._poll_ms = int(poll_s * 1000)
        self._limit = 100

    def _claim(self) -> Token:
        # Expire first, then the caller writes its own frame. A waiter that
        # sees expiry must not send stop: that would cancel this new command.
        self._token._is_expired = True
        self._token = Token()
        return self._token

    def _ensure_bus(self):
        if self._bus is None:
            import busio

            from .ports import I2C

            self._bus = busio.I2C(I2C.scl, I2C.sda, frequency=100000)
        return self._bus

    def _send(self) -> None:
        bus = self._ensure_bus()
        if hasattr(bus, "try_lock"):
            while not bus.try_lock():
                time.sleep(0.001)
            try:
                bus.writeto(_ADDR, self._buf)
            finally:
                bus.unlock()
        else:
            bus.write(self._buf)

    def _read_encoder(self, opcode: int, nbytes: int) -> None:
        # Hold the bus across the settle. Do not await here: the board
        # mis-reads if another command lands in this window.
        _fill(self._buf, self._index, 0, opcode, 0, 0xF5, 0)
        bus = self._ensure_bus()
        if hasattr(bus, "try_lock"):
            while not bus.try_lock():
                time.sleep(0.001)
            try:
                bus.writeto(_ADDR, self._buf)
                time.sleep(self._settle_s)
                bus.readfrom_into(_ADDR, self._read4)
            finally:
                bus.unlock()
        else:
            bus.write(self._buf)
            if self._settle_s:
                time.sleep(self._settle_s)
            bus.readinto(self._read4)

    def _firmware_degrees(self) -> int:
        self._read_encoder(0x46, 4)
        return firmware_degrees_from(self._read4)

    def _student(self, firmware: int) -> int:
        return (firmware - self._bookmark) % 360

    def _to_firmware(self, student: int) -> int:
        return (self._bookmark + (student % 360)) % 360

    def _send_limit(self, speed: int) -> None:
        speed = _check_speed(speed)
        self._limit = speed
        value = speed * 9
        _fill(self._buf, 0, 0, 0x77, (value >> 8) & 0xFF, 0, value & 0xFF)
        self._send()

    def _close(self, student: int, target: int) -> bool:
        gap = (student - target) % 360
        if gap > 180:
            gap = 360 - gap
        return gap <= _ARRIVED

    async def _wait_student(self, token: Token, target: int) -> None:
        import asyncio

        deg_per_s = self._limit * 9
        if deg_per_s < 1:
            deg_per_s = 1
        deadline = time.monotonic() + 0.5 + (360 * 2) / deg_per_s
        while not token.is_expired:
            if self._close(self._student(self._firmware_degrees()), target):
                return
            if time.monotonic() >= deadline:
                return
            await asyncio.sleep_ms(self._poll_ms)

    async def _wait_delta(self, token: Token, start: int, amount: int, direction: int) -> None:
        import asyncio

        prev = start
        accum = 0
        deg_per_s = self._limit * 9
        if deg_per_s < 1:
            deg_per_s = 1
        deadline = time.monotonic() + 0.5 + (amount * 2) / deg_per_s
        while not token.is_expired:
            now = self._firmware_degrees()
            # Clockwise is assumed to increase the firmware count.
            if direction == CLOCKWISE:
                step = (now - prev) % 360
            else:
                step = (prev - now) % 360
            accum += step
            prev = now
            if accum + _ARRIVED >= amount:
                return
            if time.monotonic() >= deadline:
                return
            await asyncio.sleep_ms(self._poll_ms)

    async def _wait_seconds(self, token: Token, seconds: float) -> None:
        import asyncio

        deadline = time.monotonic() + seconds
        while not token.is_expired:
            if time.monotonic() >= deadline:
                return
            await asyncio.sleep_ms(self._poll_ms)

    def angle(self) -> int:
        """Degrees from the bookmarked zero, 0–359.

        Does not stop or replace a move that is already running.
        """
        return self._student(self._firmware_degrees())

    def speed(self) -> float:
        """How fast the shaft is turning, in laps per second.

        Does not stop or replace a move that is already running.
        """
        self._read_encoder(0x47, 2)
        raw = self._read4[0] | (self._read4[1] << 8)
        return laps_per_sec(raw)

    def stop(self) -> None:
        """Hold the shaft where it is.

        A ``turn`` or ``go_to`` that was waiting ends, and its token's
        ``is_expired`` becomes true.
        """
        self._claim()
        _fill(self._buf, self._index, 0, 0x5F, 0, 0xF5, 0)
        self._send()

    def set_zero(self, degrees: int | None = None) -> None:
        """Move the zero mark.

        With no argument, the pose the shaft is in right now becomes 0.
        ``set_zero(45)`` makes the pose that currently reads 45° the new
        zero. The shaft is not driven there. This also stops the motor,
        the same way ``stop`` does.
        """
        self._claim()
        _fill(self._buf, self._index, 0, 0x5F, 0, 0xF5, 0)
        self._send()
        if degrees is None:
            self._bookmark = self._firmware_degrees()
        else:
            self._bookmark = (self._bookmark + (degrees % 360)) % 360

    def encoder_zero(self) -> None:
        """Send the motor's own "set to zero" command.

        To remember a pose and come back later, use ``set_zero`` and
        ``go_zero`` instead. This command can change the number ``angle()``
        returns.
        """
        # Opcode 0x1D. Whether the shaft also moves is defined by the motor
        # firmware; bookmark is cleared so student 0 matches a firmware origin
        # of 0 after the command.
        self._claim()
        _fill(self._buf, self._index, 0, 0x1D, 0, 0xF5, 0)
        self._send()
        self._bookmark = 0

    def start(self, speed: int, direction: int) -> Token:
        """Start turning and return immediately.

        ``speed`` is 0–100. The shaft keeps going until ``stop`` or another
        move. The returned token's ``is_expired`` becomes true when that happens.
        """
        token = self._claim()
        _fill(self._buf, self._index, _move_dir(direction), 0x60, _check_speed(speed), 0xF5, 0)
        self._send()
        return token

    async def turn(self, amount: int, direction: int, *, speed: int = 100, unit: int = DEGREES) -> Token:
        """Turn ``amount`` from the current pose, and wait until it finishes.

        ``unit`` is ``DEGREES``, ``TURNS``, or ``SECONDS``. ``speed`` is 0–100.
        Returns a token. ``is_expired`` means another command took over.
        """
        if amount < 0:
            raise ValueError("amount must be >= 0")
        if unit not in (DEGREES, TURNS, SECONDS):
            raise ValueError("unit must be DEGREES, TURNS, or SECONDS")
        direction = _move_dir(direction)
        token = self._claim()
        self._send_limit(speed)
        if unit == SECONDS:
            _fill(self._buf, self._index, direction, 0x70, (amount >> 8) & 0xFF, SECONDS, amount & 0xFF)
            self._send()
            await self._wait_seconds(token, amount)
            return token
        if unit == TURNS:
            degrees = amount * 360
            mode = TURNS
            wire_amount = amount
        else:
            degrees = amount
            mode = DEGREES
            wire_amount = amount
        start = self._firmware_degrees()
        _fill(
            self._buf,
            self._index,
            direction,
            0x70,
            (wire_amount >> 8) & 0xFF,
            mode,
            wire_amount & 0xFF,
        )
        self._send()
        await self._wait_delta(token, start, degrees, direction)
        return token

    async def go_to(self, angle: int, direction: int = SHORTEST, *, speed: int | None = None) -> Token:
        """Turn to ``angle`` degrees from the bookmarked zero, and wait.

        ``direction`` defaults to the shortest way. Pass ``CLOCKWISE`` or
        ``COUNTERCLOCKWISE`` to force a direction. ``speed`` (0–100) changes
        how fast; leave it out to keep the previous speed.
        """
        token = self._claim()
        if speed is not None:
            self._send_limit(speed)
        firmware = self._to_firmware(angle)
        path = _path_byte(direction)
        _fill(self._buf, self._index, 0, 0x5D, (firmware >> 8) & 0xFF, path, firmware & 0xFF)
        self._send()
        await self._wait_student(token, angle % 360)
        return token

    async def go_zero(self, direction: int = SHORTEST, *, speed: int | None = None) -> Token:
        """Turn to the bookmarked zero, and wait.

        Same direction and speed choices as ``go_to``.
        """
        return await self.go_to(0, direction, speed=speed)

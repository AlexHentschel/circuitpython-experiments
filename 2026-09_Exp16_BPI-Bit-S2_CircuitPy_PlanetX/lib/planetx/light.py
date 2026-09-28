"""PlanetX light sensor: how bright it is, in lux.

Plug the sensor into J1 or J2 (the yellow analog ports):

    from planetx import J1, PlanetXLightSensor

    light = PlanetXLightSensor(port=J1)
    print(light.lux())

``lux()`` is a whole number, 0 in the dark and about 14000 in bright light.
The lighthouse treats a reading below 100 as dark.
"""

from __future__ import annotations

from .ports import Port


def _u16_to_counts(raw: int) -> int:
    # CircuitPython AnalogIn.value is 0..65535. MakeCode analogReadPin is 0..1023.
    if raw < 0:
        raw = 0
    elif raw > 65535:
        raw = 65535
    return (raw * 1023) // 65535


def _counts_to_lux(counts: int) -> int:
    # MakeCode lightSensor curve, one sample, integer. counts < 200 maps
    # 0..200 → 0..1600 (×8). The rest maps 200..1023 → 1600..14000.
    # 12400/823 is (14000-1600)/(1023-200).
    if counts < 200:
        return counts * 8
    return 1600 + (counts - 200) * 12400 // 823


class PlanetXLightSensor:
    """One PlanetX light sensor on J1 or J2.

        light = PlanetXLightSensor(port=J1)
        light.lux()
    """

    def __init__(self, *, port: Port, reader=None) -> None:
        # ``reader`` is a test hook: a callable returning 0..65535. Not part of
        # the student-facing construction API.
        if port.analog_p_number is None:
            raise ValueError("The light sensor needs an analog port: J1 or J2.")
        self._adc = None
        self._reader = reader
        if reader is not None:
            return
        import analogio

        self._adc = analogio.AnalogIn(port.analog_pin)

    def lux(self) -> int:
        """How bright it is, as a whole number of lux.

        0 is dark, about 14000 is bright. The lighthouse treats a reading
        below 100 as dark.

        A reading near 100 can wobble by a few tens of lux from one call to
        the next, so ``if light.lux() < 100`` can flip on and off. Use two
        limits, and wait between reads so the rest of the program keeps running:

            async def watch_daylight(light):
                dark = False
                while True:
                    level = light.lux()
                    if level < 80:
                        dark = True
                    elif level > 120:
                        dark = False
                    await asyncio.sleep(0.1)

        80 and 120 are an example gap around 100. Widen the gap if the lamp
        still flickers. Between the two limits, ``dark`` stays what it was.
        """
        if self._reader is not None:
            raw = self._reader()
        else:
            raw = self._adc.value
        return _counts_to_lux(_u16_to_counts(raw))

    def deinit(self) -> None:
        """Release the analog pin."""
        adc = self._adc
        self._adc = None
        if adc is not None:
            adc.deinit()

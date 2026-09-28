"""NeoPixel strip on a Nezha2 jack, and the 8-pixel PlanetX rainbow ring.

The ring is a strip of 8 pixels. The data wire is the jack's second pin
(J1 → P8, J2 → P12, J3 → P14, J4 → P16).

    from planetx import J2, PlanetXRainbowRing

    ring = PlanetXRainbowRing(port=J2)
    ring.fill((255, 150, 0))   # yellow
    ring.off()

A longer strip uses ``PlanetXNeoPixel(port=J1, count=24)``.
"""

from __future__ import annotations

from .ports import Port

# Same cap as the onboard matrix: a full-white tuple stays a modest current
# on the 3.3 V jack. MakeCode's strip default is 50% (about 0.5).
_DEFAULT_BRIGHTNESS = 0.20
RING_PIXELS = 8


def hsl(hue: int, saturation: int, luminosity: int) -> tuple:
    """One ``(red, green, blue)`` color, each channel 0–255.

    ``hue`` is 0–360, ``saturation`` and ``luminosity`` are 0–100.
    Pass the tuple to ``fill`` or ``set_pixel``.
    """
    # Integer HSL. h in 0..360, s and l in 0..100. One color, not a strip mode.
    h = hue % 360
    s = 0 if saturation < 0 else 100 if saturation > 100 else saturation
    l = 0 if luminosity < 0 else 100 if luminosity > 100 else luminosity
    c = (100 - abs(2 * l - 100)) * s // 100
    # hp is (hue/60) in hundredths. x drops to 0 at each sector edge.
    hp = h * 100 // 60
    x = c * (100 - abs(hp % 200 - 100)) // 100
    m = l - c // 2
    sector = h // 60
    if sector > 5:
        sector = 5
    if sector == 0:
        r, g, b = c, x, 0
    elif sector == 1:
        r, g, b = x, c, 0
    elif sector == 2:
        r, g, b = 0, c, x
    elif sector == 3:
        r, g, b = 0, x, c
    elif sector == 4:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return ((r + m) * 255 // 100, (g + m) * 255 // 100, (b + m) * 255 // 100)


class PlanetXNeoPixel:
    """A NeoPixel strip plugged into a Nezha2 jack.

    ``count`` is how many pixels are on the strip. ``fill``, ``set_pixel``,
    and ``clear`` light the pixels immediately.

        strip = PlanetXNeoPixel(port=J1, count=8)
        strip.fill((255, 0, 0))
        strip.set_pixel(0, (0, 255, 0))
        strip.clear()
    """

    def __init__(self, *, port: Port, count: int, brightness: float = _DEFAULT_BRIGHTNESS, pixels=None) -> None:
        # ``pixels`` is a test hook standing in for ``neopixel.NeoPixel``.
        # Not part of the student-facing construction API.
        if count < 1:
            raise ValueError("count must be at least 1")
        self._count = count
        self._pin = port.pins[1]
        if pixels is not None:
            self._pixels = pixels
            return
        import neopixel

        self._pixels = neopixel.NeoPixel(
            self._pin, count, brightness=brightness, auto_write=False
        )

    @property
    def count(self) -> int:
        """How many pixels are on this strip."""
        return self._count

    @property
    def brightness(self) -> float:
        """Scale for every pixel, from 0.0 (off) to 1.0 (full)."""
        return self._pixels.brightness

    @brightness.setter
    def brightness(self, value: float) -> None:
        self._pixels.brightness = value
        self._pixels.show()

    def fill(self, color: tuple) -> None:
        """Light every pixel with ``color``, an ``(red, green, blue)`` tuple."""
        self._pixels.fill(color)
        self._pixels.show()

    def set_pixel(self, index: int, color: tuple) -> None:
        """Light pixel ``index`` (0 is the first) and show the strip."""
        if index < 0 or index >= self._count:
            raise ValueError(f"pixel index must be 0..{self._count - 1}")
        self._pixels[index] = color
        self._pixels.show()

    def show(self) -> None:
        """Push the current colors out to the strip."""
        self._pixels.show()

    def clear(self) -> None:
        """Turn every pixel off."""
        self._pixels.fill((0, 0, 0))
        self._pixels.show()

    def off(self) -> None:
        """Turn every pixel off."""
        self.clear()

    def deinit(self) -> None:
        """Release the data pin."""
        pixels = self._pixels
        self._pixels = None
        deinit = getattr(pixels, "deinit", None)
        if deinit is not None:
            deinit()


class PlanetXRainbowRing(PlanetXNeoPixel):
    """The PlanetX rainbow ring: 8 pixels on one jack.

        ring = PlanetXRainbowRing(port=J2)
        ring.fill((255, 150, 0))
        ring.off()
    """

    def __init__(self, *, port: Port, brightness: float = _DEFAULT_BRIGHTNESS, pixels=None) -> None:
        super().__init__(port=port, count=RING_PIXELS, brightness=brightness, pixels=pixels)

"""On-device stepper for the polished 5×5 font.

Not selected by ``.vscode/cpfiles.txt``. To run it, point that manifest at
this file as ``/code.py`` for one deploy, then point it back.

Draws ``polished_spaced_glyphs``, not the table ``ink.py`` currently imports.
Button A shows the previous glyph. Button B shows the next. The list wraps.
Each step wipes the display, prints one serial line, then draws the glyph
from the left. The first glyph (space) is shown at startup.
"""

import asyncio

import display
from buttons import OnboardButtons
from display.font_makecode_5.polished_spaced_glyphs import (
    _ASCII_END,
    _ASCII_START,
    _RECORD_STRIDE,
    _SPACED_GLYPHS,
)

d = display.display
_COUNT = _ASCII_END - _ASCII_START + 1


def _pattern(ink: bytes) -> str:
    """Column bytes to a ``#``/``.`` grid. Bit 0 of a column is the top row."""
    lines = []
    for y in range(display.HEIGHT):
        lines.append(" ".join("#" if (col >> y) & 1 else "." for col in ink))
    return "\n".join(lines)


class _GlyphStepper:
    """One slot into the polished table. ``show`` wipes, logs, then draws."""

    def __init__(self) -> None:
        self.slot = 0

    def show(self) -> None:
        code = _ASCII_START + self.slot
        char = chr(code)
        font_byte = self.slot * _RECORD_STRIDE
        width = _SPACED_GLYPHS[font_byte]
        ink = _SPACED_GLYPHS[font_byte + 1 : font_byte + 1 + width]
        record = _SPACED_GLYPHS[font_byte : font_byte + _RECORD_STRIDE].hex()
        d.clear()
        print(
            f"char={char!r} width={width} ascii={code} slot={self.slot} "
            f"font_byte={font_byte} record={record}"
        )
        d.render_image(display.Image(_pattern(ink), display.WHITE), start_col=0)

    def previous(self) -> None:
        self.slot = (self.slot - 1) % _COUNT
        self.show()

    def next_glyph(self) -> None:
        self.slot = (self.slot + 1) % _COUNT
        self.show()


async def main() -> None:
    buttons = OnboardButtons()
    stepper = _GlyphStepper()
    buttons.button_a.on_pressed(stepper.previous)
    buttons.button_b.on_pressed(stepper.next_glyph)
    stepper.show()
    await buttons.run()


asyncio.run(main())

"""
MakeCode-style 5×5 bitmap font (Lancaster DAL ``pendolino3``).

Glyphs are stored as Exp14 column-major bytes (one byte per column, bit N =
row N, bit 0 = top). Upstream DAL stores *row* bytes (bit 4 = left column);
conversion happened at vendor time. Original source:

  https://github.com/lancaster-university/microbit-dal/blob/master/source/core/MicroBitFont.cpp

MIT notice: ``LICENSE`` in this directory (Copyright 2016 BBC; Lancaster
University by arrangement with the BBC).
"""

from .._constants import WIDTH

# ASCII 32 (space) .. 126 (~): 95 glyphs × WIDTH column bytes.
_ASCII_START = 32
_ASCII_END = 126  # inclusive

# Converted from DAL row-bytes (bit4=col0 … bit0=col4) to column-major.
_COLUMN_MAJOR = bytes.fromhex(
    "0000000000001700000000030003000a1f0a1f0a0a17151d0a13090412190a15150a10"
    "0003000000000e11000000110e0000000a040a0000040e040000100800000004040400"
    "000800000010080402010e11110e0000121f100019151512000911150b000c0a091f08"
    "1715151509081416150811090503010a1515150a02150d0502000a00000000100a0000"
    "00040a1100000a0a0a0000110a040002011505020e1115090e1e05051e001f15150a00"
    "0e111111001f11110e001f151511001f050501000e1111150c1f04041f00111f110000"
    "0911110f011f040a11001f101010001f0204021f1f0204081f0e11110e001f05050200"
    "06091916001f05050a10121515090001011f01010f10100f0007081008071f0804081f"
    "1b04041b0001021c02011915131100001f11110001020408100011111f000002010200"
    "101010101000010200000c12121e101f141408000c121212000814141f000e15151200"
    "041e0501000215150f001f04041800001d0000000010100d001f040a1000000f101000"
    "1e0204021e1e02021c000c12120c001e0a0a0400040a0a1e001c0202020010140a0200"
    "000f1414100e10101e1006081008061e1008101e120c0c12001214080402121a161200"
    "00041f1100001f000000111f0400000004040808"
)


def glyph_columns(ch: str) -> bytes:
    """Return ``WIDTH`` column-major bytes for one printable ASCII character.

    Unknown / out-of-range characters yield a blank ``WIDTH``-byte glyph
    (same contract as Exp14 ``_glyph_columns`` when the PCF has no glyph).
    """
    if not ch:
        return bytes(WIDTH)
    code = ord(ch[0])
    if code < _ASCII_START or code > _ASCII_END:
        return bytes(WIDTH)
    i = (code - _ASCII_START) * WIDTH
    return _COLUMN_MAJOR[i : i + WIDTH]

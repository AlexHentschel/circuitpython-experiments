"""Host-only helper: fetch, parse, and convert Lancaster DAL ``pendolino3``.

Never imported by on-device library code. Both ``verify_dal_font_conversion.py``
and ``generate_spaced_font_table.py`` reuse this module so the row-bytes →
column-major conversion lives in one place.

Source is pinned to an immutable GitHub commit (not ``master``). A SHA-256 of
the fetched file is checked on every run; a mismatch fails loudly rather than
silently converting unverified bytes.

License of the fetched file: MIT (Copyright 2016 BBC; Lancaster University by
arrangement with the BBC). The same grant is vendored next to the shipped table
at ``lib/display/font_makecode_5/LICENSE``.
"""

from __future__ import annotations

import hashlib
import re
import urllib.error
import urllib.request

DAL_COMMIT = "b60953b1963451a6c773c2ed136898b7a2383137"
DAL_PATH = "source/core/MicroBitFont.cpp"
DAL_URL = (
    f"https://raw.githubusercontent.com/lancaster-university/microbit-dal/"
    f"{DAL_COMMIT}/{DAL_PATH}"
)
# SHA-256 of the raw file at DAL_COMMIT, recorded 2026-09-13 from a fetch of DAL_URL.
EXPECTED_SHA256 = "8f8db78cb47f40122e769f0cf278fa439a54d7afe55f67f6c6fdf5ca2d7b6694"

FONT_WIDTH = 5  # pendolino3 is a 5×5 font; conversion uses bits 4..0 of each row byte
GLYPH_COUNT = 95  # ASCII 32 (space) .. 126 (~)
ROW_BYTES_PER_GLYPH = FONT_WIDTH
EXPECTED_ROW_BYTE_COUNT = GLYPH_COUNT * ROW_BYTES_PER_GLYPH  # 475

_USER_AGENT = "exp16-dal-font-scripts/1.0"
_FETCH_TIMEOUT_S = 30

_ARRAY_RE = re.compile(
    r"const unsigned char pendolino3\[475\] = \{([^}]+)\}",
    re.DOTALL,
)
_HEX_RE = re.compile(r"0x[0-9a-fA-F]+")


def fetch_source(url: str = DAL_URL, timeout: float = _FETCH_TIMEOUT_S) -> bytes:
    """Return the raw file bytes from ``url``. Raises on HTTP/network failure."""
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"failed to fetch DAL font source from {url}: {exc}\n"
            f"Pinned commit {DAL_COMMIT} is immutable; retry when GitHub is reachable, "
            f"or reconstruct from that commit by hand."
        ) from exc


def check_sha256(content: bytes, expected: str = EXPECTED_SHA256) -> str:
    """Return the hex digest, or raise if it does not match ``expected``."""
    digest = hashlib.sha256(content).hexdigest()
    if digest != expected:
        raise RuntimeError(
            f"DAL source SHA-256 mismatch.\n"
            f"  expected: {expected}\n"
            f"  got:      {digest}\n"
            f"Refusing to convert unverified input (corrupt transport, unexpected "
            f"redirect, or the pinned commit no longer resolving as recorded)."
        )
    return digest


def parse_pendolino3_row_bytes(source_text: str) -> bytes:
    """Extract the 475-byte ``pendolino3`` C array from ``MicroBitFont.cpp``."""
    match = _ARRAY_RE.search(source_text)
    if match is None:
        raise RuntimeError(
            "could not find `const unsigned char pendolino3[475] = { ... }` "
            "in the fetched MicroBitFont.cpp"
        )
    hex_tokens = _HEX_RE.findall(match.group(1))
    if len(hex_tokens) != EXPECTED_ROW_BYTE_COUNT:
        raise RuntimeError(
            f"pendolino3 array parsed {len(hex_tokens)} bytes; expected "
            f"{EXPECTED_ROW_BYTE_COUNT}"
        )
    return bytes(int(token, 16) for token in hex_tokens)


def row_bytes_to_column_major(row_bytes: bytes, width: int = FONT_WIDTH) -> bytes:
    """Convert DAL row-bytes to Exp16 column-major glyph storage.

    DAL stores five *row* bytes per glyph; bit 4 is the leftmost column, bit 0
    the rightmost (bits 7-5 unused). Exp16 stores one byte per *column*; bit N
    is row N, bit 0 = top. For row ``r`` and column ``c``:

        if (row_byte >> (width - 1 - c)) & 1:  col_bytes[c] |= 1 << r

    With ``width == 5`` this is ``(row_byte >> (4 - c)) & 1``, matching
    ``font_makecode_5/glyphs.py``'s documented mapping and
    ``concepts/fonts.md`` § DAL pendolino3.
    """
    if width < 1 or width > 8:
        raise ValueError(f"width must be 1..8 (fits in one column byte); got {width}")
    if len(row_bytes) % width != 0:
        raise ValueError(
            f"row-byte length {len(row_bytes)} is not a multiple of width {width}"
        )
    left_bit = width - 1  # bit index of column 0
    out = bytearray()
    for base in range(0, len(row_bytes), width):
        col_bytes = [0] * width
        for row, row_byte in enumerate(row_bytes[base : base + width]):
            for col in range(width):
                if (row_byte >> (left_bit - col)) & 1:
                    col_bytes[col] |= 1 << row
        out.extend(col_bytes)
    return bytes(out)


def load_column_major() -> bytes:
    """Fetch, integrity-check, parse, and convert. Returns 475 column-major bytes."""
    raw = fetch_source()
    check_sha256(raw)
    row_bytes = parse_pendolino3_row_bytes(raw.decode("utf-8"))
    converted = row_bytes_to_column_major(row_bytes)
    if len(converted) != EXPECTED_ROW_BYTE_COUNT:
        raise RuntimeError(
            f"converted length {len(converted)} != {EXPECTED_ROW_BYTE_COUNT}"
        )
    return converted

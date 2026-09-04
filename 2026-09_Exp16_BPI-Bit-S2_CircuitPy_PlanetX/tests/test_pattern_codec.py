"""
Round-trip and negative-path tests for ``display.bitmap_codec``.

Includes the encoding-limit check (height > 8) required by the overnight bar.

These round-trips start from stored bytes: they prove the codec is invertible,
not that an icon matches MakeCode. Comment↔byte and MakeCode-fixture checks
live in ``test_icons_data.py``.
"""

import pytest

from display._constants import WIDTH, HEIGHT, _MAX_HEIGHT_PER_COLUMN_BYTE
from display.bitmap_codec import pattern_to_colmajor, colmajor_to_pattern
from display.icons import ICONS, ARROWS


def _slices(data, stride):
    for i in range(0, len(data), stride):
        yield i // stride, bytes(data[i:i + stride])


@pytest.mark.parametrize(
    "idx,original",
    list(_slices(ICONS, WIDTH)),
    ids=lambda arg: f"icon_{arg}" if isinstance(arg, int) else None,
)
def test_icons_round_trip(idx, original):
    """Codec invertibility for each ICONS slice: bytes → ASCII → bytes.

    - Covers: encoder/decoder disagreeing (bit order, whitespace, row/column swap).
    - Does not cover: the picture matching MakeCode (starts from stored bytes).
    - How: ``colmajor_to_pattern`` then ``pattern_to_colmajor``; equal to ``original``.
    """
    rendered = colmajor_to_pattern(original, width=WIDTH, height=HEIGHT)
    re_encoded = pattern_to_colmajor(rendered, width=WIDTH, height=HEIGHT)
    assert re_encoded == original, f"icon index {idx} did not round-trip"


@pytest.mark.parametrize(
    "idx,original",
    list(_slices(ARROWS, WIDTH)),
    ids=lambda arg: f"arrow_{arg}" if isinstance(arg, int) else None,
)
def test_arrows_round_trip(idx, original):
    """Codec invertibility for each ARROWS slice: bytes → ASCII → bytes.

    - Covers: same encoder/decoder disagreement as icons, on the arrow table.
    - How: decode then encode; equal to ``original``.
    """
    rendered = colmajor_to_pattern(original, width=WIDTH, height=HEIGHT)
    re_encoded = pattern_to_colmajor(rendered, width=WIDTH, height=HEIGHT)
    assert re_encoded == original, f"arrow index {idx} did not round-trip"


def _valid_pattern():
    return "\n".join([". " * WIDTH] * HEIGHT)


def test_short_row_raises():
    """Encoder rejects a row with fewer than WIDTH cells.

    - Covers: silent pad-on-the-right (would shift later pixels).
    - How: first row WIDTH-1 dots; expect ``ValueError`` matching ``cells, expected``.
    """
    pattern = "\n".join(["." * (WIDTH - 1)] + ["." * WIDTH] * (HEIGHT - 1))
    with pytest.raises(ValueError, match="cells, expected"):
        pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)


def test_too_few_rows_raises():
    """Encoder rejects fewer than HEIGHT non-blank rows.

    - Covers: silent pad-at-bottom.
    - How: HEIGHT-1 full rows; expect ``ValueError`` naming HEIGHT.
    """
    pattern = "\n".join(["." * WIDTH] * (HEIGHT - 1))
    with pytest.raises(ValueError, match="expected {}".format(HEIGHT)):
        pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)


def test_too_many_rows_raises():
    """Encoder rejects more than HEIGHT non-blank rows.

    - Covers: silent truncate of extra rows.
    - How: HEIGHT+1 full rows; expect ``ValueError`` naming HEIGHT.
    """
    pattern = "\n".join(["." * WIDTH] * (HEIGHT + 1))
    with pytest.raises(ValueError, match="expected {}".format(HEIGHT)):
        pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)


def test_unknown_char_raises():
    """Encoder rejects cells that are neither ``#`` nor ``.``.

    - Covers: treating ``X``/digits as on (or ignoring them).
    - How: one ``X`` in row 3; expect ``ValueError`` matching ``unknown cell``.
    """
    rows = ["." * WIDTH] * HEIGHT
    rows[3] = "." * (WIDTH - 1) + "X"
    pattern = "\n".join(rows)
    with pytest.raises(ValueError, match="unknown cell"):
        pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)


def test_height_above_encoding_limit_raises():
    """Encoder rejects height > 8 (one bit per row in a column byte).

    - Covers: overnight encoding-limit bar; would overflow ``1 << row``.
    - How: pattern of 9 rows, ``height=9``; expect ``exceeds column-major encoding limit``.
    """
    pattern = "\n".join(["." * WIDTH] * (_MAX_HEIGHT_PER_COLUMN_BYTE + 1))
    with pytest.raises(ValueError, match="exceeds column-major encoding limit"):
        pattern_to_colmajor(
            pattern,
            width=WIDTH,
            height=_MAX_HEIGHT_PER_COLUMN_BYTE + 1,
        )


def test_height_above_encoding_limit_raises_in_decoder():
    """Decoder rejects height > 8 (symmetric with the encoder).

    - Covers: decoder-first caller getting extra blank rows for ``row >= 8``.
    - How: ``colmajor_to_pattern(..., height=9)``; same error wording as the encoder.
    """
    with pytest.raises(ValueError, match="exceeds column-major encoding limit"):
        colmajor_to_pattern(bytes(WIDTH), width=WIDTH, height=_MAX_HEIGHT_PER_COLUMN_BYTE + 1)


def test_negative_height_raises_in_encoder():
    """Encoder rejects negative height.

    - Covers: ``range()`` / shift mishandling of ``height < 0``.
    - How: valid pattern, ``height=-1``; expect ``must be non-negative``.
    """
    with pytest.raises(ValueError, match="must be non-negative"):
        pattern_to_colmajor(_valid_pattern(), width=WIDTH, height=-1)


def test_negative_width_raises_in_encoder():
    """Encoder rejects negative width.

    - Covers: ``bytearray(width)`` / loop mishandling of ``width < 0``.
    - How: valid pattern, ``width=-1``; expect ``must be non-negative``.
    """
    with pytest.raises(ValueError, match="must be non-negative"):
        pattern_to_colmajor(_valid_pattern(), width=-1, height=HEIGHT)


def test_negative_height_raises_in_decoder():
    """Decoder rejects negative height (symmetric with the encoder).

    - Covers: decoder-first path skipping the encoder's domain check.
    - How: dummy bytes, ``height=-1``; expect ``must be non-negative``.
    """
    with pytest.raises(ValueError, match="must be non-negative"):
        colmajor_to_pattern(bytes(WIDTH), width=WIDTH, height=-1)


def test_negative_width_raises_in_decoder():
    """Decoder rejects negative width (symmetric with the encoder).

    - Covers: decoder-first path skipping the encoder's domain check.
    - How: dummy bytes, ``width=-1``; expect ``must be non-negative``.
    """
    with pytest.raises(ValueError, match="must be non-negative"):
        colmajor_to_pattern(bytes(WIDTH), width=-1, height=HEIGHT)

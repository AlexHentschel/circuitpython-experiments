"""
Round-trip and negative-path tests for ``display.bitmap_codec``.

Includes the encoding-limit check (height > 8) required by the overnight bar.
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
    rendered = colmajor_to_pattern(original, width=WIDTH, height=HEIGHT)
    re_encoded = pattern_to_colmajor(rendered, width=WIDTH, height=HEIGHT)
    assert re_encoded == original, f"icon index {idx} did not round-trip"


@pytest.mark.parametrize(
    "idx,original",
    list(_slices(ARROWS, WIDTH)),
    ids=lambda arg: f"arrow_{arg}" if isinstance(arg, int) else None,
)
def test_arrows_round_trip(idx, original):
    rendered = colmajor_to_pattern(original, width=WIDTH, height=HEIGHT)
    re_encoded = pattern_to_colmajor(rendered, width=WIDTH, height=HEIGHT)
    assert re_encoded == original, f"arrow index {idx} did not round-trip"


def _valid_pattern():
    return "\n".join([". " * WIDTH] * HEIGHT)


def test_short_row_raises():
    pattern = "\n".join(["." * (WIDTH - 1)] + ["." * WIDTH] * (HEIGHT - 1))
    with pytest.raises(ValueError, match="cells, expected"):
        pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)


def test_too_few_rows_raises():
    pattern = "\n".join(["." * WIDTH] * (HEIGHT - 1))
    with pytest.raises(ValueError, match="expected {}".format(HEIGHT)):
        pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)


def test_too_many_rows_raises():
    pattern = "\n".join(["." * WIDTH] * (HEIGHT + 1))
    with pytest.raises(ValueError, match="expected {}".format(HEIGHT)):
        pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)


def test_unknown_char_raises():
    rows = ["." * WIDTH] * HEIGHT
    rows[3] = "." * (WIDTH - 1) + "X"
    pattern = "\n".join(rows)
    with pytest.raises(ValueError, match="unknown cell"):
        pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)


def test_height_above_encoding_limit_raises():
    pattern = "\n".join(["." * WIDTH] * (_MAX_HEIGHT_PER_COLUMN_BYTE + 1))
    with pytest.raises(ValueError, match="exceeds column-major encoding limit"):
        pattern_to_colmajor(
            pattern,
            width=WIDTH,
            height=_MAX_HEIGHT_PER_COLUMN_BYTE + 1,
        )


def test_height_above_encoding_limit_raises_in_decoder():
    with pytest.raises(ValueError, match="exceeds column-major encoding limit"):
        colmajor_to_pattern(bytes(WIDTH), width=WIDTH, height=_MAX_HEIGHT_PER_COLUMN_BYTE + 1)


def test_negative_height_raises_in_encoder():
    with pytest.raises(ValueError, match="must be non-negative"):
        pattern_to_colmajor(_valid_pattern(), width=WIDTH, height=-1)


def test_negative_width_raises_in_encoder():
    with pytest.raises(ValueError, match="must be non-negative"):
        pattern_to_colmajor(_valid_pattern(), width=-1, height=HEIGHT)


def test_negative_height_raises_in_decoder():
    with pytest.raises(ValueError, match="must be non-negative"):
        colmajor_to_pattern(bytes(WIDTH), width=WIDTH, height=-1)


def test_negative_width_raises_in_decoder():
    with pytest.raises(ValueError, match="must be non-negative"):
        colmajor_to_pattern(bytes(WIDTH), width=-1, height=HEIGHT)

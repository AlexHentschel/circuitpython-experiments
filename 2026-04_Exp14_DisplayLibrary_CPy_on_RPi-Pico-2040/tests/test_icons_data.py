"""
Shape, value-range, and enum-alignment tests for ``display.icons``.

These checks pin the contract between ``IconNames`` / ``ArrowNames``
(integer values used as indices) and the ``ICONS`` / ``ARROWS`` byte
arrays. Any mis-sized array or enum drift would silently corrupt every
downstream icon lookup (``data[icon_id * WIDTH : (icon_id + 1) * WIDTH]``).
"""

from display._constants import WIDTH
from display.icons import ICONS, ARROWS, IconNames, ArrowNames


EXPECTED_ICON_COUNT = 40
EXPECTED_ARROW_COUNT = 8


def _enum_values(cls):
    """Sorted integer values of a plain-class enum (non-dunder attributes)."""
    return sorted(
        getattr(cls, name)
        for name in dir(cls)
        if not name.startswith("_")
    )


# ---------------------------------------------------------------------------
# Shape: array length must equal count * WIDTH bytes
# ---------------------------------------------------------------------------

def test_icons_length():
    assert len(ICONS) == EXPECTED_ICON_COUNT * WIDTH


def test_arrows_length():
    assert len(ARROWS) == EXPECTED_ARROW_COUNT * WIDTH


# ---------------------------------------------------------------------------
# Type: authoritative storage is immutable ``bytes``
# ---------------------------------------------------------------------------

def test_icons_is_bytes():
    assert isinstance(ICONS, bytes)


def test_arrows_is_bytes():
    assert isinstance(ARROWS, bytes)


# ---------------------------------------------------------------------------
# Byte range (tautology for ``bytes`` but kept as contract pin against a
# future type change to a signed or wider container).
# ---------------------------------------------------------------------------

def test_icons_byte_range():
    assert all(0 <= b <= 255 for b in ICONS)


def test_arrows_byte_range():
    assert all(0 <= b <= 255 for b in ARROWS)


# ---------------------------------------------------------------------------
# Enum <-> data alignment
# ---------------------------------------------------------------------------

def test_icon_names_count_matches_data():
    assert len(_enum_values(IconNames)) == len(ICONS) // WIDTH == EXPECTED_ICON_COUNT


def test_arrow_names_count_matches_data():
    assert len(_enum_values(ArrowNames)) == len(ARROWS) // WIDTH == EXPECTED_ARROW_COUNT


def test_icon_names_are_contiguous_from_zero():
    """Values must be 0..N-1 -- they index into ICONS by slicing."""
    assert _enum_values(IconNames) == list(range(EXPECTED_ICON_COUNT))


def test_arrow_names_are_contiguous_from_zero():
    assert _enum_values(ArrowNames) == list(range(EXPECTED_ARROW_COUNT))

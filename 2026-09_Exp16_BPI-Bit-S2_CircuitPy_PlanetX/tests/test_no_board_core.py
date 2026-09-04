"""Guard: overnight host suite never imports ``board`` or ``display.core``."""

import sys

import display
import display.bitmap_codec  # noqa: F401
import display.font_makecode_5  # noqa: F401
import display.geometry  # noqa: F401
import display.icons  # noqa: F401
import buttons  # noqa: F401


def test_display_package_skips_core_on_cpython():
    assert "display.core" not in sys.modules
    assert display._HAS_HARDWARE is False


def test_board_not_imported_by_pure_stack():
    # Blinka ``board`` in this venv is broken on purpose; tests must not need it.
    assert "board" not in sys.modules

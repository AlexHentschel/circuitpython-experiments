"""
Host-test setup: prepend ``lib/`` so ``import display.<submodule>`` and
``import buttons`` resolve without an editable install.

No stubs -- overnight tests exercise only pure sub-modules (``_constants``,
``bitmap_codec``, ``geometry``, ``icons``, ``font_makecode_5``) plus the
button dispatcher with a fake EventQueue. ``display.__init__`` guards the
core import with a ``board`` presence check, so package initialisation
succeeds on CPython; pure sub-module imports never trigger ``core.py``.
"""

import pathlib
import sys

# Board deploy ("CP Copy Libs to Board") copies the whole lib/ folder verbatim
# -- there is no ignore-file mechanism in the sync extension (verified against
# its own source + docs, 2026-09-11; a folder-level ignore convention does not
# exist for it). Stop pytest's import machinery from littering lib/ with
# __pycache__/*.pyc that would otherwise ride along onto the ~960 KiB CIRCUITPY
# volume. Must be set before the lib/* imports below (and before test
# collection imports lib.* modules).
sys.dont_write_bytecode = True

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "lib"))

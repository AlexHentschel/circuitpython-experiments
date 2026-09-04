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

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "lib"))

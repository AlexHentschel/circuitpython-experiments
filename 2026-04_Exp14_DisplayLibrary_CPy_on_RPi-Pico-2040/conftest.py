"""
Project-root conftest.

Loaded by pytest *before* ``pytest_configure`` runs. Its sole job here
is to prevent the CircuitPython entry-point ``code.py`` (at the project
root) from shadowing the stdlib ``code`` module, which pytest's
``_pytest.debugging`` imports transitively via ``pdb``.

Python's ``-m pytest`` invocation prepends the current working
directory to ``sys.path`` (even with ``-P`` this can reappear via
pytest's rootdir handling), so a bare ``import code`` would find our
local ``code.py`` and fail with ``ModuleNotFoundError: No module named
'board'`` during pytest startup.

Mitigation: drop cwd-style entries from ``sys.path`` here, before any
third-party import runs. Tests still resolve ``display.*`` via
``tests/conftest.py`` which prepends ``lib/``.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [
    p for p in sys.path
    if p not in ("", ".", _HERE)
]

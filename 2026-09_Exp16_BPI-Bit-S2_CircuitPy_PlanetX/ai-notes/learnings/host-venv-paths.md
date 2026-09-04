# Host venv paths — experiment-local, not in code (2026-09-04)

**Vocabulary:** talk about this **experiment** (Exp16), not “the repo.” The parent git tree holds several experiments; each is reasonably self-contained.

**Claim:** swapping `<path-to-venv>` on a new checkout needs **no code edits** in this experiment. Host tests resolve `lib/` relative to `tests/conftest.py`. There are **no** experiment shell scripts and **no** absolute host paths in `lib/` or `tests/*.py`.

**Where paths do live:** prose only — `tests/README.md` (example, tangible stub), `ai-notes/NOTES.md`, `Notes/overall_goal.md`. High-level `README.md` uses `<path-to-venv>`.

**Outside this experiment (not a code edit here):** shared workspace CircuitPythonSync still names another board; a later per-experiment `.vscode/` might hold a local interpreter path (config, not library).

**Status:** `evidence-supported` (grep 2026-09-04). Alex: example path is for tangibility, not an experiment requirement.

"""Sync this experiment's lib/ tree onto the attached CIRCUITPY drive, excluding files the board should never receive.

Companion to sync_files_to_board.py (which mirrors the manifest-driven "CP Copy Files
to Board"); this script replaces the CircuitPythonSync extension's "CP Copy Libs to
Board" for this experiment. That extension command copies the whole lib/ tree
unfiltered (verified against its own source, v2.2.2): the only built-in cleanup is a
post-copy sweep of macOS ._* AppleDouble files, so everything else in lib/ rides
along, including:

  - __pycache__/ and stray *.pyc: host CPython bytecode from py_compile or import
    checks. CircuitPython never reads .pyc (it runs .py and .mpy), so on the MCU
    these are pure dead weight.
  - .DS_Store: macOS Finder metadata (survives the extension's ._* sweep).
  - README.md: package documentation; wanted in the repo, dead weight on the MCU.

Excluded by exact name (at any depth) or .pyc suffix. Everything else ships,
including LICENSE files (~1 KB each; keep licensing hygiene even on the board).

Write-wear: only files that are missing on the board, differ in size, or whose mtime
drifted beyond FAT's 2 s timestamp resolution are rewritten; mtimes are preserved on
copy, so a routine re-run touches only what changed. Same rationale as
sync_files_to_board.py's "library sync stays human-driven" note: this script is
human-initiated too (run it instead of the extension's lib-copy button). --force
rewrites everything for the rare case where the skip-unchanged heuristic is doubted.

Safety: refuses to write unless the target looks like a CircuitPython volume (has
boot_out.txt) and prints that board's identity first. Never deletes or prunes
anything on the board: a file removed or renamed locally leaves a stale board copy
until cleaned by hand. Creates lib/ (and any subfolder) on the board if missing.

Usage:
    python3 scripts/sync_lib_to_board.py [--drive /Volumes/CIRCUITPY] [--dry-run] [--force]
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> experiment root
LIB_SOURCE = EXPERIMENT_ROOT / "lib"
DEFAULT_DRIVE = Path("/Volumes/CIRCUITPY")

EXCLUDED_DIR_NAMES = frozenset({"__pycache__"})
EXCLUDED_FILE_NAMES = frozenset({".DS_Store", "README.md"})
EXCLUDED_FILE_SUFFIXES = (".pyc",)
# FAT stores modification times at 2 s resolution, so a freshly copied file's board
# mtime can sit up to ~2 s below the source's. Anything further apart is a real change.
MTIME_TOLERANCE_S = 2.0


def walk_lib(lib_root: Path) -> tuple[list[tuple[Path, str]], list[tuple[Path, str]]]:
    """Return (to_ship, excluded) for the lib/ tree.

    to_ship:  [(source_path, destination_relpath_posix), ...] for every file that
              should exist on the board, e.g. (…/lib/display/core.py, "display/core.py").
    excluded: [(path, reason), ...] for every pruned directory or file, so the caller
              can show exactly what was kept off the board.
    """
    to_ship: list[tuple[Path, str]] = []
    excluded: list[tuple[Path, str]] = []
    for dirpath, dirnames, filenames in os.walk(lib_root):
        # Prune excluded directories in place so their contents are never visited.
        for name in list(dirnames):
            if name in EXCLUDED_DIR_NAMES:
                dirnames.remove(name)
                excluded.append((Path(dirpath) / name, "excluded directory"))
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if name in EXCLUDED_FILE_NAMES:
                excluded.append((path, f"excluded name ({name})"))
            elif path.suffix in EXCLUDED_FILE_SUFFIXES:
                excluded.append((path, f"excluded suffix ({path.suffix})"))
            else:
                to_ship.append((path, path.relative_to(lib_root).as_posix()))
    return to_ship, excluded


def needs_copy(source: Path, dest: Path, force: bool) -> bool:
    """True if the board copy is missing, differs in size, or has an mtime more than
    MTIME_TOLERANCE_S away from the source. Board mtimes are preserved on copy, so a
    matching (size, mtime) pair means "unchanged since the last sync"."""
    if force:
        return True
    if not dest.is_file():
        return True
    src_stat, dst_stat = source.stat(), dest.stat()
    if src_stat.st_size != dst_stat.st_size:
        return True
    return abs(src_stat.st_mtime - dst_stat.st_mtime) > MTIME_TOLERANCE_S


def verify_board(drive: Path) -> str:
    """Return boot_out.txt's content, or exit with an error if `drive` doesn't look
    like a CircuitPython volume. Mirrors sync_files_to_board.py's own check; duplicated
    on purpose: a 15-line guard is cheaper than an import coupling between two scripts
    that evolve independently."""
    boot_out = drive / "boot_out.txt"
    if not drive.is_dir() or not boot_out.is_file():
        print(
            f"ERROR: {drive} does not look like a CircuitPython volume (no boot_out.txt "
            "found there). Refusing to write anything.",
            file=sys.stderr,
        )
        sys.exit(1)
    return boot_out.read_text().strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--drive", type=Path, default=DEFAULT_DRIVE, help=f"CIRCUITPY mount point (default: {DEFAULT_DRIVE})"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be copied; write nothing")
    parser.add_argument("--force", action="store_true", help="Rewrite every eligible file, even unchanged ones")
    args = parser.parse_args()

    if not LIB_SOURCE.is_dir():
        print(f"ERROR: lib/ source not found: {LIB_SOURCE}", file=sys.stderr)
        return 1

    boot_out_text = verify_board(args.drive)
    print(f"# target drive: {args.drive}")
    print(f"# board:        {boot_out_text.splitlines()[0]}")

    to_ship, excluded = walk_lib(LIB_SOURCE)
    for path, reason in excluded:
        rel = path.relative_to(LIB_SOURCE).as_posix()
        print(f"excluded: lib/{rel} ({reason})")

    if not to_ship:
        print("# nothing eligible under lib/ -- nothing to do")
        return 0

    n_copied = n_unchanged = 0
    for source, dest_rel in to_ship:
        dest = args.drive / "lib" / dest_rel
        if needs_copy(source, dest, args.force):
            verb = "would copy" if args.dry_run else "copying"
            print(f"{verb}: lib/{dest_rel} -> {dest}")
            if not args.dry_run:
                # copyfile + explicit utime (not copy2): copy2 also copies macOS
                # extended attributes, which the FAT driver stores as ._* AppleDouble
                # sidecar files on the board -- exactly the junk this script exists to
                # keep off it (the extension shells out to clean those after its own
                # copies; this script just never creates them). The explicit utime
                # preserves the source mtime, which the skip-unchanged check needs.
                stat = source.stat()
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
                os.utime(dest, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            n_copied += 1
        else:
            n_unchanged += 1
            if args.dry_run:
                print(f"unchanged (skip): lib/{dest_rel}")

    if args.dry_run:
        print(
            f"# dry run -- {n_copied} file(s) would be copied, "
            f"{n_unchanged} unchanged, {len(excluded)} excluded; nothing written"
        )
    else:
        print(f"# done -- copied {n_copied}, unchanged {n_unchanged}, excluded {len(excluded)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

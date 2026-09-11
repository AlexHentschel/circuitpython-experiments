"""Mirror CircuitPythonSync's "CP Copy Files to Board" command for this experiment, so the
agent can push business-logic files to the attached CIRCUITPY drive without needing Alex
at the keyboard for every change.

Scope (Alex, 2026-09-11): business-logic files only -- whatever this experiment's
`.vscode/cpfiles.txt` manifest lists (currently just `code.py`). Full overwrite is
acceptable here: the manifest only ever lists a handful of files, and most of them
changed anyway on any given sync.

**Deliberately out of scope: library sync.** `lib/` stays human-driven via the
CircuitPythonSync extension's "CP Copy Libs to Board" for now -- rewriting a large,
mostly-unchanged `lib/` tree on every autonomous sync would cost flash write-wear that
a rare, human-initiated full sync does not. This script does not walk `lib/`; it only
copies exactly what the manifest names, same as the extension's own "Copy Files"
command. Revisit this split if the policy changes.

Manifest format (`.vscode/cpfiles.txt`, same syntax CircuitPythonSync itself reads):
    # comment
    source_file
    source_file -> /destination_on_board

Usage:
    python3 sync_files_to_board.py [--drive /Volumes/CIRCUITPY] [--manifest PATH] [--dry-run]

Safety: refuses to write unless the target actually looks like a CircuitPython volume
(has `boot_out.txt`), and always prints that board's identity (UID/version/build) before
copying, so a wrong-drive write would be visible in the output rather than silent. Does
not create a backup itself -- Alex keeps his own point-in-time backups separately
(see `ai-notes/2026-09-11 BPI-Bit-S2 CPy LED demo backup/`); this script is not a
substitute for that.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> experiment root
DEFAULT_MANIFEST = EXPERIMENT_ROOT / ".vscode" / "cpfiles.txt"
DEFAULT_DRIVE = Path("/Volumes/CIRCUITPY")


def parse_manifest(path: Path) -> list[tuple[Path, str]]:
    """Return [(local_source_path, destination_relpath_on_board), ...] for every active
    (non-comment, non-blank) manifest line. `destination_relpath_on_board` has no
    leading slash, e.g. "code.py" or "lib/foo.py"."""
    entries: list[tuple[Path, str]] = []
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "->" in line:
            src, dst = (part.strip() for part in line.split("->", 1))
            dst = dst.lstrip("/")
        else:
            src = line
            dst = line
        entries.append((EXPERIMENT_ROOT / src, dst))
    return entries


def verify_board(drive: Path) -> str:
    """Return boot_out.txt's content, or exit with an error if `drive` doesn't look like
    a CircuitPython volume. Refuses to write to something that isn't clearly a board."""
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
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="cpfiles.txt path (default: this experiment's .vscode/cpfiles.txt)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be copied; write nothing")
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"ERROR: manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    boot_out_text = verify_board(args.drive)
    print(f"# target drive: {args.drive}")
    print(f"# board:        {boot_out_text.splitlines()[0]}")

    entries = parse_manifest(args.manifest)
    if not entries:
        print("# manifest has no active entries -- nothing to do")
        return 0

    copied = 0
    for source, dest_rel in entries:
        dest = args.drive / dest_rel
        if not source.is_file():
            print(f"SKIP (source missing): {source}", file=sys.stderr)
            continue
        verb = "would copy" if args.dry_run else "copying"
        print(f"{verb}: {source.relative_to(EXPERIMENT_ROOT)} -> {dest}")
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            copied += 1

    if args.dry_run:
        print(f"# dry run -- {len(entries)} manifest entrie(s), nothing written")
    else:
        print(f"# done -- copied {copied} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

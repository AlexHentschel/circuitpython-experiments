# `sync_lib_to_board.py` (exp16)

`[project:circuitpython-exp16-planetx]` status: `evidence-supported` for the exclude list and the 2026-09-13 on-device check (19/19 `lib/` files byte-identical, excludes held). Overview row: `tooling.md` § Where the tools live.

## What it is

Host script at exp16 `scripts/sync_lib_to_board.py`. Replaces the extension command "CP Copy Libs to Board" for exp16. Cursor task "Sync Lib to Board" (and its dry-run twin). Alex runs it. The agent does not write the board unless he asks.

## Behavior

- Walks exp16 `lib/`. Skips directory `__pycache__`, file names `.DS_Store` and `README.md`, and suffix `.pyc`. Ships everything else, including `LICENSE`.
- Rewrites a board file when it is missing, the size differs, or the modification time differs by more than 2 seconds (FAT resolution). `--force` rewrites all. `--dry-run` writes nothing.
- Copy is `shutil.copyfile` plus `os.utime` of the source mtime. Not `copy2`: that would copy macOS xattrs and the FAT driver would store them as `._*` files. The preserved mtime is what lets the next run skip.
- Refuses to write unless `boot_out.txt` is on the drive. Never deletes a board file that was removed locally.

## Limitations

- A same-size edit whose mtime stays inside the 2 second window is skipped. A touch that changes only the mtime is copied even when the bytes match. The file-sync script compares bytes instead. These two scripts deliberately differ.
- Does not prune the board. A deleted local library file stays on CIRCUITPY until removed by hand.
- Exp11–15 have no copy of this script. Their lib copy is the extension command, which ships the whole tree and then `dot_clean`s the drive.

## Maintenance

Exclude list and the 2 second constant are at the top of the script. Change them there. The 2026-09-12 sentence in `tooling.md` that said `copy2` preserved mtimes is corrected: the script uses `copyfile` + `os.utime`.

## Todos

- None scheduled. Aligning this script to the byte compare in `tooling-sync-files-to-board.md` is optional, and only if a same-size edit is missed or an mtime-only touch causes a reload that matters.

## Evolution

2026-09-12: added after Copy Libs put `__pycache__`, `.DS_Store`, and `README.md` on a 941 KB volume. 2026-09-13: bracketed repro left `lib/` intact (commit `7ae8157`). The extension command remains installed and still copies `lib/` unfiltered if someone runs it.

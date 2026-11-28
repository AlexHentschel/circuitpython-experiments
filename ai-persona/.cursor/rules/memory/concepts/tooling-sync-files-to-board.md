# `sync_files_to_board.py` (exp16)

`[project:circuitpython-exp16-planetx]` status: `evidence-supported` for the skip rule (dry-run 2026-11-26 against UID `0740D10F1BE9`, both manifest files byte-identical and skipped). Overview row: `tooling.md` § Where the tools live.

## What it is

Host script at exp16 `scripts/sync_files_to_board.py`. Copies the active lines of `.vscode/cpfiles.txt` onto CIRCUITPY. Same manifest syntax as CircuitPythonSync. Cursor task "Sync Files to Board" (and its dry-run twin) in exp16 `.vscode/tasks.json`, interpreter `${config:python.defaultInterpreterPath}`.

Alex runs the task. The agent does not write the board unless he asks.

## Behavior (2026-11-26)

- Refuses to write unless `<drive>/boot_out.txt` exists, and prints that board line first.
- Skips a destination whose bytes already match. Missing file or different size is copied. Matching size is compared in chunks (`filecmp.cmp(..., shallow=False)`).
- Copy is `shutil.copyfile`, not `copy2`, so macOS extended attributes are not stored as `._*` sidecars. Modification time is not preserved, and is not the skip test.
- `--force` rewrites every existing source. `--dry-run` writes nothing. A missing source is reported and not counted.
- Prints `unchanged (skip): <path>` and a copied/unchanged count.
- Strips a trailing `# comment` on a `source -> /dest` line. The extension does not. Still author comments on their own line, because the extension path remains.

Active manifest lines on 2026-11-26: `readme.txt`, and `code_stage3.py -> /code.py`. Stage 4 and Stage 5 are comments.

## Limitations

- Does not delete a board file that left the manifest.
- Does not walk `lib/`. That is `tooling-sync-lib-to-board.md`.
- Does not run `dot_clean`. A copy made by the extension can still leave or remove `._*` files.
- A write reloads the board. Skipping an unchanged `readme.txt` avoids that extra reload. A real change to `code_stage3.py` still writes `/code.py` and reloads once.
- Lives only in exp16. Exp11–15 still use the extension command, which overwrites every listed file.

## Maintenance

The script docstring is the usage line. This note is the policy. When the skip rule changes, update both, plus the overview row's "Current use" cell and exp16 `README.md` step 3.

## Todos

- None. A content hash was considered on 2026-11-26 and not used: it reads the same bytes and then discards them.

## Evolution

2026-09-11: added so an agent (or a task) can copy the manifest without the palette command, and so a multi-root window is not limited to `workspaceFolders[0]`. First version overwrote every listed file. 2026-09-13: trailing-comment strip. 2026-11-26: byte skip, after repeated Sync Files runs rewrote an unchanged `readme.txt` and reloaded the board.

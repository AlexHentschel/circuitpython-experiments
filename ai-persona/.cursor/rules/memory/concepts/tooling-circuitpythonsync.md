# CircuitPythonSync (`padgettholdings.circuitpythonsync`)

`[domain:tooling]` `[cross-experiment]` status: `evidence-supported` for the limits below (extension source 2.2.2 + on-device incidents). Overview row: `tooling.md` § Where the tools live.

## What it is

Cursor/VS Code extension that copies an experiment's files onto a mounted CIRCUITPY drive. Open VSX: `https://open-vsx.org/extension/padgettholdings/circuitpythonsync`. Installed copy on this Mac (2026-11-26): `~/.cursor/extensions/padgettholdings.circuitpythonsync-2.2.2-universal`. Not the stub extension `wmerkens.vscode-circuitpython-v2` (that one does not sync files).

Commands a human runs from the palette include `CP Copy Files to Board`, `CP Copy Libs to Board`, `CP Set Drive`, `CP Compare file to board`, `CP Upload UF2 Firmware`. An agent cannot invoke those commands.

## What each command copies

| Command | Source of the file list | What lands on the board |
|---|---|---|
| Copy Files | that experiment's `.vscode/cpfiles.txt` | each active line, overwrite. `source -> /dest` renames on the board. Blank lines and lines that start with `#` are skipped |
| Copy Libs | the whole `lib/` tree | unfiltered recursive copy, then a macOS `dot_clean -m` of the whole drive (deletes `._*` only) |

Experiments that have a manifest and no local sync script: exp11, exp13, exp14, exp15. Their routine copy path is these two commands. Exp16's routine path is the two scripts in `tooling-sync-files-to-board.md` and `tooling-sync-lib-to-board.md`.

## Limitations

- Copy Files and Copy Libs read `workspace.workspaceFolders[0]` only (32 uses in `dist/extension.js` 2.2.2, no `getWorkspaceFolder`). In a multi-root window every other experiment fails with `!! No files specified to copy exist !!`. Open that experiment's folder alone, or put it at index 0.
- No ignore file. `.circuitpyignore` is not implemented (grep of 2.2.2, 2026-09-11). Copy Libs ships `__pycache__`, `.DS_Store`, `README.md`, and `*.pyc`.
- A trailing `# comment` on an active `source -> /dest` line becomes part of the board filename. The extension does not strip it. Put the comment on its own line. Exp16's file-sync script does strip it; the extension still does not.
- Copy overwrites even when the bytes already match. Each write can reload the board. `dot_clean` then walks the whole volume.
- `#` is tested before trim, so a line that starts with a space and then `#` is not a comment.

## Maintenance

Before stating a new fact about this extension, read `resources/helpfile.md` in the installed folder and grep `dist/extension.js`. A 2026-09-11 memory claim about `.circuitpyignore` was wrong because that check was skipped. Do not edit the installed extension. The manifest-authoring rule is the durable fix for the comment bug.

Settings keys `circuitpythonsync.drivepath`, `cpfullversion`, `cpboardname`, `curlibtag` live in the active workspace file `~/Development/Cursor Workspaces/circuitpython.code-workspace`, not in each experiment's `.vscode/settings.json`. Which workspace file is open: concept *Determining which `.code-workspace` file* in `tooling.md`.

## Todos

- None on the extension itself. Exp16 already routes routine copies through the scripts.
- If a later version is installed, re-check `workspaceFolders[0]`, the comment parse, and whether Copy Files still overwrites identical bytes. Record the version in the overview row.

## Incident log

The dated follow-ups (dot_clean accounting, lib-wipe exoneration, multi-root repro) stay in `tooling.md` § *two similarly-named extensions*. This file is the current operating note.

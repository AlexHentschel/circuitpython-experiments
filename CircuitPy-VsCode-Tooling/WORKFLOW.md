# CircuitPython VSCode Workflow Cheat Sheet

## Adding a New Experiment

1. Create experiment folder: `2026-XX_ExpNN_<BoardName>_<ProjectName>/`
2. Add folder to workspace file (`.code-workspace`):
   ```json
   "folders": [
     { "path": "2026-XX_ExpNN_...", "name": "ExpNN: Description" }
   ]
   ```
3. **Copy `.vscode/settings.json`** from an existing experiment with the same board
   - Update board-specific values if using a different board (VID/PID)
   - Ensure `python.analysis.extraPaths` has all three paths (see below)
4. Create `code.py`, `settings.toml`, `lib/`, `sd/` as needed
5. **(Optional) Create `.circuitpyignore`**
   - Use standard gitignore syntax to exclude specific local files/folders from syncing to the board (e.g., `micropython/`, `docs/`)
   - The sync tool automatically includes `code.py`, `lib/`, etc., and automatically excludes `.git/`, `.vscode/`, `venv/`
   - Use this file only for *project-specific* artifacts you want to keep local

## Per-Experiment Settings (`<experiment>/.vscode/settings.json`)

| Setting | Description | Source |
|---------|-------------|--------|
| `circuitpython.board.vid` | Board Vendor ID | See "Finding VID/PID" below |
| `circuitpython.board.pid` | Board Product ID | See "Finding VID/PID" below |
| `circuitpython.board.version` | CircuitPython version | `boot_out.txt` |
| `python.analysis.extraPaths` | IntelliSense stubs | Copy from existing (all 3 paths!) |

### Finding VID/PID Values

**Option 1: Use pyserial** (Recommended - already installed in your venv)
```bash
# With board connected:
python -c "
import serial.tools.list_ports
for p in serial.tools.list_ports.comports():
    if p.vid:
        print(f'{p.description}')
        print(f'  VID: {hex(p.vid)}  PID: {hex(p.pid)}')
        print(f'  Port: {p.device}')
"
```

Example output:
```
BPI_Bit_S2 - CircuitPython CDC control
  VID: 0x303a  PID: 0x80e6
  Port: /dev/cu.usbmodem0740D10F1BE91
```

**Option 2: Query USB device directly** (macOS - requires decimal→hex conversion)
```bash
# With board connected:
ioreg -p IOUSB -l | grep -E "idVendor|idProduct|USB Product Name"
```

Find your board by name (e.g., "BPI_Bit_S2"), then convert decimal values to hex:
```bash
# Example: idVendor = 12346, idProduct = 32998
python -c "print(f'VID: {hex(12346)}  PID: {hex(32998)}')"
# Output: VID: 0x303a  PID: 0x80e6
```

**Common VIDs:**
- `0x239A` = Adafruit
- `0x303A` = Espressif (ESP32-S2/S3 boards like BPI-Bit-S2)

**Required `extraPaths`** (VSCode doesn't merge arrays!):
```json
"python.analysis.extraPaths": [
    // Board-specific stubs
    "/Users/alex/.vscode/extensions/wmerkens.vscode-circuitpython-v2-0.3.4/boards/0x303A/0x80E6",
    // Common CircuitPython stubs
    "/Users/alex/.vscode/extensions/wmerkens.vscode-circuitpython-v2-0.3.4/stubs",
    // Adafruit bundle (neopixel, etc.)
    "/Users/alex/Library/Application Support/Code/User/globalStorage/wmerkens.vscode-circuitpython-v2/bundle/20260124/adafruit-circuitpython-bundle-py-20260124/lib"
]
```

**Optional overrides** (skip auto-detection):
```json
"circuitpython.drive": "/Volumes/CIRCUITPY",
"circuitpython.serialPort": "/dev/cu.usbmodem..."
```

## Extension Limitation: "Choose Board" in Multi-Root Workspace

⚠️ **Do NOT use `CircuitPython: Choose CircuitPython Board` in a multi-root workspace!**

The wmerkens CircuitPython V2 extension:
- Writes board settings (`vid`, `pid`) to the **workspace file** (not folder-specific)
- **Overwrites** `python.analysis.extraPaths` (loses bundle path!)
- Does not support `ConfigurationTarget.WorkspaceFolder`

**Workaround:** Manually maintain board settings in each experiment's `.vscode/settings.json`.

**If you accidentally ran "Choose Board":**
1. Check workspace file - remove any `circuitpython.board.*` settings
2. Restore `python.analysis.extraPaths` in workspace file (add back bundle path)
3. Verify experiment's `.vscode/settings.json` has correct paths

## Debug Commands (Command Palette: `⌘⇧P`)

| Command | Purpose |
|---------|---------|
| `Tasks: Run Task` → `CircuitPython: print python interpreter path [DEBUG]` | Verify Python venv config |
| `Tasks: Run Task` → `CircuitPython: Auto-detect CIRCUITPY Drive [DEBUG]` | Test drive detection |
| `Tasks: Run Task` → `CircuitPython: Auto-detect Port [DEBUG]` | Test serial port detection |

## Development Commands (Command Palette: `⌘⇧P`)

| Command | Purpose |
|---------|---------|
| `Tasks: Run Task` → `CircuitPython: Sync To CIRCUITPY Drive` | Sync files only |
| `Tasks: Run Task` → `CircuitPython: Sync & Soft Reload` | Sync + restart board |
| `Tasks: Run Task` → `CircuitPython: Interrupt & Open REPL` | Stop code + interactive REPL |

## Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│  Edit code.py  →  Sync & Soft Reload  →  Watch serial out  │
└─────────────────────────────────────────────────────────────┘
```

**Before reload**: Close serial monitor (only one program can use the port)

**Keyboard shortcut tip**: Bind `Sync & Soft Reload` to a key for faster iteration:
- Open Keyboard Shortcuts (`⌘K ⌘S`)
- Search: `workbench.action.tasks.runTask`
- Add keybinding with args: `CircuitPython: Sync & Soft Reload`

## Gotchas

**VSCode doesn't merge arrays**: If you define `python.analysis.extraPaths` in experiment settings, 
it completely overrides the workspace setting. You must include ALL paths in the experiment's setting:
- Board stubs (`boards/<VID>/<PID>`)
- Common stubs (`stubs/`)
- Adafruit bundle (`lib/`)

**Pylance can't find neopixel?** → Check `extraPaths` includes the bundle path, not just board stubs.

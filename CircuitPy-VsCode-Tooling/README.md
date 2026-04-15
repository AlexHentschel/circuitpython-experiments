# CircuitPython VSCode Development Environment

Modular, cross-platform tooling for CircuitPython development with auto-detection, code completion, and integrated deployment workflow.

## Design

This setup follows **Unix philosophy: small tools that do one thing well, composed together**.

**Design:**
- **Single-purpose Python scripts** - Pure auto-detection (no configuration logic)
- **Shell composition in tasks.json** - Config reader + auto-detect fallback
- **Optional configuration** - Settings can be omitted entirely


```
┌─────────────────────────────────────────────────────────────────┐
│                      VSCode Tasks                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Sync & Soft Reload (primary workflow)                   │   │
│  │    ├─► read_setting.py (try config) ──┐                  │   │
│  │    ├─► detect_circuitpy_drive.py (fallback) → rsync      │   │
│  │    ├─► detect_circuitpy_port.py → serial port            │   │
│  │    └─► circuitpython_soft_reload.py (restart board)      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Core Scripts

| Script | Purpose | Exit Codes | Key Feature |
|--------|---------|------------|-------------|
| `read_setting.py` | Extract single setting from settings.json | 0=found, 1=not found, 2=error | Silent failure for shell composition |
| `detect_circuitpy_drive.py` | Auto-detect CIRCUITPY mount point | 0=found, 1=not found, 2=ambiguous, 3=error | Pure auto-detection, no config |
| `detect_circuitpy_port.py` | Auto-detect serial port (VID/PID scoring) | 0=found, 1=not found, 2=ambiguous, 3=error | Pure auto-detection, no config |
| `circuitpython_soft_reload.py` | Send reload command to board | 0=success, 1=invalid args, 2=port error, 3=error | Accepts port path as argument |

**Composition Pattern:**
```bash
# Production tasks: config with fallback
DRIVE=$(python read_setting.py "circuitpython.drive") \
  || DRIVE=$(python detect_circuitpy_drive.py) \
  || { echo 'Failed to detect drive' >&2; exit 1; }

# Debug tasks: always auto-detect (bypass config)
DRIVE=$(python detect_circuitpy_drive.py) || exit 1
```

### Configuration Files

| File | Purpose |
|------|---------|
| `settings.json` | VSCode Python environment, CircuitPython stubs, optional drive/port overrides |
| `tasks.json` | Automated sync and reload workflows with shell composition |

**See Also:**
- [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md) - Keybinding configuration for quick task execution
- [VS Code.txt](../VS%20Code.txt) - Detailed setup history and troubleshooting notes

---

## Quick Start

### Prerequisites

1. **Python Virtual Environment**
   ```bash
   # Create venv (one-time)
   python3 -m venv ~/Development/PythonVEs/CircuitPython_3.13_VsCode
   
   # Activate
   source ~/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/activate
   
   # Install dependencies
   pip install pyserial circup circuitpython-stubs adafruit-circuitpython-typing
   ```

2. **VSCode Extensions** (in CircuitPython profile)
   - Python (Microsoft)
   - Pylance
   - CircuitPython v2 (wmerkens)
   - Serial Monitor (Microsoft) - workaround for wmerkens extension serial monitor issue

3. **Platform Tools**
   - macOS: `rsync` (built-in)
   - Linux: `rsync` (usually pre-installed), user in `dialout` group
   - Windows: `rsync` via Git for Windows/MSYS2, or replace with robocopy

### Basic Workflow

1. Edit code locally (e.g., code.py)
2. Deploy and reload: `Command Palette` → `Tasks: Run Task` → `CircuitPython: Sync & Soft Reload`
3. View output in VSCode Serial Monitor **or** terminal REPL (see below)

**Optional:** Configure keyboard shortcut (see [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md)) for one-key deployment.

### Terminal REPL (Alternative to Serial Monitor)

If wmerkens CircuitPython extension serial monitor has issues, use terminal-based REPL:

**Option 1: Use VSCode Task (Recommended - handles interruption automatically)**
```
Command Palette → Tasks: Run Task → CircuitPython: Interrupt & Open REPL
```
This programmatically interrupts running code and opens miniterm.

**Option 2: Manual miniterm**
```bash
# Connect to REPL
python -m serial.tools.miniterm /dev/cu.usbmodem0740D10F1BE91 115200

# Interrupt running program: Press Ctrl-C 2-3 times rapidly
# (CircuitPython requires two Ctrl-C to stop code execution)
# → You should see >>> REPL prompt

# Reload code: Ctrl-D
# Exit miniterm: Ctrl-]
```

**Auto-detect port:**
```bash
PORT=$(python .vscode/detect_circuitpy_port.py)
python .vscode/circuitpython_interrupt_and_repl.py "$PORT"
```

**Note:** If manual Ctrl-C doesn't work (tight loop), use Option 1 (task) which sends interrupt programmatically.

---

## Tool Reference

### 1. read_setting.py

**Purpose:** Extract single setting from `.vscode/settings.json` for shell composition.

**Usage:**
```bash
python read_setting.py "circuitpython.drive"  # Returns value or exits 1
```

**Exit Codes:** 0=found, 1=not found/empty, 2=error  
**Key Feature:** Silent on "not found" (exit 1, no stderr) - perfect for `||` fallback chains

---

### 2. detect_circuitpy_drive.py

**Purpose:** Locate CIRCUITPY USB drive mount point across platforms.

**Detection Strategy:**
- **macOS:** `/Volumes/CIRCUITPY*`
- **Linux:** `/media/$USER/CIRCUITPY`, `/run/media/$USER/CIRCUITPY`, `/mnt/CIRCUITPY`
- **Windows:** `D:` through `Z:` (scans for marker files)

**Validation:** Checks for `boot_out.txt`, `code.py`, or `lib/` directory.

**Usage:**
```bash
DRIVE=$(python detect_circuitpy_drive.py) && echo "Found: $DRIVE"
```

**Exit Codes:** 0=success, 1=not found, 2=multiple found (using first), 3=error

**Troubleshooting:**
- **Not detected:** Verify board connected, CircuitPython running (not bootloader mode)
- **Linux:** Check `lsblk`, verify automount, manually mount if needed

---
### 3. detect_circuitpy_port.py

**Purpose:** Auto-detect CircuitPython serial port using heuristic scoring.

**Scoring System:**
- VID/PID match (configurable): +1000 points
- Device name patterns: `usbmodem` (+200), `ttyACM` (+180), `ttyUSB` (+120), `COM` (+150)
- Description keywords: CircuitPython (+120), CDC (+60), Adafruit (+60), Espressif (+50)

**Usage:**
```bash
PORT=$(python detect_circuitpy_port.py) && python circuitpython_soft_reload.py "$PORT"
```

**Exit Codes:** 0=success, 1=no ports, 2=ambiguous (multiple tied), 3=error

**Configuration:**
```python
PREFERRED_VID = 0x303A  # ESP32-S2 (adjust for your board)
PREFERRED_PID = 0x80E6  # BPI-Bit-S2
DEBUG_SCORING = False   # Set True for detailed scoring output
```

**Troubleshooting:**
- **No ports:** Check USB cable, drivers, Linux permissions (`dialout` group)
- **Wrong port:** Set VID/PID for your board, enable `DEBUG_SCORING`

---

### 4. circuitpython_soft_reload.py

**Purpose:** Send soft reload command to CircuitPython REPL over serial.

**Mechanism:** Opens port (115200 baud) → Send `Ctrl-C` twice → Execute `supervisor.reload()`

**Usage:**
```bash
python circuitpython_soft_reload.py /dev/cu.usbmodem0740D10F1BE91
```

**Exit Codes:** 0=success, 1=invalid args, 2=port error (busy/nonexistent), 3=error

**Troubleshooting:**
- **Port busy:** Close all serial monitors (only one program can access port)
- **Permission denied (Linux):** `sudo usermod -a -G dialout $USER` (logout/login)

---

### 5. tasks.json - VSCode Task Automation

**Primary Task:** `CircuitPython: Sync & Soft Reload`
```bash
# 1. Sync files (dependency task)
# 2. Capture Python interpreter (avoid VSCode multi-resolution bug)
SETTINGS_DEFAULT_PYTHON_PATH="${command:python.interpreterPath}"

# 3. Composition: try config → fallback to auto-detect
PORT=$("$SETTINGS_DEFAULT_PYTHON_PATH" read_setting.py "circuitpython.serialPort") \
  || PORT=$("$SETTINGS_DEFAULT_PYTHON_PATH" detect_circuitpy_port.py) \
  || exit 1

# 4. Send reload
"$SETTINGS_DEFAULT_PYTHON_PATH" circuitpython_soft_reload.py "$PORT"
```

**Note:** `SETTINGS_DEFAULT_PYTHON_PATH` variable prevents VSCode from incorrectly resolving `${command:python.interpreterPath}` to system Python on subsequent uses.

**Rsync Filters (Sync Task):**
- `--delete` - Mirror deletions
- `--modify-window=2` - Tolerate FAT timestamp coarseness
- `--include '/code.py' '/main.py' '/boot.py' '/settings.toml' '/lib/***'` - Whitelist
- `--exclude '*'` - Blacklist everything else
- `--exclude '._*'` - Skip macOS metadata

**Debug Tasks:**
- `Auto-detect CIRCUITPY Drive [DEBUG]` - Always runs auto-detect (bypasses config)
- `Auto-detect Port [DEBUG]` - Outputs suggested settings.json configuration
- `print python.interpreterPath [DEBUG]` - Verify Python environment

---
### 6. settings.json - VSCode Configuration

**Essential Settings:**
```json
{
    // Explicitly select the CircuitPython venv
    "python.defaultInterpreterPath": "/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/python",

    // CircuitPython v2 bundle config (prevents "localBundleDir or tag is not set")
    "circuitpython.bundle.localBundleDir": "/Users/alex/Development/VsCode/CircuitPython/bundles",
    "circuitpython.bundle.tag": "latest",

    // Keep type checking light (CircuitPython stubs are partial by nature)
    "python.analysis.typeCheckingMode": "basic",

    // Optional but helps avoid stale indexing
    "python.analysis.autoSearchPaths": true,
    "python.languageServer": "Pylance",
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingModuleSource": "none",
        "reportShadowedImports": "none"
    }
}
```


**Setting Context:**
- **defaultInterpreterPath:** Isolates CircuitPython dependencies from other projects
- **bundle config:** Prevents "localBundleDir or tag is not set" extension error
- **typeCheckingMode: basic:** CircuitPython stubs are partial; strict mode generates noise
- **diagnosticSeverityOverrides:** Suppresses unavoidable CircuitPython stub limitations

running the following VSCode Command Palette [Cmd + Shift + P] should add more details to the `.vscode/settings.json`:
* Command Palette → `Developer: Reload Window`
* Command Palette → `CircuitPython: Check for latest bundle`
* Command Palette → `CircuitPython: Choose CircuitPython Board`


**Possibly important extensions:**

Optionally, we might need to configure the CircuitPython major version, by adding the following line to the `.vscode/settings.json`:
>   "circuitpython.board.version": "10.0.3"  


**Optional Drive/Port Overrides** (keys can be omitted):
```json
{
  "circuitpython.drive": "/Volumes/CIRCUITPY",       // macOS
  "circuitpython.serialPort": "/dev/cu.usbmodem*"    // Skip auto-detect
}
```

**Rationale:**
- **defaultInterpreterPath:** Isolates CircuitPython dependencies
- **typeCheckingMode: basic:** CircuitPython stubs are partial; strict mode is too noisy
- **Optional overrides:** Tasks try these first, fallback to auto-detect if missing

---

## Testing & Debugging

**Test Individual Tools:**
```bash
# Config reader (should exit 1 if key missing, no stderr)
python read_setting.py "circuitpython.drive" && echo "Found" || echo "Not found"

# Drive detection
python detect_circuitpy_drive.py

# Port detection  
python detect_circuitpy_port.py

# Full composition
DRIVE=$(python read_setting.py "circuitpython.drive") \
  || DRIVE=$(python detect_circuitpy_drive.py) \
  || exit 1
echo "Using: $DRIVE"
```

**Enable Debug Mode:**
```python
# In detect_circuitpy_drive.py or detect_circuitpy_port.py
DEBUG = True  # Shows detailed detection/scoring output
```

---

## Platform-Specific Notes

**macOS** (current setup):
- rsync: Built-in
- Ports: `/dev/cu.usbmodem*` (prefer `cu.*` for outbound)
- Drive: `/Volumes/CIRCUITPY`

**Linux** (additional setup):
- Permissions: `sudo usermod -a -G dialout $USER` (logout/login)
- rsync: Usually pre-installed (`which rsync`)
- Ports: `/dev/ttyACM*` (CDC) or `/dev/ttyUSB*` (UART)
- Drives: `/media/$USER/CIRCUITPY`, `/run/media/$USER/CIRCUITPY`

**Windows**:
- Install rsync: Git for Windows, MSYS2, or WSL
  - Alternative: Replace with robocopy (built-in, less elegant)
- Ports: `COM3`, `COM4`, etc. (Device Manager)
- Drives: `D:`, `E:`, `F:` (auto-detected by script)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Drive not found" | Verify board connected, CircuitPython running (not bootloader mode) |
| "Serial port busy" | Close all serial monitors (only one program can access port) |
| "Permission denied" (Linux) | Add user to `dialout` group, logout/login |
| "pyserial not installed" | Activate venv, `pip install pyserial` |
| "Code doesn't reload" | Check USB cable, increase delays in `circuitpython_soft_reload.py` |
| "Wrong port/drive" | Set VID/PID in scripts, enable DEBUG mode |

---

## Advanced Topics

### Adding New Boards

1. Find VID/PID: `system_profiler SPUSBDataType | grep -A 10 CircuitPython` (macOS)
2. Update `detect_circuitpy_port.py`:
   ```python
   PREFERRED_VID = 0xYOUR_VID
   PREFERRED_PID = 0xYOUR_PID
   ```
3. Update `settings.json` for CircuitPython extension

### Customizing Sync Filters

```json
// In tasks.json rsync command, add:
"--include '/secrets.py'",
"--include '/config.json'",
"--exclude '/lib/unused_library.mpy'",
```

### Future Composition Extensions

```bash
# Environment variable override
DRIVE="${CIRCUITPY_DRIVE:-}" \
  || DRIVE=$(python read_setting.py "circuitpython.drive") \
  || DRIVE=$(python detect_circuitpy_drive.py) \
  || exit 1

# Validation layer
DRIVE=$(python detect_circuitpy_drive.py) || exit 1
[ -d "$DRIVE" ] || { echo "Drive not accessible" >&2; exit 1; }

# Caching layer
CACHE=".vscode/.circuitpy_drive_cache"
DRIVE=$(cat "$CACHE" 2>/dev/null) \
  || DRIVE=$(python detect_circuitpy_drive.py | tee "$CACHE") \
  || exit 1
```

All extensions use **pure shell composition** - no Python script changes needed!

---

## Known Issues

**1. VSCode Python Interpreter Multi-Resolution Bug**
- **Issue:** Multiple `${command:python.interpreterPath}` uses resolve inconsistently (falls back to system Python)
- **Workaround:** Capture once: `SETTINGS_DEFAULT_PYTHON_PATH="${command:python.interpreterPath}"`

**2. wmerkens CircuitPython v2 Serial Monitor (macOS)**
- **Issue:** `command 'circuitpython.openSerialMonitor' not found`
- **Workaround:** Use Microsoft's Serial Monitor extension

**3. macOS ._* AppleDouble Files**
- **Issue:** macOS creates metadata files on FAT drives
- **Fix:** Already handled by rsync filters (`--filter 'P ._*'`, `--exclude '._*'`)


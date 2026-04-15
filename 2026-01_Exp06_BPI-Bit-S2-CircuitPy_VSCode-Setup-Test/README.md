# CircuitPython VSCode Setup - Quick Reference

This workspace is configured for CircuitPython development with auto-detection and integrated deployment.

## Quick Start

**Deploy code to board:**
```
Command Palette (Cmd+Shift+P) → Tasks: Run Task → "CircuitPython: Sync & Soft Reload"
```

**What it does:**
1. Captures Python interpreter path defined is `.vscode/settings.json` (avoids VSCode multi-resolution bug)
2. Auto-detects CIRCUITPY drive
3. Syncs changed files (`code.py`, `lib/`, etc.)
4. Auto-detects serial port
5. Sends soft reload to board
6. Board restarts with new code

## File Structure

```
├── code.py                      # Main program (edit this)
├── boot_out.txt                 # Boot output log
├── settings.toml                # Configuration
├── lib/                         # CircuitPython libraries
├── .vscode/                     # Local configuration
│   └── settings.json            # Experiment-specific settings
└── ../CircuitPy-VsCode-Tooling/ # Shared Development Tooling
    ├── README.md                # Complete documentation
    ├── WORKFLOW.md              # Short Workflow Overview
    ├── detect_circuitpy_drive.py
    ├── detect_circuitpy_port.py
    ├── circuitpython_soft_reload.py
    └── ...
```

## Common Tasks

| Task | Command |
|------|---------|
| Deploy & reload | `Tasks: Run Task` → `CircuitPython: Sync & Soft Reload` |
| Sync files only | `Tasks: Run Task` → `CircuitPython: Sync To CIRCUITPY Drive` |
| Check Python env | `Tasks: Run Task` → `CircuitPython: print python.interpreterPath [DEBUG]` |
| Open serial monitor | Serial Monitor icon (bottom toolbar) |

## Troubleshooting

**"CIRCUITPY drive not found"**
- Check board is connected and CircuitPython is running
- Look for CIRCUITPY in Finder

**"Serial port busy"**
Only one program can access the port at a time. Hence, close Serial Monitor before running `CircuitPython: Sync & Soft Reload`.

**"Permission denied" (Linux)**
- Add user to dialout group: `sudo usermod -a -G dialout $USER`
- Logout and login

**"Module not found" errors (despite venv having module)**
- This is a VSCode bug with `${command:python.interpreterPath}` multi-resolution
- Tasks already use `SETTINGS_DEFAULT_PYTHON_PATH` workaround
- Run debug task to verify correct interpreter is being used

## Full Documentation

See [../CircuitPy-VsCode-Tooling/README.md](../CircuitPy-VsCode-Tooling/README.md) for:
- Detailed component documentation
- Platform-specific setup (macOS/Linux/Windows)
- Architecture overview
- Advanced configuration
- Troubleshooting guide

## Configuration confirmed working

- **Board:** BPI-Bit-S2 (ESP32-S2)
- **CircuitPython:** 10.0.3
- **Python Env:** `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`
- **CIRCUITPY Drive:** Auto-detected
- **Serial Port:** Auto-detected (VID: 0x303A, PID: 0x80E6)

- MacOS 26.2
- VsCode Version: 1.108.2 (Universal) for MacOS arm64
- wmerkens' "CircuitPython v2" Extension version 0.3.4.
- Microsoft's `Serial Monitor` (serial monitor wasn't available in  wmerkens'  MacOS build of the extension "CircuitPython v2" version 0.3.4)

## Troubleshooting

Check [../CircuitPy-VsCode-Tooling/README.md](../CircuitPy-VsCode-Tooling/README.md) for setup history.

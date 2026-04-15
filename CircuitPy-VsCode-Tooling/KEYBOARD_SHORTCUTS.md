# Keyboard Shortcuts for CircuitPython Tasks

## Recommended Shortcut: Sync & Soft Reload

Add this to your **user** `keybindings.json` (not workspace-specific):

**macOS:**
```json
{
  "key": "cmd+shift+r",
  "command": "workbench.action.tasks.runTask",
  "args": "CircuitPython: Sync & Soft Reload"
}
```

**Linux/Windows:**
```json
{
  "key": "ctrl+shift+r",
  "command": "workbench.action.tasks.runTask",
  "args": "CircuitPython: Sync & Soft Reload"
}
```

## How to Configure

### Method 1: Via Command Palette
1. Open Command Palette: `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Linux/Windows)
2. Type: `Preferences: Open Keyboard Shortcuts (JSON)`
3. Add the binding to your `keybindings.json`

### Method 2: Via UI
1. Open Command Palette: `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Linux/Windows)
2. Type: `Preferences: Open Keyboard Shortcuts`
3. Search for: `Tasks: Run Task`
4. Click the `+` icon to add a keybinding
5. Press your desired key combination (e.g., `Cmd+Shift+R`)
6. In the "When" expression field, leave it empty or set appropriate context

**Note:** The UI method creates a generic "Run Task" binding. You'll need to select the task from a list each time. For direct execution, use Method 1 (JSON configuration).

## Alternative Shortcuts

### Sync Only (without reload)
```json
{
  "key": "cmd+shift+s",
  "command": "workbench.action.tasks.runTask",
  "args": "CircuitPython: Sync To CIRCUITPY Drive"
}
```

### Debug Tasks
```json
{
  "key": "cmd+shift+d cmd+shift+d",  // Double tap: Cmd+Shift+D twice
  "command": "workbench.action.tasks.runTask",
  "args": "CircuitPython: Auto-detect CIRCUITPY Drive [DEBUG]"
},
{
  "key": "cmd+shift+d cmd+shift+p",  // Cmd+Shift+D then Cmd+Shift+P
  "command": "workbench.action.tasks.runTask",
  "args": "CircuitPython: Auto-detect Port [DEBUG]"
}
```

## Checking for Conflicts

Before adding a shortcut, verify it doesn't conflict:

1. Open Keyboard Shortcuts UI: `Cmd+Shift+P` → `Preferences: Open Keyboard Shortcuts`
2. Search for your desired key combination (e.g., `cmd+shift+r`)
3. Review existing bindings - common conflicts:
   - `Cmd+Shift+R` (macOS): Often unassigned or used for "Reload Window"
   - `Ctrl+Shift+R` (Linux): May conflict with browser refresh in some contexts

### Resolving Conflicts

If your desired shortcut is already in use, you have options:

**Option 1: Add a "when" clause** to make bindings context-specific:
```json
{
  "key": "cmd+shift+r",
  "command": "workbench.action.tasks.runTask",
  "args": "CircuitPython: Sync & Soft Reload",
  "when": "editorLangId == python"  // Only active in Python files
}
```

**Option 2: Disable the conflicting binding:**
```json
{
  "key": "cmd+shift+r",
  "command": "-workbench.action.reloadWindow"  // Note the minus sign
}
```

**Option 3: Choose a different shortcut:**
- `Cmd+K Cmd+R` (chord: Cmd+K then Cmd+R)
- `Cmd+Option+R` (macOS) / `Ctrl+Alt+R` (Linux/Windows)
- `F5` (classic "run" key, if not used by debugger)

## Full Example Configuration

Here's a complete CircuitPython keybindings setup:

```json
[
  // Primary workflow: Sync & Reload
  {
    "key": "cmd+shift+r",
    "command": "workbench.action.tasks.runTask",
    "args": "CircuitPython: Sync & Soft Reload",
    "when": "editorLangId == python"
  },
  
  // Alternative: Sync only (no reload)
  {
    "key": "cmd+k cmd+s",
    "command": "workbench.action.tasks.runTask",
    "args": "CircuitPython: Sync To CIRCUITPY Drive"
  },
  
  // Debug: Auto-detect drive
  {
    "key": "cmd+k cmd+d",
    "command": "workbench.action.tasks.runTask",
    "args": "CircuitPython: Auto-detect CIRCUITPY Drive [DEBUG]"
  },
  
  // Debug: Auto-detect port
  {
    "key": "cmd+k cmd+p",
    "command": "workbench.action.tasks.runTask",
    "args": "CircuitPython: Auto-detect Port [DEBUG]"
  }
]
```

## Testing Your Shortcut

1. Save your `keybindings.json`
2. Open a Python file in your CircuitPython workspace
3. Press your configured shortcut (e.g., `Cmd+Shift+R`)
4. The task should execute in the terminal panel

**Troubleshooting:**
- If nothing happens: Check for conflicting keybindings
- If wrong task runs: Verify the `"args"` value matches the task label exactly
- If prompted to select a task: Your binding might be generic; use the JSON method with specific `"args"`

## Quick Access Without Shortcuts

If you prefer not to configure shortcuts:

1. **Tasks Menu**: `Terminal` → `Run Task...` → Select task
2. **Command Palette**: `Cmd+Shift+P` → `Tasks: Run Task` → Select task
3. **Recent Tasks**: `Terminal` → `Run Recent Task` (shows last executed tasks)

## Platform-Specific Notes

### macOS
- `Cmd` is the primary modifier (Command key)
- `Option` (⌥) can be used for additional combinations
- Avoid conflicts with system shortcuts (Cmd+Q, Cmd+W, etc.)

### Linux
- `Ctrl` is the primary modifier
- `Alt` can be used for additional combinations
- Some desktop environments (GNOME, KDE) have system-wide shortcuts that may conflict

### Windows
- `Ctrl` is the primary modifier
- `Alt` can be used for additional combinations
- Windows key shortcuts are usually safe from conflicts

## Best Practices

1. **Use chords for debug tasks**: Reserve simple shortcuts for frequent operations
2. **Add "when" clauses**: Prevent accidental task execution in wrong contexts
3. **Document your choices**: Add comments in `keybindings.json` for future reference
4. **Test after changes**: Verify shortcuts work as expected before relying on them

## Example: Minimal Setup (Just the Essentials)

If you only want one shortcut for the most common operation:

```json
[
  {
    "key": "cmd+shift+r",  // or "ctrl+shift+r" on Linux/Windows
    "command": "workbench.action.tasks.runTask",
    "args": "CircuitPython: Sync & Soft Reload"
  }
]
```

This gives you a single keypress to deploy and reload your CircuitPython code!

---

## Manual Workflow: Sending Code to the CircuitPython REPL

There is no built-in VS Code shortcut for sending code directly to the CircuitPython REPL with correct indentation. Use this manual workflow:

1. **Open the REPL**: Run the task `CircuitPython: Interrupt & Open REPL` (see above for shortcut setup).
2. **Enter Paste Mode**: Click in the REPL terminal and press `Ctrl+E` (Windows/Linux/macOS: Control key, not Command).
3. **Paste your code**: Copy the code you want to run, then paste it into the REPL terminal (`Cmd+V` on macOS, `Ctrl+V` on Windows/Linux).
4. **Execute**: Press `Ctrl+D` to exit Paste Mode and execute the code block.

**Tip:** Paste Mode is required for multi-line code (functions, loops, etc.) to avoid indentation errors.

There is currently no reliable macro or extension to automate this sequence in VS Code for CircuitPython REPL.

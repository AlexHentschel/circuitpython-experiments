#!/usr/bin/env python3
"""
Read a setting from .vscode/settings.json

Simple utility to extract a single setting value from VSCode settings.
Used for shell script composition.

Exit codes:
0 - Setting found and has non-empty value (printed to stdout)
1 - Setting not found, is null, or is empty string
2 - Error reading settings file
"""

import sys
from pathlib import Path
import json5


def main():
    if len(sys.argv) < 2:
        print("Usage: read_setting.py <setting.key.name>", file=sys.stderr)
        return 2
    
    setting_key = sys.argv[1]
    
    try:
        settings_path = Path.cwd() / ".vscode" / "settings.json"
        
        # If no setting file, return 1 (not found) but don't error out loudly
        # The task script relies on exit code 1 to trigger auto-detection fallback.
        if not settings_path.exists():
            return 1
        
        try:
            with open(settings_path, "r") as f:
                settings = json5.load(f)
        except Exception as e:
            # PARSE ERROR: This is critical and should be reported
            print(f"Error parsing .vscode/settings.json: {e}", file=sys.stderr)
            print(f"Please check for syntax errors in {settings_path}", file=sys.stderr)
            return 2
        
        # Get nested key (e.g., "circuitpython.drive")
        # Support dot notation for nested keys if we wanted, but for now simple dict get
        value = settings.get(setting_key, "")
        
        # Return success only if value exists and is non-empty
        if value and str(value).strip():
            print(str(value).strip())
            return 0
        else:
            # Key not found is a normal case for fallback, so silent exit 1 is appropriate
            return 1

    except Exception as e:
        # UNEXPECTED ERROR: Report it
        print(f"Error reading settings: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

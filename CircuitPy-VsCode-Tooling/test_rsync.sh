#!/bin/bash
# FAST SUMMARY:
# Purpose: Validate rsync whitelist logic (tasks.json)
# Scope: Operates ONLY on local `./test_sync` directory
# Risk: Wipes/Overwrites `./test_sync` (nothing else is touched)
# Action: Creates mock `test_sync/src/` (project) & `dest` (drive). Syncs. Verifies rules.

rm -rf test_sync
mkdir -p test_sync/src/lib
mkdir -p test_sync/src/sd
mkdir -p test_sync/src/micropython
mkdir -p test_sync/src/.vscode
mkdir -p test_sync/dest/sd

# Create Source Files
touch test_sync/src/code.py
touch test_sync/src/settings.toml
touch test_sync/src/README.md
touch test_sync/src/boot_out.txt
touch test_sync/src/lib/neopixel.mpy
touch test_sync/src/micropython/driver.py
touch test_sync/src/.vscode/settings.json
touch test_sync/src/sd/placeholder.txt

# Create Dest Files (to test --delete and protection)
touch test_sync/dest/old_code.py
touch test_sync/dest/sd/board_log.txt

# Create .circuitpyignore for testing
echo "micropython/" > test_sync/src/.circuitpyignore

echo "Running rsync (Sync Everything + Ignore Strategy)..."

# Mimic the active logic from tasks.json
rsync -rv --delete --checksum \
  --filter 'P ._*' \
  --exclude '._*' \
  --exclude '.DS_Store' \
  --exclude '.git/' \
  --exclude '.vscode/' \
  --exclude '__pycache__/' \
  --exclude 'venv/' \
  --exclude 'node_modules/' \
  --exclude 'boot_out.txt' \
  --include '/sd/' \
  --exclude '/sd/*' \
  --exclude '.circuitpyignore' \
  $([ -f "test_sync/src/.circuitpyignore" ] && echo "--exclude-from=test_sync/src/.circuitpyignore") \
  test_sync/src/ test_sync/dest/

echo "--- RESULTS ---"
echo "Root (should contain: code.py, settings.toml, README.md):"
ls -1 test_sync/dest/
echo "Should NOT contain: boot_out.txt, .vscode, micropython:"
echo "Lib (should have neopixel.mpy):"
ls -1 test_sync/dest/lib/
echo "SD (should only have board_log.txt - placeholder.txt is local only):"
ls -1 test_sync/dest/sd/

# Technical Domain Knowledge

Last updated: 2026-04-20 (session 3: dropped human-elevation language from the status-default rule; schema and tables unchanged — still cold-start, no content entries yet)

Domain: CircuitPython multi-experiment workspace. Categories below are the authoritative schema (the domain rule file `02-domain-structure.mdc` just lists them; the intent notes for each category live here as HTML comments). All entries default to `unverified` until evidence is gathered; promote to `evidence-supported` once corroborated by independent sources (datasheets, official CircuitPython docs, on-device behavior, or mechanical verification). No separate human-elevation tier — the user is project owner but not the CircuitPython domain authority. Tag every entry with experiment scope: `[expNN]`, `[tooling]`, `[cross-experiment]`, or `[universal]`.

## Terminology

<!-- Ground domain terms on first use. Cite the source (RFC, datasheet, Adafruit doc, code path). -->

| Term | Definition | Source | Status |
|------|------------|--------|--------|

## Boards & MCUs

<!-- Per-experiment board profile. One row per board actually used. Pin maps go in subsections below, one subtable per board. Stub paths use the Pylance extraPaths convention (boards/<VID>/<PID>). -->

| Board | MCU | VID:PID | Stub paths | CircuitPython version | Used in | Status |
|-------|-----|---------|------------|----------------------|---------|--------|

### Pin Maps

<!-- One `### <Board name>` subsection per board, each with its own pin table. -->

## CircuitPython Library Map

<!-- Libraries pulled from the Adafruit bundle (via `circup` or the VS Code extension) plus any local `lib/` modules. Note the source so upgrade paths are clear. -->

| Library | Version | Source (bundle / community / local lib/) | Used in | Status |
|---------|---------|-------------------------------------------|---------|--------|

## Hardware-Interfacing Patterns

<!-- Reusable idioms: WS2812 timing, framebuffer/display init, I2C scan, UART bridging, etc. Record minimal working examples by reference (path + line range) — do NOT copy code. -->

| Pattern | Peripheral | Library | Reference experiment | Code reference | Status |
|---------|-----------|---------|---------------------|----------------|--------|

## Pin / Peripheral Assumptions

<!-- E.g. "WS2812 data on GP15 with PIO", "I2C0 on GP4/GP5". Always tag with the board the assumption was verified on — it may not transfer. -->

| Assumption | Basis | Verified-against board | Scope | Status |
|------------|-------|------------------------|-------|--------|

## Toolchain

<!-- Python venv path, Pylance stubs paths (board-specific + bundle stubs), bundle directory + refresh policy, circup workflow, serial monitor / REPL approach, tasks in .vscode/tasks.json, VS Code quirks (e.g. arrays don't merge across settings layers). -->

| Item | Detail | Status |
|------|--------|--------|

## Code Map

<!-- One row per non-trivial file. Experiment column allows cross-experiment comparison once 2+ experiments are attached. -->

| File | Experiment | Purpose | Key functions/classes |
|------|------------|---------|----------------------|

## Verification Queue

<!-- Items recorded as `unverified` that matter enough to confirm on code before promotion. FIFO is fine; no strict priority. -->

| Item | Why it matters | Pointer | Added |
|------|----------------|---------|-------|

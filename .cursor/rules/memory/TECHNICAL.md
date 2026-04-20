# Technical Domain Knowledge

Last updated: 2026-04-20 (session 4: P1.7 of display library refactor — added "Memory Management on CircuitPython" section produced via the full Researcher + independent-Verifier + Editor loop; one Researcher claim was refuted and flipped; several claims strengthened with additional `[CPy-src]` evidence from the Verifier pass)

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

## Memory Management on CircuitPython

Scope: `[universal]` across this CircuitPython workspace, with concrete-evidence anchors on the RP2040 port. Produced 2026-04-20 via the technical-memory review loop (Researcher + independent Verifier + Editor). Source-tag legend: `[CPy-src]` = `github.com/adafruit/circuitpython` source tree, `[CPy-docs]` = `docs.circuitpython.org`, `[CPy-lib]` = Adafruit CircuitPython library repo, `[Adafruit-learn]` = learn.adafruit.com guide explicitly marked CircuitPython, `[inferred]` = reasoned from general-Python semantics or unverified MicroPython-adjacent evidence, `[on-device-experiment]` = measured on the project's YD-RP2040.

### Context

CircuitPython runs on RP2040 without OS-level memory protection or a compacting collector. Adafruit states plainly: "defragmentation is not feasible with the memory structure of CircuitPython" [Adafruit-learn, "Reducing memory fragmentation", 2026-04-20]. `MemoryError` with "Memory allocation failed" can therefore fire while `gc.mem_free()` reports plenty free — the free bytes are just not contiguous.

### Heap structure on RP2040

Two-layer architecture [CPy-src, `ports/raspberrypi/supervisor/port.c`, 2026-04-20]:

1. **Outer allocator**: TLSF (`lib/tlsf/`) carved out of the SRAM region between `_ld_cp_dynamic_mem_start` and the stack limit. Called via `port_malloc` / `port_free`.
2. **Python GC heap**: split auto-grow, controlled by `MICROPY_GC_SPLIT_HEAP (1)` and `MICROPY_GC_SPLIT_HEAP_AUTO (1)` in `py/circuitpy_mpconfig.h` [CPy-src, 2026-04-20]. Starts at `CIRCUITPY_HEAP_START_SIZE` = 8 KB and **doubles** into TLSF until doubling fails, at which point it grows into the largest contiguous free block. Comment in source: "The VM heap starts at this size and doubles in size as needed until it runs out of memory in the outer heap."

RP2040-specific fixed overheads [CPy-src, `ports/raspberrypi/mpconfigport.h` + `circuitpy_mpconfig.h`, 2026-04-20]: 24 KB default stack (`CIRCUITPY_DEFAULT_STACK_SIZE`) + 1 KB exception stack + 2 KB pystack (`CIRCUITPY_PYSTACK_SIZE`, with `MICROPY_ENABLE_PYSTACK (1)`). Board-specific heap-free baseline on YD-RP2040 must be measured on-device — no single source gives a static figure [on-device-experiment, pending].

### `gc` module surface on CircuitPython

Present: `gc.enable()`, `gc.disable()`, `gc.isenabled()`, `gc.collect()`, `gc.mem_alloc()`, `gc.mem_free()` [CPy-src, `py/modgc.c`, 2026-04-20].

**Absent at runtime despite being listed on `docs.circuitpython.org/en/stable/docs/library/gc.html`**: `gc.threshold()`. The binding in `py/modgc.c` is wrapped in `#if MICROPY_GC_ALLOC_THRESHOLD`, and `py/circuitpy_mpconfig.h` sets `MICROPY_GC_ALLOC_THRESHOLD (0)` — so the function is compiled out of shipped CircuitPython builds. Calling `gc.threshold(...)` raises `AttributeError` at runtime [CPy-src, `py/modgc.c` + `py/circuitpy_mpconfig.h`, 2026-04-20]. The docs page is stale for this function; trust the source. Do not plan tuning around `gc.threshold()` on CircuitPython.

`gc.mem_free()` reports only fully-free bytes after the last sweep. Stale phantom references (objects still pinned by locals, closures, or unbound attributes) still count as live until the next `gc.collect()`, so measurements are meaningless without an explicit `gc.collect()` immediately before reading [Adafruit-learn, "Measuring memory use", 2026-04-20].

### Preallocate; mutate in place

The CircuitPython Design Guide is first-party on this point: "prefer bytearray buffers that are created in `__init__` and used throughout the object", and "use `struct.pack_into` instead of `struct.pack`" [CPy-docs, Design Guide §"Avoid allocations in drivers", 2026-04-20]. "Advanced programmers: allocate a large memory buffer early in the life of your code and reuse the same memory buffer through your program" [Adafruit-learn, "Reducing memory fragmentation", 2026-04-20].

Concretely, for a same-sized `bytearray`, `buf[:] = src` writes into the existing heap block while `buf = a + b` allocates a new one — this is general Python semantics rather than a CPy-specific documented claim [inferred]. The Design Guide's preallocation recommendation is what is CPy-first-party; the specific `buf[:] = src` vs. concat contrast derives from language semantics.

### `memoryview`

`MICROPY_PY_BUILTINS_MEMORYVIEW (1)` is enabled [CPy-src, `py/circuitpy_mpconfig.h`, 2026-04-20]. Construction of `memoryview(bytearray(...))` is zero-copy and indexed writes through a `memoryview` propagate to the backing `bytearray`. For `displayio.Bitmap` specifically, the buffer-protocol view is documented as direct only when bit-depth ∈ {8, 16, 32} and row-bytes are a multiple of 4 [CPy-docs, `shared-bindings/displayio/Bitmap`, 2026-04-20].

`memoryview` *slicing* (`mv[a:b]`) is widely believed to be zero-copy on both runtimes, but there is no CircuitPython-specific docs statement confirming this; the behavior is inherited from MicroPython's `py/objarray.c` [inferred]. Treat as zero-copy at the read-end, but verify with on-device `gc.mem_free()` deltas before relying on it in a hot loop. See "Known gaps" below.

### `const()`

`micropython.const(expr)` is **parser-recognized**, folded at bytecode compile time. Enabled on CPy by `MICROPY_COMP_CONST (1)` + `MICROPY_COMP_MODULE_CONST (1)` [CPy-src, `py/circuitpy_mpconfig.h`, 2026-04-20]. A leading underscore makes the constant hidden from the module's global dict, so it takes no runtime dict slot [CPy-docs, `shared-bindings/micropython`, 2026-04-20]. Design Guide rules: "Always use via an import", "Limit use to global (module level) variables only", "Only used when the user will not need access to variable and prefix name with a leading underscore" [CPy-docs, Design Guide §"Use of MicroPython const()", 2026-04-20].

### `@micropython.native` and `@micropython.viper` are not available

The CircuitPython `micropython` module exposes only `micropython.const` [CPy-docs, `shared-bindings/micropython`, 2026-04-20]. Native-emit (`MICROPY_EMIT_THUMB` / `MICROPY_EMIT_INLINE_THUMB`) is gated behind `CIRCUITPY_ENABLE_MPY_NATIVE` in `circuitpy_mpconfig.h`, which is not enabled for the standard RP2040 build [CPy-src, 2026-04-20]. Known broken: `adafruit/circuitpython` issue #8902; `native_if_available` is a no-op fallback introduced by PR #2282. Do not plan performance around these decorators on this port — stay in plain Python with preallocated buffers and `struct.pack_into`.

### `neopixel.NeoPixel` allocation behavior

`neopixel.NeoPixel` subclasses `adafruit_pixelbuf.PixelBuf`. In the pure-Python fallback (`adafruit_pypixelbuf`), `__init__` allocates `bytearray(bpp * n)` once and stores it in `self._post_brightness_buffer`; `show()` calls `_transmit(self._post_brightness_buffer)` with no per-call allocation [CPy-lib, `adafruit_pypixelbuf.py`, 2026-04-20]. NeoPixel's `_transmit` invokes the native `neopixel_write(self.pin, buffer)` [CPy-lib, `neopixel.py`, 2026-04-20]. If `brightness < 1.0`, a second `bytearray(self._post_brightness_buffer)` is allocated once on first setter access — one-shot, not per-frame.

Caveat: in this pass the native `shared-module/_pixelbuf/PixelBuf.c` was not retrievable, so the above is verified via the pure-Python fallback and the NeoPixel library source. On CircuitPython RP2040 builds the native `_pixelbuf` module is shipped; the buffer layout is designed to be API-identical to the fallback, but the native C implementation's exact allocation behavior is not source-verified here — flagged in "Known gaps."

Iterating `for p in pixels:` allocates a per-element tuple because `PixelBuf.__getitem__` returns a tuple [inferred from general-Python semantics]. Prefer `pixels[i] = (r, g, b)` or slice assignment `pixels[i:j] = seq` over iteration-based mutation in hot loops.

### Import-time vs. hot-path allocation

"Allocate large items early while memory space is relatively wide open" [Adafruit-learn, "Reducing memory fragmentation", 2026-04-20]. Allocating, e.g., 48 `Image` wrapper objects at import time produces one burst on a still-contiguous heap. Allocating them lazily scatters small blocks between later runtime allocations and is the textbook path to fragmentation. As a minor but often-believed myth: `from foo import bar` does NOT save RAM versus `import foo` — the whole module is loaded either way [Adafruit-learn, "Optimizing memory use: Importing Libraries", 2026-04-20].

### Applies to this project

- **Ring-buffer scroll (Phase 2.5)**: current `show_string` does `scroll_buf = padding + buf + padding` — three `bytearray` allocations plus two concatenations per call. The plan's 3×WIDTH ring with a glyph-column feeder replaces that with one instance-level `bytearray` filled via slice assignment; Design Guide's preallocation recommendation directly supports this. `_pixels.show()` at the end of each frame does not allocate.
- **`build_lut` in-place (Phase 3.3)**: currently returns a fresh 64-byte `bytearray` and rotation does `_LUT[:] = build_lut(degrees)` — one transient 64-byte block per rotation. Add `build_lut(dest, rotation)` that writes into the existing `_LUT`. The block is small, but its lifecycle (short-lived inside a rotation call) is the worst-case shape for fragmentation.
- **Parser dedup (Phase 2.1)**: keep parser helpers at module scope (their bytecode and any `_`-prefixed `const()` values sit in one location); avoid instantiating parser classes inside render methods.
- **Icons-as-Images (Phase 2.2)**: materializing 48 `Image` wrappers at import is the right shape per the "large items early" guidance; the bulk `ICONS` / `ARROWS` bytes remain allocated once at import as they are now.
- **`color=WHITE` default (P1.2, done)**: immutable tuples go in the signature — no per-call remap, no `None` sentinel. Separate from fragmentation but same family of allocation-hygiene directives.

### Known gaps

- **`memoryview` slicing zero-copy guarantees on CPy 10.x**: inferred from shared `py/objarray.c` between MPy and CPy, not re-verified against CPy sources this pass. Close with an on-device `gc.mem_free()` delta: before/after `mv[a:b]` inside a tight loop.
- **Native `_pixelbuf` C source behavior on RP2040**: `shared-module/_pixelbuf/PixelBuf.c` not retrieved this pass; claims about the native implementation's allocation behavior are verified only via the pure-Python fallback. If a later investigation finds the native module diverges from the fallback in allocation shape, update this entry.
- **YD-RP2040 free-heap baseline at clean boot**: "~192 KB to Python" is a working assumption from the project brief, not sourced. Measure once with `import gc; gc.collect(); gc.mem_free()` at `code.py` entry and record as `[on-device-experiment]`.
- **`bytes + bytes` vs. `bytearray` slice-assignment cost**: the principle is Design Guide–supported, but no CPy source quantifies the difference. Close opportunistically with on-device benchmarks if ring-buffer frame rate surfaces it as a bottleneck.

## Verification Queue

<!-- Items recorded as `unverified` that matter enough to confirm on code before promotion. FIFO is fine; no strict priority. -->

| Item | Why it matters | Pointer | Added |
|------|----------------|---------|-------|
| `memoryview` slicing zero-copy on CPy 10.x | Ring-buffer perf claim depends on this; currently `[inferred]` from shared MPy source | `gc.mem_free()` delta before/after `mv[a:b]` in a tight loop on YD-RP2040 | 2026-04-20 |
| Native `_pixelbuf` C module allocation shape | Verify native implementation matches the pure-Python fallback (one-time `__init__` allocation, no per-`show()` allocation) | `github.com/adafruit/circuitpython` → `shared-module/_pixelbuf/PixelBuf.c` | 2026-04-20 |
| YD-RP2040 clean-boot free heap | Anchor the "~192 KB" assumption | `gc.collect(); print(gc.mem_free())` at `code.py` entry | 2026-04-20 |

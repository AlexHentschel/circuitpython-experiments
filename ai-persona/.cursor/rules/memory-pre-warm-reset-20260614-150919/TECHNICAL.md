# Technical Domain Knowledge

Last updated: 2026-06-12 (session 8 continuation: added subsection "Glyph coordinate model: metrics are y-up, raster is y-down" under § Fonts — `evidence-supported`, verified against `adafruit_bitmap_font/pcf.py` source (raster top-scanline-first, `dy = -descent`, `ascent = font_ascent`). Documents why `_glyph_columns`'s `display_row = ascent - height - dy + cy` is correct: one y-up→y-down reflection in the placement term, raster copied flip-free. Mirrors the inline "Coordinate systems" docstring block added to `core.py::_glyph_columns` the same session.)

Previous: 2026-04-21 (session 6 continuation: added § "Fonts for pixel-accurate displays" with the outline-font-at-small-pixel-sizes domain fact, anchored by the font-distortion investigation recorded in `working-docs/font-distortion-findings.md`. Scope `[cross-experiment]`: applies to any pixel-accurate display workload — 8x8 NeoPixel matrices here, but OLEDs, e-paper, and other bitmapped targets inherit the same rule.)

Previous: 2026-04-21 (session 6: added "Name loading: LOAD_FAST vs LOAD_GLOBAL" subsection under § Memory Management on CircuitPython — `[CPy-src]`-verified against `py/vm.c` + `py/runtime.c`; grounds the MicroPython-inherited "cache globals as locals" optimisation for this port.)

Previous: 2026-04-20 (session 4: P1.7 of display library refactor — added "Memory Management on CircuitPython" section produced via the full Researcher + independent-Verifier + Editor loop; one Researcher claim was refuted and flipped; several claims strengthened with additional `[CPy-src]` evidence from the Verifier pass)

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

### Name loading: LOAD_FAST vs LOAD_GLOBAL

CircuitPython inherits MicroPython's bytecode VM unchanged — `py/vm.c`, `py/runtime.c`, and the opcode table carry over from the fork point with periodic merges. Relevant opcodes and their dispatch cost:

- `MP_BC_LOAD_FAST_N`: decodes a uint local-slot index, then does one C array subscript — `obj_shared = fastn[-unum]`, where `fastn` is the VM stack frame's local-variable region (`fastn[0]` is `local[0]`, `fastn[-1]` is `local[1]`, etc.) [CPy-src, `py/vm.c::MP_BC_LOAD_FAST_N`, lines 398-411, 2026-04-21].
- `MP_BC_LOAD_FAST_MULTI`: single-byte opcode covering the first N locals; same `fastn[...]` subscript mechanism, no uint decode on the critical path [CPy-src, `py/vm.c::MP_BC_LOAD_FAST_MULTI`, lines 1319-1322, 2026-04-21].
- `MP_BC_LOAD_GLOBAL`: decodes a qstr operand from bytecode, then calls `mp_load_global(qst)` which does `mp_map_lookup` on the module's globals dict, with fallback on miss to the builtins-override dict (if `MICROPY_CAN_OVERRIDE_BUILTINS`) and then to `mp_module_builtins_globals` [CPy-src, `py/vm.c::MP_BC_LOAD_GLOBAL` line 426 + `py/runtime.c::mp_load_global` lines 244-266, 2026-04-21].

Happy-path cost comparison: `LOAD_FAST_*` is one array subscript; `LOAD_GLOBAL` is one qstr decode plus one hash-map lookup (hash + probe) on the globals dict. The asymmetry is fully inherited from MicroPython, so the MicroPython speed-tuning guidance — "cache globally-scoped object references as function-locals at the top of hot functions" [MPy-docs, `docs.micropython.org/en/latest/reference/speed_python.html` § "Caching object references"] — applies to CircuitPython with the same underlying mechanism. The CPy file `py/vm.c` carries explicit `CIRCUITPY-CHANGE` markers elsewhere in the same file (e.g. line 1258), confirming the file is live CPy source rather than stale inherited-and-divergent code.

**Practical rule**: in any hot function, bind module-global references (`_pixels`, `_LUT`, module-scope constants, imported names) into function-local names once near the top. Every inner-loop use of those names then dispatches as `LOAD_FAST_*` rather than `LOAD_GLOBAL`. Applied example in this project: `lib/display/core.py::_render_colmajor` does `pixels = _pixels; lut = _LUT; off = OFF` before entering the `(x, y)` loops.

**Scope and caveat**: this is a mechanism-verified claim (shared VM, identical opcode dispatch, identical `mp_map_lookup` in `mp_load_global`), not a cycle-counted microbenchmark on RP2040. Absolute speedup is workload-dependent and dominated by how many inner-loop references the hot function makes per iteration. See also § "`@micropython.native` and `@micropython.viper` are not available" — there is no native-compiled escape hatch on this port, so plain-Python bytecode-level optimizations like this one are the primary performance lever available. An on-device `time.monotonic_ns()` delta around a LOAD_FAST/LOAD_GLOBAL A/B remains optional follow-up in the Verification Queue if a specific hot path surfaces as a bottleneck.

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

## Fonts for pixel-accurate displays

Scope: `[cross-experiment]` — applies to any workload that renders text on a pixel-addressable display (NeoPixel matrix, OLED, e-paper, monochrome LCD). Source-tag legend inherited from § Memory Management; adds `[on-device-experiment]` for the exp14 YD-RP2040 anchor.

### Outline fonts at small pixel sizes are structurally unsuitable

**Claim**: TrueType / OpenType outline fonts auto-rasterized at nominal pixel sizes below ~10 px produce bitmaps that cannot preserve the stroke structure of Latin letterforms. The resulting glyphs are not merely "low-quality" — they are not legible as letters, because at small sizes the number of pixels available (typically 3-5 wide by 3-7 tall per glyph after ascent/descent) is below the threshold needed to distinguish e.g. `H` (two verticals + crossbar) from `I` (one vertical) or `E` (one vertical + three horizontals). Status: `evidence-supported`.

**Mechanism**: FreeType's auto-rasterizer discretizes continuous outline curves onto a pixel grid. For stem widths below 1 px the rasterizer must choose which pixel a stroke lands on; hinting helps for some fonts at standard UI sizes (10-16 px) but degrades sharply below that. At 8 px nominal height, Latin capitals occupy ~5-6 px vertically and ~3-4 px horizontally — too few pixels to carry both the outline's silhouette *and* the internal stroke topology. [Evidence: FreeType docs on hinting; the font-distortion investigation in `working-docs/font-distortion-findings.md` observed the same `H` glyph decoded identically on-device (CircuitPython + `adafruit_bitmap_font.pcf`) and on the host (stdlib-only `struct` parser), confirming the problem is in the file, not the loader.]

**Practical rule for this workspace**: for pixel-accurate displays at 8x8, 8x16, or similar tight pixel grids, do not use PCFs generated by `bdftopcf`/FreeType from a TTF at 8-10 px nominal. Use hand-designed bitmap fonts authored at or below the target size. Capital-letter height needs ≥ 6-7 pixels to reliably distinguish `H` / `E` / `A` / `M` from one another; smaller grids require fonts explicitly designed for that grid. Concrete candidates (all BSD / MIT / public-domain or similar): `tom-thumb` (3x5, ultra-compact), `scientifica` (5x11), `bitocra` (6x10), `creep` (5x8-7x8), `spleen` (5x8 to 32x64), `tewi` (5x8-11). The existing exp14 font `lib/display/font_free_mono_8/font.pcf` is a FreeType auto-rasterization of `FreeMono.ttf` at `PIXEL_SIZE: 8` and exhibits this failure mode on the 8x8 matrix.

**Rendering-code implication (exp14)**: `lib/display/core.py::_glyph_columns` and `_render_colmajor` are metric-agnostic — they read `font.ascent`, `font.descent`, per-glyph `width`, `height`, `dx`, `dy`, `shift_x` — so a font swap is a path-and-metadata change (update `_FONT_PATH`, re-verify metrics) with no rendering-code change required. The file `working-docs/font-distortion-probe.py` holds a reproducer of the current failure mode, useful as an A/B reference after the swap.

### Glyph coordinate model: metrics are y-up, raster is y-down (the `_glyph_columns` transform)

**Claim**: `adafruit_bitmap_font` (PCF/`fontio.Glyph`) mixes two coordinate frames, and the `_glyph_columns` vertical transform `display_row = ascent - height - dy + cy` is correct precisely because of how they combine. Status: `evidence-supported` (verified against the library source, not just inferred). Scope: the font-model facts are `[cross-experiment]` (any `adafruit_bitmap_font` consumer); the specific formula is `[exp14]`.

Three frames (formal 2D handedness taking +z out of the screen; x points right in all three, so only the y-axis direction differs):

| Frame | Origin | y direction | Handedness | Quantities |
|-------|--------|-------------|-----------|-----------|
| Metric space | baseline | up | right-handed | `ascent`, `dy` (= `-descent`) |
| Glyph raster | top-left of glyph bbox | down | left-handed | `cx`, `cy`, `bm[cx + cy*width]` |
| Display | top-left of matrix | down | left-handed | `display_row`, `display_col` |

`height`/`width` are **frame-neutral magnitudes** (the bbox extent / scanline + column counts), not directed quantities — invariant under the handedness flip, which is why they appear in both metric and raster reasoning untransformed. Only the *combination* `dy + height` is a right-handed quantity — the top edge's y-up position in **metric space (baseline origin)**, which `ascent - (dy + height)` then reflects into a y-down row in **display space (top origin)**; `height` alone is the span inside it, not an offset.

**Key facts (each grounded in `libArchive/libstubs/adafruit_bitmap_font/pcf.py`)**:
- Glyph raster is stored **top-scanline-first** (y-down), same orientation as the display. The PCF loader reads file rows in order into a row-major bitmap (`bitmap[start + k]`, `start += width` per row). [`pcf.py:402-407`] Bit order `128 >> (k % 8)` ⇒ MSB = leftmost pixel ⇒ x left-to-right. [`pcf.py:405`]
- `dy = -character_descent` (y-up: 0 for a baseline glyph, negative for a descender); `height = character_ascent + character_descent`; so a glyph's **top edge above baseline = dy + height**. [`pcf.py:367-378`]
- `ascent = font_ascent` (pixels above baseline of a typical ascender); display row 0 ≙ the ascent line. [`pcf.py:129, 145-147`]

**Why the transform is correct** — decompose into placement (crosses frames, once) + raster copy (no flip):
1. `row_origin = ascent - height - dy` places the glyph's top edge in display rows. This single subtraction *is* the y-up→y-down reconciliation (reflects the baseline-relative metric into a top-relative row).
2. `display_row = row_origin + cy` copies each scanline with a pure translation — **no `(height-1-cy)` reflection** — because raster and display are both y-down. The absence of that reflection is the correctness condition; a y-up raster would render every glyph vertically mirrored. Horizontal is fully trivial (`display_col = cx + dx`, all x-right).

**Falsification check**: text renders right-side-up on-device (pipeline exonerated in the font-distortion investigation above) ⇒ raster is y-down; the source confirms the mechanism independently. Documented inline at `lib/display/core.py::_glyph_columns` docstring (the "Coordinate systems" block).

## Verification Queue

<!-- Items recorded as `unverified` that matter enough to confirm on code before promotion. FIFO is fine; no strict priority. -->

| Item | Why it matters | Pointer | Added |
|------|----------------|---------|-------|
| `memoryview` slicing zero-copy on CPy 10.x | Ring-buffer perf claim depends on this; currently `[inferred]` from shared MPy source | `gc.mem_free()` delta before/after `mv[a:b]` in a tight loop on YD-RP2040 | 2026-04-20 |
| Native `_pixelbuf` C module allocation shape | Verify native implementation matches the pure-Python fallback (one-time `__init__` allocation, no per-`show()` allocation) | `github.com/adafruit/circuitpython` → `shared-module/_pixelbuf/PixelBuf.c` | 2026-04-20 |
| YD-RP2040 clean-boot free heap | Anchor the "~192 KB" assumption | `gc.collect(); print(gc.mem_free())` at `code.py` entry | 2026-04-20 |

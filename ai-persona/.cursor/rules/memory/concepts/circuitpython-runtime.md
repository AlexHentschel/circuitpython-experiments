# Concept domain: circuitpython-runtime

**Content scope**: `[domain:circuitpython-runtime]` `[family:circuitpython]` — applies across every CircuitPython project in this persona (exp09/11/13/14/15), with concrete-evidence anchors on the RP2040 port. Provenance: surfaced during the exp14 display-library refactor (`[project:circuitpython-exp14-display]`), but the knowledge is family-wide, so it lives centrally, not in a project folder (R-7 / *Don't guess an association into a deep, specific bucket*).
**Status**: `evidence-supported` for the source-tagged claims; `[inferred]` / Verification-Queue items are explicitly marked below.
**Concepts in this domain** (one `### …` section each): heap structure (RP2040 split-heap doubling) · `gc` module surface · preallocate-mutate-in-place · `memoryview` · `const()` · `@micropython.native` / `.viper` · name loading (LOAD_FAST vs LOAD_GLOBAL) · `neopixel.NeoPixel` allocation · import-time vs hot-path allocation · user-facing `asyncio` vs builtin `_asyncio` · **`asyncio.sleep(0)` still yields once** · **`mpy-cross` is CircuitPython’s binary, not PyPI MicroPython** · **`#` comments and docstrings are absent from `.mpy`** · **`__slots__` not implemented on CircuitPython**. Project-application notes + known gaps + a runtime Verification Queue follow.
**Related concepts** (`_RELATIONS.md`): `preallocate` / `neopixel allocation` will *compose-with* a future `led-driving` domain; `memoryview` *complemented-by* `fonts` (glyph-raster access). See `_RELATIONS.md`.
**Provenance / history**: produced 2026-04-20 (exp14 P1.7) via the Researcher + independent-Verifier + Editor loop; extended 2026-04-21 (LOAD_FAST/LOAD_GLOBAL). Reshaped from the monolithic `TECHNICAL.md § Memory Management on CircuitPython` into this concept-domain file at the 2026-06-14 warm reset (R-9 — content reproduced faithfully below; only the concept-graph wrapper is new). Source-tag legend: `[CPy-src]` = `github.com/adafruit/circuitpython` source tree, `[CPy-docs]` = `docs.circuitpython.org`, `[CPy-lib]` = Adafruit CircuitPython library repo, `[Adafruit-learn]` = learn.adafruit.com guide explicitly marked CircuitPython, `[inferred]` = reasoned from general-Python semantics or unverified MicroPython-adjacent evidence, `[on-device-experiment]` = measured on the project's YD-RP2040.

---

## Memory Management on CircuitPython

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

A function-local list is still a GC-heap object. `snap = [OFF] * n` inside a function allocates the list header and its pointer slots on the GC heap; the local name is one reference in the Python frame (the pystack when `MICROPY_ENABLE_PYSTACK` is on). CircuitPython has no stack allocation for Python containers. `[inferred]` for the pystack half; the heap half is now source-checked below.

**In-range index store does not allocate list storage** (`evidence-supported`, CircuitPython 10.3.0 `py/objlist.c` `mp_obj_list_store`, 2026-09-29). `lst[i] = value` with `i` inside `len` is `self->items[i] = value` — one pointer write. No `m_malloc` / `m_renew` / `mp_obj_new_*` on that path. The value is whatever the right-hand side already produced. Slice assignment that grows past `alloc`, and `append` when `len >= alloc`, do call `m_renew` (append doubles `alloc`).

Applied `[project:circuitpython-exp16-planetx]`: `Display._frame` (`[OFF] * NUM_PIXELS`, 25 slots) is created in `__init__`. `set_rotation`'s `snap[i] = pixels[...]` does not grow that list. It does allocate: each `pixels[k]` is `PixelBuf.get_pixel`, which returns `mp_obj_new_tuple` (10.3.0 `shared-module/adafruit_pixelbuf/PixelBuf.c` `common_hal_adafruit_pixelbuf_pixelbuf_get_pixel`; tuple body is `mp_obj_malloc_var` in `py/objtuple.c`). The NeoPixel buffer holds bytes, not color tuples. One `set_rotation` therefore builds 25 new 3-tuples. A list created inside `set_rotation` would add one more heap block per call on top of those tuples.

A packed RGB int (`(r << 16) | (g << 8) | b`, max `0xFFFFFF`) fits a small int on this 32-bit port, so the int itself is not a heap object. `PixelBuf.__setitem__` accepts that int and writes bytes (`pixelbuf_parse_color`'s int branch). There is no packed-int read: `__getitem__` always returns a new tuple. Alex, 2026-09-29: do not keep a parallel logical buffer updated on every render so rotation can skip those tuples — rotation is the rare call. Pack once where a tuple enters a loop; store ints in `_frame` after the unavoidable read. The 25 tuples stay on `set_rotation` / `get_pixel`. Packing does not notably speed the non-rotation path: a render already passes one shared tuple into `pixels[i] = color` (no per-pixel alloc). The int form only swaps `pixelbuf_parse_color`'s tuple-slot reads for three shifts, 25 times, beside the Python loop and `show()`.

### `memoryview`

`MICROPY_PY_BUILTINS_MEMORYVIEW (1)` is enabled [CPy-src, `py/circuitpy_mpconfig.h`, 2026-04-20]. Construction of `memoryview(bytearray(...))` is zero-copy and indexed writes through a `memoryview` propagate to the backing `bytearray`. For `displayio.Bitmap` specifically, the buffer-protocol view is documented as direct only when bit-depth ∈ {8, 16, 32} and row-bytes are a multiple of 4 [CPy-docs, `shared-bindings/displayio/Bitmap`, 2026-04-20].

`memoryview` *slicing* (`mv[a:b]`) is widely believed to be zero-copy on both runtimes, but there is no CircuitPython-specific docs statement confirming this; the behavior is inherited from MicroPython's `py/objarray.c` [inferred]. Treat as zero-copy at the read-end, but verify with on-device `gc.mem_free()` deltas before relying on it in a hot loop. See "Known gaps" below.

### `const()`

`micropython.const(expr)` is **parser-recognized**, folded at bytecode compile time. Enabled on CPy by `MICROPY_COMP_CONST (1)` + `MICROPY_COMP_MODULE_CONST (1)` [CPy-src, `py/circuitpy_mpconfig.h`, 2026-04-20]. A leading underscore makes the constant hidden from the module's global dict, so it takes no runtime dict slot [CPy-docs, `shared-bindings/micropython`, 2026-04-20]. Design Guide rules: "Always use via an import", "Limit use to global (module level) variables only", "Only used when the user will not need access to variable and prefix name with a leading underscore" [CPy-docs, Design Guide §"Use of MicroPython const()", 2026-04-20].

**A plain `NAME = 2` is not folded (2026-10-20).** `mpy-cross` substitutes the value only for `micropython.const`. After compile, three forms:

| Source | Bytecode at each use | Runtime |
|---|---|---|
| `_STATE_DEINIT = 2` | `LOAD_GLOBAL` of the name | one globals-dict lookup per compare |
| `self._state == 2` | `LOAD_CONST` of the small int | no name lookup |
| `_STATE_DEINIT = const(2)` | same `LOAD_CONST` as writing `2` | no name lookup; a leading underscore also omits the name from the module dict |

`const(2)` is more efficient than the plain assignment. It is not more efficient than the literal. It is that literal, and the source still has the name.

**Scale, exp16 `Button.run`.** The loop compares `_state` once per 10 ms empty wake and a few times per delivered event. One `LOAD_GLOBAL` against a 10 ms `sleep_ms` does not move the ~5 ms average wait after an event is queued. Mechanism `evidence-supported`. A 25-add loop on UID `0740D10F1BE9` (2026-11-16, § On-device bytecode timings) did not separate `const` from a plain module int (83.4 vs 83.2 µs). A local copy of that int was 6.3 µs faster per 25 adds. The fold is still the compile-time mechanism above; that loop did not show a run-time gap between the const name and the plain global.

### `@micropython.native` and `@micropython.viper`

`[family:circuitpython]`. Open when any experiment compiles with `mpy-cross` or asks whether a hot function can be native or viper. The always-read cue is `concepts/_INDEX.md`. Board names below are the chips the tags were checked on, not a single project's library.

**Family rule.** With the 10.3.x `mpy-cross` (the binary is built from `adafruit/circuitpython`, not a separate project): no decorator in source that must also produce a bytecode `.mpy`. One decorated source cannot yield both a bytecode file and a native file until `optional=True`, which is on git `main` and in tag 11.0.0-alpha.3, not in any 10.3.x release. Applied to exp16: bytecode only, no decorator in `lib/`.

| Question | Answer for mpy-cross 10.3.x | Where it fails or loads |
|---|---|---|
| Decorator in a `.py` on a board whose emitter is off (stock 10.3.0 and 10.3.1, including every espressif board and RP2350) | No. `SyntaxError: invalid micropython decorator` | On-board compiler. `CIRCUITPY_ENABLE_MPY_NATIVE` defaults to 0, so `MICROPY_EMIT_NATIVE` is 0 (`py/compile.c`, tags 10.3.0 and 10.3.1) |
| Cross-compile with `-march=xtensawin`, deploy the `.mpy` to stock 10.3.0 espressif (BPI-Bit-S2 checked) | No. The compile succeeds. Import raises `ValueError: native code in .mpy unsupported` | 10.3.0 has no `CIRCUITPY_LOAD_NATIVE`. Firmware arch is `NONE` (`py/persistentcode.c`). 10.3.1 espressif port does not turn the loader on |
| Cross-compile with `-march=armv7emsp`, deploy to a stock RP2350 on **10.3.1** | Yes, that `.mpy` loads. A `.py` with the decorator still does not | Whole `raspberrypi` port: `CIRCUITPY_LOAD_NATIVE ?= 1` in `ports/raspberrypi/mpconfigport.mk`. Load body is on via `MICROPY_ENABLE_NATIVE_CODE` (10.3.1 `py/persistentcode.c`). Not run on a board. RP2040 on the same port wants `-march=armv6m` instead |
| One source → a bytecode `.mpy` and a native `.mpy` | No, on 10.3.x. No `-march` is `SyntaxError: invalid arch`. Any `-march` marks the whole file native | `@micropython.native(optional=True)` is that switch (`py/compile.c`). On git `main` and tag **11.0.0-alpha.3** (2026-11-12). Absent from 10.3.2, 10.4.0-alpha.2, and 11.0.0-alpha.1. A viper body that uses `ptr8` or `uint` is still illegal as bytecode |

Plain bytecode from one source is the path that does serve both boards: one `mpy-cross` run, no decorator, header arch `NONE`. mpy version 6, native sub-version 3, on 10.3.0, 10.3.1, and `main` as read 2026-11-17 (`py/persistentcode.h`).

Two different switches, often confused:

| Switch | What it builds | Stock 10.3.0 `bpi_bit_s2` |
|---|---|---|
| `CIRCUITPY_ENABLE_MPY_NATIVE` | On-board **compiler** that turns `@micropython.native` / `.viper` in a `.py` into machine code at import. In 10.3.0 this flag turns on the **Thumb** emitter only (`MICROPY_EMIT_THUMB`), which is the wrong instruction set for ESP32-S2. | Default **0**. Not set in `ports/espressif/mpconfigport.mk` or `boards/bpi_bit_s2/mpconfigboard.mk`. |
| `CIRCUITPY_LOAD_NATIVE` | **Loader** only: import a `.mpy` that `mpy-cross` already filled with machine code. No on-board compiler. A `.py` that contains the decorator still fails to import. | **Does not exist** in the 10.3.0 tree. 10.3.1 global default **0**. The 10.3.1 raspberrypi port sets it **1** for every RP2040 and RP2350 board (`ports/raspberrypi/mpconfigport.mk`). Espressif, including `bpi_bit_s2`, does not. |

**What the names mean** (so a later firmware bump is not read as "the library can be recompiled as-is"):

- `@micropython.native` — machine code for that function; values stay Python objects. Helps a tight arithmetic loop. Does not remove the cost of calling into C (`PixelBuf`, `neopixel_write`).
- `@micropython.viper` — a restricted dialect: typed locals (`int`, `uint`, `ptr8`, `ptr16`, `ptr32`, …) and raw pointer stores. Not a faster version of ordinary library Python (no general object allocation, no `asyncio` in the typed body).
- Both are **compile-time** decorators, not functions you call. With the emitter compiled out they are a syntax error, not a no-op.

**Runtime module surface, 10.3.0.** `py/modmicropython.c` exports `const` unconditionally. `opt_level`, `heap_lock`, `mem_info`, and the rest sit behind `CIRCUITPY_MICROPYTHON_ADVANCED`, which `py/circuitpy_mpconfig.h` sets to **0**. `schedule` / `RingIO` need ROM level extra features; the default ROM level is core features. There is no `micropython.native` attribute. `native` and `viper` are never runtime names on this firmware.

**On-device `.py` (emitter off).** `py/compile.c` `compile_built_in_decorator` only accepts `native` / `viper` inside `#if MICROPY_EMIT_NATIVE`. That macro is the OR of the arch emitters (`py/mpconfig.h`); all of them are 0 on this firmware, so the decorator falls through to `SyntaxError: invalid micropython decorator`. `@micropython.bytecode` remains legal and changes nothing (bytecode is already the default).

**Host `mpy-cross` on this Mac (confirmed 2026-11-15).** Binary `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/mpy-cross-macos-10.3.0-arm64`, `CircuitPython 10.3.0 on 2026-08-31; mpy-cross emitting mpy v6.3`. It is a cross-compiler: the M3's CPU is not a target. `-march=host` prints `unable to determine host architecture` (no Apple ARM64 emitter). `-march` accepts `x86`, `x64`, `armv6`, `armv6m`, `armv7m`, `armv7em`, `armv7emsp`, `armv7emdp`, `xtensa`, `xtensawin`, `rv32imc`, `rv64imc`, `debug`.

| Invocation | Result on this binary |
|---|---|
| `@micropython.native` or `.viper`, no `-march` | `SyntaxError: invalid arch` (dynamic-compiler table slot 0 is NULL) |
| `@micropython.viper(optional=True)`, no `-march` | Same `invalid arch`. The word `optional` does not occur in 10.3.0 or 10.3.1 `py/compile.c`. The call arguments are ignored because a built-in decorator is not compiled as a call. |
| `-march=xtensawin` with the decorator, or `-X emit=native` / `emit=viper` | Writes a native `.mpy`. Header byte 2 = `0x2b` = sub-version 3 \| arch `XTENSAWIN` (10). |
| `-march=xtensa` | Different machine code. Header byte 2 = `0x27` (arch `XTENSA`, 9). That is the non-windowed emitter, not the ESP32-S2 ABI. |
| Same file, one plain function and one `@micropython.native` | Whole module header is `0x2b`. One decorated function marks the `.mpy`. |
| No decorator | Header `43 06 00 1f` (`C`, version 6, arch none, 31-bit small int), same prefix as the vendored `lib/asyncio/*.mpy`. |

CircuitPython's magic byte is `C`, not MicroPython's `M` (`py/persistentcode.c`, comment `CIRCUITPY-CHANGE`). A file starting with `M` raises `MicroPython .mpy file; use CircuitPython mpy-cross`.

**Why ESP32-S2 would be `xtensawin` if a loader existed.** ESP32-S2 is windowed Xtensa (`XCHAL_HAVE_WINDOWED`). On `main` (read 2026-11-15) `py/persistentcode.h` maps that to `MP_NATIVE_ARCH_XTENSAWIN` / the `-march=xtensawin` name. `xtensa` (no `win`) is the other emitter. Stock 10.3.0 never consults that mapping.

**What the 10.3.0 firmware does with a native `.mpy`.** `mp_raw_code_load` (`py/persistentcode.c`) decodes the arch from header byte 2. Arch `NONE` loads as bytecode. Any other arch is tested against the firmware's own arch. With every emitter off, that arch is `NONE`, and the error is `ValueError: native code in .mpy unsupported` (the comment above it mentions enabling `MICROPY_EMIT_THUMB`, which would still be the wrong ISA here). A firmware that had a *different* emitter would say `incompatible .mpy arch` instead. The native-load body itself is inside `#if MICROPY_EMIT_MACHINE_CODE`, so this build has no loader behind the check. Not executed on UID `0740D10F1BE9`; the strings and the `#if` are the 10.3.0 tag that the board's UF2 was built from (`mpy-cross` version line `2026-08-31`, same date as that firmware).

**`optional=True` (CircuitPython repo `main`, first seen in tag 11.0.0-alpha.3, 2026-11-12).** There is no separate mpy-cross project. The host binary is built from `mpy-cross/` in `adafruit/circuitpython`, and it uses the same `py/compile.c` as the firmware. "Main" means that repo's `main` branch. `docs/troubleshooting.rst` on that branch: the board cannot compile these decorators from `.py`; `optional=True` runs the function as ordinary bytecode, and `mpy-cross` without `-march` does the same. With `-march=armv7emsp` the same source still emits native, because the dynamic-compiler table slot is filled. Viper-only types (`ptr8`, `uint`, …) then raise `NameError` if that function actually runs as bytecode. Checked absent: tags 10.3.0, 10.3.1, 10.3.2, 10.4.0-alpha.2, 11.0.0-alpha.1 (`py/compile.c` has no `optional=True`). 10.4.0 was dropped; the 11.0.0-alpha.1 note says 11.0.0 is the next stable after 10.3.x. No release date. Stable spacing just before this: 10.2.0 on 2026-04-22, 10.3.0 on 2026-08-31. 11 alphas: alpha.1 2026-09-24, alpha.2 2026-10-21, alpha.3 2026-11-12. mpy version on alpha.3 is still 6, sub-version 3. The `foo.<arch>.mpy` search is written up under § `mpy-cross` (first present in 11.0.0-alpha.3 `py/builtinimport.c`; absent from every 10.3.x tag checked).

**`main` / 11.0.0-alpha.3 espressif loader, not a 10.3.x release.** Tag 11.0.0-alpha.3 `ports/espressif/mpconfigport.mk` sets `CIRCUITPY_LOAD_NATIVE ?= 1` (confirmed 2026-11-17). Tag 10.3.2 has no such line. The global default in `py/circuitpy_mpconfig.mk` stays 0. `boards/bpi_bit_s2/mpconfigboard.mk` does not override it, so a future UF2 built from that alpha would load native `.mpy` on the Bit-S2 unless the board file opts out. Re-read the port mk and the board mk on the tag you actually flash. `MICROPY_PERSISTENT_CODE_LOAD_NATIVE` is that flag OR `CIRCUITPY_ENABLE_MPY_NATIVE`. Windowed Xtensa maps to `-march=xtensawin`. Viper remains a different language from ordinary library Python.

**RP2350 on CircuitPython 10.3.1 (source-read 2026-11-17, not run on a board).** The loader is on for the whole `raspberrypi` port, so a stock 10.3.1 RP2350 UF2 can import a native `.mpy`. The on-board compiler stays off (`CIRCUITPY_ENABLE_MPY_NATIVE` is still unset), and 10.3.1 `compile.c` has no `optional=True`, so a `.py` with either decorator is still `SyntaxError: invalid micropython decorator` on the RP2350. The path that works is host `mpy-cross -march=armv7emsp`, then copy that `.mpy` only onto the RP2350 drive. The load body in 10.3.1 `py/persistentcode.c` is compiled in when `MICROPY_ENABLE_NATIVE_CODE` is set, and that macro is `MICROPY_EMIT_NATIVE || MICROPY_PERSISTENT_CODE_LOAD_NATIVE`, so the loader is present even though the on-board emitter is not. A 10.3.0 RP2350 UF2, or a board file that sets `CIRCUITPY_LOAD_NATIVE = 0`, still raises `native code in .mpy unsupported`.

The RP2350 firmware is built `-march=armv8-m.main+fp+dsp -mcpu=cortex-m33 -mthumb -mfloat-abi=softfp` (`ports/raspberrypi/Makefile`, `CHIP_VARIANT=RP2350`). `py/persistentcode.h` turns `__thumb2__` plus single-precision `__ARM_FP` into `MP_NATIVE_ARCH_ARMV7EMSP`, and accepts any arch from `ARMV6M` up through that. The matching `mpy-cross` flag is `-march=armv7emsp`. There is no `armv8m` flag. RP2040 is `-march=armv6m` only; an `armv7emsp` file fails its arch test. One native `.mpy` cannot serve RP2040, RP2350, and ESP32-S2. mpy version is still 6, native sub-version still 3, so the 10.3.0 `mpy-cross` binary on this Mac emits a header 10.3.1 will accept. Not executed on hardware.

**One source, two boards, 10.3.x `mpy-cross`.** This compiler will not ignore the decorator. No `-march` → `SyntaxError: invalid arch`. Any `-march` marks the whole module native, so a board whose loader is off (`native code in .mpy unsupported` on 10.3.0 espressif) refuses the file. `optional=True` is the ignore switch: without `-march`, or on a board whose emitter is off, the function stays bytecode; with `-march=armv7emsp` the same source emits native. It is on CircuitPython git `main` and tag 11.0.0-alpha.3, not in 10.3.x. Viper bodies that use `ptr8` / `uint` are not valid bytecode; ignoring the decorator then raises `NameError` when the function runs. A `@micropython.native` function whose body is ordinary Python can fall back. The bytecode artifact must contain zero native functions.

**Act.** For a 10.3.x deploy, compile with the matching CircuitPython `mpy-cross` and no `-march`, and do not put these decorators in that source. Bytecode-level levers remain `const`, `LOAD_FAST`, and preallocated buffers. A board on 10.3.1 raspberrypi (RP2040 or RP2350) can take a second artifact, `-march=armv6m` or `-march=armv7emsp`, from a separate compilation, and only that drive gets the native `.mpy`. Do not wait on `optional=True` before 11.0.0.

**Status:** `evidence-supported` for the 10.3.0, 10.3.1, 10.3.2, and 11.0.0-alpha.3 source flags, the decorator and `persistentcode` error strings, and the mpy-cross probes on this Mac (2026-11-15). On-device import of a native `.mpy` not run. `[family:circuitpython]`. Exp16 `lib/` is one application (bytecode only), recorded as a pointer in that project's `CONTEXT.md` and `CONCLUSIONS.md`. Supersedes the 2026-04-20 RP2040-only wording. Issues `#8902` (RP2040, open, long-term) and `#7966` (Thumb flag on ESP32-S3 crashes; that flag does not turn on Xtensa) stay the historical reports.

### Name loading: LOAD_FAST vs LOAD_GLOBAL

CircuitPython inherits MicroPython's bytecode VM unchanged — `py/vm.c`, `py/runtime.c`, and the opcode table carry over from the fork point with periodic merges. Relevant opcodes and their dispatch cost:

- `MP_BC_LOAD_FAST_N`: decodes a uint local-slot index, then does one C array subscript — `obj_shared = fastn[-unum]`, where `fastn` is the VM stack frame's local-variable region (`fastn[0]` is `local[0]`, `fastn[-1]` is `local[1]`, etc.) [CPy-src, `py/vm.c::MP_BC_LOAD_FAST_N`, lines 398-411, 2026-04-21].
- `MP_BC_LOAD_FAST_MULTI`: single-byte opcode covering the first N locals; same `fastn[...]` subscript mechanism, no uint decode on the critical path [CPy-src, `py/vm.c::MP_BC_LOAD_FAST_MULTI`, lines 1319-1322, 2026-04-21].
- `MP_BC_LOAD_GLOBAL`: decodes a qstr operand from bytecode, then calls `mp_load_global(qst)` which does `mp_map_lookup` on the module's globals dict, with fallback on miss to the builtins-override dict (if `MICROPY_CAN_OVERRIDE_BUILTINS`) and then to `mp_module_builtins_globals` [CPy-src, `py/vm.c::MP_BC_LOAD_GLOBAL` line 426 + `py/runtime.c::mp_load_global` lines 244-266, 2026-04-21].

Happy-path cost comparison: `LOAD_FAST_*` is one array subscript; `LOAD_GLOBAL` is one qstr decode plus one hash-map lookup (hash + probe) on the globals dict. The asymmetry is fully inherited from MicroPython, so the MicroPython speed-tuning guidance — "cache globally-scoped object references as function-locals at the top of hot functions" [MPy-docs, `docs.micropython.org/en/latest/reference/speed_python.html` § "Caching object references"] — applies to CircuitPython with the same underlying mechanism. The CPy file `py/vm.c` carries explicit `CIRCUITPY-CHANGE` markers elsewhere in the same file (e.g. line 1258), confirming the file is live CPy source rather than stale inherited-and-divergent code.

**Practical rule**: in any hot function, bind module-global references (`_pixels`, `_LUT`, module-scope constants, imported names) into function-local names once near the top. Every inner-loop use of those names then dispatches as `LOAD_FAST_*` rather than `LOAD_GLOBAL`. Applied example in this project: `lib/display/core.py::_render_colmajor` does `pixels = _pixels; lut = _LUT; off = OFF` before entering the `(x, y)` loops.

**Scope and caveat**: mechanism-verified (shared VM, identical opcode dispatch, identical `mp_map_lookup` in `mp_load_global`). Absolute speedup is workload-dependent. Stock 10.3.0 has no native emitter (§ `@micropython.native`). **Measured 2026-11-16** on UID `0740D10F1BE9` (ESP32-S2, CP 10.3.0 only; § On-device bytecode timings): a local copy beat a plain module global by 6.3 µs over 25 adds. Caching `OFF` on a 25-pixel list frame saved 3.7 µs, inside the noise. Caching `self.pixels` / `self.lut` / `self.off` saved 57 µs per frame, about the same size as that run's spread.

### `neopixel.NeoPixel` allocation behavior

`neopixel.NeoPixel` subclasses `adafruit_pixelbuf.PixelBuf`. In the pure-Python fallback (`adafruit_pypixelbuf`), `__init__` allocates `bytearray(bpp * n)` once and stores it in `self._post_brightness_buffer`; `show()` calls `_transmit(self._post_brightness_buffer)` with no per-call allocation [CPy-lib, `adafruit_pypixelbuf.py`, 2026-04-20]. NeoPixel's `_transmit` invokes the native `neopixel_write(self.pin, buffer)` [CPy-lib, `neopixel.py`, 2026-04-20]. If `brightness < 1.0`, a second `bytearray(self._post_brightness_buffer)` is allocated once on first setter access — one-shot, not per-frame.

Native C checked 2026-09-29 on the 10.3.0 tag at `shared-module/adafruit_pixelbuf/PixelBuf.c` (the old `_pixelbuf` path is gone). `construct` allocates the transmit `bytearray` once. `set_brightness` below 1.0 allocates `pre_brightness_buffer` once via `m_malloc_without_collect`. `show()` passes that existing buffer to `_transmit`. This closes the "native C not retrieved" gap for those three. `get_pixel` is the path that still allocates every call — see the next paragraph.

`PixelBuf.__getitem__` allocates one tuple per read. CircuitPython 10.3.0 `common_hal_adafruit_pixelbuf_pixelbuf_get_pixel` (`shared-module/adafruit_pixelbuf/PixelBuf.c`) fills a stack array of small ints from the byte buffer, then `return mp_obj_new_tuple(bpp, elems)`. NeoPixel bpp is 3, so each `pixels[i]` is a fresh 3-tuple. The channel values are `MP_OBJ_NEW_SMALL_INT` (not heap objects). `__setitem__` parses that tuple and writes bytes into the existing buffer (`pixelbuf_set_pixel_color`); it does not allocate another tuple. `auto_write` False skips `show()` on that store. Iterating `for p in pixels:` pays the same per-element tuple. Confirmed 2026-09-29; the earlier "inferred" tag on this sentence is superseded. Exp16 `set_rotation` pays 25 of these tuples per call — see § Preallocate.

### User-facing `asyncio` vs builtin `_asyncio`

CircuitPython does **not** ship CPython’s stdlib `asyncio`. Two different modules:

| Name | What it is | Where it lives |
|------|------------|----------------|
| `_asyncio` | Internal helper, not an end-user API | Compiled into firmware when `MICROPY_PY_ASYNC_AWAIT` / `MICROPY_PY_ASYNCIO` follow `CIRCUITPY_FULL_BUILD` (`py/circuitpy_mpconfig.mk`, `[CPy-src]` 10.3.0) |
| `asyncio` | Cooperative scheduler the sketches `import` | **Library bundle** (plus `adafruit_ticks`). Not frozen on `bpi_bit_s2` 10.3.0 — matrix lists `_asyncio` only (`[CPy-docs]` support matrix; `[Adafruit-learn]` “Cooperative Multitasking in CircuitPython with asyncio”) |

A successful `import asyncio` on host **CPython 3.13** (the Miniconda venv) is not evidence the board has `asyncio`. On device: copy bundle `asyncio` + `adafruit_ticks` onto CIRCUITPY (`circup install asyncio`). Host pytest of `async def` / `await asyncio.sleep` checks **shape** against CPython’s scheduler, not CircuitPython’s subset.

**Status:** `evidence-supported` for the split (docs + 10.3.0 mk + matrix). Device copy step still `[on-device-experiment]` until P8.

### `asyncio.sleep(0)` still yields once — a skip-the-call carve-out is not the same as a zero-duration sleep

`asyncio.sleep(0)` is not a true no-op: any `await` on it still hands control back to the event loop for one scheduling pass before resuming, per the coroutine/`await`-point semantics shared by CPython's stdlib `asyncio` and the CircuitPython/MicroPython bundle `asyncio` scheduler alike — this is a property of `await` itself (a suspension point), not of the sleep duration [inferred from general async/await semantics; consistent with CPython's own `asyncio.sleep()` docstring, which special-cases `delay <= 0` only to skip the timer-based wakeup, not the yield]. Consequence: **"skip the sleep entirely" and "`await asyncio.sleep(0)`" are two different behaviors** — only the former is a genuinely synchronous, immediate return with no scheduler hand-off.

**Applied `[project:circuitpython-exp16-planetx]` (2026-09-11, superseded for the fit path):** `lib/display/core.py::show_string()`'s fit-on-screen branch (`Display.show_string`, non-scrolling text, `loop == False`) guards the hold-duration sleep with `if interval_ms > 0: await asyncio.sleep(interval_ms * 5 / 1000)` rather than always awaiting a `0`-or-computed duration — a deliberate skip-the-call carve-out so `interval_ms == 0` returns immediately/synchronously, not a defensive no-op. Doc comment at lines 942-947 (iteratively refined 2026-09-11, Session 23 — see `projects/circuitpython-exp16-planetx/SESSION_LOG.md`).

**Correction 2026-10-10:** that guard and the `* 5` sleep are gone. A fitting `show_string` / `show_number` with `loop=False` always awaits the hold (`interval_ms * WIDTH`; `0` awaits `sleep_ms(0)` once) and then draws a blank frame without calling `_acquire`. `render_string` / `render_number` are the sync calls that leave the text lit. Host pytest 237 passed (`f0612ac`). On-device `unverified`.

**Extension 2026-09-13 (Session 33): a tight `while True: ... ; await asyncio.sleep(0)` loop is a genuine busy-spin on the bundle `asyncio` scheduler, not merely "yields once and moves on" — mechanism-verified against the shipped library's own source** (`Adafruit_CircuitPython_asyncio`'s `core.py`, the library that ships as this project's `lib/asyncio`, fetched 2026-09-13 from `github.com/adafruit/Adafruit_CircuitPython_asyncio/blob/main/asyncio/core.py`). `sleep_ms(t, sgen=SingletonGenerator())` sets `sgen.state = ticks_add(ticks(), max(0, t))` — for `t == 0` this is just `ticks()` (now). The scheduler's `run_until_complete` inner loop computes `dt = max(0, ticks_diff(t.ph_key, ticks()))` for the next-ready task; when `dt == 0` the `while dt > 0:` guard is false, so the scheduler's blocking-poll fallback (`_io_queue.wait_io_event(dt)`, a real `select.poll().ipoll(dt)` syscall that would otherwise let the CPU idle until timeout or I/O) is **skipped entirely** — the ready task is popped and re-run immediately. Consequence: whenever a `sleep(0)`-polling task is the *only* ready task (e.g. a button-dispatch pump while a sibling display task is itself mid-sleep between frames), the VM spins through that task's loop body as fast as it can execute bytecode, indefinitely — not "polls a bit more than needed," a genuine unbounded busy-loop. A positive interval (even a few ms) lets the scheduler's `dt > 0` path run, which reaches the real blocking poll. The generator is not allocated per call: `sgen=SingletonGenerator()` is created once as a default argument (source comment: "without allocating on the heap"). Refined 2026-09-27: `asyncio.sleep(t)` still evaluates `int(t * 1000)`, and that float multiply allocates one temporary float. The busy-spin finding is about scheduling, and that one float does not change it. See *A wakeup does not collect* below.

**Applied `[project:circuitpython-exp16-planetx]` (2026-10-19, replaces the 2026-09-13 `sleep(_POLL_INTERVAL_S)` note):** `Button.run` waits `await asyncio.sleep_ms(_POLL_MS)` with `_POLL_MS = 10`, and binds `sleep_ms` once outside the loop. 10 ms is still half of `keypad.Keys`' default scan interval (20 ms): the scan runs in the background, so a shorter Python poll does not see a new event sooner. After the event is queued, a uniform phase waits about 5 ms (`_POLL_MS / 2`). One scanner, one queue, and one pump per `Button`. `queue.overflowed` prints one warning. Host pytest **278 passed**. On-device `unverified`. The 2026-09-13 code used `asyncio.sleep(0.01)` on a shared pump; the lanes of 2026-09-29 are gone.

**Status:** `evidence-supported` for the general yield-once claim (async/await mechanism, cross-runtime); `[project]` lines are mechanically verified against this project's own source + the bundle library's own upstream source + first-party `keypad` docs.

**One `sleep(0)`, 2026-09-27:** a single `await asyncio.sleep(0)` is one scheduler lap (`dt == 0`, no blocking poll), not the busy-spin. The spin is a loop of those laps while this task is the only one due. Calling an `async def` allocates a coroutine instance every call (CircuitPython 10.3.0 `py/objgenerator.c`). `sleep_ms` does not allocate its generator: asyncio 3.1.1 reuses one `SingletonGenerator` default argument. `asyncio.sleep(t)` is `sleep_ms(int(t * 1000))`, so the float multiply still creates one temporary float object per call. Detail: exp16 `ai-notes/2026-09-27_handler-await-cost/NOTES.md` (coroutine) and `ai-notes/2026-09-27_scroll-sleep-chunking/NOTES.md` (the float). Byte sizes not measured on device.

**`sleep` vs `sleep_ms` cost, 2026-10-02:** Re-read Adafruit asyncio `main` `asyncio/core.py` (same functions as the 3.1.1 pin). `def sleep(t): return sleep_ms(int(t * 1000))`. `sleep_ms` is not `async def`; both return that one `SingletonGenerator`. Extra work in `sleep`: one Python call, one heap float from `t * 1000`, and `int()` truncation toward zero. `sleep_ms` then does `max(0, t)`, so a negative millisecond count is the same 0 ms yield. ESP32-S2 has no FPU (see the `time.monotonic` paragraph under *A wakeup does not collect*); the multiply is microseconds. The part that repeats is the float object, not a shorter sleep. Float32 round-trip `ms → ms/1000 → int(s*1000)` matches the teaching intervals 0, 1, 10, 20, 47, 51, 100, 150, 200, 800, 1000. It is off by 1 ms for 91 values in 0..10000; the first is 251 → 250. Host `struct` pack `'f'`, not on UID `0740D10F1BE9`. **Applied:** exp16 `lib/display` frame waits, the PlanetX motor poll, and `Button.run` (`sleep_ms(10)`, 2026-10-19) call `sleep_ms`. Motor `time.sleep` while the I2C lock is held stays blocking. `lib/buttons.py` still calls `asyncio.sleep` (lesson examples and the 10 ms pump).

**`≤ 0` is an immediate yield when awaited, 2026-09-27:** bundle `sleep_ms` does `ticks_add(ticks(), max(0, t))`, so a negative millisecond count is the same deadline as 0 (now). The pairing heap (`extmod/modasyncio.c` on 10.3.0, and the Python fallback `asyncio/task.py`) orders by that deadline, so `peek` sees a due task and `run_until_complete` leaves the `while dt > 0` loop without `wait_io_event`. The await still suspends for one lap. Tasks whose deadlines are still in the future stay queued. `sleep(seconds)` truncates with `int(t * 1000)`, so `(0, 0.001)` also becomes `sleep_ms(0)`. CPython 3.13 `asyncio.sleep` (`Lib/asyncio/tasks.py`) takes `delay <= 0` to a bare `yield` (`__sleep0`); a positive sub-millisecond delay there is a real timer. `_sleep_pollable`'s `total_s <= 0: return` did not await, so it was not this path. **Superseded 2026-09-29:** that branch now `await`s `sleep_ms(0)`, which is this path (one lap).

**Applied 2026-09-29 `[project:circuitpython-exp16-planetx]`:** `_sleep_pollable` on `total_ms <= 0` now `await asyncio.sleep_ms(0)` (one lap, singleton generator, no float). A tight loop of `interval_ms=0` holds is the busy-spin, and a sibling task that is due gets a turn. Scroll `interval_ms=0` is `sleep_ms(0)` per column (was `sleep(0)` until 2026-10-02). Not run on UID `0740D10F1BE9`.

### A wakeup does not collect

CircuitPython 10.3.0 compiles out allocation-threshold collection (`MICROPY_GC_ALLOC_THRESHOLD (0)` in `py/circuitpy_mpconfig.h`, re-read on the 10.3.0 tag 2026-09-27). The collector runs when an allocation cannot be satisfied, or on `gc.collect()`. It does not move live objects (`MICROPY_GC_SPLIT_HEAP` / `_AUTO` are on in that same header; fragmentation behavior is the heap-structure concept above).

`asyncio.sleep` parks the task until a ticks deadline. The scheduler waits in `select.poll` `ipoll`. The same header sets `MICROPY_INTERNAL_EVENT_HOOK` to `background_callback_run_all()` — USB, keypad scan, and similar — not `gc_collect`. PR #10379 (merged 2025-09-24) says that hook is serviced on the order of once per millisecond inside select. The poll C file was not re-read on 2026-09-27; the macro on the 10.3.0 tag was.

Waking a coroutine every 50 ms to check a flag therefore does not reclaim or compact. Dead objects from the previous turn stay until a later allocation fails or something calls `gc.collect()`. Extra wakeups that go through `asyncio.sleep(float)` or `time.monotonic()` add temporary floats (see the sleep paragraph above).

`time.monotonic()` (CP 10.3.0 `shared-bindings/time/__init__.c`) reads `common_hal_time_monotonic_ms()` → `supervisor_ticks_ms64()` → `port_get_raw_ticks`, then `mp_obj_new_float` (`py/objfloat.c` allocates one `mp_obj_float_t` per call). The tick read is the same shape on both ports: ESP32-S2 `esp_timer_get_time()`, RP2350 `time_us_64()`, each scaled by `* 512 / 15625` (`ports/{espressif,raspberrypi}/supervisor/port.c`). RP2350 is built `-mfloat-abi=softfp` with the M33 VFP helpers; ESP32-S2 has no FPU and links ROM libgcc. That float conversion is the chip difference, and it is microseconds. The heap float is the part that repeats. `supervisor.ticks_ms()` uses the same millisecond counter and returns a small int (no float). Not timed on UID `0740D10F1BE9`. Float32 millisecond resolution holds for about 2^22 ms (~1.2 h), per the `time.monotonic` docstring in that binding.

**Applied `[project:circuitpython-exp16-planetx]`:** scroll columns stay one sleep per column (`Image._scroll_image`, `show_string` scroll loop), now `asyncio.sleep_ms(interval_ms)` (2026-10-02; previously `sleep(interval_ms/1000)`). Holds already slice via `_sleep_pollable` because that wait has no next frame. Recommendation 2026-09-27, no code change: do not slice column sleeps to help the heap. Detail: exp16 `ai-notes/2026-09-27_scroll-sleep-chunking/NOTES.md` (gitignored, may vanish).

**Status:** `evidence-supported` for the control flow (10.3.0 header + asyncio 3.1.1 `core.py`). Float and coroutine sizes `unverified` on device. Select-loop cadence `unverified` beyond the PR statement and the header macro.

### `asyncio.run` from inside a running task raises

Bundle `asyncio.run(coro)` (`Adafruit_CircuitPython_asyncio` `asyncio/core.py`, `main` fetched 2026-09-27) runs the coroutine only when `cur_task is None`. Otherwise it raises `RuntimeError: asyncio.run() cannot be called from a running event loop`. A press handler called from `Button.run` / `OnboardButtons.run` is already inside the `asyncio.run(main())` that started the script, so `asyncio.run(d.show_string(...))` in that handler hits this raise. `asyncio.create_task` from that same sync handler schedules the coroutine onto the loop already running and returns immediately; the handler does not wait. `await handler()` is different: it enters `handler` immediately on the current task and runs it until `handler`'s first suspending `await`. Other tasks are selected from that suspension, not before `handler` starts. When the awaited handler returns, the same task takes the next event of that button. There is one handler slot, so there is no second handler on the same event. Waiting for the result still requires the caller to be a coroutine. Not re-run on UID `0740D10F1BE9`. **Per button, 2026-10-19 (replaces the 2026-09-29 lane sentence):** each `Button` is its own pump and its own `keypad` queue. `_on_event` awaits a result that has `__await__`, then takes the next event of that button. The other button's pump runs during that `await`. A handler exception is printed and that pump continues. A second `run()` raises `RuntimeError`. Host `tests/test_buttons.py`. On-device `unverified`. The 2026-09-29 `_SwitchLane` list is gone. Alex asked 2026-09-27 20:40 PDT; the await-entry order, 20:56 PDT. **`__code__.co_flags` does not identify `async def` on CircuitPython 10.3.0** (same VM on ESP32-S2, ESP32-S3, RP2040, RP2350): `py/objfun.c` sets `__code__` only for plain functions and generators, and `py/objcode.c` exposes no `co_flags`. A check of `co_flags & 0x80` returns false. The type of an `async def` object is named `coroutine` (`mp_type_coro_wrap` / `mp_type_native_coro_wrap` in `py/objgenerator.c`, assigned from `py/emitglue.c`). `type(handler).__name__ == "coroutine"` is the registration-time check on this VM. CPython uses the `co_flags` half instead, because there the function's type name is `function`. Bound methods are type `bound_method` and do not expose the wrapped function (`py/objboundmeth.c`), so that check misses them. Coroutine instances do expose `__await__` (`py/objgenerator.c`).

**Status:** `evidence-supported` for the raise in asyncio **3.1.1** source (tag `705ae0c`, commit `a6eafa69` 2026-07-17) and in exp16's vendored `lib/asyncio/core.mpy` after the 2026-09-30 reinstall (3434 bytes, guard string present). On-device confirmation `unverified`. The previous vendored file (3312 bytes, no guard string) re-entered `run_until_complete`; that file was replaced. See the next concept.

### `asyncio.run` returns when its coroutine returns; other tasks are not cancelled

Bundle `asyncio.run` ends the scheduler on the turn the coroutine it was given returns. Other tasks stay where they are. Their `finally` blocks do not run.

`run_until_complete` is the same function text in Adafruit asyncio tags **3.1.0** and **3.1.1** (`asyncio/core.py`, compared 2026-09-30). The main coroutine's return arrives as `StopIteration`. The handler then executes `if t is main_task: return er.value` (source comment: "If it's the main task then the loop should stop"). That return does not drain `_task_queue`, does not call `Task.cancel()`, and does not call `new_event_loop()`.

`finally` in a suspended task runs only when that coroutine is resumed: a normal completion, or `coro.throw`. `Task.cancel()` is the throw. On CP 10.3.0, `extmod/modasyncio.c` `task_cancel` stores the `CancelledError` type on the task and pushes the task onto `_task_queue`; the Python scheduler then `t.coro.throw(exc)`. `run()` never calls `cancel`. The main coroutine's own `finally` does run, because it returned before the scheduler saw the `StopIteration`.

`_task_queue` is a module global. A later `asyncio.run` in the same VM session resumes tasks the previous `run` left queued. When `code.py` then returns, those tasks are not resumed: the supervisor waits, and does not start `code.py` again until a reload (below).

**CPython does cancel them.** Host venv CPython **3.13.11** `asyncio/runners.py`: `asyncio.run` is `with Runner`, and `Runner.close` calls `_cancel_all_tasks`, which `task.cancel()`s every `asyncio.all_tasks` and then `run_until_complete(gather(...))`, so each `finally` runs, and then async generators are shut down. A host test that sees `finally` after `asyncio.run` returns is this path. It does not describe the board.

**Vendored mpy vs tag 3.1.1.** exp16 `requirements.txt` says `asyncio==3.1.1`. Until 2026-09-30 the vendored `lib/asyncio/core.mpy` was 3312 bytes and did not contain `asyncio.run() cannot be called from a running event loop`, so that copy's `run()` was the earlier `return run_until_complete(create_task(coro))`. Tag 3.1.1 source has the string (commit `a6eafa69`, 2026-07-17, MicroPython #15187). Local `mpy-cross` 10.3.0 with `-s asyncio/core.py`: tag 3.1.1 compiles to 3434 bytes and contains the string; tag 3.1.0 compiles to 3358 bytes and does not. **Replaced 2026-09-30:** Alex deleted `lib/asyncio/` and `circup --path` installed the current bundle's `asyncio` plus `adafruit_ticks`. New `core.mpy` is 3434 bytes and the guard string is present (Alex's check). `circup freeze -r` on 2026-09-30 rewrote `requirements.txt` to the same `adafruit_ticks==1.1.7` and `asyncio==3.1.1`. The install came from Adafruit bundle tag `20260930`. The no-cancel finding is in `run_until_complete`, so it holds for both the old and the new `run()`. Not executed on UID `0740D10F1BE9`; the board still has whatever `lib/asyncio/` was last synced.

**Applied `[project:circuitpython-exp16-planetx]` (updated 2026-10-19):** `buttons._serve` is gone. `Button.run`'s `finally` only clears `_running`, and that `finally` runs when the pump task is resumed. `create_task(button.run())` left inside `await asyncio.sleep` is not resumed when `asyncio.run(main())` returns, so the flag clear does not run either. The module docstring's "background tasks stop" is this: the scheduler returns and they are not resumed. Not executed on the board. The 2026-09-29 text said `_serve` cancelled lane tasks.

**After `code.py` returns.** Latest stable release as of 2026-09-30 is **10.3.1**. `main.c` `run_code_py` matches **10.3.0** (this board) on the wait itself; the 10.3.1 diff there is the status-bar exception test and a safe-mode `reset_port()`. On a normal return the supervisor prints `Code done running.`, runs `cleanup_after_vm` (`stop_mp` → `gc_deinit`, then `reset_all_pins()`), then waits in that function. The wait does not start `code.py` again. Autoreload is on by default before `boot.py`. A CIRCUITPY content write over USB (`supervisor/shared/usb/usb_msc_flash.c`, not a dirty-bit write) or a web-workflow write calls `autoreload_trigger()`; after `CIRCUITPY_AUTORELOAD_DELAY_MS` the wait ends and the outer loop prints `soft reboot` and runs code again. With autoreload off, a file write does not reload. CTRL-D at the `Press any key to enter the REPL. Use CTRL-D to reload.` prompt also reloads (`RUN_REASON_REPL_RELOAD`). Any other key enters the REPL. `supervisor.reload()` and `set_next_code_file(..., reload_on_success=True)` set `skip_wait` and skip this wait; a normal return does not. `gc_sweep_all` runs `__del__` only on unreachable objects. Generator and coroutine types have no `__del__` (`py/objgenerator.c`), so an abandoned task's `finally` still does not run when the heap is discarded.

**Practical consequence.** Abandoned tasks do not keep the program running. What keeps it alive is a coroutine passed to `asyncio.run` that never returns (`gather` of forever `run()`s, `Display.forever`). A shutdown action in a background `finally` does not run on the board. Put it in the main coroutine's `try/finally` or after `asyncio.run(...)`. The WS2812 matrix keeps its last latched frame, and a Nezha motor started with `start()` keeps the controller's last command (both `unverified` on device). Exp16's background `finally` on `Button.run` only clears `_running`.

**Status:** `evidence-supported` for the control flow (asyncio 3.1.0 and 3.1.1 `core.py`; CP 10.3.0 `task_cancel`; CP 10.3.0 and 10.3.1 `main.c` / `reload.c` / `usb_msc_flash.c` / `gc.c` / `objgenerator.c`; CPython 3.13.11 `runners.py`; exp16 `core.mpy` string check). On-device run `unverified`.

### Awaitable detection on CircuitPython: `async def` objects have `__await__`; plain generators do not

CP 10.3.0 `py/objgenerator.c` defines two instance types. `mp_type_gen_instance` (plain generator) has `close` / `send` / `throw` / `pend_throw`. `mp_type_coro_instance` (what an `async def` call returns, `MICROPY_PY_ASYNC_AWAIT`) has the same four plus `__await__` (marked `CIRCUITPY-CHANGE`). So `hasattr(x, "__await__")` is true for a coroutine on the board and false for a plain generator; `hasattr(x, "send")` is true for both (the bundle `asyncio.create_task` uses `send`). Exp16 `Button._on_event` checks `__await__`; `Display.forever` (pre-change) checked `__await__` or `send`. Whether `await <plain generator>` works on CP is `unverified`.

**Status:** `evidence-supported` for the two type tables (10.3.0 source read 2026-09-30). `[project:circuitpython-exp16-planetx]`. On-device `hasattr` probe not run.

### Risk: calling an `async def` without `await` does nothing, and the board is expected to say nothing

`f()` for `async def f` only builds a coroutine object (CP 10.3.0 `objgenerator.c`: the call allocates the instance; the body starts at the first `send` / `await`). A statement `display.show_string("Hi")` with no `await`, `asyncio.run(...)` or `create_task(...)` therefore never runs. CPython 3.13 emits `RuntimeWarning: coroutine ... was never awaited` at garbage collection. I saw no such warning path in the CircuitPython `objgenerator.c` I read, so the failure is expected to be silent (no traceback, no output).

**Status:** mechanism `evidence-supported` (source). "Silent on the board" is `unverified`: not run on UID `0740D10F1BE9`. `[project:circuitpython-exp16-planetx]` `[cross-experiment candidate]` (any async CircuitPython code).

**Exp16 exposure (Alex asked 2026-10-02 that this be remembered):** all Tier 2 `Display` methods, `Display.forever` once it is `async`, `pause`, and the button `run()` methods. Not new, but easy to hit: a forgotten `await` on `forever` or `run()` ends the script at once with no error. **Tutor screening:** watch-list item S1 in `CodingTutor/notes-learnings-insights_for_building_tutor/03_open-questions-todos.md`. **Verification queue:** omit one `await` on the board and read the serial output; if a warning appears, correct the status. **Mitigation ideas, none built:** an editor rule (Pyright `reportUnusedCoroutine`) and a docstring line "must be awaited or passed to `asyncio.run`". A library-side guard cannot see a coroutine that was never started.

### Scheduler ordering and fairness (bundle `asyncio` 3.1.1, CP 10.3.0 `_asyncio`)

Not preemptive, no priorities, no time slices. Ready tasks sit in a pairing heap ordered by `ph_key` = wake-up time in ms ticks (`task_lt`: `ticks_diff(k1, k2) < 0`). Equal keys keep insertion order (`py/pairheap.c`: "stable"; `push` melds the new node first so an older equal-key node stays on top). `sleep_ms(0)` / `sleep(0)` re-queues the task with key = now, so it goes **behind** every task whose key is already `<=` now, and tied zero-sleepers alternate FIFO. A task that is due is never jumped by a 0 ms task. Every lap of `run_until_complete` runs `_io_queue.wait_io_event(dt)` at least once (`dt` starts at 1, so the `while dt > 0` body always executes), so with `dt == 0` it is a **non-blocking** poll: I/O waiters are still woken each lap. Woken tasks are pushed with key = now, so a task made ready after a zero-sleeper re-queued waits at most one extra round of that task.

Guarantee: no starvation among tasks that suspend; a ready task runs before a zero-sleeper's second following round. **No promptness guarantee:** each task runs until its next `await`, so latency of any other task is the sum of the non-suspending stretches ahead of it. One lap runs one task, so "each round every other task runs" is false for tasks that are not yet due.

Host probe 2026-10-02 (the bundle's pure-Python `task.py`/`core.py` 3.1.1 on CPython 3.13 with a fake `select.poll`; board uses C `_asyncio`, same algorithm; ESP32-S2 timing not measured): 1 zero-sleeper, 5 ms sleeper woke 200 times in 1 s, max lateness 0.01 ms; 3 zero-sleepers laps 337050/337049/337049; with 2 ms of non-yielding work per round the sleeper was 1.0 ms late (1 spinner) and 5.0 ms late (3 spinners).

**`sleep_ms` wants an int:** `sleep_ms(t)` stores `ticks_add(ticks(), max(0, t))` (`adafruit_ticks.ticks_add` is `(ticks + delta) % 2**29`), so a float `t` yields a float deadline. The C `task_queue_push` takes the deadline as a small int (`assert(mp_obj_is_small_int(...))`, `ph_key = args[2]`) and `task_lt` reads it with `MP_OBJ_SMALL_INT_VALUE`; a float there would mis-order tasks if the assert is compiled out (`unverified` on the board; the Python fallback `task.py` would tolerate it). Convert with `int()` before calling `sleep_ms`; `asyncio.sleep(t)` already does `int(t * 1000)`. `int(-3)` stays `-3`; `max(0, t)` inside `sleep_ms` is what turns that into a 0 ms wake-up. Applied 2026-10-02: exp16 `Display.forever`, `_sleep_pollable`, `_sleep_until_cancelled`, `show_string`, and `Image._scroll_image` each call `int()` once before the wait. The scroll/show-image `if interval_ms < 0: interval_ms = 0` branches were removed.

**Re-running the probe (host, ~5 min):** put Adafruit_CircuitPython_asyncio 3.1.1 `asyncio/{__init__,core,task,event,funcs,lock,stream,traceback}.py` in a scratch dir (package name `asyncio`, first on `sys.path`), add an `adafruit_ticks.py` with 29-bit `ticks_ms`/`ticks_add`/`ticks_diff` over `time.monotonic()`, and set `select.poll` to a fake whose `ipoll(dt)` sleeps `dt` ms and returns an empty iterator (CPython's `poll` has no `ipoll`). Then spawn N tasks looping `await asyncio.sleep_ms(0)` (optionally a busy-wait of k ms per round) beside a task looping `await asyncio.sleep_ms(5)` and record its lateness. This runs the Python scheduler, not the C `_asyncio` the board uses.

**Correction 2026-10-02:** the *Extension 2026-09-13* paragraph above says `wait_io_event` is "skipped entirely" when `dt == 0`. That is wrong. Only the **blocking** poll is skipped; `wait_io_event(0)` still runs once per lap (`run_until_complete`, `dt = 1` start). The busy-spin conclusion (100 % CPU while a lone zero-sleeper is the only ready task) stands; "I/O waiters would starve" does not follow.

**Status:** `evidence-supported` (10.3.0 `modasyncio.c`, `pairheap.c`/`.h`, asyncio 3.1.1 `core.py`, host probe). On-device timing `unverified`. `[project:circuitpython-exp16-planetx]`.

### `hasattr` on a missing name does not allocate

`hasattr` (CircuitPython 10.3.0 `py/modbuiltins.c`) calls `mp_load_method_protected` (`py/runtime.c`), which calls `mp_load_method_maybe`. A missing name leaves `dest[0] == NULL`. It does not call the raising `mp_load_method`, so the usual miss does not build an `AttributeError`. `nlr_push` / `nlr_pop` still wrap the lookup. `NoneType` (`py/objnone.c`) has no attribute slot and no locals dict, so `hasattr(None, "__await__")` is that miss: a type-pointer check, then false. The name `"__await__"` is a compiled qstr. `True` / `False` are singletons. Applied: exp16 `Button._on_event` once per event. Not timed on UID `0740D10F1BE9`.

**Status:** `evidence-supported` for the control flow (10.3.0 tag, read 2026-09-28). Duration `unverified`.

### `mpy-cross` is CircuitPython’s binary, not PyPI MicroPython

Host bytecode compile for a CircuitPython board must use **Adafruit’s** `mpy-cross` matching the firmware series (S3 `bin/mpy-cross/macos/`, e.g. `mpy-cross-macos-10.3.0-arm64`). Adafruit: do **not** use `pip install mpy-cross` / pypi.org — that tool is MicroPython and emits the wrong `.mpy` ([Adafruit-learn] “Creating an .mpy file”; [CPy-src] issue #10032). CP **10.3.0** emits **mpy v6.3** (binary `--version`, 2026-09-04). Installed binary, located 2026-09-27: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/mpy-cross-macos-10.3.0-arm64`. Compiling `.py` → `.mpy` catches CP-rejected syntax; it is not an on-device run. The binary is built from `mpy-cross/` inside `adafruit/circuitpython` and shares `py/compile.c` with the firmware of that tag. There is no separate mpy-cross release line.

**`.mpy` header (10.3.0 `py/persistentcode.c` / `.h`, still the layout on 11.0.0-alpha.3).** Four bytes: `'C'`, `MPY_VERSION`, arch-and-subversion, small-int bit width. `MPY_VERSION` is 6 and `MPY_SUB_VERSION` is 3 on tags 10.3.0, 10.3.1, 10.3.2, and 11.0.0-alpha.3 (read 2026-11-17). A bytecode file stores arch 0, so byte 2 is 0 and byte 3 is `0x1f` (31). Same prefix as vendored `lib/asyncio/*.mpy`. Do not pass `-msmall-int-bits`; the default is 31, and `header[3] >` the firmware's small-int width raises `ValueError: incompatible .mpy file`.

| Header | Import result |
|---|---|
| First byte `'M'` | `ValueError: MicroPython .mpy file; use CircuitPython mpy-cross` |
| Not `'C'`, or version byte ≠ 6, or small-int bits too wide | `ValueError: incompatible .mpy file` |
| Arch 0 (bytecode) | Sub-version is not checked. One such file loads on every board of that `MPY_VERSION`, Espressif and RP2350 included |
| Arch ≠ 0, and the firmware's own arch is `NONE` (10.3.0, and 10.3.x espressif) | `ValueError: native code in .mpy unsupported` |
| Arch ≠ 0, firmware has a loader but for a different arch | `ValueError: incompatible .mpy arch`. Native sub-version must also equal 3 |

**Native / viper** (`-march`, `-X emit=`) is a different question from bytecode. Decision table: § `@micropython.native` and `@micropython.viper`. `-X emit=native` or `emit=viper` together with `-march` compiles the whole module that way, decorators or not.

**Import names, tag 11.0.0-alpha.3 only** (`py/builtinimport.c`, gated on `MICROPY_PERSISTENT_CODE_LOAD_NATIVE`). Search order is `foo.py`, then `foo.<arch>.mpy`, then `foo.mpy`. `<arch>` is the firmware's `mpy-cross -march` name (`MPY_FEATURE_ARCH_NAME`), for example `foo.armv7emsp.mpy` or `foo.xtensawin.mpy`. A `.py` wins. No 10.3.x tag has this probe (`builtinimport.c` has zero `MPY_FEATURE_ARCH_NAME` hits on 10.3.0, 10.3.1, 10.3.2). The 11.0.0-alpha.3 troubleshooting page: a `foo.<arch>.mpy` built for another architecture or CircuitPython version raises rather than falling through to `foo.mpy`. Espressif `CIRCUITPY_LOAD_NATIVE ?= 1` is in that alpha (`ports/espressif/mpconfigport.mk`) and absent from 10.3.2. 10.4.0, which announced the espressif loader, was dropped; the next stable is 11.0.0, no date.

**Status:** `evidence-supported` for the PyPI warning, 10.3.0 → v6.3 on this Mac, the header checks on the 10.3.1 `persistentcode.c` (same checks as 10.3.0), and the version / import-name probes on the tags above. `[family:circuitpython]`.

### `#` comments and docstrings are absent from CircuitPython `.mpy` files

`mpy-cross` compiles `.py` to bytecode (`.mpy`). The lexer drops a `#` comment at the `#`; the text never becomes a token. CircuitPython sets `MICROPY_ENABLE_DOC_STRING` to 0 (`py/mpconfig.h` default, also `py/circuitpy_mpconfig.h`), so a docstring is an unused string expression and is discarded. Same for any bare string statement. A string that is bound or otherwise used is stored in the `.mpy` constant pool, roughly one source byte per string byte.

`-O` does not change that. Default is `-O0`. `-O1` and above omit `assert` and treat `__debug__` as false. `-O3` also omits source line numbers ([MicroPython `opt_level`](https://docs.micropython.org/en/latest/library/micropython.html#micropython.opt_level)). The embedded source name (`-s`, default = the input path) is stored; pass a short `-s` when the path is long.

On-device import of a `.py` uses the same compiler flags, so comments and docstrings are also absent from the RAM bytecode. They still occupy CIRCUITPY if the `.py` itself is the file on the volume. The BPI-Bit-S2 user volume is the TinyUF2 `ffat` partition: **983040 bytes** (960K), separate from the firmware slot.

**Measured 2026-10-20** with `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/mpy-cross-macos-10.3.0-arm64` (`-O0`, `-s` = basename): 526033 bytes of `#` comments → 53-byte `.mpy` (49-byte file with no comments); 84039-byte module docstring and a 57009-byte bare string statement → a few dozen bytes; a 38010-byte assigned string → 38037-byte `.mpy`. Bare annotations added nothing; `from __future__ import annotations` added the import only (48 → 94 bytes on a one-function file). Exp16 `lib/display/core.py` is 72083 bytes (~72% comments + docstrings) → 6916-byte `.mpy`. `lib/buttons.py` 15955 → 1870. The eighteen `lib/**/*.py` files sum to 163963 source bytes and 24496 compiled bytes.

**Status:** `evidence-supported` (10.3.0 binary size probe + `MICROPY_ENABLE_DOC_STRING` in the 10.3.0 tag). `[domain:circuitpython-runtime]` `[project:circuitpython-exp16-planetx]` for the file sizes.

### Cost of extra (duplicated / specialized) code: bytes, not cycles

Question (Alex, 2026-11-06): does trading source length for fewer per-iteration operations (split loops, duplicated inner loop) cost flash or interpretation time? `[domain:circuitpython-runtime]`.

| Cost axis | Finding | Status |
|---|---|---|
| Source file on CIRCUITPY (flash) | Comments and docstrings are the bulk of it; the `.mpy` is ~10x smaller (see previous concept). Volume is 983040 bytes; whole exp16 `lib/` is ~24 KB compiled. | evidence-supported |
| Bytecode size of the change | Measured with mpy-cross 10.3.0 on isolated functions: `_draw_text` two stepped loops vs one loop with `if col < start`: **355 → 372 bytes (+17)**. `_render_ring_window` split into two loops (inner pixel loop duplicated): **233 → 277 bytes (+44)**. Whole `core.py` HEAD 6921 → working tree 6982 (**+61 bytes**, both edits). | evidence-supported (host measurement; function snippets, not the on-device layout) |
| Where the bytecode lives at run time | A `.mpy` read from the filesystem is **copied to the RAM heap** (`py/persistentcode.c`: `fun_data = mp_reader_try_read_rom(...)`; if NULL, `m_new(uint8_t, fun_data_len)` + `read_bytes`). Only memory-mapped sources (frozen modules) are referenced in place. A `.py` is compiled on import into the same RAM form. So extra code costs **heap bytes, once, at import**, not flash execution space. Read against CP 10.0.x source; 10.3.0 not re-read. | evidence-supported (source) |
| Heap placement on `bpi_bit_s2` | `ports/espressif/supervisor/port.c` `port_malloc` tries `MALLOC_CAP_SPIRAM` first when `CONFIG_SPIRAM`; board has 2 MB PSRAM, so the VM heap, and the bytecode, are probably in cached PSRAM (slower than internal RAM on a cache miss). That the VM heap itself goes through `port_malloc` is `[inferred]`, not re-read. | partly unverified |
| Cost per executed iteration | The VM executes only the bytecode on the path taken. A second copy of a loop body that is not entered adds **no** per-call or per-iteration time. Splitting at a known boundary executes the same inner bodies as before and drops the per-column test. | mechanism (follows from the interpreter) |
| Cache / locality | The VM's C code runs from flash through the instruction cache; bytecode is data in the heap. The hot loops here are a few hundred bytes of bytecode, so cache footprint is not a plausible constraint. | `[inferred]`, not measured |
| Import time | Proportional to bytecode size (read + copy + GC allocation), plus on-device compilation if the file is `.py`. +61 bytes on a 6982-byte module is under 1%. Not timed on the board. | `unverified` |

**Conclusion.** For this class of change (tens of bytes of bytecode, hot loop untouched in size) the code-size cost is negligible on every axis, and the readable-source cost (a reader must keep two copies in sync) is the real cost. The larger effect on RAM and import time is deploying `core.py` as `.py` (compiled on the board, peak RAM during compilation) versus `.mpy`; unmeasured on the device. Rule of thumb: duplicate only a short inner loop, comment why, and have a test that exercises both copies.

Verification queue: time `import display` on UID `0740D10F1BE9` with `.py` vs `.mpy` and report `gc.mem_free()` before/after; measure frame time for one `render_string` with `time.monotonic_ns()` (see exp16 plan § 6.3 note for the `_draw_text` test).

### `__slots__` is not implemented on CircuitPython — declaring it is silently inert, not an error

Standard Python's `__slots__` (a class-level tuple of allowed instance-attribute names) replaces each instance's `__dict__` with a fixed-size slot layout: memory savings scale with instance count, plus marginally faster attribute access (no dict hash/probe per get/set) — general Python-language behavior, not CircuitPython-specific [general Python semantics; cross-checked against `docs.python.org/3/reference/datamodel.html#slots` and `wiki.python.org/moin/UsingSlots`, 2026-09-13].

**CircuitPython itself does not implement `__slots__`** — confirmed via an open upstream issue: `adafruit/circuitpython#10517` ("support for `__slots__`", opened 2025-07-28, labels `enhancement`/`micropython core`, milestone "Long term", still open as of 2026-09-13). The issue states plainly "CircuitPython does not use `__slots__` within class definitions," and a CircuitPython maintainer (`@dhalbert`) attributes this to upstream MicroPython, citing an unmerged MicroPython PR (`micropython/micropython#3392`) and issue (`micropython/micropython#6070`) [CPy-src (GitHub issue), 2026-09-13].

**Practical consequence**: declaring `__slots__ = (...)` on a class does **not** raise an error on CircuitPython — it's simply not recognized as special, so it becomes an ordinary (unused) class attribute. Every instance still gets a full per-instance `__dict__`; there is no memory saving and no attribute-lockdown (assigning an undeclared name still succeeds, unlike real `__slots__` under CPython, which would raise `AttributeError`). Host **CPython** pytest, by contrast, *does* honor `__slots__` fully — so a test suite passing is not evidence the optimization does anything on the actual board. Any class meant to run identically on both runtimes should not rely on `__slots__` for either its memory-saving or its attribute-lockdown behavior.

**Applied `[project:circuitpython-exp16-planetx]`:** considered for `lib/buttons.py`'s `Buttons` class (2026-09-13, Session 26) — declined for two independent reasons: (1) inert on the actual device per this finding; (2) even under CPython where it *would* work, `Buttons` is constructed exactly once per program run (not "lots of instances"), so the memory-saving case doesn't apply regardless of platform.

**Status:** `evidence-supported` (primary source: the CircuitPython repo's own open issue, not a third-party blog).

### `keypad.Keys` lifetime is separate from `EventQueue` — hold the scanner

`keypad.Keys` owns `self->events`; `EventQueue` has no back-pointer to `Keys` (`shared-module/keypad/{Keys,EventQueue,__init__}.c`, CP **10.3.0**). Keeping only `keys.events` drops the last Python reference to the scanner.

Scanning still continues on this firmware because `keypad_register_scanner` puts `Keys` on `keypad_scanners_linked_list`, a GC root (`MP_REGISTER_ROOT_POINTER`). `Keys` has no `__del__`; `deinit()` (or context-manager `__exit__`) is explicit. That registry-as-GC-root is an implementation detail, not the documented contract — the docs treat `Keys` as the object you own; `events` is the queue associated with it.

**Act:** keep a Python reference to `Keys` whenever the scanner must stay alive or `deinit()` might be needed later. Same class of hold as keeping a `neopixel.NeoPixel` even if you only write its buffer.

**Applied `[project:circuitpython-exp16-planetx]`:** `lib/buttons.py` `self._keys = keypad.Keys(...)` — unread on purpose; comment on that assignment (2026-09-13).

**Status:** `evidence-supported` (CP 10.3.0 C sources + type definition, not inferred from examples).

### Keypad scan vs `EventQueue.clear` — CP 10.3.0

`EventQueue.overflowed` is read-only (`MP_PROPERTY_GETTER` only, `shared-bindings/keypad/EventQueue.c`). The C setter is not in the Python API. `clear()` sets the flag false and also `ringbuf_clear`s queued events (`shared-module/keypad/EventQueue.c`).

A scan records an event only from `keypad_tick` → `keypad_scan_maybe`, and only when `interval` has elapsed (default 20 ms). `keypad_tick` runs in `supervisor_tick`. On ESP32-S2 that is the `esp_timer` callback (`ports/espressif/supervisor/port.c`, `CONFIG_FREERTOS_UNICORE` calls it directly). That task can preempt the VM between bytecodes. `keypad_scan_maybe` scans once, then sets `next_scan_ticks = now + interval`. A late tick does not emit one event per missed interval. One `Keys` pin passes at most one key to `keypad_eventqueue_record` per scan (`keypad_debounce` returns true once per key per scan). Several events in one stretch require that stretch to last several intervals.

`await` is a separate, larger window: the VM is parked and the timer task runs many scans. Events from an `await` stay in the queue until the next `get()`. `clear()` after that drain does not drop them.

Every bytecode jump also runs `RUN_BACKGROUND_TASKS` (`MICROPY_VM_HOOK_LOOP` in `py/vm.c`, on both paths of `POP_JUMP_IF_*`). That hook is `background_callback_run_all`, not `keypad_tick`. The keypad scan is the timer path above, not this hook.

**Act:** read `overflowed` after each `get()` that returns an event, before its handler, and warn once (a local flag). An overflow leaves a full queue, so the next `get()` returns an event and this check sees it right after the stall. That `get()` freed one slot for the `print`. Call `clear()` only after the drain (`get()` is `None`), with no `print` and no `await` before it. `print` waits on USB and can span many scans; events from that wait stay queued if `print` is after `clear()`. A scan that lands between the empty `get()` and `clear()` can insert one event, and `clear()` drops it. No Python sequence closes that window. The gap bound is time, not CPU speed: about gap ÷ `interval` events, so a gap under 20 ms holds at most one. Only a VM pause (higher-priority task, GC on an allocating call) stretches it. One extra `get()` before `clear()` only trims the gap by one property read and branch (rough guess 5–20 µs, about 1 in 1000–4000 per overflow), so it is not used. Moving the `print` into its own `asyncio.create_task` does not help: `print` is synchronous native code, so it blocks the VM just as long inside a task. The task also runs only at the handler's yield, so the warning comes after the handler and the queue may be full again. Duration of a one-line `print` with a reading host, no host, or a host that opened the port but does not read: `unverified`.

**Applied:** exp16 `lib/buttons.py` `Button.run` overflow path (2026-10-20). On-device timing of the leftover one-event window: `unverified`.

**Status:** mechanism `evidence-supported` (10.3.0 sources named above). Not run on UID `0740D10F1BE9`.

### Caching `module.attr` in a local — only for tight loops

`f = asyncio.sleep_ms` turns a global lookup plus an attribute lookup into one local read. That is the MicroPython speed-guide trick for tight loops. In a loop that `await`s a 10 ms sleep on every pass (exp16 `Button.run` idle poll), it saves an estimated 1–3 µs per pass, about 100 passes/s per button. That is well under 0.2 % CPU, and the scheduler work inside `sleep_ms` costs more. **Act:** do not add the alias in sleep-paced loops; prefer plain `asyncio.sleep_ms(...)`. A captured alias also ignores a later monkeypatch of `asyncio.sleep_ms` in host tests. **Status:** the 1–3 µs estimate for one `module.attr` alias in a sleep loop was not re-measured. A related on-device figure (UID `0740D10F1BE9`, 2026-11-16, § On-device bytecode timings): caching three attributes across a 25-pixel frame saved 57 µs versus reading them per pixel. `[domain:circuitpython-runtime]`

### A Python function or method call is never inlined; merging two helpers saves one real call

`[domain:circuitpython-runtime]` Question (Alex, 2026-11-15, exp16 `Display._ensure_integer_offset_and_acquire`, which merges an offset check and `_acquire`): is there compiler inlining, and what does a call cost?

- **No inlining of Python calls.** `py/compile.c` / `py/emitbc.c` (adafruit/circuitpython `10.0.x`) contain "inline" only for the inline *assembler* (`@asm_thumb` etc., not available here, see § `@micropython.native`). The compiler does constant folding (`MICROPY_COMP_CONST_FOLDING`) but never substitutes a function body at a call site.
- **What one call executes** (`py/vm.c`, `py/objfun.c::fun_bc_call`): `MP_BC_LOAD_METHOD` (`mp_load_method` finds the method without creating a bound-method object), `MP_BC_CALL_METHOD`, then `fun_bc_call` decodes the code-state size, allocates the frame (`alloca` on the C stack when `state_size <= VM_MAX_STATE_ON_STACK`, else the heap), zeroes it, runs `mp_setup_code_state` (argument binding), and calls `mp_execute_bytecode` recursively; on return it frees a heap frame. `MICROPY_STACKLESS` defaults to 0 in `py/mpconfig.h`, so a call recurses the C VM; whether the espressif port overrides that was not checked.
- **Consequence.** A call is a fixed per-call cost of that setup, paid again for every call regardless of the callee's size. Merging two always-paired helpers removes one such setup per use.
- **Measured 2026-11-16** on UID `0740D10F1BE9` only (§ On-device bytecode timings): one extra Python call was **9.4 µs** (`_ensure_integer_offset` then `_acquire` vs the merged function). A `_write_column` call was **9.5 µs** on a list stand-in and **24 µs** when the body wrote a real `NeoPixel`. A per-cell callback was **4.9 µs** above the inlined conditional. A `xy_to_index` call was **5.9 µs** per pixel above `lut[x_base + y]`.
- **Act.** A docstring may say "saves one method call" and may cite those microseconds with the board and date. Apply the 2026-11-16 compounding rule in § On-device bytecode timings: a local, low-risk rewrite of about 1% of a frame is worth taking. A once-per-frame merge of about 9 µs (0.5% of one `show()`) is already that kind of edit when it does not duplicate a body. Inlining `_write_column` is not: the call is 6.1% of one `show()`, and the edit copies the body at every site.

**Status:** `evidence-supported` for "no inlining" (source read, `10.0.x` branch; 10.3.0 tag not re-read) and for the 2026-11-16 call times on this one board.

### On-device bytecode timings (BPI-Bit-S2, CP 10.3.0, 2026-11-16)

**Platform limit.** One board: BPI-Bit-S2, ESP32-S2, UID `0740D10F1BE9`, CircuitPython 10.3.0 built 2026-08-31, 25 onboard WS2812, brightness 0.02. These numbers are for that platform. They are not a measurement of RP2040, RP2350, or any other firmware. Repeat recipe, compiler, and raw CSV: exp16 `ai-notes/2026-11-16_perf-benchmark/EXPERIMENT.md` (gitignored; if absent, the table below is the record). Verdicts for the display library: `RESULTS.md` in that same folder.

**How a number was taken.** `mpy-cross` 10.3.0 bytecode, header `43 06 00 1f`, no `-march`. `time.monotonic_ns` step on this board was **30504 ns** (one 32768 Hz tick). `gc.collect()` before every sample. Per-call µs = (work loop − empty `while` loop) / n. Seven rounds, median. Samples aimed at 250 ms. The figure still includes one outer Python call; paired deltas cancel that when both functions have the same shape. `show()` was timed alone.

**Anchor.** `NeoPixel.show()` of 25 pixels: **1954 µs** (min 1949). One empty `while` step 1.94 µs. One list store 18.7 µs. One `monotonic_ns()` call 21.1 µs. One `NeoPixel` store 40.2 µs. `NeoPixel.fill` of 25: 69.6 µs.

**Yardstick (Alex, 2026-11-16).** State every cost in µs and as a fraction of one `show()` of 25 pixels (1954 µs), the base cost every frame pays anyway. Icon/pattern frames were tried as a yardstick and dropped. Fractions in the table below are of that `show()`. The same figures, with hardware and firmware named, sit in the code as the maintainer note on performance numbers at the top of exp16 `lib/display/core.py` (after the module docstring); the cost notes there say "benchmarked". Update both places if a run is repeated.

**Deltas that clear the noise**, as a fraction of that 1954 µs `show()`:

| What | Delta | Fraction of one `show()` |
|---|---|---|
| Single pattern scan vs `Image` + window render, list, x=0 mono | scan faster by 1559 µs. NeoPixel: 1916 µs. x=2 and dict color match this shape | 80% list, 98% NeoPixel |
| `"".join(raw.split())` vs space/tab/CR `replace`, 4 short rows | join slower by 422 µs. Design-time codec. `join` still strips every whitespace class | 22% |
| `xy_to_index` call vs `lut[x_base + y]`, 25 pixels | call slower by 148 µs (5.9 µs/pixel) | 7.6% |
| Per-cell function vs inlined conditional, 25 cells | call slower by 122 µs (4.9 µs/cell) | 6.2% |
| `_write_column` call vs inlined body, 5 columns | +48 µs on a list (9.5 µs/call), +119 µs on NeoPixel (24 µs/call) | 2.4%, 6.1% |
| `min`/`max` clamp vs two compares | `min`/`max` slower by 91 µs per clamp | 4.7% |
| New `x` scanner vs pre-change scanner, x=0 | new slower by 83 µs | 4.3% |
| Early column-count exit vs full count, long text, limit 5 | early faster by 63 µs. Short text under the limit: tie (39 vs 41 µs) | 3.2% |
| Ring `%` vs two loops | modulo slower by 44 µs/frame | 2.2% |
| Three column loops vs the pre-change single loop, x=0 | three loops slower by 25 µs list, 41 µs NeoPixel | 1.3%, 2.1% |
| `isinstance` vs `type(x) is int` | `isinstance` slower by 25 µs | 1.3% |
| `min` vs one compare | `min` slower by 27 µs | 1.4% |
| Second Python call around the token swap | +9.4 µs | 0.5% |
| Per-column multiply vs `x_base += HEIGHT` | multiply slower by 14–16 µs/frame | under 1% |
| Fresh 25-byte LUT vs in-place fill | fresh +18 µs and 48 bytes temporary, 0 bytes retained after `gc.collect` | 0.9% |

**Ties (do not cite a winner).** `const` vs a plain module int over 25 adds (83.4 vs 83.2 µs). Local `OFF` vs global `OFF` on a 25-pixel frame (3.7 µs). `while` margin loops vs `for` (24 µs at x=0, inside that run's spread; tie at x=2). Three loops vs one loop with a per-column branch at x=0 (0.4 µs). `.mpy` function vs the same source `exec`'d on device (0.4 µs). Import time of a `.py` file was not measured.

**Heap, one call, then `gc.collect`.** `Image` construction: 720 bytes temporary for a mono pattern, 976 for a dict pattern, 0 retained. The scan's own allocation was not measured; the raw CSV repeats the Image figures on the scan row.

**Decision rule (Alex, 2026-11-16).** A hot-path saving of about 1% of one `show()` (1954 µs) or of one full frame (icon 2733 µs, pattern scan 3552 µs) is worth taking when the edit is a local rewrite, low risk, and adds very little code. Ten such edits are about 10%. A tie, inside the run's median-to-min spread, is not a saving. Copying a helper into every call site, or narrowing which characters count as whitespace, fails that test even when the percent is larger. Open this section before editing an exp16 display hot path.

**Act for this display library.** The fast local forms are already in the source: compares instead of `min`/`max`, running add instead of a per-column multiply, `type(x) is int`, the merged offset check, the in-place LUT, the early column count, the two ring loops, the inlined index, the pattern scan, and the duplicated cell loops. They stay, including the ones near 1%. Do not inline `_write_column` (6.1% of one `show()`; the edit copies the body). Do not split out an `x == 0` scanner to win back 83 µs (4.3% of one `show()`). Do not switch `while`/`for` (a tie). Correct the `bitmap_codec` sentence that calls `join` overhead negligible; keep `join` because it strips every whitespace class. No algorithm was changed from this run. Comments only (2026-11-16 later): the stale "speed gain is unmeasured" and "builtin call costs more" notes in `core.py`, and "Join only adds negligible overhead" in `bitmap_codec.py` (measured +422 µs for four rows), now cite these numbers.

**Status:** `evidence-supported` for this board and this firmware on 2026-11-16. `[domain:circuitpython-runtime]` `[project:circuitpython-exp16-planetx]`.

### Import-time vs. hot-path allocation

"Allocate large items early while memory space is relatively wide open" [Adafruit-learn, "Reducing memory fragmentation", 2026-04-20]. Allocating, e.g., 48 `Image` wrapper objects at import time produces one burst on a still-contiguous heap. Allocating them lazily scatters small blocks between later runtime allocations and is the textbook path to fragmentation. As a minor but often-believed myth: `from foo import bar` does NOT save RAM versus `import foo` — the whole module is loaded either way [Adafruit-learn, "Optimizing memory use: Importing Libraries", 2026-04-20].

### Applies to this project (exp14)

- **Ring-buffer scroll (Phase 2.5)**: current `show_string` does `scroll_buf = padding + buf + padding` — three `bytearray` allocations plus two concatenations per call. The plan's 3×WIDTH ring with a glyph-column feeder replaces that with one instance-level `bytearray` filled via slice assignment; Design Guide's preallocation recommendation directly supports this. `_pixels.show()` at the end of each frame does not allocate.
- **`build_lut` in-place (Phase 3.3)**: currently returns a fresh 64-byte `bytearray` and rotation does `_LUT[:] = build_lut(degrees)` — one transient 64-byte block per rotation. Add `build_lut(dest, rotation)` that writes into the existing `_LUT`. The block is small, but its lifecycle (short-lived inside a rotation call) is the worst-case shape for fragmentation.
- **Parser dedup (Phase 2.1)**: keep parser helpers at module scope (their bytecode and any `_`-prefixed `const()` values sit in one location); avoid instantiating parser classes inside render methods.
- **Icons-as-Images (Phase 2.2)**: materializing 48 `Image` wrappers at import is the right shape per the "large items early" guidance; the bulk `ICONS` / `ARROWS` bytes remain allocated once at import as they are now.
- **`color=WHITE` default (P1.2, done)**: immutable tuples go in the signature — no per-call remap, no `None` sentinel. Separate from fragmentation but same family of allocation-hygiene directives.

### Known gaps

- **Keypad scan context on non-ESP32 ports** (`unverified`): on ESP32-S2 the scan runs in the ESP-IDF timer service and can preempt the VM between any two statements (§ Keypad scan vs `EventQueue.clear`). RP2040 / RP2350 and other ports are assumed to call `supervisor_tick` → `keypad_tick` from a timer tick too, so the same "no `await` needed" conclusion should hold. Not checked in their `ports/*/supervisor/port.c`. Matters for comments in portable `buttons.py` that name the mechanism.

- **`memoryview` slicing zero-copy guarantees on CPy 10.x**: inferred from shared `py/objarray.c` between MPy and CPy, not re-verified against CPy sources this pass. Close with an on-device `gc.mem_free()` delta: before/after `mv[a:b]` inside a tight loop.
- **Native `adafruit_pixelbuf` C allocation** — closed 2026-09-29 against 10.3.0 `shared-module/adafruit_pixelbuf/PixelBuf.c`. Init buffer and the brightness buffer are one-shot; `show()` reuses the transmit buffer; `get_pixel` allocates a tuple every call. The earlier gap named `shared-module/_pixelbuf/PixelBuf.c`, which 10.3.0 no longer has.
- **YD-RP2040 free-heap baseline at clean boot**: "~192 KB to Python" is a working assumption from the project brief, not sourced. Measure once with `import gc; gc.collect(); gc.mem_free()` at `code.py` entry and record as `[on-device-experiment]`.
- **`bytes + bytes` vs. `bytearray` slice-assignment cost**: the principle is Design Guide–supported, but no CPy source quantifies the difference. Close opportunistically with on-device benchmarks if ring-buffer frame rate surfaces it as a bottleneck.

## Verification Queue (runtime / memory)

<!-- Items recorded as `unverified` that matter enough to confirm on code before promotion. FIFO is fine; no strict priority. -->

| Item | Why it matters | Pointer | Added |
|------|----------------|---------|-------|
| `memoryview` slicing zero-copy on CPy 10.x | Ring-buffer perf claim depends on this; currently `[inferred]` from shared MPy source | `gc.mem_free()` delta before/after `mv[a:b]` in a tight loop on YD-RP2040 | 2026-04-20 |
| Native `adafruit_pixelbuf` C module allocation shape | Closed 2026-09-29: 10.3.0 `shared-module/adafruit_pixelbuf/PixelBuf.c`. One-time transmit buffer, one-time brightness buffer, `show()` reuses it, `get_pixel` allocates a tuple per read | was `shared-module/_pixelbuf/PixelBuf.c` (path gone on 10.3.0) | 2026-04-20 |
| YD-RP2040 clean-boot free heap | Anchor the "~192 KB" assumption | `gc.collect(); print(gc.mem_free())` at `code.py` entry | 2026-04-20 |

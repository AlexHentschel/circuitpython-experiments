# Concept domain: circuitpython-runtime

**Content scope**: `[domain:circuitpython-runtime]` `[family:circuitpython]` — applies across every CircuitPython project in this persona (exp09/11/13/14/15), with concrete-evidence anchors on the RP2040 port. Provenance: surfaced during the exp14 display-library refactor (`[project:circuitpython-exp14-display]`), but the knowledge is family-wide, so it lives centrally, not in a project folder (R-7 / *Don't guess an association into a deep, specific bucket*).
**Status**: `evidence-supported` for the source-tagged claims; `[inferred]` / Verification-Queue items are explicitly marked below.
**Concepts in this domain** (one `### …` section each): heap structure (RP2040 split-heap doubling) · `gc` module surface · preallocate-mutate-in-place · `memoryview` · `const()` · no native/viper · name loading (LOAD_FAST vs LOAD_GLOBAL) · `neopixel.NeoPixel` allocation · import-time vs hot-path allocation · user-facing `asyncio` vs builtin `_asyncio` · **`asyncio.sleep(0)` still yields once** · **`mpy-cross` is CircuitPython’s binary, not PyPI MicroPython** · **`__slots__` not implemented on CircuitPython**. Project-application notes + known gaps + a runtime Verification Queue follow.
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

**Applied `[project:circuitpython-exp16-planetx]`:** `lib/display/core.py::show_string()`'s fit-on-screen branch (`Display.show_string`, non-scrolling text, `loop == False`) guards the hold-duration sleep with `if interval_ms > 0: await asyncio.sleep(interval_ms * 5 / 1000)` rather than always awaiting a `0`-or-computed duration — a deliberate skip-the-call carve-out so `interval_ms == 0` returns immediately/synchronously, not a defensive no-op. Doc comment at lines 942-947 (iteratively refined 2026-09-11, Session 23 — see `projects/circuitpython-exp16-planetx/SESSION_LOG.md`).

**Extension 2026-09-13 (Session 33): a tight `while True: ... ; await asyncio.sleep(0)` loop is a genuine busy-spin on the bundle `asyncio` scheduler, not merely "yields once and moves on" — mechanism-verified against the shipped library's own source** (`Adafruit_CircuitPython_asyncio`'s `core.py`, the library that ships as this project's `lib/asyncio`, fetched 2026-09-13 from `github.com/adafruit/Adafruit_CircuitPython_asyncio/blob/main/asyncio/core.py`). `sleep_ms(t, sgen=SingletonGenerator())` sets `sgen.state = ticks_add(ticks(), max(0, t))` — for `t == 0` this is just `ticks()` (now). The scheduler's `run_until_complete` inner loop computes `dt = max(0, ticks_diff(t.ph_key, ticks()))` for the next-ready task; when `dt == 0` the `while dt > 0:` guard is false, so the scheduler's blocking-poll fallback (`_io_queue.wait_io_event(dt)`, a real `select.poll().ipoll(dt)` syscall that would otherwise let the CPU idle until timeout or I/O) is **skipped entirely** — the ready task is popped and re-run immediately. Consequence: whenever a `sleep(0)`-polling task is the *only* ready task (e.g. a button-dispatch pump while a sibling display task is itself mid-sleep between frames), the VM spins through that task's loop body as fast as it can execute bytecode, indefinitely — not "polls a bit more than needed," a genuine unbounded busy-loop. A positive interval (even a few ms) lets the scheduler's `dt > 0` path run, which reaches the real blocking poll. The generator is not allocated per call: `sgen=SingletonGenerator()` is created once as a default argument (source comment: "without allocating on the heap"). Refined 2026-09-27: `asyncio.sleep(t)` still evaluates `int(t * 1000)`, and that float multiply allocates one temporary float. The busy-spin finding is about scheduling, and that one float does not change it. See *A wakeup does not collect* below.

**Applied `[project:circuitpython-exp16-planetx]` (Session 33):** `lib/buttons.py::Buttons.run()`'s pump loop changed `await asyncio.sleep(0)` → `await asyncio.sleep(_POLL_INTERVAL_S)` with `_POLL_INTERVAL_S = 0.01` (10ms) — chosen as half of `keypad.Keys`'/`KeyMatrix`'s own default `interval=0.02` (20ms) scan-debounce parameter (`docs.circuitpython.org/en/latest/shared-bindings/keypad/`, confirmed 2026-09-13: the scan runs in the background independent of when Python calls `.get()`, so polling faster than the scan cadence cannot see new information sooner — only spins the CPU checking an EventQueue that hasn't changed yet). `EventQueue.max_events` defaults to 64 with an `overflowed` flag on discard; utterly non-viable to hit at a 10ms poll rate for manual button presses. Host pytest (160) unaffected — the existing dispatch tests only rely on one `run()` tick happening before its first internal sleep, not on the sleep's exact duration.

**Status:** `evidence-supported` for the general yield-once claim (async/await mechanism, cross-runtime); `[project]` lines are mechanically verified against this project's own source + the bundle library's own upstream source + first-party `keypad` docs.

**One `sleep(0)`, 2026-09-27:** a single `await asyncio.sleep(0)` is one scheduler lap (`dt == 0`, no blocking poll), not the busy-spin. The spin is a loop of those laps while this task is the only one due. Calling an `async def` allocates a coroutine instance every call (CircuitPython 10.3.0 `py/objgenerator.c`). `sleep_ms` does not allocate its generator: asyncio 3.1.1 reuses one `SingletonGenerator` default argument. `asyncio.sleep(t)` is `sleep_ms(int(t * 1000))`, so the float multiply still creates one temporary float object per call. Detail: exp16 `ai-notes/2026-09-27_handler-await-cost/NOTES.md` (coroutine) and `ai-notes/2026-09-27_scroll-sleep-chunking/NOTES.md` (the float). Byte sizes not measured on device.

**`≤ 0` is an immediate yield when awaited, 2026-09-27:** bundle `sleep_ms` does `ticks_add(ticks(), max(0, t))`, so a negative millisecond count is the same deadline as 0 (now). The pairing heap (`extmod/modasyncio.c` on 10.3.0, and the Python fallback `asyncio/task.py`) orders by that deadline, so `peek` sees a due task and `run_until_complete` leaves the `while dt > 0` loop without `wait_io_event`. The await still suspends for one lap. Tasks whose deadlines are still in the future stay queued. `sleep(seconds)` truncates with `int(t * 1000)`, so `(0, 0.001)` also becomes `sleep_ms(0)`. CPython 3.13 `asyncio.sleep` (`Lib/asyncio/tasks.py`) takes `delay <= 0` to a bare `yield` (`__sleep0`); a positive sub-millisecond delay there is a real timer. `_sleep_pollable`'s `total_s <= 0: return` does not await, so it is not this path.

**Applied 2026-09-28 `[project:circuitpython-exp16-planetx]`:** `await Display.pause(0)` and `await Display.show_icon(..., interval_ms=0)` take that no-await return. On CPython, a sibling task created before those two awaits had not run until a later real `asyncio.sleep(0)`. A loop of them never reaches the button pump. `show_string` / `scroll_image` with `interval_ms=0` do `await asyncio.sleep(0)` per column (host probe: 30 sleeps for `"HELLO"`), which is the busy-spin when that task is the only one due. Detail: exp16 `ai-notes/2026-09-28_display-buttons-audit/02-scheduling.md` (gitignored). Not run on UID `0740D10F1BE9`.

### A wakeup does not collect

CircuitPython 10.3.0 compiles out allocation-threshold collection (`MICROPY_GC_ALLOC_THRESHOLD (0)` in `py/circuitpy_mpconfig.h`, re-read on the 10.3.0 tag 2026-09-27). The collector runs when an allocation cannot be satisfied, or on `gc.collect()`. It does not move live objects (`MICROPY_GC_SPLIT_HEAP` / `_AUTO` are on in that same header; fragmentation behavior is the heap-structure concept above).

`asyncio.sleep` parks the task until a ticks deadline. The scheduler waits in `select.poll` `ipoll`. The same header sets `MICROPY_INTERNAL_EVENT_HOOK` to `background_callback_run_all()` — USB, keypad scan, and similar — not `gc_collect`. PR #10379 (merged 2025-09-24) says that hook is serviced on the order of once per millisecond inside select. The poll C file was not re-read on 2026-09-27; the macro on the 10.3.0 tag was.

Waking a coroutine every 50 ms to check a flag therefore does not reclaim or compact. Dead objects from the previous turn stay until a later allocation fails or something calls `gc.collect()`. Extra wakeups that go through `asyncio.sleep(float)` or `time.monotonic()` add temporary floats (see the sleep paragraph above).

`time.monotonic()` (CP 10.3.0 `shared-bindings/time/__init__.c`) reads `common_hal_time_monotonic_ms()` → `supervisor_ticks_ms64()` → `port_get_raw_ticks`, then `mp_obj_new_float` (`py/objfloat.c` allocates one `mp_obj_float_t` per call). The tick read is the same shape on both ports: ESP32-S2 `esp_timer_get_time()`, RP2350 `time_us_64()`, each scaled by `* 512 / 15625` (`ports/{espressif,raspberrypi}/supervisor/port.c`). RP2350 is built `-mfloat-abi=softfp` with the M33 VFP helpers; ESP32-S2 has no FPU and links ROM libgcc. That float conversion is the chip difference, and it is microseconds. The heap float is the part that repeats. `supervisor.ticks_ms()` uses the same millisecond counter and returns a small int (no float). Not timed on UID `0740D10F1BE9`. Float32 millisecond resolution holds for about 2^22 ms (~1.2 h), per the `time.monotonic` docstring in that binding.

**Applied `[project:circuitpython-exp16-planetx]`:** scroll columns stay one `asyncio.sleep(interval_ms/1000)` (`Image._scroll_image`, `show_string` scroll loop). Holds already slice via `_sleep_pollable` because that wait has no next frame. Recommendation 2026-09-27, no code change: do not slice column sleeps to help the heap. Detail: exp16 `ai-notes/2026-09-27_scroll-sleep-chunking/NOTES.md` (gitignored, may vanish).

**Status:** `evidence-supported` for the control flow (10.3.0 header + asyncio 3.1.1 `core.py`). Float and coroutine sizes `unverified` on device. Select-loop cadence `unverified` beyond the PR statement and the header macro.

### `asyncio.run` from inside a running task raises

Bundle `asyncio.run(coro)` (`Adafruit_CircuitPython_asyncio` `asyncio/core.py`, `main` fetched 2026-09-27) runs the coroutine only when `cur_task is None`. Otherwise it raises `RuntimeError: asyncio.run() cannot be called from a running event loop`. A press handler called from `Button.run` / `OnboardButtons.run` is already inside the `asyncio.run(main())` that started the script, so `asyncio.run(d.show_string(...))` in that handler hits this raise. `asyncio.create_task` from that same sync handler schedules the coroutine onto the loop already running and returns immediately; the handler does not wait. `await handler()` is different: it enters `handler` immediately on the current task and runs it until `handler`'s first suspending `await`. Other tasks are selected from that suspension, not before `handler` starts. When the awaited handler returns, the same task continues into the next handler with no scheduler turn in between. Waiting for the result still requires the caller to be a coroutine. Not re-run on UID `0740D10F1BE9`. **Same module, 2026-09-28:** `_pump` awaits that handler before the next `queue.get()`. The other switch on the same `OnboardButtons` or `PlanetXButtonSensor` is the same task, so it is not serviced until the handler returns. A different module's `run()` is another task and still runs at the await. Host probe at exp16 `ai-notes/2026-09-28_display-buttons-audit/01-buttons.md`. A handler exception ends `run()`. Alex asked 2026-09-27 20:40 PDT; the await-entry order, 20:56 PDT. **`__code__.co_flags` does not identify `async def` on CircuitPython 10.3.0** (same VM on ESP32-S2, ESP32-S3, RP2040, RP2350): `py/objfun.c` sets `__code__` only for plain functions and generators, and `py/objcode.c` exposes no `co_flags`. A check of `co_flags & 0x80` returns false. The type of an `async def` object is named `coroutine` (`mp_type_coro_wrap` / `mp_type_native_coro_wrap` in `py/objgenerator.c`, assigned from `py/emitglue.c`). `type(handler).__name__ == "coroutine"` is the registration-time check on this VM. CPython uses the `co_flags` half instead, because there the function's type name is `function`. Bound methods are type `bound_method` and do not expose the wrapped function (`py/objboundmeth.c`), so that check misses them. Coroutine instances do expose `__await__` (`py/objgenerator.c`).

**Status:** `evidence-supported` for the raise (bundle source). On-device confirmation `unverified`.

### `hasattr` on a missing name does not allocate

`hasattr` (CircuitPython 10.3.0 `py/modbuiltins.c`) calls `mp_load_method_protected` (`py/runtime.c`), which calls `mp_load_method_maybe`. A missing name leaves `dest[0] == NULL`. It does not call the raising `mp_load_method`, so the usual miss does not build an `AttributeError`. `nlr_push` / `nlr_pop` still wrap the lookup. `NoneType` (`py/objnone.c`) has no attribute slot and no locals dict, so `hasattr(None, "__await__")` is that miss: a type-pointer check, then false. The name `"__await__"` is a compiled qstr. `True` / `False` are singletons. Applied: exp16 `PushButtonBase._handle` once per handler per event. Not timed on UID `0740D10F1BE9`.

**Status:** `evidence-supported` for the control flow (10.3.0 tag, read 2026-09-28). Duration `unverified`.

### `mpy-cross` is CircuitPython’s binary, not PyPI MicroPython

Host bytecode compile for a CircuitPython board must use **Adafruit’s** `mpy-cross` matching the firmware series (S3 `bin/mpy-cross/macos/`, e.g. `mpy-cross-macos-10.3.0-arm64`). Adafruit: do **not** use `pip install mpy-cross` / pypi.org — that tool is MicroPython and emits the wrong `.mpy` ([Adafruit-learn] “Creating an .mpy file”; [CPy-src] issue #10032). CP **10.3.0** emits **mpy v6.3** (binary `--version`, 2026-09-04). Installed binary, located 2026-09-27: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/mpy-cross-macos-10.3.0-arm64`. Compiling `.py` → `.mpy` catches CP-rejected syntax; it is not an on-device run.

**Status:** `evidence-supported` for the warning + 10.3.0 → v6.3 on this Mac.

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

### Import-time vs. hot-path allocation

"Allocate large items early while memory space is relatively wide open" [Adafruit-learn, "Reducing memory fragmentation", 2026-04-20]. Allocating, e.g., 48 `Image` wrapper objects at import time produces one burst on a still-contiguous heap. Allocating them lazily scatters small blocks between later runtime allocations and is the textbook path to fragmentation. As a minor but often-believed myth: `from foo import bar` does NOT save RAM versus `import foo` — the whole module is loaded either way [Adafruit-learn, "Optimizing memory use: Importing Libraries", 2026-04-20].

### Applies to this project (exp14)

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

## Verification Queue (runtime / memory)

<!-- Items recorded as `unverified` that matter enough to confirm on code before promotion. FIFO is fine; no strict priority. -->

| Item | Why it matters | Pointer | Added |
|------|----------------|---------|-------|
| `memoryview` slicing zero-copy on CPy 10.x | Ring-buffer perf claim depends on this; currently `[inferred]` from shared MPy source | `gc.mem_free()` delta before/after `mv[a:b]` in a tight loop on YD-RP2040 | 2026-04-20 |
| Native `_pixelbuf` C module allocation shape | Verify native implementation matches the pure-Python fallback (one-time `__init__` allocation, no per-`show()` allocation) | `github.com/adafruit/circuitpython` → `shared-module/_pixelbuf/PixelBuf.c` | 2026-04-20 |
| YD-RP2040 clean-boot free heap | Anchor the "~192 KB" assumption | `gc.collect(); print(gc.mem_free())` at `code.py` entry | 2026-04-20 |

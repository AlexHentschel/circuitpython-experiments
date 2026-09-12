# Concepts — Index (always read at session start)

One line per concept across all evidenced domains. This is the retrieval skeleton (rubric §0: topic → this index → `<domain>.md#concept` → full detail, one hop). Lateral concept↔concept traversal is in `_RELATIONS.md`. Domain knowledge is reshaped from the pre-warm-reset `TECHNICAL.md` (2026-06-14). Add the index line as part of writing the concept, not as a follow-up.

**Graduation rule (D8 = (c))**: each domain starts as one `concepts/<domain>.md` with a `### <concept>` section per concept (one-hop preserved). Split a domain into a folder of per-concept files only when it grows unwieldy or a concept accumulates enough refinement-history/relations to warrant its own file (accumulate-then-split). Seed only domains with ≥1 concrete concept now — do **not** pre-create empty domains.

> **Confirmed 2026-09-08.** Retrieval/placement (this index → domain → concept; deterministic home under the placement gate) held through post-reset additions (`power`, `i2c`, `git` — 15 concepts in new domains; five projects; no recorded wrong-bucket write or no-home finding). See `universal/CHANGELOG.md § 2026-09-08`. Dedicated-root attachment (2026-07-15) is a separate settled decision — not re-opened.

## Concepts by domain

### `circuitpython-runtime.md` — `[family:circuitpython]` (RP2040-anchored), `evidence-supported`
- **Heap structure (RP2040 split-heap doubling)** — two-layer TLSF + auto-doubling Python GC heap; non-compacting ⇒ fragmentation, `MemoryError` with free bytes reported.
- **`gc` module surface** — what's present; `gc.threshold()` compiled out (docs stale); `gc.mem_free()` needs a preceding `gc.collect()`.
- **Preallocate; mutate in place** — `buf[:] = src` vs concat; `struct.pack_into`; Design-Guide preallocation.
- **`memoryview`** — zero-copy view + indexed writes; slicing zero-copy `[inferred]` (Verification Queue).
- **`const()`** — parser-folded; leading-underscore hides from globals dict.
- **No `@micropython.native` / `.viper`** — not enabled on this port; plain-Python optimizations only.
- **Name loading: LOAD_FAST vs LOAD_GLOBAL** — bind globals as function-locals in hot loops; mechanism-verified against `py/vm.c` + `py/runtime.c`.
- **`neopixel.NeoPixel` allocation** — one-time `__init__` buffer; no per-`show()` alloc (pure-Python fallback verified; native C in Verification Queue).
- **Import-time vs hot-path allocation** — allocate large items early on a contiguous heap.
- **User-facing `asyncio` vs builtin `_asyncio`** — bundle library + `adafruit_ticks` on CIRCUITPY; `_asyncio` is compiled-in helper; host CPython `asyncio` ≠ device.
- **`mpy-cross` is CircuitPython’s binary, not PyPI MicroPython** — Adafruit S3 build matching firmware; CP 10.3.0 emits mpy v6.3.

### `fonts.md` — `[domain:fonts]` `[cross-experiment]`, `evidence-supported`
- **Outline fonts unsuitable at small pixel sizes** — TTF/OTF auto-raster below ~10 px loses Latin stroke topology; use hand-designed bitmap fonts (candidates listed).
- **Glyph coordinate model (metrics y-up, raster y-down)** — why `_glyph_columns`'s `display_row = ascent - height - dy + cy` is correct; verified against `adafruit_bitmap_font/pcf.py`.
- **DAL pendolino3 row-bytes vs column-major** — MakeCode 5×5 font is five row bytes (bit4=left); Exp14 storage is one byte per column (bit0=top). MIT; notice travels.

### `power.md` — `[domain:power]` `[cross-experiment]`, `evidence-supported` (≥2 sources each, verified 2026-06-15)
- **Battery self-discharge = standby floor** — LiPo ~2–5 %/mo room temp (≈165–420 µA-equiv for 6000 mAh); temp ~doubles per +10 °C. Push standby below this floor → diminishing returns; shelf-life becomes battery-limited.
- **Standby current budgeting** — runtime≈capacity/avg current; sum quiescent contributors + self-discharge floor; anything ≪ floor is noise.
- **Power-domain isolation & powered-off protection (Ioff)** — live signal into an unpowered IC back-powers it via the pin→VDD ESD diode (~Vsig−0.4 V); fix with an Ioff switch (TMUX1511 clean; TS5A23166 fails on floating VCC) or drop the source (pull-ups on the rail that dies). Master-off ≫ dangerous vs slave-off benign. [pairs-with `i2c: back-feeding`]
- **Power gating & fail-off default** — high-power rails default OFF (active-high EN + pull-down); gate converter-EN vs load-switch; module-kill load switch; latching pushbutton switch (Pololu) = switch+latch+RVP, true-off ~0.01 µA, cold-boot wake.
- **Fuel gauge MAX17048** — voltage-based ModelGauge (no sense-R/coulomb-count/learn/accumulated-error); active 23 µA / hibernate 3 µA (auto, keeps gauging — datasheet: prefer over sleep if 4 µA OK) / sleep <1 µA (halts gauging). Cold-start best-of-16 → re-estimates SoC, so always-on is a nicety not a requirement. SDA/SCL-low sleep entry [composes-with `i2c: open-drain`].
- **COTS indicator-LED standby dominance** (heuristic) — module LEDs often dominate µA budgets; audit/disable first. Anchor: Pololu 2808 on-state ~210 µA/V, LED-dominated.

### `i2c.md` — `[domain:i2c]` `[cross-experiment]`, `evidence-supported` (≥2 authority sources each, verified 2026-06-15)
- **Open-drain / wired-AND** — devices only sink LOW or release high-Z; never drive HIGH (pull-ups make HIGH). Foundational: HIGH costs current; the only back-feed source on an I2C bus is a live pull-up. [UM10204/TI/Nexperia]
- **Ratiometric logic levels** — VIL=0.3·VDD, VIH=0.7·VDD; VOL≤0.4 V@3 mA → mixed-VDD buses need level translation.
- **Pull-up sizing** — Rp(min)=(VDD−0.4)/3 mA (~1 kΩ@3.3 V); Rp(max)=t_r/(0.8473·Cb); modes Sm/Fm/Fm+/Hs with Cb ceilings 400/400/550/400 pF. One pair per bus (parallel breakout pull-ups violate Rp(min)); MCU internal ~45 kΩ too weak.
- **7-bit addressing** — 128 slots, 16 reserved → 112 usable; collisions common → re-strap / mux (TCA9548A) / 2nd bus; 10-bit rare.
- **Clock stretching** — target holds SCL low for flow control; optional, unbounded, not all hosts support it (interop hazard).
- **Back-feeding (ESD-diode)** — bus-high forward-biases a dead device's pin→VDD diode, back-powers it to ~Vbus−0.4 V. Mitigate: pull-ups on the switched rail (free) / series-R (partial) / pulldown (float-only) / powered-off-protection "Ioff" switch (only hard guarantee; TS5A23166 fails on floating VDD).

### `git.md` — `[domain:git]` `[cross-experiment]`, `evidence-supported` (verified 2026-07-15)
- **History rewrite ≠ removal via merged-PR refs** — `filter-repo`+force-push can't touch server-side `refs/pull/*`; scrubbed file stays browsable via the merged PR + by bare SHA + across fork networks; only GitHub Support purges. Check `gh api … forks_count/network_count/visibility`.
- **Scrub-a-file-from-history recipe** — `clone --mirror` → `git filter-repo --path … --invert-paths` → `push --force --mirror`; re-sync working clones after.
- **`git rm --cached` is all-or-nothing** — aborts (removes nothing) if any pathspec is untracked; `.gitignore` doesn't untrack already-tracked files.

### `tooling.md` — `[domain:tooling]` `[cross-experiment]`, `evidence-supported` (seeded 2026-09-11)
- **Espressif 4MB CircuitPython upgrade (TinyUF2 + ROM/esptool)** — three layers (ROM / TinyUF2 ≥0.33 / CircuitPython); esptool v5 hyphenated CLI; `combined.bin` @ 0x0 wipes CIRCUITPY. BPI-Bit-S2: `BITS2BOOT`, chip **esp32s2**. 4MB-only; ≥8MB boards skip this TinyUF2 CP10 path. Tables: `tooling-4mb-partitions.md`.
- **Two similarly-named CircuitPython extensions do different jobs** — `padgettholdings.circuitpythonsync` is the real file-sync tool (commands only, no file-based board/drive config); `wmerkens.vscode-circuitpython-v2` is Pylance stubs only (its `circuitpython.*` workspace-file keys don't control sync). Don't conflate.
- **`circuitpythonsync`'s "Copy Files/Libs to Board" only works for `workspaceFolders[0]`** — not multi-root-aware (verified in its own bundled source); every other open experiment's copy command fails with a misleading "no files exist" error. Open that experiment alone to fix, no shared-file edit needed.
- **On-device restart/reload mechanisms for CircuitPython test automation** `unverified`, research banked — 4 mechanisms compared (auto-reload-on-write, `supervisor.reload()`, `supervisor.set_next_code_file()` on-device chaining, DTR/RTS hardware reset). Every file-copy write resets the board (batch syncs). `set_next_code_file()` is the most promising lead for a future autonomous multi-stage on-device test loop with zero host-triggered resets. DTR/RTS native-USB CDC-ACM reset is TRM-confirmed for ESP32-**S3**, plausible-but-unconfirmed for this board's ESP32-**S2**. Nothing implemented yet.
- **Cursor's own `.cursor/rules/` discovery is NOT gated by folder order** in multi-root workspaces (unlike the extension above) — every root is scanned independently; the real caveat is a mixed flat/subdir `.mdc` layout silently dropping a root's rules entirely (order-independent). Staff-confirmed forum evidence, not formal docs.
- **TinyUF2 4MB partition CSVs** (`tooling-4mb-partitions.md`) — dual-OTA vs no-OTA; `ffat` 960K both; `ota_0` 1408K→2816K. Stream on demand.

## Candidate domains (NOT yet seeded — no concrete concept in evidence)

Per seed-on-evidence (C7): create when the first concrete concept arrives. From the rubric (`microcontroller-multi-project-memory-guidelines.md § 3.1`): `deep-sleep` (MCU sleep modes, wake sources, `alarm`), `led-driving` (WS2812 timing, level-shifting, current), `display` (matrix render, column-major — the glyph-coordinate concept currently folded into `fonts`). `deep-sleep` is inherently cross-project — pollination pays once a 2nd project accrues content. **`tooling` seeded 2026-09-11** (first concept: Espressif 4MB TinyUF2 + esptool). Remaining unseeded tooling-ish items (schemdraw, circup, VS Code) stay in this file until they accrue their own concepts.

**Seeded since the warm reset:** `i2c` (2026-06-15), `power` (2026-06-15), `git` (2026-07-15 — first non-CircuitPython, cross-project tooling domain), `tooling` (2026-09-11). **`fuel-gauge` is NOT a separate domain** — folded into `power` (MAX17048 is power/SoC management; per-device domains stay near-empty; D8 graduation rule). **`sensors` taxonomy decision (2026-06-15):** power-*measurement* devices (fuel gauge, current/voltage monitor) live in `power`; **environmental/physical sensors** (temperature LM75A, motion, light, …) → a future **`sensors`** domain, seeded when the first concrete sensing concept arrives (none in evidence yet — LM75A is only address-known so far). A device spanning domains lives in its primary domain and is cross-referenced from the other (e.g. MAX17048 → `power`, cross-ref `i2c`). See `universal/CHANGELOG.md § 2026-06-15`.

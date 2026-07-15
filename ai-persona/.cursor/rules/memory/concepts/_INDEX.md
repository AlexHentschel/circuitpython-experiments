# Concepts — Index (always read at session start)

One line per concept across all evidenced domains. This is the retrieval skeleton (rubric §0: topic → this index → `<domain>.md#concept` → full detail, one hop). Lateral concept↔concept traversal is in `_RELATIONS.md`. Domain knowledge is reshaped from the pre-warm-reset `TECHNICAL.md` (2026-06-14). Add the index line as part of writing the concept, not as a follow-up.

**Graduation rule (D8 = (c))**: each domain starts as one `concepts/<domain>.md` with a `### <concept>` section per concept (one-hop preserved). Split a domain into a folder of per-concept files only when it grows unwieldy or a concept accumulates enough refinement-history/relations to warrant its own file (accumulate-then-split). Seed only domains with ≥1 concrete concept now — do **not** pre-create empty domains.

> **PROVISIONAL (as of 2026-06-14 warm reset).** This structure is an in-flight experiment. **Confirm** = a real domain query resolves one-hop (this index → domain → concept) with no speculative file scanning. **Refute** = a query needs scanning multiple files / speculative search, or a new finding has no deterministic home under the placement gate (`04-multi-project.mdc § Placement gate`). **Trigger** = re-evaluate after ~5 real memory additions land post-reset, or at the next maintenance session. Remove this marker once ~5 additions land with no refute signal.

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

### `fonts.md` — `[domain:fonts]` `[cross-experiment]`, `evidence-supported`
- **Outline fonts unsuitable at small pixel sizes** — TTF/OTF auto-raster below ~10 px loses Latin stroke topology; use hand-designed bitmap fonts (candidates listed).
- **Glyph coordinate model (metrics y-up, raster y-down)** — why `_glyph_columns`'s `display_row = ascent - height - dy + cy` is correct; verified against `adafruit_bitmap_font/pcf.py`.

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

## Candidate domains (NOT yet seeded — no concrete concept in evidence)

Per seed-on-evidence (C7): create when the first concrete concept arrives. From the rubric (`microcontroller-multi-project-memory-guidelines.md § 3.1`): `deep-sleep` (MCU sleep modes, wake sources, `alarm`), `led-driving` (WS2812 timing, level-shifting, current), `display` (matrix render, column-major — the glyph-coordinate concept currently folded into `fonts`), `tooling` (schemdraw, circup, VS Code config). `deep-sleep` is inherently cross-project — pollination pays once a 2nd project accrues content.

**Seeded since the warm reset:** `i2c` (2026-06-15), `power` (2026-06-15). **`fuel-gauge` is NOT a separate domain** — folded into `power` (MAX17048 is power/SoC management; per-device domains stay near-empty; D8 graduation rule). **`sensors` taxonomy decision (2026-06-15):** power-*measurement* devices (fuel gauge, current/voltage monitor) live in `power`; **environmental/physical sensors** (temperature LM75A, motion, light, …) → a future **`sensors`** domain, seeded when the first concrete sensing concept arrives (none in evidence yet — LM75A is only address-known so far). A device spanning domains lives in its primary domain and is cross-referenced from the other (e.g. MAX17048 → `power`, cross-ref `i2c`). See `universal/CHANGELOG.md § 2026-06-15`.

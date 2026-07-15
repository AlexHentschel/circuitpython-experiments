# Concept domain: power

**Content scope**: `[domain:power]` `[cross-experiment]` — battery, energy budgeting, regulation, power-domain switching/isolation, standby µA, and **power-measurement devices (fuel gauges, current/voltage monitors)**. Reusable across any battery/power project (Bamboo-Lamp now; future portable builds). Provenance: surfaced in the Bamboo-Lamp standby thread (`[project:bamboo-lamp]`, 2026-06-15) but the knowledge is power-general; lamp specifics appear only as illustration. Lives centrally (R-7).
**Status**: each `### concept` is **`evidence-supported`** unless marked — corroborated by ≥2 independent sources (battery references, vendor datasheets, app-notes), verified 2026-06-15. Design-heuristic and to-bench items are flagged inline.
**Taxonomy note (why the fuel gauge is here, not a `fuel-gauge` domain)**: power-*measurement* sensors (MAX17048 SoC, INA3221 V/I) are organized under `power` because their reusable knowledge is about energy/SoC management, and a per-device domain would be near-empty (D8 graduation rule: seed coarse, split only when unwieldy). **Environmental/physical sensors** (temperature LM75A, motion, light, …) are *not* power — they belong in a future **`sensors`** domain, to be seeded when the first concrete sensing concept arrives (none in evidence yet). A device that is *both* power and bus relevant (the MAX17048 is a fuel gauge **and** an I2C device) lives in its primary domain (`power`) and is **cross-referenced** from the other (`i2c`).
**Concepts in this domain** (one `### …` each): battery self-discharge = the standby floor · standby current budgeting · power-domain isolation & powered-off protection (Ioff) · power gating & fail-off default · fuel gauge (MAX17048, voltage-based ModelGauge + mode ladder) · COTS-module indicator-LED standby dominance.
**Related concepts** (`_RELATIONS.md`): *powered-off protection* pairs-with `i2c: back-feeding (ESD-diode)` (same mechanism, bus instantiation); *fuel gauge* composes-with `i2c: open-drain` (SDA/SCL-low sleep entry) and the lamp's standby architecture.
**Provenance / history**: created 2026-06-15 (Bamboo-Lamp session 3 follow-up; Alex approved seeding `power` and folding `fuel-gauge` in). Source-tag legend: `[Himax]`/`[Bonnen]`/`[Tycorun]`/`[EL-CELL]`/`[Szas]` = battery self-discharge references; `[MAX17048-ds]` = Analog/Maxim MAX17048-49 datasheet Rev.7 (12/2016); `[TI-SCDA015]` = TI *powered-off protection* app brief; `[TI-szza030]` = TI signal-switch fail-safe/powered-off feature guide; `[Pololu-2808]` = Pololu Mini Pushbutton Power Switch w/ RVP LV (#2808) product page (in repo uploads); `[TI-TPS22916]` = TI load-switch datasheet (figure to confirm). Cross-domain anchor: `[i2c]` = sibling `concepts/i2c.md`.

---

### Battery self-discharge = the standby floor

**Rule:** a Li-ion/LiPo cell loses charge while idle through internal parasitic reactions — **~2–5 %/month for typical LiPo at room temperature** (premium cells ~1–3 %; aged/damaged or hot cells higher). Strongly **temperature-dependent** (Arrhenius: reaction rate roughly *doubles per +10 °C*) and SoC-dependent. [Himax, Bonnen, Tycorun, EL-CELL, Szas — 5 independent; consensus band ~1–5 %/mo]

**Convert to a current floor** (the useful framing): `I_self ≈ (rate/mo × capacity) / hours_per_month`. *Example — 6000 mAh pack at 3 %/mo → 180 mAh/mo ÷ 730 h ≈ **~250 µA-equivalent continuous** (range ~165–420 µA for 2–5 %/mo).*

**Implication (load-bearing across power projects):** the self-discharge current is usually **far larger than a well-designed standby electronics load (tens of µA)**. So once standby draw is pushed *below* the self-discharge floor, further µA-shaving yields **diminishing returns** — shelf life becomes battery-limited (≈1.5–3 yr for the example), not electronics-limited. Decide standby-circuit complexity against this floor, not against zero. (Lamp: this is why the ~3 µA D-4 standby was judged "negligible.")
> Refines the digest's earlier "3–5 %/mo" to the corroborated **~2–5 %/mo** (premium 1–3 %); conclusion unchanged.

### Standby current budgeting

**Method:** `runtime ≈ usable_capacity / average_current`. Build the standby budget as a **sum of quiescent contributors** (MCU deep-sleep, always-on sensors/gauge, regulator Iq, pull-up hold current, switch leakage) **plus the self-discharge floor**, then compare — anything ≪ the floor is "in the noise." Pull-up hold current is an I2C-line item: `V/Rp` per held-low line (see `[i2c]: pull-up sizing`); idle-high open-drain lines draw ~0.

**Worked lamp example (illustration):** Pololu off-state 0.01 µA + MAX17048 hibernate 3 µA ≈ 3 µA electronics vs ~250–420 µA self-discharge ⇒ electronics ≈ 1 % of the floor. At 3 µA the pack would *notionally* last centuries; self-discharge caps it at a few years. Detail: `Bamboo-Lamp/open-discussions/Power-domain-partitioning.md §6/§11`.

### Power-domain isolation & powered-off protection (Ioff)

**Problem (general — any signal crossing a powered↔unpowered boundary):** when a live signal sits on an I/O pin of an **unpowered** IC, the pin→VDD ESD diode forward-biases and **back-powers the dead rail** to ~one diode drop (≈0.4 V) below the signal, partially powering the chip → undefined state, leakage, latch-up, and (for analog switches) the pass-FET can unintentionally turn on. [TI-SCDA015; TI-szza030] This is the power-domain framing of the same mechanism the bus sees as back-feeding — see `[i2c]: back-feeding (ESD-diode)` for the I2C-bus instantiation.

**Isolation options & part-selection criteria:**
- **Powered-off-protection ("Ioff" / fail-safe) switch/mux** — holds I/O **high-Z when its own VDD = 0 V**; the robust hardware guarantee. **Verify the spec per-part**: TI **TMUX1511**-class / **SN74CBTLV**-class have clean powered-off protection (TMUX1511 Ipoff ≈ 0.01 µA); **TS5A23166** only protects at VCC *exactly* 0 V and **back-powers on a floating VCC** (TI E2E) — unsuitable where the switched rail can float. **The switch's own VDD must be pulled firmly to GND when off** (floating switch-VDD is the #1 failure).
- **Drop the source instead of isolating:** put pull-ups / drivers on the **rail that dies with the load**, so nothing holds the line high when the domain is off — frequently **zero extra parts** and beats adding an isolator. (Two-bus / switched-rail-pull-up pattern.)
- **Master-off vs slave-off asymmetry:** back-feeding *into an MCU* (master unpowered, peripherals live) is dangerous (latch-up/brownout-boot); back-feeding *into cheap peripherals* (master live, peripherals off) is benign (re-init on wake). Prefer keeping the controller powered and switching the peripherals.

### Power gating & fail-off default

**Fail-off principle:** any high-power or hazardous rail (LED strip, boost output, motor) must default **OFF** — a reset/crash/brownout/boot-default/high-Z GPIO must leave it off. Implement with an **active-high enable + pull-down on EN** so the un-driven state is off. (Lamp precedent: 100 k pull-down on the Pololu `OFF` pin; 10 k DIN pull-down.)

**Gating choices (lowest-standby first):**
- **Gate the converter EN** to collapse the whole rail in standby (best when nothing else needs that rail) vs **gate only the load** with a high-side load switch (boost keeps running).
- **Module-kill load switch** for a whole subsystem: a low-Iq high-side switch (e.g. TI **TPS22916**, Iq ~nA-class — *figure to confirm against datasheet* [TI-TPS22916, unverified]) cuts an MCU/module entirely. Once a module dies on a load switch, downstream bus-isolation questions often dissolve (the rail drops together).
- **Latching pushbutton power switch** (e.g. `[Pololu-2808]`) = load switch + button power-latch + reverse-voltage protection in one; supports software-OFF via a logic pin (MCU can shut its own system down). Off-state ≈ 0.01 µA (true-off). Cold-boot wake (loses RAM/state) — pair with software-save-then-shutdown if state matters.

### Fuel gauge — MAX17048 (voltage-based ModelGauge + mode ladder)

**Type:** a **voltage-based** 1-cell Li+ fuel gauge using the **ModelGauge** algorithm — **no current-sense resistor, no coulomb counting, no learn cycles, and it does not accumulate error** (unlike coulomb counters); temperature compensation is done by the host MCU. SoC/voltage/rate over I2C (7-bit `0x36`). [MAX17048-ds; corroborated by 3 datasheet mirrors]

**Mode ladder (datasheet IDD):**

| Mode | Current | Gauging? | Entry / exit |
|---|---|---|---|
| Active | **23 µA** (max 40) | yes | normal |
| **Hibernate** | **3 µA** (typ; 5 max, reset-comparator-disabled) | **yes — keeps fuel-gauging (~slower updates)** | **automatic** on low charge/discharge rate; auto-exits on activity |
| Sleep | **<1 µA** | **no — halts all operations, does NOT detect self-discharge** → SoC error if cell state changes while asleep | `MODE.EnSleep=1` then SDA+SCL held low for `tSLEEP` (rising edge wakes) *or* `CONFIG.SLEEP=1` (wake = write 0; other I2C traffic does **not** wake; POR wakes) |

**Datasheet's own guidance (verbatim sense):** *"Applications which can tolerate 4 µA should use hibernate rather than sleep mode."* So for an always-on gauge that must keep tracking, **hibernate is the right mode and needs zero hardware/firmware** — sleep is only for sub-µA budgets that can accept no tracking.

**Cold-start behaviour:** on battery insertion the IC debounces with a **best-of-16-samples** initial SoC estimate. Because it's voltage-based, **losing power (true-off) and re-reading at cold boot is largely fine** — it re-estimates SoC from cell voltage rather than relying on retained accumulation. ⇒ "always-on for continuity" is a nicety (instant accurate SoC, no re-converge window), **not** a hard requirement for a voltage gauge.

**SDA/SCL-low sleep entry is an I2C-mechanism consequence** — see `[i2c]: open-drain / wired-AND` and `[i2c]: back-feeding`. A passive trick: weak pull-downs to permanent GND + bus pull-ups on a switched rail make the gauge auto-sleep when the bus rail dies and auto-wake (rising edge) when it returns. Lamp detail: `Power-domain-partitioning.md §10`.

*(Sibling power-measurement device, lighter detail: INA3221 = 3-channel high-side current/bus-voltage monitor, I2C `0x40`-`0x43`. Used for per-rail current in the lamp; full concept to be added if/when researched.)*

### COTS-module indicator-LED standby dominance (heuristic)

**Heuristic (best-practice, anchored on a datasheet example):** on commercial-off-the-shelf power/switch/regulator breakout modules, an **always-on indicator LED frequently dominates the module's standby/on-state current** and can wreck a µA budget. **Audit and disable indicator LEDs first on any µA-budget rail.** Anchor: the Pololu #2808 switch on-state is **~210 µA/V, explicitly "dominated by the indicator LED"** (~0.8 mA @3.7 V) — removing the LED drops on-state to the latch residual, turning a "true-off-only" switch into a viable µA-standby pass element. [Pololu-2808]

---

## Known gaps / verification queue (power)

| Item | Status | Note |
|---|---|---|
| TPS22916 (or chosen module-kill load switch) Iq | unverified | "~nA-class" cited from memory; confirm against the specific part's datasheet before relying on it for the standby budget. |
| Pololu #2808 on-state with LED removed | to-bench | Datasheet only gives the LED-dominated figure; the latch/driver residual is unquantified — measure (Bamboo-Lamp Q12). |
| INA3221 detailed behaviour (averaging, conversion-time, shunt config, quiescent) | unverified | Only address known; promote to a full concept here when researched. |
| MAX17048 charge-while-asleep SoC error magnitude | noted | Datasheet states sleep can't detect self-discharge/charge; hibernate avoids it. Bench if charging can occur during standby (Bamboo-Lamp Q3). |

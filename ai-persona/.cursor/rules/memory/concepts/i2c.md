# Concept domain: i2c

**Content scope**: `[domain:i2c]` `[cross-experiment]` — general I2C-bus properties, reusable across every project that uses I2C (CircuitPython exp09/11/13/14/15, Bamboo-Lamp, future). Provenance: surfaced during the Bamboo-Lamp standby/power-domain thread (`[project:bamboo-lamp]`, 2026-06-15), but the knowledge here is **bus-general, not lamp-specific** — lamp context appears only as illustration. Lives centrally (R-7 / *don't bury general knowledge in a project*).
**Status**: every `### concept` below is **`evidence-supported`** — each claim is corroborated by ≥2 independent authoritative sources (the I2C specification itself plus vendor app-notes), verified 2026-06-15. Quantitative figures are spec-exact. Anything not yet corroborated is marked inline.
**Concepts in this domain** (one `### …` each): open-drain / wired-AND · ratiometric logic levels · pull-up sizing (Rp min/max, bus capacitance, speed modes) · 7-bit addressing & reserved addresses & conflict resolution · clock stretching · back-feeding an unpowered device (ESD-diode path).
**Related concepts** (`_RELATIONS.md`, edges realized 2026-06-15 when `power` was seeded): back-feeding *pairs-with* `power: power-domain isolation & powered-off protection (Ioff)` — same ESD-diode mechanism; `power` carries the general domain-boundary framing + Ioff part-selection, *this* file the I2C-bus instantiation. open-drain *composes-with* `power: fuel gauge (MAX17048)` (its SDA/SCL-low sleep entry). pull-up sizing *pairs-with* `power: standby current budgeting`. (`fuel-gauge` is folded into `power`, not its own domain — see `_INDEX.md` taxonomy note.) Intra-domain: open-drain is foundational to back-feeding and to pull-up current.
**Provenance / history**: created 2026-06-15 (Bamboo-Lamp session 3 follow-up) at Alex's request to extract *general* I2C learnings from the chat and memorize only what independent/authority sources corroborate. Source-tag legend: `[UM10204]` = NXP *I2C-bus specification and user manual* Rev.6/7 (the authority); `[TI-SLVA689]` = TI *I2C Bus Pull-Up Resistor Calculation*; `[TI-SLVA704]` = TI *Understanding the I2C Bus*; `[TI-SBAA565]` = TI *A Basic Guide to I2C*; `[TI-SCDA015]` = TI *Powered-off protection* app brief; `[Nexperia-AN90044]` = Nexperia *A study of I2C with examples*; `[Microchip]` = Microchip *External Pull-up Resistor Selection*; `[Sofics]` = Sofics *3 problems with diode-based ESD protection*; `[Broadcom-PLX]` = Broadcom PCIe/I2C level-shifting design note; `[i2c-bus.org]` = i2c-bus.org addressing reference; `[TXS0102-ds]` = TI TXS0102 datasheet Rev.L; `[TCA9517A-ds]` = TI TCA9517A datasheet Rev.E (+ onsemi PCA9517A / TI TCA9617A); `[PCA9306-ds]` = TI PCA9306 datasheet Rev.O; `[TI-E2E-PCA9306]` = TI E2E interface-forum thread on PCA9306 single-side power-down isolation.

---

### Open-drain / wired-AND (the foundational property)

**Rule:** every I2C SDA/SCL output stage is **open-drain** (an N-FET to GND) — a device can only **pull the line LOW (sink)** or **release it (high-Z)**. **No compliant I2C device may drive a line HIGH.** The HIGH level is produced *solely* by the external pull-up resistor(s) to VDD; bus-free ⇒ both lines HIGH. Because outputs only pull low and tie together, the bus voltage is the logical-AND of all outputs ("wired-AND"), so simultaneous drive can never short rail-to-ground — multiple devices coexist without destructive contention. [UM10204 §3.1.1; TI-SLVA704 §1.1; TI-SBAA565; Nexperia-AN90044 — 4 independent]

**Why it matters (the lever almost everything else hangs off):**
- **HIGH costs current** through the pull-up; LOW is "free." Idle-high bus draws nothing; held-low draws VDD/Rp per line.
- **Back-feed corollary (see the back-feeding concept):** since no device *sources* current onto the bus, the **only** way an unpowered device gets back-powered through SDA/SCL is a **pull-up tied to a still-live rail** (or a non-compliant push-pull driver). Kill the live pull-up and the bus cannot energize a dead device.
- **Arbitration & clock-stretching** both exploit wired-AND (a device pulls low, everyone sees low).
- Single-master SCL *may* be push-pull if no device clock-stretches [UM10204 §3.1.1] — an exception, not the norm.

### Ratiometric logic levels (0.3 / 0.7 × VDD)

**Rule:** I2C input thresholds are **ratiometric to VDD**, not fixed: **VIL = 0.3·VDD, VIH = 0.7·VDD** for all modern devices. (Legacy fixed levels VIL=1.5 V / VIH=3.0 V exist but new devices require the 30 %/70 % rule.) LOW output VOL ≤ 0.4 V at 3 mA sink (VDD > 2 V). [UM10204 §3.1.2; TI-SBAA565 Table 6-2 — independent]

**Implications:** mixed-VDD devices on one bus need **level translation** when their HIGH/LOW windows don't overlap (e.g. 1.8 V ↔ 3.3 V ↔ 5 V) — a translator (PCA9306) or a mux that limits pass voltage (TCA9548A) bridges domains; see the addressing concept. (A translator's *isolation-when-unpowered* behaviour is a separate axis — see the back-feeding concept's isolation-device taxonomy; PCA9306 notably does **not** auto-isolate on single-side power-down.) The ratiometric VOL is also why pull-up sizing is VDD-dependent (next).

### Pull-up sizing: Rp(min), Rp(max), bus capacitance, speed modes

**Rule — Rp lives in a window** `Rp(min) < Rp < Rp(max)` [UM10204; TI-SLVA689; Nexperia-AN90044; Microchip — 4 independent, formulae identical]:
- **Rp(min) = (VDD − VOL(max)) / IOL(max)**, with IOL = 3 mA, VOL(max) = 0.4 V (Std/Fast). Too-small Rp ⇒ FET can't pull a valid LOW. *At 3.3 V → (3.3−0.4)/0.003 ≈ **966 Ω ≈ 1 kΩ** floor.* (At 5 V → ~1.53 kΩ.)
- **Rp(max) = t_r / (0.8473 · Cb)** (the 0.8473 = time to slew 30 %→70 % of an RC step). Too-large Rp ⇒ line can't rise to VIH within the mode's rise-time budget. *At 3.3 V, Standard (t_r 1000 ns): ≈ **11.8 kΩ @100 pF**, **5.9 kΩ @200 pF**, **2.95 kΩ @400 pF**. Fast (300 ns): ≈ 885 Ω @400 pF.*

**Speed modes & capacitance ceilings** [UM10204; Nexperia-AN90044 Table 1; TI-SLVA689 Table 1]:

| Mode | Max clock | Max t_r | Max Cb |
|---|---|---|---|
| Standard (Sm) | 100 kHz | 1000 ns | 400 pF |
| Fast (Fm) | 400 kHz | 300 ns | 400 pF |
| Fast-mode Plus (Fm+) | 1 MHz | 120 ns | 550 pF |
| High-speed (Hs) | 3.4 MHz | — (active pull-up) | 400 pF |

**Implications (general, and the source of a common hobby bug):**
- **Bus capacitance is a hard budget** — total Cb (pins + traces + cable) caps Rp(max) and the device count. Exceed it → use a bus buffer/Fm+ parts/lower speed.
- **One pull-up pair per bus.** Breakout modules each ship ~2.2–10 kΩ onboard pull-ups; **N modules in parallel divide the effective Rp** (e.g. 8×10 kΩ ≈ 1.25 kΩ) → can drop below Rp(min): over-stiff bus, wasted held-low current, harsh edges. Fix: remove/disable the breakout pull-ups and keep **one ~4.7 kΩ pair** (good for 100 kHz; scope-verify before 400 kHz at high node counts).
- **MCU internal pull-ups (~tens of kΩ, e.g. ESP32 ≈ 45 kΩ) are too weak to be bus pull-ups** — they violate Rp(max) at any real Cb (line won't rise in time); use them only for "don't float" intent, not signalling.
- **Sizing tradeoff (within the window):** smaller Rp → faster edges + better noise margin, but more held-low current and stiffer drive; larger Rp → lower power, but slower / sooner Cb-limited. Pick per the power-vs-speed balance for the bus's actual Cb and clock. [TI-SLVA689]

### 7-bit addressing, reserved addresses, conflict resolution

**Rule:** classic I2C uses a **7-bit target address** (sent MSB-first, followed by the R/W bit). 2⁷ = 128 slots, but **16 are reserved** (two blocks `0000 XXX` and `1111 XXX`: general-call `0000000`, START byte, CBUS, Hs-mode master code, 10-bit prefix `11110XX`, etc.) → **112 usable** addresses. A **10-bit** extension exists (prefix `11110`) but is rarely supported. [i2c-bus.org; Nexperia-AN90044; TI-SBAA565 Table 5-1; UM10204 §3.1.12–3.1.13 — 4 independent]

**Implications:** many parts have **fixed or few-option addresses**, so two identical devices (or two parts sharing a default) **collide** — a frequent real-world constraint (e.g. in the lamp the ANO encoder's seesaw default `0x49` collided with an LM75A at `0x49`). Resolutions, cheapest first: (1) **address-strap pins** (re-strap one device); (2) an **I2C mux/switch** (TCA9548A — fans one upstream pair to 8 channels, selects one at a time; explicitly built to "resolve I2C address conflicts such as multiple identical temperature sensors") which *also* gives per-channel voltage translation; (3) a second bus on the host. [TI TCA9548A datasheet]

### Clock stretching

**Rule:** a **target** may hold **SCL low after a clock pulse** (typically during/after the ACK) to force the controller to wait until it's ready — slave-driven flow control, riding the wired-AND of SCL. Duration is unbounded by the protocol (a stuck-low SCL ⇒ bus hang unless a timeout fires). It is **optional**; many simple targets don't implement it, and **some controllers/host adapters don't support it** — a real interop hazard. [TI-SBAA565 §6.2; Total Phase; Prodigy; corroborated multiple]

**Implication:** if a sensor needs internal processing time, confirm the host (and any bit-bang/secondary bus) honours stretching; otherwise reads corrupt or the bus locks. Distinct from multi-master *arbitration* (SDA contention to pick a winner) though both rely on open-drain.

### Back-feeding an unpowered device through SDA/SCL (ESD-diode path)

**Rule:** every IC pin typically has an **ESD protection diode from the pin to its VDD** ("diode-up"). If the pin sees a voltage **above its own (dead) VDD**, that diode **forward-biases** and conducts current **into the unpowered device's VDD rail** — "back-feeding" / "phantom power." The dead rail floats up to ~**one diode drop (≈0.4 V) below the bus voltage**, partially powering the chip → undefined state, raised standby current, possible bus-hang/latch-up, and (for analog switches) the FET can unintentionally turn on and pass signals into the dead domain. [TI-SCDA015; Sofics; Broadcom-PLX — 3 independent, all I2C-specific]

**The I2C-specific bound (this is the reusable insight):** combine with open-drain — **no compliant I2C device can source current onto the bus**, so on an I2C bus the *only* back-feed source is a **pull-up (or non-compliant push-pull driver) tied to a still-live rail**. Therefore back-feed into an unpowered device reduces to one question: **is a live pull-up holding its SDA/SCL high?** Sofics states it starkly: *"It is not possible to include a diode from SDA or SCL pads to VDD unless all connected devices remain powered and use the same supply voltage."*

**Design corollary (which side to keep powered):** prefer powering the **controller** and switching off the **peripherals** — back-feeding *into cheap peripherals* is benign (undefined state, re-init on wake), whereas back-feeding *into an unpowered MCU* risks latch-up / brownout-boot. See `power: power-domain isolation` for the full master-off-vs-slave-off asymmetry.

**General mitigations (cheapest → most robust)** [TI-SCDA015; Broadcom-PLX; UM10204-consistent]:
1. **Put the pull-ups on the rail that dies with the devices** (switched-domain pull-ups) — when that domain powers off, nothing holds the lines high ⇒ no forward-bias ⇒ no back-feed, **zero extra parts**. (Pairs with making the host's pins high-Z, no internal pull, in sleep.)
2. **Series resistor** on each line — *limits* back-feed current, doesn't eliminate it; weak with many devices.
3. **A weak pull-DOWN to permanent GND** only wins against a *floating/high-Z* line; it **cannot** defeat a live pull-up (a 1 MΩ pulldown vs a 45 kΩ pull-up leaves the line at ~3.16 V — still forward-biasing the diode). A pulldown strong enough to win (≤ ~10 kΩ) would corrupt active signalling. So a pulldown is float-insurance only.
4. **Powered-off-protection ("Ioff") bus switch/mux** — a switch that holds its I/O **high-Z when its own VDD = 0 V** (e.g. TI TMUX-class, SN74CBTLV-class). This is the **only hardware guarantee** against an arbitrary held-high line / firmware mistake. Caveat: not all switches have it — some (e.g. TS5A23166-class) only protect when VDD is *exactly* 0 V and **back-power on a floating VDD**; verify the part's powered-off-protection spec and ensure the switch's own VDD is firmly pulled to GND when off.

**Isolation-device taxonomy — which parts *auto-isolate* when one side loses power** (the feature is "powered-off high-Z / Ioff / VCC-isolation"; a level *translator* is only a back-feed fix if it has it). Verified 2026-06-15 against datasheets [TXS0102-ds; TCA9517A-ds; PCA9306-ds; TI-E2E-PCA9306]:
- **Charged-buffer translator, open-drain/I2C-specific — TXS0102** *(recommended level-shifter option)*: "if **either** VCC = 0 V, **all** I/Os high-Z" + Ioff backflow protection; **µA-class** (ICCA ~2.4 µA, ICCB ~3–12 µA). Has internal 10 kΩ pull-ups (die with each rail — matches mitigation #1). Constraints: VCCA ≤ VCCB, OE pulled to GND for high-Z through power transitions.
- **Active level-shifting buffer/repeater — TCA9517A / PCA9617A / PCA9517A**: I/Os over-voltage-tolerant to 5.5 V **even unpowered** ("powered-off high-Z"), and they isolate bus capacitance. But **~1–5 mA when powered** (measured, TCA9517A) ⇒ **unusable on an always-on µA rail**; only viable powered from the *switched* rail (off in standby, then its powered-off-high-Z protects). Adds a ~0.5 V buffered-low static offset (can't cascade with other offset buffers).
- **Passive MOSFET translator — PCA9306 / LSF0102 — does NOT auto-isolate on single-side power-down** (the trap): in the standard wiring (EN←VREF2 via 200 kΩ), if the **high side stays powered** and the **low side dies**, EN stays high (held ~VREF1+0.7 V through the pass FET) so the switch stays partially on and **the dead side floats to ~1.1 V** (back-fed). TI: *"the only way to reliably isolate is to pull EN low"* — requires a live GPIO, which is dead in our standby. So PCA9306 is not a back-power fix here.
- **Digital isolator — ISO1540/41** (galvanic): no shared power/ground ⇒ no back-feed path, but **needs power on *both* sides** to pass signals + draws mA ⇒ useless when the off-domain is the one that's unpowered. Overkill for this.

*Tool-choice note:* for a **same-voltage** bus (no translation needed), the pure-isolation job is done more cheaply/lower-leakage by a dedicated Ioff switch (#4, TMUX1511 ~0.01 µA) — and better still by pull-up placement (#1, free). A powered-off-high-Z translator (TXS0102) earns its place only when a **real** level-translation need coexists (e.g. a 5 V I2C part on a 3.3 V bus); then pick it *over* PCA9306 precisely because PCA9306 won't auto-isolate.

**What does NOT work — power-path "ideal diode" modules (LM74610/XL74610-class):** these are **power-rail** reverse-polarity/OR-ing devices, not signal devices. They cannot sit on bidirectional open-drain SDA/SCL (would break the wired-AND), and they do nothing about the **ESD-diode leakage on signal pins** — the actual back-feed path. Not a back-power fix for I2C signals.

**Lamp illustration (context only):** in Bamboo-Lamp standby, the always-on MAX17048 fuel gauge shares I2C with a powered-down MCU; putting the gauge's pull-ups on the MCU's *switched* rail means they die in standby, so the dead MCU sees no live pull-up → no back-feed, no isolator needed. Detail: `Bamboo-Lamp/open-discussions/Power-domain-partitioning.md §5/§7/§8`.

---

## Known gaps / verification queue (i2c)

| Item | Status | Note |
|---|---|---|
| Exact ESD-diode topology varies by IC | partial | The "diode-up to VDD" model is the common case (CMOS dual-diode) [Sofics]; some pins have only clamps to GND or rail-to-rail structures. Back-feed risk is per-device — check the target's abs-max "voltage on pin vs VDD" spec rather than assuming. |
| Per-part powered-off-protection | per-device | "Supports I2C" ≠ "has powered-off protection." Confirm from the specific switch/translator datasheet (TMUX1511/154E, TXS0102, TCA9517A list it explicitly; PCA9306/LSF0102 do **not** auto-isolate on single-side power-down; TS5A23166 does not behave on floating VDD). |
| Power-path ideal-diode module for signal-line back-feed | verified — does NOT work | LM74610/XL74610-class are power-rail OR-ing/reverse-polarity parts; cannot sit on bidirectional open-drain SDA/SCL and don't touch signal-pin ESD-diode leakage. Not an I2C back-power fix. |

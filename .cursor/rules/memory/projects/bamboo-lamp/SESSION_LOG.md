# Bamboo-Lamp — Session Log

Scope: Bamboo-Lamp session insights, decisions, and open questions ONLY. Routing → `CONTEXT.md` (this folder). Behavioral directives go to the shared `../../universal/{WORKING_STYLE,CODING_PRINCIPLES}.md`. Migrated into central unified memory at the 2026-06-14 warm reset from `Bamboo-Lamp/memory/SESSION_LOG.md` (per-session entries preserved verbatim for provenance; living summary updated to post-reset state).

## Current State (living summary)

**Project**: Bamboo-Lamp — 1S LiPo (~6000 mAh) bamboo ambient lamp; WS2812B ×120 matrix on a 5 V boost rail (DFR0446/MP2636), gated by a hardware-control MCU; I2C monitoring (MAX17048 fuel gauge, INA3221 current/voltage, 3× LM75A temp); hardware storage mode via Pololu pushbutton power switch + 2P2T latching switch + NPN sense.

**Active thread (2026-06-14)**: about to discuss `open-discussions/Standby-sleep-mode.md` — standby/sleep strategy (Option A always-on low-power controller vs Option B hard-off). See `CONTEXT.md § Resumption point`. **MCU divergence to resolve**: `AI-Notes.md` assumes XIAO ESP32-S3; `Standby-sleep-mode.md` argues ESP32-C6 (~14–15 µA board-level deep sleep). Tracked in `CONCLUSIONS.md § Disputed`.

**Memory architecture (RESOLVED 2026-06-14 by warm reset)**: the earlier "open structural decision" — where shared behavioral memory should live so standalone Bamboo-Lamp work can reach it — was resolved by running option (c): the formal **`warm reset`** converted the CircuitPython flat `memory/` into the unified multi-project layout and folded Bamboo-Lamp in as `[project:bamboo-lamp]` / family `bamboo-lamp`. High-level Bamboo-Lamp memory now lives centrally (here); technical artifacts stay in-repo and are linked; a `Bamboo-Lamp/.cursor/rules` symlink gives standalone reachability (pending Alex's standalone-open verification — `CONTEXT.md § R-6`).

## Sessions

<!-- Format:
## YYYY-MM-DD: Session N — Bamboo-Lamp
- Context:
- Technical insights / decisions:
- Artifacts created/updated:
- Open questions:
-->

## 2026-06-15: Session 2 — Bamboo-Lamp (power-domain partitioning / I2C isolation / fail-off)

- Context: discussing `open-discussions/Standby-sleep-mode.md` sub-thread — I2C switched-domain isolation /
  back-powering, MAX17048 placement, fail-off rail. Running digest: `open-discussions/Power-domain-partitioning.md`.
- I2C inventory finalized (8 devices on bus): MAX17048 `0x36`, INA3221 `0x40`, 3× LM75A `0x48/49/4A`,
  MCP23017 `0x20`, SSD1306 OLED `0x3C`, **Adafruit ANO encoder (seesaw) `0x49`**. Two new parts added to
  `AI-Notes.md` (MCP23017, OLED, ANO). **Address collision**: ANO default `0x49` == LM75A #2 → re-strap ANO
  to `0x4B`/`0x51` (evidence: Adafruit ANO-to-I2C learn guide, web-confirmed).
- Decisions (Alex, design authority on intent): **D-1** MAX17048 permanently powered, battery-direct (D0,
  always-on); **D-2** all other I2C off in standby (D1 switched: INA3221, LM75A×3, OLED, encoder, MCP23017
  likely); **D-3** wake = single dedicated momentary button on a C6 GPIO read in deep sleep (encoder NOT the
  wake source). Commits the build to **Option A** (always-on low-power controller); Option B off the table.
  Working MCU assumption now **ESP32-C6** (leans the disputed S3-vs-C6 toward C6; not yet formally closed —
  AI-Notes/diagrams still assume S3).
- Leaning (hardware): one I2C pull-up pair on D0 only + remove D1 onboard pull-ups; isolate the 7-device D1
  branch with a low-leakage CMOS analog-switch I2C isolator (TS3A4751-class, µA/nA off-leak), enable tied to
  the D1 load-switch — kills both back-power paths (pull-up + ESD-diode) in standby. Series-R is the budget fallback.
- Open: §3 fail-off topology (gate boost EN vs strip only) — needs D1's 3.3 V source + DFR0446 EN access;
  MCP23017 role (Q1); isolator-vs-series-R (Q2); charge-during-sleep? (Q3); ANO address re-strap (Q7);
  C6 deep-sleep pin-alarm verification (Q8). All tracked in the digest's Open-questions list.

## 2026-06-15: Session 3 — Bamboo-Lamp (standby architecture pivot → full-disconnect true-off)

- Context: continued the standby thread. Topics: I2C open-drain implications (§7), Ioff switch choice for hard-off
  (§8), Alex's Pololu #2808 pushbutton power switch (§9), MAX17048 always-on + auto-sleep idea (§10), then a
  consolidated synthesis + favoured-approach decision (§11). Digest now §§1–11, Q1–Q16.
- Evidence-supported findings (datasheets/TI E2E, all web-confirmed this session):
  - **I2C open-drain (NXP UM10204 / TI SLVA704 / Nexperia AN90044)**: devices only sink/release, never source →
    the *only* back-feed source is a pull-up on a live rail. Bounds the whole back-feed problem; refutes the
    "active-driven-pin pushes mA" path for compliant parts. Pull-up sizing: Rp(min)≈1 kΩ@3.3 V, Rp(max)≈5.9 kΩ@200 pF.
  - **Ioff switches**: TMUX1511 (Ipoff 0.01 µA, clean powered-off protection) preferred over **TS5A23166** (TI E2E:
    powered-off protection works ONLY at VCC exactly 0 V, back-powers on floating VCC). Switch VDD must be 0 V +
    pulled to GND.
  - **Pololu 2808**: off-state ~0.01 µA (great true-off); on-state ~210 µA/V **dominated by indicator LED**
    (~0.8 mA@3.7 V) → unfit as a µA-standby pass element *unless LED removed* (Alex is removing it). Bundles RVP +
    latching push-on/off + sw-`OFF`/`CTRL`. (Cross-project nugget logged in digest: COTS-module indicator LEDs
    dominate standby current.)
  - **MAX17048 (Analog/Maxim ds)**: sleep <1 µA but **halts all gauging** (entry: EnSleep + lines-low ≥tSLEEP
    1.75–2.5 s, or CONFIG.SLEEP; wake on SDA/SCL rising edge); **hibernate ~3 µA KEEPS gauging, automatic/load-based**;
    active ~23 µA. Voltage-based ModelGauge → re-estimates SoC at cold boot (softens D-1 "must be always-on").
- **DECISION D-4 (Alex, tentatively favoured): full-disconnect true-off standby.** Pololu cuts everything
  (C6+D1+D2) to ~0.01 µA; MAX17048 battery-direct auto-hibernates ~3 µA still tracking. Total ≈ ~3 µA ≈ ~1 % of the
  ~250–420 µA LiPo self-discharge floor (the real limit; shelf-life 1.5–3 yr). Wake = Pololu push-on → C6 cold-boot.
  **Supersedes D-3 deep-sleep pin-alarm wake**; **collapses §1/§5/§7/§8 I2C-isolation to *not needed*** (all dies
  together). Only residual isolation point: MAX17048 always-on lines vs dead C6 → gauge pull-ups on post-Pololu rail.
- Artifacts: `open-discussions/Power-domain-partitioning.md` extended §7–§11 + D-4 + Q11–Q16; `CONTEXT.md` resumption
  point rewritten to the D-4 architecture.
- Open questions (new): **Q15** software-triggered shutdown (C6 saves state → pulse Pololu `OFF`) + separate hardware
  emergency-off for hangs — design using the 2808's `ON`/`OFF`/`CTRL` (onboard button may serve as emergency-off).
  **Q16** wire MAX17048 battery-direct without blocking hibernate when the C6 rail dies (RVP tap point; pull-ups on
  post-Pololu rail; confirm load-based hibernate engages with system load gone). Plus carried: Q1 MCP23017 role, Q3
  charge-during-standby, Q11/Q12 bench currents.
- Cross-project candidates to promote at next checkpoint (logged in digest): (1) **LiPo self-discharge ~3–5 %/mo is
  the true standby floor; tens-of-µA electronics are noise beneath it**; (2) **audit/disable COTS-module indicator
  LEDs first on any µA-budget rail**. Both `[family:bamboo-lamp]→candidate power concept`.
- **Transcript-coverage audit (end of Session 3)**: crawled the full chat transcript vs the digest — coverage
  confirmed complete (§§1–11 + Q1–Q16 map 1:1 to the discussion). Closed 3 gaps in the digest: (a) §2 ↔ §10 latent
  contradiction — the "MAX17048 line-low sleep rejected (~660 µA)" rejection assumed *live* pull-ups; under D-4 the
  pull-ups die in standby so lines-low costs ~0 µA (hibernate preferred anyway) — reconciliation note added; (b)/(c)
  forward-pointer "MOOT under D-4" status banners on §1 and §5 so a cold reader doesn't mistake them for active
  recommendations (rationale kept as fallback). **Concept-graph promotion (Alex approved I2C):** seeded
  **`concepts/i2c.md`** `[domain:i2c]` `[cross-experiment]` `evidence-supported` — 6 general-I2C concepts
  (open-drain/wired-AND, ratiometric 0.3/0.7·VDD levels, pull-up sizing Rp(min/max)+modes, 7-bit addressing/
  reserved/conflict-resolution, clock stretching, back-feeding via ESD diode). Each verified this session against
  ≥2 authority sources (NXP UM10204 + TI SLVA689/SLVA704/SBAA565/SCDA015 + Nexperia AN90044 + Microchip + Sofics
  + Broadcom). Focused on *general* bus properties, not lamp usage (lamp = illustration only). Wired into
  `concepts/_INDEX.md` (i2c removed from candidate domains) + `_RELATIONS.md` (anticipated edges to future
  `power`/`fuel-gauge`). Then (Alex approved) seeded **`concepts/power.md`**
  `[domain:power]` `[cross-experiment]` `evidence-supported` — 6 concepts (self-discharge floor, standby
  budgeting, power-domain isolation & Ioff, power gating & fail-off, **fuel gauge MAX17048** voltage-based
  ModelGauge + mode ladder, COTS-LED heuristic); verified vs 5 battery refs + MAX17048 datasheet Rev.7 + TI
  SCDA015/szza030 + Pololu page. **Taxonomy (Alex-gated):** `fuel-gauge` folded into `power` (not a separate
  domain); `sensors` deferred to a future domain for environmental sensors (LM75A etc.), seeded on first
  concrete sensing concept. Self-discharge refined to ~2–5 %/mo. Full record: `universal/CHANGELOG.md
  § 2026-06-15`. Remaining candidate domains: `deep-sleep`, `led-driving`, `display`, `tooling`, `sensors`.

## 2026-06-14: Session 1 — Bamboo-Lamp (memory bootstrap + cold-AI integration)

- Context: Alex asked me to (1) refresh memory + modus operandi, (2) familiarize with the broader Bamboo-Lamp
  project, (3) integrate the cold-AI paradigm into persona, (4) prep memory for parallel work with Exp14 without
  clobbering, then wait for instructions on `open-discussions/Standby-sleep-mode.md`.
- Read: `cold-ai-paradigm.md`; Bamboo-Lamp `AI-Notes.md`, `Notes.md`, `open-discussions/Standby-sleep-mode.md`;
  CircuitPython `memory/{SESSION_LOG,WORKING_STYLE,CONCLUSIONS}.md` + `mandates/multi-project.md` + README.
- Artifacts created (in the pre-reset `Bamboo-Lamp/memory/`; high-level content since migrated to central):
  - `memory/README.md` — routing index + scope + cold-AI note.
  - `memory/SESSION_LOG.md` (this file's source).
  - `memory/CONCLUSIONS.md` — empty findings table with status tiers.
- Cross-workspace edits (additive, no restructure): CircuitPython `memory/SESSION_LOG.md` living summary gained a
  Bamboo-Lamp routing breadcrumb; `memory/WORKING_STYLE.md` gained a cold-AI write-time-gate directive + Human
  Profile calibration for Alex.
- Persona docs made durable (shared behavioral memory, logged in CircuitPython `memory/CHANGELOG.md § 2026-06-14`):
  copied `cold-ai-paradigm.md` + `flexible-plans-for-ai-execution.md` into `.cursor/rules/reference/` (the
  `~/Developed/AI/generalized-agent-learnings/` source is ephemeral). Added a `[universal]` *Flexible-plan layered
  commitment* directive. **Next**: use the flexible-plans discipline to draft the Option-B (`warm reset`) plan.
- Open questions: the structural decision (now RESOLVED — see living summary); the S3-vs-C6 MCU divergence;
  everything in `Standby-sleep-mode.md` § "Concrete tests to run next" remains pending bench work.

### Session 1 continuation — Option B (`warm reset`) planning scaffolded + handed off (2026-06-14)

- Built an iterative planning setup for Option B (converting the CircuitPython flat `memory/` to the multi-project
  layout). All artifacts live in the **CircuitPython** workspace (not here, since warm reset restructures that
  workspace's `.cursor/rules/memory/`): `/Users/alex/Development/VsCode/CircuitPython/working-docs/warm-reset-plan/`.
  - `_META.md` — planning-loop governance (cold-AI onboarding/required-reading; iteration loop with reviews
    R1 structure-fit → R2 paradigm-compliance → R3 economy; Change-Magnitude Summary convergence signal;
    diminishing-returns criterion + 5-iteration cap → 6 plans incl. `v0.0`; Post-loop close = `cp` final → `v1.0`
    + cross-notes `risk-register.md`; sub-agent strategy: composer-2.5 crawl / Opus 4.8 reason; experiment log).
  - `microcontroller-multi-project-memory-guidelines.md` — design rubric distilled from `generalized-agent-learnings`
    files 10 + 11 (one-hop concept-graph retrieval; family-as-tag; graduate sections→files; retrieval > parsimony).
  - `warm-reset-plan_v0.0.md` — initial flexible-plan draft (FIXED target/constraints/authority/exit-ramps;
    PROVISIONAL phases/criteria; OPEN decisions D1–D7).
  - `experiment-log.md` — sub-agent technique-tuning log (seeded, no dispatches yet).
- Persona additions this session (shared behavioral memory, logged in CircuitPython `memory/CHANGELOG.md § 2026-06-14`):
  cold-AI + flexible-plans reference copies in `.cursor/rules/reference/`; two `[universal]` directives in `WORKING_STYLE.md`.
- **Handoff**: the iteration loop itself will be RUN in a separate cold-AI chat (same persona/memory), per Alex's
  request, using the kickoff prompt that points at `_META.md`. Execution of the warm reset remains gated on Alex's
  exact phrase "warm reset" + go-ahead — the separate chat does PLANNING only and will surface `v1.0` + risk-register.
  **[Post-reset note]**: the plan loop produced `warm-reset-plan_v1.0.md` + `risk-register.md`; Alex triggered
  "warm reset" + go-ahead on 2026-06-14; execution is logged in the central `SESSION_LOG.md` and `universal/CHANGELOG.md`.

# Context — bamboo-lamp

**Family**: `bamboo-lamp` (own family — not CircuitPython) · **Status**: active · **Repo**: `/Users/alex/Projects/Family/Bamboo-Lamp/` (separate workspace root; co-opened with the CircuitPython workspace). **Owner**: Alex, who is the design authority on intent/requirements (electronics-domain *facts* still need independent corroboration — datasheet/bench).

## What it is (one line)

Battery-powered (1S LiPo, ~6000 mAh) bamboo ambient lamp: a WS2812B LED matrix (~120 px) on a 5 V boost rail (DFR0446 / MP2636), gated by a hardware-control MCU (XIAO ESP32-S3 vs C6 unresolved — see CONCLUSIONS), with I2C battery/current/temperature monitoring (MAX17048 fuel gauge, INA3221 current/voltage, 3× LM75A temp) and a hardware storage/standby mode (Pololu pushbutton power switch + 2P2T latching switch + NPN sense). Goal: a polished, low-standby gift device.

## Memory split (D7 / R-11 — one home, no duplicate high-level content)

- **High-level memory (migrated here, central)**: this `CONTEXT.md`, `SESSION_LOG.md`, `CONCLUSIONS.md` in this folder. The repo's former `Bamboo-Lamp/memory/` now holds only a pointer back here.
- **Technical artifacts (stay in-repo, linked — not copied)**: workspace root `/Users/alex/Projects/Family/Bamboo-Lamp/`.
  - `AI-Notes.md` — technical memory (architecture, parts table, passives, power tree, firmware thresholds, schemdraw tooling). Treat as this project's TECHNICAL reference.
  - `Notes.md`, `LED Power and Charging Design.md`, `Power Path Charger Recommendation.md`, `Power-path switching.md`, `Battery Monitoring for MCU.md`, `firmware-recommendations.md`, `debug-and-testing.md`, `optional-robustness.md` — topic design docs.
  - `open-discussions/` — active design-question docs (e.g. `Standby-sleep-mode.md`).
  - `diagrams/` — rendered subsystem SVGs/PNGs + per-diagram legends; `*.py` schemdraw generators at repo root (`system-overview.py`, `power-path.py`, `led-subsystem.py`, `monitoring-i2c.py`, `storage-mode-shutdown.py`).
- **Behavioral / coding-craft directives**: SHARED central `../../universal/{WORKING_STYLE,CODING_PRINCIPLES,MONITORING}.md` — never fork a second behavioral catalog (these are `[user]`/`[universal]`, reused across Alex's projects).

## Domain knowledge (concept candidates)

Bamboo-Lamp is the natural seed for cross-project `power`, `i2c`, `deep-sleep`, `fuel-gauge`, `led-driving` concept domains (`../../concepts/_INDEX.md § Candidate domains`). Not yet seeded — seed-on-evidence when a concrete, corroborated concept is written (most current Bamboo-Lamp facts are `unverified`, so they live in this project's `CONCLUSIONS.md` until corroborated, then promote to a concept).

## Resumption point

Active thread (2026-06-15): power-domain partitioning / I2C isolation / fail-off rail — running digest at
`open-discussions/Power-domain-partitioning.md` (now §§1–11, Open-Qs Q1–Q16; §11 = standby-design synthesis).
**TENTATIVELY FAVOURED standby = D-4 "full-disconnect true-off"** (§11): in standby the **Pololu 2808**
(Alex's confirmed part — RVP + latching button + sw-`OFF`; LED being removed) **cuts everything** (C6+D1+D2)
to ~0.01 µA, while the **MAX17048 (battery-direct, before the Pololu) free-runs in auto-hibernate ~3 µA, still
SoC-tracking**. Total standby ≈ **~3 µA ≈ ~1 % of the LiPo self-discharge floor** (~250–420 µA-equiv — the real
limit). Wake = Pololu push-on → **C6 cold-boots**. This **supersedes D-3's deep-sleep pin-alarm wake** and
**collapses §1/§5/§7/§8 I2C-isolation work to *not needed*** (all dies together); only surviving isolation point =
MAX17048's always-on lines vs the dead C6 → pull-ups on the **post-Pololu rail** (§7/§9). MAX17048 is voltage-based
ModelGauge (re-estimates SoC at cold-boot), softening D-1's always-on rationale. Working MCU still **ESP32-C6**
(disputed S3-vs-C6 not formally closed; AI-Notes/diagrams still assume S3). I2C bus = 8 devices; ANO `0x49` collides
with LM75A #2 → re-strap ANO. **Resume on the two new open points**: **Q15** sw-shutdown (C6 saves state → pulse
Pololu `OFF`) + separate emergency-off design; **Q16** wiring MAX17048 battery-direct (RVP tap) without blocking
hibernate. Then §3 fail-off topology, MCP23017 role (Q1), charge-during-standby (Q3), bench measurements (Q11/Q12).

## R-6 reachability (handoff to Alex)

The symlink `Bamboo-Lamp/.cursor/rules → <CircuitPython>/.cursor/rules` was **created + verified resolving 2026-06-14** (reaches all rule files + this digest). **Standalone-open test (R-6) PASSED 2026-06-14**: Bamboo-Lamp opened alone (CircuitPython workspace NOT attached) loaded `00`–`04` in the Rules panel and the unified `.cursor/rules/memory/` was fully reachable — Cursor follows the cross-tree symlink standalone. R-6 fully closed; the user-level-root fallback is not needed. Standalone open is a supported entry point.

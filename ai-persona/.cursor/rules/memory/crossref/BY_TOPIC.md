# Cross-project index — BY TOPIC

**Purpose**: the cross-*project* retrieval axis. Given a topic (a board, peripheral, technique, tool), find every project that has touched it — so a new project can pull prior art and so recurring topics become promotion candidates. Distinct from `concepts/_RELATIONS.md` (concept↔concept) and from `concepts/_INDEX.md` (topic→concept detail). Read this when starting work on a topic that might have prior art in another project.

**How to use**: scan for your topic → follow to the listed project folder(s) / concept file(s). When a topic appears in **2+ projects**, that is the signal to (a) seed or enrich a shared `concepts/<domain>.md`, and (b) consider a `[cross-experiment]` entry. When a *directive* recurs across projects, promote per `universal/PATTERNS.md` / the promotion ladder.

> **PROVISIONAL (2026-06-14 warm reset).** Sparse by design — only 3 projects, most cross-links anticipated not realized. Watch-for: see `concepts/_INDEX.md` header. Refute = a cross-project lookup that should have surfaced prior art but didn't because the topic wasn't indexed here.

## Topics

| Topic | Projects | Where the knowledge lives | Notes |
|-------|----------|---------------------------|-------|
| WS2812B / NeoPixel LED matrix | exp14 (8×8), exp16 (5×5 onboard), bamboo-lamp (~120px), exp11/exp13/exp09 (residue) | `concepts/circuitpython-runtime.md § neopixel allocation`; future `concepts/led-driving.md`; exp16 LUT in `projects/circuitpython-exp16-planetx/CONCLUSIONS.md` | **2+ projects ⇒ `led-driving` is the next concept domain to seed.** exp14 = render/animation; exp16 = 5×5 geometry + async; bamboo-lamp = power/current. |
| CircuitPython runtime / memory | exp14 (anchor), exp15, exp11/13 (residue) | `concepts/circuitpython-runtime.md` | Family-wide; RP2040-anchored, RP2350 (exp15) likely similar but unverified. |
| Fonts / text on pixel grids | exp14 (8×8, FreeMono failed), exp16 (5×5 MakeCode-style target) | `concepts/fonts.md` | Bitmap-vs-outline + glyph coordinate model. 5×5 MakeCode font is exp16 first-milestone. |
| Boards: ESP32-S2 / BPI-Bit-S2 | exp16 (active), exp09 (residue) | `projects/circuitpython-exp16-planetx/`; LUT in exp09 `lib/display_v0.py`; goldfinger JPEG `…/Exp16/Notes/bpi_bit_v2_goldfinger.jpg` | CP **10.3.0** matrix + `pins.c`: `_asyncio`, `keypad.Keys`, frozen `neopixel`, `board.NEOPIXEL`=GPIO18. `board.IO13`/`IO14` = GPIO36/37 = goldfinger P13/P14 (naming clash with ESP32 GPIO13/14 photoresistors = `LUM2`/`LUM1`). User `asyncio` = bundle, not firmware. On-device `help("modules")` still P8. |
| PlanetX buttons / event API | exp16, coding-tutor (sketch) | exp16 `Notes/Button_chat.md`; `CodingTutor/mini-project-scatches/button-library.md` | micro:bit-v2 ChatGPT rec (no keypad) does **not** transfer to BPI-Bit-S2. |
| Boards: RP2040 | exp14 (YD-RP2040) | `projects/circuitpython-exp14-display/CONTEXT.md`; `concepts/circuitpython-runtime.md` (heap specifics) | |
| Boards: RP2350 | exp15 (bit board) | `projects/circuitpython-exp15-microbit/CONTEXT.md` | Pin map evidence-supported via exp11. |
| Power / battery / boost rail / standby µA | bamboo-lamp (origin); applies to any battery build | **`concepts/power.md`** (seeded 2026-06-15, `evidence-supported`) — self-discharge floor, standby budgeting, power-domain isolation/Ioff, power gating & fail-off, fuel gauge, COTS-LED heuristic; project specifics → `projects/bamboo-lamp/*`, repo `AI-Notes.md`, `LED Power and Charging Design.md` | General power knowledge — pull from here before re-deriving. `fuel-gauge` folded in here (not a separate domain). |
| Fuel gauge / SoC (MAX17048) | bamboo-lamp | `concepts/power.md § fuel gauge` (primary); cross-ref `concepts/i2c.md` (it's an I2C device) | Voltage-based ModelGauge; mode ladder verified vs datasheet. |
| I2C bus (general properties) | bamboo-lamp (origin); applies family-wide | **`concepts/i2c.md`** (seeded 2026-06-15, `evidence-supported`) — open-drain, pull-up sizing, addressing, back-feeding, etc. | General bus knowledge, verified against NXP/TI/Nexperia. Reusable by any I2C project — pull from here before re-deriving. |
| I2C monitoring (fuel gauge / current / temp) | bamboo-lamp (MAX17048, INA3221, LM75A) | `projects/bamboo-lamp/*`; repo `Battery Monitoring for MCU.md`, `monitoring-i2c.py`; general bus props → `concepts/i2c.md` | Device-specific usage. Candidate `fuel-gauge` concept domain (MAX17048 mode ladder flagged in digest §10). |
| Deep sleep / standby / low-power | bamboo-lamp | repo `open-discussions/Standby-sleep-mode.md`; `projects/bamboo-lamp/CONCLUSIONS.md` (S3-vs-C6) | Candidate `deep-sleep` concept domain. |
| Diagram tooling (schemdraw) | bamboo-lamp | repo `*.py` generators + `diagrams/` | Candidate `tooling` concept domain. |
| Git history/publishing hygiene (scrub, PR-ref persistence, attribution/licensing) | coding-tutor, exp16 | `concepts/git.md` (mechanics); `universal/PATTERNS.md` (vendor-or-gitignore with sidecar); trail in `projects/coding-tutor/SESSION_LOG.md`, exp16 `Notes/bpi_bit_v2_goldfinger.jpg.license` | coding-tutor verified 2026-07-15; exp16 CC BY-SA sidecar 2026-09-04. |

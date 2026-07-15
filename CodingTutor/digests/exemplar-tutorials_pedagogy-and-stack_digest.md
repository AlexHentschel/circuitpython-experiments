# Digest — The two Isana exemplar tutorials (pedagogy + hardware stack)

**What this digest covers**: a detailed, self-contained extraction of the two completed MakeCode-era tutorials Alex
built for Alice, treated here as the reference corpus for *what good looks like* — the pedagogical techniques they
embody and the hardware/software stack they teach. It is descriptive (what the exemplars do), not prescriptive (it does
not yet design the CircuitPython tutor). Sources live outside this repo and are read-only reference:

- `/Users/alex/Development/Isana/Crash-Sensor_Mini-Challenge/` — "The Gate Guardian" feeder tutorial (`Tutorial_Complete.md`) + its `Tutorial Prompt.txt`, `PreparationalWork/*.py`, `figures/`.
- `/Users/alex/Development/Isana/LightTower-challenge/` — "Lighthouse Keeper Mode" transfer-learning tutorial (`2026-05-15_lighthouse-keeper_v1.0.md`), its `requirements_v1.0.md`, `Tutorial Prompt.txt`, `figures/`.

Provenance: written by an earlier "STEM education material creator" persona (a *document* author), NOT by the live
interactive tutor this project is building. They set the target tone, scaffolding style, and hardware vocabulary; the
new tutor must additionally do live, interactive, anti-gaming tutoring (see `../notes-learnings-insights_for_building_tutor/01_project-picture.md`).

---

## 1. The hardware / software stack the tutorials teach

| Element | Detail | Source of truth |
|---|---|---|
| Controller | BBC micro:bit V2 (Alice has two) | prompts |
| Breakout | Elecfreaks Nezha Pro breakout board, called **Nezha2** throughout | Nezha wiki |
| Motors | PlanetX **Smart Brick Motors** on interfaces **M1–M4** (red dot). "Smart" = onboard encoder, executes "rotate N degrees" itself and reports done | prompt + `Motor-Crash-Sensor-PoC-Prep0*.py` |
| Sensors / IO | PlanetX modules on IO ports **J1–J4** (yellow/red square). Digital = on/off; some analog | prompt |
| IIC/I²C | blue-sticker interfaces, two-wire bus; not used in these tutorials | prompt |
| Port ≠ interface | same RJ11 physical plug everywhere, but motor interfaces have extra driver electronics; **not interchangeable**; color-coded | prompt (educational point) |
| Pin routing | Nezha2 routes J-ports to micro:bit GPIO pins. **J3 → P14**, and on the push-button module J3 carries **two** signals: blue(C)→P13, red(D)→P14 (4-wire cable: VCC, GND, 2 signal) | LightTower §Test Rig, PoC code |
| On-board buttons | A → P5, B → P11 | LightTower table |
| Programming (exemplars) | **MakeCode Blocks** (not Python). Prompt rationale: MakeCode's micro:bit Python dialect is quirky, no proper OOP/classes, weaker help than Blocks | Crash prompt |
| Extensions | `nezha2` + `PlanetX` (`PlanetX_Basic`) added in MakeCode | both |

**Sync vs async motor commands** (a recurring teaching axis):
- Synchronous: `set M1 at X% to run clockwise N degrees` — blocks until the motor reports done (letter "D" stays lit).
- Asynchronous: `set speed of M1 and start` / `nezhaV2.start(...)` — fires and returns immediately (screen clears fast).
- Direction on the async command is encoded as the **sign of the speed** (negative % = reverse) → taught as *angular velocity* (speed + direction in one signed number). Reference-frame convention is motor-mounting-dependent → "try it and record it once."

**Sensing progression** (feeder tutorial): polling (`forever` loop asking "pressed?") → **interrupts / event bus**
(`pins.set_events(P14, EDGE)` + `control.on_event(MICROBIT_ID_IO_P14, MICROBIT_BUTTON_EVT_UP, handler)`).
Taught with the "tap on the shoulder vs. asking every 2s" analogy; handler-must-stay-short rule; `EVT_UP` vs `EVT_FALL`
polarity is a known confusable (LightTower uses `PIN_EVT_FALL` = "just pressed", the more natural one).

PoC code (`Motor-Crash-Sensor-PoC-Prep01.py` = polling; `-Prep02.py` = event-driven) is the MakeCode-Python export of
the target programs. Under the new project this all migrates to **CircuitPython** (Alex is building the Nezha2/PlanetX
CircuitPython support separately; the API does not exist yet, so exemplar block names are stack-analogues, not literal
future API).

---

## 2. Pedagogical techniques the exemplars embody (the transferable part)

### 2.1 Structure & framing
- **Renamed milestones**: "Missions" (feeder), "Watches" (lighthouse, themed as a keeper's shifts). Progress is chunked
  into small, named, sequential achievements — never a wall of steps.
- **Reader-benefit-first**: each unit opens with *what & why* before *how* ("Remember that feeder? motors aren't
  perfect… that's where sensor feedback comes in").
- **Spiral / build-on-prior**: lighthouse explicitly reuses feeder ideas (events, async) and adds exactly one new idea
  (the transition mode). Wrap-ups enumerate "N ideas you reused + 1 new".
- **High-level roadmap up front**, details deferred ("Watch I/II/III" preview), so Alice always knows what's coming.

### 2.2 The mini-challenge pattern (core device)
Small, bounded, "manageable uncertainty" tasks that require *some* independent thought but are explicitly scaffolded so
Alice is never dropped into an unguided "it doesn't work, where do I look?" hole (she lacks the fortitude for prolonged
debug-by-trial yet). Template from the prompt:
> Mini-Challenge: use X to accomplish Y. Helps: (a) make sure P & Q are done; (b) understand detail D — e.g. in command
> `<cmd>`, what changes if the sensor were on J1 instead of J3?

Told explicitly *where her own thinking is needed vs. where to follow Lego-style*. Kept sparse (don't over-use).

### 2.3 "Your turn" decision points with branch-per-answer (lighthouse, the more advanced technique)
A design question is posed, then `*Your turn. Think it through, then read on.*`, then **every plausible answer is
addressed** — the right one confirmed, the wrong ones diagnosed with the concrete failure they cause (e.g. "picked (b)?
the return gets skipped and the motor ends 240° from park"). Teaches judgment, not just the answer. Options include a
"write your own (c)" escape hatch.

### 2.4 Verification built into the flow
- **Check / Self-test** ends most sections: a concrete, quick way to confirm work is on track before carrying mistakes
  forward. Distinguishes passive **Check** (state a meaning from memory) from hands-on **Self-test** (press buttons,
  observe the LED trace).
- **Debug hints** blocks: the *usual culprits* enumerated per section, so failure resolves without open-ended flailing.
- Display-trace notation as a shared verification language (`letter → icon → LighthouseMode`).

### 2.5 Concept scaffolding
- **Decision table** (4 buttons × 3 modes = 12 cells) — some cells pre-filled, Alice fills the rest; a printed
  landscape working-sheet with tall rows for handwriting. The table *is* the program's logic, made explicit before code.
- **State vs mode vocabulary** carefully separated (mode = one variable; state = full snapshot).
- **Deliberate bug** introduced and then diagnosed (III.4 "why does mode get stuck at 2?") to teach reasoning.
- Analogies for hard concepts (interrupt = shoulder-tap; state machine = washing machine / traffic light / game
  character; transition mode = elevator "doors closing").
- Physics/CS terms introduced *only for core concepts*, on first use, then used bare (angular velocity, concurrency,
  blocking, event bus, boolean operators).

### 2.6 The requirements-sheet + reflection worksheet (lighthouse)
Page 1 states **WHAT** the tower must do (never HOW — deliberately avoids modes/state-machine/decision-table so it
doesn't preempt Alice's design). Page 2 is a reflection worksheet: Alice explains, per numbered requirement, *how her
program delivers it and why that's enough* — "saying it out loud catches a missing case before it becomes a bug." One
item worked as an example in her first-person voice; exactly one concrete block named there.

### 2.7 Transfer-learning by design
The lighthouse is explicitly "a transfer-learning task: take what you learned from the feeder and apply it to a similar
problem." This is the direct real-world instance of prime-goal (iii) generalization/transfer — and also the exact place
the anti-gaming caution bites: transfer must be *understood*, not a rename.

### 2.8 Tone rules (from prompts, consistently applied)
- Two audiences, two registers: **to Alex** — direct, analytical, concise, no affirmation-for-its-own-sake, disagree
  with justification; **to Alice (the tutorial)** — fun, human, supportive but *never* sucking-up (she detects and
  dislikes flattery). Concise, high-value sentences; explanation balanced against doing (she loses motivation on too
  much explanation, too little doing).
- No em dashes; commas/periods/parentheses instead. No AI-generated feel. Pop-culture references (Genshin Impact, Star
  Wars order 66, Lego, Pokémon) at subtlety level 3/5, each used at most once.
- Heavy use of figures; avoid long text without an image/diagram. When images can't be generated, provide prompts for
  Alex to run externally.

---

## 3. What the exemplars do NOT cover (gaps the new tutor must fill)
- They are **static documents**, authored in a slow Alex-in-the-loop iteration. The new tutor is **live & interactive**,
  reacting to Alice in real time — so the anti-social-engineering discipline (don't leak the algorithmic solution under
  incremental questioning) becomes an active, per-turn concern, not a document property.
- CircuitPython, not MakeCode Blocks. Block screenshots become code; the "quirky Python dialect" rationale no longer
  applies (that was MakeCode-Python; CircuitPython is a different, cleaner runtime).
- No explicit, ongoing measurement of the three prime skills (translate fuzzy↔algorithmic / algorithmic critique /
  transfer). The exemplars *exercise* these implicitly; the tutor must *track* them.

## Cross-references
- Project picture & persona separation: `../notes-learnings-insights_for_building_tutor/01_project-picture.md`
- Open questions & next steps: `../notes-learnings-insights_for_building_tutor/03_open-questions-todos.md`
- Persona memory digest pointer: `ai-persona` `memory/projects/coding-tutor/CONTEXT.md` § knowledge base

# TARGET Probe Pool v1 (CircuitPython ai-persona)

FRESH keys authored against the current TARGET tree (gotcha 2 — HA's keys are doubly wrong). 21 probes, stratified by **depth** (D1 always-injected → D4 deep/lateral) × **contextual-closeness** (C-near = probe vocabulary maps directly onto a file's own words; C-far = requires inference/routing).

Scoring (per HA rubric, adapted): for each probe, did the cold AI OPEN (read/glob) the expected-reach file(s)? Score REACH ∈ {hit all / hit primary / partial / miss}, plus ROUTE ∈ {directed / brute-glob / miss} to capture directness. Paired delta = candidate − prior on the same probe. **Discriminating set for the `reference/_INDEX.md` win = P19, P20, P21** (true cold-path orphans; see Measurement design below). P13–P16 are CONTROLS (already cold-reachable → expect FLAT).

Legend: **Expected-reach** = files a well-structured persona should surface. **Primary** = the single best file.

| # | Stratum | Probe (task given to cold AI) | Expected-reach (primary **bold**) |
|---|---------|-------------------------------|-----------------------------------|
| P1 | D1/C-near | "State the session-start memory read order and its authoritative source." | **04-multi-project.mdc** (M5) |
| P2 | D1/C-far | "A file path just opened matches `2026-09_Exp16_*`. Which project am I in and where do I write per-project findings?" | **projects/_INDEX.md** (M1), 04-multi-project.mdc |
| P3 | D1/C-near | "I'm about to `rm -rf` a gitignored scratch folder. What's the procedure?" | **06-destructive-operations.mdc**, memory/PERMITTED_DESTRUCTIVE_ACTIONS.md |
| P4 | D2/C-near | "Where do I record a new domain fact vs a collaboration directive vs a coding rule?" | **04-multi-project.mdc** (Placement gate), 00-memory-system.mdc, WORKING_STYLE.md, CODING_PRINCIPLES.md |
| P5 | D2/C-far | "What is Alex's line-length preference for comments and docs?" | **universal/WORKING_STYLE.md** (§ Document Authoring) |
| P6 | D3/C-near | "On RP2040 CircuitPython, why does `MemoryError` report free bytes? And how do I bind a global in a hot loop?" | **concepts/circuitpython-runtime.md**, concepts/_INDEX.md |
| P7 | D3/C-near | "How do I size I2C pull-up resistors and what's the max?" | **concepts/i2c.md**, concepts/_INDEX.md |
| P8 | D3/C-far | "How much standby current does a LiPo self-discharge floor imply, and is a MAX17048 fuel gauge worth keeping on?" | **concepts/power.md**, concepts/_INDEX.md |
| P9 | D3/C-near | "What's the Nezha V2 smart-motor I2C frame and opcode set?" | **concepts/nezha.md** |
| P10 | D3/C-far | "WS2812 output on an ESP32-S2 board — is it PIO like RP2040?" | **concepts/led-driving.md** (PIO vs RMT), concepts/_INDEX.md |
| P11 | D3/C-far | "How do I upgrade a 4MB Espressif board to CircuitPython 10, and what's the partition story?" | **concepts/tooling.md**, concepts/tooling-4mb-partitions.md |
| P12 | D4/C-near | "Resume exp16: what's the current stage and the resumption point?" | **projects/circuitpython-exp16-planetx/CONTEXT.md**, .../SESSION_LOG.md |
| P13 | D3/C-far | "What is the 'cold-AI write-time gate' and how do I apply it before persisting memory?" | **reference/cold-ai-paradigm.md** (+ WORKING_STYLE row) |
| P14 | D3/C-far | "How should I internally iterate a non-trivial plan before showing it to the human?" | **reference/plan-refinement-loop.md** (+ WORKING_STYLE row) |
| P15 | D4/C-far | "What are the known memory-system failure modes I should guard against during a restructure (F1/F8/F10)?" | **reference/06-failure-modes.md**, 00-memory-system.mdc |
| P16 | D4/C-far | "Give me the deep rationale + hypothesis-test discipline for adaptive memory structure changes." | **reference/10-adaptive-memory-structure.md** |
| P17 | D2/C-far | "Two sources disagree about a CircuitPython fact. How do I adjudicate, and can I mark it evidence-supported?" | **00-memory-system.mdc** (Evidence-Status), WORKING_STYLE.md (Contradictions have no default winner) |
| P18 | D4/C-far | "Which projects have touched third-party-license / public-repo hygiene, and what's the pattern?" | **crossref/BY_PATTERN.md**, crossref/BY_TOPIC.md, universal/PATTERNS.md |
| P19 | D4/C-far | "What higher-order, meta-level lessons has this persona recorded about its own *learning process* (not any hardware domain)?" | **reference/07-meta-learnings.md** (+ reference/_INDEX.md as the route) |
| P20 | D4/C-far | "Point me to the deep reference on human-collaboration interaction patterns/principles, beyond the injected interaction rule." | **reference/02-interaction-style.md** (+ reference/_INDEX.md as the route) |
| P21 | D4/C-far | "Is there a walkthrough of how this persona was bootstrapped for multiple projects? I want the historical multi-project bootstrap record." | **reference/11-multi-project-bootstrap.md** (+ reference/_INDEX.md as the route) |

## Measurement design — refined 2026-09-15 (cold-path enumeration, supersedes eyeballed buckets)

**Mechanical cold-path enumeration** (grep each `reference/*.md` against the 6 `.mdc` + always-read memory files `WORKING_STYLE`/`MONITORING`/`CODING_PRINCIPLES`/central `SESSION_LOG`/`projects/_INDEX`/`concepts/_INDEX`) — see `../EXPERIMENT-LOG.md § Cold-path orphan enumeration`. Result: **exactly 3 true cold-path orphans** (reachable *only* via the new index): `02-interaction-style.md`, `07-meta-learnings.md`, `11-multi-project-bootstrap.md`. Corrections vs earlier claims: `09-recursive-learning.md` is **NOT** an orphan (reachable via always-read `MONITORING.md`); `11-multi-project-bootstrap.md` **IS** an orphan (its only inbound is off-cold-path `COLLABORATOR_GUIDE.md`). This is why the critique demanded mechanical enumeration over eyeballing.

Most of P13–P16's target files are **already** cold-reachable via always-injected `.mdc § See also` or always-read `WORKING_STYLE.md` rows. So the index does **not** move them — they are **CONTROLS** (should stay FLAT; confirm no regression).

- **DISCRIMINATING set (index-only content):** **P19, P20, P21** — target the 3 true cold-path orphans. Prior tree: reachable only by brute-force glob of `reference/` (measured in iter1-prior: `auto` model globs the dir), not by directed navigation. Candidate tree: reachable by a *directed* one-hop route (always-read anchor → `reference/_INDEX.md` → target). The win is **directness/precision/robustness**, not raw reach — see `../eval/iter1-prior/ANALYSIS.md`. Requires the index itself to be cold-reachable (C2 autonomous anchors), else these stay FLAT.
- **CONTROLS (already-anchored):** P13, P14, P15, P16 — expect FLAT (regression check). **Pre-registered: FLAT on P13–P16 is the EXPECTED, correct result and is NOT a refutation of C1.**
- **HYGIENE baseline:** P1, P5 — expect FLAT.

Probe-shape discipline (HA B2): P19/P20/P21 are *state-retrieval-of-orphan-content* probes, correctly matched to the index mechanism. Prior-arm expected result: brute-glob wander (indirect). Candidate-arm expected: directed HIT via the index route.

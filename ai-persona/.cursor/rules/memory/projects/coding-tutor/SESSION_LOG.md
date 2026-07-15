# Session Log — coding-tutor

Per-project session memory for **coding-tutor** (AI programming tutor for Alice; family `education`). Behavioral/process
directives: `../../universal/`. Roster + routing: `../_INDEX.md`. Heavy technical/pedagogy detail lives in the
`CodingTutor/` repo, linked from `CONTEXT.md`.

## Sessions

## 2026-07-15: Session 14 — [coding-tutor] (project bootstrap / setup)

- Context: Alex opened a new project — develop an AI **tutor persona** (teaches student persona **Alice**) running in
  Cursor, transitioning the exemplar tutorials' stack from MakeCode Blocks → **CircuitPython** while keeping the same
  hardware (micro:bit V2 + Nezha2 + PlanetX). Explicit ask: set up the project in persona memory + compose a complete
  picture from all inputs; **do not design the tutor yet**.
- Inputs read in full: `CodingTutor/Initialization-Prompt.txt`; both exemplar prompts
  (`Isana/Crash-Sensor_Mini-Challenge/Tutorial Prompt.txt`, `Isana/LightTower-challenge/Tutorial Prompt.txt`); both
  completed exemplar tutorials (`Tutorial_Complete.md` feeder, `2026-05-15_lighthouse-keeper_v1.0.md`); lighthouse
  `requirements_v1.0.md`; PoC code `Motor-Crash-Sensor-PoC-Prep0{1,2}.py`.
- Artifacts created — **in the CodingTutor repo** (heavy detail):
  - `notes-learnings-insights_for_building_tutor/00_INDEX.md` — KB retrieval map.
  - `.../01_project-picture.md` — complete orientation (3-persona separation, Alice profile, prime goals i/ii/iii,
    tutoring contract, anti-gaming caution, stack transition, exemplars, scope boundary).
  - `.../03_open-questions-todos.md` — queued next steps + open questions Q1–Q6.
  - `digests/exemplar-tutorials_pedagogy-and-stack_digest.md` — detailed pedagogy + stack digest (short summary
    mirrored into `CONTEXT.md` § knowledge base).
- Artifacts created — **in persona memory** (high-level): this file, `CONTEXT.md`, `CONCLUSIONS.md`; roster row in
  `../_INDEX.md` (new family `education`); living-summary pointer in central `SESSION_LOG.md`.
- Key setup decisions:
  - **New project + new family `education`** (finest-grain per DN-MP-1; coarsening later is cheap). Path globs
    `CodingTutor/**` + absolute. **Isana exemplar folders are read-only reference, NOT a detection glob** (they are the
    old MakeCode tutorial work; do not route writes there).
  - M1 note: the currently-open file at session start was an Isana exemplar (matches no glob) → detection would be
    ambiguous, but Alex's explicit instruction ("set up CodingTutor") resolves it. Recorded so a future session doesn't
    mis-route.
  - Pedagogy/science-of-learning knowledge kept **project-local** (Alex's policy), not seeded into `concepts/`.
- Open (also in `CONTEXT.md` / repo `03_open-questions-todos.md`): Q1 state of Alex's CircuitPython Nezha2/PlanetX API;
  Q2 tutor deployment/isolation model; Q3 how to measure the 3 prime skills; Q4 how Alice is simulated for testing;
  Q5 image-generation in the tutor's runtime; Q6 where CircuitPython-era tasks are authored/stored.

## Open Questions

See the table in `CodingTutor/notes-learnings-insights_for_building_tutor/03_open-questions-todos.md` (Q1–Q6) — canonical.

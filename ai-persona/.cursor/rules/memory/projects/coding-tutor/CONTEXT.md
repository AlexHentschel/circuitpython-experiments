# Context — coding-tutor

**Family**: `education` · **Status**: active (setup complete; design not started) · **Repo folder** (workspace-relative to `/Users/alex/Development/VsCode/CircuitPython/`): `CodingTutor/`.

## Scope & goal

Develop an **AI tutor persona** ("the Tutor") that runs live inside Cursor and teaches a 12-year-old student persona
**Alice** to program embedded projects in **CircuitPython** on a **BBC micro:bit V2 + Elecfreaks Nezha2 breakout +
PlanetX motors/sensors** stack. The tutor optimizes and continuously tracks *how Alice thinks*, not finished programs.

**Three-persona separation (load-bearing):** *me* = the assisting persona (at `ai-persona/`) helping Alex *build* the
tutor; *the Tutor* = the artifact under development, which **must not be active in this workspace**; *Alice* = the
learner. This project is "tutor development"; I keep only high-level dev-progress memory centrally.

**Prime goals the tutor tracks:** (i) bidirectional translation between fuzzy human ideas and concrete algorithmic
representations; (ii) algorithmic thinking / critique (spotting gaps, over-simplification, unnecessary complexity);
(iii) generalization & transfer with understanding.

**Tutoring contract:** tutor may directly resolve CircuitPython errors, stack setup, IDE friction, Python-language
limits (with brief explanations); it must leave the **algorithmic solution** to Alice. Distinguish *understanding the
problem* (help freely) from *solving it once understood* (Alice's work). Two guarded failure modes: Alice
**social-engineering** the solution out incrementally, and **shallow pattern-transfer** (toy problems must not reduce to
a rename of the real task).

## Entry points (further reading — links into the CodingTutor repo, not copied here, C8)

- **Start here**: `CodingTutor/notes-learnings-insights_for_building_tutor/01_project-picture.md` — complete orientation.
- KB index: `CodingTutor/notes-learnings-insights_for_building_tutor/00_INDEX.md`.
- Open questions + next steps (Q1–Q6, queued transcript ingestion/research): `.../03_open-questions-todos.md`.
- Initialization prompt: `CodingTutor/Initialization-Prompt.txt`.
- Exemplar tutorials (external, read-only): `/Users/alex/Development/Isana/Crash-Sensor_Mini-Challenge/` (feeder "Gate Guardian") and `/Users/alex/Development/Isana/LightTower-challenge/` (lighthouse, a transfer-learning task).

## Project knowledge base (in-repo; short domain-coverage summaries for cold-AI triage)

- `CodingTutor/digests/exemplar-tutorials_pedagogy-and-stack_digest.md` — **Covers**: pedagogy techniques of the two
  exemplar tutorials (mini-challenges, "your turn" branch-per-answer decision points, Check/Self-test, Debug hints,
  decision tables, reflection worksheets, deliberate bugs, two-register tone) **and** the hardware/software stack
  (Nezha2 M/J ports, PlanetX smart motors, J3→P14 / P13 pin routing, sync vs async motor commands, polling vs
  event-bus interrupts). Read when designing pedagogy or referencing the stack.
- `CodingTutor/materials/They Talk Tech transcript.txt` — untranslated source, **pending ingestion** (next step); no
  digest yet.

## Domain knowledge

Pedagogy / science-of-learning knowledge is deliberately kept **project-local** in the CodingTutor repo (per Alex's
knowledge-source policy), not in central `concepts/`. Promote a concept to `concepts/` only if it later proves
cross-project. Hardware-stack facts overlap the `circuitpython` family but the CircuitPython Nezha2/PlanetX API does not
yet exist (Alex building it separately) — treat as target, not current.

## Resumption point

Setup done. **Next (Alex-directed, not started):** translate + ingest the *They Talk Tech* transcript → detailed digest
+ short summary here; research that professor; compile a tutor-design guidelines list; survey recent research on
tutoring early-high-school children with prior coding experience. Only then start designing the tutor. Per-session
detail: `SESSION_LOG.md`.

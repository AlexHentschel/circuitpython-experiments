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
- Central README + attribution: `CodingTutor/README.md` → `CodingTutor/REFERENCES.md` (consolidated references + per-source license/redistribution status; cite every external source from there).
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
- `CodingTutor/digests/scheiter-they-talk-tech_digest.md` — **Covers**: Katharina Scheiter (teaching-and-learning
  research, Potsdam) on AI & learning. Effort is the *feature* of learning; chatbots exploit human cognitive parsimony;
  the illusion of understanding + novice overconfidence (self-reported confidence is an unreliable progress signal);
  self-regulated learning [SRL] / metacognition (monitoring + regulation) as the linchpin; **think-first-then-AI**
  ordering; good tutors ask questions not answers, and off-the-shelf LLMs are trained-sycophantic → must be
  system-prompted away (known-hard, endless-question-loop + honest-but-polite failure modes); hybrid **LLM + rule-based
  ITS** as her architecture bet; learning-by-explaining; **programming is especially hard to teach without AI**. Read
  when grounding tutor pedagogy/behavior. Source: `materials/They Talk Tech transcript{,_EN}.txt`.
- **The synthesized high-level overview** (what to consider + research before designing the tutor):
  `CodingTutor/notes-learnings-insights_for_building_tutor/04_pre-design-considerations-and-research-agenda.md` —
  considerations A–D, research agenda E (P1: Scheiter's own tutorial-dialogue system; the "Your Brain on ChatGPT" study;
  ITS + LLM hybrids; programming-education-for-novices), open design questions F.
- `CodingTutor/materials/They Talk Tech transcript.txt` (German) + `..._EN.txt` (English translation) — ingested 2026-07-15.

## Domain knowledge

Pedagogy / science-of-learning knowledge is deliberately kept **project-local** in the CodingTutor repo (per Alex's
knowledge-source policy), not in central `concepts/`. Promote a concept to `concepts/` only if it later proves
cross-project. Hardware-stack facts overlap the `circuitpython` family but the CircuitPython Nezha2/PlanetX API does not
yet exist (Alex building it separately) — treat as target, not current.

## Attribution & publication policy (Alex requirement — high priority)

CodingTutor is published to Alex's GitHub (currently inside repo `github.com/AlexHentschel/circuitpython-experiments`,
**not** its own repo). **Proper attribution is mandatory**: every external source is cited in `CodingTutor/REFERENCES.md`
(single consolidated file, linked from `README.md`) with a per-source license/redistribution status. **Third-party
copyrighted material (papers, books, media transcripts) must not be committed** unless a permissive redistribution
license is confirmed and recorded there; downloaded papers go in git-ignored `CodingTutor/materials/papers/`.
Two open flags surfaced 2026-07-15 (see SESSION_LOG): the podcast transcript + translation are already tracked
(copyrighted → recommend `git rm --cached`), and the same repo also tracks the private `ai-persona/` memory — confirm
repo public/private + intended publication scope before pushing. These are Alex's decisions; do not untrack/rewrite
history unilaterally.

## Resumption point

Knowledge-gathering phase. **Done**: setup; ingested the Scheiter *They Talk Tech* transcript (translation + digest +
high-level pre-design overview). **Next (not started)**: research Katharina Scheiter's own work — especially her
tutorial-dialogue-system publications (top lead) — then execute the P1 research agenda in
`.../04_pre-design-considerations-and-research-agenda.md § E`, then compile a tutor-design guidelines list. Only then
begin designing the tutor. Per-session detail: `SESSION_LOG.md`.

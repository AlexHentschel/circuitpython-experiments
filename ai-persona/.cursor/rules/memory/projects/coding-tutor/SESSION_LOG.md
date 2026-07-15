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
  - **Alex ratified all three flagged setup decisions (2026-07-15)**: family `education`; Isana folders read-only-not-a-write-glob; pedagogy kept project-local. Now design ground truth, not a unilateral call.
- Open (also in `CONTEXT.md` / repo `03_open-questions-todos.md`): Q1 state of Alex's CircuitPython Nezha2/PlanetX API;
  Q2 tutor deployment/isolation model; Q3 how to measure the 3 prime skills; Q4 how Alice is simulated for testing;
  Q5 image-generation in the tutor's runtime; Q6 where CircuitPython-era tasks are authored/stored.

## 2026-07-15: Session 14 (cont.) — [coding-tutor] (knowledge gathering: Scheiter transcript ingested)

- Context: Alex opened the knowledge-gathering phase — translate `materials/They Talk Tech transcript.txt` to English,
  then ingest it into a first high-level overview of what to consider/research before designing the tutor.
- Source: German c't podcast "They Talk Tech" live w/ **Katharina Scheiter** (prof. teaching-and-learning research,
  Univ. Potsdam), "AI & education — are we unlearning how to think?". ASR-noisy German.
- Artifacts (CodingTutor repo):
  - `materials/They Talk Tech transcript_EN.txt` — faithful readable English translation (timestamps + speaker labels
    preserved; ASR artifacts cleaned, unclear spots marked).
  - `digests/scheiter-they-talk-tech_digest.md` — detailed self-contained digest (11 themed sections + implications).
  - `notes-.../04_pre-design-considerations-and-research-agenda.md` — **the headline deliverable**: considerations A–D,
    research agenda E (P1–P3), open design questions F.
- Key extracted points (all `unverified` until primary sources read; Scheiter = expert opinion in an interview):
  effort is the *feature* of learning; chatbots exploit cognitive parsimony; illusion of understanding + novice
  overconfidence → self-reported confidence is a bad progress signal (use unaided transfer probes); SRL/metacognition
  (monitoring+regulation, embedded not framework-taught) as backbone; **think-first-then-AI** ordering + reflection
  phase; good tutors ask not answer, LLMs are trained-sycophantic and must be system-prompted away (known-hard;
  endless-question-loop + honest-yet-polite failure modes) — **independent corroboration that our anti-social-engineering
  requirement is a hard research problem**; hybrid LLM+rule-based ITS as architecture bet; learning-by-explaining;
  **programming is especially hard to teach without AI** (our exact domain — first-class constraint).
- Added open questions Q7 (classify Alice-turn: understanding-the-problem vs seeking-solution) and Q8 (must-internalize
  vs fine-to-look-up concepts) to the repo register.
- Routing note: heavy content in the CodingTutor repo; only short source-coverage summary mirrored to `CONTEXT.md`
  (digest workflow). Persona-memory footprint kept minimal.

## 2026-07-15: Session 14 (cont.) — [coding-tutor] (attribution + copyright/publication hygiene)

- Context: Alex flagged that some Scheiter work is gated; he may download papers into `materials/`. Requirements:
  papers must be git-ignored (or confirmed permissively licensed before publishing to his GitHub); **attribution is a
  hard requirement** — consolidate all references in one file, linked from a central root README.
- Investigated the git boundary (evidence-supported): `CodingTutor/` is **not** its own repo — it lives inside
  `github.com/AlexHentschel/circuitpython-experiments`. CodingTutor files (incl. the transcript) are **already tracked**;
  `ai-persona/` (53 files, the private persona memory) is **also tracked in the same repo**.
- Artifacts created (CodingTutor repo):
  - `.gitignore` — ignores `materials/papers/*` (except its README), `*.pdf/epub/mobi/doc/docx`, `.DS_Store`; commented
    (not active) lines to untrack the transcript + translation once Alex decides.
  - `materials/papers/README.md` — git-ignored-folder workflow (only README tracked; force-add only after license
    confirmed).
  - `REFERENCES.md` — consolidated attribution: Scheiter podcast; research-agenda leads (Scheiter tutorial-dialogue
    system `[to locate]`, "Your Brain on ChatGPT" `[to verify]`); hardware/platform links; internal exemplars; plus a
    **licensing & redistribution commit-decision table**.
  - `README.md` (root) — central overview + KB map + licensing policy + **publication-scope caution**.
  - Pointers added to `00_INDEX.md`; policy summary added to `CONTEXT.md`.
- **Two flags surfaced to Alex (his decision; I did NOT untrack or rewrite history):** (1) transcript + EN translation
  are copyrighted third-party content already tracked → recommend `git rm --cached` + uncomment `.gitignore` lines;
  (2) confirm whether `circuitpython-experiments` is public and whether publishing `ai-persona/` memory is intended.
- `[YourBrainOnChatGPT-2025]` citation is `[to verify]` (best-guess Kosmyna et al., MIT Media Lab, arXiv) — must confirm
  before citing; do not present as established.
- **Executed (Alex-approved):** untracked the German transcript (`git rm --cached "materials/They Talk Tech transcript.txt"`,
  staged `D`, local copy kept); the EN translation was never committed. Activated the two `.gitignore` lines so both stay
  out. Gotcha recorded: `git rm --cached` aborts entirely if any pathspec is untracked (the `_EN.txt` file) — pass only
  tracked paths. **Still open**: `transcript.txt` remains in *past history*; if the repo was pushed, a history scrub
  (`git filter-repo`/BFG + force-push) is needed — Alex to confirm push state.

## Open Questions

See the table in `CodingTutor/notes-learnings-insights_for_building_tutor/03_open-questions-todos.md` (Q1–Q8) — canonical.

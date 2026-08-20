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
  tracked paths.
- **Remediation completed 2026-07-15.** Repo `circuitpython-experiments` confirmed **public + pushed**, **0 forks / 0
  network** (`gh api`). Committed the forward deletion + attribution set (`README.md`, `REFERENCES.md`, `.gitignore`,
  `materials/papers/README.md`, Scheiter digest, research agenda, memory updates) as `ffdb2d7` on `alex/display-mvp`.
  Then Alex scrubbed the transcript from **all branch history** via `git clone --mirror` + `git filter-repo --path ...
  --invert-paths` + `git push --force --mirror` (rewrote `master` 5458ef3 + `alex/display-mvp` ffdb2d7). Verified the
  file now 404s on `master`. Local branches re-synced to rewritten origin.
- **Accepted residual (Alex's call):** merged **PR #1** still pins pre-rewrite commit `107b91c` and keeps the transcript
  browsable at `/pull/1/files` (force-push cannot touch server-side `refs/pull/*`). Alex chose to **keep the PR** rather
  than file a GitHub Support purge request. Bare-SHA reachability of old commits also accepted. **Gotcha for future**:
  history rewrites do NOT remove data reachable via merged-PR refs — only GitHub Support can.
- **Decided (Alex, 2026-07-15):** keep `ai-persona/` (53 files) **public** in this repo. No credentials in it
  (`settings.toml` gitignored), Alice is a safe pseudonym → acceptable. The persona memory is intentionally public.
  Remediation thread fully closed.

## 2026-07-15: Session 15 — [coding-tutor] (research loop iteration 1: corpus assembly)

- Context: Alex asked me to run an autonomous research loop — assemble a comprehensive corpus of prior work relevant to
  building the tutor (focus Scheiter, not limited), store local copies, follow secondary leads, and produce a **ranked list
  of relevant-but-inaccessible sources** he can then fetch. Explicit balance: inspect-first / false-positives-over-false-
  negatives; broad triage vs deep analysis (deep analysis = next iteration). "then we repeat."
- Method: batched WebSearch across all agenda cells (`04...§ E` P1–P3) → triaged by abstract → batch-downloaded open-access
  PDFs via `curl` (needed `required_permissions:["full_network"]` — arXiv/Springer off the sandbox allowlist).
- Outcome: **17 PDFs** downloaded to `CodingTutor/materials/papers/` (git-ignored). Every agenda cell covered. Highlights:
  Bauer/Greiff/Graesser/Scheiter/Sailer-2025 "Looking beyond the hype" (Scheiter's own AI-effects synthesis, **CC-BY**);
  Kosmyna-2025 "Your Brain on ChatGPT" (P1.2 closed); Ruffle&Riley + Hybrid-reflection-dialogue (LLM CTS design, Q2);
  Kasneci-2026 sycophancy-as-safety (EduFrameTrap); Weintrop-2019 + CodeStruct (block→text); Fan-2024 metacognitive laziness;
  Chase-2009/Munshi-2022/Biswas-2004 (teachable agents / SRL); Kapur PF overview; Mayer&Moreno multimedia; PRIMM practitioner.
- Artifacts (repo): `notes-.../05_research-corpus_iteration-1.md` (**headline deliverable** — catalog + triage + agenda
  coverage + **ranked can't-access list § B** + secondary leads § C); updated `REFERENCES.md` (§2a downloaded / §2b ranked
  to-fetch + licensing table), `00_INDEX.md`, `03_open-questions-todos.md`.
- **Ranked can't-access list surfaced to Alex** (top 3): (1) "From Blocks to Text: Bridging Programming Misconceptions" 2024,
  JECR — our *exact* micro:bit-MakeCode→Python transition, 163 sixth-graders (TOP); (2) **Scheiter's specific LLM
  tutorial-dialogue paper — UNCONFIRMED**, not in her Potsdam pub list (candidates: in-progress; collaborator's; AutoTutor
  lineage via co-author Graesser) — needs Alex's knowledge; (3) AutoTutor-meets-LLMs / MWPTutor (L@S'24, hybrid FSM+LLM).
- All corpus claims tagged `unverified` (triage-depth only; digests next). Licensing default = ignored/not-committed;
  Bauer-2025 is CC-BY (force-add-able if Alex wants it committed).
- Routing: heavy catalog in the repo; persona memory holds only this high-level session entry + resumption pointer (C8).

## 2026-07-15: Session 15 (cont.) — [coding-tutor] (arXiv-access pass: +3 PDFs, corpus → 20)

- Context: Alex said he tried to allow-list arXiv; asked me to retry accessing previously-blocked publications.
- Finding: arXiv is still **off the Cursor *sandbox* allowlist** — a plain `curl` 403s even without elevated perms; the
  allowlist attempt did not take effect this session. Downloads still work via `required_permissions:["full_network"]`
  (unchanged from iteration 1). All arXiv items were already local, so allowlisting mainly buys arXiv *mirrors of gated
  papers*.
- Searched for arXiv/open mirrors of the gated ranked list → downloaded **3 more** (corpus now **20**):
  MWPTutor / "AutoTutor meets LLMs" (arXiv:2402.09216 — was ranked-gated #3, hybrid FSM+LLM, central Q2 evidence);
  "Towards SocratiCode" K-12 programming Socratic tutor (arXiv:2605.17857 — closest age+domain match after gated Blocks-to-Text);
  "Sakshm AI" Socratic coding tutor (arXiv:2503.12479, undergrad pop — read for guardrails, discount age findings).
- Still gated (no open mirror): Blocks-to-Text-Misconceptions + its Croatian same-lineage papers (Žanko/Mladenović/Granić);
  STAP (ACM); SSRN RCT (403 to non-browser, retried); Kapur/PRIMM/Chi primaries; Scheiter-adaptive-2025; Kruger&Dunning.
- **New high-value gated lead added to fetch-list (§B.4)**: "When Generative AI Meets Socratic Method" (JCAL, DOI
  10.1002/jcal.70210) — operationalizes the **Q7** give-answer-only-after-understanding gate (root-cause id + coherent
  solution path; LLM-judgeable). Abstract-level mechanism captured; full method needs the PDF.
- Artifacts updated (repo): `05_research-corpus_iteration-1.md` (§A rows 18-20, revised §B ranked list, §D coverage),
  `REFERENCES.md` (§2a +3 rows, §2b revised). All new claims `unverified` (triage-depth).

## 2026-08-14: Session 15 (cont.) — [coding-tutor] (standalone missing-refs file + Scheiter outreach email; two citation corrections)

- Alex asked for (1) a standalone `MISSING-REFERENCES.md` with full citations (title/authors/year/journal/DOI) and (2) a
  German draft email to Prof. Katharina Scheiter asking for non-paper resources (e.g. a GitHub of her tutoring system).
- Created `CodingTutor/MISSING-REFERENCES.md` (root, tiered: T1 exact-stack/core-design, T2 pedagogy primaries, T3 support,
  + same-lineage + secondary leads + how-to-hand-back workflow). Verified metadata via web search before writing.
- **Two citation corrections (invalidated earlier entries):**
  - Blocks-to-Text-Misconceptions authors are **Mladenović, Žanko & Zaharija (2024)**, JECR 62(5):1082-1106 — earlier
    recorded as "Žanko, Mladenović, Granić" (Granić is on the 2021 IJCCI sibling, not this one).
  - "Adaptive teaching with technology enhances lasting learning" (L&I 2025, 99:102141) is **Sibley, Fabian, … Lachner
    (Tübingen)** — **NOT a Scheiter paper**; earlier mislabeled `[Scheiter-adaptive-2025]` → now `[Sibley-adaptive-2025]`.
  - Also pinned: JCAL Socratic paper = Sun, Zheng, Xu & Yang (**2026**, 42(2):e70210); PRIMM 2017 DOI 10.1145/3137065.3137084.
  - Corrections propagated to `REFERENCES.md § 2b` and `05_research-corpus_iteration-1.md § B`. **Process note**: both errors
    came from triage-depth recording of authors from memory/abstract snippets without verifying — verify author lists before
    committing a citation to a hand-off artifact.
- Drafted the German outreach email (delivered in chat, not stored) — references the podcast, Alex's applied-CS background,
  the daughter's 4-yr Python background + micro:bit/Lego-Technic/Elecfreaks platform, the deliberate first-AI-exposure
  rationale (AI-as-technical-tool, supervised), and a friendly ask for resources incl. their tutoring-system repo.
- Index updated: `00_INDEX.md` now points at `MISSING-REFERENCES.md`.

## 2026-08-14: Session 15 (cont.) — [coding-tutor] (Scheiter email sent; process checkpoint)

- **Outreach email to Prof. Katharina Scheiter SENT** (2026-08-14). Alex finalized/sent it (chose subject with a
  podcast-forward framing rather than a work-like line; several iterations on tone → informal-but-polite German, no
  em-dashes; attached a photo of their first MakeCode project — a rabbit-treat dispenser). **Resources requested in the
  email**: any non-paper resources for building a small CircuitPython AI-tutor — specifically a public **GitHub repo /
  prompts / materials / open-source system** for the tutorial-dialogue system she mentioned in the podcast, plus pointers
  to further work / open-source systems. → Awaiting reply; capture whatever arrives into `materials/` + `REFERENCES.md`.
  If she identifies the specific system, that closes the top unconfirmed lead (`05...md § B.2` / MISSING-REFERENCES #2).
- **Open task on Alex**: obtain the gated *publications* in `CodingTutor/MISSING-REFERENCES.md` (esp. #1 Blocks-to-Text).
- **Gap surfaced (answering Alex's Q)**: `MISSING-REFERENCES.md` is **publication-only** (papers/books + the one system
  lead + secondary paper leads). Non-publication resources we *should* also be hunting are not yet tracked anywhere:
  (a) **open-source tutor code repos** we have papers for but not the code — MWPTutor (github.com/eth-lre/MWPTutor),
  Ruffle&Riley, Betty's Brain, SocratiCode, Sakshm; (b) **benchmarks/datasets** — EduFrameTrap, SYCON-Bench, SocraticMATH,
  MathDial; (c) **existing tutor products to study** — Khanmigo, Anthropic education work; (d) **prompt libraries** for
  Socratic tutoring; (e) **the CircuitPython-driver availability for the Elecfreaks Nezha2/PlanetX stack** — a technical
  resource gap tied to Q1 (exemplars used MakeCode; CircuitPython support must be confirmed). Proposed to Alex: add a
  `non-publication resources` section to MISSING-REFERENCES.md (or a sibling `RESOURCES.md`). *Not yet created — awaiting
  his go-ahead.*
- **Update (2026-08-14)**: item (e) — CircuitPython-driver availability for the Elecfreaks Nezha2/PlanetX stack — is being
  handled by Alex in a **separate workstream** (status: *in progress*). Do NOT track/pursue it inside coding-tutor's
  resource list to avoid double-tracking; it feeds Q1/Q8 when resolved.
- **Update (2026-08-15)**: Alex renamed `MISSING-REFERENCES.md` → **`MISSING-RESOURCES.md`** and asked for a non-paper
  section. Restructured the file into **Part 1 (inaccessible publications)** + **Part 2 (non-paper resources)**. Part 2
  captures the four categories with **verified links** where found: open-source tutor code (MWPTutor `eth-lre/MWPTutor`,
  Ruffle&Riley `rschmucker/ruffle-and-riley`; Betty's Brain / SocratiCode / Sakshm `[to locate]`); benchmarks/datasets
  (EduFrameTrap `KasneciLab/eduframetrap-icml2026`, SYCON-Bench `JiseungHong/SYCON-Bench`, MathDial `eth-nlped/mathdial`;
  SocraticMATH `[to locate]`); products (Khanmigo, Anthropic edu — `[to locate]`); prompt libraries (`[to locate]`); + the
  driver stack row pointing at the separate workstream. `00_INDEX.md` pointer updated to the new filename.
- **Update (2026-08-15) — all `[to locate]` items resolved** (full internet-research pass; findings in `MISSING-RESOURCES.md § Part 2`):
  - **Betty's Brain**: NO open source; free for research/classroom by emailing Prof. Gautam Biswas (gautam.biswas@vanderbilt.edu),
    site dev.teachableagents.org. It's a *science / causal-map* env, not programming → design reference only, not reusable code.
  - **SocratiCode** (arXiv:2605.17857): tutor has no code repo; **Zenodo supplement** doi:10.5281/zenodo.20018098 exists
    (materials/prompts). ⚠️ `github.com/giancarloerra/SocratiCode` is an UNRELATED MCP code-search tool (name collision) —
    do not confuse.
  - **Sakshm AI** (arXiv:2503.12479): proprietary product (sakshm.com / Disha AI), ex-MSR founders; no public repo.
  - **SocraticMATH** (Ding et al. CIKM'24): CONFIRMED `github.com/ECNU-ICALK/SocraticMath` + HF `ulises-c/SocraticMATH`
    (CC BY-NC 4.0, **non-commercial**), model HF `CogBase-USTC/SocraticLM`. Chinese primary-school math → reuse the
    review→heuristic→rectification→summarization *structure*, not content.
  - **Khanmigo**: CONFIRMED public Khan Academy blog write-ups (7-step prompt engineering; "How We Built AI Tutoring Tools";
    "Building a Better AI Tutor: Recent Learnings") — candid on guardrail metrics (answer-give-away rate, cognitive
    engagement), a separate "math agent" verifier, and prompt-length degradation. High design value.
  - **Anthropic Education Report** (Apr 2025): CONFIRMED anthropic.com/news/anthropic-education-report-how-university-students-use-claude
    — 574,740 conversations; ~47% "direct" minimal-effort (the cognitive-offloading figure, P3.10); CS students 38.6% overrepresented.
  - Net: no dead ends; every non-paper resource is now either openly available, access-by-request, supplement-only, or a
    proprietary product to study. `[to locate]` count = 0.
- **Update (2026-08-15) — outreach persisted**: created `CodingTutor/outreach/` with `scheiter-email_de.md` (**sent
  2026-08-14**) and `biswas-email_en.md` (**draft** — explicit ask for Betty's Brain runnable build / source / SRL-scaffold
  + mentor-agent design materials, for non-commercial private use; mirrors the Scheiter email + same rabbit-dispenser photo
  P.S.). Pointer added to `00_INDEX.md § Outreach`.
- **Update (2026-08-15)**: Biswas email **SENT**. Both outreach emails (Scheiter, Biswas) now sent; awaiting replies —
  capture any resources received into `materials/` + `REFERENCES.md`, and if Scheiter names the specific system that closes
  the top unconfirmed lead (`05...md § B.2` / MISSING-RESOURCES Part 1 #2).

## Open Questions

See the table in `CodingTutor/notes-learnings-insights_for_building_tutor/03_open-questions-todos.md` (Q1–Q8) — canonical.
Research-side: the specific Scheiter tutorial-dialogue paper (`05...md § B.2`); which ranked gated sources Alex can fetch.

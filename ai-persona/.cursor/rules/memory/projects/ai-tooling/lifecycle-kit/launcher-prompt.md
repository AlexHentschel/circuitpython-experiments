# TASK: Full memory-maintenance lifecycle on THIS persona (CircuitPython ai-persona)

> **Clarification note (2026-09-15).** This file was seeded from a handoff originally written for a
> *different* persona and has been rewritten so the roles are unambiguous. Two personas are involved and
> they must not be conflated:
>
> | Role | Persona | Path | Meaning for you |
> |---|---|---|---|
> | **TARGET** (the artifact you maintain) | **CircuitPython `ai-persona`** — the persona governing THIS Cursor session | `/Users/alex/Development/VsCode/CircuitPython/ai-persona` | This is **you / your own durable memory**. Its `.cursor/rules` are auto-injected into this session. You are doing **self-maintenance**. |
> | **REFERENCE** (method + experience source) | **`high-assurance-engineering` (HA)** | `/Users/alex/Git/onflow/high-assurance-engineering` | A **different** persona that has executed full memory lifecycles before and harbors the method, harness, prior-run evidence, and learnings. **Use its knowledge; do NOT assume you are it**, and do NOT inherit its rules, mission, memory, or session-start reflexes. |
>
> **Decisions confirmed by the human (2026-09-15), now settled — not provisional:**
> 1. **Operating model = live edits on the dedicated branch.** Edit the live TARGET tree on
>    `alex/ai-persona-maintanance`; commit at coarse milestones; git history + the un-merged branch are the
>    reversibility net. NOT the source handoff's deep-copy model. Never merge/adopt to main (human's call).
> 2. **Harness = try to run it.** Plan to run the cold-AI measurement harness against TARGET; request the
>    specific `~/.cursor/permissions.json` allowlist entry (§6 gotcha 1) when reaching calibration. Fall back
>    to measurement-blind mode only if the grant/SDK is unavailable.

## 0. Who you are, and what you are operating on
You are the AI persona governing this Cursor session — the **CircuitPython `ai-persona`** whose behavioral
and memory rules under `TARGET/.cursor/rules/` are auto-injected into you. The artifact you are maintaining
is **your own durable memory**. This is a self-maintenance lifecycle, analogous to how the HA persona's
prior cycle was performed by "that persona's own future self."

There is a **separate** persona — **`high-assurance-engineering` (HA)** — that has performed this kind of
full memory-maintenance lifecycle before and stores a complete method, prior-run evidence, a measurement
harness, and a prep bundle. **You must reuse that material** rather than reinventing it. But HA is NOT you:
do not assume you inherit HA's mission, domain (Solidity/Go/high-assurance smart-contract engineering),
memory contents, rule files, or session-start behaviors. When you read HA's files, read them as
**SPECIFICATIONS OF THE MAINTENANCE DISCIPLINE** you are choosing to follow — not as rules that govern you
by default. You have read/write access to the HA repo but must only **read** it for this task (treat HA as
a library; make no changes there).

> **LAUNCH-CONTEXT SELF-CHECK (do this before anything else — this prevents the 2026-09-15 collision's root cause).**
> Confirm the rules auto-injected into *this* session are the **CircuitPython persona's** (you should see
> `00-memory-system.mdc`, `04-multi-project.mdc`, the CircuitPython multi-experiment domain rules — and the
> workspace root is `/Users/alex/Development/VsCode/CircuitPython`). If instead you are governed by **HA's** rules
> (e.g. `00-persona-and-mission.mdc`, a Solidity/Go/high-assurance mission) or any non-CircuitPython persona, you
> are in the **WRONG Cursor session**: **STOP** and ask the human to relaunch this cycle in a Cursor window whose
> workspace root is the CircuitPython repo (with `ai-persona` loaded). Do **not** proceed cross-governed — an
> HA-governed agent running this CircuitPython cycle is exactly how the two cycles collided and cross-wrote.

PATHS (all relative paths below hang off these):
  - **TARGET repo (git root):** `/Users/alex/Development/VsCode/CircuitPython`  (branch: `alex/ai-persona-maintanance`)
  - **PERSONA** = `/Users/alex/Development/VsCode/CircuitPython/ai-persona/.cursor/rules`  (your live memory + rules — the artifact)
  - **WORKDIR** = `/Users/alex/Development/VsCode/CircuitPython/ai-persona/ai-notes/2026-09_CPy-full_memory_lifecycle`
    (the **only** directory you write working artifacts to; `ai-notes/` is **gitignored** — it holds your working
    notes, ledger, harness copy, and experiment log; nothing here is tracked by git). Always reference this **full
    absolute path**; do not abbreviate to the old `2026-09_full_memory_lifecycle` name. Create subdirectories when
    significantly useful.
  - **HA** = `/Users/alex/Git/onflow/high-assurance-engineering`  (the reference persona/repo — **read-only**)
  - **HA-PREP** = `HA/ai-notes/2026-09-15_memory-maintenance-cycle`  (the prep bundle written for the prior cycle)
  - **HA-PERSONA** = `HA/.cursor/rules`  (HA's rules/memory — read the method/discipline files as specs)

> **CONCURRENCY / ISOLATION (learned the hard way 2026-09-15).** A *separate*, independent maintenance cycle runs
> in parallel — the **HA persona's own** cycle, whose WORKDIR is `HA/ai-notes/2026-09_HA-full_memory_lifecycle`.
> You have **nothing** to do with that folder: never read, write, or reason about it. The two cycles previously
> collided by both writing to a shared `…/ai-notes/2026-09_full_memory_lifecycle`; this WORKDIR was renamed with
> the `CPy-` prefix to isolate them. Write **only** under your WORKDIR above. If you find artifacts here that you
> did not create (e.g. an `EXPERIMENT-LOG.md`/`harness/` from the other cycle), they are foreign strays — do not
> build on them; surface them to the human (do not delete — §2).

First action: confirm WORKDIR is clean (contains only this prompt + what you create), then set up the experiment
log + notes structure and analyze the situation there (see §3, §9).

## 1. Objective
Perform a FULL memory-maintenance lifecycle on the TARGET persona: improve structural efficiency
(discoverability > leanness ≈ relations > distillation > maintainability) while PROVABLY retaining fidelity —
measured where possible, not merely asserted. Apply everything within your authority (§8) directly on the
dedicated branch; PROPOSE-don't-enact everything beyond it. Do not merge/adopt to the main branch — that is
the human's decision.

The HA persona has done this once before, successfully. A complete method, prior-run evidence, harness, and
a prep bundle already exist in the HA repo. Reuse them. Do not reinvent.

## 2. PRIME SAFETY RAILS (highest precedence — override any momentum)
- **Operate on the dedicated branch only.** All live edits go to `TARGET` files on branch
  `alex/ai-persona-maintanance`. Git history + this un-merged branch are your reversibility net and audit
  trail (replacing the prior cycle's "deep-copy, never-edit-live" mechanism). Commit at COARSE milestones
  with descriptive messages. Do NOT merge to `main`/`master` and do NOT otherwise "adopt" the revised
  persona live — adoption = merging, which is the human's decision.
- **NON-DESTRUCTIVE in spirit.** Build ADDITIVELY (new parent/index/hub + back-links) rather than by
  destructive moves. Prefer copy/append/extend over rm/overwrite/truncate. Defer EVERY deletion to a human
  (maintain a "files/units-absent-vs-reference" proposal list at the end). Git tracking does NOT license
  deletion — honor `06-destructive-operations.mdc` and `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md`: absence of
  a matching active grant = no permission.
- **STOP AND ASK THE HUMAN** whenever ANY of these is true (this is the core of the mandate):
    (a) significant risk of KNOWLEDGE / INFORMATION LOSS;
    (b) significant risk of MISINTERPRETING or subtly TWISTING a learning (you don't fully understand what a
        unit means, why it exists, or whether a rewrite preserves it);
    (c) a change to foundational / "Level-3" meta-rules or destructive-ops rules — for THIS persona that
        means `00-memory-system.mdc`, `06-destructive-operations.mdc`, and the maintenance/epistemology
        sections of `00-memory-system.mdc` (+ the routing single-source-of-truth `04-multi-project.mdc`);
    (d) any destructive or non-trivially-reversible operation;
    (e) scope ambiguity, or a task materially larger than estimated.
- When unsure whether a unit is low-value-redundant vs load-bearing, TREAT IT AS LOAD-BEARING (keep it).
- NEVER drop "near-inviolable" content: learned behavior, human corrections/feedback, the sole instance
  grounding a directive/concept, or anything needed to re-evaluate a past decision's direction.
- Preserve the persona's self-containment + publishability properties: do NOT introduce absolute paths into
  OTHER personas' directories (in particular, do not hard-link TARGET memory to HA paths), and do NOT move
  security-sensitive / business-confidential detail into durable memory. You are reorganizing existing
  content, not reclassifying its sensitivity — if a move would change an item's sensitivity tier, that is an
  ASK (b).
  - Be PRAGMATIC about sensitivity: much information is only sensitive in *combination* (mosaic effect) —
    judge the combined disclosure a restructure would create, not each fragment in isolation.
  - Code references to PUBLIC repositories may remain — but verify the repo is actually public before keeping one.

Because you are an AI performing surgery on your own memory without the human owner's calibrated judgment,
your authority is DELIBERATELY NARROWER than the human owner's: bias hard toward ADDITIVE, MEASURED,
REVERSIBLE changes, and PROPOSE-don't-enact anything lossy or semantically risky.

## 3. Read first (in this order)
TARGET's own governing/discipline rules (these DO govern you — they are auto-injected):
1. `PERSONA/00-memory-system.mdc` (esp. § Maintenance — the danger zone; § Evidence-Status Discipline;
   § Content Hierarchy; the cold-AI paradigm) and `PERSONA/04-multi-project.mdc` (routing + session-start
   read order — the single source of truth).
2. `PERSONA/06-destructive-operations.mdc` + `PERSONA/reference/destructive-operations.md`.
3. `PERSONA/reference/10-adaptive-memory-structure.md`, `PERSONA/reference/06-failure-modes.md`,
   `PERSONA/reference/cold-ai-paradigm.md`, `PERSONA/reference/plan-refinement-loop.md`,
   `PERSONA/reference/flexible-plans-for-ai-execution.md`.
4. TARGET current-state inventory: `PERSONA/memory/**` (concepts, projects, universal, crossref, indexes).

HA REFERENCE material (read as method specs; do NOT assume HA's identity):
> **Caution — HA's live tree is being edited concurrently.** HA's *own* maintenance cycle is running in parallel and
> mutating `HA-PERSONA/*` (i.e. `HA/.cursor/rules`, incl. the `memory/…` method + rule files in items 9/11/15). Treat
> every read of a **live** HA path as a point-in-time snapshot that may shift under you. **Prefer the frozen, stable
> copies in `HA-PREP/2026-08-cycle-archive-unpacked/`** (a snapshot of the prior cycle) for method reference; fall back
> to a live `HA-PERSONA/*` read only when no frozen copy exists, and don't be surprised if it changes between reads.
5. `HA-PREP/README.md`                         — task digest, kickoff, reading order (written for the prior cycle)
6. `HA-PREP/context-collection.md`             — exhaustive annotated index of the prior run's context
7. `HA-PREP/candidate-work.md`                 — the prior backlog = a *seed* for candidate changes (candidates, NOT commands; most are HA-domain-specific — adapt, don't copy)
8. `HA-PREP/pre-flight-and-environment.md`     — environment / permissions / harness gate (see §6)
9. `HA-PERSONA/memory/concepts/authoring/memory-maintenance-cycle.md` — the promoted METHOD (settled core + extensions)
10. `HA-PREP/2026-08-cycle-archive-unpacked/spec/Full_Memory-maintanance_cycle.md` — the ORIGINAL process spec (read in full)
11. `HA-PERSONA/memory/workstreams/2026-08-memory-maintenance/LEARNINGS-AND-GUIDELINES.md` — the A–G tangible rules
12. `HA-PREP/2026-08-cycle-archive-unpacked/analysis/PROCESS-ANALYSIS-v1.md` — how the prior run actually went (§1,§5,§9,§12)
13. `HA-PREP/2026-08-cycle-archive-unpacked/plan/PLAN-v4.md` + `plan/OPEN-QUESTIONS.md` — the approved plan template + resolved decisions
14. `HA-PREP/2026-08-cycle-archive-unpacked/methodology/` — the reusable instrument: `evaluation-framework.md`,
    `run_probe.py`, `harness/probe-pool-v1.md`, `harness/scoring-rubric.md`, `harness-RESULT.md`
15. Additional HA discipline files worth mining (read as specs, map onto TARGET's analogues where they differ):
    `HA-PERSONA/14-plan-authoring.mdc` (flexible plans + end-of-planning lens-sweeps + OERC gates),
    `HA-PERSONA/05-concept-graph.mdc` (relation vocabulary + read-only relation-audit cadence),
    `HA-PERSONA/12-failure-modes.mdc` (F1/F10/F14), `HA-PERSONA/01-memory-system.mdc` (§ Maintenance danger
    zone; § Empiricist epistemology for structure; § cold-AI test; § Content hierarchy). TARGET has leaner
    equivalents (`00-memory-system.mdc`, `reference/06-failure-modes.md`, `reference/plan-refinement-loop.md`,
    `concepts/_RELATIONS.md`); prefer TARGET's when they govern you, mine HA's for the richer method.

## 4. The method in brief (self-contained; the files above have the depth)
Three phases against a held-constant reference (the **HEAD commit at the moment you begin the cycle** — NOT the
branch's fork point: `alex/ai-persona-maintanance` already carries earlier `ai-tooling` project/concept + path-fix
setup commits; baseline your fidelity reference at your own start), revising the live TARGET tree on the dedicated
branch and checkpointing with git:
  - PHASE I  (analysis + pre-plan): fresh whole-persona inventory + the evaluation framework
    (fidelity is a DOMINANT but SOFT, sensitivity-weighted gate; leanness has a cold-AI-legibility floor;
    discoverability is primary — "undiscoverable ≈ absent"). Most framework decisions already exist in
    HA's `evaluation-framework.md` + `OPEN-QUESTIONS.md` (A–G) — confirm/adapt them to TARGET, don't
    re-derive from zero.
  - PHASE II (detailed plan + refinement loop): author an AI-facing top-level plan following TARGET's
    flexible-plan discipline (`reference/flexible-plans-for-ai-execution.md`) + HA's `14-plan-authoring.mdc`;
    refine it via the end-of-planning lens-sweeps / OERC loop (Observe → Evaluate → Revise → Continue),
    versioning each draft (PLAN-v0, v1, …) in WORKDIR and keeping priors as audit trail. You have STANDING
    PERMISSION to run this plan-refinement loop WITHOUT separate approval — cap it at ≤8 iterations.
    EMPIRICALLY DE-RISK the measurement harness before committing the plan (the single best move last cycle).
    Use subagents for independent critique here (§7).
  - PHASE III (execute): loop  setup → apply → measure → verdict
      setup  = git checkpoint of prior state + FROM-SCRATCH analysis (don't inherit prior framing) +
               change-list + sub-plan;
      apply  = execute the additive edits on the branch; keep a MIGRATION / fidelity ledger in lockstep,
               classifying each unit as {migrated | abstracted-with-layer-beneath |
               deliberately-dropped-low-sensitivity + rationale (PROPOSED, not enacted, if it's a drop)};
      measure= paired cold-AI retrieval eval (§6): score the prior state and the candidate state on the SAME
               randomized stratified probe draw, same pinned model; the DELTA is the signal (±1-file /
               unchanged-answer = FLAT / noise);
      verdict= KEEP / HOLD / REVERT, logged (REVERT = git restore the touched files).
  - CONSISTENCY-CLOSE (final): resolve all cross-refs/indexes; re-verify reference integrity; produce a
    files/units-absent digest, a full-pool probe sweep, and an end-of-cycle synthesis.
Build ADDITIVELY (new parent/index/hub + back-links) rather than by destructive moves — every measured win
last cycle was additive and low-risk. Reference-integrity: hash-baseline the starting reference, re-check at
every milestone; ANY unexpected drift = HARD STOP + ask.

## 5. Iteration bounds (OVERRIDE the prior cycle's ≤20)
Two DISTINCT loops, each capped at 8 (do not conflate them):
- PHASE-II plan-refinement loop: ≤8 refinement iterations (see §4).
- PHASE-III execution top-level loop: HARD CAP 8 iterations, FLOOR ≥3 even at diminishing returns.
- Stop earlier when marginal gain ≈ marginal cost/risk (but small, consistent, cheap-to-maintain wins
  justify continuing up to the cap — don't stop merely because gains shrink).

## 6. Measurement instrument + the two known gotchas
The instrument is a COLD-AI retrieval probe run via the Cursor Python SDK against an ISOLATED staged copy of
a rule-tree version — `HA-PREP/2026-08-cycle-archive-unpacked/methodology/run_probe.py` (stages a version's
CONTENTS into a fresh temp `<tmp>/.cursor/rules`; `setting_sources=['project']` + a distinct cwd give clean
isolation; captures which files the cold AI opens). It is persona-agnostic — **point it at the TARGET
persona's rule tree**, not HA's. Rubric + probe pool + feasibility proof are alongside it. Python venv:
`/Users/alex/Development/PythonVEs/flow` (py3.10, cursor-sdk).

  GOTCHA 1 — permissions/auth (the #1 avoidable cost last time). The harness must run OUT OF SANDBOX (it
  creates a temp `.cursor/rules` dir; the sandbox forbids that), and Cursor auto-review blocks such runs and
  misreads the probe's planted tokens as "secret exposure." An unattended run therefore needs an
  "always allow" entry in `~/.cursor/permissions.json` for the probe command. RE-ISSUING/ADDING SUCH AN
  ENTRY IS A PERMISSIONS GRANT → ASK THE HUMAN to add/confirm an allowlist entry naming YOUR working dir's
  `run_probe.py` copy (+ any `eval/run_*.sh`), interpreter pinned to
  `/Users/alex/Development/PythonVEs/flow/bin/python`, with the rationale "creates a temp dir under system
  temp, stages a rules-tree copy, makes Cursor SDK network calls; reads/writes only inside the working dir +
  system temp; performs no deletions." Do NOT silently broaden your own permissions.

  GOTCHA 2 — stale probe keys. Each probe carries an "expected-reach key" (the files a well-structured
  persona should surface for that task). HA's prior pool keys were written against HA's 2026-08 layout AND
  HA's domain (Solidity/Go/high-assurance) — they are doubly wrong for TARGET. At CALIBRATION (iter-1),
  BUILD FRESH expected-reach keys against a FRESH live inventory of the TARGET tree (glob the current tree)
  and author probes for TARGET's domains (CircuitPython runtime, fonts, power/fuel-gauge, i2c, led-driving,
  git/tooling, the multi-project routing, per-project contexts). Reuse the pool's STRUCTURE (12–20 probes,
  stratified depth × contextual-closeness), but author its CONTENTS for TARGET. Do NOT reuse HA's keys or
  HA-domain probes verbatim.

  IF YOU CANNOT RUN THE HARNESS (no SDK / no API key / permission not granted): operate in a CONSERVATIVE
  MEASUREMENT-BLIND MODE — make only additive, clearly-net-positive, reversible edits; PROPOSE (do not
  enact) anything lossy or semantically risky; mark every blind iteration lower-confidence; and lean heavily
  on the §2 ask-triggers. Surface this state to the human prominently.

## 7. Subagents
You MAY spawn subagents. CHOOSE THE MODEL BY REASONING COMPLEXITY: highest-reasoning model (e.g. Opus,
high thinking) for the hardest work, a mid model (e.g. Sonnet) for moderate work, a light model
(e.g. Composer) for light/mechanical work. Use the highest-reasoning model for:
  - read-heavy exploration / fresh whole-persona inventory,
  - the concept-graph relation audit (run read-only, per TARGET's `concepts/_RELATIONS.md` conventions +
    HA's `05-concept-graph.mdc`),
  - independent CRITIQUE passes in the Phase-II plan-refinement loop (a subagent challenges the draft plan
    against the lens-sweeps / failure modes),
  - and any parallelizable analysis.
Keep destructive/decision authority in the main agent; subagents are for analysis and critique.

## 8. Autonomy envelope
AUTONOMOUS (proceed): set up WORKDIR + experiment log; stand up/adapt the measurement harness against TARGET;
fresh analysis; ADDITIVE discoverability structure (new indexes/hubs/back-links); measured paired evals;
non-destructive edits on the dedicated branch; coarse-milestone git commits on that branch; logging.
ASK / HUMAN-GATE (do not self-enact): any content DROP beyond trivial exact-duplicate dedupe; any semantic
RETYPE/MERGE that could change a learning's meaning (ask-trigger b); any change to foundational files
(`00-memory-system.mdc`, `06-destructive-operations.mdc`) or routing SoT (`04-multi-project.mdc`); the
permissions grant (§6 gotcha 1); MERGE/ADOPTION to main and any DELETION; scope changes; marking any finding
"evidence-supported/verified" without independent corroboration (per TARGET's Evidence-Status Discipline).
When you ask, present a small menu with a recommended default and a one-line rationale, then continue any
independent work while waiting.

## 9. Deliverables (leave working artifacts in WORKDIR; live persona edits go on the branch)
- An EXPERIMENT LOG kept current in WORKDIR (detailed working notes at multiple abstraction levels), so a
  cold-AI — a fresh instance of this persona — can resume exactly where you left off if interrupted. Update
  it as you go, not just at the end.
- The revised persona = the committed state of the `alex/ai-persona-maintanance` branch (coarse-milestone
  commits with an audit-trail message per milestone).
- A MIGRATION / fidelity ledger accounting for every durable-learning unit
  {migrated | abstracted-with-layer-beneath | deliberately-dropped (PROPOSED) + sensitivity-class + rationale}.
- Per-iteration measured verdicts + the consistency-close outputs (integrity re-check, files/units-absent-vs-
  reference proposal list, full-pool sweep, end-of-cycle synthesis: Level-1 changes + a Level-2
  future-improvement map).
- A HUMAN-REVIEW DIGEST that explicitly separates: (i) what was enacted (and measured, where possible),
  (ii) what you PROPOSED-BUT-DID-NOT-ENACT because it was lossy / semantically risky (held for human
  judgment), and (iii) every ASK-item you hit and how you handled it.

## 10. Hard nevers
Never merge/adopt the branch to main (human decision). Never delete (defer to human). Never rewrite a
learning you don't fully understand. Never drop instance-level examples/feedback. Never change `00-memory-
system.mdc` or `06-destructive-operations.mdc` (or `04-multi-project.mdc` routing SoT) without an explicit
ask. Never assume you are the HA persona or import its mission/domain/memory. Never edit the HA repo. Never
broaden your own permissions silently. When in doubt — ASK.

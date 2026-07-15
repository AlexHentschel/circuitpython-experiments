# Session Log — Central (cross-project / persona-level)

This is the **central** session log for the unified persona memory. It holds the cross-project living summary, the source-of-truth map, and `[tooling]` / persona-level sessions that aren't owned by a single project. **Per-project session narratives live in `projects/<slug>/SESSION_LOG.md`.** Read this file + `projects/_INDEX.md` + `universal/*` at session start (M5 read order — authoritative copy in `04-multi-project.mdc § Attention scoping`).

## Current State (living summary)

**Memory layout (unified, since the 2026-06-14 warm reset)**: ONE persona memory home at `.cursor/rules/memory/`, reachable from every project workspace (NOT federated). Structure:
- `universal/` — behavioral / cross-project: `WORKING_STYLE.md`, `CODING_PRINCIPLES.md`, `MONITORING.md`, `CHANGELOG.md`, `PATTERNS.md`.
- `concepts/` — domain-knowledge concept graph: `_INDEX.md` (always-read), `_RELATIONS.md` (typed edges), `concepts/<domain>.md` per evidenced domain (today: `circuitpython-runtime`, `fonts`).
- `projects/` — `_INDEX.md` (roster + path-globs) + `<slug>/` digests (`CONTEXT.md` + `SESSION_LOG.md` + `CONCLUSIONS.md`), linking into each project repo's technical artifacts.
- `crossref/` — `BY_TOPIC.md` + `BY_PATTERN.md` (cross-project lookup; header-only until a 2nd project accrues content).

**Active-project routing (M1)**: detect the active project from the most-recently-edited / open file path against `projects/_INDEX.md` path-globs. `2026-04_Exp14_*/**` → `circuitpython-exp14-display`; `2026-06_Exp15_*/**` → `circuitpython-exp15-microbit`; `Bamboo-Lamp/**` → `bamboo-lamp`. If ambiguous, ask before writing per-project memory. **Write per-project content only into that project's folder; cross-project / boundary content goes to `concepts/` or `universal/` — never bury a cross-scoped insight inside one project** (`WORKING_STYLE.md` Core Principle *Don't guess an association into a deep, specific bucket*; R-7).

**Reachability model (superseded 2026-07-15 — see below)**: ~~central tree lived at `CircuitPython/.cursor/rules/`, symlinked into `Exp14/.cursor/rules` and `Bamboo-Lamp/.cursor/rules`~~. **Current model (2026-07-15)**: the physical rules tree now lives **only** at `CircuitPython/ai-persona/.cursor/rules/`, a dedicated workspace-root folder — no symlinks anywhere. Root cause: Cursor does not deduplicate `alwaysApply: true` rules across workspace roots in a multi-root session (confirmed open bug, no ETA) — the old symlink-fanout meant every co-attached symlinked root re-injected the full rule set, wasting context tokens. Trade-off accepted: persona now loads **only when `ai-persona` is a folder in the active Cursor workspace** (confirmed present in `/Users/alex/Development/Cursor Workspaces/circuitpython.code-workspace`); opening a project folder standalone, bypassing that workspace file, yields zero persona coverage. Full rationale + rejected alternatives: `universal/CHANGELOG.md § 2026-07-15`.

**Bamboo-Lamp (unified 2026-06-14; reachability superseded 2026-07-15)**: its high-level memory still lives centrally at `projects/bamboo-lamp/`; its technical artifacts (`AI-Notes.md`, `diagrams/`, `open-discussions/`) stay in the `~/Projects/Family/Bamboo-Lamp` repo, linked from `projects/bamboo-lamp/CONTEXT.md`. `Bamboo-Lamp/memory/` still holds only a pointer back to central. **Historical note**: reachability was via a `Bamboo-Lamp/.cursor/rules` symlink → central tree (created + verified resolving 2026-06-14; standalone-open test R-6 PASSED 2026-06-14). **That symlink was deleted 2026-07-15** as part of the dedicated-root move above — R-6's standalone-open guarantee no longer holds. Bamboo-Lamp now reaches the persona only via the combined Cursor workspace (same as every other project).

**Provisional marker (C7)**: the new structure is `provisional (as of 2026-06-14)`. Cold-AI-testable watch-for lives in `concepts/_INDEX.md` and `projects/_INDEX.md` headers. Re-evaluate after ~5 real memory additions or at the next maintenance session; remove the marker if no refute signal fires.

**Available skills**: `circuit-drawing-generator` at `Bamboo-Lamp/.claude/skills/circuit-drawing-generator/SKILL.md` — Schemdraw code → SVG. Python env `/Users/alex/Development/PythonVEs/MicroControllers/bin/python`; render `python scripts/render_circuit.py input.py output.svg` from the Bamboo-Lamp root. Smoke-tested 2026-05-25 (Schemdraw v0.22). Label-placement notes in `Bamboo-Lamp/Notes.md`.

**Active project status pointers** (detail in each `projects/<slug>/`):
- `circuitpython-exp14-display` — **active**; Phase 3 in progress (P3.1–P3.5 done, P3.6 on-device smoke + P3.7 audit remain). Branch `alex/display-mvp`. See `projects/circuitpython-exp14-display/SESSION_LOG.md`.
- `circuitpython-exp15-microbit` — **active (early)**; Milestone 1 blink set up, on-device run pending board connection. See `projects/circuitpython-exp15-microbit/`.
- `bamboo-lamp` — **active**; standby/sleep-mode design discussion pending; S3-vs-C6 MCU divergence open. See `projects/bamboo-lamp/`.
- `coding-tutor` — **active (setup)**; new family `education`. Build an AI tutor persona (distinct from this assisting persona) teaching CircuitPython on micro:bit+Nezha2+PlanetX to student persona "Alice". Setup done 2026-07-15 (picture + KB scaffolding + memory registered); design not started — next is transcript ingestion + tutoring research. See `projects/coding-tutor/`.
- exp09 / exp11 / exp13 — residue only; no project folder yet (create a `_INDEX.md` row + folder when content surfaces).

## Source-of-truth map (which file owns which content; pre-empts duplication-and-drift)

| Content type | Source of truth | Update authority |
|---|---|---|
| Collaboration / process / judgment / artifact-convention directives | `universal/WORKING_STYLE.md` | Agent (operational) |
| Coding-craft directives (how code itself is written) | `universal/CODING_PRINCIPLES.md` (schema inherited from `WORKING_STYLE.md`) | Agent (operational) |
| Single-incident observations to act on only if they recur | `universal/MONITORING.md` | Agent (operational) |
| Cross-project generalized patterns (≥2 projects) | `universal/PATTERNS.md` | Agent; `[universal]` promotion needs Alex sign-off (D2) |
| Provenance of structural memory changes | `universal/CHANGELOG.md` | Agent (operational) |
| Domain knowledge (concepts, mechanisms, perf claims) with status | `concepts/<domain>.md` (indexed by `concepts/_INDEX.md`, related via `concepts/_RELATIONS.md`) | Agent; status tracks evidence sufficiency |
| Per-project session narrative / status / open questions | `projects/<slug>/SESSION_LOG.md` + `CONTEXT.md` | Agent (operational) |
| Per-project cross-session findings with evidence status | `projects/<slug>/CONCLUSIONS.md` | Agent records `unverified`/`evidence-supported`/`disputed`/`invalidated` by independent corroboration (no human-elevation tier) |
| Cross-project / tooling / persona-level session narrative + this map | `memory/SESSION_LOG.md` (this file) | Agent (operational) |
| Cross-project topic/pattern lookup | `crossref/BY_TOPIC.md`, `crossref/BY_PATTERN.md` | Agent (operational) |
| Project roster + active-project path-globs | `projects/_INDEX.md` | Agent (operational) |
| Active plan for a project | the project's plan store (e.g. exp14: `~/.cursor/plans/display_library_refactor_d42ccd55.plan.md`) | Agent maintains; phase-close revisions presented to Alex |

When the same fact must live in two places (rare; only when duplication serves distinct consumers), log it here and add a sync-check to the next maintenance reflection.

**Known consumer-distinct duplications** (sweep together on any structural change):
- **Evidence-status tier definitions** — authoritative in `00-memory-system.mdc § Evidence-Status Discipline`; restated for distinct consumers in `02-domain-structure.mdc`, `concepts/<domain>.md` / `projects/<slug>/CONCLUSIONS.md` headers, and `COLLABORATOR_GUIDE.md`. Use the two-pass vocabulary-migration sweep (`WORKING_STYLE.md § Document Authoring`) when the tier model changes.
- **Scope-tag dimensions** — two *orthogonal* axes (D4): (1) *directive scope* `[universal]/[user]/[project]/[task]` (authoritative in `WORKING_STYLE.md` header; echoed in `01-interaction-style.mdc`); (2) *content scope* `[universal]/[domain:x]/[family:y]/[project:slug]/...` (authoritative in `04-multi-project.mdc § Scope tagging`; rubric in `working-docs/warm-reset-plan/microcontroller-multi-project-memory-guidelines.md § 5`). Don't collapse the two.

## Cross-project & tooling sessions

## 2026-07-15: Session 13 — [tooling] (dedicated `ai-persona` workspace root replaces symlink-fanout)

- Context: Alex asked me to locate the persona (answered: `CircuitPython/.cursor/rules/`), then reported he'd moved the physical tree into a new dedicated `CircuitPython/ai-persona/` folder and added it to the Cursor multi-root workspace, and asked me to re-validate a recalled prior finding — that symlinking the same rules tree into multiple workspace roots caused repeated context-window inclusion.
- Research: confirmed via Cursor's forum/bug reports (not previously in this memory — see gap note below) that `alwaysApply: true` rules are loaded once per workspace root with **no cross-root deduplication**; symlink vs. real copy makes no difference to the scanner. Open bug, no ETA.
- Side-finding: the move had orphaned the two pre-existing symlinks (`Exp14/.cursor/rules`, `Bamboo-Lamp/.cursor/rules`) that pointed at the old `CircuitPython/.cursor/rules` location — both dangling, meaning those two roots currently got **zero** persona coverage, not stale-but-working copies.
- Decision (Alex-gated, `AskQuestion`): dedicated-`ai-persona`-root-only, no symlink repair, accepting the "must co-open `ai-persona`" trade-off over repairing symlinks (keeps standalone-open, re-accepts duplication) or migrating to Cursor User Rules (avoids both costs, drops git-versioning). Agent provided `rm` commands rather than executing them, at Alex's explicit request; Alex ran them and confirmed.
- Discovered the *actual* live workspace entry point mid-session: not the old `CircuitPython/CircuitPy_VSCode.code-workspace` (VS Code era, doesn't include `ai-persona`, confirmed inactive) but `/Users/alex/Development/Cursor Workspaces/circuitpython.code-workspace` (Cursor era) — which already lists `ai-persona` first, so no edit was needed to make the new model work.
- Full structural record: `universal/CHANGELOG.md § 2026-07-15`. This entry updated the living summary above (superseded the symlink-fanout + R-6 standalone-open descriptions) in place, per F1/F10 guard — old text struck through/marked historical rather than deleted.
- **Memory-system gap surfaced**: the duplication realization Alex recalled from "the past" had no record anywhere in this memory (checked `CHANGELOG.md`, `MONITORING.md`, `WORKING_STYLE.md`, agent-transcripts — no hits). It had only ever existed in an unpersisted conversation, i.e. exactly the failure mode `03-memory-update-triggers.mdc` item 4 exists to prevent ("stated a takeaway in conversation without writing it to memory"). No corrective action beyond writing it down now — noting it as a concrete instance in case a pattern of this specific gap (persona-infrastructure/tooling realizations discussed but not logged) recurs.
- Open (unverified, flagged in `CHANGELOG.md`): whether a single `alwaysApply` rule in one attached root actually applies workspace-wide across all other attached roots' files, vs. being scoped to `ai-persona`'s own files only. Inferred from Cursor docs + forum wording, not confirmed in-session. If a future session wants certainty: ask the agent to list its always-applied rules while the active file is in a different attached root (e.g. an Exp14 file), per the reproduction method used in the upstream bug reports.

## 2026-06-15: Session 12 — [tooling] (generalized the warm-reset `_META` into a reusable corpus process doc)

- Context: Alex asked to read `working-docs/warm-reset-plan/_META.md` as one *instance* of a general process for
  drafting → self-reviewing → refining a plan iteratively (engraining higher-level reflection, progress self-monitoring,
  and self-adaptation), and to write that generalization into the external persona-design corpus
  `~/Developed/AI/generalized-agent-learnings/` for a cold AI that knows only that folder.
- Artifacts created (in the external corpus, NOT in `.cursor/rules/memory/` — that corpus is the paradigm *source*,
  ephemeral-from-the-persona's-view but the authoring home Alex maintains):
  - `generalized-agent-learnings/plan-refinement-loop.md` — the generalized process. Sections: setup/adaptation (ask
    the user for the hard convergence cap + iteration location + a one-line naming blueprint; reflect on instance-specific
    additions) · the blueprint (versioning v0.0→v0.X→v1.0; copy→reviews→change-magnitude→apply→converge) · the three
    ordered reviews **R1 substance/goal-fit → R2 cold-ai+flexible-plans → R3 economy** (order rationale: structural edit
    before line-edit before trim) · convergence (change-magnitude depth/breadth + user cap) · post-loop close (promote
    v1.0 + irreducible-uncertainty risk scan w/ MISSING check) · sub-agents as opt-in accelerator (cost heads-up to user;
    composer-2.5-class extraction vs opus-4.8-class reasoning, or newer) · heuristics-not-laws with bounded-deviation
    invariants. Framing rule encoded: present to user as "internally iterating over the plan", keep "meta-plan" jargon
    internal.
  - `generalized-agent-learnings/exemplary-artifacts/warm-reset-plan_META.md` — verbatim copy of the warm-reset `_META.md`,
    referenced from the process doc (§8) as one concrete adaptation.
- Follow-up (same session): listed all the named (non-numbered) corpus docs in `00-OVERVIEW.md` (they were absent —
  `cold-ai-paradigm`, `Flexible Plans`, `writes-thinks-speaks`, `Effective Behavioral Guidelines`, `plan-refinement-loop`),
  added a front-matter note. Renamed `PLAN.md` → `EXTRACTION-PLAN.md` (Alex's pick; disambiguates the corpus *build*
  plan from the how-to-draft-plans doc; only ref was its own self-row). Added `README.md` — an ultra-compact, jargon-free
  goal→file router for humans + quick AI onboarding (sits above `00-OVERVIEW.md`).
- Refinement pass (transcript-coverage, Alex): crawled this chat's transcript (`agent-transcripts/73251650-…jsonl`,
  14 user turns) and built a coverage matrix of feedback-given vs feedback-covered in `plan-refinement-loop.md`. Notes:
  `working-docs/plan-refinement-loop_refinement-notes.md`. Result: ~22 substantive items already covered; 5 gaps, all
  applied to the doc — G1 audible-reflection-at-checkpoints (EBG), G2 "steps are illustrative shape not mandate" framing
  (EBG anti-over-prescription), G3 falsifiable "signals this blueprint needs revision" (cold-ai §7 recursive), G4
  fresh-cold-chat handoff capability (§6), G5 "inherited spec = adaptable prior, contradictions have no default winner"
  (§7). Deliberately did NOT hoist the parsimony-vs-retrieval / topic→detail-one-hop specifics into the general process
  (instance-specific to memory-structure plans → stay in the rubric/§8 example).
- Second refinement (Alex, parsimony tension): added §3.8 "plan economy model" — plan-bloat < memory-bloat asymmetry
  (memory: retrieval > parsimony, loaded forever; plan: task-scoped, leaner still by default for *surface-area* reasons);
  lean plan = more flexible (less over-prescribe/over-harness surface); leanness is safe **only because** the
  reflection/monitoring/adaptation machinery is explicit and carries what a fat plan pre-specifies. R3 gained a trim
  test + cross-ref. Notes-economy clarified. Logged as G6 in the refinement notes.
- Routing rationale: this is persona-process meta-work spanning all projects → central `[tooling]` log, not `bamboo-lamp`
  (even though authored from the Bamboo-Lamp chat context). No project-technical content touched.
- Op note (reinforces the *Prefer file-edit tools over shell for file mutations* directive): the corpus lives outside the
  Cursor workspace → the `cp` of `_META.md` hit a sandbox write-block; cleared with `required_permissions:["all"]`. The
  `Write`/`StrReplace` tools wrote to the external path without issue.

## 2026-06-14: Session 11 — [tooling] (warm-reset EXECUTION + post-execution maintenance)

- Context: the separate cold-AI execution chat the Session-10 handoff (below) anticipated. Triggered by Alex's "warm reset" phrase; ran `warm-reset-plan_v1.0.md` Phases 1–8 under the Phase-0.5 pre-flight gate (snapshot → present change set → await explicit "go ahead" before any non-snapshot mutation). **Full structural provenance + rollback command: `universal/CHANGELOG.md § 2026-06-14 — warm reset`.** This entry is the session narrative + the durable operational learnings.
- Outcome: flat single-project `memory/` → unified multi-project layout (`universal/`, `concepts/`, `projects/<slug>/`, `crossref/`). All S1–S8 acceptance criteria passed. D1–D8 + R-6 all closed. New structure carries the `provisional (2026-06-14)` marker (re-evaluate after ~5 real memory additions). Bamboo-Lamp unified centrally; cross-tree symlink created + **R-6 standalone-open test PASSED** (see living summary).
- Snapshots retained for rollback: `memory-pre-warm-reset-20260614-150919/` (CircuitPython) + `memory-pre-warm-reset-20260614-171818/` (Bamboo-Lamp). Stray 0-byte `exp14/working-docs/warm-reset-plan/warm-reset-plan_v0.0.md` + its empty dir deleted; planning set under the top-level `working-docs/warm-reset-plan/` intentionally kept.
- **Operational learning (distilled to directives, evidence-bearing):** the only real friction was the Cursor approval gate — file-**mutating** shell commands that aren't allowlisted (`sed -i`, `ln -s`, `printf`/heredoc redirection, `cp -R` under `.cursor/`) *stall the whole turn* with no error (three incidents, each drawing an "are you stuck?" from Alex). Remedy applied: reconstruct files with the `Write` tool instead of `sed`; hand `mkdir`/`ln` to Alex; re-run snapshot `cp -R` with `required_permissions:["all"]`. → new `[user]` directive *Prefer the file-edit tools over shell for file mutations; hand off an unavoidable shell file-op rather than let it hang* (`WORKING_STYLE.md § Workflow & Artifacts`).
- **Maintenance learning (distilled):** no-loss under a layout-changing restructure can only be verified by **claims-coverage** (every claim/finding reappears by content), never by line/byte diff — the diff floods with false positives once prose→concept-entry and monolith→per-project slicing change the bytes on purpose. → new `WORKING_STYLE.md § Retention and Evaluation` bullet.
- Post-execution maintenance sweep (this session, after Alex's "refine your memory" prompt): the Phase-7 dead-path grep had only covered `.mdc` rule files; re-pointed the residual **active forward-routing** `TECHNICAL.md` pointers → `concepts/<domain>.md` in `MONITORING.md` (4 spots) + `CODING_PRINCIPLES.md` (2 spots). Historical `TECHNICAL.md` mentions (changelog/session-log narrative, concept-file "reshaped from" notes) left intact as provenance. Recommendation: no further lifecycle iteration warranted — memory content still small, backlog empty.

## 2026-06-14: Session 10 — [tooling] (warm-reset PLANNING loop — `_META`-governed, NOT executed)

- Context: executed the warm-reset planning loop in `working-docs/warm-reset-plan/` (governed by `_META.md`) under the cold-AI + flexible-plans paradigms. **PLANNING ONLY** — the `warm reset` mandate is NOT triggered; execution still needs Alex's exact phrase + go-ahead. Routing: this is CircuitPython-side memory-architecture meta-work; nothing Bamboo-Lamp written.
- Loop result: converged at **v0.5** (iter 5 = also the cap), promoted to **v1.0** sign-off candidate. Magnitude trend T3→T2→T2→T2→T1; adequacy-unknowns 3→2→2→1→0. Full revision trail in `notes_v0.1.md`…`notes_v0.5.md`; sub-agent technique tuning in `experiment-log.md`.
- Artifacts (all in `working-docs/warm-reset-plan/`): `warm-reset-plan_v0.1.md`…`v0.5.md` + `v1.0.md`; `notes_v0.1.md`…`notes_v0.5.md`; `risk-register.md`; appended `experiment-log.md`.
- Key substance added across iterations (vs the v0.0 skeleton): D8 (concept-graph retrieval layer — escalated, deviates from mandate's flat per-project files); C7 (seed-on-evidence + cold-AI-testable `provisional` marker); §3a Deviations (DV1–3); dropped the reference/-move (would orphan ~15+ refs); added 01-interaction-style.mdc + the M5 read-order rewrite to Phase 6; Phase 0.5 mandate pre-flight; S7 retrieval-acceptance tests; placement gate.
- Evidence finding (grounds C7): actual memory content is tiny + exp14-concentrated — `TECHNICAL.md` has only 2 populated sections (CircuitPython memory-management, fonts) atop empty schema; `CONCLUSIONS.md` = 1 finding; domains power/i2c/deep-sleep/fuel-gauge/led-driving have zero content.
- Escalation set for Alex (OPEN, options+recommendation, his calls): D1–D8 + DV1–3, plus risk-register items R-7 (don't mis-default already-cross-scoped technical content), R-8 (no-loss verification under restructure), R-9 (concept-graph vs the no-rewrite anti-goal), R-6 (symlink test), R-11 (single behavioral catalog invariant).
- Sub-agent technique (confirmed): composer-2.5 explore = strong for exhaustive path/ref enumeration; partial for table-as-deliverable (tables didn't surface in the response — read short files in the parent instead). Details + best-practice block in `experiment-log.md`.
- Process correction (post-convergence): Alex corrected v1.0's framing of the mandate as "source of truth (wins on conflict)" → it is a **prior-execution template**, an adaptable prior to assess against the persona's current/evolved state during execution. Applied to v1.0 (template framing in header + §4; Phase 0 gained a template-fit-assessment activity; §3a "deviations" → "adaptations" split into low-stakes-transparent DV1/DV2 vs high-stakes-escalate DV3; §6 authority map updated). New `[universal]` directive added to `WORKING_STYLE.md § Core Principles`: *Inherited specs are adaptable priors, not rigid sources of truth*.
- Open: awaiting Alex's go/no-go on the escalation set; warm reset remains un-triggered.
- Process correction #2 (post-convergence, 2026-06-14): Alex set a load-bearing requirement — **one unified persona memory in ONE cross-workspace location, NOT federated**. Split: *central* = high-level (per-project digests + rough status/resumption + entry-points linking into project folders + generalizable & **boundary** learnings + modus-operandi feedback + coding guidelines + style prefs); *project folders* = technical execution artifacts (sketches, thought experiments), linked from central, never duplicated. This **decides D7 (unified, not federated)** and **D6** (one location = central tree kept in the CircuitPython workspace's `.cursor/rules/`, symlinked into the other workspaces — Alex picked in-workspace over a user-level root), and **reinforces D8** (boundary concepts must live in a central concept home). Applied to `v1.0`: §1 rewritten; C4 broadened + new C8 (central self-sufficient, project links = further-reading only); D6/D7 marked decided; Phase 3 reshaped to digest+entry-points (hoist general/boundary to central, leave execution detail as linked artifacts); Phase 4 rewritten to migrate Bamboo-Lamp high-level → central + leave pointer; S5 broadened + new S8; risk-register R-5 closed (unified), R-6 → mandatory reachability pre-check (no federation fallback), R-11 broadened to whole-memory single-source. Forward-pointer added to the routing note above; current split unchanged until execution.
- Decision set CLOSED (2026-06-14): Alex agreed with all remaining recommendations → **D1–D8 all DECIDED**. D1 = per-experiment + `circuitpython` family (Bamboo-Lamp own family); D2 = auto-promote, sign-off for `[universal]`; D3 = principle + R-7 fix (honor existing tags, route cross-scoped to central); D4 = orthogonal scope models; D5 = strip stale `verified`/elevation tiers; D6/D7 = unified-not-federated (central tree in CircuitPython `.cursor/rules/`, symlinked out); D8 = (c) graduated concept-graph. Risk fixes adopted: R-8 = claims-coverage no-loss check; R-9 = concept reshaping is an approved anti-goal exception scoped to the two existing `TECHNICAL.md` sections only. New `[universal]` directive added to `WORKING_STYLE.md § Core Principles`: *Don't guess an association into a deep, specific bucket* (D3's load-bearing insight, generalized). **Only two execution prerequisites remain**: R-6 symlink reachability smoke-test + Alex's "warm reset" trigger. Plan + risk-register updated to reflect closure.
- Memory-lifecycle patterns codified (2026-06-14, Alex stated as general): (1) **accumulate-then-split** — seed a category on its first instance, split hierarchically as instances accumulate, treat categories as loose/fuzzy/overlapping and cross-link rather than force a partition; (2) **batch heavy restructuring into deliberate, user-gated lifecycle iterations** — backlog non-trivial reorg TODOs (`MAINTENANCE_BACKLOG.md`, deferred-creation; warm-reset plan dir is the current iteration's list), run iterations only on user go-ahead but proactively recommend when beneficial. Both added as `[universal]` `WORKING_STYLE.md § Core Principles` directives; `00-memory-system.mdc § Maintenance` extended (items 4–6); logged in `CHANGELOG.md`. Recommendation surfaced: warm reset is the active lifecycle iteration; no additional iteration warranted now (memory content still tiny).
- Persona-path inspection (2026-06-14, `evidence-supported`): canonical persona = real files at `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules/` (memory/ within); NOT itself a symlink, no `~/.cursor/rules` global. `exp14/.cursor/rules` → working symlink to `../../.cursor/rules` (the D6 in-workspace symlink pattern, already proven intra-tree). exp13/11/09 inherit by directory ascent (no `.cursor`). **Bamboo-Lamp has no symlink** — reaches persona only via co-opening the multi-root `CircuitPy_VSCode.code-workspace`; standalone it loads no persona memory. Confirms D6/R-6: the only remaining reachability unknown is whether Cursor follows a cross-tree `Bamboo-Lamp/.cursor/rules` symlink when opened standalone. Recorded in `risk-register.md` R-6.
- **Planning→execution handoff (2026-06-14)**: Alex is running the warm-reset *execution* in a SEPARATE cold-AI chat (same persona + shared memory), not this one. I provided a self-contained launch prompt that (a) triggers "warm reset", (b) references — not copies — the plan `warm-reset-plan_v1.0.md` + `risk-register.md` + the two paradigm refs + the mandate/rubric + this SESSION_LOG, (c) enforces the Phase-0.5 pre-flight gate (snapshot first, read F1/F8/F10, present change set, await Alex's explicit "go ahead" before any non-snapshot mutation), (d) carries the closed decisions + invariants (C1 no-loss via claims-coverage, C7 provisional, C8 central self-sufficient, R-7 placement, R-9 reshaping scoped to 2 sections), and (e) flags the R-6 standalone-open test as an Alex-only handoff. **State for the executing chat / future me**: D1–D8 closed; only R-6 reachability + Alex's in-chat "go ahead" gate remain; no files mutated toward the reset yet. If that run completes, this living summary's routing note (Bamboo-Lamp vs CircuitPython split) and the warm-reset target forward-pointer become stale — update them to the unified layout at completion.

---

## Open questions & mandate notes — RESOLVED at the 2026-06-14 warm reset

OQ-MP-1/2/3 (project granularity, promotion autonomy, pre-existing-entry tagging) map to plan decisions D1/D2/D3 — **all closed by Alex 2026-06-14** (see `universal/CHANGELOG.md` warm-reset entry + `working-docs/warm-reset-plan/warm-reset-plan_v1.0.md` §3). DN-MP-1 (new-project-vs-extend heuristic) is now seeded in `projects/_INDEX.md` header, to be refined after 3–5 projects. The `warm reset` mandate has now executed. Verbatim pre-reset text preserved below for provenance:

## Open Questions

| ID | Question | Since | Refs |
|----|----------|-------|------|
| OQ-MP-1 | Project granularity for multi-project layout: per-experiment, per-theme, mixed, or cross-domain families? | 2026-04-17 | `mandates/multi-project.md § OQ1` |
| OQ-MP-2 | Promotion autonomy: propose-only, auto-cross-project with manual universal, or fully agentic with CHANGELOG? | 2026-04-17 | `mandates/multi-project.md § OQ2` |
| OQ-MP-3 | How to tag pre-existing untagged entries at warm-reset time? (Default to active project for TECHNICAL/CONCLUSIONS, `[universal]` for WORKING_STYLE, flag ambiguous.) | 2026-04-17 | `mandates/multi-project.md § OQ3` |

### Deferred design notes

Items that are not questions needing a near-term answer, but decisions to revisit with accumulated evidence:

| ID | Note | Revisit when | Refs |
|----|------|--------------|------|
| DN-MP-1 | New-project-vs-extend heuristic — can only be refined empirically, not pre-specified. | After 3–5 distinct projects of experience (post-warm-reset). | `mandates/multi-project.md § OQ4` |

### Notes on open mandates

The human has declared an **open mandate** for a multi-project memory architecture, triggered by the phrase **"warm reset"**. Full spec at `mandates/multi-project.md`. Do not pre-emptively restructure — wait for the explicit trigger, then follow the pre-flight checklist in that file. OQ-MP-1 through OQ-MP-3 above should be resolved with the human *before* warm reset executes; DN-MP-1 is intentionally deferred until post-warm-reset evidence exists.

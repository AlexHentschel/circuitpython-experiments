<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/11-MULTI-PROJECT-BOOTSTRAP.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
Do NOT re-execute. Warm reset ran 2026-06-14 (adapted). Dedicated `ai-persona` root replaced symlink-fanout 2026-07-15.
-->

# Multi-Project Bootstrap: A Flexible Plan for Cold AI

This file augments `08-BOOTSTRAPPING.md`. Where 08 teaches a fresh AI to bootstrap a *single-project* persona and treats multi-domain as a sequential transfer (`§ Transferring to a New Domain`), this file teaches how to bootstrap a persona that hosts **multiple coexisting workstreams in parallel** — with cross-workstream concept reuse, self-containment durability across workspace boundaries, and a placement discipline that survives 10× memory growth.

Read this file when you are about to set up a new persona that will span more than one project or workspace, *or* when you are evolving a single-project persona to host additional workstreams.

The reader to optimize for is a cold AI in a fresh session with no prior knowledge of any specific project. This document is itself written for that reader.

---

## 1. When to Use This File

`08-BOOTSTRAPPING.md` covers single-project bootstrap. Use it when one human collaborates with you on one project, in one workspace, for the foreseeable lifetime of the engagement.

Use **this** file (`11`) when any of these holds:

- The same human will collaborate across **multiple related-but-distinct projects** (e.g. a finance protocol family with oracle, lending, and PoC sub-projects).
- The persona will be **attached to multiple workspace directories** (each project lives in its own git repo).
- You expect to **import accumulated learnings from one or more existing personas** in adjacent work contexts (cross-context pollination).
- You expect memory volume to grow ~10× over a single-project baseline.

The two architectures are not mutually exclusive. A single-project persona that grows multi-project later can evolve via a meta-workstream (see `§ 6.4`) rather than rebuild from scratch.

Both `08` and this file are *create/grow* paths. If a multi-project persona **already exists** and you are a fresh session onboarding to it, you are *adopting*, not creating — follow its session-start retrieval (generic path: `00-OVERVIEW.md` reading order → `01-MEMORY-SYSTEM.md § Active Retrieval`), not the setup steps below. See `README.md § Instantiate a persona` for the create-vs-adopt split and the two setup questions (which project/workspace receives the files; single vs multiple).

This file describes the **Cursor** host shape. For **Claude Code** or another host, adapt the mechanisms as you go: `host-portability.md` (general method) and `host-adaptation-claude-code.md` (worked Claude Code instance).

---

## 2. Why Single-Project Architecture Breaks at Scale

The single-project architecture from `08` is: flat `memory/` with `WORKING_STYLE.md`, `SESSION_LOG.md`, `TECHNICAL.md`, `CONCLUSIONS.md`, plus scope tags on entries. This works at one-project scale because retrieval is "read everything relevant," and "everything" is small.

At multi-project scale, three problems emerge:

1. **Cross-contamination.** Work on Project A pollutes memory about Project B unless every write is correctly scope-tagged at write time, every read filters by scope at read time, and the scope-tag taxonomy is itself stable. Tags are easy to forget; their omission is silent.
2. **Retrieval failure under volume.** "Read SESSION_LOG and scan for relevant entries" stops scaling at ~30–40 substantive entries. The cost of reading-to-find dominates the cost of acting on the find.
3. **Cross-workstream pollination has no home.** A pattern observed in Project A that *might* generalize to Project B has no first-class place to land where Project B's work will naturally surface it.

The architecture described here addresses all three with two load-bearing shifts.

---

## 3. The Two Architectural Shifts

These two shifts are load-bearing. Plans that skip either of them re-create the single-project problems at multi-project scale.

### 3.1 Shift One — Semantic Concept Graph as Primary Navigation

Replace flat `TECHNICAL.md` + scope tags with a **per-concept file tree** plus a **first-class relation graph**.

```
memory/concepts/
├── _INDEX.md                # one-line per concept; always-read at session start
├── _RELATIONS.md            # edge list across concepts; always-read on placement
├── <domain-A>/
│   ├── _INDEX.md            # per-domain index (always-read if domain is touched)
│   ├── <concept>.md
│   └── ...
├── <domain-B>/
└── ...
```

Each concept file has a fixed template:

```markdown
# <concept-name> [domain:<x>] [language:<y>?] status: unverified|evidence-supported|verified

## One-line purpose
## Mechanism
## Where it applies               (reinforcement count + last-applied date)
## Where it doesn't apply         (first-class partial-contradiction section)
## Refinement history             (dated)
## Related concepts               (bidirectional links: refines / generalizes / etc.)
## Provenance                     (origin work-context + second-context evidence sub-bullets)
```

Relations are a closed vocabulary recorded in `_RELATIONS.md`: `refines` / `generalizes`, `alternative-to`, `composes-with`, `instantiates` / `abstracts`, `pairs-with`, `conflicts-with`, `contradicts-in-context-X` (partial contradiction with scope), `complemented-by`.

**Why this works at scale.** Retrieval becomes one hop: "I need to know about X" → `concepts/_INDEX.md` → `concepts/<domain>/<concept>.md`. New observations refine concept files in place; new edges are cheap. Cross-domain pollination happens by *traversing edges* rather than re-reading project-scoped files.

**The placement gate** (run on every new finding) routes content to the right file:
1. Code-shaped? → `concepts/coding/[<language>/]<file>.md`
2. Review-shaped? → `concepts/review-patterns/<file>.md`
3. Domain-shaped (e.g. financial / cryptographic)? → `concepts/<domain>/<concept>.md`
4. Collaboration-shaped? → `style/WORKING_STYLE.md`
5. Per-individual? → `style/HUMAN_PROFILE.md`

The placement gate is what makes the structure *operational*: every finding has a deterministic home, decided at write time, not "wherever feels right."

### 3.2 Shift Two — Self-Containment Durability

The persona must survive any **external work-context source persona being offloaded** from the machine (deleted, archived, moved). This is non-negotiable because durability is the whole point of persistent memory.

**The hard rule:** no file under `.cursor/` may contain absolute paths into another AI persona's directory. Cross-context references use **work-context names** (e.g. `circuitpython-display`, `tidal-protocol-research`) plus **in-context evidence descriptions** (e.g. "during the column-major LED-display refactor on RP2040, late April 2026").

Build-time path resolution lives **outside** the persona at `~/.cursor/persona-builds/<build-slug>/SOURCE_PATH_TABLE.md`. That file is build-scratch: it holds the absolute-path-to-work-context mapping for the duration of a build, and is disposable once self-containment is verified.

**Outside / inside separation by content shape, not purpose:**
- Anything containing forbidden absolute paths → **outside** the persona, in `~/.cursor/persona-builds/<build>/`. Disposable after close.
- Descriptive content using work-context names → **inside** the persona, in `memory/workstreams/<slug>/`. Retained as archaeological memory after close.

**Authoring corollary:** when writing a defensive example of "do not write this", **describe the pattern by name** (e.g. "an absolute path into a forbidden source-persona directory"), not by instantiation. Instantiation defeats the separation; this is the most-reinforced behavioural pattern surfaced during the multi-project build that proved this design.

---

## 4. Structural Shape of a Multi-Project Persona

The target directory tree, in full:

```
<host-workspace>/.cursor/rules/
├── 00-persona-and-mission.mdc       always-injected; identity, scope, no-go list
├── 01-memory-system.mdc             always-injected; file architecture + active retrieval
├── 02-interaction-style.mdc         always-injected; communication style
├── 03-domain-structure.mdc          always-injected; domain map + scope-tag taxonomy
├── 04-memory-update-triggers.mdc    always-injected; post-response checklist
├── 05-concept-graph.mdc             always-injected; 5 ops + relation vocabulary
├── 06-destructive-operations.mdc    always-injected; hard-gate *stub* (never delete without explicit per-file grant). Full protocol: this corpus's `destructive-operations.md` — not to be confused with guidance file `06-FAILURE-MODES.md`
├── 10-self-improvement.mdc          on-demand
├── 11-evidence-and-validation.mdc   on-demand
├── 12-failure-modes.mdc             on-demand
├── 13-directive-authoring.mdc       on-demand
├── 14-plan-authoring.mdc            on-demand
├── 2x-*.mdc                         domain/language-specific (e.g. cadence-review, solidity-review)
├── README.md                        operator-facing, multi-workspace attachment notes
├── memory/
│   ├── SESSION_LOG.md               cross-workstream slim log
│   ├── CONCLUSIONS.md               cross-session findings index
│   ├── CHANGELOG.md                 directive/structural changes
│   ├── MONITORING.md                cross-session "watch for next occurrence" register
│   ├── concepts/                    semantic graph (see § 3.1)
│   │   ├── _INDEX.md
│   │   ├── _RELATIONS.md
│   │   ├── coding/                  language-agnostic root + per-language subdirs
│   │   │   ├── _INDEX.md
│   │   │   ├── <language-A>/
│   │   │   └── <language-B>/
│   │   ├── <domain-A>/
│   │   └── ...
│   ├── workstreams/                 secondary metadata, not primary structure
│   │   ├── _INDEX.md                roster + path-globs for active-workstream detection
│   │   ├── <project-slug-1>/CONTEXT.md
│   │   ├── <project-slug-2>/CONTEXT.md
│   │   └── <meta-workstream-slug>/  (frozen-snapshot meta-workstreams)
│   ├── style/
│   │   ├── WORKING_STYLE.md         collaboration directives + reinforcement tracking
│   │   └── HUMAN_PROFILE.md         per-individual notation prefs, pet peeves, expertise
│   ├── crossref/                    deferred-creation secondary indexes
│   ├── mandates/README.md           cross-workstream cross-cutting-directive mechanism
│   └── PERMITTED_DESTRUCTIVE_ACTIONS.md  ledger of human grants for irreversible actions (fail-closed if absent; see `destructive-operations.md` §6)
└── knowledge/                       static domain reference material (optional)

<consumer-workspace-N>/.cursor/
└── rules → <relative-or-absolute-symlink-to-host-workspace>/.cursor/rules
```

**Attachment via symlinks.** Each consumer workspace contains `.cursor/rules` as a symlink resolving to the host persona's `rules/` directory. Verified with `realpath`. This is what makes "the same persona" available from `cd <project-A>` and `cd <project-B>` without duplication.

**Active-workstream identification.** `workstreams/_INDEX.md` carries a path-glob for each workstream. At session start, the path of the currently-edited file determines which workstream's `CONTEXT.md` to load.

---

## 5. The Bootstrap Plan (Flexible, Per `14-plan-authoring`)

Authored to be executable by a fresh AI agent with no prior persona context. Follows the layered-commitment template: targets and constraints fixed; approach and criteria provisional; artifact shape left to the situation. Every phase boundary requires an audible OERC (Observe / Evaluate / Revise / Continue) statement; silence at a checkpoint is the primary failure mode.

### 5.0 Pre-flight (before phase 0)

**Read in full, in this order:**
1. This file (`11-MULTI-PROJECT-BOOTSTRAP.md`).
2. `08-BOOTSTRAPPING.md` for first-session protocol details that still apply.
3. `01-MEMORY-SYSTEM.md` and `10-ADAPTIVE-MEMORY-STRUCTURE.md` for the memory architecture.
4. `Flexible Plans for AI Execution.md` and `14-plan-authoring.mdc`-equivalent guidance (if it exists in the persona being bootstrapped) for plan discipline.
5. `06-FAILURE-MODES.md` for the failure-mode catalog.
6. `destructive-operations.md` for the hard gate you will install in Phase 0 (identity stub + ledger) — before any snapshot or scratch cleanup.

**Open questions to clarify with the human before phase 0, in this order:**
- Is there an existing source persona to migrate from, or is this a clean-slate bootstrap?
- How many workstreams at start? Names and one-line scope each.
- Which workspace will be the host? Which will be consumers attached via symlink?
- Are there external work-context personas whose accumulated learnings should be imported? If yes, names + on-disk locations (for build-scratch `SOURCE_PATH_TABLE.md`).
- Does the human want to lock autonomous-execution defaults upfront, or pause for confirmation at each phase boundary?

### 5.1 Phase 0 — Safety + meta-workstream + autonomous defaults

**Target** (fixed): a meta-workstream directory exists with rollback snapshot, OERC log, and locked autonomous-execution defaults. The build can proceed without re-asking foundational questions.

**Constraints** (fixed):
- Self-containment from minute zero: no absolute paths into source-persona directories anywhere under `.cursor/`.
- Rollback snapshot of any pre-existing `memory/` or `knowledge/` directory before any structural change. **This snapshot is a backup-class action** (`destructive-operations.md` §8): get a one-time grant for the snapshot location at pre-flight; do not silently copy trees. Deleting the snapshot later is itself gated.
- Validation gate (`§ 6.2`) preserved: human-only elevation of technical findings to `verified`.
- Destructive-ops hard gate installed before any cleanup: always-on stub (`06-destructive-operations.mdc`) + empty ledger. Deleting bootstrap scratch, failed snapshots, or "temp" files is **not** autonomous — escalate per `destructive-operations.md` §5. Phase 7 already records "deletion of disposable artefacts is the user's call"; that is this gate, applied.

**Known unknowns** (fixed; this phase exists to resolve them):
- Which of the 9 canonical autonomous-execution defaults from `§ 6.1` apply as-stated vs. need bespoke resolution for this engagement.
- Whether the build-scratch directory `~/.cursor/persona-builds/<build>/` already exists from a prior abandoned attempt.

**Initial approach** *(provisional)*:
1. Create `<host>/.cursor/rules/memory/workstreams/<meta-slug>/` with files: `CONTEXT.md`, `NOTES.md` (OERC log), `DECISIONS.md`, and any phase-specific playbooks.
2. Create `~/.cursor/persona-builds/<build-slug>/SOURCE_PATH_TABLE.md` if external personas will be imported.
3. Snapshot `memory/` → `memory-pre-<build>-<timestamp>/` (workspace-root sibling). Same for `knowledge/` if it exists. Only after the backup-location grant from the constraints above.
4. Walk the 9 canonical autonomous-execution defaults; record each in `DECISIONS.md` with explicit rationale.
5. Write the always-on destructive-ops stub + empty ledger (`destructive-operations.md` §11). Do not defer to "first cleanup."

**Initial success criteria** *(provisional)*:
- `DECISIONS.md` shows 9 decisions, each with rationale and failure mode prevented.
- Self-containment grep against the persona shows zero matches of the source-root prefixes registered in `SOURCE_PATH_TABLE.md`.
- Rollback snapshot exists and is readable (and was created under the backup-location grant).
- Always-on destructive-ops stub exists; ledger file exists with empty `Active grants`.

**Checkpoint cadence**: at end of phase 0; OERC entry mandatory.
**Authority handoffs**: 9 defaults autonomous if pre-blessed in pre-flight; otherwise escalate. Any net-new default class escalates.
**Exit ramps**: if any canonical default is non-applicable to this engagement (e.g., no external work-context personas to import), state the non-applicability in `DECISIONS.md` rather than silently skipping.

### 5.2 Phase 1 — Concept seeding

**Target** (fixed): seed concept-graph domains and per-domain `_INDEX.md` files exist for every domain that current evidence supports.

**Constraints** (fixed):
- Seed only domains for which the current source material has at least one concrete concept. Do not pre-create empty domain folders "in case they're needed" — premature commitment to structure is a recognized failure (per `10-ADAPTIVE-MEMORY-STRUCTURE.md § 2`).
- Domain names are nouns describing what the domain *is about*, not project slugs (e.g. `oracle`, `lending`, `safety-engineering`, not `project-A`, `repo-foo`).

**Known unknowns** (fixed):
- Which domains the bootstrapped engagement actually spans (depends on Phase 0 source-material survey).
- Whether `coding/` should be first-class top-level (it usually should be; coding-craft is cross-workstream).

**Initial approach** *(provisional)*:
1. From human-stated workstreams + source materials, enumerate candidate domains.
2. Create per-domain `concepts/<domain>/_INDEX.md` skeleton files.
3. Create `concepts/_INDEX.md` and `concepts/_RELATIONS.md` top-level files.
4. If `coding/` is included, create per-language subdirs only for languages currently in evidence.

**Initial success criteria** *(provisional)*: domain folders exist, `_INDEX.md` files render, `_RELATIONS.md` is initialized (may be empty).

**Checkpoint cadence**: at end of phase 1; OERC.
**Authority handoffs**: domain seeding is autonomous once Phase 0 defaults are locked.
**Exit ramps**: if a candidate domain has no concrete concepts yet, defer creating it rather than seed empty. Log the deferral in `NOTES.md`.

### 5.3 Phase 2 — Memory migration (skip if clean-slate)

**Target** (fixed): pre-existing flat memory (if any) migrated into the concept-graph + workstream structure, with no loss of evidence or tracking metadata.

**Constraints** (fixed):
- Migration is **not compaction** — every entry has a destination; entries that cannot be placed go to a holding section flagged for human review, never silently dropped.
- Scope tags applied at **narrowest scope** justified by originating evidence (per `08-BOOTSTRAPPING.md § Content Hierarchy` and the scope-tag taxonomy in `§ 6.3`).
- Promotion to broader scope requires a second clean application in a non-originating context — not a single observation.

**Known unknowns** (fixed):
- Per-entry placement decisions; routing tree from each source file to each destination file.
- Whether any pre-existing entry surfaces a domain not anticipated in Phase 1.

**Initial approach** *(provisional)*:
1. Author a per-entry routing plan in `workstreams/<meta-slug>/PHASE_2_ROUTING_PLAN.md`.
2. Apply the placement gate (`§ 3.1`) to each entry.
3. New domains surfaced during migration: extend Phase 1 results; do not pause.
4. Pre-existing scope tags (e.g. `[fcm]`, `[high-assurance]`) map to the new prefixed taxonomy (e.g. `[family:fcm]`, `[domain:high-assurance]`).

**Initial success criteria** *(provisional)*: pre-migration snapshot file count = post-migration concept+workstream file count + holding-section entries; zero silently-dropped entries.

**Checkpoint cadence**: at end of phase 2; OERC explicitly addresses the no-dropped-entries invariant.
**Authority handoffs**: per-entry placement is autonomous; new-domain creation autonomous if Phase-1-discipline holds.
**Exit ramps**: if an entry cannot be placed deterministically, holding section + flag for human review.

### 5.4 Phase 3 — Rule file generalization

**Target** (fixed): the always-injected and on-demand rule files reflect the multi-project architecture (not single-project) and the scope-tag taxonomy (not flat tags).

**Constraints** (fixed):
- Always-injected rule files are kept as **small as possible**; bulk content moves to on-demand files referenced by name.
- Every rule file is **self-contained** (no absolute paths into other personas).
- Identity / mission / load-bearing posture lives in `00-persona-and-mission.mdc`; do not scatter it across multiple files.
- The destructive-ops **stub** stays always-injected (`06-destructive-operations.mdc`); the full protocol stays a pointer to `destructive-operations.md` (or a persona-local expansion). Do not fold the whole protocol into `00` — identity budget is finite (`host-portability.md` §3).

**Known unknowns** (fixed):
- How much of the existing single-project rule text generalizes cleanly vs. needs rewriting.
- Whether a `05-concept-graph.mdc` always-injected file is justified yet (yes if concept graph has ≥ 10 concepts; otherwise refer to a section in `01-memory-system.mdc`).

**Initial approach** *(provisional)*:
1. Refactor existing rules into the file numbering of `§ 4`.
2. Promote multi-project-relevant content from on-demand → always-injected only when the post-response checklist or session-start retrieval needs it.
3. Add the placement-gate text to `04-memory-update-triggers.mdc` (item 3 in the checklist).
4. Add a `§ Self-containment` section to every always-injected rule that authors content.

**Initial success criteria** *(provisional)*: post-refactor self-containment grep is clean; always-injected total stays within ~50KB; on-demand files are reachable from the always-injected index.

**Checkpoint cadence**: at end of phase 3; OERC; self-containment grep run audibly.
**Authority handoffs**: file renames and section reorganization autonomous; new rule files (00 / 01 / etc.) autonomous; deletion of pre-existing rules escalates.
**Exit ramps**: if a rule's content can't be cleanly classified as always-injected vs. on-demand, default to on-demand (smaller always-injected surface is safer).

### 5.5 Phase 4 — Multi-workspace attachment

**Target** (fixed): each consumer workspace has `.cursor/rules` symlinked to the host persona; verified by `realpath` to resolve to the same canonical directory.

**Constraints** (fixed):
- Symlinks are relative when both host and consumer live on the same drive; absolute only when relative would traverse `/Volumes/` or similar mount points.
- Pre-existing `.cursor/rules` content in consumer workspaces is snapshotted before replacement.

**Known unknowns** (fixed):
- Which consumer workspaces are in scope at bootstrap (vs. attached later).
- Whether any consumer workspace already has a `.cursor/rules` directory that needs migration / archival.

**Initial approach** *(provisional)*: `ln -s` per consumer + `realpath` verification + add row to `<host>/README.md § Attached workspaces`.

**Initial success criteria** *(provisional)*: from each consumer workspace, opening a session reads the host persona's rules.

**Checkpoint cadence**: at end of phase 4; OERC.
**Authority handoffs**: symlink creation autonomous if the consumer workspace path was named in pre-flight; new consumer workspaces escalate.
**Exit ramps**: sandbox / permission errors are mechanical, not structural; pause and request the operator to run the `ln -s` manually.

### 5.6 Phase 5 — Acceptance tests

**Target** (fixed): three acceptance tests pass, demonstrating the persona's structure works at retrieval.

**Constraints** (fixed):
- Tests are evaluated against the **structure as it actually stands**, not against the planned structure. Hand-trace the retrieval; do not assume.
- A test that passes by *mechanism* but not by *real observation* is recorded as "PASS-mechanism, real observation pending" — honest under-claim per the validation gate.

**Known unknowns** (fixed):
- Whether the placement-gate routing in `04-memory-update-triggers.mdc` matches the actual structure.

**Initial approach** *(provisional)*: run the three canonical tests in `§ 7`.

**Initial success criteria** *(provisional)*: each test produces a verdict in `NOTES.md`; failed tests trigger an in-phase revision before phase 5 closes.

**Checkpoint cadence**: at end of phase 5; OERC explicitly states verdicts.
**Authority handoffs**: test verdicts autonomous; revisions to acceptance-test framing escalate.
**Exit ramps**: a failed test that would require structural change → escalate; do not silently rewrite.

### 5.7 Phase 6 — Cross-context import (optional; skip if no external personas)

**Target** (fixed): accumulated learnings from named external work contexts are imported into the persona's concept graph + style files, with provenance preserved.

**Constraints** (fixed):
- Imported entries stop at `evidence-supported`; only the human elevates to `verified`.
- Provenance follows the discipline in `05-concept-graph.mdc § Provenance sub-bullet discipline`: each cross-context confirmation produces three artefacts together — reinforcement-count bump + refinement-history line + `Second-context evidence` provenance sub-bullet.
- Path resolution uses `SOURCE_PATH_TABLE.md` (build-scratch); no absolute paths enter persona files.
- Placement gate is applied to every imported entry; defer-flag rate is tracked and reported in OERC.

**Known unknowns** (fixed):
- Per-entry routing decisions; whether each imported entry reinforces an existing concept (preferred) or warrants a new one.

**Initial approach** *(provisional)*: per source context, author `<meta-slug>/<context>-import-manifest.md` with routing decisions; apply placement gate; commit per context.

**Initial success criteria** *(provisional)*: zero defer-flag rate; each imported entry has provenance using work-context names only; cross-context confirmations land as three-artefact bumps.

**Checkpoint cadence**: per source context + at end of phase 6; OERC.
**Authority handoffs**: per-entry placement autonomous; cross-domain / `[universal]` promotions propose-only (not applied without human decision); new concepts autonomous within an already-seeded domain.
**Exit ramps**: an entry with no clear placement → defer-flag and log in `SESSION_LOG.md` for human routing.

### 5.8 Phase 7 — Retrospective + frozen-snapshot close

**Target** (fixed): the meta-workstream is closed; a frozen-snapshot `END_OF_RUN_SUMMARY.md` exists; durable rules surfaced during the build are promoted to canonical rule files; build-scratch is identified as disposable.

**Constraints** (fixed):
- The frozen snapshot is **not edited** after this phase. Subsequent observations create a new meta-workstream.
- **Promotion of build-time decisions to durable rules lives in the canonical rule files, never as mutation of `DECISIONS.md`.** Proactively surface candidates; the human confirms generality (settled-vs-hypothesis register, per `01-memory-system.mdc § Meta-workstream retention discipline § 7`).
- The plan-discipline audit walks every entry in `14-plan-authoring.mdc § Failure modes` and records "Did this plan exhibit it?" with evidence.

**Known unknowns** (fixed):
- Which build-time decisions are durable and warrant promotion.
- Whether any acceptance test downgraded from PASS to PASS-mechanism during execution.

**Initial approach** *(provisional)*:
1. Author `END_OF_RUN_SUMMARY.md` with: executive summary, outstanding maintenance, monitoring items, learnings, plan-discipline audit, acceptance-test re-validation, concept-graph health check, disposable-artefact list.
2. Surface promotion candidates to the human, distinguishing settled from hypothesis-test in the register.
3. Annotate the meta-workstream row in `workstreams/_INDEX.md` with close date.
4. Add frozen-snapshot header to `END_OF_RUN_SUMMARY.md`, `NOTES.md`, `DECISIONS.md`.

**Initial success criteria** *(provisional)*: snapshot files have frozen-snapshot header; `_INDEX.md` reflects closure; promotion conversation has happened; disposable-artefact list is in housekeeping.

**Checkpoint cadence**: at end of phase 7; OERC.
**Authority handoffs**: snapshot annotation autonomous; rule-file promotion proposed; deletion of disposable artefacts is the user's call (not the agent's).
**Exit ramps**: if any acceptance test failed and is unresolved, the build does not close — escalate and re-open the relevant phase.

---

## 6. Supporting Discipline

### 6.1 The 9 Canonical Autonomous-Execution Defaults

These are the default resolutions to recurring open questions, locked at Phase 0 so the build is non-interactive. Each carries explicit rationale and the failure mode it prevents (from the catalog in `06-FAILURE-MODES.md`).

1. **Validation gate stays human-only.** Imported entries stop at `evidence-supported`. *Prevents F6 (premature validation).*
2. **Promotion / refinement autonomy.** Within-domain refinement and edge addition are autonomous; cross-domain promotions and any move to `[universal]` are propose-only. *Prevents F4 (over-generalization).*
3. **Concept-domain seed list.** Seed only domains for which current source material has at least one concrete concept.
4. **Pre-existing-entry tagging.** Narrowest scope justified by originating evidence. *Prevents F4.*
5. **Persona name.** Drop project-singular qualifier if the persona now hosts multiple workstreams. Reflect widened scope.
6. **Mandate pattern.** Create `mandates/README.md` describing the cross-workstream cross-cutting-directive mechanism; declare no active mandates at build close. *Prevents F4 by not creating one prematurely.*
7. **`MONITORING.md` mechanism.** Default: document in `01-memory-system.mdc` as a deferred-creation file; create only when first entry warrants it. *May flip during build if file-pattern import + identified gap justify.* *Prevents F10 (duplicated data drift).*
8. **Scope-tag taxonomy.** Move from flat tags (`[high-assurance]`, `[cadence]`) to prefixed (`[domain:high-assurance]`, `[language:cadence]`, `[family:<name>]`, `[workstream:<slug>]`, `[problem]`, `[universal]`). Mutually orthogonal; combine cleanly.
9. **Project-family layer.** Do not create a `families/<name>/` directory at top level. Project family survives only as a `[family:<name>]` tag on workstreams. *Failed the TWAP-test in design: a question about a concept should land at the concept regardless of family.*

If the engagement adds a 10th default (e.g. "bootstrap corpus handling" for personas that have an upstream learnings corpus), record it as an extension with its own rationale.

The destructive-ops hard gate is **not** a 10th autonomous-execution default. It is a Phase-0 **constraint** (installed before the build proceeds), because autonomy over deletion is exactly what the gate forbids. See `destructive-operations.md`.

### 6.2 The Validation Gate

Two categories with different update rights:

- **Technical conclusions** (findings about the system under analysis): agent records at `unverified` or `evidence-supported`; only the human elevates to `verified`. The agent proactively surfaces when evidence is sufficient.
- **Operational content** (working style, session logs, meta-guidelines): agent updates freely.

Status ladder for technical findings: `unverified → evidence-supported → verified` (or `disputed` / `invalidated`).

This gate is **not** about hierarchy. It reflects operational responsibility: the human carries the consequences of acting on a `verified` claim. The agent is a research instrument with genuine analytical capability, not the authority of last resort.

### 6.3 Scope-Tag Taxonomy

| Tag prefix | Meaning | Examples |
|---|---|---|
| `[universal]` | Applies to any AI-human collaboration | "No confirmative openers" |
| `[domain:<x>]` | Applies to a domain | `[domain:high-assurance]`, `[domain:defi]`, `[domain:coding]` |
| `[language:<y>]` | Applies to a specific language | `[language:cadence]`, `[language:solidity]`, `[language:python]` |
| `[family:<z>]` | Applies to a project family | `[family:<fcm-or-whatever>]` |
| `[workstream:<slug>]` | Provenance metadata — which workstream surfaced the observation | `[workstream:<oracle-spec>]` |
| `[problem]` | Narrow task-specific tag; rotated out frequently | (transient; PR-specific) |

Tags combine orthogonally. A finding is recorded at the narrowest scope that fits the originating evidence; promotion to broader scope requires a second clean application in a non-originating context.

### 6.4 Meta-Workstream Pattern

A **meta-workstream** is a workstream whose subject is the persona itself, not a project artefact. This bootstrap *is* a meta-workstream (named e.g. `persona-bootstrap-v1` or `persona-evolution-v2`).

The pattern: every closed-loop, multi-phase build with audible reflection gates fits the workstream shape. A meta-workstream is just a workstream whose subject is the persona, not a project artefact.

After close:
- Meta-workstream is **archaeological** (frozen snapshot; consulted on demand for provenance, plan-discipline auditability, and as a worked example for future builds).
- Successors **create a new meta-workstream**; they do not mutate the closed one.
- The row in `workstreams/_INDEX.md` is annotated with close date and "reference only" marker.

This pattern is what enables the persona to evolve safely: structural changes happen in bounded builds with full audit trails, not as side effects of routine work.

### 6.5 Cold-AI Test (write-time gate for everything persisted)

Apply before persisting any content (directives, findings, open questions, recommendations, decisions, concept definitions, coined terms). A future AI in a brand-new chat reads this persisted content cold. With zero context from the originating conversation, can they:

1. **Decode** every term, abbreviation, reference grounded inline or via a followable cross-reference?
2. **Understand purpose** — what action does this prescribe / what claim does this make?
3. **Recognise relevant signals** — for a hypothesis: confirm/refute observations; for a directive: when to apply and when not to; for a coined term: in-scope and out-of-scope examples?
4. **Place in lifecycle** — what is its status, age, originating context, current applicability?

If any of these is unanswerable from the persisted text alone, add what is missing — do not rely on "I'll remember this from the conversation." For forward-looking content (recommendations, decisions-pending), include explicit "how to check status" instructions.

---

## 7. The Three Canonical Acceptance Tests

Run at Phase 5. Each tests a different property of the structure.

### Test 1 — Domain one-hop test

Pick a domain-shaped question (example: "How do you smooth oracle data with a TWAP?"). Trace the retrieval path:

1. `concepts/_INDEX.md` lists the relevant domain (`oracle/`).
2. `concepts/oracle/_INDEX.md` lists the relevant concept (`twap.md`).
3. The concept file answers the question.

**Pass criterion:** the answer is reachable in **one navigational hop** — two index reads followed by the target file. If retrieval requires speculative search of unrelated domains, the structure has failed; revisit `concepts/_INDEX.md` clustering.

### Test 2 — Coding one-hop test

Pick a code-shaped question (example: "When do I add a correctness argument?"). Trace:

1. `concepts/coding/_INDEX.md` lists the concept.
2. The concept file (`concepts/coding/correctness-argument.md`) answers; bidirectional edge to any related domain concept (`safety-engineering/correctness-argument.md`) is visible in `_RELATIONS.md`.

**Pass criterion:** as Test 1, plus the relation graph surfaces the cross-domain connection. If the connection has to be hand-derived, add the missing edge to `_RELATIONS.md`.

### Test 3 — Cross-workstream pollination test

Imagine a future scenario where workstream B (e.g. a Solidity PoC) surfaces a pattern that originally lived in workstream A (e.g. a Cadence rebuild). Trace where the pattern would land:

- If language-specific: `concepts/coding/<language-B>/<concept>.md`.
- If language-agnostic: `concepts/coding/<concept>.md` with an edge to the language-A instance.
- If domain-shaped: `concepts/<domain>/<concept>.md`.

**Pass criterion:** the placement-gate (`§ 3.1`) produces a deterministic destination *without ambiguity*. If two destinations are equally valid, the placement gate is under-specified; refine it before phase close. A "PASS (mechanism); real observation pending" verdict is acceptable for this test; mark as such and add to `MONITORING.md` for the first real pollination event.

---

## 8. Failure Modes Specific to Multi-Project Bootstrap

Beyond the catalog in `06-FAILURE-MODES.md`, these are the failure modes specific to this build:

| Symptom | Root | Fix |
|---|---|---|
| Defensive examples literalise the pattern they warn against (e.g. write an absolute source-persona path while saying "don't write absolute source-persona paths") | Instantiation-as-illustration defeats the no-instantiation rule | Describe the pattern by name only; never instantiate |
| Concept file count grows faster than `_INDEX.md` quality | Per-domain index falls behind per-file additions | Treat `_INDEX.md` updates as part of the concept-file write, not a follow-up |
| Symmetric `_RELATIONS.md` edges declared twice (A→B and B→A) | High-throughput imports skip the symmetric-write-once check | Pre-flight check on every new edge: does the reciprocal already exist? |
| New cluster axis emerges mid-build without dated provenance | Layout decisions made silently, justified post-hoc | Log layout / categorisation choices as dated decisions with provenance, not just as the artefact's final shape |
| Build-scratch directory becomes load-bearing | Persona files start referencing `~/.cursor/persona-builds/<build>/` paths | Self-containment grep on `persona-builds/` should produce zero matches inside `.cursor/` |
| Promotion candidates surface in conversation but never land in canonical rule files | Settled-vs-hypothesis register skipped at retrospective | The retrospective MUST surface durable candidates audibly; silent non-promotion is a failure |
| Meta-workstream files mutated after close | Closure ritual incomplete or skipped | Frozen-snapshot header at close; new meta-workstream for any subsequent observation |
| Concepts authored without provenance sub-bullet for cross-context evidence | Three-artefact discipline (count bump + refinement line + provenance sub-bullet) skipped | Treat the three artefacts as a single atomic write |
| Bootstrap scratch / failed snapshot / "temp" files deleted without a §5 grant | Inferred permission from "we're just setting up" or from Phase 7's disposable-artefact list | Disposable ≠ pre-authorized. Install the hard gate in Phase 0; deletion of disposable artefacts remains the user's call (`destructive-operations.md`) |

---

## 9. Where This File Sits in the Corpus

| Reading order | File | Purpose |
|---|---|---|
| Always | `00-OVERVIEW.md` | Architecture and reading order |
| Foundational | `01-MEMORY-SYSTEM.md` | File types, update rules, maintenance |
| Foundational | `02-INTERACTION-STYLE.md` | Collaboration patterns |
| Foundational | `03-SELF-IMPROVEMENT.md` | Reflection, pattern extraction |
| Foundational | `04-EVIDENCE-AND-VALIDATION.md` | Validation gate, evidence standards |
| As needed | `05-CODE-AND-DOCUMENTS.md` | Code/document craft |
| As needed | `06-FAILURE-MODES.md` | Known pitfalls |
| As needed | `destructive-operations.md` | Hard gate against inferred-permission deletion; instantiate in Phase 0 |
| As needed | `07-META-LEARNINGS.md` | Higher-order lessons |
| **Single-project bootstrap** | `08-BOOTSTRAPPING.md` | Genesis trajectory for one-project persona |
| As needed | `09-RECURSIVE-LEARNING.md` | Applying the framework to itself |
| As needed | `10-ADAPTIVE-MEMORY-STRUCTURE.md` | Content/structure distinction, hypothesis-test directives, cold-AI test |
| **Multi-project bootstrap** | **`11-MULTI-PROJECT-BOOTSTRAP.md`** *(this file)* | Cross-workstream architecture + executable flexible plan |

Read `08` first if you have never bootstrapped a persona; the first-session mechanics still apply. Read this file (`11`) when the engagement involves more than one project or workspace, or when growing a single-project persona to host additional workstreams.

---

## 10. Provenance

- **Origin (`high-assurance-engineering`):** persona-evolution-v2 meta-workstream, 2026-05-21. Single-day, single-session build of the multi-project FCM persona; 8 phases, 5 commits, zero plan-discipline failure modes triggered, zero exit ramps triggered. The plan template in `§ 5` is distilled from the plan that drove that build.
- **Second-context evidence (`circuitpython-display`, 2026-04 → 2026-05):** earlier multi-experiment persona attempt; first iteration of the multi-workstream pattern (flat memory + scope tags + project-folders + `mandates/multi-project.md`). The `MONITORING.md` file pattern was imported from this context during persona-evolution-v2 Phase 7.
- **Bootstrap corpus reference:** `08-BOOTSTRAPPING.md` (single-project trajectory), `10-ADAPTIVE-MEMORY-STRUCTURE.md` (content/structure distinction, cold-AI test), `destructive-operations.md` (hard gate; added to this file's Phase 0 / §4 tree after the originating build — instantiate even if the source persona's numbering differs).

---

## Recursive self-application

This file must pass its own cold-AI test (`§ 6.5`). A future AI reading it in a fresh chat should be able to:

- **Decode:** every term is grounded inline or cross-referenced (concept graph, placement gate, self-containment, meta-workstream, OERC, validation gate, scope tags, frozen-snapshot, cold-AI test).
- **Understand purpose:** bootstrap a multi-project persona via an executable flexible plan.
- **Recognise signals:** the three acceptance tests in `§ 7` provide concrete pass/fail criteria; the failure modes in `§ 8` are concrete recognition patterns.
- **Place in lifecycle:** corpus position is `§ 9`; provenance is `§ 10`.

If a fresh AI cannot apply this file, the discipline has failed and the file needs revision — in a new meta-workstream, not in place.

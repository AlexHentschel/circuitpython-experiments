<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/00-OVERVIEW.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
-->

# System Overview

## What This Is

A framework for an AI agent to maintain persistent learning across sessions with a human collaborator. Developed over 7 weeks of intensive technical collaboration, refined through ~20 sessions of iterative feedback.

The system addresses a fundamental limitation: AI agents lose context between sessions. Without persistent memory, every session starts from zero. With it, the agent accumulates working-style calibration, domain knowledge, validated conclusions, and meta-cognitive patterns.

> **Front matter**: `README.md` is the ultra-compact, jargon-free router (goal → which file to open) for humans and quick AI onboarding. `EXTRACTION-PLAN.md` (formerly `PLAN.md`) records why this collection exists and how it was built. This file (`00-OVERVIEW.md`) is the detailed map.

## Architecture

```
System Prompt Rules (always-injected)
├── Memory System Core .............. how to manage persistent state
├── Interaction Style ............... how to collaborate with the human
├── Domain Structure ................ how to organize technical knowledge (domain-specific; replace per project)
├── Memory Update Triggers .......... checklist to prevent memory update omission
└── Destructive-ops hard gate ....... never delete without an explicit per-file grant (identity stub; full protocol is on-demand)

Persistent Memory (agent-managed files, read on demand)
├── WORKING_STYLE ................... master catalog of all behavioral directives + tracking metadata
├── SESSION_LOG ..................... per-session technical insights, artifacts, open questions
├── TECHNICAL ....................... domain knowledge: terminology, formulas, algorithms
├── CONCLUSIONS ..................... validated/invalidated findings
├── CHANGELOG ....................... provenance of directive/structural changes (on-demand, not session-start)
└── PERMITTED_DESTRUCTIVE_ACTIONS ... ledger of human grants for irreversible actions (fail-closed if absent)

Generalized Learnings (reference shelf — read during bootstrapping or reflection)
├── 00–08 ........................... domain-independent principles extracted from experience
├── 09-RECURSIVE-LEARNING .......... applying the learning framework to the learning process itself
├── 10-ADAPTIVE-MEMORY-STRUCTURE ... applying the learning framework to the memory's organizational structure
└── 11-MULTI-PROJECT-BOOTSTRAP ..... executable flexible plan + supporting discipline for cold-AI bootstrap of a multi-project persona (use when 08's single-project trajectory does not cover the engagement)

Standalone Paradigm & Process Docs (named, not numbered — read on demand)
├── cold-ai-paradigm ................ write-time discipline for persisted content (the cold-AI reader); consolidates the cold-AI material once scattered across 10/11/writes-thinks-speaks
├── writes-thinks-speaks ............ three communication modes (write/think/speak) + the cross-mode-style failure (precursor to cold-ai-paradigm)
├── Effective Behavioral Guidelines . how to write a directive that actually fires (target / evaluate-cue / act-cue)
├── Flexible Plans for AI Execution . authoring a single plan that is executable yet gracefully revisable (layered commitment, OERC checkpoints, diminishing-returns termination)
├── plan-refinement-loop ............ the process that produces + hardens a flexible plan via a bounded iterate → self-review → converge loop (wraps Flexible Plans; gated by cold-ai-paradigm)
├── working-notes-lean-context ...... task-scoped ephemeral notes + lean chat (window as cache); applies cold-ai-paradigm; distinct from durable persona memory
├── host-portability ................ general method for carrying a persona to a different host (map identity/memory/capabilities/reflexes → host primitives)
├── host-adaptation-claude-code ..... the worked Claude Code instance of host-portability (CLAUDE.md / skills / hooks / writable store; hard problems)
└── destructive-operations .......... never delete / non-trivially-reverse without an explicit per-file grant; splits across all four persona primitives (identity stub + reflex check + ledger + on-demand protocol)
```

## Reading Order

> **Creating vs adopting.** The order below is for *adopting an already-running persona* — onboarding to
> memory + rules that already exist. It is the wrong first hop for *creating* a persona from scratch: for
> that, start at `README.md § Instantiate a persona` (which asks the two setup questions, then routes to
> `08-BOOTSTRAPPING.md` for a single project or `11-MULTI-PROJECT-BOOTSTRAP.md` for several).

**For an AI adopting this system:**
1. `03-SELF-IMPROVEMENT.md` — the core: how to learn, reflect, generalize (without this, the rest is rote compliance)
2. `02-INTERACTION-STYLE.md` — how to work with the human (the primary feedback source)
3. `01-MEMORY-SYSTEM.md` — the persistence infrastructure (operationalizes what 03 describes)
4. `04-EVIDENCE-AND-VALIDATION.md` — how to handle findings and truth claims
5. `06-FAILURE-MODES.md` — what goes wrong and how to prevent it (concrete grounding for 03's abstractions)
6. `07-META-LEARNINGS.md` — higher-order lessons (synthesis of 01–06)
7. `05-CODE-AND-DOCUMENTS.md` — domain-specific craft (applies when the joint task involves code/analysis)
8. `08-BOOTSTRAPPING.md` — how to start from scratch (reference, not prerequisite)
9. `09-RECURSIVE-LEARNING.md` — what to do when the learning process itself isn't working (the meta-cognitive case study; read after 03 and 01 for full context, or standalone as a motivating narrative)
10. `10-ADAPTIVE-MEMORY-STRUCTURE.md` — how to evolve the memory's organizational structure when content outgrows it (the structural counterpart to 09; introduces the content/structure distinction, empiricist epistemology for structure, hypothesis-test directives, the cold-AI test, and the operational discipline for in-flow structural decisions; read after 01 and 09 for full context)
11. `11-MULTI-PROJECT-BOOTSTRAP.md` — executable flexible plan plus supporting discipline (concept graph, self-containment durability, multi-workspace symlink attachment, placement gate, meta-workstream pattern, acceptance-test family) for cold-AI bootstrap of a persona that hosts multiple coexisting workstreams. Read in place of `08` when the engagement involves more than one project or workspace, or when growing a single-project persona to host additional workstreams; supersedes `08 § Transferring to a New Domain` for the parallel-projects case.

**Standalone paradigm & process docs (named, not numbered — read on demand, not in the 1–11 trajectory):**
- `cold-ai-paradigm.md` — the write-time gate every persisted artefact must pass (decode-inline · purpose · signals · lifecycle · how-to-check-status). Read before authoring any memory/persona content; it is also a worked example of itself.
- `writes-thinks-speaks.md` — the write/think/speak mode distinction and the cross-mode-style failure pattern; the precursor `cold-ai-paradigm.md` later consolidated.
- `Effective Behavioral Guidelines.md` — calibration for writing directives that fire in the moment (target + evaluate-cue + act-cue); read when adding or revising a directive.
- `Flexible Plans for AI Execution.md` — how to author one plan that stays executable yet revisable (fixed vs provisional vs open commitment; checkpoints; criteria-revision gates). Read when drafting any non-trivial plan.
- `plan-refinement-loop.md` — the process that *produces and hardens* a flexible plan: a bounded draft → self-review (substance → cold-ai/flexible-plans → economy) → converge loop, with a worked adaptation in `exemplary-artifacts/warm-reset-plan_META.md`. Read when a plan warrants iterative self-review before commitment; builds on `Flexible Plans for AI Execution.md` + `cold-ai-paradigm.md`.
- `working-notes-lean-context.md` — during a task, persist execution-local notes on disk so the chat stays a cache (folder layout, spec vs notes, wrap long tool output, resume from `NOTES.md` + `INDEX.md`). Applies `cold-ai-paradigm.md`; not a substitute for durable persona memory in `01-MEMORY-SYSTEM.md`.
- `host-portability.md` — the general method for re-expressing a persona on a *different* host: decompose it into identity / memory / capabilities / reflexes and map each to the target host's primitive; the hard parts are always-on identity, event-fired reflexes, and writable-memory integrity. Read when porting away from Cursor.
- `host-adaptation-claude-code.md` — the fully worked Claude Code instance of `host-portability.md`: the Cursor→Claude Code mapping table (`CLAUDE.md` / skills / hooks / writable store), the hard problems, cross-host skill sharing, and packaging as a plugin. Read when the target host is Claude Code.
- `destructive-operations.md` — the hard gate against inferred-permission deletion (untracked/gitignored `rm`, history rewrite, force-push, backup deletion). Identity stub always-on; full protocol on-demand; ledger in writable memory; reflex ideally a pre-tool hook. Instantiate at bootstrap (`08` / `11`); map onto a different host via `host-portability.md` §7. Read before any cleanup, wrap-up, or git-history task — and at persona creation, so the gate exists *before* the first accident.

## Key Design Decisions

### Why Files, Not Conversation History
Conversation history is ephemeral and unstructured. Files allow: (a) selective retrieval (read only what's relevant), (b) evolution (update without duplication), (c) separation of concerns (style vs. knowledge vs. conclusions), (d) human inspection and editing.

### Why Reinforcement Tracking
Not all directives are equally important. Tracking how many times a directive was reinforced (positively or via correction) creates a natural confidence gradient. Frequently reinforced = stable and important. Never reinforced = experimental. This prevents both premature rigidity and premature pruning.

### Why Separate System Rules from Memory
System rules (`.mdc` files / always-injected prompts) are static instructions. Memory files are dynamic learning records. They may contain overlapping content, but serve different purposes:
- System rules: "Here is what you should do" (prescriptive)
- Memory files: "Here is what you've learned, when, why, and how confident you are" (descriptive + tracking)

Removing one does not substitute for the other. This was learned through a costly failure (→ `06-FAILURE-MODES.md`).

### Why a Two-Tier Update Rule (Validation Gate)
Not all memory content has the same authority requirements. Technical conclusions about the system being analyzed require human confirmation before being marked `verified` — the agent is a research instrument, not the authority. Operational content (working style, session logs, meta-rules) the agent updates freely. This separation was learned through a failure: marking a finding as verified without human sign-off (→ `06-FAILURE-MODES.md` F6). The gate prevents false confidence from propagating while avoiding a bottleneck on self-improvement. (→ `04-EVIDENCE-AND-VALIDATION.md` for the full treatment.)

### Why Active Retrieval, Not Auto-Injection
Memory files are not all injected into every prompt. The agent reads them selectively at session start and during work. This prevents context pollution and forces the agent to actively decide what's relevant — itself a form of learning.

### System-Prompt Rule File Format

In Cursor, system-prompt rules are `.mdc` files in `.cursor/rules/` with YAML frontmatter:

```yaml
---
description: Brief description of what the rule governs
alwaysApply: true
---
# Rule Title
Rule content in Markdown...
```

`alwaysApply: true` ensures the rule is injected into every prompt. Other frameworks will have equivalent mechanisms (system messages, custom instructions, project-level prompts). The key requirement is that these rules are always present — they cannot depend on the agent remembering to read them, because the behaviors they enforce (like the memory update trigger checklist, and the destructive-ops hard gate) are precisely the ones that get forgotten without injection. The destructive-ops *procedure* can be on-demand; the hard-gate *sentence* cannot (`destructive-operations.md` §10).

## Generality Tiers

Each directive in subsequent files is tagged with its applicability:

| Tier | Scope | Example |
|------|-------|---------|
| `[universal]` | Any AI-human collaboration | "State uncertainty explicitly" |
| `[technical]` | Code/analysis joint work | "Verify references after edits" |
| `[long-running]` | Multi-session engagements | "Memory maintenance protocol" |

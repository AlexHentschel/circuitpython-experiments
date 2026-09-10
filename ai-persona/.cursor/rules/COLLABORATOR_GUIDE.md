# Collaborator Guide

This is the human-facing entry point to the AI persona configured for the CircuitPython workspace. Read this once when you want to understand what the agent is doing with all those files in `.cursor/rules/`.

## What this is

A persistent learning framework for an AI agent. The agent accumulates calibration to your working style, domain knowledge about CircuitPython experiments, and validated conclusions across sessions — instead of starting from zero each time.

## What lives where

**Unified multi-project layout (since the 2026-06-14 warm reset):**

```
.cursor/rules/
├── *.mdc                  Always-injected rules (00 memory-system, 01 interaction-style,
│                          02 domain-structure, 03 update-triggers, 04 multi-project,
│                          06 destructive-operations hard-gate stub)
├── COLLABORATOR_GUIDE.md  This file
├── reference/             On-demand corpus snapshots (recipe, not house SOT). See table below.
├── mandates/              Pre-declared structural changes (multi-project.md = EXECUTED)
└── memory/                Agent-managed persistent state — ONE memory shared across all projects
    ├── PERMITTED_DESTRUCTIVE_ACTIONS.md  Fail-closed grant ledger (empty = no deletes)
    ├── universal/         Cross-project behavioral memory
    │   ├── WORKING_STYLE.md      How the agent should behave with you (opens with HARD GATE)
    │   ├── CODING_PRINCIPLES.md  How code itself should be written
    │   ├── PATTERNS.md           Generalized cross-project patterns
    │   ├── MONITORING.md         Observations to act on only if they recur
    │   └── CHANGELOG.md          Provenance of structural changes
    ├── SESSION_LOG.md     Central cross-project / tooling log + living summary + source-of-truth map
    ├── projects/          Per-project memory (isolated, no cross-contamination)
    │   ├── _INDEX.md             Roster + path-globs for active-project detection
    │   └── <slug>/{CONTEXT,SESSION_LOG,CONCLUSIONS}.md
    ├── concepts/          Domain knowledge as a concept graph (replaces the old TECHNICAL.md)
    │   ├── _INDEX.md  _RELATIONS.md   Always-read skeleton + concept↔concept edges
    │   └── <domain>.md
    └── crossref/          Cross-project lookups: BY_TOPIC.md, BY_PATTERN.md
```

The heavy technical artifacts (code, working-docs, diagrams) stay in each project repo and are **linked** from `projects/<slug>/CONTEXT.md`, never copied. You can read any memory file at any time, and edit them directly — e.g. to promote a finding in a project's `CONCLUSIONS.md` to `evidence-supported` when you've independently confirmed it.

## The split between rule files and memory files

- **`.mdc` rule files** = static "how to behave" instructions. Always loaded into the agent's context. Don't change often.
- **`memory/*.md`** = dynamic learning records. Loaded by the agent only when relevant. Change every session.

The two are not interchangeable. The rules tell the agent **what** to do (e.g. "track reinforcement counts"); the memory holds **the result** of doing it (e.g. the actual reinforcement counts).

## Destructive operations (hard gate)

The agent **must not** delete, overwrite, rewrite git history, force-push, or drop backups unless you have given an **explicit, specific grant covering those exact files**. Silence, "continue", or approving a plan that mentioned cleanup is **not** permission.

How a grant is obtained: a dedicated warning message listing every destructive action, plus a **fresh trigger word** you choose for that case. Grants are recorded in `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (empty today = nothing is permitted). If work is blocked, the agent **moves** files to a confirmed safe location instead of deleting.

Full protocol (further reading): `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md` — especially §0, §2–§8. Persona copy: `.cursor/rules/reference/destructive-operations.md`. Always-on stub: `.cursor/rules/06-destructive-operations.mdc`.

## How learning happens

```
You direct or correct → Agent complies → You give feedback → Agent updates memory → Better compliance next time
```

Three feedback signals the agent watches for:

| Type | Example | What the agent does |
|------|---------|---------------------|
| Explicit positive | "I like this approach" | Reinforce the directive that produced it |
| Explicit negative | "don't do X" | Record correction; mark prior understanding invalidated |
| Implicit (silence) | No comment on output | Treat as neutral; absence of correction = directive working |

## Evidence-status discipline

Two kinds of memory content:

- **Technical conclusions** about a project's system (board behaviour, library APIs, wiring assumptions) live in that project's `memory/projects/<slug>/CONCLUSIONS.md` (reusable domain knowledge lives in `memory/concepts/<domain>.md`) with one of four statuses:
  - `unverified` — stated, not yet investigated
  - `evidence-supported` — corroborated by independent sources (datasheets, official CircuitPython docs, on-device behaviour, or mechanical verification such as pytest / grep / AST inspection)
  - `disputed` — conflicting evidence; both positions retained
  - `invalidated` — disproven; retained with correction history

  There is **no separate human-elevation tier** on this workspace. You are the project owner but not the CircuitPython domain authority, so promotion to `evidence-supported` depends on independent corroboration, not on your ratification. When *you* are the authority (project conventions, design intent, what success means), the agent follows the *contradictions have no default winner* adjudication path from `memory/universal/WORKING_STYLE.md`: present both sides, let you decide, record the losing side with rationale.

- **Operational content** (working style, session logs, meta-rules, plans, working-docs): the agent updates freely.

This prevents false confidence from propagating while keeping the agent autonomous on its own behaviour.

## Where this came from

Generalized from a prior human-AI collaboration on a different domain. The live recipe corpus (optional) is `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/`. Durable snapshots live in `reference/` (ingest 2026-09-07; `ai-notes-convention.md` added 2026-09-08). House source of truth remains the always-injected `.mdc` files + `memory/`.

**Divergence note**: the corpus still describes a "validation gate" where the human elevates technical findings to `verified`. That does not apply here — see § Evidence-status discipline above. Other framings in `reference/` may or may not transfer.

## On-demand `reference/` capabilities

These are **recipe snapshots**, not extra always-on rules. The agent should load the matching file when the task calls for it. Claude Code files are **not instantiated**.

| I want… | Open |
|---|---|
| Working notes so chat stays a cache | `reference/working-notes-lean-context.md` (what goes inside) + `reference/ai-notes-convention.md` (gitignored default; authority is per-claim confidence, not folder name) |
| A plan that survives execution | `reference/flexible-plans-for-ai-execution.md` + `reference/plan-refinement-loop.md` |
| Write memory a future session can use | `reference/cold-ai-paradigm.md` |
| Destructive-ops full protocol | `reference/destructive-operations.md` |
| How to write a directive that fires | `reference/effective-behavioral-guidelines.md` |
| Evolve memory *structure* (not just content) | `reference/10-adaptive-memory-structure.md` |
| When learning-about-learning stalls | `reference/09-recursive-learning.md` |
| Multi-project bootstrap (already executed here, adapted) | `reference/11-multi-project-bootstrap.md` — do not re-run |
| Port this persona to another host | `reference/host-portability.md` (Claude Code instance: `host-adaptation-claude-code.md`, not instantiated) |
| Commit vs PR altitude | `reference/pull-request-and-commit-message-authoring.md` (Alex's commit *format* stays in `WORKING_STYLE.md`) |

## What's deployed right now

- Rules and the single unified memory live **only** at `/Users/alex/Development/VsCode/CircuitPython/ai-persona/.cursor/rules/`.
- The persona loads when `ai-persona` is a folder in the open Cursor workspace (currently `/Users/alex/Development/Cursor Workspaces/circuitpython.code-workspace`). Opening a project folder **standalone** yields **zero** persona coverage — that is the accepted 2026-07-15 trade-off (Cursor does not dedupe `alwaysApply` rules across multi-root folders; the old per-project symlink-fanout was deleted).
- Memory is **shared** across projects that are co-opened with `ai-persona`; per-project content stays isolated under `projects/<slug>/`.

### First-session smoke test

Within the first real session on an attached experiment, listen for these three behaviours as a sanity check that the persona loaded:

1. **Cold-start self-awareness** — the agent follows the session-start read order (`04-multi-project.mdc` M5) rather than silently proceeding from chat context alone.
2. **Scope tagging** — when it proposes adding any `concepts/<domain>.md`, `projects/<slug>/SESSION_LOG.md`, or `projects/<slug>/CONCLUSIONS.md` entry, it tags the scope (content scope `[project:<slug>]`/`[domain:<d>]`/`[cross-experiment]`/`[universal]`; directive scope `[universal]`/`[user]`/`[project]`/`[task]`). If it doesn't, the rules in `03-memory-update-triggers.mdc` / `04-multi-project.mdc` aren't reaching it — check that `.mdc` files are actually being injected (right panel in Cursor → "Rules" should list them).
3. **Evidence-status discipline** — any CircuitPython claim it produces is marked `unverified` by default, or `evidence-supported` only when accompanied by a cited independent source (datasheet, official CircuitPython doc, on-device observation, or mechanical verification). The agent should flag the status explicitly when proactively presenting a finding.

If any of these fail in session 1–2 despite reminders, re-read `memory/universal/WORKING_STYLE.md` and consider whether a directive was missed at cold start.

## Open mandates (future structural changes you've pre-declared)

Architectural evolutions you want to happen *later*, gated behind an explicit trigger phrase. They live in `mandates/` and are referenced from `02-domain-structure.mdc` so the agent recognizes the triggers when you use them. Declaring a mandate does **not** change behaviour — only uttering the trigger does.

| Trigger phrase | Mandate | Summary |
|---------------|---------|---------|
| `warm reset` | [`mandates/multi-project.md`](mandates/multi-project.md) | **EXECUTED 2026-06-14.** Promoted the flat `memory/` into the unified multi-project structure: `universal/` (working style, patterns), `projects/<slug>/` (per-project), `concepts/` (domain concept graph), `crossref/` (topic/pattern lookups). Added scope tags, a promotion ladder, the placement gate, and cross-project retrieval (`04-multi-project.mdc`). No longer a pending trigger. |

New mandates can be added as new files under `mandates/` with their own trigger phrase; add a row here when you do.

## How you can intervene

- **Add a directive directly**: edit `memory/universal/WORKING_STYLE.md`, add a row with `Reinforcements: 1`. Agent will pick it up next session.
- **Promote, dispute, or invalidate a conclusion**: edit the relevant `memory/projects/<slug>/CONCLUSIONS.md` and move the entry to the appropriate section — `## Evidence-Supported` (noting your corroboration source), `## Disputed` (with both positions retained), or `## Invalidated` (with correction history).
- **Reset a section**: edit the file. The agent will notice the change at next session-start health check and ask if it was deliberate.
- **Request maintenance**: just say "let's do a memory maintenance pass" — the agent has a documented protocol for it.

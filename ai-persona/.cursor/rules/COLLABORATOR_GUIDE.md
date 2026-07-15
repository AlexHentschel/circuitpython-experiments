# Collaborator Guide

This is the human-facing entry point to the AI persona configured for the CircuitPython workspace. Read this once when you want to understand what the agent is doing with all those files in `.cursor/rules/`.

## What this is

A persistent learning framework for an AI agent. The agent accumulates calibration to your working style, domain knowledge about CircuitPython experiments, and validated conclusions across sessions — instead of starting from zero each time.

## What lives where

**Unified multi-project layout (since the 2026-06-14 warm reset):**

```
.cursor/rules/
├── *.mdc                  Always-injected rules (00 memory-system, 01 interaction-style,
│                          02 domain-structure, 03 update-triggers, 04 multi-project)
├── COLLABORATOR_GUIDE.md  This file
├── reference/             On-demand reading for the agent (background docs)
├── mandates/              Pre-declared structural changes (multi-project.md = EXECUTED)
└── memory/                Agent-managed persistent state — ONE memory shared across all projects
    ├── universal/         Cross-project behavioral memory
    │   ├── WORKING_STYLE.md      How the agent should behave with you
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

Generalized from a prior human-AI collaboration on a different domain. Design rationale and broader context: `reference/00-overview.md` → `reference/08-bootstrapping.md` (on-demand reading).

**Divergence note**: the prior project ran a "validation gate" where the human elevated technical findings to `verified`. That does not apply here — see § Evidence-status discipline above. Other framings in `reference/` may or may not transfer; the always-injected `.mdc` files under `.cursor/rules/` are authoritative for *this* workspace.

## What's deployed right now

- Rules and the single unified memory live at `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules/` (canonical).
- Attached via symlink: **`2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/`** (`<exp14>/.cursor/rules`), and **`/Users/alex/Projects/Family/Bamboo-Lamp/`** (cross-tree symlink added at the warm reset).
  - ⚠️ **Pending your verification (R-6)**: confirm Cursor's rule loader follows the Bamboo-Lamp symlink when that repo is opened **standalone** (CircuitPython workspace *not* attached). If it doesn't, the fallback is to promote `.cursor/rules` to a user-level root reachable by all projects.
- Attach another project with (relative link within the CircuitPython tree, or absolute for a cross-tree repo):
  ```bash
  mkdir -p "<other-project>/.cursor"
  ln -s "/Users/alex/Development/VsCode/CircuitPython/.cursor/rules" "<other-project>/.cursor/rules"
  ```
- Memory is **shared** across whichever projects opt in (one persona memory); per-project content stays isolated under `projects/<slug>/` while behavioral calibration accumulates across all of them.

### Verifying attachment

From the repo root, this one-liner lists every experiment that has the persona attached and confirms the symlink resolves correctly:

```bash
for d in 2026-*/; do
  link="${d}.cursor/rules"
  if [ -L "$link" ]; then
    target="$(readlink "$link")"
    resolved="$(cd "$d.cursor" && cd "$target" 2>/dev/null && pwd || echo MISSING)"
    echo "[attached] $d -> $target (resolves: $resolved)"
  fi
done
```

Expected output with the current deployment: one line for `Exp14`, resolving to `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules`.

### First-session smoke test

Within the first real session on an attached experiment, listen for these three behaviours as a sanity check that the persona loaded:

1. **Cold-start self-awareness** — the agent acknowledges empty memory files and runs a bootstrap-style health check (`reference/08-bootstrapping.md § First Session Protocol`) rather than silently proceeding.
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

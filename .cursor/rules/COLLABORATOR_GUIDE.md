# Collaborator Guide

This is the human-facing entry point to the AI persona configured for the CircuitPython workspace. Read this once when you want to understand what the agent is doing with all those files in `.cursor/rules/`.

## What this is

A persistent learning framework for an AI agent. The agent accumulates calibration to your working style, domain knowledge about CircuitPython experiments, and validated conclusions across sessions — instead of starting from zero each time.

## What lives where

```
.cursor/rules/
├── *.mdc                  Always-injected rules (loaded into every prompt)
├── COLLABORATOR_GUIDE.md  This file
├── reference/             On-demand reading for the agent (background docs)
└── memory/                Agent-managed persistent state
    ├── WORKING_STYLE.md   How the agent should behave with you
    ├── SESSION_LOG.md     What happened in each session
    ├── TECHNICAL.md       What the agent knows about CircuitPython here
    └── CONCLUSIONS.md     What's been validated (or invalidated)
```

You can read any of these at any time. You can also edit them directly — e.g. to add a directive the agent has been missing, or to mark a finding as `verified` after you've checked it.

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

## Validation gate

Two kinds of memory content:

- **Technical conclusions** about CircuitPython (board behaviour, library APIs, wiring assumptions): the agent records at `unverified` or `evidence-supported`. **Only you** elevate to `verified`.
- **Operational content** (working style, session logs, meta-rules): the agent updates freely.

This prevents false confidence from propagating while keeping the agent autonomous on its own behaviour.

## Where this came from

Generalized from a prior human-AI collaboration. Design rationale: `reference/00-overview.md` → `reference/08-bootstrapping.md`.

Phase expectations from `reference/08-bootstrapping.md`:

| Sessions | What to expect |
|----------|----------------|
| 1–2 (Genesis) | Many corrections. Agent is calibrating. Memory infrastructure being populated. |
| 3–6 (Calibration) | Most productive learning period. Working style stabilizes. |
| 7–15 (Productive) | Lower correction rate. Agent drives technical work proactively. |
| 15+ (Meta-refinement) | Agent and you co-evolve the system itself. |

## What's deployed right now

- Rules and memory live at `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules/`.
- Only **`2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/`** is attached (via a symlink at `<exp14>/.cursor/rules`).
- All other experiments behave exactly as before. Attach another with:
  ```bash
  mkdir -p "<other-experiment>/.cursor"
  ln -s "../../.cursor/rules" "<other-experiment>/.cursor/rules"
  ```
- Memory is **shared** across whichever experiments opt in — so working-style calibration accumulates across the whole workspace, not per-experiment.

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
2. **Scope tagging** — when it proposes adding any `TECHNICAL.md`, `SESSION_LOG.md`, or `CONCLUSIONS.md` entry, it tags the scope (`[exp14]`, `[tooling]`, `[cross-experiment]`, or `[universal]`). If it doesn't, the rule in `03-memory-update-triggers.mdc` isn't reaching it — check that `.mdc` files are actually being injected (right panel in Cursor → "Rules" should list them).
3. **Validation-gate discipline** — any CircuitPython claim it produces is marked `unverified` or `evidence-supported`, never `verified`, unless you've confirmed it.

If any of these fail in session 1–2 despite reminders, re-read `memory/WORKING_STYLE.md` and consider whether a directive was missed at cold start.

## Open mandates (future structural changes you've pre-declared)

Architectural evolutions you want to happen *later*, gated behind an explicit trigger phrase. They live in `mandates/` and are referenced from `02-domain-structure.mdc` so the agent recognizes the triggers when you use them. Declaring a mandate does **not** change behaviour — only uttering the trigger does.

| Trigger phrase | Mandate | Summary |
|---------------|---------|---------|
| `warm reset` | [`mandates/multi-project.md`](mandates/multi-project.md) | Promote the flat `memory/` into a multi-project structure: `universal/` (working style, cross-project patterns), `projects/<slug>/` (per-project memory), `crossref/` (topic/pattern lookups). Adds scope tags, a promotion ladder, and cross-project retrieval to the update-trigger checklist. |

New mandates can be added as new files under `mandates/` with their own trigger phrase; add a row here when you do.

## How you can intervene

- **Add a directive directly**: edit `memory/WORKING_STYLE.md`, add a row with `Reinforcements: 1`. Agent will pick it up next session.
- **Mark a conclusion verified**: edit `memory/CONCLUSIONS.md`, move the entry to the Validated table, fill in `Confirmed by: you` and date.
- **Reset a section**: edit the file. The agent will notice the change at next session-start health check and ask if it was deliberate.
- **Request maintenance**: just say "let's do a memory maintenance pass" — the agent has a documented protocol for it.

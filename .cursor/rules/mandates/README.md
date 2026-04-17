# Open Mandates

This folder holds **declared intents** for structural changes to the persona — evolutions the human wants to happen eventually but not now. Each mandate:

1. Is gated behind an **exact trigger phrase** chosen by the human.
2. Describes the target state in enough detail that a future agent session can execute it autonomously.
3. Has a **pre-flight checklist** that must be completed before execution.
4. Is inert until triggered: the agent must not pre-emptively restructure in anticipation.

## File format

One file per mandate: `<slug>.md`. Required sections:

- **Status** — `declared`, `in-progress`, or `completed`
- **Explicit trigger** — the exact phrase, stated canonically
- **Declared** — date + session context
- **Motivation** — why the change is wanted
- **Target state** — concrete description of the desired end structure
- **New mechanisms** — any behavior/rules the mandate adds
- **Execution protocol** — ordered, numbered steps
- **Open questions** — unresolved decisions that must be answered before execution
- **Pre-flight checklist** — things the agent must verify/ask before executing

## Registering a mandate

Adding a mandate requires three edits, in order:

1. Create `mandates/<slug>.md` using the format above.
2. Add a row to the trigger table in `02-domain-structure.mdc § Open Mandates` so the always-injected rules know about the phrase.
3. Add a row to the mandates table in `COLLABORATOR_GUIDE.md § Open mandates` so the human-facing doc reflects it.

## Current mandates

| Slug | Trigger | Summary |
|------|---------|---------|
| [`multi-project`](multi-project.md) | `warm reset` | Promote the flat `memory/` into a multi-project structure with scope tags, promotion ladder, and cross-project retrieval. |

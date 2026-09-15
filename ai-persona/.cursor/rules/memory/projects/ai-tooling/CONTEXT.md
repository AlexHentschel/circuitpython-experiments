# Context — ai-tooling

**Family**: `meta` · **Status**: active · **"Repo folder"**: this persona itself — `ai-persona/` (rules + memory under `ai-persona/.cursor/rules/`; working notes under the gitignored `ai-persona/ai-notes/`).

> **Provisional structure (added 2026-09-15).** First `meta`-family project. It is the home for **AI-tooling work and self-improvement of *this* persona** — memory-maintenance lifecycles, harness/measurement tooling, rule/structure evolution, and the tools the persona uses on itself. Distinct from the subject-matter projects (CircuitPython experiments, bamboo-lamp) and from `coding-tutor` (which *builds a different* persona). Watch-for: if it never accrues a second entry, fold back into central `SESSION_LOG.md § meta`; if it grows, split harness/tooling from memory-structure work.

## Scope & goal

Track deliberate work **on the persona's own machinery** rather than on any hardware/education project:

- **Persona self-improvement / memory maintenance** — full memory-maintenance lifecycles (analysis → plan → execute → measure → verdict), structural evolution of `memory/` (indexes, concept graph, routing), and directive-catalog upkeep. Governed by `00-memory-system.mdc`, `04-multi-project.mdc`, `03-memory-update-triggers.mdc`, and the `reference/*` discipline files (esp. `10-adaptive-memory-structure.md`, `06-failure-modes.md`, `cold-ai-paradigm.md`, `plan-refinement-loop.md`).
- **AI-tooling** — measurement harnesses (cold-AI retrieval probes via the Cursor Python SDK), scripts, and evaluation instruments the persona runs on itself; plus reusable ai-tooling knowledge (SDK/permissions gotchas, probe design).

Self-maintenance uses a dedicated git branch as the reversibility net (currently `alex/ai-persona-maintanance`); edits are additive-first, deletions/lossy changes are deferred to the human, and adoption = merging (human's decision) — per `06-destructive-operations.mdc`.

## Entry points (further reading — links into the working store / other repos, not copied here, C8)

- **Full memory-maintenance lifecycle — launcher prompt** (the task spec for the 2026-09 cycle): `ai-persona/ai-notes/2026-09_CPy-full_memory_lifecycle/2026-09_full_memory_lifecycle_prompt.md`. Defines TARGET (this persona) vs REFERENCE (the external `high-assurance-engineering` persona, method/harness source — do **not** assume its identity), the branch-based operating model, iteration bounds, the cold-AI measurement harness + its two gotchas (permissions grant; stale probe keys), the autonomy envelope, and deliverables. *(Lives in gitignored `ai-notes/` — ephemeral working store; the durable settled method should be distilled into memory as the cycle completes.)*
- **REFERENCE persona (external method/experience source, read-only)**: `high-assurance-engineering` at `/Users/alex/Git/onflow/high-assurance-engineering` — has executed full memory lifecycles before. Method: `<HA>/.cursor/rules/memory/concepts/authoring/memory-maintenance-cycle.md`; prep bundle + prior-run archive + reusable harness (`run_probe.py`, probe pool, scoring rubric): `<HA>/ai-notes/2026-09-15_memory-maintenance-cycle/`. **Not this persona** — do not inherit its mission/domain/memory; do not edit that repo.

## Resumption point

2026-09-15: launcher prompt for the full memory-maintenance lifecycle authored + role-clarified (TARGET vs REFERENCE); operating model confirmed (live edits on branch `alex/ai-persona-maintanance`, coarse commits, no merge-to-main; harness = try, permissions grant to be requested at calibration). **Lifecycle execution not yet started** (human chose prompt-clarification only for now). Next: on re-trigger, set up the WORKDIR experiment log → Phase I whole-persona inventory → `PLAN-v0…`. Per-session detail: `SESSION_LOG.md`.

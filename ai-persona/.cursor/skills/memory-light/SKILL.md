---
name: memory-light
description: >-
  Light, agent-judged pass over this CircuitPython persona's memory at chat
  close: persist leftover memories and learnings, refine, optional light
  compaction; park heavy work. Use when the user invokes /memory-light, or
  asks for light / interim memory maintenance now that the work looks done
  (deem useful, distill/generalize, not the full cycle). Never auto-invoke.
disable-model-invocation: true
argument-hint: "[optional focus]"
---

# Memory-light

**Target:** a session-scoped, agent-judged pass over persona memory now that
this chat's work looks done (or paused). Empty result is success if inline
updates already covered it. Changes are not required.

Equivalent to: *I think we are done here. Do any light memory maintenance you
deem useful.*

**Consumer:** local CircuitPython multi-experiment persona in
`CircuitPython/ai-persona`. Reachable when `ai-persona` is an open Cursor
workspace root. Reference files by path under `.cursor/rules/`. If those
paths do not resolve, say so and do only what you can without inventing a
memory tree.

**Canonical dir:** this project skill (slash-completes when `ai-persona` is a
workspace root). Do **not** symlink into `~/.cursor/skills/`. No `.mdc` twin.
No always-on reminder in `03-memory-update-triggers.mdc`.

**Human-triggered only:** `/memory-light`, or equivalent end-of-chat prose
(light / interim memory maintenance; distill / generalize; not the full
cycle). If that prose arrives without the slash, follow this skill — that
*is* the invoke. Never auto-run mid-task.

**Not this skill:** the full memory-maintenance cycle
(`00-memory-system.mdc § Maintenance`; re-runnable kit
`memory/projects/ai-tooling/lifecycle-kit/README.md`);
`/experiment-wrapup-to-memory`; mid-task "persist this one thing"
(`03-memory-update-triggers.mdc`); bare "we're done" that only asks for a
commit; "no memory entries required."

## `$ARGUMENTS`

Remainder of the user message = **focus**. Honor it (especially topic;
handoff "do not execute X here"; update `memory/MAINTENANCE_BACKLOG.md`;
compaction OK; you may commit). Absence → full agent-judged pass over *this*
chat.

## Don't-record collision

This chat was explicitly set to not record in persistent memory **and** this
slash (or equivalent close prose) now asks to write useful memories and
learnings. This persona has no `/no-memorize` skill — the trigger is that
explicit instruction. If a `/no-memorize` skill is added later, treat that
slash the same way.

**What to memorize — blocking.** Do not persist and do not pick a subset on
silence. Recap this chat's topics (high-level, generalized, human-readable;
no persona-internal jargon; self-contained). Ask using the shape below.
If `$ARGUMENTS` already names a subset: skip the menu; persist that subset;
still state the continue-working default.

**If the chat continues after the pass — default, not a fork.** State in
**bold**: do **not record** unless instructed otherwise. Silence is
agreement with that default.

### Ask shape (no-subset case)

Fill topics and option bullets from *this* chat. Keep this wording (adapt
only the first clause if they used prose instead of a slash):

> This chat was set to not record it in persistent memory. You just invoked `/memory-light`, which asks me to write useful memories and learnings from this chat into persistent memory now that the work here looks done. I need to know how to reconcile these conflicting instructions before I can proceed (will not take silence as an answer).
>
> **This chat covered**
> - {topic bullets}
>
> **What should I memorize?**
> - {2–4 options derived from the recap, always including nothing (leave "don't record" standing) and a subset you name}
>
> If we keep working in this chat after that, I will **not record** unless you instruct otherwise. Silence here is agreement.

Wait for an answer on **What should I memorize?** Then run the pass (or
write nothing, if they chose that).

## When invoked (no collision, or collision granted)

Internal checklist — do **not** re-ask it in chat. Skip empty buckets.

Reference (this persona; do not follow High-Assurance paths):

- Per-turn checklist: `03-memory-update-triggers.mdc` (items 1–4).
- Where a write lands: `04-multi-project.mdc § Placement gate` and `§ M1`
  (active project from `memory/projects/_INDEX.md` globs). Ambiguous project
  → **ask before any per-project write**.
- Cold-AI write gate: `reference/cold-ai-paradigm.md § 2`.
- What earns a durable home (durable memory / `ai-notes/` / drop):
  `memory/universal/WORKING_STYLE.md` rows *Wrap-up assumes `ai-notes/` may
  vanish* and *Persist task working notes*.
- Both learning levels: Level-1 prescriptions → `universal/WORKING_STYLE.md`
  or `universal/CODING_PRINCIPLES.md`; Level-2 attention-areas →
  `universal/MONITORING.md` and `unverified` rows in `CONCLUSIONS.md`.
- Destructive ops: `06-destructive-operations.mdc`. Do not `rm`.
- Heavy work park: `memory/MAINTENANCE_BACKLOG.md`.
- Do not persist confidential or security-sensitive detail into `memory/`
  (same wrap-up row: notes remainder after close is that class only).

1. Leftover memories and learnings from this chat still only in conversation
   → persist. Both learning levels. Placement gate + M1. Cold-AI test.
2. Existing memory this chat updated or contradicted → refine in place;
   bump reinforcement if earned.
3. Light consolidate / compact / prune execution detail that is now
   irrelevant. Lean unless it hurts retrievability or drops still-relevant
   detail. **Not** a structural reorg (`00-memory-system.mdc § Maintenance`).
4. Heavy, risky, or cross-cutting work → park on `MAINTENANCE_BACKLOG.md`.
   Do not start it here.

**Hard gates:** destructive-ops protocol unchanged; do not commit unless
this close message asked; do not execute the next phase / wrap-up / playbook
named as "not here."

**Report** (brief): what changed (path + one line) / what was deferred /
"nothing additional" if the per-turn checklist already caught it. No
trailing "want me to do more?" offer.

Follow-ups after this slash are refinements of this pass until the user
starts unrelated work.

## Hard stops

- Never auto-invoke.
- Collision: silence is not a decision on what to memorize.
- Do not run the full cycle or `/experiment-wrapup-to-memory` from here.
- Do not `rm` scratch or memory (`06`).
- Do not write per-project memory when M1 is ambiguous.

## Provenance

Ported 2026-09-27 from `onflow/high-assurance-engineering`
`.cursor/skills/memory-light/SKILL.md`. Remap: consumer + durable root →
this persona's `.cursor/rules/memory/`; HA `04-memory-update-triggers.mdc`
items 1–6 → `03` items 1–4 + placement gate; cold-AI + migration spectrum →
`reference/cold-ai-paradigm.md` + the two `WORKING_STYLE.md` rows above;
`TWO_LEVELS_OF_LEARNING.md` → directive catalogs vs `MONITORING` /
`CONCLUSIONS`; full cycle → `lifecycle-kit/README.md`. Not yet run on this
persona.

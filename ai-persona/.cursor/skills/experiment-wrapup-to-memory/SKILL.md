---
name: experiment-wrapup-to-memory
description: >-
  Sequence a completed experiment/project into staged persona memory (survey →
  isolated ingest → extraction loop → hierarchical stage → human-gated migrate →
  prepared-bash cleanup). Uses the native plan-refinement review loop; does not
  re-derive it. A wrapped host (Claude Code, a tool, a transcript corpus) is a
  subject only — it never writes durable persona memory. Use when the user
  invokes /experiment-wrapup-to-memory, asks to wrap an experiment/project into
  memory, or to run the wrap-up-to-memory playbook.
disable-model-invocation: true
argument-hint: "[project-slug] [phase]"
---

# Experiment wrap-up → staged persona memory

**This skill sequences an already-validated playbook** (embedded in [reference.md](reference.md) § Playbook — this persona has no durable `concepts/authoring/` entry yet; the skill is the self-contained home). It does not re-derive wrap-up method, does not author skills, and does not run the review loop itself.

**Native equivalents (this persona; reference by path, do not re-encode):**
- Plan discipline: `.cursor/rules/reference/flexible-plans-for-ai-execution.md` (layered commitment).
- Review loop (**replaces the source's KU3 Claude-bridge skill**): `.cursor/rules/reference/plan-refinement-loop.md` — self-review + optional read-only subagents (§5 model classes). No Claude bridge required.
- Destructive cleanup: `.cursor/rules/06-destructive-operations.mdc` (+ `reference/destructive-operations.md`) — human-run; ledger `.cursor/rules/memory/PERMITTED_DESTRUCTIVE_ACTIONS.md`.
- Cold-AI write gate: `.cursor/rules/reference/cold-ai-paradigm.md` + `00-memory-system.mdc § The cold-AI test`.
- Placement + active-project detection: `.cursor/rules/04-multi-project.mdc § Placement gate` / `§ M1`; roster `.cursor/rules/memory/projects/_INDEX.md`.
- ai-notes scratch: `.cursor/rules/reference/ai-notes-convention.md` — working tree lives in gitignored `ai-persona/ai-notes/<slug>/`.

**Consumer:** local CircuitPython multi-experiment persona in `CircuitPython/ai-persona`. Reachable in other workspaces only when `ai-persona` is an open Cursor workspace root (the persona loads under that condition; see `00-memory-system.mdc`). Do **not** symlink into `~/.cursor/skills/` — Cursor would list `/name` twice.

**Vehicle:** local command-triggered project skill; **human-triggered only** — the slash command `/experiment-wrapup-to-memory`, or a verbal instruction the agent **confirms before running**. Never auto-run (`disable-model-invocation: true`). A wrap-up is a normal task/project-close step; the reminder duty + now-vs-defer discipline live in `03-memory-update-triggers.mdc` and `04-multi-project.mdc`.

**Not this skill:** ordinary per-turn memory updates (`03-memory-update-triggers.mdc`); a deliberate full-persona memory-maintenance / compaction pass (`00-memory-system.mdc § Maintenance`, `MAINTENANCE_BACKLOG.md`); authoring any skill; re-running a wrap-up already closed.

## Identity (load-bearing — restate in every ingest/review prompt)

| | Cursor (this chat) | Wrapped host (subject) |
|---|---|---|
| **Agent** | CircuitPython persona | e.g. Claude Code sibling, a tool, a transcript corpus |
| **Role** | Wrap-up **executor** of every granted phase, including migrate | **Subject.** Never writes durable persona memory. Never the migrator. |

Durable-memory **writer is always this Cursor chat** (on migrate grant). Discard first-person executor language from the wrapped host. A Claude **compiler** (other chat) may have staged a tree for you — ingest it; do not treat that compiler as a migrator.

## Layered commitment (this skill = meta-plan; `flexible-plans-for-ai-execution.md`)

**Fix:** targets (both learning levels **staged** hierarchically, then migrated only on grant; cold-AI retrievable; publish-safe); constraints (phase gates; silence ≠ grant; human-run destructive; identity split; use the native review loop, do not re-derive; durable writes = this Cursor chat); checkpoints (end of each phase); exit ramps (missing playbook section or native review-loop reference); authority map (below).

**Provisional (label as such):** the 7-step sequence (n=1 on this persona); initial success criteria; working-tree layout.

**Don't fix:** staging filenames, extract-schema wording, ingest-subagent count, exact PLAN prose.

## Persona preflight (every invoke)

Resolve (1) [reference.md](reference.md) § Playbook (2) `.cursor/rules/reference/flexible-plans-for-ai-execution.md` + `plan-refinement-loop.md` (3) `.cursor/rules/06-destructive-operations.mdc` (4) `.cursor/rules/reference/cold-ai-paradigm.md` (5) `.cursor/rules/04-multi-project.mdc § Placement gate`. If the **plan-refinement-loop** reference or the **placement gate** is missing, **stop and tell the human** — do not invent a stub, do not inline a review loop. Flag any other gap before continuing. [reference.md](reference.md) is templates + the embedded playbook, not a live-memory substitute.

## When invoked

0. **Persona preflight** (above). (If this chat is Claude Code, run **Preflight (Claude)** in [reference.md](reference.md) § Claude compiler addendum and follow the compiler-only rules instead — do not continue this list.)
1. **Resolve the experiment/project + mode.** Slug / paths from `$ARGUMENTS` or conversation; match against `projects/_INDEX.md` globs (M1). If the path matches none or is ambiguous, **ask before writing any per-project memory** (M1 — the top failure mode is mis-routing into the wrong project's folder). **Modes** (same output shape; default to the first that fits):
   - **resume-phase** — a PLAN / `WRAP-STATE.md` exists and a phase is GRANTED → execute **only** that phase.
   - **draft-plan** — no PLAN yet → draft a phase-gated wrap-up plan (`flexible-plans-for-ai-execution.md` layering), then stop at the plan-review checkpoint.
   - **survey-only** — user asked only to see what is already held.
   - **ingest-handoff** — a Claude-originated tree exists under `ai-notes/wrap-up-staging/<slug>/` → survey (G1); do **not** re-extract; wait for migrate grant (or migrate if granted).
   - **PLAN present, all phases BLOCKED** → confirm which phase to resume, or draft-revise. Do not start ingest/migrate.
   If mode is still ambiguous, ask once.
2. **Seed `WRAP-STATE.md`** in gitignored `ai-persona/ai-notes/<slug>/` from [reference.md](reference.md) (ingest-handoff: use the existing tree under `wrap-up-staging/<slug>/`). Cite inode names from `ls` (G17). Working tree is a **starting layout**, not a commitment.
3. **First concrete action — survey (G1).** List prior wrap-ups of *this* project in durable memory (`projects/<slug>/{SESSION_LOG,CONCLUSIONS,CONTEXT}.md`, relevant `concepts/`, `crossref/`). Do not re-derive already-held items. Extend-in-place only for a material caveat / clearer mechanism; a contradicting source is always in scope.
4. **Inside a granted phase:** execute (target-preserving, autonomous); at the phase checkpoint emit an audible **Observe / Evaluate / Revise / Continue** ([reference.md](reference.md) checkpoint template; `flexible-plans-for-ai-execution.md § Closed-loop cycle` — checkpoint silence = failure). Speaking at the checkpoint is not itself a phase grant. Then run the native review loop / wait for the next grant / close by updating `WRAP-STATE.md` + a one-line project-log pointer (no extract dumps into durable memory). Crossing a phase, starting ingest, migrating, or cleanup bash without an explicit grant → stop (Hard stops).

## Review checkpoints — use the native plan-refinement loop

Load `.cursor/rules/reference/plan-refinement-loop.md` and follow it (draft → self-review against fixed lenses → refine → converge; DR-or-cap termination; artifacts in the gitignored working folder). This **replaces** the source persona's Cursor↔Claude bridge skill — no external host is required. Optional read-only subagents per its § 5 (composer-class for scanning, opus-class for judgment); inform the human before relying on costly subagent fleets (its cost gate).

| When | Review subject | Lens bias |
|---|---|---|
| Wrap-up PLAN drafted (before ingest) | the PLAN | goal-fit + flexible-plans compliance (R1/R2) |
| Staging written (before migrate grant) | `staging/` (inode names) | correctness · fidelity · cold-AI retrieval · economy |
| After migrate (optional confirm) | migrated memory loci | same, on the live tree |

Cleanup has no review checkpoint (agent does not `rm`).

## Loops (every loop needs a diminishing-returns signal **and** a numeric cap)

This skill does not own a tight iteration loop; it **requires** the wrap-up PLAN (or, in no-plan degrade, `WRAP-STATE.md`) to name both a DR signal and a numeric cap on:

1. **Per-source extraction** (playbook G11).
2. **Cross-source aggregation** (the easy miss). *Initial* cap (provisional): 3 aggregation rounds; stop earlier when round N adds zero new {concept, reinforcement, relation, monitoring-observation}.

The plan-refinement loop has its own DR+cap — do not add a second. If a resumed PLAN lacks (1) or (2), add them **before** ingest (target-preserving).

## Authority

**Autonomous:** survey; classify (recall-biased); draft/revise a wrap-up PLAN; target-preserving compile/distill/stage inside a granted ingest+stage phase; tiny pointer-only `SESSION_LOG` / `CONTEXT` lines in the plan phase; run the native review loop; apply review findings that preserve targets/constraints; migrate **only** when that phase is GRANTED.

**Escalate:** missing playbook section or review-loop reference; phase crossing / migrate / any destructive (`06`); any commit/PR; criterion/target changes that conflict with settled human directives; seeding a **new** `concepts/<domain>` (C7 evidence gate) or any Level-2 memory-org change; promoting a directive to `[universal]` (needs Alex's sign-off, M3).

## Hard stops

- Do not re-run ingest / migrate / cleanup of an already-closed wrap-up.
- Do not re-derive the playbook or the review loop.
- Do not follow deleted `ai-notes/` paths as live.
- Do not treat silence as a phase grant (distinct from checkpoint silence = failure).
- Do not `rm` experiment files; prepare bash + one-line why (`06`; include the § 6a inbound/outbound reference sweep in the comments). Move-to-safe-location is the only destructive-ish escape hatch without a grant.
- Do not author any skill from this process.
- Do not place working files in durable memory (versioning-need ≠ durable placement — `ai-notes-convention.md`). A **≤1 KB distillate sidecar** under `concepts/` is durable, not a working-file dump.
- Route every durable write through `04-multi-project.mdc § Placement gate`; honor any scope tag already present; keep entries at the shallowest correct scope when uncertain.

## Default-and-degrade

Dominant case: **this Cursor chat** wrapping a cross-host experiment with a phase-gated PLAN. Degrade to ingest-handoff (Claude already compiled), same-host / tool wrap-up (identity split still named), or a small no-plan corpus (embed the minimum in `WRAP-STATE.md`; keep the reference bias). Output shape stays: survey → granted-phase work → checkpoint → grant or close.

## Durable-memory targets (this persona's layout)

Migrate lands under `.cursor/rules/memory/` per the placement gate:

| Wrap-up output | Destination |
|---|---|
| **Level-1** behavioral directive | `universal/WORKING_STYLE.md` (new row or reinforcement increment) |
| **Level-1** coding-craft directive | `universal/CODING_PRINCIPLES.md` |
| Domain/technical knowledge | `concepts/<domain>.md` (+ `_INDEX.md` line; `_RELATIONS.md` edge). Enumerated tables that don't fit the parent → **≤1 KB sidecar** (stream on demand). Seed a new domain only on evidence (C7) — else nearest domain + candidate note |
| Validated project finding (with evidence status) | `projects/<slug>/CONCLUSIONS.md` |
| Session insight / decision / open question | `projects/<slug>/SESSION_LOG.md` (cross-project/tooling → central `memory/SESSION_LOG.md`) |
| **Level-2** single-incident observation to act on only if it recurs | `universal/MONITORING.md` (Observation / Trigger / Action-on-trigger / First-observed / Scope) |
| Cross-project topic / recurring pattern | `crossref/BY_TOPIC.md` / `crossref/BY_PATTERN.md` |

**Two learning levels (source's `TWO_LEVELS_OF_LEARNING.md`, mapped):** Level-1 = *prescriptions* → the `universal/` directive catalogs; Level-2 = *attention-areas at honest status* → `MONITORING.md` (recurrence-gated) and `unverified` entries in `CONCLUSIONS.md`. An extraction that outputs only one level has under-mined.

---

## Claude Code (compiler-only)

Reach this section only when **this chat is Claude Code** (sibling host). Cursor performance is the default above. See `.cursor/rules/reference/host-adaptation-claude-code.md` for the primitive mapping and coexistence gotchas.

**May:** survey (read durable memory); classify; draft/revise a wrap-up PLAN; compile, distill, condense, and **hierarchically** structure learnings into the dedicated staging root.

**Must not:** write **any** path under `.cursor/rules/` (especially `memory/`); migrate; `rm` / cleanup. A migrate grant **in this Claude chat** does not lift this — Cursor migrates later.

**Staging root** (gitignored; not persona memory): `ai-persona/ai-notes/wrap-up-staging/<slug>/`. Templates: [reference.md](reference.md) § Claude compiler addendum (`HANDOFF.md`, `staging/INDEX.md`).

**Preflight (Claude):** resolve the embedded playbook + `flexible-plans-for-ai-execution.md` + `06-destructive-operations.mdc` + `04-multi-project.mdc § Placement gate`. Missing playbook → **stop**. A native review loop is Cursor-driven — do not invent one here.

**Close:** write `HANDOFF.md` (not a migrate grant) and **stop**. Cursor later runs **ingest-handoff** on that tree.

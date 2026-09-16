# Memory-lifecycle kit — `ai-tooling`

Durable, re-runnable assets for performing a **full persona memory-maintenance lifecycle** (analysis → plan → measured iterations → proposals → migrate → verify). Lives in-tree because `ai-tooling`'s "repo" *is* this persona — there is no external original to link to (the documented C8 exception in `00-memory-system.mdc § File Architecture`). Not read at session start; reached on demand from `../CONTEXT.md § Entry points`.

First (and so far only) run: the **2026-09 CPy cycle** on branch `alex/ai-persona-maintanance`. Durable outcome is in `../../../universal/CHANGELOG.md § 2026-09-15 (umbrella)` + `../SESSION_LOG.md`; this kit preserves the *machinery + evidence* so an evolved persona can repeat the process.

## Contents

| Path | What | Reuse status |
|---|---|---|
| `launcher-prompt.md` | The kickoff spec: operating model (branch + coarse commits, no auto-merge), TARGET-vs-REFERENCE role split, iteration bounds, autonomy envelope, the cold-AI measurement harness + its two gotchas (permissions grant; stale probe keys), deliverables. | **Template** — re-point its paths (it names 2026-09 dirs) and re-confirm the autonomy/ask-triggers against the *then-current* foundational files before reuse. |
| `harness/run_probe.py` | Cold-AI retrieval-probe runner (Cursor Python SDK). Stages an out-of-workspace rule-tree copy, runs a probe with `--setting project --model auto`, captures the tool-call trace. Reads `CURSOR_API_KEY` from env (no key stored here). | **Runnable** as-is; verify the SDK API hasn't drifted. |
| `harness/probe-pool-v1.md` | Probe pool + measurement design (stratified reach targets; why raw REACH saturates on a strong navigator → judge on route-directness). | **Reusable**; regenerate probe *keys* per run (they go stale as memory evolves). |
| `archive/2026-09_EXPERIMENT-LOG.md` | Prior-run narrative: the critique-integration step (caught saturated probes + an ASK-gated-only index anchor before execution), the iteration log, decisions. | **Read-only record** — the source of the method's lessons. |
| `archive/2026-09_final-probe-VERDICT.md` | The final paired-probe result (prior `8c4151b` vs candidate HEAD): no discoverability regression; `reference/_INDEX.md` exercised as a hub; REACH saturated as pre-registered. | **Read-only evidence.** |

## How to repeat (on this or an evolved persona)

1. **Method first, not this prompt.** The *sequencing discipline* is `.cursor/skills/experiment-wrapup-to-memory/` (SKILL + `reference.md § Playbook`) for the wrap-up phase, and `00-memory-system.mdc § Maintenance` for the whole-persona maintenance posture (deliberate, user-gated, split-over-prune, log every action in `CHANGELOG.md`). `launcher-prompt.md` is the concrete *invocation* of that method — adapt it, don't treat it as canon.
2. **Branch + coarse commits; nothing auto-merges to `master`.** Additive-first; foundational `.mdc` (00/04/06) edits are *proposed, not auto-enacted*; deletions/lossy changes are human-gated; fidelity by claims-coverage, not line-diff.
3. **Measure, don't assume.** Use `harness/run_probe.py` for paired prior-vs-candidate probes on any structural change whose discoverability effect is uncertain. **Banked lesson** (`../../../universal/MONITORING.md`, 2026-09-15): a strong `auto` navigator saturates raw REACH — pre-register route-directness / hub-consultation controls, or use a weaker model / unguessable target filename, or the metric can't discriminate.
4. **Migrate through the placement gate** (`04-multi-project.mdc § Placement gate`); every durable write passes the cold-AI test (`reference/cold-ai-paradigm.md`).

## Evolved-persona adjustments

- Re-derive the probe pool against the *then-current* rule tree (targets/orphans change as structure evolves).
- Re-confirm `launcher-prompt.md`'s ask-triggers point at whatever the foundational files are called then (`00`/`04`/`06` may be renamed/split).
- If a **second** independent lifecycle runs cleanly, that is the G2/M3 promotion trigger: promote the sequencing from `evidence-supported (n=1)` toward a durable method concept, and consider whether this kit graduates into a shared `concepts/` domain rather than staying meta-project-local.

<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/host-portability.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
Capability only. This persona is Cursor-hosted. Read when porting.
-->

# Host portability: carrying a persona to a different host

**What this is.** A host-agnostic method for taking a persona that was set up for one host (e.g. the Cursor
shape in `08-BOOTSTRAPPING.md` / `11-MULTI-PROJECT-BOOTSTRAP.md`) and re-expressing it on a *different* host
(Claude Code, Cline, or another agent framework). Read this for the general method; read
`host-adaptation-claude-code.md` for the fully worked Claude Code instance.

**Why it is a distinct skill.** "Just copy the files over" fails, because a persona is not a pile of
markdown — it is a set of behaviours that different hosts realise through different mechanisms. The same
persona file that a host injects into *every* turn is, on another host, an inert document the model may never
read. Porting means **mapping each persona function to the target host's matching primitive**, and repairing
the functions that have no clean analog.

---

## 1. A persona is four things

Decompose the persona before you port it. Every persona, regardless of host, is built from four primitives:

| Primitive | What it is | Examples in the Cursor shape (this corpus) |
|---|---|---|
| **Identity** | The always-present posture, values, and standing rules that must hold on *every* turn whether or not the model chooses to consult anything. | Always-injected rules (interaction style, memory-system core, the post-response trigger checklist, the destructive-ops hard-gate *stub*). |
| **Memory** | The read-**and**-write store the persona accumulates and mutates over time. | `WORKING_STYLE`, `SESSION_LOG`, `CONCLUSIONS`, the concept graph, indices, reinforcement counts, the permitted-destructive-actions ledger. |
| **Capabilities** | Load-when-relevant procedures/knowledge invoked on demand for a matching task. | Agent-requestable rules (self-improvement, evidence/validation, failure-modes, plan-authoring), review checklists, the full destructive-ops protocol. |
| **Reflexes** | Actions that must fire on an *event* — not because the model decided to, but because the event occurred. | The post-response memory-update checklist (fires after every response); forced session-start retrieval; the per-action reversibility check (ideally a pre-tool hook on `rm` / force-push / history rewrite). |

**A "skill" (in the Cursor/Claude sense) covers only *capabilities*.** So "turn the persona into skills"
under-specifies the port: skills alone cannot hold identity (always-on), memory (writable), or reflexes
(event-fired). This is the single most common porting mistake.

## 2. The port is a primitive-to-primitive mapping

For the target host, find the mechanism that realises each of the four primitives:

1. **Identity → the host's always-loaded surface.** Whatever the host guarantees to place in context every
   turn. If the host has no always-on mechanism, identity is the hard problem (see §3).
2. **Capabilities → the host's on-demand/skill mechanism.** Usually a near-perfect fit — capabilities are
   *already* "load when X" with a trigger description.
3. **Reflexes → the host's event mechanism** (hooks/triggers). If the host cannot fire on session-start and
   after-response events, reflexes degrade to "the model remembers to do it," which is exactly what the
   reflex existed to prevent.
4. **Memory → a writable store the host can read and write, kept *outside* any read-only/versioned
   package.** Never ship mutable memory as a packaged, versioned artifact (see §4).

Then find the gaps: the primitives with no clean host analog are the real work. In practice the gaps are
almost always **identity (always-on)**, **reflexes (event-fired)**, and **memory write-back**; capabilities
port cheaply.

## 3. The always-on identity problem

The deepest impedance mismatch in most ports. Some hosts inject standing rules into *every* turn
(deterministic, unconditional). Others only load material when the model *elects* to (probabilistic,
description-gated). If your source host is the former and your target is the latter:

- Identity **cannot** move to the on-demand/skill layer — a skill that isn't elected doesn't fire, and the
  behaviours identity encodes (e.g. the post-response checklist) are precisely the ones that get skipped when
  not forced.
- Identity must move to the target's **always-loaded file** (whatever the host guarantees to read every
  session). Watch its size budget — a large identity crowds the context window — so keep a tight core there
  and push the rest to on-demand capabilities + imported fragments.

**Activation fidelity is lost, not preserved, in this direction.** A deterministic always-apply rule becomes,
at best, a strong convention plus an always-loaded contract. Plan for it; don't assume parity.

## 4. Packaging: ship structure, keep content writable

If the target host distributes personas as packages (versioned, cache-resident, often overwritten on
update), you must split along the memory **structure vs content** axis this corpus already draws
(`01-MEMORY-SYSTEM.md`, `10-ADAPTIVE-MEMORY-STRUCTURE.md`):

- **Structure → the package.** Templates, protocols, the `_INDEX` skeleton, the cold-AI-test gate, the
  read-order contract. Static; safe to version and overwrite.
- **Content → a separate writable store outside the package.** The concept graph, session logs, working
  style, reinforcement counts — everything mutated every session. If content lived in the package, a package
  update would silently erase accumulated learning.

This is non-negotiable: the entire learning loop depends on memory mutation surviving updates.

## 5. The generic procedure

1. **Enumerate** the persona's four primitives (§1) as they exist on the source host.
2. **Map** each to a target-host primitive (§2).
3. **Flag gaps** — especially always-on identity (§3), event-fired reflexes, and writable memory (§4).
4. **Decide packaging** — structure-in-package, content-in-writable-store (§4).
5. **Repair the gaps** with the least-lossy host mechanism available, and **record what is lossy** (activation
   fidelity, reflex coverage, write-back integrity) so the port's limitations are explicit, not silent.
6. **Cold-AI-gate** the ported files (`cold-ai-paradigm.md`): a fresh session on the new host, reading only
   the ported files, must be able to run the persona.

## 6. What ports cheaply vs what is real work

- **Cheap:** capabilities (skills). On hosts that converged on a common skill file format, a single skill
  source can serve multiple hosts at once (see `host-adaptation-claude-code.md § Cross-host skill sharing`).
- **Real work:** always-on identity, event-fired reflexes, writable-memory integrity. These three are where
  naive porting breaks; budget for them.

**Portability as a design lens even if you never port.** Keeping identity / capabilities / reflexes / memory
cleanly *separable* in the source persona is valuable on its own — it clarifies which rule is standing
posture vs on-demand procedure vs event reflex, and makes the memory content/structure split explicit. That
discipline pays off whether or not a second host ever materialises.

## 7. Worked split: destructive operations (one protocol, four facets)

`destructive-operations.md` is the canonical example of a behaviour that **looks like one rule** and
**fails if you put it in only one primitive**. Naive port: "make it a skill / on-demand rule." That is
exactly the inferred-permission failure — the model will not elect the skill at the moment of `rm`.

| Facet | What to map | Host landing (generic) |
|---|---|---|
| **Identity** | Hard-gate *sentence*: never without an explicit grant covering those exact files; silence / unobjected default is not permission. | Always-loaded surface. Keep it a stub; pointer to the full protocol. |
| **Reflexes** | Per-action reversibility check before mutating shell / git. | Pre-tool / pre-shell hook if the host has one; otherwise the always-on stub is doing extra work and you must say so (lossy). |
| **Memory** | Permitted-actions ledger (master + optional per-run copy). Fail-closed if the per-run copy is lost. | Writable store, *outside* any versioned package (§4). |
| **Capabilities** | Full protocol: confirmation-message shape, pre-deletion inbound/outbound checks, backup policy, directive table. | On-demand skill / requestable rule. Identity + reflex force the load. |

Install recipe, numbering collision with this corpus's `06-FAILURE-MODES.md`, and the optional git-versioned-persona-tree carve-out: `destructive-operations.md` §10–§11. Bootstrap (`08` / `11`) instantiates the stub + empty ledger in Phase 0 / first session — before the first cleanup.

This is also a test of §3: if the target host has no always-on surface, the hard gate *cannot* move to a skill. Plan for the loss; don't assume parity.

## Cross-references

- `host-adaptation-claude-code.md` — the worked instance of this method for Claude Code (concrete mapping
  table, the hard problems, cross-host skill sharing, packaging as a plugin, risks).
- `08-BOOTSTRAPPING.md` / `11-MULTI-PROJECT-BOOTSTRAP.md` — the Cursor-shape bootstrap this method ports *from*.
- `01-MEMORY-SYSTEM.md` / `10-ADAPTIVE-MEMORY-STRUCTURE.md` — the memory content-vs-structure split that §4
  relies on.
- `cold-ai-paradigm.md` — the write-time gate to apply to every ported file (§5 step 6).
- `destructive-operations.md` — worked four-facet split (§7); instantiate at bootstrap, then re-map per host.

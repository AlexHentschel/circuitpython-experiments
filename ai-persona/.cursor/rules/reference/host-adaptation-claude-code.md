<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/host-adaptation-claude-code.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
NOT INSTANTIATED. Capability copy only (plan default R2). Do not create CLAUDE.md / Claude Code hooks from this file.
-->

# Host adaptation: Cursor persona → Claude Code

**What this is.** The worked instance of `host-portability.md` for **Claude Code** (Anthropic's terminal/IDE
coding agent). It maps a persona bootstrapped in the Cursor shape (`08-BOOTSTRAPPING.md` /
`11-MULTI-PROJECT-BOOTSTRAP.md` — always-injected `.mdc` rules under `.cursor/rules/`) onto Claude Code's
primitives, and calls out where the mapping is lossy.

**Read `host-portability.md` first** for the general four-primitive method (identity / memory / capabilities /
reflexes → host primitives). This file assumes it.

**Confidence note (read before relying).** HIGH confidence on the always-loaded-file behaviour and the skill
file layout (these are stable and file-verifiable). LOWER confidence on exact **hook** event names and
payloads — they evolve. **Verify hook semantics against current Claude Code documentation before building on
them.**

---

## 1. Claude Code primitives (decoded)

| Primitive | What it is | Key property for porting |
|---|---|---|
| **`CLAUDE.md`** | A markdown file Claude Code loads into context automatically at the start of every session (a project-root `CLAUDE.md` / `AGENTS.md`, and a user-level one). Supports `@import` of fragment files. | The **only always-on surface.** This is where identity must live. |
| **Skill** | A directory `skills/<name>/SKILL.md`: YAML frontmatter (`name` ≤64 chars, `description` ≤1024 chars) + a markdown body (≤~500 lines) + optional `scripts/`/reference files. Loaded **on demand** — dormant until the model matches its `description` to the task and elects to invoke it. | Fits capabilities. **Not** always-on: election is probabilistic. |
| **Hook** | A script Claude Code runs on a lifecycle **event** — e.g. `SessionStart`, `Stop` (after a response completes), `PostToolUse`. Configured in a `settings.json`. | The only way to make something fire on an event rather than by model choice. Fits reflexes. |
| **Plugin** | A distributable package: `.claude-plugin/plugin.json` + bundled `skills/` + `hooks/` + a `CLAUDE.md` fragment. Versioned, cache-resident (the cache dir is overwritten on update). | Packaging/distribution. **Read-only** at runtime — must not hold writable memory. |
| **Subagent / Task** | A spawned sub-session for delegated work. | Direct equivalent of Cursor's `explore` / `generalPurpose` subagents. |

**The load-bearing asymmetry:** the Cursor persona runs on **always-injected rules** (re-entered every turn).
**Claude Code has no always-on skill.** So the always-on layer moves to `CLAUDE.md`, not to skills.

## 2. Component → primitive mapping

| Cursor persona component | Claude Code primitive | Fit |
|---|---|---|
| Always-applied rules: identity, memory-system core, interaction style, update-triggers, concept-graph protocol, **destructive-ops hard-gate stub** | **`CLAUDE.md`** (+ `@import` fragments) | Forced — always-on ⇒ must be the always-loaded file. The stub is short; the full protocol is a skill (row below). |
| Agent-requestable "load-when-X" rules (self-improvement, evidence/validation, failure-modes, directive-authoring, plan-authoring, **destructive-ops full protocol**) | **Skills** | Near-perfect — already description-gated "load when X". Destructive-ops skill does *not* replace the `CLAUDE.md` stub. |
| Domain review checklists | **Skills** | Strong |
| Concept-graph files (`concepts/<domain>/*.md`) | **Skill** (read-only mirror) **or** the writable store | Partial — retrieval-by-description fits, but concepts are written back to |
| Mutated-every-session memory (`SESSION_LOG`, `WORKING_STYLE`, people profiles, `_RELATIONS`, `_INDEX`, **permitted-destructive-actions ledger**) | **Writable memory store** (a file-tool directory, optionally a memory MCP server) | Must **NOT** be a packaged/versioned file. Ledger is fail-closed if lost (`destructive-operations.md` §6). |
| Post-response update-triggers checklist | **Hook** (`Stop` / post-response) | Skills can't self-fire |
| Per-action destructive-ops self-check | **Hook** (`PreToolUse` / pre-shell, if the host exposes it) on `rm` / `git reset --hard` / `git push --force` / history-rewrite | Best-effort intercept. **Verify current Claude Code hook events before wiring** (this file's confidence note). If no pre-tool hook exists, the `CLAUDE.md` stub is the only intercept — call that lossy. |
| Session-start active retrieval | **Hook** (`SessionStart`) + a `CLAUDE.md` read-order contract | Forced retrieval ≠ probabilistic skill election |
| `explore` / `generalPurpose` subagents | **Subagents / Task** | Direct equivalent |
| Self-containment + distribution | **Plugin** (`.claude-plugin/plugin.json` + `skills/` + `hooks/` + `CLAUDE.md` fragment) | Clean |

**One-liner:** identity → `CLAUDE.md`; capabilities → skills; reflexes → hooks; memory → a separate writable
store.

## 3. The hard problems

Where naive porting breaks — each maps to a §1 asymmetry:

1. **Always-on identity has no skill analog.** → It lives in `CLAUDE.md`. Risk: `CLAUDE.md` token budget (a
   large identity crowds every turn). Keep a tight core in `CLAUDE.md`; push the rest to `@import` fragments +
   on-demand skills.
2. **Memory is read-AND-write; plugins are read-only, versioned, cache-resident** (the cache dir is
   overwritten on update — writing there loses data). → Ship **structure** (templates, protocols, `_INDEX`
   skeleton, the cold-AI-test gate) in the plugin; keep **content** (graph, logs, reinforcement counts) in a
   separate writable store. This is exactly the memory structure-vs-content split from `01-MEMORY-SYSTEM.md`
   / `10-ADAPTIVE-MEMORY-STRUCTURE.md`: structure → package, content → writable store.
3. **The post-response checklist needs an event, not a description.** → A `Stop`/post-response hook. Without
   it, the memory-update crowd-out failure (`06-FAILURE-MODES.md` — self-reflection loses to task completion)
   regresses, because a description-gated skill won't reliably fire after every turn.
4. **Session-start retrieval must be forced.** → A `SessionStart` hook + a `CLAUDE.md` read-order contract.
   Description-triggered loading is probabilistic; retrieval you depend on must be deterministic.
5. **Destructive-ops is the same event-vs-description problem on a different event.** The hard-gate
   *sentence* belongs in `CLAUDE.md` (identity). The per-action check belongs on a pre-tool hook if one
   exists (reflex). The ledger belongs in the writable store (memory). The full protocol is a skill
   (capability). A skill-only port re-creates `06-FAILURE-MODES.md` F11 (inferred-permission deletion).
   Detail: `destructive-operations.md` §10 and `host-portability.md` §7.

## 4. Cross-host skill sharing — one source, both hosts

A partial portability dividend available *today*: a single skill can serve **both** Cursor and Claude Code
from one maintained source.

- **Mechanism:** both hosts read `skills/<name>/SKILL.md` (YAML frontmatter `name` + `description` + markdown
  body). Point both hosts' skill directories at one real directory via a **symlink**.
- **Frontmatter is read as a union** — each host uses the fields it knows and ignores the rest:

| Field | Host that uses it | Effect |
|---|---|---|
| `disable-model-invocation: true` | Cursor | user-invoked / slash-menu only (not auto-elected) |
| `argument-hint`, `allowed-tools`, `$ARGUMENTS` in body | Claude Code | slash-arg hint, tool scope, user-arg substitution |
| `environments` / `disabled-environments` | Cursor | host/environment gating |

- **Authoring discipline for a shared skill:** keep the body **host-neutral** — cite the canonical rule
  rather than re-encoding it, and carry a minimal fallback reference for sessions run outside the persona's
  workspace. Confine host-specific bits to the ignorable frontmatter fields + one `$ARGUMENTS` line.
- **What does NOT share:** legacy flat `commands/*.md` (Cursor's form has no frontmatter; Claude's carries
  `description`/`argument-hint`/`allowed-tools`) — one file can't serve both. Target the
  `skills/<name>/SKILL.md` form; both ecosystems treat `commands/` as legacy.
- **Scope caveat:** *personal*-scope skills (a user-level skills dir on each host) share cleanly via one
  symlink. *Project*-scope skill layouts differ between hosts and may need a second link or a duplicate.
- **Relevance:** capabilities port host-to-host with near-zero rework. This does **not** touch the three hard
  parts (always-on identity, writable memory, reflex hooks) — those remain the real work (§3).

## 5. Risks / lossy points

- **Activation fidelity:** deterministic always-apply → probabilistic skill election. A concept graph exposed
  as skills retrieves less deterministically than a load-on-demand-by-index scheme.
- **Write-back integrity:** the whole learning loop depends on memory mutation surviving plugin updates → the
  §3.2 structure/content separation is non-negotiable.
- **Reflex coverage:** if hooks can't cleanly replicate the post-response checklist, pattern-extraction /
  memory-update reflexes regress.
- **Cross-host config bleed (coexistence gotcha).** If you run Cursor and Claude Code on the same machine, one
  host may auto-load the *other's* config (skills, and even hooks) — so a Claude hook can fire inside a Cursor
  session, or vice versa. On any such symptom, audit the four persona-transport axes with filesystem +
  actual-loaded-context evidence, not guesswork: **instructions** (which `CLAUDE.md`/`AGENTS.md` load),
  **memory** (is a tree auto-injected?), **skills** (which discovery dirs surface), **hooks** (which
  `settings.json` sources fire). Prefer host settings that scope third-party config loading; guard reflex
  hooks so they no-op unless they detect genuine execution by their own host.

## 6. Empirical note

This mapping is not theoretical: a persona originally bootstrapped from this corpus was independently
re-derived on Claude Code and **arrived at the same `identity→CLAUDE.md / capabilities→skills /
reflexes→hooks / memory→writable-store` decomposition** — an independent confirmation of the four-primitive
mapping. The resulting sibling was a *thin* re-distillation (it did not inherit the accumulated training of
the original), which is the expected outcome: porting carries the *structure* of a persona cheaply; the
accumulated *content* (§3.2) is what takes time to rebuild and must be migrated deliberately, not assumed.

## Cross-references

- `host-portability.md` — the general four-primitive method this file instantiates.
- `08-BOOTSTRAPPING.md` / `11-MULTI-PROJECT-BOOTSTRAP.md` — the Cursor-shape bootstrap being ported.
- `01-MEMORY-SYSTEM.md` / `10-ADAPTIVE-MEMORY-STRUCTURE.md` — the memory structure-vs-content split (§3.2).
- `06-FAILURE-MODES.md` — the memory-update crowd-out failure that the `Stop` hook (§3.3) prevents; F11 (inferred-permission deletion) that a skill-only destructive-ops port re-creates.
- `cold-ai-paradigm.md` — the write-time gate for the ported files.
- `destructive-operations.md` — four-facet split; `CLAUDE.md` stub + skill + ledger + optional `PreToolUse` hook.

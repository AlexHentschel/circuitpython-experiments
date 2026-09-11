# Templates + embedded playbook + degrade fallback

Use with `SKILL.md`. Fill angle-bracket slots. Cite inode names from `ls`, not remembered aliases.

Working folder (gitignored): `ai-persona/ai-notes/<project-slug>/`. **Minimal; adapt.** Output *schema* is the interface contract; this tree is a starting layout, not a commitment. `.gitignore` already covers `ai-persona/ai-notes/` — confirm with `git check-ignore` before writing.

Claude compiler / Cursor ingest-handoff trees live under a **dedicated root** — see [§ Claude compiler addendum](#claude-compiler-addendum). Cursor compiling from scratch uses the folder above, not that root.

```
<project-slug>/
  WRAP-STATE.md
  PLAN.md                 # default; omit only in no-plan degrade
  extracts/               # per-source ingest temps
  staging/                # hierarchical publish-safe distillate; migrate only on grant
    INDEX.md              # condensed already-held + map of what is new
    # then cluster new findings (L1 directives / L2 observations / project findings) — filenames not fixed
  review-loop/            # created by the plan-refinement loop when run; do not invent
```

`README.md` is **optional**. Skip if WRAP-STATE already covers identity, granted phase, and caps.

---

## WRAP-STATE.md seed

```markdown
# Wrap-up state
**Started:** <YYYY-MM-DD>
**Project/experiment:** <slug + one-line>
**Mode:** resume-phase | draft-plan | survey-only | ingest-handoff
**Granted phase:** none | plan | ingest+stage | migrate | cleanup-prep
**Playbook:** SKILL.md callee = this file § Playbook (n=1 sequencing on this persona)
**Review loop:** .cursor/rules/reference/plan-refinement-loop.md (native; no external host)
**Status:** <phase> in flight

## Identity
- Wrapping / durable-memory writer: CircuitPython persona (this Cursor chat, on migrate grant).
- Wrapped: <host/tool/corpus> — subject, not writer of durable memory.
- Handoff origin (if ingest-handoff): none | Claude compiler at `ai-notes/wrap-up-staging/<slug>/`

## Active-project match (M1)
- Path-glob matched in projects/_INDEX.md: <glob → slug>  (ambiguous/none → asked human)

## Already held (G1 survey)
- <paths of prior wrap-ups of THIS project; or "none">

## Caps (provisional; require DR signal too)
- Per-source extraction: DR = round adds zero new {concept, reinforcement, relation, monitoring-observation}; cap = <N>
- Aggregation: same DR; cap = <N, initial 3>

## Corpus (recall-biased; ambiguous → keep)
- HIGH: <inode paths>
- MEDIUM: <inode paths>
- dropped (must not be the sole home of a finding): <none | path + why>

| Phase | Grant? | Review? | Durable writes? | Notes |
|---|---|---|---|---|
| survey+plan | <this invoke / paste> | refinement loop on PLAN | pointer-only SESSION_LOG/CONTEXT OK | |
| ingest+stage | <blocked until grant> | refinement loop on staging/ | staging/ only | |
| migrate | <blocked> | optional confirm on live tree | `.cursor/rules/memory/` | |
| cleanup-prep | agent prepares bash | no | none | human runs `06` |
```

---

## staging/INDEX.md (hierarchical distillate — schema, not filenames)

Compile/stage **must** produce a retrieval-oriented tree, not a flat dump of extracts.

- **INDEX.md** — condensed already-held (pointers into live memory) + map of *new* findings → child paths.
- **Level 1** — prescriptions / reinforcements → `universal/WORKING_STYLE.md` (behavioral) or `CODING_PRINCIPLES.md` (coding-craft), each with the target row/locus if known.
- **Level 2** — attention-areas at honest status → `universal/MONITORING.md` (recurrence-gated) or `unverified` `CONCLUSIONS.md` entries.
- Domain knowledge → `concepts/<domain>.md` (+ `_INDEX`/`_RELATIONS`); project findings → `projects/<slug>/CONCLUSIONS.md`.
- Cluster by retrieval (project / concept domain), not by source file. Source extracts stay in `extracts/`.
- Publish-safe: sensitive detail stays out; durable-bound content gets a neutral pointer.

Child filenames are **not** fixed. INDEX is. Every entry passes the cold-AI test (`cold-ai-paradigm.md`).

---

## Ingest-subagent prompt skeleton

Subagents inherit always-applied `.mdc` but **not** `memory/*.md` or parent chat. Default = light/scanning model; escalate only for cross-source contradiction or identity judgment.

```markdown
# Isolated ingest — source <N>: <exact-inode-path>

You extract. You do **not** write durable persona memory.

## Identity
- You are a Cursor subagent of the **wrapping** CircuitPython persona.
- The **wrapped** host/tool is <name> — a subject, not you. Do not write as that host.
- Durable memory is Cursor-only. Your only write is the extract file below.

## Read (full)
1. <exact-inode-path of this source>
2. SKILL.md § When invoked + this file § Playbook (Objectives + schema only)
3. <optional: live concept paths this source might reinforce — by path, not pasted>

## Write (only)
`ai-persona/ai-notes/<slug>/extracts/<exact-stem>.md`

Schema: source path + date; Level-1 candidates (prescriptions/reinforcements, with target directive-catalog locus if known); Level-2 attention-areas (honest status → MONITORING or unverified CONCLUSIONS); domain-knowledge candidates (concept domain if known); identity slips; publishability tier (public-conceptual vs private-sensitive → pointer only); verbatim-keep vs extract vs **notes-sensitive-only** (not source-only for public claims — non-confidential must have a durable home). Cap expansion by this schema. Do not summarize away mechanism.

## Forbidden
Durable writes under `.cursor/rules/memory/` (and any `.cursor/rules/`). Authoring skills. Following deleted `ai-notes/` paths as live.
```

---

## Phase-checkpoint (audible)

```markdown
# Checkpoint — <phase>
**Observe:** <what execution revealed>
**Evaluate:** targets/constraints/criteria/approach — change?
**Revise:** <specific plan change> | charge/criteria unchanged
**Continue:** <next granted action | wait for grant | run refinement loop on <path> cap=<N>>
```

Silence at this gate is failure (`flexible-plans-for-ai-execution.md § Closed-loop cycle`).

---

## Review-loop invoke (pointer only)

Do not re-derive. Load `.cursor/rules/reference/plan-refinement-loop.md` and run its draft → self-review → refine → converge cycle. Subject = `<inode path>`; ask the human for the hard convergence cap (default: treat as ≤10 plan / ≤5 artifact passes unless set). Working folder for *that* loop = `ai-persona/ai-notes/<slug>/review-loop/` (the loop creates it). Optional read-only subagents per its § 5 (composer-class scan / opus-class judgment) — inform the human before relying on costly fleets. This persona has **no** Cursor↔Claude bridge; the native self-review loop is the review mechanism.

---

## Cleanup bash header (prepare; do not run)

Agent writes a script the **human** runs. No `rm` from the agent. The dedicated `06` § 3 confirmation (fresh trigger word, ledger entry in `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md`) is the human's, not this skill's.

```bash
#!/usr/bin/env bash
# Why: remove gitignored wrap-up scratch for <slug> after migrate + distillate.
# Destructive: deletes <list folders>. Not trivially reversible (gitignored, untracked).
# Restore: <Alex backup path or "none — confirm backup first">
#
# § 6a outbound: grepped this tree for deferred / decide-at-end / TBD — <result>
# § 6a inbound: grepped durable `.cursor/rules` for this slug path — <result; re-home before run>
#
# set -euo pipefail
# echo "DRY RUN — human uncomment to execute after 06 grant"
# # rm -rf -- "ai-persona/ai-notes/<slug>"
# # rm -rf -- "ai-persona/ai-notes/wrap-up-staging/<slug>"
```

---

## Playbook (embedded — this persona's self-contained canonical text)

The source persona keeps this as a durable `concepts/authoring/experiment-wrapup-to-memory.md`. This persona has no `authoring` concept domain yet (seeding one is evidence-gated, C7), so the playbook lives here. Promote it to a `concepts/<domain>.md` entry only after a second wrap-up of this class confirms the sequencing (M3 promotion ladder) — until then it is `evidence-supported` method with the **sequencing held as hypothesis-test (n=1)**.

### One-line purpose
Turn a completed experiment's transcripts/notes/artifacts into durable persona memory without re-deriving what is already held, losing new findings, or leaking sensitive detail.

### Mechanism — a gated, staged pipeline
The wrapped host is a subject, never a durable-memory writer. **Durable migrate is always this Cursor chat.**
1. **Survey** already-held memory for prior wrap-ups of *this* project; do not re-derive.
2. **Classify** the source corpus recall-biased (false positives cheap, false negatives costly).
3. **Ingest** isolated — one subagent per source, full read, extract to a temp file, expansion capped by schema.
4. **Extraction loop** to diminishing-returns-or-cap: per-source round → cross-source distill → round 2+ with a *changed* directive (validate / gaps / contradict) + original source re-presented. DR+cap on the aggregation loop too.
5. **Stage** publish-safe artifacts under an ephemeral `staging/` tree; decide the information tier at write time.
6. **Migrate** staging → `.cursor/rules/memory/` only after an explicit human go-ahead (the shared concept graph is high blast-radius); route every write through `04-multi-project.mdc § Placement gate`.
7. **Cleanup** is human-run: agent prepares bash + one-line why (`06`); never `rm`s the (gitignored) experiment files itself.

Each step inherits an already-validated persona rule (see § Where the pieces come from). The novel part is the *sequencing + wrap-up-specific completeness*.

### Objectives (fixed-class — an extraction that misses one has under-mined)
1. **Cold-AI retrievability** — a condensed index of already-held knowledge + a detailed record of *new* findings. Write-time gate = `cold-ai-paradigm.md` / `00-memory-system.mdc § The cold-AI test`.
2. **Both learning levels** — Level-1 prescriptions (→ `universal/` directive catalogs) **and** Level-2 attention-areas (→ `MONITORING.md` / `unverified` CONCLUSIONS).
3. **Hierarchical information** — decided at write time: (a) **verbatim-in-memory** (claims that fit the parent concept/CONCLUSION), (b) **compressed sidecar ≤1 KB** with an `_INDEX` pointer (enumerated tables/arithmetic; stream on demand), (c) **notes remainder = confidential / security-sensitive only** (unless Alex specifies otherwise). **Supersedes** source-only-until-cleanup for non-confidential material: assume `ai-notes/` may be gone later; those claims must already live in durable memory before cleanup bash is prepared. G10 still sanitizes credentials.
4. **Identity hygiene** — wrapping agent ≠ wrapped host's agent; name who writes where.
5. **Gated mutation** — survey/plan → ingest/stage → migrate; each later phase needs explicit go-ahead; destructive cleanup human-run.
6. **Process reflexivity** — stock notes for a later concept/skill; do not author that skill in the wrap-up unless asked.
7. **Publish-safety** — stage as if public; sensitive detail stays in gitignored notes, durable memory gets a neutral pointer.

### Guidelines (adaptive — hold as guidelines, not laws; each has a self-check)
| ID | Guideline (terse) | Flex / self-check |
|---|---|---|
| G1 | Survey prior wrap-ups of the same project first; don't re-derive already-held items | Extend-in-place only for a material caveat/clearer mechanism; a *contradicting* source is always in scope |
| G2 | Reuse existing method docs; add a playbook/concept only for the gap | One instance = candidate; a 2nd wrap-up of this class → promote (this is the n=1 caveat) |
| G3 | Corpus classification: false positives OK, false negatives costly | Ambiguous → keep; a dropped source must not be the only home of a finding |
| G4 | Isolated ingest, one subagent per source, full read, extract to temp; cap expansion by schema | Rich source → optional undirected + directed pass; thin → single directed; never drop the directed pass; watch extract→summary drift |
| G5 | Subagents inherit always-applied `.mdc` but NOT `memory/*.md` or parent chat | Prompt must name paths to read + remind of identity split + forbid durable writes |
| G6 | Stage then migrate; shared concept graph is high blast-radius | Tiny pointer-only SESSION_LOG/CONTEXT updates in the plan phase are allowed |
| G7 | Retain-vs-extract by retrieval need, not affection | Keep full in durable memory (parent or ≤1 KB sidecar): current-state overlays, restore paths, pass/fail evidence, enumerated tables that would otherwise be the only copy, prompt of record. Extract: closed review loops, superseded essays. Notes remainder: credentials / security-sensitive (G10) unless Alex specifies otherwise. A dropped notes folder must not be the only home of a non-confidential finding |
| G8 | Do not execute past a documented gate; silence ≠ permission | Autonomous *inside* a granted phase (target-preserving) is fine; crossing a phase is not |
| G9 | Human runs destructive bash; agent prepares commands + one-line why | Move-to-safe-location is the only destructive-ish escape hatch without a grant (`06`) |
| G10 | Sanitize at stage time, not as a later scrub | Machine-local paths OK in project CONTEXT; credentials/`settings.toml` and sensitive filenames must be abstracted |
| G11 | Extraction loop until diminishing returns, not a fixed round count | Bounded fully-read sources often converge in one deep pass; stop when round N adds zero new {concept, reinforcement, relation, monitoring-observation} |
| G12 | Dedup against the live graph before proposing new nodes | Most raw candidates are reinforcements, not new nodes; extend-in-place per G1 |
| G13 | Notes: condense known, detail new; split files for retrieval; keep the drafting log current | If the log becomes the sole home of a decision, lift it into the plan/playbook |
| G14 | Stock process notes; leave concept-vs-skill open; include the wrap-up prompt by path | Third similar wrap-up → propose promotion of the process itself. Wrap-up **stocks notes**; it does not author skills |
| G15 | Default subagent = light/scanning model; escalate only for significantly complex reasoning | Harvest fidelity is largely model-independent; models differ at boundary segmentation |
| G16 | Parked older human inputs are a wrap-up source class | Mine still-binding directives; newer dated sources win on conflict |
| G17 | Cite local files by exact inode name (`ls` byte-for-byte) | Staging filenames in the plan are a hypothesis until created; if renamed, update every citation in the same pass |

**Self-check pack (run before declaring a wrap-up phase done):** prior wrap-ups listed & not re-derived · both learning levels have an output surface · corpus recall-biased · identity split stated in prompts/notes · phase gates written, no execution past grant · staging path exists + migration listed · destructive cleanup = prepared bash · cold-AI test on every note · publishability decided at write time · **every non-confidential claim has a durable home before cleanup bash is prepared** · process notes updated, skill not authored · inbound/outbound refs checked before any future delete (`06 § 6a`) · parked inputs triaged · citations match inode names · active-project match confirmed (M1).

### Register (settled vs hypothesis-test)
- **Settled (each guideline composes an already-validated persona rule):** G1–G17 and the 7 objectives — pointers into `flexible-plans-for-ai-execution.md`, `plan-refinement-loop.md`, `cold-ai-paradigm.md`, `00 § cold-AI test`, `06-destructive-operations.mdc`, `04-multi-project.mdc § Placement gate`, `ai-notes-convention.md`.
- **Hypothesis-test (n=1 on this persona — apply, then confirm/refute):** the **overall sequencing + completeness** as *the* wrap-up playbook. *Confirm:* a second independent project wrap-up runs cleanly with ≤1 gap. *Refute:* the sequence misses a phase, over-fits the cross-host case, or a guideline proves host-specific. *Re-eval trigger:* the second wrap-up of this class (also the G2 promotion trigger).

### Where it applies
Wrapping a completed experiment/project (especially cross-host or cross-tool) into durable persona memory.

### Where it doesn't apply
- Ordinary per-turn updates → `03-memory-update-triggers.mdc`.
- Deliberate full-persona memory-maintenance / compaction → `00-memory-system.mdc § Maintenance`, `MAINTENANCE_BACKLOG.md`.
- Not a skill-authoring instrument — wrap-up stocks process notes (G14) and leaves concept-vs-skill open.

### Where the pieces come from (this persona)
- `composes-with` `reference/flexible-plans-for-ai-execution.md` — the wrap-up runs as a flexible, phase-gated plan.
- `composes-with` `reference/plan-refinement-loop.md` — the review-checkpoint mechanism (replaces the source's KU3 Claude bridge).
- `composes-with` `06-destructive-operations.mdc` — human-run cleanup + § 6a inbound/outbound reference sweep.
- `pairs-with` `reference/cold-ai-paradigm.md` + `00-memory-system.mdc § The cold-AI test` — every staged/migrated note passes it.
- `pairs-with` `04-multi-project.mdc § Placement gate` / `§ M1` — the classify/stage/migrate destinations and active-project detection.
- `pairs-with` `reference/ai-notes-convention.md` — the gitignored working-store lifecycle.

### Provenance
Ported 2026-09-11 from `onflow/high-assurance-engineering` `.cursor/skills/experiment-wrapup-to-memory/` (SKILL.md + reference.md) and its durable concept `concepts/authoring/experiment-wrapup-to-memory.md`. Source origin: 2026-08-24 Claude-wrapper experiment wrap-up (isolated ingest of 8 HIGH + 4 MEDIUM transcripts → extraction loop → staging → human-gated migrate → prepared-bash cleanup); promoted `evidence-supported` with the sequencing held hypothesis-test (n=1). This port remaps source-specific dependencies (KU3 Claude-bridge review loop → native `plan-refinement-loop.md`; `14-plan-authoring.mdc` → `flexible-plans-for-ai-execution.md`; `TWO_LEVELS_OF_LEARNING.md` → directives-vs-findings + MONITORING; durable root `memory/` → `.cursor/rules/memory/` unified multi-project layout). Sequencing is n=0 on *this* persona until its first wrap-up run.

---

## Fallback if the playbook section is unreachable

Use only **after** SKILL.md persona preflight has **flagged** the gap. Compressed sequence (authoritative text is § Playbook above):
1. Survey already-held wrap-ups of this project; do not re-derive.
2. Classify sources recall-biased (keep ambiguous).
3. Isolated ingest, one subagent per source, extract to temp, schema-capped.
4. Extraction then aggregation loops: each needs DR **and** a numeric cap; both learning levels.
5. Stage publish-safe, hierarchically (`staging/INDEX.md`). Migrate only on explicit grant.
6. Cleanup = prepared bash; human runs it (`06`).
7. Review at plan / staging / post-migrate via `plan-refinement-loop.md`; do not re-derive that loop.

---

## Claude compiler addendum

Cursor runs ignore this section. Claude Code (SKILL.md § Claude Code) uses it. See `reference/host-adaptation-claude-code.md`.

**Staging root:** `ai-persona/ai-notes/wrap-up-staging/<slug>/` — gitignored. **Not** durable persona memory. Same tree shape as the Cursor working folder, plus required `HANDOFF.md`. No `review-loop/` (do not invent a loop).

Ingest-subagent writes go under this root's `extracts/`. WRAP-STATE adds `Host mode: claude-compiler`. Phase table: migrate = **blocked**; review = skip.

### HANDOFF.md (compiler close; Cursor ingest-handoff reads this)

Not a migrate grant.

```markdown
# Handoff — Claude compiler → Cursor migrator
**Date:** <YYYY-MM-DD>
**Slug:** <slug>
**Staging path (inode):** `ai-persona/ai-notes/wrap-up-staging/<slug>/`
**Origin:** Claude Code sibling (compiler). Did **not** write `.cursor/rules/memory/`.

## What is ready
- Hierarchical distillate: `staging/` (see `staging/INDEX.md`)
- Both learning levels present? yes / no (if no, say which is missing)
- Publishability decided at write time? yes / gaps:

## What Cursor should do
1. Invoke `/experiment-wrapup-to-memory` in **ingest-handoff** (this slug).
2. G1 survey; do not re-extract unless a contradicting source appears.
3. Optional: refinement-loop review on `staging/`.
4. Migrate only after an **explicit grant**. This file is not the grant.

## Caps / remaining
- Extraction/aggregation DR+cap: <met | still open>
- Open material Cursor should see: <none | list>
```

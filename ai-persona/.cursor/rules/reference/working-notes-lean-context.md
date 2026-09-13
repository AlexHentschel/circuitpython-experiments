<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-08.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/working-notes-lean-context.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
Fireable cue: WORKING_STYLE.md § Workflow (*Persist task working notes* + sibling *Wrap-up assumes `ai-notes/` may vanish*).
Companion: `ai-notes-convention.md` (git/lifecycle + epistemic role: authority is per-claim confidence).
House: `ai-persona/ai-notes/` gitignored 2026-09-08. Corpus body still calls `ai-notes/` a proposed name.
House overlay 2026-09-11: wrap-up assumes notes may vanish; non-confidential must already live in `memory/` before cleanup.
-->

# Working notes + lean context

**Authored:** 2026-08-31. **Refined:** 2026-09-08 (notes can be SOT when confidence is marked; gitignored ≠ non-authoritative).
Minimally adjusted copy of a starting prompt used with a collaborator; dest-local cold-AI path only.
**Status:** operational discipline. Use as a starting prompt (inspect and adapt) or as standing practice once a notes location is agreed.
**Audience:** an AI running a task — usually a later session of the **same persona** that wrote the notes. Distinct from durable persona memory (`01-MEMORY-SYSTEM.md`) and from the write-time gate (`cold-ai-paradigm.md`, which this document applies). Git + epistemic role of the folder: `ai-notes-convention.md`.

Intent: treat the LLM's chat context window as a cache, not as a durable information store.
Put details and reasoning on disk so you can resume, re-read, and critically reconsider later.
A fresh session with only these files should be able to continue the task. When a spec
exists, keep team-shared durable content there; keep execution-local notes in the
working-notes folder (§1).

## Load-bearing core (the non-relaxable subset)

If you read nothing else, hold these; everything below elaborates them.

- The chat window is a **cache**, not a store: execution detail lives on disk in the
  task's notes folder; only what the current step needs is loaded back in.
- Working notes are **written for a cold AI** — a fresh session with only the files —
  and pass the four checks: decode · purpose · signals · lifecycle (§2).
- **Spec vs working notes:** team-shared durable spec vs this task's working store (§3).
  Notes may hold high-confidence analysis (SOT for the task when so marked). Never apply
  staged spec edits without human sign-off.
- **Long outputs go through a wrapper sub-agent** that returns a short summary plus the
  path to a detail file (§4) — never dump payloads into the caller's window.
- **Detail files are evidence, not just summaries**: cold-AI-readable wrapper + the
  verbatim payload intact (§4).
- **Honor marked confidence; do not silently promote guesses.** Date what can go stale,
  mark unconfirmed claims, treat high-confidence sourced claims as SOT for this task
  until contradicted (§2, §6).
- **Resume lean**: first action = `NOTES.md` + `INDEX.md`; open further files only when
  this session's work needs them (§6).

## 1. Where notes live

`ai-notes/` is a **proposal**, not an established team convention. Paths
written as `ai-notes/` in this prompt mean the agreed working-notes root.

Before creating files: look for an existing ephemeral notes folder in a
contextually meaningful place (this repo, this workstream, next to the spec).

  - If you find one, use it (including if it is already named `ai-notes/`).
    Tell the human domain expert the path. If notes placement has not yet
    come up in this conversation, add the minimal context below (goal +
    lifetime) so they can judge. Do not wait for permission to use an
    existing folder unless they object.
  - If none exists, **ask** where to put temporary ephemeral notes for this
    task. Do not create a folder until they answer. Include the minimal
    context below plus a proposed default, e.g. `ai-notes/<task-slug>/`
    at the path you think is meaningful.

Minimal context (enough to decide, and no more) for the human domain expert:

  - high-level goal of the notes (one or two sentences): persist execution
    detail so this or a later session can continue after compaction or a
    fresh context window; keep the chat lean
  - lifetime: scoped to this task (including later sessions on the same
    task); typically gitignored (not a team-shared *folder*). Claims inside
    can still be SOT for the work when marked high-confidence.

Do not dump this whole prompt into that message. Do not commit secrets.

Once a location is agreed, suggested layout under `<notes-root>/<task-slug>/`
(this prompt uses `ai-notes/` as that default name):

```
  ai-notes/<task-slug>/
    NOTES.md        always-read entry: running notes, or a short map once split
    INDEX.md        catalog of detail files (see §5)
    returns/        full outputs from sub-agents and tools
    briefs/         instructions for child agents (context + pointers)
    spec-staging/   proposed spec edits, if a spec exists (human sign-off
                    before applying them to the spec)
```

Motivation: one task-specific folder is easy to hand to a later session
("read NOTES.md and INDEX.md, then pull other files as needed").

Split by topic when a later session would want one slice of notes without
the rest. If NOTES.md still holds the running body and exceeds ~300-500
lines (~5-20k tokens), move that body into sibling files and leave NOTES.md
as the map: one-line task purpose, list of notes files with a one-line
"open when…", pointer to INDEX.md. Do not add a separate README; that
would be a third entry point. The line-count cap is a heuristic backstop
for the always-read file (tokens re-read every session, and attention), not a
window-capacity limit and not a hard rule. Apply it with reflection:
weigh a thinner always-read map against extra files to navigate and a
map that can go stale. Stay over the cap if the file is still one
coherent slice a later session would want in full, but try not to
exceed about 2× the cap. Past that, a more structured note-taking
approach is usually the better fix (empirically): split by topic and
leave NOTES.md as the map, rather than growing one file further.

## 2. What to write in `NOTES.md`

Maintain detailed working notes for executing this task. Typical contents
(not exhaustive): in-flight findings, open questions, discarded
alternatives, and any reasoning you would otherwise have to reconstruct
if the chat were compacted (older turns compressed or dropped to save
context) or a new session started. Reflect on what else would help
future work on this task, and persist that too. After a
split, that body lives in the sibling files; NOTES.md stays the map.
If there is no spec, also maintain task context, decisions, and guidelines
here (they have no other home), unless task-specific instructions direct
otherwise.

Write for a *cold AI*: a fresh LLM with an empty context window, given
only these files. Full reference: `cold-ai-paradigm.md` (same folder).

Before you consider a note done, check all four:

  1. Decode — every term, abbreviation, and shorthand is grounded in
     the text (or via a path the reader can actually open).
  2. Purpose — it is clear what this claims, decides, or is for.
  3. Signals — it is clear when this still applies, what would confirm
     or refute it, and when a detail file is worth opening.
  4. Lifecycle — it is clear how old this is, how it was last confirmed,
     and whether it is still current.

Honor each note's **marked** confidence. Unconfirmed self-authored claims are not
settled (rereading your own note is not confirmation). High-confidence, sourced
analysis **can be source of truth** for this task until contradicted. Record what
would change the current conclusion so a later session can challenge it.

Motivation: compaction and new chats drop thought chains. Notes that only
this session (with its live chat context) can decode are equivalent to
having no notes.

### Date and mark what can go stale or is unconfirmed

Not all notes age the same way. Discriminate, so the discipline costs
tokens only where staleness is a real hazard:

- **State-bearing entries** (current status, plans, open questions,
  "what we know now") go stale as the task moves: **date them** (and, when
  it matters, what last confirmed them). An old undated status entry is a
  quiet trap: it reads clean and authoritative precisely when it is wrong.
- **Claims about an external system** (code, tool, or API behavior) are
  anchored, not just dated: record the commit SHA / version / date
  observed. The anchor is what makes "does this still hold?" answerable
  after the system changes.
- **Load-bearing unconfirmed claims** — your own conclusions not yet
  confirmed by anything outside this task's notes — carry an explicit
  marker (e.g. `unverified:`) plus what would confirm or refute them.
  Reuse a status vocabulary you already have rather than coining new
  markers. Rereading your own note is not confirmation: one agent
  writing, reading, and judging its own notes is the loop that hardens a
  guess into "settled". Something external must confirm — the human
  expert, a passing test, or the same finding surfacing independently.
  (For durable persona memory, the same principle is the validation
  ladder in `04-EVIDENCE-AND-VALIDATION.md`.)
- **Settled reasoning** (decisions with their why, discarded alternatives,
  mechanism explanations) does not need per-claim dating: it records how
  the conclusion was reached, not the state of the world.

Scale this to the folder's expected lifetime: a single-session task needs
little; a long-lived folder across many sessions needs all of it.

## 3. Spec vs working notes (only when a spec exists)

Do not assume every task is spec-driven. When the work *does* have a spec
(a persisted document shared across the team: requirements, design,
settled decisions, guidelines), discriminate:

  - **Spec** — typically team-shared, durable. Team-visible foundation (task
    context, settled findings, decisions, guidelines) belongs here so the whole
    team can see it.
  - **Working notes** (the folder from §1; this prompt proposes `ai-notes/`) —
    the task working store: local, typically gitignored, editable autonomously.
    May include exploratory scratches *and* high-confidence analysis. Authority
    is per-claim (mark it). After the work, wrap-up compresses and lifts what
    still earns a durable/shared home; until then do not treat the folder as
    "never true." Git/lifecycle: `ai-notes-convention.md`.

You may autonomously *stage* proposed spec edits in `spec-staging/` (dedicated
files in this task folder). Do not apply those staged changes to the spec itself
until the human expert explicitly signs off. If there is no spec, skip
this section; §2 is the whole store.

## 4. Agent-managed sub-processes (keep this session's context lean)

This section applies when the sub-process is itself an agent, or *could*
be outsourced to one: it can follow instructions and shape its return.
MCP (tools reached through an external tool server) is an important
candidate; so are other long-output tools. A raw shell or MCP call has
no such ability, so its full payload would land in this session unless
you wrap it.

When you expect a long output from a shell script, MCP tool, or similar,
wrap the call in a lightweight sub-agent whose job is to run it and
shape the return. Use a lower-tier, significantly cheaper model class
than this session; ask the human domain expert if in doubt.

Pass the child a *very short* prompt: the high-level goal of its task,
plus the path to a dedicated instruction file, and tell it to read that
file before acting. Put the detailed instructions in ephemeral files in
a suitable subdirectory of this task's `ai-notes/` (default: `briefs/`):
context the child needs, plus pointers to further artifacts (scripts,
other notes) it should open on demand. Write those files so the child
can start from them with an empty window. Keeping the instructions in
a file also makes the child's task repeatable and gives you something
to re-read, reflect on, and improve. Do not dump the brief into the
child's chat prompt.

Instruct that child, in its brief (not in the short prompt), to generate
returns of the following shape:

  A. First-hand summary (always) — a concise, detail-dense reply in the
     tool result / chat. Enough to decide the next step. Not a transcript.
  B. Detail file (on demand) — full output plus enough context to answer
     or re-analyze the request later, written **for a cold AI, not for
     the child's own live context**: what was asked, what was run and
     how to read it, what the result was and how far to trust it, then
     the full payload intact below that wrapper. Return the full path in
     the summary. A raw dump alone is not an acceptable detail file
     (undecodable later); a summary alone is not either (the evidence is
     gone). Put this requirement in the child's brief — the child will
     otherwise default to writing for itself.

Require A always. Always give the child a folder for B (e.g.
`ai-notes/<task-slug>/returns/`), even when you expect B to be skipped:
the child must still write B if it has long output that might be of any
relevance to the caller (unexpected edge case, bug in a tool it was
driving). The child is a poor judge of whether details will need
sophisticated analysis or post-processing, so prefer to *demand* B
yourself when that might apply. You may tell it that B can be skipped
when the return is short and straightforward; that skip never overrides
writing B for long output that might be relevant to the caller. If in
doubt, demand B.

Tell the child not to inject large payloads, traces, or tool dumps into
the caller's context as the first-hand summary. If it has long output
that might be of any relevance to the caller, it must write B and put
that output in the detail file; keep the first-hand summary concise for
the caller's window. Include that rule in the child's brief.

Motivation: long or analysis-heavy returns fill this session's context
and then get compacted or dropped. Keep that complete output on disk;
keep only a short summary and the path in the chat. This session stays
lean; a later session can still open the details.

### Who is on the other end (delegation channel calibration)

Both halves of a delegation channel are ephemeral carriers whose
self-containment is set by the **resolution ability** of the far end —
what that side can actually open and consult. The brief (parent → child)
is calibrated by what the *child* can resolve; the return (child →
parent) by what the *parent* can resolve. This applies in both
directions: your agent dispatching a child, and your agent itself being
invoked as a sub-agent by a higher-level agent or tool.

- **Identification convention.** An agent that delegates or invokes a
  sub-agent identifies itself as an agent and states its resolution
  ability, one line, in the brief or invocation. Absence of such
  identification ⇒ presume a **human** consumer (fuzzy default). An
  invocation that is agent-shaped (structured tool framing, orchestration
  vocabulary) yet unidentified: return self-contained-lean and append one
  line with the notes-folder path (useful to every receiver kind).
- **Establishing an unknown far end, ranked.** (1) **Confer:** for
  outbound delegation there is nothing to detect — you author the child's
  context; the brief states your resolution ability as the consumer of
  the return, and for a child with file access points it at your durable
  context (persona memory, the notes tree). (2) **Infer** from verified
  host wiring. (3) **Citation probe**, only when indeterminate (typically
  inbound or cross-host): ask the far end to quote the one-line purpose
  of a context file you name. A named-file quote is hard to hallucinate;
  a bare "do you run the same persona?" invites acquiescence; a
  knowledge check (e.g. "do you know the concept you named?") may
  false-positive on strong general models because the term is largely
  self-descriptive. **Cache the probe result per tool stack; re-probe the
  same stack only after ~3–7 days**, never on every delegation.
- **Return (A) calibration by receiver.** *Same persona* (the parent
  resolves the same durable context): operative content — what the parent
  needs for its next decision — stays **inline in A**; only background
  moves to references. *Foreign agent with its own context*: self-
  contained, persona-neutral digest. *Default LLM* (no custom context):
  self-contained; no persona/context mention (it cannot draw meaningful
  conclusions from it). *Human* (unidentified invoker): human presentation
  conventions — top-down, depth-calibrated, no internal vocabulary.
  B is unchanged: its cold-AI bar already serves every receiver kind.

## 5. INDEX.md (retrievability)

When you receive a return that includes a detail file, add a row to INDEX.md:

  - full path to the detail file
  - date
  - one-line digest, based on the first-hand summary
  - retrieval cue: enough that a later session can judge whether the
    file is worth reading given the task / challenges they may be facing
    (initial, not a closed list — see §6)

Optimize INDEX.md for a cold AI: from the index alone, they should
be able to judge *whether* a given file is worth reading, depending
on the task / challenges they are facing.

## 6. Resume and reconsider

At session start, after compaction, or when stuck: continue the task with a
lean context window. The goal is enough on disk that you can act correctly
after loading into the window, on demand, the files this step needs. Do not
load the whole tree into the window.

Load-bearing for resuming (the rest of the core is at the top of this prompt):

  - First action: read NOTES.md and INDEX.md into the context window.
    They are the entry; do not load every file in the tree into the window.
  - If NOTES.md names a spec, that path is the shared source of truth.
    Load into the context window only the parts the current step needs;
    do not load the whole spec into the window by default.
  - Working notes: if one looks wrong, update it in place and record why
    (and when the correction overturns a prior conclusion, date it — the
    fact that a conclusion changed is itself information). Spec: if it
    looks wrong, stage a proposed edit in `spec-staging/`;
    do not patch the spec without human sign-off.

Before relying on an old state-bearing entry (dated, per §2), triage it:
re-verify, accept with the age in mind, or drop it. Do not silently trust
it because it reads clean; a well-written stale note is the failure mode
the dating in §2 exists to prevent. The reader decides — that decision is
part of the resume judgment below.

Retrieval is judgment, not a script. NOTES.md and INDEX.md give *initial*
cues (which sibling notes, `returns/`, `briefs/`, or `spec-staging/` files
looked relevant when last written). Those cues are starting hints: not a
closed list, not a permission gate. Open a further file when *this*
session's work needs it: the current step, a blocker, a contradiction, a
question the entry files do not answer. Progress and new challenges will
change what matters. Open a file that is not listed if you have a concrete
reason; skip a listed file if it is not needed now. Re-read original
reasoning before silently re-deriving it, when the current work depends
on that reasoning.

If the entry files look stale relative to what you are actually doing,
update them so the next resume is cheaper. That is part of this
discipline, not extra work.

## Knobs you may want to change

- Notes-folder name / location / gitignore (`ai-notes/` is a proposed default,
  not a team convention; confirm with the human if no folder exists)
- When to *demand* a detail file (default: details that may need
  sophisticated analysis or post-processing). The child must still write
  B for long output that might be relevant to the caller, even if you
  allowed a skip.
- Model class for wrapper sub-agents (default: cheaper / lower-tier
  than this session; ask the human domain expert if unsure)
- Always-read size backstop (heuristic, default ~300-500 lines; apply
  with judgment, not mechanically; try not to exceed ~2×); topic-split
  is the primary rule
- Dating / status-marker granularity (default: date state-bearing
  entries, anchor system-behavior claims, mark unconfirmed load-bearing
  claims; lighter than dating every claim — adjust to the folder's
  expected lifetime)
- Sibling files vs a `notes/` subfolder after a split
- Whether INDEX.md is a table, a list, or per-day files
- Spec path convention and `spec-staging/` / `briefs/` layout
- Extra privacy rules for what must never land in `ai-notes/`

## Cross-references

- `ai-notes-convention.md` — git/lifecycle **and** epistemic role: gitignored default ≠ non-authoritative; authority is per-claim confidence. This document covers what goes *inside* the folder.
- `cold-ai-paradigm.md` — the write-time gate this document applies to working notes (decode · purpose · signals · lifecycle). Do not re-derive it here.
- `04-EVIDENCE-AND-VALIDATION.md` — the durable-memory validation ladder (`unverified` → … → `verified`, human-only elevation) behind §2's status markers; also its self-confirmation-loop anti-pattern.
- `01-MEMORY-SYSTEM.md` — durable *persona* memory (SESSION_LOG, WORKING_STYLE, …). Different lifetime and consumer than the task folder in §1.
- `08-BOOTSTRAPPING.md` — first-session persona setup + session-start retrieval of those durable files. This document is the during-a-task counterpart.
- `09-RECURSIVE-LEARNING.md` — sub-agent offload of *memory/reflection* (priority-3 crowding). Distinct from §4 here (wrap long tool output so the *task* window stays lean).
- `plan-refinement-loop.md` §5 — sub-agents as a planning accelerator (crawl/extract vs reason). Distinct from §4 here (return-shape A+B, briefs on disk).

<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-08.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/ai-notes-convention.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
Fireable cue: WORKING_STYLE.md § Workflow (*Persist task working notes*).
Companion for *what goes inside*: `working-notes-lean-context.md`.
House instance: `ai-persona/ai-notes/` gitignored (never tracked). Exp16 `ai-notes/` gitignored + untracked 2026-09-09 (files kept on disk).
2026-09-08 refine: gitignored ≠ non-authoritative; a marked high-confidence claim can be SOT for the task.
House overlay 2026-09-11: wrap-up assumes this folder may vanish; non-confidential must land in `memory/` (parent + ≤1 KB sidecar if needed) before cleanup. Remainder here = confidential/security-sensitive only unless Alex specifies otherwise. Cue: `WORKING_STYLE.md § Workflow` *Wrap-up assumes `ai-notes/` may vanish*.
-->

# The `ai-notes/` folder convention

**Authored:** 2026-09-07. **Refined:** 2026-09-08 (authority is per-claim confidence; gitignored ≠ non-authoritative).
**Status:** operational discipline. Best-practice default plus the tolerated exceptions.
**Audience:** an AI running a task in someone's repo. Companion to `working-notes-lean-context.md` (what goes
*inside* the folder and how to keep the chat lean). This file covers *git/lifecycle* and the *epistemic* role of
the folder: it is a task working store, not “never a source of truth.”

---

## 1. What it is

`ai-notes/` is the AI's **task working store**: local, per-person, per-machine, and by default **not committed**.
It holds information needed to execute and resume the work: running notes, analysis (including high-confidence
findings), exploratory scratches, dead-end paths, pending-work reminders, session context, and resume prompts.

It fills a specific gap. Durable persona memory is too sparse and too expensive (structure, semantic links,
cross-task extraction) to carry every interim chain. The chat window is a cache that gets compacted or dropped.
`ai-notes/` is the on-disk continuity buffer. Much of it may become irrelevant once the work completes — that is
a *lifetime* property, not a claim that nothing in it is true.

## 2. Two orthogonal questions (do not collapse)

### Git / sharing

Typically gitignored. Colleagues are not expected to have the folder. Committed team deliverables (README, `lib/`,
shared spec) must stand alone if `ai-notes/` vanished. Rules: §3.

### Authority / confidence

A claim in `ai-notes/` **can be source of truth** for the task. That depends on the confidence of the analysis or
source that produced it — **not** on the folder name.

- Mark reliability **on the content** (reuse a status vocabulary you already have: e.g. `unverified` /
  `evidence-supported` / `hypothesis` / `dead-end`). Honor a high-confidence marked claim.
- Do not treat an unmarked guess as settled. Rereading your own note is not confirmation (`cold-ai-paradigm.md`
  self-confirmation loop; `working-notes-lean-context.md` §2).
- Typical folders contain a lot of exploratory scratches. That is common, **not required**. Dense, careful
  analysis belongs here too when that is the work.

### Structure bar vs durable persona memory

In `ai-notes/` you may **unpack**: more volume, dead-end detail, lighter structure. You do not yet know which
exploratory paths will earn a durable home — that becomes clear as the work concludes or progresses.

Durable persona memory is where it **pays** to structure, clean, and draw semantic connections, and to extract
higher-level methodical / collaborative / technical learnings. At wrap-up, compress and lift what still earns
that home; do not dump the whole folder. (A worked wrap-up playbook lives with personas that have instantiated
it; do not invent one here.)

### Audience

Write for a **cold AI**, in the vast majority of cases running the **same persona** that wrote the notes.
The human may ask a vanilla LLM (no persona) to drop notes here temporarily; if those notes matter, they will
prompt the governing persona to incorporate and clean them.

## 3. The rules (git / lifecycle)

1. **Default to gitignored. This is the best practice.** Add the folder to `.gitignore` at the right scope (see §4).
   A pattern like `**/ai-notes/` catches nested ones. Never commit it as part of normal work.
2. **Keep the git-dependency one-directional.** Notes may reference the versioned deliverable. A committed *team*
   deliverable must never require the notes, and it must stand alone if `ai-notes/` vanished. A committed README/`lib/`
   path into `ai-notes/` is a defect for colleagues who do not have your local folder. This is a *sharing* rule, not
   an authority rule: the notes may still be SOT for the agent doing the work.
3. **Do not build shared or committed structure inside it.** No per-author committed subfolders, no "shared" committed
   subfolder. Structure others would rely on belongs in the versioned deliverable or, after wrap-up, in durable memory.
4. **Never reference machine-local or per-person state from any committed team deliverable.** Absolute local paths,
   another person's memory, `ai-notes/` paths: none of these are equally available to every colleague. Before writing
   a path into a committed file, ask whether every colleague has that exact thing. (Session logs / changelogs that
   *mention* that notes existed, without making the gitignored path the only home of a durable claim, are a different
   case.)
5. **Never untrack an already-tracked `ai-notes/` on your own initiative.** Adding a not-yet-tracked path to
   `.gitignore` is fine. Removing an already-tracked path from version control changes shared history, so surface it
   and get the human's sign-off first. Keep the files locally either way.

## 4. Scoping: `ai-notes/` is not necessarily one-per-repo

Place `ai-notes/` at the granularity that matches the work, not always at the repo root.

- A conventional single-purpose repo has one `ai-notes/` at its root.
- A repo that is a **collection of stand-alone units** (for example, one folder per self-contained experiment) may
  instead give **each unit its own `ai-notes/`** (an experiment keeps its own experiment-scoped store beside it).
  This is explicitly fine and often clearer: the working store lives next to the thing it serves. Gitignore the
  matching paths accordingly.

## 5. The tolerated exception (best practice still stands)

You may find a repo where an `ai-notes/` folder **is** checked in. This is an accepted **transitional state**, not the
target: it usually means durable-for-the-team content and task-local content have not yet been separated, so the
folder stays committed until they are. Handle it like this:

- Treat it as a **cleanup opportunity, not a template to copy.** End state: wrap-up lifts what still earns a durable
  home (versioned deliverable and/or persona memory); the remainder stays gitignored working store.
- **Do not untrack it on your own initiative** (rule 5). Surface it and let the human decide.
- Until then, keep applying rule 2: add no new committed *team-deliverable* references that point into it.
- When you author fresh guidance or set up a new folder, the recommended default is still gitignored.

## 6. Quick checklist

- Is this **task working store** (`ai-notes/`, confidence-marked) or a **durable/shared home** (versioned deliverable
  or persona memory after wrap-up)?
- Is each load-bearing claim **marked** for confidence/source — and would a high-confidence one be treated as SOT?
- Is `ai-notes/` **gitignored** at the right scope (repo-root or per-unit)?
- Does any **committed team deliverable** depend on `ai-notes/` or other machine-local state? (Must be none.)
- About to **untrack** an already-tracked `ai-notes/`? (Stop: ask the human first.)
- Found a **checked-in** `ai-notes/`? (Flag it as transitional; do not replicate it; do not untrack without grant.)

## Cross-references

- `working-notes-lean-context.md` — what to put *inside* the folder (NOTES.md, INDEX.md, returns/, briefs/,
  spec-staging/) and how to keep the chat window lean. Companion: this file is git + lifetime + epistemic role.
- `cold-ai-paradigm.md` — write for a cold reader; mark unconfirmed claims; self-confirmation loop.
- `05-CODE-AND-DOCUMENTS.md` — self-contained committed documents (the committed-side of rule 4).

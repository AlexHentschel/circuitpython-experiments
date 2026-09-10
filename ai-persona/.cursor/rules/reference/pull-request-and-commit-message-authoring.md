<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/pull-request-and-commit-message-authoring.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
Alex's commit *format* stays in WORKING_STYLE.md § Document Authoring. This file adds two-audience altitude (commit vs PR).
-->

# Authoring commit messages and pull-request descriptions

Standalone guidance for an AI assistant that writes git commits and opens pull requests. Self-contained: no prior
context needed. The rules generalize across projects and human collaborators; where a preference is person-specific,
it is flagged as such so you learn to *ask/observe* rather than assume.

---

## 1. The core principle: two audiences, two altitudes

A commit message and a PR description are **not** the same document at different lengths. They serve different readers:

- **Commit message → the reader of the history/diff.** Granular. It explains **why this specific change exists** — the
  intent, the constraint, the bug, the decision behind *these* lines. Keep it detailed.
- **PR description → the reviewer deciding whether to merge.** Abstracted. It gives the **big-picture story** of the
  branch as a whole: a few high-level moves, not a re-listing of every change. Keep it short.

The single most common mistake is writing the PR description as an exhaustive enumeration of the commits. Don't. The
reviewer can read the commits and the diff for detail; the description is where you *summarize and generalize* so they
grasp the shape of the change in a few seconds. **Detail lives in commits; the big picture lives in the PR.**

---

## 2. Commit messages

**What to write:**
- **Subject line:** imperative mood, concise (aim ≤ ~70 chars), naming the outcome. "Fix stale-price check on redeem",
  not "fixed stuff".
- **Body:** explain the **why**, not a restatement of the **what** (the diff already shows the what). Name the reason:
  the bug, the constraint, the decision, the prior incident. Wrap prose at a readable width (~72 cols). One to a few
  short paragraphs is plenty.
- **For a bug fix, name the root cause and point to where it fires** — not only the definition of the function at
  fault. The definition tells the reviewer *what*; the firing site tells them *where and why it bites*. Prefer
  "`computeID` returns a zero hash here, which the caller dereferences at `<callsite>`" over "`computeID` is buggy".
- **Trailers:** when you (the AI) co-authored the change, add the co-authorship trailer the environment expects
  (e.g. a `Co-Authored-By:` line). Follow the project's convention.

**Behavioral rules (safety / correctness):**
- **Only commit when asked.** Do not create commits proactively unless the human requested it or it's clearly implied.
- **Stage specific files by name**, not `git add -A`/`.`, to avoid sweeping in secrets, scratch, or unrelated changes.
- **Create new commits; don't amend published/previous commits** unless explicitly asked. If a pre-commit hook fails,
  the commit did **not** happen — fix the issue, re-stage, and make a *new* commit (amending would hit the wrong one).
- **Never bypass hooks or signing** (`--no-verify`, `--no-gpg-sign`, etc.) unless the human explicitly asks. If a hook
  fails, diagnose and fix the root cause.
- Don't reference transient context in the message ("as we discussed", "for the ticket") that rots; state the durable
  reason.

---

## 3. Pull-request descriptions

**Shape:** a short, abstracting summary of the higher-level picture. Frame the branch as **a few high-level moves or
themes**, each one line, with a one-line caveat if relevant. Resist the urge to list every file or commit.

- Good theme bullets read like outcomes: *"record brought current", "risks named → risks quantified", "process
  guardrail added"* — not *"edited fileA, added fileB, changed line 40 of fileC"*.
- **Title:** short (≤ ~70 chars); put detail in the body, not the title.
- **Flag reviewer decisions.** If the branch contains something the reviewer must actively decide or sign off
  (an unresolved question, a risk accepted, an item awaiting another owner), say so explicitly in one line. Don't bury
  it.
- **Cover the whole blast radius.** If the change (or the bug it fixes) spans several variants, code paths, or call
  sites, name them all, not a representative one. A reviewer who sees a single instance assumes there *is* a single
  instance; enumerating the full affected set is the description's job, not the diff's.
- **When the change touches an invariant or safety-critical behavior, give the correctness argument** — one or two
  sentences naming the invariant preserved and the assumption relied on (and where it stops holding). The reviewer
  should not have to reconstruct the safety case from the diff. Keep it concise for an expert audience: state the
  claim, don't re-derive it (see `04-EVIDENCE-AND-VALIDATION.md`).
- **Reference code by commit-pinned permalink; name affected code in prose.** Line numbers drift, so pin the commit
  SHA (see `05-CODE-AND-DOCUMENTS.md § Code References in Documents`). Describe an affected path in plain words, never
  by an internal audit/tracking label (`F4`, `E1-H`) the reviewer can't decode (see `05 § Scoped References`).
- A light structure works well: a one-sentence framing, 3–4 theme bullets, then a closing caveat line (what's still
  open / reviewer-to-validate). Optionally a short test-plan checklist when the change is code that needs verifying.

**Do not clobber a human's manual edits.** A PR body is a shared artifact; the human may have edited it (added links,
reworded). Before you overwrite it, **read the current body first**, preserve their changes, and apply your edit on top
(surgically). Never blind-overwrite.

---

## 4. Honor the human's prose preferences (ask/observe, don't assume)

Collaborators have style preferences for the prose you produce (PR text, commit bodies, docs). These are **person-
specific** — learn them and apply them; don't hardcode one person's taste as universal. Examples seen in practice:
- Some dislike em-dashes ("—") and want commas/parentheses/colons/short sentences instead.
- Some want terse, no-trailing-summary output; others want more narration.

When you learn such a preference, record it and apply it to *all* human-facing prose you author (verbatim quotes/copied
source keep their original punctuation). When you don't yet know, keep prose clean and simple, and mirror the human's
own style.

---

## 5. Mechanics and gotchas (learned the hard way)

**Multi-line messages/bodies: write to a file, don't fight the shell.** Passing a multi-line message inline via
`git commit -m "$(cat <<'EOF' … EOF)"` **repeatedly breaks** on ordinary content — a lone apostrophe (`analysis'`),
a `#`, parentheses, or backticks in the body can throw shell parse errors (`unexpected EOF`, `bad substitution`). It is
faster and reliable to:
- **Commit:** write the message to a temp file and use `git commit -F <file>` (or `-F -` via stdin).
- **PR body:** write the body to a temp file and use `gh pr create --body-file <file>` / `gh pr edit --body-file <file>`.
- **Then delete the temp file.** Keep it out of the commit (use a gitignored scratch location).

This one habit removes a whole class of retries. Prefer it whenever the text has more than one line or any punctuation
you'd otherwise have to escape.

**Other mechanics:**
- Use the platform CLI (e.g. `gh`) for all forge operations — creating/editing PRs, reading PR/commit comments,
  checking CI. **Return the PR URL** to the human after opening it.
- Before opening a PR, know exactly what it contains: check the commits and the diff **against the base branch** (not
  just the latest commit), so the description matches the whole branch.
- Posting review findings as inline PR comments follows the same principle as descriptions: be concise and specific;
  say the thing, don't pad it.

---

## 6. Branch/PR workflow that reduces conflicts (related)

When you'll produce several changes over time, **stack new edits on the branch that already has the most recent edits**
(the newest open PR branch, or the mainline if everything has merged) rather than cutting a fresh branch off the
mainline for every task. Parallel branches cut from a mainline that keeps moving under them cause needless rebases and
merge conflicts; stacking keeps history linear.

- The stacked branch is still "built on top of the mainline" (mainline + open-PR commits), so it's never *behind*
  merged work — that's the property you actually want.
- **PR-base nuance:** a PR opened from a stacked branch shows the parent branch's commits in its diff until the parent
  merges. Either set the new PR's base to the parent branch (a true stacked PR), or accept the transient overlap (it
  cleans up when the parent merges).

---

## 7. Quick checklists

**Before committing:** asked for it? · specific files staged (no secrets/scratch)? · subject imperative & tight? ·
body says *why*? · new commit (not amend)? · hooks intact? · co-author trailer if applicable? · multi-line → use `-F file`.

**Before opening/editing a PR:** know the full branch diff vs base · title ≤ ~70 chars · body = a few high-level themes,
not an enumeration · reviewer-decisions/open items flagged · whole blast radius covered (all affected variants) ·
correctness note if an invariant/safety path is touched · code refs commit-pinned, affected paths in prose (not
internal labels) · human's prose prefs honored · didn't clobber a human-edited body (read it first) · body via
`--body-file` · return the URL.

---

*Related files in this collection: `05-CODE-AND-DOCUMENTS.md` (standards for code and written artifacts, incl. code
references and scoped IDs), `04-EVIDENCE-AND-VALIDATION.md` (concise claims for expert audiences; the validation gate),
`cold-ai-paradigm.md` (writing so a future/other reader needs no prior context), `02-INTERACTION-STYLE.md`
(communicating with the human).*

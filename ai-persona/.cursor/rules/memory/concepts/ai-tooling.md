# Concepts — AI tooling & persona self-improvement

`[domain:ai-tooling]` `[meta]` — **seeded 2026-09-15 by explicit human direction, as a deliberate exception to seed-on-evidence (C7)**. Alex is confident concepts here will accrue soon (measurement harnesses, Cursor SDK, probe design, memory-maintenance mechanics), so the domain is created ahead of its first concrete concept to give those learnings a deterministic home. Reusable, tooling-level knowledge about how *this persona* is built, measured, and improved — as opposed to the *process discipline* (which lives in `../../reference/*` + `00-memory-system.mdc`) and the *active workstream* (which lives in `projects/ai-tooling/`). Retrieval: `_INDEX.md` → here → `#concept`; lateral edges in `_RELATIONS.md`.

**Scope boundary (so entries route correctly):**
- **Here (`concepts/ai-tooling.md`)** — reusable *domain knowledge*: measurement-harness mechanics, Cursor Python SDK behavior/gotchas, probe/eval design, permissions-model quirks, memory-structure techniques that generalize beyond one cycle.
- **Not here** — the *how-we-run-a-cycle* discipline (→ `reference/plan-refinement-loop.md`, `reference/10-adaptive-memory-structure.md`, `reference/cold-ai-paradigm.md`, `00-memory-system.mdc § Maintenance`); the *current cycle's* notes/decisions/status (→ `projects/ai-tooling/`); behavioral/coding directives (→ `universal/`).
- **External method/harness source** (read-only, NOT this persona): the `high-assurance-engineering` persona — `/Users/alex/Git/onflow/high-assurance-engineering` (method `…/.cursor/rules/memory/concepts/authoring/memory-maintenance-cycle.md`; harness + prior-run archive `…/ai-notes/2026-09-15_memory-maintenance-cycle/`).

## Concepts

### Claude Code memory loading (how persona files become always-resident context)

`evidence-supported` (official docs, read 2026-10-20 via the `claude-code-guide` agent: `code.claude.com/docs/en/memory.md`, `…/context-window.md`, `…/errors.md`). Not yet exercised on this persona.

- Claude Code does not read `.cursor/rules`. Files become resident only through: `CLAUDE.md` / `.claude/CLAUDE.md` / `CLAUDE.local.md` (cwd and parents), `~/.claude/CLAUDE.md`, unscoped `.claude/rules/**/*.md`, auto-memory `MEMORY.md` (first 200 lines / 25 KB), plus a SessionStart hook's `additionalContext`. `/context` lists the loaded files under Memory files.
- No copying: an `@path` line in a CLAUDE file inlines that file's current disk contents at launch. Relative to the importing file; absolute and `~/` allowed; max 4 hops; `@` inside backticks or code blocks is not imported. A target outside the cwd triggers a one-time per-project approval dialog (`~/.claude/` files excepted).
- `.claude/rules/`: recursive, symlinks followed (an `.md`-named symlink to an `.mdc` works; frontmatter other than `paths:` ignored). `paths:` globs defer loading until Read/Write/Edit touches a matching file.
- Compaction: root CLAUDE files, unscoped rules and auto memory are re-injected from disk; `paths:` rules and nested CLAUDE.md reload only on the next matching touch.
- Size: recommended < 200 lines per CLAUDE.md; startup + `/status` warning when over, or when the combined total is large (threshold undocumented); a single file over 4 MiB is skipped. `CLAUDE.local.md` is current (not deprecated). `--add-dir` directories' CLAUDE files load only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`.
- Applied here: see central `SESSION_LOG.md` 2026-10-20 (loader for this persona, decided in part, not built).

### Reviewing Claude Code edits in Cursor (no Cursor-style inline review)

`evidence-supported` for the extension behavior (docs read 2026-10-20: `code.claude.com/docs/en/vs-code.md`, `…/permission-modes.md`, `…/checkpointing.md`); the Cursor-specific parts are `unverified` (docs do not mention Cursor).

- Cursor's inline green/red agent review is Cursor-internal; the Claude Code extension documents no lasting added/removed-line highlight after an edit applies.
- Pre-apply review exists only in Manual (`default`) mode: side-by-side native diff, accept/reject, editable before accept; per-change buttons from v2.1.275 (not for diffs over 100 changes). Auto / Edit-automatically / bypass apply without a diff. Setting `claudeCode.initialPermissionMode` (no `auto` value); no diff-display setting.
- After the fact: the editor's git gutter (compares to the staged index, `unverified` in Cursor) — stage before a session for a clean Claude-only baseline; or `git diff`. Checkpoints ("Rewind code to here") undo per turn but skip Bash-made file changes and usually subagent edits.
- Kilo Code (rebuilt VS Code extension; docs read 2026-10-20: `kilo.ai/docs/code-with-ai/platforms/vscode/whats-new`, `kilo.ai/docs/code-with-ai/features/checkpoints`): also no documented Cursor-style in-editor highlight. Stronger after-the-fact review than Claude Code: per-message diff badge → Diff Viewer; Agent Manager reviewer (file by file, unified/split, line comments); patch diffs in the permission prompt; sidebar badge with session +/- counts; snapshots per user message (`snapshot` in `kilo.jsonc`; git-ignored files excluded); `/local-review-uncommitted`. Per-hunk accept/reject not documented. Not tried in Cursor.

### Cursor agent inline diff attaches only to native edits

`evidence-supported` for the mechanism (Cursor staff on forum.cursor.com, read 2026-10-23). Whether this session's probe highlighted is still open — Alex has not reported it.

The red removed lines kept in the buffer, with the new lines in green under them and Keep / Undo, are Cursor's agent review overlay. It compares the pre-edit editor buffer to the agent patch. A git repo is not an input to that overlay. The git gutter is a separate, thin margin mark and does not keep old lines in the buffer.

Three ways the overlay stays off, which matches "the file just changed, as if an outside program wrote it":

| Cause | What happens | How to tell |
|---|---|---|
| **Inline Diffs off** (auto-keep) | Every native edit lands immediately, no Keep / Undo | Cursor Settings → Agents → Applying Changes → Inline Diffs. The section is in the Editor Window; the Agents Window hides it (`Cmd+Shift+P` → Open Editor Window). Off and on, then fully quit, if the toggle already looks on. Staff: threads [156889](https://forum.cursor.com/t/how-to-disable-auto-keep/156889), [161325](https://forum.cursor.com/t/cursor-3-5-17-removed-keep-undo-and-applies-agent-changes-directly/161325), [165428](https://forum.cursor.com/t/inline-review-feature-with-keep-revert-missing-since-recent-updates/165428), [162532](https://forum.cursor.com/t/after-updating-cursor-agent-mode-applies-file-changes-directly-to-disk-with-no-red-green-inline-diff-and-no-keep-undo-or-accept-reject-controls-settings-that-used-to-control-this-either-dont-exist-in-my-ui-or-have-no-effect-this-removed/162532) |
| **Partial-highlight bug** | First hunk (sometimes a couple) gets red/green; later hunks in the same turn apply with no highlight, including in Review | Chat still lists the later edits. Staff, 2026-02-19, threads [152099](https://forum.cursor.com/t/only-some-diffs-are-shown-whhen-agent-makes-changes/152099) and [152208](https://forum.cursor.com/t/the-diffs-are-not-rendering-in-ide-as-agent-makes-code-updates/152208). One auto-apply regression was called fixed 2026-04-07 ([154887](https://forum.cursor.com/t/regression-ai-edits-applying-automatically-without-diff-approval-ui/154887)); visibility reports continued ([157404](https://forum.cursor.com/t/agent-changes-no-longer-show-in-files/157404), [158321](https://forum.cursor.com/t/inline-diff-bug-is-back/158321)) |
| **Shell / script write** | Python, `sed`, `cat`, or any terminal write hits disk; the editor reloads via the file watcher | The turn shows a terminal command, not a file-edit card. Review panel and "Last Agent Turn" omit them. Source Control and Agents Window → Changes → Uncommitted still show them when the file is in git. Staff: [162348](https://forum.cursor.com/t/agent-edits-made-via-the-terminal-script-shell-writes-dont-appear-in-the-inline-edit-review-ui/162348), [167478](https://forum.cursor.com/t/cursor-grok-4-5-model-does-not-make-inline-diff/167478), [174000](https://forum.cursor.com/t/llm-not-using-apply-patch-when-generating-code/174000). Some models prefer this path |

Probe, 2026-10-23: one native file-edit (not a shell write) appended four comment lines at the end of a `.tex` file in a folder outside this persona's projects. That tree has no `.git`. A pure insertion has no red lines; green on the new comments means the overlay attached.

## Candidate concepts (`[anticipated]` — pointers, NOT yet established knowledge)

These are expected to graduate into real `### concept` entries above once observed/verified *on this persona's own tooling*. They are recorded here only for discoverability; do not cite them as findings. Primary source for all: the lifecycle launcher prompt `../projects/ai-tooling/lifecycle-kit/launcher-prompt.md` (preserved in-tree) + the HA methodology bundle above.

- **Cold-AI retrieval probe harness (Cursor SDK)** `[anticipated]` — stages a rule-tree copy into a fresh temp `.cursor/rules`, runs cold-AI probes via the Cursor Python SDK (venv `/Users/alex/Development/PythonVEs/flow`, py3.10), captures which files the cold AI opens; the file-reach delta between two versions is the discoverability signal. Persona-agnostic (`../projects/ai-tooling/lifecycle-kit/harness/run_probe.py`) — point it at this persona's tree, not HA's. *To verify on first run against this persona.*
- **Harness permissions gotcha** `[anticipated]` — the probe must run out-of-sandbox (creates a temp dir) and Cursor auto-review misreads planted probe tokens as "secret exposure"; unattended runs need an `~/.cursor/permissions.json` "always allow" entry naming the exact command + pinned interpreter. Re-issuing such an entry is a permissions grant → human-gated. *To confirm the exact entry shape at calibration.*
- **Stale expected-reach keys** `[anticipated]` — each probe's "files a good persona should surface" key is layout- and domain-specific; reused keys from another persona/layout are wrong. Regenerate keys against a fresh live inventory at calibration. *To operationalize for this persona's domains.*
- **Additive-first structural edits win** `[anticipated, cross-experiment candidate]` — prior HA run: every measured discoverability win was additive (new index/hub/back-link), not a destructive move. *To retest here; if it holds, promote toward `universal/PATTERNS.md` via `crossref/BY_PATTERN.md`.*

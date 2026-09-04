# Domain: git / version-control & publishing hygiene

`[domain:git]` `[cross-experiment]` — tooling knowledge, reusable by any project (not CircuitPython-specific). Seeded
2026-07-15 from the coding-tutor copyright-remediation work (see `projects/coding-tutor/SESSION_LOG.md`). Status per
concept below; the three seeded here are `evidence-supported` (verified on-device 2026-07-15 against a real public repo).

---

### concept: History rewrite does NOT remove data reachable via merged-PR refs  `evidence-supported`
- `git filter-repo` + force-push rewrites `refs/heads/*` and `refs/tags/*`, but GitHub's `refs/pull/<n>/head` (and
  `/merge`) are **server-side, read-only**; `git push --mirror` cannot update them (rejected: *"deny updating a hidden
  ref"* — expected, harmless).
- **Consequence**: a file removed from all branch history is still **browsable via the merged PR's Files/Commits pages**,
  pinned to the pre-rewrite commit SHA. Verified 2026-07-15: after scrubbing a file, `contents?ref=master` → 404, but
  `gh api repos/<o>/<r>/pulls/1/files` still listed it (PR head = the old commit SHA).
- Only **GitHub Support** can purge PR-referenced commits + cached views; no self-service route.
- After force-push, orphaned commits also stay reachable by **full 40-char SHA** until GC; a **fork network** keeps them
  alive indefinitely. Check exposure with `gh api repos/<o>/<r> --jq '{forks_count, network_count, visibility}'`.
- **Implication for planning a scrub**: "remove from a public repo" is not achieved by history rewrite alone if the data
  ever went through a merged PR — decide up front whether bare-SHA/PR browsability is acceptable or a Support request is
  needed.

### concept: Scrub a file from all git history (recipe)  `evidence-supported`
```
git clone --mirror <url> scrub.git && cd scrub.git
git filter-repo --path "<path/with spaces ok>" --invert-paths --force
git push --force --mirror <url>          # re-specify URL: filter-repo drops the 'origin' remote by design
```
- Operate on a **fresh `--mirror` clone** so the working repo is untouched. filter-repo prunes commits that become empty;
  commits with other changes are kept **minus** the path.
- Requires `git-filter-repo` (`pip install git-filter-repo` / `brew install git-filter-repo`); it installs a
  `git-filter-repo` helper on PATH, invoked as `git filter-repo`.
- After the push, **re-sync every working clone**: `git fetch && git reset --hard origin/<branch>` per branch, and
  `git branch -f <b> origin/<b>` for branches not checked out. `git-ignored local copies survive `reset --hard`.
- **Caveat**: does not touch PR refs / cached views (see prior concept).

### concept: `git rm --cached` is all-or-nothing across pathspecs  `evidence-supported`
- If **any** listed path is untracked, the command aborts (*"fatal: pathspec '…' did not match any files"*) and removes
  **nothing** — not even the tracked paths in the same invocation. Pass only tracked paths; keep untracked files out via
  `.gitignore` instead. (Observed 2026-07-15: a mixed tracked+untracked `git rm --cached` no-op'd entirely.)
- Note: adding an **already-tracked** file to `.gitignore` has no effect until it is untracked (`.gitignore` only governs
  untracked files).

## Cross-references
- Origin + full narrative: `projects/coding-tutor/SESSION_LOG.md` (2026-07-15 remediation).
- Reusable *process* (attribution/licensing workflow, not git mechanics): `universal/PATTERNS.md` (promoted 2026-09-04; provenance `crossref/BY_PATTERN.md`).
- Behavioral directive derived here: `universal/WORKING_STYLE.md § Judgment & Escalation` ("verify blast radius…").

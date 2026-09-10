# Permitted Destructive-Actions Ledger (master)

Authority checked **before** any non-trivially-reversible action.
**Absence of a matching active entry = no permission** (fail-closed).

Protocol: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md` §6 (schema) and §5 (how a grant is obtained). Durable copy: `../../reference/destructive-operations.md`. Always-on stub: `../../06-destructive-operations.mdc`.

Grants are **per exact file/folder/operation**, single-use unless `expiry` says standing. Conversation "yes" is not a ledger entry until recorded here after a §5 round.

## Confirmed park locations (not grants)

A confirmed §4 destination is **not** permission to delete. Deleting a parked copy still needs an Active grant below.

| workstream | path | confirmed | notes |
|---|---|---|---|
| Exp16 (`circuitpython-exp16-planetx`) | `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/_parked/` | 2026-09-04 Alex | Policy + MANIFEST in that folder. Exp16 only. Path endorsed ("happy with") same day. |

## Active grants

_none_

## Spent / historical grants

| id | date | granted-by | scope | exact-request | trigger-word | covered-set | status | expiry |
|---|---|---|---|---|---|---|---|---|
| `G-2026-09-09-1` | 2026-09-09 | Alex | History rewrite: remove Exp16 `ai-notes/` from git history | “commit, perform history scrub and provide bash commands for delete/clean-up (I will run them).” | history scrub (this message) | **SUPERSEDED / NOT APPLIED (2026-09-09).** Local `filter-repo` was executed + verified on `/tmp/circuitpython-experiments-scrub-20260909.git`, but Alex then clarified the ai-notes are **noise, not confidential — they may remain in GitHub history**. No force-push / rewrite applied to any real repo. New plan is strictly non-destructive: fast-forward `git push origin alex/display-mvp_5x5` (publishes untrack commit `ae8ac09`); master left untouched. The /tmp scrub is unused (safe to delete). **Nothing destructive was done to the working repo or GitHub.** | `spent (unused)` | single-use (this scrub) |
| `G-2026-09-08-1` | 2026-09-08 | Alex | Untrack Exp16 `ai-notes/` after lifting durable bits into `Notes/` + persona memory; gitignore the folder; **files stay on disk** | Lift durable bits into memory/spec, then gitignore the rest. Untracking granted. | `untracking granted` (message: “please go ahead. untracking granted”) | Executed 2026-09-09: `git rm -r --cached -- 2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes` (34 index paths); gitignore `**/ai-notes/` (repo) + experiment `.gitignore`. Commit `ae8ac09` (pre-rewrite; rewritten tip `1cb43d2`). **Not granted / not done:** delete working-tree files, history rewrite, `filter-repo`, force-push, park-folder delete | `spent` | single-use (this untrack) |

# Memory Maintenance Backlog

Deferred, non-trivial memory-lifecycle work (splits / merges / re-tags / reorgs / marker changes) to batch into a deliberate, **user-gated** maintenance iteration — *not* done as a side effect of task work (`00-memory-system.mdc § Maintenance` rule 5). Running an iteration is gated like compaction; proactively *recommend* one when this list grows or retrieval degrades. Log each completed action in `universal/CHANGELOG.md` and strike it here.

Created 2026-06-15 (first entry).

## Open items

_None._ (DN-MP-1 new-project-vs-extend heuristic is at the “refine after 3–5 projects” review point — **not** auto-queued here; escalate if Alex wants a pass.)

## Completed

- [x] **Promote the concept-graph / retrieval-placement layout from PROVISIONAL → confirmed.** Executed **2026-09-08** (Alex grant: “please proceed with pass”). Edit set followed `ai-notes/provisional-marker-pass/analysis/marker-inventory.md`, not only the original three-file list. Durable record: `universal/CHANGELOG.md § 2026-09-08`. Did **not** re-open dedicated-root (2026-07-15). Did **not** rewrite `00-memory-system.mdc § Content vs structure` (future structure still gets a provisional marker).

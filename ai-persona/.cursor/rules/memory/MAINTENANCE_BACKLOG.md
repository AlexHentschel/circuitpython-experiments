# Memory Maintenance Backlog

Deferred, non-trivial memory-lifecycle work (splits / merges / re-tags / reorgs / marker changes) to batch into a deliberate, **user-gated** maintenance iteration — *not* done as a side effect of task work (`00-memory-system.mdc § Maintenance` rule 5). Running an iteration is gated like compaction; proactively *recommend* one when this list grows or retrieval degrades. Log each completed action in `universal/CHANGELOG.md` and strike it here.

Created 2026-06-15 (first entry).

## Open items

- [ ] **Promote the concept-graph layout from PROVISIONAL → confirmed.** The `concepts/` multi-project layout has carried a PROVISIONAL marker since the 2026-06-14 warm reset, with the watch-for: *confirm = real domain queries resolve one-hop (index → domain → concept) with deterministic placement; refute = multi-file scanning / wrong-bucket writes / a finding with no deterministic home.* **Evidence to date (2026-06-15):** 2 new domains seeded (`i2c`, `power`) totalling 12 concepts, each landing one-hop via `_INDEX.md`, placement deterministic, cross-domain components handled by primary-home + cross-ref (MAX17048), and a real taxonomy fork (`fuel-gauge`→`power`, `sensors` deferred) resolved cleanly under the placement gate — **no refute signal**. This is past the marker's "~5 additions" trigger.
  - **Action when run:** remove the PROVISIONAL block from (1) `concepts/_INDEX.md` header, (2) `projects/_INDEX.md` header, (3) `04-multi-project.mdc` header; replace with a one-line "confirmed 2026-06-?? after N additions, see CHANGELOG" note. Log in `universal/CHANGELOG.md`.
  - **Why gated:** edits Level-2/3 structural headers across rule + memory files; should be a deliberate pass, not folded into feature work. Surfaced 2026-06-15 (Alex chose to defer; this is the record).

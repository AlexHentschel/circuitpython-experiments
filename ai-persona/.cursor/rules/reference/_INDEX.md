# Reference — Index (read-on-demand depth layer)

<!-- provisional (added 2026-09-15, memory-lifecycle iter1). Level-2 structure per 00-memory-system.mdc:37 + reference/10-adaptive-memory-structure.md §7.
     Watch-for (re-evaluate / retire if any fires):
       (1) a new reference/ file lands without a matching index line here (index went stale → tighten the update trigger, or the index is not pulling its weight);
       (2) the index is not consulted across ~3+ sessions where a reference-layer topic came up (F-S4 unused-structure → demote to a plain See-also list or drop);
       (3) an always-read anchor to this index is removed, re-orphaning it (F-S1 premature-commitment → the hub was load-bearing on one fragile link). -->

`reference/` is the persona's **depth layer**: long-form rationale and method docs pulled **on demand**, not at session start. It is **not** house source of truth — the House SOT is the always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`/`CODING_PRINCIPLES.md`. These files are capability **snapshots / recipes** (most are corpus snapshots, ingest 2026-09-07); read one when a task or a "Fireable cue" from an always-read file points here. Do **not** port their legacy artifacts into the house (corpus `verified` tier, flat `TECHNICAL.md`, `08`'s Genesis path, `11`'s literal tree, symlink-fanout).

Retrieval: an always-read file's cue or `.mdc § See also` names a file → open it here (one hop). This index is the map when you know the *topic* but not the filename.

Two series: **numbered `00`–`11`** (curated corpus-snapshot chapters) and **named** topic files. `05-*` numbering gap in the injected `.mdc` set is unrelated.

## Numbered corpus chapters

| File | Topic | Anchored from |
|------|-------|---------------|
| `00-overview.md` | Top-down architecture overview of the whole memory system | `00-memory-system.mdc § See also` |
| `01-memory-system.md` | Memory-system blueprint + full rationale behind `00-memory-system.mdc` | `00-memory-system.mdc § See also` |
| `02-interaction-style.md` | Human-collaboration patterns / interaction core principles (depth behind `01-interaction-style.mdc`) | this index (nominal parent `01-interaction-style.mdc`) |
| `03-self-improvement.md` | Reflection, pattern extraction, generalization, correction protocol | `00-memory-system.mdc`, `01-interaction-style.mdc` |
| `04-evidence-and-validation.md` | Evidence gathering + validation patterns (note: the human-elevation "validation gate" framing does **not** apply on this workspace — see `00 § Evidence-Status Discipline`) | `00-memory-system.mdc`, `01-interaction-style.mdc` |
| `05-code-and-documents.md` | Code-editing + document-authoring patterns | `01-interaction-style.mdc` |
| `06-failure-modes.md` | Failure-mode catalog (F1–F11); read F1/F8/F10 before any compaction | `00-memory-system.mdc`, `03-memory-update-triggers.mdc`, `01-interaction-style.mdc` |
| `07-meta-learnings.md` | Higher-order lessons about the learning process itself | this index (cold-path orphan before it) |
| `08-bootstrapping.md` | From-scratch persona setup (Genesis path) — historical; do **not** re-execute | `00-memory-system.mdc § See also` (bootstrapping) |
| `09-recursive-learning.md` | Applying the learning framework to itself | `universal/MONITORING.md` (sub-agent-reflection entry) |
| `10-adaptive-memory-structure.md` | Content-vs-structure discipline, adaptive memory, hypothesis-test flavor | `00-memory-system.mdc § See also` |
| `11-multi-project-bootstrap.md` | Multi-project bootstrap walkthrough — historical; do **not** re-execute | this index (+ `COLLABORATOR_GUIDE.md`) |

## Named topic files

| File | Topic | Fireable cue / parent |
|------|-------|-----------------------|
| `ai-notes-convention.md` | `ai-notes/` folder git + epistemic-role convention | `WORKING_STYLE.md § Workflow` *Persist task working notes*; `00-memory-system.mdc § See also` |
| `cold-ai-paradigm.md` | Writing persisted content for a future cold self (decode/purpose/signals/lifecycle) | `WORKING_STYLE.md` Core Principle *Apply the cold-AI write-time gate*; `04-multi-project.mdc` |
| `destructive-operations.md` | On-demand destructive-op protocol (full capability copy) | `06-destructive-operations.mdc`, `00`, `04-multi-project.mdc`, `PERMITTED_DESTRUCTIVE_ACTIONS.md` |
| `effective-behavioral-guidelines.md` | Calibration for authoring directives (target + evaluate-cue + act-cue) | `WORKING_STYLE.md § Retention` *Directive authoring calibration* |
| `flexible-plans-for-ai-execution.md` | Layered-commitment plan design for agent-executed plans | `WORKING_STYLE.md` Core Principle *Flexible-plan layered commitment* |
| `host-adaptation-claude-code.md` | Worked Cursor→Claude Code host port (reference; not instantiated) | central `SESSION_LOG.md`; `host-portability.md` §7 |
| `host-portability.md` | Host-agnostic persona-porting method + facet split | `06-destructive-operations.mdc` |
| `plan-refinement-loop.md` | Internally iterating a non-trivial plan (draft→self-review→converge) | `WORKING_STYLE.md § Workflow` *Internally iterate a non-trivial plan* |
| `pull-request-and-commit-message-authoring.md` | Commit-message + PR-description authoring altitudes | `WORKING_STYLE.md § Document Authoring` (commit/PR format row) |
| `working-notes-lean-context.md` | Task working-notes discipline / chat-as-cache / lean context | `WORKING_STYLE.md § Workflow` *Persist task working notes* + *Wrap-up assumes `ai-notes/` may vanish*; `00 § See also` |

> **This index is a topic→file map, not an authoritative link-graph mirror.** The "Anchored from / Fireable cue" column names the *typical* route; the authoritative cue lives in the anchoring file's own text. Do not treat this column as an exhaustive inbound-link ledger (that state drifts — F10). Entries marked "this index" are reachable on the cold path *only* via this hub (cold-path orphans); this index is their discoverability home.
>
> Reached on the cold path from: always-injected `00-memory-system.mdc § See also` + `01-interaction-style.mdc § See also` + the central `SESSION_LOG.md` living summary.

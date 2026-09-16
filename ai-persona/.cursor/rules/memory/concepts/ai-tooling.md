# Concepts — AI tooling & persona self-improvement

`[domain:ai-tooling]` `[meta]` — **seeded 2026-09-15 by explicit human direction, as a deliberate exception to seed-on-evidence (C7)**. Alex is confident concepts here will accrue soon (measurement harnesses, Cursor SDK, probe design, memory-maintenance mechanics), so the domain is created ahead of its first concrete concept to give those learnings a deterministic home. Reusable, tooling-level knowledge about how *this persona* is built, measured, and improved — as opposed to the *process discipline* (which lives in `../../reference/*` + `00-memory-system.mdc`) and the *active workstream* (which lives in `projects/ai-tooling/`). Retrieval: `_INDEX.md` → here → `#concept`; lateral edges in `_RELATIONS.md`.

**Scope boundary (so entries route correctly):**
- **Here (`concepts/ai-tooling.md`)** — reusable *domain knowledge*: measurement-harness mechanics, Cursor Python SDK behavior/gotchas, probe/eval design, permissions-model quirks, memory-structure techniques that generalize beyond one cycle.
- **Not here** — the *how-we-run-a-cycle* discipline (→ `reference/plan-refinement-loop.md`, `reference/10-adaptive-memory-structure.md`, `reference/cold-ai-paradigm.md`, `00-memory-system.mdc § Maintenance`); the *current cycle's* notes/decisions/status (→ `projects/ai-tooling/`); behavioral/coding directives (→ `universal/`).
- **External method/harness source** (read-only, NOT this persona): the `high-assurance-engineering` persona — `/Users/alex/Git/onflow/high-assurance-engineering` (method `…/.cursor/rules/memory/concepts/authoring/memory-maintenance-cycle.md`; harness + prior-run archive `…/ai-notes/2026-09-15_memory-maintenance-cycle/`).

## Concepts

*None evidence-supported yet* — this domain was seeded ahead of evidence (see header). Add the first `### <concept>` here (with a status tag and sources) as soon as concrete, verified knowledge arrives, and add its one-line entry to `_INDEX.md` in the same edit.

## Candidate concepts (`[anticipated]` — pointers, NOT yet established knowledge)

These are expected to graduate into real `### concept` entries above once observed/verified *on this persona's own tooling*. They are recorded here only for discoverability; do not cite them as findings. Primary source for all: the lifecycle launcher prompt `../projects/ai-tooling/lifecycle-kit/launcher-prompt.md` (preserved in-tree) + the HA methodology bundle above.

- **Cold-AI retrieval probe harness (Cursor SDK)** `[anticipated]` — stages a rule-tree copy into a fresh temp `.cursor/rules`, runs cold-AI probes via the Cursor Python SDK (venv `/Users/alex/Development/PythonVEs/flow`, py3.10), captures which files the cold AI opens; the file-reach delta between two versions is the discoverability signal. Persona-agnostic (`../projects/ai-tooling/lifecycle-kit/harness/run_probe.py`) — point it at this persona's tree, not HA's. *To verify on first run against this persona.*
- **Harness permissions gotcha** `[anticipated]` — the probe must run out-of-sandbox (creates a temp dir) and Cursor auto-review misreads planted probe tokens as "secret exposure"; unattended runs need an `~/.cursor/permissions.json` "always allow" entry naming the exact command + pinned interpreter. Re-issuing such an entry is a permissions grant → human-gated. *To confirm the exact entry shape at calibration.*
- **Stale expected-reach keys** `[anticipated]` — each probe's "files a good persona should surface" key is layout- and domain-specific; reused keys from another persona/layout are wrong. Regenerate keys against a fresh live inventory at calibration. *To operationalize for this persona's domains.*
- **Additive-first structural edits win** `[anticipated, cross-experiment candidate]` — prior HA run: every measured discoverability win was additive (new index/hub/back-link), not a destructive move. *To retest here; if it holds, promote toward `universal/PATTERNS.md` via `crossref/BY_PATTERN.md`.*

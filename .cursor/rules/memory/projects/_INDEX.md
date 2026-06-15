# Projects — Roster (always read at session start)

Roster of all projects under this unified persona memory, with **path-globs for active-project detection (M1)**. At session start, match the most-recently-edited / open file path against the globs below to pick the active project; read only that project's folder (+ `universal/*`, `concepts/_INDEX.md`, central `SESSION_LOG.md`). If a path matches none or is ambiguous, **ask before writing per-project memory** (cross-contamination is the top failure mode). Workspace root for the CircuitPython family: `/Users/alex/Development/VsCode/CircuitPython/`.

> **PROVISIONAL (as of 2026-06-14 warm reset).** Watch-for: see `concepts/_INDEX.md` header (one-hop retrieval + deterministic placement). Refute also = a session writes into the wrong project's memory because a glob was ambiguous. Re-evaluate after ~5 real additions.

## Roster

| slug | title | family | path globs | memory home | status | last-touched | notes |
|------|-------|--------|-----------|-------------|--------|--------------|-------|
| `circuitpython-exp14-display` | Exp14 Display Library | `circuitpython` | `2026-04_Exp14_*/**` | `projects/circuitpython-exp14-display/` | active | 2026-06-12 | initial project at warm reset; Phase 3 in progress (branch `alex/display-mvp`) |
| `circuitpython-exp15-microbit` | Exp15 micro:bit alternative (RP2350) | `circuitpython` | `2026-06_Exp15_*/**` | `projects/circuitpython-exp15-microbit/` | active (early) | 2026-06-07 | Milestone-1 blink set up; on-device run pending board |
| `bamboo-lamp` | Bamboo-Lamp ambient lamp electronics | `bamboo-lamp` | `Bamboo-Lamp/**`, `/Users/alex/Projects/Family/Bamboo-Lamp/**` | `projects/bamboo-lamp/` | active | 2026-06-14 | unified into central at warm reset; technical artifacts stay in the Bamboo-Lamp repo, linked |

**Residue-only experiments (no folder until content surfaces, C7)**: exp09 (`2026-02_Exp09_*`), exp11 (`2026-03_Exp11_*`), exp13 (`2026-03_Exp13_*`) — all `[family:circuitpython]`. Add a roster row + `projects/<slug>/` folder when they first accrue memory content.

## New-project-vs-extend heuristic (DN-MP-1 — refine after 3–5 projects of evidence)

Spin up a **new project** (new roster row + `projects/<slug>/CONTEXT.md`) when there is a new board **and** a new primary focus, or a new problem domain. Otherwise extend an existing project. Family is a **tag/column, not a directory** — group by the `family` column; do not create `families/` folders. Coarsening later (merging per-experiment projects into a themed one) is cheaper than splitting, so default to finest grain now (D1 = per-experiment + family).

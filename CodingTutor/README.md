# CodingTutor

Development of an **AI programming-tutor persona** that teaches a 12-year-old student ("Alice") to program embedded
projects in **CircuitPython** on a BBC micro:bit + Elecfreaks Nezha2 + PlanetX stack. The tutor optimizes *how Alice
thinks* (translating fuzzy ideas ↔ algorithms; algorithmic critique; transfer with understanding), not finished programs.

> This repository is the **development workspace for the tutor**. The tutor itself is the artifact being built and is
> **not active here**. The AI that helps build it is a separate assisting persona (kept in `../ai-persona/`).

## Where things are

| Path | What |
|---|---|
| `notes-learnings-insights_for_building_tutor/00_INDEX.md` | Start here — knowledge-base map. |
| `notes-learnings-insights_for_building_tutor/01_project-picture.md` | Complete project orientation (personas, Alice, goals, tutoring contract). |
| `notes-learnings-insights_for_building_tutor/04_pre-design-considerations-and-research-agenda.md` | What to consider & research before designing the tutor. |
| `digests/` | Detailed, self-contained digests of complex sources (each with attribution). |
| `materials/` | Validated external corpus (literature, transcripts). |
| `materials/papers/` | Downloaded academic papers — **git-ignored** (see its README). |
| `REFERENCES.md` | **Consolidated references & attribution** (all external sources + licensing status). |

## Attribution

All external sources are cited in **[`REFERENCES.md`](REFERENCES.md)**, with full citations and per-source licensing /
redistribution status. Proper attribution is a hard requirement for this project: anything that informs the tutor's
design must be traceable to an entry there.

## Licensing & third-party material policy

- Our own writing (notes, digests, references, code) is committed.
- **Third-party copyrighted material (papers, books, media transcripts) is NOT committed** unless a permissive license
  that allows redistribution is confirmed and recorded in `REFERENCES.md`.
- Downloaded papers go in `materials/papers/` (git-ignored by `.gitignore`). To publish a permissively-licensed file,
  record its license in `REFERENCES.md` and `git add -f` it.

### Publication-scope caution
This folder currently lives inside the `circuitpython-experiments` git repo (remote:
`github.com/AlexHentschel/circuitpython-experiments`), **not** its own repo. Two things to confirm before treating
publication as safe:
1. **The podcast transcript + its translation are already tracked** in that repo and are copyrighted third-party content
   (redistribution `no`). See `REFERENCES.md § Licensing & redistribution` for the untrack command.
2. That repo also tracks the private assisting-persona memory (`../ai-persona/`). Confirm whether the repo is
   public/private and whether that exposure is intended before pushing.

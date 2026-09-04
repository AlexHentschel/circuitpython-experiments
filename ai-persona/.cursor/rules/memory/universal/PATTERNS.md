# Cross-Project Patterns

Generalized patterns observed across **2 or more projects** — the cross-project tier of the promotion ladder (`04-multi-project.mdc § M3`). Seeded on evidence: an entry lands here only after a pattern has appeared in a second, non-originating project. Promotion to `[universal]` (a behavioral directive in `WORKING_STYLE.md`/`CODING_PRINCIPLES.md`, or a `[universal]`-tagged concept) requires Alex's sign-off (D2 = auto-promote cross-project, sign-off for universal).

First entry landed **2026-09-04** (public-repo third-party hygiene; coding-tutor + exp16). Was empty from warm reset (2026-06-14) until that 2nd-project occurrence.

Entry schema (mirror the concept-entry template where the pattern is domain knowledge; mirror the directive schema where it is behavioral): one-line statement · the ≥2 projects that evidence it (with dates) · status · promotion candidacy.

## Patterns

### Public-repo third-party material: confirm grant, then gitignore **or** vendor with a sidecar  `[cross-experiment]`

- **Statement:** A repo-root LICENSE does not cover vendored third-party files. Before a public commit: confirm the grant. Default = do not redistribute (gitignore + a register of license/status). If the grant allows a copy into the repo, commit the file **with attribution + a license sidecar next to it**; do not relicense it as the project license. Copyleft/ShareAlike of an *unmodified collection item* does not infect the rest of the tree; **combining** copyleft into `lib/` (import/convert into library code) is a different analysis — write a short case on that candidate; do not coarse-reject on the license name. Adaptations of a copyleft work stay under that copyleft.
- **Evidence:** coding-tutor 2026-07-15 (papers gitignored + `REFERENCES.md`; default not-redistributable). exp16 2026-09-04 (BananaPi `bpi_bit_v2_goldfinger.jpg` unmodified under site CC BY-SA + `Notes/bpi_bit_v2_goldfinger.jpg.license`).
- **Status:** `evidence-supported` at `[cross-experiment]`. Promotion to `[universal]` needs Alex sign-off (D2).
- **Not this pattern:** git history-scrub mechanics (`concepts/git.md`).
- **Provenance:** `crossref/BY_PATTERN.md` candidate row, 2nd occurrence 2026-09-04.

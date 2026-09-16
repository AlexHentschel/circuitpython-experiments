# Session Log — Central (cross-project / persona-level)

This is the **central** session log for the unified persona memory. It holds the cross-project living summary, the source-of-truth map, and `[tooling]` / persona-level sessions that aren't owned by a single project. **Per-project session narratives live in `projects/<slug>/SESSION_LOG.md`.** Read this file + `projects/_INDEX.md` + `universal/*` at session start (M5 read order — authoritative copy in `04-multi-project.mdc § Attention scoping`).

## Current State (living summary)

**Memory layout (unified, since the 2026-06-14 warm reset)**: ONE persona memory home at `.cursor/rules/memory/`, reachable from every project workspace (NOT federated). Structure:
- `universal/` — behavioral / cross-project: `WORKING_STYLE.md`, `CODING_PRINCIPLES.md`, `MONITORING.md`, `CHANGELOG.md`, `PATTERNS.md`.
- `PERMITTED_DESTRUCTIVE_ACTIONS.md` — **fail-closed grant ledger** for destructive ops (empty = nothing permitted). Always-on stub: `06-destructive-operations.mdc`. Protocol: corpus `destructive-operations.md`.
- `concepts/` — domain-knowledge concept graph: `_INDEX.md` (always-read), `_RELATIONS.md` (typed edges), `concepts/<domain>.md` per evidenced domain (today: `circuitpython-runtime`, `fonts`, `power`, `i2c`, `git`, `tooling`, `led-driving`, `nezha`).
- `projects/` — `_INDEX.md` (roster + path-globs) + `<slug>/` digests (`CONTEXT.md` + `SESSION_LOG.md` + `CONCLUSIONS.md`), linking into each project repo's technical artifacts.
- `crossref/` — `BY_TOPIC.md` (topic→projects) + `BY_PATTERN.md` (promotion-ladder working surface). First `universal/PATTERNS.md` entry landed 2026-09-04 (public-repo third-party hygiene).
- `reference/` (sibling of `memory/`, not inside it) — read-on-demand depth layer + dated corpus **snapshots** (recipe, not house SOT). Last ingest **2026-09-07**. House SOT remains always-injected `.mdc` + `memory/universal/WORKING_STYLE.md`. **Topic→file map for the whole layer: `reference/_INDEX.md`** (one hop when you know the topic but not the filename; covers docs not directly linked from any always-loaded file).

**Active-project routing (M1)**: detect the active project from the most-recently-edited / open file path against `projects/_INDEX.md` path-globs. `2026-04_Exp14_*/**` → `circuitpython-exp14-display`; `2026-06_Exp15_*/**` → `circuitpython-exp15-microbit`; `2026-09_Exp16_*/**` → `circuitpython-exp16-planetx`; `Bamboo-Lamp/**` → `bamboo-lamp`. If ambiguous, ask before writing per-project memory. **Write per-project content only into that project's folder; cross-project / boundary content goes to `concepts/` or `universal/` — never bury a cross-scoped insight inside one project** (`WORKING_STYLE.md` Core Principle *Don't guess an association into a deep, specific bucket*; R-7).

**Reachability model (superseded 2026-07-15 — see below)**: ~~central tree lived at `CircuitPython/.cursor/rules/`, symlinked into `Exp14/.cursor/rules` and `Bamboo-Lamp/.cursor/rules`~~. **Current model (2026-07-15)**: the physical rules tree now lives **only** at `CircuitPython/ai-persona/.cursor/rules/`, a dedicated workspace-root folder — no symlinks anywhere. Root cause: Cursor does not deduplicate `alwaysApply: true` rules across workspace roots in a multi-root session (confirmed open bug, no ETA) — the old symlink-fanout meant every co-attached symlinked root re-injected the full rule set, wasting context tokens. **Folder order is not the gating factor** (confirmed 2026-09-11 while planning an unrelated multi-root reorder) — every root is scanned independently regardless of position; detail + sources: `concepts/tooling.md § Cursor .cursor/rules discovery`. Trade-off accepted: persona now loads **only when `ai-persona` is a folder in the active Cursor workspace** (confirmed present in `/Users/alex/Development/Cursor Workspaces/circuitpython.code-workspace`); opening a project folder standalone, bypassing that workspace file, yields zero persona coverage. Full rationale + rejected alternatives: `universal/CHANGELOG.md § 2026-07-15`.

**Bamboo-Lamp (unified 2026-06-14; reachability superseded 2026-07-15)**: its high-level memory still lives centrally at `projects/bamboo-lamp/`; its technical artifacts (`AI-Notes.md`, `diagrams/`, `open-discussions/`) stay in the `~/Projects/Family/Bamboo-Lamp` repo, linked from `projects/bamboo-lamp/CONTEXT.md`. `Bamboo-Lamp/memory/` still holds only a pointer back to central. **Historical note**: reachability was via a `Bamboo-Lamp/.cursor/rules` symlink → central tree (created + verified resolving 2026-06-14; standalone-open test R-6 PASSED 2026-06-14). **That symlink was deleted 2026-07-15** as part of the dedicated-root move above — R-6's standalone-open guarantee no longer holds. Bamboo-Lamp now reaches the persona only via the combined Cursor workspace (same as every other project).

**Retrieval/placement (confirmed 2026-09-08):** June-14 experiment banners dropped. Confirm = one-hop index→domain/project→detail + deterministic placement; evidence exceeded the ~5-addition watch-for with no refute (`power`/`i2c`/`git`; five projects). Dedicated-root attachment remains the 2026-07-15 settlement — not re-opened. See `universal/CHANGELOG.md § 2026-09-08`. Future *new* structure still gets a provisional marker (`00-memory-system.mdc § Content vs structure`).

**Corpus ingest (2026-09-07):** complete (gap-close, not a second warm-reset). Durable record: `universal/CHANGELOG.md § 2026-09-07`. PROVISIONAL-marker promotion was left unbundled then; **executed 2026-09-08** (this living-summary block).

**`ai-notes/` (2026-09-11 destillation):** during-task working store (authority = per-claim confidence). **At wrap-up**, assume the folder may vanish — all non-confidential claims must already live in `memory/` (parent + ≤1 KB sidecar if needed). Post-wrap remainder in notes = confidential/security-sensitive only, unless Alex specifies otherwise. Cue: `WORKING_STYLE.md § Workflow` *Wrap-up assumes `ai-notes/` may vanish* (sibling of *Persist task working notes*). `ai-persona/ai-notes/` never tracked. Exp16 `ai-notes/` **untracked** (`G-2026-09-08-1`, commit `ae8ac09`). History scrub abandoned (noise, not confidential). On-disk Exp16 notes later deleted by Alex. Sibling: `**/.kilo/` gitignored 2026-09-11 (Kilo Code tool state; folder kept on disk).

**Available skills**: `circuit-drawing-generator` at `Bamboo-Lamp/.claude/skills/circuit-drawing-generator/SKILL.md` — Schemdraw code → SVG. Python env `/Users/alex/Development/PythonVEs/MicroControllers/bin/python`; render `python scripts/render_circuit.py input.py output.svg` from the Bamboo-Lamp root. Smoke-tested 2026-05-25 (Schemdraw v0.22). Label-placement notes in `Bamboo-Lamp/Notes.md`.

**Active project status pointers** (detail in each `projects/<slug>/`):
- `circuitpython-exp14-display` — **active**; Phase 3 in progress (P3.1–P3.5 done, P3.6 on-device smoke + P3.7 audit remain). Branch `alex/display-mvp`. See `projects/circuitpython-exp14-display/SESSION_LOG.md`.
- `circuitpython-exp15-microbit` — **active (early)**; Milestone 1 blink set up, on-device run pending board connection. See `projects/circuitpython-exp15-microbit/`.
- `bamboo-lamp` — **active**; standby/sleep-mode design discussion pending; S3-vs-C6 MCU divergence open. See `projects/bamboo-lamp/`.
- `coding-tutor` — **active (knowledge-gathering)**; family `education`. Build an AI tutor persona (distinct from this assisting persona) teaching CircuitPython on micro:bit+Nezha2+PlanetX to student persona "Alice". Setup + Scheiter transcript ingested; **research loop iteration 1 done 2026-07-15** — 17-source corpus downloaded (`CodingTutor/materials/papers/`, git-ignored) + cataloged/triaged/ranked in `CodingTutor/notes-.../05_research-corpus_iteration-1.md` (with a ranked can't-access list for Alex). Next: iteration-2 deep-read/digest T1/T2, then tutor-design guidelines. Design not started. See `projects/coding-tutor/`.
- `circuitpython-exp16-planetx` — **P6 host-green**; Stages 0–3 on-device (K1/K2/K3). Font-spacing Phase 4 gated. **Nezha V2 motor I2C** decoded into `concepts/nezha.md` (2026-09-14; no driver). Boot at `projects/circuitpython-exp16-planetx/CONTEXT.md § Resumption point`.
- exp09 / exp11 / exp13 — residue only; no project folder yet (create a `_INDEX.md` row + folder when content surfaces). Exp09 5×5 LUT/icons are prior art consumed by exp16.

## Source-of-truth map (which file owns which content; pre-empts duplication-and-drift)

| Content type | Source of truth | Update authority |
|---|---|---|
| Collaboration / process / judgment / artifact-convention directives | `universal/WORKING_STYLE.md` | Agent (operational) |
| Destructive-ops grants (fail-closed) | `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` | Agent records **only after** a dedicated §5 confirmation round; protocol in corpus `destructive-operations.md` |
| Coding-craft directives (how code itself is written) | `universal/CODING_PRINCIPLES.md` (schema inherited from `WORKING_STYLE.md`) | Agent (operational) |
| Single-incident observations to act on only if they recur | `universal/MONITORING.md` | Agent (operational) |
| Cross-project generalized patterns (≥2 projects) | `universal/PATTERNS.md` | Agent; `[universal]` promotion needs Alex sign-off (D2) |
| Provenance of structural memory changes | `universal/CHANGELOG.md` | Agent (operational) |
| Domain knowledge (concepts, mechanisms, perf claims) with status | `concepts/<domain>.md` (indexed by `concepts/_INDEX.md`, related via `concepts/_RELATIONS.md`) | Agent; status tracks evidence sufficiency |
| Per-project session narrative / status / open questions | `projects/<slug>/SESSION_LOG.md` + `CONTEXT.md` | Agent (operational) |
| Per-project cross-session findings with evidence status | `projects/<slug>/CONCLUSIONS.md` | Agent records `unverified`/`evidence-supported`/`disputed`/`invalidated` by independent corroboration (no human-elevation tier) |
| Cross-project / tooling / persona-level session narrative + this map | `memory/SESSION_LOG.md` (this file) | Agent (operational) |
| Cross-project topic/pattern lookup | `crossref/BY_TOPIC.md`, `crossref/BY_PATTERN.md` | Agent (operational) |
| Project roster + active-project path-globs | `projects/_INDEX.md` | Agent (operational) |
| Corpus recipe snapshots (dated; not house SOT) | `.cursor/rules/reference/` (ingest 2026-09-07; `ai-notes-convention.md` 2026-09-08) | Agent copies on an explicit ingest grant; house SOT stays `.mdc` + `WORKING_STYLE.md` |
| Task working store (`ai-notes/`) | local gitignored folder at the work unit; **authority is per-claim confidence** | Agent writes freely during the task; mark confidence. **Wrap-up destills all non-confidential into `memory/`** (parent + ≤1 KB sidecar if needed); notes remainder after wrap-up = confidential/sensitive only unless specified. Do not untrack a checked-in copy without a grant. |
| Active plan for a project | the project's plan store (e.g. exp14: `~/.cursor/plans/display_library_refactor_d42ccd55.plan.md`) | Agent maintains; phase-close revisions presented to Alex |

When the same fact must live in two places (rare; only when duplication serves distinct consumers), log it here and add a sync-check to the next maintenance reflection.

**Known consumer-distinct duplications** (sweep together on any structural change):
- **Evidence-status tier definitions** — authoritative in `00-memory-system.mdc § Evidence-Status Discipline`; restated for distinct consumers in `02-domain-structure.mdc`, `concepts/<domain>.md` / `projects/<slug>/CONCLUSIONS.md` headers, and `COLLABORATOR_GUIDE.md`. Use the two-pass vocabulary-migration sweep (`WORKING_STYLE.md § Document Authoring`) when the tier model changes.
- **Scope-tag dimensions** — two *orthogonal* axes (D4): (1) *directive scope* `[universal]/[user]/[project]/[task]` (authoritative in `WORKING_STYLE.md` header; echoed in `01-interaction-style.mdc`); (2) *content scope* `[universal]/[domain:x]/[family:y]/[project:slug]/...` (authoritative in `04-multi-project.mdc § Scope tagging`; rubric in `working-docs/warm-reset-plan/microcontroller-multi-project-memory-guidelines.md § 5`). Don't collapse the two.

## Cross-project & tooling sessions

## 2026-09-14: Session — [user]/[exp16] (`source.txt`-pinned vendor snapshots)

- New `[user]` Workflow row: before treating a local tree with sibling `source.txt` as current, compare pinned SHA to GitHub default-branch HEAD; if remote moved, notify Alex — do not silently refresh. Pins for Exp16 live in `projects/circuitpython-exp16-planetx/CONTEXT.md` *Local vendor snapshots* (notes folder may vanish). First check 2026-09-14: all three local trees matched `master`. Same day: lone-file case added — Bit-S2 schematic PDF size/blob vs GitHub `contents` API.

## 2026-09-13: Session — [tooling] (CircuitPython-profile Black wrap 88 → 160)

- Alex asked to configure the Python auto-formatter for longer rows. Active session uses `circuitpython.code-workspace` → Cursor profile **CircuitPython** (`-7aa41f79`); formatter is `ms-python.black-formatter` with format-on-save, previously no `--line-length` (Black default 88). Set `black-formatter.args` to `--line-length 160` in that profile's `settings.json`. Matches the existing 120-160 comment/doc band (`WORKING_STYLE.md` § Document Authoring, reinforcements 3→4). Takes effect on next format/save; no window reload needed. Other profile (`-4c54adea`) already had Ruff at 180 — left alone.

## 2026-09-11: Session — [exp16]/[tooling] (`circuitpythonsync` workspaceFolders[0] bug + Cursor rule-discovery order check)

- Exp16: Alex's manual `CP Copy Files to Board` failed (`"!! No files specified to copy exist !!"`). Root-caused by reading `padgettholdings.circuitpythonsync` v2.2.2's bundled `dist/extension.js` directly: the extension hardcodes `workspace.workspaceFolders[0]` for its manifest read + file-existence checks (32 occurrences, zero `getWorkspaceFolder`) — not multi-root-aware. Fails for any experiment not at folder-index 0 in the shared multi-root workspace, independent of that experiment's own setup. Fix: open the target experiment standalone, or reorder (trade-off: breaks whichever experiment was previously at index 0). Durable: `concepts/tooling.md`.
- Follow-up question before Alex reordered manually: does moving `ai-persona` off index 0 stop rule injection? Checked via `cursor-guide` subagent — **no**, Cursor's own `.cursor/rules/` discovery scans all roots independently (order-independent), unlike the extension bug above. Real order-independent caveat: mixed flat/subdir `.mdc` layout can drop a root's rules entirely; `ai-persona`'s layout checked clean. Staff-confirmed forum evidence, not formal docs — re-verify empirically post-reorder. Durable: `concepts/tooling.md` (new concept) + `_INDEX.md`; cross-linked from the Reachability-model living-summary bullet above.
- **Outcome confirmed same session**: Alex reordered manually (Exp16 → folder index 0), reports `CP Copy Files to Board` now works via the extension's own UI. Diagnosis-from-source held up end-to-end (not just plausible-in-theory) — this rule tree's rendering unaffected (still injecting normally post-reorder). `concepts/tooling.md` marked verified.

## 2026-09-11: Session — [tooling] (4MB-partition sidecar + wrap-up destillation)

- Compiled TinyUF2 4MB CSV tables into `concepts/tooling-4mb-partitions.md` (stream-on-demand sidecar of `tooling.md`; ≤1 KB). Pointers retargeted off `ai-notes/esp32-4mb-circuitpy-vs-ota/`. New WS row *Wrap-up assumes `ai-notes/` may vanish*. Playbook Objective 3 / G7 supersede source-only-until-cleanup for non-confidential. Calibration: this research + Exp16 are not confidential (Exp16 dump-all deferred). **Cleanup:** Alex moved that notes folder to Trash (`G-2026-09-11-3`); workspace path verified **absent** 2026-09-11. Restore = Trash until emptied.

## 2026-09-11: Session — [tooling] (wrap-up draft-plan: high-level CIRCUITPY vs OTA notes)

- `/experiment-wrapup-to-memory` **closed** 2026-09-11 (high-level CIRCUITPY vs OTA). Durable: `concepts/tooling.md` `df`/FAT overhead; `universal/MONITORING.md` OTA-slot ≠ user FS. Enumerated tables later distilled to `concepts/tooling-4mb-partitions.md` (same day). Wrap-up scratch removed by Alex (verified absent).

## 2026-09-11: Session — [tooling] (wrap-up draft-plan: CircuitPython firmware-update research)

- `/experiment-wrapup-to-memory` **closed** 2026-09-11. Durable: `concepts/tooling.md` + `_INDEX.md` 4MB-scope / ≥8MB skip / vendor-CSV + `#6285`. Enumerated tables later distilled to `concepts/tooling-4mb-partitions.md` (same day). Wrap-up scratch removed by Alex (verified absent).

## 2026-09-11: Session — [tooling] (port `/experiment-wrapup-to-memory` skill)

- Ported the wrap-up-to-memory skill from `onflow/high-assurance-engineering` `.cursor/skills/experiment-wrapup-to-memory/` into this persona: `.cursor/skills/experiment-wrapup-to-memory/{SKILL.md,reference.md}`. Vehicle = Cursor project skill (`disable-model-invocation: true`) → slash `/experiment-wrapup-to-memory`, human-triggered only. Reachable when `ai-persona` is an open workspace root.
- **Self-contained**: playbook (7-step gated pipeline + Objectives + G1–G17) embedded in `reference.md § Playbook` rather than seeding a durable `concepts/authoring/` domain (C7 evidence gate; promote after a 2nd wrap-up, M3). Sequencing is **n=0 on this persona** until first run.
- **Dependency remap** (source → this persona's natives): KU3 Cursor↔Claude review-loop skill → `reference/plan-refinement-loop.md` (native self/subagent review; no external host); `14-plan-authoring.mdc` → `reference/flexible-plans-for-ai-execution.md`; `TWO_LEVELS_OF_LEARNING.md` → directives (`universal/WORKING_STYLE`/`CODING_PRINCIPLES`) vs findings (`CONCLUSIONS`/`concepts`) + `MONITORING`; durable root `memory/` → `.cursor/rules/memory/` unified layout; migrate destinations routed via `04-multi-project.mdc § Placement gate`. All cited paths verified to exist (no dangling refs).

## 2026-09-11: Session — [tooling] (`/experiment-wrapup-to-memory` first content run: human-AI interaction patterns from this session's own transcript)

- Ran `/experiment-wrapup-to-memory` against this chat's own transcript, scope deliberately narrowed via
  `AskQuestion` to "human-AI interaction patterns" (excluding exp16-technical content and the separately-run
  handoff-prompt retrospective) — first "wrap up this persona's own interaction with the user" application
  (deviation from the skill's usual external-host framing). **Closed 2026-09-11.**
- **Durable**: folded a Self-confirmation-loop clause into the existing cold-AI write-time gate row (verify
  institutionalization claims via grep/read, not conversational recall) + added a new Core Principles row (a null
  result is a valid, expected outcome of a review/wrap-up task) — both in `universal/WORKING_STYLE.md`. One
  candidate (a reused "meta-processing incantation" pattern) explicitly declined by Alex, not written anywhere;
  one finding confirmed pure reinforcement, no action needed. Wrap-up scratch removed by Alex (inbound references
  cleaned first; verified absent).

## 2026-09-11: Session — [tooling] (gitignore `.kilo/`)

- Repo-root `**/.kilo/` + Exp16 `.gitignore` `.kilo/`. Folder kept on disk (never tracked). Same category as `ai-notes/`: IDE/tool state, not experiment source.

## 2026-09-09: Session — [exp16] (`ai-notes/` split + untrack + local scrub)

- Grant `G-2026-09-08-1`. Durable lift: `Notes/student-api-portability.md`, README Status, CONTEXT, CONCLUSIONS (emulation `unverified`). Then `git rm -r --cached` (34 files, working tree kept). Gitignore: exp16 `.gitignore` + repo `**/ai-notes/`. Commit `ae8ac09` on `alex/display-mvp_5x5`.
- Grant `G-2026-09-09-1` **spent (unused)**. Local `filter-repo` scrub prepped + verified on origin-mirror (ai-notes unreachable from all heads/objects; rewritten `master` vs GitHub `9f64681` differ by exactly the 34 ai-notes files; `ae8ac09^{tree}==1cb43d2^{tree}`). **Then abandoned:** Alex clarified the ai-notes are **noise, not confidential — may remain in GitHub history**. Revised plan strictly non-destructive: fast-forward `git push origin alex/display-mvp_5x5` (publishes `ae8ac09`); **master untouched, no force-push, no history rewrite**. Uncommitted persona edits never touched by a plain push (no reset/stash needed). Optional: `rm -rf` on-disk `ai-notes/` (gitignored), delete /tmp scrub. **Learning:** confirm the driver (confidentiality vs tidiness) *before* proposing a high-blast-radius history rewrite — reinforced `WORKING_STYLE § Judgment` blast-radius directive. Runbook: `/tmp/circuitpython-experiments-scrub-20260909-INSTRUCTIONS.md`.

## 2026-09-08: Session — [tooling] (PROVISIONAL-marker pass: **executed**)

- Grant: Alex “please proceed with pass” (`plan_v1.0.md`). Notes: `ai-notes/provisional-marker-pass/`.
- Confirmed retrieval/placement; did not re-open dedicated-root. Hygiene: `BY_PATTERN`/`BY_TOPIC`/`_RELATIONS` lying headers + `02-domain-structure.mdc` seeded-domain list. Left: `00.mdc` L37 standing rule, DN-MP-1, hypothesis-test first entry, Exp16 untrack, wrap-up skill, per-concept split.
- Durable record: `universal/CHANGELOG.md § 2026-09-08`. Backlog item struck.

## 2026-09-08: Session — [tooling] (PROVISIONAL-marker pass: plan only)

- Refined against post-ingest persona. **Not executed.** Notes: `ai-notes/provisional-marker-pass/` (`NOTES.md`, `analysis/marker-inventory.md`, `plan_v1.0.md`).
- Verdict: confirm retrieval/placement (watch-for exceeded, no refute). Do not re-open 2026-07-15 dedicated-root. Expand edit set past backlog’s 3 files: `00.mdc` L10 echo, living-summary echo, lying `BY_PATTERN`/`BY_TOPIC`/`_RELATIONS` headers. Leave `00.mdc` L37 standing rule.
- Out of scope unless separately granted: DN-MP-1, hypothesis-test first entry, Exp16 untrack, wrap-up skill, per-concept split.
- Digest for a later session: open the notes folder if executing; this log is only the breadcrumb.

## 2026-09-08: Session — [tooling] (`ai-notes/` authority correction)

- Alex: folder can be SOT; depends on marked confidence of the analysis/source. Typical exploratory unpack, not required. Lighter structure than `memory/`; wrap-up later compresses. Same-persona cold-AI reader (vanilla dumps incorporated when asked).
- Corpus `ai-notes-convention.md` did say “scratch, not source of truth” (§2) — refined (git vs authority split). Companion `working-notes-lean-context.md` + corpus router aligned.
- Persona WS working-notes row updated (r3). Wrap-up skill **not** copied into this persona.

## 2026-09-08: Session — [tooling] (`ai-notes/` git/lifecycle)

- Alex gitignored `ai-persona/ai-notes/` (never tracked) and pointed at corpus `ai-notes-convention.md`.
- Integrated into the **existing** WS working-notes row (no second directive, no 5th `03-triggers` item). Shelf: `reference/ai-notes-convention.md`.
- House default: gitignored at the work unit; durable claims lift to `memory/` / versioned deliverable; do not untrack without grant.
- Exp16 `ai-notes/` still tracked (34 files) — flagged in `MONITORING.md`; not untracked.
- Living summary no longer treats gitignored ingest notes as SOT (CHANGELOG § 2026-09-07 is the durable ingest record).

## 2026-09-07: Session — [tooling] (memory-sync after ingest)

- Notes/META/risks/gap-matrix brought to executed-current-state (planning inventory kept as audit trail).
- Living summary: ingest complete (not “pending”); concepts list + crossref line corrected; `reference/` added to structure + SoT map.
- R1/R2 decided (plan defaults); R3 still open — `MAINTENANCE_BACKLOG.md`, needs a fresh grant.

## 2026-09-07: Session — [tooling] (execute corpus → persona ingest)

- Grant: Alex “Please execute. Sign-off granted.” on `plan_v1.0.md`.
- P0: corpus mtimes unchanged vs planning. P1: `reference/` snapshot 2026-09-07 (21 files). P2: WS/MONITORING cues. P3: reachability hygiene + COLLABORATOR_GUIDE table. P4: CHANGELOG + this entry.
- Defaults: R1 seed hypothesis-test section; R2 copy `host-adaptation-claude-code.md` (not instantiated); R3 PROVISIONAL markers left (still recommend a separate lifecycle pass).
- Preserve-list intact. `03-triggers` still four items.
- Detail: `ai-notes/corpus-persona-integration/` (`analysis/p4-claims-coverage.md`).

## 2026-09-07: Session — [tooling] (plan corpus → persona ingest; superseded same day by execute session above)

- Context: Alex asked to analyze `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/` against this persona (bootstrapped from a precursor of that corpus) and plan integration. Execution gated on explicit approval.
- Notes folder (working-notes discipline): `ai-persona/ai-notes/corpus-persona-integration/` (`NOTES.md`, `INDEX.md`, `plan_v1.0.md`, `analysis/gap-matrix.md`, `risks.md`).
- Finding (planning; confirmed at execute session same day): this is a **gap-close**, not a second warm-reset. Multi-project layout, destructive-ops, cold-AI, and flexible-plans were already operational. Main gaps then: stale/missing `reference/` copies (09–11, working-notes, plan-refinement, host-portability, PR-authoring, EBG); fireable cues for working-notes + plan-loop; hygiene (`00.mdc` still claimed symlink C4). Preserve: no `verified` tier, dedicated-root (no symlink fanout), D8 domain files not per-concept files.

## 2026-09-04: Session — [tooling] (instantiate destructive-ops hard gate from corpus)

- Context: Alex updated `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings` (`destructive-operations.md`) and asked to prominently summarize the core rules in Exp16 notes and persona memory.
- Installed per corpus §10–§11: always-on stub `06-destructive-operations.mdc`; empty ledger `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md`; capability copy in `reference/destructive-operations.md`; WORKING_STYLE HARD GATE banner + Core Principle; COLLABORATOR_GUIDE + file-table/M5 wiring. Exp16 banners in `ai-notes/{INDEX,NOTES}.md`.
- Invalidated 2026-09-03 claim that the corpus had no named destructive-ops entry.
- Cursor: no pre-tool hook — stub is the intercept; reflex coverage lossy (recorded).
- Full structural record: `universal/CHANGELOG.md § 2026-09-04`.

## 2026-07-15: Session 13 — [tooling] (dedicated `ai-persona` workspace root replaces symlink-fanout)

- Context: Alex asked me to locate the persona (answered: `CircuitPython/.cursor/rules/`), then reported he'd moved the physical tree into a new dedicated `CircuitPython/ai-persona/` folder and added it to the Cursor multi-root workspace, and asked me to re-validate a recalled prior finding — that symlinking the same rules tree into multiple workspace roots caused repeated context-window inclusion.
- Research: confirmed via Cursor's forum/bug reports (not previously in this memory — see gap note below) that `alwaysApply: true` rules are loaded once per workspace root with **no cross-root deduplication**; symlink vs. real copy makes no difference to the scanner. Open bug, no ETA.
- Side-finding: the move had orphaned the two pre-existing symlinks (`Exp14/.cursor/rules`, `Bamboo-Lamp/.cursor/rules`) that pointed at the old `CircuitPython/.cursor/rules` location — both dangling, meaning those two roots currently got **zero** persona coverage, not stale-but-working copies.
- Decision (Alex-gated, `AskQuestion`): dedicated-`ai-persona`-root-only, no symlink repair, accepting the "must co-open `ai-persona`" trade-off over repairing symlinks (keeps standalone-open, re-accepts duplication) or migrating to Cursor User Rules (avoids both costs, drops git-versioning). Agent provided `rm` commands rather than executing them, at Alex's explicit request; Alex ran them and confirmed.
- Discovered the *actual* live workspace entry point mid-session: not the old `CircuitPython/CircuitPy_VSCode.code-workspace` (VS Code era, doesn't include `ai-persona`, confirmed inactive) but `/Users/alex/Development/Cursor Workspaces/circuitpython.code-workspace` (Cursor era) — which already lists `ai-persona` first, so no edit was needed to make the new model work.
- Full structural record: `universal/CHANGELOG.md § 2026-07-15`. This entry updated the living summary above (superseded the symlink-fanout + R-6 standalone-open descriptions) in place, per F1/F10 guard — old text struck through/marked historical rather than deleted.
- **Memory-system gap surfaced**: the duplication realization Alex recalled from "the past" had no record anywhere in this memory (checked `CHANGELOG.md`, `MONITORING.md`, `WORKING_STYLE.md`, agent-transcripts — no hits). It had only ever existed in an unpersisted conversation, i.e. exactly the failure mode `03-memory-update-triggers.mdc` item 4 exists to prevent ("stated a takeaway in conversation without writing it to memory"). No corrective action beyond writing it down now — noting it as a concrete instance in case a pattern of this specific gap (persona-infrastructure/tooling realizations discussed but not logged) recurs.
- Open (unverified, flagged in `CHANGELOG.md`): whether a single `alwaysApply` rule in one attached root actually applies workspace-wide across all other attached roots' files, vs. being scoped to `ai-persona`'s own files only. Inferred from Cursor docs + forum wording, not confirmed in-session. If a future session wants certainty: ask the agent to list its always-applied rules while the active file is in a different attached root (e.g. an Exp14 file), per the reproduction method used in the upstream bug reports.

## Warm-reset planning + execution cluster — Sessions 10–12 (2026-06-14 … 2026-06-15) — thinned 2026-09-15

> **Compacted to an index.** These three `[tooling]` sessions built + executed the 2026-06-14 warm reset (flat single-project `memory/` → the current unified multi-project layout). Their durable outcomes are fully institutionalized elsewhere; only the superseded blow-by-blow was removed. Full original prose recoverable from git (before the 2026-09-15 lifecycle commit). Authoritative homes: **`universal/CHANGELOG.md § 2026-06-14 — warm reset`** (structural record + rollback), the seeded `universal/WORKING_STYLE.md` directives, and `working-docs/warm-reset-plan/` (plan + risk-register + notes trail).

- **Session 12 (2026-06-15) — generalized the warm-reset `_META.md` into a reusable *plan-refinement-loop* process doc** for the external persona corpus (`generalized-agent-learnings/plan-refinement-loop.md` + `exemplary-artifacts/warm-reset-plan_META.md`); durable local copy `reference/plan-refinement-loop.md`. Included corpus README/OVERVIEW housekeeping + a transcript-coverage refinement pass (gaps G1–G6 applied: audible-reflection, illustrative-not-mandate framing, falsifiable revision signals, cold-chat handoff, adaptable-prior framing, plan-economy §3.8). Routing = central `[tooling]` (authored from Bamboo-Lamp context; no project-technical content).
- **Session 11 (2026-06-14) — warm-reset EXECUTION.** Ran `warm-reset-plan_v1.0.md` Phases 1–8 under the Phase-0.5 pre-flight gate; all S1–S8 acceptance criteria passed, D1–D8 + R-6 closed. Two operational learnings distilled to durable directives (now in `WORKING_STYLE.md`): *Prefer file-edit tools over shell for file mutations; hand off an unavoidable shell file-op* (evidence: 3 approval-gate stalls) and *verify no-loss by claims-coverage, not line-diff, when restructuring*. Post-exec sweep re-pointed residual active `TECHNICAL.md`→`concepts/<domain>.md` forward-pointers in `MONITORING.md`/`CODING_PRINCIPLES.md`. Full record: `CHANGELOG.md § 2026-06-14 — warm reset`.
- **Session 10 (2026-06-14) — warm-reset PLANNING loop** (`_META`-governed, converged v0.5→v1.0, NOT executed that session). Produced the plan + `risk-register.md` + `notes_v0.1..v0.5`; the full escalation set (D1–D8 + deviations DV1–3) was closed by Alex the same day. Key decisions: unified-not-federated (D6/D7), graduated concept-graph (D8), strip stale `verified`/elevation tiers (D5), claims-coverage no-loss (R-8), honor-existing-scope-tags / don't-mis-default cross-scoped content (R-7). Seeded `[universal]` directives (now in `WORKING_STYLE.md § Core Principles`): *Inherited specs are adaptable priors, not rigid sources of truth*; *Don't guess an association into a deep, specific bucket*; *accumulate-then-split*; *batch heavy restructuring into user-gated lifecycle iterations*. Full trail: `working-docs/warm-reset-plan/` + `CHANGELOG.md § 2026-06-14`.

---

## Open questions & mandate notes — RESOLVED at the 2026-06-14 warm reset

OQ-MP-1/2/3 (project granularity, promotion autonomy, pre-existing-entry tagging) map to plan decisions D1/D2/D3 — **all closed by Alex 2026-06-14** (see `universal/CHANGELOG.md` warm-reset entry + `working-docs/warm-reset-plan/warm-reset-plan_v1.0.md` §3). DN-MP-1 (new-project-vs-extend heuristic) is now seeded in `projects/_INDEX.md` header, to be refined after 3–5 projects. The `warm reset` mandate has now executed. Verbatim pre-reset text preserved below for provenance:

## Open Questions

| ID | Question | Since | Refs |
|----|----------|-------|------|
| OQ-MP-1 | Project granularity for multi-project layout: per-experiment, per-theme, mixed, or cross-domain families? | 2026-04-17 | `mandates/multi-project.md § OQ1` |
| OQ-MP-2 | Promotion autonomy: propose-only, auto-cross-project with manual universal, or fully agentic with CHANGELOG? | 2026-04-17 | `mandates/multi-project.md § OQ2` |
| OQ-MP-3 | How to tag pre-existing untagged entries at warm-reset time? (Default to active project for TECHNICAL/CONCLUSIONS, `[universal]` for WORKING_STYLE, flag ambiguous.) | 2026-04-17 | `mandates/multi-project.md § OQ3` |

### Deferred design notes

Items that are not questions needing a near-term answer, but decisions to revisit with accumulated evidence:

| ID | Note | Revisit when | Refs |
|----|------|--------------|------|
| DN-MP-1 | New-project-vs-extend heuristic — can only be refined empirically, not pre-specified. | After 3–5 distinct projects of experience (post-warm-reset). | `mandates/multi-project.md § OQ4` |

### Notes on open mandates

The human has declared an **open mandate** for a multi-project memory architecture, triggered by the phrase **"warm reset"**. Full spec at `mandates/multi-project.md`. Do not pre-emptively restructure — wait for the explicit trigger, then follow the pre-flight checklist in that file. OQ-MP-1 through OQ-MP-3 above should be resolved with the human *before* warm reset executes; DN-MP-1 is intentionally deferred until post-warm-reset evidence exists.

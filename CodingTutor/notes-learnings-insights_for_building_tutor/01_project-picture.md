# Project picture — CodingTutor (as complete as available, 2026-07-15)

Purpose of this file: the single, self-contained orientation document for anyone (human or cold AI) starting on this
project. Composed from the initialization prompt, the two exemplar tutorial prompts, and the two completed exemplar
tutorials. **This is the setup snapshot; the tutor is not yet designed.**

## 0. One line
Develop an AI **tutor persona** that runs live inside Cursor and teaches a 12-year-old student persona, **Alice**, to
program embedded projects in **CircuitPython** on a BBC micro:bit + Elecfreaks Nezha2 + PlanetX stack — optimizing for
*how she thinks*, not for finished programs.

## 1. Three personas — keep them cleanly separated (load-bearing)
| Persona | Who | Role in this workspace |
|---|---|---|
| **Me** (the assisting persona) | the AI at `/Users/alex/Development/VsCode/CircuitPython/ai-persona` | helps **Alex** *build* the tutor. Active now. Keeps high-level memory of how tutor-development is going. |
| **The Tutor** | the AI tutor persona being developed | the *artifact under development*. **Must NOT be active in this workspace.** Will run in its own context and tutor Alice. |
| **Alice** | the student (a persona; a real 12-yr-old is the ultimate audience) | the learner the Tutor serves. |

Do not let the Tutor's voice/behavior leak into my (assisting-persona) behavior, and do not let my
build-time reasoning leak into the Tutor's design as if it were Alice-facing.

## 2. Alice — the student profile
- 12 years old, strong at math and logical reasoning.
- ~4 years of Python experience via **PixelPad** (encapsulated browser IDE, Python dialect, for kids building 2D
  retro-arcade games). So: real coding fluency, but in a sheltered environment.
- Learns programming as part of education; ~2 h/week self-directed block. Motivation is real but fragile — risk of her
  framing programming as "work" and dismissing it. She self-motivates when something catches her interest.
- Interests (for subtle, rare hooks, level 3/5, each once): Genshin Impact, Star Wars (order 66), Lego, some Pokémon.
- Likes crafting, drawing, reading.
- **Temperament for learning**: enjoys "mini-challenges" with *manageable* uncertainty; lacks fortitude (yet) for
  prolonged unguided debug-by-trial. Dislikes flattery / being sucked up to — she notices.

## 3. Two behaviors the tutor must actively guard against (from Alex, emphasized)
1. **Social-engineering the solution out of the tutor.** Alice is very good at extracting a solution piece-by-piece via
   a chain of innocuous questions. The tutor must not hand over the *algorithmic* solution incrementally.
2. **Shallow pattern-transfer.** She readily lifts a pattern from one problem to another *without* understanding the
   pattern or its limits. Concretely: a toy problem must **not** be constructed so that the only remaining step is to
   rename its concepts onto the real task — she'll do the rename by trial-and-error + follow-up questions and learn
   nothing about *why* the solution works.

## 4. The prime goals the tutor must continuously track (the real objective)
Optimize and *monitor over time* Alice's:
- **(i) Bidirectional translation** between fuzzy human ideas about *how to approach* a problem and a concrete
  **algorithmic representation** of that intuition — both directions.
- **(ii) Algorithmic thinking / critique** — spotting gaps, limitations, over-simplifications, and *unnecessary
  complexity* in an algorithmic representation.
- **(iii) Generalization & transfer** — carrying a solution from one problem to another, *with understanding*.

## 5. The tutoring contract — what the tutor may give vs. must withhold
| Tutor MAY provide directly (with a brief explanation) | Tutor must largely leave to Alice |
|---|---|
| CircuitPython interpreter errors, tracebacks | developing the **algorithmic solution** to the problem |
| software-stack setup issues | the design decisions and their justification |
| IDE / Cursor friction | catching her own gaps/over-complexity |
| Python-language limitations / syntax | the transfer/generalization step |

Key distinction to maintain live: **understanding the problem to be solved** vs. **how to solve it once understood.**
Help generously with the former; protect the latter as Alice's work. Environment/tooling help is a giveaway; algorithmic
help is not.

## 6. Tech stack & the transition
- **Hardware unchanged** from the exemplars: micro:bit V2, Nezha2 breakout, PlanetX motors (M1–M4, encoder "smart")
  and sensors (J1–J4). Full connector/pin/sync-async detail: `../digests/exemplar-tutorials_pedagogy-and-stack_digest.md` §1.
- **Software changes**: exemplars used **MakeCode Blocks**; the tutor teaches **CircuitPython** (same runtime family
  used across this CircuitPython workspace).
- **Dependency, not a blocker for tutor development**: Alex is still completing **CircuitPython support for Nezha2 /
  PlanetX** (motors + sensors). That work is independent of tutor development, but tutor *content* referencing concrete
  APIs can't be finalized until that library exists. Exemplar block names are stack-analogues, not the literal future
  CircuitPython API.

## 7. Exemplar corpus (read-only reference, external)
Two completed tutorials define the target tone and pedagogy; both are transfer-learning-connected (lighthouse reuses
feeder ideas). Full technique extraction in `../digests/exemplar-tutorials_pedagogy-and-stack_digest.md` §2. Headline
techniques: renamed milestones; benefit-first framing; scaffolded **mini-challenges**; **"your turn" decision points
with a branch per answer**; per-section **Check/Self-test**; **Debug hints**; **decision tables** & reflection
worksheets; deliberate bugs; analogies; two-register tone (analytical to Alex, warm-not-flattering to Alice); heavy
figures; no em dashes.

Caveat: the exemplars are **static documents** authored slowly with Alex in the loop. The tutor is **live and
interactive**, which is precisely why the §3 anti-gaming discipline becomes an active per-turn concern rather than a
document property.

## 8. Knowledge-source policy (per Alex)
- `CodingTutor/materials/` — validated corpus: scientific literature, external examples, recommendations. (Currently:
  `They Talk Tech transcript.txt`, untranslated, **pending ingestion** — a next step, not this session.)
- `CodingTutor/notes-learnings-insights_for_building_tutor/` — my notes, learnings, digests-index, todos, open questions.
- `CodingTutor/digests/` — detailed digests of complex/long sources (self-contained, enriched with cross-refs).
- Each detailed digest yields a **very short domain-coverage summary** that lives in persona memory
  (`ai-persona` → `memory/projects/coding-tutor/CONTEXT.md`), so a cold AI can decide when to open the full digest.
- Structure is **not pre-designed**; restructure when retrievability/clarity materially improves.
- Alex is *not* an education/tutoring specialist (he is a distributed-fault-tolerant-computing + ML engineer), so
  design must be grounded in **recent research on learning/tutoring of early-high-school children**, especially
  teaching software engineering to kids with prior coding experience (if such literature exists).

## 9. Scope boundary for the setup session
Done: read all inputs; composed this picture; scaffolded the knowledge base; registered the project in persona memory.
**Not done (deliberately):** designing the tutor; web research; ingesting the transcript. See `03_open-questions-todos.md`.

## Cross-references
- `00_INDEX.md` — knowledge-base retrieval map.
- `../digests/exemplar-tutorials_pedagogy-and-stack_digest.md` — full pedagogy + stack extraction.
- `03_open-questions-todos.md` — next steps + open questions.
- Persona memory: `ai-persona` `memory/projects/coding-tutor/{CONTEXT,SESSION_LOG,CONCLUSIONS}.md`.

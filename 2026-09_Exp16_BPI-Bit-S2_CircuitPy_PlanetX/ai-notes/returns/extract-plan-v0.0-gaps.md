# Extract — plan_v0.0 gaps vs locks/digests

**Date:** 2026-09-04  
**Brief:** `ai-notes/briefs/extract-plan-v0.0-gaps.md`  
**Plan:** `ai-notes/plan/plan_v0.0.md`  
**Thoroughness:** medium (inventory only; no verdict)

---

## Findings

| id | location | source | kind | one-line fact |
|----|----------|--------|------|----------------|
| G1 | Fix layer | `NOTES.md` § Locked — "Library + project template = Exp14" | lock-miss | Plan names the Exp16 `lib/display/` copy but does not state the broader Exp14 project-template lock. |
| G2 | Fix layer | `NOTES.md` § Locked (2026-09-04) — `_MAX_HEIGHT_PER_COLUMN_BYTE = 8`; do not design for 4×4/6×6/7×7 | lock-miss | Column-byte cap and non-target geometry sizes are locked in NOTES and `exp14-display-lib.md` but absent from the plan Fix layer. |
| G3 | Fix layer | `NOTES.md` § Locked — "Exp09 supplies 5×5 LUT, orientation, pictogram bitmaps only" | lock-miss | Exp09 as the sole supplier of LUT/orientation/pictograms (not font) is not stated in Fix; only implied in phases P1–P2. |
| G4 | Fix layer | `NOTES.md` § Locked — arrows "must remain independently replaceable"; `core.py` / `bitmap_codec.py` geometry-agnostic except thin hooks | lock-miss | Swap-unit list names arrows but not independent replaceability or the geometry-agnostic core/codec constraint. |
| G5 | Fix layer | `NOTES.md` § Locked (2026-09-04) — "sub-agents authorized" for plan-refinement loop | lock-miss | Plan cites the 8-iteration cap and `loop-setup.md` but does not record sub-agent authorization from NOTES. |
| G6 | Fix layer | `NOTES.md` § Constraints — "Max 5 agent scripts, spec + uninstall in this folder" | lock-miss | Agent-script budget constraint is not reflected anywhere in plan_v0.0. |
| G7 | Fix layer | `NOTES.md` § Constraints — "Stock CP 10.3.0 `bpi_bit_s2`" | lock-miss | Target firmware is only in Known unknowns K1 / later phase P8, not in the Fix constraint layer. |
| G8 | Fix layer | `NOTES.md` § Constraints — "Human testing is rare and strategic" | lock-miss | Plan defers on-device work but does not carry the rare/strategic human-testing constraint from NOTES. |
| G9 | Fix layer | `NOTES.md` § Pictograms — port Exp09 `Image.*` to Exp14 `icons.py` column-major 5×5 | lock-miss | Pictogram port rule lives in phase P2 only, not in Fix. |
| G10 | Fix layer | `design/student-api-portability.md` § Verdict — motor/light deferred to semantic API when those phases exist | lock-miss | Motor and light deferral (Watch II–III) is not mentioned in the plan Fix or Known unknowns. |
| G11 | Success criteria § initial | `digests/lighttower-student-ops.md` § Watch I — `pause 1000` / `await display.pause(1000)` | digest-miss | `pause` is a Watch I student op in the digest but not named in success criteria. |
| G12 | Success criteria § initial | `digests/lighttower-student-ops.md` § Watch I — `show string "A"`/`"B"`/`"C"`/`"D"` | digest-miss | Letter flash for A–D is a named Watch I op; success criteria only generically require `show_string` not to crash. |
| G13 | Success criteria § initial | `digests/lighttower-student-ops.md` + `button-research.md` — `on_a_pressed` … `on_d_pressed` | digest-miss | Success criteria test only `on_c_pressed`; A/B/D press registration is not success-criteria-visible. |
| G14 | Success criteria § initial | `digests/button-research.md` § Public API — `on_*_released` handlers | digest-miss | Release handlers are in the digest API shape but absent from plan success criteria and P5 exit. |
| G15 | Success criteria § initial | `digests/lighttower-student-ops.md` § Watch I trace — `letter → (icon) → LighthouseMode` | digest-miss | Watch I self-test trace shape is in the digest but not referenced in plan success criteria or phases. |
| G16 | Success criteria § initial | `design/student-api-portability.md` G4 + `lighttower-student-ops.md` § Watch II note — N/S/E/W arrows | digest-miss | Success criteria require "one arrow" host test, not explicit N/S/E/W (LightTower nudge directions). |
| G17 | Phases / authority | `digests/INDEX.md` — spec pointer `../../Notes/overall_goal.md` | digest-miss | Digest index lists `overall_goal.md` as spec; plan_v0.0 does not reference it. |
| G18 | P-plan / loop start | `digests/INDEX.md` — "if a digest is missing, collection is incomplete and the plan-refinement loop must not start" | digest-miss | Digest-completion gate for starting the refinement loop is not stated in the plan. |
| G19 | P5 / student API | `digests/exp09-lut-icons.md` § PlanetX C/D — "Do **not** use Exp09 `Button` class as the student API" | digest-miss | Plan forbids student `update()` but does not explicitly reject Exp09 sync `Button` as the student surface. |
| G20 | P-phase gates | `plan/reflection-cadence.md` § Required gates — P-phase must re-open load-bearing **A1–A4** | digest-miss | Plan phases cite portability G1–G7 at gates but not assumptions A1–A4 from reflection-cadence. |
| G21 | Portability validation | `design/student-api-portability.md` G7 — "Student examples are the portability test" | digest-miss | G7 oracle (one LightTower student sketch) is not in success criteria or phases. |
| G22 | Library behaviour context | `digests/lighttower-student-ops.md` § Modes — library must not encode `LighthouseMode` table | digest-miss | Constraint that mode state stays in student handlers is in digest but not in plan. |
| G23 | Work on Exp16 copy | `digests/exp14-display-lib.md` § Copied tree — full absolute path to Exp16 `lib/display/` | digest-miss | Plan Fix uses ellipsis (`…/2026-09_Exp16_…/lib/display/`); digest gives the full Exp16 tree path for cold-AI one-hop. |
| G24 | § Font recommendation | `digests/exp09-lut-icons.md` § Font — overnight need includes digits **0–2** for Watch I traces | contradiction | Plan Font section targets digits 0–9; digest narrows Watch I minimum to 0–2 (plan is broader, not narrower — soft mismatch on minimum bar). |
| G25 | § Phases P1 | `digests/exp09-lut-icons.md` § LUT — host-test with visual fixture because shared-derivation hazard | over-committed-shape | P1 mandates a visual fixture without citing the digest's shared-derivation rationale (fixture type left open). |
| G26 | § Corpus digest + Fix | `plan/reflection-cadence.md` § When execution plan drafted — import cadence, do not duplicate | *(no gap)* | Plan links `reflection-cadence.md` and summarizes cadence in one Fix bullet plus checkpoint names; does not paste the full cadence file. |
| G27 | § Font / Open | `plan/plan_v0.0.md` — `PCF`, `_glyph_columns`, `pendolino3` | undecoded-term | Plan uses PCF, `_glyph_columns`, and `pendolino3` without cold-AI decode (what they are / encoding role). |
| G28 | § Phases P1 | `plan/plan_v0.0.md` — "visual fixture (not the same formula)" | undecoded-term | "Visual fixture" is required for LUT host tests but not defined for a cold reader. |
| G29 | Body (throughout) | `plan/plan_v0.0.md` — `LUT`, `codec`, `dispatcher` | undecoded-term | LUT, codec, and dispatcher appear without expansion; digests decode LUT and two-tier/codec context separately. |
| G30 | Header | `plan/plan_v0.0.md` — `loop-setup.md` | undecoded-term | Loop cap references `loop-setup.md` without stating what that file governs (file not in brief source list). |
| G31 | Fix layer | `NOTES.md` § Locked — swap units: geometry/LUT, icons, arrows, font | *(satisfied)* | Fix layer lists geometry+LUT, icons, arrows, font — check passes. |
| G32 | § Font | `NOTES.md` + `exp09-lut-icons.md` — recommendation present; source not locked; GPLv3 pitchfork flagged | *(satisfied)* | Dedicated Font section recommends DAL/pendolino3, leaves source open, escalates GPLv3 pitchfork. |
| G33 | § Pins | `NOTES.md` + `exp09-lut-icons.md` — IO13/IO14 hypothesis | *(satisfied)* | Pins table labels C/D as hypothesis with confirm-at-wiring note. |
| G34 | Fix layer | `NOTES.md` § Approach locks — overnight = host tests, not on-device | *(satisfied)* | Fix outcome and P6/P8 split state host-tests success bar; on-device is later. |
| G35 | § Phases + purpose | `NOTES.md` — no scaffold `.vscode/` or implement in planning chat | *(satisfied)* | Plan explicitly forbids 5×5 adaptation, button lib, and `.vscode/` scaffolding in the planning chat. |

---

## Counts by kind

| kind | count |
|------|------:|
| lock-miss | 10 |
| digest-miss | 13 |
| contradiction | 1 |
| over-committed-shape | 1 |
| undecoded-term | 4 |
| *(satisfied checks — not gaps)* | 5 |

**Total gap findings (excluding satisfied rows):** 29

---

## Sources read

1. `ai-notes/NOTES.md`
2. `ai-notes/design/student-api-portability.md`
3. `ai-notes/plan/plan_v0.0.md`
4. `ai-notes/digests/INDEX.md`
5. `ai-notes/digests/exp14-display-lib.md`
6. `ai-notes/digests/exp09-lut-icons.md`
7. `ai-notes/digests/lighttower-student-ops.md`
8. `ai-notes/digests/button-research.md`
9. `ai-notes/plan/reflection-cadence.md`

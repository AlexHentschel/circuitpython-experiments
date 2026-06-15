# Monitoring

Last updated: 2026-04-25 (session 7 continuation: added two entries — *On-device verification of `str.translate` performance* (Phase 3 smoke-run trigger) and *Body-size threshold for the consolidate-shared-helper rule* (second-incident promotion candidate).)

Previous: 2026-04-21 (session 6 continuation: added *Font swap for pixel-accurate display* follow-up. Also added *Pipeline-investigation scope-lift candidate* tracking the new `(experimental)` CODING_PRINCIPLES directive for cross-domain application.)

## Purpose

Short, cross-session register of *observations I want to act differently on if they recur*. Solves a specific gap in the stateless-retrieval memory architecture: a directive saying "watch for the next occurrence of X and then do Y" has no triggering mechanism — recurrence detection is not a primitive. Writing the observation down here creates an explicit, re-retrievable trigger.

**What goes here:**

- Single-incident observations where escalating to a full directive is premature (insufficient evidence, scope uncertain), but the pattern is worth noticing on recurrence.
- Scope-lift candidates: directives currently at `[project]` or `[task]` scope that would plausibly generalize to `[universal]` after one more cross-domain incident.
- Promotion triggers for unverified-but-plausible claims: "if claim X comes up again, source-verify and promote to the relevant `concepts/<domain>.md`".
- Meta-patterns noticed once (e.g. a failure mode in my own reasoning) that deserve attention rather than immediate codification.

**What does not go here:**

- Session-local open questions — those live in `SESSION_LOG.md § Open Questions`.
- On-device verification items for CircuitPython claims — those live in the relevant `concepts/<domain>.md` Verification Queue (e.g. `concepts/circuitpython-runtime.md`).
- Confirmed directives (any status, any reinforcement count) — those live in `WORKING_STYLE.md` or `CODING_PRINCIPLES.md` with their own retention rules.
- Scratchpad / brainstorming — use an ephemeral note, not this file.

## Entry schema

Bullet-per-entry. Keep each entry to 2–4 lines. Fields:

- **Observation** (one phrase).
- **Trigger** — the kind of recurrence that would warrant action.
- **Action on trigger** — concrete: where the next incident should route (file + section + shape of edit).
- **First observed** — date + session number.
- **Scope** — `[universal]` / `[user]` / `[project]` / `[task]` per the usual memory scope tags.

## Retention

- **Lifecycle**: recurrence → action on trigger → remove entry from this file (the action handles it). If trigger never fires and the observation becomes stale (no recurrence in 3+ sessions of active work in the relevant domain), re-evaluate: either delete with note, or promote to a regular directive on the thinking "pattern is real even without a second incident."
- **No silent drops**: per `WORKING_STYLE.md § Retention and Evaluation`, removals or promotions go through a stated reason and a `CHANGELOG.md` entry if structural.
- **Cross-reference on promotion**: when an entry graduates to a full directive / `concepts/<domain>.md` entry / `projects/<slug>/CONCLUSIONS.md` finding, cite this file as the original observation site in the promoted entry's Notes column so the provenance chain is preserved.

## Entries

- **Scope-lift candidate: *Cross-runtime citations require a grounding note***
  - **Observation**: directive currently at `[project]` scope, phrased around MicroPython↔CircuitPython specifically.
  - **Trigger**: any non-MicroPython cross-runtime citation incident (e.g. citing CPython docs from CircuitPython or PyPy code for a feature whose behavior may differ).
  - **Action on trigger**: lift directive scope to `[universal]`, rename to remove MicroPython-specific framing, update the Notes column of the entry at `CODING_PRINCIPLES.md § Core Principles` with both incidents as evidence. If a second non-MicroPython incident accumulates, the abstraction-lifecycle rule from `WORKING_STYLE.md § Retention` is satisfied.
  - **First observed**: 2026-04-21 (session 6).
  - **Scope**: `[project]` → candidate for `[universal]`.

- **Promotion trigger: MicroPython perf-guidance source-verification pattern**
  - **Observation**: one `docs.micropython.org/reference/speed_python.html` claim (LOAD_FAST vs LOAD_GLOBAL) has been source-verified against CircuitPython's `py/vm.c` + `py/runtime.c` and lives in `concepts/circuitpython-runtime.md` (§ "Name loading: LOAD_FAST vs LOAD_GLOBAL"). Other claims from the same doc — e.g. `const()` folding, buffer-protocol access, viper — have not been verified for this port.
  - **Trigger**: a second `speed_python.html` claim becomes relevant to a hot path in this workspace.
  - **Action on trigger**: source-verify against the CPy source tree (same method: fetch `py/vm.c` + the relevant `py/*.c`, grep for the opcode or function, confirm mechanism), then add a `### concept` to `concepts/circuitpython-runtime.md` (+ a `concepts/_INDEX.md` line) as a sibling to *Name loading: LOAD_FAST vs LOAD_GLOBAL*. Do not treat MicroPython docs as authoritative on this port without the verification step.
  - **First observed**: 2026-04-21 (session 6).
  - **Scope**: `[project]`.

- **Follow-up: font swap for pixel-accurate display on exp14**
  - **Observation**: current `lib/display/font_free_mono_8/font.pcf` is a FreeType auto-rasterization of `FreeMono.ttf` at `PIXEL_SIZE: 8` and renders illegibly on the 8x8 matrix (stroke structure lost at that pixel budget). Rendering code is exonerated — see `working-docs/font-distortion-findings.md`. The issue is well-contained but deferred from the Phase-2 refactor.
  - **Trigger**: Phase 2 or Phase 3 work surfaces text-rendering as needing demonstration-quality output (e.g. on-device verification at P3.6, retrospective demos, documentation screenshots), OR the user requests text to be legible for any demo.
  - **Action on trigger**: swap to a hand-designed bitmap font sized for the matrix (candidates named in `concepts/fonts.md § Outline fonts… unsuitable`: tom-thumb 3x5, scientifica 5x11, bitocra 6x10, creep, spleen, tewi). Drop new PCF into `lib/display/font_<name>/font.pcf`, update `_FONT_PATH` in `core.py`. Verify with `working-docs/font-distortion-probe.py` as A/B reference. No rendering-code change expected.
  - **First observed**: 2026-04-21 (session 6).
  - **Scope**: `[exp14]`.

- **Status-promotion trigger: *When localizing a bug in a pipeline, instrument stages before speculating***
  - **Observation**: directive tagged `[universal]` but currently `(experimental)` — single-incident evidence from the font-distortion investigation (rendering pipeline on CircuitPython). The posture applies to any multi-stage transform (parser, asset pipeline, sensor chain, compile pipeline, request-response flow); the evidence to date is domain-specific.
  - **Trigger**: a second debugging incident where analytical narrowing circles for 2+ exchanges before probes settle it, in a pipeline outside the display/rendering domain.
  - **Action on trigger**: update the Notes column of the entry at `CODING_PRINCIPLES.md § Core Principles` with the second incident as evidence, flip `(experimental)` → `established` per `WORKING_STYLE.md § Retention` ("at least two clean applications outside the originating incident"). If the second incident is in a qualitatively different pipeline class (e.g. async event chain vs batch transform), also evaluate whether the directive's phrasing needs generalization.
  - **First observed**: 2026-04-21 (session 6).
  - **Scope**: `[universal]`.

- **On-device verification: `str.translate(dict)` on CircuitPython for pattern parsing**
  - **Observation**: `_iter_pattern_rows_fast` in `lib/display/core.py` was added to give `Display.render_pattern` a single-allocation hot-path whitespace stripper, replacing `"".join(raw.split())` (which allocates an intermediate list + final string) with `raw.translate(_HOTPATH_WS)` (single string allocation). Verified on CPython for parse correctness; not yet verified on the RP2040 device. Two open questions: (1) does CircuitPython's str.translate accept a dict argument with `None` values for deletion, and (2) does it actually outperform split+join on this workload, or is it merely allocation-fewer-but-cycle-equivalent.
  - **Trigger**: next on-device run that exercises `Display.render_pattern` (Phase 3 smoke run is the natural occasion; any earlier debug or demo session would also do).
  - **Action on trigger**: run a short A/B microbench on-device (`time.monotonic_ns()` around N iterations of each variant on a fixed pattern), record the result. If `str.translate` is unavailable or substantially slower, swap to chained `raw.replace(" ", "").replace("\t", "").replace("\r", "")` (three string allocations, no list, no dict-lookup overhead) — that's the documented fallback. If translate works and benefits, promote a finding to `concepts/circuitpython-runtime.md` documenting the allocation-count comparison with on-device numbers and `[CPy-src]` tag pointing at `py/objstr.c`.
  - **First observed**: 2026-04-25 (session 7 continuation, this entry).
  - **Scope**: `[exp14]` for the immediate code; `[project]` for any `concepts/circuitpython-runtime.md` finding produced.

- **Promotion candidate: body-size threshold for *consolidate duplicated code in a shared function***
  - **Observation**: the consolidation rule (P2.1 audit established it for the previously-shared `_iter_pattern_rows`) has a body-size threshold below which it stops carrying weight, plus an interaction with call-site-profile distinctness. For the `_iter_pattern_rows` case (4 lines of body, two distinct call-site profiles — cold parse-once vs hot parse-per-frame), the right answer turned out to be two specialised functions, not one shared function with a configuration knob. Single incident so far; pattern not yet promoted.
  - **Trigger**: a second incident where the question "extract this duplicate into a shared helper, or keep two specialised copies" comes up on a code shape *other than* a pattern-row generator (e.g. a small render helper, a small validator, a small encoding step). The decision point is: does the body cross the drift-risk threshold, and how distinct are the call-site optimization profiles?
  - **Action on trigger**: log the second incident's resolution against the shape of the code, then if the decision criteria match this one, write a `(experimental)` directive in `CODING_PRINCIPLES.md` covering the threshold and the call-site-distinctness factor. Until then, single-incident — keep here.
  - **First observed**: 2026-04-25 (session 7 continuation, this entry).
  - **Scope**: `[universal]` candidate (the calculation isn't language-specific or experiment-specific — just code-shape-specific).

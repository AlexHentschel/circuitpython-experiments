# Phase 1 audit ledger

Status: iteration 1 open (2026-04-20).

## Reflection (pre-audit)

### What actually changed

Phase 1 is the API-hygiene phase — 8 work items, 7 git commits.

Scope:
- `lib/display/core.py`: renamed `interval` → `interval_ms` across 7 public methods and their docstrings; replaced `color=None` + remap with `color=WHITE` direct defaults at 13 sites; renamed `_cancelled` → `_is_cancelled` (7 occurrences including module docstring); rewrote the module, `_acquire`, and `_is_cancelled` docstrings to state the cancellation policy explicitly and removed "preempt" wording; removed three public-docstring leaks of internals (`Image.scroll_image` mentioned `_seq`; `Display` class mentioned `_seq`/`_acquire`; `get_pixel` said "Does not acquire"); added `loop=False` parameter to `show_string`/`show_number`.
- `lib/display/README.md`, `CONTEXT_HANDOFF.md`, top-level `README.md`: kwarg-rename propagation (`interval` → `interval_ms`; fixed a pre-existing `color_palette` drift → `color`); `_cancelled` → `_is_cancelled`.
- `code_demo_phase2.py`: call-site propagation.
- `.cursor/rules/memory/TECHNICAL.md`: new `Memory Management on CircuitPython` section via full technical-memory review loop.
- `.cursor/rules/memory/WORKING_STYLE.md`: added 3 new directives (immutable defaults, decompose into small helpers, `working-docs/` folder); documented that 4 of the 7 requested directives were already captured at higher abstraction.

### What was learned

- **Docs-vs-source drift caught in the tech-memory loop** (`gc.threshold()` documented but compiled out of CPy). The Researcher-vs-independent-Verifier separation did its job — this would have landed as a wrong claim otherwise. Evidence for the principle that CPy docs pages can be stale relative to actual shipped builds.
- **No `delay` parameter existed** (P1.1 as written assumed one); dropped silently rather than invented.
- **Pre-existing `color_palette=` drift** in demos + docs discovered during P1.1 propagation; fixed opportunistically in the same commit since the diff shape overlapped completely with the rename.
- **4-of-7 directives already captured** in P1.8 — the abstraction-lifecycle rules in `WORKING_STYLE.md` did the right thing; duplicating would have violated the file's own discipline.
- `show_string` `loop=True` semantics for short strings (text fits on screen) was ambiguous in the plan — resolved as "hold indefinitely, poll cancellation" with a 50 ms fallback poll when `interval_ms == 0`.

### What is worth auditing given that

Phase 1 is mostly mechanical renames, docstring rewrites, and memory writes. Audit focus should be:

1. **Rename completeness** — any missed `interval` / `_cancelled` site across the workspace, especially in `code.py`, `code_determine_LED-wiring.py`, top-level `README.md`, or any old comment references.
2. **Docstring-consistency** — did the cancellation-policy wording stay internally consistent? Did any other public docstring still leak `_seq` / `_acquire` / `token` that I missed?
3. **`loop=True` correctness** — the new `while True:` scroll loop and the "hold indefinitely" branch for short strings. Specifically: is cancellation responsive within one `interval_ms` window? Does `loop=True` with `interval_ms=0` poll every 50 ms as intended? Does `loop=False` with the new outer `while True:` structure still return after one pass (regression risk from the refactor)?
4. **Default-value cleanup side effects** — did replacing `color=None` + remap with `color=WHITE` break any caller that was explicitly passing `None` (e.g., as a sentinel in a wrapper)? Quick grep for `color=None` at call sites.
5. **Memory entry quality** — any inferred-but-not-flagged claims that survived the Editor pass? Any verification-queue items that should actually be promoted to in-session closure (e.g., if the on-device number is easy to get right now).

### What can be skipped or downweighted

- **No performance audit** — Phase 1 changed zero hot loops. Any perf claim from the auditor should default to Reject.
- **No heap-behavior audit** — no allocation-shape changes in Phase 1.
- **No test-coverage audit of the memory digest** — the tech-memory loop already audited that entry.
- **No audit of the working-style additions** — P1.8 is a user-stated-directives record; no evidence to audit beyond "did I paste them correctly", which a quick diff review covers.
- **No API-design audit of `loop=`** — the parameter shape is set by the plan; the audit should only check the implementation, not the design.

## Iteration 1 — Auditor findings

Seven findings, all low or medium severity, no high.

| ID | Severity | Dim | Location | Observed |
|----|----------|-----|----------|----------|
| F1 | low | 1 | `lib/display/README.md:58` | "pre-empt" residue after the cancellation-vocabulary sweep |
| F2 | medium | 1 | `README.md:82-83`, `lib/display/README.md:42-43` | API-table signatures missing the new `loop=False` parameter |
| F3 | medium | 2 | `lib/display/core.py:391` | `set_rotation` docstring silent on its no-cancel exception (unlike its peers `get_pixel`, `set_brightness`) |
| F4 | low-medium | 2 | `lib/display/core.py:17`, `:276` | "read-only methods" label imprecise for `set_brightness` / `set_rotation` which do mutate pixel output |
| F5 | low | 2 | `lib/display/core.py:419-429` | `show_string` docstring under-describes short-text `loop=True` poll cadence (incl. 50 ms fallback when `interval_ms == 0`) |
| F6 | low | 2 | `lib/display/core.py:470-472` | `show_number` docstring silent on `loop=` parameter |
| F7 | low (opportunity) | 5 | `TECHNICAL.md` verification-queue row "YD-RP2040 clean-boot free heap" | Trivially closeable in-session with `gc.collect(); print(gc.mem_free())` in `code.py` |

Dimensions 3 (`loop=` correctness) and 4 (default-value side effects) — explicit "no findings": walked through the `show_string` cancellation + off-by-one + buffer-bounds analysis; grepped for residual `color=None` call sites (zero).

## Iteration 1 — ROI assessor dispositions

| ID | Disposition | Rationale |
|----|-------------|-----------|
| F1 | Accept | Small effort, maintains the vocabulary-migration-sweep directive from `WORKING_STYLE.md`. |
| F2 | Accept | Most material finding of the pass. Small effort, medium benefit — API feature would stay invisible otherwise. |
| F3 | Accept | Consistency with `get_pixel` and `set_brightness`. Small effort. |
| F4 | Accept | "Read-only" is a semantic inaccuracy for `set_brightness` / `set_rotation`; rephrasing is cheap and prevents future misreading. Went with terse "non-cancelling" phrasing rather than the auditor's longer parenthetical. |
| F5 | Accept | Non-obvious behavior worth documenting so callers can reason about cancellation latency. |
| F6 | Accept | Trivial; docstring was out of sync with signature. |
| F7 | Defer | On-device dependency; plan's "one smoke run per phase" cadence rule batches device work to phase close (P3.6). Opportunity logged; not a code gap. |

6 Accepts, 1 Defer, 0 Rejects.

## Iteration 1 — Implementer actions

- F1: `lib/display/README.md` § "Cooperative multitasking & `_seq`" — "pre-empt" → "cancel".
- F2: top-level `README.md` Tier 2 table + `lib/display/README.md` Tier 2 list — `show_string` / `show_number` signatures updated with `loop=False`, one-line description of `loop=True` behavior added.
- F3: `lib/display/core.py` `set_rotation` docstring — appended "Does not cancel animations."
- F4: module docstring and `Display` class docstring — "read-only methods" → "non-cancelling methods", with a short parenthetical clarifying that `set_brightness`/`set_rotation` do update pixel output.
- F5: `show_string` docstring — added one sentence describing short-text `loop=True` poll cadence and the 50 ms fallback.
- F6: `show_number` docstring — added "Accepts `loop=True` (see `show_string`)." line.
- F7: not applied (deferred).

Tier 1: 78 passed. No regressions.

## Stopping signal / close

**Iteration 2 reflection**: all accepted findings applied; deferred item is device-dependent and correctly batched to phase close; further iteration would produce only cosmetic diffs. Exit.

**Plan-revision check**: re-read P2 + P3 + retrospective against Phase 1 learnings.

- P2 items unchanged in intent; P2.1 / P2.3 / P2.4 / P2.5 remain the right shape and connect naturally to the `[inferred]` gaps flagged in the P1.7 Memory Management digest (ring-buffer perf, `build_lut` in-place).
- P3.5 consistency sweep will now naturally include `working-docs/` in its scope — sub-item, not a new item.
- P3.6 on-device smoke is the right place to close F7 (free-heap baseline) and the other two `TECHNICAL.md` verification-queue items — already captured there.
- Retrospective: L1 already has one datum (zero `color=None` sites had mutable-default intent in Phase 1); L8 (`_ms` convention) landed cleanly across in-repo consumers.

**Conclusion**: no material plan revisions warranted at this checkpoint. Stated explicitly per the plan-revision discipline (silence is not enough).


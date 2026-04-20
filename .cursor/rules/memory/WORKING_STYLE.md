# Working Style Directions

Last updated: 2026-04-17 (initial cold-start; no entries yet)

## Human Profile

- Expertise areas: _to be calibrated_
- Areas needing grounding: _to be calibrated_
- Preferred notation: _to be observed_
- Pet peeves: _to be observed_

## Core Principles

| Principle | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|

## Communication Style

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Evaluate user suggestions critically with evidence; push back on weak premises rather than agreeing by default | 1 | 2026-04-17 | Explicitly reinforced after I countered a perf-framed suggestion (the "join overhead" concern in `bitmap_codec.pattern_to_colmajor`). User wants this as the default posture, not a one-off. |

## Document Authoring

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Introduce all abbreviations/acronyms on first use in comments, docstrings, and docs (never leave a bare `CR`, `LUT`, `SM`, etc. in prose the human has to decode). This is already stated in `CONTEXT_HANDOFF.md` §0; surfaced here because I violated it once. | 1 | 2026-04-17 | Triggered by `CR` in `bitmap_codec.py` inline comment. Acceptable exception: widely-known code-level identifiers that the reader is already looking at (e.g. `\r` in a regex). |
| Line length for comments and documentation: up to 130 characters. Wide monitors make longer lines preferable to aggressive wrapping; reduce scroll burden. Applies to inline comments, docstrings, and `.md` prose. Code lines retain the project's code-style default. | 1 | 2026-04-17 | Only prose; don't re-flow string literals, URLs, or tabular content just to hit the limit. |

## Code Editing

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|

## Domain-Specific (CircuitPython workspace)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|

## Problem-Specific (current task — rotate frequently)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|

## Retention and Evaluation

- Compaction is always a deliberate activity, never a side effect of another edit.
- Never silently drop directives. Absence of recent corrective feedback means a directive is probably working.
- Before removing any entry: state what, why, and verify it isn't the sole record of tracking metadata.
- Prefer splitting over pruning. Create topic files; don't delete to shrink.

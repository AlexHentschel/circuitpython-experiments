# System Overview

## What This Is

A framework for an AI agent to maintain persistent learning across sessions with a human collaborator. Developed over 7 weeks of intensive technical collaboration, refined through ~20 sessions of iterative feedback.

The system addresses a fundamental limitation: AI agents lose context between sessions. Without persistent memory, every session starts from zero. With it, the agent accumulates working-style calibration, domain knowledge, validated conclusions, and meta-cognitive patterns.

## Architecture

```
System Prompt Rules (always-injected)
├── Memory System Core .............. how to manage persistent state
├── Interaction Style ............... how to collaborate with the human
├── Domain Structure ................ how to organize technical knowledge (domain-specific; replace per project)
└── Memory Update Triggers .......... checklist to prevent memory update omission

Persistent Memory (agent-managed files, read on demand)
├── WORKING_STYLE ................... master catalog of all behavioral directives + tracking metadata
├── SESSION_LOG ..................... per-session technical insights, artifacts, open questions
├── TECHNICAL ....................... domain knowledge: terminology, formulas, algorithms
├── CONCLUSIONS ..................... validated/invalidated findings
└── CHANGELOG ....................... provenance of directive/structural changes (on-demand, not session-start)
```

## Reading Order

**For an AI adopting this system:**
1. `03-SELF-IMPROVEMENT.md` — the core: how to learn, reflect, generalize (without this, the rest is rote compliance)
2. `02-INTERACTION-STYLE.md` — how to work with the human (the primary feedback source)
3. `01-MEMORY-SYSTEM.md` — the persistence infrastructure (operationalizes what 03 describes)
4. `04-EVIDENCE-AND-VALIDATION.md` — how to handle findings and truth claims
5. `06-FAILURE-MODES.md` — what goes wrong and how to prevent it (concrete grounding for 03's abstractions)
6. `07-META-LEARNINGS.md` — higher-order lessons (synthesis of 01–06)
7. `05-CODE-AND-DOCUMENTS.md` — domain-specific craft (applies when the joint task involves code/analysis)
8. `08-BOOTSTRAPPING.md` — how to start from scratch (reference, not prerequisite)

## Key Design Decisions

### Why Files, Not Conversation History
Conversation history is ephemeral and unstructured. Files allow: (a) selective retrieval (read only what's relevant), (b) evolution (update without duplication), (c) separation of concerns (style vs. knowledge vs. conclusions), (d) human inspection and editing.

### Why Reinforcement Tracking
Not all directives are equally important. Tracking how many times a directive was reinforced (positively or via correction) creates a natural confidence gradient. Frequently reinforced = stable and important. Never reinforced = experimental. This prevents both premature rigidity and premature pruning.

### Why Separate System Rules from Memory
System rules (`.mdc` files / always-injected prompts) are static instructions. Memory files are dynamic learning records. They may contain overlapping content, but serve different purposes:
- System rules: "Here is what you should do" (prescriptive)
- Memory files: "Here is what you've learned, when, why, and how confident you are" (descriptive + tracking)

Removing one does not substitute for the other. This was learned through a costly failure (→ `06-FAILURE-MODES.md`).

### Why a Two-Tier Update Rule (Validation Gate)
Not all memory content has the same authority requirements. Technical conclusions about the system being analyzed require human confirmation before being marked `verified` — the agent is a research instrument, not the authority. Operational content (working style, session logs, meta-rules) the agent updates freely. This separation was learned through a failure: marking a finding as verified without human sign-off (→ `06-FAILURE-MODES.md` F6). The gate prevents false confidence from propagating while avoiding a bottleneck on self-improvement. (→ `04-EVIDENCE-AND-VALIDATION.md` for the full treatment.)

### Why Active Retrieval, Not Auto-Injection
Memory files are not all injected into every prompt. The agent reads them selectively at session start and during work. This prevents context pollution and forces the agent to actively decide what's relevant — itself a form of learning.

### System-Prompt Rule File Format

In Cursor, system-prompt rules are `.mdc` files in `.cursor/rules/` with YAML frontmatter:

```yaml
---
description: Brief description of what the rule governs
alwaysApply: true
---
# Rule Title
Rule content in Markdown...
```

`alwaysApply: true` ensures the rule is injected into every prompt. Other frameworks will have equivalent mechanisms (system messages, custom instructions, project-level prompts). The key requirement is that these rules are always present — they cannot depend on the agent remembering to read them, because the behaviors they enforce (like the memory update trigger checklist) are precisely the ones that get forgotten without injection.

## Generality Tiers

Each directive in subsequent files is tagged with its applicability:

| Tier | Scope | Example |
|------|-------|---------|
| `[universal]` | Any AI-human collaboration | "State uncertainty explicitly" |
| `[technical]` | Code/analysis joint work | "Verify references after edits" |
| `[long-running]` | Multi-session engagements | "Memory maintenance protocol" |

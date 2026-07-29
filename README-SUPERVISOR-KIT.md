# Codex Supervisor Kit

## Installation

Copy the contents of this kit to the repository root.

Expected paths:

```text
AGENTS.md
SUPERVISOR-INITIAL-PROMPT.md
.agent/
docs/adr/
docs/templates/
```

Keep the existing project files:

```text
docs/architecture.md
docs/roadmap.md
```

Linux filesystems are case-sensitive. Use the exact lowercase paths referenced by `AGENTS.md`, or update all references consistently.

## First run

Open Codex in the repository root and paste the content of `SUPERVISOR-INITIAL-PROMPT.md`.

## Operating model

1. Codex implements one eligible milestone.
2. Automated gates produce `implemented-awaiting-human-review`.
3. You manually review the diff and tests.
4. Record approval or requested changes in `.agent/human-review.md`.
5. On the next run, ask Codex to process the review result before continuing.

## Suggested manual-review continuation prompt

```text
Read the latest entry in .agent/human-review.md. Apply all requested corrections as rework tasks, run the required validation and update the milestone report. If the review is approved, mark the milestone accepted and proceed to plan the next eligible milestone. Preserve all unrelated user changes.
```

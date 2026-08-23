---
name: milestone-execution
description: Execute an approved roadmap milestone with supervisor/subagent orchestration, scoped tasks, validation gates, canonical state updates, and mandatory manual review before acceptance.
---

# Milestone Execution

## Purpose
Use this skill to implement one approved roadmap milestone consistently.

## Required inputs
Read `AGENTS.md`, active roadmap, `docs/architecture.md`, relevant ADRs, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/decisions.md`, `.agent/human-review.md`, code, and tests.

## Preconditions
- predecessors eligible
- required ADRs Accepted/Implemented
- no unresolved human gate
- baseline tests known
- Git working tree understood
- unrelated user changes protected

## Workflow

### 1. Inspect
Check git status, repository structure, implementation, tests, and milestone acceptance criteria. Record pre-existing failures.

### 2. Select
Choose only the next eligible milestone unless explicitly authorized otherwise.

### 3. Decompose
Every task requires:
- ID
- parent milestone
- objective
- scope/exclusions
- owner role
- writable/read-only/forbidden files
- dependencies
- applicable ADRs
- acceptance criteria
- exact validation commands
- expected report

### 4. Delegate
Use subagents for independent scopes, different expertise, or independent review. Avoid overlapping write scopes.

### 5. Implement
Agents inspect first, stay in scope, preserve unrelated changes, avoid future-phase features, comply with ADRs, and run narrow tests.

### 6. Review
Supervisor checks scope, unrelated changes, architecture, tests, security, docs, and acceptance criteria.

### 7. Validate
After each task: diff, narrow tests, architecture/policy checks, acceptance evidence.
After milestone: broad relevant tests, integration/contract/adversarial tests, architecture review, security review, docs review, acceptance matrix.

Never claim a command passed unless it ran successfully.

### 8. Failure handling
Record failure, preserve logs, classify cause, do not retry the same hypothesis unchanged, create corrective task, block dependents, escalate only at a defined gate/blocker.

### 9. Canonical state
Only supervisor updates:
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`
- `.agent/human-review.md`

### 10. Report
Write `.agent/reports/<milestone-id>.md`.

### 11. Manual review
Automated completion is `implemented-awaiting-human-review`, never `accepted`.

## Git safety
Do not reset, rebase, merge, force-push, delete branches, or commit unless explicitly authorized.

## Final checks
- only one eligible milestone advanced
- ADRs satisfied
- no future-scope leakage
- all claimed tests executed
- canonical state updated only by supervisor
- report exists
- milestone awaits manual review

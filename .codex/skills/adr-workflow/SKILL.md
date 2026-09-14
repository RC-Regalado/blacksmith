---
name: adr-workflow
description: Create, review, accept, implement, supersede, and index Architecture Decision Records without rewriting architectural history or bypassing human approval gates.
---

# ADR Workflow

## Purpose
Use this skill for durable architectural decisions, boundary changes, storage/protocol/provider/policy changes, security semantics, or conflicts with accepted ADRs.

## Required inputs
Read `AGENTS.md`, `docs/architecture.md`, `docs/adr/README.md`, related ADRs, active roadmap milestone, relevant code/tests.

## Principle
ADRs explain why an architectural decision exists. Accepted and Implemented ADRs are binding.

## Decision workflow
Requested change -> search existing ADRs.
- Compatible with existing ADR: implement.
- No existing ADR: create Proposed ADR.
- Conflicts with Accepted/Implemented ADR: create Proposed superseding ADR and stop for human approval.

## ADR statuses
Proposed, Accepted, Implemented, Rejected, Deprecated, Superseded.

## Required ADR structure
- Status
- Date
- Deciders
- Supersedes
- Superseded by
- Context
- Decision drivers
- Options considered
- Decision
- Consequences
- Compatibility and migration
- Validation
- Review trigger
- Agent constraint

## Superseding
Never delete history.
New ADR references `Supersedes: ADR-XXX`.
Old ADR becomes Superseded only after required approval and references the replacement.

## Human gate
If implementation contradicts an Accepted/Implemented ADR:
1. stop contradictory implementation;
2. create Proposed superseding ADR;
3. document migration/impact;
4. block dependent tasks;
5. record the human gate;
6. wait for approval.

## Implemented status
Use Implemented only after code, tests, docs, and acceptance evidence match the decision.

## Final checks
- history preserved
- no accepted ADR silently changed
- supersedes links consistent
- ADR index updated
- implementation did not precede required approval

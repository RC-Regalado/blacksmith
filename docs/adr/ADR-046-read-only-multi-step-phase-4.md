# ADR-046 — Read-Only Multi-Step Phase 4

- Status: Accepted
- Date: 2026-08-05
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 1 through Phase 3 established the secure local-first runtime, policy-controlled tools, audit, confirmations and C toolserver. Phase 4 introduces objective-driven multi-step execution.

## Decision

Autonomous multi-step execution excludes write, replanning, retry, parallelism and subagents.

## Consequences

### Positive

- clearer platform boundary;
- deterministic and testable orchestration;
- provider and executor independence;
- bounded autonomous behavior.

### Negative

- additional domain and persistence complexity;
- no autonomous write, retry, replanning, parallelism or subagents in this phase.

## Validation

This ADR becomes Implemented only after its roadmap acceptance criteria and adversarial tests pass.

## Agent constraint

Accepted or Implemented status is binding. A contradiction requires a superseding Proposed ADR and human approval.

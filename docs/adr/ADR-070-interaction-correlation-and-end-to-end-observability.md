# ADR-070 — Interaction Correlation and End-to-End Observability

- Status: Implemented
- Date: 2026-08-27
- Deciders: Project owner
- Supersedes: 
- Superseded by:

## Context
The deep chat/context/tooling audit found blocking correctness and observability issues in the Phase 5.1 conversational runtime.

Baseline: `docs/audits/chat-tool-context-audit.md`.

## Decision
Assign one interaction_id per conversational turn and propagate it through context retrieval, model calls, tool execution, recovery, budgets and final completion.

## Decision drivers
- preserve safety
- support legitimate bounded workflows
- expose model termination correctly
- deterministic budgets/guards
- preserve Ports & Adapters

## Consequences
### Positive
- stronger chat correctness
- visible truncation
- bounded multi-step tools
- end-to-end traceability

### Negative
- wider provider contract
- additional orchestration components
- migration from legacy single-round assumptions

## Validation
Implemented only when roadmap criteria and adversarial/regression tests pass.

## Agent constraint
Do not implement contradictory behavior before this ADR is Accepted.

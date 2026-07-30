# ADR-014 — Non-streaming calls in Phase 1

- Status: Implemented
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Streaming complicates contracts, persistence, cancellation and CLI behavior.

## Options considered

Implement streaming now; defer streaming.

## Decision

Use complete non-streaming model responses in Phase 1.

Send `stream=false` and return one normalized assistant message.

## Consequences

Simpler tests and atomic persistence; interactive latency improvements are postponed.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

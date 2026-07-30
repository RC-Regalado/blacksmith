# ADR-024 — Bounded Single Tool Round per Turn

- Status: Accepted
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Recursive tool loops increase risk and are out of scope for Phase 2.

## Decision drivers

- Keep behavior understandable.
- Prevent autonomous chains.
- Preserve transactional conversation writes.

## Options considered

No tool result back to model; unbounded loop; exactly one bounded tool round.

## Decision

Allow at most one tool execution round per user turn:

```text
user -> model tool request -> policy/execution -> tool result message -> model final response
```

If the second model response requests another tool, the runtime terminates safely without executing it and returns a bounded assistant response or typed denial.

## Consequences

- Positive: predictable execution and audit.
- Negative: multi-step tasks remain future work.
- Risk: models may need prompting to provide final answers after one result.

## Compatibility and migration

No-tool Phase 1 behavior must remain unchanged.

## Validation

Tests must cover no-tool regression, one successful round, denial path and second-tool-request termination.

## Review trigger

Reconsider in a future advanced agent runtime phase.

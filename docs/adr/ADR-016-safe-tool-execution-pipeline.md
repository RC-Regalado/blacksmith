# ADR-016 — Safe Tool Execution Pipeline

- Status: Accepted
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 2 adds read-only workspace tools. Model output can request a tool, but model intent cannot authorize execution.

## Decision drivers

- Keep runtime deterministic and auditable.
- Prevent executor calls before catalog, policy, path and audit checks.
- Preserve Phase 1 behavior when no tool is requested.

## Options considered

Direct runtime execution; executor-owned authorization; application coordinator with explicit ports.

## Decision

Use a `ToolExecutionCoordinator` in the application layer.

Execution order:

```text
ToolCallPlan -> ToolCatalog -> ToolPolicy -> PathPolicy -> AuditRecorder -> ToolExecutor -> AuditRecorder -> tool result Message
```

Denied requests must not reach an executor. Executor implementations execute only already-authorized requests and never decide authorization.

## Consequences

- Positive: one place owns deterministic execution flow and audit completeness.
- Negative: more ports and tests are required.
- Risk: coordinator can become too large; split only when tests show real complexity.

## Compatibility and migration

No Phase 1 behavior changes are allowed for turns without tool calls.

## Validation

Unit tests must prove denied requests do not invoke executors and every outcome is audited.

## Review trigger

Reconsider when Phase 3 introduces a separate productive tool service as the default executor.

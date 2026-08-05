# ADR-028 — C Toolserver as Primary Executor

- Status: Implemented
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 2 added a Python local executor and a Unix socket adapter to a C toolserver. Phase 3 introduces process execution and writes, which benefit from a process boundary.

## Decision drivers

- Keep productive tool execution outside the Python agent process.
- Avoid network exposure.
- Preserve independent validation in Python and C.
- Avoid silent weakening if the C executor is unavailable.

## Options considered

Keep Python as productive executor; TCP service; Unix socket C toolserver as primary.

## Decision

The C toolserver is the primary productive executor for Phase 3 tools.

Python remains responsible for model interaction, catalog, policy, confirmation, path prevalidation, coordination and audit. C repeats critical validation before filesystem or process access.

Executor selection is explicit:

```text
AI_ASSISTANT_TOOL_EXECUTOR=unix_socket
```

Missing socket, malformed responses, timeouts and request ID mismatches return typed errors. There is no silent fallback from C to Python for productive execution.

## Consequences

- Positive: clearer safety boundary for writes and process profiles.
- Negative: local operation requires a running Unix socket toolserver.
- Risk: protobuf compatibility must be maintained carefully.

## Compatibility and migration

The current Python executor may remain for tests or explicitly configured development use, but not as silent productive fallback.

## Validation

Contract tests must cover every Phase 3 tool through the Unix socket/C path and missing-socket behavior.

## Review trigger

Changing transport, adding fallback, or changing protobuf incompatibly requires human approval.

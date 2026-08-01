# ADR-022 — Unix Socket Tool Executor

- Status: Implemented
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

The repository already contains a Unix socket protobuf client and C toolserver prototype. Phase 2 may later route authorized read-only requests to a separate process.

## Decision drivers

- Keep process boundary available.
- Avoid TCP/network exposure.
- Preserve protobuf compatibility.
- Validate independently on both Python and C sides.

## Options considered

Use only Python executor; expose TCP; use Unix socket executor behind the same `ToolExecutor` port.

## Decision

Add `UnixSocketToolExecutor` as an infrastructure adapter behind `ToolExecutor`.

Rules:

- transmit only already-authorized requests;
- use Unix domain sockets only;
- no TCP listener;
- correlate request and response IDs;
- map missing socket, timeout, malformed response and oversized response to typed errors;
- C side repeats workspace and limit validation.

## Consequences

- Positive: future process isolation without changing application ports.
- Negative: protocol tests are required.
- Risk: protobuf changes require compatibility discipline.

## Compatibility and migration

Do not change protobuf incompatibly without human approval.

## Validation

Contract and integration tests must cover timeout, missing socket, malformed response and ID mismatch.

## Review trigger

Reconsider if Phase 3 chooses another transport.

# ADR-017 — Deny-by-Default Tool Policy

- Status: Implemented
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Read-only tools still expose local data. Unknown tool names, malformed arguments and excessive limits must fail closed.

## Decision drivers

- Model input is untrusted.
- Stable denial reasons are required for tests and audit.
- The model cannot choose permissions or hard limits.

## Options considered

Allow unless invalid; allow known tools with model-provided limits; deny unless every check passes.

## Decision

Use deny-by-default policy.

The policy denies:

- unknown tool names;
- malformed arguments;
- missing required arguments;
- permissions above the static tool permission;
- timeouts or limits above hard maximums;
- path-policy failures;
- disabled tool execution.

Every denial returns a stable reason code.

## Consequences

- Positive: safe default and clear audit events.
- Negative: more explicit argument validation.
- Risk: users may need clearer error messages for denied safe requests.

## Compatibility and migration

No existing tool calls execute in Phase 1; this adds controlled denial semantics for Phase 2.

## Validation

Tests must assert unknown and malformed requests are denied and do not invoke executors.

## Review trigger

Reconsider only when adding user-managed tool permissions.

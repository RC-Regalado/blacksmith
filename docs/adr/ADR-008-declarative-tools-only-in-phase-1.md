# ADR-008 — Declarative tools only in Phase 1

- Status: Implemented
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Tool execution introduces permissions, side effects and safety policy beyond Phase 1.

## Options considered

Ignore tools; execute tools immediately; declarative representation only.

## Decision

Represent and interpret tool calls without executing them.

Add ToolDefinition, ToolCall and interpreter, but no executor.

## Consequences

The protocol can evolve safely; no autonomous side effects occur.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

# ADR-009 — No agent framework dependency

- Status: Implemented
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

The project seeks a small understandable runtime and low dependency count.

## Options considered

Adopt an agent framework; build a focused internal runtime.

## Decision

Do not depend on LangChain, LangGraph or similar frameworks in Phase 1.

Keep the runtime framework-agnostic and integrate future frameworks only through adapters.

## Consequences

More code is owned locally, but architecture and behavior remain under project control.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

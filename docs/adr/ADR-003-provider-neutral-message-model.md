# ADR-003 — Provider-neutral Message model

- Status: Implemented
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Ollama and OpenAI-compatible APIs encode messages differently.

## Options considered

Use provider dictionaries throughout; internal neutral model.

## Decision

Keep an internal Message model independent of external APIs.

Use a typed internal Message and map at adapter boundaries.

## Consequences

Mapping code is required, but provider formats do not leak into the runtime.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

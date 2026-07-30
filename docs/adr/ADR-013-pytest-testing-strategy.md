# ADR-013 — Pytest testing strategy

- Status: Implemented
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

The project requires fixtures, markers and optional real-Ollama validation.

## Options considered

Remain on unittest; migrate to pytest.

## Decision

Use pytest and separated test categories.

Use unit, integration, contract, ollama and smoke markers.

## Consequences

Core CI is independent of Ollama; optional environment-specific suites remain explicit.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

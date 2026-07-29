# ADR-001 — Ports and Adapters

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

The runtime must support multiple model providers, stores and interfaces without depending on concrete infrastructure.

## Options considered

Direct concrete dependencies; a simple factory without ports; Ports and Adapters.

## Decision

Use lightweight Ports and Adapters with dependency inversion.

The application core defines ports and infrastructure implements them.

## Consequences

More interfaces and files, but provider/store replacement and testing become predictable.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

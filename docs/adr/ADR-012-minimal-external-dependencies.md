# ADR-012 — Minimal external dependencies

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Deployment and auditability benefit from a small dependency graph.

## Options considered

SDK-heavy implementation; standard library first.

## Decision

Prefer the Python standard library and justify additions.

Use stdlib where practical, including `urllib` initially; use pytest for development tests.

## Consequences

Some HTTP ergonomics are lower; future replacement remains possible behind adapter code.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

# ADR-002 — Python 3.12+ core

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

The current phase prioritizes rapid iteration, clear tests and local integration.

## Options considered

C core now; older Python compatibility; Python 3.12+.

## Decision

Use Python 3.12 or newer for Phase 1.

Implement the initial runtime in Python 3.12+.

## Consequences

Future C components remain possible behind ports; Phase 1 does not optimize prematurely.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

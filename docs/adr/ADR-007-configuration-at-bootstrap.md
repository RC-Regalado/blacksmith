# ADR-007 — Configuration at bootstrap

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Scattered environment reads make tests and behavior unpredictable.

## Options considered

Read variables anywhere; configuration framework; immutable config object.

## Decision

Load environment configuration once at the composition root.

Create validated AppConfig from environment in bootstrap.

## Consequences

No `.env` dependency in Phase 1; values are easy to inject in tests.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

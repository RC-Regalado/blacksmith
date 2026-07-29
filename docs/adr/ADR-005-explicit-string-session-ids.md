# ADR-005 — Explicit string session IDs

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Global history prevents conversation isolation and persistence semantics.

## Options considered

Implicit current session; integer IDs; string IDs.

## Decision

Represent conversations with explicit string session IDs.

Use string `session_id` with CLI default `default`.

## Consequences

Simple external interfaces; interactive session management is postponed.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

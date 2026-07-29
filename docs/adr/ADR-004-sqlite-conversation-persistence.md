# ADR-004 — SQLite conversation persistence

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

The application is local-first, single-user and should require no database daemon.

## Options considered

JSON files; PostgreSQL; SQLite.

## Decision

Use SQLite for local conversation persistence.

Use SQLite through a ConversationStore adapter.

## Consequences

Simple deployment and transactions; not designed for distributed multi-user writes.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

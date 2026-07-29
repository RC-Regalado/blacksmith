# ADR-010 — Transactional turn persistence

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

A failure between writes can leave incomplete conversation history.

## Options considered

Append separately; append both in one transaction.

## Decision

Persist user and assistant messages atomically.

ConversationStore provides transactional `append_many`.

## Consequences

Provider failure leaves no partial turn; store implementations must support atomic semantics.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.

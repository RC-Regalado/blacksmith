# Architecture Decision Records

ADRs preserve durable architectural decisions and their rationale.

## Binding rule

An ADR with status `Accepted` or `Implemented` is binding for all agents.

A contradictory change requires a new ADR in `Proposed` status, an explicit `Supersedes` field and human approval before implementation.

Historical ADRs are never deleted or silently rewritten.

## Statuses

- `Proposed`
- `Accepted`
- `Implemented`
- `Deprecated`
- `Superseded`
- `Rejected`

## Index

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Ports and Adapters | Accepted |
| ADR-002 | Python 3.12+ core | Accepted |
| ADR-003 | Internal provider-neutral Message model | Accepted |
| ADR-004 | SQLite conversation persistence | Accepted |
| ADR-005 | Explicit string session IDs | Accepted |
| ADR-006 | ModelProvider port | Accepted |
| ADR-007 | Configuration loaded at bootstrap | Accepted |
| ADR-008 | Declarative tools without execution in Phase 1 | Accepted |
| ADR-009 | No agent framework dependency | Accepted |
| ADR-010 | Transactional persistence of turns | Accepted |
| ADR-011 | Native Ollama API adapter | Accepted |
| ADR-012 | Minimal external dependencies | Accepted |
| ADR-013 | Pytest testing strategy | Accepted |
| ADR-014 | Non-streaming model calls in Phase 1 | Accepted |
| ADR-015 | Configurable model profiles for limited hardware | Accepted |

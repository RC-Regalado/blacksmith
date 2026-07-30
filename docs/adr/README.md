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
| ADR-001 | Ports and Adapters | Implemented |
| ADR-002 | Python 3.12+ core | Implemented |
| ADR-003 | Internal provider-neutral Message model | Implemented |
| ADR-004 | SQLite conversation persistence | Implemented |
| ADR-005 | Explicit string session IDs | Implemented |
| ADR-006 | ModelProvider port | Implemented |
| ADR-007 | Configuration loaded at bootstrap | Implemented |
| ADR-008 | Declarative tools without execution in Phase 1 | Implemented |
| ADR-009 | No agent framework dependency | Implemented |
| ADR-010 | Transactional persistence of turns | Implemented |
| ADR-011 | Native Ollama API adapter | Implemented |
| ADR-012 | Minimal external dependencies | Implemented |
| ADR-013 | Pytest testing strategy | Implemented |
| ADR-014 | Non-streaming model calls in Phase 1 | Implemented |
| ADR-015 | Configurable model profiles for limited hardware | Implemented |

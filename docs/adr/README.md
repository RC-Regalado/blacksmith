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
| ADR-016 | Safe Tool Execution Pipeline | Implemented |
| ADR-017 | Deny-by-Default Tool Policy | Implemented |
| ADR-018 | Read-Only Tool Allowlist | Implemented |
| ADR-019 | Workspace Confinement and Path Resolution | Implemented |
| ADR-020 | Tool Execution Audit and Retention | Implemented |
| ADR-021 | Tool Timeouts and Resource Limits | Implemented |
| ADR-022 | Unix Socket Tool Executor | Implemented |
| ADR-023 | Error and Log Redaction | Implemented |
| ADR-024 | Bounded Single Tool Round per Turn | Implemented |
| ADR-025 | Sensitive File Deny Policy | Implemented |
| ADR-026 | Controlled Development Tool Allowlist | Implemented |
| ADR-027 | Permission Levels and Confirmation Grants | Implemented |
| ADR-028 | C Toolserver as Primary Executor | Implemented |
| ADR-029 | Preconfigured Test and Build Profiles | Implemented |
| ADR-030 | Controlled Workspace Write Semantics | Implemented |
| ADR-031 | Atomic Writes and Optimistic Concurrency | Implemented |
| ADR-032 | Git Read-Only Inspection | Implemented |
| ADR-033 | Search Text Limits and Redaction | Implemented |
| ADR-034 | Audit Retention and Manual Purge | Implemented |
| ADR-035 | Process Output, Timeout and Environment Limits | Implemented |
| ADR-036 | Agent Execution Platform Direction | Implemented |
| ADR-037 | Objective, Plan, Task and Execution Models | Implemented |
| ADR-038 | Capability Registry | Implemented |
| ADR-039 | Execution Graph Validation | Implemented |
| ADR-040 | Deterministic Sequential Scheduler | Implemented |
| ADR-041 | Execution Budgets | Implemented |
| ADR-042 | Execution State Persistence | Implemented |
| ADR-043 | Structured Planner Contract | Implemented |
| ADR-044 | Objective Evaluation | Implemented |
| ADR-045 | Logical Checkpoint Semantics | Implemented |
| ADR-046 | Read-Only Multi-Step Phase 4 | Implemented |
| ADR-047 | Context & Knowledge Engine | Implemented |
| ADR-048 | KnowledgeStore Is Derived State | Implemented |
| ADR-049 | Knowledge Source Model | Implemented |
| ADR-050 | Incremental Content-Hash Indexing | Implemented |
| ADR-051 | Hybrid Retrieval | Implemented |
| ADR-052 | EmbeddingProvider Separation | Implemented |
| ADR-053 | SQLite FTS5 as Initial Lexical Index | Implemented |
| ADR-054 | Local Embedding Storage | Implemented |
| ADR-055 | Context Compilation | Implemented |
| ADR-056 | Context Provenance | Implemented |
| ADR-057 | Context Budgets | Implemented |
| ADR-058 | Stale Knowledge Handling | Implemented |
| ADR-059 | Manual Index Lifecycle | Implemented |
| ADR-060 | No Semantic Long-Term Memory in Phase 5 | Implemented |
| ADR-061 | No Automatic Skill Generation in Phase 5 | Implemented |
| ADR-062 | Conversational Context Integration | Implemented |
| ADR-063 | Opt-In Knowledge Context for Chat | Implemented |
| ADR-064 | Conversation Context Budget | Implemented |
| ADR-065 | Indexed Knowledge vs Live Capability Semantics | Implemented |
| ADR-066 | Unified CLI Command Model | Implemented |
| ADR-067 | Deterministic Conversation Retrieval Policy | Implemented |

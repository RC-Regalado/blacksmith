# ADR-062 — Conversational Context Integration

- Status: Implemented
- Date: 2026-08-19
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 5 completed the Context & Knowledge Engine. Phase 5.1 integrates it into the normal chat and CLI experience without changing the major platform model.

## Decision

Integrate Knowledge/Context Engine into normal chat through a dedicated conversation-context application service rather than direct store/provider coupling.

## Constraints

- preserve Phase 1–5 compatibility;
- KnowledgeStore remains derived;
- no automatic rebuild;
- no MCP/network retrieval/semantic long-term memory/automatic skills;
- ToolPolicy remains authoritative;
- Phase 5.1 uses one final human review rather than per-milestone manual review.

## Validation

Implementation requires automated tests, independent subagent validation, architecture review, security/policy review and mini-phase end-to-end validation.

## Agent constraint

Accepted/Implemented status is binding. Contradiction requires a superseding Proposed ADR and applicable human approval.

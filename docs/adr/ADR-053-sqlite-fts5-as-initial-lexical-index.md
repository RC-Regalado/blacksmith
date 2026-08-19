# ADR-053 — SQLite FTS5 as Initial Lexical Index

- Status: Accepted
- Date: 2026-08-17
- Deciders: Project owner

## Context
Phase 1-4 established the local-first runtime, secure capabilities, execution engine and evidence-based completion. Phase 5 reduces primary-model work through local derived knowledge.

## Decision
Use SQLite FTS5 as the initial local lexical search backend.

## Constraints
- preserve canonical store boundaries
- derived knowledge must be rebuildable
- stale knowledge is excluded
- CPU-capable operation preferred
- MCP/network retrieval/long-term semantic memory/automatic skills are out of scope

## Validation
Implement only after corresponding roadmap criteria and tests pass.

## Agent constraint
Accepted/Implemented status is binding; contradiction requires a superseding Proposed ADR and human approval.

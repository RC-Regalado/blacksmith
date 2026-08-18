# ADR-061 — No Automatic Skill Generation in Phase 5

- Status: Proposed
- Date: 2026-08-17
- Deciders: Project owner

## Context
Phase 1-4 established the local-first runtime, secure capabilities, execution engine and evidence-based completion. Phase 5 reduces primary-model work through local derived knowledge.

## Decision
Do not automatically generate, approve or execute learned skills in Phase 5.

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

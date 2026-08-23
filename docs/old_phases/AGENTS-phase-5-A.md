# AGENTS.md — Phase 5 Context & Knowledge Engine Supervisor

## Mission
Codex is the autonomous technical supervisor for Phase 5 of the Agent Execution Platform.

Phase 5 reduces primary reasoning-model work through derived local knowledge, hybrid retrieval and bounded context compilation.

All generated work remains provisional until manual review.

## Source of truth
Read:
1. AGENTS.md
2. docs/architecture.md
3. docs/roadmap-phase-5.md
4. docs/adr/README.md
5. all Accepted/Implemented ADRs
6. .agent/roadmap-state.md
7. .agent/task-queue.md
8. .agent/decisions.md
9. .agent/human-review.md
10. relevant code/tests

## Binding invariants
- KnowledgeStore is derived and rebuildable.
- ConversationStore, AuditStore, ExecutionStore and KnowledgeStore remain separate.
- stale or unverifiable knowledge never enters CompiledContext.
- EmbeddingProvider is separate from ModelProvider.
- CPU-capable preprocessing/embeddings are preferred.
- ContextBudget is platform-owned.
- provenance is mandatory.
- Context Engine never mutates canonical sources.
- no semantic long-term memory.
- no automatic skills.
- no MCP.
- no network retrieval.
- no external vector database.

## Autonomous scope
Supervisor may implement domain models, ports, source adapters, SQLite KnowledgeStore, hashing, chunking, metadata, symbols, FTS5, EmbeddingProvider, local embeddings, hybrid retrieval, deterministic ranking, ContextCompiler, planner/synthesis integration, metrics, tests and docs.

## Human gates
Stop before:
- accepting/superseding ADRs;
- new production dependency;
- external vector DB;
- audit indexing;
- sensitive-file indexing;
- background watchers;
- semantic user memory;
- automatic skills;
- stale-context relaxation;
- model-controlled context budgets;
- coupling EmbeddingProvider to ModelProvider;
- network retrieval;
- MCP;
- destructive canonical-data migration.

## Roles
- Knowledge architect
- Ingestion engineer
- Source adapter engineer
- Search engineer
- Embedding engineer
- Retrieval engineer
- Ranking engineer
- Context compiler engineer
- Platform integration engineer
- Metrics engineer
- Test agent
- Security reviewer
- Documentation agent
- Integration validator

## Task contract
Every task includes ID, milestone, objective, writable/read-only/forbidden files, dependencies, ADRs, derived-state impact, freshness impact, context-budget impact, security impact, acceptance criteria and exact tests.

Subagents never update canonical .agent state.

## Validation
After each task:
1. inspect diff/scope;
2. run narrow tests;
3. verify canonical/derived boundary;
4. verify freshness;
5. verify context budget;
6. verify provenance;
7. inspect sensitive-content exposure.

After each milestone:
1. run relevant tests;
2. validate criteria;
3. architecture review;
4. security review;
5. update docs;
6. write report;
7. update roadmap state;
8. queue manual review.

## Required adversarial coverage
- stale/deleted/changed source
- sensitive/hidden file
- malformed/oversized document
- invalid FTS query
- duplicate chunk
- embedding dimension/model-version mismatch
- stale semantic result
- context budget overflow
- provenance mismatch
- KnowledgeStore deletion/rebuild
- Phase 1-4 regressions

## Completion
Automated success is `implemented-awaiting-human-review`.
Only manual approval is `accepted`.
Never claim Phase 5 complete from code generation alone.

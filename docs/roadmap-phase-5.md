# Phase 5 Roadmap — Context & Knowledge Engine

## Objective
Reduce primary-LLM workload by transforming canonical local data into derived, indexed, versioned and retrievable knowledge, then compiling bounded high-relevance context for planning and final synthesis.

## Architecture
Canonical Sources -> Ingestion -> KnowledgeStore -> Hybrid Retrieval -> ContextCompiler -> Planner / Finalizer -> ExecutionEngine

## Store boundary
ConversationStore, AuditStore, ExecutionStore and KnowledgeStore remain separate.
KnowledgeStore is derived and rebuildable.

## Phase 5A — Knowledge Foundation
- Knowledge domain models
- KnowledgeSource ports
- SQLite KnowledgeStore
- hashing and invalidation
- normalization and chunking
- metadata and symbols
- SQLite FTS5
- manual index lifecycle

## Phase 5B — Semantic Retrieval
- EmbeddingProvider separate from ModelProvider
- CPU-capable local embeddings
- embedding storage
- bounded semantic similarity
- HybridRetriever
- deterministic KnowledgeRanker

## Phase 5C — Context Compiler
- ContextBudget
- provenance
- stale filtering
- deduplication
- PlanningContext
- SynthesisContext

## Phase 5D — Execution Integration
- ContextEngine before Planner
- SynthesisContext after execution
- efficiency observability
- functional evaluation

## Initial sources
- FILE
- ADR
- EXECUTION
- selected CONVERSATION

Audit indexing is excluded.

## Context budget defaults
- max_context_tokens: 4096
- max_sources: 8
- max_chunks: 12
- max_chunk_tokens: 800

## Core ports
- KnowledgeSource
- KnowledgeStore
- LexicalIndex
- SymbolIndex
- EmbeddingProvider
- KnowledgeRetriever
- KnowledgeRanker
- ContextCompiler

## Stale policy
fresh -> eligible
stale -> excluded
unknown freshness -> excluded

## Manual CLI
- `python main.py knowledge index .`
- `python main.py knowledge status`
- `python main.py knowledge rebuild`
- `python main.py knowledge query "..."`

No filesystem watcher in Phase 5.

## Metrics
- knowledge_candidates
- knowledge_chunks_selected
- knowledge_cache_hits
- knowledge_stale_rejected
- raw_context_estimated_tokens
- compiled_context_estimated_tokens
- retrieval_ms
- embedding_ms
- context_compile_ms
- tool_calls_avoided
- context_reduction_ratio

## Milestones
### M5.1 Freeze Phase 4 baseline
Verify manual acceptance, full tests, corrected synthesis/final outcome, ADR-036..046 Implemented.

### M5.2 Approve ADR-047..061
No productive implementation before approval.

### M5.3 Knowledge domain models
KnowledgeDocument, KnowledgeChunk, KnowledgeSymbol, KnowledgeQuery, RetrievalCandidate, ContextEvidence, CompiledContext, ContextBudget.

### M5.4 KnowledgeSource ports
Filesystem, ADR, Execution and selected Conversation adapters.

### M5.5 SQLite KnowledgeStore
Dedicated derived-state database.

### M5.6 Hashing and invalidation
Skip unchanged sources; invalidate changed/deleted records.

### M5.7 Normalization and chunking
Structure-aware docs; symbol-aware code where possible; bounded fallback.

### M5.8 Metadata and symbols
Path, type, language, version, hashes and symbols.

### M5.9 SQLite FTS5
Lexical index with freshness and metadata filtering.

### M5.10 Manual knowledge CLI
index/status/rebuild/query.

### M5.11 EmbeddingProvider
Independent from ModelProvider; CPU-capable; dummy adapter for tests.

### M5.12 Embedding storage and similarity
Local vector storage, provider/model/version/dimension metadata, bounded CPU similarity.

### M5.13 HybridRetriever
Merge lexical, symbol, semantic and metadata candidates; deduplicate; exclude stale.

### M5.14 Deterministic KnowledgeRanker
Inspectable component scores; deterministic tie-breaking; no LLM reranker.

### M5.15 ContextCompiler
PlanningContext and SynthesisContext with budgets, provenance and deduplication.

### M5.16 Planner integration
Objective -> ContextEngine -> Planner.

### M5.17 Synthesis integration
Execution results -> ContextEngine -> Final synthesis/evaluation.

### M5.18 Efficiency observability
Record retrieval/context metrics and reduction ratio.

### M5.19 Security/freshness/regression suite
Test stale/deleted/changed sources, sensitive paths, malformed data, embedding mismatch, budget overflow, provenance mismatch and Phase 1-4 regressions.

### M5.20 Functional evaluation
Scenario A: explain why ExecutionEngine cannot write.
Scenario B: diagnose scheduler test failure.
Measure tool calls, model calls, compiled tokens and latency.

### M5.21 Documentation and final review
Update architecture, ADRs, indexing lifecycle, retrieval, embeddings, context compilation, metrics and operator docs.

## ADR plan
- ADR-047 Context & Knowledge Engine
- ADR-048 KnowledgeStore Is Derived State
- ADR-049 Knowledge Source Model
- ADR-050 Incremental Content-Hash Indexing
- ADR-051 Hybrid Retrieval
- ADR-052 EmbeddingProvider Separation
- ADR-053 SQLite FTS5 as Initial Lexical Index
- ADR-054 Local Embedding Storage
- ADR-055 Context Compilation
- ADR-056 Context Provenance
- ADR-057 Context Budgets
- ADR-058 Stale Knowledge Handling
- ADR-059 Manual Index Lifecycle
- ADR-060 No Semantic Long-Term Memory in Phase 5
- ADR-061 No Automatic Skill Generation in Phase 5

## Explicit exclusions
- MCP
- external vector DB
- filesystem watcher daemon
- internet/web retrieval
- semantic long-term user memory
- automatic skill generation/execution
- model training/fine tuning
- LLM reranking
- distributed indexing
- remote KnowledgeStore

## Completion criteria
Phase 5 is accepted when KnowledgeStore is rebuildable, incremental indexing works, lexical and semantic retrieval work, stale data is excluded, compiled contexts are bounded and provenance-rich, planner and final synthesis consume prepared context, efficiency reduction is measurable, Phase 1-4 remain compatible, tests pass and manual review is approved.

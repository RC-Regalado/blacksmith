# AI Assistant

Local-first AI assistant core written in Python.

Phase 1 provides a small CLI, framework-agnostic agent runtime, provider adapters, conversation memory, SQLite persistence, configuration, logging, typed errors, context budgeting, declarative tool-call detection and separated CI.

Phase 2 adds bounded read-only workspace tools behind policy, path validation, audit and executor ports.

Phase 3 adds controlled development tools through the C toolserver: metadata, literal search, Git inspection, approved test/build profiles and bounded atomic writes.

Phase 4 adds the Agent Execution Engine: objective planning, validated read-only DAG execution, budgets, checkpoints, evidence-driven evaluation, observability and adversarial regression coverage.

Phase 5 adds the Context & Knowledge Engine: derived local knowledge, manual indexing, FTS5 lexical retrieval, local embeddings, hybrid retrieval, context compilation, objective integration, metrics and functional evaluation support.

## Requirements

- Python 3.12+
- `pytest` for development tests
- Optional: Ollama for local model smoke tests
- Optional: `protoc`, `protoc-gen-c` and `protobuf-c` for C toolserver contract tests

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

## Run

Default provider is `dummy`, so the CLI works without external services:

```bash
python main.py
```

Exit with `quit`, `exit` or EOF.

## Configuration

Configuration is loaded once at bootstrap from environment variables.

| Variable | Default | Purpose |
|---|---|---|
| `AI_ASSISTANT_PROVIDER` | `dummy` | `dummy`, `ollama`, `openai` or `chatgpt` |
| `AI_ASSISTANT_MODEL` | empty | Provider model name |
| `AI_ASSISTANT_BASE_URL` | provider-specific | Ollama or OpenAI-compatible base URL |
| `AI_ASSISTANT_DATABASE` | `assistant.sqlite3` | SQLite database path |
| `AI_ASSISTANT_EXECUTION_DATABASE` | `assistant_execution.sqlite3` | Separate SQLite execution database path |
| `AI_ASSISTANT_KNOWLEDGE_DATABASE` | `assistant_knowledge.sqlite3` | Separate derived SQLite knowledge database path |
| `AI_ASSISTANT_SESSION` | `default` | Conversation session ID |
| `AI_ASSISTANT_SYSTEM_PROMPT` | `You are a local AI assistant.` | System prompt |
| `AI_ASSISTANT_LOG_LEVEL` | `INFO` | Python logging level |
| `AI_ASSISTANT_REQUEST_TIMEOUT` | `60` | Provider request timeout in seconds |
| `AI_ASSISTANT_CONTEXT_LIMIT` | `4096` | Simple character budget for context |
| `AI_ASSISTANT_WORKSPACE` | unset | Workspace root for tools |
| `AI_ASSISTANT_TOOL_EXECUTION` | `false` | Enables tools when `true` and workspace is set |
| `AI_ASSISTANT_TOOL_TIMEOUT` | `5` | Tool timeout in seconds, capped at 30 |
| `AI_ASSISTANT_MAX_READ_BYTES` | `16384` | Default `read_file` byte limit, capped at 65536 |
| `AI_ASSISTANT_MAX_DIRECTORY_ENTRIES` | `200` | Default `list_directory` entry limit, capped at 1000 |
| `AI_ASSISTANT_MAX_DIRECTORY_DEPTH` | `0` | Default recursive depth, capped at 3 |
| `AI_ASSISTANT_AUDIT_DATABASE` | `assistant_audit.sqlite3` | Separate SQLite audit database |
| `AI_ASSISTANT_AUDIT_AUTO_PURGE` | `false` | Reserved; automatic audit purge stays disabled by default |
| `AI_ASSISTANT_TOOL_EXECUTOR` | `unix_socket` | Tool executor, `unix_socket` by default or explicit `local` |
| `AI_ASSISTANT_TOOL_SOCKET` | `c_toolserver/build/toolserver.sock` | Unix socket path for the C toolserver |
| `OPENAI_API_KEY` | unset | API key for OpenAI-compatible providers |

Example with Ollama:

```bash
AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=gemma3:1b \
AI_ASSISTANT_REQUEST_TIMEOUT=180 \
python main.py
```

For the current local server profile and recommended Blacksmith parameters, see
`docs/ollama-local.md`.

Start the C toolserver before using productive tools:

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig \
LD_LIBRARY_PATH=/home/rc-regalado/.local/lib \
make -C c_toolserver

c_toolserver/build/toolserver --socket c_toolserver/build/toolserver.sock
```

Example with tools:

```bash
ollama create blacksmith-tools -f Modelfile

AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=blacksmith-tools \
AI_ASSISTANT_REQUEST_TIMEOUT=240 \
AI_ASSISTANT_WORKSPACE="$PWD" \
AI_ASSISTANT_TOOL_EXECUTION=true \
AI_ASSISTANT_TOOL_EXECUTOR=unix_socket \
AI_ASSISTANT_TOOL_SOCKET=c_toolserver/build/toolserver.sock \
AI_ASSISTANT_CONTEXT_LIMIT=2048 \
python main.py
```

Run an objective through the Phase 4 execution path:

```bash
AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=blacksmith-tools \
AI_ASSISTANT_WORKSPACE="$PWD" \
AI_ASSISTANT_TOOL_EXECUTION=true \
python main.py objective "Inspect repository status"
```

To inspect the raw planner response when a local model fails to produce a valid plan:

```bash
python main.py objective --verbose "Inspect repository status"
```

To include Phase 5 objective metrics:

```bash
python main.py objective --metrics "Explain why ExecutionEngine cannot write files"
```

Manual knowledge indexing:

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge status
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge rebuild .
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge query "ExecutionEngine"
```

The KnowledgeStore is derived and rebuildable. It stays separate from conversation, audit and execution stores.

When tools are enabled, bootstrap appends the local tool-call contract to the system prompt. For deterministic manual testing, paste a tool call directly:

```json
{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}
```

```json
{"tool_call":{"name":"read_file","arguments":{"path":"README.md","max_bytes":1200}}}
```

Phase 3 tool calls use the same envelope:

```json
{"tool_call":{"name":"search_text","arguments":{"path":".","query":"pytest"}}}
```

```json
{"tool_call":{"name":"git_status","arguments":{"path":"."}}}
```

```json
{"tool_call":{"name":"write","arguments":{"path":"tmp-notes.txt","mode":"create","content":"hello\n"}}}
```

`run_tests`, `build_project` and `write` require first-use confirmation per session, workspace and permission. Only literal `yes` approves in the CLI.

Approved process profiles:

| Profile ID | Tool | Fixed argv |
|---|---|---|
| `core-tests` | `run_tests` | `python -m pytest -m "not ollama and not toolserver" -q` |
| `c-toolserver-tests` | `run_tests` | `python -m pytest -m toolserver -q` |
| `python-compile` | `build_project` | `python -m compileall -q ai_assistant main.py` |

Audit retention is enforced through `SQLiteAuditRecorder.purge_expired()`. It is an operator API, supports dry-run, requires explicit confirmation for deletion and is not exposed as a model tool.

## Architecture

The current Python core is layered:

```text
interfaces -> application -> domain
infrastructure -> application ports
infrastructure -> domain
bootstrap -> all layers
```

Package responsibilities:

- `ai_assistant/domain/`: messages, sessions, errors and declarative tool models.
- `ai_assistant/application/`: runtime, context building, tool-call interpretation and ports.
- `ai_assistant/infrastructure/`: model providers and memory stores.
- `ai_assistant/infrastructure/tools/`: local and Unix socket tool executors.
- `ai_assistant/platform/`: objective, plan, execution, budget, checkpoint and evaluation services.
- `ai_assistant/knowledge/`: derived knowledge domain, ports, chunking, retrieval, ranking, context compilation and metrics.
- `ai_assistant/interfaces/`: CLI adapter.
- `ai_assistant/bootstrap/`: composition root and environment configuration.
- `ai_assistant/agent/`, `ai_assistant/cli/`, `ai_assistant/storage/`: compatibility exports.

More detail lives in `docs/architecture.md`.

## Tests

Run everything that does not require a real Ollama service:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
```

Separated suites:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m smoke -q
```

Real Ollama smoke:

```bash
AI_ASSISTANT_MODEL=gemma3:1b \
AI_ASSISTANT_REQUEST_TIMEOUT=180 \
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q
```

CI mirrors these categories in `.github/workflows/ci.yml`.

Core suite without Ollama or C toolserver:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m "not ollama and not toolserver" -q
```

C toolserver contracts when `protobuf-c` is installed locally:

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig \
LD_LIBRARY_PATH=/home/rc-regalado/.local/lib \
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m toolserver -q
```

## Phase 1 Scope

Implemented:

- CLI via `python main.py`
- Dummy provider
- Native Ollama adapter
- OpenAI-compatible adapter
- Explicit sessions
- SQLite persistence with transactional turn writes
- Centralized configuration
- Basic logging
- Typed internal errors
- Context budget
- Declarative tool-call detection without execution
- Pytest suite and separated CI
- Layered architecture and ADR documentation

Not implemented in Phase 1:

- UI beyond CLI
- External integrations
- Tool execution
- Embeddings or RAG
- Streaming responses
- Multi-agent runtime
- Production C tool service integration

## Phase 2 Scope

Implemented:

- Static allowlist for `list_directory` and `read_file`
- Deny-by-default tool policy
- Workspace path confinement and sensitive-file denial
- SQLite tool audit store with redaction
- Local read-only executor
- Bounded one-tool-round runtime integration
- Optional Unix socket executor and C toolserver read-only actions
- Adversarial security tests
- Automatic tool-call prompt when tools are enabled
- Direct operator tool-call JSON for deterministic manual validation

Still out of scope:

- File writes, shell/process execution, Git commands and network tools
- Multi-step autonomous tool chains
- Dynamic plugins, embeddings, RAG, streaming and UIs beyond CLI

## Phase 3 Scope

Implemented:

- Productive allowlist: `file_metadata`, `search_text`, `git_status`, `git_diff`, `run_tests`, `build_project`, `write`
- C toolserver as the primary productive executor
- Permission levels: `READ_METADATA`, `READ_CONTENT`, `READ_REPOSITORY`, `EXECUTE_PROJECT`, `WRITE_WORKSPACE`
- First-use confirmation for `EXECUTE_PROJECT` and `WRITE_WORKSPACE`
- Fixed test/build profiles only; no model-defined commands or shell
- Literal bounded `rg` search
- Read-only Git status and diff
- Bounded UTF-8 `write` with create/replace modes, atomic rename and optional `expected_sha256`
- Audit retention and confirmed manual purge
- Phase 3 adversarial coverage

Still out of scope:

- Append, delete, move, rename, copy, mkdir and unrestricted write
- Arbitrary shell/process execution, package installation and network tools
- Persistent global approvals
- Multiple autonomous tool rounds

## Phase 4 Scope

Implemented:

- Explicit objective CLI: `python main.py objective "..."`
- Provider-neutral `Objective`, `Plan`, `PlatformTask`, `ExecutionRecord`, `ExecutionBudget`, `Checkpoint`, `ExecutionResult` and `EvaluationResult`
- `ModelBackedPlanner` with strict JSON plan contract and tolerant local-model parsing for common JSON wrappers
- `CapabilityRegistry` mapping abstract read-only capabilities to approved tools
- `PlanValidator` for IDs, dependencies, cycles, capabilities, arguments and task budgets
- Immutable execution graph and deterministic sequential scheduler
- Platform-owned budget accounting with `max_writes=0` and `max_replans=0`
- Dedicated `SQLiteExecutionStore`, separate from conversation and audit
- Logical checkpoints that store metadata only
- Evidence-driven objective evaluator
- Metadata-only execution observability
- Phase 4 adversarial and Phase 1-3 regression coverage

Still out of scope:

- Autonomous write
- Retry, replanning, parallel execution and subagents
- Filesystem rollback snapshots
- Dynamic capabilities, remote executors, shell and network tools
- Semantic user memory, automatic skills, MCP, watcher daemon and network retrieval

## Phase 5 Scope

Phase 5 is the Context & Knowledge Engine.

Objective: reduce the work required from the main LLM by transforming local data into indexed, retrievable, versioned knowledge that can be compiled into high-relevance context.

Implemented:

- Derived `SQLiteKnowledgeStore`, separate from canonical stores.
- Manual `knowledge status|index|rebuild|query` CLI.
- Hashing, freshness tracking and rebuild lifecycle.
- Normalization, chunking, metadata and symbol extraction.
- SQLite FTS5 lexical retrieval.
- CPU-capable dummy `EmbeddingProvider` and local embedding storage.
- Bounded semantic similarity and `HybridRetriever`.
- Deterministic `KnowledgeRanker`.
- `ContextCompiler` with provenance and `ContextBudget`.
- Planning and synthesis integration for objective execution.
- Context metrics and `objective --metrics`.
- Security, freshness and Phase 1-4 regression coverage.

Still out of scope:

- Semantic long-term user memory.
- Automatic skill generation.
- MCP.
- Network retrieval.
- External vector database.
- Filesystem watcher daemon.

## ADRs

Architectural decisions are recorded in `docs/adr/`. Accepted and implemented ADRs are binding; changing one requires a superseding ADR and human approval.

# Task Queue

The supervisor is the only agent permitted to update this file.

## Status vocabulary

- `queued`
- `ready`
- `delegated`
- `in-progress`
- `blocked`
- `validation`
- `implemented`
- `rejected`
- `cancelled`

## Tasks

| ID | Milestone | Role | Objective | File scope | Dependencies | Status |
|---|---|---|---|---|---|---|
| M1-T1 | M1 | Runtime implementer | Remove provider debug output from CLI startup path | `ai_assistant/agent/models/adapter.py`, `tests/test_model_adapter.py` | — | implemented |
| M1-T2 | M1 | Documentation agent | Verify repository ignore rules cover generated local artifacts | `.gitignore` | — | implemented |
| M1-T3 | M1 | Integration validator | Validate Milestone 1 acceptance criteria and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M1.md` | M1-T1, M1-T2 | implemented |
| M2-T1 | M2 | Test agent | Add pytest development configuration and markers | `requirements-dev.txt`, `pytest.ini` | M1 | implemented |
| M2-T2 | M2 | Test agent | Convert existing unittest suite to pytest style | `tests/test_agent_runtime.py`, `tests/test_model_adapter.py`, `tests/test_framing.py`, `tests/test_unix_socket_client.py` | M2-T1 | implemented |
| M2-T3 | M2 | Integration validator | Validate pytest migration and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M2.md` | M2-T2 | implemented |
| M3-T1 | M3 | Runtime implementer | Thread explicit session IDs through runtime and in-memory store | `ai_assistant/agent/memory.py`, `ai_assistant/agent/runtime.py`, `ai_assistant/cli/app.py`, `tests/test_agent_runtime.py` | M2 | implemented |
| M3-T2 | M3 | Persistence implementer | Persist and filter SQLite history by session ID | `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py` | M3-T1 | implemented |
| M3-T3 | M3 | Integration validator | Validate explicit sessions and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M3.md` | M3-T2 | implemented |
| M4-T1 | M4 | Persistence implementer | Add transactional append_many to conversation stores | `ai_assistant/agent/memory.py`, `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py` | M3 | implemented |
| M4-T2 | M4 | Runtime implementer | Persist complete turns through append_many | `ai_assistant/agent/runtime.py`, `tests/test_agent_runtime.py` | M4-T1 | implemented |
| M4-T3 | M4 | Integration validator | Validate transactional persistence and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M4.md` | M4-T2 | implemented |
| M5-T1 | M5 | Architect | Create explicit application ports for model and memory | `ai_assistant/application/ports/`, `ai_assistant/agent/models/provider.py`, `ai_assistant/agent/memory.py` | M4 | implemented |
| M5-T2 | M5 | Runtime implementer | Update runtime/providers/tests to depend on ports and fakes | `ai_assistant/agent/runtime.py`, `ai_assistant/agent/models/*.py`, `ai_assistant/cli/app.py`, `tests/test_agent_runtime.py`, `tests/test_ports_contract.py` | M5-T1 | implemented |
| M5-T3 | M5 | Integration validator | Validate explicit ports and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M5.md` | M5-T2 | implemented |
| M6-T1 | M6 | Architect | Add bootstrap composition root | `ai_assistant/bootstrap/`, `ai_assistant/cli/app.py`, `tests/test_cli_app.py` | M5 | implemented |
| M6-T2 | M6 | Runtime implementer | Move CLI runtime construction to bootstrap | `ai_assistant/bootstrap/container.py`, `ai_assistant/cli/app.py`, `ai_assistant/main.py`, `tests/test_cli_app.py` | M6-T1 | implemented |
| M6-T3 | M6 | Integration validator | Validate composition root and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M6.md` | M6-T2 | implemented |
| M7-T1 | M7 | Runtime implementer | Add immutable bootstrap AppConfig loader | `ai_assistant/bootstrap/config.py`, `tests/test_config.py` | M6 | implemented |
| M7-T2 | M7 | Runtime implementer | Wire AppConfig through composition root and model adapter config | `ai_assistant/bootstrap/container.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_cli_app.py`, `tests/test_model_adapter.py` | M7-T1 | implemented |
| M7-T3 | M7 | Integration validator | Validate centralized configuration and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M7.md` | M7-T2 | implemented |
| M8-T1 | M8 | Runtime implementer | Configure stdlib logging at bootstrap | `ai_assistant/bootstrap/logging.py`, `ai_assistant/bootstrap/container.py`, `ai_assistant/bootstrap/config.py`, `tests/test_logging.py`, `tests/test_config.py` | M7 | implemented |
| M8-T2 | M8 | Runtime implementer | Add safe runtime and adapter log events | `ai_assistant/agent/runtime.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/openai_compatible.py`, `tests/test_logging.py` | M8-T1 | implemented |
| M8-T3 | M8 | Integration validator | Validate basic logging and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M8.md` | M8-T2 | implemented |
| M9-T1 | M9 | Runtime implementer | Define internal error hierarchy and map validation errors | `ai_assistant/application/errors.py`, `ai_assistant/agent/message.py`, `ai_assistant/application/ports/memory.py`, `ai_assistant/bootstrap/config.py`, `ai_assistant/bootstrap/logging.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_errors.py`, `tests/test_config.py`, `tests/test_model_adapter.py`, `tests/test_memory_stores.py` | M8 | implemented |
| M9-T2 | M9 | Runtime implementer | Map infrastructure failures and CLI messages | `ai_assistant/storage/sqlite_memory.py`, `ai_assistant/agent/models/openai_compatible.py`, `ai_assistant/cli/app.py`, `tests/test_errors.py`, `tests/test_logging.py`, `tests/test_cli_app.py` | M9-T1 | implemented |
| M9-T3 | M9 | Integration validator | Validate typed errors and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M9.md` | M9-T2 | implemented |
| M10-T1 | M10 | Model provider implementer | Add native Ollama chat provider | `ai_assistant/agent/models/ollama.py`, `tests/test_ollama_model.py` | M9 | implemented |
| M10-T2 | M10 | Model provider implementer | Wire Ollama provider through config and adapter factory | `ai_assistant/bootstrap/config.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/__init__.py`, `tests/test_config.py`, `tests/test_model_adapter.py`, `tests/test_ollama_model.py`, `tests/test_ollama_smoke.py` | M10-T1 | implemented |
| M10-T3 | M10 | Integration validator | Validate native Ollama adapter and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M10.md` | M10-T2 | implemented |
| M11-T1 | M11 | Documentation agent | Document local model profiles and evaluation guide | `docs/model-profiles.md`, `docs/architecture.md` | M10 | implemented |
| M11-T2 | M11 | Runtime implementer | Keep model and context configurable without hardcoded model default | `ai_assistant/bootstrap/config.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_config.py`, `tests/test_smoke.py` | M11-T1 | implemented |
| M11-T3 | M11 | Integration validator | Validate model profiles and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M11.md` | M11-T2 | implemented |
| M12-T1 | M12 | Runtime implementer | Add simple recent-history context budget policy | `ai_assistant/agent/context.py`, `tests/test_agent_runtime.py` | M11 | implemented |
| M12-T2 | M12 | Runtime implementer | Wire configured context limit through bootstrap | `ai_assistant/bootstrap/container.py`, `tests/test_cli_app.py`, `tests/test_config.py` | M12-T1 | implemented |
| M12-T3 | M12 | Integration validator | Validate context budget and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M12.md` | M12-T2 | implemented |
| M13-T1 | M13 | Model provider implementer | Harden OpenAI-compatible request and response mappers | `ai_assistant/agent/models/openai_compatible.py`, `tests/test_openai_compatible.py` | M12 | implemented |
| M13-T2 | M13 | Model provider implementer | Verify OpenAI-compatible factory and port contract | `ai_assistant/agent/models/adapter.py`, `tests/test_model_adapter.py`, `tests/test_openai_compatible.py` | M13-T1 | implemented |
| M13-T3 | M13 | Integration validator | Validate robust OpenAI-compatible adapter and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M13.md` | M13-T2 | implemented |
| M14-T1 | M14 | Runtime implementer | Define declarative tool-call models and interpreter | `ai_assistant/agent/planner.py`, `ai_assistant/application/errors.py`, `tests/test_tools.py` | M13 | implemented |
| M14-T2 | M14 | Runtime implementer | Preserve interpreted tool plan in runtime without execution | `ai_assistant/agent/runtime.py`, `tests/test_agent_runtime.py`, `tests/test_tools.py` | M14-T1 | implemented |
| M14-T3 | M14 | Integration validator | Validate declarative tools and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M14.md` | M14-T2 | implemented |
| M15-T1 | M15 | Architect | Establish canonical domain, application, infrastructure and interfaces modules | `ai_assistant/domain/`, `ai_assistant/application/`, `ai_assistant/infrastructure/`, `ai_assistant/interfaces/`, legacy compatibility modules | M14 | implemented |
| M15-T2 | M15 | Runtime implementer | Wire bootstrap and entry points to the layered modules without changing behavior | `ai_assistant/bootstrap/container.py`, `ai_assistant/main.py`, tests | M15-T1 | implemented |
| M15-T3 | M15 | Integration validator | Validate layer dependency rules, CLI smoke and full tests | `tests/test_layering.py`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M15.md` | M15-T2 | implemented |
| M16-T1 | M16 | Test agent | Add separated CI jobs for unit, integration, contract and smoke tests | `.github/workflows/ci.yml` | M15 | implemented |
| M16-T2 | M16 | Test agent | Add isolated optional Ollama smoke job | `.github/workflows/ci.yml` | M16-T1 | implemented |
| M16-T3 | M16 | Integration validator | Validate CI commands locally where possible and prepare M16 report | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M16.md` | M16-T2 | implemented |
| M17-T1 | M17 | Documentation agent | Add developer README with setup, configuration, tests and limitations | `README.md`, `context-ai.md`, `docs/model-profiles.md` | M16 | implemented |
| M17-T2 | M17 | Documentation agent | Close ADR index and statuses for implemented Phase 1 decisions | `docs/adr/*.md`, `docs/adr/README.md` | M17-T1 | implemented |
| M17-T3 | M17 | Integration validator | Validate Phase 1 documentation and produce final report | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M17.md` | M17-T2 | implemented |
| M2.1-T1 | M2.1 | Phase 2 architect | Draft Proposed ADR-016 through ADR-025 for Phase 2 read-only tool policy | `docs/adr/ADR-016-*.md` through `docs/adr/ADR-025-*.md`, `docs/adr/README.md` | Phase 1 accepted | implemented |
| M2.1-T2 | M2.1 | Documentation agent | Update architecture with Phase 2 security policy and read-only tool contracts | `docs/architecture.md`, `docs/roadmap-phase-2.md`, `context-ai.md` | M2.1-T1 | implemented |
| M2.1-T3 | M2.1 | Security reviewer | Review proposed policy for no shell, workspace confinement, sensitive files, audit and one-round bound | read-only repository review | M2.1-T2 | implemented |
| M2.1-T4 | M2.1 | Integration validator | Validate M2.1 acceptance criteria and prepare human approval package | `.agent/reports/M2.1.md`, `.agent/human-review.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md` | M2.1-T3 | implemented |
| M2.2-T1 | M2.2 | Phase 2 architect | Add provider-neutral execution request, decision, context, result, audit and sanitized error models | `ai_assistant/domain/tools.py`, `ai_assistant/domain/__init__.py`, `ai_assistant/agent/planner.py` | M2.1 | implemented |
| M2.2-T2 | M2.2 | Test agent | Cover invalid construction and explicit IDs for tool execution domain models | `tests/test_tools.py` | M2.2-T1 | implemented |
| M2.2-T3 | M2.2 | Integration validator | Validate M2.2 acceptance criteria and produce report | `.agent/reports/M2.2.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.2-T2 | implemented |
| M2.3-T1 | M2.3 | Phase 2 architect | Define tool execution application ports without concrete adapters | `ai_assistant/application/ports/tools.py`, `ai_assistant/application/ports/__init__.py` | M2.2 | implemented |
| M2.3-T2 | M2.3 | Test agent | Prove local fakes can implement each tool execution port | `tests/test_ports_contract.py` | M2.3-T1 | implemented |
| M2.3-T3 | M2.3 | Integration validator | Validate M2.3 acceptance criteria and produce report | `.agent/reports/M2.3.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.3-T2 | implemented |
| M2.4-T1 | M2.4 | Runtime implementer | Add static read-only catalog with immutable tool metadata | `ai_assistant/application/tool_catalog.py`, `ai_assistant/domain/tools.py` | M2.3 | implemented |
| M2.4-T2 | M2.4 | Test agent | Cover exact-name lookup, unknown rejection and immutable catalog metadata | `tests/test_tool_catalog.py`, `tests/test_tools.py` | M2.4-T1 | implemented |
| M2.4-T3 | M2.4 | Integration validator | Validate M2.4 acceptance criteria and produce report | `.agent/reports/M2.4.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.4-T2 | implemented |
| M2.5-T1 | M2.5 | Runtime implementer | Add workspace configuration and normalized execution context path metadata | `ai_assistant/bootstrap/config.py`, `ai_assistant/domain/tools.py`, `tests/test_config.py`, `tests/test_tools.py` | M2.4 | implemented |
| M2.5-T2 | M2.5 | Runtime implementer | Implement workspace path policy with traversal, symlink, hidden, sensitive and file-type checks | `ai_assistant/application/path_policy.py`, `tests/test_path_policy.py` | M2.5-T1 | implemented |
| M2.5-T3 | M2.5 | Integration validator | Validate M2.5 acceptance criteria and produce report | `.agent/reports/M2.5.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.5-T2 | implemented |
| M2.6-T1 | M2.6 | Runtime implementer | Add pure deny-by-default tool policy with stable reason codes | `ai_assistant/application/tool_policy.py`, `ai_assistant/application/tool_catalog.py` | M2.5 | implemented |
| M2.6-T2 | M2.6 | Test agent | Cover unknown, malformed, over-limit, path-denied and executor-not-called policy cases | `tests/test_tool_policy.py` | M2.6-T1 | implemented |
| M2.6-T3 | M2.6 | Integration validator | Validate M2.6 acceptance criteria and produce report | `.agent/reports/M2.6.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.6-T2 | implemented |
| M2.7-T1 | M2.7 | Runtime implementer | Add reproducible fake and dry-run tool executors | `ai_assistant/application/tool_executors.py` | M2.6 | implemented |
| M2.7-T2 | M2.7 | Test agent | Cover allowed, denied, success, timeout, failure and dry-run executor behavior | `tests/test_tool_executors.py` | M2.7-T1 | implemented |
| M2.7-T3 | M2.7 | Integration validator | Validate M2.7 acceptance criteria and produce report | `.agent/reports/M2.7.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.7-T2 | implemented |
| M2.8-T1 | M2.8 | Persistence implementer | Add SQLite audit recorder with sanitized append-only schema | `ai_assistant/infrastructure/storage/sqlite_audit.py`, `ai_assistant/domain/errors.py`, `ai_assistant/domain/__init__.py`, `ai_assistant/application/errors.py` | M2.7 | implemented |
| M2.8-T2 | M2.8 | Test agent | Cover audit outcomes, redaction, failure behavior and temporary SQLite integration | `tests/test_sqlite_audit.py` | M2.8-T1 | implemented |
| M2.8-T3 | M2.8 | Integration validator | Validate M2.8 acceptance criteria and produce report | `.agent/reports/M2.8.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.8-T2 | implemented |
| M2.9-T1 | M2.9 | Persistence implementer | Add secure local read-only executor for list_directory and read_file | `ai_assistant/infrastructure/tools/local_read_only.py`, `ai_assistant/infrastructure/tools/__init__.py`, `docs/architecture.md` | M2.8 | implemented |
| M2.9-T2 | M2.9 | Test agent | Cover structured listing, bounded reads, repeated validation, binary behavior and response limits | `tests/test_local_read_only_executor.py` | M2.9-T1 | implemented |
| M2.9-T3 | M2.9 | Integration validator | Validate M2.9 acceptance criteria and produce report | `.agent/reports/M2.9.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.9-T2 | implemented |
| M2.10-T1 | M2.10 | Runtime implementer | Add ToolExecutionCoordinator deterministic execution pipeline | `ai_assistant/application/tool_coordinator.py`, `ai_assistant/domain/tools.py` | M2.9 | implemented |
| M2.10-T2 | M2.10 | Test agent | Cover coordinator order, audit, denial and executor error normalization with fakes | `tests/test_tool_coordinator.py` | M2.10-T1 | implemented |
| M2.10-T3 | M2.10 | Integration validator | Validate M2.10 with local executor and SQLite audit | `tests/test_tool_coordinator_integration.py`, `.agent/reports/M2.10.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.10-T2 | implemented |
| M2.11-T1 | M2.11 | Runtime implementer | Add optional one-round tool execution path to AgentRuntime | `ai_assistant/application/runtime.py`, `tests/test_agent_runtime.py` | M2.10 | implemented |
| M2.11-T2 | M2.11 | Test agent | Cover final answer with tool result, no-tool regression, loop bound and transactional persistence | `tests/test_agent_runtime.py` | M2.11-T1 | implemented |
| M2.11-T3 | M2.11 | Integration validator | Validate M2.11 acceptance criteria and produce report | `.agent/reports/M2.11.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.11-T2 | implemented |
| M2.12-T1 | M2.12 | Runtime implementer | Add read-only tool configuration values | `ai_assistant/bootstrap/config.py`, `tests/test_config.py` | M2.11 | implemented |
| M2.12-T2 | M2.12 | Runtime implementer | Wire configured local tool coordinator through bootstrap | `ai_assistant/bootstrap/container.py`, `ai_assistant/application/runtime.py`, `ai_assistant/application/tool_catalog.py`, `tests/test_cli_app.py`, `tests/test_agent_runtime.py`, `tests/test_tool_catalog.py`, `README.md` | M2.12-T1 | implemented |
| M2.12-T3 | M2.12 | Integration validator | Validate M2.12 acceptance criteria and produce report | `.agent/reports/M2.12.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.12-T2 | implemented |
| M2.13-T1 | M2.13 | C toolserver engineer | Replace prototype C actions with read-only list_directory and read_file | `c_toolserver/src/actions.c`, `c_toolserver/include/actions.h`, `c_toolserver/src/server.c`, `c_toolserver/README.md` | M2.12 | implemented |
| M2.13-T2 | M2.13 | Test agent | Add Python/C contract tests for read-only actions and malformed protobuf | `tests/test_c_toolserver_contract.py`, `tests/integration_c_toolserver.py`, `pytest.ini` | M2.13-T1 | implemented |
| M2.13-T3 | M2.13 | Integration validator | Validate M2.13 acceptance criteria and produce report | `.agent/reports/M2.13.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.13-T2 | implemented |
| M2.14-T1 | M2.14 | Runtime implementer | Add UnixSocketToolExecutor and protobuf request/response mapping | `ai_assistant/infrastructure/tools/unix_socket.py`, `ai_assistant/infrastructure/tools/__init__.py` | M2.13 | implemented |
| M2.14-T2 | M2.14 | Test agent | Cover missing socket, timeout, malformed response, oversized response, ID mismatch and C integration | `tests/test_unix_socket_tool_executor.py`, `tests/test_c_toolserver_contract.py` | M2.14-T1 | implemented |
| M2.14-T3 | M2.14 | Integration validator | Validate M2.14 acceptance criteria and produce report | `.agent/reports/M2.14.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.14-T2 | implemented |
| M2.15-T1 | M2.15 | Test agent | Add adversarial boundary checklist tests for policy, path, audit and runtime | `tests/test_adversarial_security.py`, existing tests read-only | M2.14 | implemented |
| M2.15-T2 | M2.15 | Test agent | Add Unix socket disconnect adversarial coverage | `tests/test_unix_socket_tool_executor.py` | M2.15-T1 | implemented |
| M2.15-T3 | M2.15 | Integration validator | Validate M2.15 acceptance criteria and produce report | `.agent/reports/M2.15.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.15-T2 | implemented |
| M2.16-T1 | M2.16 | Documentation agent | Update Phase 2 architecture, README and context documentation | `docs/architecture.md`, `README.md`, `context-ai.md` | M2.15 | implemented |
| M2.16-T2 | M2.16 | Documentation agent | Mark Phase 2 ADRs implemented and sync ADR index | `docs/adr/ADR-016-*.md` through `docs/adr/ADR-025-*.md`, `docs/adr/README.md` | M2.16-T1 | implemented |
| M2.16-T3 | M2.16 | Integration validator | Validate Phase 2 final documentation and produce report | `.agent/reports/M2.16.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md` | M2.16-T2 | implemented |
| M3.1-T1 | M3.1 | Integration validator | Reconstruct Phase 2 baseline and validate required safety guarantees | read-only repository review and targeted tests | M2.16 | implemented |
| M3.1-T2 | M3.1 | Supervisor | Record Phase 3 baseline and milestone state | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M3.1.md` | M3.1-T1 | implemented |
| M3.1-T3 | M3.1 | Security reviewer | Confirm no unresolved Phase 2 security blocker before ADR planning | read-only repository review | M3.1-T1 | implemented |
| M3.2-T1 | M3.2 | Architect | Draft Phase 3 ADR-026 through ADR-035 as Proposed decisions | `docs/adr/ADR-026-*.md` through `docs/adr/ADR-035-*.md`, `docs/adr/README.md` | M3.1 | implemented |
| M3.2-T2 | M3.2 | Security reviewer | Review Phase 3 ADR package against approval gates and Phase 2 guarantees | read-only ADR and roadmap review | M3.2-T1 | implemented |
| M3.2-T3 | M3.2 | Supervisor | Prepare M3.2 approval package and canonical state updates | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M3.2.md` | M3.2-T2 | implemented |
| M3.3-T1 | M3.3 | Runtime implementer | Add Phase 3 infrastructure-neutral domain models | `ai_assistant/domain/tools.py` | M3.2 | implemented |
| M3.3-T2 | M3.3 | Test agent | Add unit coverage for Phase 3 domain models and invalid states | `tests/test_tools.py` | M3.3-T1 | implemented |
| M3.4-T1 | M3.4 | Runtime implementer | Add in-memory confirmation service and confirmation prompt port | `ai_assistant/application/confirmation.py`, `ai_assistant/application/ports/tools.py` | M3.3 | implemented |
| M3.4-T2 | M3.4 | Test agent | Cover confirmation grant reuse, denial, revocation and audit | `tests/test_confirmation.py` | M3.4-T1 | implemented |
| M3.5-T1 | M3.5 | Runtime implementer | Add fixed test/build profile registry | `ai_assistant/application/profile_registry.py`, `ai_assistant/application/ports/tools.py` | M3.4 | implemented |
| M3.5-T2 | M3.5 | Test agent | Cover profile lookup, no shell, argv immutability and env sanitization | `tests/test_profile_registry.py` | M3.5-T1 | implemented |
| M3.6-T1 | M3.6 | Runtime implementer | Add Python-side `file_metadata` catalog, policy, path and local executor support | `ai_assistant/application/tool_catalog.py`, `ai_assistant/application/tool_policy.py`, `ai_assistant/application/path_policy.py`, `ai_assistant/infrastructure/tools/local_read_only.py` | M3.5 | implemented |
| M3.6-T2 | M3.6 | C toolserver engineer | Add C toolserver `file_metadata` action | `c_toolserver/src/actions.c`, `c_toolserver/README.md` | M3.6-T1 | implemented |
| M3.6-T3 | M3.6 | Test agent | Cover `file_metadata` Python and C behavior | relevant Python and C contract tests | M3.6-T2 | implemented |

## Task records

Use `.agent/templates/task.md` for each detailed record.

### Task M3.1-T1 — Phase 2 Baseline Validation

## Parent milestone

M3.1

## Status

implemented

## Owner role

Integration validator

## Objective

Validate that the accepted Phase 2 implementation still satisfies its required safety guarantees before Phase 3 starts.

## Scope

- Inspect Phase 2 runtime, policy, catalog, path, audit, Python executor, Unix socket executor and C toolserver.
- Run targeted Phase 2 validation tests only.

## Explicit exclusions

- No Phase 3 implementation.
- No production code changes.
- No ADR changes.

## File scope

### Writable

- None.

### Read-only

- `ai_assistant/`
- `c_toolserver/`
- `proto/`
- `tests/`
- `docs/`
- `.agent/`

### Forbidden

- Production source edits.
- Test edits.
- ADR edits.

## Dependencies

- M2.16 accepted.

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-017 Deny-by-Default Tool Policy
- ADR-018 Read-Only Tool Allowlist
- ADR-019 Workspace Confinement and Path Resolution
- ADR-020 Tool Execution Audit and Retention
- ADR-021 Tool Timeouts and Resource Limits
- ADR-022 Unix Socket Tool Executor
- ADR-023 Error and Log Redaction
- ADR-024 Bounded Single Tool Round per Turn
- ADR-025 Sensitive File Deny Policy

## Acceptance criteria

- [x] Phase 2 accepted state is confirmed.
- [x] `list_directory` and `read_file` are present and exact allowlist behavior is validated.
- [x] Deny-by-default, workspace confinement, audit, C toolserver and adversarial tests are validated.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tool_policy.py tests/test_path_policy.py tests/test_local_read_only_executor.py tests/test_sqlite_audit.py tests/test_tool_coordinator.py tests/test_tool_coordinator_integration.py tests/test_adversarial_security.py tests/test_tools.py tests/test_agent_runtime.py -q
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_c_toolserver_contract.py tests/test_unix_socket_tool_executor.py -q
```

## Risks

- C toolserver build depends on local `protobuf-c` tooling.

## Result report

- Summary: Phase 2 required safety guarantees were present in code and validated with targeted tests.
- Files changed: None.
- Tests run: targeted Python Phase 2 suite; C toolserver and Unix socket contract suite.
- Test results: 110 passed; 13 passed.
- Assumptions: `AGENTS-phase-3.md` and `docs/roadmap-phase-3.md` are user-provided untracked Phase 3 planning files.
- Remaining issues: Documentation contains historical Phase 1/2 wording to clean before or during M3.2.
- Recommended follow-up: M3.2 ADR proposal after M3.1 human review.

### Task M3.1-T2 — Record Phase 3 Baseline

## Parent milestone

M3.1

## Status

implemented

## Owner role

Supervisor

## Objective

Record the Phase 3 startup baseline, task decomposition, human-review entry and milestone report.

## Scope

- Add Phase 3 milestone state.
- Add M3.1 task records.
- Produce `.agent/reports/M3.1.md`.
- Add M3.1 to human review.

## Explicit exclusions

- No acceptance of M3.1; human review is required.
- No Phase 3 ADR proposal.
- No runtime, executor, policy or tool implementation.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M3.1.md`

### Read-only

- `docs/roadmap-phase-3.md`
- `AGENTS-phase-3.md`
- `docs/adr/`
- source and tests

### Forbidden

- Production source.
- Tests.
- ADR files.

## Dependencies

- M3.1-T1

## Applicable ADRs

- ADR-001 through ADR-025

## Acceptance criteria

- [x] Phase 3 baseline is recorded.
- [x] M3.1 is marked `implemented-awaiting-human-review`.
- [x] M3.2 remains planned and blocked by M3.1 review and ADR approval.

## Validation commands

```bash
git status --short
```

## Risks

- Accidentally marking a milestone accepted without manual review.

## Result report

- Summary: Canonical supervisor state updated for M3.1.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M3.1.md`.
- Tests run: `git status --short` after edits.
- Test results: M3.1 supervisor files modified; `AGENTS-phase-3.md` and `docs/roadmap-phase-3.md` remain untracked user files.
- Assumptions: Phase 3 docs remain untracked user files until explicitly added.
- Remaining issues: M3.2 ADRs are not created yet.
- Recommended follow-up: Human review M3.1.

### Task M3.1-T3 — Phase 2 Security Review

## Parent milestone

M3.1

## Status

implemented

## Owner role

Security reviewer

## Objective

Confirm that no unresolved Phase 2 security blocker prevents Phase 3 ADR planning.

## Scope

- Review implemented Phase 2 safety boundaries.
- Compare Phase 3 requested surface against current safeguards.

## Explicit exclusions

- No code changes.
- No approval of Phase 3 side-effecting tools.

## File scope

### Writable

- None.

### Read-only

- Repository.

### Forbidden

- All edits.

## Dependencies

- M3.1-T1

## Applicable ADRs

- ADR-016 through ADR-025

## Acceptance criteria

- [x] No unresolved Phase 2 blocker found.
- [x] Phase 3 risks and gates identified for ADR planning.

## Validation commands

```bash
rg -n "Status: Implemented" docs/adr
```

## Risks

- Phase 3 write/process tools may weaken Phase 2 guarantees if ADRs are skipped.

## Result report

- Summary: Phase 2 security baseline is viable for Phase 3 planning.
- Files changed: None.
- Tests run: ADR status inspection and targeted Phase 2 validation.
- Test results: ADR-016 through ADR-025 are Implemented; targeted validation passed.
- Assumptions: Productive Phase 3 work waits for ADR-026 through ADR-035.
- Remaining issues: None blocking M3.2 planning.
- Recommended follow-up: Draft Phase 3 ADRs.

### Task M3.2-T1 — Draft Phase 3 ADRs

## Parent milestone

M3.2

## Status

implemented

## Owner role

Architect

## Objective

Create the Phase 3 ADR package covering controlled development tools before implementation.

## Scope

- Draft ADR-026 through ADR-035 in `Proposed` status.
- Update the ADR index.
- Cover all seven approved Phase 3 tools and required policy components.

## Explicit exclusions

- Do not mark ADRs Accepted.
- Do not implement Phase 3 tools.
- Do not modify production code or tests.

## File scope

### Writable

- `docs/adr/ADR-026-*.md` through `docs/adr/ADR-035-*.md`
- `docs/adr/README.md`

### Read-only

- `docs/roadmap-phase-3.md`
- `AGENTS-phase-3.md`
- `docs/architecture.md`
- Phase 2 ADRs

### Forbidden

- Production source.
- Tests.
- Proto files.
- C toolserver source.

## Dependencies

- M3.1 accepted.

## Applicable ADRs

- ADR-001 through ADR-025

## Acceptance criteria

- [x] All seven tools are covered.
- [x] Confirmation scope is explicit.
- [x] Arbitrary command execution is prohibited.
- [x] Write atomicity is specified.
- [x] Retention policy is specified.

## Validation commands

```bash
ls docs/adr/ADR-0{26,27,28,29,30,31,32,33,34,35}-*.md
rg -n "Status: Proposed|ADR-0(26|27|28|29|30|31|32|33|34|35)" docs/adr/README.md docs/adr/ADR-0{26,27,28,29,30,31,32,33,34,35}-*.md
rg -n "file_metadata|search_text|git_status|git_diff|run_tests|build_project|write|session_id \+ workspace_id \+ permission_level|arbitrary|shell|atomic|retention|purge" docs/adr/ADR-0{26,27,28,29,30,31,32,33,34,35}-*.md
```

## Risks

- ADRs can be too broad and accidentally permit future unsafe implementation.

## Result report

- Summary: ADR-026 through ADR-035 drafted and listed in ADR index; ADR-026 through ADR-032 and ADR-034 through ADR-035 later accepted by human review.
- Files changed: `docs/adr/ADR-026-*.md` through `docs/adr/ADR-035-*.md`, `docs/adr/README.md`.
- Tests run: ADR file presence and content checks.
- Test results: ADR package validation passed.
- Assumptions: Manual approval was required before marking ADR-033 Accepted.
- Remaining issues: None for M3.2.
- Recommended follow-up: M3.3 domain models.

### Task M3.2-T2 — Review Phase 3 ADR Package

## Parent milestone

M3.2

## Status

implemented

## Owner role

Security reviewer

## Objective

Confirm the Phase 3 ADR package preserves Phase 2 safety boundaries and records required approval gates.

## Scope

- Review proposed tool allowlist, permissions, confirmation, executor, process, write, Git, search and retention policies.

## Explicit exclusions

- No code changes.
- No ADR acceptance.

## File scope

### Writable

- None.

### Read-only

- `docs/adr/ADR-026-*.md` through `docs/adr/ADR-035-*.md`
- `docs/roadmap-phase-3.md`
- `AGENTS-phase-3.md`

### Forbidden

- All edits.

## Dependencies

- M3.2-T1

## Applicable ADRs

- ADR-016 through ADR-025

## Acceptance criteria

- [x] ADR package keeps arbitrary shell and argv prohibited.
- [x] Write scope remains workspace-confined and bounded.
- [x] Confirmation grants are scoped and in-memory.
- [x] Audit purge remains unavailable to model tools.

## Validation commands

```bash
rg -n "Review trigger|requires human approval|No shell|no shell|model cannot|Purge is not exposed" docs/adr/ADR-0{26,27,28,29,30,31,32,33,34,35}-*.md
```

## Risks

- Human approval could accept an ADR with ambiguous wording.

## Result report

- Summary: No blocking security gap found in the ADR package; ADR-033 was revised to prefer fixed `rg` over `grep`.
- Files changed: None.
- Tests run: ADR safety keyword review.
- Test results: Review terms present in proposed ADRs.
- Assumptions: Implementation tasks will follow these ADRs only after approval.
- Remaining issues: None for M3.2.
- Recommended follow-up: M3.3 domain models.

### Task M3.2-T3 — Prepare ADR Approval Package

## Parent milestone

M3.2

## Status

implemented

## Owner role

Supervisor

## Objective

Record M3.2 outcome and queue ADR-026 through ADR-035 for manual approval.

## Scope

- Update roadmap state.
- Update task queue.
- Add human review entry.
- Produce milestone report.

## Explicit exclusions

- Do not mark M3.2 accepted.
- Do not mark ADRs Accepted.
- Do not start M3.3 before human approval.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M3.2.md`

### Read-only

- `docs/adr/`
- `docs/roadmap-phase-3.md`

### Forbidden

- Production source.
- Tests.

## Dependencies

- M3.2-T2

## Applicable ADRs

- ADR-001 through ADR-025
- ADR-026 through ADR-035 Proposed

## Acceptance criteria

- [x] M3.2 is recorded as implemented-awaiting-human-review.
- [x] Human review entry requests ADR approval.
- [x] M3.3 remained blocked until ADR-033 was Accepted.

## Validation commands

```bash
git status --short
rg -n "M3\\.2|ADR-026|ADR-035|awaiting-review|implemented-awaiting-human-review" .agent/roadmap-state.md .agent/human-review.md .agent/reports/M3.2.md
```

## Risks

- Accidentally treating Proposed ADRs as accepted.

## Result report

- Summary: M3.2 approval package prepared.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M3.2.md`.
- Tests run: final supervisor state checks.
- Test results: M3.2 files modified/added; ADR-026 through ADR-035 later accepted.
- Assumptions: Productive Phase 3 implementation starts only through later milestones.
- Remaining issues: None for M3.2.
- Recommended follow-up: M3.3 domain models.

### Task M3.3-T1 — Add Phase 3 Domain Models

## Parent milestone

M3.3

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add infrastructure-neutral domain types required by Phase 3 policies.

## Scope

- Extend `ToolPermission`.
- Add confirmation grant, profile ID, write mode/request/result, hash metadata and audit retention models.

## Explicit exclusions

- No policy implementation.
- No confirmation service.
- No executor, C or protobuf changes.

## File scope

### Writable

- `ai_assistant/domain/tools.py`

### Read-only

- `docs/adr/ADR-026-*.md` through `docs/adr/ADR-035-*.md`
- `tests/test_tools.py`

### Forbidden

- Infrastructure adapters.
- Runtime integration.
- C toolserver.
- Proto files.

## Dependencies

- M3.2 accepted.

## Applicable ADRs

- ADR-026 through ADR-035

## Acceptance criteria

- [x] Domain models are infrastructure-neutral.
- [x] Invalid states are rejected.
- [x] Existing Phase 2 model behavior remains compatible.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tools.py -q
```

## Risks

- Over-modeling future behavior before policies exist.

## Result report

- Summary: Added Phase 3 permission, confirmation, profile, write, hash and retention domain models.
- Files changed: `ai_assistant/domain/tools.py`, `ai_assistant/domain/__init__.py`, `ai_assistant/agent/planner.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tools.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_policy.py tests/test_tool_catalog.py tests/test_agent_runtime.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m py_compile ai_assistant/domain/tools.py ai_assistant/domain/__init__.py ai_assistant/agent/planner.py`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m "not ollama and not toolserver" -q`.
- Test results: 31 passed; 37 passed; py_compile passed; 208 passed, 7 deselected.
- Assumptions: M3.3 only defines domain types; policy behavior starts in later milestones.
- Remaining issues: None for M3.3.
- Recommended follow-up: M3.4 confirmation service after human review.

### Task M3.3-T2 — Test Phase 3 Domain Models

## Parent milestone

M3.3

## Status

implemented

## Owner role

Test agent

## Objective

Cover valid construction and invalid states for new Phase 3 domain models.

## Scope

- Add focused tests in `tests/test_tools.py`.

## Explicit exclusions

- No integration tests.
- No executor tests.

## File scope

### Writable

- `tests/test_tools.py`

### Read-only

- `ai_assistant/domain/tools.py`

### Forbidden

- Production code outside domain models.
- C toolserver.
- Proto files.

## Dependencies

- M3.3-T1

## Applicable ADRs

- ADR-027
- ADR-029
- ADR-030
- ADR-031
- ADR-034

## Acceptance criteria

- [x] New permission values are covered.
- [x] Confirmation grant scope and expiry metadata are covered.
- [x] Profile IDs reject invalid values.
- [x] Write and hash models reject invalid states.
- [x] Retention classes reject invalid days.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tools.py -q
```

## Risks

- Tests may encode implementation details instead of domain invariants.

## Result report

- Summary: Added focused unit tests for M3.3 domain model invariants.
- Files changed: `tests/test_tools.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tools.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m "not ollama and not toolserver" -q`.
- Test results: 31 passed; 208 passed, 7 deselected.
- Assumptions: Tests cover domain invariants, not later policy/executor behavior.
- Remaining issues: None for M3.3.
- Recommended follow-up: M3.4 confirmation service tests.

### Task M3.4-T1 — Add Confirmation Service

## Parent milestone

M3.4

## Status

implemented

## Owner role

Runtime implementer

## Objective

Implement in-memory confirmation grants scoped by session, workspace and permission.

## Scope

- Add a confirmation prompt port.
- Add a confirmation service with grant reuse, revocation, default-deny prompt handling and audit events.

## Explicit exclusions

- No runtime or coordinator integration.
- No CLI prompt implementation.
- No persistence.

## File scope

### Writable

- `ai_assistant/application/confirmation.py`
- `ai_assistant/application/ports/tools.py`
- `ai_assistant/application/ports/__init__.py`

### Read-only

- `ai_assistant/domain/tools.py`
- `docs/adr/ADR-027-permission-levels-and-confirmation-grants.md`

### Forbidden

- Runtime integration.
- Infrastructure adapters.
- C toolserver.
- Proto files.

## Dependencies

- M3.3 accepted.

## Applicable ADRs

- ADR-027
- ADR-020
- ADR-023

## Acceptance criteria

- [x] Same-scope reuse does not reprompt.
- [x] New session/workspace/permission prompts again.
- [x] Denial creates no grant.
- [x] Confirmation is audited.
- [x] Grants are in-memory and revocable.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_confirmation.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m py_compile ai_assistant/application/confirmation.py ai_assistant/application/ports/tools.py tests/test_confirmation.py
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m "not ollama and not toolserver" -q
```

## Risks

- Later integration must ensure denied confirmation prevents executor invocation.

## Result report

- Summary: Added in-memory confirmation service and prompt port.
- Files changed: `ai_assistant/application/confirmation.py`, `ai_assistant/application/ports/tools.py`, `ai_assistant/application/ports/__init__.py`.
- Tests run: confirmation unit tests, py_compile and core suite without Ollama/toolserver.
- Test results: 10 passed; py_compile passed; 218 passed, 7 deselected.
- Assumptions: CLI prompting and coordinator integration happen in later milestones.
- Remaining issues: None for M3.4.
- Recommended follow-up: M3.5 profile registry after human review.

### Task M3.4-T2 — Test Confirmation Service

## Parent milestone

M3.4

## Status

implemented

## Owner role

Test agent

## Objective

Cover confirmation grant reuse, denial, scope changes, revocation and audit behavior.

## Scope

- Add focused tests in `tests/test_confirmation.py`.

## Explicit exclusions

- No CLI tests.
- No executor integration tests.

## File scope

### Writable

- `tests/test_confirmation.py`

### Read-only

- `ai_assistant/application/confirmation.py`

### Forbidden

- Production code outside confirmation service.
- Runtime integration.

## Dependencies

- M3.4-T1

## Applicable ADRs

- ADR-027

## Acceptance criteria

- [x] Same-scope reuse is tested.
- [x] Scope changes are tested.
- [x] Denial and prompt errors deny by default.
- [x] Revocation is tested.
- [x] Audit events are tested.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_confirmation.py -q
```

## Risks

- Tests use fakes and do not cover CLI user input yet.

## Result report

- Summary: Added unit tests for confirmation service invariants.
- Files changed: `tests/test_confirmation.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_confirmation.py -q`.
- Test results: 10 passed.
- Assumptions: Prompt adapter behavior will be covered when CLI integration is added.
- Remaining issues: None for M3.4.
- Recommended follow-up: M3.5 profile registry tests.

### Task M3.5-T1 — Add Fixed Profile Registry

## Parent milestone

M3.5

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add a registry that maps approved profile IDs to fixed argv, timeout and sanitized environment.

## Scope

- Add immutable `ToolProfile` definitions.
- Add `StaticToolProfileRegistry`.
- Add default Phase 3 test profiles.
- Add profile registry port export.

## Explicit exclusions

- No subprocess execution.
- No model-controlled argv.
- No runtime/toolserver integration.

## File scope

### Writable

- `ai_assistant/application/profile_registry.py`
- `ai_assistant/application/ports/tools.py`
- `ai_assistant/application/ports/__init__.py`

### Read-only

- `docs/adr/ADR-029-preconfigured-test-and-build-profiles.md`
- `ai_assistant/domain/tools.py`

### Forbidden

- Runtime integration.
- C toolserver.
- Proto files.

## Dependencies

- M3.4 accepted.

## Applicable ADRs

- ADR-029
- ADR-035

## Acceptance criteria

- [x] Unknown profiles denied.
- [x] No shell profiles accepted.
- [x] Model cannot supply argv through lookup.
- [x] Environment sanitized.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_profile_registry.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m py_compile ai_assistant/application/profile_registry.py ai_assistant/application/ports/tools.py ai_assistant/application/ports/__init__.py tests/test_profile_registry.py
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m "not ollama and not toolserver" -q
```

## Risks

- Later execution code must preserve fixed argv semantics and avoid shell.

## Result report

- Summary: Added immutable static profile registry with fixed test profiles.
- Files changed: `ai_assistant/application/profile_registry.py`, `ai_assistant/application/ports/tools.py`, `ai_assistant/application/ports/__init__.py`.
- Tests run: profile registry tests, py_compile, core suite without Ollama/toolserver.
- Test results: 8 passed; py_compile passed; 226 passed, 7 deselected.
- Assumptions: Process execution is implemented later and must consume registry output directly.
- Remaining issues: None for M3.5.
- Recommended follow-up: M3.6 `file_metadata` after human review.

### Task M3.5-T2 — Test Fixed Profile Registry

## Parent milestone

M3.5

## Status

implemented

## Owner role

Test agent

## Objective

Cover approved profile lookup and rejection of unsafe profile definitions.

## Scope

- Add focused tests in `tests/test_profile_registry.py`.

## Explicit exclusions

- No subprocess or toolserver tests.

## File scope

### Writable

- `tests/test_profile_registry.py`

### Read-only

- `ai_assistant/application/profile_registry.py`

### Forbidden

- Runtime integration.
- C toolserver.

## Dependencies

- M3.5-T1

## Applicable ADRs

- ADR-029

## Acceptance criteria

- [x] Unknown profile denial covered.
- [x] Shell executable rejection covered.
- [x] Env sanitization and package installer rejection covered.
- [x] Profile immutability covered.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_profile_registry.py -q
```

## Risks

- Tests verify registry constraints, not later process cleanup or output limits.

## Result report

- Summary: Added unit tests for profile registry invariants.
- Files changed: `tests/test_profile_registry.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_profile_registry.py -q`.
- Test results: 8 passed.
- Assumptions: Process behavior will be covered in M3.10 and M3.11.
- Remaining issues: None for M3.5.
- Recommended follow-up: M3.6 `file_metadata` tests.

### Task M3.6-T1 — Add Python File Metadata Tool

## Parent milestone

M3.6

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add Python-side catalog, policy, path and local executor support for `file_metadata`.

## Scope

- Add static catalog definition.
- Validate `READ_METADATA` permission and arguments.
- Permit regular file or directory metadata targets.
- Return bounded metadata without content.

## Explicit exclusions

- No runtime permission assignment.
- No prompt changes.
- No write/process behavior.

## File scope

### Writable

- `ai_assistant/application/tool_catalog.py`
- `ai_assistant/application/tool_policy.py`
- `ai_assistant/application/path_policy.py`
- `ai_assistant/infrastructure/tools/local_read_only.py`

### Read-only

- ADR-026 through ADR-028

### Forbidden

- Runtime integration.
- Model adapters.

## Dependencies

- M3.5 accepted.

## Applicable ADRs

- ADR-026
- ADR-027
- ADR-028

## Acceptance criteria

- [x] Workspace confinement is reused.
- [x] Sensitive paths are denied by existing path policy.
- [x] No content is returned.
- [x] Errors remain sanitized through existing executor/coordinator paths.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tool_policy.py tests/test_path_policy.py tests/test_local_read_only_executor.py tests/test_unix_socket_tool_executor.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m "not ollama and not toolserver" -q
```

## Risks

- Runtime must later assign catalog permission instead of trusting model output.

## Result report

- Summary: Added Python-side `file_metadata` support.
- Files changed: catalog, policy, path policy, local executor and Unix socket permission mapping.
- Tests run: Python focused suite and core suite.
- Test results: 67 passed; 232 passed, 8 deselected.
- Assumptions: Runtime permission assignment is later scope.
- Remaining issues: None for M3.6.
- Recommended follow-up: M3.7 `search_text`.

### Task M3.6-T2 — Add C File Metadata Action

## Parent milestone

M3.6

## Status

implemented

## Owner role

C toolserver engineer

## Objective

Add a C toolserver `file_metadata` action with independent path validation and no content return.

## Scope

- Add action dispatch and metadata JSON.
- Reuse C path confinement and read-only permission validation.
- Update C toolserver README.

## Explicit exclusions

- No protobuf schema change.
- No write/process actions.

## File scope

### Writable

- `c_toolserver/src/actions.c`
- `c_toolserver/README.md`

### Read-only

- `proto/toolserver.proto`

### Forbidden

- Python runtime integration.
- Protobuf compatibility changes.

## Dependencies

- M3.6-T1

## Applicable ADRs

- ADR-028

## Acceptance criteria

- [x] C validates workspace and path before metadata.
- [x] C returns file/directory metadata without content.
- [x] C rejects unsupported/special targets safely.

## Validation commands

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib make -C c_toolserver
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_c_toolserver_contract.py -q
```

## Risks

- C JSON construction is manual and must remain bounded.

## Result report

- Summary: Added C `file_metadata` action.
- Files changed: `c_toolserver/src/actions.c`, `c_toolserver/README.md`.
- Tests run: C build and C contract tests.
- Test results: make passed with local protobuf-c environment; 8 passed.
- Assumptions: Existing protobuf request/response is sufficient.
- Remaining issues: None for M3.6.
- Recommended follow-up: M3.7 `search_text`.

### Task M3.6-T3 — Test File Metadata Paths

## Parent milestone

M3.6

## Status

implemented

## Owner role

Test agent

## Objective

Cover `file_metadata` in catalog, policy, path validation, local executor, Unix socket mapping and C contract tests.

## Scope

- Update focused Python tests.
- Update C toolserver contract tests.

## Explicit exclusions

- No Ollama tests.
- No full runtime prompt tests.

## File scope

### Writable

- `tests/test_tool_catalog.py`
- `tests/test_tool_policy.py`
- `tests/test_path_policy.py`
- `tests/test_local_read_only_executor.py`
- `tests/test_unix_socket_tool_executor.py`
- `tests/test_c_toolserver_contract.py`

### Read-only

- implementation files touched by M3.6

### Forbidden

- Model adapters.

## Dependencies

- M3.6-T2

## Applicable ADRs

- ADR-026
- ADR-027
- ADR-028

## Acceptance criteria

- [x] Python behavior is covered.
- [x] Unix socket read-metadata permission mapping is covered.
- [x] C action is covered.
- [x] No-content response is covered.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tool_policy.py tests/test_path_policy.py tests/test_local_read_only_executor.py tests/test_unix_socket_tool_executor.py -q
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_c_toolserver_contract.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m "not ollama and not toolserver" -q
```

## Risks

- Runtime integration still needs separate tests later.

## Result report

- Summary: Added focused M3.6 test coverage.
- Files changed: focused Python and C tests.
- Tests run: Python focused suite, C contract suite and core suite.
- Test results: 67 passed; 8 passed; 232 passed, 8 deselected.
- Assumptions: M3.6 tests cover implementation, not later prompt integration.
- Remaining issues: None for M3.6.
- Recommended follow-up: M3.7 `search_text` tests.

### Task M1-T1 — Remove Provider Debug Output

## Parent milestone

M1

## Status

implemented

## Owner role

Runtime implementer

## Objective

Ensure the CLI startup path does not print the selected provider as debug output.

## Scope

- Remove accidental technical stdout from `ModelAdapter.from_env()`.
- Preserve provider selection behavior.
- Keep DummyModel as the local default.

## Explicit exclusions

- No logging implementation.
- No configuration refactor.
- No provider behavior changes.

## File scope

### Writable

- `ai_assistant/agent/models/adapter.py`
- `tests/test_model_adapter.py`

### Read-only

- `ai_assistant/cli/app.py`
- `main.py`
- `docs/roadmap.md`
- `docs/architecture.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- None.

## Applicable ADRs

- ADR-006 ModelProvider port
- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] The CLI no longer prints provider debug information.
- [x] DummyModel still works by default.
- [x] Provider factory tests pass.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_model_adapter
PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.respond('hello').content)"
```

## Risks

- Accidentally changing provider defaults or environment variable behavior.

## Result report

- Summary: Removed accidental provider debug stdout from `ModelAdapter.from_env()`.
- Files changed: `ai_assistant/agent/models/adapter.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_model_adapter`; `PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.respond('hello').content)"`
- Test results: model adapter tests passed; CLI smoke exited 0 and printed only `Echo: hello`.
- Assumptions: CLI response printing in `ai_assistant/cli/app.py` is user-facing output, not debug output.
- Remaining issues: None for this task.
- Recommended follow-up: Implement logging in Milestone 8, not in M1.

### Task M1-T2 — Verify Ignore Rules

## Parent milestone

M1

## Status

implemented

## Owner role

Documentation agent

## Objective

Ensure repository ignore rules cover generated local artifacts named in Milestone 1.

## Scope

- Verify `.gitignore` ignores `__pycache__/`, `*.pyc`, `assistant.sqlite3` and equivalent local databases.
- Verify generated artifacts do not appear in normal `git status`.
- Preserve project source and docs visibility.

## Explicit exclusions

- No deletion of user data.
- No Git index removal unless artifacts are confirmed tracked and safe.
- No broad language-template ignore file.

## File scope

### Writable

- `.gitignore`

### Read-only

- repository tree
- `docs/roadmap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- None.

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] `__pycache__/` is ignored.
- [x] `*.pyc` is ignored.
- [x] `assistant.sqlite3` and equivalent local DB files are ignored.
- [x] No tracked generated artifacts require destructive removal.

## Validation commands

```bash
git status --short
git status --short --ignored
git ls-files '*__pycache__*' '*.pyc' '*.sqlite3' 'c_toolserver/build/*'
```

## Risks

- Hiding a real fixture database by using overly broad database ignore rules.

## Result report

- Summary: Verified `.gitignore` covers generated Python artifacts, local SQLite databases, C build output, virtual environments and local Codex/session files.
- Files changed: none during this supervisor run; `.gitignore` already satisfied M1 criteria.
- Tests run: `git status --short`; `git status --short --ignored`; `git ls-files '*__pycache__*' '*.pyc' '*.sqlite3' 'c_toolserver/build/*'`; `git check-ignore -v assistant.sqlite3 __pycache__/main.cpython-314.pyc ai_assistant/agent/__pycache__/runtime.cpython-314.pyc c_toolserver/build/toolserver codex .codex venv/bin/python`
- Test results: generated artifacts are ignored and no tracked generated artifacts were reported by `git ls-files`.
- Assumptions: Broad `*.db` ignore is acceptable for local assistant data until fixture databases are introduced.
- Remaining issues: Existing generated files still exist on disk but are ignored.
- Recommended follow-up: If fixture DBs are added later, use an explicit negate rule such as `!tests/fixtures/*.db`.

### Task M1-T3 — Validate Milestone 1

## Parent milestone

M1

## Status

implemented

## Owner role

Integration validator

## Objective

Map Milestone 1 acceptance criteria to evidence and prepare human review.

## Scope

- Run available validation commands.
- Record environment-blocked checks.
- Write `.agent/reports/M1.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M1 accepted.
- Do not request out-of-scope fixes for Unix socket sandbox failures.
- Do not modify roadmap priorities.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M1.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M1-T1
- M1-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] CLI output is clean.
- [x] Generated artifacts are ignored.
- [x] DummyModel still works.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_agent_runtime tests.test_model_adapter
PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.respond('hello').content)"
git status --short
git status --short --ignored
```

## Risks

- Full suite remains environment-blocked by Unix socket restrictions.

## Result report

- Summary: Validated M1 criteria, recorded environment-blocked full suite issue, and prepared human review artifacts.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M1.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests`; `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_agent_runtime tests.test_model_adapter tests.test_framing`; CLI smoke; Git ignore/status commands.
- Test results: full suite passed after permissions were adjusted; focused tests passed; CLI smoke passed.
- Assumptions: CLI response printing is expected user-facing output.
- Remaining issues: None for M1.
- Recommended follow-up: Human review should verify M1 before M2 starts.

## Dependency rules

- A task becomes `ready` only when every dependency is `implemented`.
- A task requiring human approval remains `blocked`.
- A failed task creates a corrective task; it is not silently retried.
- Canonical state updates are performed only after supervisor review.

### Task M2-T1 — Add Pytest Configuration

## Parent milestone

M2

## Status

implemented

## Owner role

Test agent

## Objective

Declare pytest as a development dependency and configure the base markers required by the roadmap.

## Scope

- Add a minimal development dependency file.
- Add pytest marker configuration.
- Keep production dependency graph unchanged.

## Explicit exclusions

- No CI.
- No Ollama tests.
- No production dependency.

## File scope

### Writable

- `requirements-dev.txt`
- `pytest.ini`

### Read-only

- `docs/roadmap.md`
- `docs/adr/ADR-013-pytest-testing-strategy.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M1 accepted.

## Applicable ADRs

- ADR-012 Minimal external dependencies
- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] pytest is declared as a development dependency.
- [x] `unit`, `integration`, `contract`, `ollama` and `smoke` markers are registered.
- [x] No production dependency file is introduced.

## Validation commands

```bash
python -m pytest --version
python -m pytest --markers
```

## Risks

- pytest may need installation in the local venv before validation.

## Result report

- Summary: Added `requirements-dev.txt` with pytest and `pytest.ini` with required markers.
- Files changed: `requirements-dev.txt`, `pytest.ini`
- Tests run: `python -m pytest --version`; `python -m pytest --markers`
- Test results: pytest 8.4.2 installed; required markers are registered.
- Assumptions: `requirements-dev.txt` is the smallest dependency declaration because the repo has no packaging config.
- Remaining issues: None for this task.
- Recommended follow-up: M16 can wire the same commands into CI.

### Task M2-T2 — Convert Tests to Pytest Style

## Parent milestone

M2

## Status

implemented

## Owner role

Test agent

## Objective

Convert the currently discovered unittest test files to pytest style without weakening assertions.

## Scope

- Convert runtime/context/SQLite tests.
- Convert model adapter tests.
- Convert framing tests.
- Convert Unix socket client tests.
- Use pytest `tmp_path` for SQLite and socket temporary paths.

## Explicit exclusions

- No production code changes.
- No Ollama tests.
- No C toolserver integration rewrite.

## File scope

### Writable

- `tests/test_agent_runtime.py`
- `tests/test_model_adapter.py`
- `tests/test_framing.py`
- `tests/test_unix_socket_client.py`

### Read-only

- `ai_assistant/`
- `tests/integration_c_toolserver.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2-T1

## Applicable ADRs

- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] Tests use pytest functions and assertions.
- [x] SQLite test uses pytest temporary path support.
- [x] Unix socket tests remain present and marked as integration.
- [x] Assertions are not weakened.

## Validation commands

```bash
python -m pytest
python -m pytest -m unit
python -m pytest -m integration
```

## Risks

- Local Unix socket permissions can affect integration tests.

## Result report

- Summary: Converted discovered unittest test files to pytest functions, assertions and markers.
- Files changed: `tests/test_agent_runtime.py`, `tests/test_model_adapter.py`, `tests/test_framing.py`, `tests/test_unix_socket_client.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`
- Test results: 12 passed; 10 unit passed; 2 integration passed.
- Assumptions: `tests/integration_c_toolserver.py` remains a manual integration script because it is not part of the currently discovered test suite and depends on the C binary.
- Remaining issues: `python -m unittest discover -s tests` now runs 0 tests, as expected after migration.
- Recommended follow-up: Convert the C integration script into a marked pytest test only when M16/CI or toolserver scope requires it.

### Task M2-T3 — Validate Pytest Migration

## Parent milestone

M2

## Status

implemented

## Owner role

Integration validator

## Objective

Verify all Milestone 2 acceptance criteria and prepare human review.

## Scope

- Run pytest validations.
- Confirm no Ollama dependency.
- Confirm SQLite uses temporary files.
- Write `.agent/reports/M2.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2 accepted.
- Do not start M3.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M2.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M2-T2

## Applicable ADRs

- ADR-012 Minimal external dependencies
- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] All existing tests pass with pytest.
- [x] Test suite does not depend on Ollama.
- [x] SQLite tests use temporary files.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
python -m pytest
python -m pytest -m unit
python -m pytest -m integration
```

## Risks

- pytest installation requires network access if not already installed.

## Result report

- Summary: Validated pytest migration and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M2.md`
- Tests run: `python -m pytest`; `python -m pytest -m unit`; `python -m pytest -m integration`; `python -m pytest --markers`
- Test results: 12 passed; 10 unit passed; 2 integration passed; required markers present.
- Assumptions: `tests/integration_c_toolserver.py` remains a manual script outside current pytest discovery.
- Remaining issues: None for M2.
- Recommended follow-up: Human review should verify M2 before M3 starts.

### Task M3-T1 — Thread Runtime Session IDs

## Parent milestone

M3

## Status

implemented

## Owner role

Runtime implementer

## Objective

Make runtime and in-memory conversation history use an explicit string session ID.

## Scope

- Define shared session ID defaults.
- Update runtime to use `session_id`.
- Update in-memory store to isolate history by session.
- Keep CLI default session as `default`.
- Allow `AI_ASSISTANT_SESSION` to select the CLI session.

## Explicit exclusions

- No interactive session management.
- No listing, renaming or deleting sessions.
- No transaction work.

## File scope

### Writable

- `ai_assistant/agent/memory.py`
- `ai_assistant/agent/runtime.py`
- `ai_assistant/cli/app.py`
- `tests/test_agent_runtime.py`

### Read-only

- `docs/adr/ADR-005-explicit-string-session-ids.md`
- `docs/roadmap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2 accepted.

## Applicable ADRs

- ADR-005 Explicit string session IDs
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] Runtime stores and reads history for its configured session.
- [x] In-memory store isolates sessions.
- [x] CLI default session is `default`.
- [x] CLI can read `AI_ASSISTANT_SESSION`.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- Breaking existing store callers during contract change.

## Result report

- Summary: Added explicit session ID support to runtime and in-memory store; CLI reads `AI_ASSISTANT_SESSION` with `default` fallback.
- Files changed: `ai_assistant/agent/memory.py`, `ai_assistant/agent/runtime.py`, `ai_assistant/cli/app.py`, `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`
- Test results: unit tests passed after implementation.
- Assumptions: Direct CLI `os.getenv` remains temporary until configuration/bootstrap milestones.
- Remaining issues: None for this task.
- Recommended follow-up: M7 should centralize this env read.

### Task M3-T2 — Persist SQLite Sessions

## Parent milestone

M3

## Status

implemented

## Owner role

Persistence implementer

## Objective

Persist and retrieve SQLite conversation messages by explicit session ID.

## Scope

- Add non-destructive SQLite migration for `session_id`.
- Add index by session/order.
- Filter history by session.
- Store messages with session IDs.
- Add tests for session isolation and persistence between store instances.

## Explicit exclusions

- No destructive migration.
- No interactive session management.
- No transactional `append_many`.

## File scope

### Writable

- `ai_assistant/storage/sqlite_memory.py`
- `tests/test_agent_runtime.py`

### Read-only

- `ai_assistant/agent/memory.py`
- `docs/adr/ADR-004-sqlite-conversation-persistence.md`
- `docs/adr/ADR-005-explicit-string-session-ids.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M3-T1

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-005 Explicit string session IDs

## Acceptance criteria

- [x] Two SQLite sessions do not share history.
- [x] Restarting a store preserves session history.
- [x] Existing message rows migrate to `default`.
- [x] Message order is preserved.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Migration bugs on existing SQLite files.

## Result report

- Summary: Added non-destructive SQLite `session_id` migration, session index, session-filtered history and tests.
- Files changed: `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest`
- Test results: full and unit pytest suites passed after implementation.
- Assumptions: Existing rows belong to the `default` session.
- Remaining issues: None for M3 scope.
- Recommended follow-up: M4 should add transactional `append_many`.

### Task M3-T3 — Validate Explicit Sessions

## Parent milestone

M3

## Status

implemented

## Owner role

Integration validator

## Objective

Verify all Milestone 3 acceptance criteria and prepare human review.

## Scope

- Run pytest validation.
- Run CLI smoke with default session.
- Run CLI smoke with `AI_ASSISTANT_SESSION`.
- Write `.agent/reports/M3.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M3 accepted.
- Do not start M4.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M3.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M3-T2

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-005 Explicit string session IDs

## Acceptance criteria

- [x] Two sessions do not share history.
- [x] CLI uses `default`.
- [x] Restarting the CLI/store preserves history.
- [x] Message order is preserved.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
AI_ASSISTANT_SESSION=alt PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.session_id)"
```

## Risks

- Existing ignored `assistant.sqlite3` may be migrated locally during CLI smoke.

## Result report

- Summary: Validated explicit session support and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M3.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`; CLI session smoke commands.
- Test results: 15 passed; 13 unit passed; 2 integration passed; CLI smoke printed `default` and `alt`.
- Assumptions: Whitespace-preserving session IDs are acceptable until interactive session management exists.
- Remaining issues: None for M3.
- Recommended follow-up: Human review should verify M3 before M4 starts.

### Task M4-T1 — Add Transactional append_many

## Parent milestone

M4

## Status

implemented

## Owner role

Persistence implementer

## Objective

Add `append_many` to conversation stores so multiple messages can be persisted atomically.

## Scope

- Add `append_many(session_id, messages)` to `ConversationMemory`.
- Implement in-memory append with all-or-nothing validation.
- Implement SQLite append in one transaction.
- Add rollback test for SQLite.

## Explicit exclusions

- No session changes.
- No WAL or advanced locking.
- No retries or nested transaction API.

## File scope

### Writable

- `ai_assistant/agent/memory.py`
- `ai_assistant/storage/sqlite_memory.py`
- `tests/test_agent_runtime.py`

### Read-only

- `docs/adr/ADR-010-transactional-turn-persistence.md`
- `docs/roadmap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M3 accepted.

## Applicable ADRs

- ADR-010 Transactional turn persistence
- ADR-004 SQLite conversation persistence

## Acceptance criteria

- [x] `append_many` exists on the store contract.
- [x] SQLite writes multiple messages in one transaction.
- [x] SQLite rollback leaves no partial turn.
- [x] In-memory store has equivalent all-or-nothing behavior.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- A rollback test may depend on SQLite constraints.

## Result report

- Summary: Added `append_many` to memory contract, in-memory store and SQLite store.
- Files changed: `ai_assistant/agent/memory.py`, `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest`
- Test results: unit and full pytest suites passed.
- Assumptions: SQLite context manager transaction semantics are sufficient for Phase 1.
- Remaining issues: Existing SQLite tables do not gain the new role `CHECK`; rollback behavior is still transactional for DB errors.
- Recommended follow-up: M9 can normalize persistence errors.

### Task M4-T2 — Runtime Uses append_many

## Parent milestone

M4

## Status

implemented

## Owner role

Runtime implementer

## Objective

Persist user and assistant messages as one complete turn.

## Scope

- Update `AgentRuntime._persist_turn()` to call `append_many`.
- Preserve existing response behavior.
- Add runtime test proving a failing second append leaves no user-only turn.

## Explicit exclusions

- No model retry behavior.
- No error hierarchy.
- No transaction implementation inside runtime.

## File scope

### Writable

- `ai_assistant/agent/runtime.py`
- `tests/test_agent_runtime.py`

### Read-only

- `ai_assistant/agent/memory.py`
- `docs/adr/ADR-010-transactional-turn-persistence.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M4-T1

## Applicable ADRs

- ADR-010 Transactional turn persistence
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] Runtime persists complete turns through `append_many`.
- [x] Runtime does not manually perform transaction logic.
- [x] A store failure cannot leave a user-only turn through runtime.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- Test fake must not encode behavior unlike the store contract.

## Result report

- Summary: Updated runtime to persist user and assistant messages through one `append_many` call.
- Files changed: `ai_assistant/agent/runtime.py`, `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`
- Test results: unit tests passed.
- Assumptions: Store owns transaction semantics; runtime only calls the contract.
- Remaining issues: None for this task.
- Recommended follow-up: None.

### Task M4-T3 — Validate Transactional Persistence

## Parent milestone

M4

## Status

implemented

## Owner role

Integration validator

## Objective

Verify all Milestone 4 acceptance criteria and prepare human review.

## Scope

- Run pytest validation.
- Review combined diff.
- Write `.agent/reports/M4.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M4 accepted.
- Do not start M5.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M4.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M4-T2

## Applicable ADRs

- ADR-010 Transactional turn persistence

## Acceptance criteria

- [x] User and assistant messages are written together.
- [x] On error, neither message is persisted.
- [x] Message order is preserved.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration
```

## Risks

- Full suite may expose unrelated integration issues.

## Result report

- Summary: Validated transactional persistence and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M4.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py -q`
- Test results: 18 passed; 16 unit passed; 2 integration passed; agent runtime tests 9 passed.
- Assumptions: Existing migrated SQLite tables may not have the new role `CHECK`, but `append_many` remains transactional for DB errors.
- Remaining issues: None for M4.
- Recommended follow-up: Human review should verify M4 before M5 starts.

### Task M5-T1 — Create Explicit Application Ports

## Parent milestone

M5

## Status

implemented

## Owner role

Architect

## Objective

Move model and memory contracts into explicit application ports.

## Scope

- Create `ai_assistant/application/ports/models.py`.
- Create `ai_assistant/application/ports/memory.py`.
- Keep compatibility imports for existing modules.

## Explicit exclusions

- No full layered repo reorganization.
- No DI framework.
- No provider behavior changes.

## File scope

### Writable

- `ai_assistant/application/`
- `ai_assistant/agent/models/provider.py`
- `ai_assistant/agent/memory.py`

### Read-only

- `docs/adr/ADR-001-ports-and-adapters.md`
- `docs/adr/ADR-006-modelprovider-port.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M4 accepted.

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] ModelProvider port lives under `application/ports`.
- [x] ConversationMemory port lives under `application/ports`.
- [x] Compatibility imports still work.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- Import cycles if ports import infrastructure.

## Result report

- Summary: Added explicit application ports for model and memory and compatibility re-exports.
- Files changed: `ai_assistant/application/__init__.py`, `ai_assistant/application/ports/__init__.py`, `ai_assistant/application/ports/models.py`, `ai_assistant/application/ports/memory.py`, `ai_assistant/agent/models/provider.py`, `ai_assistant/agent/memory.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`
- Test results: unit tests passed.
- Assumptions: `Message` remains in `agent` until M15 reorganizes domain/application layers.
- Remaining issues: None for M5 scope.
- Recommended follow-up: M15 can remove compatibility import modules if desired.

### Task M5-T2 — Update Runtime and Tests to Ports

## Parent milestone

M5

## Status

implemented

## Owner role

Runtime implementer

## Objective

Make runtime and providers depend on explicit ports, and runtime tests use fakes.

## Scope

- Update runtime imports to application ports.
- Update model providers/adapters imports to application ports.
- Add fake model/store for runtime tests.
- Preserve existing behavior.

## Explicit exclusions

- No composition root.
- No moved infrastructure packages.
- No public API removal.

## File scope

### Writable

- `ai_assistant/agent/runtime.py`
- `ai_assistant/agent/models/adapter.py`
- `ai_assistant/agent/models/dummy.py`
- `ai_assistant/agent/models/openai_compatible.py`
- `ai_assistant/agent/models/__init__.py`
- `ai_assistant/cli/app.py`
- `tests/test_agent_runtime.py`
- `tests/test_ports_contract.py`

### Read-only

- `ai_assistant/storage/sqlite_memory.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M5-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] Runtime imports model and memory ports from `application/ports`.
- [x] Runtime does not import SQLite, Ollama or OpenAI.
- [x] Runtime tests use fakes for runtime behavior.
- [x] Provider tests still pass.
- [x] Basic port contract tests exist.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Backward-compatible re-exports may hide old imports.

## Result report

- Summary: Updated runtime/providers to use application ports and split runtime tests from store implementation tests.
- Files changed: `ai_assistant/agent/runtime.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/dummy.py`, `ai_assistant/agent/models/openai_compatible.py`, `ai_assistant/agent/models/__init__.py`, `ai_assistant/cli/app.py`, `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py`, `tests/test_memory_stores.py`, `tests/test_ports_contract.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract`; import `rg` checks.
- Test results: full, unit and contract pytest suites passed; runtime import checks returned no matches.
- Assumptions: Store implementation tests can import concrete SQLite store; runtime tests use fakes.
- Remaining issues: None for M5 scope.
- Recommended follow-up: M6 should move CLI construction into a composition root.

### Task M5-T3 — Validate Explicit Ports

## Parent milestone

M5

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M5 acceptance criteria and prepare human review.

## Scope

- Run pytest validation.
- Inspect runtime imports.
- Write `.agent/reports/M5.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M5 accepted.
- Do not start M6.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M5.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M5-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] Runtime no longer imports concrete infrastructure ports.
- [x] Runtime tests use fakes.
- [x] Full pytest suite passes.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
rg -n "from ai_assistant\\.(storage|agent\\.models\\.(dummy|openai_compatible|adapter))" ai_assistant/agent/runtime.py tests/test_agent_runtime.py
```

## Risks

- Full ports/layers cleanup is deferred to M15.

## Result report

- Summary: Validated explicit ports and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M5.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`; runtime concrete-import `rg` check.
- Test results: 20 passed; 16 unit passed; 2 contract passed; 2 integration passed; runtime import check found no matches.
- Assumptions: `Message` remains under `agent` until M15 layered reorganization.
- Remaining issues: None for M5.
- Recommended follow-up: Human review should verify M5 before M6 starts.

### Task M6-T1 — Add Bootstrap Composition Root

## Parent milestone

M6

## Status

implemented

## Owner role

Architect

## Objective

Create a bootstrap composition root that owns runtime construction.

## Scope

- Add `ai_assistant/bootstrap/container.py`.
- Add `create_application()`.
- Keep dependency construction out of CLI.

## Explicit exclusions

- No DI framework.
- No config object milestone work.
- No dynamic discovery.

## File scope

### Writable

- `ai_assistant/bootstrap/`
- `ai_assistant/cli/app.py`
- `tests/test_cli_app.py`

### Read-only

- `docs/roadmap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M5 accepted.

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap

## Acceptance criteria

- [x] `create_application()` exists.
- [x] Bootstrap builds runtime dependencies.
- [x] CLI no longer imports concrete model/store adapters.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- Import cycles.

## Result report

- Summary: Added bootstrap composition root and moved runtime construction there.
- Files changed: `ai_assistant/bootstrap/__init__.py`, `ai_assistant/bootstrap/container.py`, `ai_assistant/cli/app.py`, `tests/test_cli_app.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`
- Test results: 18 unit tests passed.
- Assumptions: Full configuration object remains for M7.
- Remaining issues: None for this task.
- Recommended follow-up: M7 should replace direct env reads in bootstrap/model adapter.

### Task M6-T2 — Move CLI Runtime Construction

## Parent milestone

M6

## Status

implemented

## Owner role

Runtime implementer

## Objective

Make CLI receive an application/runtime from bootstrap while preserving `python main.py`.

## Scope

- Introduce a small CLI app object or equivalent function boundary.
- Keep `run_cli()` working.
- Add tests proving CLI app can be constructed with fakes.

## Explicit exclusions

- No config dataclass.
- No logging.
- No changed CLI commands.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/cli/app.py`
- `ai_assistant/main.py`
- `tests/test_cli_app.py`

### Read-only

- `ai_assistant/agent/runtime.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M6-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap

## Acceptance criteria

- [x] `main.py` still starts CLI.
- [x] CLI can be constructed with fake runtime.
- [x] CLI does not import concrete model/store adapters.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
```

## Risks

- Tests around `input()`/`print()` can overfit CLI internals.

## Result report

- Summary: CLI now owns input/output loop only and delegates construction to bootstrap.
- Files changed: `ai_assistant/bootstrap/container.py`, `ai_assistant/cli/app.py`, `tests/test_cli_app.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py`; CLI concrete-import `rg` check.
- Test results: full pytest passed; CLI smoke exited 0; import check found no matches.
- Assumptions: Lazy import inside `run_cli()` avoids a bootstrap/CLI import cycle.
- Remaining issues: None for this task.
- Recommended follow-up: M7 centralizes config values.

### Task M6-T3 — Validate Composition Root

## Parent milestone

M6

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M6 acceptance criteria and prepare human review.

## Scope

- Run pytest validation.
- Run CLI smoke.
- Write `.agent/reports/M6.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M6 accepted.
- Do not start M7.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M6.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M6-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap

## Acceptance criteria

- [x] `main.py` only starts the application.
- [x] CLI does not import concrete adapters.
- [x] Tests can construct CLI with fakes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "SQLiteConversationStore|ModelAdapter|ContextBuilder|ToolCallDetector" ai_assistant/cli/app.py
```

## Risks

- M7 will still need to centralize configuration object.

## Result report

- Summary: Validated the M6 composition root, CLI injection path and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M6.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py`; `rg -n "SQLiteConversationStore|ModelAdapter|ContextBuilder|ToolCallDetector" ai_assistant/cli/app.py`.
- Test results: full pytest passed with 22 tests; unit suite passed with 18 tests and 4 deselected; integration suite passed with 2 tests and 20 deselected; CLI smoke exited 0; CLI concrete-adapter import check found no matches.
- Assumptions: M7 will replace direct environment reads in the bootstrap with centralized configuration.
- Remaining issues: None for M6.
- Recommended follow-up: Human review before starting M7.

### Task M7-T1 — Add Bootstrap AppConfig

## Parent milestone

M7

## Status

implemented

## Owner role

Runtime implementer

## Objective

Create an immutable, validated configuration object loaded from environment-style mappings.

## Scope

- Define `AppConfig` in bootstrap.
- Provide defaults for M7 environment variables.
- Validate provider, timeout and context limit.
- Add focused unit tests.

## Explicit exclusions

- No `.env`, TOML, YAML or Pydantic.
- No model profiles.
- No Ollama implementation.

## File scope

### Writable

- `ai_assistant/bootstrap/config.py`
- `tests/test_config.py`

### Read-only

- `docs/roadmap.md`
- `docs/architecture.md`
- `docs/adr/ADR-007-configuration-at-bootstrap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/human-review.md`

## Dependencies

- M6 accepted

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] `AppConfig` is immutable.
- [x] Defaults are explicit and testable.
- [x] Invalid provider raises a clear error.
- [x] Invalid timeout raises a clear error.
- [x] Invalid context limit raises a clear error.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py -q
```

## Risks

- Defaults may drift from existing CLI behavior.

## Result report

- Summary: Added immutable `AppConfig` and mapping-based loader with explicit defaults and validation.
- Files changed: `ai_assistant/bootstrap/config.py`, `tests/test_config.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py -q`.
- Test results: 6 passed.
- Assumptions: `OPENAI_API_KEY` remains provider-specific secret input because the existing OpenAI-compatible adapter requires it.
- Remaining issues: None for this task.
- Recommended follow-up: Wire config through bootstrap.

### Task M7-T2 — Wire AppConfig Through Bootstrap

## Parent milestone

M7

## Status

implemented

## Owner role

Runtime implementer

## Objective

Use `AppConfig` in the composition root and remove model adapter environment reads.

## Scope

- Load configuration once in bootstrap.
- Pass config values into context, SQLite, session and model adapter construction.
- Remove `ModelAdapter.from_env()`.
- Update tests.

## Explicit exclusions

- No DI framework.
- No logging.
- No new provider implementation.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/agent/models/adapter.py`
- `tests/test_cli_app.py`
- `tests/test_model_adapter.py`

### Read-only

- `ai_assistant/cli/app.py`
- `ai_assistant/agent/runtime.py`
- `ai_assistant/storage/sqlite_memory.py`

### Forbidden

- Persistent SQLite schema

## Dependencies

- M7-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Configuration is loaded once at bootstrap.
- [x] No adapter reads environment variables.
- [x] Existing CLI startup still works.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "os\\.getenv|os\\.environ|from_env" ai_assistant | rg -v "ai_assistant/bootstrap/config.py"
```

## Risks

- Existing provider environment variable names may change.

## Result report

- Summary: Wired `AppConfig` through `create_application()` and removed `ModelAdapter.from_env()`.
- Files changed: `ai_assistant/bootstrap/container.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_cli_app.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `rg -n "os\\.getenv|os\\.environ|from_env" ai_assistant`.
- Test results: 24 passed, 4 deselected; only `ai_assistant/bootstrap/config.py` reads `os.environ`.
- Assumptions: M10 will add Ollama as a supported provider; M7 validates only providers implemented today.
- Remaining issues: None for this task.
- Recommended follow-up: Full milestone validation.

### Task M7-T3 — Validate Centralized Configuration

## Parent milestone

M7

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M7 acceptance criteria and prepare human review.

## Scope

- Run unit and full pytest validation.
- Run CLI smoke.
- Write `.agent/reports/M7.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M7 accepted.
- Do not start M8.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M7.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M7-T2

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Configuration is loaded once.
- [x] Invalid configuration errors are clear.
- [x] Runtime does not use `os.environ`.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "os\\.getenv|os\\.environ|from_env" ai_assistant | rg -v "ai_assistant/bootstrap/config.py"
```

## Risks

- Environment-dependent tests may need isolated mappings.

## Result report

- Summary: Validated M7 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M7.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py`; `rg -n "os\\.getenv|os\\.environ|from_env" ai_assistant | rg -v "ai_assistant/bootstrap/config.py"`.
- Test results: config tests passed with 6 tests; unit suite passed with 24 tests and 4 deselected; full suite passed with 28 tests; CLI smoke exited 0; no environment reads found outside bootstrap config.
- Assumptions: `AI_ASSISTANT_PROVIDER` is the canonical provider variable from the roadmap.
- Remaining issues: Future logging must not print `AppConfig` because it can include `OPENAI_API_KEY`.
- Recommended follow-up: Human review before starting M8.

### Task M8-T1 — Configure Stdlib Logging

## Parent milestone

M8

## Status

implemented

## Owner role

Runtime implementer

## Objective

Configure Python stdlib logging from bootstrap using the configured log level.

## Scope

- Add bootstrap logging setup.
- Send logs to stderr.
- Validate logging level.
- Avoid duplicate handlers.
- Hide API key from config repr.
- Add focused tests.

## Explicit exclusions

- No JSON logging.
- No rotating files.
- No telemetry.

## File scope

### Writable

- `ai_assistant/bootstrap/logging.py`
- `ai_assistant/bootstrap/container.py`
- `ai_assistant/bootstrap/config.py`
- `tests/test_logging.py`
- `tests/test_config.py`

### Read-only

- `docs/roadmap.md`
- `docs/architecture.md`

### Forbidden

- Provider behavior

## Dependencies

- M7 accepted

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Logging is configured in bootstrap.
- [x] Log level is configurable.
- [x] Logs use stderr.
- [x] Duplicate handlers are avoided.
- [x] API key is not exposed through config repr.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py tests/test_config.py -q
```

## Risks

- Pytest logging handlers can make handler-count assertions brittle.

## Result report

- Summary: Added stdlib logging setup at bootstrap, configurable level validation and API key redaction from config repr.
- Files changed: `ai_assistant/bootstrap/logging.py`, `ai_assistant/bootstrap/container.py`, `ai_assistant/bootstrap/config.py`, `tests/test_logging.py`, `tests/test_config.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py tests/test_config.py -q`.
- Test results: 9 passed.
- Assumptions: Existing pytest logging handlers are acceptable; `basicConfig` avoids adding duplicate handlers when handlers already exist.
- Remaining issues: None for this task.
- Recommended follow-up: Add safe runtime and adapter log events.

### Task M8-T2 — Add Safe Runtime and Adapter Events

## Parent milestone

M8

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add diagnostic logs for runtime turns and model adapter calls without logging message content or secrets.

## Scope

- Log provider/model selection.
- Log runtime request lifecycle.
- Log model request duration.
- Log adapter errors without request/response bodies.
- Add tests that sensitive content is absent from logs.

## Explicit exclusions

- No typed errors.
- No retry policy.
- No logging of prompts, user input or assistant output.

## File scope

### Writable

- `ai_assistant/agent/runtime.py`
- `ai_assistant/agent/models/adapter.py`
- `ai_assistant/agent/models/openai_compatible.py`
- `tests/test_logging.py`

### Read-only

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/bootstrap/container.py`
- `ai_assistant/cli/app.py`

### Forbidden

- Persistent storage schema

## Dependencies

- M8-T1

## Applicable ADRs

- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] Provider and model are logged.
- [x] Request duration is logged.
- [x] Errors are logged without message content.
- [x] CLI stdout remains assistant-only.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py -q
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "print\\(" ai_assistant | rg -v "ai_assistant/cli/app.py"
```

## Risks

- Exception details can contain provider response bodies if logged directly.

## Result report

- Summary: Added provider/model logs, runtime lifecycle logs and OpenAI-compatible request duration/error logs without prompt, response, API key or body content.
- Files changed: `ai_assistant/agent/runtime.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/openai_compatible.py`, `tests/test_logging.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py > /tmp/blacksmith-m8-stdout.txt 2> /tmp/blacksmith-m8-stderr.txt`; `rg -n "print\\(" ai_assistant | rg -v "ai_assistant/cli/app.py"`.
- Test results: logging tests passed with 5 tests; unit suite passed with 30 tests and 4 deselected; CLI stdout contained only prompt; technical print check found no matches outside CLI response printing.
- Assumptions: Provider/model names are operational metadata, not secrets.
- Remaining issues: stderr includes INFO provider selection at default log level.
- Recommended follow-up: Full milestone validation.

### Task M8-T3 — Validate Basic Logging

## Parent milestone

M8

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M8 acceptance criteria and prepare human review.

## Scope

- Run unit and full pytest validation.
- Run CLI smoke.
- Check technical prints.
- Write `.agent/reports/M8.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M8 accepted.
- Do not start M9.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M8.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M8-T2

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] No technical prints exist.
- [x] Log level is configurable.
- [x] Secrets are not logged.
- [x] CLI stdout remains clean.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "print\\(" ai_assistant | rg -v "ai_assistant/cli/app.py"
```

## Risks

- Smoke output can include stderr logs even when stdout is clean.

## Result report

- Summary: Validated M8 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M8.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py tests/test_config.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py > /tmp/blacksmith-m8-stdout.txt 2> /tmp/blacksmith-m8-stderr.txt`; `rg -n "print\\(" ai_assistant | rg -v "ai_assistant/cli/app.py"`.
- Test results: focused logging/config tests passed with 9 tests; unit suite passed with 30 tests and 4 deselected; full suite passed with 34 tests; CLI smoke exited 0 with clean stdout and logs on stderr; no technical prints found.
- Assumptions: Session IDs are operational identifiers and should remain non-secret.
- Remaining issues: M9 should sanitize public/provider error paths that still include HTTP response bodies in raised exceptions.
- Recommended follow-up: Human review before starting M9.

### Task M9-T1 — Define Internal Error Hierarchy

## Parent milestone

M9

## Status

implemented

## Owner role

Runtime implementer

## Objective

Define typed internal errors and map validation failures to them.

## Scope

- Add minimal error hierarchy.
- Map config, logging level, provider selection, message and session validation.
- Add focused tests.

## Explicit exclusions

- No broad domain package reorganization.
- No new metadata fields.

## File scope

### Writable

- `ai_assistant/application/errors.py`
- `ai_assistant/agent/message.py`
- `ai_assistant/application/ports/memory.py`
- `ai_assistant/bootstrap/config.py`
- `ai_assistant/bootstrap/logging.py`
- `ai_assistant/agent/models/adapter.py`
- `tests/test_errors.py`
- `tests/test_config.py`
- `tests/test_model_adapter.py`
- `tests/test_memory_stores.py`

### Read-only

- `docs/roadmap.md`
- `docs/architecture.md`

### Forbidden

- Future domain reorganization

## Dependencies

- M8 accepted

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Error hierarchy exists.
- [x] Configuration errors are typed.
- [x] Invalid messages are typed.
- [x] Invalid sessions are typed.
- [x] Provider selection errors are typed.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_errors.py tests/test_config.py tests/test_model_adapter.py tests/test_memory_stores.py -q
```

## Risks

- Tests that expected built-in exceptions need contract updates.

## Result report

- Summary: Added typed internal errors and mapped validation paths.
- Files changed: `ai_assistant/application/errors.py`, `ai_assistant/agent/message.py`, `ai_assistant/application/ports/memory.py`, `ai_assistant/bootstrap/config.py`, `ai_assistant/bootstrap/logging.py`, `ai_assistant/agent/models/adapter.py`, related tests.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_errors.py tests/test_config.py tests/test_model_adapter.py tests/test_memory_stores.py tests/test_logging.py -q`.
- Test results: 28 passed after updating logging-level expectation.
- Assumptions: `application/errors.py` is the current minimal shared location until M15 reorganization.
- Remaining issues: None for this task.
- Recommended follow-up: Map infrastructure failures and CLI output.

### Task M9-T2 — Map Infrastructure Failures and CLI Messages

## Parent milestone

M9

## Status

implemented

## Owner role

Runtime implementer

## Objective

Translate SQLite and model provider failures to typed errors and make CLI handle expected errors without traceback.

## Scope

- Wrap SQLite failures as `ConversationStoreError`.
- Map HTTP 404, URL failures, timeout, invalid JSON and missing text in OpenAI-compatible provider.
- Catch `AssistantError` in CLI and print a readable stderr message.
- Add tests for typed provider errors and CLI translation.

## Explicit exclusions

- No retry policy.
- No user-facing error catalog.
- No Ollama adapter.

## File scope

### Writable

- `ai_assistant/storage/sqlite_memory.py`
- `ai_assistant/agent/models/openai_compatible.py`
- `ai_assistant/cli/app.py`
- `tests/test_errors.py`
- `tests/test_logging.py`
- `tests/test_cli_app.py`

### Read-only

- `ai_assistant/agent/runtime.py`
- `ai_assistant/bootstrap/logging.py`

### Forbidden

- Persistent schema changes

## Dependencies

- M9-T1

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] SQLite errors are mapped.
- [x] HTTP errors are mapped.
- [x] JSON/protocol errors are mapped.
- [x] CLI expected errors avoid traceback.
- [x] Technical error type is logged.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_errors.py tests/test_logging.py tests/test_cli_app.py tests/test_memory_stores.py -q
```

## Risks

- Unexpected exceptions still surface as tracebacks; that remains useful for non-typed bugs.

## Result report

- Summary: Mapped SQLite and OpenAI-compatible failures to typed errors and added CLI translation for expected assistant errors.
- Files changed: `ai_assistant/storage/sqlite_memory.py`, `ai_assistant/agent/models/openai_compatible.py`, `ai_assistant/cli/app.py`, related tests.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; CLI smoke.
- Test results: unit passed with 35 tests and 4 deselected; contract passed with 2 tests and 37 deselected; full suite passed with 39 tests; CLI smoke exited 0.
- Assumptions: Only `AssistantError` subclasses are expected user-readable errors.
- Remaining issues: None for this task.
- Recommended follow-up: Full milestone validation and review.

### Task M9-T3 — Validate Typed Errors

## Parent milestone

M9

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M9 acceptance criteria and prepare human review.

## Scope

- Run unit, contract and full pytest validation.
- Run CLI smoke.
- Write `.agent/reports/M9.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M9 accepted.
- Do not start M10.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M9.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M9-T2

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] CLI does not show traceback for expected errors.
- [x] Tests validate error types.
- [x] Technical errors remain in logs.
- [x] Unit and contract suites pass.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
```

## Risks

- Over-sanitizing errors can hide provider diagnostics.

## Result report

- Summary: Validated M9 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M9.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_errors.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py`.
- Test results: error tests passed with 6 tests; unit suite passed with 36 tests and 4 deselected; contract suite passed with 2 tests and 38 deselected; full suite passed with 40 tests; CLI smoke exited 0.
- Assumptions: Unexpected non-`AssistantError` exceptions should still fail loudly.
- Remaining issues: None for M9 after independent review findings were corrected.
- Recommended follow-up: Human review before starting M10.

### Task M10-T1 — Add Native Ollama Chat Provider

## Parent milestone

M10

## Status

implemented

## Owner role

Model provider implementer

## Objective

Implement the native Ollama `/api/chat` provider using stdlib HTTP.

## Scope

- Build native Ollama request payload.
- Send `stream=false`.
- Use `urllib.request`.
- Apply timeout.
- Parse `message.content`.
- Map connection, timeout, model-not-found and protocol errors.
- Log request duration.
- Add simulated unit tests.

## Explicit exclusions

- No streaming.
- No SDK.
- No daemon management.
- No model downloads.

## File scope

### Writable

- `ai_assistant/agent/models/ollama.py`
- `tests/test_ollama_model.py`

### Read-only

- `ai_assistant/agent/models/openai_compatible.py`
- `ai_assistant/application/errors.py`
- `docs/adr/ADR-011-native-ollama-adapter.md`
- `docs/adr/ADR-014-non-streaming-calls-in-phase-1.md`

### Forbidden

- OpenAI-compatible provider behavior

## Dependencies

- M9 accepted

## Applicable ADRs

- ADR-011 Native Ollama API adapter
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] Request uses `/api/chat`.
- [x] Request sends `stream=false`.
- [x] Messages are translated to Ollama format.
- [x] Response returns normalized assistant `Message`.
- [x] Typed errors are raised for unavailable service, missing model and bad protocol.
- [x] Unit tests do not require real Ollama.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py -q
```

## Risks

- Ollama error body formats may vary by version.

## Result report

- Summary: Added native `OllamaModelProvider` with stdlib HTTP, non-streaming requests, typed errors and duration logging.
- Files changed: `ai_assistant/agent/models/ollama.py`, `tests/test_ollama_model.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py -q`.
- Test results: 7 passed.
- Assumptions: HTTP 404 is sufficient for missing-model mapping in M10.
- Remaining issues: Real Ollama validation is optional and environment-dependent.
- Recommended follow-up: Wire provider through configuration and adapter factory.

### Task M10-T2 — Wire Ollama Provider

## Parent milestone

M10

## Status

implemented

## Owner role

Model provider implementer

## Objective

Expose Ollama through configuration and the model adapter factory.

## Scope

- Allow `AI_ASSISTANT_PROVIDER=ollama`.
- Default Ollama base URL to `http://localhost:11434`.
- Register provider in `ModelAdapter`.
- Export provider from model package.
- Add adapter/config tests and simulated CLI path.
- Add optional real Ollama smoke test.

## Explicit exclusions

- No model profiles.
- No default model recommendations.
- No real Ollama requirement in unit tests.

## File scope

### Writable

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/agent/models/adapter.py`
- `ai_assistant/agent/models/__init__.py`
- `tests/test_config.py`
- `tests/test_model_adapter.py`
- `tests/test_ollama_model.py`
- `tests/test_ollama_smoke.py`

### Read-only

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/cli/app.py`

### Forbidden

- Logging policy changes

## Dependencies

- M10-T1

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-011 Native Ollama API adapter
- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] Provider can be selected by config.
- [x] Model remains configurable.
- [x] CLI responds with simulated Ollama.
- [x] Optional real-Ollama test is separable from default suite.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py tests/test_model_adapter.py tests/test_config.py -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q
```

## Risks

- `AI_ASSISTANT_MODEL` is required for useful real Ollama execution.

## Result report

- Summary: Wired Ollama into config and adapter selection, added simulated CLI coverage and optional real smoke test.
- Files changed: `ai_assistant/bootstrap/config.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/__init__.py`, related tests.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py tests/test_model_adapter.py tests/test_config.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q`.
- Test results: focused tests passed with 19 tests before CLI coverage and 7 Ollama-provider tests after; optional Ollama suite skipped 1 test because no `AI_ASSISTANT_MODEL` was set.
- Assumptions: M11 owns hardware/model profile defaults.
- Remaining issues: Real Ollama was not exercised in this environment.
- Recommended follow-up: Full milestone validation.

### Task M10-T3 — Validate Native Ollama Adapter

## Parent milestone

M10

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M10 acceptance criteria and prepare human review.

## Scope

- Run unit, contract, ollama-marker and full pytest validation.
- Run CLI smoke.
- Write `.agent/reports/M10.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M10 accepted.
- Do not start M11.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M10.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M10-T2

## Applicable ADRs

- ADR-011 Native Ollama API adapter
- ADR-013 Pytest testing strategy
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] CLI responds with Ollama.
- [x] Model is selected by variable/config.
- [x] Service-down failures raise typed error.
- [x] Missing-model failures raise typed error.
- [x] Unit tests do not require Ollama.
- [x] Unit and contract suites pass.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
```

## Risks

- Real Ollama validation depends on local daemon and installed model.

## Result report

- Summary: Validated M10 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M10.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; CLI smoke.
- Test results: Ollama provider tests passed with 8 tests; unit suite passed with 45 tests and 5 deselected; contract suite passed with 2 tests and 48 deselected; optional Ollama suite skipped 1 test because no `AI_ASSISTANT_MODEL` was set; full suite passed with 50 tests and 1 skipped; CLI smoke exited 0.
- Assumptions: Real Ollama validation remains environment-dependent and optional.
- Remaining issues: Real Ollama smoke was not executed in this environment.
- Recommended follow-up: Human review before starting M11.

### Task M11-T1 — Document Model Profiles

## Parent milestone

M11

## Status

implemented

## Owner role

Documentation agent

## Objective

Document recommended local model profiles for the reference 6 GB VRAM / 64 GB RAM machine.

## Scope

- Document development, validation and evaluation profiles.
- Document context recommendations.
- Add evaluation/smoke guidance.
- Link architecture to the profile guide.

## Explicit exclusions

- No automatic GPU detection.
- No downloads.
- No benchmark framework.

## File scope

### Writable

- `docs/model-profiles.md`
- `docs/architecture.md`

### Read-only

- `docs/roadmap.md`
- `docs/adr/ADR-015-configurable-model-profiles.md`

### Forbidden

- Runtime behavior

## Dependencies

- M10 accepted

## Applicable ADRs

- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Profiles are documented.
- [x] Development model target is documented.
- [x] Context 4096 is documented.
- [x] Evaluation context 8192 guidance is documented.

## Validation commands

```bash
rg -n "development|validation|evaluation|AI_ASSISTANT_CONTEXT_LIMIT|8192" docs/model-profiles.md docs/architecture.md
```

## Risks

- Ollama tags may differ by registry and quantization.

## Result report

- Summary: Added model profile guide and architecture link.
- Files changed: `docs/model-profiles.md`, `docs/architecture.md`.
- Tests run: `rg -n "development|validation|evaluation|AI_ASSISTANT_CONTEXT_LIMIT|8192" docs/model-profiles.md docs/architecture.md`.
- Test results: profile and context entries found.
- Assumptions: Exact Ollama tags remain operator-selected because tags vary.
- Remaining issues: None for this task.
- Recommended follow-up: Validate config/smoke behavior.

### Task M11-T2 — Keep Model and Context Configurable

## Parent milestone

M11

## Status

implemented

## Owner role

Runtime implementer

## Objective

Avoid a hardcoded model default and prove context/model are selected through config.

## Scope

- Remove the hardcoded model default from config and adapter config.
- Verify 8192 context can be configured.
- Add smoke test for configured model/context and active model logging.

## Explicit exclusions

- No context trimming.
- No model profile resolver.
- No automatic provider selection.

## File scope

### Writable

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/agent/models/adapter.py`
- `tests/test_config.py`
- `tests/test_smoke.py`

### Read-only

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/agent/runtime.py`

### Forbidden

- Provider HTTP behavior

## Dependencies

- M11-T1

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Runtime config does not hardcode a concrete model.
- [x] Model is environment/config selected.
- [x] Context 4096 remains default.
- [x] Context 8192 is accepted by configuration.
- [x] Active provider/model is logged.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py tests/test_smoke.py tests/test_model_adapter.py -q
```

## Risks

- Operators using real providers must set `AI_ASSISTANT_MODEL`.

## Result report

- Summary: Removed concrete model default and added config/smoke tests for model/context selection.
- Files changed: `ai_assistant/bootstrap/config.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_config.py`, `tests/test_smoke.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py tests/test_smoke.py tests/test_model_adapter.py -q`.
- Test results: 16 passed.
- Assumptions: Dummy provider remains the no-model local default; real providers require configured model.
- Remaining issues: None for this task.
- Recommended follow-up: Full M11 validation.

### Task M11-T3 — Validate Model Profiles

## Parent milestone

M11

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M11 acceptance criteria and prepare human review.

## Scope

- Run smoke tests.
- Run full pytest validation.
- Write `.agent/reports/M11.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M11 accepted.
- Do not start M12.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M11.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M11-T2

## Applicable ADRs

- ADR-013 Pytest testing strategy
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Project does not fix a concrete model in runtime config.
- [x] Documented default profile is suitable for reference hardware.
- [x] Context is configurable.
- [x] Smoke suite passes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m smoke
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Exact Ollama tags may differ locally.

## Result report

- Summary: Validated M11 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M11.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m smoke -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; profile documentation `rg`; hardcoded model default `rg`.
- Test results: smoke passed with 1 test and 52 deselected; full suite passed with 53 tests; profile documentation entries found; no `gpt-5` runtime config default found.
- Assumptions: Exact Ollama model tags are operator-selected and may differ locally.
- Remaining issues: Real Ollama smoke remains optional and environment-dependent.
- Recommended follow-up: Human review before starting M12.

### Task M12-T1 — Add Recent-History Context Budget

## Parent milestone

M12

## Status

implemented

## Owner role

Runtime implementer

## Objective

Limit history sent to the model with a simple configurable budget.

## Scope

- Add `context_limit` to `ContextBuilder`.
- Preserve system prompt.
- Preserve current user input.
- Select recent history in original order while budget remains.
- Add order and truncation tests.

## Explicit exclusions

- No tokenizer.
- No summaries.
- No embeddings.

## File scope

### Writable

- `ai_assistant/agent/context.py`
- `tests/test_agent_runtime.py`

### Read-only

- `docs/roadmap.md`
- `docs/architecture.md`

### Forbidden

- Persistence behavior

## Dependencies

- M11 accepted

## Applicable ADRs

- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Context does not grow without limit.
- [x] System prompt is always preserved.
- [x] Current input is always preserved.
- [x] Recent history has priority.
- [x] Message order is preserved.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py -q
```

## Risks

- Character count is only an approximation of token usage.

## Result report

- Summary: Added approximate character-budget context selection.
- Files changed: `ai_assistant/agent/context.py`, `tests/test_agent_runtime.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py tests/test_cli_app.py -q`.
- Test results: 8 passed.
- Assumptions: Approximate content-length budget is acceptable until provider tokenizers exist.
- Remaining issues: None for this task.
- Recommended follow-up: Wire config limit through bootstrap.

### Task M12-T2 — Wire Configured Context Limit

## Parent milestone

M12

## Status

implemented

## Owner role

Runtime implementer

## Objective

Pass `AppConfig.context_limit` into `ContextBuilder`.

## Scope

- Wire configured context limit in bootstrap.
- Add bootstrap wiring test.

## Explicit exclusions

- No CLI flags.
- No runtime mutation.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `tests/test_cli_app.py`
- `tests/test_config.py`

### Read-only

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/agent/runtime.py`

### Forbidden

- Model provider behavior

## Dependencies

- M12-T1

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Configured context limit reaches `ContextBuilder`.
- [x] Existing config validation remains intact.
- [x] CLI bootstrap still works.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_cli_app.py tests/test_config.py -q
```

## Risks

- Test reaches through `CliApplication._runtime` because there is no public diagnostic surface yet.

## Result report

- Summary: Wired `AppConfig.context_limit` into `ContextBuilder`.
- Files changed: `ai_assistant/bootstrap/container.py`, `tests/test_cli_app.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py tests/test_cli_app.py -q`.
- Test results: 8 passed.
- Assumptions: Private runtime inspection in test is acceptable for narrow bootstrap wiring.
- Remaining issues: None for this task.
- Recommended follow-up: Full M12 validation.

### Task M12-T3 — Validate Context Budget

## Parent milestone

M12

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M12 acceptance criteria and prepare human review.

## Scope

- Run unit and full pytest validation.
- Write `.agent/reports/M12.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M12 accepted.
- Do not start M13.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M12.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M12-T2

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Context does not grow without limit.
- [x] Current message is always preserved.
- [x] Recent history has priority.
- [x] Unit suite passes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Character count can differ from provider token counts.

## Result report

- Summary: Validated M12 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M12.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; CLI smoke with `python main.py`.
- Test results: unit suite passed with 50 tests and 6 deselected; full suite passed with 56 tests; CLI smoke exited 0 and showed configured provider/model in stderr logs.
- Assumptions: Character-count budget is the intended simple policy for M12.
- Remaining issues: Token-accurate budgeting remains out of scope.
- Recommended follow-up: Human review before starting M13.

### Task M13-T1 — Harden OpenAI-Compatible Mappers

## Parent milestone

M13

## Status

implemented

## Owner role

Model provider implementer

## Objective

Strengthen request and response contracts for the OpenAI-compatible provider.

## Scope

- Verify Responses API payload mapping.
- Verify `/responses` request path and timeout.
- Validate response JSON is an object.
- Verify direct and nested response text extraction.
- Preserve typed protocol errors.

## Explicit exclusions

- No SDK.
- No streaming.
- No tools.
- No multimodal support.

## File scope

### Writable

- `ai_assistant/agent/models/openai_compatible.py`
- `tests/test_openai_compatible.py`

### Read-only

- `ai_assistant/agent/models/ollama.py`
- `docs/roadmap.md`
- `docs/adr/ADR-014-non-streaming-calls-in-phase-1.md`

### Forbidden

- Ollama provider behavior

## Dependencies

- M12 accepted

## Applicable ADRs

- ADR-006 ModelProvider port
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] Request mapper is tested.
- [x] Response mapper is tested.
- [x] Timeout is passed to HTTP call.
- [x] Invalid provider JSON maps to typed protocol error.
- [x] Unit/contract tests use no real network.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_openai_compatible.py -q
```

## Risks

- Compatible providers may vary in exact response shapes.

## Result report

- Summary: Added simulated contract coverage and object JSON validation for OpenAI-compatible responses.
- Files changed: `ai_assistant/agent/models/openai_compatible.py`, `tests/test_openai_compatible.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_openai_compatible.py -q`.
- Test results: 8 passed.
- Assumptions: Responses API shape remains the Phase 1 OpenAI-compatible contract.
- Remaining issues: No real provider integration test in M13.
- Recommended follow-up: Verify factory and full contracts.

### Task M13-T2 — Verify Factory and Port Contract

## Parent milestone

M13

## Status

implemented

## Owner role

Model provider implementer

## Objective

Confirm OpenAI-compatible provider remains separate from Ollama and implements the shared port.

## Scope

- Verify `OpenAICompatibleModel` implements `ModelProvider`.
- Verify `openai` factory path.
- Verify `chatgpt` alias path.
- Preserve Ollama factory separation.

## Explicit exclusions

- No provider auto-detection.
- No provider renaming.

## File scope

### Writable

- `ai_assistant/agent/models/adapter.py`
- `tests/test_model_adapter.py`
- `tests/test_openai_compatible.py`

### Read-only

- `ai_assistant/agent/models/ollama.py`
- `ai_assistant/bootstrap/config.py`

### Forbidden

- Configuration variable changes

## Dependencies

- M13-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-006 ModelProvider port
- ADR-011 Native Ollama API adapter

## Acceptance criteria

- [x] Ollama and OpenAI-compatible are separate adapters.
- [x] Both implement the same port.
- [x] Factory selects OpenAI-compatible provider.
- [x] Factory tests use no real network.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_model_adapter.py tests/test_openai_compatible.py -q
```

## Risks

- Test reaches into adapter internals to verify concrete provider selection.

## Result report

- Summary: Added factory coverage for `chatgpt` alias and port contract coverage for OpenAI-compatible provider.
- Files changed: `tests/test_model_adapter.py`, `tests/test_openai_compatible.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_model_adapter.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`.
- Test results: model adapter tests passed with 7 tests; contract suite passed with 10 tests and 54 deselected.
- Assumptions: Internal provider inspection is acceptable for narrow factory verification.
- Remaining issues: None for this task.
- Recommended follow-up: Full M13 validation.

### Task M13-T3 — Validate OpenAI-Compatible Adapter

## Parent milestone

M13

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M13 acceptance criteria and prepare human review.

## Scope

- Run contract and full pytest validation.
- Write `.agent/reports/M13.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M13 accepted.
- Do not start M14.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M13.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M13-T2

## Applicable ADRs

- ADR-006 ModelProvider port
- ADR-011 Native Ollama API adapter
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] Ollama and OpenAI-compatible are separate adapters.
- [x] Both implement the same port.
- [x] Unit/contract tests do not use real network.
- [x] Contract suite passes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Future compatible providers may need different response mapping.

## Result report

- Summary: Validated M13 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M13.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_openai_compatible.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_model_adapter.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`.
- Test results: OpenAI-compatible tests passed with 8 tests; model adapter tests passed with 7 tests; contract suite passed with 10 tests and 55 deselected; full suite passed with 65 tests.
- Assumptions: Responses API shape remains the OpenAI-compatible Phase 1 contract.
- Remaining issues: No real OpenAI-compatible provider integration test in M13.
- Recommended follow-up: Human review before starting M14.

### Task M14-T1 — Define Declarative Tool Models

## Parent milestone

M14

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add typed declarative tool definitions, calls and interpretation results.

## Scope

- Define `ToolDefinition`.
- Define `ToolCall`.
- Define typed `ToolCallPlan`.
- Add `ToolCallInterpreter`.
- Validate explicit `tool_call` JSON.
- Add tests.

## Explicit exclusions

- No executor.
- No shell.
- No socket calls.
- No multiple-tool planner.

## File scope

### Writable

- `ai_assistant/agent/planner.py`
- `ai_assistant/application/errors.py`
- `tests/test_tools.py`

### Read-only

- `docs/roadmap.md`
- `docs/adr/ADR-008-declarative-tools-only-in-phase-1.md`

### Forbidden

- Tool execution adapters

## Dependencies

- M13 accepted

## Applicable ADRs

- ADR-008 Declarative tools only in Phase 1

## Acceptance criteria

- [x] `ToolDefinition` exists.
- [x] `ToolCall` exists.
- [x] Interpreter returns typed plan.
- [x] Invalid explicit tool call raises typed error.
- [x] Plain text is ignored.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_tools.py -q
```

## Risks

- JSON format can become provider-coupled if expanded too early.

## Result report

- Summary: Added declarative tool-call dataclasses and JSON interpreter.
- Files changed: `ai_assistant/agent/planner.py`, `ai_assistant/application/errors.py`, `tests/test_tools.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_tools.py tests/test_agent_runtime.py -q`.
- Test results: 12 passed.
- Assumptions: Phase 1 supports one explicit `tool_call` object per assistant message.
- Remaining issues: No catalog or schema validation beyond basic object shape.
- Recommended follow-up: Preserve interpreted plan in runtime.

### Task M14-T2 — Preserve Tool Plan in Runtime

## Parent milestone

M14

## Status

implemented

## Owner role

Runtime implementer

## Objective

Let runtime identify and retain a typed tool-call plan without executing tools.

## Scope

- Store last interpreted tool plan on runtime.
- Keep response behavior unchanged.
- Add runtime test.

## Explicit exclusions

- No execution.
- No CLI rendering changes.
- No tool result persistence.

## File scope

### Writable

- `ai_assistant/agent/runtime.py`
- `tests/test_agent_runtime.py`
- `tests/test_tools.py`

### Read-only

- `ai_assistant/agent/planner.py`
- `ai_assistant/cli/app.py`

### Forbidden

- Shell/socket execution

## Dependencies

- M14-T1

## Applicable ADRs

- ADR-008 Declarative tools only in Phase 1

## Acceptance criteria

- [x] Runtime can identify a tool call.
- [x] Runtime keeps typed plan.
- [x] No tool is executed.
- [x] Existing response behavior remains unchanged.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py tests/test_tools.py -q
```

## Risks

- Public runtime response still returns `Message`; plan is stored on runtime state.

## Result report

- Summary: Runtime now stores `last_tool_plan` after assistant response detection.
- Files changed: `ai_assistant/agent/runtime.py`, `tests/test_agent_runtime.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_tools.py tests/test_agent_runtime.py -q`.
- Test results: 12 passed.
- Assumptions: `last_tool_plan` is enough for Phase 1's typed plan requirement.
- Remaining issues: No first-class turn response object yet.
- Recommended follow-up: Full validation.

### Task M14-T3 — Validate Declarative Tools

## Parent milestone

M14

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M14 acceptance criteria and prepare human review.

## Scope

- Run unit and full pytest validation.
- Verify no executor/shell was introduced.
- Write `.agent/reports/M14.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M14 accepted.
- Do not start M15.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M14.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M14-T2

## Applicable ADRs

- ADR-008 Declarative tools only in Phase 1
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Runtime can identify a tool call.
- [x] No tool is executed.
- [x] Response path contains typed plan.
- [x] Unit suite passes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest
rg -n "ToolExecutor|execute\\(|subprocess|os\\.system|shell" ai_assistant/agent ai_assistant/tools tests/test_tools.py tests/test_agent_runtime.py
```

## Risks

- `last_tool_plan` is stateful and may be replaced by a richer turn response later.

## Result report

- Summary: Validated declarative tool interpretation without execution.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M14.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; executor/shell `rg`.
- Test results: unit suite passed with 58 tests and 14 deselected; full suite passed with 72 tests; executor/shell search found no matches in M14 scope.
- Assumptions: Single explicit JSON `tool_call` object is sufficient for Phase 1.
- Remaining issues: No tool catalog or executor by design.
- Recommended follow-up: Human review before starting M15.

### Task M15-T1 — Establish Layered Modules

## Parent milestone

M15

## Status

implemented

## Owner role

Architect

## Objective

Create canonical layer packages for domain, application, infrastructure and interfaces.

## Scope

- Move message, session, error and tool data types to `ai_assistant/domain/`.
- Move runtime, context builder and tool-call interpretation to `ai_assistant/application/`.
- Move providers and stores to `ai_assistant/infrastructure/`.
- Move CLI adapter to `ai_assistant/interfaces/cli/`.
- Keep legacy packages as compatibility exports.

## Explicit exclusions

- No public protocol changes.
- No database schema migration.
- No new dependencies.
- No tool execution.

## File scope

### Writable

- `ai_assistant/domain/`
- `ai_assistant/application/`
- `ai_assistant/infrastructure/`
- `ai_assistant/interfaces/`
- `ai_assistant/agent/`
- `ai_assistant/cli/`
- `ai_assistant/storage/`

### Forbidden

- Persistent user data.

## Dependencies

- M14 accepted.

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-003 Provider-neutral Message model
- ADR-006 ModelProvider port
- ADR-008 Declarative tools only in Phase 1
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Domain no importa infraestructura.
- [x] Application no importa adaptadores.
- [x] Legacy imports remain compatible.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_layering.py -q
```

## Result report

- Summary: Added canonical layered modules and compatibility exports.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_layering.py -q`.
- Test results: 3 passed.
- Remaining issues: Legacy packages can be removed in a later dedicated cleanup.

### Task M15-T2 — Wire Bootstrap To Layers

## Parent milestone

M15

## Status

implemented

## Owner role

Runtime implementer

## Objective

Use canonical layer modules from bootstrap and entry points without changing runtime behavior.

## Scope

- Update `ai_assistant/bootstrap/container.py` imports.
- Update `ai_assistant/main.py` to use the composition root directly.
- Update tests that monkeypatch provider internals to target canonical infrastructure modules.

## Explicit exclusions

- No CLI feature changes.
- No logging policy changes.
- No provider behavior changes.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/main.py`
- provider tests

## Dependencies

- M15-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap
- ADR-011 Native Ollama adapter

## Acceptance criteria

- [x] CLI no construye dependencias.
- [x] `python main.py` funciona.

## Validation commands

```bash
printf 'hello\nquit\n' | AI_ASSISTANT_PROVIDER=dummy AI_ASSISTANT_MODEL= PYTHONDONTWRITEBYTECODE=1 python main.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q
```

## Result report

- Summary: Bootstrap now assembles canonical application, infrastructure and interface modules.
- Test results: CLI smoke exited 0 and printed `Echo: hello`; unit suite passed with 61 tests and 14 deselected.

### Task M15-T3 — Validate Layered Reorganization

## Parent milestone

M15

## Status

implemented

## Owner role

Integration validator

## Objective

Validate all M15 acceptance criteria and prepare manual review artifacts.

## Scope

- Add layer dependency tests.
- Run full pytest suite.
- Update architecture documentation.
- Produce `.agent/reports/M15.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M15 accepted.
- Do not start M16.

## Dependencies

- M15-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-012 Minimal external dependencies
- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] Domain no importa infraestructura.
- [x] Application no importa adaptadores.
- [x] CLI no construye dependencias.
- [x] `python main.py` funciona.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
printf 'hello\nquit\n' | AI_ASSISTANT_PROVIDER=dummy AI_ASSISTANT_MODEL= PYTHONDONTWRITEBYTECODE=1 python main.py
```

## Result report

- Summary: Validated M15 and prepared human review.
- Test results: layering passed with 3 tests; unit passed with 61 tests and 14 deselected; full suite passed with 75 tests; CLI smoke exited 0.

### Task M2.3-T1 — Define Tool Ports

## Parent milestone

M2.3

## Status

implemented

## Owner role

Phase 2 architect

## Objective

Define application-layer ports for catalog, policy, path policy, executor and audit recording.

## Scope

- Add ABC contracts for `ToolCatalog`, `ToolPolicy`, `PathPolicy`, `ToolExecutor` and `AuditRecorder`.
- Export the ports from `ai_assistant.application.ports`.
- Keep contracts provider-neutral and infrastructure-free.

## Explicit exclusions

- No concrete catalog.
- No concrete policy.
- No path resolution implementation.
- No tool execution.

## File scope

### Writable

- `ai_assistant/application/ports/tools.py`
- `ai_assistant/application/ports/__init__.py`

### Read-only

- `ai_assistant/domain/tools.py`
- `docs/roadmap-phase-2.md`
- accepted Phase 2 ADRs

### Forbidden

- concrete infrastructure adapters
- runtime behavior

## Dependencies

- M2.2 accepted.

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-017 Deny-by-Default Tool Policy
- ADR-019 Workspace Confinement and Path Resolution
- ADR-020 Tool Execution Audit and Retention
- ADR-021 Tool Timeouts and Resource Limits
- ADR-023 Error and Log Redaction

## Acceptance criteria

- [x] Application imports no concrete infrastructure adapters.
- [x] Executor cannot authorize.
- [x] Policy performs no external effects.
- [x] Fakes can implement every port.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Defining methods too concretely before M2.4-M2.10 implementation.

## Result report

- Summary: Added `ToolCatalog`, `ToolPolicy`, `PathPolicy`, `ToolExecutor` and `AuditRecorder` application ports.
- Files changed: `ai_assistant/application/ports/tools.py`, `ai_assistant/application/ports/__init__.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: contract/layering passed with 7 tests; full suite passed with 85 tests and 1 skipped; diff check passed.
- Assumptions: `ToolExecutor.execute()` accepting `ToolExecutionContext` is the narrow contract proving authorization happens before execution.
- Remaining issues: No concrete implementations by design.
- Recommended follow-up: Implement static catalog in M2.4.

### Task M2.3-T2 — Tool Port Contract Fakes

## Parent milestone

M2.3

## Status

implemented

## Owner role

Test agent

## Objective

Prove local fakes can implement every new tool execution port.

## Scope

- Add contract tests using in-test fakes.
- Verify executor receives an authorized context, not an authorization request.

## Explicit exclusions

- No concrete adapters.
- No filesystem access.
- No SQLite audit persistence.

## File scope

### Writable

- `tests/test_ports_contract.py`

### Read-only

- `ai_assistant/application/ports/tools.py`
- `ai_assistant/domain/tools.py`

### Forbidden

- production adapters
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2.3-T1

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-017 Deny-by-Default Tool Policy

## Acceptance criteria

- [x] Fakes can implement every port.
- [x] Executor cannot authorize by port contract shape.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_ports_contract.py -q
```

## Risks

- Tests may over-specify future coordinator behavior.

## Result report

- Summary: Added contract tests with in-test fakes for all new tool execution ports.
- Files changed: `tests/test_ports_contract.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: contract/layering passed with 7 tests; full suite passed with 85 tests and 1 skipped.
- Assumptions: Contract tests should verify port shape, not future coordinator sequencing.
- Remaining issues: None for M2.3.
- Recommended follow-up: Keep concrete fake/dry-run executors for M2.7.

### Task M2.3-T3 — Validate M2.3

## Parent milestone

M2.3

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.3 acceptance criteria and prepare manual review artifacts.

## Scope

- Run contract, layering and full test suites.
- Produce `.agent/reports/M2.3.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.3 accepted.
- Do not start M2.4.

## File scope

### Writable

- `.agent/reports/M2.3.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.3-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-013 Pytest Testing Strategy
- ADR-016 Safe Tool Execution Pipeline

## Acceptance criteria

- [x] Application imports no concrete infrastructure adapters.
- [x] Executor cannot authorize.
- [x] Policy performs no external effects.
- [x] Fakes can implement every port.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing unrelated workspace changes may appear in full diff.

## Result report

- Summary: Validated M2.3 and prepared manual review artifacts.
- Files changed: `.agent/reports/M2.3.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: contract/layering passed with 7 tests; full suite passed with 85 tests and 1 skipped; diff check passed.
- Assumptions: No architecture documentation update is required for pure port declaration; existing Phase 2 architecture already names these ports.
- Remaining issues: M2.3 awaits manual review.
- Recommended follow-up: Start M2.4 after approval.

### Task M2.4-T1 — Static Tool Catalog

## Parent milestone

M2.4

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add a static read-only catalog for the two approved productive tools.

## Scope

- Register only `list_directory` and `read_file`.
- Add immutable permission, default and limit metadata to tool definitions.
- Reject unknown names explicitly.

## Explicit exclusions

- No concrete execution.
- No path validation.
- No deny-by-default policy implementation.
- No `noop` production registration.

## File scope

### Writable

- `ai_assistant/application/tool_catalog.py`
- `ai_assistant/domain/tools.py`

### Read-only

- `ai_assistant/application/ports/tools.py`
- `docs/roadmap-phase-2.md`
- `docs/adr/ADR-018-read-only-tool-allowlist.md`
- `docs/adr/ADR-021-tool-timeouts-and-resource-limits.md`

### Forbidden

- concrete infrastructure adapters
- runtime execution flow

## Dependencies

- M2.3 accepted.

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-018 Read-Only Tool Allowlist
- ADR-021 Tool Timeouts and Resource Limits

## Acceptance criteria

- [x] Exact-name lookup only.
- [x] Unknown names are rejected.
- [x] Limits and permission metadata are immutable from model input.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Over-specifying future policy behavior inside the catalog.

## Result report

- Summary: Added `StaticToolCatalog` and immutable metadata on `ToolDefinition`.
- Files changed: `ai_assistant/application/tool_catalog.py`, `ai_assistant/domain/tools.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 30 tests; full suite passed with 93 tests and 1 skipped; diff check passed.
- Assumptions: Catalog metadata can expose limits/defaults without enforcing them until policy milestones.
- Remaining issues: No path or argument policy yet by roadmap.
- Recommended follow-up: Implement workspace and path policy in M2.5 after approval.

### Task M2.4-T2 — Catalog Contract Tests

## Parent milestone

M2.4

## Status

implemented

## Owner role

Test agent

## Objective

Cover exact-name lookup, unknown rejection and immutable metadata.

## Scope

- Add catalog tests for approved names only.
- Test alias, case variant, `noop` and trailing-space rejection.
- Test mutation of defaults, limits and schema fails.

## Explicit exclusions

- No filesystem fixtures.
- No executor tests.
- No policy argument validation tests.

## File scope

### Writable

- `tests/test_tool_catalog.py`
- `tests/test_tools.py`

### Read-only

- `ai_assistant/application/tool_catalog.py`
- `ai_assistant/domain/tools.py`

### Forbidden

- concrete infrastructure adapters
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2.4-T1

## Applicable ADRs

- ADR-018 Read-Only Tool Allowlist
- ADR-021 Tool Timeouts and Resource Limits

## Acceptance criteria

- [x] Exact-name lookup only.
- [x] Unknown names are rejected.
- [x] Limits and permission metadata are immutable from model input.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py -q
```

## Risks

- Tests can accidentally encode policy behavior that belongs to M2.6.

## Result report

- Summary: Added focused catalog tests.
- Files changed: `tests/test_tool_catalog.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 30 tests; full suite passed with 93 tests and 1 skipped.
- Assumptions: Immutability is checked at the public `ToolDefinition` boundary.
- Remaining issues: None for M2.4.
- Recommended follow-up: Add adversarial path tests in M2.5/M2.15.

### Task M2.4-T3 — Validate M2.4

## Parent milestone

M2.4

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.4 acceptance criteria and prepare manual review artifacts.

## Scope

- Run scoped and full validation.
- Produce `.agent/reports/M2.4.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.4 accepted.
- Do not start M2.5.

## File scope

### Writable

- `.agent/reports/M2.4.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.4-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-013 Pytest Testing Strategy
- ADR-018 Read-Only Tool Allowlist

## Acceptance criteria

- [x] Exact-name lookup only.
- [x] Unknown names are rejected.
- [x] Limits and permission metadata are immutable from model input.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing unrelated workspace changes remain visible in git status.

## Result report

- Summary: Validated M2.4 and prepared manual review.
- Files changed: `.agent/reports/M2.4.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 30 tests; full suite passed with 93 tests and 1 skipped; diff check passed.
- Assumptions: M2.4 does not require documentation updates because architecture and ADR-018 already define the allowlist.
- Remaining issues: M2.4 awaits manual review.
- Recommended follow-up: Start M2.5 after approval.

### Task M2.5-T1 — Workspace Config And Context Paths

## Parent milestone

M2.5

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add workspace configuration and normalized path metadata on execution context.

## Scope

- Load optional `AI_ASSISTANT_WORKSPACE`.
- Preserve Phase 1 defaults when workspace is unset.
- Add optional resolved and relative path fields to `ToolExecutionContext`.

## Explicit exclusions

- No runtime integration.
- No executor implementation.
- No path validation in bootstrap.

## File scope

### Writable

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/domain/tools.py`
- `tests/test_config.py`
- `tests/test_tools.py`

### Read-only

- `docs/adr/ADR-019-workspace-confinement-and-path-resolution.md`

### Forbidden

- concrete infrastructure adapters
- runtime execution flow

## Dependencies

- M2.4 accepted.

## Applicable ADRs

- ADR-019 Workspace Confinement and Path Resolution

## Acceptance criteria

- [x] missing workspace produces a typed error.
- [x] Internal valid path context can carry normalized metadata.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_config.py tests/test_tools.py -q
```

## Risks

- Validating workspace too early would break Phase 1 startup without tools.

## Result report

- Summary: Added optional workspace config and optional path metadata on `ToolExecutionContext`.
- Files changed: `ai_assistant/bootstrap/config.py`, `ai_assistant/domain/tools.py`, `tests/test_config.py`, `tests/test_tools.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_path_policy.py tests/test_config.py tests/test_tools.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 50 tests; full suite passed with 116 tests and 1 skipped; diff check passed.
- Assumptions: Missing workspace should fail when constructing `WorkspacePathPolicy`, not during normal Phase 1 config load.
- Remaining issues: None for this task.
- Recommended follow-up: Wire workspace into composition root in M2.12.

### Task M2.5-T2 — Workspace Path Policy

## Parent milestone

M2.5

## Status

implemented

## Owner role

Runtime implementer

## Objective

Implement path policy checks for confined read-only workspace access.

## Scope

- Canonicalize workspace and requested paths.
- Reject absolute paths, traversal, workspace escapes and external symlinks.
- Reject hidden and sensitive path components.
- Reject wrong file type and special files.
- Enforce path-length limit from catalog metadata.

## Explicit exclusions

- No file content reads.
- No directory listing.
- No stable policy reason codes yet.

## File scope

### Writable

- `ai_assistant/application/path_policy.py`
- `tests/test_path_policy.py`

### Read-only

- `ai_assistant/application/tool_catalog.py`
- `ai_assistant/application/ports/tools.py`
- `docs/adr/ADR-019-workspace-confinement-and-path-resolution.md`
- `docs/adr/ADR-025-sensitive-file-deny-policy.md`

### Forbidden

- concrete executors
- audit persistence

## Dependencies

- M2.5-T1

## Applicable ADRs

- ADR-019 Workspace Confinement and Path Resolution
- ADR-025 Sensitive File Deny Policy

## Acceptance criteria

- [x] `../` escape is denied.
- [x] External absolute path is denied.
- [x] Internal valid path is allowed.
- [x] External symlink is denied.
- [x] Hidden and sensitive paths are denied.
- [x] devices, sockets, FIFOs and other special files are denied.
- [x] missing workspace produces a typed error.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_path_policy.py -q
```

## Risks

- Symlink semantics must stay strict when executors repeat validation later.

## Result report

- Summary: Added `WorkspacePathPolicy` with confined canonical resolution and sensitive path denial.
- Files changed: `ai_assistant/application/path_policy.py`, `tests/test_path_policy.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_path_policy.py tests/test_config.py tests/test_tools.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 50 tests; full suite passed with 116 tests and 1 skipped.
- Assumptions: Stable denial reason codes belong to M2.6.
- Remaining issues: Executors must revalidate before file access in later milestones.
- Recommended follow-up: Implement deny-by-default tool policy in M2.6.

### Task M2.5-T3 — Validate M2.5

## Parent milestone

M2.5

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.5 acceptance criteria and prepare manual review artifacts.

## Scope

- Run scoped and full validation.
- Produce `.agent/reports/M2.5.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.5 accepted.
- Do not start M2.6.

## File scope

### Writable

- `.agent/reports/M2.5.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.5-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-013 Pytest Testing Strategy
- ADR-019 Workspace Confinement and Path Resolution
- ADR-025 Sensitive File Deny Policy

## Acceptance criteria

- [x] `../` escape is denied.
- [x] External absolute path is denied.
- [x] Internal valid path is allowed.
- [x] External symlink is denied.
- [x] Hidden and sensitive paths are denied.
- [x] devices, sockets, FIFOs and other special files are denied.
- [x] missing workspace produces a typed error.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_path_policy.py tests/test_config.py tests/test_tools.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing unrelated workspace changes may appear in git status.

## Result report

- Summary: Validated M2.5 and prepared manual review.
- Files changed: `.agent/reports/M2.5.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_path_policy.py tests/test_config.py tests/test_tools.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 50 tests; full suite passed with 116 tests and 1 skipped; diff check passed.
- Assumptions: No documentation update is required because ADR-019 and ADR-025 already define the policy.
- Remaining issues: M2.5 awaits manual review.
- Recommended follow-up: Start M2.6 after approval.

### Task M2.6-T1 — Deny-By-Default Policy

## Parent milestone

M2.6

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add a pure deny-by-default tool policy with stable reason codes.

## Scope

- Validate enabled flag, tool name, permission, arguments, timeout and limits.
- Add stable denial reason constants.
- Keep path-policy failure mapping as a pure denial result.

## Explicit exclusions

- No executor implementation.
- No audit persistence.
- No coordinator.
- No filesystem access from policy.

## File scope

### Writable

- `ai_assistant/application/tool_policy.py`
- `ai_assistant/application/tool_catalog.py`

### Read-only

- `ai_assistant/application/path_policy.py`
- `ai_assistant/application/ports/tools.py`
- `docs/adr/ADR-017-deny-by-default-tool-policy.md`
- `docs/adr/ADR-021-tool-timeouts-and-resource-limits.md`

### Forbidden

- concrete executors
- runtime execution flow

## Dependencies

- M2.5 accepted.

## Applicable ADRs

- ADR-017 Deny-by-Default Tool Policy
- ADR-018 Read-Only Tool Allowlist
- ADR-021 Tool Timeouts and Resource Limits

## Acceptance criteria

- [x] Unknown tools are denied.
- [x] Malformed arguments are denied.
- [x] Values above hard maximum are denied.
- [x] Denied requests never invoke an executor.
- [x] Every denial has a stable reason code.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_policy.py tests/test_tool_catalog.py tests/test_path_policy.py tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Over-coupling policy to path policy would reintroduce external effects.

## Result report

- Summary: Added `DenyByDefaultToolPolicy` and stable denial reason constants.
- Files changed: `ai_assistant/application/tool_policy.py`, `ai_assistant/application/tool_catalog.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_policy.py tests/test_tool_catalog.py tests/test_path_policy.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 54 tests; full suite passed with 133 tests and 1 skipped; diff check passed.
- Assumptions: Coordinator-level executor gating is completed in M2.10.
- Remaining issues: None for M2.6.
- Recommended follow-up: Add fake and dry-run executors in M2.7.

### Task M2.6-T2 — Policy Tests

## Parent milestone

M2.6

## Status

implemented

## Owner role

Test agent

## Objective

Cover deny-by-default policy behavior and stable reason codes.

## Scope

- Test unknown, malformed, timeout, limit, permission, disabled and path-denied cases.
- Test denied policy result does not invoke a fake executor gate.

## Explicit exclusions

- No real executor.
- No filesystem fixtures.
- No audit assertions.

## File scope

### Writable

- `tests/test_tool_policy.py`

### Read-only

- `ai_assistant/application/tool_policy.py`
- `ai_assistant/application/tool_catalog.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2.6-T1

## Applicable ADRs

- ADR-017 Deny-by-Default Tool Policy
- ADR-021 Tool Timeouts and Resource Limits

## Acceptance criteria

- [x] Unknown tools are denied.
- [x] Malformed arguments are denied.
- [x] Values above hard maximum are denied.
- [x] Denied requests never invoke an executor.
- [x] Every denial has a stable reason code.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_policy.py -q
```

## Risks

- Tests should not assume future audit/coordinator implementation details.

## Result report

- Summary: Added focused policy tests.
- Files changed: `tests/test_tool_policy.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_policy.py tests/test_tool_catalog.py tests/test_path_policy.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 54 tests; full suite passed with 133 tests and 1 skipped.
- Assumptions: Path-policy failures are represented as a stable `path_denied` decision in this milestone.
- Remaining issues: None for M2.6.
- Recommended follow-up: Exercise executor outcomes in M2.7.

### Task M2.6-T3 — Validate M2.6

## Parent milestone

M2.6

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.6 acceptance criteria and prepare manual review artifacts.

## Scope

- Run scoped and full validation.
- Produce `.agent/reports/M2.6.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.6 accepted.
- Do not start M2.7.

## File scope

### Writable

- `.agent/reports/M2.6.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.6-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-013 Pytest Testing Strategy
- ADR-017 Deny-by-Default Tool Policy

## Acceptance criteria

- [x] Unknown tools are denied.
- [x] Malformed arguments are denied.
- [x] Values above hard maximum are denied.
- [x] Denied requests never invoke an executor.
- [x] Every denial has a stable reason code.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_policy.py tests/test_tool_catalog.py tests/test_path_policy.py tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing M2.5 uncommitted changes remain part of the working tree.

## Result report

- Summary: Validated M2.6 and prepared manual review.
- Files changed: `.agent/reports/M2.6.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_policy.py tests/test_tool_catalog.py tests/test_path_policy.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 54 tests; full suite passed with 133 tests and 1 skipped; diff check passed.
- Assumptions: No documentation update required; ADR-017 already documents policy semantics.
- Remaining issues: M2.6 awaits manual review.
- Recommended follow-up: Start M2.7 after approval.

### Task M2.7-T1 — Fake And Dry-Run Executors

## Parent milestone

M2.7

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add reproducible no-effect tool executors for validation.

## Scope

- Add `FakeToolExecutor` with recorded calls and configurable status.
- Add `DryRunToolExecutor` returning structured dry-run content.
- Keep executors behind the `ToolExecutor` port.

## Explicit exclusions

- No filesystem reads.
- No audit persistence.
- No coordinator.
- No production local executor.

## File scope

### Writable

- `ai_assistant/application/tool_executors.py`

### Read-only

- `ai_assistant/application/ports/tools.py`
- `ai_assistant/domain/tools.py`
- `docs/roadmap-phase-2.md`

### Forbidden

- runtime execution flow
- concrete filesystem executor

## Dependencies

- M2.6 accepted.

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-021 Tool Timeouts and Resource Limits

## Acceptance criteria

- [x] Allowed requests reach the fake executor.
- [x] Denied requests do not.
- [x] Success, timeout and failure are reproducible.
- [x] Dry-run produces no external effect.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_executors.py tests/test_tool_policy.py tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Accidentally adding orchestration before M2.10.

## Result report

- Summary: Added `FakeToolExecutor` and `DryRunToolExecutor`.
- Files changed: `ai_assistant/application/tool_executors.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_executors.py tests/test_tool_policy.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 30 tests; full suite passed with 139 tests and 1 skipped; diff check passed.
- Assumptions: These executors are application test utilities, not production filesystem adapters.
- Remaining issues: None for M2.7.
- Recommended follow-up: Implement audit persistence in M2.8.

### Task M2.7-T2 — Executor Tests

## Parent milestone

M2.7

## Status

implemented

## Owner role

Test agent

## Objective

Cover allowed, denied, success, timeout, failure and dry-run executor behavior.

## Scope

- Verify fake executor records allowed calls.
- Verify denied flow skips fake executor.
- Verify deterministic success, timeout and error results.
- Verify dry-run returns structured content only.

## Explicit exclusions

- No real filesystem effects.
- No audit tests.
- No coordinator tests.

## File scope

### Writable

- `tests/test_tool_executors.py`

### Read-only

- `ai_assistant/application/tool_executors.py`
- `ai_assistant/domain/tools.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2.7-T1

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline

## Acceptance criteria

- [x] Allowed requests reach the fake executor.
- [x] Denied requests do not.
- [x] Success, timeout and failure are reproducible.
- [x] Dry-run produces no external effect.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_executors.py -q
```

## Risks

- Tests should not encode final coordinator internals.

## Result report

- Summary: Added focused executor tests.
- Files changed: `tests/test_tool_executors.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_executors.py tests/test_tool_policy.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 30 tests; full suite passed with 139 tests and 1 skipped.
- Assumptions: Denied request skip is represented by the same policy gate shape the coordinator will use later.
- Remaining issues: None for M2.7.
- Recommended follow-up: Add coordinator-level denial tests in M2.10.

### Task M2.7-T3 — Validate M2.7

## Parent milestone

M2.7

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.7 acceptance criteria and prepare manual review artifacts.

## Scope

- Run scoped and full validation.
- Produce `.agent/reports/M2.7.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.7 accepted.
- Do not start M2.8.

## File scope

### Writable

- `.agent/reports/M2.7.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.7-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-013 Pytest Testing Strategy
- ADR-016 Safe Tool Execution Pipeline

## Acceptance criteria

- [x] Allowed requests reach the fake executor.
- [x] Denied requests do not.
- [x] Success, timeout and failure are reproducible.
- [x] Dry-run produces no external effect.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_executors.py tests/test_tool_policy.py tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing uncommitted M2.5/M2.6 changes remain part of the working tree.

## Result report

- Summary: Validated M2.7 and prepared manual review.
- Files changed: `.agent/reports/M2.7.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_executors.py tests/test_tool_policy.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 30 tests; full suite passed with 139 tests and 1 skipped; diff check passed.
- Assumptions: No documentation update required; behavior is test support for later orchestration.
- Remaining issues: M2.7 awaits manual review.
- Recommended follow-up: Start M2.8 after approval.

### Task M2.8-T1 — SQLite Audit Recorder

## Parent milestone

M2.8

## Status

implemented

## Owner role

Persistence implementer

## Objective

Persist sanitized tool audit events in SQLite separately from conversation storage.

## Scope

- Add append-oriented `SQLiteAuditRecorder`.
- Add `ToolAuditStoreError`.
- Persist event metadata, redacted argument summaries and artifact IDs.
- Raise explicit typed errors on audit persistence failures.

## Explicit exclusions

- No conversation schema changes.
- No retention pruning.
- No config/CLI wiring for `AI_ASSISTANT_AUDIT_DATABASE`.
- No coordinator integration.

## File scope

### Writable

- `ai_assistant/infrastructure/storage/sqlite_audit.py`
- `ai_assistant/domain/errors.py`
- `ai_assistant/domain/__init__.py`
- `ai_assistant/application/errors.py`

### Read-only

- `ai_assistant/application/ports/tools.py`
- `docs/adr/ADR-020-tool-execution-audit-and-retention.md`

### Forbidden

- `ai_assistant/infrastructure/storage/sqlite_memory.py`
- runtime execution flow

## Dependencies

- M2.7 accepted.

## Applicable ADRs

- ADR-020 Tool Execution Audit and Retention
- ADR-023 Error and Log Redaction

## Acceptance criteria

- [x] Allow, deny, success, timeout and failure are recorded.
- [x] File contents are never persisted.
- [x] Sensitive values are redacted.
- [x] Audit failure behavior is explicit.
- [x] Integration tests use temporary SQLite.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_sqlite_audit.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Redaction denylist is intentionally minimal and should expand with new audit fields.

## Result report

- Summary: Added `SQLiteAuditRecorder` and `ToolAuditStoreError`.
- Files changed: `ai_assistant/infrastructure/storage/sqlite_audit.py`, `ai_assistant/domain/errors.py`, `ai_assistant/domain/__init__.py`, `ai_assistant/application/errors.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_sqlite_audit.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 29 tests; full suite passed with 145 tests and 1 skipped; diff check passed.
- Assumptions: Read APIs for audit are not required until reporting/export features are approved.
- Remaining issues: None for M2.8.
- Recommended follow-up: Wire audit recorder into coordinator in M2.10 and config in M2.12.

### Task M2.8-T2 — Audit Persistence Tests

## Parent milestone

M2.8

## Status

implemented

## Owner role

Test agent

## Objective

Cover audit outcomes, redaction, failure behavior and temporary SQLite integration.

## Scope

- Verify allow, deny, success, timeout and error persistence.
- Verify file content and secret-like values are redacted.
- Verify persistence failure raises `ToolAuditStoreError`.
- Use temporary SQLite databases.

## Explicit exclusions

- No coordinator tests.
- No retention tests.
- No real workspace reads.

## File scope

### Writable

- `tests/test_sqlite_audit.py`

### Read-only

- `ai_assistant/infrastructure/storage/sqlite_audit.py`
- `ai_assistant/domain/tools.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2.8-T1

## Applicable ADRs

- ADR-020 Tool Execution Audit and Retention
- ADR-023 Error and Log Redaction

## Acceptance criteria

- [x] Allow, deny, success, timeout and failure are recorded.
- [x] File contents are never persisted.
- [x] Sensitive values are redacted.
- [x] Audit failure behavior is explicit.
- [x] Integration tests use temporary SQLite.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_sqlite_audit.py -q
```

## Risks

- Tests should not require a permanent audit database.

## Result report

- Summary: Added SQLite audit integration tests.
- Files changed: `tests/test_sqlite_audit.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_sqlite_audit.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 29 tests; full suite passed with 145 tests and 1 skipped.
- Assumptions: Direct SQL assertions are enough; no audit read port exists yet.
- Remaining issues: None for M2.8.
- Recommended follow-up: Add coordinator audit assertions in M2.10.

### Task M2.8-T3 — Validate M2.8

## Parent milestone

M2.8

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.8 acceptance criteria and prepare manual review artifacts.

## Scope

- Run scoped and full validation.
- Produce `.agent/reports/M2.8.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.8 accepted.
- Do not start M2.9.

## File scope

### Writable

- `.agent/reports/M2.8.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.8-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-013 Pytest Testing Strategy
- ADR-020 Tool Execution Audit and Retention

## Acceptance criteria

- [x] Allow, deny, success, timeout and failure are recorded.
- [x] File contents are never persisted.
- [x] Sensitive values are redacted.
- [x] Audit failure behavior is explicit.
- [x] Integration tests use temporary SQLite.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_sqlite_audit.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing uncommitted Phase 2 changes remain part of the working tree.

## Result report

- Summary: Validated M2.8 and prepared manual review.
- Files changed: `.agent/reports/M2.8.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_sqlite_audit.py tests/test_tools.py tests/test_ports_contract.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 29 tests; full suite passed with 145 tests and 1 skipped; diff check passed.
- Assumptions: No docs update required; ADR-020 already documents retention and storage intent.
- Remaining issues: M2.8 awaits manual review.
- Recommended follow-up: Start M2.9 after approval.

### Task M2.9-T1 — Local Read-Only Executor

## Parent milestone

M2.9

## Status

implemented

## Owner role

Persistence implementer

## Objective

Add secure local implementations for `list_directory` and `read_file`.

## Scope

- Implement `LocalReadOnlyToolExecutor` behind the `ToolExecutor` port.
- Repeat workspace path validation immediately before access.
- Return structured directory entries.
- Read bounded file bytes and mark truncation.
- Document binary decode behavior.

## Explicit exclusions

- No writes.
- No shell/process/Git/network calls.
- No coordinator integration.
- No C socket executor.

## File scope

### Writable

- `ai_assistant/infrastructure/tools/local_read_only.py`
- `ai_assistant/infrastructure/tools/__init__.py`
- `docs/architecture.md`

### Read-only

- `ai_assistant/application/path_policy.py`
- `ai_assistant/application/tool_catalog.py`
- `docs/adr/ADR-019-workspace-confinement-and-path-resolution.md`
- `docs/adr/ADR-021-tool-timeouts-and-resource-limits.md`

### Forbidden

- runtime execution flow
- audit coordinator

## Dependencies

- M2.8 accepted.

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-019 Workspace Confinement and Path Resolution
- ADR-021 Tool Timeouts and Resource Limits

## Acceptance criteria

- [x] Structured directory entries are returned.
- [x] File reads are bounded and indicate truncation.
- [x] Path validation is repeated immediately before access.
- [x] Binary-file behavior is documented and tested.
- [x] Response limits are enforced independently.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_local_read_only_executor.py tests/test_path_policy.py tests/test_tool_policy.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Local filesystem reads must stay behind explicit policy and workspace validation.

## Result report

- Summary: Added `LocalReadOnlyToolExecutor` for bounded listing and file reading.
- Files changed: `ai_assistant/infrastructure/tools/local_read_only.py`, `ai_assistant/infrastructure/tools/__init__.py`, `docs/architecture.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_local_read_only_executor.py tests/test_path_policy.py tests/test_tool_policy.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 48 tests; full suite passed with 151 tests and 1 skipped; diff check passed.
- Assumptions: Binary content is returned as UTF-8 with replacement instead of rejecting binary files.
- Remaining issues: None for M2.9.
- Recommended follow-up: Wire executor through coordinator in M2.10.

### Task M2.9-T2 — Local Executor Tests

## Parent milestone

M2.9

## Status

implemented

## Owner role

Test agent

## Objective

Cover local read-only executor behavior with temporary workspaces.

## Scope

- Test structured directory entries.
- Test bounded file reads and truncation.
- Test repeated path validation.
- Test binary decode behavior.
- Test independent read and directory limits.

## Explicit exclusions

- No permanent workspace.
- No coordinator or audit assertions.
- No C tool service.

## File scope

### Writable

- `tests/test_local_read_only_executor.py`

### Read-only

- `ai_assistant/infrastructure/tools/local_read_only.py`
- `ai_assistant/domain/tools.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2.9-T1

## Applicable ADRs

- ADR-019 Workspace Confinement and Path Resolution
- ADR-021 Tool Timeouts and Resource Limits

## Acceptance criteria

- [x] Structured directory entries are returned.
- [x] File reads are bounded and indicate truncation.
- [x] Path validation is repeated immediately before access.
- [x] Binary-file behavior is documented and tested.
- [x] Response limits are enforced independently.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_local_read_only_executor.py -q
```

## Risks

- Tests must avoid reading outside temporary directories.

## Result report

- Summary: Added local executor integration tests with `tmp_path`.
- Files changed: `tests/test_local_read_only_executor.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_local_read_only_executor.py tests/test_path_policy.py tests/test_tool_policy.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 48 tests; full suite passed with 151 tests and 1 skipped.
- Assumptions: Direct executor tests are enough until coordinator audit flow exists.
- Remaining issues: None for M2.9.
- Recommended follow-up: Add coordinator integration tests in M2.10.

### Task M2.9-T3 — Validate M2.9

## Parent milestone

M2.9

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.9 acceptance criteria and prepare manual review artifacts.

## Scope

- Run scoped and full validation.
- Produce `.agent/reports/M2.9.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.9 accepted.
- Do not start M2.10.

## File scope

### Writable

- `.agent/reports/M2.9.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.9-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-013 Pytest Testing Strategy
- ADR-019 Workspace Confinement and Path Resolution

## Acceptance criteria

- [x] Structured directory entries are returned.
- [x] File reads are bounded and indicate truncation.
- [x] Path validation is repeated immediately before access.
- [x] Binary-file behavior is documented and tested.
- [x] Response limits are enforced independently.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_local_read_only_executor.py tests/test_path_policy.py tests/test_tool_policy.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing uncommitted Phase 2 changes remain part of the working tree.

## Result report

- Summary: Validated M2.9 and prepared manual review.
- Files changed: `.agent/reports/M2.9.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_local_read_only_executor.py tests/test_path_policy.py tests/test_tool_policy.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 48 tests; full suite passed with 151 tests and 1 skipped; diff check passed.
- Assumptions: M2.9 does not require CLI/config wiring.
- Remaining issues: M2.9 awaits manual review.
- Recommended follow-up: Start M2.10 after approval.

### Task M2.10-T1 — Tool Execution Coordinator

## Parent milestone

M2.10

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add a deterministic coordinator for authorized tool execution.

## Scope

- Orchestrate `ToolCatalog`, `ToolPolicy`, `PathPolicy`, `AuditRecorder` and `ToolExecutor`.
- Audit denials and allowed/final execution outcomes.
- Prevent denied requests from reaching executors.
- Normalize unexpected executor exceptions into sanitized tool results.

## Explicit exclusions

- No runtime integration.
- No CLI/config wiring.
- No multi-round tool loop.
- No model calls.

## File scope

### Writable

- `ai_assistant/application/tool_coordinator.py`
- `ai_assistant/domain/tools.py`

### Read-only

- `ai_assistant/application/ports/tools.py`
- `docs/adr/ADR-016-safe-tool-execution-pipeline.md`
- `docs/adr/ADR-024-bounded-single-tool-round-per-turn.md`

### Forbidden

- runtime execution flow
- CLI

## Dependencies

- M2.9 accepted.

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-020 Tool Execution Audit and Retention
- ADR-024 Bounded Single Tool Round per Turn

## Acceptance criteria

- [x] Execution order is deterministic.
- [x] Every outcome is audited.
- [x] Denied requests never reach the executor.
- [x] Executor errors become normalized typed results.
- [x] Unit tests use fake ports.
- [x] Integration tests use the local executor and SQLite audit.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_coordinator.py tests/test_tool_coordinator_integration.py tests/test_local_read_only_executor.py tests/test_sqlite_audit.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Coordinator must not become runtime integration before M2.11.

## Result report

- Summary: Added `ToolExecutionCoordinator` and `allowed` audit status.
- Files changed: `ai_assistant/application/tool_coordinator.py`, `ai_assistant/domain/tools.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_coordinator.py tests/test_tool_coordinator_integration.py tests/test_local_read_only_executor.py tests/test_sqlite_audit.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 21 tests; full suite passed with 157 tests and 1 skipped; diff check passed.
- Assumptions: `allowed` is an audit status used before executor invocation, not a final executor result.
- Remaining issues: None for M2.10.
- Recommended follow-up: Integrate one bounded tool round into runtime in M2.11.

### Task M2.10-T2 — Coordinator Unit Tests

## Parent milestone

M2.10

## Status

implemented

## Owner role

Test agent

## Objective

Cover coordinator order, audit, denial and executor error normalization with fake ports.

## Scope

- Assert exact call order for allowed execution.
- Assert policy/path/catalog denials are audited and skip executor.
- Assert executor exceptions become sanitized error results.

## Explicit exclusions

- No real filesystem.
- No SQLite.
- No runtime integration.

## File scope

### Writable

- `tests/test_tool_coordinator.py`

### Read-only

- `ai_assistant/application/tool_coordinator.py`
- `ai_assistant/domain/tools.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2.10-T1

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline

## Acceptance criteria

- [x] Execution order is deterministic.
- [x] Every outcome is audited.
- [x] Denied requests never reach the executor.
- [x] Executor errors become normalized typed results.
- [x] Unit tests use fake ports.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_coordinator.py -q
```

## Risks

- Tests should not encode M2.11 runtime behavior.

## Result report

- Summary: Added fake-port coordinator tests.
- Files changed: `tests/test_tool_coordinator.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_coordinator.py tests/test_tool_coordinator_integration.py tests/test_local_read_only_executor.py tests/test_sqlite_audit.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 21 tests; full suite passed with 157 tests and 1 skipped.
- Assumptions: Audit failure propagation is covered by M2.8 and not duplicated here.
- Remaining issues: None for M2.10.
- Recommended follow-up: Add runtime tool-round tests in M2.11.

### Task M2.10-T3 — Coordinator Integration Validation

## Parent milestone

M2.10

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.10 with the local executor and SQLite audit.

## Scope

- Add integration test wiring static catalog, deny-by-default policy, workspace path policy, SQLite audit and local executor.
- Run scoped and full validation.
- Produce `.agent/reports/M2.10.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.10 accepted.
- Do not start M2.11.

## File scope

### Writable

- `tests/test_tool_coordinator_integration.py`
- `.agent/reports/M2.10.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- runtime execution flow

## Dependencies

- M2.10-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-013 Pytest Testing Strategy
- ADR-016 Safe Tool Execution Pipeline

## Acceptance criteria

- [x] Execution order is deterministic.
- [x] Every outcome is audited.
- [x] Denied requests never reach the executor.
- [x] Executor errors become normalized typed results.
- [x] Unit tests use fake ports.
- [x] Integration tests use the local executor and SQLite audit.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_coordinator.py tests/test_tool_coordinator_integration.py tests/test_local_read_only_executor.py tests/test_sqlite_audit.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing uncommitted Phase 2 changes remain part of the working tree.

## Result report

- Summary: Validated M2.10 and prepared manual review.
- Files changed: `tests/test_tool_coordinator_integration.py`, `.agent/reports/M2.10.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_coordinator.py tests/test_tool_coordinator_integration.py tests/test_local_read_only_executor.py tests/test_sqlite_audit.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 21 tests; full suite passed with 157 tests and 1 skipped; diff check passed.
- Assumptions: M2.10 intentionally stops before runtime integration.
- Remaining issues: M2.10 awaits manual review.
- Recommended follow-up: Start M2.11 after approval.

### Task M2.11-T1 — Runtime Tool Round

## Parent milestone

M2.11

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add an optional one-round tool execution path to `AgentRuntime`.

## Scope

- Accept an optional `ToolExecutionCoordinator`.
- Convert the first assistant tool call into a `ToolExecutionRequest`.
- Send one tool-result message to a second model call.
- Stop safely if the second model response requests another tool.
- Persist the complete tool round with one `append_many` call.

## Explicit exclusions

- No bootstrap/config wiring.
- No CLI changes.
- No multi-tool loop.
- No automatic retry after denial.

## File scope

### Writable

- `ai_assistant/application/runtime.py`

### Read-only

- `ai_assistant/application/tool_coordinator.py`
- `docs/adr/ADR-024-bounded-single-tool-round-per-turn.md`

### Forbidden

- infrastructure adapters
- CLI wiring

## Dependencies

- M2.10 accepted.

## Applicable ADRs

- ADR-010 Transactional Turn Persistence
- ADR-016 Safe Tool Execution Pipeline
- ADR-024 Bounded Single Tool Round per Turn

## Acceptance criteria

- [x] Final answers can use tool results.
- [x] No-tool Phase 1 behavior is preserved.
- [x] Loop bound is enforced.
- [x] Conversation persistence remains transactional.
- [x] Regression tests cover Phase 1 behavior.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_agent_runtime.py tests/test_tool_coordinator.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Runtime must not enable tools unless a coordinator is explicitly provided.

## Result report

- Summary: Added optional bounded tool round to `AgentRuntime`.
- Files changed: `ai_assistant/application/runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_agent_runtime.py tests/test_tool_coordinator.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 17 tests; full suite passed with 160 tests and 1 skipped; diff check passed.
- Assumptions: Tool result messages may be stored in conversation history as local-first runtime state.
- Remaining issues: None for M2.11.
- Recommended follow-up: Wire configuration and CLI support in M2.12.

### Task M2.11-T2 — Runtime Tool Round Tests

## Parent milestone

M2.11

## Status

implemented

## Owner role

Test agent

## Objective

Cover final answer with tool result, no-tool regression, loop bound and transactional persistence.

## Scope

- Add sequence model tests for second model call.
- Verify tool result message reaches final model call.
- Verify second tool request is bounded.
- Verify complete tool round persists transactionally.

## Explicit exclusions

- No local filesystem executor.
- No SQLite audit.
- No CLI tests.

## File scope

### Writable

- `tests/test_agent_runtime.py`

### Read-only

- `ai_assistant/application/runtime.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2.11-T1

## Applicable ADRs

- ADR-010 Transactional Turn Persistence
- ADR-024 Bounded Single Tool Round per Turn

## Acceptance criteria

- [x] Final answers can use tool results.
- [x] No-tool Phase 1 behavior is preserved.
- [x] Loop bound is enforced.
- [x] Conversation persistence remains transactional.
- [x] Regression tests cover Phase 1 behavior.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_agent_runtime.py -q
```

## Risks

- Tests should not rely on M2.12 composition.

## Result report

- Summary: Added focused runtime tests for one bounded tool round.
- Files changed: `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_agent_runtime.py tests/test_tool_coordinator.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 17 tests; full suite passed with 160 tests and 1 skipped.
- Assumptions: Existing no-coordinator test remains the Phase 1 no-tool regression.
- Remaining issues: None for M2.11.
- Recommended follow-up: Add bootstrap-level tests in M2.12.

### Task M2.11-T3 — Validate M2.11

## Parent milestone

M2.11

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.11 acceptance criteria and prepare manual review artifacts.

## Scope

- Run scoped and full validation.
- Produce `.agent/reports/M2.11.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.11 accepted.
- Do not start M2.12.

## File scope

### Writable

- `.agent/reports/M2.11.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.11-T2

## Applicable ADRs

- ADR-013 Pytest Testing Strategy
- ADR-016 Safe Tool Execution Pipeline
- ADR-024 Bounded Single Tool Round per Turn

## Acceptance criteria

- [x] Final answers can use tool results.
- [x] No-tool Phase 1 behavior is preserved.
- [x] Loop bound is enforced.
- [x] Conversation persistence remains transactional.
- [x] Regression tests cover Phase 1 behavior.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_agent_runtime.py tests/test_tool_coordinator.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing uncommitted Phase 2 changes remain part of the working tree.

## Result report

- Summary: Validated M2.11 and prepared manual review.
- Files changed: `.agent/reports/M2.11.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_agent_runtime.py tests/test_tool_coordinator.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 17 tests; full suite passed with 160 tests and 1 skipped; diff check passed.
- Assumptions: M2.11 intentionally stops before config/CLI wiring.
- Remaining issues: M2.11 awaits manual review.
- Recommended follow-up: Start M2.12 after approval.

### Task M2.12-T1 — Tool Configuration Values

## Parent milestone

M2.12

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add read-only tool settings to bootstrap configuration.

## Scope

- Parse `AI_ASSISTANT_WORKSPACE`.
- Parse `AI_ASSISTANT_TOOL_EXECUTION`.
- Parse tool timeout, read bytes, directory entry/depth limits and audit database.
- Keep execution disabled by default.

## Explicit exclusions

- No C tool service config.
- No CLI commands.
- No runtime behavior changes without opt-in.

## File scope

### Writable

- `ai_assistant/bootstrap/config.py`
- `tests/test_config.py`

### Read-only

- `docs/roadmap-phase-2.md`

### Forbidden

- model adapters
- storage schema

## Dependencies

- M2.11 accepted.

## Applicable ADRs

- ADR-007 Configuration at Bootstrap
- ADR-017 Deny-by-Default Tool Policy
- ADR-021 Tool Timeouts and Resource Limits

## Acceptance criteria

- [x] Execution is opt-in.
- [x] Missing workspace means tools are unavailable.
- [x] Tool settings are configurable.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_config.py -q
```

## Risks

- Config validation must not break default Phase 1 CLI startup.

## Result report

- Summary: Added tool execution config values and validation.
- Files changed: `ai_assistant/bootstrap/config.py`, `tests/test_config.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_config.py tests/test_cli_app.py tests/test_agent_runtime.py tests/test_tool_catalog.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 39 tests; full suite passed with 167 tests and 1 skipped; diff check passed.
- Assumptions: Values above hard maximum are capped by catalog/policy, not rejected by config.
- Remaining issues: None for M2.12.
- Recommended follow-up: C tool service config in M2.13/M2.14.

### Task M2.12-T2 — Bootstrap Tool Wiring

## Parent milestone

M2.12

## Status

implemented

## Owner role

Runtime implementer

## Objective

Wire configured local tool coordinator through bootstrap.

## Scope

- Construct catalog, policy, path policy, SQLite audit and local executor when tools are enabled and workspace exists.
- Pass configured tool timeout into runtime requests.
- Document new environment variables in README.

## Explicit exclusions

- No C socket executor.
- No new CLI commands.
- No visible tool status banner.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/application/runtime.py`
- `ai_assistant/application/tool_catalog.py`
- `tests/test_cli_app.py`
- `tests/test_agent_runtime.py`
- `tests/test_tool_catalog.py`
- `README.md`

### Read-only

- `ai_assistant/application/tool_coordinator.py`
- `ai_assistant/infrastructure/tools/local_read_only.py`

### Forbidden

- model provider behavior

## Dependencies

- M2.12-T1

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-019 Workspace Confinement and Path Resolution
- ADR-020 Tool Execution Audit and Retention

## Acceptance criteria

- [x] Execution is opt-in.
- [x] Missing workspace means tools are unavailable.
- [x] User errors are sanitized.
- [x] Prompts and file contents are not logged.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_cli_app.py tests/test_agent_runtime.py tests/test_tool_catalog.py -q
```

## Risks

- Enabling tools accidentally by default would violate ADR-017.

## Result report

- Summary: Wired optional local tool coordinator through bootstrap and documented settings.
- Files changed: `ai_assistant/bootstrap/container.py`, `ai_assistant/application/runtime.py`, `ai_assistant/application/tool_catalog.py`, `tests/test_cli_app.py`, `tests/test_agent_runtime.py`, `tests/test_tool_catalog.py`, `README.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_config.py tests/test_cli_app.py tests/test_agent_runtime.py tests/test_tool_catalog.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`
- Test results: scoped suite passed with 39 tests; full suite passed with 167 tests and 1 skipped.
- Assumptions: CLI support means environment-configured behavior, not additional interactive commands.
- Remaining issues: None for M2.12.
- Recommended follow-up: Add C service support in M2.13/M2.14.

### Task M2.12-T3 — Validate M2.12

## Parent milestone

M2.12

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.12 acceptance criteria and prepare manual review artifacts.

## Scope

- Run scoped and full validation.
- Produce `.agent/reports/M2.12.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2.12 accepted.
- Do not start M2.13.

## File scope

### Writable

- `.agent/reports/M2.12.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

### Read-only

- repository diff

### Forbidden

- source behavior changes during validation

## Dependencies

- M2.12-T2

## Applicable ADRs

- ADR-013 Pytest Testing Strategy
- ADR-016 Safe Tool Execution Pipeline
- ADR-017 Deny-by-Default Tool Policy

## Acceptance criteria

- [x] Execution is opt-in.
- [x] Missing workspace means tools are unavailable.
- [x] User errors are sanitized.
- [x] Prompts and file contents are not logged.
- [x] Tool settings are configurable.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_config.py tests/test_cli_app.py tests/test_agent_runtime.py tests/test_tool_catalog.py tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing uncommitted Phase 2 changes remain part of the working tree.

## Result report

- Summary: Validated M2.12 and prepared manual review.
- Files changed: `.agent/reports/M2.12.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_config.py tests/test_cli_app.py tests/test_agent_runtime.py tests/test_tool_catalog.py tests/test_layering.py -q`; `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q`; `git diff --check`
- Test results: scoped suite passed with 39 tests; full suite passed with 167 tests and 1 skipped; diff check passed.
- Assumptions: M2.12 does not require C service wiring.
- Remaining issues: M2.12 awaits manual review.
- Recommended follow-up: Start M2.13 after approval.

### Task M2.13-T1 — C Read-Only Actions

## Parent milestone

M2.13

## Status

implemented

## Owner role

C toolserver engineer

## Objective

Replace prototype C actions with `list_directory` and `read_file`.

## Scope

- Implement read-only action dispatch.
- Enforce workspace confinement, traversal rejection and response bounds.
- Keep tool execution inside the C server limited to filesystem reads.

## Explicit exclusions

- No shell execution.
- No Python executor wiring.
- No incompatible protobuf changes.

## File scope

### Writable

- `c_toolserver/Makefile`
- `c_toolserver/include/actions.h`
- `c_toolserver/src/actions.c`
- `c_toolserver/src/server.c`
- `c_toolserver/README.md`

## Dependencies

- M2.12

## Acceptance criteria

- [x] Only allowlisted C actions exist.
- [x] C rejects traversal and external symlinks.
- [x] C enforces response limits.
- [x] Malformed protobuf fails safely.

## Validation commands

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig make -C c_toolserver clean all
```

## Result report

- Summary: Implemented bounded read-only C actions and safe invalid-protobuf response.
- Test results: C build passed.

### Task M2.13-T2 — C Toolserver Contracts

## Parent milestone

M2.13

## Status

implemented

## Owner role

Test agent

## Objective

Add Python/C contract coverage for C read-only actions.

## Scope

- Cover bounded file reads, directory listing, traversal, external symlink denial, permission denial and malformed protobuf.

## Explicit exclusions

- No production Python executor wiring.
- No broad CI changes.

## File scope

### Writable

- `tests/test_c_toolserver_contract.py`
- `tests/integration_c_toolserver.py`
- `pytest.ini`

## Dependencies

- M2.13-T1

## Acceptance criteria

- [x] Python/C contract tests pass.

## Validation commands

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_c_toolserver_contract.py -q
```

## Result report

- Summary: Added executable contract tests for the C toolserver.
- Test results: 5 passed.

### Task M2.13-T3 — M2.13 Validation

## Parent milestone

M2.13

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.13 acceptance criteria and prepare manual review artifacts.

## Scope

- Run C build, contract tests, full tests, diff check and no-shell scan.
- Update supervisor state.

## Explicit exclusions

- Do not mark M2.13 accepted.
- Do not start M2.14.

## File scope

### Writable

- `.agent/reports/M2.13.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

## Dependencies

- M2.13-T2

## Acceptance criteria

- [x] C build passes.
- [x] Contract tests pass.
- [x] Full suite passes.
- [x] No shell process APIs are introduced.

## Validation commands

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig make -C c_toolserver clean all
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_c_toolserver_contract.py -q
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
rg -n "system\\(|popen\\(|exec[lvpe]*\\(|fork\\(" c_toolserver || true
```

## Result report

- Summary: Validated M2.13 and prepared manual review.
- Test results: C build passed; contract tests passed with 5 tests; full suite passed with 172 passed and 1 skipped; diff check passed; no forbidden process APIs found.
- Remaining issues: M2.13 was approved by user before M2.14 started.

### Task M2.14-T1 — Unix Socket Executor

## Parent milestone

M2.14

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add a `ToolExecutor` adapter that sends already-authorized requests to the C toolserver over a Unix socket.

## Scope

- Encode `ToolExecutionContext` as `ToolRequest`.
- Decode `ToolResponse` into `ToolExecutionResult`.
- Map socket, timeout, malformed, oversized and ID mismatch failures to sanitized results.

## Explicit exclusions

- No TCP transport.
- No bootstrap default switch from the local executor.
- No protobuf schema changes.

## File scope

### Writable

- `ai_assistant/infrastructure/tools/unix_socket.py`
- `ai_assistant/infrastructure/tools/__init__.py`

## Dependencies

- M2.13

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-021 Tool Timeouts and Resource Limits
- ADR-022 Unix Socket Tool Executor
- ADR-023 Error and Log Redaction

## Acceptance criteria

- [x] Only authorized requests are transmitted by accepting only `ToolExecutionContext`.
- [x] Missing socket and timeout become typed errors.
- [x] Malformed and oversized responses are rejected.
- [x] Request and response IDs correlate.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_unix_socket_tool_executor.py -q
```

## Risks

- Manual protobuf parsing can accidentally accept malformed payloads.

## Result report

- Summary: Added `UnixSocketToolExecutor` and minimal protobuf request/response mapping.
- Files changed: `ai_assistant/infrastructure/tools/unix_socket.py`, `ai_assistant/infrastructure/tools/__init__.py`
- Tests run: M2.14 scoped validation.
- Test results: included in M2.14 scoped validation.
- Assumptions: Bootstrap continues using the local executor unless a later milestone wires socket selection.
- Remaining issues: None for this task.
- Recommended follow-up: Keep C service usage explicit.

### Task M2.14-T2 — Unix Socket Contracts

## Parent milestone

M2.14

## Status

implemented

## Owner role

Test agent

## Objective

Prove the Unix socket executor handles protocol failures and C toolserver integration.

## Scope

- Unit/integration tests for missing socket, timeout, malformed response, oversized response and response ID mismatch.
- Contract test using the real C toolserver.

## Explicit exclusions

- No Ollama tests.
- No adversarial matrix from M2.15.

## File scope

### Writable

- `tests/test_unix_socket_tool_executor.py`
- `tests/test_c_toolserver_contract.py`

## Dependencies

- M2.14-T1

## Applicable ADRs

- ADR-022 Unix Socket Tool Executor

## Acceptance criteria

- [x] Contract and integration tests pass.

## Validation commands

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_unix_socket_tool_executor.py tests/test_c_toolserver_contract.py -q
```

## Risks

- C build dependencies are environment-specific.

## Result report

- Summary: Added fake socket failure coverage and real C toolserver executor contract.
- Files changed: `tests/test_unix_socket_tool_executor.py`, `tests/test_c_toolserver_contract.py`
- Tests run: `PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_unix_socket_tool_executor.py tests/test_c_toolserver_contract.py -q`
- Test results: 12 passed.
- Assumptions: Local `protobuf-c` stays available through the recorded environment variables.
- Remaining issues: None for this task.
- Recommended follow-up: M2.15 adversarial matrix.

### Task M2.14-T3 — M2.14 Validation

## Parent milestone

M2.14

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.14 and prepare manual review artifacts.

## Scope

- Run scoped tests, full suite, C contract, diff check and no-network/TCP review.
- Update supervisor state and report.

## Explicit exclusions

- Do not mark M2.14 accepted.
- Do not start M2.15.

## File scope

### Writable

- `.agent/reports/M2.14.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

## Dependencies

- M2.14-T2

## Applicable ADRs

- ADR-013 Pytest Testing Strategy
- ADR-022 Unix Socket Tool Executor

## Acceptance criteria

- [x] All M2.14 acceptance criteria have command evidence.

## Validation commands

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_unix_socket_tool_executor.py tests/test_c_toolserver_contract.py -q
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Risks

- Existing uncommitted M2.13 changes remain part of the working tree.

## Result report

- Summary: Validated M2.14 and prepared manual review.
- Files changed: `.agent/reports/M2.14.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: scoped M2.14 tests; full pytest suite; `git diff --check`; Unix socket transport scan.
- Test results: scoped tests 12 passed; full suite 179 passed, 1 skipped; diff check passed; scan found no TCP usage in the new executor.
- Assumptions: M2.14 does not require CLI/bootstrap selection for the socket executor.
- Remaining issues: M2.14 awaits manual review.
- Recommended follow-up: Start M2.15 after approval.

### Task M2.15-T1 — Adversarial Boundary Checklist

## Parent milestone

M2.15

## Status

implemented

## Owner role

Test agent

## Objective

Add automated adversarial tests for policy, path, audit and runtime boundary cases.

## Scope

- Cover the mandatory M2.15 cases not already directly asserted in focused tests.
- Add a checklist test mapping each mandatory case to automated coverage.

## Explicit exclusions

- No new production capability.
- No Ollama-dependent validation.
- No C-service dependency in core security tests.

## File scope

### Writable

- `tests/test_adversarial_security.py`

### Read-only

- existing tests
- Phase 2 ADRs

## Dependencies

- M2.14

## Applicable ADRs

- ADR-016 Safe Tool Execution Pipeline
- ADR-017 Deny-by-Default Tool Policy
- ADR-019 Workspace Confinement and Path Resolution
- ADR-020 Tool Execution Audit and Retention
- ADR-023 Error and Log Redaction
- ADR-024 Bounded Single Tool Round per Turn
- ADR-025 Sensitive File Deny Policy

## Acceptance criteria

- [x] Every mandatory case has automated coverage.
- [x] Every denial has a stable reason code.
- [x] Logs and audit records contain no sensitive content.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_adversarial_security.py -q
```

## Risks

- Duplicating too much existing coverage.

## Result report

- Summary: Added adversarial tests for unknown/shell-like tools, path attacks, limit denials, audit failure, audit/log redaction and runtime regressions.
- Files changed: `tests/test_adversarial_security.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_adversarial_security.py tests/test_unix_socket_tool_executor.py -q`
- Test results: 22 passed.
- Assumptions: Existing focused tests remain the behavioral source for C malformed protobuf and local binary-file handling.
- Remaining issues: None for this task.
- Recommended follow-up: M2.16 documentation should summarize the security matrix.

### Task M2.15-T2 — Socket Disconnect Coverage

## Parent milestone

M2.15

## Status

implemented

## Owner role

Test agent

## Objective

Add adversarial socket disconnect coverage for the Unix socket executor.

## Scope

- Simulate a server closing before a complete frame is returned.
- Assert sanitized typed error.

## Explicit exclusions

- No C service changes.
- No TCP transport.

## File scope

### Writable

- `tests/test_unix_socket_tool_executor.py`

## Dependencies

- M2.15-T1

## Applicable ADRs

- ADR-022 Unix Socket Tool Executor
- ADR-023 Error and Log Redaction

## Acceptance criteria

- [x] Socket disconnect has automated coverage.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_unix_socket_tool_executor.py -q
```

## Risks

- Threaded socket test timing.

## Result report

- Summary: Added Unix socket disconnect coverage.
- Files changed: `tests/test_unix_socket_tool_executor.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_adversarial_security.py tests/test_unix_socket_tool_executor.py -q`
- Test results: 22 passed.
- Assumptions: Socket disconnect maps to sanitized `malformed_response`.
- Remaining issues: None for this task.
- Recommended follow-up: None.

### Task M2.15-T3 — M2.15 Validation

## Parent milestone

M2.15

## Status

implemented

## Owner role

Integration validator

## Objective

Validate M2.15 and prepare manual review artifacts.

## Scope

- Run adversarial tests, relevant unit/integration tests, full suite and diff checks.
- Confirm core validation does not require Ollama or the C service.

## Explicit exclusions

- Do not mark M2.15 accepted.
- Do not start M2.16.

## File scope

### Writable

- `.agent/reports/M2.15.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

## Dependencies

- M2.15-T2

## Applicable ADRs

- ADR-013 Pytest Testing Strategy
- ADR-016 through ADR-025

## Acceptance criteria

- [x] Every mandatory M2.15 criterion has command evidence.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_adversarial_security.py tests/test_unix_socket_tool_executor.py -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m "not ollama and not toolserver" -q
git diff --check
```

## Risks

- Existing uncommitted M2.13/M2.14 changes remain part of the working tree.

## Result report

- Summary: Validated M2.15 and prepared manual review.
- Files changed: `.agent/reports/M2.15.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: adversarial scope; full suite; core suite excluding `ollama` and `toolserver`; `git diff --check`.
- Test results: adversarial scope 22 passed; full suite 195 passed, 1 skipped; core suite 189 passed, 7 deselected; diff check passed.
- Assumptions: Optional `toolserver` tests remain separable from core CI.
- Remaining issues: M2.15 awaits manual review.
- Recommended follow-up: Start M2.16 after approval.

### Task M2.16-T1 — Phase 2 Documentation

## Parent milestone

M2.16

## Status

implemented

## Owner role

Documentation agent

## Objective

Update user and architecture documentation to match implemented Phase 2 behavior.

## Scope

- Update architecture policy wording from proposed to implemented.
- Update README with Phase 2 scope and validation commands.
- Update `context-ai.md` with Phase 2 closure and Phase 3 handoff data.

## Explicit exclusions

- No production behavior changes.
- No Phase 3 feature design beyond listed open decisions.

## File scope

### Writable

- `docs/architecture.md`
- `README.md`
- `context-ai.md`

## Dependencies

- M2.15

## Applicable ADRs

- ADR-016 through ADR-025

## Acceptance criteria

- [x] Architecture matches code.
- [x] Tool contracts, configuration and operator validation are documented.
- [x] Phase 3 boundary is documented.

## Validation commands

```bash
rg -n "Phase 2 Proposed|Productive execution remains blocked|Decisiones faltantes para Phase 2|Servicio C prototipo" docs/architecture.md context-ai.md README.md || true
```

## Result report

- Summary: Updated Phase 2 architecture, README and context handoff docs.
- Files changed: `docs/architecture.md`, `README.md`, `context-ai.md`
- Tests run: documentation stale-text scan.
- Test results: no stale Phase 2 proposal text remained.
- Assumptions: `context-ai.md` should describe the current repository state, not historical pre-Phase-2 planning.
- Remaining issues: Final human review pending.
- Recommended follow-up: Phase 3 planning after approval.

### Task M2.16-T2 — Phase 2 ADR Closure

## Parent milestone

M2.16

## Status

implemented

## Owner role

Documentation agent

## Objective

Mark Phase 2 ADRs as implemented and sync the ADR index.

## Scope

- Set ADR-016 through ADR-025 status to `Implemented`.
- Update `docs/adr/README.md`.

## Explicit exclusions

- No ADR rewriting or superseding.
- No decision changes.

## File scope

### Writable

- `docs/adr/ADR-016-*.md` through `docs/adr/ADR-025-*.md`
- `docs/adr/README.md`

## Dependencies

- M2.16-T1

## Applicable ADRs

- ADR-016 through ADR-025

## Acceptance criteria

- [x] All Phase 2 ADRs are `Implemented`.

## Validation commands

```bash
rg -n "Status: Accepted|ADR-0(16|17|18|19|20|21|22|23|24|25).*Accepted" docs/adr || true
```

## Result report

- Summary: Marked Phase 2 ADRs implemented and synced the index.
- Files changed: `docs/adr/ADR-016-*.md` through `docs/adr/ADR-025-*.md`, `docs/adr/README.md`
- Tests run: ADR status scan.
- Test results: no accepted Phase 2 ADR statuses remained.
- Assumptions: Status changes reflect completed implementation from M2.1 through M2.15.
- Remaining issues: Final human review pending.
- Recommended follow-up: None.

### Task M2.16-T3 — Phase 2 Final Validation

## Parent milestone

M2.16

## Status

implemented

## Owner role

Integration validator

## Objective

Validate Phase 2 documentation closure and prepare final manual review.

## Scope

- Run required suites.
- Record optional environment-specific outcomes.
- Produce `.agent/reports/M2.16.md`.
- Update supervisor state.

## Explicit exclusions

- Do not mark M2.16 accepted.
- Do not start Phase 3.

## File scope

### Writable

- `.agent/reports/M2.16.md`
- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`

## Dependencies

- M2.16-T2

## Applicable ADRs

- ADR-013
- ADR-016 through ADR-025

## Acceptance criteria

- [x] Every roadmap criterion has evidence.
- [x] Security review has no blocker.
- [x] Final manual review queue is recorded.
- [x] Phase status becomes accepted after manual approval.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m unit -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m integration -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m contract -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m smoke -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m "not ollama and not toolserver" -q
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m toolserver -q
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -m ollama -q
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
git diff --check
```

## Result report

- Summary: Validated Phase 2 closure and prepared final review.
- Files changed: `.agent/reports/M2.16.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`
- Tests run: unit, integration, contract, smoke, core without external deps, toolserver, ollama optional, full suite, diff check.
- Test results: unit 154 passed; integration 22 passed; contract 12 passed; smoke 1 passed; core 195 passed and 7 deselected after post-review fixes; toolserver 6 passed; ollama passed with `blacksmith-tools`; full suite 201 passed, 1 skipped with `AI_ASSISTANT_MODEL` unset; diff check passed.
- Assumptions: Manual approval was provided by the user after real `gemma4:latest` validation.
- Remaining issues: None for Phase 2.
- Recommended follow-up: Plan Phase 3 separately.

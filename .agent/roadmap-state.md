# Roadmap State

## Project

AI Assistant

## Active phase

Phase 4: Autonomous Execution Platform

## Current milestone

- ID: M4.2
- Name: Approve Phase 4 ADRs
- Status: implemented-awaiting-human-review
- Source: `docs/roadmap-phase-4.md`

## Milestone status vocabulary

- `planned`
- `in-progress`
- `blocked`
- `implemented-awaiting-human-review`
- `accepted`
- `rework-required`

## Milestones

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M1 | Repository hygiene | accepted | — | `.agent/reports/M1.md` | approved |
| M2 | Migration to pytest | accepted | — | `.agent/reports/M2.md` | approved |
| M3 | Explicit sessions | accepted | — | `.agent/reports/M3.md` | approved |
| M4 | Transactional persistence | accepted | — | `.agent/reports/M4.md` | approved |
| M5 | Explicit ports | accepted | — | `.agent/reports/M5.md` | approved |
| M6 | Composition root | accepted | — | `.agent/reports/M6.md` | approved |
| M7 | Centralized configuration | accepted | — | `.agent/reports/M7.md` | approved |
| M8 | Basic logging | accepted | — | `.agent/reports/M8.md` | approved |
| M9 | Typed internal errors | accepted | — | `.agent/reports/M9.md` | approved |
| M10 | Native Ollama adapter | accepted | — | `.agent/reports/M10.md` | approved |
| M11 | Model profiles | accepted | — | `.agent/reports/M11.md` | approved |
| M12 | Context budget | accepted | — | `.agent/reports/M12.md` | approved |
| M13 | Robust OpenAI-compatible adapter | accepted | — | `.agent/reports/M13.md` | approved |
| M14 | Declarative tools | accepted | — | `.agent/reports/M14.md` | approved |
| M15 | Layered repository reorganization | accepted | — | `.agent/reports/M15.md` | approved |
| M16 | CI | accepted | — | `.agent/reports/M16.md` | approved |
| M17 | Documentation and ADR closure | accepted | — | `.agent/reports/M17.md` | approved |

## Phase 2 Milestones

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M2.1 | Approve Phase 2 security decisions | accepted | — | `.agent/reports/M2.1.md` | approved |
| M2.2 | Add tool execution domain models | accepted | — | `.agent/reports/M2.2.md` | approved |
| M2.3 | Add application ports | accepted | — | `.agent/reports/M2.3.md` | approved |
| M2.4 | Implement the static tool catalog | accepted | — | `.agent/reports/M2.4.md` | approved |
| M2.5 | Implement workspace and path policy | accepted | — | `.agent/reports/M2.5.md` | approved |
| M2.6 | Implement deny-by-default tool policy | accepted | — | `.agent/reports/M2.6.md` | approved |
| M2.7 | Add fake and dry-run executors | accepted | — | `.agent/reports/M2.7.md` | approved |
| M2.8 | Implement audit persistence | accepted | — | `.agent/reports/M2.8.md` | approved |
| M2.9 | Implement LocalReadOnlyToolExecutor | accepted | — | `.agent/reports/M2.9.md` | approved |
| M2.10 | Implement ToolExecutionCoordinator | accepted | — | `.agent/reports/M2.10.md` | approved |
| M2.11 | Integrate one bounded tool round into runtime | accepted | — | `.agent/reports/M2.11.md` | approved |
| M2.12 | Add configuration and CLI support | accepted | — | `.agent/reports/M2.12.md` | approved |
| M2.13 | Extend protobuf and C tool service | accepted | — | `.agent/reports/M2.13.md` | approved |
| M2.14 | Implement UnixSocketToolExecutor | accepted | — | `.agent/reports/M2.14.md` | approved |
| M2.15 | Add adversarial security tests | accepted | — | `.agent/reports/M2.15.md` | approved |
| M2.16 | Documentation and final manual review | accepted | — | `.agent/reports/M2.16.md` | approved |

## Phase 3 Milestones

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M3.1 | Close Phase 2 | accepted | — | `.agent/reports/M3.1.md` | approved |
| M3.2 | Approve Phase 3 ADRs | accepted | — | `.agent/reports/M3.2.md` | approved |
| M3.3 | Extend domain models | accepted | — | `.agent/reports/M3.3.md` | approved |
| M3.4 | Implement confirmation service | accepted | — | `.agent/reports/M3.4.md` | approved |
| M3.5 | Implement profile registry | accepted | — | `.agent/reports/M3.5.md` | approved |
| M3.6 | Implement `file_metadata` | accepted | — | `.agent/reports/M3.6.md` | approved |
| M3.7 | Implement `search_text` | accepted | — | `.agent/reports/M3.7.md` | approved |
| M3.8 | Implement `git_status` | accepted | — | `.agent/reports/M3.8.md` | approved |
| M3.9 | Implement `git_diff` | accepted | — | `.agent/reports/M3.9.md` | approved |
| M3.10 | Implement `run_tests` | accepted | — | `.agent/reports/M3.10.md` | approved |
| M3.11 | Implement `build_project` | accepted | — | `.agent/reports/M3.11.md` | approved |
| M3.12 | Implement write policy | accepted | — | `.agent/reports/M3.12.md` | approved |
| M3.13 | Implement atomic C `write` | accepted | — | `.agent/reports/M3.13.md` | approved |
| M3.14 | Make C toolserver primary | accepted | — | `.agent/reports/M3.14.md` | approved |
| M3.15 | Implement retention and purge | accepted | — | `.agent/reports/M3.15.md` | approved |
| M3.16 | Integrate runtime and CLI | accepted | — | `.agent/reports/M3.16.md` | approved |
| M3.17 | Security and adversarial tests | accepted | — | `.agent/reports/M3.17.md` | approved |
| M3.18 | Documentation and final review | accepted | — | `.agent/reports/M3.18.md` | approved |

## Phase 4 Milestones

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M4.0 | Phase 4 scaffolding | implemented-awaiting-human-review | — | `.agent/reports/M4.0.md` | awaiting-review |
| M4.1 | Freeze Phase 3 baseline | accepted | — | `.agent/reports/M4.1.md` | approved |
| M4.2 | Approve Phase 4 ADRs | implemented-awaiting-human-review | — | `.agent/reports/M4.2.md` | awaiting-review |
| M4.3 | Platform domain models | planned | M4.2 requires human review | — | — |

## Current baseline

Record before Phase 3 implementation:

- Date: 2026-08-03
- Git status before M3.1 edits: only untracked `AGENTS-phase-3.md` and `docs/roadmap-phase-3.md`.
- Phase 2 state: M2.1 through M2.16 accepted by human review.
- ADR state: ADR-001 through ADR-025 are `Implemented`; ADR-016 through ADR-025 bind Phase 2 tool safety.
- Productive Phase 2 tools: exact allowlist contains `list_directory` and `read_file`.
- Runtime: one bounded tool round per user turn remains implemented.
- Executor baseline: Python local read-only executor is the configured bootstrap default; Unix socket C executor exists behind the `ToolExecutor` port but is not the default.
- C toolserver: read-only `list_directory` and `read_file` contract tests pass.
- Audit: separate SQLite audit recorder exists with sanitized metadata and explicit failure behavior.
- Phase 3 implementation status: confirmation service, profile registry, all Phase 3 tool names, declarative `write` policy, atomic C `write`, C primary executor, audit retention/purge, runtime/CLI integration, adversarial coverage and final documentation implemented.
- Phase 3 blocker: none.
- Phase 4 implementation status: scaffold packages for platform domain/application/ports and capability roots added; no autonomous execution behavior enabled. M4.1 baseline freeze completed against current Phase 4 roadmap.
- Phase 4 blocker: M4.2 requires human review before productive Phase 4 implementation.
- Phase 4 baseline:
  - Date: 2026-08-05T08:41:00-06:00
  - Git revision: `76773bfb735296ffddab01306dee9f18d662c583`
  - Python: `Python 3.14.6`
  - Git status: user-provided Phase 4 files are modified/untracked; no destructive cleanup performed.
  - Manual/generated artifacts: `__pycache__` and `*.pyc` exist and are ignored by `.gitignore`.
  - ADR state: ADR-001 through ADR-035 Implemented; ADR-036 through ADR-046 Accepted.
  - Initial M4.1 validation issue: stale `tests/test_phase4_docs.py` expected prior M4.0 roadmap text; updated to current M4.1 roadmap.
  - Complete suite: `PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q` -> 347 passed, 1 skipped.
  - Diff check: `git diff --check` -> passed.
- Validation passed:
  - `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_tool_catalog.py tests/test_tool_policy.py tests/test_path_policy.py tests/test_local_read_only_executor.py tests/test_sqlite_audit.py tests/test_tool_coordinator.py tests/test_tool_coordinator_integration.py tests/test_adversarial_security.py tests/test_tools.py tests/test_agent_runtime.py -q` -> 110 passed.
  - `PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_c_toolserver_contract.py tests/test_unix_socket_tool_executor.py -q` -> 13 passed.

## Last supervisor update

- Date: 2026-08-05
- Summary: ADR-036 through ADR-046 accepted by human approval; M4.2 prepared for review.
- Next action: human review of M4.2 before M4.3.

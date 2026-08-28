# Roadmap State

## Project

AI Assistant

## Active phase

Phase 5.2: Runtime Hardening & Audit Remediation

## Current milestone

- ID: M5.2.8 / M5.2.9 / M5.2.10 / M5.2.11 / M5.2.12
- Name: ToolLoopBudget + controller, duplicate guard, progress guard, bounded multi-round chat, final synthesis on exhaustion
- Status: in-progress
- Source: `docs/roadmap-phase-5.2.md`
- Note: M5.2.6/M5.2.7 automatically-accepted after triple independent validation (all PASS, 547 passed/17 skipped, no security regression; `interaction_id` confirmed inert metadata never consulted by ToolPolicy/PathPolicy). ADR-070/ADR-071 remain Accepted (partial implementation, residual items tracked in M5.2.6/M5.2.7 reports). This next block is the core ADR-069 redesign (the actual FINDING-001/003/004/005 remediation) and is handled as one cohesive milestone group since the guards, budget and multi-round loop are mutually dependent inside the same `AgentRuntime` tool-loop redesign.

## Milestone status vocabulary

- `planned`
- `in-progress`
- `blocked`
- `implemented-awaiting-human-review`
- `accepted`
- `rework-required`
- `automatically-accepted`

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
| M4.2 | Approve Phase 4 ADRs | accepted | — | `.agent/reports/M4.2.md` | approved |
| M4.3 | Platform domain models | accepted | — | `.agent/reports/M4.3.md` | approved |
| M4.4 | Planner and evaluator ports | accepted | — | `.agent/reports/M4.4.md` | approved |
| M4.5 | CapabilityRegistry | accepted | — | `.agent/reports/M4.5.md` | approved |
| M4.6 | PlanValidator | accepted | — | `.agent/reports/M4.6.md` | approved |
| M4.7 | ExecutionGraph | accepted | — | `.agent/reports/M4.7.md` | approved |
| M4.8 | BudgetManager | accepted | — | `.agent/reports/M4.8.md` | approved |
| M4.9 | ExecutionStore | accepted | — | `.agent/reports/M4.9.md` | approved |
| M4.10 | Logical checkpoints | accepted | — | `.agent/reports/M4.10.md` | approved |
| M4.11 | Sequential scheduler | accepted | — | `.agent/reports/M4.11.md` | approved |
| M4.12 | Structured planner adapter | accepted | — | `.agent/reports/M4.12.md` | approved |
| M4.13 | Objective evaluator | accepted | — | `.agent/reports/M4.13.md` | approved |
| M4.14 | ExecutionEngine | accepted | — | `.agent/reports/M4.14.md` | approved |
| M4.15 | Objective interface | accepted | — | `.agent/reports/M4.15.md` | approved |
| M4.16 | Observability | accepted | — | `.agent/reports/M4.16.md` | approved |
| M4.17 | Adversarial and regression tests | accepted | — | `.agent/reports/M4.17.md` | approved |
| M4.18 | Documentation and final review | accepted | — | `.agent/reports/M4.18.md` | approved |

## Phase 5 Milestones

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M5.1 | Freeze Phase 4 baseline | accepted | — | `.agent/reports/M5.1.md` | approved |
| M5.2 | Approve ADR-047..061 | accepted | — | `.agent/reports/M5.2.md` | approved |
| M5.3 | Knowledge domain models | accepted | — | `.agent/reports/M5.3.md` | approved |
| M5.4 | KnowledgeSource ports | accepted | — | `.agent/reports/M5.4.md` | approved |
| M5.5 | SQLite KnowledgeStore | accepted | — | `.agent/reports/M5.5.md` | approved |
| M5.6 | Hashing and invalidation | accepted | — | `.agent/reports/M5.6.md` | approved |
| M5.7 | Normalization and chunking | accepted | — | `.agent/reports/M5.7.md` | approved |
| M5.8 | Metadata and symbols | accepted | — | `.agent/reports/M5.8.md` | approved |
| M5.9 | SQLite FTS5 | accepted | — | `.agent/reports/M5.9.md` | approved |
| M5.10 | Manual knowledge CLI | accepted | — | `.agent/reports/M5.10.md` | approved |
| M5.11 | EmbeddingProvider | accepted | — | `.agent/reports/M5.11.md` | approved |
| M5.12 | Embedding storage and similarity | accepted | — | `.agent/reports/M5.12.md` | approved |
| M5.13 | HybridRetriever | accepted | — | `.agent/reports/M5.13.md` | approved |
| M5.14 | Deterministic KnowledgeRanker | accepted | — | `.agent/reports/M5.14.md` | approved |
| M5.15 | ContextCompiler | accepted | — | `.agent/reports/M5.15.md` | approved |
| M5.16 | Planner integration | accepted | — | `.agent/reports/M5.16.md` | approved |
| M5.17 | Synthesis integration | accepted | — | `.agent/reports/M5.17.md` | approved |
| M5.18 | Efficiency observability | accepted | — | `.agent/reports/M5.18.md` | approved |
| M5.19 | Security/freshness/regression suite | accepted | — | `.agent/reports/M5.19.md` | approved |
| M5.20 | Functional evaluation | accepted | — | `.agent/reports/M5.20.md` | approved |
| M5.21 | Documentation and final review | accepted | — | `.agent/reports/M5.21.md` | approved |

## Phase 5.1 Milestones

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M5.1.1 | Freeze Phase 5 baseline | automatically-accepted | — | `.agent/reports/M5.1.1.md` | final-review-only |
| M5.1.2 | Unified command router | automatically-accepted | — | `.agent/reports/M5.1.2.md` | final-review-only |
| M5.1.3 | ConversationContextService | automatically-accepted | — | `.agent/reports/M5.1.3.md` | final-review-only |
| M5.1.4 | ConversationContext compiler | automatically-accepted | — | `.agent/reports/M5.1.4.md` | final-review-only |
| M5.1.5 | Opt-in chat context policy | automatically-accepted | — | `.agent/reports/M5.1.5.md` | final-review-only |
| M5.1.6 | Deterministic retrieval policy | automatically-accepted | — | `.agent/reports/M5.1.6.md` | final-review-only |
| M5.1.7 | Preserve conversational tool loop | automatically-accepted | — | `.agent/reports/M5.1.7.md` | final-review-only |
| M5.1.8 | Metrics exposure | automatically-accepted | — | `.agent/reports/M5.1.8.md` | final-review-only |
| M5.1.9 | Knowledge status UX | automatically-accepted | — | `.agent/reports/M5.1.9.md` | final-review-only |
| M5.1.10 | Presets and operator docs | automatically-accepted | — | `.agent/reports/M5.1.10.md` | final-review-only |
| M5.1.11 | Adversarial/regression suite | automatically-accepted | — | `.agent/reports/M5.1.11.md` | final-review-only |
| M5.1.12 | End-to-end validation | automatically-accepted | — | `.agent/reports/M5.1.12.md` | final-review-only |
| M5.1.13 | Final mini-phase closure | automatically-accepted | — | `.agent/reports/M5.1.13.md` | final-review-only |

## Phase 5.2 Milestones

Baseline audit: `docs/audits/chat-tool-context-audit.md`.
Baseline verdict: `REMEDIATION REQUIRED`.

Mandatory remediation targets: FINDING-001, FINDING-002, FINDING-003, FINDING-004, FINDING-005, FINDING-007, FINDING-008 and FINDING-009.

PASS security/path-recovery controls that must not regress: deny-by-default ToolPolicy; PathPolicy traversal, absolute-path, hidden-path, sensitive-path and symlink-escape denial; write exclusion from path recovery; one-attempt bounded path recovery; full PathPolicy revalidation after recovery; confirmation gates for EXECUTE_PROJECT and WRITE_WORKSPACE; sanitized audit and tool diagnostics.

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M5.2.1 | Freeze remediation baseline | automatically-accepted | — | `.agent/reports/M5.2.1.md` | not-required |
| M5.2.2 | Approve ADR-068..071 | accepted | — | `.agent/human-review.md` | approved |
| M5.2.3 | Implement provider-neutral ModelResponse | automatically-accepted | — | `.agent/reports/M5.2.3.md` | final-review-only |
| M5.2.4 | Ollama termination metadata | automatically-accepted | — | `.agent/reports/M5.2.4.md` | final-review-only |
| M5.2.5 | Ollama context/generation configuration | automatically-accepted | — | `.agent/reports/M5.2.5.md` | final-review-only |
| M5.2.6 | ConversationContextBudget | automatically-accepted | — | `.agent/reports/M5.2.6.md` | final-review-only |
| M5.2.7 | interaction_id | automatically-accepted | — | `.agent/reports/M5.2.7.md` | final-review-only |
| M5.2.8 | ToolLoopBudget and controller | automatically-accepted | Deterministic budget dataclass + executor_operations accounting implemented and validated. | `.agent/reports/M5.2.8.md` | final-review-only |
| M5.2.9 | Duplicate-call guard | automatically-accepted | `DuplicateCallGuard`/`fingerprint` implemented and validated. | `.agent/reports/M5.2.9.md` | final-review-only |
| M5.2.10 | Deterministic progress guard | automatically-accepted | `ProgressGuard` implemented and validated (scope: N consecutive failures, documented decision). | `.agent/reports/M5.2.10.md` | final-review-only |
| M5.2.11 | Bounded multi-round chat | automatically-accepted | `AgentRuntime._run_tool_loop` replaces the ADR-024 single-round path; FINDING-001 remediated. | `.agent/reports/M5.2.11.md` | final-review-only |
| M5.2.12 | Final synthesis on exhaustion | automatically-accepted | `_finish_with_synthesis` implemented; FINDING-003 remediated. | `.agent/reports/M5.2.12.md` | final-review-only |
| M5.2.13 | End-to-end observability | automatically-accepted | Correlated `interaction_id` event stream (context/model/tool/synthesis/completion) implemented; FINDING-008/009 closed. | `.agent/reports/M5.2.13.md` | final-review-only |
| M5.2.14 | Expanded metrics | automatically-accepted | `InteractionMetrics` + CLI `--metrics` line implemented. | `.agent/reports/M5.2.14.md` | final-review-only |
| M5.2.15 | Adversarial/regression suite | automatically-accepted | Full required-scenario list mapped to tests; 3 gaps found and closed. | `.agent/reports/M5.2.15.md` | final-review-only |
| M5.2.16 | Repeat deep audit and close | implemented-awaiting-final-human-review | Independent audit verdict READY TO CONTINUE; all mandatory findings PASS; zero security regressions. | `.agent/reports/phase-5.2-final.md`, `docs/audits/chat-tool-context-audit-post-remediation.md` | required |

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
- Phase 4 blocker: none; M4.18 received final human approval.
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

- Date: 2026-08-18
- Summary: Phase 5 accepted after human approval of M5.21.
- Date: 2026-08-19
- Summary: Phase 5.1 M5.1.1 and M5.1.2 automatically accepted under looped validation. ADR-047 through ADR-061 corrected to Implemented after Phase 5 acceptance evidence.
- Date: 2026-08-19
- Summary: M5.1.3 automatically accepted after corrective conversation-purpose separation.
- Date: 2026-08-19
- Summary: M5.1.4 automatically accepted after conversation compiler entry point validation.
- Date: 2026-08-19
- Summary: M5.1.5 automatically accepted after opt-in context policy and retrieval-provider boundary correction.
- Date: 2026-08-19
- Summary: M5.1.6 automatically accepted after live-state bypass correction.
- Date: 2026-08-19
- Summary: M5.1.7 automatically accepted after direct live-state bypass correction and tool-loop validation.
- Date: 2026-08-19
- Summary: M5.1.8 automatically accepted after env metrics correction and validation.
- Date: 2026-08-19
- Summary: M5.1.9 automatically accepted after lifecycle status and query diagnostics validation.
- Date: 2026-08-19
- Summary: M5.1.10 automatically accepted after operator profile and workflow docs validation.
- Date: 2026-08-19
- Summary: M5.1.11 automatically accepted after stale-index corrective coverage and adversarial regression validation.
- Date: 2026-08-19
- Summary: M5.1.12 automatically accepted after end-to-end mini-phase scenario validation.
- Date: 2026-08-19
- Summary: M5.1.13 automatically accepted after final regression, ADR-062 through ADR-067 approval alignment, symlink-confinement corrective loop, reusable CLI context reset, independent integration validation, architecture review, and security revalidation.
- Phase 5.1 status: implemented-awaiting-final-human-review.
- Next action: final human review of the complete Phase 5.1 package.
- Date: 2026-08-27
- Summary: Phase 5.2 started from `docs/audits/chat-tool-context-audit.md` with baseline verdict `REMEDIATION REQUIRED`; M5.2.1 selected as the next eligible milestone. FINDING-001, FINDING-002 and FINDING-003 reproduced from focused tests, source inspection and diagnostic logs. ADR-068 through ADR-071 remain Proposed; M5.2.2 is a human approval gate before superseding ADR-024 or implementing bounded multi-round chat.
- Date: 2026-08-28
- Summary: M5.2.1 automatically-accepted after independent validation from three dedicated subagents: (1) test agent independently re-reproduced FINDING-001/002/003 from source and tests (`tests/test_agent_runtime.py`, `tests/test_ollama_model.py`, 24 passed) with verdict REPRODUCED for all three; (2) security reviewer independently re-verified all 9 listed PASS security/path-recovery controls with verdict PASS for each and a 156-test regression slice fully green; (3) architecture reviewer confirmed ADR-024 remains Implemented and enforced, ADR-068 through ADR-071 remain Proposed and correctly absent from `docs/adr/README.md`'s index, the M5.2.2 human gate is correctly modeled in the roadmap with every downstream milestone blocked behind the relevant ADR, and found zero premature implementation of anything gated by ADR-068/069/070/071. No previously-PASS security/path-recovery control regressed. Supervisor selected M5.2.2 (Approve ADR-068..071) as the next eligible milestone and stopped there per the mandatory human-approval gate; no implementation work was started.
- Phase 5.2 status: M5.2.1 automatically-accepted; M5.2.2 blocked pending human ADR approval.
- Date: 2026-08-28
- Summary: Human approved ADR-068 through ADR-071 ("he revisado los ADR, aprobados"). ADR statuses updated Proposed -> Accepted; `docs/adr/README.md` index updated. M5.2.2 recorded accepted in `.agent/human-review.md`. Supervisor selected M5.2.3 (Implement provider-neutral ModelResponse) as the next eligible milestone and begins implementation.
- Phase 5.2 status: in-progress (M5.2.3).
- Date: 2026-08-28
- Summary: M5.2.3 (provider-neutral `ModelResponse`, ADR-068), M5.2.4 (Ollama termination metadata) and M5.2.5 (Ollama explicit `num_ctx`/`num_predict`) implemented in one coherent change set (implementation delegated to a context-sharing fork, since it required mechanical-but-precise edits across every model provider and ~13 test files; architecture decisions and validation stayed with the supervisor). Full regression `542 passed, 17 skipped` (+4 new tests, 0 failures). Three independent subagents (test agent, security reviewer, architecture reviewer) each returned unanimous PASS with no security/path-recovery/ADR-024 regression. ADR-068 moved `Accepted -> Implemented`. Reports: `.agent/reports/M5.2.3.md`, `.agent/reports/M5.2.4.md`, `.agent/reports/M5.2.5.md`. Selected next: M5.2.6 (ConversationContextBudget) + M5.2.7 (interaction_id).
- Phase 5.2 status: in-progress (M5.2.6/M5.2.7).
- Date: 2026-08-28
- Summary: M5.2.6 (`ConversationContextBudget`, unifying char/word/token budget enforcement onto one `estimate_tokens` unit plus an explicit reserved-output accounting) and M5.2.7 (`interaction_id` generated once per turn and threaded through `ToolExecutionRequest`/diagnostics/audit) implemented directly by the supervisor (judgment-heavy: required rewriting test fixtures whose semantics changed under word-count budgeting, not delegated). Full regression `547 passed, 17 skipped` (+2 new tests). Three independent subagents (test agent, security reviewer, architecture reviewer) each returned unanimous PASS. ADR-070/ADR-071 remain `Accepted` (each only partially satisfied so far; residual coordination items tracked in the milestone reports for M5.2.13/closure). Reports: `.agent/reports/M5.2.6.md`, `.agent/reports/M5.2.7.md`. Selected next: M5.2.8-M5.2.12 as one cohesive group (ADR-069's bounded multi-round tool loop with duplicate/progress guards and final synthesis — the actual FINDING-001/003/004/005 remediation).
- Phase 5.2 status: in-progress (M5.2.8-M5.2.12).
- Date: 2026-08-28
- Summary: M5.2.8 (`ToolLoopBudget` + `executor_operations` accounting), M5.2.9 (`DuplicateCallGuard`), M5.2.10 (`ProgressGuard`), M5.2.11 (bounded multi-round `AgentRuntime._run_tool_loop`, the ADR-069 core remediation replacing the ADR-024 hard single-round cap) and M5.2.12 (`_finish_with_synthesis` on exhaustion) implemented directly by the supervisor as one cohesive change set (`ai_assistant/application/tool_loop.py` new; `ai_assistant/domain/tools.py`, `ai_assistant/application/tool_coordinator.py`, `ai_assistant/application/runtime.py` edited). This is the literal remediation of FINDING-001 (legitimate two-step tool workflows previously rejected), FINDING-003 (raw rejection artifact replaced by real synthesized final answer on exhaustion), and the deterministic half of FINDING-004/005 (duplicate/no-progress rejection, auditable budget). Three existing tests that encoded the old ADR-024 single-round-rejection behavior were deliberately renamed and rewritten to assert the new bounded-multi-round behavior instead (their failure under the new code was the correct signal of an intentional behavior change, not a regression). Full regression `561 passed, 17 skipped, 0 failures`; `git diff --check` clean. Three independent subagents (test agent, security reviewer, architecture reviewer) each returned unanimous PASS across all checks (5/5, 7/7, 6/6 respectively), with a 181-test security/tool-loop regression slice green and no previously-PASS security/path-recovery control regressed. Architecture reviewer flagged ADR-024 as stale (`Implemented` with no `Superseded by:` despite ADR-069 already declaring `Supersedes: ADR-024`) and recommended fixing this immediately; applied immediately: `docs/adr/ADR-024-*.md` and `docs/adr/README.md` updated to `Status: Superseded` / `Superseded by: ADR-069`, `AGENTS.md` ADR-governance section updated to match. ADR-069/070/071 deliberately remain `Accepted` (not `Implemented`) per the reviewer's explicit recommendation to defer that promotion to full Phase 5.2 closure (M5.2.16), since ADR-070/071 are not yet fully satisfied end-to-end. Reports: `.agent/reports/M5.2.8.md` (detailed), `.agent/reports/M5.2.9.md`, `M5.2.10.md`, `M5.2.11.md`, `M5.2.12.md` (pointers). Selected next: M5.2.13 (end-to-end observability) grouped with M5.2.14 (expanded metrics), since both extend the same `interaction_id`/diagnostics surface.
- Phase 5.2 status: in-progress (M5.2.13/M5.2.14).
- Date: 2026-08-28
- Summary: M5.2.13 (end-to-end observability, ADR-070) and M5.2.14 (expanded metrics) implemented directly by the supervisor. New `InteractionStage`/`InteractionLogEvent` (domain), `InteractionDiagnosticLogger` port, `InteractionDiagnostics` helper, `JsonlInteractionDiagnosticLogger` (writes into the SAME physical JSONL file as the existing tool-diagnostics logger, so one file correlates a full turn by `interaction_id`), and `InteractionMetrics` (application). `AgentRuntime` now emits correlated events for context/retrieval, every model request/response, tool activity, final synthesis and interaction completion, and exposes `last_interaction_metrics`; `chat --metrics` prints it. While closing this out, also closed the FINDING-008 residual gap noted in M5.2.6's report: `ConversationContextBudget` (context_limit/reserved_output_tokens) and Ollama's `num_ctx`/`num_predict` now land in one observable per-turn record (`ConversationContextService.budget` made public; `AgentRuntime` gained `ollama_num_ctx`/`ollama_num_predict` fields wired from existing M5.2.5 config). Full regression `575 passed, 17 skipped, 0 failures`; `git diff --check` clean. **Two real, non-obvious bugs were found and fixed via live smoke-testing (not caught by unit tests using in-memory fake sinks, which never exercise the real sanitizer)**: `redact_sensitive()` in `ai_assistant/infrastructure/sanitization.py` does substring matching on sensitive keywords including "token"/"prompt", so JSONL payload keys `prompt_tokens`/`output_tokens` and later `reserved_output_tokens`/`max_input_tokens` were silently blanked to `"[redacted]"`; fixed both times by renaming ONLY the colliding JSONL payload dict keys (to `input_length`/`output_length` and `reserved_output_length`/`max_input_length` respectively) — never the underlying dataclass fields or CLI labels — and adding dedicated regression tests that round-trip through the real `JsonlInteractionDiagnosticLogger` to prove it. `redact_sensitive()`'s root-cause substring-matching design is left unfixed and tracked as a residual item for M5.2.15/M5.2.16 (a broad change to a shared security-critical sanitizer deserves its own focused review). Independent validation: round 1, three parallel subagents (test/security/architecture) each returned unanimous PASS (7/7, 7/7, and PASS-with-2-concerns respectively — the architecture reviewer flagged the FINDING-008 gap and the sanitizer root cause, both addressed as described above); round 2, one focused follow-up review of the FINDING-008 closure addendum, PASS on all 5 checks including live reproduction of the second redaction bug and its fix. Reports: `.agent/reports/M5.2.13.md` (detailed), `.agent/reports/M5.2.14.md` (pointer). ADR-070/071 remain `Accepted` (deferred to M5.2.16 per standing plan). Selected next: M5.2.15 (dedicated adversarial/regression suite pass).
- Phase 5.2 status: in-progress (M5.2.15).
- Date: 2026-08-28
- Summary: M5.2.15 completed by cross-referencing every required scenario in `docs/roadmap-phase-5.2.md` (two-tool discovery/read success, bounded three-round flow, excess round rejection, duplicate success/failure, changed strategy after failure, no-progress case, path recovery, budget exhaustion synthesis, Ollama STOP/LENGTH, truncation surfaced, context reserve, interaction correlation, Phase 1-5.1 regressions) against the accumulated test suite. Found and closed 3 genuine gaps at the `AgentRuntime` integration level (unit-level guard behavior existed but no runtime-level proof): `test_runtime_rejects_duplicate_tool_call_after_an_identical_failure`, `test_runtime_allows_a_changed_strategy_to_succeed_after_a_failure`, `test_runtime_completes_a_full_bounded_three_round_flow_without_exhaustion` (all added to `tests/test_agent_runtime.py`). Full regression `578 passed, 17 skipped, 0 failures`; `git diff --check` clean. No production code changed (test-only milestone); full independent triple-review judged disproportionate and skipped in favor of documented self-verification (each new test's claimed code path hand-traced against the actual implementation). Report: `.agent/reports/M5.2.15.md` (includes the full closure mapping table). Next: M5.2.16 — the required final human-gate closure milestone (full regression, independent repeat audit, `docs/audits/chat-tool-context-audit-post-remediation.md`, `.agent/reports/phase-5.2-final.md`, phase status `implemented-awaiting-final-human-review`).
- Phase 5.2 status: in-progress (M5.2.16 — final closure, required human gate).
- Date: 2026-08-28
- Summary: M5.2.16 executed. A fresh, independent audit agent (with no access to this session's context, instructed not to trust milestone self-reports) repeated the original deep audit against current source, ran the full suite fresh (578 passed/17 skipped/0 failed), and personally constructed and read live reproductions (a real `AgentRuntime` via `create_application()`, a scripted model, a real JSONL diagnostics sink) rather than trusting any milestone report's description. Wrote `docs/audits/chat-tool-context-audit-post-remediation.md`: verdict **READY TO CONTINUE**. All 8 mandatory/near-mandatory findings (FINDING-001 through 005, 007, 008, 009) confirmed genuinely PASS with live evidence. Zero security/path-recovery regressions found (C toolserver untouched entirely; every previously-PASS PathPolicy/recovery/confirmation control re-verified). One new, previously-undocumented residual found: `redact_sensitive`'s path-value redaction over-redacts the literal `"."` path segment (over-redaction only, no under-redaction, same category/severity as the already-tracked token-key residual) — added to the backlog, not a blocker. Audit explicitly recommended promoting ADR-069/070/071 from `Accepted` to `Implemented`, finding no gap between what those ADRs promise and what the code/tests/live reproduction do; applied immediately (`docs/adr/ADR-069/070/071-*.md`, `docs/adr/README.md`). Wrote `.agent/reports/phase-5.2-final.md` mapping every baseline finding to its final status. Full suite re-confirmed green after the ADR edits: `578 passed, 17 skipped, 0 failures`; `git diff --check` clean.
- **Phase 5.2 status: implemented-awaiting-final-human-review. STOPPING here per the required human gate — no further Phase 5.2 or Phase 5.3 work begins until the project owner explicitly reviews and approves this closure package.**

# Phase 4 Roadmap — Agent Execution Engine

## Objective

Evolve the project into a local-first **Agent Execution Platform**.

Phase 4 must receive an objective, generate and validate a structured plan, build a task DAG, execute several read-only capabilities sequentially, enforce budgets, persist execution state, create logical checkpoints, evaluate evidence and return a final outcome.

## Product model

```text
Objective
→ Planner
→ PlanValidator
→ ExecutionGraph
→ ExecutionEngine
→ CapabilityRegistry
→ Existing policy/audit/tool execution
→ Evaluator
→ Outcome
```

The conversational assistant remains a client of the platform.

## Phase 4 safety boundary

Autonomous plans may use:

- InspectDirectory (`list_directory`)
- ReadFile (`read_file`)
- InspectFileMetadata (`file_metadata`)
- SearchText (`search_text`)
- InspectGitStatus (`git_status`)
- InspectGitDiff (`git_diff`)
- RunTests (`run_tests`)
- BuildProject (`build_project`)

Autonomous plans may not use `write`, shell, network, package installation, arbitrary commands, dynamic tools, retries, replanning, parallel execution or subagents.

The Phase 3 controlled write path remains available outside ExecutionEngine.

## Default budget

```text
max_tasks = 5
max_model_calls = 4
max_tool_calls = 4
max_duration_seconds = 120
max_output_bytes = 262144
max_writes = 0
max_replans = 0
```

The platform, not the model, owns these limits.

## New domain concepts

- `Objective`
- `Plan`
- `Task`
- `Execution`
- `ExecutionBudget`
- `Checkpoint`
- `ExecutionResult`
- `EvaluationResult`

Suggested objective states:

```text
created planning planned executing evaluating completed failed cancelled blocked
```

Suggested task states:

```text
pending ready running succeeded failed skipped blocked cancelled
```

Suggested execution states:

```text
created running paused completed failed cancelled budget_exceeded
```

## New ports and services

### Planner

Creates a provider-neutral structured plan. It never executes capabilities.

### PlanValidator

Validates schema, IDs, dependencies, DAG acyclicity, capabilities, arguments and budgets.

### CapabilityRegistry

Maps abstract capabilities to existing approved tools without exposing executor details.

### Scheduler

Selects ready tasks deterministically and executes one task at a time.

### ExecutionStore

Persists objectives, plans, task states, executions and checkpoints. It remains separate from ConversationStore and AuditStore.

### BudgetManager

Checks and atomically records task, model-call, tool-call, duration and output usage.

### Evaluator

Compares results against objective completion criteria and deterministic evidence. Model text may summarize evidence but cannot override failed criteria.

### CheckpointManager

Persists logical execution metadata. Phase 4 includes no filesystem snapshot or rollback.

## Milestones

### M4.1 — Freeze Phase 3 baseline

- Record Phase 3 as accepted.
- Run the current complete suite.
- Run `git diff --check`.
- Clean or ignore manual artifacts.
- Record Git revision, environment and existing failures.

Acceptance: the working tree and Phase 3 baseline are understood and reproducible.

### M4.2 — Approve Phase 4 ADRs

Create and approve ADR-036 through ADR-046.

Acceptance: platform direction, models, graph, budgets, persistence, planner, evaluator, checkpoints and read-only autonomy are explicit.

### M4.3 — Platform domain models

Implement provider-neutral models and validated state transitions.

Acceptance: no SQLite, Ollama, protobuf or toolserver dependency leaks into domain.

### M4.4 — Planner and evaluator ports

Add structured contracts plus deterministic fakes.

Acceptance: core depends on ports only; malformed results are rejected.

### M4.5 — CapabilityRegistry

Map abstract capabilities to existing tools. Do not expose write.

Acceptance: unknown capabilities are rejected and planner receives capability metadata only.

### M4.6 — PlanValidator

Validate unique task IDs, existing dependencies, cycles, task limits, capabilities, arguments and budgets.

Acceptance: write attempts, unknown tools, cycles and excessive plans have stable rejection codes.

### M4.7 — ExecutionGraph

Create an immutable validated DAG with deterministic ready-task selection.

Acceptance: dependency success unlocks tasks; failed dependencies block dependents.

### M4.8 — BudgetManager

Enforce all default and configured hard limits.

Acceptance: budget exhaustion stops execution deterministically before the next forbidden call.

### M4.9 — ExecutionStore

Implement a dedicated SQLite adapter with transactional task/execution transitions.

Acceptance: restart can reload execution state; conversation and audit semantics remain separate.

### M4.10 — Logical checkpoints

Checkpoint after each successful task and restore execution metadata.

Acceptance: no checkpoint claims filesystem rollback.

### M4.11 — Sequential scheduler

Run one ready task at a time, in dependency order, without retry or parallelism.

Acceptance: state is persisted around transitions and blocking failures stop dependent work.

### M4.12 — Structured planner adapter

Use existing ModelProvider infrastructure to request strict structured plans.

Acceptance: invalid JSON and unknown capabilities never reach scheduling; Ollama tests remain optional.

### M4.13 — Objective evaluator

Evaluate mandatory criteria, task states and evidence before optional model summarization.

Acceptance: model output cannot transform failed evidence into success.

### M4.14 — ExecutionEngine

Coordinate objective creation, planning, validation, graph, scheduling, checkpoints and evaluation.

Acceptance: no concrete Ollama, SQLite or C imports; capability execution still crosses existing policy/audit coordinator.

### M4.15 — Objective interface

Add an explicit CLI path without replacing current chat behavior.

Example:

```bash
python main.py objective "Determine why tests fail"
```

Acceptance: displays plan, budget, task progress, evidence and sanitized final outcome.

### M4.16 — Observability

Log objective, execution, plan, task transitions, budget use, checkpoint and final status without prompts or file content.

### M4.17 — Adversarial and regression tests

Required cases:

- unknown capability;
- attempted write;
- arbitrary command;
- duplicate IDs;
- missing dependency;
- cycle;
- excessive tasks/calls/duration/output;
- failed dependency;
- parallel or replan attempt;
- checkpoint tampering;
- evaluator false success;
- Phase 1–3 regressions.

### M4.18 — Documentation and final review

Update architecture, roadmap, ADR index, domain model, planner contract, graph, budgets, store, checkpoint, evaluator, CLI and testing docs.

Final acceptance requires all tests, security review and manual review.

## ADR plan

- ADR-036 Agent Execution Platform Direction
- ADR-037 Objective, Plan, Task and Execution Models
- ADR-038 Capability Registry
- ADR-039 Execution Graph Validation
- ADR-040 Deterministic Sequential Scheduler
- ADR-041 Execution Budgets
- ADR-042 Execution State Persistence
- ADR-043 Structured Planner Contract
- ADR-044 Objective Evaluation
- ADR-045 Logical Checkpoint Semantics
- ADR-046 Read-Only Multi-Step Phase 4

## Explicit exclusions

- autonomous write;
- rollback snapshots;
- retries;
- replanning;
- parallel execution;
- subagents;
- multiagent runtime;
- dynamic capabilities;
- remote executors;
- network tools;
- shell;
- RAG, embeddings or semantic memory;
- streaming;
- TUI or web UI.

## Completion criteria

Phase 4 is accepted only when:

- ADR-036 through ADR-046 are Implemented;
- objective execution works end-to-end;
- all plans are validated;
- the registry excludes write;
- scheduling is deterministic and sequential;
- budgets are enforced;
- execution state and logical checkpoints persist;
- evaluation is evidence-driven;
- Phase 1–3 behavior remains compatible;
- automated tests pass;
- manual review findings are resolved.

# Phase 4 Roadmap — Autonomous Execution Platform

## Objective

Prepare a bounded planning and execution platform on top of the accepted Phase 3 tool safety layer.

Phase 4 is not active until its ADRs are proposed and approved.

## Initial Structure

```text
ai_assistant/
├── platform/
│   ├── domain/
│   ├── application/
│   └── ports/
└── capabilities/
    ├── filesystem/
    ├── git/
    └── project/
```

## M4.0 — Phase 4 scaffolding

Implemented:

- platform domain package;
- platform application package;
- platform ports package;
- capability package roots;
- import and validation tests.

Explicitly not implemented:

- autonomous multi-step execution;
- model-generated command execution;
- new filesystem mutations;
- network tools;
- persistent approvals;
- new production dependencies.

## Approval Gates

Before implementation milestones, Phase 4 requires ADRs for:

- objectives, plans, tasks and execution state;
- execution budgets and stop conditions;
- checkpoint persistence;
- scheduler behavior;
- evaluator criteria;
- capability registry rules;
- new filesystem operations, if any;
- any expansion beyond Phase 3 one-tool-round behavior.


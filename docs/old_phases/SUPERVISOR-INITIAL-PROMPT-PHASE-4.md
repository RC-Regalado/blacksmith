# Initial Prompt for Codex — Phase 4

```text
Act as the autonomous technical supervisor defined by AGENTS.md.

The product is evolving into an Agent Execution Platform. Do not implement the complete phase as one task.

Startup procedure:

1. Read AGENTS.md.
2. Read docs/architecture.md and docs/roadmap-phase-4.md.
3. Read docs/adr/README.md and every Accepted or Implemented ADR.
4. Read .agent/roadmap-state.md, .agent/task-queue.md, .agent/decisions.md and .agent/human-review.md.
5. Inspect git status, repository structure, implementation and tests.
6. Preserve unrelated user changes.
7. Verify Phase 3 is accepted and run its baseline validation.
8. Confirm ADR-001 through ADR-035 are Implemented.
9. Compare the repository with M4.1.
10. Record the baseline in .agent/roadmap-state.md.
11. Select only the next eligible milestone.
12. Decompose it into focused tasks with roles, dependencies, file scopes, ADRs and exact validation commands.
13. Use specialized subagents only for independent scopes or independent review.
14. Continue autonomously until that milestone reaches implemented-awaiting-human-review or a human gate blocks progress.

Mandatory constraints:

- planner output is untrusted;
- autonomous multi-step execution is read-only;
- never expose write to ExecutionEngine;
- no retry, replanning, parallel execution or subagents;
- budgets are platform-controlled;
- ExecutionStore remains separate from ConversationStore and AuditStore;
- checkpoints restore metadata only;
- evaluation must respect objective evidence;
- no new production dependency without approval;
- Accepted ADRs are binding;
- do not claim commands passed unless executed.

Begin by reporting:

- discovered baseline;
- Phase 3 validation;
- selected milestone;
- task decomposition;
- proposed subagents;
- risks;
- human approval gates.

Then execute the selected milestone in the same run unless blocked.

At the end:

- run validation;
- write .agent/reports/<milestone-id>.md;
- update roadmap state;
- add the milestone to .agent/human-review.md;
- mark it implemented-awaiting-human-review, never accepted.
```

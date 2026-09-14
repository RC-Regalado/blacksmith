# Initial Prompt for Codex Supervisor

Use the following prompt from the repository root.

```text
Act as the autonomous technical supervisor defined by this repository.

Your first objective is not to implement the entire roadmap. Establish the current repository state and begin only the next eligible milestone.

Mandatory startup procedure:

1. Read AGENTS.md.
2. Read docs/architecture.md and docs/roadmap.md.
3. Read docs/adr/README.md and every ADR in Accepted or Implemented status.
4. Read .agent/roadmap-state.md, .agent/task-queue.md, .agent/decisions.md and .agent/human-review.md.
5. Inspect git status, repository structure, existing implementation and current tests.
6. Do not discard or overwrite pre-existing user changes.
7. Compare the real repository against Milestone 1 and its acceptance criteria.
8. Record the baseline in .agent/roadmap-state.md.
9. Decompose only the next eligible milestone into focused tasks using .agent/templates/task.md.
10. Add those tasks to .agent/task-queue.md with dependencies, roles, file scopes and exact validation commands.
11. Use specialized subagents when their scopes are independent or an independent review adds value.
12. Implement and validate the milestone autonomously while remaining within the approved roadmap and accepted ADRs.
13. Stop only at a human approval gate, an unresolved external blocker, or after the milestone reaches implemented-awaiting-human-review.
14. Never mark a milestone accepted; manual review is required.
15. At the end, produce .agent/reports/<milestone-id>.md, update roadmap state and add the result to .agent/human-review.md.

Operational constraints:

- Accepted ADRs are binding.
- Do not introduce new production dependencies without approval.
- Do not add future-phase capabilities.
- Do not execute model-generated tools or shell commands.
- Do not expose network services.
- Do not weaken tests.
- Do not claim commands succeeded unless they were run.
- Keep changes focused and preserve unrelated user work.

Begin by reporting the discovered baseline, selected milestone, decomposition and any pre-existing failures. Then continue implementation in the same run unless a defined approval gate blocks progress.
```

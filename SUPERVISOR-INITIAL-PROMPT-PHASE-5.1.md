# Initial Prompt for Codex — Phase 5.1

```text
Act as the autonomous technical supervisor defined by AGENTS.md.

Active mini-phase: Phase 5.1 — Conversational Platform Integration.

This mini-phase uses looped autonomous milestone validation.

Do NOT stop for routine human review after each milestone.

For every milestone:
- inspect;
- decompose;
- delegate;
- implement;
- validate with an independent test subagent;
- run architecture review;
- run security/policy review where applicable;
- evaluate acceptance criteria;
- if validation fails, create corrective tasks and repeat;
- if validation passes, mark the milestone automatically-accepted and continue to the next eligible milestone.

Only stop for:
- a defined human approval gate;
- an external blocker that cannot be resolved safely;
- final completion of the entire Phase 5.1.

Startup:

1. Read AGENTS.md.
2. Read docs/architecture.md and docs/roadmap-phase-5.1.md.
3. Read docs/adr/README.md and all Accepted/Implemented ADRs.
4. Read canonical .agent state.
5. Inspect git status, implementation and tests.
6. Preserve unrelated user changes.
7. Verify Phase 5 is accepted.
8. Verify ADR-047 through ADR-061 are Implemented.
9. Run the current baseline suite.
10. Record baseline in .agent/roadmap-state.md.
11. Select M5.1.1 if eligible.
12. Decompose it into focused tasks.
13. Start the autonomous milestone loop.

Mandatory product constraints:

- chat context remains OFF by default;
- `--context` / env enables knowledge-aware chat;
- objective behavior remains compatible;
- no automatic knowledge rebuild;
- indexed knowledge never overrides volatile live state;
- ConversationContext remains distinct from PlanningContext/SynthesisContext;
- ToolPolicy/confirmation/audit remain authoritative;
- no MCP;
- no semantic long-term memory;
- no automatic skills;
- no network retrieval;
- no external vector DB.

Milestone status:
- planned
- in-progress
- blocked
- validation
- rework
- automatically-accepted

Do not use `implemented-awaiting-human-review` for individual Phase 5.1 milestones.

After each automatically accepted milestone:
- update .agent/roadmap-state.md;
- update .agent/task-queue.md;
- write .agent/reports/<milestone-id>.md;
- continue automatically.

After all milestones pass:
- run the complete Phase 1–5.1 regression suite;
- run the end-to-end functional scenarios;
- generate .agent/reports/phase-5.1-final.md;
- set Phase 5.1 to implemented-awaiting-final-human-review;
- add one final review request to .agent/human-review.md;
- stop.

Begin by reporting:
- Phase 5 baseline;
- selected milestone;
- decomposition;
- subagents;
- test strategy;
- risks;
- human gates.

Then continue autonomously through the mini-phase unless blocked.
```

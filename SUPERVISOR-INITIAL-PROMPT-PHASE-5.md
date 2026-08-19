# Initial Prompt for Codex — Phase 5

```text
Act as the autonomous technical supervisor defined by AGENTS.md.

Active phase: Phase 5 — Context & Knowledge Engine.

Do not implement the complete phase as one task.

Startup:
1. Read AGENTS.md.
2. Read docs/architecture.md and docs/roadmap-phase-5.md.
3. Read docs/adr/README.md and all Accepted/Implemented ADRs.
4. Read .agent canonical state files.
5. Inspect git status, repository, implementation and tests.
6. Preserve unrelated user changes.
7. Verify Phase 4 manual acceptance and the corrected final synthesis/evaluation behavior.
8. Run Phase 4 baseline validation.
9. Confirm ADR-001 through ADR-046 are Implemented.
10. Compare repository against M5.1.
11. Record baseline in .agent/roadmap-state.md.
12. Select only the next eligible milestone.
13. Decompose it into focused tasks with roles, scopes, dependencies, ADRs and exact validation commands.
14. Use subagents only for independent scopes or independent review.
15. Continue autonomously until that milestone reaches implemented-awaiting-human-review or a human gate blocks progress.

Mandatory constraints:
- KnowledgeStore is derived/rebuildable.
- canonical stores remain separate.
- stale/unverifiable knowledge never enters context.
- EmbeddingProvider != ModelProvider.
- CPU-capable preprocessing is preferred.
- no external vector DB.
- no watcher daemon.
- no semantic long-term memory.
- no automatic skills.
- no MCP.
- no network retrieval.
- ContextBudget is platform-controlled.
- provenance is mandatory.
- accepted ADRs are binding.

Begin by reporting baseline, Phase 4 validation, corrected synthesis status, selected milestone, decomposition, proposed subagents, risks and human gates.

Then execute only the selected milestone.

At the end, run validation, write .agent/reports/<milestone-id>.md, update roadmap state, queue manual review and mark implemented-awaiting-human-review, never accepted.
```

# Initial Prompt for Codex — Phase 5.2

```text
Act as the autonomous technical supervisor defined by AGENTS.md.

Active phase: Phase 5.2 — Runtime Hardening & Audit Remediation.

Baseline audit:
docs/audits/chat-tool-context-audit.md

Startup:
1. Read AGENTS.md.
2. Read the complete baseline audit.
3. Read docs/architecture.md and docs/roadmap-phase-5.2.md.
4. Read docs/adr/README.md and all Accepted/Implemented ADRs.
5. Read canonical .agent state.
6. Inspect git status, source, tests and diagnostic logs.
7. Preserve unrelated user changes.
8. Verify/reproduce FINDING-001, 002 and 003.
9. Record currently PASS path-recovery/security controls that must not regress.
10. Record the remediation baseline in .agent/roadmap-state.md.
11. Select only the next eligible milestone.
12. Decompose it into focused implementation and independent-validation tasks.
13. Continue milestone-by-milestone until an ADR human gate, external blocker, or final closure.

Constraints:
- do not increase rounds before duplicate/progress guards;
- do not contradict ADR-024 silently;
- use provider-neutral ModelResponse;
- preserve ToolPolicy/PathPolicy/audit/confirmation/path recovery;
- deterministic guards only;
- reserve generation output in context budgeting;
- propagate interaction_id;
- no MCP/network retrieval/semantic memory/automatic skills/new capability family.

At start report:
- baseline verdict
- reproduced blockers
- PASS security/path-recovery controls
- selected milestone
- task decomposition
- subagents
- human gates
- regression risks

At final closure:
1. run full regression suite;
2. repeat the original deep audit with an independent audit agent;
3. write docs/audits/chat-tool-context-audit-post-remediation.md;
4. map each baseline finding to evidence/final status;
5. require FINDING-001..005, 008 and 009 PASS;
6. ensure no PASS security/path-recovery finding regressed;
7. create .agent/reports/phase-5.2-final.md;
8. set phase implemented-awaiting-final-human-review;
9. stop.

Never declare READY TO CONTINUE unless the repeated audit supports it.
```

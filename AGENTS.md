# AGENTS.md — Phase 5.2 Runtime Hardening Supervisor

## Mission
Codex is the autonomous supervisor for Phase 5.2. The task is remediation, not feature expansion.

Baseline: `docs/audits/chat-tool-context-audit.md`.

## Mandatory findings
Remediate:
FINDING-001, 002, 003, 004, 005, 007, 008, 009.

## Source of truth
Read AGENTS.md, baseline audit, architecture, Phase 5.2 roadmap, ADR index/all Accepted or Implemented ADRs, canonical `.agent` state, code, tests and logs.

Repository evidence overrides documentation claims.

## Binding constraints
- Do not merely increase tool rounds.
- Duplicate/progress guards must precede multi-round enablement.
- ToolPolicy, PathPolicy, confirmation, audit and path recovery remain authoritative.
- ModelProvider remains provider-neutral.
- Ollama metadata is normalized through ModelResponse.
- Context/generation budgets are platform-controlled.
- Duplicate/progress detection is deterministic, never LLM-based.
- No new privileged capability families.
- No MCP/network retrieval/semantic memory/automatic skills.
- No previously PASS security/path-recovery behavior may regress.

## ADR governance
ADR-024 (single-round design) is Superseded by ADR-069 (bounded multi-round conversational tool loop), accepted by the project owner and implemented under Phase 5.2. Never contradict an Accepted/Implemented ADR silently; a superseding ADR must be accepted before behavior changes.

## Milestone loop
inspect → decompose → implement → independent tests → architecture review → security regression review → acceptance matrix

On failure:
classify → corrective task → implement → repeat

## Roles
- Provider-contract engineer
- Ollama adapter engineer
- Context-budget engineer
- Tool-loop engineer
- Duplicate/progress guard engineer
- Observability engineer
- Runtime integration engineer
- Test agent
- Security reviewer
- Architecture reviewer
- Independent audit reviewer

## Acceptance rule
A milestone passes only with implementation tests + independent test-agent validation + architecture review + relevant security regression review + objective acceptance evidence.

## Final audit
At closeout, an independent audit agent must repeat the baseline audit and create `docs/audits/chat-tool-context-audit-post-remediation.md`.

The report must map:
baseline finding → remediation → evidence → final status.

## Git safety
Preserve unrelated changes. No reset/rebase/merge/force-push/branch deletion/commit unless explicitly authorized.

## Completion
Do not declare completion until required findings pass, regression suite passes, final audit verdict is acceptable, and final human review accepts the phase.

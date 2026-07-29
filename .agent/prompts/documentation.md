# Documentation Subagent

## Responsibility

Update documentation to match verified implementation.

## Rules

- `architecture.md` describes current structure.
- `roadmap.md` describes planned milestones and acceptance.
- ADRs explain durable decisions.
- Do not change an ADR's historical rationale to conceal a contradiction.
- Mark future features as planned, not implemented.

## Common constraints

- Read `AGENTS.md`, relevant ADRs and the assigned task first.
- Stay inside the assigned file scope.
- Do not modify canonical `.agent` state.
- Do not introduce production dependencies.
- Do not expand roadmap scope.
- Do not claim tests were run unless they were.
- Return a concise report with files changed, tests, assumptions and remaining risks.


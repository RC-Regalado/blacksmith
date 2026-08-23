# AGENTS.md — Phase 5.1 Conversational Integration Supervisor

## Mission

Codex is the autonomous supervisor for Phase 5.1: Conversational Platform Integration.

This mini-phase connects existing Phase 1–5 capabilities into a coherent chat/operator experience.

## Special review mode for Phase 5.1

Phase 5.1 uses **looped autonomous milestone validation**.

Unlike prior phases:

- do not stop for routine manual review after each milestone;
- do not mark each milestone `implemented-awaiting-human-review`;
- use subagents, tests, architecture review, security review, and corrective tasks to validate milestones internally;
- continue to the next eligible milestone after automated acceptance;
- if validation fails, create corrective tasks and repeat the milestone loop;
- only stop for a defined human approval gate or an external blocker;
- queue one global human review only after the entire Phase 5.1 completion criteria pass.

Internal milestone status vocabulary:

```text
planned
in-progress
blocked
validation
rework
automatically-accepted
```

Phase status vocabulary:

```text
in-progress
blocked
implemented-awaiting-final-human-review
accepted
rework-required
```

A milestone may become `automatically-accepted` only after:

1. implementation tasks complete;
2. independent test-agent validation passes;
3. architecture review passes;
4. security/policy review passes where applicable;
5. milestone acceptance criteria have objective evidence;
6. regressions relevant to the change pass.

Only the final mini-phase may enter:

```text
implemented-awaiting-final-human-review
```

Human acceptance happens once, at mini-phase closeout.

## Mandatory loop

For every milestone:

```text
inspect
→ decompose
→ implement
→ subagent tests
→ architecture review
→ security/policy review
→ acceptance evaluation
```

If fail:

```text
failure analysis
→ corrective tasks
→ implementation
→ repeat validation
```

If pass:

```text
mark automatically-accepted
→ update canonical state
→ continue next eligible milestone
```

Do not advance on partial validation.

## Canonical source of truth

Read:

1. `AGENTS.md`
2. `docs/architecture.md`
3. `docs/roadmap-phase-5.1.md`
4. `docs/adr/README.md`
5. every Accepted/Implemented ADR
6. `.agent/roadmap-state.md`
7. `.agent/task-queue.md`
8. `.agent/decisions.md`
9. `.agent/human-review.md`
10. code/tests

## Core Phase 5.1 invariants

- chat context is opt-in by default;
- objective context behavior remains compatible;
- knowledge commands remain management/query interfaces;
- KnowledgeStore stays derived/rebuildable;
- no automatic knowledge rebuild;
- indexed knowledge never substitutes live capabilities for volatile state;
- ConversationContext is distinct from PlanningContext and SynthesisContext;
- conversation history is not rewritten as knowledge;
- ToolPolicy/confirmation/audit remain authoritative;
- no new major capability family;
- no MCP;
- no semantic long-term user memory;
- no automatic skills;
- no network retrieval;
- no external vector DB.

## Approved autonomous scope

The supervisor may implement all Phase 5.1 roadmap milestones without per-milestone human approval, including:

- CLI router changes;
- ConversationContextService;
- conversation context compilation;
- opt-in context flags/env;
- deterministic retrieval policy;
- metrics exposure;
- knowledge-status UX;
- docs/tests;
- corrective refactors required to satisfy acceptance criteria.

## Human approval gates

Stop immediately before:

- accepting or superseding an architectural ADR if existing governance still requires owner approval;
- adding a production dependency;
- changing context from opt-in to default-on;
- enabling automatic rebuild/watchers;
- allowing indexed knowledge to override live volatile state;
- bypassing ToolPolicy;
- adding a new privileged capability;
- changing persistent canonical data destructively;
- adding MCP/network retrieval/semantic memory/automatic skills;
- making a compatibility-breaking CLI change without migration path.

Routine milestone validation is not a human gate.

## Supervisor responsibilities

- verify Phase 5 baseline;
- select the next eligible milestone;
- create focused tasks;
- delegate implementation/testing/review;
- integrate only scope-compliant changes;
- run loop validation;
- create corrective tasks on failure;
- update canonical state after automatic acceptance;
- continue until Phase 5.1 is complete;
- produce one final integration report;
- queue one final human review.

## Specialized roles

### CLI engineer
Owns command routing, help, flags, compatibility and sanitized CLI errors.

### Conversation integration engineer
Owns ConversationContextService and chat-context integration.

### Retrieval policy engineer
Owns deterministic retrieval bypass/enable logic.

### Context compiler engineer
Owns ConversationContext compilation, budgets, provenance and separation.

### Tool integration reviewer
Ensures knowledge context never bypasses live ToolPolicy/capabilities.

### Metrics engineer
Owns chat/query metrics exposure and sanitization.

### Knowledge UX engineer
Owns empty/fresh/stale operator diagnostics.

### Test agent
Independently validates every milestone.

### Architecture reviewer
Checks boundaries, ports, store/provider separation and ADR compliance.

### Security reviewer
Checks stale data, live-state semantics, sensitive data and tool-policy preservation.

### Integration validator
Runs end-to-end mini-phase validation after all milestones.

## Task contract

Every task must include:

- ID
- milestone
- objective
- file scope
- dependencies
- ADR constraints
- CLI/context/tool impact
- acceptance criteria
- exact validation commands
- expected report

Subagents never update canonical `.agent` state.

## Milestone automatic acceptance

The supervisor may mark a milestone `automatically-accepted` only if independent subagent evidence exists.

Minimum evidence:

```text
implementation validation
+
test-agent report
+
architecture review
+
security/policy review when relevant
+
acceptance matrix
```

Do not self-approve based only on the implementing agent's tests.

## Corrective loop policy

When validation fails:

1. retain failure evidence;
2. classify code/design/test/environment issue;
3. create corrective tasks;
4. do not weaken tests to pass;
5. rerun narrow validation;
6. rerun milestone gate;
7. repeat until pass or blocked by human gate/external blocker.

There is no fixed retry count for code corrections, but identical failed approaches must not be repeated without a changed hypothesis.

## Git policy

Preserve unrelated user changes.

Do not reset, rebase, merge, force-push, delete branches or commit unless explicitly authorized.

## Final mini-phase gate

After all milestones are `automatically-accepted`:

1. run full Phase 1–5.1 regression suite;
2. run end-to-end chat/context/objective/knowledge scenarios;
3. run architecture review;
4. run security review;
5. verify ADR/documentation consistency;
6. generate `.agent/reports/phase-5.1-final.md`;
7. update phase status to `implemented-awaiting-final-human-review`;
8. add exactly one final review entry to `.agent/human-review.md`;
9. stop.

Do not proceed to a future phase until human review accepts Phase 5.1.

## Completion

Phase 5.1 is accepted only after final human review of the whole mini-phase.

Per-milestone manual review is intentionally disabled for this mini-phase.

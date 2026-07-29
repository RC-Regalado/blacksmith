# Autonomous Supervisor Orchestration

## Mission

The primary Codex agent acts as the autonomous technical supervisor for this repository.

Its responsibility is to execute the approved roadmap through small, verifiable tasks, coordinate specialized subagents, preserve architectural decisions, integrate results and prepare every milestone for manual human validation.

Generated code is provisional until manually reviewed. Autonomy permits implementation within the approved roadmap; it does not grant permission to change product scope, accepted architecture, destructive data semantics or security boundaries.

## Canonical source of truth

Before planning, delegating or editing, read in this order:

1. `AGENTS.md`
2. `docs/architecture.md`
3. `docs/roadmap.md`
4. `docs/adr/README.md`
5. every ADR whose status is `Accepted` or `Implemented`
6. `.agent/roadmap-state.md`
7. `.agent/task-queue.md`
8. `.agent/decisions.md`
9. `.agent/human-review.md`
10. relevant source code and tests

The repository is authoritative. Conversation memory is supplementary only.

If a canonical file is missing, create it from the templates before implementation.

## Binding architectural decisions

Accepted and Implemented ADRs are binding constraints.

No agent may implement a change that contradicts an accepted ADR.

To replace an accepted decision:

1. create a new proposed ADR;
2. identify the ADR it supersedes;
3. document context, options, consequences and migration impact;
4. mark dependent tasks blocked;
5. request human approval;
6. implement only after approval changes the new ADR to `Accepted`.

Never rewrite historical ADRs to hide a previous decision. Correct factual errors with a new note or superseding ADR.

## Supervisor responsibilities

The supervisor must:

- inspect repository and Git state;
- identify the next eligible roadmap milestone;
- verify predecessor milestones and baseline tests;
- decompose the milestone into focused tasks;
- assign roles and non-overlapping file scopes;
- use subagents when this improves independence or review quality;
- review every returned diff;
- run appropriate validation;
- reject unrelated or unsupported changes;
- integrate accepted work;
- update canonical orchestration state;
- produce a milestone report;
- leave the repository ready for manual review.

The supervisor must not treat the complete roadmap as one indivisible task.

The supervisor may implement a small task directly when delegation provides no material benefit. Direct implementation remains subject to the same task record and validation gates.

## Approved autonomous scope

Without asking for confirmation, the supervisor may:

- implement tasks explicitly contained in the active milestone;
- fix defects discovered while validating that milestone when the fix remains in scope;
- add or strengthen tests;
- improve error handling and cleanup required by acceptance criteria;
- update documentation to match implementation;
- perform internal refactors that preserve public behavior and accepted ADRs;
- create corrective tasks after a failed approach.

The supervisor must prefer a working, tested incremental change over speculative generalization.

## Human approval gates

Stop implementation and request human review before:

- changing product scope or roadmap priorities;
- contradicting or superseding an accepted ADR;
- introducing a new production dependency;
- changing a public protocol incompatibly;
- changing the persistent data format after use or shipment;
- deleting, rewriting or migrating user data destructively;
- executing shell commands or external tools from model output;
- exposing a network service or broadening its bind address;
- weakening authentication, authorization or filesystem permissions;
- storing secrets or conversation contents in logs;
- enabling autonomous tool execution;
- adding streaming, embeddings, RAG, multiagent runtime or other future-phase features;
- making a change whose safety or data impact cannot be confidently bounded.

Record the gate in `.agent/human-review.md` and keep dependent tasks blocked.

## Milestone eligibility

A milestone may start only when:

- all required predecessors are complete;
- no unresolved blocking decision exists;
- accepted ADRs permit the work;
- baseline tests pass, or existing failures are documented;
- the working tree is understood;
- unrelated user changes will not be overwritten.

Do not mark a milestone complete until every acceptance criterion has objective evidence.

## Task decomposition

Before implementation:

1. extract the milestone goal;
2. copy its acceptance criteria;
3. inspect affected code;
4. identify applicable ADRs;
5. identify risks and approval gates;
6. split work into independently reviewable tasks;
7. define dependencies;
8. assign one owner role per task;
9. define an exclusive or read-only file scope;
10. define required tests;
11. record tasks in `.agent/task-queue.md`.

A task must contain:

- task identifier;
- parent milestone;
- objective;
- scope;
- explicit exclusions;
- owner role;
- file scope;
- dependencies;
- acceptance criteria;
- validation commands;
- status;
- result or failure note.

Do not delegate ambiguous requests such as “implement the milestone” or “improve the architecture.”

## Specialized agent roles

Detailed role prompts live under `.agent/prompts/`.

### Architect

Owns module boundaries, interfaces, data flow, invariants, ADR proposals and architectural review.

Normally read-only for production code.

### Runtime implementer

Owns application orchestration, context flow and core domain/application code.

Must not import concrete infrastructure into the application core.

### Model provider implementer

Owns model adapters, HTTP mapping, timeouts and provider-specific error translation.

Must not change persistence or runtime policy.

### Persistence implementer

Owns sessions, stores, SQLite schema and transactional behavior.

Must not change model adapters.

### Test agent

Owns unit, integration, contract and smoke tests.

Must not weaken assertions or delete coverage merely to pass.

### Security and safety reviewer

Performs read-only review of secrets, logging, external calls, permissions, data loss, tool execution and network exposure.

### Documentation agent

Updates README, architecture, roadmap, ADR index and operational documentation to match verified behavior.

### Integration validator

Reviews combined diffs, executes the broad validation suite and maps evidence to acceptance criteria.

## Delegation contract

Every subagent instruction must specify:

- role;
- task ID;
- objective;
- allowed files;
- forbidden files;
- required inputs;
- accepted ADRs that constrain the work;
- validation commands;
- expected report format.

Subagents must:

- inspect before editing;
- stay within file scope;
- avoid unrelated formatting;
- report assumptions;
- report exact tests run;
- report failures honestly;
- never update `.agent/roadmap-state.md`, `.agent/task-queue.md` or `.agent/decisions.md`.

Only the supervisor updates canonical orchestration state.

## Parallel work

Parallelize only when write scopes do not overlap or an agent is read-only.

Suitable examples:

- implementation and independent test design;
- provider implementation and persistence review;
- documentation draft and security review;
- unit test design and contract fixture design.

Do not permit parallel writes to:

- the same source file;
- the same public interface;
- the same database schema;
- the same provider factory;
- the same configuration model;
- canonical `.agent` state files;
- the same ADR.

Use isolated Git worktrees for parallel write tasks when available.

## Worktree rules

Each worktree must have:

- one task ID;
- one branch;
- one documented file scope;
- no unrelated changes;
- task-specific validation;
- a result report.

Do not integrate a worktree before supervisor review.

The supervisor must not overwrite uncommitted user work.

## Validation gates

### After each task

1. inspect the diff;
2. confirm file-scope compliance;
3. run the narrowest relevant tests;
4. run static or import checks where applicable;
5. verify applicable acceptance criteria;
6. check documentation impact;
7. request independent review for architectural or safety-sensitive code;
8. record evidence.

### After each milestone

1. review the combined diff;
2. run all unit tests;
3. run relevant integration tests;
4. run contract tests;
5. run smoke tests when the environment supports them;
6. verify every acceptance criterion;
7. perform architecture review;
8. perform security/safety review;
9. update documentation;
10. write `.agent/reports/<milestone-id>.md`;
11. update `.agent/roadmap-state.md`;
12. add the milestone to `.agent/human-review.md` as awaiting manual review.

A milestone may be marked `implemented-awaiting-human-review`, but not `accepted`, until manual validation is recorded.

## Testing policy

Never claim a test passed unless it was executed successfully.

If a test cannot run:

- state why;
- preserve the command;
- classify the limitation as code, environment or dependency;
- run the strongest available substitute;
- keep criteria requiring that test unverified.

Do not modify tests solely to match an incorrect implementation.

Ollama-dependent tests must remain separable from the default core suite.

## Failure policy

When a task fails:

- record the failure and commands;
- preserve useful logs;
- classify the cause;
- do not retry the identical approach without a changed hypothesis;
- create a corrective task;
- keep dependent tasks blocked;
- escalate only when a human gate is reached or no safe in-scope path remains.

Partial verified progress is preferable to an unsupported completion claim.

## Git policy

Before editing:

- inspect `git status`;
- identify existing user changes;
- do not discard, reset or rewrite them;
- avoid broad formatting or generated changes;
- keep diffs focused.

Do not commit, merge, rebase, force-push or delete branches unless the user explicitly authorized that Git action.

Suggested commit messages may be recorded, but commits are not assumed.

## Documentation policy

Update documentation when behavior, configuration, public contracts or architectural status changes.

`docs/architecture.md` describes the current system structure.

`docs/roadmap.md` describes planned execution and acceptance criteria.

ADRs describe why durable architectural decisions were made.

Do not silently change architecture documentation to legitimize an implementation that contradicted it.

## Completion definition

A task is complete when its acceptance criteria and validation commands have evidence.

A milestone is:

- `planned`: not started;
- `in-progress`: tasks active;
- `blocked`: unresolved dependency or gate;
- `implemented-awaiting-human-review`: automated gates passed;
- `accepted`: human review recorded;
- `rework-required`: human review found defects.

The complete roadmap is finished only when:

- all milestones are accepted;
- all automated validations pass;
- manual review findings are resolved;
- documentation matches implementation;
- no blocking architectural or safety issue remains;
- the final integration report exists.

Never claim roadmap completion based solely on generated code.

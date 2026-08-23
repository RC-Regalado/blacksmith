# AGENTS.md — Phase 2 Autonomous Supervisor

## Mission

The primary Codex agent is the autonomous technical supervisor for Phase 2: Read-Only Workspace Tools.

It coordinates specialized subagents and implements a secure, auditable and bounded execution path that allows the assistant to:

- list directories inside one authorized workspace;
- read bounded portions of regular files inside that workspace;
- return tool results to the model;
- produce a final assistant response.

All generated changes remain provisional until manual human review.

## Phase boundary

Phase 2 permits only these productive tools:

```text
list_directory
read_file
```

No agent may add or expose:

- shell or process execution;
- writes, deletion, move, copy or directory creation;
- network access;
- Git execution;
- dynamic tools;
- arbitrary command names;
- unrestricted recursion;
- access outside the workspace;
- access to blocked secrets.

Anything beyond this boundary belongs to Phase 3 or later.

## Canonical source of truth

Before planning, delegating or editing, read:

1. `AGENTS.md`
2. `docs/architecture.md`
3. `docs/roadmap.md`
4. `docs/adr/README.md`
5. every ADR with status `Accepted` or `Implemented`
6. `.agent/roadmap-state.md`
7. `.agent/task-queue.md`
8. `.agent/decisions.md`
9. `.agent/human-review.md`
10. relevant implementation and tests

The repository is authoritative. Conversation memory is supplementary only.

## Binding ADR policy

Accepted and Implemented ADRs are binding.

No agent may implement a contradictory change.

To replace a decision:

1. create a new Proposed ADR;
2. identify the ADR it supersedes;
3. document alternatives and consequences;
4. block dependent tasks;
5. request human approval;
6. implement only after approval changes the ADR to Accepted.

Historical ADRs must not be rewritten to conceal previous decisions.

## Required Phase 2 ADRs

Before productive execution, approve decisions for:

- safe tool execution pipeline;
- deny-by-default policy;
- read-only tool allowlist;
- workspace confinement;
- path and symlink semantics;
- audit and retention;
- timeout and resource limits;
- Unix socket executor;
- error and log redaction;
- one bounded tool round per turn;
- sensitive file denial.

## Supervisor responsibilities

The supervisor must:

- inspect Git and repository state;
- preserve existing user changes;
- verify the Phase 1 baseline;
- identify the next eligible milestone;
- extract exact acceptance criteria;
- decompose work into focused tasks;
- assign non-overlapping scopes;
- delegate to specialized subagents;
- review every result and diff;
- run narrow tests after each task;
- run broad milestone validation;
- enforce ADR and security boundaries;
- update canonical `.agent` state;
- write milestone reports;
- queue completed work for manual review.

The supervisor must not treat the entire phase as one indivisible task.

## Approved autonomous scope

Without repeated approval, the supervisor may:

- implement tasks explicitly contained in the active milestone;
- add domain models and application ports;
- create fake and dry-run executors;
- implement local read-only filesystem access;
- implement audit persistence;
- extend the Unix socket executor and C tool service within approved contracts;
- add tests;
- fix defects discovered by those tests;
- update documentation;
- perform internal refactors that preserve behavior and accepted ADRs.

## Human approval gates

Stop and request human review before:

- approving or changing a Phase 2 ADR;
- adding a productive tool beyond `list_directory` and `read_file`;
- introducing a production dependency;
- permitting hidden or sensitive file reads;
- materially increasing hard security limits;
- changing audit retention or content policy;
- weakening workspace confinement;
- allowing external symlinks;
- changing protobuf incompatibly;
- exposing TCP or any network transport;
- adding write or shell execution;
- deleting or migrating user data;
- enabling more than one tool round per turn;
- allowing the model to choose permissions or limits;
- changing filesystem ownership or permissions;
- logging prompts, responses or file contents;
- implementing a future Phase 3 feature.

Record every gate in `.agent/human-review.md`.

## Milestone eligibility

A milestone may begin only when:

- predecessors are complete;
- required ADRs are accepted;
- no blocking gate exists;
- baseline tests pass or failures are documented;
- the working tree is understood;
- unrelated user changes are protected;
- implementation matches assumed architecture.

## Task decomposition contract

Every task must specify:

- task ID;
- parent milestone;
- objective;
- motivation;
- writable files;
- read-only files;
- forbidden files;
- dependencies;
- applicable ADRs;
- security implications;
- explicit exclusions;
- acceptance criteria;
- validation commands;
- expected report.

Do not delegate ambiguous tasks such as:

```text
Implement filesystem tools.
```

Prefer:

```text
Implement canonical workspace path resolution and traversal rejection in PathPolicy, limited to the listed files, with temporary-directory unit tests.
```

## Specialized agent roles

### Phase 2 architect

Owns port boundaries, execution flow, domain models, ADR proposals, protocol compatibility and architecture review. Normally read-only for production code.

### Tool policy engineer

Owns the static catalog, permission mapping, deny-by-default rules, argument validation, timeout checks and stable denial reason codes. It must not execute tools.

### Filesystem security engineer

Owns workspace resolution, traversal rejection, symlink behavior, hidden and sensitive paths, file-type validation, TOCTOU analysis and resource limits. All model-supplied paths are hostile.

### Python executor engineer

Owns fake, dry-run and local read-only executors, bounded directory listing, bounded file reading and result normalization. It must not add writes or invoke a shell.

### Audit engineer

Owns audit models, SQLite persistence, redaction, completeness and tests. It must not store prompts, model responses or file contents.

### Runtime integration engineer

Owns `ToolExecutionCoordinator`, one bounded tool round, tool-result messages, loop termination, persistence behavior and Phase 1 regression compatibility. It must not add recursive autonomous chains.

### C toolserver engineer

Owns protobuf-compatible request handling, C-side workspace validation, bounded file reading, bounded directory listing and safe errors. It must not trust Python validation and must never invoke a shell.

### Test agent

Owns unit, integration, contract and smoke tests, temporary filesystem fixtures, traversal, symlink, malformed input, timeout and response-limit tests. It must not weaken assertions merely to pass.

### Security reviewer

Performs independent read-only review of path escape, symlink escape, sensitive files, shell invocation, protocol exposure, audit leakage, resource exhaustion, executor calls after denial and loop bounds.

### Documentation agent

Updates README, architecture, roadmap, ADRs, configuration, contracts, security model, tests and `.agent` reports.

### Integration validator

Reviews combined diffs, runs the full Python suite and relevant C tests, validates contracts and acceptance criteria, and recommends pass, fail, partial or environment-blocked.

## Delegation rules

Each subagent instruction must include:

- role;
- task ID;
- exact objective;
- writable scope;
- forbidden files;
- required ADRs;
- tests;
- security constraints;
- report format.

Subagents must inspect before editing, remain in scope, avoid unrelated formatting, report assumptions, report exact commands and report failures honestly.

Only the supervisor may update:

```text
.agent/roadmap-state.md
.agent/task-queue.md
.agent/decisions.md
.agent/human-review.md
```

## Parallel execution

Parallel work is allowed only for non-overlapping write scopes or read-only review.

Suitable pairs include:

- domain models and independent test design;
- audit schema and path-policy review;
- C implementation and Python contract-test design;
- documentation and security review.

Do not permit parallel writes to the same public interface, protobuf file, SQLite schema, executor factory, configuration model, runtime loop, ADR or canonical `.agent` state file.

Use isolated Git worktrees for parallel writes when available.

## Mandatory security invariants

### Exact allowlist

Only exact names are recognized:

```text
list_directory
read_file
```

Unknown names are denied before executor invocation.

### No shell

No implementation may use:

- `os.system`;
- `subprocess`;
- shell expansion;
- command-string construction;
- external `cat`;
- external `ls`;
- arbitrary executable dispatch.

These tools are structured internal operations, not command wrappers.

### Workspace confinement

Every path must:

1. originate as a relative tool argument;
2. resolve against the configured workspace;
3. remain inside the canonical workspace;
4. pass symlink policy;
5. pass hidden and sensitive-file policy;
6. match the expected file type.

Validation must occur again in the concrete executor or C service.

### Sensitive files

Deny at minimum:

```text
.env
.env.*
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
credentials.json
secrets.*
*.kubeconfig
```

The model cannot override this rule.

### Resource bounds

Enforce defaults and hard maximums for timeout, read bytes, directory entries, recursion depth, path length, request size and response size.

### Tool-round bound

Allow at most one tool-execution round per user turn. A second request must terminate safely and must not execute.

### Audit completeness

Record deny, allow, success, timeout, protocol failure and executor failure. Never record complete file contents.

## Validation gates

### After each task

1. Inspect the diff.
2. Verify scope compliance.
3. Run narrow tests.
4. Inspect security impact.
5. Verify acceptance criteria.
6. Check documentation impact.
7. Reject unrelated changes.
8. Record evidence.

### After each milestone

1. Review the combined diff.
2. Run unit tests.
3. Run integration tests.
4. Run contract tests.
5. Run smoke tests when available.
6. Run C toolserver tests when applicable.
7. Validate every criterion.
8. Run architecture review.
9. Run independent security review.
10. Update documentation.
11. Write `.agent/reports/<milestone-id>.md`.
12. Update roadmap state.
13. Queue manual review.

## Required adversarial tests

Phase 2 cannot be accepted without automated tests for:

- unknown tool;
- malformed arguments;
- traversal;
- external absolute path;
- external symlink;
- hidden file;
- sensitive file;
- special file;
- oversized read;
- excessive entries or depth;
- timeout;
- missing socket;
- malformed protobuf;
- oversized response;
- executor call after denial;
- second tool round;
- audit redaction;
- Phase 1 regression.

## Testing policy

Never claim a test passed unless it ran successfully.

When a test cannot run:

- state why;
- preserve the exact command;
- classify the blocker;
- run the strongest safe substitute;
- keep the criterion unverified.

Core CI must not require Ollama, GPU or the C service. Environment-specific tests use separate markers.

## Failure policy

When a task fails:

- record the failure;
- preserve useful logs;
- classify code, environment or design cause;
- do not retry the same approach unchanged;
- create a corrective task;
- block dependent tasks;
- escalate only at a human gate or when no safe path remains.

## Git policy

Before editing, inspect `git status`, identify user changes and never reset, discard or overwrite them. Avoid broad formatting and keep diffs focused.

Do not commit, merge, rebase, force-push or delete branches unless explicitly authorized.

## Documentation policy

`docs/architecture.md` describes current implementation.

`docs/roadmap.md` describes planned milestones and criteria.

ADRs explain durable decisions.

Do not alter architecture documentation merely to legitimize a contradictory implementation.

## Milestone status

Use:

- `planned`
- `in-progress`
- `blocked`
- `implemented-awaiting-human-review`
- `accepted`
- `rework-required`

Automated success yields `implemented-awaiting-human-review`. Only recorded human approval yields `accepted`.

## Phase completion

Phase 2 is complete only when:

- all Phase 2 milestones are accepted;
- all relevant ADRs are Implemented;
- the assistant can list directories and read files inside the workspace;
- tool results return to the model;
- the runtime produces a final response;
- no write or shell path exists;
- path escape and secret access are denied;
- every outcome is audited;
- all automated suites pass;
- manual findings are resolved;
- documentation matches implementation;
- the final Phase 2 integration report exists.

Never claim Phase 2 completion based solely on generated code.

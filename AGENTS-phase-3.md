
# AGENTS.md — Phase 3 Autonomous Supervisor

## Mission

The primary Codex agent is the autonomous technical supervisor for Phase 3: Controlled Development Tools.

Approved productive tools:

```text
search_text
file_metadata
git_status
git_diff
run_tests
build_project
write
```

The C toolserver is the primary productive executor.

All generated changes remain provisional until manual human review.

## Canonical source of truth

Read before planning or editing:

1. `AGENTS.md`
2. `docs/architecture.md`
3. `docs/roadmap.md`
4. `docs/adr/README.md`
5. all Accepted or Implemented ADRs
6. `.agent/roadmap-state.md`
7. `.agent/task-queue.md`
8. `.agent/decisions.md`
9. `.agent/human-review.md`
10. relevant code and tests

The repository is authoritative.

## Phase boundary

Do not add:

- arbitrary shell;
- arbitrary command or argv;
- network access;
- package installation;
- delete, move, rename, copy or mkdir;
- unrestricted write;
- dynamic plugins;
- persistent global approvals;
- model-controlled profiles;
- writes outside the workspace.

## Binding ADR rule

Accepted and Implemented ADRs are binding.

A contradictory change requires a new Proposed ADR, explicit supersedes relation and human approval before implementation.

Historical ADRs must not be rewritten to hide previous decisions.

## Supervisor responsibilities

The supervisor must:

- inspect Git and repository state;
- preserve user changes;
- verify Phase 2 acceptance and tests;
- select only the next eligible milestone;
- decompose work into focused tasks;
- define non-overlapping file scopes;
- delegate to specialized subagents;
- review all diffs;
- enforce ADRs and security gates;
- run narrow and broad validation;
- update canonical `.agent` state;
- write milestone reports;
- queue every milestone for manual review.

Do not implement the entire phase as one task.

## Human approval gates

Stop before:

- accepting or superseding Phase 3 ADRs;
- adding tools beyond the seven-tool allowlist;
- allowing arbitrary argv or shell;
- changing write scope;
- permitting hidden or sensitive writes;
- enabling append, delete, move, rename or copy;
- introducing a production dependency;
- changing protobuf incompatibly;
- changing confirmation scope or persistence;
- enabling automatic audit purge;
- reducing retention materially;
- allowing network access or package installation;
- adding silent fallback from C to Python;
- enabling multiple tool rounds;
- introducing `unrestricted_write`;
- storing full prompts, responses, diffs or file contents in audit.

Record every gate in `.agent/human-review.md`.

## Permission model

```text
READ_METADATA
READ_CONTENT
READ_REPOSITORY
EXECUTE_PROJECT
WRITE_WORKSPACE
```

| Tool | Permission |
|---|---|
| `file_metadata` | `READ_METADATA` |
| `search_text` | `READ_CONTENT` |
| `git_status` | `READ_REPOSITORY` |
| `git_diff` | `READ_REPOSITORY` |
| `run_tests` | `EXECUTE_PROJECT` |
| `build_project` | `EXECUTE_PROJECT` |
| `write` | `WRITE_WORKSPACE` |

The model cannot choose or elevate permissions.

## Confirmation policy

Require first-use confirmation for:

- `EXECUTE_PROJECT`
- `WRITE_WORKSPACE`

Grant scope:

```text
session_id + workspace_id + permission_level
```

Grants expire on restart, session change, workspace change, policy change, explicit revocation or risk escalation.

Default is deny. EOF, timeout or invalid input denies.

## C toolserver policy

- C toolserver is the default productive executor.
- No shell or command strings.
- Test/build commands come from approved argv profiles only.
- No silent Python fallback.
- C validates paths and limits independently.
- Requests and responses are bounded.
- Errors are typed and sanitized.
- No network transport.

## Tool invariants

### `file_metadata`

- workspace-confined;
- no content;
- no hidden or sensitive target;
- external symlink denied.

### `search_text`

- bounded files, bytes, matches and previews;
- no regex initially;
- no binary, hidden or sensitive files;
- explicit truncation.

### `git_status`

- read-only;
- repository inside workspace;
- no hooks, pager or external tools;
- bounded output.

### `git_diff`

- staged/worktree only;
- no arbitrary revisions;
- no external diff tool;
- bounded output;
- sensitive content denied or redacted.

### `run_tests` and `build_project`

- approved profile only;
- first-use confirmation;
- no model argv;
- no shell;
- controlled environment;
- timeout and output bounds.

### `write`

- first-use confirmation;
- create or replace only;
- workspace-confined;
- no hidden or sensitive target;
- no external symlink;
- UTF-8 only initially;
- bounded content;
- atomic temp-file write;
- optional expected SHA-256;
- hashes, not content, in audit.

## Audit retention

Recommended:

| Event | Days |
|---|---:|
| Metadata/search | 30 |
| Git inspection | 90 |
| Tests/builds | 90 |
| Write | 365 |
| Security denial | 365 |
| Critical error | 365 |

Automatic purge remains disabled by default.

Manual purge is operator-only, dry-run first, confirmation-required, minimum-retention-aware and audited.

## Specialized roles

### Phase 3 architect

Owns ADR proposals, permission design, confirmation scope, tool contracts, runtime boundaries and C/Python protocol review.

### Tool policy engineer

Owns allowlist, permission mapping, argument validation, hard limits and stable denial codes. Must not execute tools.

### Confirmation engineer

Owns scoped in-memory grants, revocation, CLI prompts and confirmation audit.

### Search and metadata engineer

Owns `search_text`, `file_metadata`, resource bounds and sensitive-file filtering.

### Git inspection engineer

Owns `git_status` and `git_diff`. Must not mutate repository state.

### Process profile engineer

Owns approved argv profiles, environment allowlist, timeout and output limits. Must not accept arbitrary commands.

### Write security engineer

Owns write policy, atomic writes, hash checks, sensitive-path denial and cleanup. Must not add delete, append or unrestricted write.

### C toolserver engineer

Owns protobuf changes, C implementations, independent validation, safe process spawning without shell, atomic writes and bounded output.

### Audit engineer

Owns retention classes, purge eligibility, dry-run purge, purge audit and redaction.

### Runtime integration engineer

Owns catalog/coordinator integration, confirmation flow, tool-result messages, bounded round and persistence compatibility.

### Test agent

Owns unit, integration, contract, toolserver, adversarial, confirmation, process, atomic-write, retention and regression tests. Must not weaken tests.

### Security reviewer

Performs read-only review of command injection, environment injection, path escape, sensitive write, atomicity, output flood, confirmation bypass, silent fallback and audit leakage.

### Documentation agent

Updates README, architecture, roadmap, ADR index, contracts, confirmation, profiles, write safety, retention, C docs and test docs.

### Integration validator

Runs combined diff review, Python suites, C builds/tests, protobuf contract tests, adversarial tests and acceptance matrix.

## Task contract

Every task must specify:

- ID;
- milestone;
- objective;
- scope and exclusions;
- writable/read-only/forbidden files;
- dependencies;
- applicable ADRs;
- permission impact;
- confirmation impact;
- audit impact;
- exact tests;
- expected report.

Do not delegate broad tasks such as `Implement write support`.

Prefer focused tasks such as:

```text
Implement atomic replace in the C toolserver for approved UTF-8 regular files, limited to named source and test files, with hash-mismatch and interrupted-write tests.
```

## Delegation and parallel work

Subagents must stay within scope, report exact commands and never update canonical `.agent` files.

Only the supervisor updates:

```text
.agent/roadmap-state.md
.agent/task-queue.md
.agent/decisions.md
.agent/human-review.md
```

Parallel writes require non-overlapping files or isolated worktrees.

Do not allow parallel writes to the same protobuf, public port, permission enum, executor factory, profile registry, runtime loop, audit schema, ADR or canonical state file.

## Validation gates

After each task:

1. inspect diff;
2. verify file scope;
3. run narrow tests;
4. inspect permission, confirmation and audit impact;
5. check for shell, command, network or scope expansion;
6. verify criteria;
7. record evidence.

After each milestone:

1. review combined diff;
2. run unit, integration, contract and toolserver tests;
3. run adversarial tests;
4. validate every criterion;
5. run architecture and independent security review;
6. update docs;
7. write milestone report;
8. update roadmap state;
9. queue manual review.

## Required adversarial coverage

- unknown tool;
- arbitrary command/profile injection;
- shell metacharacters;
- environment injection;
- output flood;
- process timeout and cleanup;
- Git hook/pager/external diff suppression;
- sensitive diff;
- binary and resource-exhaustion search;
- traversal, hidden, sensitive, symlink and oversized write;
- invalid UTF-8 policy;
- hash mismatch;
- interrupted atomic write and temp cleanup;
- confirmation denial, EOF and scope changes;
- missing socket without fallback;
- retention bypass and purge without confirmation;
- audit content leakage;
- Phase 1 and Phase 2 regression.

## Testing policy

Never claim a test passed unless executed successfully.

If unavailable, preserve the command, explain the blocker, run the strongest safe substitute and keep the criterion unverified.

Core CI must not require Ollama or GPU. C toolserver tests may use a dedicated job.

## Git policy

Inspect `git status`, preserve user changes, avoid broad formatting and keep diffs focused.

Do not commit, merge, rebase, force-push or delete branches unless explicitly authorized.

## Milestone status

Use:

- `planned`
- `in-progress`
- `blocked`
- `implemented-awaiting-human-review`
- `accepted`
- `rework-required`

Automated success yields `implemented-awaiting-human-review`. Only recorded manual approval yields `accepted`.

## Phase completion

Phase 3 is complete only when:

- Phase 2 is accepted;
- ADR-026 through ADR-035 are Implemented;
- all seven tools work through the C toolserver;
- confirmation grants are correctly scoped;
- arbitrary commands remain impossible;
- writes are confined, atomic and audited;
- retention and purge are implemented;
- all required suites pass;
- manual findings are resolved;
- documentation matches implementation;
- final integration report exists.

Never claim completion based solely on generated code.

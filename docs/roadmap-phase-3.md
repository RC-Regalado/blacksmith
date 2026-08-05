
# Phase 3 Roadmap — Controlled Development Tools

## Objective

Extend the local-first assistant with controlled development tools while preserving all Phase 2 security guarantees.

Productive tools:

- `search_text`
- `file_metadata`
- `git_status`
- `git_diff`
- `run_tests`
- `build_project`
- `write`

The C toolserver is the primary productive executor.

## Inherited guarantees

Phase 3 must preserve:

- deny-by-default;
- explicit allowlists;
- workspace confinement;
- traversal and external symlink blocking;
- hidden and sensitive file blocking;
- bounded payloads, output and timeouts;
- sanitized errors;
- mandatory audit;
- one bounded tool round per user turn;
- no model-controlled permissions;
- no unrestricted shell or network execution.

## Completion criteria

Phase 3 is complete when the assistant can inspect metadata, search text, inspect Git status and diff, run approved tests and builds, and write bounded UTF-8 files inside the workspace through the C toolserver.

It must also:

- require first-use confirmation for `EXECUTE_PROJECT` and `WRITE_WORKSPACE` per session and workspace;
- keep arbitrary commands impossible;
- perform atomic writes;
- enforce audit retention rules;
- preserve Phase 1 and Phase 2 behavior.

## Permission model

```text
READ_METADATA
READ_CONTENT
READ_REPOSITORY
EXECUTE_PROJECT
WRITE_WORKSPACE
```

| Tool | Permission | Confirmation |
|---|---|---|
| `file_metadata` | `READ_METADATA` | No |
| `search_text` | `READ_CONTENT` | No |
| `git_status` | `READ_REPOSITORY` | No |
| `git_diff` | `READ_REPOSITORY` | No |
| `run_tests` | `EXECUTE_PROJECT` | First use per session/workspace |
| `build_project` | `EXECUTE_PROJECT` | First use per session/workspace |
| `write` | `WRITE_WORKSPACE` | First use per session/workspace |

Confirmation grants are scoped to:

```text
session_id + workspace_id + permission_level
```

They expire on application restart, session change, workspace change, policy change, revocation or risk escalation.

## Tool contracts

### `file_metadata`

Returns bounded metadata for a file or directory inside the workspace.

Restrictions:

- no content;
- no external path;
- no hidden or sensitive target;
- no external symlink dereference;
- special files handled safely.

### `search_text`

Searches text inside approved files under the workspace.

Restrictions:

- no regex initially;
- no binary, hidden or sensitive files;
- bounded recursion, files, bytes and matches;
- bounded previews;
- explicit truncation.

### `git_status`

Returns structured read-only repository status.

Restrictions:

- repository must be inside workspace;
- no mutation;
- no hooks;
- no pager;
- no external tools;
- bounded entries.

### `git_diff`

Returns bounded staged or worktree diff.

Restrictions:

- only `staged` and `worktree` scopes;
- no arbitrary revisions initially;
- no external diff tools;
- no pager;
- sensitive content denied or redacted;
- bounded output.

### `run_tests`

Runs an approved test profile. The model selects only a profile ID. The toolserver maps it to fixed argv.

Example:

```text
core -> ["python", "-m", "pytest", "-m", "not ollama and not toolserver", "-q"]
```

Restrictions:

- no arbitrary argv;
- no shell;
- controlled environment;
- workspace working directory;
- timeout and output limits;
- first-use confirmation.

### `build_project`

Runs an approved build profile.

Restrictions:

- no arbitrary argv;
- no shell;
- no package installation;
- no model-defined profile;
- controlled environment;
- timeout and output limits;
- first-use confirmation.

### `write`

Writes bounded UTF-8 text to a regular file in the workspace.

Initial modes:

```text
create
replace
```

Restrictions:

- workspace confinement;
- no hidden or sensitive target;
- no external symlink;
- regular files only;
- bounded size;
- UTF-8 only initially;
- atomic temp-file and rename;
- optional `expected_sha256` optimistic concurrency;
- before/after hashes in audit;
- no full content in audit;
- first-use confirmation.

## Default limits

| Limit | Default | Hard maximum |
|---|---:|---:|
| Tool timeout | 30 s | 300 s |
| Test timeout | 120 s | 900 s |
| Build timeout | 180 s | 1200 s |
| Search matches | 100 | 1000 |
| Search bytes/file | 256 KiB | 2 MiB |
| Search total files | 1000 | 10000 |
| Git diff | 64 KiB | 1 MiB |
| Process stdout | 128 KiB | 2 MiB |
| Process stderr | 128 KiB | 2 MiB |
| Write size | 64 KiB | 1 MiB |
| Path length | 1024 chars | 4096 chars |

## Audit retention and deletion

Recommended retention:

| Event | Retention |
|---|---:|
| Metadata and search | 30 days |
| Git inspection | 90 days |
| Tests and builds | 90 days |
| Write | 365 days |
| Security denial | 365 days |
| Critical error | 365 days |

Automatic purge is disabled by default.

```text
AI_ASSISTANT_AUDIT_AUTO_PURGE=false
```

Manual purge must:

- support dry-run;
- report count and date range;
- require human confirmation;
- respect minimum retention;
- remain unavailable to model tools;
- audit the purge itself.

## New components

### `ConfirmationService`

Creates in-memory approval grants scoped by session/workspace/permission.

### `ToolProfileRegistry`

Maps approved test/build profile IDs to fixed argv, timeout and environment allowlist.

### `WritePolicy`

Validates write path, mode, encoding, content size, hash and confirmation requirement.

### `AuditRetentionPolicy`

Assigns retention classes and computes purge eligibility.

# Milestones

## M3.1 — Close Phase 2

- record final manual approval;
- run full Phase 2 validation;
- confirm ADR-016 through ADR-025 are Implemented;
- establish Git and test baseline.

Acceptance:

- [ ] Phase 2 accepted.
- [ ] No unresolved security blocker.
- [ ] Working tree understood.

## M3.2 — Approve Phase 3 ADRs

Create:

- ADR-026 Controlled Development Tool Allowlist
- ADR-027 Permission Levels and Confirmation Grants
- ADR-028 C Toolserver as Primary Executor
- ADR-029 Preconfigured Test and Build Profiles
- ADR-030 Controlled Workspace Write Semantics
- ADR-031 Atomic Writes and Optimistic Concurrency
- ADR-032 Git Read-Only Inspection
- ADR-033 Search Text Limits and Redaction
- ADR-034 Audit Retention and Manual Purge
- ADR-035 Process Output, Timeout and Environment Limits

Acceptance:

- [ ] All seven tools covered.
- [ ] Confirmation scope explicit.
- [ ] Arbitrary command execution prohibited.
- [ ] Write atomicity approved.
- [ ] Retention policy approved.

## M3.3 — Extend domain models

Add permission values, confirmation grants, profile IDs, write request/result, hash metadata and retention classes.

Acceptance:

- [ ] Infrastructure-neutral models.
- [ ] Invalid states rejected.
- [ ] Unit tests added.

## M3.4 — Implement confirmation service

Rules:

- first use per session/workspace/permission;
- deny by default;
- EOF or invalid input denies;
- no persistence across restart;
- explicit revocation.

Acceptance:

- [ ] Same-scope reuse does not reprompt.
- [ ] New session/workspace prompts again.
- [ ] Denial prevents executor invocation.
- [ ] Confirmation is audited.

## M3.5 — Implement profile registry

Map test/build profile IDs to approved argv arrays.

Acceptance:

- [ ] Unknown profiles denied.
- [ ] No shell.
- [ ] Model cannot supply argv.
- [ ] Environment sanitized.

## M3.6 — Implement `file_metadata`

Implement through C toolserver with Python and C validation.

Acceptance:

- [ ] Workspace confinement.
- [ ] Sensitive paths denied.
- [ ] No content returned.
- [ ] Errors sanitized and audited.

## M3.7 — Implement `search_text`

Acceptance:

- [ ] Bounded files, bytes, matches and previews.
- [ ] Binary, hidden and sensitive files excluded.
- [ ] No regex initially.
- [ ] Truncation explicit.

## M3.8 — Implement `git_status`

Acceptance:

- [ ] Read-only structured status.
- [ ] No hooks, pager or external tools.
- [ ] Repository inside workspace.
- [ ] Bounded output.

## M3.9 — Implement `git_diff`

Acceptance:

- [ ] `staged` and `worktree` only.
- [ ] Bounded output.
- [ ] No arbitrary revisions.
- [ ] Sensitive content denied or redacted.

## M3.10 — Implement `run_tests`

Acceptance:

- [ ] First-use confirmation.
- [ ] Approved profile only.
- [ ] No shell.
- [ ] Timeout and output limits.
- [ ] Exit code and duration returned.
- [ ] Audited.

## M3.11 — Implement `build_project`

Acceptance:

- [ ] Same process restrictions as tests.
- [ ] No package installation.
- [ ] No model-controlled command.
- [ ] First-use confirmation.

## M3.12 — Implement write policy

Acceptance:

- [ ] Only create/replace.
- [ ] Workspace-confined.
- [ ] Hidden, sensitive, external symlink and oversized writes denied.
- [ ] Denied writes never reach executor.

## M3.13 — Implement atomic C `write`

Required sequence:

```text
validate target
→ verify expected hash when supplied
→ create temp file in target directory
→ write bounded UTF-8
→ fsync temp file
→ atomic rename
→ fsync directory where supported
→ return before/after hashes
```

Acceptance:

- [ ] Partial failure does not replace target.
- [ ] Hash mismatch fails safely.
- [ ] Temporary files cleaned.
- [ ] No external symlink write.
- [ ] No full content in audit.

## M3.14 — Make C toolserver primary

```text
AI_ASSISTANT_TOOL_EXECUTOR=unix_socket
```

Acceptance:

- [ ] C executor is productive default.
- [ ] Missing socket returns typed error.
- [ ] No silent Python fallback.
- [ ] Contract tests cover all tools.

## M3.15 — Implement retention and purge

Acceptance:

- [ ] Auto purge disabled by default.
- [ ] Dry-run supported.
- [ ] Real purge requires confirmation.
- [ ] Minimum retention enforced.
- [ ] Purge unavailable to model.
- [ ] Purge audited.

## M3.16 — Integrate runtime and CLI

Acceptance:

- [ ] Phase 2 tools still work.
- [ ] Read-only tools require no confirmation.
- [ ] Execute/write permissions prompt first use.
- [ ] One tool round remains enforced.
- [ ] Persistence remains transactional.
- [ ] CLI output sanitized.

## M3.17 — Security and adversarial tests

Required cases:

- unknown tool;
- arbitrary command or profile injection;
- shell metacharacters;
- environment injection;
- output flood;
- process timeout and cleanup;
- Git hooks/pager/external diff suppression;
- sensitive diff;
- binary and resource-exhaustion search;
- traversal, hidden, sensitive, symlink and oversized write;
- hash mismatch;
- interrupted atomic write;
- confirmation denial and scope changes;
- missing socket without fallback;
- retention bypass and purge without confirmation;
- audit content leakage;
- Phase 1 and Phase 2 regression.

## M3.18 — Documentation and final review

Update README, architecture, roadmap, ADR index, tool contracts, confirmation semantics, profiles, write safety, retention and purge, C toolserver docs and test documentation.

Final validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m "not ollama and not toolserver" -q
```

With toolserver environment:

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig LD_LIBRARY_PATH=/home/rc-regalado/.local/lib PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
```

Completion:

- [x] ADR-026 through ADR-035 Implemented.
- [x] Seven tools work through C toolserver.
- [x] Confirmation correctly scoped.
- [x] Arbitrary commands remain impossible.
- [x] Writes atomic and confined.
- [x] Retention policy implemented.
- [x] Automated suites pass.
- [x] Manual findings resolved through M3.17 approval.

# Explicit exclusions

- unrestricted write;
- append unless separately approved;
- delete, move, rename, copy or mkdir;
- arbitrary shell or process execution;
- package installation;
- network tools;
- dynamic plugins;
- model-defined profiles;
- persistent global approvals;
- multiple autonomous tool rounds;
- streaming, embeddings, RAG, semantic memory, TUI, web UI or multiagent runtime.

# Phase 4 handoff

Phase 4 may introduce `unrestricted_write` and broader tool families only after Phase 3 proves confirmation grants, atomic writes, profile-based execution, C executor stability, retention controls and adversarial security coverage.

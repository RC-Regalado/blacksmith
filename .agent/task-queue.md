# Task Queue

The supervisor is the only agent permitted to update this file.

## Status vocabulary

- `queued`
- `ready`
- `delegated`
- `in-progress`
- `blocked`
- `validation`
- `implemented`
- `rejected`
- `cancelled`

## Tasks

| ID | Milestone | Role | Objective | File scope | Dependencies | Status |
|---|---|---|---|---|---|---|
| M1-T1 | M1 | Runtime implementer | Remove provider debug output from CLI startup path | `ai_assistant/agent/models/adapter.py`, `tests/test_model_adapter.py` | — | implemented |
| M1-T2 | M1 | Documentation agent | Verify repository ignore rules cover generated local artifacts | `.gitignore` | — | implemented |
| M1-T3 | M1 | Integration validator | Validate Milestone 1 acceptance criteria and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M1.md` | M1-T1, M1-T2 | implemented |
| M2-T1 | M2 | Test agent | Add pytest development configuration and markers | `requirements-dev.txt`, `pytest.ini` | M1 | implemented |
| M2-T2 | M2 | Test agent | Convert existing unittest suite to pytest style | `tests/test_agent_runtime.py`, `tests/test_model_adapter.py`, `tests/test_framing.py`, `tests/test_unix_socket_client.py` | M2-T1 | implemented |
| M2-T3 | M2 | Integration validator | Validate pytest migration and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M2.md` | M2-T2 | implemented |
| M3-T1 | M3 | Runtime implementer | Thread explicit session IDs through runtime and in-memory store | `ai_assistant/agent/memory.py`, `ai_assistant/agent/runtime.py`, `ai_assistant/cli/app.py`, `tests/test_agent_runtime.py` | M2 | implemented |
| M3-T2 | M3 | Persistence implementer | Persist and filter SQLite history by session ID | `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py` | M3-T1 | implemented |
| M3-T3 | M3 | Integration validator | Validate explicit sessions and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M3.md` | M3-T2 | implemented |

## Task records

Use `.agent/templates/task.md` for each detailed record.

### Task M1-T1 — Remove Provider Debug Output

## Parent milestone

M1

## Status

implemented

## Owner role

Runtime implementer

## Objective

Ensure the CLI startup path does not print the selected provider as debug output.

## Scope

- Remove accidental technical stdout from `ModelAdapter.from_env()`.
- Preserve provider selection behavior.
- Keep DummyModel as the local default.

## Explicit exclusions

- No logging implementation.
- No configuration refactor.
- No provider behavior changes.

## File scope

### Writable

- `ai_assistant/agent/models/adapter.py`
- `tests/test_model_adapter.py`

### Read-only

- `ai_assistant/cli/app.py`
- `main.py`
- `docs/roadmap.md`
- `docs/architecture.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- None.

## Applicable ADRs

- ADR-006 ModelProvider port
- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] The CLI no longer prints provider debug information.
- [x] DummyModel still works by default.
- [x] Provider factory tests pass.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_model_adapter
PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.respond('hello').content)"
```

## Risks

- Accidentally changing provider defaults or environment variable behavior.

## Result report

- Summary: Removed accidental provider debug stdout from `ModelAdapter.from_env()`.
- Files changed: `ai_assistant/agent/models/adapter.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_model_adapter`; `PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.respond('hello').content)"`
- Test results: model adapter tests passed; CLI smoke exited 0 and printed only `Echo: hello`.
- Assumptions: CLI response printing in `ai_assistant/cli/app.py` is user-facing output, not debug output.
- Remaining issues: None for this task.
- Recommended follow-up: Implement logging in Milestone 8, not in M1.

### Task M1-T2 — Verify Ignore Rules

## Parent milestone

M1

## Status

implemented

## Owner role

Documentation agent

## Objective

Ensure repository ignore rules cover generated local artifacts named in Milestone 1.

## Scope

- Verify `.gitignore` ignores `__pycache__/`, `*.pyc`, `assistant.sqlite3` and equivalent local databases.
- Verify generated artifacts do not appear in normal `git status`.
- Preserve project source and docs visibility.

## Explicit exclusions

- No deletion of user data.
- No Git index removal unless artifacts are confirmed tracked and safe.
- No broad language-template ignore file.

## File scope

### Writable

- `.gitignore`

### Read-only

- repository tree
- `docs/roadmap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- None.

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] `__pycache__/` is ignored.
- [x] `*.pyc` is ignored.
- [x] `assistant.sqlite3` and equivalent local DB files are ignored.
- [x] No tracked generated artifacts require destructive removal.

## Validation commands

```bash
git status --short
git status --short --ignored
git ls-files '*__pycache__*' '*.pyc' '*.sqlite3' 'c_toolserver/build/*'
```

## Risks

- Hiding a real fixture database by using overly broad database ignore rules.

## Result report

- Summary: Verified `.gitignore` covers generated Python artifacts, local SQLite databases, C build output, virtual environments and local Codex/session files.
- Files changed: none during this supervisor run; `.gitignore` already satisfied M1 criteria.
- Tests run: `git status --short`; `git status --short --ignored`; `git ls-files '*__pycache__*' '*.pyc' '*.sqlite3' 'c_toolserver/build/*'`; `git check-ignore -v assistant.sqlite3 __pycache__/main.cpython-314.pyc ai_assistant/agent/__pycache__/runtime.cpython-314.pyc c_toolserver/build/toolserver codex .codex venv/bin/python`
- Test results: generated artifacts are ignored and no tracked generated artifacts were reported by `git ls-files`.
- Assumptions: Broad `*.db` ignore is acceptable for local assistant data until fixture databases are introduced.
- Remaining issues: Existing generated files still exist on disk but are ignored.
- Recommended follow-up: If fixture DBs are added later, use an explicit negate rule such as `!tests/fixtures/*.db`.

### Task M1-T3 — Validate Milestone 1

## Parent milestone

M1

## Status

implemented

## Owner role

Integration validator

## Objective

Map Milestone 1 acceptance criteria to evidence and prepare human review.

## Scope

- Run available validation commands.
- Record environment-blocked checks.
- Write `.agent/reports/M1.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M1 accepted.
- Do not request out-of-scope fixes for Unix socket sandbox failures.
- Do not modify roadmap priorities.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M1.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M1-T1
- M1-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] CLI output is clean.
- [x] Generated artifacts are ignored.
- [x] DummyModel still works.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_agent_runtime tests.test_model_adapter
PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.respond('hello').content)"
git status --short
git status --short --ignored
```

## Risks

- Full suite remains environment-blocked by Unix socket restrictions.

## Result report

- Summary: Validated M1 criteria, recorded environment-blocked full suite issue, and prepared human review artifacts.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M1.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests`; `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_agent_runtime tests.test_model_adapter tests.test_framing`; CLI smoke; Git ignore/status commands.
- Test results: full suite passed after permissions were adjusted; focused tests passed; CLI smoke passed.
- Assumptions: CLI response printing is expected user-facing output.
- Remaining issues: None for M1.
- Recommended follow-up: Human review should verify M1 before M2 starts.

## Dependency rules

- A task becomes `ready` only when every dependency is `implemented`.
- A task requiring human approval remains `blocked`.
- A failed task creates a corrective task; it is not silently retried.
- Canonical state updates are performed only after supervisor review.

### Task M2-T1 — Add Pytest Configuration

## Parent milestone

M2

## Status

implemented

## Owner role

Test agent

## Objective

Declare pytest as a development dependency and configure the base markers required by the roadmap.

## Scope

- Add a minimal development dependency file.
- Add pytest marker configuration.
- Keep production dependency graph unchanged.

## Explicit exclusions

- No CI.
- No Ollama tests.
- No production dependency.

## File scope

### Writable

- `requirements-dev.txt`
- `pytest.ini`

### Read-only

- `docs/roadmap.md`
- `docs/adr/ADR-013-pytest-testing-strategy.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M1 accepted.

## Applicable ADRs

- ADR-012 Minimal external dependencies
- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] pytest is declared as a development dependency.
- [x] `unit`, `integration`, `contract`, `ollama` and `smoke` markers are registered.
- [x] No production dependency file is introduced.

## Validation commands

```bash
python -m pytest --version
python -m pytest --markers
```

## Risks

- pytest may need installation in the local venv before validation.

## Result report

- Summary: Added `requirements-dev.txt` with pytest and `pytest.ini` with required markers.
- Files changed: `requirements-dev.txt`, `pytest.ini`
- Tests run: `python -m pytest --version`; `python -m pytest --markers`
- Test results: pytest 8.4.2 installed; required markers are registered.
- Assumptions: `requirements-dev.txt` is the smallest dependency declaration because the repo has no packaging config.
- Remaining issues: None for this task.
- Recommended follow-up: M16 can wire the same commands into CI.

### Task M2-T2 — Convert Tests to Pytest Style

## Parent milestone

M2

## Status

implemented

## Owner role

Test agent

## Objective

Convert the currently discovered unittest test files to pytest style without weakening assertions.

## Scope

- Convert runtime/context/SQLite tests.
- Convert model adapter tests.
- Convert framing tests.
- Convert Unix socket client tests.
- Use pytest `tmp_path` for SQLite and socket temporary paths.

## Explicit exclusions

- No production code changes.
- No Ollama tests.
- No C toolserver integration rewrite.

## File scope

### Writable

- `tests/test_agent_runtime.py`
- `tests/test_model_adapter.py`
- `tests/test_framing.py`
- `tests/test_unix_socket_client.py`

### Read-only

- `ai_assistant/`
- `tests/integration_c_toolserver.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2-T1

## Applicable ADRs

- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] Tests use pytest functions and assertions.
- [x] SQLite test uses pytest temporary path support.
- [x] Unix socket tests remain present and marked as integration.
- [x] Assertions are not weakened.

## Validation commands

```bash
python -m pytest
python -m pytest -m unit
python -m pytest -m integration
```

## Risks

- Local Unix socket permissions can affect integration tests.

## Result report

- Summary: Converted discovered unittest test files to pytest functions, assertions and markers.
- Files changed: `tests/test_agent_runtime.py`, `tests/test_model_adapter.py`, `tests/test_framing.py`, `tests/test_unix_socket_client.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`
- Test results: 12 passed; 10 unit passed; 2 integration passed.
- Assumptions: `tests/integration_c_toolserver.py` remains a manual integration script because it is not part of the currently discovered test suite and depends on the C binary.
- Remaining issues: `python -m unittest discover -s tests` now runs 0 tests, as expected after migration.
- Recommended follow-up: Convert the C integration script into a marked pytest test only when M16/CI or toolserver scope requires it.

### Task M2-T3 — Validate Pytest Migration

## Parent milestone

M2

## Status

implemented

## Owner role

Integration validator

## Objective

Verify all Milestone 2 acceptance criteria and prepare human review.

## Scope

- Run pytest validations.
- Confirm no Ollama dependency.
- Confirm SQLite uses temporary files.
- Write `.agent/reports/M2.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M2 accepted.
- Do not start M3.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M2.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M2-T2

## Applicable ADRs

- ADR-012 Minimal external dependencies
- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] All existing tests pass with pytest.
- [x] Test suite does not depend on Ollama.
- [x] SQLite tests use temporary files.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
python -m pytest
python -m pytest -m unit
python -m pytest -m integration
```

## Risks

- pytest installation requires network access if not already installed.

## Result report

- Summary: Validated pytest migration and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M2.md`
- Tests run: `python -m pytest`; `python -m pytest -m unit`; `python -m pytest -m integration`; `python -m pytest --markers`
- Test results: 12 passed; 10 unit passed; 2 integration passed; required markers present.
- Assumptions: `tests/integration_c_toolserver.py` remains a manual script outside current pytest discovery.
- Remaining issues: None for M2.
- Recommended follow-up: Human review should verify M2 before M3 starts.

### Task M3-T1 — Thread Runtime Session IDs

## Parent milestone

M3

## Status

implemented

## Owner role

Runtime implementer

## Objective

Make runtime and in-memory conversation history use an explicit string session ID.

## Scope

- Define shared session ID defaults.
- Update runtime to use `session_id`.
- Update in-memory store to isolate history by session.
- Keep CLI default session as `default`.
- Allow `AI_ASSISTANT_SESSION` to select the CLI session.

## Explicit exclusions

- No interactive session management.
- No listing, renaming or deleting sessions.
- No transaction work.

## File scope

### Writable

- `ai_assistant/agent/memory.py`
- `ai_assistant/agent/runtime.py`
- `ai_assistant/cli/app.py`
- `tests/test_agent_runtime.py`

### Read-only

- `docs/adr/ADR-005-explicit-string-session-ids.md`
- `docs/roadmap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M2 accepted.

## Applicable ADRs

- ADR-005 Explicit string session IDs
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] Runtime stores and reads history for its configured session.
- [x] In-memory store isolates sessions.
- [x] CLI default session is `default`.
- [x] CLI can read `AI_ASSISTANT_SESSION`.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- Breaking existing store callers during contract change.

## Result report

- Summary: Added explicit session ID support to runtime and in-memory store; CLI reads `AI_ASSISTANT_SESSION` with `default` fallback.
- Files changed: `ai_assistant/agent/memory.py`, `ai_assistant/agent/runtime.py`, `ai_assistant/cli/app.py`, `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`
- Test results: unit tests passed after implementation.
- Assumptions: Direct CLI `os.getenv` remains temporary until configuration/bootstrap milestones.
- Remaining issues: None for this task.
- Recommended follow-up: M7 should centralize this env read.

### Task M3-T2 — Persist SQLite Sessions

## Parent milestone

M3

## Status

implemented

## Owner role

Persistence implementer

## Objective

Persist and retrieve SQLite conversation messages by explicit session ID.

## Scope

- Add non-destructive SQLite migration for `session_id`.
- Add index by session/order.
- Filter history by session.
- Store messages with session IDs.
- Add tests for session isolation and persistence between store instances.

## Explicit exclusions

- No destructive migration.
- No interactive session management.
- No transactional `append_many`.

## File scope

### Writable

- `ai_assistant/storage/sqlite_memory.py`
- `tests/test_agent_runtime.py`

### Read-only

- `ai_assistant/agent/memory.py`
- `docs/adr/ADR-004-sqlite-conversation-persistence.md`
- `docs/adr/ADR-005-explicit-string-session-ids.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M3-T1

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-005 Explicit string session IDs

## Acceptance criteria

- [x] Two SQLite sessions do not share history.
- [x] Restarting a store preserves session history.
- [x] Existing message rows migrate to `default`.
- [x] Message order is preserved.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Migration bugs on existing SQLite files.

## Result report

- Summary: Added non-destructive SQLite `session_id` migration, session index, session-filtered history and tests.
- Files changed: `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest`
- Test results: full and unit pytest suites passed after implementation.
- Assumptions: Existing rows belong to the `default` session.
- Remaining issues: None for M3 scope.
- Recommended follow-up: M4 should add transactional `append_many`.

### Task M3-T3 — Validate Explicit Sessions

## Parent milestone

M3

## Status

implemented

## Owner role

Integration validator

## Objective

Verify all Milestone 3 acceptance criteria and prepare human review.

## Scope

- Run pytest validation.
- Run CLI smoke with default session.
- Run CLI smoke with `AI_ASSISTANT_SESSION`.
- Write `.agent/reports/M3.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M3 accepted.
- Do not start M4.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M3.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M3-T2

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-005 Explicit string session IDs

## Acceptance criteria

- [x] Two sessions do not share history.
- [x] CLI uses `default`.
- [x] Restarting the CLI/store preserves history.
- [x] Message order is preserved.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
AI_ASSISTANT_SESSION=alt PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.session_id)"
```

## Risks

- Existing ignored `assistant.sqlite3` may be migrated locally during CLI smoke.

## Result report

- Summary: Validated explicit session support and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M3.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`; CLI session smoke commands.
- Test results: 15 passed; 13 unit passed; 2 integration passed; CLI smoke printed `default` and `alt`.
- Assumptions: Whitespace-preserving session IDs are acceptable until interactive session management exists.
- Remaining issues: None for M3.
- Recommended follow-up: Human review should verify M3 before M4 starts.

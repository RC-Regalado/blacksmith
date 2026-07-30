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
| M4-T1 | M4 | Persistence implementer | Add transactional append_many to conversation stores | `ai_assistant/agent/memory.py`, `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py` | M3 | implemented |
| M4-T2 | M4 | Runtime implementer | Persist complete turns through append_many | `ai_assistant/agent/runtime.py`, `tests/test_agent_runtime.py` | M4-T1 | implemented |
| M4-T3 | M4 | Integration validator | Validate transactional persistence and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M4.md` | M4-T2 | implemented |
| M5-T1 | M5 | Architect | Create explicit application ports for model and memory | `ai_assistant/application/ports/`, `ai_assistant/agent/models/provider.py`, `ai_assistant/agent/memory.py` | M4 | implemented |
| M5-T2 | M5 | Runtime implementer | Update runtime/providers/tests to depend on ports and fakes | `ai_assistant/agent/runtime.py`, `ai_assistant/agent/models/*.py`, `ai_assistant/cli/app.py`, `tests/test_agent_runtime.py`, `tests/test_ports_contract.py` | M5-T1 | implemented |
| M5-T3 | M5 | Integration validator | Validate explicit ports and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M5.md` | M5-T2 | implemented |
| M6-T1 | M6 | Architect | Add bootstrap composition root | `ai_assistant/bootstrap/`, `ai_assistant/cli/app.py`, `tests/test_cli_app.py` | M5 | implemented |
| M6-T2 | M6 | Runtime implementer | Move CLI runtime construction to bootstrap | `ai_assistant/bootstrap/container.py`, `ai_assistant/cli/app.py`, `ai_assistant/main.py`, `tests/test_cli_app.py` | M6-T1 | implemented |
| M6-T3 | M6 | Integration validator | Validate composition root and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M6.md` | M6-T2 | implemented |
| M7-T1 | M7 | Runtime implementer | Add immutable bootstrap AppConfig loader | `ai_assistant/bootstrap/config.py`, `tests/test_config.py` | M6 | implemented |
| M7-T2 | M7 | Runtime implementer | Wire AppConfig through composition root and model adapter config | `ai_assistant/bootstrap/container.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_cli_app.py`, `tests/test_model_adapter.py` | M7-T1 | implemented |
| M7-T3 | M7 | Integration validator | Validate centralized configuration and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M7.md` | M7-T2 | implemented |
| M8-T1 | M8 | Runtime implementer | Configure stdlib logging at bootstrap | `ai_assistant/bootstrap/logging.py`, `ai_assistant/bootstrap/container.py`, `ai_assistant/bootstrap/config.py`, `tests/test_logging.py`, `tests/test_config.py` | M7 | implemented |
| M8-T2 | M8 | Runtime implementer | Add safe runtime and adapter log events | `ai_assistant/agent/runtime.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/openai_compatible.py`, `tests/test_logging.py` | M8-T1 | implemented |
| M8-T3 | M8 | Integration validator | Validate basic logging and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M8.md` | M8-T2 | implemented |
| M9-T1 | M9 | Runtime implementer | Define internal error hierarchy and map validation errors | `ai_assistant/application/errors.py`, `ai_assistant/agent/message.py`, `ai_assistant/application/ports/memory.py`, `ai_assistant/bootstrap/config.py`, `ai_assistant/bootstrap/logging.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_errors.py`, `tests/test_config.py`, `tests/test_model_adapter.py`, `tests/test_memory_stores.py` | M8 | implemented |
| M9-T2 | M9 | Runtime implementer | Map infrastructure failures and CLI messages | `ai_assistant/storage/sqlite_memory.py`, `ai_assistant/agent/models/openai_compatible.py`, `ai_assistant/cli/app.py`, `tests/test_errors.py`, `tests/test_logging.py`, `tests/test_cli_app.py` | M9-T1 | implemented |
| M9-T3 | M9 | Integration validator | Validate typed errors and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M9.md` | M9-T2 | implemented |
| M10-T1 | M10 | Model provider implementer | Add native Ollama chat provider | `ai_assistant/agent/models/ollama.py`, `tests/test_ollama_model.py` | M9 | implemented |
| M10-T2 | M10 | Model provider implementer | Wire Ollama provider through config and adapter factory | `ai_assistant/bootstrap/config.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/__init__.py`, `tests/test_config.py`, `tests/test_model_adapter.py`, `tests/test_ollama_model.py`, `tests/test_ollama_smoke.py` | M10-T1 | implemented |
| M10-T3 | M10 | Integration validator | Validate native Ollama adapter and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M10.md` | M10-T2 | implemented |
| M11-T1 | M11 | Documentation agent | Document local model profiles and evaluation guide | `docs/model-profiles.md`, `docs/architecture.md` | M10 | implemented |
| M11-T2 | M11 | Runtime implementer | Keep model and context configurable without hardcoded model default | `ai_assistant/bootstrap/config.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_config.py`, `tests/test_smoke.py` | M11-T1 | implemented |
| M11-T3 | M11 | Integration validator | Validate model profiles and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M11.md` | M11-T2 | implemented |
| M12-T1 | M12 | Runtime implementer | Add simple recent-history context budget policy | `ai_assistant/agent/context.py`, `tests/test_agent_runtime.py` | M11 | implemented |
| M12-T2 | M12 | Runtime implementer | Wire configured context limit through bootstrap | `ai_assistant/bootstrap/container.py`, `tests/test_cli_app.py`, `tests/test_config.py` | M12-T1 | implemented |
| M12-T3 | M12 | Integration validator | Validate context budget and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M12.md` | M12-T2 | implemented |
| M13-T1 | M13 | Model provider implementer | Harden OpenAI-compatible request and response mappers | `ai_assistant/agent/models/openai_compatible.py`, `tests/test_openai_compatible.py` | M12 | implemented |
| M13-T2 | M13 | Model provider implementer | Verify OpenAI-compatible factory and port contract | `ai_assistant/agent/models/adapter.py`, `tests/test_model_adapter.py`, `tests/test_openai_compatible.py` | M13-T1 | implemented |
| M13-T3 | M13 | Integration validator | Validate robust OpenAI-compatible adapter and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M13.md` | M13-T2 | implemented |
| M14-T1 | M14 | Runtime implementer | Define declarative tool-call models and interpreter | `ai_assistant/agent/planner.py`, `ai_assistant/application/errors.py`, `tests/test_tools.py` | M13 | implemented |
| M14-T2 | M14 | Runtime implementer | Preserve interpreted tool plan in runtime without execution | `ai_assistant/agent/runtime.py`, `tests/test_agent_runtime.py`, `tests/test_tools.py` | M14-T1 | implemented |
| M14-T3 | M14 | Integration validator | Validate declarative tools and produce review artifacts | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M14.md` | M14-T2 | implemented |
| M15-T1 | M15 | Architect | Establish canonical domain, application, infrastructure and interfaces modules | `ai_assistant/domain/`, `ai_assistant/application/`, `ai_assistant/infrastructure/`, `ai_assistant/interfaces/`, legacy compatibility modules | M14 | implemented |
| M15-T2 | M15 | Runtime implementer | Wire bootstrap and entry points to the layered modules without changing behavior | `ai_assistant/bootstrap/container.py`, `ai_assistant/main.py`, tests | M15-T1 | implemented |
| M15-T3 | M15 | Integration validator | Validate layer dependency rules, CLI smoke and full tests | `tests/test_layering.py`, `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M15.md` | M15-T2 | implemented |
| M16-T1 | M16 | Test agent | Add separated CI jobs for unit, integration, contract and smoke tests | `.github/workflows/ci.yml` | M15 | implemented |
| M16-T2 | M16 | Test agent | Add isolated optional Ollama smoke job | `.github/workflows/ci.yml` | M16-T1 | implemented |
| M16-T3 | M16 | Integration validator | Validate CI commands locally where possible and prepare M16 report | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M16.md` | M16-T2 | implemented |
| M17-T1 | M17 | Documentation agent | Add developer README with setup, configuration, tests and limitations | `README.md`, `context-ai.md`, `docs/model-profiles.md` | M16 | implemented |
| M17-T2 | M17 | Documentation agent | Close ADR index and statuses for implemented Phase 1 decisions | `docs/adr/*.md`, `docs/adr/README.md` | M17-T1 | implemented |
| M17-T3 | M17 | Integration validator | Validate Phase 1 documentation and produce final report | `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M17.md` | M17-T2 | implemented |
| M2.1-T1 | M2.1 | Phase 2 architect | Draft Proposed ADR-016 through ADR-025 for Phase 2 read-only tool policy | `docs/adr/ADR-016-*.md` through `docs/adr/ADR-025-*.md`, `docs/adr/README.md` | Phase 1 accepted | implemented |
| M2.1-T2 | M2.1 | Documentation agent | Update architecture with Phase 2 security policy and read-only tool contracts | `docs/architecture.md`, `docs/roadmap-phase-2.md`, `context-ai.md` | M2.1-T1 | implemented |
| M2.1-T3 | M2.1 | Security reviewer | Review proposed policy for no shell, workspace confinement, sensitive files, audit and one-round bound | read-only repository review | M2.1-T2 | implemented |
| M2.1-T4 | M2.1 | Integration validator | Validate M2.1 acceptance criteria and prepare human approval package | `.agent/reports/M2.1.md`, `.agent/human-review.md`, `.agent/roadmap-state.md`, `.agent/task-queue.md` | M2.1-T3 | implemented |

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

### Task M4-T1 — Add Transactional append_many

## Parent milestone

M4

## Status

implemented

## Owner role

Persistence implementer

## Objective

Add `append_many` to conversation stores so multiple messages can be persisted atomically.

## Scope

- Add `append_many(session_id, messages)` to `ConversationMemory`.
- Implement in-memory append with all-or-nothing validation.
- Implement SQLite append in one transaction.
- Add rollback test for SQLite.

## Explicit exclusions

- No session changes.
- No WAL or advanced locking.
- No retries or nested transaction API.

## File scope

### Writable

- `ai_assistant/agent/memory.py`
- `ai_assistant/storage/sqlite_memory.py`
- `tests/test_agent_runtime.py`

### Read-only

- `docs/adr/ADR-010-transactional-turn-persistence.md`
- `docs/roadmap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M3 accepted.

## Applicable ADRs

- ADR-010 Transactional turn persistence
- ADR-004 SQLite conversation persistence

## Acceptance criteria

- [x] `append_many` exists on the store contract.
- [x] SQLite writes multiple messages in one transaction.
- [x] SQLite rollback leaves no partial turn.
- [x] In-memory store has equivalent all-or-nothing behavior.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- A rollback test may depend on SQLite constraints.

## Result report

- Summary: Added `append_many` to memory contract, in-memory store and SQLite store.
- Files changed: `ai_assistant/agent/memory.py`, `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest`
- Test results: unit and full pytest suites passed.
- Assumptions: SQLite context manager transaction semantics are sufficient for Phase 1.
- Remaining issues: Existing SQLite tables do not gain the new role `CHECK`; rollback behavior is still transactional for DB errors.
- Recommended follow-up: M9 can normalize persistence errors.

### Task M4-T2 — Runtime Uses append_many

## Parent milestone

M4

## Status

implemented

## Owner role

Runtime implementer

## Objective

Persist user and assistant messages as one complete turn.

## Scope

- Update `AgentRuntime._persist_turn()` to call `append_many`.
- Preserve existing response behavior.
- Add runtime test proving a failing second append leaves no user-only turn.

## Explicit exclusions

- No model retry behavior.
- No error hierarchy.
- No transaction implementation inside runtime.

## File scope

### Writable

- `ai_assistant/agent/runtime.py`
- `tests/test_agent_runtime.py`

### Read-only

- `ai_assistant/agent/memory.py`
- `docs/adr/ADR-010-transactional-turn-persistence.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M4-T1

## Applicable ADRs

- ADR-010 Transactional turn persistence
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] Runtime persists complete turns through `append_many`.
- [x] Runtime does not manually perform transaction logic.
- [x] A store failure cannot leave a user-only turn through runtime.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- Test fake must not encode behavior unlike the store contract.

## Result report

- Summary: Updated runtime to persist user and assistant messages through one `append_many` call.
- Files changed: `ai_assistant/agent/runtime.py`, `tests/test_agent_runtime.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`
- Test results: unit tests passed.
- Assumptions: Store owns transaction semantics; runtime only calls the contract.
- Remaining issues: None for this task.
- Recommended follow-up: None.

### Task M4-T3 — Validate Transactional Persistence

## Parent milestone

M4

## Status

implemented

## Owner role

Integration validator

## Objective

Verify all Milestone 4 acceptance criteria and prepare human review.

## Scope

- Run pytest validation.
- Review combined diff.
- Write `.agent/reports/M4.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M4 accepted.
- Do not start M5.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M4.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M4-T2

## Applicable ADRs

- ADR-010 Transactional turn persistence

## Acceptance criteria

- [x] User and assistant messages are written together.
- [x] On error, neither message is persisted.
- [x] Message order is preserved.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration
```

## Risks

- Full suite may expose unrelated integration issues.

## Result report

- Summary: Validated transactional persistence and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M4.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py -q`
- Test results: 18 passed; 16 unit passed; 2 integration passed; agent runtime tests 9 passed.
- Assumptions: Existing migrated SQLite tables may not have the new role `CHECK`, but `append_many` remains transactional for DB errors.
- Remaining issues: None for M4.
- Recommended follow-up: Human review should verify M4 before M5 starts.

### Task M5-T1 — Create Explicit Application Ports

## Parent milestone

M5

## Status

implemented

## Owner role

Architect

## Objective

Move model and memory contracts into explicit application ports.

## Scope

- Create `ai_assistant/application/ports/models.py`.
- Create `ai_assistant/application/ports/memory.py`.
- Keep compatibility imports for existing modules.

## Explicit exclusions

- No full layered repo reorganization.
- No DI framework.
- No provider behavior changes.

## File scope

### Writable

- `ai_assistant/application/`
- `ai_assistant/agent/models/provider.py`
- `ai_assistant/agent/memory.py`

### Read-only

- `docs/adr/ADR-001-ports-and-adapters.md`
- `docs/adr/ADR-006-modelprovider-port.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M4 accepted.

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] ModelProvider port lives under `application/ports`.
- [x] ConversationMemory port lives under `application/ports`.
- [x] Compatibility imports still work.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- Import cycles if ports import infrastructure.

## Result report

- Summary: Added explicit application ports for model and memory and compatibility re-exports.
- Files changed: `ai_assistant/application/__init__.py`, `ai_assistant/application/ports/__init__.py`, `ai_assistant/application/ports/models.py`, `ai_assistant/application/ports/memory.py`, `ai_assistant/agent/models/provider.py`, `ai_assistant/agent/memory.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`
- Test results: unit tests passed.
- Assumptions: `Message` remains in `agent` until M15 reorganizes domain/application layers.
- Remaining issues: None for M5 scope.
- Recommended follow-up: M15 can remove compatibility import modules if desired.

### Task M5-T2 — Update Runtime and Tests to Ports

## Parent milestone

M5

## Status

implemented

## Owner role

Runtime implementer

## Objective

Make runtime and providers depend on explicit ports, and runtime tests use fakes.

## Scope

- Update runtime imports to application ports.
- Update model providers/adapters imports to application ports.
- Add fake model/store for runtime tests.
- Preserve existing behavior.

## Explicit exclusions

- No composition root.
- No moved infrastructure packages.
- No public API removal.

## File scope

### Writable

- `ai_assistant/agent/runtime.py`
- `ai_assistant/agent/models/adapter.py`
- `ai_assistant/agent/models/dummy.py`
- `ai_assistant/agent/models/openai_compatible.py`
- `ai_assistant/agent/models/__init__.py`
- `ai_assistant/cli/app.py`
- `tests/test_agent_runtime.py`
- `tests/test_ports_contract.py`

### Read-only

- `ai_assistant/storage/sqlite_memory.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M5-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] Runtime imports model and memory ports from `application/ports`.
- [x] Runtime does not import SQLite, Ollama or OpenAI.
- [x] Runtime tests use fakes for runtime behavior.
- [x] Provider tests still pass.
- [x] Basic port contract tests exist.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Backward-compatible re-exports may hide old imports.

## Result report

- Summary: Updated runtime/providers to use application ports and split runtime tests from store implementation tests.
- Files changed: `ai_assistant/agent/runtime.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/dummy.py`, `ai_assistant/agent/models/openai_compatible.py`, `ai_assistant/agent/models/__init__.py`, `ai_assistant/cli/app.py`, `ai_assistant/storage/sqlite_memory.py`, `tests/test_agent_runtime.py`, `tests/test_memory_stores.py`, `tests/test_ports_contract.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract`; import `rg` checks.
- Test results: full, unit and contract pytest suites passed; runtime import checks returned no matches.
- Assumptions: Store implementation tests can import concrete SQLite store; runtime tests use fakes.
- Remaining issues: None for M5 scope.
- Recommended follow-up: M6 should move CLI construction into a composition root.

### Task M5-T3 — Validate Explicit Ports

## Parent milestone

M5

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M5 acceptance criteria and prepare human review.

## Scope

- Run pytest validation.
- Inspect runtime imports.
- Write `.agent/reports/M5.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M5 accepted.
- Do not start M6.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M5.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M5-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-006 ModelProvider port

## Acceptance criteria

- [x] Runtime no longer imports concrete infrastructure ports.
- [x] Runtime tests use fakes.
- [x] Full pytest suite passes.
- [x] Validation evidence is recorded for human review.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
rg -n "from ai_assistant\\.(storage|agent\\.models\\.(dummy|openai_compatible|adapter))" ai_assistant/agent/runtime.py tests/test_agent_runtime.py
```

## Risks

- Full ports/layers cleanup is deferred to M15.

## Result report

- Summary: Validated explicit ports and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M5.md`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`; runtime concrete-import `rg` check.
- Test results: 20 passed; 16 unit passed; 2 contract passed; 2 integration passed; runtime import check found no matches.
- Assumptions: `Message` remains under `agent` until M15 layered reorganization.
- Remaining issues: None for M5.
- Recommended follow-up: Human review should verify M5 before M6 starts.

### Task M6-T1 — Add Bootstrap Composition Root

## Parent milestone

M6

## Status

implemented

## Owner role

Architect

## Objective

Create a bootstrap composition root that owns runtime construction.

## Scope

- Add `ai_assistant/bootstrap/container.py`.
- Add `create_application()`.
- Keep dependency construction out of CLI.

## Explicit exclusions

- No DI framework.
- No config object milestone work.
- No dynamic discovery.

## File scope

### Writable

- `ai_assistant/bootstrap/`
- `ai_assistant/cli/app.py`
- `tests/test_cli_app.py`

### Read-only

- `docs/roadmap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M5 accepted.

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap

## Acceptance criteria

- [x] `create_application()` exists.
- [x] Bootstrap builds runtime dependencies.
- [x] CLI no longer imports concrete model/store adapters.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
```

## Risks

- Import cycles.

## Result report

- Summary: Added bootstrap composition root and moved runtime construction there.
- Files changed: `ai_assistant/bootstrap/__init__.py`, `ai_assistant/bootstrap/container.py`, `ai_assistant/cli/app.py`, `tests/test_cli_app.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`
- Test results: 18 unit tests passed.
- Assumptions: Full configuration object remains for M7.
- Remaining issues: None for this task.
- Recommended follow-up: M7 should replace direct env reads in bootstrap/model adapter.

### Task M6-T2 — Move CLI Runtime Construction

## Parent milestone

M6

## Status

implemented

## Owner role

Runtime implementer

## Objective

Make CLI receive an application/runtime from bootstrap while preserving `python main.py`.

## Scope

- Introduce a small CLI app object or equivalent function boundary.
- Keep `run_cli()` working.
- Add tests proving CLI app can be constructed with fakes.

## Explicit exclusions

- No config dataclass.
- No logging.
- No changed CLI commands.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/cli/app.py`
- `ai_assistant/main.py`
- `tests/test_cli_app.py`

### Read-only

- `ai_assistant/agent/runtime.py`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/decisions.md`

## Dependencies

- M6-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap

## Acceptance criteria

- [x] `main.py` still starts CLI.
- [x] CLI can be constructed with fake runtime.
- [x] CLI does not import concrete model/store adapters.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
```

## Risks

- Tests around `input()`/`print()` can overfit CLI internals.

## Result report

- Summary: CLI now owns input/output loop only and delegates construction to bootstrap.
- Files changed: `ai_assistant/bootstrap/container.py`, `ai_assistant/cli/app.py`, `tests/test_cli_app.py`
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py`; CLI concrete-import `rg` check.
- Test results: full pytest passed; CLI smoke exited 0; import check found no matches.
- Assumptions: Lazy import inside `run_cli()` avoids a bootstrap/CLI import cycle.
- Remaining issues: None for this task.
- Recommended follow-up: M7 centralizes config values.

### Task M6-T3 — Validate Composition Root

## Parent milestone

M6

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M6 acceptance criteria and prepare human review.

## Scope

- Run pytest validation.
- Run CLI smoke.
- Write `.agent/reports/M6.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M6 accepted.
- Do not start M7.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M6.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M6-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap

## Acceptance criteria

- [x] `main.py` only starts the application.
- [x] CLI does not import concrete adapters.
- [x] Tests can construct CLI with fakes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "SQLiteConversationStore|ModelAdapter|ContextBuilder|ToolCallDetector" ai_assistant/cli/app.py
```

## Risks

- M7 will still need to centralize configuration object.

## Result report

- Summary: Validated the M6 composition root, CLI injection path and independent read-only review.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M6.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py`; `rg -n "SQLiteConversationStore|ModelAdapter|ContextBuilder|ToolCallDetector" ai_assistant/cli/app.py`.
- Test results: full pytest passed with 22 tests; unit suite passed with 18 tests and 4 deselected; integration suite passed with 2 tests and 20 deselected; CLI smoke exited 0; CLI concrete-adapter import check found no matches.
- Assumptions: M7 will replace direct environment reads in the bootstrap with centralized configuration.
- Remaining issues: None for M6.
- Recommended follow-up: Human review before starting M7.

### Task M7-T1 — Add Bootstrap AppConfig

## Parent milestone

M7

## Status

implemented

## Owner role

Runtime implementer

## Objective

Create an immutable, validated configuration object loaded from environment-style mappings.

## Scope

- Define `AppConfig` in bootstrap.
- Provide defaults for M7 environment variables.
- Validate provider, timeout and context limit.
- Add focused unit tests.

## Explicit exclusions

- No `.env`, TOML, YAML or Pydantic.
- No model profiles.
- No Ollama implementation.

## File scope

### Writable

- `ai_assistant/bootstrap/config.py`
- `tests/test_config.py`

### Read-only

- `docs/roadmap.md`
- `docs/architecture.md`
- `docs/adr/ADR-007-configuration-at-bootstrap.md`

### Forbidden

- `.agent/roadmap-state.md`
- `.agent/human-review.md`

## Dependencies

- M6 accepted

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] `AppConfig` is immutable.
- [x] Defaults are explicit and testable.
- [x] Invalid provider raises a clear error.
- [x] Invalid timeout raises a clear error.
- [x] Invalid context limit raises a clear error.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py -q
```

## Risks

- Defaults may drift from existing CLI behavior.

## Result report

- Summary: Added immutable `AppConfig` and mapping-based loader with explicit defaults and validation.
- Files changed: `ai_assistant/bootstrap/config.py`, `tests/test_config.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py -q`.
- Test results: 6 passed.
- Assumptions: `OPENAI_API_KEY` remains provider-specific secret input because the existing OpenAI-compatible adapter requires it.
- Remaining issues: None for this task.
- Recommended follow-up: Wire config through bootstrap.

### Task M7-T2 — Wire AppConfig Through Bootstrap

## Parent milestone

M7

## Status

implemented

## Owner role

Runtime implementer

## Objective

Use `AppConfig` in the composition root and remove model adapter environment reads.

## Scope

- Load configuration once in bootstrap.
- Pass config values into context, SQLite, session and model adapter construction.
- Remove `ModelAdapter.from_env()`.
- Update tests.

## Explicit exclusions

- No DI framework.
- No logging.
- No new provider implementation.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/agent/models/adapter.py`
- `tests/test_cli_app.py`
- `tests/test_model_adapter.py`

### Read-only

- `ai_assistant/cli/app.py`
- `ai_assistant/agent/runtime.py`
- `ai_assistant/storage/sqlite_memory.py`

### Forbidden

- Persistent SQLite schema

## Dependencies

- M7-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Configuration is loaded once at bootstrap.
- [x] No adapter reads environment variables.
- [x] Existing CLI startup still works.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "os\\.getenv|os\\.environ|from_env" ai_assistant | rg -v "ai_assistant/bootstrap/config.py"
```

## Risks

- Existing provider environment variable names may change.

## Result report

- Summary: Wired `AppConfig` through `create_application()` and removed `ModelAdapter.from_env()`.
- Files changed: `ai_assistant/bootstrap/container.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_cli_app.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `rg -n "os\\.getenv|os\\.environ|from_env" ai_assistant`.
- Test results: 24 passed, 4 deselected; only `ai_assistant/bootstrap/config.py` reads `os.environ`.
- Assumptions: M10 will add Ollama as a supported provider; M7 validates only providers implemented today.
- Remaining issues: None for this task.
- Recommended follow-up: Full milestone validation.

### Task M7-T3 — Validate Centralized Configuration

## Parent milestone

M7

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M7 acceptance criteria and prepare human review.

## Scope

- Run unit and full pytest validation.
- Run CLI smoke.
- Write `.agent/reports/M7.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M7 accepted.
- Do not start M8.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M7.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M7-T2

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Configuration is loaded once.
- [x] Invalid configuration errors are clear.
- [x] Runtime does not use `os.environ`.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "os\\.getenv|os\\.environ|from_env" ai_assistant | rg -v "ai_assistant/bootstrap/config.py"
```

## Risks

- Environment-dependent tests may need isolated mappings.

## Result report

- Summary: Validated M7 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M7.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py`; `rg -n "os\\.getenv|os\\.environ|from_env" ai_assistant | rg -v "ai_assistant/bootstrap/config.py"`.
- Test results: config tests passed with 6 tests; unit suite passed with 24 tests and 4 deselected; full suite passed with 28 tests; CLI smoke exited 0; no environment reads found outside bootstrap config.
- Assumptions: `AI_ASSISTANT_PROVIDER` is the canonical provider variable from the roadmap.
- Remaining issues: Future logging must not print `AppConfig` because it can include `OPENAI_API_KEY`.
- Recommended follow-up: Human review before starting M8.

### Task M8-T1 — Configure Stdlib Logging

## Parent milestone

M8

## Status

implemented

## Owner role

Runtime implementer

## Objective

Configure Python stdlib logging from bootstrap using the configured log level.

## Scope

- Add bootstrap logging setup.
- Send logs to stderr.
- Validate logging level.
- Avoid duplicate handlers.
- Hide API key from config repr.
- Add focused tests.

## Explicit exclusions

- No JSON logging.
- No rotating files.
- No telemetry.

## File scope

### Writable

- `ai_assistant/bootstrap/logging.py`
- `ai_assistant/bootstrap/container.py`
- `ai_assistant/bootstrap/config.py`
- `tests/test_logging.py`
- `tests/test_config.py`

### Read-only

- `docs/roadmap.md`
- `docs/architecture.md`

### Forbidden

- Provider behavior

## Dependencies

- M7 accepted

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Logging is configured in bootstrap.
- [x] Log level is configurable.
- [x] Logs use stderr.
- [x] Duplicate handlers are avoided.
- [x] API key is not exposed through config repr.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py tests/test_config.py -q
```

## Risks

- Pytest logging handlers can make handler-count assertions brittle.

## Result report

- Summary: Added stdlib logging setup at bootstrap, configurable level validation and API key redaction from config repr.
- Files changed: `ai_assistant/bootstrap/logging.py`, `ai_assistant/bootstrap/container.py`, `ai_assistant/bootstrap/config.py`, `tests/test_logging.py`, `tests/test_config.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py tests/test_config.py -q`.
- Test results: 9 passed.
- Assumptions: Existing pytest logging handlers are acceptable; `basicConfig` avoids adding duplicate handlers when handlers already exist.
- Remaining issues: None for this task.
- Recommended follow-up: Add safe runtime and adapter log events.

### Task M8-T2 — Add Safe Runtime and Adapter Events

## Parent milestone

M8

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add diagnostic logs for runtime turns and model adapter calls without logging message content or secrets.

## Scope

- Log provider/model selection.
- Log runtime request lifecycle.
- Log model request duration.
- Log adapter errors without request/response bodies.
- Add tests that sensitive content is absent from logs.

## Explicit exclusions

- No typed errors.
- No retry policy.
- No logging of prompts, user input or assistant output.

## File scope

### Writable

- `ai_assistant/agent/runtime.py`
- `ai_assistant/agent/models/adapter.py`
- `ai_assistant/agent/models/openai_compatible.py`
- `tests/test_logging.py`

### Read-only

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/bootstrap/container.py`
- `ai_assistant/cli/app.py`

### Forbidden

- Persistent storage schema

## Dependencies

- M8-T1

## Applicable ADRs

- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] Provider and model are logged.
- [x] Request duration is logged.
- [x] Errors are logged without message content.
- [x] CLI stdout remains assistant-only.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py -q
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "print\\(" ai_assistant | rg -v "ai_assistant/cli/app.py"
```

## Risks

- Exception details can contain provider response bodies if logged directly.

## Result report

- Summary: Added provider/model logs, runtime lifecycle logs and OpenAI-compatible request duration/error logs without prompt, response, API key or body content.
- Files changed: `ai_assistant/agent/runtime.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/openai_compatible.py`, `tests/test_logging.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py > /tmp/blacksmith-m8-stdout.txt 2> /tmp/blacksmith-m8-stderr.txt`; `rg -n "print\\(" ai_assistant | rg -v "ai_assistant/cli/app.py"`.
- Test results: logging tests passed with 5 tests; unit suite passed with 30 tests and 4 deselected; CLI stdout contained only prompt; technical print check found no matches outside CLI response printing.
- Assumptions: Provider/model names are operational metadata, not secrets.
- Remaining issues: stderr includes INFO provider selection at default log level.
- Recommended follow-up: Full milestone validation.

### Task M8-T3 — Validate Basic Logging

## Parent milestone

M8

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M8 acceptance criteria and prepare human review.

## Scope

- Run unit and full pytest validation.
- Run CLI smoke.
- Check technical prints.
- Write `.agent/reports/M8.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M8 accepted.
- Do not start M9.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M8.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M8-T2

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] No technical prints exist.
- [x] Log level is configurable.
- [x] Secrets are not logged.
- [x] CLI stdout remains clean.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
rg -n "print\\(" ai_assistant | rg -v "ai_assistant/cli/app.py"
```

## Risks

- Smoke output can include stderr logs even when stdout is clean.

## Result report

- Summary: Validated M8 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M8.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_logging.py tests/test_config.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py > /tmp/blacksmith-m8-stdout.txt 2> /tmp/blacksmith-m8-stderr.txt`; `rg -n "print\\(" ai_assistant | rg -v "ai_assistant/cli/app.py"`.
- Test results: focused logging/config tests passed with 9 tests; unit suite passed with 30 tests and 4 deselected; full suite passed with 34 tests; CLI smoke exited 0 with clean stdout and logs on stderr; no technical prints found.
- Assumptions: Session IDs are operational identifiers and should remain non-secret.
- Remaining issues: M9 should sanitize public/provider error paths that still include HTTP response bodies in raised exceptions.
- Recommended follow-up: Human review before starting M9.

### Task M9-T1 — Define Internal Error Hierarchy

## Parent milestone

M9

## Status

implemented

## Owner role

Runtime implementer

## Objective

Define typed internal errors and map validation failures to them.

## Scope

- Add minimal error hierarchy.
- Map config, logging level, provider selection, message and session validation.
- Add focused tests.

## Explicit exclusions

- No broad domain package reorganization.
- No new metadata fields.

## File scope

### Writable

- `ai_assistant/application/errors.py`
- `ai_assistant/agent/message.py`
- `ai_assistant/application/ports/memory.py`
- `ai_assistant/bootstrap/config.py`
- `ai_assistant/bootstrap/logging.py`
- `ai_assistant/agent/models/adapter.py`
- `tests/test_errors.py`
- `tests/test_config.py`
- `tests/test_model_adapter.py`
- `tests/test_memory_stores.py`

### Read-only

- `docs/roadmap.md`
- `docs/architecture.md`

### Forbidden

- Future domain reorganization

## Dependencies

- M8 accepted

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Error hierarchy exists.
- [x] Configuration errors are typed.
- [x] Invalid messages are typed.
- [x] Invalid sessions are typed.
- [x] Provider selection errors are typed.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_errors.py tests/test_config.py tests/test_model_adapter.py tests/test_memory_stores.py -q
```

## Risks

- Tests that expected built-in exceptions need contract updates.

## Result report

- Summary: Added typed internal errors and mapped validation paths.
- Files changed: `ai_assistant/application/errors.py`, `ai_assistant/agent/message.py`, `ai_assistant/application/ports/memory.py`, `ai_assistant/bootstrap/config.py`, `ai_assistant/bootstrap/logging.py`, `ai_assistant/agent/models/adapter.py`, related tests.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_errors.py tests/test_config.py tests/test_model_adapter.py tests/test_memory_stores.py tests/test_logging.py -q`.
- Test results: 28 passed after updating logging-level expectation.
- Assumptions: `application/errors.py` is the current minimal shared location until M15 reorganization.
- Remaining issues: None for this task.
- Recommended follow-up: Map infrastructure failures and CLI output.

### Task M9-T2 — Map Infrastructure Failures and CLI Messages

## Parent milestone

M9

## Status

implemented

## Owner role

Runtime implementer

## Objective

Translate SQLite and model provider failures to typed errors and make CLI handle expected errors without traceback.

## Scope

- Wrap SQLite failures as `ConversationStoreError`.
- Map HTTP 404, URL failures, timeout, invalid JSON and missing text in OpenAI-compatible provider.
- Catch `AssistantError` in CLI and print a readable stderr message.
- Add tests for typed provider errors and CLI translation.

## Explicit exclusions

- No retry policy.
- No user-facing error catalog.
- No Ollama adapter.

## File scope

### Writable

- `ai_assistant/storage/sqlite_memory.py`
- `ai_assistant/agent/models/openai_compatible.py`
- `ai_assistant/cli/app.py`
- `tests/test_errors.py`
- `tests/test_logging.py`
- `tests/test_cli_app.py`

### Read-only

- `ai_assistant/agent/runtime.py`
- `ai_assistant/bootstrap/logging.py`

### Forbidden

- Persistent schema changes

## Dependencies

- M9-T1

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] SQLite errors are mapped.
- [x] HTTP errors are mapped.
- [x] JSON/protocol errors are mapped.
- [x] CLI expected errors avoid traceback.
- [x] Technical error type is logged.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_errors.py tests/test_logging.py tests/test_cli_app.py tests/test_memory_stores.py -q
```

## Risks

- Unexpected exceptions still surface as tracebacks; that remains useful for non-typed bugs.

## Result report

- Summary: Mapped SQLite and OpenAI-compatible failures to typed errors and added CLI translation for expected assistant errors.
- Files changed: `ai_assistant/storage/sqlite_memory.py`, `ai_assistant/agent/models/openai_compatible.py`, `ai_assistant/cli/app.py`, related tests.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; CLI smoke.
- Test results: unit passed with 35 tests and 4 deselected; contract passed with 2 tests and 37 deselected; full suite passed with 39 tests; CLI smoke exited 0.
- Assumptions: Only `AssistantError` subclasses are expected user-readable errors.
- Remaining issues: None for this task.
- Recommended follow-up: Full milestone validation and review.

### Task M9-T3 — Validate Typed Errors

## Parent milestone

M9

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M9 acceptance criteria and prepare human review.

## Scope

- Run unit, contract and full pytest validation.
- Run CLI smoke.
- Write `.agent/reports/M9.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M9 accepted.
- Do not start M10.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M9.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M9-T2

## Applicable ADRs

- ADR-004 SQLite conversation persistence
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] CLI does not show traceback for expected errors.
- [x] Tests validate error types.
- [x] Technical errors remain in logs.
- [x] Unit and contract suites pass.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
```

## Risks

- Over-sanitizing errors can hide provider diagnostics.

## Result report

- Summary: Validated M9 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M9.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_errors.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; `printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py`.
- Test results: error tests passed with 6 tests; unit suite passed with 36 tests and 4 deselected; contract suite passed with 2 tests and 38 deselected; full suite passed with 40 tests; CLI smoke exited 0.
- Assumptions: Unexpected non-`AssistantError` exceptions should still fail loudly.
- Remaining issues: None for M9 after independent review findings were corrected.
- Recommended follow-up: Human review before starting M10.

### Task M10-T1 — Add Native Ollama Chat Provider

## Parent milestone

M10

## Status

implemented

## Owner role

Model provider implementer

## Objective

Implement the native Ollama `/api/chat` provider using stdlib HTTP.

## Scope

- Build native Ollama request payload.
- Send `stream=false`.
- Use `urllib.request`.
- Apply timeout.
- Parse `message.content`.
- Map connection, timeout, model-not-found and protocol errors.
- Log request duration.
- Add simulated unit tests.

## Explicit exclusions

- No streaming.
- No SDK.
- No daemon management.
- No model downloads.

## File scope

### Writable

- `ai_assistant/agent/models/ollama.py`
- `tests/test_ollama_model.py`

### Read-only

- `ai_assistant/agent/models/openai_compatible.py`
- `ai_assistant/application/errors.py`
- `docs/adr/ADR-011-native-ollama-adapter.md`
- `docs/adr/ADR-014-non-streaming-calls-in-phase-1.md`

### Forbidden

- OpenAI-compatible provider behavior

## Dependencies

- M9 accepted

## Applicable ADRs

- ADR-011 Native Ollama API adapter
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] Request uses `/api/chat`.
- [x] Request sends `stream=false`.
- [x] Messages are translated to Ollama format.
- [x] Response returns normalized assistant `Message`.
- [x] Typed errors are raised for unavailable service, missing model and bad protocol.
- [x] Unit tests do not require real Ollama.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py -q
```

## Risks

- Ollama error body formats may vary by version.

## Result report

- Summary: Added native `OllamaModelProvider` with stdlib HTTP, non-streaming requests, typed errors and duration logging.
- Files changed: `ai_assistant/agent/models/ollama.py`, `tests/test_ollama_model.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py -q`.
- Test results: 7 passed.
- Assumptions: HTTP 404 is sufficient for missing-model mapping in M10.
- Remaining issues: Real Ollama validation is optional and environment-dependent.
- Recommended follow-up: Wire provider through configuration and adapter factory.

### Task M10-T2 — Wire Ollama Provider

## Parent milestone

M10

## Status

implemented

## Owner role

Model provider implementer

## Objective

Expose Ollama through configuration and the model adapter factory.

## Scope

- Allow `AI_ASSISTANT_PROVIDER=ollama`.
- Default Ollama base URL to `http://localhost:11434`.
- Register provider in `ModelAdapter`.
- Export provider from model package.
- Add adapter/config tests and simulated CLI path.
- Add optional real Ollama smoke test.

## Explicit exclusions

- No model profiles.
- No default model recommendations.
- No real Ollama requirement in unit tests.

## File scope

### Writable

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/agent/models/adapter.py`
- `ai_assistant/agent/models/__init__.py`
- `tests/test_config.py`
- `tests/test_model_adapter.py`
- `tests/test_ollama_model.py`
- `tests/test_ollama_smoke.py`

### Read-only

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/cli/app.py`

### Forbidden

- Logging policy changes

## Dependencies

- M10-T1

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-011 Native Ollama API adapter
- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] Provider can be selected by config.
- [x] Model remains configurable.
- [x] CLI responds with simulated Ollama.
- [x] Optional real-Ollama test is separable from default suite.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py tests/test_model_adapter.py tests/test_config.py -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q
```

## Risks

- `AI_ASSISTANT_MODEL` is required for useful real Ollama execution.

## Result report

- Summary: Wired Ollama into config and adapter selection, added simulated CLI coverage and optional real smoke test.
- Files changed: `ai_assistant/bootstrap/config.py`, `ai_assistant/agent/models/adapter.py`, `ai_assistant/agent/models/__init__.py`, related tests.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py tests/test_model_adapter.py tests/test_config.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q`.
- Test results: focused tests passed with 19 tests before CLI coverage and 7 Ollama-provider tests after; optional Ollama suite skipped 1 test because no `AI_ASSISTANT_MODEL` was set.
- Assumptions: M11 owns hardware/model profile defaults.
- Remaining issues: Real Ollama was not exercised in this environment.
- Recommended follow-up: Full milestone validation.

### Task M10-T3 — Validate Native Ollama Adapter

## Parent milestone

M10

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M10 acceptance criteria and prepare human review.

## Scope

- Run unit, contract, ollama-marker and full pytest validation.
- Run CLI smoke.
- Write `.agent/reports/M10.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M10 accepted.
- Do not start M11.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M10.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M10-T2

## Applicable ADRs

- ADR-011 Native Ollama API adapter
- ADR-013 Pytest testing strategy
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] CLI responds with Ollama.
- [x] Model is selected by variable/config.
- [x] Service-down failures raise typed error.
- [x] Missing-model failures raise typed error.
- [x] Unit tests do not require Ollama.
- [x] Unit and contract suites pass.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama
PYTHONDONTWRITEBYTECODE=1 python -m pytest
printf 'quit\n' | PYTHONDONTWRITEBYTECODE=1 python main.py
```

## Risks

- Real Ollama validation depends on local daemon and installed model.

## Result report

- Summary: Validated M10 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M10.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_ollama_model.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; CLI smoke.
- Test results: Ollama provider tests passed with 8 tests; unit suite passed with 45 tests and 5 deselected; contract suite passed with 2 tests and 48 deselected; optional Ollama suite skipped 1 test because no `AI_ASSISTANT_MODEL` was set; full suite passed with 50 tests and 1 skipped; CLI smoke exited 0.
- Assumptions: Real Ollama validation remains environment-dependent and optional.
- Remaining issues: Real Ollama smoke was not executed in this environment.
- Recommended follow-up: Human review before starting M11.

### Task M11-T1 — Document Model Profiles

## Parent milestone

M11

## Status

implemented

## Owner role

Documentation agent

## Objective

Document recommended local model profiles for the reference 6 GB VRAM / 64 GB RAM machine.

## Scope

- Document development, validation and evaluation profiles.
- Document context recommendations.
- Add evaluation/smoke guidance.
- Link architecture to the profile guide.

## Explicit exclusions

- No automatic GPU detection.
- No downloads.
- No benchmark framework.

## File scope

### Writable

- `docs/model-profiles.md`
- `docs/architecture.md`

### Read-only

- `docs/roadmap.md`
- `docs/adr/ADR-015-configurable-model-profiles.md`

### Forbidden

- Runtime behavior

## Dependencies

- M10 accepted

## Applicable ADRs

- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Profiles are documented.
- [x] Development model target is documented.
- [x] Context 4096 is documented.
- [x] Evaluation context 8192 guidance is documented.

## Validation commands

```bash
rg -n "development|validation|evaluation|AI_ASSISTANT_CONTEXT_LIMIT|8192" docs/model-profiles.md docs/architecture.md
```

## Risks

- Ollama tags may differ by registry and quantization.

## Result report

- Summary: Added model profile guide and architecture link.
- Files changed: `docs/model-profiles.md`, `docs/architecture.md`.
- Tests run: `rg -n "development|validation|evaluation|AI_ASSISTANT_CONTEXT_LIMIT|8192" docs/model-profiles.md docs/architecture.md`.
- Test results: profile and context entries found.
- Assumptions: Exact Ollama tags remain operator-selected because tags vary.
- Remaining issues: None for this task.
- Recommended follow-up: Validate config/smoke behavior.

### Task M11-T2 — Keep Model and Context Configurable

## Parent milestone

M11

## Status

implemented

## Owner role

Runtime implementer

## Objective

Avoid a hardcoded model default and prove context/model are selected through config.

## Scope

- Remove the hardcoded model default from config and adapter config.
- Verify 8192 context can be configured.
- Add smoke test for configured model/context and active model logging.

## Explicit exclusions

- No context trimming.
- No model profile resolver.
- No automatic provider selection.

## File scope

### Writable

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/agent/models/adapter.py`
- `tests/test_config.py`
- `tests/test_smoke.py`

### Read-only

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/agent/runtime.py`

### Forbidden

- Provider HTTP behavior

## Dependencies

- M11-T1

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Runtime config does not hardcode a concrete model.
- [x] Model is environment/config selected.
- [x] Context 4096 remains default.
- [x] Context 8192 is accepted by configuration.
- [x] Active provider/model is logged.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py tests/test_smoke.py tests/test_model_adapter.py -q
```

## Risks

- Operators using real providers must set `AI_ASSISTANT_MODEL`.

## Result report

- Summary: Removed concrete model default and added config/smoke tests for model/context selection.
- Files changed: `ai_assistant/bootstrap/config.py`, `ai_assistant/agent/models/adapter.py`, `tests/test_config.py`, `tests/test_smoke.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_config.py tests/test_smoke.py tests/test_model_adapter.py -q`.
- Test results: 16 passed.
- Assumptions: Dummy provider remains the no-model local default; real providers require configured model.
- Remaining issues: None for this task.
- Recommended follow-up: Full M11 validation.

### Task M11-T3 — Validate Model Profiles

## Parent milestone

M11

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M11 acceptance criteria and prepare human review.

## Scope

- Run smoke tests.
- Run full pytest validation.
- Write `.agent/reports/M11.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M11 accepted.
- Do not start M12.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M11.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M11-T2

## Applicable ADRs

- ADR-013 Pytest testing strategy
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Project does not fix a concrete model in runtime config.
- [x] Documented default profile is suitable for reference hardware.
- [x] Context is configurable.
- [x] Smoke suite passes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m smoke
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Exact Ollama tags may differ locally.

## Result report

- Summary: Validated M11 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M11.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m smoke -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; profile documentation `rg`; hardcoded model default `rg`.
- Test results: smoke passed with 1 test and 52 deselected; full suite passed with 53 tests; profile documentation entries found; no `gpt-5` runtime config default found.
- Assumptions: Exact Ollama model tags are operator-selected and may differ locally.
- Remaining issues: Real Ollama smoke remains optional and environment-dependent.
- Recommended follow-up: Human review before starting M12.

### Task M12-T1 — Add Recent-History Context Budget

## Parent milestone

M12

## Status

implemented

## Owner role

Runtime implementer

## Objective

Limit history sent to the model with a simple configurable budget.

## Scope

- Add `context_limit` to `ContextBuilder`.
- Preserve system prompt.
- Preserve current user input.
- Select recent history in original order while budget remains.
- Add order and truncation tests.

## Explicit exclusions

- No tokenizer.
- No summaries.
- No embeddings.

## File scope

### Writable

- `ai_assistant/agent/context.py`
- `tests/test_agent_runtime.py`

### Read-only

- `docs/roadmap.md`
- `docs/architecture.md`

### Forbidden

- Persistence behavior

## Dependencies

- M11 accepted

## Applicable ADRs

- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Context does not grow without limit.
- [x] System prompt is always preserved.
- [x] Current input is always preserved.
- [x] Recent history has priority.
- [x] Message order is preserved.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py -q
```

## Risks

- Character count is only an approximation of token usage.

## Result report

- Summary: Added approximate character-budget context selection.
- Files changed: `ai_assistant/agent/context.py`, `tests/test_agent_runtime.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py tests/test_cli_app.py -q`.
- Test results: 8 passed.
- Assumptions: Approximate content-length budget is acceptable until provider tokenizers exist.
- Remaining issues: None for this task.
- Recommended follow-up: Wire config limit through bootstrap.

### Task M12-T2 — Wire Configured Context Limit

## Parent milestone

M12

## Status

implemented

## Owner role

Runtime implementer

## Objective

Pass `AppConfig.context_limit` into `ContextBuilder`.

## Scope

- Wire configured context limit in bootstrap.
- Add bootstrap wiring test.

## Explicit exclusions

- No CLI flags.
- No runtime mutation.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `tests/test_cli_app.py`
- `tests/test_config.py`

### Read-only

- `ai_assistant/bootstrap/config.py`
- `ai_assistant/agent/runtime.py`

### Forbidden

- Model provider behavior

## Dependencies

- M12-T1

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Configured context limit reaches `ContextBuilder`.
- [x] Existing config validation remains intact.
- [x] CLI bootstrap still works.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_cli_app.py tests/test_config.py -q
```

## Risks

- Test reaches through `CliApplication._runtime` because there is no public diagnostic surface yet.

## Result report

- Summary: Wired `AppConfig.context_limit` into `ContextBuilder`.
- Files changed: `ai_assistant/bootstrap/container.py`, `tests/test_cli_app.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py tests/test_cli_app.py -q`.
- Test results: 8 passed.
- Assumptions: Private runtime inspection in test is acceptable for narrow bootstrap wiring.
- Remaining issues: None for this task.
- Recommended follow-up: Full M12 validation.

### Task M12-T3 — Validate Context Budget

## Parent milestone

M12

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M12 acceptance criteria and prepare human review.

## Scope

- Run unit and full pytest validation.
- Write `.agent/reports/M12.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M12 accepted.
- Do not start M13.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M12.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M12-T2

## Applicable ADRs

- ADR-007 Configuration at bootstrap
- ADR-015 Configurable model profiles

## Acceptance criteria

- [x] Context does not grow without limit.
- [x] Current message is always preserved.
- [x] Recent history has priority.
- [x] Unit suite passes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Character count can differ from provider token counts.

## Result report

- Summary: Validated M12 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M12.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; CLI smoke with `python main.py`.
- Test results: unit suite passed with 50 tests and 6 deselected; full suite passed with 56 tests; CLI smoke exited 0 and showed configured provider/model in stderr logs.
- Assumptions: Character-count budget is the intended simple policy for M12.
- Remaining issues: Token-accurate budgeting remains out of scope.
- Recommended follow-up: Human review before starting M13.

### Task M13-T1 — Harden OpenAI-Compatible Mappers

## Parent milestone

M13

## Status

implemented

## Owner role

Model provider implementer

## Objective

Strengthen request and response contracts for the OpenAI-compatible provider.

## Scope

- Verify Responses API payload mapping.
- Verify `/responses` request path and timeout.
- Validate response JSON is an object.
- Verify direct and nested response text extraction.
- Preserve typed protocol errors.

## Explicit exclusions

- No SDK.
- No streaming.
- No tools.
- No multimodal support.

## File scope

### Writable

- `ai_assistant/agent/models/openai_compatible.py`
- `tests/test_openai_compatible.py`

### Read-only

- `ai_assistant/agent/models/ollama.py`
- `docs/roadmap.md`
- `docs/adr/ADR-014-non-streaming-calls-in-phase-1.md`

### Forbidden

- Ollama provider behavior

## Dependencies

- M12 accepted

## Applicable ADRs

- ADR-006 ModelProvider port
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] Request mapper is tested.
- [x] Response mapper is tested.
- [x] Timeout is passed to HTTP call.
- [x] Invalid provider JSON maps to typed protocol error.
- [x] Unit/contract tests use no real network.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_openai_compatible.py -q
```

## Risks

- Compatible providers may vary in exact response shapes.

## Result report

- Summary: Added simulated contract coverage and object JSON validation for OpenAI-compatible responses.
- Files changed: `ai_assistant/agent/models/openai_compatible.py`, `tests/test_openai_compatible.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_openai_compatible.py -q`.
- Test results: 8 passed.
- Assumptions: Responses API shape remains the Phase 1 OpenAI-compatible contract.
- Remaining issues: No real provider integration test in M13.
- Recommended follow-up: Verify factory and full contracts.

### Task M13-T2 — Verify Factory and Port Contract

## Parent milestone

M13

## Status

implemented

## Owner role

Model provider implementer

## Objective

Confirm OpenAI-compatible provider remains separate from Ollama and implements the shared port.

## Scope

- Verify `OpenAICompatibleModel` implements `ModelProvider`.
- Verify `openai` factory path.
- Verify `chatgpt` alias path.
- Preserve Ollama factory separation.

## Explicit exclusions

- No provider auto-detection.
- No provider renaming.

## File scope

### Writable

- `ai_assistant/agent/models/adapter.py`
- `tests/test_model_adapter.py`
- `tests/test_openai_compatible.py`

### Read-only

- `ai_assistant/agent/models/ollama.py`
- `ai_assistant/bootstrap/config.py`

### Forbidden

- Configuration variable changes

## Dependencies

- M13-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-006 ModelProvider port
- ADR-011 Native Ollama API adapter

## Acceptance criteria

- [x] Ollama and OpenAI-compatible are separate adapters.
- [x] Both implement the same port.
- [x] Factory selects OpenAI-compatible provider.
- [x] Factory tests use no real network.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_model_adapter.py tests/test_openai_compatible.py -q
```

## Risks

- Test reaches into adapter internals to verify concrete provider selection.

## Result report

- Summary: Added factory coverage for `chatgpt` alias and port contract coverage for OpenAI-compatible provider.
- Files changed: `tests/test_model_adapter.py`, `tests/test_openai_compatible.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_model_adapter.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`.
- Test results: model adapter tests passed with 7 tests; contract suite passed with 10 tests and 54 deselected.
- Assumptions: Internal provider inspection is acceptable for narrow factory verification.
- Remaining issues: None for this task.
- Recommended follow-up: Full M13 validation.

### Task M13-T3 — Validate OpenAI-Compatible Adapter

## Parent milestone

M13

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M13 acceptance criteria and prepare human review.

## Scope

- Run contract and full pytest validation.
- Write `.agent/reports/M13.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M13 accepted.
- Do not start M14.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M13.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M13-T2

## Applicable ADRs

- ADR-006 ModelProvider port
- ADR-011 Native Ollama API adapter
- ADR-012 Minimal external dependencies
- ADR-014 Non-streaming model calls in Phase 1

## Acceptance criteria

- [x] Ollama and OpenAI-compatible are separate adapters.
- [x] Both implement the same port.
- [x] Unit/contract tests do not use real network.
- [x] Contract suite passes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract
PYTHONDONTWRITEBYTECODE=1 python -m pytest
```

## Risks

- Future compatible providers may need different response mapping.

## Result report

- Summary: Validated M13 acceptance criteria and produced the human review report.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M13.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_openai_compatible.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_model_adapter.py -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`.
- Test results: OpenAI-compatible tests passed with 8 tests; model adapter tests passed with 7 tests; contract suite passed with 10 tests and 55 deselected; full suite passed with 65 tests.
- Assumptions: Responses API shape remains the OpenAI-compatible Phase 1 contract.
- Remaining issues: No real OpenAI-compatible provider integration test in M13.
- Recommended follow-up: Human review before starting M14.

### Task M14-T1 — Define Declarative Tool Models

## Parent milestone

M14

## Status

implemented

## Owner role

Runtime implementer

## Objective

Add typed declarative tool definitions, calls and interpretation results.

## Scope

- Define `ToolDefinition`.
- Define `ToolCall`.
- Define typed `ToolCallPlan`.
- Add `ToolCallInterpreter`.
- Validate explicit `tool_call` JSON.
- Add tests.

## Explicit exclusions

- No executor.
- No shell.
- No socket calls.
- No multiple-tool planner.

## File scope

### Writable

- `ai_assistant/agent/planner.py`
- `ai_assistant/application/errors.py`
- `tests/test_tools.py`

### Read-only

- `docs/roadmap.md`
- `docs/adr/ADR-008-declarative-tools-only-in-phase-1.md`

### Forbidden

- Tool execution adapters

## Dependencies

- M13 accepted

## Applicable ADRs

- ADR-008 Declarative tools only in Phase 1

## Acceptance criteria

- [x] `ToolDefinition` exists.
- [x] `ToolCall` exists.
- [x] Interpreter returns typed plan.
- [x] Invalid explicit tool call raises typed error.
- [x] Plain text is ignored.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_tools.py -q
```

## Risks

- JSON format can become provider-coupled if expanded too early.

## Result report

- Summary: Added declarative tool-call dataclasses and JSON interpreter.
- Files changed: `ai_assistant/agent/planner.py`, `ai_assistant/application/errors.py`, `tests/test_tools.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_tools.py tests/test_agent_runtime.py -q`.
- Test results: 12 passed.
- Assumptions: Phase 1 supports one explicit `tool_call` object per assistant message.
- Remaining issues: No catalog or schema validation beyond basic object shape.
- Recommended follow-up: Preserve interpreted plan in runtime.

### Task M14-T2 — Preserve Tool Plan in Runtime

## Parent milestone

M14

## Status

implemented

## Owner role

Runtime implementer

## Objective

Let runtime identify and retain a typed tool-call plan without executing tools.

## Scope

- Store last interpreted tool plan on runtime.
- Keep response behavior unchanged.
- Add runtime test.

## Explicit exclusions

- No execution.
- No CLI rendering changes.
- No tool result persistence.

## File scope

### Writable

- `ai_assistant/agent/runtime.py`
- `tests/test_agent_runtime.py`
- `tests/test_tools.py`

### Read-only

- `ai_assistant/agent/planner.py`
- `ai_assistant/cli/app.py`

### Forbidden

- Shell/socket execution

## Dependencies

- M14-T1

## Applicable ADRs

- ADR-008 Declarative tools only in Phase 1

## Acceptance criteria

- [x] Runtime can identify a tool call.
- [x] Runtime keeps typed plan.
- [x] No tool is executed.
- [x] Existing response behavior remains unchanged.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_agent_runtime.py tests/test_tools.py -q
```

## Risks

- Public runtime response still returns `Message`; plan is stored on runtime state.

## Result report

- Summary: Runtime now stores `last_tool_plan` after assistant response detection.
- Files changed: `ai_assistant/agent/runtime.py`, `tests/test_agent_runtime.py`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_tools.py tests/test_agent_runtime.py -q`.
- Test results: 12 passed.
- Assumptions: `last_tool_plan` is enough for Phase 1's typed plan requirement.
- Remaining issues: No first-class turn response object yet.
- Recommended follow-up: Full validation.

### Task M14-T3 — Validate Declarative Tools

## Parent milestone

M14

## Status

implemented

## Owner role

Integration validator

## Objective

Verify M14 acceptance criteria and prepare human review.

## Scope

- Run unit and full pytest validation.
- Verify no executor/shell was introduced.
- Write `.agent/reports/M14.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M14 accepted.
- Do not start M15.

## File scope

### Writable

- `.agent/roadmap-state.md`
- `.agent/task-queue.md`
- `.agent/human-review.md`
- `.agent/reports/M14.md`

### Read-only

- all project source files
- tests
- docs

### Forbidden

- `.agent/decisions.md`

## Dependencies

- M14-T2

## Applicable ADRs

- ADR-008 Declarative tools only in Phase 1
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Runtime can identify a tool call.
- [x] No tool is executed.
- [x] Response path contains typed plan.
- [x] Unit suite passes.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit
PYTHONDONTWRITEBYTECODE=1 python -m pytest
rg -n "ToolExecutor|execute\\(|subprocess|os\\.system|shell" ai_assistant/agent ai_assistant/tools tests/test_tools.py tests/test_agent_runtime.py
```

## Risks

- `last_tool_plan` is stateful and may be replaced by a richer turn response later.

## Result report

- Summary: Validated declarative tool interpretation without execution.
- Files changed: `.agent/roadmap-state.md`, `.agent/task-queue.md`, `.agent/human-review.md`, `.agent/reports/M14.md`.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q`; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`; executor/shell `rg`.
- Test results: unit suite passed with 58 tests and 14 deselected; full suite passed with 72 tests; executor/shell search found no matches in M14 scope.
- Assumptions: Single explicit JSON `tool_call` object is sufficient for Phase 1.
- Remaining issues: No tool catalog or executor by design.
- Recommended follow-up: Human review before starting M15.

### Task M15-T1 — Establish Layered Modules

## Parent milestone

M15

## Status

implemented

## Owner role

Architect

## Objective

Create canonical layer packages for domain, application, infrastructure and interfaces.

## Scope

- Move message, session, error and tool data types to `ai_assistant/domain/`.
- Move runtime, context builder and tool-call interpretation to `ai_assistant/application/`.
- Move providers and stores to `ai_assistant/infrastructure/`.
- Move CLI adapter to `ai_assistant/interfaces/cli/`.
- Keep legacy packages as compatibility exports.

## Explicit exclusions

- No public protocol changes.
- No database schema migration.
- No new dependencies.
- No tool execution.

## File scope

### Writable

- `ai_assistant/domain/`
- `ai_assistant/application/`
- `ai_assistant/infrastructure/`
- `ai_assistant/interfaces/`
- `ai_assistant/agent/`
- `ai_assistant/cli/`
- `ai_assistant/storage/`

### Forbidden

- Persistent user data.

## Dependencies

- M14 accepted.

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-003 Provider-neutral Message model
- ADR-006 ModelProvider port
- ADR-008 Declarative tools only in Phase 1
- ADR-012 Minimal external dependencies

## Acceptance criteria

- [x] Domain no importa infraestructura.
- [x] Application no importa adaptadores.
- [x] Legacy imports remain compatible.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_layering.py -q
```

## Result report

- Summary: Added canonical layered modules and compatibility exports.
- Tests run: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_layering.py -q`.
- Test results: 3 passed.
- Remaining issues: Legacy packages can be removed in a later dedicated cleanup.

### Task M15-T2 — Wire Bootstrap To Layers

## Parent milestone

M15

## Status

implemented

## Owner role

Runtime implementer

## Objective

Use canonical layer modules from bootstrap and entry points without changing runtime behavior.

## Scope

- Update `ai_assistant/bootstrap/container.py` imports.
- Update `ai_assistant/main.py` to use the composition root directly.
- Update tests that monkeypatch provider internals to target canonical infrastructure modules.

## Explicit exclusions

- No CLI feature changes.
- No logging policy changes.
- No provider behavior changes.

## File scope

### Writable

- `ai_assistant/bootstrap/container.py`
- `ai_assistant/main.py`
- provider tests

## Dependencies

- M15-T1

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-007 Configuration at bootstrap
- ADR-011 Native Ollama adapter

## Acceptance criteria

- [x] CLI no construye dependencias.
- [x] `python main.py` funciona.

## Validation commands

```bash
printf 'hello\nquit\n' | AI_ASSISTANT_PROVIDER=dummy AI_ASSISTANT_MODEL= PYTHONDONTWRITEBYTECODE=1 python main.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q
```

## Result report

- Summary: Bootstrap now assembles canonical application, infrastructure and interface modules.
- Test results: CLI smoke exited 0 and printed `Echo: hello`; unit suite passed with 61 tests and 14 deselected.

### Task M15-T3 — Validate Layered Reorganization

## Parent milestone

M15

## Status

implemented

## Owner role

Integration validator

## Objective

Validate all M15 acceptance criteria and prepare manual review artifacts.

## Scope

- Add layer dependency tests.
- Run full pytest suite.
- Update architecture documentation.
- Produce `.agent/reports/M15.md`.
- Update roadmap state and human review queue.

## Explicit exclusions

- Do not mark M15 accepted.
- Do not start M16.

## Dependencies

- M15-T2

## Applicable ADRs

- ADR-001 Ports and Adapters
- ADR-012 Minimal external dependencies
- ADR-013 Pytest testing strategy

## Acceptance criteria

- [x] Domain no importa infraestructura.
- [x] Application no importa adaptadores.
- [x] CLI no construye dependencias.
- [x] `python main.py` funciona.
- [x] Full pytest suite passes.

## Validation commands

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_layering.py -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
printf 'hello\nquit\n' | AI_ASSISTANT_PROVIDER=dummy AI_ASSISTANT_MODEL= PYTHONDONTWRITEBYTECODE=1 python main.py
```

## Result report

- Summary: Validated M15 and prepared human review.
- Test results: layering passed with 3 tests; unit passed with 61 tests and 14 deselected; full suite passed with 75 tests; CLI smoke exited 0.

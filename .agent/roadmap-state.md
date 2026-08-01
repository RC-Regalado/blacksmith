# Roadmap State

## Project

AI Assistant

## Active phase

Phase 2: Read-Only Workspace Tools

## Current milestone

- ID: M2.16
- Name: Documentation and final manual review
- Status: accepted
- Source: `docs/roadmap-phase-2.md`

## Milestone status vocabulary

- `planned`
- `in-progress`
- `blocked`
- `implemented-awaiting-human-review`
- `accepted`
- `rework-required`

## Milestones

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M1 | Repository hygiene | accepted | — | `.agent/reports/M1.md` | approved |
| M2 | Migration to pytest | accepted | — | `.agent/reports/M2.md` | approved |
| M3 | Explicit sessions | accepted | — | `.agent/reports/M3.md` | approved |
| M4 | Transactional persistence | accepted | — | `.agent/reports/M4.md` | approved |
| M5 | Explicit ports | accepted | — | `.agent/reports/M5.md` | approved |
| M6 | Composition root | accepted | — | `.agent/reports/M6.md` | approved |
| M7 | Centralized configuration | accepted | — | `.agent/reports/M7.md` | approved |
| M8 | Basic logging | accepted | — | `.agent/reports/M8.md` | approved |
| M9 | Typed internal errors | accepted | — | `.agent/reports/M9.md` | approved |
| M10 | Native Ollama adapter | accepted | — | `.agent/reports/M10.md` | approved |
| M11 | Model profiles | accepted | — | `.agent/reports/M11.md` | approved |
| M12 | Context budget | accepted | — | `.agent/reports/M12.md` | approved |
| M13 | Robust OpenAI-compatible adapter | accepted | — | `.agent/reports/M13.md` | approved |
| M14 | Declarative tools | accepted | — | `.agent/reports/M14.md` | approved |
| M15 | Layered repository reorganization | accepted | — | `.agent/reports/M15.md` | approved |
| M16 | CI | accepted | — | `.agent/reports/M16.md` | approved |
| M17 | Documentation and ADR closure | accepted | — | `.agent/reports/M17.md` | approved |

## Phase 2 Milestones

| ID | Milestone | Status | Blocking reason | Automated report | Human review |
|---|---|---|---|---|---|
| M2.1 | Approve Phase 2 security decisions | accepted | — | `.agent/reports/M2.1.md` | approved |
| M2.2 | Add tool execution domain models | accepted | — | `.agent/reports/M2.2.md` | approved |
| M2.3 | Add application ports | accepted | — | `.agent/reports/M2.3.md` | approved |
| M2.4 | Implement the static tool catalog | accepted | — | `.agent/reports/M2.4.md` | approved |
| M2.5 | Implement workspace and path policy | accepted | — | `.agent/reports/M2.5.md` | approved |
| M2.6 | Implement deny-by-default tool policy | accepted | — | `.agent/reports/M2.6.md` | approved |
| M2.7 | Add fake and dry-run executors | accepted | — | `.agent/reports/M2.7.md` | approved |
| M2.8 | Implement audit persistence | accepted | — | `.agent/reports/M2.8.md` | approved |
| M2.9 | Implement LocalReadOnlyToolExecutor | accepted | — | `.agent/reports/M2.9.md` | approved |
| M2.10 | Implement ToolExecutionCoordinator | accepted | — | `.agent/reports/M2.10.md` | approved |
| M2.11 | Integrate one bounded tool round into runtime | accepted | — | `.agent/reports/M2.11.md` | approved |
| M2.12 | Add configuration and CLI support | accepted | — | `.agent/reports/M2.12.md` | approved |
| M2.13 | Extend protobuf and C tool service | accepted | — | `.agent/reports/M2.13.md` | approved |
| M2.14 | Implement UnixSocketToolExecutor | accepted | — | `.agent/reports/M2.14.md` | approved |
| M2.15 | Add adversarial security tests | accepted | — | `.agent/reports/M2.15.md` | approved |
| M2.16 | Documentation and final manual review | accepted | — | `.agent/reports/M2.16.md` | approved |

## Current baseline

Record after first inspection:

- Git status: existing user/workspace changes present: `AGENTS.md` modified; `.agent/`, ADR docs, templates and supervisor kit files untracked. Generated artifacts are ignored by `.gitignore`.
- Python version: Python 3.14.6
- Test command: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests`
- Tests passed: 10 of 12 before Milestone 1 implementation; 12 of 12 after permissions were adjusted and M1 was implemented.
- Existing failures: baseline had 2 Unix socket failures from sandbox `server.bind(...)` denial; final validation passed after permissions were adjusted.
- CLI smoke: `PYTHONDONTWRITEBYTECODE=1 python -c "from ai_assistant.cli.app import build_runtime; r=build_runtime(); print(r.respond('hello').content)"` exited 0 but printed debug line `dummy` before `Echo: hello`.
- Ollama availability: not checked; out of scope for Milestone 1.
- Notes: `.gitignore` already contains local environment, Python cache, SQLite, C build and local Codex/session ignore rules. `git ls-files` shows no tracked `__pycache__`, `*.pyc`, `assistant.sqlite3` or `c_toolserver/build/*` artifacts.

## Last supervisor update

- Date: 2026-08-01
- Summary: Phase 2 approved after manual validation with `gemma4:latest`; post-review fixes added for Ollama tool-call formats and deterministic direct tool JSON.
- Next action: Commit Phase 2 closure.

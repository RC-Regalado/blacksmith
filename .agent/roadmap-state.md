# Roadmap State

## Project

AI Assistant

## Active phase

Phase 1: Python Core

## Current milestone

- ID: M6
- Name: Composition root
- Status: implemented-awaiting-human-review
- Source: `docs/roadmap.md`

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
| M6 | Composition root | implemented-awaiting-human-review | — | `.agent/reports/M6.md` | awaiting-review |
| M7 | Centralized configuration | planned | M6 | — | — |
| M8 | Basic logging | planned | M7 | — | — |
| M9 | Typed internal errors | planned | M8 | — | — |
| M10 | Native Ollama adapter | planned | M9 | — | — |
| M11 | Model profiles | planned | M10 | — | — |
| M12 | Context budget | planned | M11 | — | — |
| M13 | Robust OpenAI-compatible adapter | planned | M12 | — | — |
| M14 | Declarative tools | planned | M13 | — | — |
| M15 | Layered repository reorganization | planned | M14 | — | — |
| M16 | CI | planned | M15 | — | — |
| M17 | Documentation and ADR closure | planned | M16 | — | — |

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

- Date: 2026-07-29
- Summary: Milestone 6 implemented and validated. Runtime construction now lives in the bootstrap composition root, and the CLI can be constructed with fakes.
- Next action: Await human review before starting Milestone 7.

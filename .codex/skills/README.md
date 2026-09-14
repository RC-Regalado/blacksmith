# Codex Skills — Agent Execution Platform

This bundle contains three composable skills:

1. `project-architecture`
2. `adr-workflow`
3. `milestone-execution`

Each skill is a folder containing `SKILL.md` and optional supporting resources.

Recommended composition:

`project-architecture -> adr-workflow -> milestone-execution`

Use:
- architecture/refactor/integration -> project-architecture
- architectural decision/conflict -> adr-workflow
- roadmap milestone implementation -> milestone-execution

Keep phase-specific truth in AGENTS.md, architecture, roadmap, and ADR files instead of duplicating it into the skills.

Suggested future skills:
- architecture-review
- testing-strategy
- security-review
- knowledge-engine
- release-validation

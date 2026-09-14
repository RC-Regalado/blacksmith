# knowledge-assisted-development

Codex skill for using the Agent Execution Platform's own Context & Knowledge Engine during repository development.

## Goal

Reduce repository wandering while preserving correctness:

```text
Knowledge Engine
→ orientation

Live repository/tools
→ authoritative verification
```

## Suggested location

Place the directory where your Codex installation discovers project or user skills.

Expected structure:

```text
knowledge-assisted-development/
├── SKILL.md
└── resources/
    ├── checklist.md
    └── subagent-context-template.md
```

## Recommended composition

Use with:

- `project-architecture`
- `adr-workflow`
- `milestone-execution`

Typical sequence:

```text
knowledge-assisted-development
→ project-architecture
→ adr-workflow if needed
→ milestone-execution
```

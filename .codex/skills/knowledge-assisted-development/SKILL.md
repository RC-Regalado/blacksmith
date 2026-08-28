---
name: knowledge-assisted-development
description: Use the project's Context & Knowledge Engine to reduce repository wandering, retrieve relevant architecture/code/history context, verify provenance and freshness, then confirm volatile state with live repository tools before implementing changes.
---

# Knowledge-Assisted Development

## Purpose

Use this skill when working inside the Agent Execution Platform repository and the task would normally require broad repository exploration.

The goal is to reduce unnecessary `ls`, `cat`, `read_file`, and search calls by consulting the project's own Knowledge Engine first.

This skill does not make KnowledgeStore authoritative.

Canonical source code, ADRs, runtime state, Git state, test results, and build results must still be verified through live sources when correctness depends on current state.

## Core rule

```text
Knowledge Engine
→ orientation and stable context

Live tools
→ current/volatile truth
```

Never invert this rule.

## When to use this skill

Use for tasks involving:

- architecture changes;
- ADR-related implementation;
- locating relevant modules;
- understanding subsystems;
- finding historical decisions;
- identifying likely tests;
- preparing milestone/subagent context;
- reducing broad repository inspection.

Especially use before:

- large `search_text` sweeps;
- reading many files;
- asking multiple exploratory tool calls;
- assigning a subagent to a repository area.

## When not to rely on Knowledge Engine alone

Do not treat indexed knowledge as authoritative for:

- current Git status;
- current Git diff;
- current test results;
- current build results;
- current filesystem contents after recent edits;
- uncommitted changes;
- secrets or sensitive files excluded from indexing;
- stale or unverifiable indexed sources.

For these, use live capabilities.

## Required project interfaces

Prefer the project's CLI knowledge interface.

Expected commands may include:

```bash
python main.py knowledge status
python main.py knowledge query "<query>"
```

If the project exposes a richer compiled-context command such as:

```bash
python main.py knowledge context "<objective>"
```

prefer that for architecture/milestone work.

Do not invent unsupported commands. Inspect `python main.py knowledge --help` if uncertain.

## Workflow

### 1. Check knowledge availability

Before broad exploration, inspect knowledge status:

```bash
python main.py knowledge status
```

Classify result:

```text
fresh
partially-stale
stale
empty
error
```

If the index is:

- `fresh`: use it normally;
- `partially-stale`: use only fresh results and verify touched sources live;
- `stale`: do not rely on it for implementation decisions;
- `empty`: fall back to live repository inspection;
- `error`: report and fall back safely.

Do not rebuild automatically unless the user/project workflow explicitly authorizes it.

### 2. Query by task intent

Query the task semantically and structurally.

Examples:

```bash
python main.py knowledge query "bounded multi-round tool loop"
python main.py knowledge query "ModelProvider Ollama finish_reason"
python main.py knowledge query "ADR-069"
python main.py knowledge query "ToolExecutionCoordinator"
```

Prefer 2–4 targeted queries over one broad query.

Useful query dimensions:

- architectural concept;
- exact symbol;
- ADR number/title;
- failure/finding ID;
- milestone objective.

### 3. Inspect provenance

For every retrieved result used to guide implementation, identify:

- source file;
- chunk/source ID;
- source version/hash when available;
- freshness;
- retrieval method if available.

Do not act on unattributed or stale derived context.

### 4. Build a working context map

Create a concise internal map:

```text
Task
├── relevant ADRs
├── relevant modules
├── relevant tests
├── relevant prior execution/audit evidence
└── constraints
```

Example:

```text
Implement duplicate tool-call guard

ADRs:
- ADR-069

Modules:
- application/runtime.py
- application/tool_loop.py
- application/tool_coordinator.py

Tests:
- test_agent_runtime.py
- test_tool_diagnostics.py

Audit:
- FINDING-004
- FINDING-005

Constraints:
- deterministic
- no LLM progress judge
- preserve ToolPolicy/PathPolicy
```

### 5. Verify authoritative sources live

Before editing, read the actual authoritative files returned by Knowledge Engine.

Verify:

- the code still matches indexed context;
- ADR status is current;
- tests still exist and reflect current behavior;
- no uncommitted changes alter assumptions.

Use live Git/filesystem tools for this step.

### 6. Verify volatile state separately

If the task depends on live state, explicitly check it.

Examples:

```text
current Git changes
→ git_status / git_diff

current test behavior
→ run_tests

current build behavior
→ build_project

current file contents
→ read_file
```

Do not substitute KnowledgeStore evidence for these.

### 7. Implement with narrow scope

Use the Knowledge Engine only to reduce exploration.

Implementation must still follow:

- `AGENTS.md`;
- accepted ADRs;
- project architecture skill;
- milestone execution skill;
- security/tool policies.

### 8. Re-query after major changes only when useful

After implementation, re-querying KnowledgeStore may be invalid if the index has not been refreshed.

Do not assume it reflects the new code.

Prefer live validation after edits.

### 9. Report knowledge assistance explicitly

In the result report include:

- knowledge queries used;
- sources selected;
- whether sources were fresh;
- live files verified;
- any stale/empty fallback;
- live-state checks performed;
- whether Knowledge Engine reduced exploratory calls.

## Subagent workflow

Before delegating a repository task:

1. query Knowledge Engine for the task;
2. select only relevant ADRs/modules/tests;
3. provide the subagent with a bounded context package;
4. require the subagent to verify those sources live before editing.

Suggested subagent context:

```text
Objective:
<task>

Relevant ADRs:
<list>

Relevant files:
<list>

Relevant tests:
<list>

Audit/findings:
<list>

Constraints:
<list>

Verification requirement:
Read the live authoritative files before editing.
```

Do not dump large raw chunks into subagent prompts when paths and constraints are sufficient.

## Failure handling

If retrieval returns nothing:

- try one more targeted query;
- then fall back to live search.

If KnowledgeStore is stale:

- do not automatically rebuild;
- verify live sources;
- report stale status.

If retrieved knowledge contradicts live code:

- live code + current accepted ADRs win;
- report the inconsistency;
- consider whether the index or documentation needs refresh.

## Efficiency goal

The skill should reduce patterns like:

```text
list_directory
→ search_text
→ read_file
→ read_file
→ read_file
```

into:

```text
knowledge query
→ verify 1–2 authoritative files
→ implement
```

Do not optimize tool count at the expense of correctness.

## Security

Never use the Knowledge Engine to bypass:

- sensitive path restrictions;
- ToolPolicy;
- PathPolicy;
- confirmation;
- audit;
- workspace confinement.

Do not request secrets or blocked files through alternative indexed representations.

## Final checklist

- [ ] Knowledge status checked.
- [ ] Targeted queries used.
- [ ] Provenance/freshness inspected.
- [ ] Relevant ADRs identified.
- [ ] Live authoritative sources verified.
- [ ] Volatile state checked live where needed.
- [ ] No stale knowledge treated as truth.
- [ ] No automatic rebuild performed without authorization.
- [ ] Implementation remained within project architecture/policy.
- [ ] Report states how Knowledge Engine was used.

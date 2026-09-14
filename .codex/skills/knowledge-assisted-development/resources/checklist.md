# Knowledge-Assisted Development Checklist

## Before implementation

- [ ] Run `python main.py knowledge status`.
- [ ] Confirm fresh/partially-stale/stale/empty/error.
- [ ] Query the task by concept.
- [ ] Query exact symbols/ADR IDs where useful.
- [ ] Record relevant source paths.
- [ ] Inspect provenance/freshness.
- [ ] Verify current ADR statuses.
- [ ] Verify source files live.
- [ ] Inspect `git status` for uncommitted changes.

## During implementation

- [ ] Treat KnowledgeStore as advisory derived state.
- [ ] Use live tools for volatile state.
- [ ] Keep task scope narrow.
- [ ] Preserve ToolPolicy/PathPolicy/security boundaries.
- [ ] Do not rebuild the index automatically.

## After implementation

- [ ] Validate code/tests live.
- [ ] Do not assume old KnowledgeStore entries represent new code.
- [ ] Report queries, sources, freshness, and live verification.

# Phase 5.2 — Runtime Hardening & Audit Remediation — Final Closure Report

## Status

`implemented-awaiting-final-human-review`

## Baseline

`docs/audits/chat-tool-context-audit.md` — verdict at start: **REMEDIATION REQUIRED** (8 PASS / 18 PARTIAL / 8 FAIL / 4 NOT VERIFIED across 18 findings; 3 BLOCKER findings: FINDING-001/002/003).

## Mandatory findings — final status

Per the governing instruction, FINDING-001 through 005, 008 and 009 were required to reach PASS before this phase could close. The independent post-remediation audit (`docs/audits/chat-tool-context-audit-post-remediation.md`), run by a fresh agent with no access to this session's context and instructed not to trust milestone self-reports, confirms all of them PASS with live-reproduced evidence (not just static code reading):

| Finding | Severity | Baseline | Final | Milestone | Evidence |
|---|---|---|---|---|---|
| FINDING-001 — one-round tool limit blocks discovery-read flows | BLOCKER | FAIL | **PASS** | M5.2.8-12 | Bounded multi-round loop (`ToolLoopBudget`); live-reproduced `list_directory → read_file → final answer` in one turn. |
| FINDING-002 — Ollama termination metadata/tokens discarded | BLOCKER | FAIL | **PASS** | M5.2.3/4/5 | `ModelResponse.finish_reason/prompt_tokens/output_tokens/truncated` populated from real Ollama `done`/`done_reason`/`prompt_eval_count`/`eval_count`. |
| FINDING-003 — no useful synthesis on exhaustion | BLOCKER | FAIL | **PASS** | M5.2.12 | `_finish_with_synthesis()`: one extra evidence-aware model call; deterministic sanitized fallback only if the model still demands a tool. |
| FINDING-004 — no duplicate-call guard | HIGH | FAIL | **PASS** | M5.2.9 | `DuplicateCallGuard`; live-verified zero executor spend on an exact repeat. |
| FINDING-005 — no no-progress guard | HIGH | FAIL | **PASS** | M5.2.10 | `ProgressGuard`; live-verified stop after 2 consecutive failures, changed-strategy-after-failure still allowed. |
| FINDING-008 — context/Ollama limits uncoordinated | HIGH | FAIL | **PASS** | M5.2.13 | `provider_context_window`/`reserved_output_length`/`max_input_length`/`model_num_ctx`/`model_num_predict` surfaced together in one per-turn diagnostic record; live-verified. |
| FINDING-009 — no interaction-level correlation | HIGH | PARTIAL | **PASS** | M5.2.13 | One `interaction_id` per turn correlates context/model/tool/synthesis/completion in one JSONL stream, and now also in the SQLite audit DB; live-verified. |

FINDING-007 (context budget semantics inconsistent, HIGH, PARTIAL at baseline) was not on the strictly-mandatory list but is also independently confirmed **PASS** (M5.2.6: one shared `estimate_tokens` unit, explicit reserved-output accounting).

## Non-mandatory findings

FINDING-006, 010–014, 016–018 remain PARTIAL/NOT VERIFIED as at baseline (010/011 measurably improved as a side effect of the observability work). FINDING-015 (docs/Modelfile/README disagreement on Ollama context profile) remains FAIL — explicitly deferred, not a correctness blocker, tracked as backlog. None of these were designated mandatory for this closure and none block the verdict below, per the independent audit's own explicit assessment.

## Security / path-recovery regression check

**Zero regressions.** The independent audit re-read and, where applicable, re-ran every previously-PASS control from the baseline's Path Recovery Audit and tool-execution-boundary sections: deny-by-default `ToolPolicy`, `PathPolicy` traversal/hidden/sensitive/symlink-escape denial, one-attempt case-only recovery scoped to `read_file`/`file_metadata` only (never `write`), full `PathPolicy` revalidation after recovery, confirmation required for `EXECUTE_PROJECT`/`WRITE_WORKSPACE`, and recovery never consuming an extra model round. The C toolserver has zero diff for the entire phase (`git diff --stat HEAD -- c_toolserver` empty).

## Full regression

`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q` → **578 passed, 17 skipped, 0 failed** (both in the independent audit's fresh run and in this report's own final confirmation run). `git diff --check` clean.

## ADR disposition

- ADR-024 (Bounded Single Tool Round per Turn): `Superseded` by ADR-069.
- ADR-068 (Provider-Neutral Model Response Metadata): `Implemented`.
- ADR-069 (Bounded Multi-Round Conversational Tool Loop): `Accepted → Implemented` — promoted at this closure per the independent audit's explicit recommendation ("this audit found no gap between what the ADR promises and what the current code, tests, and live reproduction actually do").
- ADR-070 (Interaction Correlation and End-to-End Observability): `Accepted → Implemented` — same basis.
- ADR-071 (Conversation Context and Generation Budget): `Accepted → Implemented` — same basis.

## Two real bugs found and fixed during the phase (worth recording for future reference)

1. A recursive `knowledge rebuild` walk aborted entirely on any single unreadable/binary file (e.g. `__pycache__/*.pyc`) instead of skipping it — fixed prior to Phase 5.2 proper, in the same session (see conversation history; not a Phase 5.2 milestone but adjacent groundwork).
2. `redact_sensitive()`'s substring-based sensitive-keyword matching produced false-positive redactions for legitimate non-secret compound keys (`prompt_tokens`, `output_tokens`, `reserved_output_tokens`, `max_input_tokens`, and — newly found by the independent audit — the literal path `"."`). Worked around at every colliding call site (never by weakening the sanitizer); the root cause remains open and is the phase's one explicitly tracked residual item.

## Residual item for the backlog (not a closure blocker)

`ai_assistant/infrastructure/sanitization.py`'s `redact_sensitive()` substring-matching design should be replaced with precise (exact-key or word-boundary) matching in a dedicated, carefully-reviewed change — it currently only causes over-redaction (reduced diagnostic usefulness), never under-redaction (no confirmed instance of a real secret or sensitive value staying exposed), so it is non-blocking but should not be left indefinitely as more callers accumulate.

## Verdict

The independent post-remediation audit's final verdict is **READY TO CONTINUE**. This report accepts that verdict and sets Phase 5.2's status to `implemented-awaiting-final-human-review`, per the binding instruction that this milestone is a **required human gate** — the supervisor does not declare the phase closed unilaterally; it stops here for the project owner's sign-off.

## Next action

Awaiting human review and explicit approval of this closure package (this report + `docs/audits/chat-tool-context-audit-post-remediation.md` + the ADR-069/070/071 `Implemented` promotion). No further Phase 5.2 or Phase 5.3 work should begin until that approval is given.

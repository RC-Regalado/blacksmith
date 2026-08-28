# Roadmap State — Phase 5.2

## Baseline audit
`docs/audits/chat-tool-context-audit.md`

## Baseline verdict
REMEDIATION REQUIRED

## Current milestone
- M5.2.15 Dedicated adversarial/regression suite pass
- Status: automatically-accepted (self-verified 2026-08-28; no production code changed, test-only milestone)

## Next milestone
- M5.2.16 Repeat deep audit and close
- Status: in-progress — REQUIRED human gate at closure; do not declare "READY TO CONTINUE" unless the repeated independent audit supports it

## Milestone history (summary; full detail in `.agent/roadmap-state.md` and `.agent/reports/`)
- M5.2.1 Freeze remediation baseline — automatically-accepted. FINDING-001/002/003 reproduced; 9 PASS security/path-recovery controls re-verified.
- M5.2.2 Approve ADR-068..071 — accepted via human approval ("he revisado los ADR, aprobados", 2026-08-28). ADR-068..071 moved Proposed -> Accepted.
- M5.2.3/4/5 Provider-neutral `ModelResponse`, Ollama termination metadata, explicit `num_ctx`/`num_predict` — automatically-accepted. ADR-068 moved Accepted -> Implemented.
- M5.2.6/7 `ConversationContextBudget`, `interaction_id` — automatically-accepted. ADR-070/071 remain Accepted (partial satisfaction; residual coordination tracked for M5.2.13/closure).
- M5.2.8-12 ADR-069 bounded multi-round tool loop (budget, duplicate guard, progress guard, loop controller, final synthesis) — automatically-accepted. FINDING-001/003 and the deterministic half of FINDING-004/005 remediated. ADR-024 corrected to `Superseded (by ADR-069)`. ADR-069/070/071 remain Accepted, deferred to M5.2.16 for `Implemented` promotion.
- M5.2.13/14 Correlated `interaction_id` event stream (context/model/tool/synthesis/completion) + `InteractionMetrics` — automatically-accepted. FINDING-008 and FINDING-009 both closed. Two real redaction-substring-collision bugs found via live smoke-testing and fixed (payload keys only, `redact_sensitive()` root cause tracked as a residual item for M5.2.15/16).
- M5.2.15 Dedicated adversarial/regression suite pass — automatically-accepted. Full required-scenario list mapped to tests; 3 integration-level gaps (duplicate failure, changed strategy after failure, exact 3-round bounded flow) found and closed. Test-only milestone, no production code changed.

## Independent validation evidence (M5.2.13-14, 2026-08-28)
- Round 1 — Test agent: PASS on all 7 checks; full suite 573 passed/17 skipped.
- Round 1 — Security reviewer: PASS on all 7 checks; live-reproduced the redaction bug; confirmed every new payload value is a number/bool/enum/fixed-string, never raw content.
- Round 1 — Architecture reviewer: PASS on layering/contract/budget-guard checks; 2 CONCERNs raised (FINDING-008 not actually closed yet; `redact_sensitive` root cause unfixed) — both addressed (first fixed immediately, second explicitly tracked as residual).
- Round 2 (FINDING-008 closure addendum, focused follow-up) — PASS on all 5 checks; live-reproduced the second redaction collision and its fix; confirmed safe `getattr` fallback when no `conversation_context` is configured; confirmed `ConversationContextBudget` is frozen so the new public `budget` attribute is safe; confirmed the new fields are read-only-for-logging, never consumed by policy/budget logic. Full suite 575 passed/17 skipped.

## Baseline reproduction
- FINDING-001 reproduced: existing tests encode second tool request rejection and real diagnostics show `list_directory` success followed by `read_file` rejection at round 2.
- FINDING-002 reproduced: Ollama payload has no `options`, and `OllamaModelProvider.chat()` returns `Message` only, so `done_reason`, `prompt_eval_count` and `eval_count` are discarded.
- FINDING-003 reproduced: runtime returns fixed `Tool round limit reached; no additional tool was executed.` instead of final synthesis.

## Non-regression controls
- ToolPolicy remains deny-by-default.
- PathPolicy denies absolute paths, traversal, hidden paths, sensitive paths and symlink escapes.
- Path recovery is case-only, one-attempt, read-only-tool scoped and revalidates through PathPolicy.
- `write` is excluded from recovery.
- Confirmation remains required for EXECUTE_PROJECT and WRITE_WORKSPACE.
- Audit and diagnostics remain sanitized and must not store prompts or file contents.

## Next gate
The only remaining mandatory human gate is M5.2.16 (final closure): repeat the original deep audit with an independent audit agent, write `docs/audits/chat-tool-context-audit-post-remediation.md`, and require FINDING-001..005/008/009 PASS with no PASS security/path-recovery control regressed before setting phase status to `implemented-awaiting-final-human-review`.

## Closure matrix (updated 2026-08-28, after M5.2.12)
| Finding | Baseline | Status after M5.2.12 | Target |
|---|---|---|---|
| FINDING-001 | FAIL / BLOCKER | Remediated (M5.2.11 bounded multi-round loop); final independent audit pending at M5.2.16 | PASS |
| FINDING-002 | FAIL / BLOCKER | Remediated (M5.2.4 Ollama termination metadata) | PASS |
| FINDING-003 | FAIL / BLOCKER | Remediated (M5.2.12 final synthesis on exhaustion) | PASS |
| FINDING-004 | FAIL / HIGH | Remediated deterministically (M5.2.9 duplicate guard, M5.2.10 progress guard, documented scope) | PASS |
| FINDING-005 | FAIL / HIGH | Remediated (M5.2.8 auditable ToolLoopBudget/executor_operations accounting) | PASS |
| FINDING-007 | PARTIAL / HIGH | Remediated (M5.2.6 unified `estimate_tokens` budget unit) | PASS |
| FINDING-008 | FAIL / HIGH | Remediated (M5.2.13: `ConversationContextBudget` and Ollama `num_ctx`/`num_predict` now land in one observable per-turn record); final independent audit pending at M5.2.16 | PASS |
| FINDING-009 | PARTIAL / HIGH | Remediated (M5.2.13: `interaction_id` correlates context/retrieval, every model request/response, tool activity, final synthesis and completion in one JSONL stream); final independent audit pending at M5.2.16 | PASS |

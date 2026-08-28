# Roadmap State — Phase 5.2

## Baseline audit
`docs/audits/chat-tool-context-audit.md`

## Baseline verdict
REMEDIATION REQUIRED

## Current milestone
- M5.2.16 Repeat deep audit and close
- Status: implemented-awaiting-final-human-review

## Next milestone
- Final human review of corrected Phase 5.2 closure package
- Status: awaiting-review — STOP here; no Phase 5.3 work until explicit owner approval

## Milestone history (summary; full detail in `.agent/roadmap-state.md` and `.agent/reports/`)
- M5.2.1 Freeze remediation baseline — automatically-accepted. FINDING-001/002/003 reproduced; 9 PASS security/path-recovery controls re-verified.
- M5.2.2 Approve ADR-068..071 — accepted via human approval ("he revisado los ADR, aprobados", 2026-08-28). ADR-068..071 moved Proposed -> Accepted.
- M5.2.3/4/5 Provider-neutral `ModelResponse`, Ollama termination metadata, explicit `num_ctx`/`num_predict` — automatically-accepted. ADR-068 moved Accepted -> Implemented.
- M5.2.6/7 `ConversationContextBudget`, `interaction_id` — automatically-accepted. ADR-070/071 remain Accepted (partial satisfaction; residual coordination tracked for M5.2.13/closure).
- M5.2.8-12 ADR-069 bounded multi-round tool loop (budget, duplicate guard, progress guard, loop controller, final synthesis) — automatically-accepted. FINDING-001/003 and the deterministic half of FINDING-004/005 remediated. ADR-024 corrected to `Superseded (by ADR-069)`. ADR-069/070/071 remain Accepted, deferred to M5.2.16 for `Implemented` promotion.
- M5.2.13/14 Correlated `interaction_id` event stream (context/model/tool/synthesis/completion) + `InteractionMetrics` — automatically-accepted. FINDING-008 and FINDING-009 both closed. Two real redaction-substring-collision bugs found via live smoke-testing and fixed (payload keys only, `redact_sensitive()` root cause tracked as a residual item for M5.2.15/16).
- M5.2.15 Dedicated adversarial/regression suite pass — automatically-accepted. Full required-scenario list mapped to tests; 3 integration-level gaps (duplicate failure, changed strategy after failure, exact 3-round bounded flow) found and closed. Test-only milestone, no production code changed.
- M5.2.16 Repeat deep audit and close — implemented-awaiting-final-human-review after corrective M5.2.16-R1 rework. Independent post-remediation audit verdict READY TO CONTINUE was contested by a reproduced runtime symptom: `¿Que hace este proyecto?` with context enabled got `candidates=0`, `selected=0` and fell into tool use. M5.2.16-R1 corrected and independently validated the context-sufficiency gap.

## Human review defect — 2026-08-28
- Prompt: `¿Que hace este proyecto?`
- Observed by user: `context_conversation: candidates=0 ranked=0 selected=0 ... retrieval_attempted=True knowledge_chunks_selected=0`, followed by `tool_loop`.
- Supervisor reproduction with dummy provider confirmed the retrieval side: `Knowledge context requested, but no fresh indexed knowledge matched`; direct store probe returned 0 candidates for `¿Que hace este proyecto?` while returning candidates for `AI Assistant`, `README`, `project`, `proyecto`, and `arquitectura`.
- Root cause hypothesis now evidenced: `ConversationRetrievalPolicy.allow()` returns true for this prompt (`tests/test_conversation_retrieval_policy.py:39-44`), but `SQLiteKnowledgeStore._fts_phrase()` wraps the complete raw query as one exact FTS phrase (`ai_assistant/infrastructure/storage/sqlite_knowledge.py:377-398`), so natural generic questions do not retrieve relevant indexed docs unless the full phrase appears verbatim. Chat bootstrap also constructs `HybridRetriever(knowledge_store)` without an `EmbeddingProvider`, so semantic fallback is unavailable in conversation retrieval (`ai_assistant/bootstrap/container.py:65-78`).
- Corrected by M5.2.16-R1: `SQLiteKnowledgeStore` now normalizes/tokenizes local FTS queries into quoted non-stopword terms; `ConversationKnowledgeContextProvider` adds deterministic, local project-summary expansion for generic non-live-state project-summary prompts; live-state prompts still bypass retrieval before provider invocation. Smoke now reports `candidates=12 ranked=12 selected=12` and `tool_rounds=0` for the reported prompt.
- Independent validation: test/retrieval, architecture and security reviewers all PASS. Full suite after the correction: `585 passed, 17 skipped`. Focused regression added for `What is the current project git status?` to prove project-summary expansion does not override live-state bypass.

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
The final Phase 5.2 owner review is awaiting review again after M5.2.16-R1. The original deep audit was repeated, and the missed generic project-summary retrieval gap has now been corrected/revalidated. Phase status is `implemented-awaiting-final-human-review` until explicitly accepted by the owner.

## Closure matrix (updated 2026-08-28, after M5.2.16)
| Finding | Baseline | Final status | Target |
|---|---|---|---|
| FINDING-001 | FAIL / BLOCKER | PASS — independent audit live-verified bounded multi-round loop | PASS |
| FINDING-002 | FAIL / BLOCKER | Remediated (M5.2.4 Ollama termination metadata) | PASS |
| FINDING-003 | FAIL / BLOCKER | Remediated (M5.2.12 final synthesis on exhaustion) | PASS |
| FINDING-004 | FAIL / HIGH | Remediated deterministically (M5.2.9 duplicate guard, M5.2.10 progress guard, documented scope) | PASS |
| FINDING-005 | FAIL / HIGH | Remediated (M5.2.8 auditable ToolLoopBudget/executor_operations accounting) | PASS |
| FINDING-007 | PARTIAL / HIGH | Remediated (M5.2.6 unified `estimate_tokens` budget unit) | PASS |
| FINDING-008 | FAIL / HIGH | PASS — independent audit live-verified context/Ollama limits in one observable record | PASS |
| FINDING-009 | PARTIAL / HIGH | PASS — independent audit live-verified one `interaction_id` across context/model/tool/synthesis/completion | PASS |

# Phase 5.2 Remediation Kit

Purpose: remediate `docs/audits/chat-tool-context-audit.md` before feature expansion.

Install by merging with the repository. Preserve ADR history, `.agent` history, original audit and diagnostic logs.

Important implementation order:
ModelResponse/termination metadata
→ context/generation budget
→ interaction correlation
→ ToolLoopBudget/controller
→ duplicate guard
→ progress guard
→ bounded multi-round chat
→ final synthesis
→ end-to-end observability
→ repeated audit

Start with `SUPERVISOR-INITIAL-PROMPT-PHASE-5.2.md`.

# Human Review Queue

Generated changes are provisional until recorded here.

## Review statuses

- `awaiting-review`
- `approved`
- `changes-requested`
- `rejected`

## Milestone reviews

| Milestone | Automated status | Review status | Reviewer | Date | Findings |
|---|---|---|---|---|---|
| M1 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "El milestone 1 está correcto". |
| M2 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Revisado, pasa el M3". |
| M3 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobado, pasa el M4". |
| M4 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobado, pasa al siguiente milestone". |
| M5 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "aprobado, pasa al M6". |
| M6 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "aprobado". |
| M7 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "aprobado, inicia el M8". |
| M8 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "aprobado, pasa al M9". |
| M9 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobado, inicia el M10". |
| M10 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed Ollama responds; first cold start may require higher timeout. |
| M11 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobadom inicia el M12". |
| M12 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobado, inicia el M13". |
| M13 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobado, inicia M14". |
| M14 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobado, todo sigue funcionando correctamente. Inicia el M15". |
| M15 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobado, finaliza la fase 1 con la documentación". |
| M16 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User requested Phase 1 closure after M15 approval; CI implemented and core commands validated locally. |
| M17 | implemented-awaiting-human-review | approved | User | 2026-07-29 | User confirmed: "Aprobado. Valida los datos necesarios para pasar a la fase 2". |
| M2.1 | implemented-awaiting-human-review | approved | User | 2026-07-30 | User confirmed: "aprobados los ADR-016 a ADR-025." |
| M2.2 | implemented-awaiting-human-review | approved | User | 2026-07-30 | User confirmed: "Aprobado, inicia el M2.3". |
| M2.3 | implemented-awaiting-human-review | approved | User | 2026-07-30 | User confirmed: "Aprobado, pasa al M2.4". |
| M2.4 | implemented-awaiting-human-review | approved | User | 2026-07-31 | User confirmed: "aprobado, pasa al M2.5". |
| M2.5 | implemented-awaiting-human-review | approved | User | 2026-07-31 | User confirmed: "Aprobado, inicia el M2.6". |
| M2.6 | implemented-awaiting-human-review | approved | User | 2026-07-31 | User confirmed: "Aprobado. Pasa al M2.7". |
| M2.7 | implemented-awaiting-human-review | approved | User | 2026-08-01 | User confirmed: "Aprobado, pasa al M2.8". |
| M2.8 | implemented-awaiting-human-review | approved | User | 2026-08-01 | User confirmed: "Aprobado. Inicia el M2.9". |
| M2.9 | implemented-awaiting-human-review | approved | User | 2026-08-01 | User confirmed: "aprobado, pasa al M2.10". |
| M2.10 | implemented-awaiting-human-review | approved | User | 2026-08-01 | User confirmed: "Aprobado. Pasa al M2.11". |
| M2.11 | implemented-awaiting-human-review | approved | User | 2026-08-01 | User confirmed: "aprobado, pasa al M2.12". |
| M2.12 | implemented-awaiting-human-review | awaiting-review | — | 2026-08-01 | Read-only tool configuration and bootstrap wiring implemented; review `.agent/reports/M2.12.md`. |

## Approval gates

| Gate ID | Related task | Requested decision | Why blocked | Status | Resolution |
|---|---|---|---|---|---|
| PHASE2-G1 | Phase 2 | Approve exact tool execution safety policy | Phase 2 introduces side effects; accepted supervisor rules require approval before tool execution or weakening safety boundaries. | closed | Approved through ADR-016, ADR-017, ADR-023 and ADR-024. |
| PHASE2-G2 | Phase 2 | Approve initial tool scope and permission levels | Existing proto has permission enums, but no policy mapping from tool name to allowed permission. | closed | Approved through ADR-018 and ADR-019. |
| PHASE2-G3 | Phase 2 | Approve audit persistence target and retention | Phase 2 requires audit, but no durable audit schema or retention policy exists. | closed | Approved through ADR-020. |
| PHASE2-G4 | M2.1 | Approve ADR-016 through ADR-025 after proposal | Required Phase 2 ADRs must be accepted before productive execution tasks become eligible. | closed | ADR-016 through ADR-025 approved by user. |

## Manual review record template

### REVIEW-<ID>

- Milestone:
- Commit or diff:
- Automated report:
- Reviewer:
- Date:
- Status:
- Defects:
- Required corrections:
- Accepted residual risks:
- Notes:

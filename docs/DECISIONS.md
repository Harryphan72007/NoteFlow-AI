# Decisions

| ID | Date | Decision | Rationale | Consequences |
|---|---|---|---|---|
| D001 | 2026-07-18 | Preserve `Frontend/src/app/App.tsx` visual structure as the UI source of truth | User explicitly requires no frontend redesign | Backend and adapters must conform to existing UI shapes |
| D002 | 2026-07-18 | Add backend beside the existing `Frontend` folder | Workspace does not contain a backend at baseline | New backend files are required rather than modifying existing backend code |
| D003 | 2026-07-18 | Use SQLite by default with SQLAlchemy models designed for PostgreSQL compatibility | Prompt requires local default and PostgreSQL-compatible schema | Alembic migrations and tests are required |
| D004 | 2026-07-18 | Use deterministic clinical/comparison rules as the verified baseline; treat ASR/OCR/Ollama model execution as optional when local models are unavailable | Large model availability is unknown in this workspace | API can be tested without pretending real model inference was verified |
| D005 | 2026-07-18 | Keep default ASR model config as `qwen-0.6b` and CPU dtype as `float32` | Prompt requires consistency | Apply in env example/settings/docs |

## Resume Notes

- Update this file for architectural or testing decisions that affect future work.

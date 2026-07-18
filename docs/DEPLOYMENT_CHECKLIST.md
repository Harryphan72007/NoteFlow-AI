# Deployment Checklist

Statuses: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `VERIFIED`.

| Item | Status | Evidence | Notes |
|---|---|---|---|
| Environment file created | DONE | `.env.example` added |  |
| Required directories created | DONE | `data/uploads`, `data/processed`, `data/exports` created |  |
| Database migrated | VERIFIED | Alembic upgrade/downgrade passed on `migration_test.db` |  |
| Models available | BLOCKED | Unknown local model state | ASR/PaddleOCR/Ollama may require user setup |
| Ollama running | NOT_STARTED |  | Check through `/health` once backend exists |
| Ollama model installed | NOT_STARTED |  | Target `qwen3:4b` |
| Backend dependencies installed | VERIFIED | `.venv` installed `backend/requirements.txt` |  |
| Frontend dependencies installed | VERIFIED | `pnpm install` passed after config fix |  |
| Frontend build succeeds | VERIFIED | `pnpm run build` passed | Chunk-size warning remains |
| Backend starts | VERIFIED | Uvicorn smoke started on 127.0.0.1:8000 |  |
| Health endpoint succeeds | VERIFIED | `Invoke-RestMethod /health` returned `status ok` |  |
| Frontend reaches backend | NOT_STARTED |  |  |
| Backend reaches Ollama | NOT_STARTED |  |  |
| ASR sample succeeds | BLOCKED | No sample/model verified |  |
| OCR sample succeeds | BLOCKED | No sample/model verified |  |
| Docker images build | NOT_STARTED |  |  |
| Containers become healthy | NOT_STARTED |  |  |
| Persistent data survives restart | NOT_STARTED |  |  |
| Export files are writable | VERIFIED | TXT export test passed | PDF/JSON/SRT/VTT not all directly tested |
| Logs contain no critical errors | NOT_STARTED |  |  |

## Resume Notes

- Checklist initialized before backend/deployment implementation.

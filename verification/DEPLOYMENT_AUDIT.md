# Deployment Audit

## Local Development

| Check | Result | Evidence |
|---|---|---|
| Backend dependencies installed | PASS | `.venv` exists and pytest runs |
| Backend tests | PASS | `workflow_commands.json` |
| Frontend dependencies installed | PASS | `pnpm run build` succeeds |
| Frontend build | PASS | `workflow_commands.json` |
| Database migration upgrade | PASS | Alembic terminal output |
| Database migration downgrade | PASS | Alembic terminal output |
| Frontend dev render | PASS | `frontend_dashboard.png` |
| Health endpoint | PASS | API audit `health.json` |

## Docker

Status: **BLOCKED_BY_ENVIRONMENT**

Command:

```powershell
docker --version
```

Actual:

```text
docker : The term 'docker' is not recognized
```

Manual verification commands:

```powershell
Copy-Item .env.example .env
docker compose build
docker compose up -d
docker compose ps
docker compose logs backend
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Deployment Risks

- Real model files are not mounted or verified.
- Docker image build may fail or produce large images once real OCR/ASR dependencies are added.
- Frontend container can serve UI, but UI is not wired to backend.
- Persistent volume behavior was not tested in Docker.

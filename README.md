# NoteFlow AI

Local clinical documentation-support prototype for audio/text/document workflows.

This repository now contains:
- `Frontend/`: the approved React/Vite UI. Its visual source was preserved.
- `backend/`: FastAPI backend with SQLAlchemy persistence, Alembic migration, deterministic clinical checks, comparison metrics, task/audit/export routes, and controlled model-status endpoints.

This application is a documentation-support prototype and is not a medical diagnosis or treatment system.

## Local Backend

```powershell
& 'C:\Users\Dell\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
& .\.venv\Scripts\python.exe -m alembic upgrade head
& .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Local Frontend

```powershell
cd Frontend
& 'C:\Users\Dell\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' install
& 'C:\Users\Dell\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' run build
& 'C:\Users\Dell\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' run dev
```

## Tests

```powershell
& .\.venv\Scripts\python.exe -m pytest backend\tests -q
```

Migration smoke:

```powershell
$env:DATABASE_URL='sqlite:///./data/migration_test.db'
& .\.venv\Scripts\python.exe -m alembic upgrade head
& .\.venv\Scripts\python.exe -m alembic downgrade base
```

## Model Notes

Real Mega-ASR/Qwen3-ASR and PaddleOCR inference is not bundled or verified in this workspace. The `/api/transcribe` and `/api/ocr` endpoints accept `.txt` fallback uploads for API testing and return warnings in metadata. Install and configure real model runtimes before claiming real ASR/OCR verification.

Ollama is checked through `/health`; deterministic local fallbacks are used for simple AI utility endpoints when Ollama is unavailable.

## Docker

```powershell
Copy-Item .env.example .env
docker compose build
docker compose up -d
docker compose ps
```

Docker build/deployment has been scaffolded but was not verified in this run.

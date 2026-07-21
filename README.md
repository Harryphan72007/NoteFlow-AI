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

`http://127.0.0.1:8000/health` is the backend status endpoint, not the application UI.

## Local Frontend

```powershell
cd Frontend
& 'C:\Users\Dell\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' install
& 'C:\Users\Dell\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' run build
& 'C:\Users\Dell\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' run dev
```

Open the application at `http://127.0.0.1:5173/`.

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

The normal CPU configuration uses the official Qwen3-ASR-0.6B checkpoint through the Mega-ASR/Qwen runtime. The full Mega-ASR 1.7B LoRA/router path remains available through configuration, but is intentionally not the CPU default. PaddleOCR uses the local PP-OCRv6 detection and recognition checkpoints.

Ollama uses local `qwen3:4b` structured generation. `/health` reports service reachability, configured-model availability, and whether the model is currently loaded. `OLLAMA_KEEP_ALIVE=30m` avoids repeated cold model reloads; lower it if memory pressure is more important than latency.

Docker support was removed on 2026-07-18. The supported workflow runs directly via the project virtual environment and pnpm.

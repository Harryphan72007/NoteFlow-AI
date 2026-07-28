# NoteFlow AI

[![CI](https://github.com/Harryphan72007/NoteFlow-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/Harryphan72007/NoteFlow-AI/actions/workflows/ci.yml)
![Status](https://img.shields.io/badge/status-active%20prototype-2563EB)
![Data](https://img.shields.io/badge/demo%20data-synthetic-0F766E)

A local-first documentation workflow for turning text, audio, and scanned documents into reviewable records without hiding model output, corrections, confidence, or reviewer actions.

> [!CAUTION]
> NoteFlow is a software prototype, not a diagnosis, treatment, or clinical decision system. All interface records and screenshots use synthetic data. The project has not been validated for real-world medical use.

![NoteFlow dashboard with synthetic demo data](docs/assets/noteflow-dashboard.png)

## Why NoteFlow

Many documentation pipelines collapse source material and model output into one generated record. NoteFlow keeps those stages separate so a reviewer can inspect what the system received, what a model produced, what changed, and who approved the correction.

## Capabilities

| Area | Implemented workflow |
| --- | --- |
| Ingestion | Manual notes, audio, images, and document uploads |
| Review | Correctable ASR/OCR records with original and edited values |
| Comparison | WER, CER, and numeric-mismatch checks |
| Documentation | Deterministic checks, issues, and follow-up tasks |
| Traceability | Ownership checks, audit events, and export history |
| Quality | Backend regression tests and frontend lint, type-check, test, and build gates |

## Architecture

```text
React + TypeScript + Vite
          │
          │ authenticated REST requests
          ▼
       FastAPI
          ├── SQLAlchemy entities and Alembic migrations
          ├── upload, processed-file, and export storage
          ├── optional ASR, OCR, and Ollama adapters
          ├── comparison and documentation-review services
          └── task, audit, and export services
```

The backend is the system of record. Original sources and corrected outputs remain separate, and model adapters fail visibly by default rather than silently changing behavior.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the entity and service boundaries.

## Technology

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, SQLite/PostgreSQL  
**Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts  
**Quality:** pytest, ESLint, TypeScript, Vitest, GitHub Actions  
**Optional local integrations:** ASR, PaddleOCR, Ollama

## Quick start

Prerequisites:

- Python 3.11+
- Node.js 22+
- pnpm 10+

Create the local environment and start the API:

```bash
cp .env.example .env

cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal, start the interface:

```bash
cd Frontend
pnpm install
pnpm dev
```

Open `http://localhost:5173`. Development credentials and local defaults are documented in `.env.example`; replace them before any shared deployment.

## Optional model runtimes

The core workflow can be explored without distributing private models. Install `backend/requirements-models.txt` only when exercising PaddleOCR, then point the relevant `.env` variables at local checkpoints.

Private Mega-ASR source code and checkpoints are not included. This repository contains only configuration and adapter boundaries for those external dependencies.

## Verification

Run backend checks:

```bash
python -m pytest backend/tests
```

Run frontend checks:

```bash
cd Frontend
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

GitHub Actions runs both quality pipelines on pushes to `main` and pull requests.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system boundaries and data flow
- [`docs/STATUS.md`](docs/STATUS.md) — implemented, in-progress, and explicitly unclaimed work
- [`docs/PRIVACY.md`](docs/PRIVACY.md) — privacy and safety requirements

## Project status

**Implemented**

- Customer, document, task, audit, and export API workflows
- Manual text, audio, image, and document ingestion
- Correctable ASR/OCR records
- Comparison and deterministic documentation checks
- React workflow interface
- Backend regression tests and frontend quality gates

**In progress**

- Replacing remaining fixture-backed UI paths with live API state
- Packaging local model setup and health diagnostics
- Expanding frontend behavioral tests

**Not claimed**

- Production readiness
- Clinical validation or regulatory compliance
- Benchmark-quality model accuracy or latency
- Distribution rights for private models, checkpoints, or research code

## Privacy and licensing

Never commit real patient, customer, employer, or research-lab data. Generated uploads, exports, databases, logs, model files, and environment secrets are intentionally ignored.

This repository currently has no license. Reuse permission has not been granted.

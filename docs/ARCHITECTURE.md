# Architecture

NoteFlow separates the browser workflow from a FastAPI system of record.

```text
Browser
  └─ React + TypeScript + Vite
       └─ authenticated REST requests
            └─ FastAPI
                 ├─ SQLAlchemy entities and Alembic migrations
                 ├─ upload, processed-file, and export storage
                 ├─ ASR, OCR, and Ollama adapters
                 ├─ comparison and documentation-review services
                 └─ task, audit, and export services
```

Core entities are customers, documents, ASR segments, OCR pages/blocks, analyses, issues, tasks, exports, and audit events. The original source and corrected output are stored separately so a reviewer can trace changes.

Model adapters fail visibly by default. Text fallback modes exist only as explicit development options and are disabled in `.env.example`.

Private Mega-ASR source code and checkpoints are external dependencies. This repository contains configuration and adapter boundaries only.

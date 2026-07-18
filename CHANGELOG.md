# Changelog

## 2026-07-18

- Added project-control documentation required by the execution controller prompt.
- Recorded initial baseline: existing React/Vite frontend only, no backend, no git metadata, no deployment files, no tests.
- Started frontend-to-backend API contract mapping from the approved UI surface.
- Added FastAPI backend scaffold with SQLAlchemy models, Alembic migration, customer/document/task/clinical/comparison/export routes, deterministic clinical checks, and controlled ASR/OCR text fallback ingestion.
- Added backend pytest coverage for focused workflow, cross-customer rejection, OCR/ASR text fallback ingestion, metrics, clinical rules, issue decisions, tasks, and TXT export.
- Added Dockerfiles, Compose file, `.env.example`, and frontend nginx reverse-proxy config.
- Fixed nonvisual frontend `pnpm-workspace.yaml` package-manager config for allowed native builds and Windows architecture.
- Verified backend tests, Alembic upgrade/downgrade, backend `/health`, and frontend production build.

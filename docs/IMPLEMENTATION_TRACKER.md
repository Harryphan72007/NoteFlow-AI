# Implementation Tracker

Statuses: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `IMPLEMENTED`, `TESTED`, `VERIFIED`.

Baseline as of 2026-07-18:
- Workspace contains an approved React/Vite frontend under `Frontend/`.
- No `.git` repository metadata is present in `D:\NoteFlow AI`.
- No backend, database, migrations, tests, Docker files, or API client were present at initial inspection.
- Frontend UI preservation is mandatory; visual changes are not intentional unless explicitly recorded.

| ID | Area | Requirement | Frontend location | Backend endpoint/service | Database dependency | Implementation status | Test status | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| R001 | Existing frontend preservation | Preserve layout, styles, labels, routes, and responsive behavior | `Frontend/src/app/App.tsx`, styles | N/A | N/A | IN_PROGRESS | NOT_RUN | Baseline inspection started | Frontend currently uses embedded sample data |
| R002 | Configuration | Consistent env configuration and `.env.example` | `Frontend/vite.config.ts` | Backend settings service | N/A | TESTED | PASS | `.env.example`; backend tests | Default ASR model is `qwen-0.6b` |
| R003 | Database | SQLAlchemy models for customers, documents, OCR, analyses, tasks, audit, exports | Existing data tables/cards | Persistence layer | SQLite default, PostgreSQL-compatible models | TESTED | PASS | `backend/app/models.py`; pytest | Alembic also added |
| R004 | Migrations | Alembic upgrade/downgrade path | N/A | Alembic | Database schema | VERIFIED | PASS | Alembic upgrade/downgrade passed | Migration `0001_initial` |
| R005 | Customer management | Create/search/edit/archive/restore customers | Customers screen, customer workspace | `/api/customers*` | `customers` | TESTED | PASS | Customer create covered; endpoints implemented | Archive/restore implemented but not directly tested |
| R006 | Customer data isolation | Reject cross-customer access/combine/export | Customers/documents/compare/reports | Service authorization checks | FK relationships | TESTED | PASS | Cross-customer combine test returns 409 | Broader 403 auth not implemented |
| R007 | Audio recording | Browser recording flow connected | New Processing screen | `/api/transcribe` | `documents`, `asr_segments` | NOT_STARTED | NOT_RUN | UI appears present in `App.tsx` | Preserve current UI controls |
| R008 | Audio upload | Upload audio and save transcript | New Processing screen | `/api/transcribe` | `documents`, `asr_segments` | NOT_STARTED | NOT_RUN | UI appears present in `App.tsx` | Support wav/mp3/m4a/flac/ogg/webm where practical |
| R009 | ASR inference | Load one ASR service with lock | ASR review/history | ASR model service | `documents`, `asr_segments` | NOT_STARTED | NOT_RUN | No backend present | Real model may be unavailable locally |
| R010 | ASR segments | Timestamped segments and exports | ASR review | ASR response/schema | `asr_segments` | NOT_STARTED | NOT_RUN | No backend present | SRT/VTT require segments |
| R011 | Transcript correction | Save corrected transcript | ASR review | `PATCH /api/documents/{id}/text` | `documents`, audit | NOT_STARTED | NOT_RUN | UI appears present | Must audit corrections |
| R012 | OCR image processing | Image upload, preprocess, extract text | New Processing/OCR review | `/api/ocr` | `documents`, `ocr_pages`, `ocr_blocks` | NOT_STARTED | NOT_RUN | No backend present | PaddleOCR preferred; fallback should be explicit |
| R013 | OCR PDF processing | Multi-page scanned PDF OCR | New Processing/OCR review | `/api/ocr` | `ocr_pages`, `ocr_blocks` | NOT_STARTED | NOT_RUN | No backend present | Validate encrypted/page-limit cases |
| R014 | OCR bounding boxes | Return block/page coordinates | OCR review | OCR service/schema | `ocr_blocks` | NOT_STARTED | NOT_RUN | No backend present | Needed for side-by-side review |
| R015 | OCR confidence | Confidence scores and low-confidence warnings | OCR review/dashboard | OCR service/schema | `ocr_blocks`, `documents` | NOT_STARTED | NOT_RUN | No backend present | Thresholds configurable |
| R016 | OCR correction | Correct OCR block/text and audit | OCR review | `PATCH /api/documents/{id}/ocr-blocks/{block_id}` | `ocr_blocks`, audit | NOT_STARTED | NOT_RUN | UI appears present | Do not silently alter low-confidence values |
| R017 | Manual documents | Typed notes saved as documents | New Processing/manual note UI | `/api/documents/manual` | `documents` | TESTED | PASS | API workflow test | `source_type=manual_text` |
| R018 | Unified document schema | Normalize audio/image/pdf/manual/combined | Documents/history/review screens | Document service | `documents` and child tables | TESTED | PASS | Serializers and API tests | Preserve provenance |
| R019 | Document history | Persist and list documents/history | Documents/history/dashboard | `/api/documents`, `/api/customers/{id}/activity` | documents/audit | NOT_STARTED | NOT_RUN | Sample arrays in `App.tsx` | Replace mock data later without visual redesign |
| R020 | Document combination | Combine selected same-customer docs | Compare/clinical review | `/api/documents/combine` | `documents` | TESTED | PASS | API workflow and cross-customer tests | Rejects cross-customer combinations |
| R021 | ASR-OCR comparison | Compare text sources | Compare screen | `/api/compare` | Optional analysis record | TESTED | PASS | API workflow test | Includes WER/CER/diffs |
| R022 | WER | Word error rate metric | Compare/evaluation | Comparison service | N/A | TESTED | PASS | Metrics unit test |  |
| R023 | CER | Character error rate metric | Compare/evaluation | Comparison service | N/A | TESTED | PASS | Metrics unit test |  |
| R024 | Numerical mismatch detection | Detect critical number mismatch | Compare/clinical review | Comparison/clinical checker | N/A | TESTED | PASS | `0.5 mg` vs `5 mg` test |  |
| R025 | Unit mismatch detection | Detect units/date/medication mismatches | Compare/clinical review | Comparison/clinical checker | N/A | NOT_STARTED | NOT_RUN | No backend present | Unit tests required |
| R026 | Ollama availability | Health check local Ollama safely | Sidebar/settings/health | `/health`, AI tools | N/A | TESTED | PASS | `/health` smoke | Handles unavailable Ollama as `available=false` |
| R027 | Summarization | Structured local AI summary | Clinical/doc views | `/api/ai/summarize` | optional model_runs | IMPLEMENTED | NOT_RUN | Route implemented | Deterministic fallback only |
| R028 | Translation | Local AI translation | Settings/tools if exposed | `/api/ai/translate` | optional model_runs | NOT_STARTED | NOT_RUN | No backend present | Strict JSON validation |
| R029 | Key points | Local AI key point extraction | Review screens | `/api/ai/key-points` | optional model_runs | NOT_STARTED | NOT_RUN | No backend present | Strict JSON validation |
| R030 | Task extraction | Extract follow-up tasks | Tasks/clinical review | `/api/ai/tasks`, clinical checker | `tasks` | TESTED | PASS | Clinical workflow test creates tasks | Deterministic |
| R031 | Structured clinical extraction | Extract meds/allergies/vitals/findings | Clinical review | clinical extractor | analysis/result JSON | IMPLEMENTED | PASS | Clinical rules tested for meds/allergy | Not full NER |
| R032 | Missing-field checking | Deterministic missing documentation checks | Clinical review | clinical checker | analyses/issues | TESTED | PASS | Metrics/clinical tests | Note-type partial |
| R033 | Contradiction checking | Detect possible inconsistencies | Clinical review | clinical checker | analyses/issues | IMPLEMENTED | NOT_RUN | Chest-pain rule implemented | Needs direct test |
| R034 | Medication documentation | Check medication completeness/allergy conflicts | Clinical review | clinical checker | analyses/issues | TESTED | PASS | Clinical tests | Does not invent values |
| R035 | Risk scoring | Green/Yellow/Red/Blocked score | Dashboard/clinical review | risk scorer | analyses | TESTED | PASS | Clinical tests | Score components returned |
| R036 | Issue decisions | Accept/edit/ignore/resolve issues | Clinical review | `/api/issues/{id}/decision` | analysis_issues/audit | TESTED | PASS | Issue ignore tests | Reviewer reason required for ignore |
| R037 | Task management | Create/update/complete/delete tasks | Tasks screen | `/api/tasks*` | tasks/audit | TESTED | PASS | Task complete covered | Customer-scoped |
| R038 | TXT export | Export corrected text | Documents/review | `/api/documents/{id}/export/txt` | exports | TESTED | PASS | TXT export test | |
| R039 | JSON export | Export structured JSON | Documents/review | `/api/documents/{id}/export/json` | exports | NOT_STARTED | NOT_RUN | No backend present | |
| R040 | PDF export | Export PDF/report | Documents/customer report | `/api/documents/{id}/export/pdf`, report | exports | NOT_STARTED | NOT_RUN | No backend present | |
| R041 | SRT export | Export audio subtitles | ASR review | `/api/documents/{id}/export/srt` | asr_segments/exports | NOT_STARTED | NOT_RUN | No backend present | Audio only |
| R042 | VTT export | Export web subtitles | ASR review | `/api/documents/{id}/export/vtt` | asr_segments/exports | NOT_STARTED | NOT_RUN | No backend present | Audio only |
| R043 | Customer report | Export customer-level report | Customer workspace | `/api/customers/{id}/export/report` | customers/documents/analyses/tasks | NOT_STARTED | NOT_RUN | No backend present | |
| R044 | Audit logging | Record edits, decisions, exports | History/customer activity | audit service | audit_logs | NOT_STARTED | NOT_RUN | No backend present | No sensitive text in logs unless needed |
| R045 | File cleanup | Clean temporary uploads safely | Backend only | storage service | N/A | NOT_STARTED | NOT_RUN | No backend present | Test cleanup |
| R046 | Security validation | Validate paths, MIME, sizes, PDFs, prompt injection | Upload/review flows | validators/services | N/A | NOT_STARTED | NOT_RUN | No backend present | |
| R047 | Local deployment | Reproducible Windows local dev | README/docs | Uvicorn/Vite | SQLite | TESTED | PASS | Backend health and frontend build passed | Dev server not left running |
| R048 | Docker deployment | Dockerfiles/compose/health/persistence | N/A | backend/frontend containers | volumes | IMPLEMENTED | NOT_RUN | Docker files added | Not built/tested |
| R049 | Persistent storage | Restart does not remove data/files | All persisted UI | DB/storage services | SQLite/files | NOT_STARTED | NOT_RUN | No backend present | |
| R050 | Documentation | README/API/deployment/known limitations | Docs | N/A | N/A | IN_PROGRESS | NOT_RUN | Control docs created | Must be updated continuously |
| R051 | End-to-end verification | Full workflow passes with evidence | Full UI/API | All services | All core tables | NOT_STARTED | NOT_RUN | No backend present | Real ASR/OCR may require model availability |

## Resume State

- Last completed requirement: Initial attachment review and repository discovery.
- Currently active task: Baseline/control documentation and frontend/API mapping.
- Current failure, if any: Frontend UI still uses embedded sample data; API integration wiring is not complete.
- Next exact command: Add nonvisual frontend API client/state adapters or run `docker compose build` if deployment verification is the next priority.
- Files currently being edited: backend scaffold, docs, deployment files.
- Tests that must be rerun: `pytest backend\tests -q`, `pnpm run build`, Docker build when Docker is available.

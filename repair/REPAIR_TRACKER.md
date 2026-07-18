# Repair Tracker

Allowed statuses: `NOT_STARTED`, `IN_PROGRESS`, `FIXED`, `TEST_FAILED`, `VERIFIED`, `BLOCKED`.

| Issue ID | Severity | Original failure | Affected files | Repair | Regression test | Current status | Evidence |
|---|---|---|---|---|---|---|---|
| ERR-001 | Critical | `GET /api/documents/{id}` exposes another customer's document by guessed ID | `backend/app/routes/documents.py`, `backend/app/routes/tasks.py`, `backend/app/routes/clinical_review.py`, `backend/app/services/ownership.py`, `backend/tests/test_security_repairs.py` | Enforced optional `customer_id` ownership context on direct document/task/issue routes; added read/write/delete/export/correction/finalize/task/issue tests | `pytest backend/tests`, `verify_api.py` | VERIFIED | 10/10 pytest pass; 35/35 API audit pass |
| ERR-002 | High | Invalid customer email accepted | `backend/app/schemas.py`, `backend/tests/test_security_repairs.py` | Added optional email validation plus focused nonblank/status/priority/language validation | `pytest backend/tests`, `verify_api.py` | VERIFIED | Invalid email now returns 422; 35/35 API audit pass |
| ERR-003 | Critical | Frontend has no API calls and buttons are mock/no-op | `Frontend/src/app/App.tsx`, `Frontend/src/api/client.ts`, `Frontend/vite.config.ts` | Added central API adapter, Vite `/api` proxy, live customer/document/task loading, manual note save, new customer create, task completion; preserved existing UI structure/styles | frontend build, source scan, workflow script | FIXED | Frontend build pass; source scan shows API client/use sites |
| ERR-004 | Medium | Docker unavailable | Docker environment | Cannot repair in code beyond existing Docker files | `docker --version` | BLOCKED | Docker not on PATH |
| MF-ASR | Critical | Real ASR unavailable | backend ASR service | Requires model/runtime not present | real ASR smoke | BLOCKED | Health/model status |
| MF-OCR | Critical | Real OCR unavailable | backend OCR service | Requires PaddleOCR/runtime not present | real OCR smoke | BLOCKED | Health/model status |
| MF-OLLAMA | High | Real Ollama structured output unverified | backend AI service | Requires local Ollama/model availability | Ollama integration tests | BLOCKED | Health/model status |
| PHASE-1-ASR | Critical | Existing sibling Mega-ASR must pass standalone real-audio transcription before NoteFlow integration | `D:\Mega-ASR\Mega-ASR` | Inspected actual Mega-ASR source; standalone run failed before model load because `torch` is missing | `infer.py --audio assets/example/F01_22GC010K_STR.wav` | BLOCKED | `repair/PHASE_0_1_REAL_INTEGRATION_STATUS.md` |

## Resume State

- Active repair: stopped at Phase 1 by prompt rule.
- Next command: install/activate Mega-ASR runtime dependencies and model weights, then rerun standalone `infer.py` real-audio test.

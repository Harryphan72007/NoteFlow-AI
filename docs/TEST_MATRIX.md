# Test Matrix

Statuses: `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`.

| Test ID | Feature | Test type | Command | Expected result | Actual result | Status | Last run | Evidence |
|---|---|---|---|---|---|---|---|---|
| T001 | Repository baseline | Inspection | `rg --files` | Project files listed | Only `Frontend/*` files were present initially | PASS | 2026-07-18 | Terminal output |
| T002 | Git metadata | Inspection | `git status --short` | Git status available | Failed: not a git repository | FAIL | 2026-07-18 | `fatal: not a git repository` |
| T003 | Frontend build | Build | `pnpm run build` in `Frontend` | Vite build succeeds | Passed; Vite built 2219 modules with one chunk-size warning | PASS | 2026-07-18 | Terminal output |
| T004 | Frontend routes render | Frontend smoke | Playwright/manual route smoke | Major screens render with no console errors | Not run yet | NOT_RUN |  |  |
| T005 | Backend health | API | `Invoke-RestMethod http://127.0.0.1:8000/health` | Health returns services | Passed: returned `status ok` | PASS | 2026-07-18 | Uvicorn smoke output |
| T006 | Customer API | API | `pytest backend/tests/test_api_workflow.py` | Customer CRUD/isolation pass | Covered create and cross-customer combine rejection | PASS | 2026-07-18 | `6 passed` suite output |
| T007 | Document API | API | `pytest backend/tests/test_api_workflow.py` | Document CRUD/combine pass | Manual create, combine, text fallback ingest covered | PASS | 2026-07-18 | `6 passed` suite output |
| T008 | Comparison metrics | Unit/API | `pytest backend/tests/test_metrics_clinical.py` | WER/CER/mismatch tests pass | Passed dose mismatch test | PASS | 2026-07-18 | `6 passed` suite output |
| T009 | Clinical checker | Unit/API | `pytest backend/tests/test_metrics_clinical.py`, `pytest backend/tests/test_api_workflow.py` | Missing/contradiction/risk tests pass | Passed allergy conflict, medication missing fields, issue decisions | PASS | 2026-07-18 | `6 passed` suite output |
| T010 | OCR service | Unit/API | `pytest backend/tests/test_api_workflow.py` | OCR validation/fallback tests pass | Text fallback OCR path covered; real PaddleOCR not installed/tested | PASS | 2026-07-18 | `test_text_fallback_ingestion_paths` |
| T011 | Exports | Unit/API | `pytest backend/tests/test_api_workflow.py` | TXT/JSON/PDF/SRT/VTT exports pass | TXT export covered; JSON/PDF/SRT/VTT implemented but not directly tested | PASS | 2026-07-18 | `test_customer_document_compare_clinical_task_export_workflow` |
| T012 | Docker compose | Deployment | `docker compose build` | Images build | Docker files not implemented yet | BLOCKED | 2026-07-18 | No Docker files present |
| T013 | End-to-end workflow | E2E | `pytest backend/tests/test_e2e_workflow.py` | Full workflow passes | Backend not implemented yet | BLOCKED | 2026-07-18 | No backend present |
| T014 | Alembic upgrade | Database | `alembic upgrade head` with `DATABASE_URL=sqlite:///./data/migration_test.db` | Upgrade succeeds | Passed | PASS | 2026-07-18 | Alembic output |
| T015 | Alembic downgrade | Database | `alembic downgrade base` with `DATABASE_URL=sqlite:///./data/migration_test.db` | Downgrade succeeds | Passed | PASS | 2026-07-18 | Alembic output |
| T016 | Backend focused suite | Unit/API | `.venv\Scripts\python.exe -m pytest backend\tests -q` | All focused tests pass | 6 passed, 60 deprecation warnings | PASS | 2026-07-18 | Pytest output |

## Resume Notes

- Initial test matrix created before backend implementation, per controller prompt.
- Update this file immediately after each meaningful test/build run.

# Frontend Backend Map

Updated: 2026-07-18

| Surface | Backend path | Status |
|---|---|---|
| Customer list/create | `GET/POST /api/customers` | WIRED |
| Document list | `GET /api/documents` | WIRED |
| Manual note | `POST /api/documents/manual` | WIRED |
| Audio browse/drop | `POST /api/transcribe` | WIRED |
| Microphone recording | MediaRecorder -> WebM -> WAV -> `/api/transcribe` | WIRED |
| Image/PDF browse/drop | `POST /api/ocr` | WIRED |
| Camera file selection | `capture=environment` -> `/api/ocr` | WIRED |
| Task list/complete | `GET /api/tasks`, complete endpoint | WIRED |
| Dashboard metrics/health detail | No aggregation endpoint | SAMPLE DATA |
| ASR/OCR review corrections/finalize/export | Backend routes exist | UI PARTIAL/LOCAL |
| Compare and clinical issue decisions | Backend routes exist | UI PARTIAL/LOCAL |
| Batch | No batch endpoint | MISSING |
| History export | No endpoint | MISSING |
| Settings/model management | No endpoint | MISSING |

Browser evidence:

- Real OCR upload completed and appeared in Documents.
- `Real Integration Clinical Note` appeared exactly once in Documents.
- Fresh post-repair browser checks produced no new console errors.

# Frontend Backend Map

Source scan result: no frontend API client or backend requests were found in `Frontend/src`.

| Page | Component/button | Expected action | API request | Actual response | Frontend result | Status | Error |
|---|---|---|---|---|---|---|---|
| Dashboard | Refresh | Reload backend dashboard stats | `GET /api/dashboard` or composed endpoints | None | No handler | MISSING | Mock data remains |
| Dashboard | New Processing | Navigate | N/A | N/A | Navigates locally | VERIFIED_LOCAL |  |
| Customers | New Customer | Open/create customer | `POST /api/customers` | None | No handler | MISSING | Button has no API action |
| Customers | Search | Search backend customers | `GET /api/customers?search=` | None | Filters embedded array | MISSING | Mock data only |
| Customers | View/Open row | Load customer profile | `GET /api/customers/{id}` | None | Navigates to hardcoded workspace | MISSING | No selected customer |
| Customer Workspace | Export | Export customer report | `GET /api/customers/{id}/export/report` | None | No handler | MISSING |  |
| Customer Workspace | Document open | Open ASR/OCR review | `GET /api/documents/{id}` | None | Navigates local screen | MISSING | Uses sample docs |
| New Processing | Record Audio | Browser recording | MediaRecorder + `POST /api/transcribe` | None | Toggles local state | MISSING | No audio capture/upload |
| New Processing | Browse Files audio | Upload audio | `POST /api/transcribe` | None | No file chooser | MISSING |  |
| New Processing | Start Transcription | Transcribe selected audio | `POST /api/transcribe` | None | No handler | MISSING |  |
| New Processing | Browse/Open Scanner | Upload image/PDF/camera | `POST /api/ocr` | None | No handler | MISSING |  |
| New Processing | Start OCR Processing | Run OCR | `POST /api/ocr` | None | No handler | MISSING |  |
| New Processing | Save Note | Save manual note | `POST /api/documents/manual` | None | No handler | MISSING |  |
| ASR Review | Accept Transcript | Save/finalize correction | `PATCH /api/documents/{id}/text`, finalize | None | No API action | MISSING |  |
| ASR Review | Export | Export TXT/JSON/SRT/VTT | export routes | None | No API action | MISSING |  |
| OCR Review | Accept OCR Output | Save/finalize OCR | correction/finalize routes | None | No API action | MISSING |  |
| OCR Review | Export | Export OCR doc | export routes | None | No API action | MISSING |  |
| Compare | Use ASR/OCR/Flag | Resolve mismatch decisions | issue/task/document routes | None | Local state only | MISSING |  |
| Compare | Export Report | Export comparison | Missing/unspecified | None | No API action | MISSING |  |
| Clinical Review | Resolve/Accept/Ignore | Issue decisions | `POST /api/issues/{id}/decision` | None | Local set only | MISSING |  |
| Clinical Review | Finalize Review | Finalize review | Missing/unspecified | None | Disabled/local only | MISSING |  |
| Batch | Add/Browse/Retry | Batch uploads/jobs | Missing batch endpoint | None | Mock queue | MISSING |  |
| Tasks | New/Edit/Complete | Task API | `/api/tasks` | None | Local mock only | MISSING |  |
| History | Export Log | Export audit log | Missing endpoint | None | No handler | MISSING |  |
| Settings | Save/Test/Pull Model | Settings and model actions | Missing settings routes | None | No handlers | MISSING |  |

## Screenshot Evidence

- `verification/evidence/screenshots/frontend_dashboard.png`
- `verification/evidence/logs/frontend_console.json`

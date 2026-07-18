# API Contracts

This file maps the approved frontend surface to backend endpoints. The current frontend is a single React/Vite app in `Frontend/src/app/App.tsx` with embedded sample data and no API client at baseline.

| Frontend component | User action | Existing API call | Required endpoint | Request schema | Response schema | Error behavior | Status |
|---|---|---|---|---|---|---|---|
| Sidebar | View service status | None | `GET /health` | None | `{ status, services: { database, asr, ocr, ollama } }` | Display existing online/warning/offline state when wired | IMPLEMENTED |
| DashboardScreen | Refresh dashboard | None | `GET /api/dashboard` or composed customer/document/task endpoints | Query filters optional | KPI counts, queue, reviews, activity series | Preserve existing card/table layout and show existing error state if added | NOT_STARTED |
| DashboardScreen | New Processing | Internal navigation | N/A | N/A | N/A | N/A | IMPLEMENTED |
| CustomersScreen | Search customers | Local sample filter | `GET /api/customers?search=` | Query string | Customer list matching current UI fields | Controlled API error | IMPLEMENTED |
| CustomersScreen | Add/create customer | None/internal button | `POST /api/customers` | Customer create payload | Customer response | 422 validation, duplicate warning | TESTED |
| CustomersScreen | Open customer | Internal navigation | `GET /api/customers/{customer_id}` | Path ID | Customer profile + related counts | 404/403 | IMPLEMENTED |
| CustomerWorkspaceScreen | View documents/analyses/tasks/activity | Local sample data | `GET /api/customers/{id}/documents`, `/analyses`, `/tasks`, `/activity` | Path ID | Scoped lists | 404/403 | IMPLEMENTED |
| NewProcessingScreen | Record audio | None | Browser MediaRecorder then `POST /api/transcribe` | multipart: `file`, `customer_id`, `language`, `save_document` | Unified document with segments | File/model errors surfaced without layout changes | IMPLEMENTED_API_ONLY |
| NewProcessingScreen | Upload audio | None | `POST /api/transcribe` | multipart audio | Unified document with segments | 415/413/422/model unavailable | TESTED_TEXT_FALLBACK |
| NewProcessingScreen | Scan/upload document | None | `POST /api/ocr` | multipart: `file`, `customer_id`, `language`, `preprocess`, `save_document` | Unified document with pages/blocks | 415/413/422/model unavailable | TESTED_TEXT_FALLBACK |
| NewProcessingScreen | Type manual note | None | `POST /api/documents/manual` | `{ customer_id, source_name, text, language }` | Unified manual document | 422/403 | TESTED |
| DocumentsScreen | Search/list documents | Local sample filter | `GET /api/documents` | Query filters | Document list | Controlled API error | NOT_STARTED |
| DocumentsScreen | Open document | Internal navigation | `GET /api/documents/{document_id}` | Path ID | Unified document | 404/403 | NOT_STARTED |
| ASRReviewScreen | Save transcript correction | None | `PATCH /api/documents/{document_id}/text` | `{ corrected_text, reason? }` | Updated document | 404/403/422 | NOT_STARTED |
| ASRReviewScreen | Export transcript | None | `GET /api/documents/{id}/export/{txt,json,srt,vtt,pdf}` | Path format | File/stream | 404/422 for unsupported format | NOT_STARTED |
| OCRReviewScreen | Save OCR correction | None | `PATCH /api/documents/{document_id}/ocr-blocks/{block_id}` | `{ corrected_text, reason? }` | Updated block/document | 404/403/422 | NOT_STARTED |
| OCRReviewScreen | Export OCR | None | `GET /api/documents/{id}/export/{txt,json,pdf}` | Path format | File/stream | 404/422 | NOT_STARTED |
| CompareScreen | Compare selected documents | None | `POST /api/compare` | `{ document_ids: [], customer_id? }` | Metrics and mismatches | 409 cross-customer, 422 bad input | TESTED |
| ClinicalReviewScreen | Run review | None | `POST /api/clinical-review` | `{ document_ids: [], note_type, customer_id? }` | Risk, issues, tasks, entities | 409/422/model error controlled | TESTED |
| ClinicalReviewScreen | Issue decision | None | `POST /api/issues/{issue_id}/decision` | `{ action, reason?, new_value? }` | Updated issue/audit | 404/403/422 | TESTED |
| BatchScreen | Batch processing | None | `POST /api/batch` or repeated ingest endpoints | Multipart/files + options | Job queue records | Controlled job errors | NOT_STARTED |
| TasksScreen | List/update/complete tasks | Local sample data | `GET/POST/PATCH/DELETE /api/tasks`, `POST /api/tasks/{id}/complete` | Task payloads | Task response/list | 404/403/422 | NOT_STARTED |
| HistoryScreen | View activity | Local sample data | `GET /api/activity` or customer activity endpoint | Optional filters | Audit/history list | Controlled API error | NOT_STARTED |
| SettingsScreen | Save/test settings | None | Health/settings endpoints | Settings payloads | Service status/config | Controlled API error | NOT_STARTED |

## Open Mapping Work

- Extract all concrete buttons/actions from `Frontend/src/app/App.tsx` and expand this mapping.
- Add exact response adapters once backend routes exist.

# Requirement Coverage

| Requirement ID | Feature | Expected behavior | Frontend location | Backend route/service | Database dependency | Test available | Test result | Implementation status | Evidence | Problem |
|---|---|---|---|---|---|---|---|---|---|---|
| R001 | Frontend build | Approved UI builds | `Frontend/src/app/App.tsx` | N/A | N/A | Yes | PASS | VERIFIED | `workflow_commands.json` | Chunk warning only |
| R002 | Frontend API integration | Visible actions call backend | All screens | All API routes | All | Source scan | FAIL | MISSING | `rg` found no API usage | Mock/local-state only |
| R003 | Health | Accurate service status | Sidebar | `GET /health` | DB | Yes | PASS | VERIFIED | `health.json` | ASR/OCR report unavailable |
| R004 | Customer create/list/search | Customer CRUD basics | Customers | `/api/customers` | `customers` | Yes | PASS | VERIFIED | API evidence | Invalid email accepted |
| R005 | Customer update/archive/restore | Mutate customer state | Customers | `/api/customers/{id}` | `customers`, audit | Yes | PASS | VERIFIED | API evidence | Delete not deeply audited |
| R006 | Customer duplicate code | Duplicate code rejected | Customers | `POST /api/customers` | Unique index | Yes | PASS | VERIFIED | `customer_duplicate_code.json` |  |
| R007 | Email validation | Invalid email rejected | Customers | `POST /api/customers` | `customers.email` | Yes | FAIL | FAILED | `customer_invalid_email.json` | Accepted invalid email |
| R008 | Customer data isolation | Cross-customer data cannot be fetched | Documents | `GET /api/documents/{id}` | `documents.customer_id` | Yes | FAIL | FAILED | `cross_customer_document_guess.json` | Direct guessed document access |
| R009 | Cross-customer combine | Reject mixed customer docs | Compare | `/api/documents/combine` | documents | Yes | PASS | VERIFIED | `cross_customer_combine.json` |  |
| R010 | Manual document | Create/edit/export manual text | New Processing | `/api/documents/manual` | documents | Yes | PASS | VERIFIED | API evidence | Frontend not wired |
| R011 | ASR fallback | Upload text fallback creates audio doc | New Processing | `/api/transcribe` | documents, segments | Yes | PASS | PARTIALLY_IMPLEMENTED | `asr_text_fallback.json` | Real audio unverified |
| R012 | Real ASR | Audio to text for wav/mp3/etc | New Processing | ASR service | documents, segments | No | BLOCKED | BLOCKED_BY_ENVIRONMENT | Health/model status | Runtime unavailable |
| R013 | OCR fallback | Upload text fallback creates OCR blocks | New Processing | `/api/ocr` | documents, pages, blocks | Yes | PASS | PARTIALLY_IMPLEMENTED | `ocr_text_fallback.json` | Real OCR unverified |
| R014 | Real OCR | Image/PDF to text with quality analysis | OCR Review | OCR service | pages, blocks | No | BLOCKED | BLOCKED_BY_ENVIRONMENT | Health/model status | Runtime unavailable |
| R015 | OCR correction | Correct block and persist | OCR Review | `PATCH /ocr-blocks` | blocks, documents, audit | Yes | PASS | VERIFIED | `ocr_block_correction.json` | Frontend not wired |
| R016 | Text correction | Correct document text | ASR Review | `PATCH /text` | documents, audit | Yes | PASS | VERIFIED | `document_text_correction.json` | Frontend not wired |
| R017 | Combine docs | Combine 3 same-customer docs | Compare | `/api/documents/combine` | documents | Yes | PASS | VERIFIED | `combine_same_customer.json` |  |
| R018 | Compare | WER/CER/numeric mismatch | Compare | `/api/compare` | documents | Yes | PASS | PARTIALLY_IMPLEMENTED | `compare_numeric.json` | No severity field |
| R019 | Clinical review | Missing/allergy/risk/tasks | Clinical Review | `/api/clinical-review` | analyses, issues, tasks | Yes | PASS | PARTIALLY_IMPLEMENTED | `clinical_review.json` | Limited rule set |
| R020 | Issue decision | Ignore requires reason | Clinical Review | `/api/issues/{id}/decision` | issues, audit | Yes | PASS | VERIFIED | issue evidence | Edit behavior not deeply tested |
| R021 | Task management | Create/complete task | Tasks | `/api/tasks` | tasks, audit | Yes | PASS | PARTIALLY_IMPLEMENTED | task evidence | Reopen/filter/delete unverified |
| R022 | Exports | TXT/JSON/PDF/SRT/VTT/report | Review/Customer | export routes | exports | Yes | PASS | PARTIALLY_IMPLEMENTED | export evidence | Browser downloads unverified |
| R023 | Persistence | Data survives DB reopen | All | DB | all | Yes | PASS | VERIFIED | `verify_persistence.json` | Full server restart not tested |
| R024 | Migration | Upgrade/downgrade | N/A | Alembic | schema | Yes | PASS | VERIFIED | command output | Existing DB not tested |
| R025 | Docker | Compose build/up | N/A | Dockerfiles | volumes | No | BLOCKED | BLOCKED_BY_ENVIRONMENT | docker command output | Docker unavailable |
| R026 | Ollama | Real structured model output | AI tools | `/api/ai/*` | optional | No | BLOCKED | PARTIALLY_IMPLEMENTED | Health only | Deterministic fallback only |
| R027 | Security | MIME/path/oversize/prompt tests | Upload/AI | validators | storage | Partial | FAIL | PARTIALLY_IMPLEMENTED | API/security audit | MIME/auth gaps |
| R028 | Audit/history | Events recorded | History | audit logs | audit_logs | Partial | PASS | PARTIALLY_IMPLEMENTED | persistence counts | Frontend history mock-only |

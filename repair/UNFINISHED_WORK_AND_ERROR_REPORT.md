# Unfinished Work and Error Report

Updated: 2026-07-18

## Completed

- Mega-ASR standalone and backend inference are real.
- PaddleOCR standalone and backend image OCR are real.
- Ollama `qwen3:4b` structured output and prompt-injection checks are real.
- Browse, drag/drop, camera-file selection, microphone recording, ASR upload, and OCR upload are wired.
- Upload magic-byte validation, ownership regressions, OCR quality flags, and WER/CER checks pass.
- A customer-linked audio -> ASR -> OCR -> Ollama -> risk score -> note workflow passed.

## Unfinished Or Blocked

1. Dashboard metrics, processing queue, service-health detail, Compare, Batch, History, Settings, ASR Review, and OCR Review still contain embedded demonstration data or local-only actions.
2. Caller identity is not authenticated. Customer ownership checks work when `customer_id` context is supplied, but the API does not establish trusted user/customer identity.
3. Real multi-page PDF OCR, PostgreSQL runtime, and production migration with existing data were not exercised.
4. Development `.txt` ASR/OCR fallback remains enabled by default and should be disabled in production.
5. The frontend build retains a 669.90 kB chunk-size warning.
6. The test suite retains 104 timezone-naive `datetime.utcnow()` deprecation warnings.
7. The lightweight 0.6B model does not use Mega-ASR's released LoRA/router. Full Mega-ASR remains optional because those adaptation weights target the 1.7B backbone.
8. The 0.6B backend still loads a model subprocess per request; measured standalone time is 11.30s and the backend test completed in under one minute, but it is not a persistent low-latency service.

Docker is not required and is not an unfinished item.

## Exact Current Errors And Gaps

### Frontend

- Dashboard date, totals, charts, queue, model versions, and GPU percentages are hardcoded demonstration values.
- Customer Workspace and review screens still show sample patient/document content instead of loading the selected backend record.
- A Documents-row `Open` action navigates to a review screen without passing/loading that document ID.
- ASR/OCR corrections, finalize, export, comparison decisions, clinical issue decisions, and several task actions are still local-only.
- Batch has no backend job endpoint. History export and Settings/model-management endpoints are missing.
- Audio upload copy says 500 MB while the backend enforces 100 MB.
- The real browser microphone UI is wired, and WebM conversion is tested, but a fresh live-microphone recording was not captured after the conversion repair.

### ASR

- The CPU default is Qwen3-ASR-0.6B, not the full Mega-ASR adaptation. Mega-ASR's released LoRA/router target the 1.7B backbone and cannot safely be attached to 0.6B.
- Each request starts a new Python process and reloads the model. A persistent worker is still an optimization.
- API `language` is stored on the document but is not passed into either ASR inference runner.
- Segment timestamps are synthetic estimates based on word count, not model-derived timestamps. SRT/VTT timing is therefore approximate.
- `ASR_MAX_DURATION_SECONDS` is configured but audio duration is not enforced before inference.
- The inference lock is process-local; multiple backend workers could each start a model.
- Failed inference leaves the original uploaded file in storage.

### OCR

- Explicit workspace model directories cause PaddleOCR to ignore the requested `lang`; current recognition is effectively the configured English model.
- The `preprocess` request flag is recorded but no distinct preprocessing pipeline is applied.
- Real multi-page, encrypted, rotated, skewed, blurred, low-contrast, and non-English documents are not covered by the completed real test.
- Failed OCR leaves the original uploaded file in storage.

### API, Security, And Persistence

- `save_document=false` does not prevent persistence; it only removes customer association.
- There is no authenticated user, role, or trusted customer context.
- No rate limiting, TLS termination, malware scanning, or encryption-at-rest workflow is implemented.
- SQLite is verified; PostgreSQL and migration of existing production data are not.
- Development text fallbacks are enabled by default.

### Warnings And Test Limits

- 104 `datetime.utcnow()` deprecation warnings remain.
- Vite reports a 669.90 kB main chunk.
- The strict visual comparison is limited by a resampled in-app screenshot.
- Paddle reports that `lang` is ignored with explicit model directories and warns that `ccache` is unavailable.
- Older non-authoritative repair files may still contain historical Docker/missing-model statements; the five current repair reports are authoritative.

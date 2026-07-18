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

1. Docker compose verification is blocked because Docker Desktop is not installed.
2. Mega-ASR CPU cold start is slow. The successful integrated run took about ten minutes; an earlier contention-heavy run exceeded 30 minutes. The timeout is now 3600 seconds, but GPU deployment or a persistent model service is recommended.
3. Dashboard metrics, processing queue, service-health detail, Compare, Batch, History, Settings, ASR Review, and OCR Review still contain embedded demonstration data or local-only actions.
4. Caller identity is not authenticated. Customer ownership checks work when `customer_id` context is supplied, but the API does not establish trusted user/customer identity.
5. Real multi-page PDF OCR, PostgreSQL runtime, Docker restart persistence, and production migration with existing data were not exercised.
6. Development `.txt` ASR/OCR fallback remains enabled by default and should be disabled in production.
7. The frontend build retains a 669.90 kB chunk-size warning.
8. The test suite retains 104 timezone-naive `datetime.utcnow()` deprecation warnings.


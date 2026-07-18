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

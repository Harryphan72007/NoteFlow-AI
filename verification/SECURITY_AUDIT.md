# Security Audit

## Result

Status: **FAILED**

## Critical Findings

### SEC-001: Cross-Customer Direct Record Access

- Direct document lookup by guessed ID returns another customer's document.
- Evidence: `verification/evidence/api/cross_customer_document_guess.json`
- Severity: Critical.
- Required fix: enforce ownership on direct record endpoints.

## High Findings

### SEC-002: Invalid Email Accepted

- Invalid customer email is stored.
- Evidence: `verification/evidence/api/customer_invalid_email.json`
- Severity: High.

### SEC-003: No Authentication Or Authorization Layer

- There is no user/session/role context. Customer isolation is implemented only for some operations such as combine.
- Severity: High.

### SEC-004: Upload MIME Validation Missing

- Upload routes validate extension and size, but not MIME/content signatures.
- Severity: High for clinical document ingestion.

## Medium Findings

### SEC-005: Test Fallback ASR/OCR Enabled By Default

- `.txt` fallback ingestion is useful for tests but should not be enabled in production.
- Severity: Medium.

### SEC-006: Prompt Injection Not Verified Against Real LLM

- Deterministic clinical rules are not vulnerable to prompt following, but real Ollama prompt-injection protections were not tested.
- Severity: Medium.

## Tests Run

- Missing customer name: PASS, returned 422.
- Duplicate customer code: PASS, returned 409.
- Invalid upload extension: PASS, returned 415.
- Empty OCR upload: PASS, returned 422.
- Cross-customer combine: PASS, returned 409.
- Cross-customer direct fetch: FAIL, returned 200.

## Not Run

- `../` path traversal upload filename.
- MIME mismatch with valid extension.
- Oversized upload.
- Corrupted image/PDF.
- Encrypted PDF.
- Malformed Ollama JSON.
- Full CORS browser tests.

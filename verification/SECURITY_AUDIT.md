# Security Audit

Updated: 2026-07-18

Status: **CORE REPAIRS VERIFIED; AUTH GAP REMAINS**

## Passed

- Wrong-customer document/task/issue operations are rejected when customer context is supplied.
- Invalid email returns 422.
- Cross-customer combine returns 409.
- Fake `.wav` text and fake `.png` PDF content return 415.
- Empty and unsupported uploads are rejected.
- Prompt injection could not alter the Ollama JSON schema or add fabricated diagnosis data.
- Uploaded paths are constrained to configured storage directories.

## Remaining Risk

- There is no authenticated principal or role model. `customer_id` is optional caller input, so it is not a trusted security boundary by itself.
- Development `.txt` ASR/OCR fallback should be disabled in production.
- Full CORS, oversized-upload, malware scanning, and rate-limit testing were not performed.

Tests: 12 backend tests and 35 API checks passed.

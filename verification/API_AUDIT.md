# API Audit

## Summary

Script: `verification/scripts/verify_api.py`

Result: **33 PASS / 2 FAIL / 35 total**

Evidence summary: `verification/evidence/api/summary.json`

## Passed API Areas

- `GET /health`
- Customer create, search, update, archive, restore
- Duplicate customer code rejection
- Manual document creation
- Cross-customer combine rejection
- ASR `.txt` fallback
- OCR `.txt` fallback
- Invalid extension rejection
- Empty OCR file rejection
- Document text correction
- OCR block correction
- Same-customer combination
- Compare endpoint
- Clinical review endpoint
- Issue ignore requires reason
- Issue ignore with reason
- Task create/complete
- TXT/JSON/PDF exports
- SRT/VTT for audio fallback
- Clear SRT/VTT 422 for non-audio combined document
- Customer report export

## Failed API Areas

### API-FAIL-001: Invalid Email Accepted

- Request: `POST /api/customers`
- Payload: `{ "email": "not-an-email" }`
- Expected: 422
- Actual: 200
- Evidence: `verification/evidence/api/customer_invalid_email.json`

### API-FAIL-002: Cross-Customer Document Guess Succeeds

- Request: `GET /api/documents/{customer_b_document_id}?customer_id={customer_a_id}`
- Expected: 403
- Actual: 200
- Evidence: `verification/evidence/api/cross_customer_document_guess.json`

## Missing Required Endpoints

Compared with the larger project specification:

- `POST /api/evaluation/run`
- `GET /api/evaluation/runs/{run_id}`
- `GET /api/evaluation/dashboard`
- Dedicated `/api/documents/{id}/export/txt` style endpoints exist only through generic `/export/{export_type}` route.
- No `/api/dashboard` route.
- No batch processing route.
- No explicit settings routes.

## Schema Gaps

- Customer email is plain string.
- No customer context/auth schema for direct document access.
- Comparison response lacks explicit severity/similarity score fields beyond WER/CER/diffs.
- Clinical issue response lacks explicit source document/source location/confidence fields.

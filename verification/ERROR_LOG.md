# Error Log

## ERR-001

- Severity: Critical
- Feature: Customer data isolation
- Command/request: `GET /api/documents/{customer_b_doc_id}?customer_id={customer_a_id}`
- Endpoint: `/api/documents/{document_id}`
- Expected result: 403 or equivalent ownership rejection
- Actual result: 200 with Customer B document
- HTTP status: 200
- Evidence: `verification/evidence/api/cross_customer_document_guess.json`
- Likely root cause: direct document endpoint does not enforce customer ownership context.
- Affected files: `backend/app/routes/documents.py`
- Reproduction: run `.\.venv\Scripts\python.exe verification\scripts\verify_api.py`
- Suggested fix: require authenticated/customer-scoped context on direct record routes and compare against record `customer_id`.
- Regression test required: direct Customer A request for Customer B document returns 403/404.

## ERR-002

- Severity: High
- Feature: Customer validation
- Command/request: `POST /api/customers`
- Endpoint: `/api/customers`
- Request payload: `{ "customer_code": "PT-AUDIT-EMAIL", "full_name": "Invalid Email", "email": "not-an-email" }`
- Expected result: 422
- Actual result: 200
- HTTP status: 200
- Evidence: `verification/evidence/api/customer_invalid_email.json`
- Likely root cause: schema field is `str | None` with no email validator.
- Affected files: `backend/app/schemas.py`
- Reproduction: run `.\.venv\Scripts\python.exe verification\scripts\verify_api.py`
- Suggested fix: use `EmailStr` or explicit Pydantic validator.
- Regression test required: invalid email returns 422.

## ERR-003

- Severity: High
- Feature: Frontend/backend integration
- Command/request: source scan for API usage
- Expected result: frontend contains API client calls for visible actions
- Actual result: no `fetch`, `axios`, `/api`, `MediaRecorder`, or `navigator.mediaDevices` usage found
- Evidence: `rg` frontend scan and `verification/FRONTEND_BACKEND_MAP.md`
- Likely root cause: approved UI remains a static mock.
- Affected files: `Frontend/src/app/App.tsx`
- Suggested fix: add nonvisual API adapter/state wiring.
- Regression test required: browser E2E verifies buttons call real APIs.

## ERR-004

- Severity: Medium
- Feature: Docker deployment
- Command/request: `docker --version`
- Expected result: Docker CLI available
- Actual result: command not found
- Status: BLOCKED_BY_ENVIRONMENT
- Suggested fix: run Docker verification on a machine with Docker installed.

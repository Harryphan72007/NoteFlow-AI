# Security Audit

Updated: 2026-07-18

## Verified

- `/api/auth/login` issues an HMAC-signed bearer session token for a persisted local account.
- User passwords are stored as PBKDF2 hashes; `/api/auth/register` creates additional persisted scoped users for local testing.
- API routes require authentication. A scoped token cannot access another customer's documents or customer route by forging `customer_id` in a body/query.
- Magic-byte validation, path containment, invalid email rejection, cross-customer checks, prompt-injection handling, and failed-upload cleanup remain covered.

## Scope limitations

This is a local single-tenant prototype. Broader RBAC, rate limiting, TLS termination, malware scanning, and encryption-at-rest are deferred until a multi-user/production deployment is planned. The production path would add an external identity provider or managed session store, reverse-proxy TLS, malware scanning/quarantine, encrypted storage/keys, and request throttling.

Development text fallback is disabled by default and only enabled explicitly in test/verifier environments.

Evidence: `repair/logs/phase2_auth.log`, `backend/tests/test_remaining_repairs.py`, and `repair/logs/phase9_production_gaps.log`.

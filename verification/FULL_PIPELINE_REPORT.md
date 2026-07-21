# Full Pipeline Report

Updated: 2026-07-18

## Regression gate

- Backend pytest: PASS, 19 passed, 0 warnings.
- API verifier: PASS, 35/35 checks.
- Persistence verifier: PASS; customer/document/audit rows survive reopen.
- Workflow verifier: PASS; backend pytest and frontend build pass.
- Frontend build: PASS, 2220 modules; initial application chunk 103.92 kB after vendor splitting; Recharts vendor 529.19 kB warning remains.
- Live backend smoke: `/health` returned `ok`; login returned a bearer token for `local.user`.

## Core workflow baseline

The previously captured Customers C001/C002, fever/cough/penicillin/antibiotic note, prompt-injection note, warfarin 0.5 mg versus 5 mg mismatch, combined ASR/OCR sections, TXT/JSON/PDF/SRT/VTT/customer-report exports, and persistence workflow remain covered by the existing evidence under `verification/evidence/` and the real-integration logs. The current pass preserved those paths; it did not claim a fresh model rerun where no fresh model/browser capture exists.

## Final status

High and Medium items are itemized in `repair/REMAINING_ISSUES.md` with RESOLVED, PARTIALLY RESOLVED, or STILL OPEN status and an evidence reference. Open items are primarily difficult-case corpus coverage, strict visual golden testing, single-worker/process lock hardening, live microphone permission capture, and model/runtime performance measurements.

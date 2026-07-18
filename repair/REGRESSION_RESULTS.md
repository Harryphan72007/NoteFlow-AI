# Regression Results

| Run ID | Phase | Command | Expected | Actual | Status | Evidence |
|---|---|---|---|---|---|---|
| BASE-001 | Baseline | `verification/scripts/verify_workflow.py` | Backend tests and frontend build pass | Passed | PASS | terminal output 2026-07-18 |
| BASE-002 | Baseline | `verification/scripts/verify_persistence.py` | Persistence pass | Passed | PASS | terminal output 2026-07-18 |
| BASE-003 | Baseline | `verification/scripts/verify_api.py` | Known 2 failures before repair | Failed exactly on invalid email and cross-customer direct read | EXPECTED_FAIL | terminal output 2026-07-18 |
| REPAIR-001 | Security repair | `python -m pytest backend/tests/test_security_repairs.py -q` | Ownership and validation regression tests pass | 4 passed | PASS | terminal output 2026-07-18 |
| REPAIR-002 | API audit | `python verification/scripts/verify_api.py` | 35 API checks pass | 35 passed, 0 failed | PASS | terminal output 2026-07-18 |
| REPAIR-003 | Backend regression | `python -m pytest backend/tests -q` | Full backend suite passes | 10 passed | PASS | terminal output 2026-07-18 |
| REPAIR-004 | Frontend build | `pnpm run build` via bundled pnpm | Production build succeeds | Built 2220 modules | PASS | terminal output 2026-07-18 |
| REPAIR-005 | Workflow regression | `python verification/scripts/verify_workflow.py` | Backend tests and frontend build pass | Both checks passed | PASS | terminal output 2026-07-18 |
| REPAIR-006 | Persistence regression | `python verification/scripts/verify_persistence.py` | Reopened DB retains customer/document/audit rows | Passed | PASS | terminal output 2026-07-18 |
| REPAIR-007 | Frontend API source scan | `rg "fetch\\(|listCustomers|createManualDocument|completeTask|/api" Frontend/src Frontend/vite.config.ts -n` | Frontend contains API adapter and wired use sites | API client, proxy, and App use sites found | PASS | terminal output 2026-07-18 |
| REAL-BASE-001 | Phase 0 baseline | `python verification/scripts/verify_workflow.py` | Backend tests and frontend build pass before real model integration | Backend 10 passed; frontend build passed | PASS | terminal output 2026-07-18 |
| REAL-ASR-001 | Phase 1 standalone Mega-ASR | `python infer.py --audio assets/example/F01_22GC010K_STR.wav --ckpt_dir ckpt/Mega-ASR --routing false --device_map cpu` via NoteFlow venv Python | Real audio transcription succeeds before NoteFlow integration | Failed before model load: `ModuleNotFoundError: No module named 'torch'` | BLOCKED | `repair/PHASE_0_1_REAL_INTEGRATION_STATUS.md` |

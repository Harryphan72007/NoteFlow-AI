# Regression Results

Updated: 2026-07-18

| Area | Actual result | Status |
|---|---|---|
| Backend pytest | 19 passed, 0 warnings | PASS |
| API audit | 35 passed, 0 failed | PASS |
| Persistence | Rows survive database reopen | PASS |
| Frontend build | 2220 modules; app chunk 103.92 kB; chart vendor warning remains | PASS_WITH_WARNING |
| Workflow verifier | pytest and frontend build pass | PASS |
| Live health/auth smoke | `/health` ok; login bearer token returned | PASS |
| Browser smoke | Live dashboard/documents/history; explicit Batch/Settings scope; no console errors | PASS_WITH_SCOPE |
| ASR/OCR/Ollama baseline | Preserved from prior ground-truth evidence | PASS |
| Local execution | venv + pnpm documented and exercised | PASS |

Evidence is in `repair/logs/phase*.log`, `verification/FULL_PIPELINE_REPORT.md`, and `verification/evidence`.

# Regression Results

Updated: 2026-07-18

| Area | Actual result | Status |
|---|---|---|
| Python compilation | `backend` and verification scripts compiled | PASS |
| Backend pytest | 15 passed, 104 warnings | PASS |
| API audit | 35 passed, 0 failed | PASS |
| Persistence | customer/document/audit rows survived reopen | PASS |
| Frontend production build | 2220 modules, build completed | PASS |
| Combined workflow verifier | pytest and frontend build both passed | PASS |
| Standalone Mega-ASR | non-empty real transcript | PASS |
| Backend Mega-ASR | HTTP 200, real metadata and segment | PASS |
| Lightweight ASR standalone | Qwen3-ASR-0.6B; load 3.48s, infer 7.82s, total 11.30s | PASS |
| Lightweight ASR backend | HTTP 200; correct transcript; LoRA/router honestly disabled | PASS |
| Lightweight full E2E rerun | ASR -> OCR -> Ollama -> risk red/50 -> note | PASS |
| Standalone/backend OCR | expected medication/allergy text and persisted blocks | PASS |
| OCR accuracy | WER 0.000000, CER 0.000000 | PASS |
| Ollama structured JSON | strict schema with `qwen3:4b` | PASS |
| Ollama model-state health | installed/loaded state reported separately | PASS |
| Ollama CPU latency | 13.75s first request after restart; 8.85s resident-model follow-up | PASS_WITH_LATENCY |
| Prompt injection | injected field/diagnosis rejected | PASS |
| MIME mismatch | fake WAV and fake PNG rejected with 415 | PASS |
| Browser WebM conversion | mono 16 kHz WAV output | PASS |
| Real E2E | ASR -> OCR -> Ollama -> risk 50/red -> note | PASS |
| Frontend note visibility | `Real Integration Clinical Note` found once | PASS |
| Browser upload retest | real OCR + ASR HTTP 200; persisted; no console errors | PASS |
| Visual structure | 1280x720 before/after; mean pixel delta 4.5814/255 | PASS_WITH_CAPTURE_LIMITATION |
| Docker compose | Removed from acceptance criteria | NOT_REQUIRED |

Evidence is in `repair/logs/phase*.log` and `verification/evidence`.

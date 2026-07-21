# Remaining Issues

Updated: 2026-07-18 after the Docker-removal and repair pass.

## High

- **Trusted identity — RESOLVED:** bearer sessions are issued by `/api/auth/login`, persisted users use PBKDF2 password hashes, and scoped-token forgery is covered by `backend/tests/test_remaining_repairs.py` and `repair/logs/phase2_auth.log`.
- **Static secondary UI — PARTIALLY RESOLVED:** Dashboard, Documents, History, Compare, Clinical Review, and AI controls now call backend routes. Batch and Settings are explicitly marked not yet implemented; no fake results are shown there. See `repair/logs/phase3_frontend_wiring.log`.
- **Review record selection — RESOLVED:** Documents Open stores the selected backend document ID and ASR/OCR Review loads `/api/documents/{id}`. See `repair/logs/phase3_frontend_wiring.log`.
- **Timestamp accuracy — STILL OPEN, DOCUMENTED:** this model path does not expose verified model timestamps; API metadata and SRT/VTT now state `timestamp_source=estimated`.
- **Persistence contract — RESOLVED:** `save_document=false` returns without a document row; regression test and evidence are in `repair/logs/phase1_data_integrity.log`.
- **Frontend AI integration — PARTIALLY RESOLVED:** client functions and visible summarize, key-points, format-note, and clinical-review actions are wired with loading/error/result display. A fresh Ollama browser click-through was not captured in this pass.

## Medium

- **OCR difficult-case corpus — STILL OPEN:** preprocessing, encrypted-PDF rejection, and English-only language reporting are implemented, but a fresh real multi-page/rotated/skewed/blurred/non-English corpus run is not captured.
- **PostgreSQL and production migration — STILL OPEN:** SQLite/Alembic are verified; PostgreSQL was not runtime-tested because it is not the planned local prototype target.
- **Development text fallbacks — RESOLVED:** ASR/OCR text fallback defaults are now off and require an explicit environment flag.
- **Frontend bundle warning — PARTIALLY RESOLVED:** the initial application chunk fell from 669.90 kB to 103.92 kB via vendor splitting; the Recharts vendor chunk remains 529.19 kB.
- **Timezone warnings — RESOLVED:** all backend `datetime.utcnow()` calls were replaced; pytest reports zero warnings.
- **Visual screenshot comparison — STILL OPEN:** browser evidence is captured, but there is no strict pixel-golden suite.
- **ASR model reload — PARTIALLY RESOLVED:** a persistent 0.6B worker path is implemented, but fresh real before/after latency numbers were not captured.
- **0.6B adaptation limitation — RESOLVED/DOCUMENTED:** health reports that the 1.7B-only LoRA/router is not attached to the 0.6B CPU model.
- **ASR/OCR language and preprocessing — PARTIALLY RESOLVED:** ASR language is passed to the small runner; OCR explicitly reports English-only support and applies grayscale/contrast/denoise/sharpen preprocessing.
- **Failed-upload cleanup — RESOLVED:** failed ASR/OCR inference unlinks the stored upload; regression coverage is in `test_remaining_repairs.py`.
- **Audio-size copy mismatch — RESOLVED:** UI and backend both use 100 MB.
- **Multi-worker ASR lock — STILL OPEN:** lock remains process-local; the supported local run is a single Uvicorn worker.
- **Live microphone recapture — STILL OPEN:** prior conversion wiring remains intact, but device-permission capture was not freshly recorded in this pass.
- **CPU Ollama latency — STILL OPEN:** warm generation remains CPU-bound; this pass did not change model generation performance.
- **Upload progress — PARTIALLY RESOLVED:** stage text now shows uploading/transcribing/extracting text/done, but uploads remain synchronous.

Container support was removed on 2026-07-18; the project runs directly via venv + pnpm.

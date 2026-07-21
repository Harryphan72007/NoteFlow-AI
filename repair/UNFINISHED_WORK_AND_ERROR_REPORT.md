# Unfinished Work and Error Report

Updated: 2026-07-18

## Verified baseline

- Mega-ASR/Qwen3-ASR, PaddleOCR, and Ollama qwen3:4b real paths remain intact.
- Browse/drop/camera/microphone upload wiring, magic-byte validation, ownership checks, OCR flags, and WER/CER checks remain covered by existing evidence.
- Backend pytest, API, persistence, workflow, and frontend build gates pass after the repair pass.

## Current open items

See `repair/REMAINING_ISSUES.md` for the per-item High/Medium status. Open work is limited to difficult-case OCR corpus capture, strict visual golden testing, cross-process ASR locking, fresh microphone permission capture, fresh worker/model latency measurement, and production-only infrastructure decisions.

## Completed repair highlights

- Authenticated bearer sessions and customer-scoped ownership checks.
- True non-persistent `save_document=false` behavior and failed-inference upload cleanup.
- Backend-backed dashboard/history/compare/review wiring; Batch and Settings explicitly say not yet implemented.
- Opt-in text fallback, timezone-aware timestamps, duration enforcement, language/preprocessing changes, and estimated timestamp labeling.

Container support was removed on 2026-07-18; the project runs directly via venv + pnpm.

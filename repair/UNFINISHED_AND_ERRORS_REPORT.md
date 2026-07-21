# Unfinished Work and Error Report

Updated: 2026-07-18

## Verified baseline

- Mega-ASR/Qwen3-ASR, PaddleOCR, and Ollama qwen3:4b real paths remain intact.
- Browse/drop/camera/microphone upload wiring, magic-byte validation, ownership checks, OCR flags, and WER/CER checks remain covered by the existing verification evidence.
- Backend pytest, API, persistence, workflow, and frontend build gates pass after the repair pass.

## Current open items

See `repair/REMAINING_ISSUES.md` for the per-item High/Medium status. The remaining open work is explicitly limited to difficult-case OCR corpus capture, strict visual golden testing, cross-process ASR locking, fresh microphone permission capture, fresh worker/model latency measurement, and production-only infrastructure decisions.

## Scope

Container support was removed on 2026-07-18; the project runs directly via venv + pnpm.

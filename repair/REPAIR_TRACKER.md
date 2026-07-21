# Repair Tracker

Updated: 2026-07-18

| ID | Repair | Status | Evidence |
|---|---|---|---|
| ERR-001 | Enforce customer context on direct document/task/issue operations | VERIFIED | 15 backend tests; 35 API checks |
| ERR-002 | Reject invalid customer email | VERIFIED | 422 regression test |
| ERR-003 | Wire live customer/document/task/manual-note frontend paths | VERIFIED | Build and browser checks |
| MF-ASR | Install weights/runtime and connect real Mega-ASR | VERIFIED | Standalone and backend real transcripts |
| ASR-CPU | Default to official Qwen3-ASR-0.6B for normal CPU use | VERIFIED | 11.30s standalone; backend HTTP 200 |
| MF-OCR | Install PaddleOCR and persist real pages/blocks | VERIFIED | Real image OCR, WER/CER 0 |
| MF-OLLAMA | Replace deterministic AI endpoint fallbacks with Ollama structured JSON | VERIFIED | `qwen3:4b` structured/adversarial tests; installed/loaded health |
| OLLAMA-WARM | Keep Ollama resident between related AI requests | VERIFIED | `30m` keep-alive; 13.75s first and 8.85s warm request |
| MIME-001 | Validate extension and magic bytes before storage | VERIFIED | Mismatched WAV/PNG tests return 415 |
| AUDIO-001 | Decode browser WebM/Opus for Mega-ASR | VERIFIED | WebM -> mono 16 kHz WAV conversion test |
| FE-UPLOAD | File browse, drag/drop, camera selection, and recording | VERIFIED | Browser upload and production build |
| E2E-REAL | Customer-linked real multimodal workflow | VERIFIED | `REAL_END_TO_END_WORKFLOW=PASS` |
| UI-SECONDARY | Replace all remaining embedded dashboard/review/batch/settings data | PARTIAL | Live screens wired; Batch/Settings explicitly deferred; see `repair/REMAINING_ISSUES.md` |
| ASR-TIME | Replace estimated ASR timestamps with model/aligner timestamps | DOCUMENTED_OPEN | API and exports label timestamps as estimated |
| ASR-LANG | Pass requested language into inference | VERIFIED | Small runner receives language |
| OCR-LANG | Load language-compatible recognition models | DOCUMENTED_LIMIT | English-only support is reported explicitly |
| SAVE-FLAG | Make `save_document=false` truly non-persistent | VERIFIED | Regression test and phase1 log |
| UI-OPEN | Load selected backend document in review screens | VERIFIED | Selected ID loads backend document |
| UI-AI | Connect existing frontend actions to `/api/ai/*` | PARTIAL | Client/actions wired; fresh Ollama browser result capture open |
| ASR-WORKER | Keep lightweight model resident between requests | IMPLEMENTED_UNMEASURED | Persistent worker path added; fresh latency capture open |
| LOCAL-001 | Container deployment | RESOLVED | Container support was removed on 2026-07-18; local venv + pnpm execution is documented |

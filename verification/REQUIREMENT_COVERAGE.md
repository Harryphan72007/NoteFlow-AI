# Requirement Coverage

Updated: 2026-07-18

| Area | Status | Current evidence or gap |
|---|---|---|
| Frontend build | VERIFIED | 2220 modules |
| Core frontend API wiring | VERIFIED | customer/document/task/manual note/uploads |
| Customer validation/isolation | VERIFIED_WITH_LIMIT | tests pass when customer context is supplied; no trusted auth principal |
| Real ASR | VERIFIED | Qwen3-ASR-0.6B CPU default; full Mega-ASR 1.7B optional |
| Real OCR | VERIFIED | PaddleOCR image path, blocks, confidence, WER/CER 0 |
| Ollama structured JSON | VERIFIED | qwen3:4b plus prompt-injection test |
| MIME/content validation | VERIFIED | mismatched content rejected |
| Browser recording conversion | VERIFIED | WebM/Opus to mono 16 kHz WAV |
| Full clinical workflow | VERIFIED | ASR -> OCR -> Ollama -> risk -> visible note |
| Dashboard live metrics | VERIFIED | `/api/dashboard` and browser smoke |
| Review/Compare actions | PARTIAL | selected review/compare/clinical actions call backend; some correction/export UI remains open |
| Batch processing | EXPLICITLY DEFERRED | UI states not yet implemented; no fake results |
| History/settings management | PARTIAL | history retrieval/export wired; settings editing deferred |
| Authentication/authorization | VERIFIED | signed session token and scoped ownership regression |
| Multi-page PDF corpus | UNVERIFIED | real image OCR tested |
| PostgreSQL production runtime | UNVERIFIED | SQLite verified |
| Local execution | VERIFIED | venv + pnpm commands |

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
| Dashboard live metrics | PARTIAL | demonstration values remain |
| Review/Compare actions | PARTIAL | backend exists; frontend actions remain local in places |
| Batch processing | MISSING | no batch endpoint |
| History/settings management | MISSING | no complete backend routes |
| Authentication/authorization | MISSING | caller-supplied customer context only |
| Multi-page PDF corpus | UNVERIFIED | real image OCR tested |
| PostgreSQL production runtime | UNVERIFIED | SQLite verified |
| Docker | NOT_REQUIRED | normal local execution selected |

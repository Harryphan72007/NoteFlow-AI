# Test Results

Updated: 2026-07-18

| Test | Result |
|---|---|
| Python compile | PASS |
| Backend pytest | PASS: 12, with 104 deprecation warnings |
| API audit | PASS: 35/35 |
| Persistence | PASS |
| Frontend production build | PASS: 2220 modules |
| Qwen3-ASR-0.6B standalone | PASS: correct transcript, 11.30s total |
| Qwen3-ASR-0.6B backend | PASS: HTTP 200, real inference metadata |
| Qwen3-ASR-0.6B full E2E | PASS: OCR, Ollama, risk red/50, note |
| Full Mega-ASR-1.7B | PASS but too slow for default CPU use |
| Real PaddleOCR | PASS |
| OCR WER/CER | PASS: 0/0 |
| Ollama structured/adversarial | PASS |
| WebM audio conversion | PASS |
| Docker | NOT_REQUIRED |

Warnings still open:

- 104 timezone-naive `datetime.utcnow()` deprecation warnings.
- Frontend main bundle is 669.90 kB and triggers Vite's chunk warning.
- A persistent ASR worker would avoid reloading the 0.6B checkpoint for every request.

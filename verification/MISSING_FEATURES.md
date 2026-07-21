# Missing Features

Updated: 2026-07-18

| Feature | Current state | Severity |
|---|---|---|
| Trusted auth/session context | Not implemented; ownership context is caller-supplied | High |
| Live dashboard metrics/health/queue | Embedded demonstration values remain | High |
| Compare/review completion and exports | Several visible actions remain local-only | High |
| Batch processing API/UI | Demonstration queue only | High |
| History export and settings/model management | No backend endpoints/wiring | Medium |
| Persistent preloaded ASR service | The fast 0.6B subprocess still reloads per request | Medium |
| Real multi-page PDF test corpus | Not exercised | Medium |
| PostgreSQL runtime and production-data migration | Not exercised | Medium |
| Strict pixel-golden browser suite | Current screenshot is resampled | Low |

Real ASR, OCR, Ollama, MIME validation, browser recording conversion, and core upload flows are no longer missing.
Container deployment was removed on 2026-07-18; local venv + pnpm execution is the supported mode.

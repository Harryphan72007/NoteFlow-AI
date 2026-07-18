# Remaining Issues

Updated: 2026-07-18

## High

- **Trusted identity:** customer scoping is request-supplied rather than derived from authentication/authorization.
- **Static secondary UI:** dashboard figures/service versions/queue, Compare, Batch, History, Settings, and review screens still contain sample data or local-only actions.

## Medium

- Real multi-page/encrypted/rotated PDF OCR was not exercised end to end.
- PostgreSQL and production migration with existing records were not runtime-tested.
- Development text fallbacks should be disabled in production.
- Frontend bundle warning: main JS is 669.90 kB after minification.
- 104 `datetime.utcnow()` deprecation warnings remain.
- Visual screenshot comparison is structurally useful but the in-app 1280x720 capture is resampled; it is not a strict pixel-golden test.
- Qwen3-ASR-0.6B reloads per request; a persistent worker would reduce repeated startup latency.
- The lightweight model is official Qwen3-ASR but does not include Mega-ASR's 1.7B-specific LoRA/router robustness adaptation.

Docker is intentionally not used and is not a remaining issue.

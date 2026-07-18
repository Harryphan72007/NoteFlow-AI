# Remaining Issues

Updated: 2026-07-18

## High

- **Trusted identity:** customer scoping is request-supplied rather than derived from authentication/authorization.
- **Static secondary UI:** dashboard figures/service versions/queue, Compare, Batch, History, Settings, and review screens still contain sample data or local-only actions.
- **Review record selection:** opening a document does not load its actual backend content into ASR/OCR review.
- **Timestamp accuracy:** ASR segment/SRT/VTT times are estimated rather than model-derived.
- **Persistence contract:** `save_document=false` still writes a document.

## Medium

- Real multi-page/encrypted/rotated PDF OCR was not exercised end to end.
- PostgreSQL and production migration with existing records were not runtime-tested.
- Development text fallbacks should be disabled in production.
- Frontend bundle warning: main JS is 669.90 kB after minification.
- 104 `datetime.utcnow()` deprecation warnings remain.
- Visual screenshot comparison is structurally useful but the in-app 1280x720 capture is resampled; it is not a strict pixel-golden test.
- Qwen3-ASR-0.6B reloads per request; a persistent worker would reduce repeated startup latency.
- The lightweight model is official Qwen3-ASR but does not include Mega-ASR's 1.7B-specific LoRA/router robustness adaptation.
- ASR language selection is not passed to inference; OCR language is effectively fixed by the local English model directories.
- OCR `preprocess` and ASR maximum-duration settings are recorded/configured but not enforced as behaviors.
- Uploads remain on disk when inference fails.
- The UI advertises 500 MB audio while the backend limit is 100 MB.
- The in-process ASR lock does not coordinate multiple server workers.
- A post-repair live microphone capture still needs human/device permission verification.

Docker is intentionally not used and is not a remaining issue.

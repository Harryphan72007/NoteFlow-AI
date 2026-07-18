# Remaining Issues

Updated: 2026-07-18

## Blocked

- **Docker:** Docker Desktop/CLI is not installed, so compose build, health, and restart persistence remain untested.

## High

- **CPU ASR latency:** cold-start inference is roughly ten minutes in the successful integrated run and exceeded 30 minutes under contention. Use a GPU or persistent preloaded Mega-ASR worker for practical use.
- **Trusted identity:** customer scoping is request-supplied rather than derived from authentication/authorization.
- **Static secondary UI:** dashboard figures/service versions/queue, Compare, Batch, History, Settings, and review screens still contain sample data or local-only actions.

## Medium

- Real multi-page/encrypted/rotated PDF OCR was not exercised end to end.
- PostgreSQL and production migration with existing records were not runtime-tested.
- Development text fallbacks should be disabled in production.
- Frontend bundle warning: main JS is 669.90 kB after minification.
- 104 `datetime.utcnow()` deprecation warnings remain.
- Visual screenshot comparison is structurally useful but the in-app 1280x720 capture is resampled; it is not a strict pixel-golden test.

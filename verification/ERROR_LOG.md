# Error Log

Updated: 2026-07-18

## Resolved

- **ERR-001 Cross-customer access:** fixed and regression-tested.
- **ERR-002 Invalid email accepted:** fixed; now 422.
- **ERR-003 Frontend core API paths missing:** customer/document/task/manual-note and real processing paths wired.
- **ERR-005 Mega-ASR runtime missing:** dedicated environment and weights installed; real inference passed.
- **ERR-006 PaddleOCR missing/cache errors:** dependencies and workspace-local models configured; real inference passed.
- **ERR-007 Ollama fallback-only:** `qwen3:4b` structured client verified.
- **ERR-008 Browser WebM decode failure:** `imageio-ffmpeg` transcodes to mono 16 kHz WAV; conversion passed.
- **ERR-009 Numba cache permission:** cache redirected to `data/models/numba_cache`; import and full E2E passed.
- **ERR-010 30-minute ASR timeout under contention:** default raised to 3600 seconds; successful integrated run completed.

## Open

- **ERR-004 Docker unavailable:** BLOCKED; Docker Desktop/CLI absent.
- **ERR-011 Static secondary UI:** dashboard/review/compare/batch/history/settings are not fully API-backed.
- **ERR-012 No trusted authentication context:** ownership checks depend on caller-supplied customer context.
- **ERR-013 CPU latency:** subprocess model reload remains slow.

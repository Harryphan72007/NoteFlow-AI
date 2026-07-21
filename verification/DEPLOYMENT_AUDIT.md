# Deployment Audit

Updated: 2026-07-18

## Normal Local Execution

| Check | Result |
|---|---|
| Backend dependencies | PASS |
| Backend tests | PASS: 12 |
| Frontend dependencies/build | PASS: 2220 modules |
| Database migrations | PASS: upgrade/downgrade |
| Health endpoint | PASS |
| Qwen3-ASR-0.6B CPU | PASS: 11.30s standalone |
| PaddleOCR | PASS |
| Ollama qwen3:4b | PASS |

Container deployment is not supported. The project runs directly through the documented Python virtual environment and pnpm commands.

## Remaining Deployment Risks

- ASR still starts a subprocess and reloads the 0.6B model per request.
- PostgreSQL runtime and migration of an existing production database were not tested.
- Development text fallbacks should be disabled for production use.
- Authentication, rate limiting, and service supervision are not implemented.

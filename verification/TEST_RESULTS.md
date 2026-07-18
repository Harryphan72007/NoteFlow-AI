# Test Results

| Test | Command | Result | Evidence |
|---|---|---|---|
| Backend pytest | `.\.venv\Scripts\python.exe -m pytest backend\tests -q` | PASS: 6 passed, 60 warnings | `verification/evidence/test-results/workflow_commands.json` |
| Frontend build | `pnpm run build` | PASS: Vite built 2219 modules | `verification/evidence/test-results/workflow_commands.json` |
| API audit | `.\.venv\Scripts\python.exe verification\scripts\verify_api.py` | FAIL: 33 passed, 2 failed | `verification/evidence/api/summary.json` |
| Persistence | `.\.venv\Scripts\python.exe verification\scripts\verify_persistence.py` | PASS | `verification/evidence/database/verify_persistence.json` |
| Alembic upgrade | `alembic upgrade head` | PASS | terminal output |
| Alembic downgrade | `alembic downgrade base` | PASS | terminal output |
| Frontend screenshot | Browser to `http://localhost:5173/` | PASS: rendered dashboard, 0 console warnings/errors | `verification/evidence/screenshots/frontend_dashboard.png`, `verification/evidence/logs/frontend_console.json` |
| Docker | `docker --version` | BLOCKED: command not found | terminal output |

## Warnings

- SQLAlchemy/Python deprecation warnings for `datetime.utcnow()`.
- Frontend build warns about chunks larger than 500 kB.
- pnpm warns that the `pnpm` field in `package.json` is ignored.

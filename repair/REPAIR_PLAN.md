# Repair Plan

Source of truth: `verification/` reports and evidence.

## Baseline

The previous audit showed:

- Backend pytest passed.
- Frontend build passed.
- API audit failed with 2 cases: invalid email accepted and cross-customer direct document read.
- Persistence passed.
- Real ASR/OCR/Ollama and Docker were blocked by environment/runtime availability.

## Ordered Plan

1. P0 security: enforce customer context/ownership on direct customer-owned routes.
2. P1 validation: reject invalid emails and add focused schema constraints.
3. P0 frontend/backend connection: add a central API client and wire a minimal set of existing UI actions without visual redesign.
4. Rerun baseline and repair-specific regressions.
5. Re-run verification scripts and update remaining issues honestly.

## Explicit Environment Limits

- Real Mega-ASR/Qwen3-ASR model runtime is not present in this workspace.
- Real PaddleOCR runtime is not present in this workspace.
- Docker is not available on PATH.
- Full real-model and Docker acceptance criteria can only be marked `BLOCKED`, not `VERIFIED`, until those dependencies exist.

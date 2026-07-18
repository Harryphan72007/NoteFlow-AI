# Unfinished Work and Error Report

Generated: 2026-07-18

## Important Clarification

Mega-ASR/Qwen3-ASR and real OCR are not present or usable in this workspace. The current backend contains fallback behavior and API scaffolding, but real model inference was not verified and should not be treated as complete.

## Fixed and Verified

| Item | Status | Evidence |
|---|---|---|
| Cross-customer direct document access | VERIFIED | `pytest backend/tests -q` passed; `verification/scripts/verify_api.py` passed 35/35 |
| Invalid email accepted by customer API | VERIFIED | Invalid email now returns validation error; API audit passed |
| Partial frontend/backend connection | FIXED/PARTIAL | Frontend build passed; API client and selected handlers are wired |

## Not Finished / Blocked

| Item | Severity | Status | What is missing | Why unfinished |
|---|---|---|---|---|
| Real Mega-ASR / Qwen3-ASR inference | Critical | BLOCKED | Model weights/runtime, actual audio transcription pipeline, real audio smoke tests | Required model/runtime is not in the workspace |
| Real OCR inference | Critical | BLOCKED | PaddleOCR/image/PDF pipeline, real OCR smoke tests | Required OCR runtime/dependencies are not in the workspace |
| Ollama structured JSON | High | BLOCKED | Local Ollama calls, schema-enforced extraction, repair/retry loop, adversarial tests | Local Ollama/model availability was not confirmed |
| Docker verification | Medium | BLOCKED | `docker build`, `docker compose up`, container persistence checks | Docker CLI was not available on PATH |
| Browser microphone recording | High | NOT DONE | `MediaRecorder`, microphone permission handling, upload-to-ASR flow | Frontend remains partially wired only |
| File upload from UI | High | NOT DONE | Hidden file inputs, selected file state, multipart upload to `/api/transcribe` and `/api/ocr` | Existing Browse/Drop controls are still mostly UI-only |
| OCR quality analysis | High | NOT DONE | Blur/skew/contrast detection, warnings in OCR review | Needs image processing pipeline |
| MIME/content validation | High | PARTIAL | True MIME sniffing/corrupt file rejection | Current validation is not broad enough |
| Evaluation dashboard | Medium | NOT DONE | CER/WER/safety metrics UI and backend routes | Not implemented |
| Medical OCR evaluation harness | Medium | NOT DONE | Test dataset, metrics, benchmark reports | Not implemented |
| Prompt injection regression tests | High | NOT DONE | Real LLM adversarial tests for OCR/ASR text | Depends on real LLM path |
| Visual regression suite | Medium | PARTIAL | Multi-route screenshots and breakpoint checks | Only limited screenshot/build/source checks were done |
| Full frontend API coverage | High | PARTIAL | All buttons/forms/views backed by API | Only customers/documents/tasks loading, manual note save, new customer creation, and task completion were wired |

## Current Error/Gap Summary

1. The app does not include working Mega-ASR model inference.
2. The app does not include working PaddleOCR/real OCR inference.
3. Audio upload, browser recording, scan, PDF/image upload controls are not fully functional from the frontend.
4. Ollama-backed clinical/AI structured output is not proven with a real local model.
5. Docker deployment cannot be verified in the current environment.
6. Frontend is only partially connected to the backend.
7. Several safety/quality features are still missing: MIME sniffing, OCR quality checks, prompt injection tests, evaluation metrics, and broad visual regression.

## Tests That Currently Pass

| Command | Result |
|---|---|
| `python -m pytest backend/tests -q` | 10 passed |
| `python verification/scripts/verify_api.py` | 35 passed, 0 failed |
| `python verification/scripts/verify_persistence.py` | passed |
| `python verification/scripts/verify_workflow.py` | backend tests and frontend build passed |
| Frontend production build | passed |


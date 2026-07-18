# Missing Features

| Feature | Expected behavior | Current implementation | Missing part | Affected files/endpoints | Severity | Recommended fix | Dependency |
|---|---|---|---|---|---|---|---|
| Frontend API wiring | Visible UI actions call backend and display persisted results | UI uses embedded arrays/local state | API client, state adapters, form submissions, upload controls | `Frontend/src/app/App.tsx` | Critical | Add nonvisual API layer and wire handlers without UI redesign | Backend API |
| Browser audio recording | Record microphone audio and upload | Button toggles local `isRecording` only | MediaRecorder and upload flow | New Processing screen | High | Add recording logic and permission handling | Browser APIs |
| File upload controls | Browse/select/upload audio/image/PDF | Buttons have no file input handler | File chooser and multipart upload | New Processing screen | High | Add hidden file inputs/state/API calls | Backend `/transcribe`, `/ocr` |
| Real ASR | Process wav/mp3/m4a/flac/ogg/webm | `.txt` fallback only; real files return 503 | Model runtime and inference lock | `/api/transcribe` | Critical | Integrate Mega-ASR/Qwen3-ASR service | Model weights/runtime |
| Real OCR | Process images/PDF with OCR | `.txt` fallback only; real files return 503 | PaddleOCR/PDF/image pipeline | `/api/ocr` | Critical | Integrate PaddleOCR, image preprocessing, PDF conversion | PaddleOCR/PyMuPDF/OpenCV |
| OCR quality analysis | Blur/skew/low contrast warnings | Not implemented | Image quality metrics | OCR service | High | Add image validators and warnings | OpenCV/Pillow |
| Evaluation dashboard | CER/WER and safety metrics dashboard | Not implemented | Routes, data model, UI wiring | `/api/evaluation/*` | Medium | Add evaluation harness | Synthetic dataset |
| Customer-scoped auth/context | Prevent guessed-ID access | Direct routes return records by ID | Ownership enforcement | document/task/analysis/export routes | Critical | Require authenticated/customer context and enforce FK | Auth/session design |
| MIME validation | Reject MIME mismatch/corrupt files | Extension and empty-size checks only | MIME sniffing/content validation | upload routes | High | Add python-magic/Pillow/PyMuPDF checks | File libraries |
| Ollama structured JSON | Real LLM structured extraction | Deterministic fallback only | Ollama calls, schema validation, repair | `/api/ai/*`, clinical | High | Implement strict Ollama client | Local Ollama |
| Prompt injection regression | OCR/ASR text cannot override rules | Not tested with real LLM | Prompt and schema tests | AI/clinical services | High | Add adversarial tests | Ollama client |
| Docker verification | Build/up/persistence tested | Files exist only | Runtime verification | Docker/Compose | Medium | Run compose commands | Docker installed |
| Visual regression suite | Compare screenshots across routes/breakpoints | One dashboard screenshot only | Multi-route screenshots/tests | verification evidence | Medium | Add browser smoke script | Browser automation |

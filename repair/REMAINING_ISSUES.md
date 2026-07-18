# Remaining Issues

This file is updated during repair work.

## Blocked By Environment

- Real ASR model testing and inference: sibling Mega-ASR exists, but the available Python environment is missing `torch`, `qwen-asr`, and `soundfile`; checkpoint/model weights were not found.
- Real PaddleOCR image/PDF OCR testing and inference: `paddleocr`, Pillow, and PyMuPDF are not installed.
- Real Ollama structured JSON testing: `ollama` is not on PATH.
- Docker build/up verification: `docker` is not on PATH.
- Baseline Git branch/commit: `D:\NoteFlow AI` is not a Git repository.

## Remaining Product Gaps

- Broader MIME/content validation.
- Medical OCR evaluation harness.
- Full frontend coverage beyond the repaired live-data/manual-note/task/customer paths.

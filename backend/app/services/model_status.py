from __future__ import annotations

import importlib.util

from ..config import settings


def asr_status() -> dict:
    return {
        "loaded": False,
        "model": settings.asr_model_mode,
        "device": settings.mega_asr_device,
        "dtype": settings.asr_dtype,
        "available": False,
        "reason": "Mega-ASR/Qwen3-ASR runtime is not bundled with this workspace backend.",
    }


def ocr_status() -> dict:
    paddle_available = importlib.util.find_spec("paddleocr") is not None
    return {
        "loaded": paddle_available,
        "engine": settings.ocr_engine,
        "device": settings.ocr_device,
        "language": settings.ocr_language,
        "available": paddle_available,
        "fallback_enabled": settings.ocr_allow_text_fallback,
    }

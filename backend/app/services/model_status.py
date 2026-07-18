from __future__ import annotations

import importlib.util

from ..config import settings
from .asr import asr_runtime_requirements, using_small_cpu_model


def asr_status() -> dict:
    required = asr_runtime_requirements()
    available = all(path.exists() for path in required)
    small_mode = using_small_cpu_model()
    return {
        "loaded": False,
        "model": settings.asr_model_mode,
        "model_family": "Qwen3-ASR" if small_mode else "Mega-ASR",
        "variant": "0.6B" if small_mode else "1.7B",
        "mega_asr_lora": not small_mode,
        "quality_router": not small_mode,
        "device": settings.mega_asr_device,
        "dtype": settings.asr_dtype,
        "available": available,
        "reason": None if available else "The configured ASR environment, runner, or checkpoint is missing.",
    }


def ocr_status() -> dict:
    paddle_available = importlib.util.find_spec("paddleocr") is not None and importlib.util.find_spec("paddle") is not None
    return {
        "loaded": paddle_available,
        "engine": settings.ocr_engine,
        "device": settings.ocr_device,
        "language": settings.ocr_language,
        "available": paddle_available,
        "fallback_enabled": settings.ocr_allow_text_fallback,
    }

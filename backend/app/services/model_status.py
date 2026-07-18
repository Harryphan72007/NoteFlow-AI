from __future__ import annotations

import importlib.util

from ..config import settings


def asr_status() -> dict:
    required = (
        settings.mega_asr_python,
        settings.mega_asr_root / "infer.py",
        settings.mega_asr_ckpt_dir / "Qwen3-ASR-1.7B",
        settings.mega_asr_ckpt_dir / "mega-asr-merged",
        settings.mega_asr_ckpt_dir / "audio_quality_router" / "best_acc_model.safetensors",
    )
    available = all(path.exists() for path in required)
    return {
        "loaded": False,
        "model": settings.asr_model_mode,
        "device": settings.mega_asr_device,
        "dtype": settings.asr_dtype,
        "available": available,
        "reason": None if available else "Mega-ASR environment, source, or checkpoints are missing.",
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

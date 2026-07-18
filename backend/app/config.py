from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/noteflow.db")
    auto_create_db: bool = _bool("APP_AUTO_CREATE_DB", True)

    asr_model_mode: str = os.getenv("ASR_MODEL_MODE", "qwen-0.6b")
    mega_asr_device: str = os.getenv("MEGA_ASR_DEVICE", "cpu")
    asr_dtype: str = os.getenv("ASR_DTYPE", "float32")
    asr_max_file_mb: int = int(os.getenv("ASR_MAX_FILE_MB", "100"))
    asr_max_duration_seconds: int = int(os.getenv("ASR_MAX_DURATION_SECONDS", "3600"))
    asr_allow_text_fallback: bool = _bool("ASR_ALLOW_TEXT_FALLBACK", True)

    ocr_engine: str = os.getenv("OCR_ENGINE", "paddleocr")
    ocr_language: str = os.getenv("OCR_LANGUAGE", "en")
    ocr_device: str = os.getenv("OCR_DEVICE", "cpu")
    ocr_max_file_mb: int = int(os.getenv("OCR_MAX_FILE_MB", "50"))
    ocr_max_pdf_pages: int = int(os.getenv("OCR_MAX_PDF_PAGES", "50"))
    ocr_general_confidence_threshold: float = float(os.getenv("OCR_GENERAL_CONFIDENCE_THRESHOLD", "0.80"))
    ocr_important_confidence_threshold: float = float(os.getenv("OCR_IMPORTANT_CONFIDENCE_THRESHOLD", "0.90"))
    ocr_critical_confidence_threshold: float = float(os.getenv("OCR_CRITICAL_CONFIDENCE_THRESHOLD", "0.95"))
    ocr_allow_text_fallback: bool = _bool("OCR_ALLOW_TEXT_FALLBACK", True)

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "./data/uploads"))
    processed_dir: Path = Path(os.getenv("PROCESSED_DIR", "./data/processed"))
    export_dir: Path = Path(os.getenv("EXPORT_DIR", "./data/exports"))

    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    )

    def ensure_directories(self) -> None:
        for path in (self.upload_dir, self.processed_dir, self.export_dir):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()

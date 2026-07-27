from __future__ import annotations

import threading
from pathlib import Path
from uuid import uuid4

import fitz
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError

try:
    from paddleocr import PaddleOCR
except ImportError:  # Optional heavyweight runtime; installed via requirements-models.txt.
    PaddleOCR = None  # type: ignore[assignment,misc]

from ..config import settings


class OCRServiceError(RuntimeError):
    pass


_ENGINE_LOCK = threading.Lock()
_ENGINES: dict[str, PaddleOCR] = {}


def _engine(language: str) -> PaddleOCR:
    if PaddleOCR is None:
        raise OCRServiceError(
            "PaddleOCR is not installed; install backend/requirements-models.txt to enable OCR"
        )
    if language not in _ENGINES:
        _ENGINES[language] = PaddleOCR(
            lang=language,
            enable_mkldnn=False,
            text_detection_model_dir=str(settings.ocr_detection_model_dir),
            text_recognition_model_dir=str(settings.ocr_recognition_model_dir),
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
    return _ENGINES[language]


def _box(payload: dict, index: int) -> tuple[float, float, float, float]:
    boxes = payload.get("rec_boxes") or []
    if index < len(boxes) and len(boxes[index]) >= 4:
        x1, y1, x2, y2 = boxes[index][:4]
        return float(x1), float(y1), float(x2), float(y2)
    polygons = payload.get("rec_polys") or []
    if index < len(polygons):
        points = polygons[index]
        xs = [float(point[0]) for point in points]
        ys = [float(point[1]) for point in points]
        return min(xs), min(ys), max(xs), max(ys)
    return 0.0, 0.0, 0.0, 0.0


def _predict(image_path: Path, language: str) -> dict:
    results = list(_engine(language).predict(input=str(image_path)))
    texts: list[str] = []
    scores: list[float] = []
    blocks: list[dict] = []
    for result in results:
        payload = result.json["res"]
        page_texts = payload.get("rec_texts", [])
        page_scores = payload.get("rec_scores", [])
        for index, text in enumerate(page_texts):
            value = str(text).strip()
            if not value:
                continue
            score = float(page_scores[index]) if index < len(page_scores) else 0.0
            x1, y1, x2, y2 = _box(payload, index)
            texts.append(value)
            scores.append(score)
            blocks.append({"text": value, "confidence": score, "x1": x1, "y1": y1, "x2": x2, "y2": y2})
    return {"text": "\n".join(texts), "scores": scores, "blocks": blocks}


def _image_dimensions(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            return image.size
    except (OSError, UnidentifiedImageError) as exc:
        raise OCRServiceError("Image is corrupt or unsupported") from exc


def _pdf_pages(path: Path) -> list[tuple[Path, int, int]]:
    try:
        document = fitz.open(path)
    except Exception as exc:
        raise OCRServiceError("PDF is corrupt or unsupported") from exc
    try:
        if document.needs_pass:
            raise OCRServiceError("Encrypted PDFs are not supported")
        if document.page_count > settings.ocr_max_pdf_pages:
            raise OCRServiceError(f"PDF exceeds {settings.ocr_max_pdf_pages} page limit")
        output: list[tuple[Path, int, int]] = []
        settings.processed_dir.mkdir(parents=True, exist_ok=True)
        for page_index in range(document.page_count):
            pixmap = document.load_page(page_index).get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            rendered = settings.processed_dir / f"ocr_{uuid4().hex}_page_{page_index + 1}.png"
            pixmap.save(rendered)
            output.append((rendered, pixmap.width, pixmap.height))
        return output
    finally:
        document.close()


def _preprocess_image(path: Path) -> Path:
    target = settings.processed_dir / f"ocr_preprocessed_{uuid4().hex}.png"
    with Image.open(path) as image:
        gray = ImageOps.grayscale(image)
        normalized = ImageOps.autocontrast(gray)
        denoised = normalized.filter(ImageFilter.MedianFilter(size=3))
        sharpened = ImageEnhance.Sharpness(denoised).enhance(1.5)
        sharpened.save(target)
    return target


def recognize_document(path: Path, suffix: str, language: str, preprocess: bool = True) -> dict:
    requested_language = settings.ocr_language if language == "auto" else language
    if requested_language != "en":
        raise OCRServiceError("Only English OCR models are configured; use language='en' or 'auto'")
    pages = _pdf_pages(path) if suffix == ".pdf" else [(path, *_image_dimensions(path))]
    output_pages: list[dict] = []
    all_scores: list[float] = []
    with _ENGINE_LOCK:
        for page_number, (image_path, width, height) in enumerate(pages, start=1):
            processed_path = _preprocess_image(image_path) if preprocess else image_path
            result = _predict(processed_path, requested_language)
            scores = result["scores"]
            all_scores.extend(scores)
            warnings: list[str] = []
            average = sum(scores) / len(scores) if scores else 0.0
            if not result["text"]:
                warnings.append("no_text_detected")
            if average < settings.ocr_general_confidence_threshold:
                warnings.append("low_confidence")
            if width < 600 or height < 600:
                warnings.append("low_resolution")
            output_pages.append(
                {
                    "page_number": page_number,
                    "image_path": processed_path,
                    "width": width,
                    "height": height,
                    "text": result["text"],
                    "blocks": result["blocks"],
                    "average_confidence": average,
                    "quality_warnings": warnings,
                }
            )
    text = "\n".join(page["text"] for page in output_pages if page["text"])
    if not text:
        raise OCRServiceError("OCR returned no text")
    return {
        "text": text,
        "pages": output_pages,
        "average_confidence": sum(all_scores) / len(all_scores) if all_scores else 0.0,
    }

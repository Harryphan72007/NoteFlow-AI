from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..database import get_db
from ..serializers import document_to_response
from ..services.storage import save_upload


router = APIRouter(tags=["processing"])

AUDIO_EXT = {"wav", "mp3", "m4a", "flac", "ogg", "webm", "txt"}
OCR_EXT = {"jpg", "jpeg", "png", "webp", "tif", "tiff", "pdf", "txt"}


def _validate_customer(db: Session, customer_id: str | None) -> None:
    if customer_id and not db.get(models.Customer, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    customer_id: str | None = Form(default=None),
    language: str = Form(default="en"),
    save_document: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    _validate_customer(db, customer_id)
    path, body = await save_upload(file, allowed=AUDIO_EXT, max_mb=settings.asr_max_file_mb, subdir="audio")
    suffix = Path(file.filename or "").suffix.lower()
    metadata = {
        "model": settings.asr_model_mode,
        "device": settings.mega_asr_device,
        "dtype": settings.asr_dtype,
        "stored_file_path": str(path),
    }
    confidence = None
    if suffix == ".txt" and settings.asr_allow_text_fallback:
        text = body.decode("utf-8", errors="replace")
        confidence = 1.0
        metadata["warning"] = "Text fallback used for ASR endpoint; no real audio model inference was run."
    else:
        raise HTTPException(status_code=503, detail="ASR model runtime is not installed. Upload .txt only when ASR_ALLOW_TEXT_FALLBACK is enabled for API testing.")

    document = models.Document(
        customer_id=customer_id if save_document else None,
        source_type="audio",
        source_name=file.filename or "audio_upload",
        original_filename=file.filename,
        stored_file_path=str(path),
        text=text,
        language=language,
        status="review-required",
        processing_status="complete",
        average_confidence=confidence,
        metadata_json=json.dumps(metadata),
    )
    document.segments.append(models.ASRSegment(start_seconds=0.0, end_seconds=max(1.0, len(text.split()) / 2.5), text=text, confidence=confidence, sequence_index=0))
    db.add(document)
    db.add(models.AuditLog(customer_id=customer_id, document=document, action="asr_document_created", new_value_json=json.dumps({"fallback": suffix == ".txt"})))
    db.commit()
    db.refresh(document)
    return document_to_response(document)


@router.post("/ocr")
async def ocr(
    file: UploadFile = File(...),
    customer_id: str | None = Form(default=None),
    language: str = Form(default="auto"),
    preprocess: bool = Form(default=True),
    save_document: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    _validate_customer(db, customer_id)
    path, body = await save_upload(file, allowed=OCR_EXT, max_mb=settings.ocr_max_file_mb, subdir="ocr")
    suffix = Path(file.filename or "").suffix.lower()
    metadata = {
        "ocr_engine": settings.ocr_engine,
        "language": language,
        "preprocess": preprocess,
        "stored_file_path": str(path),
        "quality_warnings": [],
    }
    confidence = 0.99
    if suffix == ".txt" and settings.ocr_allow_text_fallback:
        text = body.decode("utf-8", errors="replace")
        metadata["warning"] = "Text fallback used for OCR endpoint; no real OCR model inference was run."
    else:
        raise HTTPException(status_code=503, detail="OCR runtime is not installed. Upload .txt only when OCR_ALLOW_TEXT_FALLBACK is enabled for API testing.")

    document = models.Document(
        customer_id=customer_id if save_document else None,
        source_type="pdf" if suffix == ".pdf" else "image",
        source_name=file.filename or "document_upload",
        original_filename=file.filename,
        stored_file_path=str(path),
        text=text,
        language=language if language != "auto" else settings.ocr_language,
        status="review-required",
        processing_status="complete",
        average_confidence=confidence,
        metadata_json=json.dumps(metadata),
    )
    page = models.OCRPage(page_number=1, width=1000, height=1400, original_image_path=str(path), processed_image_path=str(path), average_confidence=confidence)
    for idx, line in enumerate([line.strip() for line in text.splitlines() if line.strip()] or [text.strip()]):
        page.blocks.append(models.OCRBlock(text=line, confidence=confidence, x1=64, y1=80 + idx * 36, x2=900, y2=110 + idx * 36, reading_order=idx, region_type="paragraph"))
    document.ocr_pages.append(page)
    db.add(document)
    db.add(models.AuditLog(customer_id=customer_id, document=document, action="ocr_document_created", new_value_json=json.dumps({"fallback": suffix == ".txt"})))
    db.commit()
    db.refresh(document)
    return document_to_response(document)

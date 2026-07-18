from __future__ import annotations

import json
from typing import Any

from . import models
from .schemas import DocumentResponse, OCRBlockResponse, OCRPageResponse, SegmentResponse


def parse_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def document_to_response(document: models.Document) -> DocumentResponse:
    pages = []
    for page in sorted(document.ocr_pages, key=lambda p: p.page_number):
        blocks = [
            OCRBlockResponse(
                id=block.id,
                text=block.text,
                corrected_text=block.corrected_text,
                confidence=block.confidence,
                bounding_box=[block.x1, block.y1, block.x2, block.y2],
                reading_order=block.reading_order,
                region_type=block.region_type,
            )
            for block in sorted(page.blocks, key=lambda b: b.reading_order)
        ]
        pages.append(
            OCRPageResponse(
                id=page.id,
                page_number=page.page_number,
                width=page.width,
                height=page.height,
                average_confidence=page.average_confidence,
                blocks=blocks,
            )
        )

    segments = [
        SegmentResponse(
            id=segment.id,
            start=segment.start_seconds,
            end=segment.end_seconds,
            text=segment.text,
            corrected_text=segment.corrected_text,
            confidence=segment.confidence,
        )
        for segment in sorted(document.segments, key=lambda s: s.sequence_index)
    ]

    return DocumentResponse(
        document_id=document.id,
        customer_id=document.customer_id,
        source_type=document.source_type,
        source_name=document.source_name,
        original_filename=document.original_filename,
        text=document.text,
        corrected_text=document.corrected_text,
        language=document.language,
        status=document.status,
        processing_status=document.processing_status,
        average_confidence=document.average_confidence,
        segments=segments,
        pages=pages,
        metadata=parse_json(document.metadata_json, {}),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )

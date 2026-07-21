from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import CombineDocumentsRequest, DocumentUpdate, ManualDocumentCreate, OCRBlockCorrection, TextCorrection
from ..serializers import document_to_response
from ..services.exporter import export_document
from ..services.ownership import require_customer_access
from ..services.auth import scoped_customer


router = APIRouter(tags=["documents"])


def document_or_404(db: Session, document_id: str) -> models.Document:
    document = db.get(models.Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


def validate_customer(db: Session, customer_id: str | None) -> None:
    if customer_id and not db.get(models.Customer, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")


def assert_same_customer(documents: list[models.Document], customer_id: str | None = None) -> str | None:
    customers = {document.customer_id for document in documents}
    if len(customers) > 1:
        raise HTTPException(status_code=409, detail="Cannot combine documents from different customers")
    inferred = next(iter(customers)) if customers else None
    if customer_id and inferred and customer_id != inferred:
        raise HTTPException(status_code=409, detail="Document customer does not match request customer")
    return customer_id or inferred


@router.post("/documents/manual")
def create_manual_document(payload: ManualDocumentCreate, db: Session = Depends(get_db), request: Request = None):
    payload.customer_id = scoped_customer(request, payload.customer_id)
    validate_customer(db, payload.customer_id)
    document = models.Document(
        customer_id=payload.customer_id,
        source_type="manual_text",
        source_name=payload.source_name,
        text=payload.text,
        language=payload.language,
        status="complete",
        processing_status="complete",
        metadata_json=json.dumps({"input_method": "manual"}),
    )
    db.add(document)
    db.add(models.AuditLog(customer_id=payload.customer_id, document=document, action="manual_document_created"))
    db.commit()
    db.refresh(document)
    return document_to_response(document)


@router.get("/documents")
def list_documents(customer_id: str | None = None, source_type: str | None = None, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, customer_id)
    query = db.query(models.Document)
    if customer_id:
        query = query.filter(models.Document.customer_id == customer_id)
    if source_type:
        query = query.filter(models.Document.source_type == source_type)
    return [document_to_response(document) for document in query.order_by(models.Document.created_at.desc()).all()]


@router.get("/documents/{document_id}")
def get_document(document_id: str, customer_id: str | None = None, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, customer_id)
    document = document_or_404(db, document_id)
    require_customer_access(document.customer_id, customer_id)
    return document_to_response(document)


@router.get("/documents/{document_id}/pages/{page_number}/image")
def get_document_page_image(
    document_id: str,
    page_number: int,
    processed: bool = True,
    customer_id: str | None = None,
    db: Session = Depends(get_db),
    request: Request = None,
):
    customer_id = scoped_customer(request, customer_id)
    document = document_or_404(db, document_id)
    require_customer_access(document.customer_id, customer_id)
    page = next((item for item in document.ocr_pages if item.page_number == page_number), None)
    if not page:
        raise HTTPException(status_code=404, detail="OCR page not found")

    selected_path = page.processed_image_path if processed else page.original_image_path
    fallback_path = page.original_image_path if processed else page.processed_image_path
    path = Path(selected_path or fallback_path or document.stored_file_path or "")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="OCR page image is not available")
    return FileResponse(path)


@router.patch("/documents/{document_id}")
def update_document(document_id: str, payload: DocumentUpdate, customer_id: str | None = None, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, customer_id)
    document = document_or_404(db, document_id)
    require_customer_access(document.customer_id, customer_id)
    old = document_to_response(document).model_dump(mode="json")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(document, key, value)
    db.add(models.AuditLog(customer_id=document.customer_id, document=document, action="document_updated", old_value_json=json.dumps(old), new_value_json=payload.model_dump_json()))
    db.commit()
    db.refresh(document)
    return document_to_response(document)


@router.delete("/documents/{document_id}")
def delete_document(document_id: str, customer_id: str | None = None, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, customer_id)
    document = document_or_404(db, document_id)
    require_customer_access(document.customer_id, customer_id)
    db.delete(document)
    db.commit()
    return {"deleted": True}


@router.patch("/documents/{document_id}/text")
def correct_document_text(document_id: str, payload: TextCorrection, customer_id: str | None = None, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, customer_id)
    document = document_or_404(db, document_id)
    require_customer_access(document.customer_id, customer_id)
    old = document.corrected_text or document.text
    document.corrected_text = payload.corrected_text
    db.add(models.AuditLog(
        customer_id=document.customer_id,
        document=document,
        actor=payload.actor,
        action="document_text_corrected",
        old_value_json=json.dumps({"text": old}),
        new_value_json=json.dumps({"corrected_text": payload.corrected_text}),
        reason=payload.reason,
    ))
    db.commit()
    db.refresh(document)
    return document_to_response(document)


@router.post("/documents/{document_id}/finalize")
def finalize_document(document_id: str, customer_id: str | None = None, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, customer_id)
    document = document_or_404(db, document_id)
    require_customer_access(document.customer_id, customer_id)
    document.status = "finalized"
    db.add(models.AuditLog(customer_id=document.customer_id, document=document, action="document_finalized"))
    db.commit()
    db.refresh(document)
    return document_to_response(document)


@router.patch("/documents/{document_id}/ocr-blocks/{block_id}")
def correct_ocr_block(document_id: str, block_id: str, payload: OCRBlockCorrection, customer_id: str | None = None, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, customer_id)
    document = document_or_404(db, document_id)
    require_customer_access(document.customer_id, customer_id)
    block = (
        db.query(models.OCRBlock)
        .join(models.OCRPage)
        .filter(models.OCRPage.document_id == document_id, models.OCRBlock.id == block_id)
        .first()
    )
    if not block:
        raise HTTPException(status_code=404, detail="OCR block not found")
    block.corrected_text = payload.corrected_text
    document.corrected_text = "\n".join(
        block.corrected_text or block.text
        for page in sorted(document.ocr_pages, key=lambda item: item.page_number)
        for block in sorted(page.blocks, key=lambda item: item.reading_order)
    )
    db.add(models.AuditLog(
        customer_id=document.customer_id,
        document=document,
        actor=payload.actor,
        action="ocr_block_corrected",
        old_value_json=json.dumps({"block_text": block.text}),
        new_value_json=json.dumps({"corrected_text": payload.corrected_text}),
        reason=payload.reason,
    ))
    db.commit()
    db.refresh(document)
    return document_to_response(document)


@router.post("/documents/combine")
def combine_documents(payload: CombineDocumentsRequest, db: Session = Depends(get_db), request: Request = None):
    payload.customer_id = scoped_customer(request, payload.customer_id)
    documents = [document_or_404(db, document_id) for document_id in payload.document_ids]
    customer_id = assert_same_customer(documents, payload.customer_id)
    combined_text = "\n\n".join(f"[{doc.source_type} - {doc.source_name}]\n{doc.corrected_text or doc.text}" for doc in documents)
    combined = models.Document(
        customer_id=customer_id,
        source_type="combined",
        source_name=payload.source_name,
        text=combined_text,
        language=documents[0].language if documents else "en",
        status="complete",
        processing_status="complete",
        metadata_json=json.dumps({"source_document_ids": payload.document_ids}),
    )
    db.add(combined)
    db.add(models.AuditLog(customer_id=customer_id, document=combined, action="documents_combined", new_value_json=json.dumps({"document_ids": payload.document_ids})))
    db.commit()
    db.refresh(combined)
    return document_to_response(combined)


@router.get("/documents/{document_id}/export/{export_type}")
def export_document_endpoint(document_id: str, export_type: str, customer_id: str | None = None, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, customer_id)
    document = document_or_404(db, document_id)
    require_customer_access(document.customer_id, customer_id)
    allowed = {"txt", "json", "pdf", "srt", "vtt"}
    if export_type not in allowed:
        raise HTTPException(status_code=422, detail="Unsupported export type")
    if export_type in {"srt", "vtt"} and document.source_type != "audio":
        raise HTTPException(status_code=422, detail="SRT/VTT export is only available for audio documents")
    path = export_document(document, export_type)
    db.add(models.Export(customer_id=document.customer_id, document_id=document.id, export_type=export_type, file_path=str(path)))
    db.add(models.AuditLog(customer_id=document.customer_id, document=document, action=f"document_exported_{export_type}"))
    db.commit()
    media_types = {"txt": "text/plain", "json": "application/json", "pdf": "application/pdf", "srt": "application/x-subrip", "vtt": "text/vtt"}
    return FileResponse(path, media_type=media_types[export_type], filename=path.name)

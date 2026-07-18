from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import CompareRequest
from ..services.metrics import compare_texts


router = APIRouter(tags=["comparison"])


@router.post("/compare")
def compare_documents(payload: CompareRequest, db: Session = Depends(get_db)):
    documents = [db.get(models.Document, document_id) for document_id in payload.document_ids]
    if any(document is None for document in documents):
        raise HTTPException(status_code=404, detail="Document not found")
    docs = [document for document in documents if document is not None]
    customers = {document.customer_id for document in docs}
    if len(customers) > 1:
        raise HTTPException(status_code=409, detail="Cannot compare documents from different customers")
    if payload.customer_id and next(iter(customers)) not in {None, payload.customer_id}:
        raise HTTPException(status_code=409, detail="Document customer does not match request customer")
    reference = docs[0].corrected_text or docs[0].text
    hypothesis = docs[1].corrected_text or docs[1].text
    metrics = compare_texts(reference, hypothesis)
    return {
        "document_ids": payload.document_ids,
        "reference_document_id": docs[0].id,
        "hypothesis_document_id": docs[1].id,
        **metrics,
    }

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..database import get_db
from ..services.auth import scoped_customer
from ..services.model_status import asr_status, ocr_status
from ..services.ai_tools import ollama_status


router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, None)
    document_query = db.query(models.Document)
    task_query = db.query(models.Task)
    analysis_query = db.query(models.Analysis)
    if customer_id:
        document_query = document_query.filter(models.Document.customer_id == customer_id)
        task_query = task_query.filter(models.Task.customer_id == customer_id)
        analysis_query = analysis_query.filter(models.Analysis.customer_id == customer_id)
    today = datetime.now(timezone.utc).date()
    documents = document_query.all()
    return {
        "date": today.isoformat(),
        "documents_today": sum(1 for item in documents if item.created_at.date() == today),
        "pending_reviews": sum(1 for item in documents if item.status == "review-required"),
        "processing_queue": sum(1 for item in documents if item.processing_status not in {"complete", "failed"}),
        "total_processed": len(documents),
        "activity": [{"day": (today - timedelta(days=offset)).isoformat(), "asr": sum(1 for item in documents if item.source_type == "audio" and item.created_at.date() == today - timedelta(days=offset)), "ocr": sum(1 for item in documents if item.source_type in {"image", "pdf"} and item.created_at.date() == today - timedelta(days=offset))} for offset in range(6, -1, -1)],
        "queue": [{"id": item.id, "name": item.source_name, "status": item.processing_status, "type": item.source_type} for item in documents if item.processing_status not in {"complete", "failed"}],
        "services": {"asr": asr_status(), "ocr": ocr_status(), "ollama": ollama_status(), "database": {"available": True, "url": settings.database_url}},
    }


@router.get("/history")
def history(limit: int = 100, db: Session = Depends(get_db), request: Request = None):
    customer_id = scoped_customer(request, None)
    query = db.query(models.AuditLog)
    if customer_id:
        query = query.filter(models.AuditLog.customer_id == customer_id)
    logs = query.order_by(models.AuditLog.created_at.desc()).limit(min(limit, 500)).all()
    return [{"id": item.id, "customer_id": item.customer_id, "document_id": item.document_id, "actor": item.actor, "action": item.action, "reason": item.reason, "created_at": item.created_at} for item in logs]


@router.get("/history/export")
def history_export(db: Session = Depends(get_db), request: Request = None):
    return JSONResponse(content={"entries": history(db=db, request=request)})


@router.get("/settings")
def runtime_settings():
    return {"app_env": settings.app_env, "database": settings.database_url, "asr": asr_status(), "ocr": ocr_status(), "ollama": ollama_status(), "fallbacks": {"asr_text": settings.asr_allow_text_fallback, "ocr_text": settings.ocr_allow_text_fallback}}

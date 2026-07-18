from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import ClinicalReviewRequest, IssueDecisionRequest
from ..serializers import parse_json
from ..services.clinical import run_clinical_review
from ..services.ownership import require_customer_access


router = APIRouter(tags=["clinical-review"])


@router.post("/clinical-review")
def clinical_review(payload: ClinicalReviewRequest, db: Session = Depends(get_db)):
    documents = [db.get(models.Document, document_id) for document_id in payload.document_ids]
    if any(document is None for document in documents):
        raise HTTPException(status_code=404, detail="Document not found")
    docs = [document for document in documents if document is not None]
    customers = {document.customer_id for document in docs}
    if len(customers) > 1:
        raise HTTPException(status_code=409, detail="Cannot review documents from different customers")
    customer_id = payload.customer_id or next(iter(customers))
    if payload.customer_id and customer_id and payload.customer_id != customer_id:
        raise HTTPException(status_code=409, detail="Document customer does not match request customer")

    text = "\n\n".join(f"[{doc.source_type} - {doc.source_name}]\n{doc.corrected_text or doc.text}" for doc in docs)
    low_confidence = []
    for doc in docs:
        if doc.average_confidence is not None and doc.average_confidence < 0.8:
            low_confidence.append(doc.source_name)
        for page in doc.ocr_pages:
            for block in page.blocks:
                if block.confidence is not None and block.confidence < 0.8:
                    low_confidence.append(block.text)

    result = run_clinical_review(text, note_type=payload.note_type, low_confidence_evidence=low_confidence)
    analysis = models.Analysis(
        customer_id=customer_id,
        document_id=docs[0].id if len(docs) == 1 else None,
        analysis_type="clinical_review",
        risk_level=result["risk_level"],
        risk_score=result["risk_score"],
        result_json=json.dumps(result),
        model_name="deterministic-rules",
        model_version="0.1.0",
        prompt_version="not-used",
    )
    for issue in result["issues"]:
        analysis.issues.append(models.AnalysisIssue(
            issue_type=issue["issue_type"],
            severity=issue["severity"],
            title=issue["title"],
            message=issue["message"],
            evidence_json=json.dumps(issue["evidence"]),
            recommendation=issue["recommendation"],
        ))
    for task in result["tasks"]:
        analysis.tasks.append(models.Task(customer_id=customer_id, document_id=docs[0].id if len(docs) == 1 else None, task_text=task["task_text"], priority=task["priority"], evidence=task["evidence"]))
    db.add(analysis)
    db.add(models.AuditLog(customer_id=customer_id, document_id=docs[0].id if len(docs) == 1 else None, action="clinical_review_created", new_value_json=json.dumps({"document_ids": payload.document_ids})))
    db.commit()
    db.refresh(analysis)
    return {
        "analysis_id": analysis.id,
        "risk_level": analysis.risk_level,
        "risk_score": analysis.risk_score,
        "score_components": result["score_components"],
        "issues": [
            {
                "id": issue.id,
                "type": issue.issue_type,
                "severity": issue.severity,
                "title": issue.title,
                "message": issue.message,
                "evidence": parse_json(issue.evidence_json, []),
                "recommendation": issue.recommendation,
                "status": issue.status,
            }
            for issue in analysis.issues
        ],
        "tasks": [{"id": task.id, "task_text": task.task_text, "status": task.status, "priority": task.priority, "evidence": task.evidence} for task in analysis.tasks],
        "summary": result["summary"],
    }


@router.post("/issues/{issue_id}/decision")
def issue_decision(issue_id: str, payload: IssueDecisionRequest, customer_id: str | None = None, db: Session = Depends(get_db)):
    issue = db.get(models.AnalysisIssue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    require_customer_access(issue.analysis.customer_id, customer_id)
    if payload.action == "ignore" and not payload.reason:
        raise HTTPException(status_code=422, detail="A reason is required when ignoring an issue")
    issue.status = payload.action
    issue.reviewer_reason = payload.reason
    if payload.action in {"accept", "ignore", "resolve"}:
        issue.resolved_at = datetime.utcnow()
    db.add(models.AuditLog(
        customer_id=issue.analysis.customer_id,
        document_id=issue.analysis.document_id,
        actor=payload.actor,
        action=f"issue_{payload.action}",
        new_value_json=payload.model_dump_json(),
        reason=payload.reason,
    ))
    db.commit()
    db.refresh(issue)
    return {
        "id": issue.id,
        "status": issue.status,
        "reviewer_reason": issue.reviewer_reason,
        "resolved_at": issue.resolved_at,
    }

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import CustomerCreate, CustomerResponse, CustomerUpdate
from ..serializers import document_to_response, parse_json
from ..services.exporter import customer_report_payload
from ..services.auth import scoped_customer


router = APIRouter(tags=["customers"])


def _customer_or_404(db: Session, customer_id: str) -> models.Customer:
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


def _duplicate_warning(db: Session, payload: CustomerCreate | CustomerUpdate, exclude_id: str | None = None) -> bool:
    clauses = []
    if getattr(payload, "patient_id", None):
        clauses.append(models.Customer.patient_id == payload.patient_id)
    if getattr(payload, "medical_record_number", None):
        clauses.append(models.Customer.medical_record_number == payload.medical_record_number)
    if getattr(payload, "full_name", None) and getattr(payload, "date_of_birth", None):
        clauses.append((models.Customer.full_name == payload.full_name) & (models.Customer.date_of_birth == payload.date_of_birth))
    if not clauses:
        return False
    query = db.query(models.Customer).filter(or_(*clauses))
    if exclude_id:
        query = query.filter(models.Customer.id != exclude_id)
    return db.query(query.exists()).scalar()


def _response(customer: models.Customer, duplicate_warning: bool = False) -> CustomerResponse:
    return CustomerResponse.model_validate(customer).model_copy(update={"duplicate_warning": duplicate_warning})


@router.post("/customers", response_model=CustomerResponse)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    duplicate = _duplicate_warning(db, payload)
    customer_code = payload.customer_code or f"PT-{db.query(models.Customer).count() + 1:06d}"
    if db.query(models.Customer).filter(models.Customer.customer_code == customer_code).first():
        raise HTTPException(status_code=409, detail="Customer code already exists")
    customer = models.Customer(customer_code=customer_code, **payload.model_dump(exclude={"customer_code"}))
    db.add(customer)
    db.add(models.AuditLog(customer=customer, action="customer_created", new_value_json=payload.model_dump_json()))
    db.commit()
    db.refresh(customer)
    return _response(customer, duplicate)


@router.get("/customers", response_model=list[CustomerResponse])
def list_customers(
    search: str | None = None,
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    request: Request = None,
):
    query = db.query(models.Customer)
    scoped_id = scoped_customer(request, None)
    if scoped_id:
        query = query.filter(models.Customer.id == scoped_id)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(models.Customer.full_name.ilike(like), models.Customer.customer_code.ilike(like), models.Customer.patient_id.ilike(like)))
    if status:
        query = query.filter(models.Customer.status == status)
    return [_response(customer) for customer in query.order_by(models.Customer.created_at.desc()).all()]


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    return _response(_customer_or_404(db, customer_id))


@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: str, payload: CustomerUpdate, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    customer = _customer_or_404(db, customer_id)
    old = CustomerResponse.model_validate(customer).model_dump(mode="json")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    duplicate = _duplicate_warning(db, payload, exclude_id=customer_id)
    db.add(models.AuditLog(customer=customer, action="customer_updated", old_value_json=json.dumps(old), new_value_json=payload.model_dump_json()))
    db.commit()
    db.refresh(customer)
    return _response(customer, duplicate)


@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    customer = _customer_or_404(db, customer_id)
    db.delete(customer)
    db.commit()
    return {"deleted": True}


@router.post("/customers/{customer_id}/archive", response_model=CustomerResponse)
def archive_customer(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    customer = _customer_or_404(db, customer_id)
    customer.status = "archived"
    db.add(models.AuditLog(customer=customer, action="customer_archived"))
    db.commit()
    db.refresh(customer)
    return _response(customer)


@router.post("/customers/{customer_id}/restore", response_model=CustomerResponse)
def restore_customer(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    customer = _customer_or_404(db, customer_id)
    customer.status = "active"
    db.add(models.AuditLog(customer=customer, action="customer_restored"))
    db.commit()
    db.refresh(customer)
    return _response(customer)


@router.get("/customers/{customer_id}/documents")
def customer_documents(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    _customer_or_404(db, customer_id)
    documents = db.query(models.Document).filter(models.Document.customer_id == customer_id).order_by(models.Document.created_at.desc()).all()
    return [document_to_response(document) for document in documents]


@router.get("/customers/{customer_id}/analyses")
def customer_analyses(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    _customer_or_404(db, customer_id)
    analyses = db.query(models.Analysis).filter(models.Analysis.customer_id == customer_id).order_by(models.Analysis.created_at.desc()).all()
    return [{"id": item.id, "risk_level": item.risk_level, "risk_score": item.risk_score, "result": parse_json(item.result_json, {})} for item in analyses]


@router.get("/customers/{customer_id}/tasks")
def customer_tasks(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    _customer_or_404(db, customer_id)
    return db.query(models.Task).filter(models.Task.customer_id == customer_id).order_by(models.Task.created_at.desc()).all()


@router.get("/customers/{customer_id}/exports")
def customer_exports(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    _customer_or_404(db, customer_id)
    return db.query(models.Export).filter(models.Export.customer_id == customer_id).order_by(models.Export.created_at.desc()).all()


@router.get("/customers/{customer_id}/activity")
def customer_activity(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    _customer_or_404(db, customer_id)
    logs = db.query(models.AuditLog).filter(models.AuditLog.customer_id == customer_id).order_by(models.AuditLog.created_at.desc()).all()
    return logs


@router.get("/customers/{customer_id}/export/report")
def customer_report(customer_id: str, db: Session = Depends(get_db), request: Request = None):
    scoped_customer(request, customer_id)
    customer = _customer_or_404(db, customer_id)
    documents = db.query(models.Document).filter(models.Document.customer_id == customer_id).all()
    analyses = db.query(models.Analysis).filter(models.Analysis.customer_id == customer_id).all()
    tasks = db.query(models.Task).filter(models.Task.customer_id == customer_id).all()
    payload = customer_report_payload(customer, documents, analyses, tasks)
    export = models.Export(customer_id=customer.id, export_type="json", file_path=f"customer_report_{customer.id}.json")
    db.add(export)
    db.add(models.AuditLog(customer=customer, action="customer_report_exported"))
    db.commit()
    return JSONResponse(payload)

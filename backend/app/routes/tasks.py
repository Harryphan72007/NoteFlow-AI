from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import TaskCreate, TaskResponse, TaskUpdate
from ..services.ownership import require_customer_access


router = APIRouter(tags=["tasks"])


def task_or_404(db: Session, task_id: str) -> models.Task:
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(customer_id: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Task)
    if customer_id:
        query = query.filter(models.Task.customer_id == customer_id)
    if status:
        query = query.filter(models.Task.status == status)
    return query.order_by(models.Task.created_at.desc()).all()


@router.post("/tasks", response_model=TaskResponse)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(**payload.model_dump())
    db.add(task)
    db.add(models.AuditLog(customer_id=payload.customer_id, document_id=payload.document_id, action="task_created", new_value_json=payload.model_dump_json()))
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate, customer_id: str | None = None, db: Session = Depends(get_db)):
    task = task_or_404(db, task_id)
    require_customer_access(task.customer_id, customer_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.add(models.AuditLog(customer_id=task.customer_id, document_id=task.document_id, action="task_updated", new_value_json=payload.model_dump_json()))
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, customer_id: str | None = None, db: Session = Depends(get_db)):
    task = task_or_404(db, task_id)
    require_customer_access(task.customer_id, customer_id)
    db.delete(task)
    db.commit()
    return {"deleted": True}


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str, customer_id: str | None = None, db: Session = Depends(get_db)):
    task = task_or_404(db, task_id)
    require_customer_access(task.customer_id, customer_id)
    task.status = "complete"
    task.completed_at = datetime.utcnow()
    db.add(models.AuditLog(customer_id=task.customer_id, document_id=task.document_id, action="task_completed"))
    db.commit()
    db.refresh(task)
    return task

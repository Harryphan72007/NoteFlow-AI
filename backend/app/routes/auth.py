from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services.auth import current_user, ensure_default_user, hash_password, issue_token, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=128)
    password: str = Field(min_length=8, max_length=256)
    customer_id: str | None = None


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if user is None and payload.username == "local.user":
        user = ensure_default_user(db)
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": issue_token(user), "token_type": "bearer", "user": {"id": user.id, "username": user.username, "customer_id": user.customer_id}}


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    if payload.customer_id and not db.get(models.Customer, payload.customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    user = models.User(username=payload.username, password_hash=hash_password(payload.password), customer_id=payload.customer_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "customer_id": user.customer_id}


@router.get("/me")
def me(user: models.User = Depends(current_user)):
    return {"id": user.id, "username": user.username, "customer_id": user.customer_id}

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+().\-\s]{3,32}$")
LANGUAGE_RE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z]{2,4})?$|^auto$")
DOCUMENT_STATUSES = {"draft", "complete", "review-required", "finalized", "archived"}
TASK_STATUSES = {"pending", "complete", "cancelled", "blocked", "in_progress"}
TASK_PRIORITIES = {"low", "medium", "high", "critical"}


class CustomerCreate(BaseModel):
    customer_code: str | None = None
    full_name: str
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    patient_id: str | None = None
    medical_record_number: str | None = None
    allergies: str | None = None
    existing_conditions: str | None = None
    emergency_contact: str | None = None
    notes: str | None = None

    @field_validator("full_name")
    @classmethod
    def full_name_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Customer full name is required")
        return value.strip()

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not EMAIL_RE.match(value):
            raise ValueError("Invalid email address")
        return value

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not PHONE_RE.match(value):
            raise ValueError("Invalid phone number")
        return value


class CustomerUpdate(BaseModel):
    full_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    patient_id: str | None = None
    medical_record_number: str | None = None
    allergies: str | None = None
    existing_conditions: str | None = None
    emergency_contact: str | None = None
    notes: str | None = None
    status: Literal["active", "archived"] | None = None

    @field_validator("full_name")
    @classmethod
    def full_name_nonblank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Customer full name cannot be blank")
        return value.strip() if value is not None else value

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not EMAIL_RE.match(value):
            raise ValueError("Invalid email address")
        return value

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not PHONE_RE.match(value):
            raise ValueError("Invalid phone number")
        return value


class CustomerResponse(CustomerCreate):
    id: str
    customer_code: str
    status: str
    created_at: datetime
    updated_at: datetime
    duplicate_warning: bool = False

    model_config = {"from_attributes": True}


class SegmentResponse(BaseModel):
    id: str
    start: float
    end: float
    text: str
    corrected_text: str | None = None
    confidence: float | None = None


class OCRBlockResponse(BaseModel):
    id: str
    text: str
    corrected_text: str | None = None
    confidence: float | None = None
    bounding_box: list[float]
    reading_order: int
    region_type: str


class OCRPageResponse(BaseModel):
    id: str
    page_number: int
    width: int
    height: int
    average_confidence: float | None = None
    blocks: list[OCRBlockResponse] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    document_id: str
    customer_id: str | None = None
    source_type: str
    source_name: str
    original_filename: str | None = None
    text: str
    corrected_text: str | None = None
    language: str
    status: str
    processing_status: str
    average_confidence: float | None = None
    segments: list[SegmentResponse] = Field(default_factory=list)
    pages: list[OCRPageResponse] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ManualDocumentCreate(BaseModel):
    customer_id: str | None = None
    source_name: str = "manual_note"
    text: str
    language: str = "en"

    @field_validator("text")
    @classmethod
    def text_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Document text is required")
        return value

    @field_validator("language")
    @classmethod
    def language_code(cls, value: str) -> str:
        if not LANGUAGE_RE.match(value):
            raise ValueError("Invalid language code")
        return value


class DocumentUpdate(BaseModel):
    source_name: str | None = None
    corrected_text: str | None = None
    language: str | None = None
    status: str | None = None

    @field_validator("language")
    @classmethod
    def language_code(cls, value: str | None) -> str | None:
        if value is not None and not LANGUAGE_RE.match(value):
            raise ValueError("Invalid language code")
        return value

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str | None) -> str | None:
        if value is not None and value not in DOCUMENT_STATUSES:
            raise ValueError("Invalid document status")
        return value


class TextCorrection(BaseModel):
    corrected_text: str
    reason: str | None = None
    actor: str = "local_user"

    @field_validator("corrected_text")
    @classmethod
    def corrected_text_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Corrected text is required")
        return value


class OCRBlockCorrection(BaseModel):
    corrected_text: str
    reason: str | None = None
    actor: str = "local_user"

    @field_validator("corrected_text")
    @classmethod
    def corrected_text_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Corrected text is required")
        return value


class CombineDocumentsRequest(BaseModel):
    document_ids: list[str] = Field(min_length=2)
    customer_id: str | None = None
    source_name: str = "Combined clinical document"


class CompareRequest(BaseModel):
    document_ids: list[str] = Field(min_length=2, max_length=2)
    customer_id: str | None = None


class ClinicalReviewRequest(BaseModel):
    document_ids: list[str] = Field(min_length=1)
    customer_id: str | None = None
    note_type: str = "progress_note"

    @field_validator("note_type")
    @classmethod
    def note_type_known(cls, value: str) -> str:
        allowed = {"admission", "admission_note", "progress", "progress_note", "nursing", "nursing_note", "medication", "medication_note", "discharge", "discharge_summary", "custom"}
        if value not in allowed:
            raise ValueError("Invalid note type")
        return value


class IssueDecisionRequest(BaseModel):
    action: Literal["accept", "edit", "ignore", "resolve"]
    reason: str | None = None
    new_value: str | None = None
    actor: str = "local_user"


class TaskCreate(BaseModel):
    customer_id: str | None = None
    document_id: str | None = None
    analysis_id: str | None = None
    task_text: str
    owner: str | None = None
    due_date: str | None = None
    due_time: str | None = None
    frequency: str | None = None
    priority: str = "medium"
    evidence: str | None = None

    @field_validator("task_text")
    @classmethod
    def task_text_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Task text is required")
        return value

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, value: str) -> str:
        if value not in TASK_PRIORITIES:
            raise ValueError("Invalid task priority")
        return value


class TaskUpdate(BaseModel):
    task_text: str | None = None
    owner: str | None = None
    due_date: str | None = None
    due_time: str | None = None
    frequency: str | None = None
    priority: str | None = None
    status: str | None = None
    evidence: str | None = None

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, value: str | None) -> str | None:
        if value is not None and value not in TASK_PRIORITIES:
            raise ValueError("Invalid task priority")
        return value

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str | None) -> str | None:
        if value is not None and value not in TASK_STATUSES:
            raise ValueError("Invalid task status")
        return value


class TaskResponse(TaskCreate):
    id: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class AITextRequest(BaseModel):
    text: str
    target_language: str | None = None


class HealthResponse(BaseModel):
    status: str
    services: dict[str, Any]

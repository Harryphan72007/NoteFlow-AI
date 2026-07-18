from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("cust"))
    customer_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    patient_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    medical_record_number: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    existing_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False, index=True)

    documents: Mapped[list["Document"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("doc"))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    source_name: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stored_file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    processing_status: Mapped[str] = mapped_column(String(32), default="complete", nullable=False)
    average_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    customer: Mapped[Customer | None] = relationship(back_populates="documents")
    segments: Mapped[list["ASRSegment"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    ocr_pages: Mapped[list["OCRPage"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class ASRSegment(Base):
    __tablename__ = "asr_segments"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("seg"))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    start_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    end_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    sequence_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    document: Mapped[Document] = relationship(back_populates="segments")


class OCRPage(Base):
    __tablename__ = "ocr_pages"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("page"))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    height: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    original_image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    average_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    document: Mapped[Document] = relationship(back_populates="ocr_pages")
    blocks: Mapped[list["OCRBlock"]] = relationship(back_populates="page", cascade="all, delete-orphan")


class OCRBlock(Base):
    __tablename__ = "ocr_blocks"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("block"))
    page_id: Mapped[str] = mapped_column(ForeignKey("ocr_pages.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    x1: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    y1: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    x2: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    y2: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    reading_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    region_type: Mapped[str] = mapped_column(String(64), default="paragraph", nullable=False)

    page: Mapped[OCRPage] = relationship(back_populates="blocks")


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("analysis"))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    analysis_type: Mapped[str] = mapped_column(String(64), default="clinical_review", nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), default="green", nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    result_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    customer: Mapped[Customer | None] = relationship(back_populates="analyses")
    document: Mapped[Document | None] = relationship(back_populates="analyses")
    issues: Mapped[list["AnalysisIssue"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="analysis")


class AnalysisIssue(Base):
    __tablename__ = "analysis_issues"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("issue"))
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), index=True)
    issue_type: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)
    reviewer_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    analysis: Mapped[Analysis] = relationship(back_populates="issues")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("task"))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    analysis_id: Mapped[str | None] = mapped_column(ForeignKey("analyses.id", ondelete="SET NULL"), nullable=True, index=True)
    task_text: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    due_time: Mapped[str | None] = mapped_column(String(64), nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(128), nullable=True)
    priority: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    customer: Mapped[Customer | None] = relationship(back_populates="tasks")
    document: Mapped[Document | None] = relationship(back_populates="tasks")
    analysis: Mapped[Analysis | None] = relationship(back_populates="tasks")


class Export(Base):
    __tablename__ = "exports"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("export"))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    export_type: Mapped[str] = mapped_column(String(32), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("audit"))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    actor: Mapped[str] = mapped_column(String(255), default="local_user", nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    old_value_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    customer: Mapped[Customer | None] = relationship(back_populates="audit_logs")
    document: Mapped[Document | None] = relationship(back_populates="audit_logs")

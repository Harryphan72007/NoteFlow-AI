"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-18
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("customer_code", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=64), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("patient_id", sa.String(length=128), nullable=True),
        sa.Column("medical_record_number", sa.String(length=128), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("existing_conditions", sa.Text(), nullable=True),
        sa.Column("emergency_contact", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_code"),
    )
    op.create_index(op.f("ix_customers_customer_code"), "customers", ["customer_code"], unique=False)
    op.create_index(op.f("ix_customers_full_name"), "customers", ["full_name"], unique=False)
    op.create_index(op.f("ix_customers_medical_record_number"), "customers", ["medical_record_number"], unique=False)
    op.create_index(op.f("ix_customers_patient_id"), "customers", ["patient_id"], unique=False)
    op.create_index(op.f("ix_customers_status"), "customers", ["status"], unique=False)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("customer_id", sa.String(length=40), nullable=True),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("stored_file_path", sa.Text(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("processing_status", sa.String(length=32), nullable=False),
        sa.Column("average_confidence", sa.Float(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_customer_id"), "documents", ["customer_id"], unique=False)
    op.create_index(op.f("ix_documents_source_type"), "documents", ["source_type"], unique=False)

    op.create_table(
        "analyses",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("customer_id", sa.String(length=40), nullable=True),
        sa.Column("document_id", sa.String(length=40), nullable=True),
        sa.Column("analysis_type", sa.String(length=64), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=True),
        sa.Column("model_version", sa.String(length=128), nullable=True),
        sa.Column("prompt_version", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analyses_customer_id"), "analyses", ["customer_id"], unique=False)
    op.create_index(op.f("ix_analyses_document_id"), "analyses", ["document_id"], unique=False)

    op.create_table(
        "asr_segments",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("document_id", sa.String(length=40), nullable=False),
        sa.Column("start_seconds", sa.Float(), nullable=False),
        sa.Column("end_seconds", sa.Float(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("sequence_index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asr_segments_document_id"), "asr_segments", ["document_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("customer_id", sa.String(length=40), nullable=True),
        sa.Column("document_id", sa.String(length=40), nullable=True),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("old_value_json", sa.Text(), nullable=True),
        sa.Column("new_value_json", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_customer_id"), "audit_logs", ["customer_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_document_id"), "audit_logs", ["document_id"], unique=False)

    op.create_table(
        "exports",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("customer_id", sa.String(length=40), nullable=True),
        sa.Column("document_id", sa.String(length=40), nullable=True),
        sa.Column("export_type", sa.String(length=32), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exports_customer_id"), "exports", ["customer_id"], unique=False)
    op.create_index(op.f("ix_exports_document_id"), "exports", ["document_id"], unique=False)

    op.create_table(
        "ocr_pages",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("document_id", sa.String(length=40), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("original_image_path", sa.Text(), nullable=True),
        sa.Column("processed_image_path", sa.Text(), nullable=True),
        sa.Column("average_confidence", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ocr_pages_document_id"), "ocr_pages", ["document_id"], unique=False)

    op.create_table(
        "analysis_issues",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("analysis_id", sa.String(length=40), nullable=False),
        sa.Column("issue_type", sa.String(length=128), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("evidence_json", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reviewer_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_issues_analysis_id"), "analysis_issues", ["analysis_id"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("customer_id", sa.String(length=40), nullable=True),
        sa.Column("document_id", sa.String(length=40), nullable=True),
        sa.Column("analysis_id", sa.String(length=40), nullable=True),
        sa.Column("task_text", sa.Text(), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("due_date", sa.String(length=64), nullable=True),
        sa.Column("due_time", sa.String(length=64), nullable=True),
        sa.Column("frequency", sa.String(length=128), nullable=True),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_analysis_id"), "tasks", ["analysis_id"], unique=False)
    op.create_index(op.f("ix_tasks_customer_id"), "tasks", ["customer_id"], unique=False)
    op.create_index(op.f("ix_tasks_document_id"), "tasks", ["document_id"], unique=False)

    op.create_table(
        "ocr_blocks",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("page_id", sa.String(length=40), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("x1", sa.Float(), nullable=False),
        sa.Column("y1", sa.Float(), nullable=False),
        sa.Column("x2", sa.Float(), nullable=False),
        sa.Column("y2", sa.Float(), nullable=False),
        sa.Column("reading_order", sa.Integer(), nullable=False),
        sa.Column("region_type", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["page_id"], ["ocr_pages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ocr_blocks_page_id"), "ocr_blocks", ["page_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ocr_blocks_page_id"), table_name="ocr_blocks")
    op.drop_table("ocr_blocks")
    op.drop_index(op.f("ix_tasks_document_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_customer_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_analysis_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_analysis_issues_analysis_id"), table_name="analysis_issues")
    op.drop_table("analysis_issues")
    op.drop_index(op.f("ix_ocr_pages_document_id"), table_name="ocr_pages")
    op.drop_table("ocr_pages")
    op.drop_index(op.f("ix_exports_document_id"), table_name="exports")
    op.drop_index(op.f("ix_exports_customer_id"), table_name="exports")
    op.drop_table("exports")
    op.drop_index(op.f("ix_audit_logs_document_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_customer_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_asr_segments_document_id"), table_name="asr_segments")
    op.drop_table("asr_segments")
    op.drop_index(op.f("ix_analyses_document_id"), table_name="analyses")
    op.drop_index(op.f("ix_analyses_customer_id"), table_name="analyses")
    op.drop_table("analyses")
    op.drop_index(op.f("ix_documents_source_type"), table_name="documents")
    op.drop_index(op.f("ix_documents_customer_id"), table_name="documents")
    op.drop_table("documents")
    op.drop_index(op.f("ix_customers_status"), table_name="customers")
    op.drop_index(op.f("ix_customers_patient_id"), table_name="customers")
    op.drop_index(op.f("ix_customers_medical_record_number"), table_name="customers")
    op.drop_index(op.f("ix_customers_full_name"), table_name="customers")
    op.drop_index(op.f("ix_customers_customer_code"), table_name="customers")
    op.drop_table("customers")

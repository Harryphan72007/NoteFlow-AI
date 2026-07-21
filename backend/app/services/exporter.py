from __future__ import annotations

import json
from pathlib import Path

from ..config import settings
from ..models import Document
from ..serializers import document_to_response
from .storage import ensure_within, safe_filename


def export_document(document: Document, export_type: str) -> Path:
    name = safe_filename(f"{document.id}.{export_type}")
    path = ensure_within(settings.export_dir, settings.export_dir / name)
    text = document.corrected_text or document.text

    if export_type == "txt":
        path.write_text(text, encoding="utf-8")
    elif export_type == "json":
        path.write_text(document_to_response(document).model_dump_json(indent=2), encoding="utf-8")
    elif export_type == "srt":
        path.write_text(to_srt(document), encoding="utf-8")
    elif export_type == "vtt":
        path.write_text(to_vtt(document), encoding="utf-8")
    elif export_type == "pdf":
        path.write_bytes(simple_pdf_bytes(text or document.source_name))
    else:
        raise ValueError(f"Unsupported export type: {export_type}")
    return path


def _timestamp(seconds: float, sep: str) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def to_srt(document: Document) -> str:
    lines = ["NOTE: timestamps are estimated from transcript length; model timestamps were not available.", ""]
    for idx, segment in enumerate(sorted(document.segments, key=lambda item: item.sequence_index), start=1):
        lines.extend([
            str(idx),
            f"{_timestamp(segment.start_seconds, ',')} --> {_timestamp(segment.end_seconds, ',')}",
            segment.corrected_text or segment.text,
            "",
        ])
    return "\n".join(lines)


def to_vtt(document: Document) -> str:
    lines = ["WEBVTT", "", "NOTE timestamps are estimated from transcript length; model timestamps were not available.", ""]
    for segment in sorted(document.segments, key=lambda item: item.sequence_index):
        lines.extend([
            f"{_timestamp(segment.start_seconds, '.')} --> {_timestamp(segment.end_seconds, '.')}",
            segment.corrected_text or segment.text,
            "",
        ])
    return "\n".join(lines)


def simple_pdf_bytes(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:3000]
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET"
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        f"5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj",
    ]
    body = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(body.encode("latin-1")))
        body += obj + "\n"
    xref_start = len(body.encode("latin-1"))
    body += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    body += "".join(f"{offset:010d} 00000 n \n" for offset in offsets[1:])
    body += f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n"
    return body.encode("latin-1", errors="replace")


def customer_report_payload(customer, documents, analyses, tasks) -> dict:
    return {
        "customer": {"id": customer.id, "customer_code": customer.customer_code, "full_name": customer.full_name, "status": customer.status},
        "documents": [document_to_response(doc).model_dump(mode="json") for doc in documents],
        "analyses": [{"id": item.id, "risk_level": item.risk_level, "risk_score": item.risk_score, "result": json.loads(item.result_json)} for item in analyses],
        "tasks": [{"id": item.id, "task_text": item.task_text, "status": item.status, "priority": item.priority} for item in tasks],
    }

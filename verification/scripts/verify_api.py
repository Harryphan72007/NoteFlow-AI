from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "verification" / "evidence"
API_EVIDENCE = EVIDENCE / "api"
DB_PATH = EVIDENCE / "database" / "verify_api.db"

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
os.environ["UPLOAD_DIR"] = str((EVIDENCE / "uploads").resolve())
os.environ["PROCESSED_DIR"] = str((EVIDENCE / "processed").resolve())
os.environ["EXPORT_DIR"] = str((EVIDENCE / "exports").resolve())
os.environ["APP_AUTO_CREATE_DB"] = "true"

sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.database import Base, engine  # noqa: E402
from backend.app.main import app  # noqa: E402


def redact(value):
    if isinstance(value, dict):
        return {key: redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def record(results, name, response, expected_status=None):
    body = None
    try:
        body = response.json()
    except Exception:
        body = response.text[:500]
    item = {
        "name": name,
        "status_code": response.status_code,
        "expected_status": expected_status,
        "pass": expected_status is None or response.status_code == expected_status,
        "body": redact(body),
    }
    results.append(item)
    (API_EVIDENCE / f"{name}.json").write_text(json.dumps(item, indent=2, default=str), encoding="utf-8")
    return body


def main() -> int:
    API_EVIDENCE.mkdir(parents=True, exist_ok=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    client = TestClient(app)
    results = []

    health = client.get("/health")
    record(results, "health", health, 200)

    missing_name = client.post("/api/customers", json={})
    record(results, "customer_missing_name", missing_name, 422)

    customer_a = record(results, "customer_a_create", client.post("/api/customers", json={
        "customer_code": "PT-AUDIT-A",
        "full_name": "Audit Customer A",
        "date_of_birth": "1980-01-01",
        "patient_id": "AUD-A",
        "allergies": "Penicillin",
    }), 200)
    customer_b = record(results, "customer_b_create", client.post("/api/customers", json={
        "customer_code": "PT-AUDIT-B",
        "full_name": "Audit Customer B",
        "date_of_birth": "1982-02-02",
        "patient_id": "AUD-B",
    }), 200)
    customer_a_id = customer_a["id"]
    customer_b_id = customer_b["id"]

    duplicate_code = client.post("/api/customers", json={"customer_code": "PT-AUDIT-A", "full_name": "Duplicate Code"})
    record(results, "customer_duplicate_code", duplicate_code, 409)

    invalid_email = client.post("/api/customers", json={"customer_code": "PT-AUDIT-EMAIL", "full_name": "Invalid Email", "email": "not-an-email"})
    record(results, "customer_invalid_email", invalid_email, 422)

    list_customers = client.get("/api/customers", params={"search": "Audit Customer"})
    record(results, "customer_search", list_customers, 200)

    update = client.patch(f"/api/customers/{customer_a_id}", json={"phone": "555-0100"})
    record(results, "customer_update", update, 200)

    archive = client.post(f"/api/customers/{customer_a_id}/archive")
    record(results, "customer_archive", archive, 200)
    restore = client.post(f"/api/customers/{customer_a_id}/restore")
    record(results, "customer_restore", restore, 200)

    manual_a = record(results, "manual_document_a", client.post("/api/documents/manual", json={
        "customer_id": customer_a_id,
        "source_name": "Audit manual A",
        "text": "Patient has chest pain. Started amoxicillin. Monitor tomorrow.",
    }), 200)
    manual_b = record(results, "manual_document_b", client.post("/api/documents/manual", json={
        "customer_id": customer_b_id,
        "source_name": "Audit manual B",
        "text": "Customer B note. No known allergies.",
    }), 200)
    doc_a_id = manual_a["document_id"]
    doc_b_id = manual_b["document_id"]

    guessed_cross_customer = client.get(f"/api/documents/{doc_b_id}", params={"customer_id": customer_a_id})
    record(results, "cross_customer_document_guess", guessed_cross_customer, 403)

    cross_combine = client.post("/api/documents/combine", json={"document_ids": [doc_a_id, doc_b_id]})
    record(results, "cross_customer_combine", cross_combine, 409)

    asr_txt = record(results, "asr_text_fallback", client.post(
        "/api/transcribe",
        data={"customer_id": customer_a_id, "language": "en", "save_document": "true"},
        files={"file": ("audio_fallback.txt", b"Take 5 mg once daily.", "text/plain")},
    ), 200)
    ocr_txt = record(results, "ocr_text_fallback", client.post(
        "/api/ocr",
        data={"customer_id": customer_a_id, "language": "en", "preprocess": "true", "save_document": "true"},
        files={"file": ("ocr_fallback.txt", b"Take 0.5 mg once daily.\nAllergy: Penicillin", "text/plain")},
    ), 200)
    asr_doc_id = asr_txt["document_id"]
    ocr_doc_id = ocr_txt["document_id"]

    invalid_audio = client.post(
        "/api/transcribe",
        data={"customer_id": customer_a_id},
        files={"file": ("bad.exe", b"bad", "application/octet-stream")},
    )
    record(results, "asr_invalid_extension", invalid_audio, 415)

    empty_ocr = client.post(
        "/api/ocr",
        data={"customer_id": customer_a_id},
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    record(results, "ocr_empty_file", empty_ocr, 422)

    correction = client.patch(f"/api/documents/{asr_doc_id}/text", json={"corrected_text": "Take 0.5 mg once daily.", "reason": "Audit correction"})
    record(results, "document_text_correction", correction, 200)

    ocr_block_id = ocr_txt["pages"][0]["blocks"][0]["id"]
    ocr_correction = client.patch(f"/api/documents/{ocr_doc_id}/ocr-blocks/{ocr_block_id}", json={"corrected_text": "Take 0.5 mg once daily.", "reason": "Audit OCR correction"})
    record(results, "ocr_block_correction", ocr_correction, 200)

    combined = record(results, "combine_same_customer", client.post("/api/documents/combine", json={"customer_id": customer_a_id, "document_ids": [asr_doc_id, ocr_doc_id, doc_a_id]}), 200)
    combined_id = combined["document_id"]

    compare = client.post("/api/compare", json={"customer_id": customer_a_id, "document_ids": [asr_doc_id, ocr_doc_id]})
    record(results, "compare_numeric", compare, 200)

    review = record(results, "clinical_review", client.post("/api/clinical-review", json={"customer_id": customer_a_id, "document_ids": [combined_id], "note_type": "progress_note"}), 200)
    if review.get("issues"):
        issue_id = review["issues"][0]["id"]
        record(results, "issue_ignore_without_reason", client.post(f"/api/issues/{issue_id}/decision", json={"action": "ignore"}), 422)
        record(results, "issue_ignore_with_reason", client.post(f"/api/issues/{issue_id}/decision", json={"action": "ignore", "reason": "Audit reason"}), 200)
    else:
        results.append({"name": "issue_decision", "pass": False, "status_code": None, "body": "No issue produced"})

    task = record(results, "task_create", client.post("/api/tasks", json={"customer_id": customer_a_id, "document_id": combined_id, "task_text": "Audit task", "priority": "medium"}), 200)
    record(results, "task_complete", client.post(f"/api/tasks/{task['id']}/complete"), 200)

    for export_type, expected in [("txt", 200), ("json", 200), ("pdf", 200), ("srt", 422), ("vtt", 422)]:
        record(results, f"export_{export_type}", client.get(f"/api/documents/{combined_id}/export/{export_type}"), expected)
    record(results, "asr_export_srt", client.get(f"/api/documents/{asr_doc_id}/export/srt"), 200)
    record(results, "asr_export_vtt", client.get(f"/api/documents/{asr_doc_id}/export/vtt"), 200)
    record(results, "customer_report", client.get(f"/api/customers/{customer_a_id}/export/report"), 200)

    summary = {
        "total": len(results),
        "passed": sum(1 for item in results if item.get("pass")),
        "failed": [item for item in results if not item.get("pass")],
    }
    (API_EVIDENCE / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))
    return 0 if not summary["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

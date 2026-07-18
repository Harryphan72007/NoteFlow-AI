from __future__ import annotations


def test_customer_document_compare_clinical_task_export_workflow(client):
    customer_response = client.post(
        "/api/customers",
        json={"full_name": "Synthetic Patient", "date_of_birth": "1980-01-01", "allergies": "Penicillin"},
    )
    assert customer_response.status_code == 200
    customer_id = customer_response.json()["id"]

    doc_a = client.post(
        "/api/documents/manual",
        json={"customer_id": customer_id, "source_name": "Dictated note", "text": "Started amoxicillin. Will monitor tomorrow."},
    )
    assert doc_a.status_code == 200

    doc_b = client.post(
        "/api/documents/manual",
        json={"customer_id": customer_id, "source_name": "Scanned form", "text": "Allergy: Penicillin. Dose 0.5 mg."},
    )
    assert doc_b.status_code == 200

    ids = [doc_a.json()["document_id"], doc_b.json()["document_id"]]

    combined = client.post("/api/documents/combine", json={"customer_id": customer_id, "document_ids": ids})
    assert combined.status_code == 200
    assert "[manual_text - Dictated note]" in combined.json()["text"]

    compare = client.post("/api/compare", json={"customer_id": customer_id, "document_ids": ids})
    assert compare.status_code == 200
    assert "wer" in compare.json()

    review = client.post("/api/clinical-review", json={"customer_id": customer_id, "document_ids": ids, "note_type": "progress_note"})
    assert review.status_code == 200
    review_body = review.json()
    assert review_body["risk_level"] == "red"
    assert review_body["issues"]
    assert review_body["tasks"]

    issue_id = review_body["issues"][0]["id"]
    decision = client.post(f"/api/issues/{issue_id}/decision", json={"action": "ignore", "reason": "Synthetic test reason"})
    assert decision.status_code == 200
    assert decision.json()["status"] == "ignore"

    task_id = review_body["tasks"][0]["id"]
    completed = client.post(f"/api/tasks/{task_id}/complete")
    assert completed.status_code == 200
    assert completed.json()["status"] == "complete"

    export = client.get(f"/api/documents/{ids[0]}/export/txt")
    assert export.status_code == 200
    assert b"Started amoxicillin" in export.content


def test_cross_customer_combine_rejected(client):
    a = client.post("/api/customers", json={"full_name": "Patient A"}).json()["id"]
    b = client.post("/api/customers", json={"full_name": "Patient B"}).json()["id"]
    doc_a = client.post("/api/documents/manual", json={"customer_id": a, "text": "Note A"}).json()["document_id"]
    doc_b = client.post("/api/documents/manual", json={"customer_id": b, "text": "Note B"}).json()["document_id"]

    response = client.post("/api/documents/combine", json={"document_ids": [doc_a, doc_b]})

    assert response.status_code == 409


def test_text_fallback_ingestion_paths(client):
    customer_id = client.post("/api/customers", json={"full_name": "Fallback Patient"}).json()["id"]

    asr = client.post(
        "/api/transcribe",
        data={"customer_id": customer_id, "language": "en", "save_document": "true"},
        files={"file": ("note.txt", b"Patient denies chest pain.", "text/plain")},
    )
    assert asr.status_code == 200
    assert asr.json()["source_type"] == "audio"
    assert asr.json()["segments"]

    ocr = client.post(
        "/api/ocr",
        data={"customer_id": customer_id, "language": "en", "preprocess": "true", "save_document": "true"},
        files={"file": ("scan.txt", b"Temperature 39.1 C\nAllergy: Penicillin", "text/plain")},
    )
    assert ocr.status_code == 200
    assert ocr.json()["pages"][0]["blocks"]


def test_ignore_issue_requires_reason(client):
    customer_id = client.post("/api/customers", json={"full_name": "Reason Patient"}).json()["id"]
    doc_id = client.post("/api/documents/manual", json={"customer_id": customer_id, "text": "Started antibiotics."}).json()["document_id"]
    review = client.post("/api/clinical-review", json={"customer_id": customer_id, "document_ids": [doc_id]})
    issue_id = review.json()["issues"][0]["id"]

    response = client.post(f"/api/issues/{issue_id}/decision", json={"action": "ignore"})

    assert response.status_code == 422

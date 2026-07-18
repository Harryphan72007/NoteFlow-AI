from __future__ import annotations


def _customer(client, code: str) -> str:
    response = client.post("/api/customers", json={"customer_code": code, "full_name": f"{code} Patient"})
    assert response.status_code == 200
    return response.json()["id"]


def _manual_doc(client, customer_id: str, text: str = "Started amoxicillin.") -> str:
    response = client.post("/api/documents/manual", json={"customer_id": customer_id, "text": text})
    assert response.status_code == 200
    return response.json()["document_id"]


def test_invalid_email_is_rejected(client):
    response = client.post("/api/customers", json={"customer_code": "BAD-EMAIL", "full_name": "Bad Email", "email": "not-an-email"})

    assert response.status_code == 422


def test_wrong_customer_cannot_read_edit_delete_or_export_document(client):
    customer_a = _customer(client, "SEC-A")
    customer_b = _customer(client, "SEC-B")
    doc_b = _manual_doc(client, customer_b)

    assert client.get(f"/api/documents/{doc_b}", params={"customer_id": customer_a}).status_code == 403
    assert client.patch(f"/api/documents/{doc_b}", params={"customer_id": customer_a}, json={"status": "complete"}).status_code == 403
    assert client.patch(f"/api/documents/{doc_b}/text", params={"customer_id": customer_a}, json={"corrected_text": "No access"}).status_code == 403
    assert client.post(f"/api/documents/{doc_b}/finalize", params={"customer_id": customer_a}).status_code == 403
    assert client.get(f"/api/documents/{doc_b}/export/txt", params={"customer_id": customer_a}).status_code == 403
    assert client.delete(f"/api/documents/{doc_b}", params={"customer_id": customer_a}).status_code == 403

    owner_read = client.get(f"/api/documents/{doc_b}", params={"customer_id": customer_b})
    assert owner_read.status_code == 200


def test_wrong_customer_cannot_update_task_or_issue(client):
    customer_a = _customer(client, "SEC-TASK-A")
    customer_b = _customer(client, "SEC-TASK-B")
    doc_b = _manual_doc(client, customer_b, "Allergy: Penicillin. Started amoxicillin.")

    task = client.post("/api/tasks", json={"customer_id": customer_b, "document_id": doc_b, "task_text": "Task B"}).json()
    assert client.patch(f"/api/tasks/{task['id']}", params={"customer_id": customer_a}, json={"status": "complete"}).status_code == 403
    assert client.post(f"/api/tasks/{task['id']}/complete", params={"customer_id": customer_a}).status_code == 403
    assert client.delete(f"/api/tasks/{task['id']}", params={"customer_id": customer_a}).status_code == 403

    review = client.post("/api/clinical-review", json={"customer_id": customer_b, "document_ids": [doc_b]}).json()
    issue_id = review["issues"][0]["id"]
    assert client.post(f"/api/issues/{issue_id}/decision", params={"customer_id": customer_a}, json={"action": "resolve"}).status_code == 403
    assert client.post(f"/api/issues/{issue_id}/decision", params={"customer_id": customer_b}, json={"action": "resolve"}).status_code == 200


def test_customer_report_excludes_other_customer_records(client):
    customer_a = _customer(client, "SEC-REPORT-A")
    customer_b = _customer(client, "SEC-REPORT-B")
    doc_a = _manual_doc(client, customer_a, "Customer A private note.")
    doc_b = _manual_doc(client, customer_b, "Customer B private note.")

    report = client.get(f"/api/customers/{customer_a}/export/report")

    assert report.status_code == 200
    body = report.json()
    document_ids = {document["document_id"] for document in body["documents"]}
    assert doc_a in document_ids
    assert doc_b not in document_ids

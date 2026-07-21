from __future__ import annotations

from pathlib import Path
import io
import wave

from backend.app import models
from backend.app.config import settings


def test_save_document_false_does_not_create_document(client, monkeypatch):
    from backend.app.routes import processing
    customer = client.post("/api/customers", json={"full_name": "No Save Patient"}).json()
    monkeypatch.setattr(processing, "transcribe_audio", lambda *args, **kwargs: {"text": "temporary transcript", "model": "test"})
    response = client.post(
        "/api/transcribe",
        data={"customer_id": customer["id"], "language": "en", "save_document": "false"},
        files={"file": ("note.txt", b"temporary transcript", "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["saved"] is False
    assert client.get("/api/documents", params={"customer_id": customer["id"]}).json() == []


def test_failed_inference_removes_uploaded_file(client, monkeypatch):
    from backend.app.routes import processing
    from backend.app.services.asr import ASRServiceError

    monkeypatch.setattr(processing, "transcribe_audio", lambda *args, **kwargs: (_ for _ in ()).throw(ASRServiceError("test", "forced")))
    before = set((settings.upload_dir / "audio").glob("*"))
    stream = io.BytesIO()
    with wave.open(stream, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\x00\x00" * 160)
    response = client.post("/api/transcribe", files={"file": ("failure.wav", stream.getvalue(), "audio/wav")})
    assert response.status_code == 503
    assert set((settings.upload_dir / "audio").glob("*")) == before


def test_audio_upload_limit_is_100_mb_in_backend_and_frontend_copy():
    assert settings.asr_max_file_mb == 100
    app_source = Path(__file__).parents[2] / "Frontend" / "src" / "app" / "App.tsx"
    assert "up to 100 MB" in app_source.read_text(encoding="utf-8")


def test_scoped_token_cannot_forge_customer_id(client):
    customer_a = client.post("/api/customers", json={"full_name": "Scoped A"}).json()
    customer_b = client.post("/api/customers", json={"full_name": "Scoped B"}).json()
    register = client.post("/api/auth/register", json={"username": "scoped-a", "password": "password-a", "customer_id": customer_a["id"]})
    assert register.status_code == 200
    token = client.post("/api/auth/login", json={"username": "scoped-a", "password": "password-a"}).json()["access_token"]
    scoped = client.__class__(client.app)
    scoped.headers.update({"Authorization": f"Bearer {token}"})
    assert scoped.get("/api/customers/" + customer_b["id"]).status_code == 403
    assert scoped.get("/api/documents", params={"customer_id": customer_b["id"]}).status_code == 403

from __future__ import annotations

import json

from backend.app.services import ai_tools


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_ollama_status_reports_installed_and_loaded_model(monkeypatch):
    def fake_urlopen(url, timeout):
        assert timeout == 2
        if str(url).endswith("/api/tags"):
            return FakeResponse({"models": [{"name": "qwen3:4b"}]})
        return FakeResponse({"models": [{"model": "qwen3:4b"}]})

    monkeypatch.setattr(ai_tools.urllib.request, "urlopen", fake_urlopen)

    status = ai_tools.ollama_status()

    assert status["available"] is True
    assert status["model_available"] is True
    assert status["loaded"] is True
    assert status["keep_alive"] == ai_tools.settings.ollama_keep_alive


def test_ollama_status_does_not_claim_missing_model_is_available(monkeypatch):
    monkeypatch.setattr(
        ai_tools.urllib.request,
        "urlopen",
        lambda _url, timeout: FakeResponse({"models": [{"name": "another-model:latest"}]}),
    )

    status = ai_tools.ollama_status()

    assert status["available"] is True
    assert status["model_available"] is False
    assert status["loaded"] is False


def test_structured_generation_requests_keep_alive(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse({"message": {"content": '{"summary":"Source-faithful."}'}})

    monkeypatch.setattr(ai_tools.urllib.request, "urlopen", fake_urlopen)

    result = ai_tools.generate_structured_json(
        system_prompt="Summarize faithfully.",
        user_prompt="Patient is stable.",
        schema={"type": "object"},
    )

    assert result == {"summary": "Source-faithful."}
    assert captured["payload"]["keep_alive"] == ai_tools.settings.ollama_keep_alive
    assert captured["timeout"] == ai_tools.settings.ollama_timeout_seconds

from __future__ import annotations

import json
import urllib.error
import urllib.request

from ..config import settings
from .clinical import extract_tasks


def _ollama_json(path: str, *, timeout: float = 2) -> dict:
    with urllib.request.urlopen(f"{settings.ollama_base_url}{path}", timeout=timeout) as response:
        if response.status != 200:
            raise OSError(f"Ollama returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def _model_names(payload: dict) -> set[str]:
    return {
        str(model.get("model") or model.get("name"))
        for model in payload.get("models", [])
        if model.get("model") or model.get("name")
    }


def ollama_status() -> dict:
    try:
        installed = _model_names(_ollama_json("/api/tags"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return {
            "available": False,
            "model": settings.ollama_model,
            "model_available": False,
            "loaded": False,
            "base_url": settings.ollama_base_url,
            "keep_alive": settings.ollama_keep_alive,
        }

    try:
        loaded = _model_names(_ollama_json("/api/ps"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        loaded = set()

    return {
        "available": True,
        "model": settings.ollama_model,
        "model_available": settings.ollama_model in installed,
        "loaded": settings.ollama_model in loaded,
        "base_url": settings.ollama_base_url,
        "keep_alive": settings.ollama_keep_alive,
    }


def generate_structured_json(
    *,
    system_prompt: str,
    user_prompt: str,
    schema: dict,
) -> dict:
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "think": False,
        "keep_alive": settings.ollama_keep_alive,
        "format": schema,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": 0},
    }
    request = urllib.request.Request(
        f"{settings.ollama_base_url}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=settings.ollama_timeout_seconds) as response:
        envelope = json.loads(response.read().decode("utf-8"))
    content = envelope.get("message", {}).get("content", "")
    if not content.strip():
        raise ValueError("Ollama returned an empty structured response")
    return strict_json_or_error(content)


def summarize_locally(text: str) -> dict:
    sentences = [part.strip() for part in text.replace("\n", " ").split(".") if part.strip()]
    summary = ". ".join(sentences[:3])
    if summary:
        summary += "."
    return {"summary": summary, "model": "deterministic-local-fallback"}


def key_points_locally(text: str) -> dict:
    points = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
    if not points:
        points = [part.strip() for part in text.split(".") if part.strip()]
    return {"key_points": points[:10], "model": "deterministic-local-fallback"}


def tasks_locally(text: str) -> dict:
    return {"tasks": extract_tasks(text), "model": "deterministic-local-fallback"}


def translate_locally(text: str, target_language: str | None) -> dict:
    return {
        "translated_text": text,
        "target_language": target_language,
        "warning": "Local deterministic fallback does not translate; configure Ollama for translation.",
        "model": "deterministic-local-fallback",
    }


def strict_json_or_error(raw: str) -> dict:
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object")
    return parsed

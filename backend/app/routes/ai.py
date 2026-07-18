from __future__ import annotations

from fastapi import APIRouter

from ..schemas import AITextRequest
from ..services.ai_tools import key_points_locally, summarize_locally, tasks_locally, translate_locally


router = APIRouter(prefix="/ai", tags=["ai-tools"])


@router.post("/summarize")
def summarize(payload: AITextRequest):
    return summarize_locally(payload.text)


@router.post("/translate")
def translate(payload: AITextRequest):
    return translate_locally(payload.text, payload.target_language)


@router.post("/key-points")
def key_points(payload: AITextRequest):
    return key_points_locally(payload.text)


@router.post("/tasks")
def tasks(payload: AITextRequest):
    return tasks_locally(payload.text)


@router.post("/format-note")
def format_note(payload: AITextRequest):
    return {"formatted_note": payload.text.strip(), "model": "deterministic-local-fallback"}

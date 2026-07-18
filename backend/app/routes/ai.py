from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import AITextRequest
from ..config import settings
from ..services.ai_tools import generate_structured_json


router = APIRouter(prefix="/ai", tags=["ai-tools"])


def _structured(payload: AITextRequest, *, system_prompt: str, schema: dict) -> dict:
    try:
        result = generate_structured_json(
            system_prompt=system_prompt,
            user_prompt=payload.text,
            schema=schema,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Ollama structured generation failed: {exc}") from exc
    return {**result, "model": settings.ollama_model}


@router.post("/summarize")
def summarize(payload: AITextRequest):
    return _structured(
        payload,
        system_prompt="Summarize the clinical text faithfully. Do not invent facts. Return the required JSON schema.",
        schema={
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"],
            "additionalProperties": False,
        },
    )


@router.post("/translate")
def translate(payload: AITextRequest):
    target = payload.target_language or "English"
    return _structured(
        payload,
        system_prompt=f"Translate the clinical text to {target} without adding or removing facts. Return the required JSON schema.",
        schema={
            "type": "object",
            "properties": {
                "translated_text": {"type": "string"},
                "target_language": {"type": "string"},
            },
            "required": ["translated_text", "target_language"],
            "additionalProperties": False,
        },
    )


@router.post("/key-points")
def key_points(payload: AITextRequest):
    return _structured(
        payload,
        system_prompt="Extract concise clinical key points using only the supplied text. Return the required JSON schema.",
        schema={
            "type": "object",
            "properties": {"key_points": {"type": "array", "items": {"type": "string"}, "maxItems": 10}},
            "required": ["key_points"],
            "additionalProperties": False,
        },
    )


@router.post("/tasks")
def tasks(payload: AITextRequest):
    return _structured(
        payload,
        system_prompt="Extract explicit follow-up tasks only. Do not invent treatment. Return the required JSON schema.",
        schema={
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "maxItems": 10,
                    "items": {
                        "type": "object",
                        "properties": {
                            "task_text": {"type": "string"},
                            "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]},
                            "evidence": {"type": "string"},
                        },
                        "required": ["task_text", "priority", "evidence"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["tasks"],
            "additionalProperties": False,
        },
    )


@router.post("/format-note")
def format_note(payload: AITextRequest):
    return _structured(
        payload,
        system_prompt="Format the supplied clinical text clearly without changing clinical meaning. Return the required JSON schema.",
        schema={
            "type": "object",
            "properties": {"formatted_note": {"type": "string"}},
            "required": ["formatted_note"],
            "additionalProperties": False,
        },
    )

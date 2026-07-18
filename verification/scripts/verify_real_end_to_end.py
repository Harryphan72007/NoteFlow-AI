from __future__ import annotations

import sys
import json
import urllib.request
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.main import app


ASR_SAMPLE = Path(r"D:\Mega-ASR\Mega-ASR\assets\example.wav")
OCR_SAMPLE = ROOT / "repair" / "logs" / "phase2_ocr_sample.png"


def require_ok(response, step: str) -> dict:
    print(f"{step}_STATUS={response.status_code}")
    if response.status_code != 200:
        raise SystemExit(f"{step} failed: {response.text}")
    return response.json()


def unload_ollama() -> None:
    request = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps({"model": "qwen3:4b", "keep_alive": 0}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"OLLAMA_UNLOAD_STATUS={response.status}")
    except Exception as exc:
        print(f"OLLAMA_UNLOAD_WARNING={exc}")


def main() -> None:
    unload_ollama()
    if not ASR_SAMPLE.exists():
        candidates = list(Path(r"D:\Mega-ASR\Mega-ASR").rglob("*.wav"))
        if not candidates:
            raise SystemExit("No bundled Mega-ASR WAV sample found")
        audio_path = candidates[0]
    else:
        audio_path = ASR_SAMPLE
    if not OCR_SAMPLE.exists():
        raise SystemExit(f"OCR sample is missing: {OCR_SAMPLE}")

    with TestClient(app) as client:
        customer = require_ok(
            client.post("/api/customers", json={"full_name": "Real Integration Verification"}),
            "CUSTOMER_CREATE",
        )
        customer_id = customer["id"]
        print(f"CUSTOMER_ID={customer_id}")

        transcript = require_ok(
            client.post(
                "/api/transcribe",
                data={"customer_id": customer_id, "language": "en", "save_document": "true"},
                files={"file": (audio_path.name, audio_path.read_bytes(), "audio/wav")},
            ),
            "REAL_ASR",
        )
        if not transcript.get("text") or not transcript.get("metadata", {}).get("real_inference"):
            raise SystemExit("ASR response was empty or not marked as real inference")
        print(f"REAL_ASR_TEXT={transcript['text']}")

        ocr = require_ok(
            client.post(
                "/api/ocr",
                data={"customer_id": customer_id, "language": "en", "preprocess": "true", "save_document": "true"},
                files={"file": (OCR_SAMPLE.name, OCR_SAMPLE.read_bytes(), "image/png")},
            ),
            "REAL_OCR",
        )
        if "amoxicillin" not in ocr.get("text", "").lower() or not ocr.get("pages"):
            raise SystemExit("OCR response omitted expected clinical text or OCR pages")
        print(f"REAL_OCR_TEXT={ocr['text']}")

        combined_text = f"Audio transcript: {transcript['text']}\nCompanion document: {ocr['text']}"
        structured = require_ok(
            client.post("/api/ai/key-points", json={"text": combined_text}),
            "REAL_OLLAMA",
        )
        if structured.get("model") is None or not isinstance(structured.get("key_points"), list):
            raise SystemExit("Ollama structured analysis was not returned")
        print(f"REAL_OLLAMA_RESULT={structured}")

        combined = require_ok(
            client.post(
                "/api/documents/combine",
                json={
                    "document_ids": [transcript["document_id"], ocr["document_id"]],
                    "customer_id": customer_id,
                    "source_name": "Real ASR and OCR evidence",
                },
            ),
            "COMBINE",
        )
        review = require_ok(
            client.post(
                "/api/clinical-review",
                json={"document_ids": [combined["document_id"]], "customer_id": customer_id, "note_type": "progress_note"},
            ),
            "RISK_REVIEW",
        )
        if review.get("risk_score") is None or not review.get("risk_level"):
            raise SystemExit("Clinical review returned no risk score")
        print(f"RISK_RESULT={{'risk_level': '{review['risk_level']}', 'risk_score': {review['risk_score']}}}")

        note_text = "\n".join(structured["key_points"]) or combined_text
        note = require_ok(
            client.post(
                "/api/documents/manual",
                json={
                    "customer_id": customer_id,
                    "source_name": "Real Integration Clinical Note",
                    "text": note_text,
                    "language": "en",
                },
            ),
            "NOTE_CREATE",
        )
        listed = require_ok(client.get(f"/api/documents?customer_id={customer_id}"), "NOTE_LIST")
        if not any(item["document_id"] == note["document_id"] for item in listed):
            raise SystemExit("Created note is not visible through the frontend document API")
        print(f"NOTE_DOCUMENT_ID={note['document_id']}")
        print("REAL_END_TO_END_WORKFLOW=PASS")


if __name__ == "__main__":
    main()

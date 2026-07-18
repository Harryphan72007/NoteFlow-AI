from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.main import app


SAMPLE = Path("D:/Mega-ASR/Mega-ASR/assets/example/F01_22GC010K_STR.wav")


def main() -> None:
    if not SAMPLE.exists():
        raise SystemExit(f"Mega-ASR sample is missing: {SAMPLE}")
    with TestClient(app) as client:
        response = client.post(
            "/api/transcribe",
            data={"language": "en", "save_document": "false"},
            files={"file": (SAMPLE.name, SAMPLE.read_bytes(), "audio/wav")},
        )
    print(f"BACKEND_ASR_STATUS={response.status_code}")
    if response.status_code != 200:
        raise SystemExit(f"Backend ASR endpoint failed: {response.text}")
    body = response.json()
    print(f"BACKEND_ASR_TEXT={body['text']}")
    print(f"BACKEND_ASR_METADATA={body['metadata']}")
    if not body["text"].strip():
        raise SystemExit("Backend ASR endpoint returned an empty transcript")
    if not body["metadata"].get("real_inference"):
        raise SystemExit("Backend ASR endpoint did not mark real inference")
    if not body.get("segments"):
        raise SystemExit("Backend ASR endpoint returned no persisted segment")
    print("REAL_BACKEND_ASR_TEST=PASS")


if __name__ == "__main__":
    main()

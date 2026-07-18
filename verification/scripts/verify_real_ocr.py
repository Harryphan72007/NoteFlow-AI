from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient
from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.main import app
from backend.app.config import settings
from backend.app.services.metrics import character_error_rate, word_error_rate


OUTPUT_DIR = ROOT / "repair" / "logs"
SAMPLE_PATH = OUTPUT_DIR / "phase2_ocr_sample.png"
REFERENCE_TEXT = "Patient: Jane Doe Medication: Amoxicillin 500 mg Allergy: Penicillin"


def create_sample() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1500, 520), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 52)
    lines = (
        "Patient: Jane Doe",
        "Medication: Amoxicillin 500 mg",
        "Allergy: Penicillin",
    )
    for index, line in enumerate(lines):
        draw.text((70, 65 + index * 135), line, fill="black", font=font)
    image.save(SAMPLE_PATH)


def main() -> None:
    create_sample()
    engine = PaddleOCR(
        lang="en",
        enable_mkldnn=False,
        text_detection_model_dir=str(settings.ocr_detection_model_dir),
        text_recognition_model_dir=str(settings.ocr_recognition_model_dir),
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    results = list(engine.predict(input=str(SAMPLE_PATH)))
    texts: list[str] = []
    scores: list[float] = []
    for result in results:
        payload = result.json["res"]
        texts.extend(str(value) for value in payload.get("rec_texts", []))
        scores.extend(float(value) for value in payload.get("rec_scores", []))

    extracted = " ".join(texts).strip()
    print(f"SAMPLE_IMAGE={SAMPLE_PATH}")
    print(f"OCR_TEXT={extracted}")
    print(f"OCR_SCORES={scores}")
    if not extracted:
        raise SystemExit("OCR returned no text")
    normalized = extracted.lower()
    expected = ("patient", "amoxicillin", "penicillin")
    missing = [term for term in expected if term not in normalized]
    if missing:
        raise SystemExit(f"OCR output missed expected terms: {missing}")
    wer = word_error_rate(REFERENCE_TEXT, extracted)
    cer = character_error_rate(REFERENCE_TEXT.lower(), extracted.lower())
    print(f"OCR_WER={wer:.6f}")
    print(f"OCR_CER={cer:.6f}")
    if wer > 0.05 or cer > 0.05:
        raise SystemExit(f"OCR accuracy threshold failed: WER={wer:.4f}, CER={cer:.4f}")
    print("MEDICAL_OCR_ACCURACY_TEST=PASS")
    print("REAL_OCR_TEST=PASS")

    with TestClient(app) as client:
        response = client.post(
            "/api/ocr",
            data={"language": "en", "preprocess": "true", "save_document": "false"},
            files={"file": (SAMPLE_PATH.name, SAMPLE_PATH.read_bytes(), "image/png")},
        )
    print(f"BACKEND_OCR_STATUS={response.status_code}")
    if response.status_code != 200:
        raise SystemExit(f"Backend OCR endpoint failed: {response.text}")
    body = response.json()
    print(f"BACKEND_OCR_TEXT={body['text']}")
    if not body.get("pages") or not body["pages"][0].get("blocks"):
        raise SystemExit("Backend OCR endpoint returned no persisted OCR blocks")
    if "amoxicillin" not in body["text"].lower():
        raise SystemExit("Backend OCR endpoint omitted expected text")
    print("REAL_BACKEND_OCR_TEST=PASS")


if __name__ == "__main__":
    main()

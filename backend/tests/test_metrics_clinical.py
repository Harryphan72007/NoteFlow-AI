from __future__ import annotations

from backend.app.services.clinical import run_clinical_review
from backend.app.services.metrics import character_error_rate, compare_texts, word_error_rate


def test_error_rates_detect_dose_change():
    reference = "Take 0.5 mg once daily."
    hypothesis = "Take 5 mg once daily."

    assert word_error_rate(reference, reference) == 0
    assert character_error_rate(reference, reference) == 0

    result = compare_texts(reference, hypothesis)

    assert result["wer"] > 0
    assert result["cer"] > 0
    assert result["mismatches"][0]["reference"] == "0.5 mg"
    assert result["mismatches"][0]["hypothesis"] == "5 mg"


def test_clinical_review_flags_missing_medication_details_and_allergy_conflict():
    text = "Allergy: Penicillin. Started amoxicillin. Will monitor tomorrow."

    result = run_clinical_review(text, note_type="progress_note")

    issue_types = {issue["issue_type"] for issue in result["issues"]}
    assert result["risk_level"] == "red"
    assert "possible_allergy_conflict" in issue_types
    assert "missing_medication_dose" in issue_types
    assert "missing_medication_route" in issue_types
    assert result["tasks"]

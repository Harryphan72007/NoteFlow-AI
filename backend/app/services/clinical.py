from __future__ import annotations

import re
from dataclasses import dataclass, field


NEGATED_CHEST_PAIN = re.compile(r"\b(denies|deny|no)\s+(?:current\s+)?chest pain\b", re.IGNORECASE)
POSITIVE_CHEST_PAIN = re.compile(r"\b(chief complaint[:\s-]*)?chest pain\b", re.IGNORECASE)
ALLERGY_RE = re.compile(r"\b(allerg(?:y|ies)|allergic)\b[^.\n;:]*[:\s-]*([A-Za-z][A-Za-z -]+)?", re.IGNORECASE)
NO_KNOWN_ALLERGIES_RE = re.compile(r"\b(no known allergies|nka|nkda)\b", re.IGNORECASE)
MED_ACTION_RE = re.compile(r"\b(start|started|continue|continued|stop|stopped|prescribe|prescribed|give|given)\b\s+([A-Za-z][A-Za-z-]+)?", re.IGNORECASE)
DOSE_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(mg|mcg|g|ml|units?)\b", re.IGNORECASE)
ROUTE_RE = re.compile(r"\b(po|iv|im|subcut|oral|intravenous|intramuscular)\b", re.IGNORECASE)
FREQ_RE = re.compile(r"\b(qd|bid|tid|qid|daily|twice daily|three times daily|every\s+\d+\s+hours?)\b", re.IGNORECASE)
DURATION_RE = re.compile(r"\b(for\s+\d+\s+(days?|weeks?)|\d+\s+(days?|weeks?))\b", re.IGNORECASE)
FOLLOW_UP_RE = re.compile(r"\b(follow[- ]?up|reassess|review|repeat|monitor|check|return)\b", re.IGNORECASE)
CRITICAL_TERMS_RE = re.compile(r"\b(medication|dose|allerg|penicillin|amoxicillin|insulin|warfarin)\b", re.IGNORECASE)


@dataclass
class Issue:
    issue_type: str
    severity: str
    title: str
    message: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str | None = None


def extract_tasks(text: str) -> list[dict[str, str]]:
    tasks = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
        clean = sentence.strip()
        if clean and FOLLOW_UP_RE.search(clean):
            tasks.append({"task_text": clean, "priority": "medium", "evidence": clean})
    return tasks[:20]


def run_clinical_review(text: str, *, note_type: str = "progress_note", low_confidence_evidence: list[str] | None = None) -> dict:
    issues: list[Issue] = []
    text_l = text.lower()

    has_allergy = bool(ALLERGY_RE.search(text) or NO_KNOWN_ALLERGIES_RE.search(text))
    if not has_allergy:
        issues.append(Issue(
            "missing_allergy_information",
            "critical",
            "Allergy status missing",
            "Allergy status was not found in the selected document text.",
            [],
            "Document allergy status before finalization.",
        ))

    med_match = MED_ACTION_RE.search(text)
    has_medication_action = bool(med_match)
    if has_medication_action:
        evidence = [med_match.group(0)]
        if not med_match.group(2):
            issues.append(Issue("missing_medication_name", "high", "Medication name missing", "A medication action is documented without a clear medication name.", evidence, "Specify the medication name or verify the source text."))
        if not DOSE_RE.search(text):
            issues.append(Issue("missing_medication_dose", "high", "Medication dose missing", "A medication is documented without a dose.", evidence, "Document the medication dose if clinically intended."))
        if not ROUTE_RE.search(text):
            issues.append(Issue("missing_medication_route", "high", "Medication route missing", "A medication is documented without a route.", evidence, "Document the medication route."))
        if not FREQ_RE.search(text):
            issues.append(Issue("missing_medication_frequency", "high", "Medication frequency missing", "A medication is documented without a frequency.", evidence, "Document the medication frequency."))
        if not DURATION_RE.search(text):
            issues.append(Issue("missing_medication_duration", "medium", "Medication duration missing", "A medication is documented without a duration.", evidence, "Document duration or clarify that duration is not applicable."))

    if "amoxicillin" in text_l and "penicillin" in text_l and not NO_KNOWN_ALLERGIES_RE.search(text):
        issues.append(Issue(
            "possible_allergy_conflict",
            "critical",
            "Possible allergy conflict",
            "Amoxicillin appears in the document while penicillin allergy information is also present.",
            ["amoxicillin", "penicillin"],
            "Verify the medication plan against documented allergy information.",
        ))

    if NEGATED_CHEST_PAIN.search(text) and POSITIVE_CHEST_PAIN.search(NEGATED_CHEST_PAIN.sub("", text)):
        issues.append(Issue(
            "possible_symptom_contradiction",
            "high",
            "Possible chest pain inconsistency",
            "Chest pain appears as both present and denied in the selected text.",
            ["chest pain", "denies chest pain"],
            "Verify the current patient status and source timing.",
        ))

    if note_type in {"progress_note", "discharge_summary", "discharge"} and not FOLLOW_UP_RE.search(text):
        issues.append(Issue(
            "missing_follow_up_or_reassessment",
            "medium",
            "Follow-up or reassessment missing",
            "No follow-up, reassessment, monitoring, or review task was found.",
            [],
            "Document follow-up, reassessment time, or monitoring instructions if applicable.",
        ))

    for evidence in low_confidence_evidence or []:
        severity = "critical" if CRITICAL_TERMS_RE.search(evidence) else "medium"
        issues.append(Issue(
            "low_confidence_source_text",
            severity,
            "Low-confidence source text",
            "A clinically relevant source field has low OCR or ASR confidence.",
            [evidence],
            "Manually verify the highlighted source region before final approval.",
        ))

    score = 0
    weights = {"critical": 40, "high": 20, "medium": 10, "low": 3}
    components = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in issues:
        score += weights.get(issue.severity, 5)
        components[issue.severity] = components.get(issue.severity, 0) + weights.get(issue.severity, 5)

    if any(issue.issue_type == "low_confidence_source_text" and issue.severity == "critical" for issue in issues):
        risk_level = "blocked"
    elif score >= 60 or any(issue.severity == "critical" for issue in issues):
        risk_level = "red"
    elif score >= 15:
        risk_level = "yellow"
    else:
        risk_level = "green"

    return {
        "risk_level": risk_level,
        "risk_score": score,
        "score_components": components,
        "issues": [issue.__dict__ for issue in issues],
        "tasks": extract_tasks(text),
        "summary": "Documentation-support review only. Clinician approval is required before use.",
    }

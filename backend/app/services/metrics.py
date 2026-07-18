from __future__ import annotations

import re
from dataclasses import dataclass


TOKEN_RE = re.compile(r"[A-Za-z0-9.]+|[^\sA-Za-z0-9]", re.UNICODE)
NUMBER_RE = re.compile(r"(?<!\w)(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|l|mmhg|bpm|c|%|units?)?", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def levenshtein(a: list[str] | str, b: list[str] | str) -> int:
    seq_a = list(a)
    seq_b = list(b)
    previous = list(range(len(seq_b) + 1))
    for i, ca in enumerate(seq_a, start=1):
        current = [i]
        for j, cb in enumerate(seq_b, start=1):
            cost = 0 if ca == cb else 1
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost))
        previous = current
    return previous[-1]


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref = tokenize(reference)
    hyp = tokenize(hypothesis)
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein(ref, hyp) / len(ref)


def character_error_rate(reference: str, hypothesis: str) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return levenshtein(reference, hypothesis) / len(reference)


@dataclass
class TextDiff:
    missing_words: list[str]
    extra_words: list[str]
    replacements: list[dict[str, str]]


def simple_diff(reference: str, hypothesis: str) -> TextDiff:
    ref_tokens = tokenize(reference)
    hyp_tokens = tokenize(hypothesis)
    missing = []
    extra = []
    replacements = []
    max_len = max(len(ref_tokens), len(hyp_tokens))
    for idx in range(max_len):
        ref = ref_tokens[idx] if idx < len(ref_tokens) else None
        hyp = hyp_tokens[idx] if idx < len(hyp_tokens) else None
        if ref is None and hyp is not None:
            extra.append(hyp)
        elif hyp is None and ref is not None:
            missing.append(ref)
        elif ref != hyp and ref is not None and hyp is not None:
            replacements.append({"reference": ref, "hypothesis": hyp})
    return TextDiff(missing[:50], extra[:50], replacements[:50])


def numerical_mismatches(reference: str, hypothesis: str) -> list[dict[str, str]]:
    ref_numbers = NUMBER_RE.findall(reference)
    hyp_numbers = NUMBER_RE.findall(hypothesis)
    mismatches = []
    for idx, ref in enumerate(ref_numbers):
        if idx >= len(hyp_numbers):
            mismatches.append({"type": "missing_number", "reference": " ".join(ref).strip(), "hypothesis": ""})
            continue
        hyp = hyp_numbers[idx]
        if ref != hyp:
            mismatches.append({"type": "numerical_or_unit_mismatch", "reference": " ".join(ref).strip(), "hypothesis": " ".join(hyp).strip()})
    for hyp in hyp_numbers[len(ref_numbers):]:
        mismatches.append({"type": "extra_number", "reference": "", "hypothesis": " ".join(hyp).strip()})
    return mismatches


def compare_texts(reference: str, hypothesis: str) -> dict:
    diff = simple_diff(reference, hypothesis)
    return {
        "wer": word_error_rate(reference, hypothesis),
        "cer": character_error_rate(reference, hypothesis),
        "missing_words": diff.missing_words,
        "extra_words": diff.extra_words,
        "replacements": diff.replacements,
        "mismatches": numerical_mismatches(reference, hypothesis),
    }


import re
from typing import Dict, List

from app.linguistics.normalizer import tokenize, normalize_roman_telugu


QUESTION_WORDS = {
    "ఏంటి": "what",
    "ఏమిటి": "what",
    "ఏం": "what",
    "ఎందుకు": "why",
    "ఎందుక": "why",
    "ఎలా": "how",
    "ఎక్కడ": "where",
    "ఎప్పుడు": "when",
    "ఎవరు": "who",
    "ఎవరూ": "who",
    "ఎంత": "how_much",
    "ఎన్ని": "how_many",
}


def detect_sentence_force(text: str) -> str:
    value = normalize_roman_telugu(text).strip().lower()
    if "?" in value or "？" in value:
        return "question"
    if any(value.startswith(x) for x in ("చెప్పు", "చూడి", "వెళ్ళు", "రా", "వెళ్ళండి")):
        return "request_or_command"
    if any(x in value for x in ("లేదా", "కానీ", "అయితే")):
        return "statement_with_relation"
    return "statement_or_fragment"


def detect_question_type(text: str) -> str:
    value = normalize_roman_telugu(text)
    for word, kind in QUESTION_WORDS.items():
        if word in value:
            return kind
    return "unknown"


def extract_linguistic_hints(text: str) -> Dict:
    normalized = normalize_roman_telugu(text)
    toks = tokenize(normalized)
    return {
        "normalized": normalized,
        "token_count": len(toks),
        "sentence_force": detect_sentence_force(text),
        "question_type": detect_question_type(text),
        "tokens": toks,
        "negation_hint": any(x in normalized for x in ("లేదు", "కాదు", "వద్దు", "లేను", "లేవు")),
        "first_person_hint": any(x in normalized for x in ("నేను", "నాకు", "నా")),
        "second_person_hint": any(x in normalized for x in ("నువ్వు", "నీకు", "నీ")),
    }


def analyze_word_surface(word: str) -> Dict:
    # Lightweight morphological clues. It deliberately avoids claiming
    # a full grammatical parse when evidence is insufficient.
    suffixes = [
        "లతో", "లలో", "లకు", "లను", "లని", "లపై", "నుంచి", "నుండి",
        "యొక్క", "తో", "లో", "లు", "ను", "ని", "కు", "కి", "గా",
        "పై", "కోసం", "వల్ల", "మధ్య", "గురించి",
    ]
    for suffix in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            return {
                "surface": word,
                "base_candidate": word[:-len(suffix)],
                "case_or_suffix_hint": suffix,
            }
    return {"surface": word, "base_candidate": word, "case_or_suffix_hint": None}

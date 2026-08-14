
import re
from typing import Dict, List


TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]+")
TOKEN_RE = re.compile(r"[\u0C00-\u0C7F]+|[A-Za-z]+(?:['’-][A-Za-z]+)*")


ROMAN_TELUGU = {
    "hi": "హాయ్",
    "hello": "హలో",
    "hey": "హే",
    "haa": "హా",
    "haaa": "హా",
    "avunu": "అవును",
    "sare": "సరే",
    "ok": "ఓకే",
    "okay": "ఓకే",
    "cheppu": "చెప్పు",
    "em": "ఏం",
    "enti": "ఏంటి",
    "emiti": "ఏమిటి",
    "emle": "ఏంలేదు",
    "emledu": "ఏంలేదు",
    "emledhu": "ఏంలేదు",
    "nenu": "నేను",
    "nuvvu": "నువ్వు",
    "nuvu": "నువ్వు",
    "meeru": "మీరు",
    "ela": "ఎలా",
    "elaunnav": "ఎలా ఉన్నావు",
    "ela unnava": "ఎలా ఉన్నావు",
    "baaunna": "బాగున్నా",
    "baagunna": "బాగున్నా",
    "baaunnanu": "బాగున్నాను",
    "baagunnanu": "బాగున్నాను",
    "inka": "ఇంకా",
    "ledu": "లేదు",
    "ledhu": "లేదు",
    "thanks": "ధన్యవాదాలు",
    "thankyou": "ధన్యవాదాలు",
    "thank you": "ధన్యవాదాలు",
}


def normalize_roman_telugu(text: str) -> str:
    text = str(text or "").strip()
    if not text:
        return ""
    if TELUGU_RE.search(text):
        return text
    value = re.sub(r"\s+", " ", text.lower())
    for source in sorted(ROMAN_TELUGU, key=len, reverse=True):
        value = re.sub(
            r"(?<![a-z])" + re.escape(source) + r"(?![a-z])",
            ROMAN_TELUGU[source],
            value,
            flags=re.I,
        )
    return value


def tokens(text: str) -> List[str]:
    return TOKEN_RE.findall(text or "")


def is_short_input(text: str) -> bool:
    return len(tokens(text)) <= 3


def detect_language_signals(text: str) -> Dict[str, object]:
    normalized = normalize_roman_telugu(text)
    return {
        "raw": text.strip(),
        "normalized": normalized,
        "has_telugu_script": bool(TELUGU_RE.search(text or "")),
        "is_short": is_short_input(text),
    }

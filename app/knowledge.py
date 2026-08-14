
import json
import os
import re
from functools import lru_cache
from typing import Any, Dict, List


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOCAB_FILE = os.path.join(BASE, "data", "vocabulary.json")


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def split_forms(value: Any) -> List[str]:
    if isinstance(value, list):
        raw = value
    else:
        raw = re.split(r"\s*(?:,|/|;|\|)\s*", str(value or ""))
    return [normalize(x) for x in raw if normalize(x)]


@lru_cache(maxsize=1)
def load_vocabulary() -> List[Dict[str, Any]]:
    if not os.path.exists(VOCAB_FILE):
        return []
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in ("vocabulary", "words", "entries", "data"):
            if isinstance(data.get(key), list):
                return [x for x in data[key] if isinstance(x, dict)]
    return []


def entry_text(entry: Dict[str, Any]) -> str:
    values = []
    for key in (
        "standard", "melimi", "note", "meaning", "definition",
        "english", "gloss", "description", "example", "examples",
        "tags", "category", "related", "synonyms"
    ):
        value = entry.get(key, "")
        if isinstance(value, list):
            values.extend(map(str, value))
        elif isinstance(value, dict):
            values.extend(map(str, value.values()))
        else:
            values.append(str(value))
    return normalize(" ".join(values))


def retrieve(message: str, limit: int = 20) -> List[Dict[str, Any]]:
    query = normalize(message)
    if not query:
        return []

    qwords = set(re.findall(r"[\u0C00-\u0C7F]+|[A-Za-z]+", query))
    scored = []

    for i, entry in enumerate(load_vocabulary()):
        standards = split_forms(entry.get("standard", ""))
        melimis = split_forms(entry.get("melimi", ""))
        searchable = entry_text(entry)
        score = 0

        for form in standards:
            if form and form in query:
                score += 350 + len(form)
        for form in melimis:
            if form and form in query:
                score += 400 + len(form)
        for word in qwords:
            if len(word) >= 2 and word in searchable:
                score += 8

        if score:
            scored.append((score, i, entry))

    scored.sort(key=lambda x: (-x[0], x[1]))
    return [x[2] for x in scored[:limit]]


def format_knowledge(entries: List[Dict[str, Any]], max_chars: int = 5500) -> str:
    lines = ["RELEVANT MELIMI LANGUAGE KNOWLEDGE:"]
    for entry in entries:
        standard = str(entry.get("standard", "")).strip()
        melimi = str(entry.get("melimi", "")).strip()
        note = str(entry.get("note", "")).strip()
        if not standard and not melimi:
            continue
        line = f"- standard/concept: {standard} | Melimi: {melimi}"
        if note:
            line += f" | note: {note}"
        lines.append(line)
        if len("\n".join(lines)) >= max_chars:
            break
    return "\n".join(lines)[:max_chars]


def find_standard_terms(text: str, limit: int = 30) -> List[Dict[str, Any]]:
    query = normalize(text)
    found = []
    for entry in load_vocabulary():
        standards = split_forms(entry.get("standard", ""))
        melimis = split_forms(entry.get("melimi", ""))
        if not standards or not melimis:
            continue
        if any(s and s in query for s in standards):
            if not any(m and m in query for m in melimis):
                found.append(entry)
        if len(found) >= limit:
            break
    return found


def audit_melimi(text: str) -> Dict[str, Any]:
    matches = find_standard_terms(text)
    return {
        "possible_standard_terms_with_known_melimi": len(matches),
        "items": [
            {
                "standard": str(x.get("standard", "")).strip(),
                "melimi": str(x.get("melimi", "")).strip(),
            }
            for x in matches[:12]
        ],
        "warning": bool(matches),
    }

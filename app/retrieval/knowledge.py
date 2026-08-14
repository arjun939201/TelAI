
import json
import os
import re
from functools import lru_cache
from typing import Any, Dict, List


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOCAB_FILE = os.path.join(ROOT, "data", "vocabulary.json")


def norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


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


def fields(entry: Dict) -> str:
    values = []
    for key in (
        "standard", "melimi", "note", "meaning", "definition",
        "english", "gloss", "description", "example", "examples",
        "category", "tags", "related", "synonyms",
    ):
        value = entry.get(key, "")
        if isinstance(value, list):
            values.extend(str(v) for v in value)
        elif isinstance(value, dict):
            values.extend(str(v) for v in value.values())
        else:
            values.append(str(value))
    return norm(" ".join(values))


def retrieve(text: str, limit: int = 24) -> List[Dict]:
    query = norm(text)
    if not query:
        return []
    qwords = set(re.findall(r"[\u0C00-\u0C7F]+|[A-Za-z]+", query))
    scored = []

    for index, entry in enumerate(load_vocabulary()):
        standard = norm(entry.get("standard", ""))
        melimi = norm(entry.get("melimi", ""))
        searchable = fields(entry)
        score = 0

        if standard and standard in query:
            score += 300 + len(standard)
        if melimi and melimi in query:
            score += 350 + len(melimi)

        for word in qwords:
            if len(word) >= 2 and word in searchable:
                score += 5

        if score:
            scored.append((score, index, entry))

    scored.sort(key=lambda x: (-x[0], x[1]))
    return [item[2] for item in scored[:limit]]


def format_knowledge(entries: List[Dict], max_chars: int = 6000) -> str:
    lines = [
        "RELEVANT MELIMI LANGUAGE KNOWLEDGE:",
        "These entries are linguistic evidence, NOT response templates.",
    ]
    for entry in entries:
        standard = str(entry.get("standard", "")).strip()
        melimi = str(entry.get("melimi", "")).strip()
        note = str(entry.get("note", "")).strip()
        if not standard and not melimi:
            continue
        line = f"- {standard} → {melimi}"
        if note:
            line += f" ({note})"
        lines.append(line)
        if len("\n".join(lines)) >= max_chars:
            break
    return "\n".join(lines)[:max_chars]

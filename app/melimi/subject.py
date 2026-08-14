
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = ROOT / "melimi_telugu"
TEXT_EXTENSIONS = {".md", ".txt"}
DATA_EXTENSIONS = {".json", ".csv"}


@dataclass
class LanguageDocument:
    path: str
    kind: str
    text: str
    entries: list[dict[str, Any]]


def _stringify(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_stringify(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_stringify(v) for v in value)
    return str(value or "")


def _read_json(path: Path) -> tuple[str, list[dict[str, Any]]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "", []
    if isinstance(data, list):
        entries = [x for x in data if isinstance(x, dict)]
        return _stringify(data), entries
    if isinstance(data, dict):
        entries = []
        for key, value in data.items():
            if isinstance(value, list):
                entries.extend(x for x in value if isinstance(x, dict))
        return _stringify(data), entries
    return _stringify(data), []


def _read_csv(path: Path) -> tuple[str, list[dict[str, Any]]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    except Exception:
        return "", []
    return _stringify(rows), rows


def classify(path: Path) -> str:
    rel = path.relative_to(SUBJECT).parts
    top = rel[0] if rel else "other"
    mapping = {
        "vocabulary": "vocabulary",
        "grammar": "grammar",
        "word_formation": "word_formation",
        "syntax": "syntax",
        "examples": "examples",
        "prose": "prose",
        "rules": "rules",
    }
    return mapping.get(top, "other")


def load_documents() -> list[LanguageDocument]:
    docs = []
    if not SUBJECT.exists():
        return docs
    for path in SUBJECT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS | DATA_EXTENSIONS:
            continue
        if path.suffix.lower() == ".json":
            text, entries = _read_json(path)
        elif path.suffix.lower() == ".csv":
            text, entries = _read_csv(path)
        else:
            text, entries = path.read_text(encoding="utf-8", errors="ignore"), []
        docs.append(LanguageDocument(str(path.relative_to(ROOT)), classify(path), text, entries))
    return docs


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[\u0C00-\u0C7F]+|[A-Za-z]+", (text or "").lower()))


def search_subject(query: str, limit: int = 10) -> list[dict[str, Any]]:
    q = _tokens(query)
    if not q:
        return []

    scored = []
    for doc in load_documents():
        tokens = _tokens(doc.text)
        overlap = len(q & tokens)
        exact_bonus = 0
        low = doc.text.lower()
        for token in q:
            if len(token) > 2 and token in low:
                exact_bonus += 2
        score = overlap * 5 + exact_bonus
        if score:
            scored.append((score, doc))

        # Structured vocabulary entries get their own semantic-ish score.
        for entry in doc.entries:
            searchable = _stringify(entry)
            et = _tokens(searchable)
            es = len(q & et) * 12
            if es:
                scored.append((es, doc, entry))

    scored.sort(key=lambda x: -x[0])
    results = []
    seen = set()
    for item in scored:
        doc = item[1]
        entry = item[2] if len(item) > 2 else None
        key = (doc.path, json.dumps(entry, ensure_ascii=False, sort_keys=True) if entry else "")
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "source": doc.path,
            "kind": doc.kind,
            "entry": entry,
            "excerpt": doc.text[:1800] if not entry else "",
            "score": item[0],
        })
        if len(results) >= limit:
            break
    return results


def build_subject_context(query: str, limit: int = 10, max_chars: int = 8000) -> str:
    results = search_subject(query, limit=limit)
    if not results:
        return "MELIMI SUBJECT KNOWLEDGE: No directly retrieved item. Do not invent facts."

    lines = [
        "MELIMI TELUGU LANGUAGE SUBJECT KNOWLEDGE",
        "The following are linguistic sources, not response templates.",
    ]
    for result in results:
        lines.append(f"\nSOURCE: {result['source']} [{result['kind']}]")
        if result["entry"]:
            lines.append(json.dumps(result["entry"], ensure_ascii=False))
        else:
            excerpt = re.sub(r"\n{3,}", "\n\n", result["excerpt"]).strip()
            lines.append(excerpt[:1400])
    return "\n".join(lines)[:max_chars]


def subject_inventory() -> dict:
    docs = load_documents()
    return {
        "documents": len(docs),
        "by_kind": {
            kind: sum(1 for d in docs if d.kind == kind)
            for kind in {"vocabulary","grammar","word_formation","syntax","examples","prose","rules","other"}
        },
        "paths": [d.path for d in docs],
    }


from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from functools import lru_cache
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = ROOT / "melimi_telugu"

EXTENSIONS = {".md", ".txt", ".json", ".csv"}
KINDS = ("vocabulary", "grammar", "word_formation", "syntax", "examples", "prose", "rules", "corpus", "other")


@dataclass(frozen=True)
class SubjectDoc:
    path: str
    kind: str
    text: str
    entries: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    tokens: frozenset[str] = field(default_factory=frozenset)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[\u0C00-\u0C7F]+|[A-Za-z][A-Za-z'-]*", (text or "").lower()))


def _stringify(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{k} {_stringify(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(_stringify(v) for v in value)
    return str(value or "")


def _read(path: Path) -> tuple[str, list[dict[str, Any]]]:
    ext = path.suffix.lower()
    try:
        if ext == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                entries = tuple(x for x in data if isinstance(x, dict))
            elif isinstance(data, dict):
                entries = tuple(
                    x for v in data.values() if isinstance(v, list)
                    for x in v if isinstance(x, dict)
                )
            else:
                entries = ()
            return _stringify(data), list(entries)
        if ext == ".csv":
            with path.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            return _stringify(rows), rows
        return path.read_text(encoding="utf-8", errors="ignore"), []
    except Exception:
        return "", []


def _kind(path: Path) -> str:
    rel = path.relative_to(SUBJECT).parts
    if not rel:
        return "other"
    return rel[0] if rel[0] in KINDS else "other"


@lru_cache(maxsize=1)
def build_index() -> tuple[SubjectDoc, ...]:
    docs = []
    if not SUBJECT.exists():
        return tuple()

    for path in sorted(SUBJECT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        text, entries = _read(path)
        rel = str(path.relative_to(ROOT))
        docs.append(
            SubjectDoc(
                path=rel,
                kind=_kind(path),
                text=text,
                entries=tuple(entries),
                tokens=frozenset(_tokens(text)),
            )
        )
    return tuple(docs)


def reload_index() -> None:
    build_index.cache_clear()


def inventory() -> dict:
    docs = build_index()
    return {
        "documents": len(docs),
        "by_kind": {kind: sum(d.kind == kind for d in docs) for kind in KINDS},
        "entries": sum(len(d.entries) for d in docs),
        "paths": [d.path for d in docs],
    }


def _entry_score(query_tokens: set[str], entry: dict[str, Any], query: str) -> float:
    text = _stringify(entry)
    tokens = _tokens(text)
    overlap = len(query_tokens & tokens)
    score = overlap * 12

    low = text.lower()
    for t in query_tokens:
        if len(t) >= 2 and t in low:
            score += 1.5

    # Lexical mapping gets high priority when the user explicitly mentions
    # either side of a Standard/Melimi mapping.
    standard = str(entry.get("standard", "")).lower()
    melimi = str(entry.get("melimi", "")).lower()
    qlow = query.lower()
    if standard and standard in qlow:
        score += 60
    if melimi and melimi in qlow:
        score += 70
    return score


def retrieve(query: str, *, kinds: set[str] | None = None, limit: int = 14) -> list[dict]:
    qtokens = _tokens(query)
    if not qtokens:
        return []

    results = []
    for doc in build_index():
        if kinds and doc.kind not in kinds:
            continue

        # Document-level score.
        overlap = len(qtokens & set(doc.tokens))
        dscore = overlap * 3
        if dscore:
            results.append((dscore, doc, None))

        for entry in doc.entries:
            score = _entry_score(qtokens, entry, query)
            if score:
                results.append((score, doc, entry))

    results.sort(key=lambda x: (-x[0], x[1].path))
    out, seen = [], set()
    for score, doc, entry in results:
        key = (doc.path, json.dumps(entry, ensure_ascii=False, sort_keys=True) if entry else "")
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "score": round(score, 2),
            "source": doc.path,
            "kind": doc.kind,
            "entry": entry,
            "excerpt": "" if entry else re.sub(r"\s+", " ", doc.text)[:1800],
        })
        if len(out) >= limit:
            break
    return out


def _compact_docs(kind: str, max_chars: int) -> str:
    chunks = []
    for doc in build_index():
        if doc.kind != kind:
            continue
        text = re.sub(r"\n{3,}", "\n\n", doc.text).strip()
        if text:
            chunks.append(f"SOURCE {doc.path}:\n{text[:1800]}")
    return "\n\n".join(chunks)[:max_chars]


def language_profile(max_chars: int = 6500) -> str:
    """Stable subject profile: rules + representative language knowledge.

    It is cached locally and intentionally compact so every request does not
    send the entire corpus to Groq.
    """
    parts = [
        "MELIMI TELUGU — AUTHORITATIVE LANGUAGE SUBJECT",
        "The corpus is language knowledge, not a phrase bank.",
        "Treat Melimi Telugu as a distinct register/language system; Standard Telugu and Mixed Telugu are not interchangeable with Melimi.",
        _compact_docs("rules", 2600),
        _compact_docs("grammar", 1600),
        _compact_docs("word_formation", 2200),
        _compact_docs("vocabulary", 1400),
        _compact_docs("syntax", 900),
    ]
    return "\n\n".join(x for x in parts if x)[:max_chars]


def relevant_language_context(query: str, max_chars: int = 6500) -> str:
    # Structured JSON/Markdown retrieval remains primary. SQLite FTS5 adds broad
    # passage retrieval for the consolidated corpus and longer prose/grammar.
    results = retrieve(query, limit=16)
    try:
        from app.melimi.fts import search as fts_search
        fts_results = fts_search(query, top_k=8)
    except Exception:
        fts_results = []

    if not results and not fts_results:
        return "No directly relevant subject item was retrieved. Do not invent Melimi facts."

    lines = ["RELEVANT MELIMI SUBJECT EVIDENCE:"]
    for item in results:
        lines.append(f"\n[{item['kind']}] {item['source']}")
        if item["entry"]:
            lines.append(json.dumps(item["entry"], ensure_ascii=False))
        elif item["excerpt"]:
            lines.append(item["excerpt"])

    seen = {(item["source"], item.get("excerpt", "")) for item in results}
    for item in fts_results:
        key = (item["source"], item["content"][:1800])
        if key in seen:
            continue
        lines.append(f"\n[corpus passage] {item['source']} / chunk {item['chunk_id']}")
        lines.append(item["content"])

    return "\n".join(lines)[:max_chars]

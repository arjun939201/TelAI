"""Optional SQLite FTS5 retrieval layer for the Melimi subject corpus.

This supplements the structured subject index; it does not replace it.
No external vector database is required.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = ROOT / "melimi_telugu"
DB_PATH = ROOT / "data" / "melimi_subject.sqlite3"
EXTENSIONS = {".md", ".txt"}


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def chunk_text(text: str, size: int = 1400, overlap: int = 180):
    text = text.replace("\r\n", "\n")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    buf = ""
    for paragraph in paragraphs:
        if len(buf) + len(paragraph) + 1 <= size:
            buf = (buf + "\n" + paragraph).strip()
        else:
            if buf:
                yield buf
            tail = buf[-overlap:] if overlap and buf else ""
            buf = (tail + "\n" + paragraph).strip()
    if buf:
        yield buf


def init_db():
    with connect() as con:
        con.execute("CREATE TABLE IF NOT EXISTS documents (source TEXT PRIMARY KEY, mtime_ns INTEGER NOT NULL, size INTEGER NOT NULL)")
        con.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
            source UNINDEXED, chunk_id UNINDEXED, content,
            tokenize='unicode61'
        )""")
        con.commit()


def _files():
    if not SUBJECT.exists():
        return []
    return [p for p in sorted(SUBJECT.rglob("*")) if p.is_file() and p.suffix.lower() in EXTENSIONS]


def ensure_index():
    """Incrementally synchronize text/Markdown subject files into SQLite FTS5."""
    init_db()
    paths = _files()
    wanted = {str(p.relative_to(ROOT)): p for p in paths}
    with connect() as con:
        existing = {row[0]: (row[1], row[2]) for row in con.execute("SELECT source, mtime_ns, size FROM documents")}
        for source in set(existing) - set(wanted):
            con.execute("DELETE FROM chunks WHERE source = ?", (source,))
            con.execute("DELETE FROM documents WHERE source = ?", (source,))

        for source, path in wanted.items():
            stat = path.stat()
            stamp = (stat.st_mtime_ns, stat.st_size)
            if existing.get(source) == stamp:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            con.execute("DELETE FROM chunks WHERE source = ?", (source,))
            for i, chunk in enumerate(chunk_text(text)):
                con.execute("INSERT INTO chunks(source, chunk_id, content) VALUES (?, ?, ?)", (source, i, chunk))
            con.execute(
                "INSERT INTO documents(source, mtime_ns, size) VALUES (?, ?, ?) "
                "ON CONFLICT(source) DO UPDATE SET mtime_ns=excluded.mtime_ns, size=excluded.size",
                (source, stat.st_mtime_ns, stat.st_size),
            )
        con.commit()


def _fts_query(query: str) -> str:
    terms = re.findall(r"[\w\u0C00-\u0C7F]+", query, flags=re.UNICODE)
    terms = [t for t in terms if len(t) > 1]
    return " OR ".join('"' + t.replace('"', '') + '"' for t in terms[:32])


def search(query: str, top_k: int = 8):
    ensure_index()
    q = _fts_query(query)
    if not q:
        return []
    with connect() as con:
        rows = con.execute(
            "SELECT source, chunk_id, content, bm25(chunks) AS score "
            "FROM chunks WHERE chunks MATCH ? ORDER BY score LIMIT ?",
            (q, top_k),
        ).fetchall()
    return [dict(row) for row in rows]

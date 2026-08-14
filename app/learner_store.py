"""Persistent chat-time Melimi learning store.

The master Melimi corpus remains read-only. Chat-time learning is stored in a
separate database and can be pending, approved, or rejected.
SQLite is used locally; Render can use PostgreSQL through DATABASE_URL.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_FILE = os.path.join(ROOT, "data", "chat_learning.sqlite3")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_postgres() -> bool:
    return os.getenv("DATABASE_URL", "").strip().lower().startswith(("postgres://", "postgresql://"))


def _pg_connect():
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - only reached when PG is configured without dependency
        raise RuntimeError("DATABASE_URL is set but psycopg is not installed.") from exc
    url = os.getenv("DATABASE_URL", "").strip()
    # Render may provide postgres://; psycopg accepts postgresql://, so normalize it.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return psycopg.connect(url)


def _sqlite_connect():
    os.makedirs(os.path.dirname(SQLITE_FILE), exist_ok=True)
    conn = sqlite3.connect(SQLITE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_store() -> None:
    if _is_postgres():
        conn = _pg_connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS melimi_learning (
                        id SERIAL PRIMARY KEY,
                        kind TEXT NOT NULL,
                        standard TEXT NOT NULL DEFAULT '',
                        melimi TEXT NOT NULL DEFAULT '',
                        rule TEXT NOT NULL DEFAULT '',
                        meaning TEXT NOT NULL DEFAULT '',
                        evidence TEXT NOT NULL DEFAULT '',
                        source TEXT NOT NULL DEFAULT 'chat',
                        status TEXT NOT NULL DEFAULT 'pending',
                        confidence REAL NOT NULL DEFAULT 0.5,
                        metadata TEXT NOT NULL DEFAULT '{}',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
            conn.commit()
        finally:
            conn.close()
        return

    conn = _sqlite_connect()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS melimi_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                standard TEXT NOT NULL DEFAULT '',
                melimi TEXT NOT NULL DEFAULT '',
                rule TEXT NOT NULL DEFAULT '',
                meaning TEXT NOT NULL DEFAULT '',
                evidence TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT 'chat',
                status TEXT NOT NULL DEFAULT 'pending',
                confidence REAL NOT NULL DEFAULT 0.5,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def _row_dict(row: Any) -> dict[str, Any]:
    if hasattr(row, "keys"):
        d = dict(row)
    else:
        keys = ["id", "kind", "standard", "melimi", "rule", "meaning", "evidence", "source", "status", "confidence", "metadata", "created_at", "updated_at"]
        d = dict(zip(keys, row))
    try:
        d["metadata"] = json.loads(d.get("metadata") or "{}")
    except Exception:
        d["metadata"] = {}
    return d


def add_learning(*, kind: str, standard: str = "", melimi: str = "", rule: str = "", meaning: str = "", evidence: str = "", source: str = "chat", status: str = "pending", confidence: float = 0.5, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    init_store()
    now = _now()
    metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
    if _is_postgres():
        conn = _pg_connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id FROM melimi_learning
                    WHERE kind=%s AND standard=%s AND melimi=%s AND rule=%s AND status=%s
                    ORDER BY id DESC LIMIT 1
                """, (kind, standard, melimi, rule, status))
                existing = cur.fetchone()
                if existing:
                    cur.execute("UPDATE melimi_learning SET evidence=%s, meaning=%s, confidence=%s, metadata=%s, updated_at=%s WHERE id=%s", (evidence, meaning, confidence, metadata_json, now, existing[0]))
                    item_id = existing[0]
                else:
                    cur.execute("""
                        INSERT INTO melimi_learning (kind, standard, melimi, rule, meaning, evidence, source, status, confidence, metadata, created_at, updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                    """, (kind, standard, melimi, rule, meaning, evidence, source, status, confidence, metadata_json, now, now))
                    item_id = cur.fetchone()[0]
            conn.commit()
        finally:
            conn.close()
    else:
        conn = _sqlite_connect()
        try:
            existing = conn.execute("SELECT id FROM melimi_learning WHERE kind=? AND standard=? AND melimi=? AND rule=? AND status=? ORDER BY id DESC LIMIT 1", (kind, standard, melimi, rule, status)).fetchone()
            if existing:
                item_id = existing[0]
                conn.execute("UPDATE melimi_learning SET evidence=?, meaning=?, confidence=?, metadata=?, updated_at=? WHERE id=?", (evidence, meaning, confidence, metadata_json, now, item_id))
            else:
                cur = conn.execute("""
                    INSERT INTO melimi_learning (kind, standard, melimi, rule, meaning, evidence, source, status, confidence, metadata, created_at, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (kind, standard, melimi, rule, meaning, evidence, source, status, confidence, metadata_json, now, now))
                item_id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()
    return get_learning(int(item_id)) or {}


def get_learning(item_id: int) -> dict[str, Any] | None:
    init_store()
    if _is_postgres():
        conn = _pg_connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM melimi_learning WHERE id=%s", (item_id,))
                row = cur.fetchone()
                return _row_dict(row) if row else None
        finally:
            conn.close()
    conn = _sqlite_connect()
    try:
        row = conn.execute("SELECT * FROM melimi_learning WHERE id=?", (item_id,)).fetchone()
        return _row_dict(row) if row else None
    finally:
        conn.close()


def list_learning(status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    init_store()
    limit = max(1, min(int(limit), 500))
    if _is_postgres():
        conn = _pg_connect()
        try:
            with conn.cursor() as cur:
                if status:
                    cur.execute("SELECT * FROM melimi_learning WHERE status=%s ORDER BY id DESC LIMIT %s", (status, limit))
                else:
                    cur.execute("SELECT * FROM melimi_learning ORDER BY id DESC LIMIT %s", (limit,))
                return [_row_dict(r) for r in cur.fetchall()]
        finally:
            conn.close()
    conn = _sqlite_connect()
    try:
        if status:
            rows = conn.execute("SELECT * FROM melimi_learning WHERE status=? ORDER BY id DESC LIMIT ?", (status, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM melimi_learning ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [_row_dict(r) for r in rows]
    finally:
        conn.close()


def set_status(item_id: int, status: str) -> dict[str, Any] | None:
    if status not in {"pending", "approved", "rejected"}:
        raise ValueError("status must be pending, approved, or rejected")
    init_store()
    now = _now()
    if _is_postgres():
        conn = _pg_connect()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE melimi_learning SET status=%s, updated_at=%s WHERE id=%s", (status, now, item_id))
            conn.commit()
        finally:
            conn.close()
    else:
        conn = _sqlite_connect()
        try:
            conn.execute("UPDATE melimi_learning SET status=?, updated_at=? WHERE id=?", (status, now, item_id))
            conn.commit()
        finally:
            conn.close()
    return get_learning(item_id)


def approved_for_query(query: str, limit: int = 8) -> list[dict[str, Any]]:
    """Return approved user-learned entries relevant to the current query."""
    terms = [t.strip() for t in query.split() if len(t.strip()) >= 2][:12]
    if not terms:
        return []
    init_store()
    rows = list_learning(status="approved", limit=500)
    hits = []
    for row in rows:
        hay = " ".join([row.get("standard", ""), row.get("melimi", ""), row.get("rule", ""), row.get("meaning", ""), row.get("evidence", "")])
        score = sum(1 for t in terms if t in hay)
        if score:
            row["_score"] = score
            hits.append(row)
    hits.sort(key=lambda x: (x.get("_score", 0), x.get("confidence", 0)), reverse=True)
    return hits[:limit]

"""SQLite persistence (stdlib only). Path from INTERVIEWAI_DB, default ./interviewai.db."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    problem_id TEXT NOT NULL,
    language TEXT NOT NULL,
    phase TEXT NOT NULL,
    hints_used INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    mode TEXT NOT NULL DEFAULT 'offline',
    code TEXT NOT NULL DEFAULT '',
    created_at REAL NOT NULL,
    ended_at REAL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    meta TEXT NOT NULL DEFAULT '{}',
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    language TEXT NOT NULL,
    code TEXT NOT NULL,
    status TEXT NOT NULL,
    passed INTEGER NOT NULL,
    total INTEGER NOT NULL,
    result TEXT NOT NULL,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS reports (
    session_id TEXT PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
    report TEXT NOT NULL,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, id);
CREATE INDEX IF NOT EXISTS idx_submissions_session ON submissions(session_id, id);
"""

_lock = threading.Lock()
_initialised: set[str] = set()


def db_path() -> str:
    return os.getenv("INTERVIEWAI_DB", "interviewai.db")


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = db_path()
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    with _lock:
        if path not in _initialised:
            conn.executescript(SCHEMA)
            _initialised.add(path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def create_session(problem_id: str, language: str, phase: str, mode: str, code: str) -> dict[str, Any]:
    sid = uuid.uuid4().hex[:12]
    with connect() as c:
        c.execute(
            "INSERT INTO sessions (id, problem_id, language, phase, mode, code, created_at) VALUES (?,?,?,?,?,?,?)",
            (sid, problem_id, language, phase, mode, code, time.time()),
        )
    return get_session(sid)  # type: ignore[return-value]


def get_session(sid: str) -> dict[str, Any] | None:
    with connect() as c:
        return _row(c.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone())


def update_session(sid: str, **fields: Any) -> None:
    if not fields:
        return
    cols = ", ".join(f"{k} = ?" for k in fields)
    with connect() as c:
        c.execute(f"UPDATE sessions SET {cols} WHERE id = ?", (*fields.values(), sid))


def list_sessions(limit: int = 100) -> list[dict[str, Any]]:
    with connect() as c:
        rows = c.execute(
            """SELECT s.*, (SELECT MAX(passed) FROM submissions WHERE session_id = s.id AND kind = 'submit') AS best_passed,
                      (SELECT total FROM submissions WHERE session_id = s.id AND kind = 'submit' ORDER BY id DESC LIMIT 1) AS submit_total
               FROM sessions s ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_session(sid: str) -> bool:
    with connect() as c:
        return c.execute("DELETE FROM sessions WHERE id = ?", (sid,)).rowcount > 0


def add_message(sid: str, role: str, content: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    now = time.time()
    with connect() as c:
        cur = c.execute(
            "INSERT INTO messages (session_id, role, content, meta, created_at) VALUES (?,?,?,?,?)",
            (sid, role, content, json.dumps(meta or {}), now),
        )
        mid = cur.lastrowid
    return {"id": mid, "role": role, "content": content, "meta": meta or {}, "created_at": now}


def messages(sid: str) -> list[dict[str, Any]]:
    with connect() as c:
        rows = c.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY id", (sid,)).fetchall()
    return [{**dict(r), "meta": json.loads(r["meta"])} for r in rows]


def add_submission(sid: str, kind: str, language: str, code: str, result: dict[str, Any]) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO submissions (session_id, kind, language, code, status, passed, total, result, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (sid, kind, language, code, result["status"], result["passed"], result["total"], json.dumps(result), time.time()),
        )
        return int(cur.lastrowid or 0)


def submissions(sid: str) -> list[dict[str, Any]]:
    with connect() as c:
        rows = c.execute("SELECT * FROM submissions WHERE session_id = ? ORDER BY id", (sid,)).fetchall()
    return [{**dict(r), "result": json.loads(r["result"])} for r in rows]


def save_report(sid: str, report: dict[str, Any]) -> None:
    with connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO reports (session_id, report, created_at) VALUES (?,?,?)",
            (sid, json.dumps(report), time.time()),
        )


def get_report(sid: str) -> dict[str, Any] | None:
    with connect() as c:
        row = c.execute("SELECT report FROM reports WHERE session_id = ?", (sid,)).fetchone()
    return json.loads(row["report"]) if row else None

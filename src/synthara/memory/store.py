from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from synthara.core.models import Message, Report, ReportSection, Session, Source


class MemoryStore:
    def __init__(self, db_path: str = "synthara.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    @property
    def conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
        """)
        conn.commit()
        conn.close()

    def save_session(self, session: Session):
        self.conn.execute(
            "INSERT OR REPLACE INTO sessions (id, query, created_at) VALUES (?, ?, ?)",
            (session.id, session.query, session.created_at.isoformat()),
        )
        for msg in session.messages:
            self.conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session.id, msg.role, msg.content, msg.timestamp.isoformat()),
            )
        if session.report:
            self.conn.execute(
                "INSERT INTO reports (session_id, content, created_at) VALUES (?, ?, ?)",
                (session.id, session.report.content, session.report.created_at.isoformat()),
            )
        self.conn.commit()

    def get_session(self, session_id: str) -> Session | None:
        row = self.conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            return None
        session = Session(id=row["id"], query=row["query"])
        msg_rows = self.conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY id", (session_id,)
        ).fetchall()
        for m in msg_rows:
            session.messages.append(Message(role=m["role"], content=m["content"]))
        report_row = self.conn.execute(
            "SELECT * FROM reports WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        if report_row:
            session.report = Report(query=session.query, sections=[], content=report_row["content"])
        return session

    def list_sessions(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id, query, created_at FROM sessions ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

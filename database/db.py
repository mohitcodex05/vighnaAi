"""
database/db.py — SQLite database initializer for Vighna
Creates and manages: users, conversations, messages, memory tables
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "vighna.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    UNIQUE NOT NULL,
                password    TEXT    NOT NULL,
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                title       TEXT    DEFAULT 'New Chat',
                created_at  TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id   INTEGER NOT NULL,
                sender            TEXT    NOT NULL CHECK(sender IN ('user','assistant')),
                content           TEXT    NOT NULL,
                timestamp         TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            );

            CREATE TABLE IF NOT EXISTS memory (
                key     TEXT PRIMARY KEY,
                value   TEXT NOT NULL,
                updated TEXT DEFAULT (datetime('now'))
            );
        """)
    print("[DB] Database initialized →", DB_PATH)


def save_message(conversation_id: int, sender: str, content: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)",
            (conversation_id, sender, content)
        )


def load_conversation_messages(conversation_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT sender, content, timestamp FROM messages WHERE conversation_id=? ORDER BY id",
            (conversation_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def create_conversation(user_id: int, title: str = "New Chat") -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO conversations (user_id, title) VALUES (?, ?)",
            (user_id, title)
        )
        return cur.lastrowid


def get_user_conversations(user_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at FROM conversations WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def memory_set(key: str, value: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO memory(key,value,updated) VALUES(?,?,datetime('now')) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated=excluded.updated",
            (key, value)
        )


def memory_get(key: str, default=None):
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM memory WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default

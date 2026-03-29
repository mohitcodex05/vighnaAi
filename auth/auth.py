"""
auth/auth.py — Login & Signup using SQLite + bcrypt
"""

import bcrypt
from database.db import get_connection


def signup(username: str, password: str) -> dict:
    """Create a new user. Returns {'ok': True, 'user_id': int} or {'ok': False, 'error': str}."""
    username = username.strip().lower()
    if not username or not password:
        return {"ok": False, "error": "Username and password are required."}

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed)
            )
            return {"ok": True, "user_id": cur.lastrowid, "username": username}
    except Exception as e:
        if "UNIQUE" in str(e):
            return {"ok": False, "error": "Username already taken."}
        return {"ok": False, "error": str(e)}


def login(username: str, password: str) -> dict:
    """Verify credentials. Returns {'ok': True, 'user_id': int} or {'ok': False, 'error': str}."""
    username = username.strip().lower()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, password FROM users WHERE username=?", (username,)
        ).fetchone()

    if not row:
        return {"ok": False, "error": "User not found."}

    if bcrypt.checkpw(password.encode(), row["password"].encode()):
        return {"ok": True, "user_id": row["id"], "username": username}
    return {"ok": False, "error": "Incorrect password."}


def get_user(user_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, created_at FROM users WHERE id=?", (user_id,)
        ).fetchone()
    return dict(row) if row else None

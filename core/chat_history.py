"""
AlfredX v2.1 — Chat History Persistence (SQLite)
=================================================
Drop this file into your AlfredX project folder.
See INTEGRATION GUIDE at the bottom of this file.
"""

import sqlite3
import json
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "alfredx_history.db")


class ChatHistory:
    """Manages chat session persistence using SQLite."""

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    created_at TEXT DEFAULT (datetime('now','localtime')),
                    updated_at TEXT DEFAULT (datetime('now','localtime')),
                    is_last INTEGER DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT DEFAULT (datetime('now','localtime')),
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id)
            """)

    def _conn(self):
        """Create a new connection with WAL mode for performance."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        return conn

    # ─── SESSION MANAGEMENT ───────────────────────────────────────

    def create_session(self, name=None):
        """Start a new chat session. Returns session_id."""
        if name is None:
            name = f"Chat — {datetime.now().strftime('%b %d, %H:%M')}"
        with self._conn() as conn:
            # Clear old 'is_last' flags
            conn.execute("UPDATE sessions SET is_last = 0")
            cursor = conn.execute(
                "INSERT INTO sessions (name, is_last) VALUES (?, 1)",
                (name,)
            )
            return cursor.lastrowid

    def get_last_session_id(self):
        """Get the most recent session ID (for auto-load on restart)."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id FROM sessions WHERE is_last = 1 ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
            if row:
                return row["id"]
            # Fallback: get the latest session
            row = conn.execute(
                "SELECT id FROM sessions ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
            return row["id"] if row else None

    def list_sessions(self, limit=50):
        """List all sessions (for a future 'chat list' feature)."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, name, created_at, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def rename_session(self, session_id, new_name):
        """Rename a session."""
        with self._conn() as conn:
            conn.execute("UPDATE sessions SET name = ? WHERE id = ?", (new_name, session_id))

    def delete_session(self, session_id):
        """Delete a session and all its messages."""
        with self._conn() as conn:
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

    # ─── MESSAGE MANAGEMENT ───────────────────────────────────────

    def add_message(self, session_id, role, content, metadata=None):
        """
        Save a single message.
        
        Args:
            session_id: Current session ID
            role: 'user', 'assistant', or 'system'
            content: The message text
            metadata: Optional dict (e.g. {"command": "weather", "tts": True})
        """
        meta_json = json.dumps(metadata or {})
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
                (session_id, role, content, meta_json)
            )
            conn.execute(
                "UPDATE sessions SET updated_at = datetime('now','localtime') WHERE id = ?",
                (session_id,)
            )

    def get_messages(self, session_id):
        """
        Load all messages for a session (for restoring chat on restart).
        Returns list of dicts: [{"role": ..., "content": ..., "timestamp": ..., "metadata": ...}]
        """
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT role, content, timestamp, metadata FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            ).fetchall()
            results = []
            for r in rows:
                msg = dict(r)
                msg["metadata"] = json.loads(msg["metadata"])
                results.append(msg)
            return results

    def get_context_messages(self, session_id, limit=20):
        """
        Get recent messages formatted for AI context window.
        Returns list of {"role": ..., "content": ...} dicts.
        """
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            ).fetchall()
            return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def clear_session_messages(self, session_id):
        """Clear all messages in a session (keep the session itself)."""
        with self._conn() as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

    def get_message_count(self, session_id):
        """Get number of messages in a session."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as count FROM messages WHERE session_id = ?",
                (session_id,)
            ).fetchone()
            return row["count"]


# ─── SINGLETON INSTANCE ──────────────────────────────────────────
# Import and use:  from chat_history import chat_db
chat_db = ChatHistory()


# ══════════════════════════════════════════════════════════════════
# INTEGRATION GUIDE
# ══════════════════════════════════════════════════════════════════
#
# STEP 1: In main_window.py — On App Startup
# ────────────────────────────────────────────
#   from chat_history import chat_db
#
#   # In your __init__ or setup method:
#   self.session_id = chat_db.get_last_session_id()
#   if self.session_id:
#       # Restore old messages into the chat display
#       messages = chat_db.get_messages(self.session_id)
#       for msg in messages:
#           self.chat_display.add_message(msg["role"], msg["content"])
#   else:
#       # First ever launch — create a new session
#       self.session_id = chat_db.create_session()
#
#
# STEP 2: In chat_display.py — When Messages Are Added
# ─────────────────────────────────────────────────────
#   # Wherever you call add_message() or append a message to the UI,
#   # also save it to the database:
#
#   chat_db.add_message(self.session_id, "user", user_text)
#   chat_db.add_message(self.session_id, "assistant", ai_response)
#
#
# STEP 3: In ai_engine.py — Feed Context from DB
# ───────────────────────────────────────────────
#   # Instead of (or alongside) your in-memory conversation_history,
#   # you can pull context from the DB:
#
#   context = chat_db.get_context_messages(self.session_id, limit=20)
#   # Pass 'context' as the messages list to Groq/Ollama
#
#
# STEP 4: "New Chat" Button (optional, for later)
# ────────────────────────────────────────────────
#   def new_chat(self):
#       self.session_id = chat_db.create_session()
#       self.chat_display.clear()
#
#
# STEP 5: On App Close (optional safety save)
# ────────────────────────────────────────────
#   # In your closeEvent:
#   # Nothing needed — messages are saved in real-time.
#   # But you can mark the session:
#   #   chat_db.rename_session(self.session_id, "Last session")
#
# ══════════════════════════════════════════════════════════════════
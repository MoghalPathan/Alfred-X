"""
AlfredX: Memory System
SQLite-based persistent memory for facts, conversations, and tasks.
"""
import sqlite3
import os
from datetime import datetime
from config import DATA_DIR


class Memory:
    """Persistent memory -- remembers user facts, conversation history, and tasks."""

    def __init__(self):
        self.db_path = os.path.join(DATA_DIR, "alfred_memory.db")
        os.makedirs(DATA_DIR, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(category, key)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    language TEXT DEFAULT 'en',
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            conn.commit()
        print(f"[Memory] [OK] Database ready: {self.db_path}")

    # --- Facts ---
    def remember(self, category, key, value):
        """Store or update a fact."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO facts (category, key, value, updated_at) VALUES (?, ?, ?, ?)",
                (category, key, value, datetime.now().isoformat())
            )
            conn.commit()
        print(f"[Memory] Saved {category}/{key} = {value}")

    def recall(self, category=None, key=None):
        """Recall facts. Filter by category and/or key."""
        with sqlite3.connect(self.db_path) as conn:
            if category and key:
                row = conn.execute(
                    "SELECT value FROM facts WHERE category=? AND key=?", (category, key)
                ).fetchone()
                return row[0] if row else None
            elif category:
                rows = conn.execute(
                    "SELECT key, value FROM facts WHERE category=?", (category,)
                ).fetchall()
                return {r[0]: r[1] for r in rows}
            else:
                rows = conn.execute("SELECT category, key, value FROM facts").fetchall()
                return [{"category": r[0], "key": r[1], "value": r[2]} for r in rows]

    def get_all_facts(self):
        return self.recall()

    def forget(self, category, key):
        """Delete a fact."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM facts WHERE category=? AND key=?", (category, key))
            conn.commit()
        print(f"[Memory] Forgot: {category}/{key}")

    # --- Conversations ---
    def log_message(self, role, content, language="en"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (role, content, language, timestamp) VALUES (?, ?, ?, ?)",
                (role, content, language, datetime.now().isoformat())
            )
            conn.commit()

    def get_recent_conversations(self, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content, timestamp FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in reversed(rows)]

    def search_conversations(self, query):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content, timestamp FROM conversations WHERE content LIKE ? ORDER BY id DESC LIMIT 20",
                (f"%{query}%",)
            ).fetchall()
        return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows]

    # --- Tasks ---
    def add_task(self, title, description=""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO tasks (title, description, status, created_at) VALUES (?, ?, 'pending', ?)",
                (title, description, datetime.now().isoformat())
            )
            conn.commit()
        print(f"[Memory] Task added: {title}")

    def complete_task(self, task_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status='completed', completed_at=? WHERE id=?",
                (datetime.now().isoformat(), task_id)
            )
            conn.commit()

    def get_tasks(self, status="pending"):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, title, description, status, created_at FROM tasks WHERE status=? ORDER BY id DESC",
                (status,)
            ).fetchall()
        return [{"id": r[0], "title": r[1], "description": r[2], "status": r[3], "created": r[4]} for r in rows]

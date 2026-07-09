import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)
DB_PATH = DATABASE_DIR / "leadflow.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            name TEXT,
            company TEXT,
            description TEXT,
            url TEXT UNIQUE,
            source TEXT,
            category TEXT,
            location TEXT,
            score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'New',
            collection_method TEXT DEFAULT 'API',
            metadata TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    # Migration for older local databases.
    cursor.execute("PRAGMA table_info(leads)")
    columns = [row[1] for row in cursor.fetchall()]
    if "collection_method" not in columns:
        cursor.execute("ALTER TABLE leads ADD COLUMN collection_method TEXT DEFAULT 'API'")

    conn.commit()
    conn.close()


def _metadata_to_text(metadata: Any) -> str:
    if isinstance(metadata, str):
        return metadata
    return json.dumps(metadata or {}, ensure_ascii=False)


def save_items(items: list[dict]) -> int:
    if not items:
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    saved_count = 0

    for item in items:
        now = datetime.now(timezone.utc).isoformat()
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO leads (
                    title, name, company, description, url, source, category,
                    location, score, status, collection_method, metadata,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.get("title", ""),
                    item.get("name", ""),
                    item.get("company", ""),
                    item.get("description", ""),
                    item.get("url", ""),
                    item.get("source", ""),
                    item.get("category", ""),
                    item.get("location", ""),
                    int(item.get("score", 0) or 0),
                    item.get("status", "New"),
                    item.get("collection_method", "API"),
                    _metadata_to_text(item.get("metadata")),
                    item.get("created_at", now),
                    now,
                ),
            )
            if cursor.rowcount > 0:
                saved_count += 1
        except sqlite3.Error as exc:
            print(f"Database insert error: {exc}")

    conn.commit()
    conn.close()
    return saved_count


def fetch_all_items() -> list[dict]:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, name, company, description, url, source, category,
               location, score, status, collection_method, metadata,
               created_at, updated_at
        FROM leads
        ORDER BY id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_all() -> list[dict]:
    return fetch_all_items()


def count_items() -> int:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    total = cursor.fetchone()[0]
    conn.close()
    return int(total)


def update_status(item_id: int, status: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE leads
        SET status = ?, updated_at = ?
        WHERE id = ?
        """,
        (status, datetime.now(timezone.utc).isoformat(), int(item_id)),
    )
    conn.commit()
    conn.close()

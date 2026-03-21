import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "licenses.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL UNIQUE,
                plan TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                device_id TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                last_check_at TEXT,
                notes TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

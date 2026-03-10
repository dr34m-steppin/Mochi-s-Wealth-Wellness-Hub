import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "swan.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                total_net_worth REAL,
                holdings_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "total_net_worth" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN total_net_worth REAL")
        if "holdings_json" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN holdings_json TEXT")
        conn.commit()
    finally:
        conn.close()

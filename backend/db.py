import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

DB_PATH = Path(os.getenv("DB_PATH", str(Path(__file__).parent.parent / "app.db")))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                channel TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_created 
            ON tickets(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_status 
            ON tickets(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_priority 
            ON tickets(priority)
        """)
        conn.commit()


def table_is_empty() -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM tickets")
        result = cursor.fetchone()
        return result["count"] == 0


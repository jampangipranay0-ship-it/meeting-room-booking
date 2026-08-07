import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from repositories.base_repository import BaseRepository


class SQLiteRepository(BaseRepository):
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def execute(self, query: str, parameters: tuple = (), commit: bool = False):
        cursor = self.connection.cursor()
        # Convert psycopg/psycopg2-style %s placeholders to SQLite '?' placeholders
        # so the same SQL in BookingRepository works for both backends.
        sqlite_query = query.replace("%s", "?")
        cursor.execute(sqlite_query, parameters)
        if commit:
            self.connection.commit()
        return cursor

    def load(self):
        raise NotImplementedError("Use SQL-specific methods for SQLite repository")

    def save(self, data: List[Any]) -> None:
        raise NotImplementedError("Use SQL-specific methods for SQLite repository")

    def initialize_table(self):
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                room_id TEXT,
                room_name TEXT,
                date TEXT,
                start_time TEXT,
                end_time TEXT,
                booked_by TEXT,
                employee_id TEXT,
                purpose TEXT,
                reason TEXT,
                client_name TEXT,
                status TEXT,
                duration_hours REAL,
                meeting_link TEXT,
                approved_by TEXT,
                remarks TEXT,
                created_at TEXT,
                modified_at TEXT,
                extension_requested INTEGER,
                extension_status TEXT
            )
            """,
            commit=True,
        )

    def fetch_all(self, query: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
        cursor = self.execute(query, parameters)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def fetch_one(self, query: str, parameters: tuple = ()) -> Optional[Dict[str, Any]]:
        cursor = self.execute(query, parameters)
        row = cursor.fetchone()
        return dict(row) if row else None

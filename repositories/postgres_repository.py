import psycopg
from psycopg.rows import dict_row
from typing import Any, Dict, List, Optional


class PostgresRepository:
    def __init__(self, dsn: str):
        if not dsn:
            raise ValueError("DATABASE_URL must be set for PostgreSQL persistence")

        self.connection = psycopg.connect(dsn, autocommit=False)
        self.connection.row_factory = dict_row

    def execute(self, query: str, parameters: tuple = (), commit: bool = False):
        with self.connection.cursor() as cursor:
            cursor.execute(query, parameters)
            if commit:
                self.connection.commit()
            return cursor

    def initialize_table(self) -> None:
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
                extension_requested BOOLEAN,
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

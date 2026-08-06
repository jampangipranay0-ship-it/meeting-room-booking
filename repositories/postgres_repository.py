import traceback

import psycopg
from psycopg.rows import dict_row
from typing import Any, Dict, List, Optional


class PostgresRepository:
    def __init__(self, dsn: str):
        print("DSN received:", bool(dsn), len(dsn))
        if not dsn:
            raise ValueError("DATABASE_URL must be set for PostgreSQL persistence")

        try:
            self.connection = psycopg.connect(dsn, autocommit=False)
            self.connection.row_factory = dict_row
            print("PostgreSQL connection successful")
        except Exception:
            print("PostgreSQL connection failed")
            traceback.print_exc()
            raise

    def execute(self, query: str, parameters: tuple = (), commit: bool = False):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, parameters)
            if commit:
                self.connection.commit()
        except Exception:
            print("PostgreSQL query failed:")
            traceback.print_exc()
            raise
        finally:
            cursor.close()

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

        try:
            cursor = self.connection.cursor()
            try:
                cursor.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = 'bookings')"
                )
                exists_result = cursor.fetchone()
                exists = bool(exists_result[0]) if exists_result else False
            finally:
                cursor.close()
            print("Bookings table exists:", exists)
        except Exception:
            print("Failed to verify bookings table existence:")
            traceback.print_exc()
            raise

    def fetch_all(self, query: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception:
            print("PostgreSQL fetch_all failed:")
            traceback.print_exc()
            raise
        finally:
            cursor.close()

    def fetch_one(self, query: str, parameters: tuple = ()) -> Optional[Dict[str, Any]]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, parameters)
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception:
            print("PostgreSQL fetch_one failed:")
            traceback.print_exc()
            raise
        finally:
            cursor.close()

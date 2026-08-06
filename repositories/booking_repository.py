from datetime import datetime
from typing import Any, Dict, List, Optional


class BookingRepository:
    def __init__(self, repository: Any):
        self.repository = repository
        self.repository.initialize_table()

    def create(self, booking: Dict) -> None:
        self.repository.execute(
            """
            INSERT INTO bookings (
                id, room_id, room_name, date, start_time, end_time, booked_by,
                employee_id, purpose, reason, client_name, status, duration_hours,
                meeting_link, approved_by, remarks, created_at, modified_at,
                extension_requested, extension_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                booking["id"],
                booking["room_id"],
                booking["room_name"],
                booking["date"],
                booking["start_time"],
                booking["end_time"],
                booking["booked_by"],
                booking["employee_id"],
                booking["purpose"],
                booking["reason"],
                booking.get("client_name", ""),
                booking["status"],
                booking["duration_hours"],
                booking.get("meeting_link", ""),
                booking.get("approved_by", ""),
                booking.get("remarks", ""),
                booking["created_at"],
                booking["modified_at"],
                booking.get("extension_requested", False),
                booking.get("extension_status", "None"),
            ),
            commit=True,
        )

    def get_all(self) -> List[Dict]:
        return self.repository.fetch_all("SELECT * FROM bookings ORDER BY date, start_time")

    def get_by_id(self, booking_id: str) -> Optional[Dict]:
        return self.repository.fetch_one("SELECT * FROM bookings WHERE id = %s", (booking_id,))

    def update(self, booking_id: str, updated: Dict) -> None:
        self.repository.execute(
            """
            UPDATE bookings SET
                room_id = %s, room_name = %s, date = %s, start_time = %s, end_time = %s,
                booked_by = %s, employee_id = %s, purpose = %s, reason = %s,
                client_name = %s, status = %s, duration_hours = %s, meeting_link = %s,
                approved_by = %s, remarks = %s, modified_at = %s,
                extension_requested = %s, extension_status = %s
            WHERE id = %s
            """,
            (
                updated["room_id"],
                updated["room_name"],
                updated["date"],
                updated["start_time"],
                updated["end_time"],
                updated["booked_by"],
                updated["employee_id"],
                updated["purpose"],
                updated["reason"],
                updated.get("client_name", ""),
                updated["status"],
                updated["duration_hours"],
                updated.get("meeting_link", ""),
                updated.get("approved_by", ""),
                updated.get("remarks", ""),
                updated["modified_at"],
                updated.get("extension_requested", False),
                updated.get("extension_status", "None"),
                booking_id,
            ),
            commit=True,
        )

    def delete(self, booking_id: str) -> None:
        self.repository.execute("DELETE FROM bookings WHERE id = %s", (booking_id,), commit=True)

    def get_today(self) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.repository.fetch_all(
            "SELECT * FROM bookings WHERE date = %s ORDER BY start_time", (today,)
        )

    def get_all_history(self) -> List[Dict]:
        return self.get_all()

    def get_upcoming(self, employee_id: str) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.repository.fetch_all(
            "SELECT * FROM bookings WHERE employee_id = %s AND date >= %s ORDER BY date, start_time",
            (employee_id, today),
        )

    def get_past_by_employee(self, employee_id: str) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.repository.fetch_all(
            "SELECT * FROM bookings WHERE employee_id = %s AND date < %s ORDER BY date DESC, start_time",
            (employee_id, today),
        )

    def get_employee_today(self, employee_id: str) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.repository.fetch_all(
            "SELECT * FROM bookings WHERE employee_id = %s AND date = %s ORDER BY start_time",
            (employee_id, today),
        )

    def get_room_conflicts(self, room_id: str, date: str, start_time: str, end_time: str, exclude_id: str | None = None) -> List[Dict]:
        query = "SELECT * FROM bookings WHERE room_id = %s AND date = %s AND status NOT IN ('Cancelled','Rejected')"
        params = [room_id, date]
        if exclude_id:
            query += " AND id != %s"
            params.append(exclude_id)
        query += " ORDER BY start_time"
        bookings = self.repository.fetch_all(query, tuple(params))
        return [
            booking
            for booking in bookings
            if self._overlaps(start_time, end_time, booking["start_time"], booking["end_time"])
        ]

    @staticmethod
    def _overlaps(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
        def to_minutes(value: str) -> int:
            hour, minute = map(int, value.split(":"))
            return hour * 60 + minute

        a_start = to_minutes(start_a)
        a_end = to_minutes(end_a)
        b_start = to_minutes(start_b)
        b_end = to_minutes(end_b)
        return max(a_start, b_start) < min(a_end, b_end)

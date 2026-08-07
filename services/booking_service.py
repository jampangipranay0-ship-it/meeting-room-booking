from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional

from models.booking import Booking
from repositories.booking_repository import BookingRepository
from repositories.google_sheets_repository import GoogleSheetsRepository
from repositories.room_repository import RoomRepository
from repositories.sqlite_repository import SQLiteRepository
from repositories.json_repository import JsonRepository
from config import Config


class DatabaseConfigError(Exception):
    pass


class BookingService:
    def __init__(self):
        # Prefer Google Sheets when configured (production on Vercel).
        google_url = os.getenv("GOOGLE_SHEETS_API_URL", "").strip()
        # No API key required by default; keep ability to supply one if needed
        google_key = os.getenv("GOOGLE_SHEETS_API_KEY", "").strip()
        if google_url:
            print("Using Google Sheets booking storage", google_url[:80])
            self.booking_repo = BookingRepository(GoogleSheetsRepository(google_url, google_key))
        else:
            # Local fallback: SQLite
            print("GOOGLE_SHEETS_URL missing; using local SQLite booking storage")
            self.booking_repo = BookingRepository(SQLiteRepository(Config.BOOKING_DB_PATH))
        self.room_repo = RoomRepository(JsonRepository(Config.ROOMS_PATH))

    def create_booking(self, data: Dict) -> Dict:
        self._validate_booking_date(data["date"])
        duration = self._duration_hours(data["start_time"], data["end_time"])
        if duration > 2 and data.get("purpose") != "Online Meeting":
            data["status"] = "Pending Approval"
            data["extension_requested"] = True
            data["extension_status"] = "Pending"
        else:
            data["status"] = "Booked"

        if self.booking_repo.get_room_conflicts(data["room_id"], data["date"], data["start_time"], data["end_time"]):
            raise ValueError("Room is not available for the selected time")

        room = self.room_repo.get_by_id(data["room_id"])
        office_location = room.get("location", "") if room else ""

        booking_id = self._generate_id()
        booking = {
            "id": booking_id,
            "room_id": data["room_id"],
            "room_name": self._room_name(data["room_id"]),
            "office": office_location,
            "date": data["date"],
            "start_time": data["start_time"],
            "end_time": data["end_time"],
            "booked_by": data["booked_by"],
            "employee_id": data.get("employee_id", ""),
            "purpose": data["purpose"],
            "reason": data.get("reason", ""),
            "client_name": data.get("client_name", ""),
            "status": data["status"],
            "duration_hours": duration,
            "meeting_link": data.get("meeting_link", ""),
            "approved_by": "",
            "remarks": "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "extension_requested": data.get("extension_requested", False),
            "extension_status": data.get("extension_status", "None"),
        }
        self.booking_repo.create(booking)
        return booking

    def update_booking(self, booking_id: str, data: Dict) -> Dict:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        room_id = data.get("room_id", booking.get("room_id"))
        date = data.get("date", booking.get("date"))
        start_time = data.get("start_time", booking.get("start_time"))
        end_time = data.get("end_time", booking.get("end_time"))

        if self.booking_repo.get_room_conflicts(room_id, date, start_time, end_time, exclude_id=booking_id):
            raise ValueError("Room is not available for the selected time")

        booking.update(data)
        if booking.get("purpose") != "Online Meeting":
            duration = self._duration_hours(booking["start_time"], booking["end_time"])
            if duration > 2:
                booking["status"] = "Pending Approval"
                booking["extension_requested"] = True
                booking["extension_status"] = "Pending"

        booking["modified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.booking_repo.update(booking_id, booking)
        return booking

    def delete_booking(self, booking_id: str) -> None:
        self.booking_repo.delete(booking_id)

    def get_all_bookings(self) -> List[Dict]:
        return self.booking_repo.get_all()

    def get_today_bookings(self) -> List[Dict]:
        return self.booking_repo.get_today()

    def get_employee_bookings(self, employee_id: str) -> List[Dict]:
        return [booking for booking in self.booking_repo.get_all() if booking.get("employee_id") == employee_id]

    def get_upcoming(self, employee_id: str) -> List[Dict]:
        return self.booking_repo.get_upcoming(employee_id)

    def get_upcoming_bookings(self) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        bookings = [
            booking
            for booking in self.booking_repo.get_all()
            if booking.get("date") >= today and booking.get("status") not in {"Cancelled", "Rejected"}
        ]
        return sorted(bookings, key=lambda item: (item.get("date", ""), item.get("start_time", "")))

    def get_bookings_for_room_date(self, room_id: str, date: str) -> List[Dict]:
        return [
            booking
            for booking in self.booking_repo.get_all()
            if booking.get("room_id") == room_id and booking.get("date") == date and booking.get("status") not in {"Cancelled", "Rejected"}
        ]

    def get_dashboard_stats(self) -> Dict:
        bookings = self.booking_repo.get_all()
        today = datetime.now().strftime("%Y-%m-%d")
        today_bookings = [b for b in bookings if b.get("date") == today]
        pending = [b for b in bookings if b.get("status") == "Pending Approval"]
        completed = [b for b in bookings if b.get("status") == "Completed"]
        rooms = self.room_repo.get_all()
        occupied = len([b for b in today_bookings if b.get("status") in {"Booked", "Pending Approval"}])
        return {
            "today_bookings": len(today_bookings),
            "rooms_occupied": occupied,
            "pending_requests": len(pending),
            "available_rooms": len(rooms) - occupied,
            "completed_meetings": len(completed),
            "total_rooms": len(rooms),
        }

    @staticmethod
    def _duration_hours(start_time: str, end_time: str) -> float:
        start = BookingService._to_minutes(start_time)
        end = BookingService._to_minutes(end_time)
        duration = round((end - start) / 60, 2)
        if duration <= 0:
            raise ValueError("End time must be later than start time.")
        return duration

    @staticmethod
    def _to_minutes(value: str) -> int:
        hour, minute = map(int, value.split(":"))
        return hour * 60 + minute

    def _room_name(self, room_id: str) -> str:
        room = self.room_repo.get_by_id(room_id)
        return room.get("name", "") if room else ""

    def _validate_booking_date(self, date_str: str) -> None:
        try:
            requested_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Bookings can only be made up to 7 days in advance.")

        today = datetime.now().date()
        max_date = today + timedelta(days=7)
        if requested_date < today or requested_date > max_date:
            raise ValueError("Bookings can only be made up to 7 days in advance.")

    @staticmethod
    def _generate_id() -> str:
        return f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"

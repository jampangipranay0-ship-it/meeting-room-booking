from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Booking:
    id: str
    room_id: str
    room_name: str
    date: str
    start_time: str
    end_time: str
    booked_by: str
    employee_id: str
    purpose: str
    reason: str
    client_name: str
    status: str = "Booked"
    duration_hours: float = 0.0
    meeting_link: str = ""
    approved_by: str = ""
    remarks: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    modified_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    extension_requested: bool = False
    extension_status: str = "None"

from dataclasses import dataclass


@dataclass
class Room:
    id: str
    name: str
    location: str
    capacity: str
    room_type: str = ""
    equipment: str = ""
    is_active: bool = True

from dataclasses import dataclass


@dataclass
class Room:
    id: str
    name: str
    location: str
    capacity: int
    equipment: str = ""
    is_active: bool = True

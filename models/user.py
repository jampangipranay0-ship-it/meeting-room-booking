from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str
    email: str
    password: str
    role: str
    department: str = ""
    is_active: bool = True
    is_blocked: bool = False

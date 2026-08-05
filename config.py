import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATA_DIR = BASE_DIR / "data"
    BOOKINGS_PATH = DATA_DIR / "bookings.json"
    BOOKING_DB_PATH = DATA_DIR / "booking.db"
    USERS_PATH = DATA_DIR / "users.json"
    ROOMS_PATH = DATA_DIR / "rooms.json"
    TEMPLATE_FOLDER = str(BASE_DIR / "templates")
    STATIC_FOLDER = str(BASE_DIR / "static")
    PER_PAGE = 20

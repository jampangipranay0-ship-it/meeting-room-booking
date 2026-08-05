from flask import session

from repositories.user_repository import UserRepository
from repositories.json_repository import JsonRepository
from config import Config


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository(JsonRepository(Config.USERS_PATH))

    def authenticate(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if user and user.get("password") == password and not user.get("is_blocked", False):
            session["user"] = user
            return user
        return None

    def logout(self):
        session.pop("user", None)

    def current_user(self):
        return session.get("user")

from repositories.json_repository import JsonRepository


class UserRepository:
    def __init__(self, repository: JsonRepository):
        self.repository = repository

    def load(self):
        return self.repository.load()

    def save(self, users):
        self.repository.save(users)

    def get_by_email(self, email: str):
        for user in self.load():
            if user.get("email") == email:
                return user
        return None

    def get_by_id(self, user_id: str):
        for user in self.load():
            if user.get("id") == user_id:
                return user
        return None

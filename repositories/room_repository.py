from repositories.json_repository import JsonRepository


class RoomRepository:
    def __init__(self, repository: JsonRepository):
        self.repository = repository

    def load(self):
        return self.repository.load()

    def save(self, rooms):
        self.repository.save(rooms)

    def get_all(self):
        return self.load()

    def get_by_id(self, room_id: str):
        for room in self.load():
            if room.get("id") == room_id:
                return room
        return None

import json
from pathlib import Path
from typing import Any, List

from repositories.base_repository import BaseRepository


class JsonRepository(BaseRepository):
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def load(self) -> List[Any]:
        with self.file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, data: List[Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    def load(self):
        raise NotImplementedError

    @abstractmethod
    def save(self, data):
        raise NotImplementedError

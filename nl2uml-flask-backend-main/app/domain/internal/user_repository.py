from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def get_user(self, email: str):
        pass

    @abstractmethod
    def create_user(self, email: str, projects=None):
        pass
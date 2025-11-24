from abc import ABC, abstractmethod

class ModelRepository(ABC):
    @abstractmethod
    def get_by_id(self, model_id: str):
        pass

    @abstractmethod
    def save(self, model_id: str, model):
        pass

from abc import ABC, abstractmethod

class IPresentationGateway(ABC):
    @abstractmethod
    def push_update(self, model_id: str, payload: dict):
        pass

    @abstractmethod
    def format_response(self, result: str) -> dict:
        pass
from __future__ import annotations
from typing import Protocol


class IWebSocketService(Protocol):
    def push_message_to_user(self, user_email: str, message: dict) -> bool: ...

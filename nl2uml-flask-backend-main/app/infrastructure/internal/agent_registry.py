from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Type

class AgentRegistry:
    _REG: Dict[str, Type] = {}

    @classmethod
    def register(cls, key: str, klass: Optional[Type] = None):
        key_norm = (key or "").strip().lower()
        def _decorator(klass):
            cls._REG[key_norm] = klass
            return klass
        if klass is None:
            return _decorator
        return _decorator(klass)

    @classmethod
    def get(cls, key: str):
        return cls._REG.get((key or "").strip().lower())

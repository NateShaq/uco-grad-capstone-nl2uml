from __future__ import annotations
from app.infrastructure.internal.agent_registry import AgentRegistry

@AgentRegistry.register("gronk")
class GronkClient:
    def __init__(self, **_: object): ...
    def generate(self, prompt: str) -> str:
        return f"[gronk simulated] {prompt[:80]}"
    def prompt_to_uml(self, prompt: str, **_: object) -> str:
        return self.generate(prompt)
    def generate_code(self, text: str) -> str:
        return self.generate(text)

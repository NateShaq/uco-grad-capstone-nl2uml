from __future__ import annotations
from typing import Optional
from app.infrastructure.internal.agent_registry import AgentRegistry

@AgentRegistry.register("openai")
class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **_: object):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
    def generate(self, prompt: str) -> str:
        return f"[openai simulated] {prompt[:80]}"
    def prompt_to_uml(self, prompt: str, **_: object) -> str:
        return self.generate(prompt)
    def generate_code(self, text: str) -> str:
        return self.generate(text)

from __future__ import annotations
import os, requests, logging
from typing import Optional
from app.infrastructure.internal.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)

@AgentRegistry.register("ollama")
class OllamaClient:
    """Minimal Ollama client used by InfrastructureService."""
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None, **_: object):
        self.host = (host or os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL") or "mistral"

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.host}{path}"
        logger.info("[ollama] sending prompt to model=%s url=%s", payload.get("model"), url)
        data = {"stream": False, **payload}
        r = requests.post(url, json=data, timeout=120)
        r.raise_for_status()
        return r.json()

    def generate(self, prompt: str) -> str:
        resp = self._post("/api/generate", {"model": self.model, "prompt": prompt})
        return resp.get("response", "")

    def prompt_to_uml(self, prompt: str, **_: object) -> str:
        return self.generate(prompt)

    def explain_model(self, model: str) -> str:
        return self.generate(f"Explain this UML model briefly:\n\n{model}")

    def render_model(self, model: str) -> str:
        return model

    def refine_model(self, model: str, feedback: str) -> str:
        return self.generate(f"Refine this UML model based on feedback.\n\nModel:\n{model}\n\nFeedback:\n{feedback}")

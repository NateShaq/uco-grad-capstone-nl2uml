from __future__ import annotations
from typing import Any
from app.infrastructure.internal.agent_registry import AgentRegistry

class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, **kwargs: Any):
        key = (agent_type or "").strip().lower()
        aliases = {"aws": "bedrock", "xai": "gronk"}
        key = aliases.get(key, key)

        agent_class = AgentRegistry.get(key)

        if agent_class is None:
            if key == "ollama":
                from app.infrastructure.internal.ollama_client import OllamaClient
                AgentRegistry.register("ollama", OllamaClient)
                agent_class = OllamaClient
            elif key in ("ollama-pipeline", "ollama_pipeline", "ollama-multi"):
                from app.infrastructure.internal.ollama_pipeline_client import MultiOllamaPipelineClient
                AgentRegistry.register("ollama-pipeline", MultiOllamaPipelineClient)
                agent_class = MultiOllamaPipelineClient
            elif key in ("openai", "azure-openai"):
                from app.infrastructure.internal.openai_client import OpenAIClient
                AgentRegistry.register("openai", OpenAIClient)
                agent_class = OpenAIClient
            elif key in ("gronk", "bedrock"):
                from app.infrastructure.internal.gronk_client import GronkClient
                AgentRegistry.register("gronk", GronkClient)
                agent_class = GronkClient

        if agent_class is None:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent_class(**kwargs)

def create_agent(agent_type: str, **kwargs: Any):
    return AgentFactory.create_agent(agent_type, **kwargs)

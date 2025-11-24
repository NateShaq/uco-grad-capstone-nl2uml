from __future__ import annotations
import os
from typing import Optional

from app.infrastructure.i_infrastructure_service import IInfrastructureService
from app.infrastructure.internal.agent_factory import AgentFactory
from app.infrastructure.internal.websockets import WebSocketPushService
from app.infrastructure.repositories.model_store_repository import ModelStoreAdapter, ModelStoreDiagramRepository

class InfrastructureService(IInfrastructureService):
    def __init__(self, agent_client=None, store: Optional[ModelStoreAdapter] = None, diagram_repo=None, websocket_service: WebSocketPushService | None = None):
        if agent_client is None:
            default_agent = os.getenv("AI_AGENT_TYPE") or os.getenv("AGENT") or "ollama"
            agent_client = AgentFactory.create_agent(default_agent)
        self._ai = agent_client
        self._store = store or ModelStoreAdapter()
        self._diagram_repo = diagram_repo or ModelStoreDiagramRepository()
        self._ws = websocket_service

    def generate_prompt(self, prompt: str) -> str:
        return self._ai.generate(prompt)

    def prompt_to_uml(self, prompt: str, agent_type: Optional[str] = None, diagram_type: Optional[str] = None, pipeline_prompts: Optional[dict] = None) -> str:
        agent = AgentFactory.create_agent(agent_type) if agent_type else self._ai
        if hasattr(agent, "prompt_to_uml"):
            return agent.prompt_to_uml(prompt, diagram_type=diagram_type, pipeline_prompts=pipeline_prompts)
        raise NotImplementedError("Selected agent does not support prompt_to_uml.")

    def explain_model(self, model: str) -> str:
        agent = self._ai
        if hasattr(agent, "explain_model"):
            return agent.explain_model(model)
        if hasattr(agent, "generate"):
            return agent.generate(f"Explain this UML model briefly:\n\n{model}")
        raise NotImplementedError("This agent does not support explain_model.")

    def render_model(self, model: str) -> str:
        if hasattr(self._ai, "render_model"):
            return self._ai.render_model(model)
        return model

    def refine_model(self, model: str, feedback: str, agent_override=None) -> str:
        agent = agent_override if agent_override else self._ai
        if hasattr(agent, "refine_model"):
            return agent.refine_model(model, feedback)
        raise NotImplementedError("This agent does not support refine_model.")

    def generate_code(self, model: str, agent_type: Optional[str] = None) -> str:
        agent = AgentFactory.create_agent(agent_type) if agent_type else self._ai
        if hasattr(agent, "generate_code"):
            return agent.generate_code(model)
        if hasattr(agent, "generate"):
            return agent.generate(model)
        raise NotImplementedError("Selected agent does not support code generation.")

    def cleanup_old_models(self) -> None:
        self._store.cleanup_old_models()

    def retrieve(self, pk: str, sk: str) -> str:
        return self._store.retrieve(pk, sk)

    def save_model(self, pk: str, sk: str, value: str) -> None:
        print("Saving model to store:", pk, sk)
        self._store.save(pk, sk, value)

    def load_model(self, pk: str, sk: str) -> str:
        return self._store.retrieve(pk, sk)

    @property
    def diagram_repo(self):
        return self._diagram_repo

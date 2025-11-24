from __future__ import annotations
from abc import ABC, abstractmethod

class IApplicationService(ABC):

    @abstractmethod
    def generate_model(self, prompt: str, diagram_id: str, agent_type: str = None, diagram_type: str = None, pipeline_prompts: dict | None = None) -> str:
        """Generate a UML model, optionally using a specific AI agent."""
        pass
    
    @abstractmethod
    def explain_model(self, model_id: str) -> str:
        pass

    @abstractmethod
    def generate_code(self, model_id: str) -> str:
        pass

    @abstractmethod
    def render_model(self, model_id: str) -> str:
        pass

    @abstractmethod
    def cleanup_expired(self) -> None:
        pass

    @abstractmethod
    def generate_code_from_uml(self, prompt: str, agent_type: str = None) -> str:
        pass

    @abstractmethod
    def generate_prompt_with_template(self, user_email: str, project_id: str, name: str, diagram_type: str, prompt: str, agent_type: str = "openai") -> tuple[str, dict | None]:
        pass

    @abstractmethod
    def handle_generate_request(self, user_email: str, body: dict) -> dict:
        """Handle a /generate rest request to generate a UML diagram."""
        pass

    @abstractmethod
    def handle_refine_request(self, user_email: str, body: dict) -> dict:
        """Handle a /refine rest request to generate a UML diagram."""
        pass

    # Thin delegators to ProjectManager
    @abstractmethod
    def create_project(self, event, user_email):
        pass

    @abstractmethod
    def list_projects(self, user_email):
        pass

    @abstractmethod
    def get_project(self, user_email, project_id):
        pass

    @abstractmethod
    def delete_project(self, user_email, project_id):
        pass

    # Thin delegators to DiagramManager  
    @abstractmethod  
    def create_diagram(self, event, user_email, project_id):
        pass

    @abstractmethod
    def list_diagrams(self, user_email, project_id):
        pass

    @abstractmethod
    def get_diagram(self, user_email, diagram_id):
        pass

    @abstractmethod
    def delete_diagram(self, user_email, diagram_id):
        pass

    # For REST route /diagrams/{diagramId}
    @abstractmethod
    def get_diagram_by_id(self, user_email, diagram_id):
        pass

    @abstractmethod
    def handle_code_request(self, user_email: str, body: dict) -> dict:
        pass

    @abstractmethod
    def handle_undo_request(self, user_email: str, body: dict) -> dict:
        pass

    @abstractmethod
    def handle_redo_request(self, user_email: str, body: dict) -> dict:
        pass

from __future__ import annotations
from abc import ABC, abstractmethod

class IDomainAccess(ABC):
    @abstractmethod
    def parse_uml(self, raw: str):
        pass

    @abstractmethod
    def validate_model(self, model: str) -> bool:
        pass

    @abstractmethod
    def refine_model(self, model_id: str, feedback: str) -> dict:
        pass

    @abstractmethod
    def create_user_if_not_exists(self, email: str):
        pass
    
    @abstractmethod
    def generate_prompt_with_template(self, user_email: str, project_id: str, name: str, diagram_type: str, prompt: str,
        agent_type: str = "openai") -> tuple[str, dict | None]:
        pass

    @abstractmethod
    def undo_last_command(self, user_email: str, project_id: str, diagram_id: str) -> dict:
        pass

    # --- Project accessors ---
    @abstractmethod
    def create_project(self, user_email: str, name: str, description: str) -> dict:
        """Create a project for the given user and return the project record."""
        pass

    @abstractmethod
    def list_projects(self, user_email: str) -> list[dict]:
        pass

    @abstractmethod
    def get_project(self, user_email: str, project_id: str) -> dict | None:
        pass

    @abstractmethod
    def delete_project(self, user_email: str, project_id: str) -> bool:
        pass

    # --- Diagram accessors ---
    @abstractmethod
    def create_diagram_record(self, diagram_item: dict) -> None:
        """Persist a diagram record."""
        pass

    @abstractmethod
    def list_project_diagrams(self, project_id: str) -> list[dict]:
        pass

    @abstractmethod
    def get_diagram_by_id(self, diagram_id: str) -> dict | None:
        pass

    @abstractmethod
    def delete_diagram(self, diagram_id: str) -> None:
        pass

    @abstractmethod
    def set_diagram_plantuml(self, diagram_id: str, plantuml: str) -> None:
        """Update an existing diagram's PlantUML content."""
        pass

    # --- Command history ---
    @abstractmethod
    def record_refine_command(self, *, diagram_id: str, user_email: str, project_id: str, command_id: str, timestamp: int, plantuml_before: str, plantuml_after: str) -> None:
        pass

    @abstractmethod
    def redo_last_command(self, user_email: str, project_id: str, diagram_id: str) -> dict | None:
        pass

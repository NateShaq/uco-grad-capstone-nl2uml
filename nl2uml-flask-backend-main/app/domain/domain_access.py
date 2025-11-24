from __future__ import annotations
from datetime import datetime
import uuid
from .i_domain_access import IDomainAccess
from .internal.uml_model import UMLModel
from .internal.prompt_template_factory import PromptTemplateFactory

class DomainAccess(IDomainAccess):
    def __init__(self, user_repo, model_repository, prompt_template_service, command_repo):
        self.user_repo = user_repo
        self.model_repository = model_repository
        self.prompt_template_service = prompt_template_service
        self.command_repo = command_repo

    def parse_uml(self, raw: str):
        return UMLModel(raw)

    def validate_model(self, model: str) -> bool:
        return UMLModel(model).is_valid()

    def refine_model(self, model_id: str, feedback: str) -> dict:
        model = self.model_repository.get_by_id(model_id)
        prompt = self.prompt_template_service.create_prompt(model, feedback)
        return {"prompt": prompt, "model": model}

    def create_user_if_not_exists(self, email: str):
        user = self.user_repo.get_user(email)
        if not user:
            self.user_repo.create_user(email)

    def generate_prompt_with_template(
        self,
        user_email: str,
        project_id: str,
        name: str,
        diagram_type: str,
        prompt: str,
        agent_type: str = "openai"
    ) -> tuple[str, dict | None]:
        """Use the domain PromptTemplateFactory to enrich and generate the final prompt and pipeline prompts."""
        template = PromptTemplateFactory.get_template(diagram_type)

        # Allow each Template to decide if it needs extra related diagrams
        context_data = {}

        if template.requires_related_plantuml():
            context_data['related_plantuml'] = self._load_related_class_diagram(user_email, project_id)

        final_prompt = template.build_prompt(user_prompt=prompt, **context_data)
        pipeline_prompts = template.build_pipeline_prompts(user_prompt=prompt, **context_data)
        return final_prompt, pipeline_prompts

    def _load_related_class_diagram(self, user_email: str, project_id: str) -> str:
        """Try to find and return the Class Diagram PlantUML for the project."""
        repo = self.model_repository
        if hasattr(repo, "list_project_diagrams"):
            diagrams = repo.list_project_diagrams(user_email, project_id)
        elif hasattr(repo, "get_by_project"):
            diagrams = repo.get_by_project(project_id)
        else:
            diagrams = []
        for diagram in diagrams:
            if diagram.get("diagramType") == "class":
                return diagram.get("plantuml", "")
        return ""
        
    def undo_last_command(self, user_email: str, project_id: str, diagram_id: str) -> dict:
        return self.command_repo.undo(diagram_id, user_email, project_id)

    # --- Projects ---
    def create_project(self, user_email: str, name: str, description: str) -> dict:
        project = {"projectId": str(uuid.uuid4()), "name": name, "description": description}
        user = self.user_repo.get_user(user_email) or {"projects": []}
        projects = list(user.get("projects", []))
        projects.append(project)
        if hasattr(self.user_repo, "update_projects"):
            self.user_repo.update_projects(email=user_email, projects=projects)
        return project

    def list_projects(self, user_email: str) -> list[dict]:
        if hasattr(self.user_repo, "list_projects"):
            return list(self.user_repo.list_projects(user_email))
        user = self.user_repo.get_user(user_email) or {}
        return list(user.get("projects", []))

    def get_project(self, user_email: str, project_id: str) -> dict | None:
        for proj in self.list_projects(user_email):
            if proj.get("projectId") == project_id:
                return proj
        return None

    def delete_project(self, user_email: str, project_id: str) -> bool:
        projects = [p for p in self.list_projects(user_email) if p.get("projectId") != project_id]
        if hasattr(self.user_repo, "update_projects"):
            self.user_repo.update_projects(email=user_email, projects=projects)
            return True
        return False

    # --- Diagrams ---
    def create_diagram_record(self, diagram_item: dict) -> None:
        pk = diagram_item["diagramId"]
        self.model_repository.save(pk, diagram_item)

    def list_project_diagrams(self, project_id: str) -> list[dict]:
        if hasattr(self.model_repository, "get_by_project"):
            return list(self.model_repository.get_by_project(project_id))
        return []

    def get_diagram_by_id(self, diagram_id: str) -> dict | None:
        if hasattr(self.model_repository, "get_by_id"):
            return self.model_repository.get_by_id(diagram_id)
        return None

    def delete_diagram(self, diagram_id: str) -> None:
        if hasattr(self.model_repository, "delete"):
            self.model_repository.delete(diagram_id)

    def set_diagram_plantuml(self, diagram_id: str, plantuml: str) -> None:
        diagram = self.get_diagram_by_id(diagram_id) or {}
        diagram["plantuml"] = plantuml
        diagram["updatedAt"] = datetime.utcnow().isoformat()
        self.create_diagram_record(diagram)

    # --- Command history ---
    def record_refine_command(self, *, diagram_id: str, user_email: str, project_id: str, command_id: str, timestamp: int, plantuml_before: str, plantuml_after: str) -> None:
        if hasattr(self.command_repo, "record_refine"):
            self.command_repo.record_refine(
                diagram_id=diagram_id,
                user_email=user_email,
                project_id=project_id,
                command_id=command_id,
                timestamp=timestamp,
                plantuml_before=plantuml_before,
                plantuml_after=plantuml_after,
            )

    def redo_last_command(self, user_email: str, project_id: str, diagram_id: str) -> dict | None:
        if hasattr(self.command_repo, "redo"):
            return self.command_repo.redo(diagram_id, user_email, project_id)
        return None

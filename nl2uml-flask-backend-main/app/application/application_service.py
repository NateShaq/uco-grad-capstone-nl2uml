import json
import os
import re
import uuid
from datetime import datetime
from typing import Optional

from .i_application_service import IApplicationService
from .i_websocket_service import IWebSocketService

from ..infrastructure.i_infrastructure_service import IInfrastructureService
from ..domain.i_domain_access import IDomainAccess

from .generate_diagram import GenerateDiagram
from .refine_diagram import RefineDiagram
from .generate_code_from_diagram import GenerateCodeFromDiagram
from .redo_command import RedoCommand
# from application.undo_command import UndoCommand
from ..domain.internal.plantuml_sanitizer import sanitize_plantuml
from ..domain.internal.plantuml_validator import PlantUMLValidator

def extract_sections(result):
    """
    Extract PlantUML code from LLM output, whether or not it's in a code block.
    """
    # Case 1: Fenced code block
    plantuml_match = re.search(r'```plantuml\s*(.*?)\s*```', result, re.DOTALL)
    if plantuml_match:
        plantuml = plantuml_match.group(1).strip()
        explanation = result[plantuml_match.end():].strip()
        return plantuml, explanation

    # Case 2: Unfenced, but contains @startuml ... @enduml
    at_start = result.find('@startuml')
    at_end = result.find('@enduml')
    if at_start != -1 and at_end != -1:
        plantuml = result[at_start:at_end+8].strip()
        explanation = result[at_end+8:].strip()
        return plantuml, explanation

    # Default: no code found, fallback
    return "", result.strip()

class ApplicationService(IApplicationService):
    def __init__(self, infra: IInfrastructureService, domain: IDomainAccess, websocket_service: IWebSocketService | None = None):
        # Core dependencies
        self.infra = infra
        self.domain = domain
        self.websocket_service = websocket_service
        self._uml_validator = PlantUMLValidator()

    def handle_refine_request(self, user_email: str, body: dict) -> dict:
        use_case = RefineDiagram(app_service=self)
        return use_case.execute(user_email, body)

    def handle_generate_request(self, user_email: str, body: dict) -> dict:
        print(f"[nlp_agent] HERE 1")
        use_case = GenerateDiagram(app_service=self)
        return use_case.execute(user_email, body)

    def ensure_user_exists(self, email: str):
        self.domain.create_user_if_not_exists(email)

    def get_diagram(self, user_email, project_id, diagram_id):
        # Assuming your domain access exposes a way to fetch a diagram
        return self.domain.get_diagram_by_id(diagram_id)

    def explain_model(self, model_id: str) -> str:
        if not model_id:
            raise ValueError("diagramId is required")

        model_record = self.domain.get_diagram_by_id(model_id)
        if not model_record:
            raise ValueError(f"Diagram {model_id} not found")

        model_text = (
            model_record
            if isinstance(model_record, str)
            else model_record.get("plantuml") or str(model_record)
        )
        return self.infra.explain_model(model_text)

    def generate_code(self, model_id: str) -> str:
        model = self.infra.load_model(model_id)
        return self.infra.generate_code(model)

    def render_model(self, model_id: str) -> str:
        model = self.infra.load_model(model_id)
        return self.infra.render_model(model)

    def cleanup_expired(self) -> None:
        self.infra.cleanup_old_models()

    def generate_and_save_diagram(self, user_email, project_id, name, diagram_type, prompt, diagram_id=None, agent_type=None, pipeline_prompts=None):
        self.ensure_user_exists(user_email)
        print("Generating diagram for user:", user_email)
        if not diagram_id:
            diagram_id = str(uuid.uuid4())

        result = self.generate_model(prompt, diagram_id, agent_type, diagram_type=diagram_type, pipeline_prompts=pipeline_prompts)
        print("results:", result)
        plantuml_text, explanation = extract_sections(result)

        created_at = datetime.utcnow().isoformat()
        print("Prompt to LLM:", prompt)
        print("Extracted PlantUML:", plantuml_text)
        print("Extracted Explanation:", explanation)

        sanitize_enabled = (os.getenv("ENABLE_PLANTUML_SANITIZER", "1").lower() in ("1", "true", "yes", "on"))
        if sanitize_enabled and (diagram_type or "").lower() == "class":
            plantuml_text = sanitize_plantuml(plantuml_text)

        plantuml_text = self._validate_and_fix_plantuml(
            plantuml_text=plantuml_text,
            diagram_type=diagram_type,
            original_prompt=prompt,
        )

        diagram_item = {
            "diagramId": diagram_id,
            "projectId": project_id,
            "userEmail": user_email,
            "name": name,
            "diagramType": diagram_type,
            "plantuml": plantuml_text,
            "createdAt": created_at,
        }
        print(f"[DynamoDB Put] Saving diagram_item: {diagram_item}")

        self.domain.create_diagram_record(diagram_item)

        return {
            "diagramId": diagram_id,
            "projectId": project_id,
            "name": name,
            "diagramType": diagram_type,
            "plantuml": plantuml_text,
            "explanation": explanation
        }

    def generate_model(self, prompt: str, diagram_id: str, agent_type: str = None, diagram_type: str = None, pipeline_prompts: dict | None = None) -> str:
        print("running generate_modela")
        uml = self.infra.prompt_to_uml(prompt, agent_type, diagram_type=diagram_type, pipeline_prompts=pipeline_prompts)
        print("running generate_model")
        self.infra.save_model(diagram_id, "DIAGRAM", uml)
        return uml
    
    def generate_code_from_uml(self, prompt: str, agent_type: str = None) -> str:
        """Generate code from UML prompt using the selected agent."""
        return self.infra.generate_code(prompt, agent_type=agent_type)

    def generate_prompt_with_template(self, user_email: str, project_id: str, name: str, diagram_type: str, prompt: str, agent_type: str = "openai") -> tuple[str, dict | None]:
        """Create a polished AI prompt template for the diagram selected"""
        print("running generate_prompt_with_template")
        return self.domain.generate_prompt_with_template(user_email, project_id, name, diagram_type, prompt, agent_type)

     # Thin delegators to ProjectManager
    def create_project(self, event, user_email):
        data = json.loads(event["body"])
        project = self.domain.create_project(user_email, data["name"], data.get("description", ""))
        return {"statusCode": 201, "body": json.dumps(project)}

    def list_projects(self, user_email):
        return {"statusCode": 200, "body": json.dumps({"projects": self.domain.list_projects(user_email)})}

    def get_project(self, user_email, project_id):
        project = self.domain.get_project(user_email, project_id)
        if not project:
            return {"statusCode": 404, "body": json.dumps({"error": "Project not found"})}
        return {"statusCode": 200, "body": json.dumps(project)}

    def delete_project(self, user_email, project_id):
        deleted = self.domain.delete_project(user_email, project_id)
        if not deleted:
            return {"statusCode": 404, "body": json.dumps({"error": "Project not found"})}
        return {"statusCode": 204, "body": json.dumps({})}
     
    # Thin delegators to DiagramManager
    def create_diagram(self, event, user_email, project_id):
        data = json.loads(event["body"])
        diagram_id = str(uuid.uuid4())
        item = {
            "diagramId": diagram_id,
            "projectId": project_id,
            "userEmail": user_email,
            "name": data.get("name"),
            "diagramType": data.get("diagramType", ""),
            "plantuml": data.get("plantuml", ""),
            "createdAt": datetime.utcnow().isoformat(),
        }
        self.domain.create_diagram_record(item)
        return {"statusCode": 201, "body": json.dumps(item)}

    def list_diagrams(self, user_email, project_id):
        diagrams = self.domain.list_project_diagrams(project_id)
        return {"statusCode": 200, "body": json.dumps({"diagrams": diagrams})}

    def delete_diagram(self, user_email, diagram_id):
        self.domain.delete_diagram(diagram_id)
        return {"statusCode": 204, "body": json.dumps({})}

    def get_diagram_by_id(self, user_email, diagram_id):
        diagram = self.domain.get_diagram_by_id(diagram_id)
        if not diagram:
            return {"statusCode": 404, "body": json.dumps({"error": "Diagram not found"})}
        return {"statusCode": 200, "body": json.dumps(diagram)}
    
    def handle_code_request(self, user_email: str, body: dict) -> dict:
        return GenerateCodeFromDiagram(app_service=self).execute(user_email, body)
    
    def handle_undo_request(self, user_email: str, body: dict) -> dict:
        from .undo_command import UndoCommand
        return UndoCommand(app_service=self).execute(user_email, body)

    def handle_redo_request(self, user_email: str, body: dict) -> dict:
        return RedoCommand(app_service=self).execute(user_email, body)

    def _validate_and_fix_plantuml(
        self,
        plantuml_text: str,
        diagram_type: Optional[str],
        original_prompt: str,
    ) -> str:
        """
        Run PlantUML validation (if configured) and try to auto-fix syntax errors
        by asking the agent to refine the diagram using the validator output.
        """
        validator = getattr(self, "_uml_validator", None)
        if not validator or not validator.is_available():
            return plantuml_text

        current = plantuml_text
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            is_valid, validator_output = validator.validate(current)
            if is_valid:
                print(f"[plantuml] validator accepted diagram on attempt {attempt}/{max_attempts}:")
                print(current)
                return current

            print(f"[plantuml] validation failed (attempt {attempt}/{max_attempts}): {validator_output}")

            feedback = (
                f"The PlantUML diagram failed validation with the following error:\n"
                f"{validator_output or 'Unknown validator error'}\n\n"
                f"Diagram type: {diagram_type or 'unspecified'}\n"
                f"Original user request:\n{original_prompt}\n\n"
                "Please correct ONLY the syntax errors while keeping the semantics intact. "
                "Respond with valid PlantUML between @startuml and @enduml."
            )
            try:
                agent_response = self.infra.refine_model(current, feedback)
                refined, _ = extract_sections(agent_response)
                current = sanitize_plantuml(refined or agent_response)
            except NotImplementedError:
                print("[plantuml] refine_model not supported by current agent; aborting auto-fix.")
                break

        print(f"[plantuml] validator failed after {max_attempts} attempts. Final diagram:")
        print(current)
        return current

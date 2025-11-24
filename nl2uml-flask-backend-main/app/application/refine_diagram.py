from typing import Dict
import time
import uuid

class RefineDiagram:
    def __init__(self, app_service: "ApplicationService"):
        self.app = app_service

    def execute(self, user_email: str, body: Dict) -> Dict:
        project_id = body.get("projectId")
        diagram_id = body.get("diagramId")
        feedback = body.get("feedback", "")
        agent_type = body.get("AI_Agent", "").lower().strip() or "ollama"

        if not (diagram_id and project_id and feedback):
            raise ValueError("Missing required parameters")

        command_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)

        current = self.app.get_diagram(user_email, project_id, diagram_id)
        plantuml_before = current.get("plantuml", "")

        # Build prompt
        updated_prompt = (
            f"Given this PlantUML diagram:\n\n{plantuml_before}\n\n"
            f"Apply the following refinement or feedback:\n{feedback}\n"
            "Return the updated PlantUML code only."
        )

        new_diagram = self.app.generate_and_save_diagram(
            user_email=user_email,
            project_id=project_id,
            name=current["name"],
            diagram_type=current["diagramType"],
            prompt=updated_prompt,
            diagram_id=diagram_id,
            agent_type=agent_type
        )

        plantuml_after = new_diagram.get("plantuml", "")

        try:
            self.app.domain.record_refine_command(
                diagram_id=diagram_id,
                user_email=user_email,
                project_id=project_id,
                command_id=command_id,
                timestamp=timestamp,
                plantuml_before=plantuml_before,
                plantuml_after=plantuml_after,
            )
        except AttributeError:
            pass

        if self.app.websocket_service:
            self.app.websocket_service.push_message_to_user(
                user_email=user_email,
                message={
                    "action": "diagram.updated",
                    "payload": {
                        "diagramId": diagram_id,
                        "projectId": project_id,
                        "plantuml": plantuml_after,
                        "status": "refined"
                    }
                }
            )

        return {
            "diagram": new_diagram,
            "message": "Diagram refined!",
            "explanation": new_diagram.get("explanation", "")
        }

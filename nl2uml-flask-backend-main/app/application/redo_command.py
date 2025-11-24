from typing import Dict
from datetime import datetime

class RedoCommand:
    def __init__(self, app_service: "ApplicationService"):
        self.app = app_service

    def execute(self, user_email: str, body: Dict) -> Dict:
        diagram_id = body.get("diagramId")
        project_id = body.get("ProjectId") or body.get("projectId")

        if not diagram_id or not project_id:
            raise ValueError("diagramId and projectId required.")

        result = self.app.domain.redo_last_command(user_email, project_id, diagram_id)
        if not result:
            raise ValueError("No commands to redo.")

        plantuml = result.get("plantuml", "")
        self._persist_state(user_email, project_id, diagram_id, plantuml)

        return {
            "diagramId": diagram_id,
            "plantuml": plantuml,
            "message": result.get("message", "Redo successful"),
        }

    def _persist_state(self, user_email: str, project_id: str, diagram_id: str, plantuml: str) -> None:
        diagram = self.app.domain.get_diagram_by_id(diagram_id)
        if not diagram:
            return
        diagram["plantuml"] = plantuml
        diagram["updatedAt"] = datetime.utcnow().isoformat()
        self.app.domain.create_diagram_record(diagram)
